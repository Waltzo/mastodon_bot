#!/usr/bin/python3
# -*- coding: utf-8 -*-
from modules.spreadsheet_utils import members, craft_result
from worksheet_columns import define_columns
from collections import Counter

from modules.game_logic.update_inv import update_inventory, find_owner_col
from modules.game_logic.Gathering import get_item_list
from modules.game_logic.tools import calc_total_price, check_items_exist, is_enough, colnum_to_alpha, split_item_list, tuple2str, str2tuple, user_inv

from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))
import re

def buy_item(account, item_list_str):
    finder = members.find(account, in_column=define_columns["members"]["CHRID"], case_sensitive=True)
    if not finder:
        return "NONE"
    
    account_row = finder.row
    row_values = members.row_values(account_row)
    money_idx = define_columns["members"]["GIL"] - 1
    money_int = int(row_values[money_idx]) if len(row_values) > money_idx else ''
    
    item_list = split_item_list(item_list_str)
    buy_list = get_item_list("전체","구매")
    
    yes_list, no_list = check_items_exist(buy_list, item_list)

    if len(yes_list) == 0:
        return "NO_ITEM"
    
    total_cost = calc_total_price(buy_list, yes_list)
    if total_cost > money_int:
        return "NOT_ENOUGH"

    update_inventory(account_row, row_values,"add", yes_list)
    members.update_cell(account_row, define_columns["members"]["GIL"], money_int - total_cost)

    return tuple2str(yes_list), tuple2str(no_list)

    
def use_potion(account_row, row_values, owned_row, foc_val, name, colour, stet):
    
    DEXD_col = define_columns["members"]["DEXD"]-1
    INSD_col = define_columns["members"]["INSD"]-1
    MHPA_col_alpha = colnum_to_alpha(define_columns["members"]["MHPA"])
    DEXA_col_alpha = colnum_to_alpha(define_columns["members"]["DEXA"])
    
    fmt = '%m-%d %H:%M:%S'
    current_datetime = datetime.now(KST).strftime(fmt)
    
    members.update_cell(account_row, define_columns["members"]["POTI"], current_datetime)
    
    if colour == "붉은색":
        members.update(f'{MHPA_col_alpha}{account_row}:{DEXA_col_alpha}{account_row}', [[0,stet,0,0]])
        foc_val[6] = True
        foc_val[7] = name
        craft_result.update([foc_val], f"A{owned_row+1}:H{owned_row+1}")
        return f"{colour}색 연금약을 사용했습니다.\n하루동안 전투력에 [{stet}]만큼의 보정치를 추가합니다."
    
    elif colour == "초록색":
        if int(row_values[DEXD_col]) >= 1:
            effec = "손재주"
            stets = [[0,0,0,stet]]
        elif int(row_values[INSD_col]) >= 1:
            effec = "안목"
            stets = [[0,0,stet,0]]
        else:
            return "NO_EFFECT"
        members.update(f'{MHPA_col_alpha}{account_row}:{DEXA_col_alpha}{account_row}', stets)
        foc_val[6] = True
        foc_val[7] = name
        craft_result.update([foc_val], f"A{owned_row+1}:H{owned_row+1}")
        return f"{colour}색 연금약을 사용했습니다.\n하루동안 {effec}에 [{stet}]만큼의 보정치를 추가합니다."
    
    elif colour == "푸른색":
        foc_val[6] = True
        foc_val[7] = name
        craft_result.update([foc_val], f"A{owned_row+1}:H{owned_row+1}")
        return f"{colour}색 연금약을 사용했습니다.\n체력을 [{stet}]만큼 회복합니다."
    
