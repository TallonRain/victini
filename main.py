import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import fixup
import datetime
from zoneinfo import ZoneInfo
import random
from wavecast import Wavecast, const_types

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
wavecast = Wavecast()
wavecast_filepath = None


# async bot functions
async def setup_hook(self) -> None:
    self.spin_wheel.start()


@tasks.loop(time=trigger_time)
async def spin_wheel():
    print("Activating the V-Wheel!!")
    # need to iterate through the roles so that the previous winner can be dehoisted automatically
    try:
        for role in bot.guilds[0].roles:
            if role.name in const_types:
                await role.edit(hoist=False)
    except discord.Forbidden:
        owner = bot.guilds[0].owner
        await owner.send(
            "Hey! I don't have permission to manage roles. "
            "Please make sure my role is above the type roles in Server Settings > Roles!"
        )
        return
    await v_wheel_channel.send("https://i.imgur.com/3EZpMlF.gif")
    await v_wheel_channel.send("It's time to spin the V-Wheeeeeeeeeeeeeeeel!")
    vwheel_type = wavecast.cycle()  # spiiiiiinnnnnnn
    await v_wheel_channel.send(f"Today's V-Wave type is... {vwheel_type}! Go say hi to the lucky {vwheel_type}s!")
    role_id = type_roles.get(vwheel_type)  # fetch the roleID of the winner
    role = bot.guilds[0].get_role(role_id)  # format it as a Discord object so it can be manipulated
    if role is not None:
        print("Fetched the role ID successfully")
        try:
            await role.edit(hoist=not role.hoist)  # inverts the current setting
        except discord.Forbidden:
            owner = bot.guilds[0].owner
            await owner.send(
                f"Hey! I couldn't hoist the {vwheel_type} role. "
                "Please make sure my role is above the type roles in Server Settings > Roles!"
            )
    else:
        print("Error fetching server roles, cannot hoist the V-Wheel winner")
    wavecast.save(wavecast_filepath)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!spin'):
        await message.channel.send(
            'Let\'s spin the V-Wheee- oh, you don\'t have any <:poke:1317397305615323196>? Can\'t spin it, then.')

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
    global wavecast_filepath
    wavecast_filepath = FILE_STORAGE + "wavecast.vwheel"
    if os.path.isfile(wavecast_filepath):
        wavecast.load(wavecast_filepath)
    else:
        wavecast.generate()
        wavecast.save(wavecast_filepath)
    spin_wheel.start()
    v_wheel_channel = await bot.fetch_channel(VWHEEL_CHANNEL_ID)  # channel id, as an int, goes here
    print(f"Found the {v_wheel_channel} channel, saying hi!")
    if not DEBUG_MODE:  # only send this message when we are NOT in debug mode
        await v_wheel_channel.send("Tadaaaa~! It's me, Victini~!")
    for role in bot.guilds[0].roles:
        type_roles[role.name] = role.id  # fetch the server's roles and put them in a dictionary with the name and ID
        print(f"Role Name: {role.name} | Role ID: {role.id}")


@bot.command(name="forcespin", description="Forces a fresh spin of the V-Wheel!")
async def forcespin(ctx):
    if ctx.guild is None:
        await ctx.respond("This command cannot be used in DMs.", ephemeral=True)
        return
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        return
    await ctx.defer(ephemeral=True)
    await spin_wheel()
    await ctx.followup.send(content="Fine, I've spun the V-Wheeeeeel~!", ephemeral=True)


@bot.command(name="reroll", description="Throw away the current wavecast and generate a fresh one!")
async def reroll(ctx):
    if ctx.guild is None:
        await ctx.respond("This command cannot be used in DMs.", ephemeral=True)
        return
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        return
    wavecast.generate()
    wavecast.save(wavecast_filepath)
    await ctx.respond(content="Done! I've re-rolled a brand new wavecast~!", ephemeral=True)


@bot.command(name="wavecast", description="Fetch the full V-Wavecast!")
async def show_wavecast(ctx):
    if ctx.guild is None:
        await ctx.respond("This command cannot be used in DMs.", ephemeral=True)
        return
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        return
    wavecast_message = f"# Wavecast\n"
    for i in range(len(wavecast.queue)):
        wavecast_message += f"{i + 1}. {wavecast.queue[i]}"
        if i == 0: wavecast_message += " **(Up next!)**"
        wavecast_message += "\n"
    wavecast_message.rstrip()
    await ctx.respond(content=wavecast_message, ephemeral=True)


@bot.command(name="futuresight", description="Use the move Future Sight to learn tomorrow's v-wave")
async def futuresight(ctx):
    if ctx.guild is None:
        await ctx.respond("This command cannot be used in DMs.", ephemeral=True)
        return
    user = ctx.user
    wavecast_message = f"You used Future Sight!\n"
    if discord.utils.get(user.roles, name="Psychic Type"):
        wavecast_message += f"You foresee that the next v-wave could be... {wavecast.queue[0]}!"
    else:
        wavecast_message += f"You get the feeling that the next v-wheel is {random.choice(const_types)}... you think...\n"
    wavecast_message.rstrip()
    await ctx.respond(content=wavecast_message, ephemeral=True)


# TODO: Is this still necessary for Pycord?
fixup.run(bot, DISCORD_TOKEN, DEBUG_MODE)
