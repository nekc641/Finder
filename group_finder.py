import random
import asyncio
from discord import Embed, Webhook
from colorama import Fore, Style
import aiohttp
from config import get_webhook_url  # Your original config.py

async def groupfinder(webhook_url):
    async with aiohttp.ClientSession() as session:
        while True:
            group_id = random.randint(10000000, 99999999)

            try:
                # Fetch group data from Roblox API
                async with session.get(f"https://groups.roblox.com/v1/groups/{group_id}", timeout=5) as response:
                    if response.status == 404:
                        print(f"{Fore.YELLOW}[-] Group does not exist: {group_id}{Style.RESET_ALL}")
                        await asyncio.sleep(1)
                        continue

                    data = await response.json()

                    # Skip locked groups
                    if data.get('isLocked'):
                        print(f"{Fore.RED}[-] Group Locked: {group_id}{Style.RESET_ALL}")
                        await asyncio.sleep(1)
                        continue

                    # Skip owned groups
                    if data.get('owner') is not None:
                        print(f"{Fore.YELLOW}[-] Group Owned: {group_id}{Style.RESET_ALL}")
                        await asyncio.sleep(1)
                        continue

                    # Skip groups that don't allow public entry
                    if not data.get('publicEntryAllowed'):
                        print(f"{Fore.RED}[-] Public Entry Not Allowed: {group_id}{Style.RESET_ALL}")
                        await asyncio.sleep(1)
                        continue

                    # Valid group found
                    embed = Embed(
                        title="Unclaimed Group Found!",
                        description=f"[Click here to view the group](https://www.roblox.com/communities/{group_id})",
                        color=0x00ff00
                    )
                    embed.set_footer(text="RoFinder | By: RXNationGaming")

                    webhook = Webhook.from_url(webhook_url, session=session)
                    await webhook.send(embed=embed)

                    print(f"{Fore.GREEN}[+] HIT: Group ID {group_id}{Style.RESET_ALL}")

            except asyncio.TimeoutError:
                print(f"{Fore.RED}Timeout while checking group {group_id}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

            await asyncio.sleep(1)  # Sleep to avoid rate limits

if __name__ == '__main__':
    webhook_url = get_webhook_url()
    if webhook_url:
        asyncio.run(groupfinder(webhook_url))
