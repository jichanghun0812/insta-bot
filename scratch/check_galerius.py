import requests

def list_311_events():
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/04/30"
    headers = {"User-Agent": "HistoryBot/1.0"}
    response = requests.get(url, headers=headers)
    data = response.json()
    events = data.get("events", [])
    
    for event in events:
        if event.get("year") == 311:
            print(f"Year: {event.get('year')}")
            print(f"Text: {event.get('text')}")
            pages = event.get("pages", [])
            for p in pages:
                print(f"  Page Title: {p.get('title')}")
                img = p.get("originalimage") or p.get("thumbnail")
                print(f"  Image: {img.get('source') if img else 'None'}")

list_311_events()
