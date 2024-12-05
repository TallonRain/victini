import os
import sys
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import fixup
import datetime
from zoneinfo import ZoneInfo
import random

# Load environment variables from the .env file (if present) and declare the variable
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Check to see if we are in debug mode or not
gettrace = getattr(sys, 'gettrace', None)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Set trigger time: Noon PST -> 20:00 UTC (adjust as needed)
pacific = ZoneInfo("America/Los_Angeles")
trigger_time = datetime.time(hour=9, minute=00, tzinfo=pacific)
v_wheel_channel = None

# list of server roles
type_roles = {}
const_types = ["Normal Type", "Fire Type", "Water Type", "Grass Type", "Electric Type", "Ice Type", "Fighting Type", "Poison Type", "Ground Type", "Flying Type", "Psychic Type", "Bug Type", "Rock Type", "Ghost Type", "Dragon Type", "Dark Type", "Steel Type", "Fairy Type"]

async def setup_hook(self) -> None:
    self.spin_wheel.start()

@tasks.loop(time=trigger_time)
async def spin_wheel():
    print("Activating the V-Wheel!!")
    # need to iterate through the roles so that the previous winner can be dehoisted automatically
    for role in bot.guilds[0].roles:
        if role.name in const_types:
            await role.edit(hoist=False)
    await v_wheel_channel.send("https://i.imgur.com/3EZpMlF.gif")
    await v_wheel_channel.send("It's time to spin the V-Wheeeeeeeeeeeeeeeel!")
    vwheel_type = random.choice(const_types) # spiiiiiinnnnnnn
    await v_wheel_channel.send(f"Today's V-Wave type is... {vwheel_type}! Go say hi to the lucky {vwheel_type} types!")
    role_id = type_roles.get(vwheel_type) # fetch the roleID of the winner
    role = bot.guilds[0].get_role(role_id) # format it as a Discord object so it can be manipulated
    if role is not None:
        print("Fetched the role ID successfully")
        await role.edit(hoist=not role.hoist) # inverts the current setting
    else:
        print("Error fetching server roles, cannot hoist the v-wheel winner")

@bot.event
async def on_ready():
    print(f'{bot.user} has logged into Discord!')

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
    global v_wheel_channel
    print(f"{bot.user} has logged into Discord! Setting up...")
    spin_wheel.start()
    v_wheel_channel = await bot.fetch_channel(1302838580443615332) # channel id, as an int, goes here
    print(f"Found the {v_wheel_channel} channel, saying hi!")
    if gettrace is None:
        await v_wheel_channel.send("Tadaaaa~! It's me, Victini~!")
    for role in bot.guilds[0].roles:
        type_roles[role.name] = role.id # fetch the server's roles and put them in a dictionary with the name and ID
        print(f"Role Name: {role.name} | Role ID: {role.id}")

# fixup addresses a fatal SSL & authentication bug in Discord.py
fixup.run(bot, DISCORD_TOKEN)

