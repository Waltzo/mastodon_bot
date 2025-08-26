
from modules.spreadsheet_utils import members
from modules.game_logic.tools import colnum_to_alpha, user_inv, is_enough
from modules.game_logic.update_inv import update_inventory
from worksheet_columns import define_columns
from datetime import datetime, timezone, timedelta
import random
import ast
import re
KST = timezone(timedelta(hours=9))

def lottery(account, money=None, retry=False):
    """
        도박
        ## 확률정보 (기본값)
            -5배 5% / -2배 15% / -1배 30% / +1배 30% / +2배 15% / +5배 5%
        ## API 요청 4회
            읽기: 2회
            쓰기: 2회
    """
    
    try:
        money = int(re.sub(r'[^0-9]', '', money))
    except:
        money = None 
        
    if not money and not retry:
        return "INSERT_MONEY"
    
    current_datetime = datetime.now(KST).strftime('%Y-%m-%d')
    
    finder = members.find(account, in_column=define_columns["members"]["CHRID"], case_sensitive=True) ## API 요청 1회
    if not finder:
        return "NONE"

    account_row = finder.row
    row_values = members.row_values(account_row) ## API 요청 1회
    
    user_money_col = define_columns["members"]["GIL"]
    user_luck_col = define_columns["members"]["LUK"]
    user_tdbg_col = define_columns["members"]["TDGB"]
    user_tdbgr_col = define_columns["members"]["TDGB_R"]
    
    user_money = int(row_values[user_money_col-1])
    user_luck = int(row_values[user_luck_col-1])
    user_tdbg = row_values[user_tdbg_col-1]
    
    if retry:
        if not user_tdbg == current_datetime:
            return "NO_RETRY"
        user_invenroty = user_inv(row_values)
        if not is_enough(user_invenroty,[("도박 재굴림권",1)]):
            return "NO_RETRY_ITEM"
        user_tdbgr = ast.literal_eval(row_values[user_tdbgr_col-1])
        money = int(user_tdbgr[0])
        # user_tdbgr = (직전 건 돈, 직전 결과)
    
    if not retry and money > user_money:
        return "NOT_ENOUGH"
    if not retry and user_tdbg == current_datetime:
        return "ALREADY_DONE"

    rand = random.randint(1,100)
    luck_cal = user_luck - 3

    if rand + luck_cal <= 5:
        result = (1, -5 * money) if not retry else (1, -5 * money, money)
    elif rand + luck_cal <= 20:
        result = (2, -2 * money) if not retry else (2, -2 * money, money)
    elif rand + luck_cal <= 50:
        result = (3, -1 * money) if not retry else (3, -1 * money, money)
    elif rand + luck_cal <= 80:
        result = (4, +0 * money) if not retry else (4, +0 * money, money)
    elif rand + luck_cal <= 95:
        result = (5, +1 * money) if not retry else (5, +1 * money, money)
    else:
        result = (6, +4 * money) if not retry else (6, +4 * money, money)
    
    ## API 요청 2회
    if retry:
        update_inventory(account_row, row_values, "sub", [("도박 재굴림권",1)])
        members.update_cell(account_row, user_money_col, max(0, user_money + result[1] - user_tdbgr[1]))
        members.update([[current_datetime, str((money, result[1]))]], f"{colnum_to_alpha(user_tdbg_col)}{account_row}:{colnum_to_alpha(user_tdbgr_col)}{account_row}")
        return result
    else:
        members.update_cell(account_row, user_money_col, max(0, user_money + result[1]))
        members.update([[current_datetime, str((money, result[1]))]], f"{colnum_to_alpha(user_tdbg_col)}{account_row}:{colnum_to_alpha(user_tdbgr_col)}{account_row}")
        return result
        

def slot_machine(account, money):
    try:
        money = int(re.sub(r'[^0-9]', '', money))
    except:
        money = None 
        
    if not money:
        return "INSERT_MONEY"
    
    current_datetime = datetime.now(KST).strftime('%Y-%m-%d')
    # 화요일 제한
    # if datetime.now(KST).weekday() != 1:
    #     return "NOT_TUESDAY"

    finder = members.find(account, in_column=define_columns["members"]["CHRID"], case_sensitive=True) ## API 요청 1회
    if not finder:
        return "NONE"
    
    account_row = finder.row
    row_values = members.row_values(account_row) ## API 요청 1회
    
    user_money_col = define_columns["members"]["GIL"]
    user_TDSM_col = define_columns["members"]["TDSM"]
    
    user_money = int(row_values[user_money_col-1])
    user_TDSM = row_values[user_TDSM_col-1]
    
    if money > user_money:
        return "NOT_ENOUGH"
    if user_TDSM == current_datetime:
        return "ALREADY_DONE"
    
    slots = [random.randint(0, 9) for _ in range(3)]
    if slots[0] == slots[1] == slots[2]:
        if slots[0] == 6:
            result = ("666", -10*money, f"| {slots[0]} | {slots[1]} | {slots[2]} |")
        elif slots[0] == 7:
            result = ("777", 777, f"| {slots[0]} | {slots[1]} | {slots[2]} |")
        else:
            result = ("333", 5*money, f"| {slots[0]} | {slots[1]} | {slots[2]} |")
    else:
        if slots[0] == slots[1] or slots[0] == slots[2] or slots[1] == slots[2]:
            result = ("222", 3*money, f"| {slots[0]} | {slots[1]} | {slots[2]} |")
        else:
            result = ("111", -1*money, f"| {slots[0]} | {slots[1]} | {slots[2]} |")
    
    members.update_cell(account_row, user_money_col, max(0, user_money + result[1]))
    members.update_cell(account_row, user_TDSM_col, current_datetime)
    return result