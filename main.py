import requests
from bs4 import BeautifulSoup
import os

# 從環境變數讀取 Webhook（安全做法）
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
TARGET_URL = "https://garena.tw"
LAST_NEWS_FILE = "last_news.txt"

def get_latest_news():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(TARGET_URL, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 抓取第一條公告
        news_item = soup.select_one(".news_list_item a") 
        if not news_item: return None, None
        
        title = news_item.select_one(".news_item_title").get_text(strip=True)
        link = news_item['href']
        if link.startswith('/'): link = f"https://garena.tw{link}"
        
        return title, link
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def main():
    title, link = get_latest_news()
    if not title: return

    # 讀取舊標題
    last_title = ""
    if os.path.exists(LAST_NEWS_FILE):
        with open(LAST_NEWS_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    # 比對並發送
    if title != last_title:
        print(f"發現新公告: {title}")
        payload = {"content": f"📢 **鋼鐵傳說新公告**\n【{title}】\n🔗 {link}"}
        requests.post(WEBHOOK_URL, json=payload)
        
        with open(LAST_NEWS_FILE, "w", encoding="utf-8") as f:
            f.write(title)
    else:
        print("沒有新公告")

if __name__ == "__main__":
    main()