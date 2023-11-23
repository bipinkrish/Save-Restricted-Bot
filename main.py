import datetime
import pyrogram
from pyrogram import Client, filters, __version__
from pyrogram.raw.all import layer
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import web_server
from aiohttp import web
import time
import os
import logging
import logging.config
import threading
from config import Config
from pytz import timezone


logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

class Bot (Client):

    def __init__(self):
        super().__init__(
            name="SnowEncoderBot",
            in_memory=True,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins={'root': 'plugins'}
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, Config.PORT).start()
        logging.info(f"✅ {me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}. ✅")

        try:
            await self.send_message(Config.ADMIN, f"**__{me.first_name}  Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**")
        except:
            pass

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped ⛔")


if Config.STRING_SESSION is not None:
    acc = Client("myacc", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION)
    acc.start()
else:
    acc = None

# download status


def downstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            Client.edit_message_text(
                message.chat.id, message.id, f"__Downloaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)


# upload status
def upstatus(statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            Client.edit_message_text(
                message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)


# progress writter
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


# start command
@Client.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    Client.send_message(message.chat.id, f"__👋 Hi **{message.from_user.mention}**, I am Save Restricted Bot, I can send you restricted content by it's post link__\n\n{USAGE}",
                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Source Code", url="https://github.com/Snowball-0/Save-Restricted-Bot")]]), reply_to_message_id=message.id)


@Client.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    print(message.text)

    # joining chats
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:

        if acc is None:
            Client.send_message(
                message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
            return

        try:
            try:
                acc.join_chat(message.text)
            except Exception as e:
                Client.send_message(
                    message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)
                return
            Client.send_message(message.chat.id, "**Chat Joined**",
                             reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            Client.send_message(
                message.chat.id, "**Chat alredy Joined**", reply_to_message_id=message.id)
        except InviteHashExpired:
            Client.send_message(message.chat.id, "**Invalid Link**",
                             reply_to_message_id=message.id)

    # getting message
    elif "https://t.me/" in message.text:

        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        for msgid in range(fromID, toID+1):

            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])

                # if acc is None:
                # 	Client.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
                # 	return

                # handle_private(message,chatid,msgid)

                try:
                    handle_private(message, chatid, msgid)
                except Exception as e:
                    Client.send_message(
                        message.chat.id, f"{msgid} This Messge id is either Deleted or Empty Doesn't contain any files", reply_to_message_id=message.id)
                continue

            # Client
            elif "https://t.me/b/" in message.text:
                username = datas[4]

                if acc is None:
                    Client.send_message(
                        message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                    return
                try:
                    handle_private(message, username, msgid)
                except Exception as e:
                    Client.send_message(
                        message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

            # public
            else:
                username = datas[3]

                try:
                    msg = Client.get_messages(username, msgid)
                except UsernameNotOccupied:
                    Client.send_message(
                        message.chat.id, f"**The username is not occupied by anyone**", reply_to_message_id=message.id)
                    return

                try:
                    Client.copy_message(message.chat.id, msg.chat.id,
                                     msg.id, reply_to_message_id=message.id)
                except:
                    if acc is None:
                        Client.send_message(
                            message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                        return
                    try:
                        handle_private(message, username, msgid)
                    except Exception as e:
                        Client.send_message(
                            message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

            # wait time
            time.sleep(3)


# handle private
def handle_private(message: pyrogram.types.messages_and_media.message.Message, chatid: int, msgid: int):
    msg: pyrogram.types.messages_and_media.message.Message = acc.get_messages(
        chatid, msgid)
    msg_type = get_message_type(msg)

    if "Text" == msg_type:
        Client.send_message(message.chat.id, msg.text,
                         entities=msg.entities, reply_to_message_id=message.id)
        return

    smsg = Client.send_message(
        message.chat.id, '__Downloading__', reply_to_message_id=message.id)
    dosta = threading.Thread(target=lambda: downstatus(
        f'{message.id}downstatus.txt', smsg), daemon=True)
    dosta.start()
    file = acc.download_media(msg, progress=progress,
                              progress_args=[message, "down"])
    os.remove(f'{message.id}downstatus.txt')

    upsta = threading.Thread(target=lambda: upstatus(
        f'{message.id}upstatus.txt', smsg), daemon=True)
    upsta.start()

    if "Document" == msg_type:
        try:
            thumb = acc.download_media(msg.document.thumbs[0].file_id)
        except:
            thumb = None

        Client.send_document(message.chat.id, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities,
                          reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        if thumb != None:
            os.remove(thumb)

    elif "Video" == msg_type:
        try:
            thumb = acc.download_media(msg.video.thumbs[0].file_id)
        except:
            thumb = None

        Client.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb,
                       caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        if thumb != None:
            os.remove(thumb)

    elif "Animation" == msg_type:
        Client.send_animation(message.chat.id, file,
                           reply_to_message_id=message.id)

    elif "Sticker" == msg_type:
        Client.send_sticker(message.chat.id, file, reply_to_message_id=message.id)

    elif "Voice" == msg_type:
        Client.send_voice(message.chat.id, file, caption=msg.caption, thumb=thumb, caption_entities=msg.caption_entities,
                       reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

    elif "Audio" == msg_type:
        try:
            thumb = acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            thumb = None

        Client.send_audio(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities,
                       reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
        if thumb != None:
            os.remove(thumb)

    elif "Photo" == msg_type:
        Client.send_photo(message.chat.id, file, caption=msg.caption,
                       caption_entities=msg.caption_entities, reply_to_message_id=message.id)

    os.remove(file)
    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
    Client.delete_messages(message.chat.id, [smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass


USAGE = """**FOR PUBLIC CHATS**

__just send post/s link__

**FOR PRIVATE CHATS**

__first send invite link of the chat (unnecessary if the account of string session already member of the chat)
then send post/s link__

**FOR BOT CHATS**

__send link with '/b/', Client's username and message id, you might want to install some unofficial client to get the id like below__

```
https://t.me/b/botusername/4321
```

**MULTI POSTS**

__send public/private posts link as explained above with formate "from - to" to send multiple messages like below__

```
https://t.me/xxxx/1001-1010

https://t.me/c/xxxx/101 - 120
```

__note that space in between doesn't matter__
"""


# infinty polling
bot = Bot()
bot.run()
