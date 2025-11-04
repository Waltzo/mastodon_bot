#!/usr/bin/python3
# -*- coding: utf-8 -*-
from modules.spreadsheet_utils import members, craft_result
from modules.text_utils import filterText
from worksheet_columns import define_columns
import re
from modules.game_logic.update_inv import str2tuple, update_inventory
from modules.game_logic.Gathering import get_item_list
import random
from modules.game_logic.tools import stat_adj, split_item_list, is_enough, job_check, user_inv
from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))

def check_item_valid(item_type, output_item_list, min_count=5):
    """
        제작시 투입 아이템이 유효한지 확인하는 함수
        ## args
            item_type
                아이템 종류 (무기, 방어구, 연금약, 음식)
            item_list
                투입 아이템 리스트
        ## API 요청
            읽기: 1회
            쓰기: 0회
    """
    # 아이템 리스트 호출 - API 요청 1회
    if item_type in ["무기", "방어구"]:
        glist = get_item_list("일반재료","재료")
    elif item_type == "연금약":
        glist = get_item_list("연금재","재료")
    elif item_type == "음식":
        glist = get_item_list("식재료","재료")
    count = sum(qty for name, qty in output_item_list if name in glist)
    return count >= min_count

def find_first_empty_row():
    """ 
        craft_result 의 첫 빈 행을 확인하는 함수
        ## API 요청
            읽기: 1회
            쓰기: 0회
    """
    crafter_col = define_columns["craft_result"]["CRAFTER"]
    col_values = craft_result.col_values(crafter_col) # API 요청 1회
    for idx, val in enumerate(col_values, start=1): 
        if not val.strip():
            return idx
    return len(col_values) + 1  # 모두 차있으면 다음 행 반환


def calc_value(init, dex, max_val):
    """
        초기치 + (손재주 수치 ~ 최대치) 사이의 랜덤값
    """
    return init + random.randint(0, min(dex, max_val-init))

def crafting(user_account, user_name, item_type, ingr_list):
    """
        아이템 제작 함수
        ## args
            user_account
                사용자 계정 
            user_name
                사용자 닉네임
            item_type
                제작 타입
            ingr_list
                재료 리스트(튜플리스트)
        ## API 요청 총 9~13회
            읽기: 7회
            쓰기(무/방/음): 2회
            쓰기(연금약): 3~6회
    """
    # API 요청 1회
    finder = members.find(user_account, in_column=define_columns["members"]["CHRID"], case_sensitive=True) 
    if not finder:
        return "NONE"
    
    account_row = finder.row
    # API 요청 1회
    row_values = members.row_values(account_row)  
    
    if not job_check(row_values) == "CRAFTER_GATHERER":
        return "INVALID_JOB"

    if check_empty_item_name_value(user_name):
        return "NAME_FIRST"

    if item_type not in ["무기", "방어구", "연금약", "음식"]:
        return "INVALID_TYPE"
    
    ingr_items = split_item_list(ingr_list)
    
    if isinstance(ingr_items, str):
        return ingr_items
    
    item_count = 0
    for _, b in ingr_items:
        item_count += b
    if item_count < 5:
        return "NOT_ENOUGH_1"
    
    user_inventory = user_inv(row_values)
    
    # API 요청 3회
    if not check_item_valid(item_type, ingr_items): 
        return "NOT_ENOUGH_3"
    
    if not is_enough(user_inventory, ingr_items):
        return "NOT_ENOUGH_2"
    
    # API 요청 2회
    update_inventory(account_row, row_values, "sub", ingr_items)
    
    # API 요청 1회
    empty_row = find_first_empty_row()
    
    dex = int(row_values[define_columns["members"]["DEX"] - 1] or 0)

    craft_time = datetime.now(KST).strftime('%Y-%m-%d')
    if item_type == "무기": # API 요청 1회
        item_effect = f"[{calc_value(1, dex, 4)}]턴 간 공격시 적에게 [{2 + stat_adj(dex)}]만큼의 추가 대미지"
        craft_result.update(f'A{empty_row}:H{empty_row}', [[user_name,user_name,'',item_type,item_effect,craft_time,False,'']])
        return item_effect
    
    elif item_type ==  "방어구": # API 요청 1회
        item_effect = f"[{calc_value(1, dex, 4)}]턴 간 피격시 [{5 + stat_adj(dex)}]만큼 막아냄"
        craft_result.update(f'A{empty_row}:H{empty_row}', [[user_name,user_name,'',item_type,item_effect,craft_time,False,'']])
        return item_effect
        
    elif item_type == "연금약": # API 요청 2~4회
        
        med_type = random.choice(['붉은색', '푸른색', '초록색'])
        if med_type == "붉은색":
            stet = stat_adj(dex)
            item_effect = f"하루동안 전투력에 [{stet}]만큼의 보정치를 추가"
        elif med_type == "초록색":
            stet = stat_adj(dex)
            item_effect = f"하루동안 안목 혹은 손놀림에 [{stet}]만큼의 보정치를 추가"
        elif med_type == "푸른색":
            stet = stat_adj(dex)*10
            item_effect = f"체력을 [{stet}]만큼 회복"
            
        item_count = calc_value(1, dex, 3)
        for _ in range(item_count):
            empty_row = find_first_empty_row()
            craft_result.update(f'A{empty_row}:H{empty_row}', [[user_name,user_name,f"{med_type} 연금약(+{stet})",item_type,item_effect,craft_time,False,'']])

        update_inventory(account_row, row_values, "add", [(f"{med_type} 연금약(+{stet})", item_count)])

        return item_effect, item_count, med_type
        
    elif item_type == "음식": # API 요청 1회
        item_stet = 10 + stat_adj(dex)
        item_effect = f"하루동안 [{item_stet}]만큼 최대 체력을 올림"
        item_count = calc_value(1, dex, 5)
        for _ in range(item_count):
            empty_row = find_first_empty_row()
            craft_result.update(f'A{empty_row}:H{empty_row}', [[user_name,user_name,'',item_type,item_effect,craft_time,False,'']])
        return item_effect, item_count
    
