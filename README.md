# YesWeHack-BOT 

The best Discord bot to track Yes We Hack reports.

# How to start

## Requirements

```bash
# Clone the repo
git clone https://github.com/0xSysR3ll/yeswebot.git
```

1. Create a bot on the [Discord Developers](https://discord.com/developers/applications)'s website.
2. Grab the associated Discord token.
3. Invite the bot on your server with the Oauth generated URL.

## Configuration

Adapt the `docker-compose.yml` file to your needs

>Environment variables :
>- `DISCORD_TOKEN` : You bot's authentication token.
>- `CHANNEL_ID` : The channel ID where you want the bot be active.
>- `CUSTOM` (True|False) : Choose wether you want to use the custom version of `main.py` or not.

If you choose `True`, you will have to specify in `yeswebot/main-custom.py` the list of `HUNTERS` you want their reports to be notified about.

```python
#file: main-custom.py
...
from pretty_help import PrettyHelp

# CONSTANTS
HUNTERS = ['SpawnZii', 'W0rty', "Perce", "0xSysr3ll", "rabhi", "Sharan"]
...
```

Else, you will be notified of all hunters's reports.

## Launch

Run the docker
```bash
$ sudo docker-compose up --build --detach
```

# How to use

>**!infos <hunter>**
> ```
>Display informations about a hunter (if his profile is not in private).
>```
>**!latest**
> ```
>Display the latest report of the feed. You can also specify <hunter> to a get a hunter's latest report.
>```
>**!today <hunter>**
>```
>Display a hunter todays's reports and updates.
>```

