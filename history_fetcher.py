"""
history_fetcher.py — Wikimedia에서 오늘의 역사 사건 가져오기

이 파일의 역할:
  Wikimedia 공식 API를 통해 오늘 날짜에 발생했던 역사적 사건들을 조회합니다.
  조회된 사건 중 이미지가 있고 가장 흥미로운 사건을 선정하여 반환합니다.

API 정보:
  - URL: https://api.wikimedia.org/feed/v1/wikipedia/ko/onthisday/events/{월}/{일}
  - 별도의 API 키 없이 사용 가능한 공개 API입니다.

사용법:
  python history_fetcher.py
"""

import io
import os
import sys
import requests
from datetime import datetime

# Windows 터미널 한글 깨짐 방지
if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


# ============================================
# 핵심 함수: 오늘 날짜의 역사 조회
# ============================================

def get_todays_history() -> list[dict]:
    """
    오늘 날짜에 발생한 모든 역사적 사건 리스트를 가져옵니다.

    반환값:
        list[dict]: [{year, text, image_url, wiki_url}, ...] 형태의 리스트
    """
    # 1. 오늘 날짜 추출 (MM, DD 형식)
    today = datetime.now()
    month = f"{today.month:02d}"
    day = f"{today.day:02d}"

    print(f"📡 Wikimedia API 호출 중... ({month}월 {day}일 역사 조회)")

    # 2. API URL 구성 (영어 위키백과 사용 - 한국어보다 데이터가 훨씬 풍부함)
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
    
    # Wikimedia API는 명확한 User-Agent를 요구합니다.
    headers = {
        "User-Agent": "HistoryBot/1.0 (https://github.com/user/insta-bot; user@example.com) Python-requests/2.31"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # 에러 발생 시 예외 처리
        data = response.json()

        events = data.get("events", [])
        history_list = []

        for event in events:
            year = event.get("year")
            text = event.get("text", "")
            
            # 관련 문서(pages) 제목을 키워드로 추출
            pages = event.get("pages", [])
            keywords = [p.get("title") for p in pages if p.get("title")]
            
            image_url = ""
            wiki_url = ""

            if pages:
                # 관련 이미지 정보 추출
                image_info = pages[0].get("originalimage") or pages[0].get("thumbnail")
                if image_info:
                    image_url = image_info.get("source", "")
                
                # 위키백과 상세 링크
                wiki_info = pages[0].get("content_urls", {}).get("desktop", {})
                wiki_url = wiki_info.get("page", "")

            history_list.append({
                "year": year,
                "text": text,
                "keywords": keywords, # 명언 검색용 키워드
                "image_url": image_url,
                "wiki_url": wiki_url
            })

        print(f"  ✅ 총 {len(history_list)}개의 사건을 발견했습니다.")
        return history_list

    except Exception as e:
        print(f"  ❌ API 호출 실패: {e}")
        return []


def get_search_keywords(event: dict) -> list:
    """
    사건 데이터에서 명언 검색에 사용할 키워드를 추출합니다.
    """
    # 위키백과 문서 제목들이 가장 정확한 인명/지명 키워드입니다.
    return event.get("keywords", [])[:7] # 최대 7개 반환


def get_top_event() -> dict | None:
    """
    오늘의 사건 중 가장 '인스타에 올리기 좋은' 사건 1개를 선정합니다.
    선정 기준: 이미지 있는 사건 > 역사적 중요도(오래된 순)
    """
    events = get_todays_history()
    
    if not events:
        return None

    # 1. 이미지가 있는 사건들만 먼저 거릅니다.
    with_image = [e for e in events if e["image_url"]]
    
    # 2. 이미지가 있으면 그 중에서 가장 오래된(역사적 깊이가 있는) 사건을 고릅니다.
    #    없으면 전체 리스트에서 가장 오래된 사건을 고릅니다.
    candidates = with_image if with_image else events
    
    # 연도(year) 기준 오름차순 정렬 (가장 옛날 사건이 맨 위로)
    candidates.sort(key=lambda x: x["year"] if x["year"] is not None else 9999)
    
    return candidates[0]


# ============================================
# 메인 실행부 (테스트용)
# ============================================

if __name__ == "__main__":
    print("\n📜 [오늘의 역사] 데이터 수집 테스트 시작!")
    print("=" * 50)

    top_event = get_top_event()

    if top_event:
        print(f"\n✨ 오늘의 주요 사건 선정:")
        print(f"  📅 연도: {top_event['year']}년")
        print(f"  📝 내용: {top_event['text']}")
        print(f"  🔍 키워드: {get_search_keywords(top_event)}")
        print(f"  🖼️ 이미지: {top_event['image_url'] or '없음'}")
    else:
        print("\n😔 오늘 날짜의 역사 정보를 가져오지 못했습니다.")

    print("\n" + "=" * 50)
