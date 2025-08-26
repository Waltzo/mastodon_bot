#!/usr/bin/python3
# -*- coding: utf-8 -*-

from mastodon import Mastodon
from mastodon.streaming import StreamListener
from dotenv import load_dotenv
from datetime import datetime
import os
import re
from modules.text_utils import filterText, ennunyiga, ullul, yiga, wagwa, ennun
from modules.game_logic.DailyDuty import play_duty, check_duty
from modules.game_logic.Attendance import checkAttendance
from modules.game_logic.KeywordInvestigate import investigate
from modules.game_logic.Stetup import stet_up

# 환경변수 로드
load_dotenv()

# 주의사항
# 마스토돈 API 사용 제한: 5분/300회
# 구글스프레드 API 사용 제한: 1분/300회
# 봇 세팅
try:
    mastodon = Mastodon(
        client_id       = "kd3h8pX3MOD8Fb1lMm5YUkd3eJo7zemtvnjr7lETT3o",
        client_secret   = "4X2T8TVPAlPtoQzf_tJ2A4S7yv_4FfdKIc7IxL1iyJc",
        access_token    = "QFRz1HFxhLrBlU4djnA4Ej6d_dE3baQqzdqqLMojAnM",
        api_base_url    = os.getenv("API_BASE_URL")
            )
    # print('auth success')
except Exception as e:
    print('auth fail')
    print(e)

try:
    me = mastodon.account_verify_credentials()
except Exception as e:\dt

    print("API 인증 실패:", e)

print("bot initialized")


# 이벤트 리스너
class StoryListener(StreamListener):
    def on_notification(self, notification):
        print(notification)
        if notification['type'] == "mention":
            user_text = filterText(notification['status']['content'])
            user_account = notification['status']['account']["username"]
            print({user_account}," input :" , user_text)

    def handle_heartbeat(self):
        return super().handle_heartbeat()

# 메인함수
def main():
    mastodon.stream_user(StoryListener())

# 실행
if __name__ == '__main__':
    main()
