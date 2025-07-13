import requests
import random
import discord
import asyncio
from discord import Embed
from colorama import Fore, Style
import aiohttp
from retrying import retry
from dotenv import load_dotenv
import os

load_dotenv()

async def groupfinder(webhook_url):
    @retry(stop_max_attempt_number=1, wait_fixed=1000)
    def make_request(url):
        return requests.get(url, timeout=1)

    while True:
        group_id = random.randint(10000000, 99999999)
        try:
            r = make_request(f"https://www.roblox.com/groups/group.aspx?gid={group_id}")
            r.raise_for_status()

            if 'owned' not in r.text:
                re = make_request(f"https://groups.roblox.com/v1/groups/{group_id}")
                re.raise_for_status()

                if 'isLocked' not in re.text and 'owner' in re.text:
                    if re.json()['publicEntryAllowed'] and re.json()['owner'] is None:
                        embed = Embed(
                            title="Group Found!",
                            description=f"[Click here to view the group](https://www.roblox.com/groups/group.aspx?gid={group_id})",
                            color=discord.Colour.green()
                        )
                        embed.set_footer(text="RoFinder | By: RXNationGaming")

                        async with aiohttp.ClientSession() as session:
                            webhook = discord.Webhook.from_url(webhook_url, adapter=discord.AsyncWebhookAdapter(session))
                            await webhook.send(embed=embed)

                        print(f"{Fore.GREEN}[+] Hit: {group_id}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[-] No Entry Allowed: {group_id}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[-] Group Locked: {group_id}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[-] Group Already Owned: {group_id}{Style.RESET_ALL}")

        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error making request: {e}{Style.RESET_ALL}")

        await asyncio.sleep(1)

if __name__ == '__main__':
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    if webhook_url is None:
        print("Please set DISCORD_WEBHOOK in your .env file.")
    else:
        asyncio.run(groupfinder(webhook_url))
