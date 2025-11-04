#!/usr/bin/python3
# -*- coding: utf-8 -*-

from mastodon import Mastodon
from mastodon.streaming import StreamListener
from dotenv import load_dotenv
from datetime import datetime
from gspread.exceptions import APIError
import os
import re
from modules.text_utils import filterText, ennunyiga, ullul, yiga, wagwa, ennun
from modules.game_logic.DailyDuty import play_duty, check_duty
from modules.game_logic.Attendance import checkAttendance
from modules.game_logic.KeywordInvestigate import investigate
from modules.game_logic.Stetup import stet_up
import traceback
import time

# 환경변수 로드
load_dotenv()

# 주의사항
# 마스토돈 API 사용 제한: 5분/300회
# 구글스프레드 API 사용 제한: 1분/300회
# 봇 세팅
try:
    mastodon = Mastodon(
        client_id       = os.getenv("STORY_CLIENT_ID"),
        client_secret   = os.getenv("STORY_CLIENT_SECRET"),
        access_token    = os.getenv("STORY_ACCESS_TOKEN"),
        api_base_url    = os.getenv("API_BASE_URL")
            )
    # print('auth success')
except Exception as e:
    print('auth fail')
    print(e)

try:
    me = mastodon.account_verify_credentials()
except Exception as e:
    print("API 인증 실패:", e)

print("bot initialized")


# 이벤트 리스너
class StoryListener(StreamListener):
    def on_notification(self, notification):
        try:
            if notification['type'] == "mention":
                user_text = filterText(notification['status']['content'])
                user_account = notification['status']['account']["username"]
                if user_account in ["story","doh_dol","shop"]: return
                print(f"[INPUT ] {user_account} : {user_text}")
                # 키워드가 [ ]로 감싸져 있으면 추출
                if match := re.search(r'\[(.*?)\]', user_text):
                    user_text = match.group(1)

                    # 출석
                    # 키워드 형식: [출석]
                    if user_text == "출석":
                        user_account = notification['status']['account']["username"]
                        
                        try:
                            result = checkAttendance(user_account)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            return
                            
                        if result == 'NONE':
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result == 'OVERWRITE':
                            mastodon.status_reply(notification['status'], "오늘 이미 출석을 했습니다.", visibility='unlisted')
                        elif result == 'CRAFTER_GATHERER':
                            mastodon.status_reply(notification['status'], "오늘은 [일일의뢰/납품], [일일의뢰/조달] 이 가능합니다.", visibility='unlisted')
                        elif result == 'FIGHTER':
                            todays_duty = check_duty()
                            if len(todays_duty) !=0:
                                _yiga = yiga(todays_duty[-1].strip('[]').split('/')[-1])
                                mastodon.status_reply(notification['status'], f"오늘은 {', '.join(todays_duty)} {_yiga} 가능합니다.", visibility='unlisted')
                            else:
                                mastodon.status_reply(notification['status'], f"오늘은 수행 가능한 일일의뢰가 없습니다.", visibility='unlisted')
                            
                    # 키워드 형식: [일일의뢰/ㅇㅇ]
                    elif user_text.startswith("일일의뢰/"):
                        pattern = r'^[^/]+/[^/]+$'
                        if not re.match(pattern, user_text):
                            mastodon.status_reply(notification['status'], "일일의뢰 커맨드 형식이 올바르지 않습니다.", visibility='unlisted')
                            return
                            
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        duty = user_text.split("/", 1)[1]
                        
                        try:
                            result = play_duty(user_account, duty)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            
                        if result == 'NONE':
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result == "ATTENDANCE_FIRST":
                            mastodon.status_reply(notification['status'], "[출석]을 먼저 진행해주세요.", visibility='unlisted')
                        elif result == "DUTY_ALREADY_DONE":
                            mastodon.status_reply(notification['status'], "오늘은 일일의뢰를 이미 진행했습니다.", visibility='unlisted')
                        elif result == "DUTY_NOT_AVAILABLE":
                            mastodon.status_reply(notification['status'], "오늘 수행 불가능한 의뢰입니다.", visibility='unlisted')
                        elif result == "JOB_MISSMATCH":
                            mastodon.status_reply(notification['status'], "해당 직업으로는 수행 불가능한 의뢰입니다.", visibility='unlisted')
                        else:
                            result = ennunyiga(name=user_name,text=result,name_type="user")
                            mastodon.status_reply(notification['status'], f"{result}", visibility='unlisted')
                            
                    elif user_text.startswith("조사/"):
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        search_keyword = user_text.split("/", 1)[1]
                        
                        try:
                            result = investigate(user_account, search_keyword)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            
                        if result == 'NONE':
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        else:
                            result = ennunyiga(user_name, result, "user")
                            mastodon.status_reply(notification['status'], f"{result}", visibility='unlisted')

                    # 키워드 형식: [강화/ㅇㅇ]
                    elif user_text.startswith("강화/"):
                        pattern = r'^[^/]+/[^/]+$'
                        if not re.match(pattern, user_text):
                            mastodon.status_reply(notification['status'], "강화 커맨드 형식이 올바르지 않습니다.", visibility='unlisted')
                            
                        user_account = notification['status']['account']["username"]
                        keyword = user_text.split("/", 1)[1]
                        
                        try:
                            result = stet_up(user_account, keyword)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            
                        if result == 'NONE':
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result == "NOT_ENOUGH_SP":
                            mastodon.status_reply(notification['status'], "SP가 부족합니다", visibility='unlisted')
                        elif result == "ALREADY_UP":
                            mastodon.status_reply(notification['status'], "강화 최대치에 도달했습니다.", visibility='unlisted')
                        elif result == "STAT_NONE":
                            mastodon.status_reply(notification['status'], "강화할 수 없는 능력치입니다.", visibility='unlisted')
                        elif result == "KEYWORD_ERROR":
                            mastodon.status_reply(notification['status'], "키워드가 올바르지 않습니다.", visibility='unlisted')
                        elif result == "SUCCESS":
                            keyword_A = ullul(keyword)
                            mastodon.status_reply(notification['status'], f"'{keyword}'{keyword_A} 성공적으로 강화했습니다.", visibility='unlisted')

                    else:
                        mastodon.status_reply(notification['status'], "키워드 형식이 올바르지 않습니다.", visibility='unlisted')
                        print("형식이 올바르지 아니함")
        except Exception as e:
            print("on_notification error:", e)
            traceback.print_exc()
            # 예외 발생 시 스트림이 죽지 않도록 내부에서 무시(원하면 알림 전송 등 추가)
            try:
                mastodon.status_reply(notification.get('status', {}), "내부 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.", visibility='unlisted')
            except Exception:
                pass   
            
    def handle_heartbeat(self):
        return super().handle_heartbeat()


# 메인함수
def main():
    while True:
        try:
            mastodon.stream_user(StoryListener())
        except Exception as e:
            print("stream error:", e)
            traceback.print_exc()
            time.sleep(5)
# 실행
if __name__ == '__main__':
    main()
