from flask import Flask
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import get_webhook_url
from groupfinder import groupfinder

app = Flask(__name__)

def start_groupfinder(webhook_url, max_workers):
    # Each thread runs its own event loop
    def runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(groupfinder(webhook_url))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _ in range(max_workers):
            executor.submit(runner)

@app.route('/')
def index():
    return "RoFinder | Roblox Group Finder is running."

if __name__ == '__main__':
    try:
        if os.name == "nt":
            os.system("title RoGroup Finder")
        else:
            print("\033]2;RXGroup Finder\007", end="")  # Linux/macOS title set
    except Exception as e:
        print(f"Error setting console title: {e}")

    print(r"""
     ____  _____  ___  ____  _____  __  __  ____    ____  ____  _  _  ____  ____  ____ 
    (  _ \(  _  )/ __)(  _ \(  _  )(  )(  )(  _ \  ( ___)(_  _)( \( )(  _ \( ___)(  _ \\
     )   / )(_)(( (_-. )   / )(_)(  )(__)(  )___/   )__)  _)(_  )  (  )(_) ))__)  )   /
    (_)\_)(_____)\___/(_)\_)(_____)(______)(__)    (__)  (____)(_)\_)(____/(____)(_)\_)

                 By RXNationGaming
    """)

    # Load webhook and start thread workers
    webhook_url = get_webhook_url()
    max_workers = 30  # Adjust this based on your CPU and connection

    # Start group finder in background threads
    start_groupfinder(webhook_url, max_workers)

    # Start Flask app (status page)
    app.run(host="0.0.0.0", port=8080, debug=False)
