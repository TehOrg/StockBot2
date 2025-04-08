import discord
from discord.ext import commands
import random
import logging
import yfinance
import os
import sys

from datetime import datetime
from table2ascii import table2ascii, Alignment

token = os.getenv("DISCORD_TOKEN")
if not token:
    logging.error("DISCORD_TOKEN env variable missing")
    sys.exit()

stockschannelid = os.getenv("STOCKS_CHANNEL_ID")
if not stockschannelid:
    logging.error("STOCKS_CHANNEL_ID env variable missing")
    sys.exit()

stockschannelid = int(stockschannelid)

description = "A bot that people can annoy about stocks."

indexes = {"^DJI": "DJI","^GSPC": "S&P 500","^IXIC":"NASDAQ","^RUT":"R 2000"}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', description=description, intents=intents)

sleepMessages = [
    "Fuck off! I'm sleeping.",
    "Go away. I'm trying to sleep.",
    "Make like a tree and fuck off. It's the weekend.",
    "Why don't you go play hide-and-go-fuck-yourself? It's the weekend.",
    "Why don't you go take a flying fuck at a rolling donut? It's the weekend.",
    "On your mark, get set, go fuck yourself! It's the weekend.",
    "Pick any direction away from me, and fuck off in it.  It's the weekend.",
    "How much time between right now and you fucking off? It's the weekend."
]

# Generates stonks down and stonks up emojis based on index data
def GetEmoji(value):
    fullemojistring = ""
    if float(value) >= 3:
        emojistring = " :exploding_head: "
    elif float(value) <= -3:
        emojistring = " <:fine:682657326070759449> "
    elif float(value) >= .5:
        emojistring = " <:stonks_up:690604708020224071> "
    elif float(value) <= -.5:
        emojistring = " <:stonks_down:690604763066138655> "
    else:
        shrugemojioptions = ['person_shrugging',
                        'man_shrugging',
                        'woman_shrugging']
        emojistring = create_random_tone_emoji(random.choice(shrugemojioptions))
    fullemojistring = fullemojistring + emojistring
    return fullemojistring

# Create an emoji with a random tone
def create_random_tone_emoji(baseemoji):
    toneoptions = ["", "_tone1", "_tone2", "_tone3", "_tone4", "_tone5"]
    randomtoneemojistring = " :" + baseemoji + random.choice(toneoptions) + ": "
    return randomtoneemojistring

def GetEmoji(value:float):
    if value >= 3:
        emojistring = " :exploding_head: "
    elif value <= -3:
        emojistring = " <:fine:682657326070759449> "
    elif value >= .5:
        emojistring = " <:stonks_up:690604708020224071> "
    elif value <= -.5:
        emojistring = " <:stonks_down:690604763066138655> "
    else:
        shrugemojioptions = ['person_shrugging',
                        'man_shrugging',
                        'woman_shrugging']
        emojistring = create_random_tone_emoji(random.choice(shrugemojioptions))
    return emojistring

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logging.info("Using {} for channel.".format(bot.get_channel(stockschannelid)))
    message_channel = bot.get_channel(stockschannelid)
    await message_channel.send("I'm (sorta) back, bitches!")

@bot.command()
async def index(ctx):
    logging.info("Heard /tehindex command in {}".format(ctx.message.channel))
    if ctx.message.channel == bot.get_channel(stockschannelid):
        logging.info("Message is in our configured listening channel")
        now = datetime.now()
        logging.info("It's currently {}. ISO weekday is {}.".format(now, now.isoweekday()))

        if now.isoweekday() in {6, 7}:
            logging.info("It's the weekend. Sent sleeping message.")
            message = random.choice(sleepMessages)
            await ctx.send(message)
        else:
            tickers = yfinance.Tickers(" ".join(indexes.keys()))

            header = ["Name", "Price", "% Change"]
            tabledata = []
            emojimessage = ""

            for symbol, ticker in tickers.tickers.items():
                logging.debug(ticker.info)
                tabledata.append([indexes[symbol],f"${round(ticker.info['regularMarketPrice'],2)}",f"{round(ticker.info['regularMarketChangePercent'], 2)}%"])
                emojimessage += GetEmoji(ticker.info['regularMarketChangePercent'])

            output = table2ascii(
                header=header,
                body=tabledata,
                first_col_heading=True,
                alignments=[Alignment.LEFT, Alignment.RIGHT, Alignment.RIGHT]
            )
            messagetext = f"```\n{output}\n```"
            embedVar = discord.Embed(title="US Indexes", description=messagetext)
            # await ctx.send(f"```\n{output}\n```")
            await ctx.send(embed=embedVar)
            await ctx.send(emojimessage)
    

bot.run(token)