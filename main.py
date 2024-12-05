import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import fixup
import datetime
import random

# Load environment variables from the .env file (if present) and declare the variable
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = discord.Client(command_prefix='!', intents=intents)

# Set trigger time: Noon PST -> 20:00 UTC (adjust as needed)
utc = datetime.timezone.utc
trigger_time = datetime.time(hour=00, minute=30, tzinfo=utc)

class Victini(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        self.spin_wheel.start()

    @tasks.loop(time=datetime.time(hour=0, minute=11))
    async def spin_wheel(self):
        print("Made it to wheel-spinning!")

    @spin_wheel.before_loop
    async def pre_check(self):
        await self.wait_until_ready()

@bot.event
async def on_ready():
    print(f'{bot.user} has logged into Discord!')
    v_wheel_channel = await bot.fetch_channel(1313952056481939586)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    ## Teeny tini doesn't want to be touched
    if message.content.startswith('!pet'):
        response = random.randrange(1, 13)
        case_dict = {
            1: 'Eep!! >~<',
            2: 'Wh-what? What was that for?',
            3: 'Huh...? Is there something on my head?',
            4: 'Huh? What? ...You\'re weird.',
            5: 'No touchy!! >n<',
            6: 'Thanks, but I\'m not going to let you change the V-wave.',
            7: 'I-I\'m not a pet... >///>',
            8: 'Careful, my fur might burn you!',
            9: '♪',
            10: '*is petted* >///<',
            11: 'Please do not tap on the glass.',
            12: '`Your pet has been forwarded to an automated pet messaging system. 8-4-2-8-4-6-4 is not available. At the tone please record your pet. When you are finished recording you may hang up, or press snoot for more options. *beep*`',
        }
        await message.channel.send(case_dict.get(response, "# ***EXPLODES***"))

@bot.event
async def on_ready():
    print(f"{bot.user} has logged into Discord! Setting up...")
    v_wheel_channel = await bot.fetch_channel(1313952056481939586) # channel id, as an int, goes here
    print(f"Found the {v_wheel_channel} channel, saying hi!")
    # await v_wheel_channel.send("Tadaaaa~! It's me, Victini~!")

# fixup addresses a fatal SSL & authentication bug in Discord.py
fixup.run(bot, DISCORD_TOKEN)
bot.start(DISCORD_TOKEN)

