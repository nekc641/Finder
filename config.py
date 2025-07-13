import os
from dotenv import load_dotenv

load_dotenv()

def get_webhooks():
    hit = os.getenv("WEBHOOK_HIT")
    owned = os.getenv("WEBHOOK_OWNED")
    locked = os.getenv("WEBHOOK_LOCKED")

    if not hit or not owned or not locked:
        print("⚠️ One or more webhooks are missing in .env file.")
        if not hit:
            hit = input("Enter HIT webhook: ")
        if not owned:
            owned = input("Enter OWNED webhook: ")
        if not locked:
            locked = input("Enter LOCKED webhook: ")

    return {
        "hit": hit,
        "owned": owned,
        "locked": locked
    }

def get_thread_count():
    return 99999999999999999
    
