import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import fixup
import time
import schedule

# Load environment variables from the .env file (if present) and declare the variable
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has logged into Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!pet'):
        await message.channel.send('Eep!! >~<')



fixup.run(client, DISCORD_TOKEN)