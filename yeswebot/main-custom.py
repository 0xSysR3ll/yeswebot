#!/usr/bin/env python3
# *-* coding: utf-8 *-*

from asyncio import tasks
from datetime import datetime
import discord
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import CommandNotFound
import requests as req
import hashlib
import json
import os
from pretty_help import PrettyHelp

# CONSTANTS
HUNTERS = ['SpawnZii', 'W0rty', "Perce", "0xSysr3ll", "rabhi", "Sharan"]
USER_URL = f"https://api.yeswehack.com/hunters/"
HKTVTY_URL = f"https://api.yeswehack.com/hacktivity/"
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Status dictionnary for pretty display on Discord
dict_status = {'new': 'New 🆕',
               'accepted': 'Accepted 🔥', 'resolved': 'Resolved ✅'}

tdy = datetime.today().strftime("%Y-%m-%d")


def get_user(username):
    url = f"{USER_URL}{username}"
    infos = req.get(url)
    if infos.status_code != 404:
        return infos.json()


def profile_infos(username):
    user_infos = get_user(username)
    if user_infos is not None:
        # Parsing user data
        username = user_infos['username']
        profile = f"https://yeswehack.com/hunters/{username}"
        github = f"https://github.com/{user_infos['hunter_profile']['github']}"
        points = user_infos['points']
        reports = user_infos['nb_reports']
        rank = user_infos['rank']
        impact = user_infos['impact']
        avatar_url = user_infos['avatar']['url']
        return username, profile, github, points, reports, rank, impact, avatar_url
    else:
        return None, None, None, None, None, None, None, None


def hunter_feed(username):
    global tdy
    url = f"{HKTVTY_URL}{username}"
    feed = req.get(url)
    if feed.status_code != 404:
        return feed.json()


@tasks.loop(minutes=0.5)
async def live_update():
    global tdy
    tdy = datetime.today().strftime("%Y-%m-%d")
    channel = bot.get_channel(CHANNEL_ID)
    # print(f"Working on channel {channel}")
    feed = req.get(HKTVTY_URL).json()

    try:
        old_feed = json.load(open("feed.json"))
        pass
    except:
        with open("feed.json", "w+") as fout:
            out = json.dumps(feed)
            fout.write(out)
        update_feed(feed)
        return

    old_feed = json.load(open("feed.json", "r"))
    latest_report = feed['items'][0]
    date = latest_report['date']
    hunter = latest_report['report']['hunter']['username']
    bug_name = latest_report['report']['bug_type']['name']
    bug_state = latest_report['status']['workflow_state']

    if (hunter in HUNTERS) and (tdy == date) and (bug_state == "new") and latest_report != old_feed['items'][0]:
        embed = discord.Embed(
            title=f"**{hunter}** just reported a new bug !", color=discord.Color.red())
        embed.add_field(name="Bug type", value=bug_name, inline=False)
        print(f"[+] New report by **{hunter}**.")
        await channel.send(embed=embed)
    elif (hunter in HUNTERS) and (tdy == date) and (bug_state == "accepted") and latest_report != old_feed['items'][0]:
        embed = discord.Embed(
            title=f"Congratz to **{hunter}** ! His report has been accepted 🔥", color=discord.Color.green())
        embed.add_field(name="Bug type", value=bug_name, inline=False)
        print(
            f"[+] Update on report {bug_name}. State changed to {bug_state}")
        await channel.send(embed=embed)
    elif (hunter in HUNTERS) and (tdy == date) and (bug_state == "resolved") and latest_report != old_feed['items'][0]:
        embed = discord.Embed(
            title=f"**{hunter}**'s report has been resolved. ", color=discord.Color.grey())
        embed.add_field(name="Bug type", value=bug_name, inline=False)
        print(
            f"[+] Update on report {bug_name}. State changed to {bug_state}")
        await channel.send(embed=embed)

    update_feed(feed)


def update_feed(tmp_feed):
    print("[?] Updating feed ...")
    tmp_hash = hashlib.sha256()
    feed_hash = hashlib.sha256()

    tmp_hash.update(str(tmp_feed).encode())
    tmp_hash = tmp_hash.hexdigest()

    with open("feed.json", "r") as fin:
        feed = str(json.load(fin))
        feed_hash.update(feed.encode())
        feed_hash = feed_hash.hexdigest()

    if tmp_hash != feed_hash:
        print("[+] New report found !")
        with open("feed.json", "w+") as fout:
            out = json.dumps(tmp_feed)
            fout.write(out)
    else:
        print("[-] No new report")


