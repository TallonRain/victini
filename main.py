import os
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
VWHEEL_CHANNEL_ID = int(os.getenv('VWHEEL_CHANNEL_ID'))
DEBUG_MODE = bool(int(os.getenv('DEBUG_MODE')))
FILE_STORAGE = os.getenv('FILE_STORAGE')

intents = discord.Intents.all()

bot = discord.Bot(command_prefix='!', intents=intents, activity=discord.Game("with the V-Wheeeeeel~!"),
                  application_commands=True)

# Set trigger time
pacific = ZoneInfo("America/Los_Angeles")
trigger_time = datetime.time(hour=9, minute=00, tzinfo=pacific)
v_wheel_channel = None

# list of server roles
type_roles = {}
const_types = ["Normal Type", "Fire Type", "Water Type", "Grass Type", "Electric Type", "Ice Type", "Fighting Type",
               "Poison Type", "Ground Type", "Flying Type", "Psychic Type", "Bug Type", "Rock Type", "Ghost Type",
               "Dragon Type", "Dark Type", "Steel Type", "Fairy Type"]
wavecast = {"bag": None, "queue": None}  # filled with lists later!


# wavecast functions
def generate_wavecast():
    wavecast["bag"] = const_types.copy()  # fill the bag!
    wavecast["queue"] = []
    for _ in range(7):
        index = random.randint(0, len(wavecast["bag"]) - 1)  # grab a random index from the bag!
        next_type = wavecast["bag"].pop(index)  # grab the type from the random index!
        wavecast["queue"].append(next_type)  # add it to the queue
    print(f"Wavecast generated: {wavecast}\nAttempting save...")
    # save generated wavecast to a file
    save_wavecast()


def save_wavecast():
    with open(FILE_STORAGE + "wavecast.vwheel", "w") as file:
        for item in wavecast["queue"]:  # save the queue first! always 7 elements
            file.write(f"{item},")
        for item in wavecast["bag"]:  # save the bag next! variable number of elements (0 <= len(bag) <= 11)
            file.write(f"{item},")
    # ending the "with open()" block auto-closes the file, no need to manually close
    print("Wavecast saved!")


def load_wavecast():
    loaded_wavecast = None
    with open("wavecast.vwheel", "r") as file:
        loaded_wavecast = file.read().rstrip(",").split(",")  # read both bag and queue!
    wavecast["queue"] = loaded_wavecast[:7]  # slice off the first seven elements for the queue
    wavecast["bag"] = loaded_wavecast[7:]  # slice the rest for the queue

    # a wavecast is deemed corrupt if:
    # - the queue is not exactly seven elements long
    # - the wavecast has a type that doesn't exist (not in const_types)
    if (len(wavecast["queue"]) == 7 and \
            all(t in const_types for t in wavecast["queue"] + wavecast["bag"])):
        # all checks clear!
        print(f"Wavecast loaded: {wavecast}")
    else:
        print("Huh? The Wavecast file was corrupt... whatever! Generating a new Wavecast!")
        generate_wavecast()
    return


def cycle_wavecast():
    if len(wavecast["bag"]) == 0:  # is bag empty?
        wavecast["bag"].extend(const_types)  # fill the bag!
    index = random.randint(0, len(wavecast["bag"]) - 1)  # grab a random index from the bag!
    next_type = wavecast["bag"].pop(index)  # grab the type from the random index!
    wavecast["queue"].append(next_type)  # add it to the queue
    # queue now has 8 elements! pop to reduce it back to 7
    return wavecast["queue"].pop(0)


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
    vwheel_type = cycle_wavecast()  # spiiiiiinnnnnnn
    await v_wheel_channel.send(f"Today's V-Wave type is... {vwheel_type}! Go say hi to the lucky {vwheel_type}s!")
    role_id = type_roles.get(vwheel_type)  # fetch the roleID of the winner
    role = bot.guilds[0].get_role(role_id)  # format it as a Discord object so it can be manipulated
    if role is not None:
        print("Fetched the role ID successfully")
        await role.edit(hoist=not role.hoist)  # inverts the current setting
    else:
        print("Error fetching server roles, cannot hoist the V-Wheel winner")
    save_wavecast()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!spin'):
        await message.channel.send(
            'Let\'s spin the V-Wheee- oh, you don\'t have any <:poke:1317397305615323196>? Can\'t spin it, then.')

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
    if DEBUG_MODE:
        print("DEBUG MODE ENABLED")
    global v_wheel_channel
    print(f"{bot.user} has logged into Discord! Setting up...")
    if os.path.isfile("wavecast.vwheel"):
        load_wavecast()
    else:
        generate_wavecast()
    spin_wheel.start()
    v_wheel_channel = await bot.fetch_channel(VWHEEL_CHANNEL_ID)  # channel id, as an int, goes here
    print(f"Found the {v_wheel_channel} channel, saying hi!")
    if not DEBUG_MODE:  # only send this message when we are NOT in debug mode
        await v_wheel_channel.send("Tadaaaa~! It's me, Victini~!")
    for role in bot.guilds[0].roles:
        type_roles[role.name] = role.id  # fetch the server's roles and put them in a dictionary with the name and ID
        print(f"Role Name: {role.name} | Role ID: {role.id}")


@bot.command(name="forcespin", description="Forces a fresh spin of the V-Wheel!")
@commands.has_permissions(administrator=True)
async def forcespin(ctx):
    await spin_wheel()
    await ctx.respond(content="Fine, I've spun the V-Wheeeeeel~!", ephemeral=True)


@bot.command(name="wavecast", description="Fetch the full V-Wavecast!")
@commands.has_permissions(administrator=True)
async def show_wavecast(ctx):
    wavecast_message = f"# Wavecast\n"
    for i in range(len(wavecast["queue"])):
        wavecast_message += f"{i + 1}. {wavecast["queue"][i]}"
        if i == 0: wavecast_message += " **(Up next!)**"
        wavecast_message += "\n"
    wavecast_message.rstrip()
    await ctx.respond(content=wavecast_message, ephemeral=True)


@bot.command(name="futuresight", description="Use the move Future Sight to learn tomorrow's v-wave")
async def futuresight(ctx):
    user = ctx.user
    wavecast_message = f"You used Future Sight!\n"
    if discord.utils.get(user.roles, name="Psychic Type"):
        wavecast_message += f"You foresee that the next v-wave could be... {wavecast["queue"][0]}!"
    else:
        wavecast_message += f"You get the feeling that the next v-wheel is {random.choice(const_types)}... you think...\n"
    wavecast_message.rstrip()
    await ctx.respond(content=wavecast_message, ephemeral=True)


# TODO: Is this still necessary for Pycord?
fixup.run(bot, DISCORD_TOKEN, DEBUG_MODE)
