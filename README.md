# Skylbot

**Skylbot** is a collaborative Discord bot written in Python. It combines interactive minigames, a virtual economy, collectible characters, and an AI chat command.

> **Status:** Experimental hobby project developed for a community Discord server. Some functionality depends on server-specific configuration and is not intended for turnkey public deployment.

## Features

| Area | Functionality |
| --- | --- |
| **Minigames** | Blackjack, roulette and rock-paper-scissors, including player-versus-player challenges and interactive Discord buttons. |
| **Economy** | Earn and transfer virtual currency, see balances and a leaderboard, or use points to play games and obtain characters. |
| **Collectibles** | Gacha pulls, character rarity and levels, inventories, training, selling, bosses and combat. |
| **AI chat** | Language-model-powered responses with a small in-memory conversation history and a reset command. |
| **Community** | Polls, jokes, welcome messages and utility commands. |
| **HTTP API** | Flask endpoints for user, balance and gacha information. |

## Example commands

The bot uses the prefix `*`:

```text
*guide
*balance
*work
*pay @member 100
*leaderboard

*blackjack 100
*roulette 100 red
*ppt 100
*ppt @member 100

*pull
*inventory
*train 1
*combat
*boss

*ai Tell me something interesting
*clear
```

Some commands require sufficient virtual currency, an inventory item or another player. Use `*guide` to see the currently registered commands.

## Tech stack

**Python · discord.py · SQLite · Flask · Z.ai SDK / GLM**

```text
main.py                 Discord bot and Flask entry point
other_commands.py       Utility and economy commands
juegos/                 Blackjack, roulette, rock-paper-scissors
vicio/                  Collectibles, gacha, inventory and combat
ai/                     AI assistant and conversation history
database/               SQLite persistence and migration utilities
assets/                 Images and other game resources
requirements.txt        Dependencies
```

## Local development

The project requires a configured Discord bot, the corresponding privileged intents and a local SQLite database. Install the declared dependencies in a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Provide the required tokens in an ignored `.env` file:

```dotenv
DISCORD_TOKEN=your_discord_bot_token
AI_TOKEN=your_ai_provider_api_key
```

Once the Discord application, database and integrations are configured, run `python main.py`.

**Development limitations:** The repository does not currently provide a complete first-run database initializer; the migration scripts expect an existing `users` table. Some channel, emoji and role IDs are server-specific. The Flask API exposes user-related information and requires authentication and other security hardening before being made publicly accessible. Never commit API tokens or `bot.db`.

## Contributors

Developed collaboratively by [Alogenes](https://github.com/Alogenes), [nestx0](https://github.com/nestx0), [Parpas16](https://github.com/Parpas16) and . See the [commit history](https://github.com/nestx0/Skylbot/commits/main/) for individual contributions.

Skylbot is a hobby project for exploring Python development, Discord interactions and stateful games.