import os
import yt_dlp
import requests
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
        "Hello There, I'm **Url Uploader Bot** 😉\n\nJust send me a URL. Do /help for more details 🧐",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("Source", url="https://github.com/ImJanindu/UrlUploaderBot"),
                InlineKeyboardButton("Dev", url="https://t.me/Infinity_BOTs")
            ]]
        ),
    )

# Help message
@JEBotZ.on_message(filters.command("help"))
async def help(client, message: Message):
    await message.reply(
        "**Just send me a URL** to upload it as a file.\n\n**NOTE:** Some URLs are unsupported, if I said 'Unsupported URL 😐' try to transload your URL via @HK_Transloader_BOT and send the transloaded URL to me."
    )

# Function to fetch available quality formats using yt-dlp
def get_video_formats(url):
    ydl_opts = {'quiet': True, 'format': 'bestvideo+bestaudio/best'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            if not formats:
                raise ValueError("No formats found")
            return formats
        except Exception as e:
            print(f"Error fetching formats: {e}")
            return []

# Callback query handler for format selection
@JEBotZ.on_callback_query()
async def callback_query_handler(client, callback_query):
    url = callback_query.message.reply_to_message.text
    selected_format_id = callback_query.data

    ydl_opts = {
        'format': selected_format_id,
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Change this to desired format
        }],
    }
    
    try:
        await callback_query.message.edit("Downloading the selected format 😉")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)

            # Get the original thumbnail URL from the metadata
            thumb_url = info_dict.get('thumbnail')
            thumb_filename = "thumbnail.jpg"

            # Download the original thumbnail
            if thumb_url:
                thumb_response = requests.get(thumb_url)
                with open(thumb_filename, 'wb') as thumb_file:
                    thumb_file.write(thumb_response.content)
            else:
                thumb_filename = None

        # Upload the downloaded video
        await callback_query.message.edit("Uploading File 🤡")
        await callback_query.message.reply_video(downloaded_file, caption="@JEBotZ", thumb=thumb_filename)
        await callback_query.message.delete()

        # Remove the downloaded file and thumbnail
        os.remove(downloaded_file)
        if thumb_filename and os.path.exists(thumb_filename):
            os.remove(thumb_filename)
    except Exception as e:
        print(f"Error: {e}")
        await callback_query.message.edit("Failed to download the video 😐")

# URL upload handler
@JEBotZ.on_message(filters.regex(pattern=".*http.*"))
async def urlupload(client, message: Message):
    url = message.text
    msg = await message.reply_text("Fetching available qualities... 🧐")

    try:
        formats = get_video_formats(url)
        if not formats:
            await msg.edit("No formats available 😐")
            return

        buttons = []
        for f in formats:
            if 'format_id' in f and 'format_note' in f and 'filesize' in f:
                size_mb = f['filesize'] / 1024**2 if f['filesize'] else 0
                buttons.append(
                    [InlineKeyboardButton(f"{f['format_note']} - {size_mb:.2f}MB", callback_data=f['format_id'])]
                )
        
        if buttons:
            await msg.edit(
                "Choose the quality to download:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await msg.edit("No valid formats to show 😐")

    except yt_dlp.utils.DownloadError as de:
        print(f"DownloadError: {de}")
        await msg.edit("Failed to fetch video formats or unsupported URL 😐")
    except Exception as e:
        print(f"Error: {e}")
        await msg.edit("Failed to fetch video formats or unsupported URL 😐")

print("JEBotZ Started!")

# Run the bot
JEBotZ.run()
