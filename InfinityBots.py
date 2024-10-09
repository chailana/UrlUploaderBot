#    Copyright (c) 2021 Infinity BOTs <https://t.me/Infinity_BOTs>

#    This program is free software: you can redistribute it and/or modify  
#    it under the terms of the GNU General Public License as published by  
#    the Free Software Foundation, version 3.
# 
#    This program is distributed in the hope that it will be useful, but 
#    WITHOUT ANY WARRANTY; without even the implied warranty of 
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
#    General Public License for more details.

import os
import yt_dlp
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config

# login to pyrogram client
JEBotZ = Client(
   "URL Uploader",
   api_id=Config.APP_ID,
   api_hash=Config.API_HASH,
   bot_token=Config.TG_BOT_TOKEN,
)

# start message
@JEBotZ.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Hello There, I'm **Url Uploader Bot** 😉\n\nJust send me a url. Do /help for more details 🧐",
                        reply_markup=InlineKeyboardMarkup(
                                [[
                                        InlineKeyboardButton(
                                            "Source", url="https://github.com/ImJanindu/UrlUploaderBot"),
                                        InlineKeyboardButton(
                                            "Dev", url="https://t.me/Infinity_BOTs")
                                    ]]
                            ),)

# help message
@JEBotZ.on_edited_message(filters.command("help"))
async def help(client, message: Message):
    await message.reply("**Just send me a url** to upload it as a file.\n\n**NOTE:** Some urls are unsupported, if I said 'Unsupported Url 😐' try to transload your url via @HK_Transloader_BOT and send transloaded url to me.") 

# url upload
@JEBotZ.on_message(filters.regex(pattern=".*http.*"))
async def urlupload(client, message: Message):
    msg = await message.reply_text(text="Checking URL 🧐", quote=True)
    url = message.text
    cap = "@JEBotZ"
    thurl = "https://telegra.ph/file/a23b8f38fde1914a4bbe9.jpg" 

    # yt-dlp options to download video
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',  # Save file with title
        'format': 'best',  # Best quality format
        'noplaylist': True,  # Disable playlist download
        'quiet': True,  # Suppress verbose output
    }
    
    try: 
        # Using yt-dlp to download media file
        await msg.edit("Trying to download the video 😉")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)

        # Download thumbnail
        thumb = wget.download(thurl)
        pak = "a23b8f38fde1914a4bbe9.jpg"

        await msg.edit("Uploading File 🤡")
        await message.reply_document(downloaded_file, caption=cap, thumb=pak)  # upload downloaded file
        await msg.delete()

        # Remove downloaded files
        os.remove(downloaded_file)  # Remove downloaded media file from server
        os.remove(thumb)  # Remove thumbnail file from server
    except Exception as e:
        print(f"Error: {e}")
        await msg.edit("Unsupported URL or failed to download 😐")  # Error message


print("JEBotZ Started!")

# run bot
JEBotZ.run()
