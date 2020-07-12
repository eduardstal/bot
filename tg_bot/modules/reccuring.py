from io import BytesIO
from time import sleep
from typing import Optional

from telegram import TelegramError, Chat, Message
from telegram import Update, Bot
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async

import tg_bot.modules.sql.users_sql as sql
from tg_bot import dispatcher, OWNER_ID, LOGGER
from tg_bot.modules.helper_funcs.filters import CustomFilters


#pundix_reccuring
@run_async
def r1 (bot: Bot, update: Update):
    time = 18000
    while True:
        bot.send_message(-1001123984838, 'Dear Pundians, with the recent release of the Function X test-net, numerous scams have started to appear. Beware that the FX coin in the current state is purely for testing purposes and has no value assigned to it. \
                                        \n\
                                        \nDo not try to send FX tokens from an ERC-20 (ethereum) address to a FX test-net address cause you will risk losing your tokens.')
        bot.send_message(-1001123984838, 'Let the Function X development team hear your voice, know your feedback and suggestions on the test-net. We are eager to learn and improve.\
                                        \n\
                                        \nhttps://forms.gle/chCg27wQVD1fGXz36')
        sleep(time)

#functionx_reccuring
@run_async
def r2 (bot: Bot, update: Update):
    time = 15000
    while True:
        bot.send_message(-1001272071252, 'Dear Pundians, with the recent release of the Function X test-net, numerous scams have started to appear. Beware that the FX coin in the current state is purely for testing purposes and has no value assigned to it. \
                                        \n\
                                        \nDo not try to send FX tokens from an ERC-20 (ethereum) address to a FX test-net address cause you will risk losing your tokens.')
        bot.send_message(-1001272071252, 'Let the Function X development team hear your voice, know your feedback and suggestions on the test-net. We are eager to learn and improve.\
                                        \n\
                                        \nhttps://forms.gle/chCg27wQVD1fGXz36')
        sleep(time)

#gift_reccuring
@run_async
def r3 (bot: Bot, update: Update):
    time = 10000
    while True:
        bot.send_message(-1001187701589, "If you've noticed someone is breaking the rules repeatedly: Reply with '!report <reason>' or '@admin <reason>' to a message sent by that individual and s/he will be warned (6 reports needed to a message for the warn to be issued) \
                                        \n\
                                        \nMembers will be banned permanently after two warns. (Please do not abuse the report system, or you might be the one who gets banned :)")
        sleep(time)

#nem_reccuring
@run_async
def r4 (bot: Bot, update: Update):
    time = 99999999999
    while True:
        bot.send_message(-1001272816705, 'Reccuring message 1')
        sleep(time)



__mod_name__ = "Reccuring"
R1_HANDLER = CommandHandler("r1", r1, filters=Filters.user(OWNER_ID))
R2_HANDLER = CommandHandler("r2", r2, filters=Filters.user(OWNER_ID))
R3_HANDLER = CommandHandler("r3", r3, filters=Filters.user(OWNER_ID))
R4_HANDLER = CommandHandler("r4", r4, filters=Filters.user(OWNER_ID))
dispatcher.add_handler(R1_HANDLER)
dispatcher.add_handler(R2_HANDLER)
dispatcher.add_handler(R3_HANDLER)
dispatcher.add_handler(R4_HANDLER)
