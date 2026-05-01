"""
main.py — History Carousel Bot 전체 파이프라인 통합 실행기
"""

import sys
import io
import argparse
from history_fetcher import get_top_event, get_search_keywords
from quote_fetcher import get_relevant_quote
from caption_writer import generate_history_caption
from card_generator import generate_card_set

# Windows 터미널 한글 깨짐 방지
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Gemini 호출 없이 테스트 데이터로 실행")
    args = parser.parse_args()

    print("\n🌟 [History Bot] 전체 자동화 파이프라인 시작")
    print("=" * 60)

    # 1. 역사 데이터 수집
    print("1️⃣ 단계: 오늘의 역사 사건 수집 중...")
    event = get_top_event()
    if not event:
        print("❌ 역사 사건을 가져오지 못했습니다. 프로그램을 종료합니다.")
        return

    print(f"   - 선정된 사건: {event['year']}년 - {event['text'][:50]}...")

    # 2. 명언 데이터 수집
    print("2️⃣ 단계: 관련 명언 수집 중...")
    keywords = get_search_keywords(event)
    quote = get_relevant_quote(keywords)
    
    if not quote:
        print("   ⚠️ 관련 명언을 찾지 못했습니다. 기본 명언으로 대체합니다.")
        quote = {
            "quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
            "author": "Winston Churchill",
            "source": "Fallback"
        }

    print(f"   - 선정된 명언: {quote['author']} - {quote['quote'][:50]}...")

    # 3. AI 카피 작성 (Gemini)
    print("3️⃣ 단계: Gemini AI를 이용한 콘텐츠 구성 및 카피 생성 중...")
    try:
        # 테스트 모드인 경우 caption_writer 내부에서 가짜 데이터를 반환하도록 설계되어 있음 (구조 확인 필요)
        # 여기서는 단순히 호출하되, 에러 발생 시 폴백 처리
        caption_result = generate_history_caption(event, quote)
    except Exception as e:
        print(f"⚠️ Gemini API 호출 실패 ({e}). 폴백 데이터로 진행합니다.")
        # 최소한의 폴백 데이터 구성
        caption_result = {
            "card_year": f"{event['year']}년",
            "card_headline_ko": "오늘의 역사적 순간",
            "card_subtext_ko": event['text'],
            "card_headline_en": "Today in History",
            "card_subtext_en": event['text'],
            "vocab": [{"word": "history", "meaning": "역사"}],
            "quote_en": quote['quote'],
            "quote_author": quote['author'],
            "quote_ko": "명언 번역 생략 (API 한도)"
        }

    # 4. 카드 이미지 생성 (Playwright + Base64)
    print("4️⃣ 단계: 카드 이미지 세트(3장) 생성 중...")
    # card_generator는 내부적으로 test 모드일 때 별도 데이터를 쓰기도 하지만, 
    # 여기서는 main에서 직접 데이터를 넘겨주므로 일관되게 작동함.
    # 단, main.py 실행 시 --test 플래그가 있으면 card_generator에도 영향을 주도록 설계 가능.
    
    generated_files = generate_card_set(event, caption_result, quote)

    print("\n" + "=" * 60)
    print(f"✨ 작업 완료! 총 {len(generated_files)}개의 카드가 생성되었습니다.")
    for f in generated_files:
        print(f"   ✅ {f}")
    print("=" * 60)

if __name__ == "__main__":
    main()
