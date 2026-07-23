import os
import re
import json
import discord
from discord import app_commands
from dotenv import load_dotenv

from ai import classify_text
from youtube import (
    get_youtube,
    get_playlist_items_full,
    add_to_playlist
)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# -------------------
# CONFIGURATION FILE HANDLING
# -------------------
CONFIG_FILE = "config.json"

def load_config():
    """Loads configuration from config.json or returns defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                # Ensure backward compatibility
                if "categories" not in data:
                    data["categories"] = {
                        "1": "basics",
                        "2": "understanding",
                        "3": "debates"
                    }
                if "levels" not in data:
                    data["levels"] = {"level_1": "", "level_2": "", "level_3": ""}
                return data
        except Exception:
            pass
    return {
        "categories": {
            "1": "basics (introductory concepts)",
            "2": "understanding (detailed explanations)",
            "3": "debates (arguments and controversies)"
        },
        "levels": {"level_1": "", "level_2": "", "level_3": ""}
    }

def save_config(config):
    """Saves configuration to config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Load config on startup
BOT_CONFIG = load_config()

# -------------------
# INTENTS
# -------------------
intents = discord.Intents.default()

# -------------------
# HELPERS
# -------------------
def clean_playlist_id(value: str) -> str:
    """Extracts playlist ID from URL or raw string."""
    match = re.search(r"list=([a-zA-Z0-9_-]+)", value)
    if match:
        return match.group(1)
    if "&" in value:
        return value.split("&").strip()
    return value.strip()

def safe_send_list(results_list: list, max_chars: int = 1900) -> list:
    """Splits a list of strings into chunks that fit within Discord's message limit."""
    chunks = []
    current_chunk = []
    current_length = 0
    
    for line in results_list:
        if current_length + len(line) + 1 > max_chars:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = len(line)
        else:
            current_chunk.append(line)
            current_length += len(line) + 1
            
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    return chunks

# -------------------
# BOT CLIENT
# -------------------
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot online as {self.user}")
        print(f"CATEGORIES: {BOT_CONFIG['categories']}")
        print(f"LEVELS: {BOT_CONFIG['levels']}")

client = MyClient()

# -------------------
# COMMANDS
# -------------------

@client.tree.command(name="ping", description="Check latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong. Latency: {round(client.latency * 1000)}ms")

@client.tree.command(name="about", description="Information about the bot and its creator")
async def about_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="M365 Nopilot Bot", color=discord.Color.dark_blue())
    embed.description = (
        "An automated YouTube playlist organizer powered by local AI.\n\n"
        "This bot analyzes video titles using Large Language Models (via Ollama) "
        "to classify content into customizable categories. It can then automatically "
        "sort videos into designated playlists based on these classifications.\n\n"
        "**Features:**\n"
        "- Local AI processing (Privacy-focused)\n"
        "- Bulk playlist analysis\n"
        "- Automatic sorting via YouTube Data API\n"
        "- Customizable classification criteria\n\n"
        "**Created by:** KaasRijkeTurk\n"
        "**Repository:** https://github.com/KaasRijkeTurk/M365-Nopilot"
    )
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="help", description="List all available commands and their usage")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="Command List", color=discord.Color.blue())
    
    embed.add_field(name="/ping", value="Checks bot latency.", inline=False)
    embed.add_field(name="/about", value="Displays bot information and credits.", inline=False)
    embed.add_field(name="/info", value="Shows current configuration status (Categories & Levels).", inline=False)
    embed.add_field(name="/install_guide", value="Step-by-step installation instructions for Windows/Linux.", inline=False)
    
    embed.add_field(name="Configuration:", value="", inline=False)
    embed.add_field(name="/set_categories", value="Define meanings for Level 1, 2, and 3.\nUsage: /set_categories cat_1:Basic cat_2:Intermediate cat_3:Advanced", inline=False)
    embed.add_field(name="/config_levels", value="Set target Playlist IDs for sorting.\nUsage: /config_levels level_1:PLxxx level_2:PLyyy level_3:PLzzz", inline=False)
    
    embed.add_field(name="Actions:", value="", inline=False)
    embed.add_field(name="/classify", value="Classify a single text string.\nUsage: /classify text:Your text here", inline=False)
    embed.add_field(name="/analyze", value="Analyze one or more playlists (IDs separated by space).\nUsage: /analyze PLid1 PLid2", inline=False)
    embed.add_field(name="/sort_playlist", value="Sort videos from a source playlist into configured levels.\nUsage: /sort_playlist PL_source_id", inline=False)
    embed.add_field(name="/list_playlists", value="List all playlists from your connected YouTube account.", inline=False)
    
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="install_guide", description="Installation guide for Windows/Linux users")
async def install_guide(interaction: discord.Interaction):
    guide = (
        "**Installation Guide**\n\n"
        "**1. Prerequisites**\n"
        "- Python 3.10+\n"
        "- Ollama installed (https://ollama.ai)\n"
        "- Run `ollama pull llama3.2` in terminal\n\n"
        "**2. Install Dependencies**\n"
        "`pip install discord.py python-dotenv requests google-api-python-client google-auth-oauthlib google-auth-httplib2`\n\n"
        "**3. YouTube API Setup**\n"
        "- Create project at Google Cloud Console\n"
        "- Enable YouTube Data API v3\n"
        "- Create OAuth 2.0 Client ID (Desktop App)\n"
        "- Download `client_secret.json` to bot directory\n\n"
        "**4. Discord Token**\n"
        "- Create `.env` file with: `DISCORD_TOKEN=your_token`\n\n"
        "**5. Configuration**\n"
        "- Use `/set_categories` to define classification rules\n"
        "- Use `/config_levels` to set target playlist IDs\n\n"
        "**6. Start Bot**\n"
        "- Linux/Mac: `python3 bot.py`\n"
        "- Windows: `python bot.py`"
    )
    await interaction.response.send_message(guide)

