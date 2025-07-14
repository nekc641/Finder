import os
import random
import asyncio
from discord import Embed, Webhook
from colorama import Fore, Style
import aiohttp
from config import get_webhooks
from datetime import datetime

scan_count = 0
hit_count = 0
owned_count = 0
locked_count = 0
seen_ids = set()

# Weighted ranges: (min, max, weight)
RANGES = [
    (1000000, 4999999, 1),     # older groups
    (5000000, 24999999, 2),    # medium era
    (25000000, 99999999, 4)    # newer groups, higher likelihood
]

def pick_group_id():
    total_weight = sum(weight for _, _, weight in RANGES)
    r = random.uniform(0, total_weight)
    upto = 0
    for low, high, weight in RANGES:
        if upto + weight >= r:
            return random.randint(low, high)
        upto += weight
    return random.randint(1000000, 99999999)

async def groupfinder():
    global scan_count, hit_count, owned_count, locked_count, seen_ids
    webhooks = get_webhooks()

    summary = os.getenv("WEBHOOK_SUMMARY")
    if not summary:
        summary = input("Enter SUMMARY webhook: ")
    webhooks["summary"] = summary

    async with aiohttp.ClientSession() as session:
        while True:
            group_id = pick_group_id()
            if group_id in seen_ids:
                print(f"{Fore.CYAN}[=] Skipped duplicate group ID: {group_id}{Style.RESET_ALL}")
                await asyncio.sleep(0.1)
                continue
            seen_ids.add(group_id)

            scan_count += 1
            start_time = datetime.now()

            try:
                async with session.get(f"https://groups.roblox.com/v1/groups/{group_id}", timeout=5) as response:
                    if response.status == 429:
                        print(f"{Fore.RED}Rate limited by Roblox! Backing off...{Style.RESET_ALL}")
                        await asyncio.sleep(random.uniform(5, 10))
                        continue

                    if response.status == 404:
                        print(f"{Fore.YELLOW}[-] Group does not exist: {group_id}{Style.RESET_ALL}")
                        await asyncio.sleep(1)
                        continue

                    data = await response.json()
                    group_url = f"https://www.roblox.com/communities/{group_id}"
                    name = data.get("name", "Unknown")
                    description = data.get("description", "No description.")
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
                            creation_date = datetime.fromisoformat(creation.replace("Z", "+00:00")).strftime("%B %d, %Y")
                        except Exception:
                            pass

                    avatar_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={owner_id}&width=150&height=150&format=png" if owner_id else None
                    icon_url = data.get("emblemUrl") or "https://tr.rbxcdn.com/9c65a8e927d79e419cb4dc86169d7453/150/150/Image/Png"

                    # 🔒 Locked
                    if owner_data is None and not data.get('publicEntryAllowed'):
                        print(f"{Fore.MAGENTA}[!] Locked group (unclaimable): {group_id}{Style.RESET_ALL}")
                        embed = Embed(
                            title=f"Locked Group - {name}",
                            description=f"[View Group]({group_url})\n{description}",
                            color=0x8e44ad
                        )
                        embed.set_thumbnail(url=icon_url)
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

                    # 🟡 Owned
                    if owner_data:
                        print(f"{Fore.YELLOW}[-] Owned group: {group_id}{Style.RESET_ALL}")
                        embed = Embed(
                            title=f"Owned Group - {name}",
                            description=f"[View Group]({group_url})\n{description}",
                            color=0xf1c40f
                        )
                        embed.set_author(name=owner_username, icon_url=avatar_url or icon_url)
                        embed.set_thumbnail(url=icon_url)
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

                    # ✅ HIT
                    print(f"{Fore.GREEN}[+] HIT: Unclaimed group ID {group_id}{Style.RESET_ALL}")
                    embed = Embed(
                        title=f"HIT: {name}",
                        description=f"[Claim This Group Now!]({group_url})\n{description}",
                        color=0x2ecc71
                    )
                    embed.set_thumbnail(url=icon_url)
                    embed.add_field(name="Group ID", value=str(group_id), inline=True)
                    embed.add_field(name="Members", value=str(members), inline=True)
                    embed.add_field(name="Created", value=creation_date, inline=True)
                    embed.add_field(name="Status", value="Joinable", inline=True)
                    elapsed = datetime.now() - start_time
                    embed.set_footer(text=f"Scan #{scan_count} • Took {elapsed.total_seconds():.2f}s")
                    webhook = Webhook.from_url(webhooks["hit"], session=session)
                    await webhook.send(content="@here", embed=embed)
                    hit_count += 1

                    # 📊 Send summary every 20 scans
                    if scan_count % 20 == 0:
                        summary = Embed(
                            title="Group Finder Summary",
                            description=f"**Scans:** {scan_count}\n**Hits:** {hit_count}\n**Owned:** {owned_count}\n**Locked:** {locked_count}",
                            color=0x95a5a6
                        )
                        summary.set_footer(text=f"Updated • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
                        webhook = Webhook.from_url(webhooks["summary"], session=session)
                        await webhook.send(embed=summary)

            except asyncio.TimeoutError:
                print(f"{Fore.RED}Timeout while checking group {group_id}{Style.RESET_ALL}")
                await asyncio.sleep(random.uniform(5, 8))  # back off on timeout
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                await asyncio.sleep(2)

            await asyncio.sleep(random.uniform(2.0, 3.0))

if __name__ == '__main__':
    asyncio.run(groupfinder())
