# Discord Message Summarizer

This project is code for a Discord bot that summarizes messages from specific channels and users and generates a newsletter based on those summaries.

## Features

- Summarizes messages from specified Discord channels and users given a number of days back
- Generates summaries for different types of channels
- Creates a consolidated summary file
- Generates a newsletter based on the summaries
- Uses Claude 3.5 Sonnet for summarization and newsletter generation

## Prerequisites

- Python 3.7+
- Discord Bot Token (You'll need to create a [Discord application](https://discord.com/developers/applications)
- Anthropic API Key
- Poetry (Python package manager)

## Installation

1. Install Poetry:
   Poetry is a dependency management and packaging tool for Python. If you don't have Poetry installed, you can install it by following the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

2. Clone the repository:
   ```
   git clone https://github.com/samjulien/discord-message-summarizer.git
   cd discord-message-summarizer
   ```

3. Install the project dependencies using Poetry:
   ```
   poetry install
   ```

4. Create a `.env` file in the project root and add the following environment variables, changing whatever channels or user ID variables as needed:
   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token
   ANTHROPIC_API_KEY=your_anthropic_api_key
   NEWSLETTER_CHANNEL_ID=your_newsletter_channel_id
   AI_NEWS_CHANNEL_ID=your_ai_news_channel_id
   DEVREL_CHANNEL_ID=your_devrel_channel_id
   SHARE_YOUR_WORK_CHANNEL_ID=your_share_your_work_channel_id
   SAM_USER_ID=sam_user_id
   ```

5. Modify the CHANNELS and USERS variables in `src/discord_message_summarizer.py` to include the channels and users you want to summarize.

6. Modify the prompts to your liking. You may want to change the prompts for different types of channels.

## Usage

Run the script using Poetry:

```bash
poetry run summarize --days=5
```

The bot will:
1. Connect to Discord
2. Fetch messages from specified channels
3. Summarize the messages using Claude 3.5 Sonnet
4. Save the summaries to a file in the `src/summaries` directory
5. Generate a newsletter based on the summaries and save it in the `src/newsletters` directory

## Project Structure

- `src/discord_message_summarizer.py`: Main script containing the Discord bot and summarization logic
- `src/summaries/`: Directory where summary files are saved
- `src/newsletters/`: Directory where generated newsletters are saved
- `pyproject.toml`: Poetry configuration file specifying project dependencies


## License

This project is licensed under the MIT License.