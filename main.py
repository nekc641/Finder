from flask import Flask
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from group_finder import groupfinder  # uses internal webhook config

app = Flask(__name__)

def start_group_finder(max_workers):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while True:
            executor.submit(lambda: loop.run_until_complete(groupfinder()))

@app.route('/')
def index():
    return "RoFinder | Roblox Group Finder"

if __name__ == '__main__':
    try:
        os.system("RoGroup Finder" if os.name == "nt" else "printf '\033]2;RXGroup Finder\033\\'")
    except Exception as e:
        print(f"Error setting console title: {e}")

    print("""
     
______ _____ _   _______ _   _ 
| ___ \  ___| | / /  _  | \ | |
| |_/ / |__ | |/ /| | | |  \| |
|    /|  __||    \| | | | . ` |
| |\ \| |___| |\  \ \_/ / |\  |
\_| \_\____/\_| \_/\___/\_| \_/
                               
          By: @Fin                       

    """)

    max_workers = 2  # safe default for Termux or VPS
    start_group_finder(max_workers)

    # Optional: You can disable Flask if you're not using the web UI
    app.run(host="0.0.0.0", debug=True, port=8080)
