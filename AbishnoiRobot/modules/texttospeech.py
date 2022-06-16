import os

from gtts import gTTS
from gtts import gTTSError
from telethon import *
from telethon.tl import functions
from telethon.tl import types
from telethon.tl.types import *

from AbishnoiRobot import *
from AbishnoiRobot import telethn as tbot
from AbishnoiRobot.events import register


@register(pattern="^/tts (.*)")
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await event.reply(
            "Invalid Syntax\nFormat `/tts lang | text`\nFor eg: `/tts en | hello`"
        )
        return
    text = text.strip()
    lan = lan.strip()
    try:
        tts = gTTS(text, tld="com", lang=lan)
        tts.save("k.mp3")
    except AssertionError:
        await event.reply(
            "The text is empty.\n"
            "Nothing left to speak after pre-precessing, "
            "tokenizing and cleaning."
        )
        return
    except ValueError:
        await event.reply("Language is not supported.")
        return
    except RuntimeError:
        await event.reply("Error loading the languages dictionary.")
        return
    except gTTSError:
        await event.reply("Error in Google Text-to-Speech API request !")
        return
    with open("k.mp3", "r"):
        await tbot.send_file(
            event.chat_id, "k.mp3", voice_note=True, reply_to=reply_to_id
        )
        os.remove("k.mp3")


__help__ = """ 
ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs ꜰᴏʀ ᴛᴇxᴛ ᴛᴏ sᴘᴇᴇᴄʜ :

𝙵𝚘𝚛𝚖𝚊𝚝 /tts 𝚕𝚊𝚗𝚐𝚞𝚊𝚐𝚎 | 𝚝𝚎𝚡𝚝
𝙴𝚡𝚊𝚖𝚙𝚕𝚎 : /tts  𝚎𝚗 | 𝚑𝚎𝚕𝚕𝚘
"""

__mod_name__ = "ᴛᴇxᴛ ᴛᴏ sᴘᴇᴇᴄʜ"
