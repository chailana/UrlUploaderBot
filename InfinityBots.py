import os
import yt_dlp
import requests
from pyrogram import filters, Client, StringSession
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified, MessageIdInvalid, ChatAdminRequired, InviteHashExpired
from config import Config

# Your session string generated from Pyrogram StringSession
session_string = "BQFWHgUAkKYKqHTzQpzU7Ea4H0ct7aaDCCkAU9oIBgan6-s4YC_PylsYdMK4t46CY4c1CxuL4kfC2DxO7q4SmTOvW5TaHlDh7Ucq9P-MeqkrLCYHDqUjS0Vi8cgdM7UNObIUVIeKfi8knCZIeEI_bEm9KjdHajVfCDA7gci8kDAhTuV2tENG_GOT3NR9naeo551ZT2HUpgjM4Pl3dkKTPIzAHTx3AbnW_nFqfMC9q--8N-iSm3BRq7n4D4MIS5f-Mydu57ZdWODNESD28T1OotG9hCIzGqeCMe345jU5JdRq_CBujDuMrj3QdzHJznzIs5YMCPdgNxWwWpTHH6EMdwrv0S5W3gAAAAGrZATKAA"

# Login to Pyrogram client using the session string
JEBotZ = Client(
    StringSession(session_string),  # Use session string here
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.TG_BOT_TOKEN
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

# Join private channels or groups via invite link
async def join_private_channel(client, invite_link):
    try:
        chat = await client.join_chat(invite_link)  # Join the channel or group
        return chat.id  # Return the chat ID for future references
    except ChatAdminRequired:
        return "admin_required"  # Bot needs admin privileges to join
    except InviteHashExpired:
        return "invalid_link"  # Invite link is invalid or expired

# URL upload and format selection
@JEBotZ.on_message(filters.regex(pattern=".*http.*"))
async def urlupload(client, message: Message):
    msg = await message.reply_text(text="Checking URL 🧐", quote=True)
    url = message.text

    # Check if the URL is a private Telegram invite link
    if "t.me/joinchat/" in url or "t.me/+" in url:
        try:
            await msg.edit("Joining the private channel/group... 😌")
            invite_link = url.split("t.me/")[1]  # Extract invite link after t.me/
            result = await join_private_channel(client, invite_link)
            
            if result == "admin_required":
                await msg.edit("Unable to join. Bot needs admin rights to join this chat 😐")
            elif result == "invalid_link":
                await msg.edit("Invalid or expired invite link 😐")
            else:
                await msg.edit(f"Successfully joined the private chat. Chat ID: {result} 😉")
        except Exception as e:
            print(f"Error: {e}")
            await msg.edit("Failed to join the private channel/group 😐")
        return  # Stop further execution if it's an invite link

    # Check if URL is in the format https://c/<channel_id>/<message_id>
    elif "https://c/" in url:
        try:
            parts = url.split('/')
            channel_id = int(parts[-2])
            message_id = int(parts[-1])
            
            await msg.edit(f"Fetching message {message_id} from channel {channel_id} 😌")
            telegram_message = await client.get_messages(channel_id, message_id)

            # Check if the message contains media
            if telegram_message.media:
                download_path = await telegram_message.download()
                
                # Reply with the downloaded file
                await message.reply_document(download_path, caption=f"Downloaded message {message_id} from channel {channel_id}")
                
                # Optional: Clean up the files after sending
                os.remove(download_path)
            else:
                await msg.edit(f"Message {message_id} does not contain media 😐")

        except MessageIdInvalid:
            await msg.edit("Invalid message ID 😐")
        except Exception as e:
            print(f"Error: {e}")
            await msg.edit("Failed to retrieve the message 😐")
        return  # Stop further execution if it's a private channel/group message

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
