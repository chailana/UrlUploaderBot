import os
import yt_dlp
import requests  # Import requests to download the thumbnail
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config

# Login to Pyrogram client
JEBotZ = Client(
    "URL Uploader",
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.TG_BOT_TOKEN,
)

# Start message
@JEBotZ.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "Hello There, I'm **Url Uploader Bot** 😉\n\nJust send me a url. Do /help for more details 🧐",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "Source", url="https://github.com/ImJanindu/UrlUploaderBot"),
                InlineKeyboardButton(
                    "Dev", url="https://t.me/Infinity_BOTs")
            ]]
        ),
    )

# Help message
@JEBotZ.on_message(filters.command("help"))
async def help(client, message: Message):
    await message.reply(
        "**Just send me a url** to upload it as a file.\n\n**NOTE:** Some urls are unsupported, if I said 'Unsupported Url 😐' try to transload your url via @HK_Transloader_BOT and send transloaded url to me."
    )

# URL upload
@JEBotZ.on_message(filters.regex(pattern=".*http.*"))
async def urlupload(client, message: Message):
    msg = await message.reply_text(text="Checking URL 🧐", quote=True)
    url = message.text
    cap = "69"
    
    # yt-dlp options to download video
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',  # Save file with title
        'format': 'best',  # Best quality format
        'noplaylist': True,  # Disable playlist download
        'quiet': True,  # Suppress verbose output
        'cookiefile': 'cookies.txt',  # Path to your cookies file
    }
    
    try:
        # Using yt-dlp to download media file
        await msg.edit("Trying to download the video 😉")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)

            # Get the original thumbnail URL from the metadata
            thumb_url = info_dict.get('thumbnail')
            thumb_filename = "thumbnail.jpg"  # Filename to save thumbnail

            # Download the original thumbnail
            if thumb_url:
                thumb_response = requests.get(thumb_url)
                with open(thumb_filename, 'wb') as thumb_file:
                    thumb_file.write(thumb_response.content)
            else:
                thumb_filename = None  # No thumbnail available

        await msg.edit("Uploading File 🤡")
        await message.reply_video(downloaded_file, caption=cap, thumb=thumb_filename)  # upload downloaded file as video
        await msg.delete()

        # Remove downloaded files
        os.remove(downloaded_file)  # Remove downloaded media file from server
        if thumb_filename and os.path.exists(thumb_filename):
            os.remove(thumb_filename)  # Remove thumbnail file from server
    except Exception as e:
        print(f"Error: {e}")
        await msg.edit("Unsupported URL or failed to download 😐")  # Error message

print("JEBotZ Started!")

# Run bot
JEBotZ.run()
