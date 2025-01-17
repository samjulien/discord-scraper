import os
from datetime import datetime, timedelta, UTC
import argparse

import discord
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Discord client
intents = discord.Intents.default()
intents.guilds = True  # This allows the bot to access guild data
intents.messages = True  # This allows the bot to read message content
intents.message_content = True
client = discord.Client(intents=intents)

# Channel and User IDs - replace the sample values with your own
CHANNELS = {
    'NEWSLETTER': {
        'id': int(os.getenv('NEWSLETTER_CHANNEL_ID')),
        'users': [int(os.getenv('SAM_USER_ID'))],
        'name': 'Newsletter'
    },
    'AI_CODING': {
        'id': int(os.getenv('AI_CODING_CHANNEL_ID')),
        'users': [int(os.getenv('SAM_USER_ID'))],
        'name': 'AI Coding'
    },
    'AI_NEWS': {
        'id': int(os.getenv('AI_NEWS_CHANNEL_ID')),
        'users': [int(os.getenv('SAM_USER_ID'))],
        'name': 'AI News and Resources'
    },
    'DEVREL': {
        'id': int(os.getenv('DEVREL_CHANNEL_ID')),
        'users': [int(os.getenv('SAM_USER_ID'))],
        'name': 'DevRel'
    },
    'SHARE_YOUR_WORK': {
        'id': int(os.getenv('SHARE_YOUR_WORK_CHANNEL_ID')),
        'users': [int(os.getenv('SAM_USER_ID'))],
        'name': 'Share Your Work'
    }
}

# Set up Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

async def summarize(channel_id: int, user_id: int, channel_name: str, days_back: int = 7):
    channel = client.get_channel(channel_id)
    print(f"Channel: {channel_name}")
    user = await client.fetch_user(user_id)
    print(f"User: {user}")
    
    if not channel:
        print(f"Channel not found.")
        return

    # Calculate the cutoff date
    cutoff_date = datetime.now(UTC) - timedelta(days=days_back)

    # Fetch messages from all users if it's the "Share Your Work" channel, otherwise from the specified user
    messages = []
    async for message in channel.history(limit=100, after=cutoff_date):
        if channel_name == "Share Your Work" or message.author == user:
            messages.append(message.content)
    
    if not messages:
        print(f"No messages found in this channel within the last {days_back} days.")
        return

    # Combine messages into a single string
    messages_text = "\n".join(messages)

    thread_content = []
    threads = channel.threads
    print(f"Threads: {threads}")
    for thread in threads:
        async for message in thread.history(limit=100):
            thread_content.append(message.content)

    threads_text = "\n".join(thread_content)

    print(f"Messages: {messages_text}")
    print(f"Threads: {threads_text}")
    
    # Adjust the prompt based on the channel
    if channel_name == "Share Your Work":
        prompt = f"""Please summarize the following Discord messages and conversation threads from the "Share Your Work" channel:

        <messages>
        {messages_text}
        </messages>

        <threads>
        {threads_text}
        </threads>

        Write the summary in third person, e.g. "User X shared a video about...", and include any links used in the messages. Be sure the links are in Markdown format and include the username where you have it.

        Make the summary for each message a separate paragraph. Do not include any additional commentary at the end.

        """
    else:
        prompt = f"""Please summarize the following Discord messages and conversation threads:

        <messages>
        {messages_text}
        </messages>

        <threads>
        {threads_text}
        </threads>

        Write the summary in first person, e.g. "I watched a video about...", and include any links used in the messages. Be sure the links are in Markdown format.

        Make the summary for each message a separate paragraph. Do not include any additional commentary at the end.

        """

    try:
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response = f"## {channel_name}\n\n{message.content[0].text}"
        return response
    except Exception as e:
        print(f"An error occurred while creating the message: {e}")
        return

def save_summaries(summaries: list):
    # Create the summaries folder if it doesn't exist
    os.makedirs("src/summaries", exist_ok=True)
    
    # Create a filename for all summaries
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"src/summaries/all_summaries_{current_date}.md"
    
    # Write all summaries to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Summaries\n\n")  # Add the h1 header
        f.write("\n\n".join(summaries))
    
    print(f"All summaries saved to {filename}")
    return filename

def generate_newsletter(summaries_file: str):
    print(f"Generating newsletter from {summaries_file}")
    with open(summaries_file, "r", encoding="utf-8") as f:
        summaries_content = f.read()

    prompt = f"""Please turn the following summaries into an issue of the Developer Microskills newsletter by Sam Julien:

    {summaries_content}

    The newsletter should have a friendly, engaging tone. Organize the content into sections based on the headings in the summaries. Add a brief introduction at the beginning and a conclusion at the end. Feel free to add transitions between sections to improve readability.

    The newsletter should be in Markdown format.
    """

    try:
        message = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        newsletter_content = message.content[0].text
        
        # Save the newsletter
        newsletter_filename = summaries_file.replace("all_summaries", "newsletter")
        newsletter_filename = newsletter_filename.replace("src/summaries", "src/newsletters")
        os.makedirs(os.path.dirname(newsletter_filename), exist_ok=True)
        with open(newsletter_filename, "w", encoding="utf-8") as f:
            f.write(newsletter_content)
        
        print(f"Newsletter generated and saved to {newsletter_filename}")
        return newsletter_filename
    except Exception as e:
        print(f"An error occurred while generating the newsletter: {e}")
        return None

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    for guild in client.guilds:
        print(f'Bot is connected to: {guild.name} (id: {guild.id})')

    try:
        summaries = []
        for channel_name, channel_info in CHANNELS.items():
            channel_id = channel_info['id']
            channel_display_name = channel_info['name']
            for user_id in channel_info['users']:
                response = await summarize(channel_id=channel_id, user_id=user_id, channel_name=channel_display_name, days_back=args.days)
                if response:
                    summaries.append(response)
        
        # Save all summaries to a single file
        if summaries:
            summaries_file = save_summaries(summaries)
            # Generate newsletter from summaries
            newsletter_file = generate_newsletter(summaries_file)
            if newsletter_file:
                print(f"Newsletter generated successfully: {newsletter_file}")
            else:
                print("Failed to generate newsletter")
    finally:
        # Close the client after summarization
        print("Closing client")
        await client.close()

def main():
    parser = argparse.ArgumentParser(description="Discord Message Summarizer")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back for messages (default: 7)")
    global args
    args = parser.parse_args()
    
    client.run(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    main()