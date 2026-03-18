import requests
import os

# 從 GitHub Secrets 讀取
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
TARGET_URL = "https://garena.tw"

def send_discord(msg):
    payload = {"content": f"🤖 **機器人回報：**\n{msg}"}
    try:
        r = requests.post(WEBHOOK_URL, json=payload)
        print(f"Discord 狀態碼: {r.status_code}")
    except Exception as e:
        print(f"發送 Discord 失敗: {e}")

def main():
    print("🚀 啟動監控...")
    
    # 先測試 Webhook 是否正常運作
    send_discord("正在檢查天刀 M 官網公告...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://garena.tw"
    }

    try:
        # 嘗試抓取 HTML
        res = requests.get(TARGET_URL, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        
        # 這次我們改用最原始的關鍵字搜尋，避開所有標籤報錯
        html_text = res.text
        
        # 搜尋關鍵字：3/18 (或你截圖中的日期)
        # 如果抓得到 HTML，我們直接把前 500 個字傳回去看抓到了什麼
        sample = html_text[:200].replace('\n', ' ')
        send_discord(f"成功連線官網！網頁開頭預覽：\n`{sample}`")

    except Exception as e:
        send_discord(f"❌ 連線官網失敗，錯誤原因：{str(e)}")

if __name__ == "__main__":
    main()
