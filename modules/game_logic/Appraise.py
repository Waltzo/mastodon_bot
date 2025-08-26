#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import Counter
import random
from modules.text_utils import ennun, ullul
from modules.game_logic.Gathering import get_item_list
from modules.game_logic.update_inv import update_inventory
from modules.spreadsheet_utils import members
from worksheet_columns import define_columns

def Appraise(user_account, user_name):
    """
        ## API 요청 4회
            읽기: 3회
            쓰기: 2회
    """
    # API 요청 총 5회
    finder = members.find(user_account, in_column=define_columns["members"]["CHRID"], case_sensitive=True)  # [API +1] 멤버 시트에서 계정 찾기
    if not finder:
        return "NONE"
    account_row = finder.row
    row_values = members.row_values(account_row)  # [API +1] 멤버 시트에서 행 전체 읽기
    WINS_idx = define_columns["members"]["WINS"] - 1
    wins = int(row_values[WINS_idx] if len(row_values) > WINS_idx else 0)
    
    if wins < 1:
        return "NOT_ENOUGH_WINS"
    else:
        wins -= 1
        members.update_cell(account_row, define_columns["members"]["WINS"], wins)  # [API +1] 멤버 시트에서 승수 차감
        random_number = random.randint(1, 3)
        if random_number == 1:
            user_name = f"'{user_name}'{ennun(user_name)}"
            item_list = get_item_list("일반재료","채집")  # [API +1] 아이템 시트에서 일반재료 목록 조회
            item = random.choice(item_list)
            update_inventory(account_row, row_values, "add", [(item,1)])  # [API +1] 멤버 시트 인벤토리 추가
            item = f"'{item}'{ullul(item)}"
            return f"마물에게서 얻은 전리품의 겉면을 덮고 있는 흙과 먼지를 털어내자 반짝이는 것이 보입니다. {user_name} {item} 획득했습니다."
        elif random_number == 2:
            user_name += ennun(user_name)
            item_list = get_item_list("연금재","채집")  # [API +1] 아이템 시트에서 연금재 목록 조회
            item = random.choice(item_list)
            update_inventory(account_row, row_values, "add", [(item,1)])  # [API +1] 멤버 시트 인벤토리 추가
            item = f"'{item}'{ullul(item)}"
            return f"마물에게서 얻은 전리품을 잘 살펴보자, 잘 가공하면 연금약의 재료로 쓸 수 있을 것 같습니다. {user_name} {item} 획득했습니다."
        else:
            user_name += ennun(user_name)
            item_list = get_item_list("식재료","채집")  # [API +1] 아이템 시트에서 식재료 목록 조회
            item = random.choice(item_list)
            update_inventory(account_row, row_values, "add", [(item,1)])  # [API +1] 멤버 시트 인벤토리 추가
            item = f"'{item}'{ullul(item)}"
            return f"마물에게서 얻은 전리품의 독성을 잘 제거하면 꽤 괜찮은 식재료가 될 것 같습니다. {user_name} {item} 획득했습니다."