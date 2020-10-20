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

def less_decimals(x):
    var = str(x)
    if len(var) > 3:
        var = var[0 : 5 ]
    if (var[0]=="-"):
        pass
    else:
        var="+"+var
    return var

def btcnpxs ():
    btc = "https://api.coingecko.com/api/v3/simple/price?ids=pundi-x&vs_currencies=btc&include_24hr_change=true"
    response=requests.get(btc).json()
    price = float(response['pundi-x']['btc'])
    change = float(response['pundi-x']['btc_24h_change'])
    price_dec = decimal_str(price)
    change_dec = less_decimals(change)
    ret = "{} BTC        {}% in 24h".format(price_dec, change_dec)
    return ret

def ethnpxs():
    eth = "https://api.coingecko.com/api/v3/simple/price?ids=pundi-x&vs_currencies=eth&include_24hr_change=true"
    response=requests.get(eth).json()
    price = float(response['pundi-x']['eth'])
    change = float(response['pundi-x']['eth_24h_change'])
    price_dec = decimal_str(price)
    change_dec = less_decimals(change)
    ret = "{} ETH      {}% in 24h".format(price_dec, change_dec)
    return ret

def btcfx ():
    btc = "https://api.coingecko.com/api/v3/simple/price?ids=fx-coin&vs_currencies=btc&include_24hr_change=true"
    response=requests.get(btc).json()
    price = float(response['fx-coin']['btc'])
    change = float(response['fx-coin']['btc_24h_change'])
    price_dec = decimal_str(price)
    change_dec = less_decimals(change)
    ret = "{} BTC      {}% in 24h".format(price_dec, change_dec)
    return ret

def ethfx ():
    eth = "https://api.coingecko.com/api/v3/simple/price?ids=fx-coin&vs_currencies=eth&include_24hr_change=true"
    response=requests.get(eth).json()
    price = float(response['fx-coin']['eth'])
    change = float(response['fx-coin']['eth_24h_change'])
    price_dec = decimal_str(price)
    change_dec = less_decimals(change)
    ret = "{} ETH      {}% in 24h".format(price_dec, change_dec)
    return ret

def usdfx ():
    usd = "https://api.coingecko.com/api/v3/simple/price?ids=fx-coin&vs_currencies=usd&include_24hr_change=true"
    response=requests.get(usd).json()
    price = float(response['fx-coin']['usd'])
    change = float(response['fx-coin']['usd_24h_change'])
    price_dec = decimal_str(price)
    change_dec = less_decimals(change)
    ret = "{} USD           {}% in 24h".format(price_dec, change_dec)
    return ret

def fx(bot: Bot, update: Update):
    chat_id = update.effective_chat.id
    message="The price of 1 FX is:\
                                \n {} \
                                \n {} \
                                \n {} ".format(btcfx(),ethfx(),usdfx())
    bot.send_message(chat_id, message)

def npxs (bot: Bot, update: Update):
    chat_id = update.effective_chat.id
    message="The price of 1 NPXS is:\
                                \n {} \
                                \n {} ".format(btcnpxs(),ethnpxs())
    bot.send_message(chat_id, message)

__mod_name__ = "Price"
NPXS_HANDLER = CommandHandler("npxs", npxs)
FX_HANDLER = CommandHandler("fx", fx)
dispatcher.add_handler(NPXS_HANDLER)
dispatcher.add_handler(FX_HANDLER)
