#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import Counter
from modules.spreadsheet_utils import members, craft_result
from worksheet_columns import define_columns
from modules.game_logic.tools import tuple2str, str2tuple, is_enough, user_inv

def find_owner_col(name, item_name):
    """
        ## 사용법
            디스플레이네임과 아이템네임 입력시 최상단부터 아이템 소유자와 이름이 동일한 제작템에 대한 전체 정보 출력
        ## API 요청
            읽기: 4회
            쓰기: 0회
    """
    data = craft_result.get_all_values()
    for idx, val in enumerate(data[1:], start=1): 
        if val[1].strip() == name and val[2] == item_name and val[6] == "FALSE":
            return idx, val
    return "NO_OWNED_ITEM"  # 없으면

    
def update_inventory(account_row, row_values, method, item: list):
    """
        ## API 요청
            읽기: 0회
            쓰기: 1회
    """
    row_values = members.row_values(account_row)
    user_inventory = user_inv(row_values)
    
    counter1 = Counter(dict(user_inventory))
    counter2 = Counter(dict(item))

    if method == "add":
        merged_counter = counter1 + counter2
        merged_inventory = list(merged_counter.items())
    elif method == "sub" and is_enough(user_inventory, item):
        merged_counter = counter1 - counter2
        merged_inventory = list(merged_counter.items())
    elif method == "sub" and not is_enough(user_inventory, item):
        return "NOT_ENOUGH"
    merged_inventory = str(tuple2str(merged_inventory))
    members.update_cell(account_row, define_columns["members"]["ITEM"], merged_inventory)   # API 쓰기 1회
    