#!/usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime, timezone, timedelta
from modules.game_logic.tools import job_check
from modules.spreadsheet_utils import members
from worksheet_columns import define_columns
KST = timezone(timedelta(hours=9))

def checkAttendance(account):
    finder = members.find(account, in_column=define_columns["members"]["CHRID"], case_sensitive=True)
    if not finder:
        return "NONE"
    account_row = finder.row
    row_values = members.row_values(account_row)  # 한 번에 row 전체 읽기

    count_idx = define_columns["members"]["COUNT"] - 1
    attd_idx = define_columns["members"]["ATTD"] - 1

    attendance_count = row_values[count_idx] if len(row_values) > count_idx else None
    previous_datetime = row_values[attd_idx] if len(row_values) > attd_idx else None

    current_datetime = datetime.now(KST).strftime('%Y-%m-%d')

    if previous_datetime != current_datetime:
        count = int(attendance_count) if attendance_count else 0
        members.update_cell(account_row, define_columns["members"]["COUNT"], count + 1)
        members.update_cell(account_row, define_columns["members"]["ATTD"], current_datetime)
        return job_check(row_values)
    else:
        return "OVERWRITE"