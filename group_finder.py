import random
import asyncio
from discord import Embed, Webhook
from colorama import Fore, Style
import aiohttp
from config import get_webhooks

async def groupfinder():
    webhooks = get_webhooks()

    async with aiohttp.ClientSession() as session:
        while True:
            group_id = random.randint(1000000, 99999999)

            try:
                async with session.get(f"https://groups.roblox.com/v1/groups/{group_id}", timeout=5) as response:
                    if response.status == 404:
                        print(f"{Fore.YELLOW}[-] Group does not exist: {group_id}{Style.RESET_ALL}")
                        await asyncio.sleep(1)
                        continue

                    data = await response.json()

                    # 🔒 LOCKED
                    if data.get('isLocked'):
                        print(f"{Fore.RED}[-] Group Locked: {group_id}{Style.RESET_ALL}")
                        await asyncio.sleep(1)
                        continue

                    # 🟡 OWNED
                    if data.get('owner') is not None:
                        print(f"{Fore.YELLOW}[-] Group Owned: {group_id}{Style.RESET_ALL}")
                        embed = Embed(
                            title="🟡 Group Already Owned",
                            description=f"[View Group](https://www.roblox.com/communities/{group_id})",
                            color=0xffcc00
                        )
                        embed.add_field(name="Group ID", value=str(group_id), inline=True)
                        embed.add_field(name="Status", value="❌ Claimed", inline=True)
                        webhook = Webhook.from_url(webhooks["owned"], session=session)
                        await webhook.send(embed=embed)
                        await asyncio.sleep(random.uniform(2.0, 3.2))
                        continue

                    # 🔒 UNCLAIMED BUT NOT JOINABLE
                    if not data.get('publicEntryAllowed'):
                        print(f"{Fore.MAGENTA}[!] Unclaimed but No Public Entry: {group_id}{Style.RESET_ALL}")
                        embed = Embed(
                            title="🔒 Unclaimed Group (Locked)",
                            description=f"[View Group](https://www.roblox.com/communities/{group_id})",
                            color=0xff00ff
                        )
                        embed.add_field(name="Group ID", value=str(group_id), inline=True)
                        embed.add_field(name="Status", value="🚫 Public entry disabled", inline=True)
                        webhook = Webhook.from_url(webhooks["locked"], session=session)
                        await webhook.send(embed=embed)
                        await asyncio.sleep(random.uniform(2.0, 3.2))
                        continue

                    # ✅ HIT (Unclaimed and Joinable)
                    print(f"{Fore.GREEN}[+] HIT: Unclaimed Group ID {group_id}{Style.RESET_ALL}")
                    embed = Embed(
                        title="🔥 Unclaimed Group Found!",
                        description=f"**[Click to View Group](https://www.roblox.com/communities/{group_id})**",
                        color=0x00ff00
                    )
                    embed.add_field(name="Group ID", value=str(group_id), inline=True)
                    embed.add_field(name="Status", value="✅ Joinable", inline=True)
                    webhook = Webhook.from_url(webhooks["hit"], session=session)
                    await webhook.send(embed=embed)

            except asyncio.TimeoutError:
                print(f"{Fore.RED}Timeout while checking group {group_id}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

            delay = random.uniform(2.0, 3.0)
            print(f"{Fore.BLUE}[~] Sleeping for {delay:.2f} seconds{Style.RESET_ALL}")
            await asyncio.sleep(delay)

# Optional standalone test
if __name__ == '__main__':
    asyncio.run(groupfinder())
