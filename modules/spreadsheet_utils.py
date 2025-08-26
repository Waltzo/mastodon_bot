import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_to_spreadsheet(json_path, sheet_url):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
    gc = gspread.authorize(credentials)
    return gc.open_by_url(sheet_url)

def connect_to_spreadsheet_from_env():
    from dotenv import load_dotenv
    import os
    load_dotenv()
    return connect_to_spreadsheet(
        json_path=os.getenv("CRENDENTIAL_JSON"),
        sheet_url=os.getenv("GOOGLE_SHEET_URL")
    )

sh = connect_to_spreadsheet_from_env()

# 워크시트 선택
members         = sh.worksheet("멤버정보")
daily_duty      = sh.worksheet("일일의뢰")
auto_invest     = sh.worksheet("자동조사")
craft_result    = sh.worksheet("제작 결과")
items           = sh.worksheet("아이템 목록")