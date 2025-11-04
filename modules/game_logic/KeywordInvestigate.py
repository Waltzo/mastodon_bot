#!/usr/bin/python3
# -*- coding: utf-8 -*-
from modules.spreadsheet_utils import members, auto_invest
from worksheet_columns import define_columns

def investigate(account,keyword):
    """
        ## API 요청
            읽기: 3회
            쓰기: 0회
    """
    finder = members.find(account, in_column=define_columns["members"]["CHRID"], case_sensitive=True) # API 요청 1회
    if not finder:
        return "NONE"
    
    finder = auto_invest.find(keyword, in_column=define_columns["auto_invest"]["KEYWORD"], case_sensitive=True)  # API 요청 1회
    if finder:
        keyword_row = finder.row
    else:
        return "존재하지 않는 조사 키워드입니다."
    return f"[{keyword}] " + auto_invest.cell(keyword_row, define_columns["auto_invest"]["DESCRIPTION"]).value  # API 요청 1회
