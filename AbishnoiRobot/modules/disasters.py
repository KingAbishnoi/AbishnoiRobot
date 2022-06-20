import html
import json
import os
from typing import Optional

from AbishnoiRobot import (
    DEV_USERS,
    OWNER_ID,
    DRAGONS,
    SUPPORT_CHAT,
    DEMONS,
    TIGERS,
    WOLVES,
    dispatcher,
)
from AbishnoiRobot.modules.helper_funcs.chat_status import (
    dev_plus,
    sudo_plus,
    whitelist_plus,
)
from AbishnoiRobot.modules.helper_funcs.extraction import extract_user
from AbishnoiRobot.modules.log_channel import gloggable
from telegram import ParseMode, TelegramError, Update
from telegram.ext import CallbackContext, CommandHandler, run_async
from telegram.utils.helpers import mention_html

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), "AbishnoiRobot/elevated_users.json")


def check_user_id(user_id: int, context: CallbackContext) -> Optional[str]:
    bot = context.bot
    if not user_id:
        reply = "Tʜᴀᴛ...ɪs ᴀ ᴄʜᴀᴛ! ʙᴀᴋᴀ ᴋᴀ ᴏᴍᴀᴇ?"

    elif user_id == bot.id:
        reply = "Tʜɪs ᴅᴏᴇs ɴᴏᴛ ᴡᴏʀᴋ ᴛʜᴀᴛ ᴡᴀʏ."

    else:
        reply = None
    return reply


# This can serve as a deeplink example.
# disasters =
# """ Text here """

# do not async, not a handler
# def send_disasters(update):
#    update.effective_message.reply_text(
#        disasters, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

### Deep link example ends


