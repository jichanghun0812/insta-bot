import os
import requests
import time

# 아이콘 리스트 정의
ICON_CATEGORIES = {
    "modern": ["tv", "radio", "phone", "camera", "film", "music", "mic", "gamepad-2", "wifi", "cpu", "monitor", "smartphone"],
    "culture": ["medal", "trophy", "award", "palette", "clapperboard", "ticket"],
    "life": ["user", "user-plus", "user-minus", "baby", "cake", "heart", "cross", "home", "graduation-cap"],
    "health": ["pill", "virus", "syringe", "activity", "droplet", "snowflake", "stethoscope", "thermometer", "ambulance"],
    "conflict": ["swords", "shield", "bomb", "flame", "skull", "target", "flag", "map", "crosshair", "axe", "crown", "building-2", "landmark", "scroll", "gavel", "users", "globe", "key"],
    "science": ["rocket", "microscope", "flask-conical", "lightbulb", "compass", "telescope", "atom", "dna", "database", "cog"],
    "trade": ["ship", "anchor", "map-pinned", "plane", "truck", "coins", "banknote", "briefcase", "shopping-cart"],
    "nature": ["cloud-lightning", "wind", "waves", "mountain", "tree-pine", "bird", "frown", "alert-triangle", "sun", "moon", "infinity", "eye", "sparkles"]
}

BASE_DIR = "assets/icons"
CDN_URL = "https://unpkg.com/lucide-static@latest/icons/{name}.svg"

def download_icons():
    print("Lucide icon download started...")
    
    success_count = 0
    fail_count = 0
    
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        
    for category, icons in ICON_CATEGORIES.items():
        cat_dir = os.path.join(BASE_DIR, category)
        if not os.path.exists(cat_dir):
            os.makedirs(cat_dir)
            
        print(f"Category: {category}")
        
        for name in icons:
            target_path = os.path.join(cat_dir, f"{name}.svg")
            url = CDN_URL.format(name=name)
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(target_path, "wb") as f:
                        f.write(response.content)
                    print(f"  OK: {name}.svg downloaded")
                    success_count += 1
                else:
                    print(f"  FAIL: {name}.svg (HTTP {response.status_code})")
                    fail_count += 1
            except Exception as e:
                print(f"  ERROR: {name}.svg: {e}")
                fail_count += 1
            
            time.sleep(0.1)  # Server load protection
            
    print("\n" + "="*40)
    print(f"Job Finished!")
    print(f"SUCCESS: {success_count}")
    print(f"FAIL: {fail_count}")
    print("="*40)

if __name__ == "__main__":
    download_icons()
