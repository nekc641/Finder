import os
import aiohttp
import asyncio

async def send_summary_to_telegram(message: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("❌ Telegram bot token or chat ID is missing.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as resp:
                if resp.status != 200:
                    print(f"❌ Telegram API Error: {resp.status}")
                    response_text = await resp.text()
                    print(f"Response: {response_text}")
    except Exception as e:
        print(f"❌ Failed to send Telegram summary: {e}")
