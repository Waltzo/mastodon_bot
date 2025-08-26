#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))

from modules.game_logic.tools import job_check

from modules.spreadsheet_utils import members, daily_duty
from worksheet_columns import define_columns

def duty_helper():
    random_number = random.randint(1, 10)
    if random_number <= 8:
        return "GOOD"
    else:
        return "GREAT"

def check_duty():
    keyword_col  = daily_duty.col_values(define_columns["daily_duty"]["WORD"]) # SH API 1회
    used_col     = daily_duty.col_values(define_columns["daily_duty"]["USED"]) # SH API 1회
    todays_duty  = []
    for idx in range(1, len(keyword_col)):
        gather_val = str(used_col[idx]).strip().upper() if idx < len(used_col) else ''
        if gather_val == "TRUE":
            todays_duty.append(f"[{keyword_col[idx]}]")
    return todays_duty

def get_result_and_update(account_row, duty_row, result, money, exp):
    members.update_cell(account_row, define_columns["members"]["TDDT"], datetime.now(KST).strftime('%Y-%m-%d'))  # SH API 1회
    if result == "GOOD":
        money += 2
        exp += 5
        members.update_cell(account_row, define_columns["members"]["GIL"], money)  # SH API 1회
        members.update_cell(account_row, define_columns["members"]["EXP"], exp)    # SH API 1회
        return daily_duty.cell(duty_row, define_columns["daily_duty"]["END1"]).value  # SH API 1회
    else:
        money += 5
        exp += 5
        members.update_cell(account_row, define_columns["members"]["GIL"], money)  # SH API 1회
        members.update_cell(account_row, define_columns["members"]["EXP"], exp)    # SH API 1회
        return daily_duty.cell(duty_row, define_columns["daily_duty"]["END2"]).value  # SH API 1회

def play_duty(account, duty): 
    finder = members.find(account, in_column=define_columns["members"]["CHRID"], case_sensitive=True)
    if not finder:
        return "NONE"
    
    account_row = finder.row
    row_values = members.row_values(account_row)
    current_datetime = datetime.now(KST).strftime('%Y-%m-%d')
    attendence_datetime = row_values[define_columns["members"]["ATTD"] - 1]

    if attendence_datetime and attendence_datetime.strip():
        attend_date = datetime.strptime(attendence_datetime, "%Y-%m-%d").date()
    else:
        attend_date = None
    current_date = datetime.strptime(current_datetime, "%Y-%m-%d").date()

    if attend_date is None or attend_date != current_date:
        return "ATTENDANCE_FIRST"

    tddt_idx = define_columns["members"]["TDDT"] - 1
    last_duty = row_values[tddt_idx] if len(row_values) > tddt_idx else ''
    if last_duty:
        if datetime.strptime(last_duty, "%Y-%m-%d").date() == datetime.strptime(current_datetime, "%Y-%m-%d").date():
            return "DUTY_ALREADY_DONE"

    job = job_check(row_values) 
    result = duty_helper()
    money_str = row_values[define_columns["members"]["GIL"] - 1] if len(row_values) > define_columns["members"]["GIL"] - 1 else ''
    money = int(money_str) if money_str.isdigit() else 0
    exp_str = row_values[define_columns["members"]["EXP"] - 1] if len(row_values) > define_columns["members"]["EXP"] - 1 else ''
    exp = int(exp_str) if exp_str.isdigit() else 0

    if duty in ["납품", "조달"] and job == "CRAFTER_GATHERER":
        duty_row = 2 if duty == "납품" else 3
        return get_result_and_update(account_row, duty_row, result, money, exp)
    
    elif duty in ["조사", "토벌", "봉인"] and job == "FIGHTER":
        duty_name = f"[일일의뢰/{duty}]"
        if duty_name not in check_duty():
            return "DUTY_NOT_AVAILABLE"
        duty_row = {"조사": 4, "토벌": 5, "봉인": 6}[duty]
        return get_result_and_update(account_row, duty_row, result, money, exp)
    else:
        return "JOB_MISSMATCH"