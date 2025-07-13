from flask import Flask
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import get_webhook_url
from group_finder import groupfinder

app = Flask(__name__)

def start_groupfinder(webhook_url, max_workers):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while True:
            executor.submit(lambda: loop.run_until_complete(groupfinder(webhook_url)))

@app.route('/')
def index():
    return "RoFinder | Roblox Group Finder"

if __name__ == '__main__':
    try:
        os.system("RoGroup Finder" if os.name == "nt" else "printf '\033]2;RXGroup Finder\033\\'")
    except Exception as e:
        print(f"Error setting console title: {e}")

    print("""
     ____  _____  ___  ____  _____  __  __  ____    ____  ____  _  _  ____  ____  ____ 
    (  _ \(  _  )/ __)(  _ \(  _  )(  )(  )(  _ \  ( ___)(_  _)( \( )(  _ \( ___)(  _ \\
     )   / )(_)(( (_-. )   / )(_)(  )(__)(  )___/   )__)  _)(_  )  (  )(_) ))__)  )   /
    (_)\_)(_____)\___/(_)\_)(_____)(______)(__)    (__)  (____)(_)\_)(____/(____)(_)\_)

                 By RXNationGaming
    """)

    hook = get_webhook_url()
    max_workers = 30  # Adjust the number of workers based on your system's capabilities
    start_groupfinder(hook, max_workers)

    app.run(host="0.0.0.0", debug=True, port=8080)
