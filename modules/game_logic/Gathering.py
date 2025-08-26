#!/usr/bin/python3
# -*- coding: utf-8 -*-
from modules.spreadsheet_utils import items, members
from worksheet_columns import define_columns
from collections import Counter
from modules.game_logic.update_inv import tuple2str, update_inventory
from modules.game_logic.tools import stat_adj, colnum_to_alpha, job_check

from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))

import random

# 세부 기능 정의
def get_item_list(input_type:str = None, search_type:str = None):
    """
        ## args
            input_type: 아이템 종류 (전체, 일반재료, 식재료, 연금재)
            search_type: 검색 종류 (채집, 재료, 구매)
        ## 사용예시
            gather_list() = 전체 아이템 리스트
            gather_list("채집","구매") = 구매가능한 채집템 튜플리스트
            gather_list("일반 재료","채집") = 일반 재료 리스트
            gather_list(search_type="구매") = 구매가능 아이템 튜플리스트
        ## API 요청
            읽기: 1회
            쓰기: 0회
    """
    # API 요청 총 2~4회
    data = items.get_all_values()
    if search_type == "채집":
        column = 3
    elif search_type == "재료":
        column = 4
    elif search_type == "구매":
        column = 5
    else:
        column = None
    
    if column:
        if input_type in ["일반 재료","연금재","식재료"]:
            item_list = [(row[0],row[2]) if column==5 else row[0] for row in data[1:] if len(row) > column and row[column].upper() == "TRUE" and row[1] == input_type.strip()]
        else:
            item_list = [(row[0],row[2]) if column==5 else row[0] for row in data[1:] if len(row) > column and row[column].upper() == "TRUE"]
    else:
        item_list = [row[0] for row in data[1:]]
    
    return item_list

def gathering(account, duty):
    """
        ## API 요청 6회
            읽기: 5회
            쓰기: 1회
    """
    duty = duty.replace(" ", "").strip()
    if duty not in ["일반재료","식재료","연금재"]:
        return "INVALID_DUTY"
    
    finder = members.find(account, in_column=define_columns["members"]["CHRID"], case_sensitive=True) ## API 요청 1회
    if not finder:
        return "NONE"
    
    account_row = finder.row
    row_values = members.row_values(account_row) ## API 요청 1회

    if not job_check(row_values) == "CRAFTER_GATHERER":
        return "INVALID_JOB"
    
    tdgcc_idx = define_columns["members"]["TDGC"] - 1
    tdgcd_idx = define_columns["members"]["TDGC_DATE"] - 1

    today_gather_count = today_gather_count = int(row_values[tdgcc_idx]) if len(row_values) > tdgcc_idx and row_values[tdgcc_idx] else 0
    last_gather_datetime = row_values[tdgcd_idx] if len(row_values) > tdgcd_idx else None

    current_datetime = datetime.now(KST).strftime('%Y-%m-%d')

    if today_gather_count == 3 and last_gather_datetime == current_datetime:
        return "OVERDUTY"
    elif today_gather_count < 3 and last_gather_datetime == current_datetime:
        today_gather_count += 1
    elif last_gather_datetime != current_datetime:
        today_gather_count = 1
    
    insight_idx = define_columns["members"]["INS"] - 1
    user_insight = int(row_values[insight_idx]) if len(row_values) > tdgcd_idx else None
    item_count = min(1 + stat_adj(user_insight), 5)
    item_list = get_item_list(duty,"채집")  ## API 요청 1회
    selected_items = random.choices(item_list, k=item_count)
    item_tuples = list(Counter(selected_items).items())
    update_inventory(account_row, row_values, "add", item_tuples) ## API 요청 2회

    TDGC_col_alpha = colnum_to_alpha(define_columns["members"]["TDGC"])
    TDGC_DATE_col_alpha = colnum_to_alpha(define_columns["members"]["TDGC_DATE"])
    
    members.update(f'{TDGC_col_alpha}{account_row}:{TDGC_DATE_col_alpha}{account_row}', [[today_gather_count,current_datetime]]) ## API 요청 1회
    
    return tuple2str(item_tuples)