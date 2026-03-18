import requests
import os
import json

# 設定區
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
# 改用 Garena 官方列表 API (這是最穩定的來源)
API_URL = "https://garena.tw"
LAST_NEWS_FILE = "last_news.txt"

def send_to_discord(title, link=None, is_error=False):
    if not WEBHOOK_URL:
        print("錯誤：找不到 WEBHOOK_URL")
        return

    if is_error:
        payload = {"content": f"⚠️ **機器人回報錯誤**：{title}"}
    else:
        payload = {
            "username": "天刀M 公告助手",
            "embeds":
        }
    
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"發送 Discord 失敗: {e}")

def get_latest_news():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://garena.tw"
    }
    try:
        response = requests.get(API_URL, headers=headers, timeout=15)
        # 如果伺服器回傳錯誤代碼 (如 403 或 500)
        if response.status_code != 200:
            return None, None, f"伺服器回傳狀態碼: {response.status_code}"
            
        data = response.json()
        
        # 檢查 JSON 結構是否存在資料
        if data.get('status') == 0 and 'data' in data and data['data'].get('list'):
            item = data['data']['list']
            title = item.get('title', '無標題')
            news_id = item.get('id')
            link = f"https://garena.tw/detail/{news_id}" if news_id else "https://garena.tw"
            return title, link, None
        else:
            return None, None, "API 資料結構變動或內容為空"
            
    except Exception as e:
        return None, None, f"程式執行異常: {str(e)}"

def main():
    print("🚀 開始執行監控...")
    title, link, error_msg = get_latest_news()
    
    if error_msg:
        print(f"❌ 錯誤: {error_msg}")
        # 只有在偵錯時才開啟這行，避免洗版
        # send_to_discord(error_msg, is_error=True)
        return

    if not title:
        print("❌ 抓不到公告標題")
        return

    print(f"✅ 抓取成功：{title}")

    # 讀取舊紀錄
    last_title = ""
    if os.path.exists(LAST_NEWS_FILE):
        with open(LAST_NEWS_FILE, "r", encoding="utf-8") as f:
            last_title = f.read().strip()

    if title != last_title:
        print("📫 發現新公告，準備發送...")
        send_to_discord(title, link)
        # 更新紀錄檔案
        with open(LAST_NEWS_FILE, "w", encoding="utf-8") as f:
            f.write(title)
    else:
        print("😴 標題無變動，跳過。")

if __name__ == "__main__":
    main()
