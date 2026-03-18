import requests
import os

# 設定區
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
# Garena 官方公告資料接口 (API)
API_URL = "https://garena.tw"
LAST_NEWS_FILE = "last_news.txt"

def get_latest_news():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://garena.tw"
    }
    try:
        # 直接請求 JSON 資料
        response = requests.get(API_URL, headers=headers)
        data = response.json()
        
        # 解析 JSON 結構
        if data.get('status') == 0 and data.get('data', {}).get('list'):
            latest = data['data']['list'][0]
            title = latest.get('title')
            # 建立公告連結
            news_id = latest.get('id')
            link = f"https://garena.tw/detail/{news_id}"
            return title, link
        else:
            print("❌ API 資料結構異常")
            return None, None
    except Exception as e:
        print(f"❌ 抓取失敗: {e}")
        return None, None

def main():
    title, link = get_latest_news()
    if not title: return

    print(f"📡 伺服器回傳最新公告：{title}")

    last_title = ""
    if os.path.exists(LAST_NEWS_FILE):
        with open(LAST_NEWS_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title != last_title:
        print("✅ 發現新公告，發送至 Discord")
        payload = {
            "username": "天刀M 公告助手",
            "embeds":
        }
        r = requests.post(WEBHOOK_URL, json=payload)
        print(f"Discord 回應: {r.status_code}")
        
        with open(LAST_NEWS_FILE, "w", encoding="utf-8") as f:
            f.write(title)
    else:
        print("😴 目前沒有新公告。")

if __name__ == "__main__":
    main()
