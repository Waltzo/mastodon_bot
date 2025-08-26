#!/usr/bin/python3
# -*- coding: utf-8 -*-

from modules.spreadsheet_utils import members
from worksheet_columns import define_columns

def stet_up(account, keyword):
    finder = members.find(account, in_column=define_columns["members"]["CHRID"], case_sensitive=True)
    if not finder:
        return "NONE"
    row = finder.row
    row_values = members.row_values(row)
    asp = int(row_values[define_columns["members"]["ASP"] - 1] or 0)
    usp = int(row_values[define_columns["members"]["USP"] - 1] or 0)
    ab1 = row_values[define_columns["members"]["AB1"] - 1] if len(row_values) >= define_columns["members"]["AB1"] else ''
    ab2 = row_values[define_columns["members"]["AB2"] - 1] if len(row_values) >= define_columns["members"]["AB2"] else ''

    stat_map = {
        "이동력": define_columns["members"]["MOV"],
        "전투력": define_columns["members"]["STRD"],
        "안목": define_columns["members"]["INSD"],
        "손재주": define_columns["members"]["DEXD"],
        "운": define_columns["members"]["LUK"],
        "의지": define_columns["members"]["DET"]
    }

    if keyword in stat_map:
        if asp < 2:
            return "NOT_ENOUGH_SP"
        col = stat_map[keyword]
        stat = int(members.cell(row, col).value or 0)
        if stat < 1:
            return "STAT_NONE"
        if keyword == "의지" and stat == 5:
            return "ALREADY_UP"
        elif stat == 10:
            return "ALREADY_UP"
        members.update_cell(row, col, stat + 1)
        members.update_cell(row, define_columns["members"]["USP"], usp + 2)
        return "SUCCESS"

    for ab, up_col in [(ab1, define_columns["members"]["UP1"]), (ab2, define_columns["members"]["UP2"])]:
        if keyword == ab:
            if asp < 3:
                return "NOT_ENOUGH_SP"
            if members.cell(row, up_col).value == "TRUE":
                return "ALREADY_UP"
            members.update_cell(row, up_col, "TRUE")
            members.update_cell(row, define_columns["members"]["USP"], usp + 3)
            return "SUCCESS"

    return "KEYWORD_ERROR"