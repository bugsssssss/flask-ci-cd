import requests
import os 

TELEGRAM_BOT_TOKEN = ''
TELEGRAM_CHAT_ID = '' 

def notify_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bot credentials not set.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response  = requests.post(url, data=payload, timeout=10)
        print(response.text)
    except Exception as e:
        print("Telegram notify error:", e)
