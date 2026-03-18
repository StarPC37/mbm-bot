import requests
from bs4 import BeautifulSoup
import json
import os

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
TARGET_URL = "https://garena.tw"
LAST_NEWS_FILE = "last_news.txt"

def get_latest_news():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://garena.tw"
    }
    try:
        res = requests.get(TARGET_URL, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 🎯 關鍵技術：找出 Next.js 隱藏在網頁底部的數據 (JSON)
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if script_tag:
            data = json.loads(script_tag.string)
            # 從數據路徑抓取最新一則公告 (通常在 queries 裡面)
            # 這是針對 Garena 新版網頁結構的精準定位
            queries = data.get('props', {}).get('pageProps', {}).get('dehydratedState', {}).get('queries', [])
            
            for q in queries:
                if 'news/list' in q.get('queryKey', [None])[0]:
                    latest = q['state']['data']['list'][0]
                    title = latest['title']
                    news_id = latest['id']
                    link = f"https://garena.tw/detail/{news_id}"
                    return title, link
        
        # 如果 JSON 抓不到，嘗試備用的 CSS 選擇器（兼容模式）
        news_item = soup.select_one("a[class*='news_list_item']")
        if news_item:
            title = news_item.get_text(strip=True)
            link = news_item['href']
            if link.startswith('/'): link = f"https://garena.tw{link}"
            return title, link

    except Exception as e:
        print(f"解析失敗: {e}")
    return None, None

def main():
    title, link = get_latest_news()
    
    if not title:
        print("❌ 依然抓不到公告標題")
        return

    print(f"✅ 成功抓取：{title}")

    # 讀取與比對
    last_title = ""
    if os.path.exists(LAST_NEWS_FILE):
        with open(LAST_NEWS_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title != last_title:
        payload = {
            "username": "天刀M 公告助手",
            "embeds":
        }
        requests.post(WEBHOOK_URL, json=payload)
        
        with open(LAST_NEWS_FILE, "w", encoding="utf-8") as f:
            f.write(title)
    else:
        print("😴 標題相同，不重複發送。")

if __name__ == "__main__":
    main()
