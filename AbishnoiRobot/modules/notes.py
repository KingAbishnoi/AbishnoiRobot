import re, ast
from io import BytesIO
import random
from typing import Optional

import AbishnoiRobot.modules.sql.notes_sql as sql
from AbishnoiRobot import LOGGER, JOIN_LOGGER, SUPPORT_CHAT, dispatcher, DRAGONS
from AbishnoiRobot.modules.disable import DisableAbleCommandHandler
from AbishnoiRobot.modules.helper_funcs.handlers import MessageHandlerChecker
from AbishnoiRobot.modules.helper_funcs.chat_status import user_admin, connection_status
from AbishnoiRobot.modules.helper_funcs.misc import build_keyboard, revert_buttons
from AbishnoiRobot.modules.helper_funcs.msg_types import get_note_type
from AbishnoiRobot.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
)
from telegram import (
    MAX_MESSAGE_LENGTH,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
    Update,
    InlineKeyboardButton,
)
from telegram.error import BadRequest
from telegram.utils.helpers import escape_markdown, mention_markdown
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import run_async

FILE_MATCHER = re.compile(r"^###file_id(!photo)?###:(.*?)(?:\s|$)")
STICKER_MATCHER = re.compile(r"^###sticker(!photo)?###:")
BUTTON_MATCHER = re.compile(r"^###button(!photo)?###:(.*?)(?:\s|$)")
MYFILE_MATCHER = re.compile(r"^###file(!photo)?###:")
MYPHOTO_MATCHER = re.compile(r"^###photo(!photo)?###:")
MYAUDIO_MATCHER = re.compile(r"^###audio(!photo)?###:")
MYVOICE_MATCHER = re.compile(r"^###voice(!photo)?###:")
MYVIDEO_MATCHER = re.compile(r"^###video(!photo)?###:")
MYVIDEONOTE_MATCHER = re.compile(r"^###video_note(!photo)?###:")

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: dispatcher.bot.send_message,
    sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
    sql.Types.STICKER.value: dispatcher.bot.send_sticker,
    sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
    sql.Types.PHOTO.value: dispatcher.bot.send_photo,
    sql.Types.AUDIO.value: dispatcher.bot.send_audio,
    sql.Types.VOICE.value: dispatcher.bot.send_voice,
    sql.Types.VIDEO.value: dispatcher.bot.send_video,
}


