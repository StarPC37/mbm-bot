import requests
from bs4 import BeautifulSoup
import os

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
TARGET_URL = "https://mbm.garena.tw/news"
LAST_NEWS_FILE = "last_news.txt"

def get_latest_news():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(TARGET_URL, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 🎯 關鍵修正：跳過上方的輪播圖 (swiper)，直接鎖定下方的公告列表區塊
        # 這裡鎖定包含「伺服器維護完成公告」的那種列表項
        news_item = soup.select_one(".news_list_item") 
        
        if news_item:
            # 抓取標題（例如：3/18 (三) 伺服器維護完成公告）
            title_el = news_item.select_one(".news_item_title")
            title = title_el.get_text(strip=True) if title_el else "未知標題"
            
            # 抓取連結
            link = news_item.get('href', '')
            if link.startswith('/'): link = f"https://mbm.garena.tw{link}"
            
            return title, link
        else:
            print("❌ 找不到下方公告列表，請檢查網頁是否改版。")
            return None, None
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return None, None

def main():
    title, link = get_latest_news()
    if not title: return

    print(f"目前偵測到最新公告：{title}")

    # 讀取舊紀錄
    last_title = ""
    if os.path.exists(LAST_NEWS_FILE):
        with open(LAST_NEWS_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    # 如果標題不一樣，代表有「真正的」新公告
    if title != last_title:
        print("✅ 發現新公告，發送至 Discord")
        payload = {
            "username": "天刀M 公告小助手",
            "embeds":
        }
        requests.post(WEBHOOK_URL, json=payload)
        
        # 更新最後紀錄
        with open(LAST_NEWS_FILE, "w", encoding="utf-8") as f:
            f.write(title)
    else:
        print("😴 內容與上次相同，不重複發送。")

if __name__ == "__main__":
    main()
