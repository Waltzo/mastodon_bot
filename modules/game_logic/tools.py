def calc_total_price(shop_item_list, item_list):
    """
        아이템 리스트의 총 가격을 확인
        ## args
            shop_item_list: 
                상점 아이템 리스트
            item_list: 
                사려는 아이템 리스트 [(아이템이름,개수), ...]
        ## API 요청
            없음
    """
    price_dict = {name: int(price) for name, price in shop_item_list}
    total = 0
    for name, count in item_list:
        total += price_dict.get(name, 0) * int(count)
    return total

def is_enough(inventory: list, itemlist: list):
    """
        두 튜플리스트를 비교해 inventory에 itemlist가 충분히 있는지 확인하는 함수
    """
    from collections import Counter
    counter1 = Counter(dict(inventory))
    counter2 = Counter(dict(itemlist))
    for key, value in counter2.items():
        if counter1[key] < value:
            return False
    return True

def check_items_exist(shop_item_list, item_list):
    """
        아이템 구매 가능 여부 확인
        ## args
            shop_item_list: list
                상점 아이템 리스트
            item_list: list
                사려는 아이템 리스트 [("아이템이름",개수), ...]
        ## return
            yes_list: list
                구매 가능한 아이템 리스트 [("아이템이름",개수), ...]
            no_list: list
                구매 불가능한 아이템 리스트 [("아이템이름",개수), ...]
        ## API 요청 
            없음
    """
    item_names = {name for name, _ in shop_item_list}
    no_list = []
    yes_list = []
    for name, count in item_list:
        if name in item_names:
            yes_list.append((name,count))
        else:
            no_list.append((name,count))
    return yes_list, no_list

def stat_adj(x):
    """
        손재주/안목 보정치 적용
    """
    if x <= 1:
        return 1
    elif x <= 3:
        return 3
    elif x <= 7:
        return 5
    elif x <= 9:
        return 9
    else:
        return 10
    
def split_item_list(item_list_str):
    """
        따옴표로 감싼 항목 안의 콤마를 보존하며 아이템명/개수 파싱 및 동일 이름 합산
        ## args
            item_list_str: str
                아이템 리스트 ("조미료 세트 3 개, 완벽한 방어구, 버섯*2")
        ## return
            output_item_list: list
                아이템 리스트 [("조미료 세트",3),("완벽한 방어구",1),("버섯",2)]
            "INVALID_ITEM_FORMAT": str
                아이템 형식이 잘못된 경우
        ## API 요청 
            없음
    """
    import re

    s = (item_list_str or "").strip()
    items = []
    pos = 0
    n = len(s)

    while pos < n:
        # 공백 건너뛰기
        while pos < n and s[pos].isspace():
            pos += 1
        if pos >= n:
            break

        # 따옴표로 감싼 항목 처리: 'name, with, comma' 1개 등
        if s[pos] == "'":
            end = s.find("'", pos + 1)
            if end == -1:
                # 닫는 따옴표가 없으면 남은 문자열 전체(따옴표 포함)를 이름으로 사용
                name = s[pos:].strip()
                pos = n
            else:
                # 따옴표 포함해서 이름 보존
                name = s[pos:end+1]
                pos = end + 1

            # 따옴표 뒤의 개수 파싱: "*N", "N개", 또는 " N"
            m = re.match(r'\s*(?:\*\s*(\d+)|(\d+)\s*개|\s+(\d+))', s[pos:])
            if m:
                count = int(next(g for g in m.groups() if g))
                pos += m.end()
            else:
                count = 1

            # 다음 구분자(콤마)가 있으면 건너뜀
            while pos < n and s[pos].isspace():
                pos += 1
            if pos < n and s[pos] == ',':
                pos += 1

            items.append((name, count))
            continue

        # 비따옴표 항목: 콤마까지 잘라서 처리
        comma_idx = s.find(',', pos)
        token = s[pos:comma_idx] if comma_idx != -1 else s[pos:]
        pos = (comma_idx + 1) if comma_idx != -1 else n
        token = token.strip()
        if not token:
            continue

        # 여러 표기 지원: "*N", "N개", "name N", 기본 1
        if '*' in token:
            m = re.match(r'(.+?)\s*\*\s*(\d+)\s*$', token)
            if not m:
                return "INVALID_ITEM_FORMAT"
            name, count = m.group(1).strip(), int(m.group(2))
        elif token.endswith('개'):
            m = re.match(r'(.+?)\s*(\d+)\s*개\s*$', token)
            if not m:
                return "INVALID_ITEM_FORMAT"
            name, count = m.group(1).strip(), int(m.group(2))
        else:
            m = re.match(r'(.+?)\s+(\d+)\s*$', token)
            if m:
                name, count = m.group(1).strip(), int(m.group(2))
            else:
                name, count = token, 1

        items.append((name, count))

    # 동일 이름 합산(등장 순서 유지)
    aggregated = {}
    order = []
    for name, cnt in items:
        if name not in aggregated:
            aggregated[name] = 0
            order.append(name)
        aggregated[name] += cnt

    return [(n, aggregated[n]) for n in order]

def colnum_to_alpha(n):
    """
        컬럼 넘버를 알파벳으로 바꿔주는 함수
        ## args
            n: int
                컬럼 번호. 
                A열은 1, B열은 2 ...
    """
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

def tuple2str(tuple_list):
    """
        [("조미료 세트",3), ...] 를 "조미료 세트 3 개, ..." 로 변경
    """
    str_list = [f"{name} {count} 개" for name, count in tuple_list]
    return ", ".join(str_list)

def str2tuple(str_items):
    """
        "조미료 세트 3 개, ..." 를 [("조미료 세트",3), ...] 로 변경
    """
    str_list=str_items.split(",")
    result = []
    for s in str_list:
        # 오른쪽에서부터 2번만 분리
        name, count, _ = s.rsplit(' ', 2)
        result.append((name.strip(), int(count)))
    return result

def job_check(row_values):
    """
        row_values 에서 INS, DEX 를 확인해 CRAFTER_GATHERER/FIGHTER 를 구분
    """
    from worksheet_columns import define_columns
    insight = int(row_values[define_columns["members"]["INS"] - 1] or 0)
    dexterity = int(row_values[define_columns["members"]["DEX"] - 1] or 0)
    if insight + dexterity >= 1:
        return "CRAFTER_GATHERER"
    else:
        return "FIGHTER"
    
def user_inv(row_values):
    """
        row_values 에서 인벤토리를 튜플리스트로 반환
    """
    from worksheet_columns import define_columns
    inventory_idx = define_columns["members"]["ITEM"] - 1
    inventory_str = row_values[inventory_idx] if len(row_values) > inventory_idx else ''
    user_inventory = [] if inventory_str == '' else str2tuple(inventory_str)
    return user_inventory