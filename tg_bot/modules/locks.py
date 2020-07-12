import html
from typing import Optional, List

import telegram.ext as tg
from telegram import Message, Chat, Update, Bot, ParseMode, User, MessageEntity
from telegram import TelegramError
from telegram.error import BadRequest
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_html, escape_markdown

import tg_bot.modules.sql.locks_sql as sql
from tg_bot import dispatcher, SUDO_USERS, LOGGER
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.chat_status import can_delete, is_user_admin, user_not_admin, user_admin, \
    bot_can_delete, is_bot_admin
from tg_bot.modules.helper_funcs.filters import CustomFilters
from tg_bot.modules.helper_funcs.misc import split_message
from tg_bot.modules.log_channel import loggable
from tg_bot.modules.sql import users_sql

LOCK_TYPES = {'sticker': Filters.sticker,
              'audio': Filters.audio,
              'voice': Filters.voice,
              'document': Filters.document.category("application"),
              'video': Filters.video,
              'contact': Filters.contact,
              'photo': Filters.photo,
              'gif': CustomFilters.mime_type("video/mp4"),
              'url': Filters.entity(MessageEntity.URL) |
                     Filters.caption_entity(MessageEntity.URL) |
                     Filters.entity(MessageEntity.TEXT_LINK) |
                     Filters.caption_entity(MessageEntity.TEXT_LINK),
              'bots': Filters.status_update.new_chat_members,
              'forward': Filters.forwarded,
              'game': Filters.game
              }

GIF = Filters.document & CustomFilters.mime_type("video/mp4")
OTHER = Filters.game | Filters.sticker | GIF
MEDIA = Filters.audio | Filters.document | Filters.video | Filters.voice | Filters.photo
MESSAGES = Filters.text | Filters.contact | Filters.location | Filters.venue | Filters.command | MEDIA | OTHER
PREVIEWS = Filters.entity("url")

RESTRICTION_TYPES = {'messages': MESSAGES,
                     'media': MEDIA,
                     'other': OTHER,
                     # 'previews': PREVIEWS, # NOTE: this has been removed cos its useless atm.
                     'all': Filters.all}

PERM_GROUP = 1
REST_GROUP = 2


class CustomCommandHandler(tg.CommandHandler):
    def __init__(self, command, callback, **kwargs):
        super().__init__(command, callback, **kwargs)

    def check_update(self, update):
        return super().check_update(update) and not (
                sql.is_restr_locked(update.effective_chat.id, 'messages') and not is_user_admin(update.effective_chat,
                                                                                                update.effective_user.id))


tg.CommandHandler = CustomCommandHandler


# NOT ASYNC
def restr_members(bot, chat_id, members, messages=False, media=False, other=False, previews=False):
    for mem in members:
        if mem.user in SUDO_USERS:
            pass
        try:
            bot.restrict_chat_member(chat_id, mem.user,
                                     can_send_messages=messages,
                                     can_send_media_messages=media,
                                     can_send_other_messages=other,
                                     can_add_web_page_previews=previews)
        except TelegramError:
            pass


# NOT ASYNC
def unrestr_members(bot, chat_id, members, messages=True, media=True, other=True, previews=True):
    for mem in members:
        try:
            bot.restrict_chat_member(chat_id, mem.user,
                                     can_send_messages=messages,
                                     can_send_media_messages=media,
                                     can_send_other_messages=other,
                                     can_add_web_page_previews=previews)
        except TelegramError:
            pass


@run_async
def locktypes(bot: Bot, update: Update):
    update.effective_message.reply_text("\n - ".join(["Locks: "] + list(LOCK_TYPES) + list(RESTRICTION_TYPES)))


