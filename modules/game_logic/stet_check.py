#!/usr/bin/python3
# -*- coding: utf-8 -*-
from modules.spreadsheet_utils import members
from modules.game_logic.tools import colnum_to_alpha
from worksheet_columns import define_columns
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

def Effect_check():
    """
        포션과 음식 체크. 24시간 초과시 갱신
        ## API 요청 
            2분 마다 
            2회 
            + ( 음식 24시간 초과인 유저 수 * 2 ) 
            + ( 연금약 24시간 초과인 유저 수 * 2 )
    """
    import sys
    sys.path.append('/root/waltzbot')
    
    fmt = '%m-%d %H:%M:%S'
    
    current_datetime = datetime.now(KST).strftime(fmt)

    poti_times = members.col_values(define_columns["members"]["POTI"])
    food_times = members.col_values(define_columns["members"]["FOOD"])
    
    STRA_col_alpha = colnum_to_alpha(define_columns["members"]["STRA"])
    DEXA_col_alpha = colnum_to_alpha(define_columns["members"]["DEXA"])
    
    for idx, poti_time in enumerate(poti_times, start=1):
        if idx == 1 : pass
        elif poti_time:
            dt_potion = datetime.strptime(poti_time, fmt)
            dt_current = datetime.strptime(poti_time, fmt)
            diff_seconds = (dt_current - dt_potion).total_seconds()
            if 0 <= diff_seconds < 86400:
                pass
            else:
                members.update(f'{STRA_col_alpha}{idx}:{DEXA_col_alpha}{idx}', [[0,0,0]])  # API 요청 1회
                members.update_cell(idx, define_columns["members"]["POTI"], '')  # API 요청 1회

    for idx, food_time in enumerate(food_times, start=1):
        if idx == 1 : pass
        elif food_time:
            dt_food = datetime.strptime(food_time, fmt)
            dt_current = datetime.strptime(current_datetime, fmt)
            diff_seconds = (dt_current - dt_food).total_seconds()
            if 0 <= diff_seconds < 86400:
                pass
            else:
                members.update_cell(idx, define_columns["members"]["MHPA"], 0)  # API 요청 1회
                members.update_cell(idx, define_columns["members"]["FOOD"], '')  # API 요청 1회
    return
        
if __name__ == "__main__":
    Effect_check()