@client.tree.command(name="info", description="Show current bot configuration status")
async def info_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Configuration Status", color=discord.Color.green())
    
    # Show configured categories
    cats = BOT_CONFIG['categories']
    cat_str = "\n".join([f"L{k}: {v}" for k, v in cats.items()])
    embed.add_field(name="Classification Categories", value=cat_str, inline=False)
    
    # Show level config status
    levels = BOT_CONFIG['levels']
    l1_status = "Configured" if levels["level_1"] else "Not Set"
    l2_status = "Configured" if levels["level_2"] else "Not Set"
    l3_status = "Configured" if levels["level_3"] else "Not Set"
    
    embed.add_field(name="Sorting Targets", value=f"L1: {l1_status}\nL2: {l2_status}\nL3: {l3_status}", inline=False)
    
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="set_categories", description="Define what Level 1, 2, and 3 mean for classification")
async def set_categories(interaction: discord.Interaction, cat_1: str, cat_2: str, cat_3: str):
    await interaction.response.defer()
    
    # Update config
    BOT_CONFIG['categories'] = {
        "1": cat_1.lower(),
        "2": cat_2.lower(),
        "3": cat_3.lower()
    }
    save_config(BOT_CONFIG)
    
    await interaction.followup.send(
        f"Categories updated successfully.\n"
        f"- Level 1: {cat_1}\n"
        f"- Level 2: {cat_2}\n"
        f"- Level 3: {cat_3}"
    )

@client.tree.command(name="config_levels", description="Set the YouTube Playlist IDs for sorting targets")
async def config_levels(interaction: discord.Interaction, level_1: str = None, level_2: str = None, level_3: str = None):
    await interaction.response.defer()
    
    if not level_1 and not level_2 and not level_3:
        await interaction.followup.send("Provide at least one level ID.\nExample: /config_levels level_1:PLxxx level_2:PLyyy")
        return

    if level_1: BOT_CONFIG["levels"]["level_1"] = clean_playlist_id(level_1)
    if level_2: BOT_CONFIG["levels"]["level_2"] = clean_playlist_id(level_2)
    if level_3: BOT_CONFIG["levels"]["level_3"] = clean_playlist_id(level_3)
    
    save_config(BOT_CONFIG)
    
    msg = "Sorting targets updated:\n"
    msg += f"- Level 1: {BOT_CONFIG['levels']['level_1'] or 'Not Set'}\n"
    msg += f"- Level 2: {BOT_CONFIG['levels']['level_2'] or 'Not Set'}\n"
    msg += f"- Level 3: {BOT_CONFIG['levels']['level_3'] or 'Not Set'}"
    
    await interaction.followup.send(msg)

