import os
import random
import asyncio
from discord import Embed, Webhook
from colorama import Fore, Style
import aiohttp
from config import get_webhooks
from datetime import datetime
import pytz

seen_ids = set()
scan_count = 0
hit_count = 0
owned_count = 0
locked_count = 0

PH_TZ = pytz.timezone("Asia/Manila")
ROBLOX_LOGO = "https://upload.wikimedia.org/wikipedia/commons/6/69/Roblox_Logo_2022.svg"

async def groupfinder():
    global scan_count, hit_count, owned_count, locked_count, seen_ids
    webhooks = get_webhooks()

    summary = os.getenv("WEBHOOK_SUMMARY")
    if not summary:
        summary = input("Enter SUMMARY webhook: ")
    webhooks["summary"] = summary

    async with aiohttp.ClientSession() as session:
        while True:
            group_id = random.choice([
                random.randint(1000000, 5000000),
                random.randint(5000001, 10000000),
                random.randint(10000001, 99999999)
            ])

            if group_id in seen_ids:
                print(f"{Fore.CYAN}[=] Duplicate group ID skipped: {group_id}{Style.RESET_ALL}")
                await asyncio.sleep(0.1)
                continue
            seen_ids.add(group_id)

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
                    owner_data = data.get("owner")
                    owner_username = owner_data.get("username") if owner_data else "None"
                    owner_id = owner_data.get("userId") if owner_data else None

                    if len(description) > 200:
                        description = description[:200] + "..."

                    creation_date = "Unknown"
                    if creation:
                        try:
                            dt = datetime.fromisoformat(creation.replace("Z", "+00:00"))
                            creation_date = dt.astimezone(PH_TZ).strftime("%B %d, %Y")
                        except Exception:
                            pass

                    avatar_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={owner_id}&width=150&height=150&format=png" if owner_id else ROBLOX_LOGO

                    # LOCKED
                    if owner_data is None and not data.get('publicEntryAllowed'):
                        print(f"{Fore.MAGENTA}[!] Unclaimed but No Public Entry: {group_id}{Style.RESET_ALL}")
                        embed = Embed(
                            title=f"Locked Group - {name}",
                            description=f"[View Group]({group_url})\n{description}",
                            color=0x8e44ad
                        )
                        embed.set_image(url=ROBLOX_LOGO)
                        embed.add_field(name="Group ID", value=str(group_id), inline=True)
                        embed.add_field(name="Members", value=str(members), inline=True)
                        embed.add_field(name="Created", value=creation_date, inline=True)
                        embed.add_field(name="Status", value="Locked", inline=True)
                        elapsed = datetime.now() - start_time
                        embed.set_footer(text=f"Scan #{scan_count} • Took {elapsed.total_seconds():.2f}s")
                        webhook = Webhook.from_url(webhooks["locked"], session=session)
                        await webhook.send(embed=embed)
                        locked_count += 1
                        await asyncio.sleep(random.uniform(2.0, 3.2))
                        continue

                    # OWNED
                    if owner_data is not None:
                        print(f"{Fore.YELLOW}[-] Group Owned: {group_id}{Style.RESET_ALL}")
                        embed = Embed(
                            title=f"Owned Group - {name}",
                            description=f"[View Group]({group_url})\n{description}",
                            color=0xf1c40f
                        )
                        embed.set_thumbnail(url=avatar_url)
                        embed.add_field(name="Group ID", value=str(group_id), inline=True)
                        embed.add_field(name="Owner", value=owner_username, inline=True)
                        embed.add_field(name="Members", value=str(members), inline=True)
                        embed.add_field(name="Created", value=creation_date, inline=True)
                        embed.add_field(name="Status", value="Claimed", inline=True)
                        elapsed = datetime.now() - start_time
                        embed.set_footer(text=f"Scan #{scan_count} • Took {elapsed.total_seconds():.2f}s")
                        webhook = Webhook.from_url(webhooks["owned"], session=session)
                        await webhook.send(embed=embed)
                        owned_count += 1
                        await asyncio.sleep(random.uniform(2.0, 3.2))
                        continue

                    # HIT
                    print(f"{Fore.GREEN}[+] HIT: Unclaimed Group ID {group_id}{Style.RESET_ALL}")
                    embed = Embed(
                        title=f"HIT: {name}",
                        description=f"[Claim This Group Now!]({group_url})\n{description}",
                        color=0x2ecc71
                    )
                    embed.set_thumbnail(url=ROBLOX_LOGO)
                    embed.add_field(name="Group ID", value=str(group_id), inline=True)
                    embed.add_field(name="Members", value=str(members), inline=True)
                    embed.add_field(name="Created", value=creation_date, inline=True)
                    embed.add_field(name="Status", value="Joinable", inline=True)
                    elapsed = datetime.now() - start_time
                    embed.set_footer(text=f"Scan #{scan_count} • Took {elapsed.total_seconds():.2f}s")
                    webhook = Webhook.from_url(webhooks["hit"], session=session)
                    await webhook.send(content="@here", embed=embed)
                    hit_count += 1

                
                    if scan_count % 5 == 0:
                        summary = Embed(
                            title="Group Finder Summary",
                            description=f"Total Scans: {scan_count}\nHits: {hit_count}\nLocked: {locked_count}\nOwned: {owned_count}",
                            color=0x7289DA
                        )
                        now = datetime.now(PH_TZ)
                        summary.set_thumbnail(url=ROBLOX_LOGO)
                        summary.set_footer(text=f"Updated • {now.strftime('%b %d, %Y %I:%M:%S %p')} PH Time")
                        webhook = Webhook.from_url(webhooks["summary"], session=session)
                        await webhook.send(embed=summary)

            except asyncio.TimeoutError:
                print(f"{Fore.RED}Timeout while checking group {group_id}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

            delay = random.uniform(2.0, 3.0)
            print(f"{Fore.BLUE}[~] Sleeping for {delay:.2f} seconds{Style.RESET_ALL}")
            await asyncio.sleep(delay)

if __name__ == '__main__':
    asyncio.run(groupfinder())
