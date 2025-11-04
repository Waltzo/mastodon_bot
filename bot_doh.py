#!/usr/bin/python3
# -*- coding: utf-8 -*-

from mastodon import Mastodon
from mastodon.streaming import StreamListener
from dotenv import load_dotenv
from datetime import datetime
from gspread.exceptions import APIError
import os
import re
import random
from collections import Counter
from worksheet_columns import define_columns
from modules.spreadsheet_utils import connect_to_spreadsheet_from_env
from modules.text_utils import filterText, ennunyiga, ullul, yiga, wagwa, ennun
from modules.game_logic.Gathering import get_item_list, gathering
from modules.game_logic.Appraise import Appraise
from modules.game_logic.Crafting import crafting, job_done
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
        client_id       = os.getenv("LIFE_CLIENT_ID"),
        client_secret   = os.getenv("LIFE_CLIENT_SECRET"),
        access_token    = os.getenv("LIFE_ACCESS_TOKEN"),
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


# 고유 로직 추가
class LifeListener(StreamListener):
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

                    if user_text == "재료감정":
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        
                        try:
                            result = Appraise(user_account, user_name)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            
                        if result == "NONE":
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result == "NOT_ENOUGH_WINS":
                            mastodon.status_reply(notification['status'], "전리품이 부족합니다.", visibility='unlisted')
                        else:
                            mastodon.status_reply(notification['status'], result, visibility='unlisted')
                    
                    elif user_text.startswith("채집/"):
                        pattern = r'^[^/]+/[^/]+$'
                        if not re.match(pattern, user_text):
                            mastodon.status_reply(notification['status'], "채집 커맨드 형식이 올바르지 않습니다.", visibility='unlisted')
                            return
                        # 채집/종류
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        duty = user_text.split("/", 1)[1]
                        
                        try:
                            result = gathering(user_account, duty)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            return
                            
                        if result == "NONE":
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        if result == "INVALID_JOB":
                            mastodon.status_reply(notification['status'], "채집이 불가능한 직업입니다.", visibility='unlisted')
                        elif result == "OVERDUTY":
                            mastodon.status_reply(notification['status'], "금일 채집 가능 횟수를 모두 소모하였습니다.", visibility='unlisted')
                        elif result == "INVALID_DUTY":
                            mastodon.status_reply(notification['status'], "유효하지 않은 채집 종류입니다.", visibility='unlisted')
                        else:
                            josa1 = yiga(user_name)
                            mastodon.status_reply(notification['status'], f"'{user_name}'{josa1} {result}를 획득합니다.", visibility='unlisted')
                        return
                    
                    elif user_text.startswith("제작/"):
                        pattern = r'^[^/]+/[^/]+/[^/]+$'
                        if not re.match(pattern, user_text):
                            mastodon.status_reply(notification['status'], "제작 커맨드 형식이 올바르지 않습니다.", visibility='unlisted')
                            return
                        # 제작/종류/재료명
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        item_type = user_text.split("/", 2)[1].strip()
                        ingr_list = user_text.split("/", 2)[2].strip()
                        
                        try:
                            result = crafting(user_account, user_name, item_type, ingr_list)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            
                        if item_type == "무기":
                            ingr_type = "일반재료"
                            desc = "재료를 능숙한 손길로 갈고 다듬어 예리한 무기를 만들어 냅니다."
                            
                        elif item_type == "방어구":
                            ingr_type = "일반재료"
                            desc = "재료를 잘 다듬고 이어붙이더니, 튼튼한 방어구를 완성합니다."
                            
                        elif item_type == "연금약":
                            ingr_type = "연금재"
                            desc1 = "재료를 약연에 잘 갈아 증류하더니, "
                            desc2 = "의 연금약을 완성합니다."
                            
                        elif item_type == "음식":
                            ingr_type = "식재료"
                            desc = "재료를 잘 손질하여 요리하기 시작하더니, 먹음직스러운 음식을 완성합니다."

                        if result == "NONE":
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result == "INVALID_JOB":
                            mastodon.status_reply(notification['status'], "제작이 불가능한 직업입니다.", visibility='unlisted')
                        elif result == "NAME_FIRST":
                            mastodon.status_reply(notification['status'], "이전 제작 물품이 존재합니다. 먼저 [완성/(아이템이름)]을 통해 이전 제작을 완성해주세요.", visibility='unlisted')
                        elif result == "INVALID_TYPE":
                            mastodon.status_reply(notification['status'], "유효하지 않은 제작 종류입니다.", visibility='unlisted')
                        elif result == "INVALID_ITEM_FORMAT":
                            mastodon.status_reply(notification['status'], "재료 형식이 올바르지 않습니다.", visibility='unlisted')
                        elif result == "NOT_ENOUGH_1":
                            mastodon.status_reply(notification['status'], f"투입한 재료의 총 개수가 5개 미만입니다.", visibility='unlisted')
                        elif result == "NOT_ENOUGH_2":
                            mastodon.status_reply(notification['status'], "소지품에 재료가 부족합니다.", visibility='unlisted')
                        elif result == "NOT_ENOUGH_3":
                            mastodon.status_reply(notification['status'], f"투입한 '{ingr_type}'의 개수가 부족합니다.", visibility='unlisted')
                        else:
                            josa1 = yiga(user_name)
                            josa2 = ennun(user_name)
                            if item_type in  ["무기", "방어구"]:
                                mastodon.status_reply(notification['status'], f"'{user_name}'{josa1} {desc}\n\n'{user_name}'{josa2}「{result}」 효과가 있는 {item_type}를 제작했습니다.\n아래로 [완성/({item_type}의 이름)]을 입력해 {item_type}를 등록해주십시오.", visibility='unlisted')
                                
                            elif item_type == "연금약":
                                mastodon.status_reply(notification['status'], f"'{user_name}'{josa1} {desc1}「{result[2]}」{desc2}\n\n'{user_name}'{josa2} 「{result[0]}」 효과가 있는 {item_type}을 {result[1]}개 제작했습니다. \n인벤토리에 {result[2]} 연금약 {result[1]}개 가 등록됩니다.", visibility='unlisted')
                                
                            elif item_type == "음식":
                                mastodon.status_reply(notification['status'], f"'{user_name}'{josa1} {desc} \n\n'{user_name}'{josa2} 「{result[0]}」 효과가 있는 {item_type}을 {result[1]}개 제작했습니다. \n아래로 [완성/(요리의 이름)]을 입력해 요리를 등록해주십시오.", visibility='unlisted')
                                
                    elif user_text.startswith("완성/"):
                        pattern = r'^[^/]+/[^/]+$'
                        if not re.match(pattern, user_text):
                            mastodon.status_reply(notification['status'], "완성 커맨드 형식이 올바르지 않습니다.", visibility='unlisted')
                            return
                            
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        item_name = user_text.split("/", 1)[1].strip()
                        
                        try:
                            result = job_done(user_account, user_name, item_name)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            
                        if result == "NONE":
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                            
                        elif result == "NO_ITEM":
                            mastodon.status_reply(notification['status'], "완성 가능한 아이템이 존재하지 않습니다.", visibility='unlisted')
                        
                        elif result == "NAME_TAKEN":
                            mastodon.status_reply(notification['status'], "사용되지 않은 아이템 중 동일한 이름의 아이템이 존재합니다.", visibility='unlisted')
                            
                        elif result == "CANNOT_USE":
                            mastodon.status_reply(notification['status'], "사용할 수 없는 이름입니다.", visibility='unlisted')
                            
                        else:
                            CLEANER = re.compile(r'[^\w\s]')
                            item_name = filterText(item_name, CLEANER)
                            mastodon.status_reply(notification['status'], f"아이템 이름을 '{filterText(item_name)}'으로 확정했습니다.", visibility='unlisted')

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

def main():
    while True:
        try:
            mastodon.stream_user(LifeListener())
        except Exception as e:
            print("stream error:", e)
            traceback.print_exc()
            time.sleep(5)

if __name__ == '__main__':
    main()