@client.tree.command(name="classify", description="Classify a specific text using current categories")
async def classify(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    try:
        level = classify_text(text, categories=BOT_CONFIG['categories'])
        label = BOT_CONFIG['categories'].get(level, "Unknown")
        await interaction.followup.send(f"Result: Level {level} ({label})")
    except Exception as e:
        await interaction.followup.send(f"Error: {e}")

@client.tree.command(name="analyze", description="Analyze one or more playlists (IDs separated by space)")
async def analyze(interaction: discord.Interaction, playlist_ids: str):
    await interaction.response.defer()
    try:
        raw_inputs = playlist_ids.split()
        if not raw_inputs:
            await interaction.followup.send("No playlist IDs found.")
            return

        youtube = get_youtube()
        all_results = []
        total_playlists = len(raw_inputs)
        status_msg = await interaction.followup.send(f"Analyzing {total_playlists} playlist(s)...")

        for i, raw_input in enumerate(raw_inputs):
            clean_id = clean_playlist_id(raw_input)
            
            if i % 5 == 0 and i > 0:
                await status_msg.edit(content=f"Processing playlist {i}/{total_playlists}...")

            playlist_name = f"ID: {clean_id}"
            try:
                pl_request = youtube.playlists().list(part="snippet", id=clean_id)
                pl_res = pl_request.execute()
                items = pl_res.get('items', [])
                if items and len(items) > 0:
                    title = items.get('snippet', {}).get('title')
                    if title: playlist_name = title
            except Exception:
                pass

            try:
                videos = get_playlist_items_full(youtube, clean_id)
            except Exception as e:
                all_results.append(f"Playlist: {playlist_name}\nFailed to load.\n")
                continue
            
            if not videos:
                all_results.append(f"Playlist: {playlist_name}\nEmpty.\n")
                continue

            playlist_lines = [f"Playlist: {playlist_name}"]
            scanned_count = 0
            
            for v in videos[:50]:
                title = v.get("title", "No Title")
                if "deleted" in title.lower(): continue
                
                level = classify_text(title, categories=BOT_CONFIG['categories'])
                label = BOT_CONFIG['categories'].get(level, "?")
                
                title_short = title[:50] + "..." if len(title) > 50 else title
                playlist_lines.append(f"- {title_short} -> L{level} ({label})")
                scanned_count += 1
            
            playlist_lines.append(f"({scanned_count} videos analyzed)\n")
            all_results.extend(playlist_lines)

        full_report = "\n".join(all_results)
        if len(full_report) > 1900:
             lines = full_report.split('\n')
             chunks = safe_send_list(lines, max_chars=1800)
             await status_msg.edit(content="Analysis Complete.")
             for chunk in chunks:
                 await interaction.followup.send(chunk)
        else:
             await status_msg.edit(content=f"Analysis Complete.\n\n{full_report}")

    except Exception as e:
        await interaction.followup.send(f"Analysis error: {e}")

@client.tree.command(name="sort_playlist", description="Sort videos into configured level playlists")
async def sort_playlist(interaction: discord.Interaction, playlist_id: str):
    await interaction.response.defer()

    levels = BOT_CONFIG["levels"]
    if not levels["level_1"] or not levels["level_2"] or not levels["level_3"]:
        await interaction.followup.send("Error: Sorting targets not configured.\nUse /config_levels to set Level 1, 2, and 3 playlists.")
        return

    try:
        youtube = get_youtube()
        clean_id = clean_playlist_id(playlist_id)
        items = get_playlist_items_full(youtube, clean_id)

        if not items:
            await interaction.followup.send("No videos found.")
            return

        results = []
        status_msg = await interaction.followup.send(f"Sorting up to 50 videos...")

        lvl1 = levels["level_1"]
        lvl2 = levels["level_2"]
        lvl3 = levels["level_3"]

        for item in items[:50]:
            title = item["title"]
            video_id = item["video_id"]

            level = classify_text(title, categories=BOT_CONFIG['categories'])

            if level == "1": target = lvl1
            elif level == "2": target = lvl2
            else: target = lvl3

            try:
                add_to_playlist(youtube, target, video_id)
                label = BOT_CONFIG['categories'].get(level, "")
                results.append(f"[OK] {title[:40]}... -> L{level} ({label})")
            except Exception as e:
                results.append(f"[FAIL] {title[:40]}... Error: {str(e)[:20]}")

        chunks = safe_send_list(results)
        await status_msg.edit(content="Sorting Complete.")
        for chunk in chunks:
            await interaction.followup.send(chunk)

    except Exception as e:
        await interaction.followup.send(f"Sort error: {e}")

@client.tree.command(name="list_playlists", description="List all playlists from your connected YouTube account")
async def list_playlists(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        youtube = get_youtube()
        request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
        response = request.execute()
        
        results = []
        for item in response.get('items', []):
            title = item['snippet']['title']
            pid = item['id']
            results.append(f"- {title} ({pid})")
            
        if not results:
            await interaction.followup.send("No playlists found.")
            return
            
        output = "Your Playlists:\n" + "\n".join(results)
        
        if len(output) > 1900:
            chunks = safe_send_list(output.split('\n'), max_chars=1800)
            await interaction.followup.send(chunks)
            for c in chunks[1:]:
                await interaction.followup.send(c)
        else:
            await interaction.followup.send(output)
            
    except Exception as e:
        await interaction.followup.send(f"Error: {e}")

# -------------------
# RUN
# -------------------
if not TOKEN:
    raise ValueError("DISCORD_TOKEN missing in .env")

client.run(TOKEN)
