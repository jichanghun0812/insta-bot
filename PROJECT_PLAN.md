# 📜 인스타그램 "오늘의 역사" 자동 게시 봇 — 프로젝트 계획서

> 매일 오늘 날짜에 일어난 역사적 사건을 정리해 카드 이미지로 제작하고 인스타그램에 자동 게시하는 Python 봇  
> 작성일: 2026-04-30 (컨셉 최종 확정)

---

## 1. 시스템 아키텍처

```
⏰ GitHub Actions (매일 아침 실행)
        │
        ▼
  ┌─────────────┐
  │   main.py   │ ← 전체 흐름 지휘
  └─────┬───────┘
        │
        ├──① Wikimedia API ─────→ 오늘 날짜의 역사적 사건(Events) 수집
        │                         (https://api.wikimedia.org/feed/v1/wikipedia/ko/onthisday/events/...)
        │
        ├──② Gemini API ────────→ 사건 요약 및 "타임라인" 컨셉의 역사 카피 생성
        │
        ├──③ HTML + Playwright ─→ 역사 카드 이미지 생성 (연도 뱃지 + 역사적 분위기)
        │
        ├──④ GitHub Pages ─────→ 이미지 호스팅 (업로드용 URL 생성)
        │
        └──⑤ Instagram API ────→ 이미지 + 캡션 자동 게시
```

---

## 2. 프로젝트 폴더 구조

```
insta-bot/
├── main.py               # 메인 실행 파일
├── history_fetcher.py     # [NEW] Wikimedia API 연동 (사건 조회)
├── caption_writer.py      # [MODIFY] 역사 컨셉 프롬프트 수정
├── card_generator.py      # [MODIFY] 역사 데이터 매핑 수정
├── templates/
│   └── card.html          # [MODIFY] 타임라인 카드 디자인 (연도 뱃지 등)
├── _archive/             # 이전 OTT 관련 코드 보관
├── .env                   # 🔒 API 키 보관
├── requirements.txt       # 패키지 목록
└── PROJECT_PLAN.md        # 이 문서
```

---

## 3. 개발 로드맵 (오늘의 역사)

### 1단계: 역사 데이터 수집 (history_fetcher.py)
- 오늘 월/일 자동 추출 및 Wikimedia API 호출 (한국어)
- 사건 리스트 중 가장 흥미로운 사건 1개 선정
- 반환: 연도(year), 내용(text), 이미지(originalimage), 상세 링크

### 2단계: 역사 스토리텔러 Gemini (caption_writer.py)
- 프롬프트 수정: 역사적 사실을 흥미로운 이야기로 구성
- 출력: `card_year`, `card_headline`, `card_subtext`, `instagram_caption`

### 3단계: 타임라인 카드 생성 (card.html)
- 디자인 변경: OTT 브랜드 컬러 → 사건 연도 강조 디자인
- 역사적 사진/일러스트를 배경으로 활용 (Netflix 스타일 계승)

### 4단계~: 인스타 자동 게시 및 자동화
- 기존 계획과 동일 (GitHub Pages 호스팅 + Instagram API)

---

## 4. 비용 & 일정
- **비용**: 완전 무료 (Wikipedia API 무제한)
- **일정**: 파이프라인이 구축되어 있어 1~2일 내 전환 완료 가능

---

## 다음 단계
> 계획서 업데이트가 완료되었습니다. 승인하시면 기존 `tmdb_fetcher.py`를 아카이브하고 **1단계: history_fetcher.py 작성**을 시작하겠습니다! 📜🚀
