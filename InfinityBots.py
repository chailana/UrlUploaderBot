import os
import yt_dlp
import requests
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified, MessageIdInvalid
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
        "**Just send me a URL** to upload it as a file.\n\n**NOTE:** Some URLs are unsupported. If I say 'Unsupported URL 😐', try transloading your URL via @HK_Transloader_BOT and send the transloaded URL to me."
    )

# URL upload and format selection
@JEBotZ.on_message(filters.regex(pattern=".*http.*"))
async def urlupload(client, message: Message):
    msg = await message.reply_text(text="Checking URL 🧐", quote=True)
    url = message.text
    
    # Check if URL is a Telegram URL (e.g., t.me)
    if "t.me" in url:
        try:
            # Extract the message ID and chat ID from the Telegram URL
            # Assuming the URL format is: https://t.me/<username>/<message_id>
            parts = url.split('/')
            username = parts[-2]
            message_id = int(parts[-1])

            # Get the message from the chat
            telegram_message = await client.get_messages(username, message_id)
            
            # Check if the message contains media
            if telegram_message.media:
                # Download the media file
                download_path = await telegram_message.download()

                # Reply with the downloaded file
                await message.reply_document(download_path, caption="@JEBotZ")
                
                await msg.edit("Telegram URL processed and file uploaded successfully 😉")
            else:
                await msg.edit("This Telegram message does not contain any media 😐")

        except (MessageIdInvalid, MessageNotModified) as e:
            print(f"Error: {e}")
            await msg.edit("Failed to retrieve Telegram message or media 😐")

        return  # Stop further execution since it's a Telegram URL

    # Otherwise, proceed with yt-dlp for other URLs
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',  # Save file with title
        'noplaylist': True,  # Disable playlist download
        'quiet': True,  # Suppress verbose output
    }

    try:
        await msg.edit("Fetching available formats 😌")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)  # Don't download yet
            formats = info_dict.get('formats')  # Get available formats
            
            # Video duration (for size calculation)
            duration = info_dict.get('duration', 0)  # Duration in seconds
            
            # Build a message listing the available formats
            buttons = []
            for f in formats:
                quality = f.get('format_note', 'unknown')  # Quality description
                size = f.get('filesize', None)  # File size (if available)
                bitrate = f.get('tbr', None)  # Total bitrate in kbps

                # Check if size is available and convert to MB if so, otherwise estimate
                if size is not None:
                    file_size = f"{size / (1024 * 1024):.2f} MB"  # Convert bytes to MB
                elif bitrate and duration:
                    # Estimate file size if bitrate and duration are available
                    estimated_size = (bitrate * 1000 / 8) * duration  # Size in bytes
                    file_size = f"~{estimated_size / (1024 * 1024):.2f} MB"
                else:
                    file_size = "Unknown size"
                
                format_id = f.get('format_id')
                resolution = f.get('height', 'unknown')  # Get resolution if available
                
                # Update button label to include resolution and size
                buttons.append([InlineKeyboardButton(f"{resolution}p - {file_size}", callback_data=f"format_{format_id}")])

            # Send format options to the user as inline buttons
            await msg.edit(
                "Select the video quality:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    except Exception as e:
        print(f"Error: {e}")
        await msg.edit("Unsupported URL or failed to retrieve formats 😐")  # Error message

# Callback handler for format selection
@JEBotZ.on_callback_query(filters.regex(r"format_(\d+)"))
async def format_callback(client, callback_query: CallbackQuery):
    format_id = callback_query.data.split("_")[1]  # Extract format ID from callback
    url = callback_query.message.reply_to_message.text  # Get the original URL from the message
    msg = await callback_query.message.edit("Downloading the selected format... 😉")
    
    # yt-dlp options to download the selected format
    ydl_opts = {
        'format': format_id,  # Download the selected format
        'outtmpl': '%(title)s.%(ext)s',  # Save file with title
        'noplaylist': True,  # Disable playlist download
        'quiet': True,  # Suppress verbose output
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)

            # Get the original thumbnail URL from the metadata
            thumb_url = info_dict.get('thumbnail')
            thumb_filename = "thumbnail.jpg"  # Filename to save thumbnail

            # Download the original thumbnail if available
            if thumb_url:
                thumb_response = requests.get(thumb_url)
                with open(thumb_filename, 'wb') as thumb_file:
                    thumb_file.write(thumb_response.content)
            else:
                thumb_filename = None  # No thumbnail available

            # Upload the video with thumbnail
            await msg.edit("Uploading File 🤡")
            await callback_query.message.reply_video(downloaded_file, caption="@JEBotZ", thumb=thumb_filename)
            
            # Clean up files after upload
            os.remove(downloaded_file)
            if thumb_filename and os.path.exists(thumb_filename):
                os.remove(thumb_filename)
    except Exception as e:
        print(f"Error: {e}")
        await msg.edit("Failed to download the selected format 😐")

# Run bot
print("JEBotZ Started!")
JEBotZ.run()
