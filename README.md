# Victini

A Discord bot written in Python using [Pycord](https://pycord.dev)

Victini's primary function is to spin the [V-Wheel](https://bulbapedia.bulbagarden.net/wiki/Victini_(Gates_to_Infinity)) daily and hoist the relevant Pokémon type roles (Fire, Grass, Electric, etc.) in the server for 24 hours.

Secondary functions include some user-facing commands, invoked using the `!` prfix or as aslash commands. The current list of available commands are as follows:

| ! Commands | Effects                                   | Permissions |
|------------|-------------------------------------------|-------------|
| !pet       | Pets Victini (They might not like that)   | Everyone    |
| !spin      | Don't like the result? Spin the V-Wheel!  | Everyone    |
----
| Slash Commands | Effects                                                                                                                                                        | Permissions    |
|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|
| /forcespin     | Manually re-spin the v-wheel instantly                                                                                                                         | Administrators |
| /wavecast      | Fetch the full canonical list of upcoming v-wheel results                                                                                                      | Administrators |
| /futuresight   | Use [Future Sight](https://bulbapedia.bulbagarden.net/wiki/Future_Sight_(move)) to see tomorrow's v-wave!<br/>But not all Pokémon can use that move, right...? | Everyone       |

### Installation & Requirements

Currently, you must populate a `.env` file with three values:

- `DISCORD_TOKEN`: must be populated with the bot's auth token from the developer portal
- `VWHEEL_CHANNEL_ID`: must have the channel ID of the v-wheel channel
- `DEBUG_MODE`: Enable or disable debug mode as a boolean value, `1` or `0` (Disable this with `0` when deploying)
- `FILE_STORAGE`: Define a directory where the bot writes persistent data to, such as `/data/` or leave blank for local directory

#### Required permissions

The bot must be granted the following role permissions in order to function correctly:
- `Manage Roles`

Additionally, the bot's role (Probably called `Victini`) _must_ be listed ABOVE all of the Pokémon Type roles in the list of roles in order to manipulate their hoisted status.

#### Server Settings

Your Discord server MUST have 18 "Type" roles available and they must have *exactly* the names as follows:

- Normal Type
- Fire Type
- Water Type
- Grass Type
- Electric Type
- Ice Type
- Fighting Type
- Poison Type
- Ground Type
- Flying Type
- Psychic Type
- Bug Type
- Rock Type
- Ghost Type
- Dragon Type
- Dark Type
- Steel Type
- Fairy Type

Once all of the above requirements are met, Victini should run as expected.
