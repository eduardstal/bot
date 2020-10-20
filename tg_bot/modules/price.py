import requests 
from telegram.ext.dispatcher import run_async
from telegram import TelegramError, Chat, Message
from telegram import Update, Bot
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler
import re
from io import BytesIO
from typing import Optional, List
import decimal
from tg_bot import dispatcher, OWNER_ID, LOGGER
from tg_bot.modules.helper_funcs.filters import CustomFilters

def decimal_str(x: float, decimals: int = 10) -> str:
    return format(x, f".{decimals}f").lstrip().rstrip('0')


def btcnpxs (): #price in satoshi
    btc = "https://api.coingecko.com/api/v3/simple/price?ids=pundi-x&vs_currencies=btc"
    response=requests.get(btc).json()
    strip = float(response['pundi-x']['btc'])
    decimal = decimal_str(strip)
    return decimal

def ethnpxs(): #price in gwei
    eth = "https://api.coingecko.com/api/v3/simple/price?ids=pundi-x&vs_currencies=eth"
    response=requests.get(eth).json()
    strip = float(response['pundi-x']['eth'])
    decimal = decimal_str(strip)
    #char = 'e'
    #mod = 10*float(strip.split(char, 1)[0])
    #stripped = str(mod)
    #if len(stripped) > 3:
        #stripped = stripped[0 : 4 ]
    return decimal

def btcfx ():
    btc = "https://api.coingecko.com/api/v3/simple/price?ids=fx-coin&vs_currencies=btc"
    response=requests.get(btc).json()
    strip = float(response['fx-coin']['btc'])
    decimal = decimal_str(strip)
    return decimal

def ethfx ():
    eth = "https://api.coingecko.com/api/v3/simple/price?ids=fx-coin&vs_currencies=eth"
    response=requests.get(eth).json()
    strip = float(response['fx-coin']['eth'])
    decimal = decimal_str(strip)
    return decimal

def usdfx ():
    usd = "https://api.coingecko.com/api/v3/simple/price?ids=fx-coin&vs_currencies=usd"
    response=requests.get(usd).json()
    strip = float(response['fx-coin']['usd'])
    decimal = decimal_str(strip)
    return decimal

def fx(bot: Bot, update: Update):
    chat_id = update.effective_chat.id
    message="The price of 1 FX is:\
                                \n {} BTC\
                                \n {} ETH\
                                \n {} USD".format(btcfx(),ethfx(),usdfx())
    bot.send_message(chat_id, message)

def npxs (bot: Bot, update: Update):
    chat_id = update.effective_chat.id
    message="The price of 1 NPXS is:\
                                \n {} BTC\
                                \n {} ETH".format(btcnpxs(),ethnpxs())
    bot.send_message(chat_id, message)

__mod_name__ = "Price"
NPXS_HANDLER = CommandHandler("npxs", npxs)
FX_HANDLER = CommandHandler("fx", fx)
dispatcher.add_handler(NPXS_HANDLER)
dispatcher.add_handler(FX_HANDLER)