# Declare the bot
bot = commands.Bot(command_prefix="!",
                   description="Available commands.", help_command=PrettyHelp())

bot.help_command = PrettyHelp(
    no_category="Yes We Hack tracker",
    show_index=False,
    ending_note="Made with ❤️ by 0xSysr3ll & SpawnZii",
    color=discord.Color.red()
)


@bot.event
async def on_ready():
    print("Bot is Ready !")
    live_update.start()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send(f"Sorry but this command does not exist !\nPlease check available commands with `!help`")
        return


@bot.command(name="infos", help="Display informations about a hunter (if his profile is not in private).")
async def infos(ctx, hunter):
    # Searching for user
    username, profile, github, points, reports, rank, impact, avatar_url = profile_infos(
        hunter)
    if username is None:
        await ctx.send(f"**{hunter}** was not found in YesWeHack or his profile is private 😞")
        return

    # Creating nice embed
    embed = discord.Embed(color=discord.Color.red())
    embed.set_author(
        name=f"Profile of {username}", url=profile, icon_url=avatar_url)
    embed.add_field(name="Rank 🏆", value=rank, inline=False)
    embed.add_field(name="Points 🏅", value=points, inline=False)
    embed.add_field(name="Reports 🚩", value=reports, inline=False)
    embed.add_field(name="Impact 💀", value=impact, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="today", help="Display a hunter todays's reports and updates.")
async def today(ctx, hunter=None):
    if hunter is None:
        await ctx.send(f"Please specify the hunter's username in your command !")
        return

    global tdy

    # Searching for user
    feed = hunter_feed(hunter)
    if feed is not None:
        if tdy in str(feed):
            counter = 0
            username, profile, github, points, reports, rank, impact, avatar_url = profile_infos(
                hunter)
            embed = discord.Embed(color=discord.Color.blue())
            embed.set_author(
                name=f"{username} todays's new reports and updates", url=profile, icon_url=avatar_url)
            for report in feed['items']:
                if report['date'] == tdy:
                    counter += 1
                    name = report['report']['bug_type']['name']
                    status = report['status']['workflow_state']
                    embed.add_field(
                        name=f"Report {counter} : {name}", value=dict_status[status], inline=False)
        else:
            await ctx.send(f"No report for **{hunter}** today.")
            return

    else:
        await ctx.send(f"**{hunter}**  was not found in YesWeHack or his profile is private 😞")
        return
    await ctx.send(embed=embed)


@bot.command(name="latest", help="Display the latest report of the feed. You can also specify <hunter> to a get a hunter's latest report.")
async def latest(ctx, hunter=None):
    if hunter is not None:
        feed = hunter_feed(hunter)
    else:
        feed = json.load(open("feed.json", "r"))

    if feed is None:
        await ctx.send(f"**{hunter}**  was not found in YesWeHack or his profile is private 😞")
        return
    latest_report = feed["items"][0]
    bug_date = latest_report['date']
    username = latest_report['report']['hunter']['username']
    bug_name = latest_report['report']['bug_type']['name']
    bug_state = latest_report['status']['workflow_state']

    if bug_state == "new" and hunter is None:
        embed = discord.Embed(
            title=f"Latest report was made by **{username}**", color=discord.Color.red())
        embed.add_field(name="Bug type", value=bug_name, inline=False)
    elif bug_state == "new" and hunter is not None:
        embed = discord.Embed(
            title=f"**{username}**'s latest report", color=discord.Color.red())
        embed.add_field(name="Date", value=bug_date, inline=False)
        embed.add_field(name="Bug type", value=bug_name, inline=False)
    elif bug_state == "accepted":
        embed = discord.Embed(
            title=f"**{username}**'s latest report has been accepted ! 🔥", color=discord.Color.green())
        embed.add_field(name="Date", value=bug_date, inline=False)
        embed.add_field(name="Bug type", value=bug_name, inline=False)
    else:
        embed = discord.Embed(
            title=f"**{username}**'s latest report has been resolved.", color=discord.Color.grey())
        embed.add_field(name="Date", value=bug_date, inline=False)
        embed.add_field(name="Bug type", value=bug_name, inline=False)
    await ctx.send(embed=embed)


bot.run(DISCORD_TOKEN)
