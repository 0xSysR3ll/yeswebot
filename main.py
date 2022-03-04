from ast import Return
from asyncio import tasks
from distutils.log import info
from email import feedparser, message
from http import client
from aiohttp import request
import discord
from discord.ext import commands
from discord.ext import tasks
import requests
import threading
import time

bot = commands.Bot(command_prefix="!",description="Yes We Hack tracker")

def user_infos(user):
    url = f"https://api.yeswehack.com/hunters/{user}"
    r = requests.get(url)
    if r.status_code != 404:
        return r.text
    else:
        return False


def live_hactivity(hunter):
    url = "https://api.yeswehack.com/hacktivity"
    r = requests.get(url)
    feed = r.text.rsplit("date")
    news = []
    for report in feed:
        if hunter in report:
            report = feed[feed.index(report)]
            report = report.split('"')
            bug = report[report.index("bug_type")+4]
            status = report[report.index("workflow_state")+2]
            news.append(bug)
            news.append(status)
    return news


def get_feed_bug():
    url = f"https://api.yeswehack.com/hacktivity/"
    r = requests.get(url)
    feed = r.text.rsplit("date")
    news = []
    for report in feed:
        report = feed[feed.index(report)]
        news.append(report)
    return news[1::]


def live_check(news_feed,hold_feed):
    if news_feed != hold_feed:
        news_feed = news_feed[0].rsplit('"')
        bug = news_feed[news_feed.index("bug_type")+4]
        return bug
    else:
        False

@tasks.loop(minutes=1)
async def lives(saved_feed):
    if saved_feed != get_feed_bug():
        embed=discord.Embed(title="__Yes We Hack Tracker__", description=f"News Repport By\n\n", color=discord.Color.red())
        channel = bot.get_channel(831949020804939837)
        await channel.send(embed=embed)
        saved_feed.clear()
        saved_feed = get_feed_bug()
    else: 
        print(saved_feed[0])


saved_feed = get_feed_bug()
@bot.event
async def on_ready():
    print("Bot is Ready")
    lives.start(saved_feed)

@bot.command()
async def infos(ctx,user):
    if user_infos(user) is False:
        await ctx.send(f"User **{user}** not found")
    else:
        infos = user_infos(user).rsplit('"')
        rank = infos[infos.index('rank') + 1]
        rank = rank.replace(",","").replace(":","")
        point = infos[infos.index('points') + 1]
        point = point.replace(",","").replace(":","")
        report = infos[infos.index('nb_reports') + 1]
        report = report.replace(",","").replace(":","")
        impact = infos[infos.index('impact') + 2]
        
        embed=discord.Embed(title="__Yes We Hack Tracker__", description=f" **{user.upper()} Stats** 📈 \n\n***RANK*** 🏆 : *{rank}*\n***POINTS*** 🥇 : *{point}*\n ***REPORTS*** 🚩 : *{report}*\n ***IMPACT*** 💀 : *{impact}*", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command()    
async def hunter(ctx):
    user = ["w0rty","spawnzii"] # change the username
    for hunter in user:
        feed = live_hactivity(hunter)
        if not(feed):
            embed=discord.Embed(title="__Yes We Hack Tracker__", description=f"What our hunters reported ?\n\n **{hunter}** didn't report anything :(", color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title="__Yes We Hack Tracker__", description=f"What our hunters reported ?\n\n **{hunter}** have found\n **{feed}**", color=discord.Color.red())
            await ctx.send(embed=embed)

bot.run("") # add your token 
