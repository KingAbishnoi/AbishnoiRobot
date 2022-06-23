from platform import python_version as y
from telegram import __version__ as o
from pyrogram import __version__ as z
from telethon import __version__ as s
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
from AbishnoiRobot import pbot as client


ANON = "https://telegra.ph/file/77bb85443f0a5f099c875.jpg"


@client.on_message(filters.command(["repo", "source"]))
async def repo(client, message):
    await message.reply_photo(
        photo=ANON,
        caption=f"""**ʜᴇʏ​ {message.from_user.mention()},\n\nɪ ᴀᴍ [「 ᴀʙɢ 𒆜 ʀᴏʙᴏᴛ 」](t.me/Abishnoi_ro_bot)**

**» ᴍʏ ᴅᴇᴠᴇʟᴏᴘᴇʀ​ :** [𝐀𝐁𝐈𝐒𝐇𝐍𝐎𝐈](tg://user?id=1452219013)
**» ᴩʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ :** `{y()}`
**» ʟɪʙʀᴀʀʏ ᴠᴇʀsɪᴏɴ :** `{o}` 
**» ᴛᴇʟᴇᴛʜᴏɴ ᴠᴇʀsɪᴏɴ :** `{s}` 
**» ᴘʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ :** `{z}`

**「 ᴀʙɢ 𒆜 ʀᴏʙᴏᴛ ᴏʀ ᴍᴜsɪ 」 sᴏᴜʀᴄᴇ ɪs ɴᴏᴡ ᴩᴜʙʟɪᴄ ᴀɴᴅ ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴍᴀᴋᴇ ʏᴏᴜʀ ᴏᴡɴ ʙᴏᴛ.**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/Abishnoi1M"),
                    InlineKeyboardButton(
                        "ʀᴏʙᴏᴛ", url="https://github.com/KingAbishnoi/AbishnoiRobot"
                    ),
                    InlineKeyboardButton(
                        "ᴍᴜsɪᴄ",
                        url="https://github.com/KingAbishnoi/AbishnoiXMusic",
                    ),
                ]
            ]
        ),
    )


__mod_name__ = "Rᴇᴩᴏ"
