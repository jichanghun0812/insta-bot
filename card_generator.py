"""
card_generator.py — 역사 x 영어 x 명언 3장 카드 세트 생성기 (로컬 이미지 처리 버전)
"""

import io
import os
import sys
import argparse
import requests
import base64
from playwright.sync_api import sync_playwright

# Windows 터미널 한글 깨짐 방지
if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

OUTPUT_DIR = "output"
TEMP_IMAGE = os.path.join(OUTPUT_DIR, "temp_bg.jpg")


def download_image(url: str, save_path: str) -> bool:
    """이미지를 다운로드하여 로컬에 저장합니다."""
    if not url:
        print("  ⚠️ 이미지 URL이 비어 있습니다.")
        return False
    try:
        # 403 에러 방지를 위해 실제 최신 크롬 브라우저의 User-Agent 사용
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        print(f"  📥 이미지 다운로드 시도 (User-Agent 교체): {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"  ✅ 이미지 저장 완료: {save_path} ({len(response.content)} bytes)")
            return True
        else:
            print(f"  ❌ 이미지 다운로드 실패 (상태 코드: {response.status_code})")
            return False
    except Exception as e:
        print(f"  ⚠️ 이미지 다운로드 중 에러 발생: {e}")
    return False


# ============================================
# 핵심 함수: 카드 세트 생성
# ============================================

def generate_card_set(history_data: dict, caption_data: dict, quote_data: dict = None) -> list[str]:
    print(f"🎨 카드 세트 생성 시작... ({history_data.get('year')}년 사건)")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. 배경 이미지 미리 다운로드
    image_url = history_data.get("image_url", "")
    has_local_image = download_image(image_url, TEMP_IMAGE)

    # 로컬 이미지를 Base64로 인코딩
    image_base64 = ""
    if has_local_image:
        try:
            with open(TEMP_IMAGE, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                image_base64 = f"data:image/jpeg;base64,{encoded_string}"
        except Exception as e:
            print(f"  ⚠️ Base64 인코딩 실패: {e}")
            has_local_image = False

    # 템플릿 읽기
    template_path = os.path.join("templates", "card.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    generated_files = []
    modes = [
        {"id": "1_ko", "name": "ko", "tag": "📜 오늘의 역사 🇰🇷"},
        {"id": "2_en", "name": "en", "tag": "📜 Today in History 🇺🇸"}
    ]
    if quote_data:
        modes.append({"id": "3_quote", "name": "quote", "tag": "✍️ 오늘의 명언"})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1080})

        for m in modes:
            html = template_html
            
            # 배경 이미지 설정 (Base64 데이터 주입)
            html = html.replace("{{image_base64}}", image_base64)
            bg_display = "block" if has_local_image and m["name"] != "quote" else "none"
            html = html.replace("{{bg_image_display}}", bg_display)
            
            # 공통 및 모드별 설정
            html = html.replace("{{header_tag}}", m["tag"])
            html = html.replace("{{card_year}}", caption_data.get("card_year", ""))
            html = html.replace("{{mode_ko_display}}", "block" if m["name"] == "ko" else "none")
            html = html.replace("{{mode_en_display}}", "block" if m["name"] == "en" else "none")
            html = html.replace("{{mode_quote_display}}", "block" if m["name"] == "quote" else "none")

            # 데이터 채우기 (KO/EN/QUOTE)
            html = html.replace("{{card_headline_ko}}", caption_data.get("card_headline_ko", ""))
            html = html.replace("{{card_subtext_ko}}", caption_data.get("card_subtext_ko", ""))
            html = html.replace("{{card_headline_en}}", caption_data.get("card_headline_en", ""))
            html = html.replace("{{card_subtext_en}}", caption_data.get("card_subtext_en", ""))
            
            vocab_html = "".join([f'<div class="vocab-item"><span class="vocab-word">{v["word"]}</span><span class="vocab-meaning">{v["meaning"]}</span></div>' for v in caption_data.get("vocab", [])])
            html = html.replace("{{vocab_html}}", vocab_html)
            
            html = html.replace("{{quote_en}}", caption_data.get("quote_en", ""))
            html = html.replace("{{quote_author}}", caption_data.get("quote_author", ""))
            html = html.replace("{{quote_ko}}", caption_data.get("quote_ko", ""))

            # 이미지 생성
            output_path = os.path.abspath(os.path.join(OUTPUT_DIR, f"card_{m['id']}.jpg"))
            page.set_content(html)
            page.wait_for_load_state("networkidle")
            page.screenshot(path=output_path, type="jpeg", quality=90)
            
            generated_files.append(output_path)
            print(f"  ✅ {m['id']} 카드 생성 완료")

        browser.close()

    return generated_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Gemini 호출 없이 테스트 데이터로 실행")
    args = parser.parse_args()

    print("\n🚀 [오늘의 역사] 전체 파이프라인 실행!")
    print("=" * 50)

    if args.test:
        print("🧪 테스트 모드: 샘플 데이터를 사용하여 카드를 생성합니다.")
        event = {
            "year": "311",
            "text": "The Edict of Toleration by Galerius was issued in 311...",
            # 더 안정적인 고해상도 로마 관련 이미지 (Unsplash)
            "image_url": "https://images.unsplash.com/photo-1552168324-d612d77725e3?q=80&w=1080&auto=format&fit=crop"
        }
        quote = {"quote": "Where there is no gentleness, there is no power.", "author": "Marcus Aurelius", "source": "Wikiquote"}
        caption_result = {
            "card_year": "311년", "card_headline_ko": "로마 제국, 기독교를 인정하다!", "card_subtext_ko": "박해를 끝낸 갈레리우스 황제의 관용 칙령",
            "card_headline_en": "The Edict of Toleration", "card_subtext_en": "Rome ends the persecution of Christianity",
            "vocab": [{"word": "persecution", "meaning": "박해"}, {"word": "toleration", "meaning": "관용"}, {"word": "edict", "meaning": "칙령"}],
            "quote_en": quote["quote"], "quote_author": quote["author"], "quote_ko": "관용이 없는 곳에는 진정한 힘도 존재할 수 없다."
        }
    else:
        from history_fetcher import get_top_event, get_search_keywords
        from quote_fetcher import get_relevant_quote
        from caption_writer import generate_history_caption
        event = get_top_event()
        if not event: sys.exit(0)
        keywords = get_search_keywords(event)
        quote = get_relevant_quote(keywords)
        caption_result = generate_history_caption(event, quote)

    generate_card_set(event, caption_result, quote)
    print("\n" + "=" * 50 + "\n✨ 작업 완료! \n" + "=" * 50)