def use_item(account, name, item_list_str):
    finder = members.find(account, in_column=define_columns["members"]["CHRID"], case_sensitive=True)
    if not finder:
        return "NONE"

    account_row = finder.row
    row_values = members.row_values(account_row)
    user_inventory = user_inv(row_values)
    
    # 단일 아이템 사용 여부
    item_list = split_item_list(item_list_str)
    if len(item_list) != 1 :
        return "MULTIPLE_ITEMS"
    
    if item_list[0][1] != 1 :
        return "MULTIPLE_ITEMS"
    
    # 인벤토리에 존재 여부
    if not is_enough(user_inventory, item_list):
        return "NOT_ENOUGH"
    
    # 아이템 목록에 존재하는 아이템인지 확인
    if item_list[0][0] == '포션':
        update_inventory(account_row, row_values, "sub", item_list)
        return "포션을 사용했습니다. 체력을 [5] 회복합니다."
    elif item_list[0][0] == '하이 포션':
        update_inventory(account_row, row_values, "sub", item_list)
        return "하이 포션을 사용했습니다. 체력을 [15] 회복합니다."
        
    else:
        # 제작 결과 시트에 소유 및 미사용 확인
        foc = find_owner_col(name, item_list[0][0])
        if isinstance(foc, str):
            return foc
        
        owned_row , val = foc
        item_type = val[3]
        effect = val[4]

        if match := re.search(r"([가-힣]+색)\s*연금약\s*\(\+(\d+)\)", item_list[0][0]) and item_type == "연금약":
            colour = match.group(2)
            stet = match.group(3)
            result = use_potion(account_row, row_values, owned_row, val, name, colour, stet)
            if not result == "NO_EFFECT":
                update_inventory(account_row, row_values, "sub", item_list)
            return result
        
        elif item_type == "요리":
            fmt = '%m-%d %H:%M:%S'
            current_datetime = datetime.now(KST).strftime(fmt)
            members.update_cell(account_row, define_columns["members"]["FOOD"], current_datetime)
            stet = re.findall(r'\[(.*?)\]', effect)[0]
            members.update_cell(account_row, define_columns["members"]["MHPA"], stet)
            
            update_inventory(account_row, row_values, "sub", item_list)
            val[6] = True
            val[7] = name
            craft_result.update([val], f"A{owned_row+1}:H{owned_row+1}")
            return f"{item_list[0][0]} 의 효과가 발동했습니다.\n「{effect}」 효과를 받습니다."
            
        elif item_type in ["방어구", "무기"]:
            update_inventory(account_row, row_values, row_values, "sub", item_list)
            val[6] = True
            val[7] = name
            craft_result.update([val], f"A{owned_row+1}:H{owned_row+1}")
            return f"{item_list[0][0]} 의 효과가 발동했습니다.\n「{effect}」 효과를 받습니다."
        else:
            update_inventory(account_row, row_values, row_values, "sub", item_list)
            val[6] = True
            val[7] = name
            craft_result.update([val], f"A{owned_row+1}:H{owned_row+1}")
            
    
def handover_item(from_user_account, user_name, to_who, items):
    finder1 = members.find(from_user_account, in_column=define_columns["members"]["CHRID"], case_sensitive=True)
    if not finder1:
        return "NONE_FROM"
    
    finder2 = members.find(to_who, in_column=define_columns["members"]["CHRID"], case_sensitive=True)
    if not finder2:
        return "NONE_TO"
    
    from_account_row = finder1.row
    to_account_row = finder2.row
    
    from_row_values = members.row_values(from_account_row)
    to_row_values = members.row_values(to_account_row)
    
    from_user_inventory = user_inv(from_row_values)
    
    handover_item_list = split_item_list(items)

    item_list = get_item_list("전체","전체")
    
    # 인벤토리에 존재 여부
    if not is_enough(from_user_inventory, handover_item_list):
        return "NOT_ENOUGH"
    
    in_list = []
    in_craft = []
    focs = []
    # 일반템 확인
    for item in handover_item_list:
        if item[0] in item_list:
            in_list.append(item)
        else:
            in_craft.append(item)

    # 제작템이 존재한다면 확인
    if len(in_craft)>0:
        data = craft_result.get_all_values()
        owner_col_values       = [row[1] for row in data[1:]]
        item_name_col_values   = [row[2] for row in data[1:]]
        item_used_col_values   = [row[6] for row in data[1:]]
        
        for item_name, count in in_craft:
            matched_idxs = []
            for idx, val in enumerate(owner_col_values, start=1):
                if val.strip() == user_name and item_name_col_values[idx-1] == item_name and item_used_col_values[idx-1] == "FALSE":
                    matched_idxs.append(idx)
            if len(matched_idxs) >= count:
                focs.extend(matched_idxs[:count])
            else:
                print(f"Error occur at : {user_name}, {item_name}")
                return "SOMETHING_WRONG"

    in_list.extend(in_craft)
    
    try:
        update_inventory(from_account_row, from_row_values, "sub", in_list)
    except:
        return "SUBMISSION_ERROR"
    if len(focs)>0:
        try:
            for owned_row in focs:
                craft_result.update_cell(owned_row+1, define_columns["craft_result"]["OWNER"], to_who)
        except:
            return "CHOWN_ERROR"
    try:
        update_inventory(to_account_row, to_row_values, "add", in_list)
    except:
        return "ADD_ERROR"
    

def change_item(user_account, items):
    finder = members.find(user_account, in_column=define_columns["members"]["CHRID"], case_sensitive=True)
    if not finder:
        return "NONE"
    
    account_row = finder.row
    row_values = members.row_values(account_row)
    user_inventory = user_inv(row_values)
    
    item_list = split_item_list(items)
    
    shop_list = dict(get_item_list("전체","구매"))
    
    total = 0
    for item, count in item_list:
        print(item, count)
        if item not in list(shop_list.keys()):
            return "CANT_BUY"
        else:
            if int(shop_list[item]) <=10:
                total += int(count)
            else:
                return "TOO_MUCH"
        
    # 인벤토리에 존재 여부
    if not is_enough(user_inventory, [("상점 교환권",total)]):
        return "NOT_ENOUGH"
    
    
    update_inventory(account_row, row_values, "sub", [("상점 교환권",total)])
    update_inventory(account_row, row_values, "add", item_list)