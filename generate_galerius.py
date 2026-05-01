import sys
import io
from card_generator import generate_card_set

# Windows 터미널 한글 깨짐 방지
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 311년 갈레리우스 사건 진짜 데이터
event = {
    "year": "311",
    "text": "The Edict of Toleration by Galerius was issued in 311, ending the Diocletianic Persecution of Christians.",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Follis-Domitius_Alexander-carthage_RIC_68.jpg"
}

# 마르쿠스 아우렐리우스 명언 (Wikiquote 검증됨)
quote = {
    "quote": "Waste no more time arguing about what a good man should be. Be one.",
    "author": "Marcus Aurelius",
    "source": "Wikiquote"
}

# 고품질 카피 데이터
caption_result = {
    "card_year": "311년",
    "card_headline_ko": "로마 제국, 기독교를 인정하다!",
    "card_subtext_ko": "박해를 끝낸 갈레리우스 황제의 '관용 칙령'",
    "card_headline_en": "The Edict of Toleration",
    "card_subtext_en": "Rome ends the persecution of Christianity",
    "vocab": [
        {"word": "persecution", "meaning": "박해"},
        {"word": "toleration", "meaning": "관용"},
        {"word": "edict", "meaning": "칙령"}
    ],
    "quote_en": quote["quote"],
    "quote_author": quote["author"],
    "quote_ko": "좋은 사람이 어떤 사람인지 논쟁하느라 시간을 낭비하지 마라. 스스로 그런 사람이 되어라."
}

# 카드 생성 실행
generate_card_set(event, caption_result, quote)
