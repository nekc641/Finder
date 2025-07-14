import random
import asyncio
from discord import Embed, Webhook
from colorama import Fore, Style
import aiohttp
from config import get_webhooks
from datetime import datetime

THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/1394012837575131138/1394108844971393055/Untitled6_20250601183907.png"
AUTHOR_ICON = "https://cdn.discordapp.com/attachments/1394012837575131138/1394109975277600818/Noah_windbreaker.jpg"
AUTHOR_NAME = "**Rekon**"

scan_count = 0

async def groupfinder():
    global scan_count
    webhooks = get_webhooks()

    async with aiohttp.ClientSession() as session:
        while True:
            group_id = random.randint(1000000, 99999999)
            scan_count += 1
            start_time = datetime.now()

            try:
                async with session.get(f"https://groups.roblox.com/v1/groups/{group_id}", timeout=5) as response:
                    if response.status == 404:
                        print(f"{Fore.YELLOW}[-] Group does not exist: {group_id}{Style.RESET_ALL}")
                        await asyncio.sleep(1)
                        continue

                    data = await response.json()
                    group_url = f"https://www.roblox.com/communities/{group_id}"
                    name = data.get("name", "Unknown")
                    description = data.get("description", "No description provided.")
                    members = data.get("memberCount", 0)
                    creation = data.get("created")

                    if len(description) > 200:
                        description = description[:200] + "..."

                    creation_date = "Unknown"
                    if creation:
                        try:
                            creation_date = datetime.fromisoformat(creation.replace("Z", "+00:00")).strftime("%B %d, %Y")
                        except Exception:
                            pass

                    # 🔒 LOCKED
                    if data.get('isLocked'):
                        print(f"{Fore.RED}[-] Group Locked: {group_id}{Style.RESET_ALL}")
                        embed = Embed(
                            title=f"🔒 Locked Group - {name}",
                            description=f"[View Group]({group_url})\n{description}",
                            color=0x8e44ad
                        )
                        embed.set_author(name=AUTHOR_NAME, icon_url=AUTHOR_ICON)
                        embed.set_thumbnail(url=THUMBNAIL_URL)
                        embed.add_field(name="🔗 Group ID", value=str(group_id), inline=True)
                        embed.add_field(name="👥 Members", value=str(members), inline=True)
                        embed.add_field(name="📆 Created", value=creation_date, inline=True)
                        embed.add_field(name="📶 Status", value="🔐 Locked", inline=True)
                        elapsed = datetime.now() - start_time
                        embed.set_footer(text=f"Scan #{scan_count} • Took {elapsed.total_seconds():.2f}s")
                        webhook = Webhook.from_url(webhooks["locked"], session=session)
                        await webhook.send(embed=embed)
                        await asyncio.sleep(random.uniform(2.0, 3.2))
                        continue

                    # 👑 OWNED
                    if data.get('owner') is not None:
                        print(f"{Fore.YELLOW}[-] Group Owned: {group_id}{Style.RESET_ALL}")
                        embed = Embed(
                            title=f"👑 Owned Group - {name}",
                            description=f"[View Group]({group_url})\n{description}",
                            color=0xf1c40f
                        )
                        embed.set_author(name=AUTHOR_NAME, icon_url=AUTHOR_ICON)
                        embed.set_thumbnail(url=THUMBNAIL_URL)
                        embed.add_field(name="🔗 Group ID", value=str(group_id), inline=True)
                        embed.add_field(name="👥 Members", value=str(members), inline=True)
                        embed.add_field(name="📆 Created", value=creation_date, inline=True)
                        embed.add_field(name="📶 Status", value="❌ Claimed", inline=True)
                        elapsed = datetime.now() - start_time
                        embed.set_footer(text=f"Scan #{scan_count} • Took {elapsed.total_seconds():.2f}s")
                        webhook = Webhook.from_url(webhooks["owned"], session=session)
                        await webhook.send(embed=embed)
                        await asyncio.sleep(random.uniform(2.0, 3.2))
                        continue

                    # ✅ HIT (Unclaimed and Joinable)
                    print(f"{Fore.GREEN}[+] HIT: Unclaimed Group ID {group_id}{Style.RESET_ALL}")
                    embed = Embed(
                        title=f"🎯 HIT: {name}",
                        description=f"[Claim This Group Now!]({group_url})\n{description}",
                        color=0x2ecc71
                    )
                    embed.set_author(name=AUTHOR_NAME, icon_url=AUTHOR_ICON)
                    embed.set_thumbnail(url=THUMBNAIL_URL)
                    embed.add_field(name="🔗 Group ID", value=str(group_id), inline=True)
                    embed.add_field(name="👥 Members", value=str(members), inline=True)
                    embed.add_field(name="📆 Created", value=creation_date, inline=True)
                    embed.add_field(name="📶 Status", value="✅ Joinable", inline=True)
                    elapsed = datetime.now() - start_time
                    embed.set_footer(text=f"Scan #{scan_count} • Took {elapsed.total_seconds():.2f}s")
                    webhook = Webhook.from_url(webhooks["hit"], session=session)
                    await webhook.send(content="@here", embed=embed)

            except asyncio.TimeoutError:
                print(f"{Fore.RED}Timeout while checking group {group_id}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

            delay = random.uniform(2.0, 3.0)
            print(f"{Fore.BLUE}[~] Sleeping for {delay:.2f} seconds{Style.RESET_ALL}")
            await asyncio.sleep(delay)

if __name__ == '__main__':
    asyncio.run(groupfinder())
