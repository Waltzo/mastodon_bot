import re
from bs4 import BeautifulSoup

CLEANER = re.compile(r'[^\w\s\[\]/,\*@\'\"\.\?\(\)\+]')

def filterText(rawText, CLEANER = CLEANER):
    soup = BeautifulSoup(rawText, 'html.parser')
    parsed_text = soup.get_text(strip=True)
    return re.sub(CLEANER, '', parsed_text)

def ends_with_jong(kstr):
    k = kstr[-1]
    return "가" <= k <= "힣" and (ord(k) - ord("가")) % 28 > 0

def ullul(kstr): 
    return f"{'을' if ends_with_jong(kstr) else '를'}"
def yiga(kstr): 
    return f"{'이' if ends_with_jong(kstr) else '가'}"
def wagwa(kstr): 
    return f"{'과' if ends_with_jong(kstr) else '와'}"
def ennun(kstr): 
    return f"{'은' if ends_with_jong(kstr) else '는'}"

def ennunyiga(name, text, name_type):
    prefix = "'{}'".format(name)
    targets = {
        "user": "(캐릭터 이름)",
        "item": "(아이템 이름)"
    }
    if name_type in targets:
        base = targets[name_type]
        text = text.replace(f"{base}(이가)", f"{prefix}{yiga(name)}")
        text = text.replace(f"{base}(은는)", f"{prefix}{ennun(name)}")
        text = text.replace(f"{base}(을를)", f"{prefix}{ullul(name)}")
        text = text.replace(f"{base}(와가)", f"{prefix}{wagwa(name)}")
    return text
