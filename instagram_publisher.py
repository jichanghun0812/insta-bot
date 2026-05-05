"""
instagram_publisher.py — Instagram Graph API를 이용한 자동 게시 모듈
"""

import os
import time
import sys
import io
import requests
from dotenv import load_dotenv

# Windows 터미널 한글 깨짐 방지
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# .env 파일 로드
load_dotenv()

# API 설정
API_VERSION = "v23.0"  # 최신 버전
BASE_URL = f"https://graph.instagram.com/{API_VERSION}"

def _get_config():
    """환경 변수 로드 및 검증"""
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
    
    if not token or not account_id:
        print("⚠️ 에러: .env 파일에 INSTAGRAM_ACCESS_TOKEN 또는 INSTAGRAM_ACCOUNT_ID가 설정되지 않았습니다.")
        return None, None
    return token, account_id

def post_carousel(image_urls, caption):
    """
    3장 이상의 이미지를 캐러셀(슬라이드) 형태로 게시합니다.
    
    1단계: 각 이미지의 미디어 컨테이너 생성 (is_carousel_item=true)
    2단계: 컨테이너 ID들을 묶어 캐러셀 컨테이너 생성
    3단계: 캐러셀 컨테이너를 실제 게시(Publish)
    """
    token, account_id = _get_config()
    if not token: return None

    print(f"\n🚀 인스타그램 캐러셀 게시 시작 (이미지 {len(image_urls)}장)")
    print("-" * 50)

    try:
        # 1. 각 이미지별 컨테이너 생성
        child_ids = []
        for i, url in enumerate(image_urls):
            print(f"📦 [1단계] 이미지 {i+1} 컨테이너 생성 중... ({url[:40]}...)")
            
            payload = {
                "image_url": url,
                "is_carousel_item": "true",
                "access_token": token
            }
            res = requests.post(f"{BASE_URL}/{account_id}/media", data=payload)
            res_data = res.json()
            
            if "id" not in res_data:
                print(f"❌ 에러: 이미지 {i+1} 컨테이너 생성 실패 - {res_data}")
                return None
                
            child_ids.append(res_data["id"])
            print(f"   ✅ 생성 완료 (ID: {res_data['id']})")
            time.sleep(3) # API 부하 방지 및 처리 대기

        # 2. 캐러셀 컨테이너(부모) 생성
        print(f"📂 [2단계] 캐러셀 부모 컨테이너 구성 중...")
        carousel_payload = {
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids), # 쉼표로 구분된 ID 리스트
            "caption": caption,
            "access_token": token
        }
        res = requests.post(f"{BASE_URL}/{account_id}/media", data=carousel_payload)
        carousel_data = res.json()
        
        if "id" not in carousel_data:
            print(f"❌ 에러: 캐러셀 부모 컨테이너 생성 실패 - {carousel_data}")
            return None
            
        creation_id = carousel_data["id"]
        print(f"   ✅ 캐러셀 구성 완료 (ID: {creation_id})")
        time.sleep(5) # 인스타그램 서버 처리 대기

        # 3. 실제 게시 (Media Publish)
        print(f"📢 [3단계] 인스타그램에 최종 게시물 업로드 중...")
        publish_payload = {
            "creation_id": creation_id,
            "access_token": token
        }
        res = requests.post(f"{BASE_URL}/{account_id}/media_publish", data=publish_payload)
        publish_data = res.json()
        
        if "id" not in publish_data:
            print(f"❌ 에러: 최종 게시 실패 - {publish_data}")
            return None

        print(f"\n✨ [성공] 인스타그램 게시 완료! (게시물 ID: {publish_data['id']})")
        print("-" * 50)
        return publish_data["id"]

    except Exception as e:
        print(f"⚠️ 게시 중 예외 발생: {e}")
        return None

if __name__ == "__main__":
    # 실제 GitHub Pages에 호스팅된 이미지 URL로 테스트
    print("🧪 [실제 테스트] 인스타그램 게시 시도 중...")
    
    real_urls = [
        "https://jichanghun0812.github.io/insta-bot/output/card_1_ko.jpg",
        "https://jichanghun0812.github.io/insta-bot/output/card_2_en.jpg",
        "https://jichanghun0812.github.io/insta-bot/output/card_3_quote.jpg"
    ]
    real_caption = "오늘의 역사 - 테스트 게시 🎉\n\n#오늘의역사 #역사 #history #테스트"
    
    # .env 설정 확인 후 실행
    t, a = _get_config()
    if t and a:
        post_carousel(real_urls, real_caption)
    else:
        print("💡 .env 파일에 INSTAGRAM_ACCESS_TOKEN 및 INSTAGRAM_ACCOUNT_ID를 먼저 입력해 주세요.")
