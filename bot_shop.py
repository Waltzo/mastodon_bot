#!/usr/bin/python3
# -*- coding: utf-8 -*-

from mastodon import Mastodon
from mastodon.streaming import StreamListener
from dotenv import load_dotenv
import os
import re
from gspread.exceptions import APIError
from modules.spreadsheet_utils import connect_to_spreadsheet_from_env
from modules.text_utils import filterText, ennunyiga, ullul, yiga, wagwa, ennun
from modules.game_logic.Store import buy_item, use_item, handover_item, change_item
from modules.game_logic.Roulette import lottery, slot_machine
import traceback
import time

# 환경변수 로드
load_dotenv()

# 주의사항
try:
    mastodon = Mastodon(
        client_id       = os.getenv("SHOP_CLIENT_ID"),
        client_secret   = os.getenv("SHOP_CLIENT_SECRET"),
        access_token    = os.getenv("SHOP_ACCESS_TOKEN"),
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

# Google Spreadsheet 연결
sh = connect_to_spreadsheet_from_env()

# 고유 로직 추가
class ShopListener(StreamListener):
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

                    if user_text.startswith("구매/"):
                        pattern = r'^[^/]+/[^/]+$'
                        if not re.match(pattern, user_text):
                            mastodon.status_reply(notification['status'], "구매 커맨드 형식이 올바르지 않습니다.", visibility='unlisted')
                            return
                        # [구매/아이템이름]
                        user_account = notification['status']['account']["username"]
                        keyword = user_text.split("/", 1)[1]
                        
                        try:
                            result = buy_item(user_account, keyword)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            return
                            
                        if result == "NONE":
                            print(result)
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result == "NO_ITEM":
                            print(result)
                            mastodon.status_reply(notification['status'], "구매 가능한 아이템이 존재하지 않습니다.", visibility='unlisted')
                        elif result == "NOT_ENOUGH":
                            print(result)
                            mastodon.status_reply(notification['status'], "소지금이 부족합니다.", visibility='unlisted')
                        else:
                            yes_str , no_str = result
                            print("yes: ", yes_str)
                            print("no: ", no_str)
                            mastodon.status_reply(notification['status'], f"아이템 구매를 완료했습니다. 다음에도 방문 부탁드립니다.\n\n구매 성공: {yes_str}\n구매 실패: {no_str}", visibility='unlisted')

                    elif user_text.startswith("사용/"):
                        pattern = r'^[^/]+/[^/]+$'
                        if not re.match(pattern, user_text):
                            mastodon.status_reply(notification['status'], "사용 커맨드 형식이 올바르지 않습니다.", visibility='unlisted')
                            return
                        # [사용/아이템이름]
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        items = user_text.split("/", 1)[1]
                        
                        try:
                            result = use_item(user_account, user_name, items)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            return
                        
                        if result == "NONE":
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result == "NO_OWNED_ITEM":
                            mastodon.status_reply(notification['status'], "사용 가능한 아이템이 없습니다.", visibility='unlisted')
                        elif result == "MULTIPLE_ITEMS":
                            mastodon.status_reply(notification['status'], "한 번에 하나의 아이템만 사용할 수 있습니다.", visibility='unlisted')
                        elif result == "NOT_ENOUGH":
                            mastodon.status_reply(notification['status'], "해당 아이템이 인벤토리에 존재하지 않습니다.", visibility='unlisted')
                        elif result == "NO_EFFECT":
                            mastodon.status_reply(notification['status'], "해당 연금약을 사용할 수 없습니다.", visibility='unlisted')
                        else:
                            mastodon.status_reply(notification['status'], result, visibility='unlisted')
                    
                    elif user_text.startswith("양도/"):
                        pattern = r'^[^/]+/[^/]+@[^/]+$'
                        if not re.match(pattern, user_text):
                            mastodon.status_reply(notification['status'], "양도 커맨드 형식이 올바르지 않습니다.", visibility='unlisted')
                            return
                        # [양도/대상/아이템이름]
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        item_to = user_text.split("/", 1)[1].strip()
                        items = item_to.split("@", 1)[0].strip()
                        to_who = item_to.split("@", 1)[1].strip()
                        
                        try:
                            result = handover_item(user_account, user_name, to_who, items)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            return
                            
                        if result == "NONE_FROM" or result == "NONE_TO":
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result == "NOT_ENOUGH":
                            mastodon.status_reply(notification['status'], "해당 아이템이 인벤토리에 존재하지 않습니다.", visibility='unlisted')
                        elif result == "SOMETHING_WRONG":
                            mastodon.status_reply(notification['status'], "알 수 없는 문제가 발생했습니다. 운영자에게 문의해주세요.", visibility='unlisted')
                        elif result == "SUBMISSION_ERROR":
                            mastodon.status_reply(notification['status'], "아이템 전달 과정에 문제가 생겼습니다. 운영자에게 문의해주세요.", visibility='unlisted')
                        elif result == "CHOWN_ERROR":
                            mastodon.status_reply(notification['status'], "아이템 소유 변경 과정에 문제가 발생했습니다. 운영자에게 문의해주세요.", visibility='unlisted')
                        elif result == "ADD_ERROR":
                            mastodon.status_reply(notification['status'], "아이템 수취 과정에 문제가 생겼습니다. 운영자에게 문의해주세요.", visibility='unlisted')
                        else:
                            mastodon.status_reply(notification['status'], "아이템 양도를 완료했습니다.", visibility='unlisted')

                    elif user_text.startswith("교환/"):
                        pattern = r'^[^/]+/[^/]+$'
                        if not re.match(pattern, user_text):
                            mastodon.status_reply(notification['status'], "교환 커맨드 형식이 올바르지 않습니다.", visibility='unlisted')
                            return
                        # [교환/아이템이름]
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        items = user_text.split("/", 1)[1].strip()
                        
                        try:
                            result = change_item(user_account, items)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            
                        if result == "NONE":
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result == "CANT_BUY":
                            mastodon.status_reply(notification['status'], "구매 불가능한 아이템이 존재합니다.", visibility='unlisted')
                        elif result == "TOO_MUCH":
                            mastodon.status_reply(notification['status'], "10닢을 초과하는 아이템이 존재합니다.", visibility='unlisted')
                        elif result == "NOT_ENOUGH":
                            mastodon.status_reply(notification['status'], "티켓이 부족합니다.", visibility='unlisted')
                        else:
                            mastodon.status_reply(notification['status'], "교환이 정상적으로 완료되었습니다.", visibility='unlisted')
                            
                    elif user_text.startswith("도박/"):
                        pattern = r'^[^/]+/[^/]+$'
                        if not re.match(pattern, user_text):
                            mastodon.status_reply(notification['status'], "도박 커맨드 형식이 올바르지 않습니다.", visibility='unlisted')
                            return
                        # [도박/00 닢]
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        money = user_text.split("/", 1)[1].strip()
                        
                        try:
                            result = lottery(user_account, money)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            
                        if result =="NONE":
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result =="INSERT_MONEY":
                            mastodon.status_reply(notification['status'], "금액을 정확히 입력하세요.", visibility='unlisted')
                        elif result =="ALREADY_DONE":
                            mastodon.status_reply(notification['status'], "오늘 이미 도박을 진행했습니다.", visibility='unlisted')
                        elif result =="NOT_ENOUGH":
                            mastodon.status_reply(notification['status'], "소지금이 부족합니다.", visibility='unlisted')
                        elif result =="NOT_TUESDAY":
                            mastodon.status_reply(notification['status'], "화요일에만 도박이 가능합니다.", visibility='unlisted')
                        else:
                            lot_result, lot_money = result
                            _yiga = yiga(user_name)
                            if lot_result == 1:
                                text = f"\n{money}을 걸고 오늘의 운을 시험합니다. \n동전이 튕겨집니다.\n\n... 오늘은 운이 아주 좋지 않았나봅니다. \n{user_name}{_yiga} {abs(lot_money)}닢만큼 돈을 잃습니다."
                            elif lot_result == 2:
                                text = f"\n{money}을 걸고 오늘의 운을 시험합니다. \n동전이 튕겨집니다.\n\n... 오늘은 운이 좋지 않았나봅니다. \n{user_name}{_yiga} {abs(lot_money)}닢만큼 돈을 잃습니다."
                            elif lot_result == 3:
                                text = f"\n{money}을 걸고 오늘의 운을 시험합니다. \n동전이 튕겨집니다.\n\n... 오늘은 운이 그럭저럭인가봅니다. \n{user_name}{_yiga} {abs(lot_money)}닢만큼 돈을 잃습니다."
                            elif lot_result == 4:
                                text = f"\n{money}을 걸고 오늘의 운을 시험합니다. \n동전이 튕겨집니다.\n\n나쁘지 않은 날입니다. \n{user_name}{_yiga} 걸었던 {int(re.sub(r'[^0-9]', '', money))}닢을 다시 획득합니다."
                            elif lot_result == 5:
                                text = f"\n{money}을 걸고 오늘의 운을 시험합니다. \n동전이 튕겨집니다.\n\n운이 좋네요. \n{user_name}{_yiga} {int(re.sub(r'[^0-9]', '', money))+lot_money}닢만큼 돈을 획득합니다."
                            else:
                                text = f"\n{money}을 걸고 오늘의 운을 시험합니다. \n동전이 튕겨집니다.\n\n운수대통! \n{user_name}{_yiga} {int(re.sub(r'[^0-9]', '', money))+lot_money}닢만큼 돈을 획득합니다."
                                
                            mastodon.status_reply(notification['status'], text, visibility='unlisted')
                            
                    elif user_text == "도박재굴림":
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        
                        try:
                            result = lottery(user_account, retry=True)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            return
                            
                        if result =="NONE":
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result =="NO_RETRY":
                            mastodon.status_reply(notification['status'], "기존 도박 정보가 없어 재굴림권을 사용할 수 없습니다.", visibility='unlisted')
                        elif result =="NO_RETRY_ITEM":
                            mastodon.status_reply(notification['status'], "도박 재굴림권이 부족합니다", visibility='unlisted')
                        else:
                            lot_result, lot_money, money = result
                            _yiga = yiga(user_name)
                            if lot_result in [1,2,3]:
                                text = f"\n이전 결과를 덮어 둔 채 다시 한 번 운을 시험합니다. \n동전을 튕기고, 그대로 덮은 뒤 손을 내리면… \n\n... {user_name}{_yiga} {abs(lot_money)}닢만큼 돈을 잃습니다."
                            elif lot_result == 4:
                                text = f"\n이전 결과를 덮어 둔 채 다시 한 번 운을 시험합니다. \n동전을 튕기고, 그대로 덮은 뒤 손을 내리면… \n\n... {user_name}{_yiga} 걸었던 {money}닢을 다시 획득합니다."
                            elif lot_result in [5,6]:
                                text = f"\n이전 결과를 덮어 둔 채 다시 한 번 운을 시험합니다. \n동전을 튕기고, 그대로 덮은 뒤 손을 내리면… \n\n{user_name}{_yiga} {money+lot_money}닢만큼 돈을 획득합니다."
                            mastodon.status_reply(notification['status'], text, visibility='unlisted')

                    elif user_text.startswith("슬롯머신/"):
                        pattern = r'^[^/]+/[^/]+$'
                        if not re.match(pattern, user_text):
                            mastodon.status_reply(notification['status'], "슬롯머신 커맨드 형식이 올바르지 않습니다.", visibility='unlisted')
                            return
                        # [슬롯머신/00 닢]
                        user_account = notification['status']['account']["username"]
                        user_name = notification['status']['account']["display_name"]
                        money = user_text.split("/", 1)[1].strip()
                        
                        try:
                            result = slot_machine(user_account, money)
                            print(f"[OUTPUT] {user_account} : {result}")
                        except APIError:
                            mastodon.status_reply(notification['status'], "잠시 후 다시 메세지를 보내주세요.", visibility='unlisted')
                            return
                            
                        if result =="NONE":
                            mastodon.status_reply(notification['status'], "존재하지 않는 사용자입니다.", visibility='unlisted')
                        elif result =="INSERT_MONEY":
                            mastodon.status_reply(notification['status'], "금액을 정확히 입력하세요.", visibility='unlisted')
                        elif result =="ALREADY_DONE":
                            mastodon.status_reply(notification['status'], "이미 이번주 슬롯머신을 진행했습니다.", visibility='unlisted')
                        elif result =="NOT_ENOUGH":
                            mastodon.status_reply(notification['status'], "소지금이 부족합니다.", visibility='unlisted')
                        elif result =="NOT_TUESDAY":
                            mastodon.status_reply(notification['status'], "화요일에만 슬롯머신이 가능합니다.", visibility='unlisted')
                        else:
                            lot_result, lot_money, slots = result
                            # print(lot_result, lot_money, slots)
                            _yiga = yiga(user_name)
                            if lot_result == "111":
                                text = f"날마다 오는 기회가 아닌 행운에 도전합니다.\n{user_name}{_yiga} {int(re.sub(r'[^0-9]', '', money))}닢을 슬롯머신에 넣고 레버를 당기면...\n숫자가 빠르게 돌아가더니 하나씩 멈춥니다. \n\n결과는… \n{slots}!\n\n 일치하는 숫자가 하나도 없네요. 오늘은 운이 별로 좋지 않나 봅니다. 걸었던 돈을 모두 잃습니다."
                            elif lot_result == "222":
                                text = f"날마다 오는 기회가 아닌 행운에 도전합니다.\n{user_name}{_yiga} {int(re.sub(r'[^0-9]', '', money))}닢을 슬롯머신에 넣고 레버를 당기면...\n숫자가 빠르게 돌아가더니 하나씩 멈춥니다. \n\n결과는… \n{slots}!\n\n 일치하는 숫자가 두 개 있습니다! 오늘은 운이 아주 좋나보네요. {lot_money}닢을 획득합니다."
                            elif lot_result == "333":
                                text = f"날마다 오는 기회가 아닌 행운에 도전합니다.\n{user_name}{_yiga} {int(re.sub(r'[^0-9]', '', money))}닢을 슬롯머신에 넣고 레버를 당기면...\n숫자가 빠르게 돌아가더니 하나씩 멈춥니다. \n\n결과는… \n{slots}!\n \n세상에, 숫자가 모두 일치합니다! {lot_money}닢을 획득합니다!"
                            elif lot_result == "777":
                                text = f"날마다 오는 기회가 아닌 행운에 도전합니다.\n{user_name}{_yiga} {int(re.sub(r'[^0-9]', '', money))}닢을 슬롯머신에 넣고 레버를 당기면...\n숫자가 빠르게 돌아가더니 하나씩 멈춥니다. \n\n결과는… \n{slots}!\n\n 럭키 세븐! {user_name}{_yiga} {lot_money}닢을 획득합니다!"
                            elif lot_result == "666":
                                text = f"날마다 오는 기회가 아닌 행운에 도전합니다.\n{user_name}{_yiga} {int(re.sub(r'[^0-9]', '', money))}닢을 슬롯머신에 넣고 레버를 당기면...\n숫자가 빠르게 돌아가더니 하나씩 멈춥니다. \n\n결과는… \n{slots}!\n\n 이런! 오늘은 운이 끔찍하게 좋지 않나봅니다. {user_name}{_yiga} {abs(lot_money)}닢을 잃습니다…."
                            mastodon.status_reply(notification['status'], text, visibility='unlisted')

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
            mastodon.stream_user(ShopListener())
        except Exception as e:
            print("stream error:", e)
            traceback.print_exc()
            time.sleep(5)

if __name__ == '__main__':
    main()
