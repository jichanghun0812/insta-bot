"""
quote_fetcher.py — Wikiquote에서 검증된 명언 가져오기

이 파일의 역할:
  전달받은 키워드 리스트(인물명 등)를 사용하여 Wikiquote에서 실제 명언을 검색합니다.
  AI가 생성하는 것이 아니라, 실제 기록된 어록만 가져와 할루시네이션을 방지합니다.

사용법:
  python quote_fetcher.py
"""

import io
import sys
import random
import wikiquotes

# Windows 터미널 한글 깨짐 방지
if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


# ============================================
# 핵심 함수: 관련 명언 가져오기
# ============================================

def get_relevant_quote(keywords: list) -> dict | None:
    """
    키워드 리스트를 순차적으로 검색하여 가장 먼저 발견된 명언을 반환합니다.

    매개변수:
        keywords (list): 검색할 키워드 리스트 (예: ['Albert Einstein', 'Science'])

    반환값:
        dict: {"quote": "명언 내용", "author": "저자", "source": "Wikiquote"}
        None: 명언을 찾지 못한 경우
    """
    print(f"🔍 Wikiquote에서 명언 검색 중... (대상 키워드: {keywords})")

    for keyword in keywords:
        if not keyword:
            continue
            
        try:
            # 1. 해당 키워드(인물)로 검색 가능한 리스트 확인
            # (wikiquotes는 정확한 인물명을 요구하므로 search로 먼저 확인)
            search_results = wikiquotes.search(keyword, "en")
            
            if not search_results:
                continue

            # 2. 첫 번째 검색 결과(가장 정확한 인물명)로 명언 가져오기
            author = search_results[0]
            quotes = wikiquotes.get_quotes(author, "en")

            if quotes:
                # 너무 짧거나 너무 긴 명언 제외 (인스타용 50~150자 선호)
                suitable_quotes = [q for q in quotes if 30 < len(q) < 200]
                
                # 적당한 게 없으면 그냥 아무거나 하나 선택
                final_quote = random.choice(suitable_quotes if suitable_quotes else quotes)
                
                print(f"  ✅ 명언 발견! 저자: {author}")
                return {
                    "quote": final_quote,
                    "author": author,
                    "source": "Wikiquote"
                }

        except Exception as e:
            # 검색 실패 시 다음 키워드로 넘어감
            continue

    print("  ❌ 관련 명언을 찾지 못했습니다.")
    return None


# ============================================
# 메인 실행부 (테스트용)
# ============================================

if __name__ == "__main__":
    test_keywords = ["Albert Einstein", "Isaac Newton", "History"]
    
    print("\n📜 [명언 수집] 테스트 시작!")
    print("=" * 50)

    result = get_relevant_quote(test_keywords)

    if result:
        print(f"\n✨ 오늘의 명언:")
        print(f"  💬 \"{result['quote']}\"")
        print(f"  ✍️  저자: {result['author']}")
        print(f"  📚 출처: {result['source']}")
    else:
        print("\n😔 적절한 명언을 찾지 못했습니다.")

    print("\n" + "=" * 50)
