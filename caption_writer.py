"""
caption_writer.py — 역사 + 영어 + 명언 통합 카피 생성기

이 파일의 역할:
  영문 역사 사건 데이터를 바탕으로 Gemini AI가 다음을 수행합니다.
  1. 흥미로운 한국어 역사 스토리텔링 및 캡션 생성
  2. 영어 학습을 위한 핵심 단어 3개 추출
  3. (옵션) Wikiquote에서 가져온 명언의 한국어 번역

사용법:
  python caption_writer.py
"""

import io
import json
import os
import sys

# Windows 터미널 한글 깨짐 방지
if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일 로드 및 모델 설정
load_dotenv()
GEMINI_MODEL = "gemini-2.5-flash"


def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Gemini API 키가 없습니다. .env 파일을 확인하세요.")
        sys.exit(1)
    return api_key


# ============================================
# 프롬프트 (역사 + 영어 학습 컨셉)
# ============================================

HISTORY_PROMPT_TEMPLATE = """
당신은 역사 지식과 영어 학습 콘텐츠를 제공하는 인기 인스타그램 크리에이터입니다.
제공된 영문 역사 사건 정보를 바탕으로 3장 분량의 카드뉴스 콘텐츠를 구성해주세요.

## 사건 정보 (영문)
- 연도: {year}
- 내용: {text}

## 명언 정보 (있을 때만)
- 원문: {raw_quote}
- 저자: {quote_author}

## 요청 사항

### 1. 한국어 스토리텔링 (1장용)
- 사건을 한국어로 아주 흥미진진하게 요약해주세요.
- `card_headline_ko` (15자 이내 임팩트 있는 제목)
- `card_subtext_ko` (간결한 부제)

### 2. 영어 학습 (2장용)
- 영문 텍스트를 바탕으로 핵심 문구와 단어를 선정하세요.
- `card_headline_en` (사건의 영어 제목)
- `card_subtext_en` (사건의 영어 짧은 요약)
- `vocab` (텍스트에서 추출한 핵심 단어 3개: 단어, 발음, 한국어 뜻)

### 3. 명언 번역 (3장용, 명언 정보가 있을 때만)
- 제공된 명언의 의미를 살려 멋진 한국어로 번역해주세요.

### 4. 인스타그램 캡션
- 역사적 맥락과 현대적 교훈을 담은 풍부한 내용의 게시글 본문.
- 이모지와 해시태그 포함.

## 응답 형식 (반드시 이 JSON 형식을 지키세요)
{{
  "card_year": "{year}년",
  "card_headline_ko": "제목",
  "card_subtext_ko": "부제",
  "card_headline_en": "English Title",
  "card_subtext_en": "English Summary",
  "vocab": [
    {{"word": "word1", "pron": "[발음]", "meaning": "뜻"}},
    {{"word": "word2", "pron": "[발음]", "meaning": "뜻"}},
    {{"word": "word3", "pron": "[발음]", "meaning": "뜻"}}
  ],
  "quote_ko": "명언 번역 (없으면 빈 문자열)",
  "instagram_caption": "본문 내용..."
}}
"""


# ============================================
# 핵심 함수: 캡션 생성
# ============================================

def generate_history_caption(history_data: dict, quote_data: dict = None) -> dict:
    """
    역사 데이터와 명언 데이터를 결합하여 통합 카피를 생성합니다.
    """
    print(f"  🤖 Gemini에게 역사 카피 요청 중... ({history_data.get('year')}년 사건)")

    api_key = _get_api_key()
    genai.configure(api_key=api_key)

    # 명언 정보 준비
    raw_quote = quote_data.get("quote", "") if quote_data else ""
    quote_author = quote_data.get("author", "") if quote_data else ""

    prompt = HISTORY_PROMPT_TEMPLATE.format(
        year=history_data.get("year", "알 수 없음"),
        text=history_data.get("text", "정보 없음"),
        raw_quote=raw_quote,
        quote_author=quote_author
    )

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # JSON 파싱 로직 (기존과 동일)
        result = _parse_response(response.text)
        if result:
            # 명언 원문과 저자 정보도 결과에 합쳐서 반환
            if quote_data:
                result["quote_en"] = raw_quote
                result["quote_author"] = quote_author
            return result

    except Exception as e:
        print(f"  ⚠️ Gemini API 실패: {e}")

    return _create_fallback(history_data, quote_data)


def _parse_response(response_text: str) -> dict | None:
    text = response_text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    try:
        return json.loads(text)
    except:
        return None


def _create_fallback(history_data: dict, quote_data: dict = None) -> dict:
    year = history_data.get("year", "")
    fallback = {
        "card_year": f"{year}년",
        "card_headline_ko": "역사적 오늘",
        "card_subtext_ko": "오늘 일어난 놀라운 사건",
        "card_headline_en": "Today in History",
        "card_subtext_en": "A significant event occurred today.",
        "vocab": [{"word": "History", "pron": "[ˈhɪstri]", "meaning": "역사"}],
        "quote_ko": "명언 정보가 없습니다." if not quote_data else "명언 번역 오류 (API 한도)",
        "instagram_caption": f"{year}년 오늘 있었던 역사적 사건입니다."
    }
    
    if quote_data:
        fallback["quote_en"] = quote_data.get("quote", "")
        fallback["quote_author"] = quote_data.get("author", "")
        
    return fallback


# ============================================
# 메인 실행부 (통합 테스트)
# ============================================

if __name__ == "__main__":
    from history_fetcher import get_top_event, get_search_keywords
    from quote_fetcher import get_relevant_quote

    # 1. 역사 데이터 가져오기
    event = get_top_event()
    if not event:
        sys.exit(0)

    # 2. 명언 데이터 가져오기
    keywords = get_search_keywords(event)
    quote = get_relevant_quote(keywords)

    # 3. 통합 카피 생성
    result = generate_history_caption(event, quote)

    # 4. 결과 출력
    print("\n" + "=" * 50)
    print(f"📅 연도: {result['card_year']}")
    print(f"🇰🇷 제목: {result['card_headline_ko']}")
    print(f"🇺🇸 제목: {result['card_headline_en']}")
    print(f"🔤 단어: {[v['word'] for v in result['vocab']]}")
    if result.get("quote_ko"):
        print(f"💬 명언: {result['quote_ko']}")
    print("=" * 50)
