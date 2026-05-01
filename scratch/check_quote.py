import requests

def check_wikiquote_manual(author):
    url = "https://en.wikiquote.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": author,
        "format": "json"
    }
    # Try with verify=False just to confirm existence if SSL is broken
    response = requests.get(url, params=params, verify=False)
    print(response.json())

check_wikiquote_manual("Marcus Aurelius")
