import os
import random
import asyncio
from discord import Embed, Webhook
from colorama import Fore, Style
import aiohttp
from config import get_webhooks
from datetime import datetime, timedelta, timezone

THUMBNAIL_URL = None  # Custom thumbnail removed, use Roblox group icon instead
scan_count = 0
hit_count = 0
owned_count = 0
locked_count = 0
seen_ids = set()

# Define Manila timezone
MANILA_TZ = timezone(timedelta(hours=8))

# Define ID RANGES
ID_RANGES = [
    (1000000, 5000000),
    (5000001, 10000000),
    (10000001, 99999999)
]
current_range_index = 0

async def groupfinder():
    global scan_count, hit_count, owned_count, locked_count, seen_ids, current_range_index
    webhooks = get_webhooks()

    summary = os.getenv("WEBHOOK_SUMMARY")
    if not summary:
        summary = input("Enter SUMMARY webhook: ")
    webhooks["summary"] = summary

    async with aiohttp.ClientSession() as session:
        while True:
            start_id, end_id = ID_RANGES[current_range_index]
            group_id = random.randint(start_id, end_id)
            current_range_index = (current_range_index + 1) % len(ID_RANGES)

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
                            creation_date = dt.astimezone(MANILA_TZ).strftime("%B %d, %Y")
                        except Exception:
                            pass

                    icon_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={owner_id}&width=150&height=150&format=png" if owner_id else f"https://thumbnails.roblox.com/v1/groups/icons?groupIds={group_id}&size=150x150&format=Png&isCircular=false"

                    # LOCKED
                    if owner_data is None and not data.get('publicEntryAllowed'):
                        print(f"{Fore.MAGENTA}[!] Unclaimed but No Public Entry: {group_id}{Style.RESET_ALL}")
                        embed = Embed(
                            title=f"Locked Group - {name}",
                            description=f"[View Group]({group_url})\n{description}",
                            color=0x8e44ad
                        )
                        embed.set_image(url=icon_url)
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
                        embed.set_author(name=owner_username, icon_url=icon_url)
                        embed.set_image(url=icon_url)
                        embed.add_field(name="Group ID", value=str(group_id), inline=True)
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
                    embed.set_image(url=icon_url)
                    embed.add_field(name="Group ID", value=str(group_id), inline=True)
                    embed.add_field(name="Members", value=str(members), inline=True)
                    embed.add_field(name="Created", value=creation_date, inline=True)
                    embed.add_field(name="Status", value="Joinable", inline=True)
                    elapsed = datetime.now() - start_time
                    embed.set_footer(text=f"Scan #{scan_count} • Took {elapsed.total_seconds():.2f}s")
                    webhook = Webhook.from_url(webhooks["hit"], session=session)
                    await webhook.send(content="@here", embed=embed)
                    hit_count += 1

                    if scan_count % 20 == 0:
                        summary = Embed(
                            title="Group Finder Summary",
                            description=f"Total Scans: {scan_count}\nHits: {hit_count}\nLocked: {locked_count}\nOwned: {owned_count}",
                            color=0x95a5a6
                        )
                        time_now = datetime.now(MANILA_TZ).strftime("%Y-%m-%d %I:%M:%S %p %Z")
                        summary.set_footer(text=f"Last 20 scan summary at {time_now}")
                        stats_webhook = Webhook.from_url(webhooks["summary"], session=session)
                        await stats_webhook.send(embed=summary)

            except asyncio.TimeoutError:
                print(f"{Fore.RED}Timeout while checking group {group_id}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

            delay = random.uniform(2.0, 3.0)
            print(f"{Fore.BLUE}[~] Sleeping for {delay:.2f} seconds{Style.RESET_ALL}")
            await asyncio.sleep(delay)

if __name__ == '__main__':
    asyncio.run(groupfinder())
