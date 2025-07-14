import os
import aiohttp

async def send_telegram_summary(message: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ Telegram bot token or chat ID is missing from .env")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data=payload) as response:
                if response.status != 200:
                    error = await response.text()
                    print(f"❌ Failed to send Telegram message: {error}")
        except Exception as e:
            print(f"❌ Exception while sending Telegram message: {e}")
          
