# M365 Nopilot Bot

An automated Discord bot that analyzes and sorts YouTube playlists using local AI. Powered by Ollama and the YouTube Data API v3.

Languages: EN

---

## Features

- **Local AI Classification** — Powered by Ollama (local LLM). Classifies video titles into customizable categories without sending data to third-party clouds.
- **Dynamic Categories** — Define what "Level 1", "Level 2", and "Level 3" mean directly via Discord commands.
- **Bulk Analysis** — Scan multiple playlists simultaneously to see content distribution.
- **Automatic Sorting** — Move videos from a source playlist into target playlists based on AI classification.
- **Privacy First** — All AI processing happens locally on your machine. No user data is stored or transmitted externally.

---

## Commands

### ── General ──

| Command | Description |
|---|---|
| `/ping` | Check bot latency |
| `/about` | Information about the bot and its creator |
| `/help` | List all available commands and their usage |
| `/info` | Show current configuration status (Categories & Levels) |
| `/install_guide` | Step-by-step installation instructions |

### ── Configuration ──

| Command | Description |
|---|---|
| `/set_categories` | Define meanings for Level 1, 2, and 3 |
| `/config_levels` | Set target Playlist IDs for sorting |

### ── Actions ──

| Command | Description |
|---|---|
| `/classify` | Classify a single text string using current categories |
| `/analyze` | Analyze one or more playlists (IDs separated by space) |
| `/sort_playlist` | Sort videos from a source playlist into configured levels |
| `/list_playlists` | List all playlists from your connected YouTube account |

---

## Setup

### Prerequisites

- [Python](https://www.python.org/) 3.10+
- [Ollama](https://ollama.ai/) running locally with a model (default: `llama3.2`)
- A Discord Bot Token ([create one here](https://discord.com/developers/applications))
- A Google Cloud Project with YouTube Data API v3 enabled

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/KaasRijkeTurk/M365-Nopilot.git
cd M365-Nopilot

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install discord.py python-dotenv requests google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### Configuration

#### 1. Discord Token

Create a `.env` file in the root directory and add your Discord bot token:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

#### 2. YouTube API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the **YouTube Data API v3**.
4. Go to **Credentials** > **Create Credentials** > **OAuth client ID**.
5. Select **Desktop app** as the application type.
6. Download the JSON file and rename it to `client_secret.json`.
7. Place `client_secret.json` in the same directory as `bot.py`.

#### 3. Ollama Model

Ensure Ollama is running and you have the required model installed:

```bash
ollama pull llama3.2
ollama serve
```

You can change the model name in `ai.py` if you prefer a different one.

---

## Running the Bot

```bash
python bot.py
```

On first run, the bot will prompt you to authorize access to your YouTube account via a browser window. Complete the OAuth flow to generate `token.json`.

---

## Usage Guide

### 1. Set Categories

Define what each level means for classification:

```
/set_categories cat_1:Basics cat_2:Intermediate cat_3:Advanced
```

### 2. Configure Target Playlists

Set the Playlist IDs where sorted videos should be moved:

```
/config_levels level_1:PLxxx level_2:PLyyy level_3:PLzzz
```

*To find a Playlist ID, go to the playlist URL on YouTube. The ID is the value after `list=`.*

### 3. Analyze or Sort

- **Analyze:** View classifications without moving videos.
  ```
  /analyze PL_source_playlist_id
  ```

- **Sort:** Automatically move videos to target playlists.
  ```
  /sort_playlist PL_source_playlist_id
  ```

---

## Project Structure

```
├── ai.py                 # AI classification logic via Ollama
├── bot.py                # Main Discord bot file
├── youtube.py            # YouTube API interactions
├── config.json           # Stores category and level configurations (auto-generated)
├── token.json            # YouTube OAuth token (auto-generated)
├── .env                  # Environment variables (DO NOT COMMIT)
├── client_secret.json    # YouTube API credentials (DO NOT COMMIT)
└── README.md             # This file
```

---

## Important

- Never commit your `.env`, `client_secret.json`, or `token.json` files — they are included in `.gitignore`.
- Ensure Ollama is running before starting the bot.
- The bot processes up to 50 videos per command execution to prevent timeouts.

---

## License

MIT

---

*Created by [KaasRijkeTurk](https://github.com/KaasRijkeTurk)*