# Do not async
def get(update, context, notename, show_none=True, no_format=False):
    bot = context.bot
    chat_id = update.effective_message.chat.id
    note_chat_id = update.effective_chat.id
    note = sql.get_note(note_chat_id, notename)
    message = update.effective_message  # type: Optional[Message]

    if note:
        if MessageHandlerChecker.check_user(update.effective_user.id):
            return
        # If we're replying to a message, reply to that message (unless it's an error)
        if message.reply_to_message:
            reply_id = message.reply_to_message.message_id
        else:
            reply_id = message.message_id
        if note.is_reply:
            if JOIN_LOGGER:
                try:
                    bot.forward_message(
                        chat_id=chat_id, from_chat_id=JOIN_LOGGER, message_id=note.value
                    )
                except BadRequest as excp:
                    if excp.message == "Mᴇssᴀɢᴇ ᴛᴏ ғᴏʀᴡᴀʀᴅ ɴᴏᴛ ғᴏᴜɴᴅ":
                        message.reply_text(
                            "This message seems to have been lost - I'll remove it "
                            "from your notes list."
                        )
                        sql.rm_note(note_chat_id, notename)
                    else:
                        raise
            else:
                try:
                    bot.forward_message(
                        chat_id=chat_id, from_chat_id=chat_id, message_id=note.value
                    )
                except BadRequest as excp:
                    if excp.message == "Mᴇssᴀɢᴇ ᴛᴏ ғᴏʀᴡᴀʀᴅ ɴᴏᴛ ғᴏᴜɴᴅ":
                        message.reply_text(
                            "Lᴏᴏᴋs ʟɪᴋᴇ ᴛʜᴇ ᴏʀɪɢɪɴᴀʟ sᴇɴᴅᴇʀ ᴏғ ᴛʜɪs ɴᴏᴛᴇ ʜᴀs ᴅᴇʟᴇᴛᴇᴅ "
                            "ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇ - sᴏʀʀʏ! Gᴇᴛ ʏᴏᴜʀ ʙᴏᴛ ᴀᴅᴍɪɴ ᴛᴏ sᴛᴀʀᴛ ᴜsɪɴɢ ᴀ "
                            "ᴍᴇssᴀɢᴇ ᴅᴜᴍᴘ ᴛᴏ ᴀᴠᴏɪᴅ ᴛʜɪs. I'ʟʟ ʀᴇᴍᴏᴠᴇ ᴛʜɪs ɴᴏᴛᴇ ғʀᴏᴍ "
                            "ʏᴏᴜʀ sᴀᴠᴇᴅ ɴᴏᴛᴇs."
                        )
                        sql.rm_note(note_chat_id, notename)
                    else:
                        raise
        else:
            VALID_NOTE_FORMATTERS = [
                "first",
                "last",
                "fullname",
                "username",
                "id",
                "chatname",
                "mention",
            ]
            valid_format = escape_invalid_curly_brackets(
                note.value, VALID_NOTE_FORMATTERS
            )
            if valid_format:
                if not no_format:
                    if "%%%" in valid_format:
                        split = valid_format.split("%%%")
                        if all(split):
                            text = random.choice(split)
                        else:
                            text = valid_format
                    else:
                        text = valid_format
                else:
                    text = valid_format
                text = text.format(
                    first=escape_markdown(message.from_user.first_name),
                    last=escape_markdown(
                        message.from_user.last_name or message.from_user.first_name
                    ),
                    fullname=escape_markdown(
                        " ".join(
                            [message.from_user.first_name, message.from_user.last_name]
                            if message.from_user.last_name
                            else [message.from_user.first_name]
                        )
                    ),
                    username="@" + message.from_user.username
                    if message.from_user.username
                    else mention_markdown(
                        message.from_user.id, message.from_user.first_name
                    ),
                    mention=mention_markdown(
                        message.from_user.id, message.from_user.first_name
                    ),
                    chatname=escape_markdown(
                        message.chat.title
                        if message.chat.type != "private"
                        else message.from_user.first_name
                    ),
                    id=message.from_user.id,
                )
            else:
                text = ""

            keyb = []
            parseMode = ParseMode.MARKDOWN
            buttons = sql.get_buttons(note_chat_id, notename)
            if no_format:
                parseMode = None
                text += revert_buttons(buttons)
            else:
                keyb = build_keyboard(buttons)

            keyboard = InlineKeyboardMarkup(keyb)

            try:
                if note.msgtype in (sql.Types.BUTTON_TEXT, sql.Types.TEXT):
                    bot.send_message(
                        chat_id,
                        text,
                        reply_to_message_id=reply_id,
                        parse_mode=parseMode,
                        disable_web_page_preview=True,
                        reply_markup=keyboard,
                    )
                else:
                    ENUM_FUNC_MAP[note.msgtype](
                        chat_id,
                        note.file,
                        caption=text,
                        reply_to_message_id=reply_id,
                        parse_mode=parseMode,
                        disable_web_page_preview=True,
                        reply_markup=keyboard,
                    )

            except BadRequest as excp:
                if excp.message == "Entity_mention_user_invalid":
                    message.reply_text(
                        "Lᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ ᴍᴇɴᴛɪᴏɴ sᴏᴍᴇᴏɴᴇ I'ᴠᴇ ɴᴇᴠᴇʀ sᴇᴇɴ ʙᴇғᴏʀᴇ. Iғ ʏᴏᴜ ʀᴇᴀʟʟʏ "
                        "ᴡᴀɴᴛ ᴛᴏ ᴍᴇɴᴛɪᴏɴ ᴛʜᴇᴍ, ғᴏʀᴡᴀʀᴅ ᴏɴᴇ ᴏғ ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇs ᴛᴏ ᴍᴇ, ᴀɴᴅ I'ʟʟ ʙᴇ ᴀʙʟᴇ "
                        "ᴛᴏ ᴛᴀɢ ᴛʜᴇᴍ!"
                    )
                elif FILE_MATCHER.match(note.value):
                    message.reply_text(
                        "Tʜɪs ɴᴏᴛᴇ ᴡᴀs ᴀɴ ɪɴᴄᴏʀʀᴇᴄᴛʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ғɪʟᴇ ғʀᴏᴍ ᴀɴᴏᴛʜᴇʀ ʙᴏᴛ - I ᴄᴀɴ'ᴛ ᴜsᴇ "
                        "ɪᴛ. Iғ ʏᴏᴜ ʀᴇᴀʟʟʏ ɴᴇᴇᴅ ɪᴛ, ʏᴏᴜ'ʟʟ ʜᴀᴠᴇ ᴛᴏ sᴀᴠᴇ ɪᴛ ᴀɢᴀɪɴ. Iɴ "
                        "ᴛʜᴇ ᴍᴇᴀɴᴛɪᴍᴇ, I'ʟʟ ʀᴇᴍᴏᴠᴇ ɪᴛ ғʀᴏᴍ ʏᴏᴜʀ ɴᴏᴛᴇs ʟɪsᴛ."
                    )
                    sql.rm_note(note_chat_id, notename)
                else:
                    message.reply_text(
                        "Tʜɪs ɴᴏᴛᴇ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ sᴇɴᴛ, ᴀs ɪᴛ ɪs ɪɴᴄᴏʀʀᴇᴄᴛʟʏ ғᴏʀᴍᴀᴛᴛᴇᴅ. Asᴋ ɪɴ "
                        f"@{SUPPORT_CHAT}  Iғ ʏᴏᴜ ᴄᴀɴ'ᴛ ғɪɢᴜʀᴇ ᴏᴜᴛ ᴡʜʏ!"
                    )
                    LOGGER.exception(
                        "Cᴏᴜʟᴅ ɴᴏᴛ ᴘᴀʀsᴇ ᴍᴇssᴀɢᴇ #%s ɪɴ ᴄʜᴀᴛ %s",
                        notename,
                        str(note_chat_id),
                    )
                    LOGGER.warning("Mᴇssᴀɢᴇ ᴡᴀs: %s", str(note.value))
        return
    elif show_none:
        message.reply_text("Tʜɪs ɴᴏᴛᴇ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ")