def get_rows_by_crafter(user_name):
    crafter_col = define_columns["craft_result"]["CRAFTER"]
    all_values = craft_result.get_all_values()
    # enumerate로 행 번호(1부터)와 함께 반환
    return [(idx+1, row[:7]) for idx, row in enumerate(all_values) if len(row) >= crafter_col and row[crafter_col-1] == user_name]

def get_rows_by_itemname(item_name):
    item_name_col = define_columns["craft_result"]["ITEMNAME"]-1
    all_values = craft_result.get_all_values()
    # enumerate로 행 번호(1부터)와 함께 반환
    return [(idx+1, row[:7]) for idx, row in enumerate(all_values) if len(row) >= item_name_col and row[item_name_col] == item_name]

def name_check(item_name):
    used_col = define_columns["craft_result"]["USED"]-1
    rows = get_rows_by_itemname(item_name)
    for _, cols in rows:
        if len(cols) >= 2 and (cols[used_col] == 'FALSE' or cols[used_col] is None):
            return "NAME_TAKEN"

def check_empty_item_name_value(user_name):
    itemname_col = define_columns["craft_result"]["ITEMNAME"]-1
    rows = get_rows_by_crafter(user_name)
    for _, cols in rows:
        if len(cols) >= 2 and (cols[itemname_col] == '' or cols[itemname_col] is None):
            return "NAME_FIRST"


def job_done(user_account, user_name, item_name):
    """
        아이템 제작 함수
        ## args
            user_account
                사용자 계정 
            user_name
                사용자 닉네임
            item_type
                제작 타입
            ingr_list
                재료 리스트(튜플리스트)
        ## API 요청 총 9~13회
            읽기: 7회
            쓰기: 2회
            쓰기: 3~6회(연금약)
    """
    
    CLEANER = re.compile(r'[^\w\s]')
    
    finder = members.find(user_account, in_column=define_columns["members"]["CHRID"], case_sensitive=True)
    if not finder:
        return "NONE"
    account_row = finder.row
    # API 요청 1회
    row_values = members.row_values(account_row)  
    
    rows = get_rows_by_crafter(user_name)
    if check_empty_item_name_value(user_name) != "NAME_FIRST":
        return "NO_ITEM"
    if name_check(item_name):
        return "NAME_TAKEN"
    
    item_lists = get_item_list("전체","전체")
    if item_name in item_lists:
        return "CANNOT_USE"
    
    item_name = f'"{filterText(item_name, CLEANER).strip()}"'

    itemname_col = define_columns["craft_result"]["ITEMNAME"]
    cell_list = [craft_result.cell(row_num, itemname_col) for row_num, cols in rows if len(cols) >= itemname_col and (cols[itemname_col-1] == '' or cols[itemname_col-1] is None)]
    for cell in cell_list:
        cell.value = item_name
    if cell_list:
        craft_result.update_cells(cell_list)
    update_inventory(account_row, row_values, "add", [(item_name, len(cell_list))])