@run_async
@user_admin
@loggable
def add_whitelist(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    entities = message.parse_entities([MessageEntity.URL])
    added = []
    for url in entities.values():
        if sql.add_whitelist(chat.id, url):
            added.append(url)
    if added:
        message.reply_text("Added to whitelist:\n- "+'\n- '.join(added))
        return "<b>{}:</b>" \
               "\n#WHITELIST" \
               "\n<b>Admin:</b> {}" \
               "\nWhitelisted:\n<pre>- {}</pre>".format(html.escape(chat.title),
                                                         mention_html(user.id, user.first_name),
                                                         html.escape('\n- '.join(added)))
    else:
        message.reply_text("No URLs were added to the whitelist")
        return ""


@run_async
@user_admin
@loggable
def remove_whitelist(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    entities = message.parse_entities(MessageEntity.URL)
    removed = []
    for url in entities.values():
        if sql.remove_whitelist(chat.id, url):
            removed.append(url)
    if removed:
        message.reply_text("Removed from whitelist:\n<pre>- {}</pre>".format(html.escape('\n- '.join(removed))),
                           parse_mode=ParseMode.HTML)
        return "<b>{}:</b>" \
               "\n#UNWHITELIST" \
               "\n<b>Admin:</b> {}" \
               "\nRemoved from whitelist:\n<pre>- {}</pre>".format(html.escape(chat.title),
                                                                    mention_html(user.id, user.first_name),
                                                                    html.escape('\n- '.join(removed)))
    else:
        message.reply_text("Could not remove URL from whitelist or URL not found.")
        return ""


@run_async
def list_whitelist(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    all_whitelisted = sql.get_whitelist(chat.id)

    if not all_whitelisted:
        message.reply_text("No URLs are whitelisted here!")
        return

    whitelist_string = "Whitelisted URLs:\n- "+'\n- '.join(all_whitelisted)

    for i, part in enumerate(split_message(whitelist_string)):
        #only send first part as a reply
        if i == 0:
            message.reply_text(part, disable_web_page_preview=True)
        else:
            chat.send_message(part, disable_web_page_preview=True)


@user_admin
@bot_can_delete
@loggable
def lock(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    if can_delete(chat, bot.id):
        if len(args) >= 1:
            if args[0] in LOCK_TYPES:
                sql.update_lock(chat.id, args[0], locked=True)
                message.reply_text("Locked {} messages for all non-admins!".format(args[0]))

                return "<b>{}:</b>" \
                       "\n#LOCK" \
                       "\n<b>Admin:</b> {}" \
                       "\nLocked <code>{}</code>.".format(html.escape(chat.title),
                                                          mention_html(user.id, user.first_name), args[0])

            elif args[0] in RESTRICTION_TYPES:
                sql.update_restriction(chat.id, args[0], locked=True)
                if args[0] == "previews":
                    members = users_sql.get_chat_members(str(chat.id))
                    restr_members(bot, chat.id, members, messages=True, media=True, other=True)

                message.reply_text("Locked {} for all non-admins!".format(args[0]))
                return "<b>{}:</b>" \
                       "\n#LOCK" \
                       "\n<b>Admin:</b> {}" \
                       "\nLocked <code>{}</code>.".format(html.escape(chat.title),
                                                          mention_html(user.id, user.first_name), args[0])

            else:
                message.reply_text("What are you trying to lock...? Try /locktypes for the list of lockables")

    else:
        message.reply_text("I'm not an administrator, or haven't got delete rights.")

    return ""


@run_async
@user_admin
@loggable
def unlock(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    if is_user_admin(chat, message.from_user.id):
        if len(args) >= 1:
            if args[0] in LOCK_TYPES:
                sql.update_lock(chat.id, args[0], locked=False)
                message.reply_text("Unlocked {} for everyone!".format(args[0]))
                return "<b>{}:</b>" \
                       "\n#UNLOCK" \
                       "\n<b>Admin:</b> {}" \
                       "\nUnlocked <code>{}</code>.".format(html.escape(chat.title),
                                                            mention_html(user.id, user.first_name), args[0])

            elif args[0] in RESTRICTION_TYPES:
                sql.update_restriction(chat.id, args[0], locked=False)
                """
                members = users_sql.get_chat_members(chat.id)
                if args[0] == "messages":
                    unrestr_members(bot, chat.id, members, media=False, other=False, previews=False)

                elif args[0] == "media":
                    unrestr_members(bot, chat.id, members, other=False, previews=False)

                elif args[0] == "other":
                    unrestr_members(bot, chat.id, members, previews=False)

                elif args[0] == "previews":
                    unrestr_members(bot, chat.id, members)

                elif args[0] == "all":
                    unrestr_members(bot, chat.id, members, True, True, True, True)
                """
                message.reply_text("Unlocked {} for everyone!".format(args[0]))

                return "<b>{}:</b>" \
                       "\n#UNLOCK" \
                       "\n<b>Admin:</b> {}" \
                       "\nUnlocked <code>{}</code>.".format(html.escape(chat.title),
                                                            mention_html(user.id, user.first_name), args[0])
            else:
                message.reply_text("Unlock filter unknown! Try /locktypes.")

        else:
            bot.sendMessage(chat.id, "Unlock filter unknown! Try /locktypes.")

    return ""


@run_async
@user_not_admin
def del_lockables(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]

    for lockable, filter in LOCK_TYPES.items():
        if filter(message) and sql.is_locked(chat.id, lockable) and can_delete(chat, bot.id):
            if lockable == "bots":
                new_members = update.effective_message.new_chat_members
                for new_mem in new_members:
                    if new_mem.is_bot:
                        if not is_bot_admin(chat, bot.id):
                            message.reply_text("Cannot ban a bot as I'm not an admin")
                            return

                        chat.kick_member(new_mem.id)
                        message.reply_text("Only admins can add bots!")
            else:
                #allow whitelisted URLs
                if lockable == 'url':
                    entities = set(message.parse_entities([MessageEntity.URL]).values())

                    # MessageEntity.TEXT_LINK could be added in the filter above, but would return the text, not the
                    # url. So I must add all entities that have a 'url' field separately
                    entities = entities | set(entity.url for entity in message.entities if entity.url)
                    #if all URLs are any of the whitelisted ones, accept the message
                    if all( any(regexp.search(text) for regexp in sql.get_whitelist(chat.id).values())
                            for text in entities):
                        continue
                try:
                    message.delete()
                except BadRequest as excp:
                    if excp.message == "Message to delete not found":
                        pass
                    else:
                        LOGGER.exception("ERROR in lockables")

            break


@run_async
@user_not_admin
def rest_handler(bot: Bot, update: Update):
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    for restriction, filter in RESTRICTION_TYPES.items():
        if filter(msg) and sql.is_restr_locked(chat.id, restriction) and can_delete(chat, bot.id):
            try:
                msg.delete()
            except BadRequest as excp:
                if excp.message == "Message to delete not found":
                    pass
                else:
                    LOGGER.exception("ERROR in restrictions")
            break


def build_lock_message(chat_id):
    locks = sql.get_locks(chat_id)
    restr = sql.get_restr(chat_id)
    if not (locks or restr):
        res = "There are no current locks in this chat."
    else:
        res = "These are the locks in this chat:"
        if locks:
            res += "\n - sticker = `{}`" \
                   "\n - audio = `{}`" \
                   "\n - voice = `{}`" \
                   "\n - document = `{}`" \
                   "\n - video = `{}`" \
                   "\n - contact = `{}`" \
                   "\n - photo = `{}`" \
                   "\n - gif = `{}`" \
                   "\n - url = `{}`" \
                   "\n - bots = `{}`" \
                   "\n - forward = `{}`" \
                   "\n - game = `{}`".format(locks.sticker, locks.audio, locks.voice, locks.document,
                                             locks.video, locks.contact, locks.photo, locks.gif, locks.url, locks.bots,
                                             locks.forward, locks.game)
        if restr:
            res += "\n - messages = `{}`" \
                   "\n - media = `{}`" \
                   "\n - other = `{}`" \
                   "\n - previews = `{}`" \
                   "\n - all = `{}`".format(restr.messages, restr.media, restr.other, restr.preview,
                                            all([restr.messages, restr.media, restr.other, restr.preview]))
    return res


@run_async
@user_admin
def list_locks(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]

    res = build_lock_message(chat.id)

    update.effective_message.reply_text(res, parse_mode=ParseMode.MARKDOWN)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return build_lock_message(chat_id)


__help__ = """
 - /locktypes: a list of possible locktypes
 - /whitelisted: lists urls in this chat's whitelist

*Admin only:*
 - /lock <type>: lock items of a certain type (not available in private)
 - /unlock <type>: unlock items of a certain type (not available in private)
 - /locks: the current list of locks in this chat.
 - /whitelist <url>: add url to whitelist so it's not deleted by URL lock (accepts multiple)
 - /unwhitelist <url>: remove url from whitelist (accepts multiple)

Locks can be used to restrict a group's users.
eg:
Locking urls will auto-delete all messages with urls which haven't been whitelisted, locking stickers will delete all \
stickers, etc.
Locking bots will stop non-admins from adding bots to the chat.
"""

__mod_name__ = "Locks"

LOCKTYPES_HANDLER = DisableAbleCommandHandler("locktypes", locktypes)
LOCK_HANDLER = CommandHandler("lock", lock, pass_args=True, filters=Filters.group)
UNLOCK_HANDLER = CommandHandler("unlock", unlock, pass_args=True, filters=Filters.group)
LOCKED_HANDLER = CommandHandler("locks", list_locks, filters=Filters.group)
WHITELIST_HANDLER = CommandHandler("whitelist", add_whitelist, filters=Filters.group)
UNWHITELIST_HANDLER = CommandHandler("unwhitelist", remove_whitelist, filters=Filters.group)
WHITELISTED_HANDLER = DisableAbleCommandHandler("whitelisted", list_whitelist, filters=Filters.group, admin_ok=True)

dispatcher.add_handler(LOCK_HANDLER)
dispatcher.add_handler(UNLOCK_HANDLER)
dispatcher.add_handler(LOCKTYPES_HANDLER)
dispatcher.add_handler(LOCKED_HANDLER)
dispatcher.add_handler(WHITELIST_HANDLER)
dispatcher.add_handler(UNWHITELIST_HANDLER)
dispatcher.add_handler(WHITELISTED_HANDLER)

dispatcher.add_handler(MessageHandler(Filters.all & Filters.group, del_lockables), PERM_GROUP)
dispatcher.add_handler(MessageHandler(Filters.all & Filters.group, rest_handler), REST_GROUP)