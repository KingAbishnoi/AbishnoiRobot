from AbishnoiRobot.modules.sql_extended.night_mode_sql import (
    add_nightmode,
    rmnightmode,
    get_all_chat_id,
    is_nightmode_indb,
)
from telethon.tl.types import ChatBannedRights
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import functions
from telethon import types
from AbishnoiRobot.events import register
from AbishnoiRobot import telethn as tbot
import os


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    elif isinstance(chat, types.InputPeerChat):

        ui = await tbot.get_peer_id(user)
        ps = (
            await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    else:
        return None


hehes = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)
openhehe = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    send_polls=False,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)


@register(pattern="^/night")
async def close_ws(event):
    if event.is_group:
        if not (await is_register_admin(event.input_chat, event.message.sender_id)):
            await event.reply(
                "🤦🏻‍♂️Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ 🤦.."
            )
            return

    if not event.is_group:
        await event.reply("Yᴏᴜ Cᴀɴ Oɴʟʏ Eɴᴀʙʟᴇ Nɪɢʜᴛ Mᴏᴅᴇ ɪɴ Gʀᴏᴜᴘs.")
        return
    if is_nightmode_indb(str(event.chat_id)):
        await event.reply("Tʜɪs Cʜᴀᴛ ɪs Hᴀs Aʟʀᴇᴀᴅʏ Eɴᴀʙʟᴇᴅ Nɪɢʜᴛ Mᴏᴅᴇ.")
        return
    add_nightmode(str(event.chat_id))
    await event.reply(
        f"Aᴅᴅᴇᴅ ᴄʜᴀᴛ {event.chat.title} ᴡɪᴛʜ ɪᴅ  {event.chat_id} ᴛᴏ ᴅᴀᴛᴀʙᴀs . **Tʜɪs Gʀᴏᴜᴘ Wɪʟʟ Bᴇ Cʟᴏsᴇᴅ Oɴ 12Aᴍ(IST) Aɴᴅ Wɪʟʟ Oᴘᴇɴᴇᴅ Oɴ 06Aᴍ(IST)**"
    )


@register(pattern="^/rmnight")
async def disable_ws(event):
    if event.is_group:
        if not (await is_register_admin(event.input_chat, event.message.sender_id)):
            await event.reply(
                "🤦🏻‍♂️Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ...🤦 "
            )
            return

    if not event.is_group:
        await event.reply("Yᴏᴜ Cᴀɴ Oɴʟʏ Dɪsᴀʙʟᴇ Nɪɢʜᴛ Mᴏᴅᴇ ɪɴ Gʀᴏᴜᴘs.")
        return
    if not is_nightmode_indb(str(event.chat_id)):
        await event.reply("This Chat is Has Not Enabled Night Mode.")
        return
    rmnightmode(str(event.chat_id))
    await event.reply(
        f"Rᴇᴍᴏᴠᴇᴅ Chat {event.chat.title} Wɪᴛʜ ɪᴅ  {event.chat_id} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ ."
    )


async def job_close():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                "12:00 Aᴍ, Gʀᴏᴜᴘ Is Cʟᴏsɪɴɢ Tɪʟʟ 6 Aᴍ. Nɪɢʜᴛ Mᴏᴅᴇ Sᴛᴀʀᴛᴇᴅ ! \n**ᴘᴏᴠᴇʀᴅ ʙʏ ➪ ᴀʙɢ ʀᴏʙᴏᴛ**",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=hehes
                )
            )
        except Exception as e:
            logger.info(f"Uɴᴀʙʟᴇ Tᴏ Cʟᴏsᴇ Gʀᴏᴜᴘ {warner} - {e}")


# Run everyday at 12am
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_close, trigger="cron", hour=23, minute=59)
scheduler.start()


async def job_open():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                "ɴᴏᴡ ᴀʟʟᴏᴡᴇᴅ ᴄʜᴀᴛ\n** Pᴏᴡᴇʀᴇᴅ Bʏ「 ᴀʙɢ 𒆜 ʀᴏʙᴏᴛ **",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=openhehe
                )
            )
        except Exception as e:
            logger.info(f"Uɴᴀʙʟᴇ Tᴏ Oᴘᴇɴ Gʀᴏᴜᴘ {warner.chat_id} - {e}")


# Run everyday at 06
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_open, trigger="cron", hour=5, minute=59)
scheduler.start()


__mod_name__ = "Nɪɢʜᴛ​"
