define_columns = {
    "members": {
        "CHRID": 1,  # 캐릭터 ID
        "NAME": 2,  # 캐릭터 이름
        "MOV": 3,  # 이동력
        "MHP": 4,  # 최대체력
        "STR": 5,  # 전투력-총합
        "INS": 6,  # 안목-총합
        "DEX": 7,  # 손재주-총합
        "MHPD": 8,  # 최대체력-기본
        "STRD": 9,  # 전투력-기본
        "INSD": 10,  # 안목-기본
        "DEXD": 11,  # 손재주-기본
        "MHPA": 12,  # 최대체력-변경
        "STRA": 13,  # 전투력-변경
        "INSA": 14,  # 안목-변경
        "DEXA": 15,  # 손재주-변경
        "POTI": 16,  # 연금약 사용시간
        "FOOD": 17,  # 음식 사용시간
        "LUK": 18,  # 운
        "DET": 19,  # 의지
        "GIL": 20,  # 재화
        "ITEM": 21,  # 아이템
        "COUNT": 22,  # 출석일수
        "LVL": 23,  # 레벨
        "EXP": 24,  # 경험치
        "ASP": 25,  # 사용 가능 AP
        "TSP": 26,  # 누적 AP
        "USP": 27,  # 사용 AP
        "AB1": 28,  # 기술 1
        "AB2": 29,  # 기술 2
        "UP1": 30,  # 기술 1 강화 여부
        "UP2": 31,  # 기술 2 강화 여부
        "ATTD": 32,  # 마지막 출석 날짜
        "TDGC": 33,  # 당일 채집 횟수
        "TDGC_DATE": 34,  # 마지막 채집 일자
        "TDSM": 35,  # 당일 슬롯머신 여부
        "TDGB": 36,  # 당일 도박 여부
        "TDGB_R": 37,  # 당일 도박 결과
        "TDDT": 38,  # 마지막 의뢰 일자
        "WINS": 39,  # 전리품 개수
    },
    "daily_duty": {
        "WORD": 1,
        "USED": 2,
        "END1": 3,
        "END2": 4,
    },
    "items": {
        "NAME": 1,  # 재료 이름
        "TYPE": 2,  # 종류
        "COST": 3,  # 가격
        "GATH": 4,  # 채집 가능 여부
        "INGR": 5,  # 재료 가능 여부
        "MERC": 6,  # 구매 가능 여부
    },
    "craft_result": {
        "CRAFTER": 1,  # 제작자
        "OWNER": 2,  # 소유자
        "ITEMNAME": 3,  # 아이템 이름
        "ITEMTYPE": 4,  # 아이템 종류
        "EFFECT": 5,  # 아이템 효과
        "TIME": 6,  # 완성 시각
        "USED": 7,  # 사용 여부
        "WHO_USED": 8,  # 사용한 사람 이름
    },
    "auto_invest": {
        "KEYWORD": 1,
        "DESCRIPTION": 2,
    },
}
