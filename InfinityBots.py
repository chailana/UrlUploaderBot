import os
import yt_dlp
import requests  # To download the thumbnail
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

# Function to fetch available quality formats using yt-dlp
def get_video_formats(url):
    ydl_opts = {'quiet': True}  # Suppress verbose output
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])
        return formats

# Callback query handler for format selection
@JEBotZ.on_callback_query()
async def callback_query_handler(client, callback_query):
    url = callback_query.message.reply_to_message.text
    selected_format_id = callback_query.data
    cap = "@JEBotZ"

    # Update yt-dlp options with selected format
    ydl_opts = {
        'format': selected_format_id,
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'cookiefile': 'cookies.txt',  # Path to your cookies file
    }
    
    try:
        await callback_query.message.edit("Downloading the selected format 😉")
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

        # Upload the downloaded video
        await callback_query.message.edit("Uploading File 🤡")
        await callback_query.message.reply_video(downloaded_file, caption=cap, thumb=thumb_filename)
        await callback_query.message.delete()

        # Remove the downloaded file and thumbnail
        os.remove(downloaded_file)
        if thumb_filename and os.path.exists(thumb_filename):
            os.remove(thumb_filename)
    except Exception as e:
        print(f"Error: {e}")
        await callback_query.message.edit("Failed to download the video 😐")


# URL upload
@JEBotZ.on_message(filters.regex(pattern=".*http.*"))
async def urlupload(client, message: Message):
    url = message.text
    msg = await message.reply_text("Fetching available qualities... 🧐", quote=True)

    try:
        # Fetch available formats using yt-dlp
        formats = get_video_formats(url)
        if not formats:
            await msg.edit("No formats available 😐")
            return

        # Create buttons for available formats
        buttons = []
        for f in formats:
            if 'format_id' in f and 'format_note' in f and 'filesize' in f:
                size_mb = f['filesize'] / 1024**2 if f['filesize'] else 0
                buttons.append(
                    [InlineKeyboardButton(f"{f['format_note']} - {size_mb:.2f}MB", callback_data=f['format_id'])]
                )
        
        # Send the list of quality options as inline buttons
        await msg.edit(
            "Choose the quality to download:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        print(f"Error: {e}")
        await msg.edit("Failed to fetch video formats or unsupported URL 😐")

print("JEBotZ Started!")

# Run the bot
JEBotZ.run()
