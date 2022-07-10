# Dear Pro  , Don't Remove This Link
# . Tg @Abishnoi1M
# All Bots @Abishnoi_bots
# Github :- KingAbishnoi


import asyncio
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)


from AbishnoiRobot import pbot as bot

ABISHNOI = "https://telegra.ph/file/348fd99cf32b44153f5c1.jpg"


@bot.on_message(filters.command(["noob", "owner"]))
async def repo(client, message):
    await message.reply_photo(
        photo=ABISHNOI,
        caption=f"""**ʜᴇʏ {message.from_user.mention()},\n\nɪ ᴀᴍ [「 ᴀʙɢ 𒆜 ʀᴏʙᴏᴛ 」](t.me/Abishnoi_ro_bot)**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("• ᴏᴡɴᴇʀ •", url="https://t.me/Abishnoi1M"),
                ]
            ]
        ),
    )


__mod_name__ = "Oᴡɴᴇʀ"
