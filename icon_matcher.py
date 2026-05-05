import os

# 카테고리별 기본 폴백 아이콘 정의
CATEGORY_FALLBACKS = {
    "modern": "smartphone",
    "culture": "award",
    "life": "user",
    "health": "pill",
    "conflict": "swords",
    "science": "lightbulb",
    "trade": "coins",
    "nature": "mountain"
}

UNIVERSAL_FALLBACK = "scroll" # 모든 상황 실패 시 '역사 일반' 아이콘
ICONS_BASE_DIR = os.path.join("assets", "icons")

def get_icon_path(category: str, primary_keyword: str, keywords: list = None) -> str:
    """
    사건 정보에 맞는 최적의 아이콘 SVG 경로를 반환합니다.
    Exact Match > Keyword Match > Category Fallback > Universal Fallback 순으로 매칭합니다.
    """
    # 1. 사용 가능한 아이콘 맵 생성 (이름: 경로)
    icon_map = {}
    for root, dirs, files in os.walk(ICONS_BASE_DIR):
        for file in files:
            if file.endswith(".svg"):
                name = file.replace(".svg", "")
                # 윈도우/리눅스 호환을 위해 슬래시 처리
                path = os.path.join(root, file).replace("\\", "/")
                icon_map[name] = path

    # 2. Exact Match (Primary Keyword)
    if primary_keyword and primary_keyword.lower() in icon_map:
        return icon_map[primary_keyword.lower()]

    # 3. Keyword Match (서브 키워드 리스트 순회)
    if keywords:
        for kw in keywords:
            if kw.lower() in icon_map:
                return icon_map[kw.lower()]

    # 4. Category Fallback
    fb_name = CATEGORY_FALLBACKS.get(category, UNIVERSAL_FALLBACK)
    if fb_name in icon_map:
        return icon_map[fb_name]

    # 5. Universal Fallback (최후의 수단)
    return icon_map.get(UNIVERSAL_FALLBACK, "")

if __name__ == "__main__":
    # 간단한 테스트
    print("--- Icon Matcher Test ---")
    print(f"Match 'crown': {get_icon_path('conflict', 'crown')}")
    print(f"Match 'unknown' in 'modern': {get_icon_path('modern', 'unknown')}")
    print(f"Match 'rocket' from keywords: {get_icon_path('science', 'nothing', ['rocket', 'atom'])}")
    print(f"Universal fallback: {get_icon_path('invalid', 'nothing')}")