@run_async
@dev_plus
@gloggable
def addsudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("Tʜɪs ᴍᴇᴍʙᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀ Dʀᴀɢᴏɴ Dɪsᴀsᴛᴇʀ")
        return ""

    if user_id in DEMONS:
        rt += "Rᴇǫᴜᴇsᴛᴇᴅ HA ᴛᴏ ᴘʀᴏᴍᴏᴛᴇ ᴀ Dᴇᴍᴏɴ Dɪsᴀsᴛᴇʀ ᴛᴏ Dʀᴀɢᴏɴ."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "Rᴇǫᴜᴇsᴛᴇᴅ HA ᴛᴏ ᴘʀᴏᴍᴏᴛᴇ ᴀ Wᴏʟғ Dɪsᴀsᴛᴇʀ ᴛᴏ Dʀᴀɢᴏɴ."
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["sudos"].append(user_id)
    DRAGONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt
        + "\nSᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ Dɪsᴀsᴛᴇʀ ʟᴇᴠᴇʟ ᴏғ {} ᴛᴏ Dʀᴀɢᴏɴ !".format(
            user_member.first_name
        )
    )

    log_message = (
        f"#SUDO\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@sudo_plus
@gloggable
def addsupport(
    update: Update,
    context: CallbackContext,
) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "Rᴇǫᴜᴇsᴛᴇᴅ HA ᴛᴏ ᴅᴇᴍᴏᴛᴇ ᴛʜɪs Dʀᴀɢᴏɴ ᴛᴏ Dᴇᴍᴏɴ"
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        message.reply_text("Tʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀ Dᴇᴍᴏɴ Dɪsᴀsᴛᴇʀ.")
        return ""

    if user_id in WOLVES:
        rt += "Rᴇǫᴜᴇsᴛᴇᴅ HA ᴛᴏ ᴘʀᴏᴍᴏᴛᴇ ᴛʜɪs Wᴏʟғ Dɪsᴀsᴛᴇʀ ᴛᴏ Dᴇᴍᴏɴ"
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["supports"].append(user_id)
    DEMONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\n{user_member.first_name} ᴡᴀs ᴀᴅᴅᴇᴅ ᴀs ᴀ Dᴇᴍᴏɴ Dɪsᴀsᴛᴇʀ!"
    )

    log_message = (
        f"#SUPPORT\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@sudo_plus
@gloggable
def addwhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "Tʜɪs ᴍᴇᴍʙᴇʀ ɪs ᴀ Dʀᴀɢᴏɴ Dɪsᴀsᴛᴇʀ, Dᴇᴍᴏᴛɪɴɢ ᴛᴏ Wᴏʟғ."
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "Tʜɪs ᴍᴇᴍʙᴇʀ ɪs ᴀ Dʀᴀɢᴏɴ Dɪsᴀsᴛᴇʀ, Dᴇᴍᴏᴛɪɴɢ ᴛᴏ Wᴏʟғ."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        message.reply_text("Tʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀ Wᴏʟғ Dɪsᴀsᴛᴇʀ.")
        return ""

    data["whitelists"].append(user_id)
    WOLVES.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSᴜᴄᴄᴇssғᴜʟʟʏ ᴘʀᴏᴍᴏᴛᴇᴅ {user_member.first_name} ᴛᴏ ᴀ Wᴏʟғ Dɪsᴀsᴛᴇʀ !"
    )

    log_message = (
        f"#WHITELIST\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@sudo_plus
@gloggable
def addtiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "Tʜɪs ᴍᴇᴍʙᴇʀ ɪs ᴀ Dʀᴀɢᴏɴ Dɪsᴀsᴛᴇʀ, Dᴇᴍᴏᴛɪɴɢ ᴛᴏ Tɪɢᴇʀ."
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "Tʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀ Dᴇᴍᴏɴ Dɪsᴀsᴛᴇʀ, Dᴇᴍᴏᴛɪɴɢ ᴛᴏ Tɪɢᴇʀ."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "Tʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀ Wᴏʟғ Dɪsᴀsᴛᴇʀ, Dᴇᴍᴏᴛɪɴɢ ᴛᴏ Tɪɢᴇʀ."
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    if user_id in TIGERS:
        message.reply_text("Tʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀ Tɪɢᴇʀ.")
        return ""

    data["tigers"].append(user_id)
    TIGERS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSᴜᴄᴄᴇssғᴜʟʟʏ ᴘʀᴏᴍᴏᴛᴇᴅ {user_member.first_name} ᴛᴏ ᴀ Tɪɢᴇʀ Dɪsᴀsᴛᴇʀ!"
    )

    log_message = (
        f"#TIGER\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@dev_plus
@gloggable
def removesudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("Rᴇǫᴜᴇsᴛᴇᴅ HA ᴛᴏ ᴅᴇᴍᴏᴛᴇ ᴛʜɪs ᴜsᴇʀ ᴛᴏ Cɪᴠɪʟɪᴀɴ")
        DRAGONS.remove(user_id)
        data["sudos"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNSUDO\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = "<b>{}:</b>\n".format(html.escape(chat.title)) + log_message

        return log_message

    else:
        message.reply_text("Tʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴀ Dʀᴀɢᴏɴ Dɪsᴀsᴛᴇʀ!")
        return ""


@run_async
@sudo_plus
@gloggable
def removesupport(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DEMONS:
        message.reply_text("Rᴇǫᴜᴇsᴛᴇᴅ HA ᴛᴏ ᴅᴇᴍᴏᴛᴇ ᴛʜɪs ᴜsᴇʀ ᴛᴏ Cɪᴠɪʟɪᴀɴ")
        DEMONS.remove(user_id)
        data["supports"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNSUPPORT\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message

    else:
        message.reply_text("Tʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴀ Dᴇᴍᴏɴ ʟᴇᴠᴇʟ Dɪsᴀsᴛᴇʀ!")
        return ""


@run_async
@sudo_plus
@gloggable
def removewhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in WOLVES:
        message.reply_text("Demoting to normal user")
        WOLVES.remove(user_id)
        data["whitelists"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNWHITELIST\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("Tʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴀ Wᴏʟғ Dɪsᴀsᴛᴇʀ!")
        return ""


@run_async
@sudo_plus
@gloggable
def removetiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in TIGERS:
        message.reply_text("Demoting to normal user")
        TIGERS.remove(user_id)
        data["tigers"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNTIGER\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("Dᴇᴍᴏᴛɪɴɢ ᴛᴏ ɴᴏʀᴍᴀʟ ᴜsᴇ!")
        return ""


@run_async
@whitelist_plus
def whitelistlist(update: Update, context: CallbackContext):
    reply = "<b>Kɴᴏᴡɴ Wᴏʟғ Dɪsᴀsᴛᴇʀs 🐺:</b>\n"
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>", parse_mode=ParseMode.HTML
    )
    bot = context.bot
    for each_user in WOLVES:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)

            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def tigerlist(update: Update, context: CallbackContext):
    reply = "<b>Kɴᴏᴡɴ Tɪɢᴇʀ Dɪsᴀsᴛᴇʀs 🐯:</b>\n"
    m = update.effective_message.reply_text(
        "<code>Gᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ..</code>", parse_mode=ParseMode.HTML
    )
    bot = context.bot
    for each_user in TIGERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def supportlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Gᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ..</code>", parse_mode=ParseMode.HTML
    )
    reply = "<b>Kɴᴏᴡɴ Dᴇᴍᴏɴ Dɪsᴀsᴛᴇʀs 👹:</b>\n"
    for each_user in DEMONS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def sudolist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Gᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ..</code>", parse_mode=ParseMode.HTML
    )
    true_sudo = list(set(DRAGONS) - set(DEV_USERS))
    reply = "<b>Kɴᴏᴡɴ Dʀᴀɢᴏɴ Dɪsᴀsᴛᴇʀs 🐉:</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def devlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Gᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ..</code>", parse_mode=ParseMode.HTML
    )
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b>Hᴇʀᴏ Assᴏᴄɪᴀᴛɪᴏɴ Mᴇᴍʙᴇʀs ⚡️:</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


SUDO_HANDLER = CommandHandler(("addsudo", "adddragon"), addsudo)
SUPPORT_HANDLER = CommandHandler(("addsupport", "adddemon"), addsupport)
TIGER_HANDLER = CommandHandler(("addtiger"), addtiger)
WHITELIST_HANDLER = CommandHandler(("addwhitelist", "addwolf"), addwhitelist)
UNSUDO_HANDLER = CommandHandler(("removesudo", "removedragon"), removesudo)
UNSUPPORT_HANDLER = CommandHandler(("removesupport", "removedemon"), removesupport)
UNTIGER_HANDLER = CommandHandler(("removetiger"), removetiger)
UNWHITELIST_HANDLER = CommandHandler(("removewhitelist", "removewolf"), removewhitelist)

WHITELISTLIST_HANDLER = CommandHandler(["whitelistlist", "wolves"], whitelistlist)
TIGERLIST_HANDLER = CommandHandler(["tigers"], tigerlist)
SUPPORTLIST_HANDLER = CommandHandler(["supportlist", "demons"], supportlist)
SUDOLIST_HANDLER = CommandHandler(["sudolist", "dragons"], sudolist)
DEVLIST_HANDLER = CommandHandler(["devlist", "heroes"], devlist)

dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SUPPORT_HANDLER)
dispatcher.add_handler(TIGER_HANDLER)
dispatcher.add_handler(WHITELIST_HANDLER)
dispatcher.add_handler(UNSUDO_HANDLER)
dispatcher.add_handler(UNSUPPORT_HANDLER)
dispatcher.add_handler(UNTIGER_HANDLER)
dispatcher.add_handler(UNWHITELIST_HANDLER)

dispatcher.add_handler(WHITELISTLIST_HANDLER)
dispatcher.add_handler(TIGERLIST_HANDLER)
dispatcher.add_handler(SUPPORTLIST_HANDLER)
dispatcher.add_handler(SUDOLIST_HANDLER)
dispatcher.add_handler(DEVLIST_HANDLER)

__mod_name__ = "Devs​"
__handlers__ = [
    SUDO_HANDLER,
    SUPPORT_HANDLER,
    TIGER_HANDLER,
    WHITELIST_HANDLER,
    UNSUDO_HANDLER,
    UNSUPPORT_HANDLER,
    UNTIGER_HANDLER,
    UNWHITELIST_HANDLER,
    WHITELISTLIST_HANDLER,
    TIGERLIST_HANDLER,
    SUPPORTLIST_HANDLER,
    SUDOLIST_HANDLER,
    DEVLIST_HANDLER,
]
