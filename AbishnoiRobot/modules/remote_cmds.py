from AbishnoiRobot import dispatcher
from AbishnoiRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    is_bot_admin,
    is_user_ban_protected,
    is_user_in_chat,
)
from AbishnoiRobot.modules.helper_funcs.extraction import extract_user_and_text
from AbishnoiRobot.modules.helper_funcs.filters import CustomFilters
from telegram import Update, ChatPermissions
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, run_async

RBAN_ERRORS = {
    "Usᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "Nᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "Usᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "Pᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "Gʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "Nᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴘᴜɴᴄʜ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "Cʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "Oɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴘᴜɴᴄʜ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "Cʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "Nᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RUNBAN_ERRORS = {
    "Usᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "Nᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "Usᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "Pᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "Gʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "Nᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴘᴜɴᴄʜ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "Cʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "Oɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴘᴜɴᴄʜ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "Cʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "Nᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RKICK_ERRORS = {
    "Usᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "Nᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "Usᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "Pᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "Gʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "Nᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴘᴜɴᴄʜ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "Cʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "Oɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴘᴜɴᴄʜ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "Cʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "Nᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RMUTE_ERRORS = {
    "Usᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "Nᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "Usᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "Pᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "Gʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "Nᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴘᴜɴᴄʜ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "Cʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "Oɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴘᴜɴᴄʜ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "Cʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "Nᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RUNMUTE_ERRORS = {
    "Usᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "Nᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "Usᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "Pᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "Gʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "Nᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴘᴜɴᴄʜ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "Cʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "Oɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴘᴜɴᴄʜ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "Cʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "Nᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}


@run_async
@bot_admin
def rban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ chat/user.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ.."
        )
        return
    elif not chat_id:
        message.reply_text("Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text(
                "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! Mᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ID ᴀɴᴅ I'ᴍ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ."
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("I'ᴍ sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "I ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ʙᴀɴ ᴜsᴇʀs . "
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I ʀᴇᴀʟʟʏ ᴡɪsʜ I ᴄᴏᴜʟᴅ ʙᴀɴ ᴀᴅᴍɪɴs...")
        return

    if user_id == bot.id:
        message.reply_text("I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ BAN ᴍʏsᴇʟғ, ᴀʀᴇ ʏᴏᴜ ᴄʀᴀᴢʏ?")
        return

    try:
        chat.kick_member(user_id)
        message.reply_text("Bᴀɴɴᴇᴅ ғʀᴏᴍ ᴄʜᴀᴛ!")
    except BadRequest as excp:
        if excp.message == "Rᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            message.reply_text("Banned!", quote=False)
        elif excp.message in RBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s ",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Wᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ʙᴀɴ ᴛʜᴀᴛ ᴜsᴇʀ.")


@run_async
@bot_admin
def runban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ.."
        )
        return
    elif not chat_id:
        message.reply_text("Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ..")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text(
                "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! Mᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ID ᴀɴᴅ I'ᴍ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ."
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("I'ᴍ sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "I ᴄᴀɴ'ᴛ ᴜɴʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴜɴʙᴀɴ ᴜsᴇʀs."
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ ᴛʜᴇʀᴇ")
            return
        else:
            raise

    if is_user_in_chat(chat, user_id):
        message.reply_text(
            "Wʜʏ ᴀʀᴇ ʏᴏᴜ ᴛʀʏɪɴɢ ᴛᴏ ʀᴇᴍᴏᴛᴇʟʏ ᴜɴʙᴀɴ sᴏᴍᴇᴏɴᴇ ᴛʜᴀᴛ's ᴀʟʀᴇᴀᴅʏ ɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ?"
        )
        return

    if user_id == bot.id:
        message.reply_text("I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ UNBAN ᴍʏsᴇʟғ, I'ᴍ ᴀɴ ᴀᴅᴍɪɴ ᴛʜᴇʀᴇ!")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("Yᴇᴘ, ᴛʜɪs ᴜsᴇʀ ᴄᴀɴ ᴊᴏɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ!")
    except BadRequest as excp:
        if excp.message == "Rᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            message.reply_text("Unbanned!", quote=False)
        elif excp.message in RUNBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴜɴʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s ",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Wᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴜɴʙᴀɴ ᴛʜᴀᴛ ᴜsᴇʀ")


@run_async
@bot_admin
def rkick(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ.."
        )
        return
    elif not chat_id:
        message.reply_text("Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text(
                "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! Mᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ID ᴀɴᴅ I'ᴍ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ."
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("ɪ'ᴍ  sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "I ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴘᴜɴᴄʜ ᴜsᴇʀs."
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I ʀᴇᴀʟʟʏ ᴡɪsʜ I ᴄᴏᴜʟᴅ ᴘᴜɴᴄʜ ᴀᴅᴍɪɴs...")
        return

    if user_id == bot.id:
        message.reply_text("I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ ᴘᴜɴᴄʜ ᴍʏsᴇʟғ, ᴀʀᴇ ʏᴏᴜ ᴄʀᴀᴢʏ?")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("Pᴜɴᴄʜᴇᴅ ғʀᴏᴍ ᴄʜᴀᴛ!!")
    except BadRequest as excp:
        if excp.message == "Rᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            message.reply_text("Punched!", quote=False)
        elif excp.message in RKICK_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴘᴜɴᴄʜɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Wᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴘᴜɴᴄʜ ᴛʜᴀᴛ ᴜsᴇʀ.")


@run_async
@bot_admin
def rmute(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ.."
        )
        return
    elif not chat_id:
        message.reply_text("Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text(
                "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! Mᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ID ᴀɴᴅ I'ᴍ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ."
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("ɪ'ᴍ  sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "I ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴍᴜᴛᴇ ᴜsᴇʀs."
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I ʀᴇᴀʟʟʏ ᴡɪsʜ I ᴄᴏᴜʟᴅ ᴍᴜᴛᴇ ᴀᴅᴍɪɴs...")
        return

    if user_id == bot.id:
        message.reply_text("I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ MUTE ᴍʏsᴇʟғ, ᴀʀᴇ ʏᴏᴜ ᴄʀᴀᴢʏ?")
        return

    try:
        bot.restrict_chat_member(
            chat.id, user_id, permissions=ChatPermissions(can_send_messages=False)
        )
        message.reply_text("Mᴜᴛᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴄʜᴀᴛ!")
    except BadRequest as excp:
        if excp.message == "Rᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            message.reply_text("Muted!", quote=False)
        elif excp.message in RMUTE_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴍᴜᴛᴇ  ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Wᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴍᴜᴛᴇ ᴛʜᴀᴛ ᴜsᴇʀ.")


@run_async
@bot_admin
def runmute(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ.."
        )
        return
    elif not chat_id:
        message.reply_text("Yᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text(
                "Cʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! Mᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ID ᴀɴᴅ I'ᴍ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ."
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("ɪ'ᴍ  sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "I ᴄᴀɴ'ᴛ ᴜɴʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴜɴʙᴀɴ ᴜsᴇʀs."
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "Usᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ there")
            return
        else:
            raise

    if is_user_in_chat(chat, user_id):
        if (
            member.can_send_messages
            and member.can_send_media_messages
            and member.can_send_other_messages
            and member.can_add_web_page_previews
        ):
            message.reply_text("Tʜɪs ᴜsᴇʀ ᴀʟʀᴇᴀᴅʏ ʜᴀs ᴛʜᴇ ʀɪɢʜᴛ ᴛᴏ sᴘᴇᴀᴋ ɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ.")
            return

    if user_id == bot.id:
        message.reply_text("I'm not gonna UNMUTE myself, I'm an admin there!")
        return

    try:
        bot.restrict_chat_member(
            chat.id,
            int(user_id),
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        message.reply_text("Yᴇᴘ, ᴛʜɪs ᴜsᴇʀ ᴄᴀɴ ᴛᴀʟᴋ ɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ!")
    except BadRequest as excp:
        if excp.message == "Rᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            message.reply_text("Unmuted!", quote=False)
        elif excp.message in RUNMUTE_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴜɴᴍɴᴜᴛɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Wᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴜɴᴍᴜᴛᴇ ᴛʜᴀᴛ ᴜsᴇʀ.")


RBAN_HANDLER = CommandHandler("rban", rban, filters=CustomFilters.sudo_filter)
RUNBAN_HANDLER = CommandHandler("runban", runban, filters=CustomFilters.sudo_filter)
RKICK_HANDLER = CommandHandler("rpunch", rkick, filters=CustomFilters.sudo_filter)
RMUTE_HANDLER = CommandHandler("rmute", rmute, filters=CustomFilters.sudo_filter)
RUNMUTE_HANDLER = CommandHandler("runmute", runmute, filters=CustomFilters.sudo_filter)

dispatcher.add_handler(RBAN_HANDLER)
dispatcher.add_handler(RUNBAN_HANDLER)
dispatcher.add_handler(RKICK_HANDLER)
dispatcher.add_handler(RMUTE_HANDLER)
dispatcher.add_handler(RUNMUTE_HANDLER)
