from asyncio import tasks
import discord
from discord.ext import commands
from discord.ext import tasks
import requests
import filecmp

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
    update = get_feed_bug()
    for i in update:
        saved_feed = open('new.txt','a')
        saved_feed.write(i)
    
    saved_feed = "feed.txt"
    new_feed = "new.txt"

    if filecmp.cmp(saved_feed, new_feed) is False:
        saved_feed = get_feed_bug()
        buglist = saved_feed[0].rsplit('"')
        bug = buglist[buglist.index("bug_type")+4]
        user = buglist[buglist.index("username")+2]
        status = buglist[buglist.index("status")+4]
        print(status)
        print(user)
        if user.lower() == "w0rty" or user.lower() == "spawnzii" and status.lower() == "new":
            embed=discord.Embed(title="__Yes We Hack Tracker__", description=f"New Report By **{user}**\n\n {bug} status : **{status}**", color=discord.Color.red())
            channel = bot.get_channel(948965313750380645)
            spoofers = bot.get_channel(831249140087652382)
            await channel.send(embed=embed)
            await spoofers.send(embed=embed)
            

        elif user.lower() == "w0rty" or user.lower() == "spawnzii" and status.lower() == "accepted":
            embed=discord.Embed(title="__Yes We Hack Tracker__", description=f"Congrats ! **{user}**'s {bug} was **{status}**", color=discord.Color.green())
            channel = bot.get_channel(948965313750380645)
            spoofers = bot.get_channel(831249140087652382)
            await channel.send(embed=embed)
            await spoofers.send(embed=embed)
            

        elif user.lower() == "w0rty" or user.lower() == "spawnzii" and status.lower() == "resolved":
            embed=discord.Embed(title="__Yes We Hack Tracker__", description=f"**{user}**'s {bug} was **{status}** !", color=discord.Color.red())
            channel = bot.get_channel(948965313750380645)
            spoofers = bot.get_channel(831249140087652382)
            await channel.send(embed=embed)
            await spoofers.send(embed=embed)
            

#831249140087652382
        open('feed.txt', 'w').close()
        open('new.txt', 'w').close()
        for i in update:
            saved_feed = open('feed.txt','a')
            saved_feed.write(i)

    else: 
        update = get_feed_bug()
        open('feed.txt', 'w').close()
        open('new.txt', 'w').close()
        for i in update:
            saved_feed = open('feed.txt','a')
            saved_feed.write(i)
        log = get_feed_bug()
        logs = log[0].rsplit('"')
        user = logs[logs.index("username")+2]


saved_feed = open('feed.txt','r')
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
    user = ["w0rty","spawnzii","perce"] # change the username
    for hunter in user:
        feed = live_hactivity(hunter)
        if not(feed):
            embed=discord.Embed(title="__Yes We Hack Tracker__", description=f"What our hunters reported ?\n\n **{hunter}** didn't report anything :(", color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title="__Yes We Hack Tracker__", description=f"What our hunters reported ?\n\n **{hunter}** has found\n **{feed}**", color=discord.Color.red())
            await ctx.send(embed=embed)

bot.run("") # add your token 
