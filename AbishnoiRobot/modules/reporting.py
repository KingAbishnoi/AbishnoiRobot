import html

from AbishnoiRobot import LOGGER, DRAGONS, TIGERS, WOLVES, dispatcher
from AbishnoiRobot.modules.helper_funcs.chat_status import user_admin, user_not_admin
from AbishnoiRobot.modules.log_channel import loggable
from AbishnoiRobot.modules.sql import reporting_sql as sql
from telegram import Chat, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import mention_html

REPORT_GROUP = 12
REPORT_IMMUNE_USERS = DRAGONS + TIGERS + WOLVES


@run_async
@user_admin
def report_setting(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    msg = update.effective_message

    if chat.type == chat.PRIVATE:
        if len(args) >= 1:
            if args[0] in ("yes", "on"):
                sql.set_user_setting(chat.id, True)
                msg.reply_text(
                    "Tᴜʀɴᴇᴅ ᴏɴ ʀᴇᴘᴏʀᴛɪɴɢ! Yᴏᴜ'ʟʟ ʙᴇ ɴᴏᴛɪғɪᴇᴅ ᴡʜᴇɴᴇᴠᴇʀ ᴀɴʏᴏɴᴇ ʀᴇᴘᴏʀᴛs sᴏᴍᴇᴛʜɪɴɢ."
                )

            elif args[0] in ("no", "off"):
                sql.set_user_setting(chat.id, False)
                msg.reply_text("Tᴜʀɴᴇᴅ ᴏғғ ʀᴇᴘᴏʀᴛɪɴɢ! Yᴏᴜ ᴡᴏɴᴛ ɢᴇᴛ ᴀɴʏ ʀᴇᴘᴏʀᴛs.")
        else:
            msg.reply_text(
                f"Yᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ʀᴇᴘᴏʀᴛ ᴘʀᴇғᴇʀᴇɴᴄᴇ ɪs: `{sql.user_should_report(chat.id)}`",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if len(args) >= 1:
            if args[0] in ("yes", "on"):
                sql.set_chat_setting(chat.id, True)
                msg.reply_text(
                    "Tᴜʀɴᴇᴅ ᴏɴ ʀᴇᴘᴏʀᴛɪɴɢ! Aᴅᴍɪɴs ᴡʜᴏ ʜᴀᴠᴇ ᴛᴜʀɴᴇᴅ ᴏɴ ʀᴇᴘᴏʀᴛs ᴡɪʟʟ ʙᴇ ɴᴏᴛɪғɪᴇᴅ ᴡʜᴇɴ /report  "
                    "ᴏʀ @admin ɪs ᴄᴀʟʟᴇᴅ."
                )

            elif args[0] in ("no", "off"):
                sql.set_chat_setting(chat.id, False)
                msg.reply_text(
                    "Tᴜʀɴᴇᴅ ᴏғғ ʀᴇᴘᴏʀᴛɪɴɢ! Nᴏ ᴀᴅᴍɪɴs ᴡɪʟʟ ʙᴇ ɴᴏᴛɪғɪᴇᴅ ᴏɴ /report ᴏʀ @admin ."
                )
        else:
            msg.reply_text(
                f"Tʜɪs ɢʀᴏᴜᴘ's ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢ ɪs: `{sql.chat_should_report(chat.id)}`",
                parse_mode=ParseMode.MARKDOWN,
            )


@run_async
@user_not_admin
@loggable
def report(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if chat and message.reply_to_message and sql.chat_should_report(chat.id):
        reported_user = message.reply_to_message.from_user
        chat_name = chat.title or chat.first or chat.username
        admin_list = chat.get_administrators()
        message = update.effective_message

        if not args:
            message.reply_text("Aᴅᴅ ᴀ ʀᴇᴀsᴏɴ ғᴏʀ ʀᴇᴘᴏʀᴛɪɴɢ ғɪʀsᴛ.")
            return ""

        if user.id == reported_user.id:
            message.reply_text("Uʜ ʏᴇᴀʜ, Sᴜʀᴇ sᴜʀᴇ...ᴍᴀsᴏ ᴍᴜᴄʜ?")
            return ""

        if user.id == bot.id:
            message.reply_text("Nɪᴄᴇ ᴛʀʏ.")
            return ""

        if reported_user.id in REPORT_IMMUNE_USERS:
            message.reply_text("Uʜ? Yᴏᴜ ʀᴇᴘᴏʀᴛɪɴɢ ᴀ ᴅɪsᴀsᴛᴇʀ?")
            return ""

        if chat.username and chat.type == Chat.SUPERGROUP:

            reported = f"{mention_html(user.id, user.first_name)} ʀᴇᴘᴏʀᴛᴇᴅ  {mention_html(reported_user.id, reported_user.first_name)} ᴛᴏ ᴀᴅᴍɪɴs !"

            msg = (
                f"<b>⚠️Rᴇᴘᴏʀᴛ : </b>{html.escape(chat.title)}\n"
                f"<b> • Rᴇᴘᴏʀᴛ ʙʏ :</b> {mention_html(user.id, user.first_name)}(<code>{user.id}</code>)\n"
                f"<b> • Rᴇᴘᴏʀᴛᴇᴅ ᴜsᴇʀ :</b> {mention_html(reported_user.id, reported_user.first_name)} (<code>{reported_user.id}</code>)\n"
            )
            link = f'<b> • Rᴇᴘᴏʀᴛᴇᴅ ᴍᴇssᴀɢᴇ:</b> <a href="https://t.me/{chat.username}/{message.reply_to_message.message_id}">click here</a>'
            should_forward = False
            keyboard = [
                [
                    InlineKeyboardButton(
                        "➡ Message",
                        url=f"https://t.me/{chat.username}/{message.reply_to_message.message_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "• ᴋɪᴄᴋ •",
                        callback_data=f"report_{chat.id}=kick={reported_user.id}={reported_user.first_name}",
                    ),
                    InlineKeyboardButton(
                        "• ʙᴀɴ •",
                        callback_data=f"report_{chat.id}=banned={reported_user.id}={reported_user.first_name}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "• ᴅᴇʟ. ᴍᴇssᴀɢᴇ •",
                        callback_data=f"report_{chat.id}=delete={reported_user.id}={message.reply_to_message.message_id}",
                    )
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reported = (
                f"{mention_html(user.id, user.first_name)} ʀᴇᴘᴏʀᴛᴇᴅ  "
                f"{mention_html(reported_user.id, reported_user.first_name)} ᴛᴏ ᴛʜᴇ ᴀᴅᴍɪɴs!"
            )

            msg = f'{mention_html(user.id, user.first_name)} ɪs ᴄᴀʟʟɪɴɢ ғᴏʀ ᴀᴅᴍɪɴs "{html.escape(chat_name)}"!'
            link = ""
            should_forward = True

        for admin in admin_list:
            if admin.user.is_bot:  # can't message bots
                continue

            if sql.user_should_report(admin.user.id):
                try:
                    if not chat.type == Chat.SUPERGROUP:
                        bot.send_message(
                            admin.user.id, msg + link, parse_mode=ParseMode.HTML
                        )

                        if should_forward:
                            message.reply_to_message.forward(admin.user.id)

                            if (
                                len(message.text.split()) > 1
                            ):  # If user is giving a reason, send his message too
                                message.forward(admin.user.id)
                    if not chat.username:
                        bot.send_message(
                            admin.user.id, msg + link, parse_mode=ParseMode.HTML
                        )

                        if should_forward:
                            message.reply_to_message.forward(admin.user.id)

                            if (
                                len(message.text.split()) > 1
                            ):  # If user is giving a reason, send his message too
                                message.forward(admin.user.id)

                    if chat.username and chat.type == Chat.SUPERGROUP:
                        bot.send_message(
                            admin.user.id,
                            msg + link,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup,
                        )

                        if should_forward:
                            message.reply_to_message.forward(admin.user.id)

                            if (
                                len(message.text.split()) > 1
                            ):  # If user is giving a reason, send his message too
                                message.forward(admin.user.id)

                except Unauthorized:
                    pass
                except BadRequest as excp:  # TODO: cleanup exceptions
                    LOGGER.exception("Exᴄᴇᴘᴛɪᴏɴ ᴡʜɪʟᴇ ʀᴇᴘᴏʀᴛɪɴɢ ᴜsᴇʀ")

        message.reply_to_message.reply_text(
            f"{mention_html(user.id, user.first_name)} ʀᴇᴘᴏʀᴛᴇᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴛʜᴇ ᴀᴅᴍɪɴs.",
            parse_mode=ParseMode.HTML,
        )
        return msg

    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, _):
    return f"Tʜɪs ᴄʜᴀᴛ ɪs sᴇᴛᴜᴘ ᴛᴏ sᴇɴᴅ ᴜsᴇʀ ʀᴇᴘᴏʀᴛs ᴛᴏ ᴀᴅᴍɪɴs, ᴠɪᴀ /report and @admin: `{sql.chat_should_report(chat_id)}`"


def __user_settings__(user_id):
    if sql.user_should_report(user_id) is True:
        text = "Yᴏᴜ ᴡɪʟʟ ʀᴇᴄᴇɪᴠᴇ ʀᴇᴘᴏʀᴛs ғʀᴏᴍ ᴄʜᴀᴛs ʏᴏᴜ'ʀᴇ ᴀᴅᴍɪɴ."
    else:
        text = "Yᴏᴜ ᴡɪʟʟ *ɴᴏᴛ* ʀᴇᴄᴇɪᴠᴇ ʀᴇᴘᴏʀᴛs ғʀᴏᴍ ᴄʜᴀᴛs ʏᴏᴜ'ʀᴇ ᴀᴅᴍɪɴ."
    return text


def buttons(update: Update, context: CallbackContext):
    bot = context.bot
    query = update.callback_query
    splitter = query.data.replace("report_", "").split("=")
    if splitter[1] == "kick":
        try:
            bot.kickChatMember(splitter[0], splitter[2])
            bot.unbanChatMember(splitter[0], splitter[2])
            query.answer("Sᴜᴄᴄᴇsғᴜʟʟʏ ᴋɪᴄᴋᴇᴅ")
            return ""
        except Exception as err:
            query.answer(" Fᴀɪʟᴇᴅ ᴛᴏ Pᴜɴᴄʜ")
            bot.sendMessage(
                text=f"Error: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
    elif splitter[1] == "banned":
        try:
            bot.kickChatMember(splitter[0], splitter[2])
            query.answer("Sᴜᴄᴄᴇsғᴜʟʟʏ Bᴀɴɴᴇᴅ")
            return ""
        except Exception as err:
            bot.sendMessage(
                text=f"Error: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
            query.answer("Fᴀɪʟᴇᴅ ᴛᴏ Bᴀɴ")
    elif splitter[1] == "delete":
        try:
            bot.deleteMessage(splitter[0], splitter[3])
            query.answer("Mᴇssᴀɢᴇ Dᴇʟᴇᴛᴇᴅ")
            return ""
        except Exception as err:
            bot.sendMessage(
                text=f"Error: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
            query.answer("Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇ!")


__help__ = """
❍ /report   <ʀᴇᴀsᴏɴ>*:* ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴛᴏ ᴀᴅᴍɪɴs.
 ❍ @admin *:* ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴛᴏ ᴀᴅᴍɪɴs.
*NOTE:* Nᴇɪᴛʜᴇʀ ᴏғ ᴛʜᴇsᴇ ᴡɪʟʟ ɢᴇᴛ ᴛʀɪɢɢᴇʀᴇᴅ ɪғ ᴜsᴇᴅ ʙʏ ᴀᴅᴍɪɴs.

*Aᴅᴍɪɴs ᴏɴʟʏ:*
 ❍ /reports <ᴏɴ/ᴏғғ>*:* ᴄʜᴀɴɢᴇ ʀᴇᴘᴏʀᴛ sᴇᴛᴛɪɴɢ, ᴏʀ ᴠɪᴇᴡ ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs.
   • Iғ ᴅᴏɴᴇ ɪɴ ᴘᴍ, ᴛᴏɢɢʟᴇs ʏᴏᴜʀ sᴛᴀᴛᴜs.
   • Iғ ɪɴ ɢʀᴏᴜᴘ, ᴛᴏɢɢʟᴇs ᴛʜᴀᴛ ɢʀᴏᴜᴘs's sᴛᴀᴛᴜs.
"""

SETTING_HANDLER = CommandHandler("reports", report_setting)
REPORT_HANDLER = CommandHandler("report", report, filters=Filters.group)
ADMIN_REPORT_HANDLER = MessageHandler(Filters.regex(r"(?i)@admin(s)?"), report)

REPORT_BUTTON_USER_HANDLER = CallbackQueryHandler(buttons, pattern=r"report_")
dispatcher.add_handler(REPORT_BUTTON_USER_HANDLER)

dispatcher.add_handler(SETTING_HANDLER)
dispatcher.add_handler(REPORT_HANDLER, REPORT_GROUP)
dispatcher.add_handler(ADMIN_REPORT_HANDLER, REPORT_GROUP)

__mod_name__ = "Rᴇᴘᴏʀᴛs​"
__handlers__ = [
    (REPORT_HANDLER, REPORT_GROUP),
    (ADMIN_REPORT_HANDLER, REPORT_GROUP),
    (SETTING_HANDLER),
]
