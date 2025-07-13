import random
import asyncio
from discord import Embed, Webhook
from colorama import Fore, Style
import aiohttp
from config import get_webhook_url

async def groupfinder(webhook_url):
    async with aiohttp.ClientSession() as session:
        while True:
            group_id = random.randint(10000000, 99999999)

            try:
                async with session.get(f"https://groups.roblox.com/v1/groups/{group_id}", timeout=5) as response:
                    if response.status == 404:
                        print(f"{Fore.YELLOW}[-] Group does not exist: {group_id}{Style.RESET_ALL}")
                        await asyncio.sleep(1)
                        continue

                    data = await response.json()

                    # Handle locked groups
                    if data.get('isLocked'):
                        print(f"{Fore.RED}[-] Group Locked: {group_id}{Style.RESET_ALL}")
                        await asyncio.sleep(1)
                        continue

                    # Handle already owned groups (SEND WEBHOOK)
                    if data.get('owner') is not None:
                        print(f"{Fore.YELLOW}[-] Group Owned: {group_id}{Style.RESET_ALL}")

                        embed = Embed(
                            title="Group Already Owned",
                            description=f"[View Group](https://www.roblox.com/communities/{group_id})",
                            color=0xffcc00
                        )
                        embed.set_footer(text="RoFinder | By: RXNationGaming")

                        webhook = Webhook.from_url(webhook_url, session=session)
                        await webhook.send(embed=embed)

                        await asyncio.sleep(random.uniform(3.5, 6.5))
                        continue

                    # Handle groups without public entry
                    if not data.get('publicEntryAllowed'):
                        print(f"{Fore.RED}[-] Public Entry Not Allowed: {group_id}{Style.RESET_ALL}")
                        await asyncio.sleep(random.uniform(3.5, 6.5))
                        continue

                    # Unclaimed group found!
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

            # Sleep between checks to avoid rate limiting
            delay = random.uniform(3.5, 6.5)
            print(f"{Fore.BLUE}[~] Sleeping for {delay:.2f} seconds{Style.RESET_ALL}")
            await asyncio.sleep(delay)

if __name__ == '__main__':
    webhook_url = get_webhook_url()
    if webhook_url:
        asyncio.run(groupfinder(webhook_url))
    
