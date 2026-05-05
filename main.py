"""
main.py — History Carousel Bot 전체 파이프라인 통합 실행기
(수집 -> 생성 -> 호스팅 업데이트 -> 인스타 게시)

사용법:
  # 테스트 모드 (이미지 생성까지만 수행, 인스타 게시 X):
  python main.py --test

  # 실제 게시 (콘텐츠 생성부터 인스타 업로드까지 전체 실행):
  python main.py
"""

import os
import sys
import io
import time
import subprocess
import argparse
from history_fetcher import get_top_event, get_search_keywords
from quote_fetcher import get_relevant_quote
from caption_writer import generate_history_caption
from card_generator import generate_card_set
from instagram_publisher import post_carousel
from icon_matcher import get_icon_path

COUNTER_FILE = "post_counter.txt"

def get_post_num():
    if not os.path.exists(COUNTER_FILE):
        return 1
    try:
        with open(COUNTER_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 1

def increment_post_num():
    num = get_post_num()
    with open(COUNTER_FILE, "w") as f:
        f.write(str(num + 1))

# Windows 터미널 한글 깨짐 방지 (필요 시에만 실행)
def set_utf8_stdout():
    if hasattr(sys.stdout, "buffer"):
        try:
            # 이미 UTF-8이거나 리다이렉션 중일 경우 에러 방지
            if sys.stdout.encoding.lower() != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        except Exception:
            pass

def run_command(command):
    """터미널 명령어를 실행하고 결과를 반환합니다."""
    try:
        # shell=True를 사용하여 git 명령어 등 쉘 내장 명령어 지원
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def setup_github_actions_git():
    """GitHub Actions 환경에서 Git 설정을 자동화합니다."""
    if os.getenv("GITHUB_ACTIONS") == "true":
        print("🌐 GitHub Actions 환경 감지 - Git 유저 설정 중...")
        run_command('git config --global user.email "github-actions[bot]@users.noreply.github.com"')
        run_command('git config --global user.name "github-actions[bot]"')
        return True
    else:
        print("💻 로컬 개발 환경")
        return False

def main():
    set_utf8_stdout()
    setup_github_actions_git()
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="인스타 게시 없이 카드 생성까지만 수행")
    args = parser.parse_args()

    print("\n🌟 [History Bot] 전체 자동화 파이프라인 시작")
    print("=" * 60)

    # 1. 데이터 수집 단계
    print("1️⃣ [수집] 오늘의 역사 및 명언 데이터 가져오는 중...")
    event = get_top_event()
    if not event:
        print("❌ 실패: 역사 사건을 가져오지 못했습니다.")
        return
    
    keywords = get_search_keywords(event)
    quote = get_relevant_quote(keywords)
    print(f"   ✅ 수집 완료: {event['year']}년 사건 선정")

    # 2. 콘텐츠 구성 단계 (AI)
    print("2️⃣ [AI] Gemini를 이용한 스토리텔링 및 카피 생성 중... (12초 안전 대기)")
    time.sleep(12) # 분당 API 호출 한도(429 에러) 방지용 안전 장치
    caption_result = generate_history_caption(event, quote)
    
    # --- [진단 로그 추가] ---
    import json
    print("\n🔍 [진단] caption_result 데이터 흐름 확인:")
    print(json.dumps(caption_result, indent=2, ensure_ascii=False))
    print("----------------------------------------\n")
    # ----------------------
    
    print("   ✅ 카피 생성 완료")

    # 2.5 아이콘 매칭 단계 (NEW)
    icon_path = get_icon_path(
        caption_result.get("category"),
        caption_result.get("icon_primary"),
        caption_result.get("icon_keywords")
    )
    print(f"   🎯 매칭된 아이콘: {icon_path}")

    # 3. 이미지 생성 단계
    print("3️⃣ [이미지] 1080x1080 카드 뉴스 3장 제작 중...")
    post_num = get_post_num()
    generated_files = generate_card_set(event, caption_result, quote, icon_path=icon_path, post_num=post_num)
    if not generated_files:
        print("❌ 실패: 카드 이미지 생성에 실패했습니다.")
        return
    print(f"   ✅ 생성 완료: {len(generated_files)}장의 카드")

    # --test 플래그가 있으면 여기서 중단 --
    if args.test:
        print("\n🧪 테스트 모드입니다. 인스타 게시를 건너뜁니다.")
        print("=" * 60)
        return

    # 4. GitHub 호스팅 업데이트 단계
    print("4️⃣ [호스팅] GitHub Pages 이미지 업데이트 중...")
    # 순차적으로 git 명령어 실행
    git_commands = [
        "git add output",
        'git commit -m "Auto-update history cards for hosting"',
        "git push origin main"
    ]
    
    for cmd in git_commands:
        success, output_or_err = run_command(cmd)
        if not success:
            # 변경 사항이 없을 때 commit 시 실패할 수 있으므로 메시지 확인
            if "nothing to commit" in output_or_err or "up to date" in output_or_err:
                continue
            print(f"   ⚠️ 경고: Git 명령어 실패 ('{cmd}') - {output_or_err}")
    
    print("   ✅ GitHub Push 완료. 서버 반영을 위해 60초간 대기합니다...")
    time.sleep(60) # GitHub Pages가 이미지를 새로고침할 시간 확보

    # 5. 인스타그램 게시 단계
    print("5️⃣ [게시] 인스타그램 Graph API 호출 중...")
    
    # GitHub Pages 기반 이미지 URL 구성
    github_user = "jichanghun0812"
    repo_name = "insta-bot"
    image_urls = [
        f"https://{github_user}.github.io/{repo_name}/output/card_1_ko.jpg",
        f"https://{github_user}.github.io/{repo_name}/output/card_2_en.jpg",
        f"https://{github_user}.github.io/{repo_name}/output/card_3_quote.jpg"
    ]
    
    # 캡션 조합 (AI가 만든 본문)
    final_caption = caption_result.get("instagram_caption", "오늘의 역사 소식입니다.")
    
    post_id = post_carousel(image_urls, final_caption)
    
    if post_id:
        print(f"\n🎉 [최종 성공] 인스타그램 게시가 완료되었습니다! (ID: {post_id})")
        increment_post_num()
        print(f"   📈 연재 차수 업데이트 완료 (다음 번호: {get_post_num()})")
    else:
        print("\n❌ 최종 실패: 인스타그램 게시 단계에서 문제가 발생했습니다.")

    print("=" * 60)

if __name__ == "__main__":
    main()
