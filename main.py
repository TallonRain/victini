import os
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import fixup
import datetime
from zoneinfo import ZoneInfo
import random
import secrets

# Load environment variables from the .env file (if present) and declare the variable
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
VWHEEL_CHANNEL_ID = int(os.getenv('VWHEEL_CHANNEL_ID'))
DEBUG_MODE = bool(int(os.getenv('DEBUG_MODE')))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents, activity=discord.Game("with the V-Wheeeeeel~!"))

# Set trigger time
pacific = ZoneInfo("America/Los_Angeles")
trigger_time = datetime.time(hour=9, minute=00, tzinfo=pacific)
v_wheel_channel = None

# list of server roles
type_roles = {}
const_types = ["Normal Type", "Fire Type", "Water Type", "Grass Type", "Electric Type", "Ice Type", "Fighting Type", "Poison Type", "Ground Type", "Flying Type", "Psychic Type", "Bug Type", "Rock Type", "Ghost Type", "Dragon Type", "Dark Type", "Steel Type", "Fairy Type"]
wavecast = []

# wavecast functions
def generate_wavecast():
    for i in range(7):
        next_type = ""
        while next_type == "" or next_type in wavecast:
            next_type = random.choice(const_types)
        wavecast.append(next_type)
    print(f"Wavecast generated: {wavecast}\nAttempting save...")
    # save generated wavecast to a file
    save_wavecast()

def save_wavecast():
    with open("wavecast.vwheel", "w") as file:
        for item in wavecast:
            file.write(f"{item},")
    file.close()
    print("Wavecast saved!")

def load_wavecast():
    loaded_wavecast = []
    with open("wavecast.vwheel", "r") as file:
        loaded_wavecast = file.read().split(",", 6)
    file.close()
    loaded_wavecast[-1] = loaded_wavecast[-1].rstrip(",")
    print(f"Wavecast loaded: {loaded_wavecast}")
    return loaded_wavecast

def cycle_wavecast():
    next_type = ""
    while next_type == "" or next_type in wavecast:
        next_type = random.choice(const_types)
    wavecast.append(next_type)
    return wavecast.pop(0)

# async bot functions
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
    vwheel_type = cycle_wavecast() # spiiiiiinnnnnnn
    await v_wheel_channel.send(f"Today's V-Wave type is... {vwheel_type}! Go say hi to the lucky {vwheel_type}s!")
    role_id = type_roles.get(vwheel_type) # fetch the roleID of the winner
    role = bot.guilds[0].get_role(role_id) # format it as a Discord object so it can be manipulated
    if role is not None:
        print("Fetched the role ID successfully")
        await role.edit(hoist=not role.hoist) # inverts the current setting
    else:
        print("Error fetching server roles, cannot hoist the V-Wheel winner")
    save_wavecast()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!spin'):
        await message.channel.send('Let\'s spin the V-Wheee- oh, you don\'t have any <:poke:1317397305615323196>? Can\'t spin it, then.')

    if message.content.startswith('!wavecast'):
        poke_type = random.choice(const_types)
        await message.channel.send(f"Here's the V-Wavecast! Tomorrow's V-Wave is {poke_type}! Probably. Maybe.")

    ## Teeny tini doesn't want to be touched
    if message.content.startswith('!pet'):
        response = random.randrange(1, 15)
        case_dict = {
            1: 'Eep!! >~<',
            2: 'Wh-what? What was that for?',
            3: 'Huh...? Is there something on my head?',
            4: 'Huh? What? ...You\'re weird.',
            5: 'No touchy!! >n<',
            6: 'Thanks, but I\'m not going to let you change the V-Wave. Definitely.',
            7: 'I-I\'m not a pet... >///>',
            8: 'Careful, my fur might burn you!',
            9: '♪',
            10: '*squeak* /)~(\\',
            11: 'Hey, you could instead try spinning the V-Wheel!',
            12: 'Are you looking for the V-Wavecast? Maybe?',
            13: await explosion_response(),
            14: 'O-Oh, okay...',
        }
        await message.channel.send(case_dict.get(response, "# ***EXPLODES***"))

async def explosion_response():
    result = random.randint(1, 2)
    if result == 1:
        return "# ***EXPLODES***"
    else:
        return "<a:VictiniPet:1317408257652031580>"

@bot.event
async def on_ready():
    global v_wheel_channel
    print(f"{bot.user} has logged into Discord! Setting up...")
    if os.path.isfile("wavecast.vwheel"):
        wavecast.extend(load_wavecast())
    else:
        generate_wavecast()
    spin_wheel.start()
    v_wheel_channel = await bot.fetch_channel(VWHEEL_CHANNEL_ID) # channel id, as an int, goes here
    print(f"Found the {v_wheel_channel} channel, saying hi!")
    if not DEBUG_MODE: # only send this message when we are NOT in debug mode
        await v_wheel_channel.send("Tadaaaa~! It's me, Victini~!")
    for role in bot.guilds[0].roles:
        type_roles[role.name] = role.id # fetch the server's roles and put them in a dictionary with the name and ID
        print(f"Role Name: {role.name} | Role ID: {role.id}")
    await bot.tree.sync() # update app_command related stuff on discord's end, but it's sometimes slow

@bot.tree.command(name = "forcespin")
@app_commands.default_permissions()
async def forcespin(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    await spin_wheel()
    await interaction.edit_original_response(content = "Fine, I've spun the V-Wheeeeeel~!")

@bot.tree.command(name = "wavecast")
@app_commands.default_permissions()
async def show_wavecast(interaction:discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    wavecast_message = f"# Wavecast\n"
    for i in range(len(wavecast)):
        wavecast_message += f"{i+1}. {wavecast[i]}\n"
    wavecast_message.rstrip()
    await interaction.edit_original_response(content = wavecast_message)

# fixup addresses a fatal SSL & authentication bug in Discord.py
fixup.run(bot, DISCORD_TOKEN)

