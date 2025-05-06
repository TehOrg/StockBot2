import discord
from discord.ext import commands
import random
import logging
import yfinance
import os
import sys

from datetime import datetime
from table2ascii import table2ascii, Alignment
import yfinance.exceptions

# Get log level from env variable, default to INFO
logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO').upper()
)

# Pull discord token from env variable, exit if we can't find it
token = os.getenv("DISCORD_TOKEN")
if not token:
    logging.error("DISCORD_TOKEN env variable missing")
    sys.exit()

# Pull channel id from env variable, exit if we can't find it
stockschannelid = os.getenv("STOCKS_CHANNEL_ID")
if not stockschannelid:
    logging.error("STOCKS_CHANNEL_ID env variable missing")
    sys.exit()

# Make sure channel id is an int cause discord.py is picky
stockschannelid = int(stockschannelid)

# No idea where this actually shows up
description = "A bot that people can annoy about stocks."

# list of tickers and display names
indexes = {"^DJI": "DJI","^GSPC": "S&P 500","^IXIC":"NASDAQ","^RUT":"R 2000"}

# Request permissions
intents = discord.Intents.default()
intents.message_content = True

# Setup both with command prefix
bot = commands.Bot(command_prefix='/', description=description, intents=intents)

# Messages for weekend requests
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

# Create an emoji with a random tone
def create_random_tone_emoji(baseemoji):
    toneoptions = ["", "_tone1", "_tone2", "_tone3", "_tone4", "_tone5"]
    randomtoneemojistring = " :" + baseemoji + random.choice(toneoptions) + ": "
    return randomtoneemojistring

# Generates emojis based on value provided
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

# method to check if it's the weekend
def IsWeekend():
    now = datetime.now()
    logging.info("It's currently {}. ISO weekday is {}.".format(now, now.isoweekday()))

    # Check day of week
    # If Sat or sun, tell people to go away
    if now.isoweekday() in {6, 7}:
        return True
    else:
        return False

def DoesSymbolExist(symbol: str) -> bool:
    """
    Checks if a symbol is available via the Yahoo Finance API.
    """

    ticker = yfinance.Ticker(symbol)
    try:
        info = ticker.info
        return True
    except:
        print(f"Cannot get info of {symbol}, it probably does not exist")
    return False

# Runs when bot starts
@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logging.info("Using {} for channel.".format(bot.get_channel(stockschannelid)))
    #message_channel = bot.get_channel(stockschannelid)
    #await message_channel.send("I'm (sorta) back, bitches!")

# /index command
@bot.command()
async def index(ctx):
    logging.info("Heard /index command in {}".format(ctx.message.channel))

    # Check if we got a message from the monitored channel
    if ctx.message.channel == bot.get_channel(stockschannelid):
        logging.info("Message is in our configured listening channel")
        # Check day of week
        # If Sat or sun, tell people to go away
        if IsWeekend():
            logging.info("It's the weekend. Sent sleeping message.")
            message = random.choice(sleepMessages)
            await ctx.send(message)
        else:
            try:
                # Create spaced list of tickers, it's what yfinanace expects for multiple tickers
                tickers = yfinance.Tickers(" ".join(indexes.keys()))

                header = ["Name", "Price", "% Change"]
                tabledata = []
                emojimessage = ""
                marketstate = ""

                # Loop through all our monitored tickers and pull data
                for symbol, ticker in tickers.tickers.items():
                    logging.debug(ticker.info)
                    tabledata.append([indexes[symbol],f"${'{:.2f}'.format(round(ticker.info['regularMarketPrice'],2))}",f"{'{:.2f}'.format(round(ticker.info['regularMarketChangePercent'], 2))}%"])
                    emojimessage += GetEmoji(ticker.info['regularMarketChangePercent'])
                    marketstate = ticker.info["marketState"]

                # Covert table to ascii
                output = table2ascii(
                    header=header,
                    body=tabledata,
                    first_col_heading=True,
                    alignments=[Alignment.LEFT, Alignment.RIGHT, Alignment.RIGHT]
                )

                # Make sure we output in monospace
                messagetext = f"```\n{output}\n```"

                # Create message embed
                embedVar = discord.Embed(title="US Indexes", description=messagetext)
                # await ctx.send(f"```\n{output}\n```")

                # send messages
                await ctx.send(f"Market state is {marketstate}", embed=embedVar)
                await ctx.send(emojimessage)
            except yfinance.exceptions.YFRateLimitError:
                logging.warning("Rate limited")
                await ctx.send("YFinance has rated limited me. Try again later.")

# /ticker command
@bot.command()
async def ticker(ctx, symbol: str):
    logging.info(f"Heard /ticker command in {ctx.message.channel} for ticker {symbol}")

    # Check if we got a message from the monitored channel
    if ctx.message.channel == bot.get_channel(stockschannelid):
        logging.info("Message is in our configured listening channel")
        # Check day of week
        # If Sat or sun, tell people to go away
        if IsWeekend():
            logging.info("It's the weekend. Sent sleeping message.")
            message = random.choice(sleepMessages)
            await ctx.send(message)
        else:
            try:
                if DoesSymbolExist(symbol):
                    ticker = yfinance.Ticker(symbol)
                    logging.debug(ticker.info)
                    embedVar = discord.Embed(title=ticker.info['longName'], color=0x00ff00)
                    embedVar.add_field(name="Current Quote", value=f"${'{:.2f}'.format(round(ticker.info['regularMarketPrice'],2))}", inline=False)
                    embedVar.add_field(name="Previous Close", value=f"${'{:.2f}'.format(round(ticker.info['regularMarketPreviousClose'],2))}", inline=False)
                    embedVar.add_field(name="Open Price", value=f"${'{:.2f}'.format(round(ticker.info['regularMarketOpen'],2))}", inline=False)
                    embedVar.add_field(name="Day Change", value=f"{'{:.2f}'.format(round(ticker.info['regularMarketChangePercent'],2))}%", inline=False)
                    await ctx.send(f"Market state is {ticker.info['marketState']}", embed=embedVar)
                else:
                    await ctx.send(f"I can't find symbol: {symbol}")
            except yfinance.exceptions.YFRateLimitError:
                logging.warning("Rate limited")
                await ctx.send("YFinance has rated limited me. Try again later.")
            

# Run the bot
bot.run(token)