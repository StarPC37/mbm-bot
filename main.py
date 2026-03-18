import requests
from bs4 import BeautifulSoup
import os

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
TARGET_URL = "https://garena.tw"
LAST_NEWS_FILE = "last_news.txt"

def get_latest_news():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(TARGET_URL, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 修正後的抓取路徑：Garena 官網公告目前的結構
        news_item = soup.find("a", class_="news_list_item")
        
        if news_item:
            title_el = news_item.find("div", class_="news_item_title")
            title = title_el.get_text(strip=True) if title_el else "找不到標題"
            link = news_item['href']
            if link.startswith('/'): link = f"https://garena.tw{link}"
            return title, link
        else:
            print("❌ 錯誤：在網頁上找不到任何公告項目 (.news_list_item)")
            return None, None
    except Exception as e:
        print(f"❌ 抓取異常: {e}")
        return None, None

def main():
    # 強制測試 Webhook 是否連通 (如果 Discord 收到這條，代表 Webhook 沒問題)
    # requests.post(WEBHOOK_URL, json={"content": "🤖 機器人檢查中..."})

    title, link = get_latest_news()
    print(f"目前抓到的最新公告：{title}")

    if not title: return

    last_title = ""
    if os.path.exists(LAST_NEWS_FILE):
        with open(LAST_NEWS_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    # 為了測試，我們先讓它標題不同就發送
    if title != last_title:
        print("✅ 發現新內容，正在發送到 Discord...")
        payload = {
            "embeds": [{
                "title": title,
                "url": link,
                "color": 16711680,
                "description": "鋼鐵傳說 MBM 有新公告囉！"
            }]
        }
        r = requests.post(WEBHOOK_URL, json=payload)
        print(f"Discord 回應狀態碼: {r.status_code}")
        
        with open(LAST_NEWS_FILE, "w", encoding="utf-8") as f:
            f.write(title)
    else:
        print("ℹ️ 標題與上次相同，跳過發送。")

if __name__ == "__main__":
    main()