@run_async
@connection_status
def cmd_get(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    if len(args) >= 2 and args[1].lower() == "noformat":
        get(update, context, args[0].lower(), show_none=True, no_format=True)
    elif len(args) >= 1:
        get(update, context, args[0].lower(), show_none=True)
    else:
        update.effective_message.reply_text("Get rekt")


@run_async
@connection_status
def hash_get(update: Update, context: CallbackContext):
    message = update.effective_message.text
    fst_word = message.split()[0]
    no_hash = fst_word[1:].lower()
    get(update, context, no_hash, show_none=False)


@run_async
@connection_status
def slash_get(update: Update, context: CallbackContext):
    message, chat_id = update.effective_message.text, update.effective_chat.id
    no_slash = message[1:]
    note_list = sql.get_all_chat_notes(chat_id)

    try:
        noteid = note_list[int(no_slash) - 1]
        note_name = str(noteid).strip(">").split()[1]
        get(update, context, note_name, show_none=False)
    except IndexError:
        update.effective_message.reply_text("Wʀᴏɴɢ Nᴏᴛᴇ ID 😾")


@run_async
@user_admin
@connection_status
def save(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = update.effective_message  # type: Optional[Message]

    note_name, text, data_type, content, buttons = get_note_type(msg)
    note_name = note_name.lower()
    if data_type is None:
        msg.reply_text("Dᴜᴅᴇ, ᴛʜᴇʀᴇ's ɴᴏ ɴᴏᴛᴇ")
        return

    sql.add_note_to_db(
        chat_id, note_name, text, data_type, buttons=buttons, file=content
    )

    msg.reply_text(
        f"Yᴀs ! ᴀᴅᴅᴇᴅ ɴᴏᴛᴇ `{note_name}`.\n Gᴇᴛ ɪᴛ ᴡɪᴛʜ  /get `{note_name}`,\n  or `#{note_name}`",
        parse_mode=ParseMode.MARKDOWN,
    )

    if msg.reply_to_message and msg.reply_to_message.from_user.is_bot:
        if text:
            msg.reply_text(
                "Sᴇᴇᴍs ʟɪᴋᴇ ʏᴏᴜ'ʀᴇ ᴛʀʏɪɴɢ ᴛᴏ sᴀᴠᴇ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴀ ʙᴏᴛ. Uɴғᴏʀᴛᴜɴᴀᴛᴇʟʏ, "
                "ʙᴏᴛs ᴄᴀɴ'ᴛ ғᴏʀᴡᴀʀᴅ ʙᴏᴛ ᴍᴇssᴀɢᴇs, sᴏ I ᴄᴀɴ'ᴛ sᴀᴠᴇ ᴛʜᴇ ᴇxᴀᴄᴛ ᴍᴇssᴀɢᴇ. "
                "\ɴI'ʟʟ sᴀᴠᴇ ᴀʟʟ ᴛʜᴇ ᴛᴇxᴛ I ᴄᴀɴ, ʙᴜᴛ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴍᴏʀᴇ, ʏᴏᴜ'ʟʟ ʜᴀᴠᴇ ᴛᴏ "
                "ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ʏᴏᴜʀsᴇʟғ, ᴀɴᴅ ᴛʜᴇɴ sᴀᴠᴇ ɪᴛ."
            )
        else:
            msg.reply_text(
                "Bᴏᴛs ᴀʀᴇ ᴋɪɴᴅᴀ ʜᴀɴᴅɪᴄᴀᴘᴘᴇᴅ ʙʏ ᴛᴇʟᴇɢʀᴀᴍ, ᴍᴀᴋɪɴɢ ɪᴛ ʜᴀʀᴅ ғᴏʀ ʙᴏᴛs ᴛᴏ "
                "ɪɴᴛᴇʀᴀᴄᴛ ᴡɪᴛʜ ᴏᴛʜᴇʀ ʙᴏᴛs, sᴏ I ᴄᴀɴ'ᴛ sᴀᴠᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ "
                "ʟɪᴋᴇ I ᴜsᴜᴀʟʟʏ ᴡᴏᴜʟᴅ - ᴅᴏ ʏᴏᴜ ᴍɪɴᴅ ғᴏʀᴡᴀʀᴅɪɴɢ ɪᴛ ᴀɴᴅ "
                "ᴛʜᴇɴ sᴀᴠɪɴɢ ᴛʜᴀᴛ ɴᴇᴡ ᴍᴇssᴀɢᴇ? Tʜᴀɴᴋs!"
            )
        return


@run_async
@user_admin
@connection_status
def clear(update: Update, context: CallbackContext):
    args = context.args
    chat_id = update.effective_chat.id
    if len(args) >= 1:
        notename = args[0].lower()

        if sql.rm_note(chat_id, notename):
            update.effective_message.reply_text("Sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ɴᴏᴛᴇ.")
        else:
            update.effective_message.reply_text("Tʜᴀᴛ's ɴᴏᴛ ᴀ ɴᴏᴛᴇ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ!!")


@run_async
def clearall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "Oɴʟʏ ᴛʜᴇ ᴄʜᴀᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴄʟᴇᴀʀ ᴀʟʟ ɴᴏᴛᴇs ᴀᴛ ᴏɴᴄᴇ."
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Dᴇʟᴇᴛᴇ ᴀʟʟ ɴᴏᴛᴇs", callback_data="notes_rmall"
                    )
                ],
                [InlineKeyboardButton(text="Cancel", callback_data="notes_cancel")],
            ]
        )
        update.effective_message.reply_text(
            f"Aʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ᴄʟᴇᴀʀ ALL ɴᴏᴛᴇs ɪɴ {chat.title}? Tʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


@run_async
def clearall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "notes_rmall":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            note_list = sql.get_all_chat_notes(chat.id)
            try:
                for notename in note_list:
                    note = notename.name.lower()
                    sql.rm_note(chat.id, note)
                message.edit_text("Dᴇʟᴇᴛᴇᴅ ᴀʟʟ ɴᴏᴛᴇs.")
            except BadRequest:
                return

        if member.status == "administrator":
            query.answer("Oɴʟʏ ᴏᴡɴᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ ᴄᴀɴ ᴅᴏ ᴛʜɪs.")

        if member.status == "member":
            query.answer("Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ᴛʜɪs.")
    elif query.data == "notes_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            message.edit_text("Cʟᴇᴀʀɪɴɢ ᴏғ ᴀʟʟ ɴᴏᴛᴇs ʜᴀs ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
            return
        if member.status == "administrator":
            query.answer("Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴏᴡɴᴇʀ ᴛᴏ ᴅᴏ ᴛʜɪs.")
        if member.status == "member":
            query.answer("Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ᴛʜɪs.")


@run_async
@connection_status
def list_notes(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    note_list = sql.get_all_chat_notes(chat_id)
    notes = len(note_list) + 1
    msg = "Gᴇᴛ ɴᴏᴛ ʙʏ  `/notenumber` or `#notename` \n\n  *ɪᴅ*    *ɴᴏᴛᴇ* \n"
    for note_id, note in zip(range(1, notes), note_list):
        if note_id < 10:
            note_name = f"`{note_id:2}.`  `#{(note.name.lower())}`\n"
        else:
            note_name = f"`{note_id}.`  `#{(note.name.lower())}`\n"
        if len(msg) + len(note_name) > MAX_MESSAGE_LENGTH:
            update.effective_message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            msg = ""
        msg += note_name

    if not note_list:
        try:
            update.effective_message.reply_text("Nᴏ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ!")
        except BadRequest:
            update.effective_message.reply_text("Nᴏ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ!", quote=False)

    elif len(msg) != 0:
        update.effective_message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


def __import_data__(chat_id, data):
    failures = []
    for notename, notedata in data.get("extra", {}).items():
        match = FILE_MATCHER.match(notedata)
        matchsticker = STICKER_MATCHER.match(notedata)
        matchbtn = BUTTON_MATCHER.match(notedata)
        matchfile = MYFILE_MATCHER.match(notedata)
        matchphoto = MYPHOTO_MATCHER.match(notedata)
        matchaudio = MYAUDIO_MATCHER.match(notedata)
        matchvoice = MYVOICE_MATCHER.match(notedata)
        matchvideo = MYVIDEO_MATCHER.match(notedata)
        matchvn = MYVIDEONOTE_MATCHER.match(notedata)

        if match:
            failures.append(notename)
            notedata = notedata[match.end() :].strip()
            if notedata:
                sql.add_note_to_db(chat_id, notename[1:], notedata, sql.Types.TEXT)
        elif matchsticker:
            content = notedata[matchsticker.end() :].strip()
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.STICKER, file=content
                )
        elif matchbtn:
            parse = notedata[matchbtn.end() :].strip()
            notedata = parse.split("<###button###>")[0]
            buttons = parse.split("<###button###>")[1]
            buttons = ast.literal_eval(buttons)
            if buttons:
                sql.add_note_to_db(
                    chat_id,
                    notename[1:],
                    notedata,
                    sql.Types.BUTTON_TEXT,
                    buttons=buttons,
                )
        elif matchfile:
            file = notedata[matchfile.end() :].strip()
            file = file.split("<###TYPESPLIT###>")
            notedata = file[1]
            content = file[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.DOCUMENT, file=content
                )
        elif matchphoto:
            photo = notedata[matchphoto.end() :].strip()
            photo = photo.split("<###TYPESPLIT###>")
            notedata = photo[1]
            content = photo[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.PHOTO, file=content
                )
        elif matchaudio:
            audio = notedata[matchaudio.end() :].strip()
            audio = audio.split("<###TYPESPLIT###>")
            notedata = audio[1]
            content = audio[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.AUDIO, file=content
                )
        elif matchvoice:
            voice = notedata[matchvoice.end() :].strip()
            voice = voice.split("<###TYPESPLIT###>")
            notedata = voice[1]
            content = voice[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.VOICE, file=content
                )
        elif matchvideo:
            video = notedata[matchvideo.end() :].strip()
            video = video.split("<###TYPESPLIT###>")
            notedata = video[1]
            content = video[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.VIDEO, file=content
                )
        elif matchvn:
            video_note = notedata[matchvn.end() :].strip()
            video_note = video_note.split("<###TYPESPLIT###>")
            notedata = video_note[1]
            content = video_note[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.VIDEO_NOTE, file=content
                )
        else:
            sql.add_note_to_db(chat_id, notename[1:], notedata, sql.Types.TEXT)

    if failures:
        with BytesIO(str.encode("\n".join(failures))) as output:
            output.name = "failed_imports.txt"
            dispatcher.bot.send_document(
                chat_id,
                document=output,
                filename="failed_imports.txt",
                caption="Tʜᴇsᴇ ғɪʟᴇs/ᴘʜᴏᴛᴏs ғᴀɪʟᴇᴅ ᴛᴏ ɪᴍᴘᴏʀᴛ ᴅᴜᴇ ᴛᴏ ᴏʀɪɢɪɴᴀᴛɪɴɢ "
                "ғʀᴏᴍ ᴀɴᴏᴛʜᴇʀ ʙᴏᴛ. Tʜɪs ɪs ᴀ ᴛᴇʟᴇɢʀᴀᴍ API ʀᴇsᴛʀɪᴄᴛɪᴏɴ, ᴀɴᴅ ᴄᴀɴ'ᴛ "
                "ʙᴇ ᴀᴠᴏɪᴅᴇᴅ. Sᴏʀʀʏ ғᴏʀ ᴛʜᴇ ɪɴᴄᴏɴᴠᴇɴɪᴇɴᴄᴇ!",
            )


def __stats__():
    return f"• {sql.num_notes()} ɴᴏᴛᴇs , ᴀᴄʀᴏss {sql.num_chats()} ᴄʜᴀᴛs."


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    notes = sql.get_all_chat_notes(chat_id)
    return f"Tʜᴇʀᴇ ᴀʀᴇ  `{len(notes)}` ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ ."


__help__ = """
 ❍ /get <ɴᴏᴛᴇɴᴀᴍᴇ>*:* ɢᴇᴛ ᴛʜᴇ ɴᴏᴛᴇ ᴡɪᴛʜ ᴛʜɪs ɴᴏᴛᴇɴᴀᴍᴇ
 ❍ #<ɴᴏᴛᴇɴᴀᴍᴇ>*:* sᴀᴍᴇ ᴀs /ɢᴇᴛ
 ❍ /notes ᴏʀ /saved *:* ʟɪsᴛ ᴀʟʟ sᴀᴠᴇᴅ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ
 ❍ /number *:* Wɪʟʟ ᴘᴜʟʟ ᴛʜᴇ ɴᴏᴛᴇ ᴏғ ᴛʜᴀᴛ ɴᴜᴍʙᴇʀ ɪɴ ᴛʜᴇ ʟɪsᴛ
Iғ ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛs ᴏғ ᴀ ɴᴏᴛᴇ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ғᴏʀᴍᴀᴛᴛɪɴɢ, ᴜsᴇ `/ɢᴇᴛ <ɴᴏᴛᴇɴᴀᴍᴇ> ɴᴏғᴏʀᴍᴀᴛ`. Tʜɪs ᴄᴀɴ \
ʙᴇ ᴜsᴇғᴜʟ ᴡʜᴇɴ ᴜᴘᴅᴀᴛɪɴɢ ᴀ ᴄᴜʀʀᴇɴᴛ ɴᴏᴛᴇ

*Aᴅᴍɪɴs ᴏɴʟʏ:*
 ❍ /save <ɴᴏᴛᴇɴᴀᴍᴇ> <ɴᴏᴛᴇᴅᴀᴛᴀ>*:* sᴀᴠᴇs ɴᴏᴛᴇᴅᴀᴛᴀ ᴀs ᴀ ɴᴏᴛᴇ ᴡɪᴛʜ ɴᴀᴍᴇ ɴᴏᴛᴇɴᴀᴍᴇ
A ʙᴜᴛᴛᴏɴ ᴄᴀɴ ʙᴇ ᴀᴅᴅᴇᴅ ᴛᴏ ᴀ ɴᴏᴛᴇ ʙʏ ᴜsɪɴɢ sᴛᴀɴᴅᴀʀᴅ ᴍᴀʀᴋᴅᴏᴡɴ ʟɪɴᴋ sʏɴᴛᴀx - ᴛʜᴇ ʟɪɴᴋ sʜᴏᴜʟᴅ ᴊᴜsᴛ ʙᴇ ᴘʀᴇᴘᴇɴᴅᴇᴅ ᴡɪᴛʜ ᴀ \
`ʙᴜᴛᴛᴏɴᴜʀʟ:` sᴇᴄᴛɪᴏɴ, ᴀs sᴜᴄʜ: `[sᴏᴍᴇʟɪɴᴋ](ʙᴜᴛᴛᴏɴᴜʀʟ:ᴇxᴀᴍᴘʟᴇ.ᴄᴏᴍ)`. Cʜᴇᴄᴋ `/markdownhelp ` ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏ
 ❍ /save  <ɴᴏᴛᴇɴᴀᴍᴇ>*:* sᴀᴠᴇ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ᴀs ᴀ ɴᴏᴛᴇ ᴡɪᴛʜ ɴᴀᴍᴇ ɴᴏᴛᴇɴᴀᴍᴇ
 Sᴇᴘᴀʀᴀᴛᴇ ᴅɪғғ ʀᴇᴘʟɪᴇs ʙʏ `%%%` ᴛᴏ ɢᴇᴛ ʀᴀɴᴅᴏᴍ ɴᴏᴛᴇs
 *Exᴀᴍᴘʟᴇ:* 
 `/save  ɴᴏᴛᴇɴᴀᴍᴇ
 Rᴇᴘʟʏ 1
 %%%
 Rᴇᴘʟʏ 2
 %%%
 Rᴇᴘʟʏ 3`
 ❍ /ᴄʟᴇᴀʀ <ɴᴏᴛᴇɴᴀᴍᴇ>*:* ᴄʟᴇᴀʀ ɴᴏᴛᴇ ᴡɪᴛʜ ᴛʜɪs ɴᴀᴍᴇ
 ❍ /ʀᴇᴍᴏᴠᴇᴀʟʟɴᴏᴛᴇs*:* ʀᴇᴍᴏᴠᴇs ᴀʟʟ ɴᴏᴛᴇs ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ
 *Nᴏᴛᴇ:* Nᴏᴛᴇ ɴᴀᴍᴇs ᴀʀᴇ ᴄᴀsᴇ-ɪɴsᴇɴsɪᴛɪᴠᴇ, ᴀɴᴅ ᴛʜᴇʏ ᴀʀᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴄᴏɴᴠᴇʀᴛᴇᴅ ᴛᴏ ʟᴏᴡᴇʀᴄᴀsᴇ ʙᴇғᴏʀᴇ ɢᴇᴛᴛɪɴɢ sᴀᴠᴇᴅ

"""

__mod_name__ = "Nᴏᴛᴇs"

GET_HANDLER = CommandHandler("get", cmd_get)
HASH_GET_HANDLER = MessageHandler(Filters.regex(r"^#[^\s]+"), hash_get)
SLASH_GET_HANDLER = MessageHandler(Filters.regex(r"^/\d+$"), slash_get)
SAVE_HANDLER = CommandHandler("save", save)
DELETE_HANDLER = CommandHandler("clear", clear)

LIST_HANDLER = DisableAbleCommandHandler(["notes", "saved"], list_notes, admin_ok=True)

CLEARALL = DisableAbleCommandHandler("removeallnotes", clearall)
CLEARALL_BTN = CallbackQueryHandler(clearall_btn, pattern=r"notes_.*")

dispatcher.add_handler(GET_HANDLER)
dispatcher.add_handler(SAVE_HANDLER)
dispatcher.add_handler(LIST_HANDLER)
dispatcher.add_handler(DELETE_HANDLER)
dispatcher.add_handler(HASH_GET_HANDLER)
dispatcher.add_handler(SLASH_GET_HANDLER)
dispatcher.add_handler(CLEARALL)
dispatcher.add_handler(CLEARALL_BTN)
