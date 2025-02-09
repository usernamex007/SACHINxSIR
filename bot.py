import os
import asyncio
import qrcode
from dotenv import load_dotenv
from pyrogram import Client, filters
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from pyrogram.errors import SessionPasswordNeeded
from telethon.errors import SessionPasswordNeededError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔹 Load Environment Variables
load_dotenv()

# 🔹 Bot Credentials
API_ID = int(os.getenv("API_ID", "28795512"))
API_HASH = os.getenv("API_HASH", "c17e4eb6d994c9892b8a8b6bfea4042a")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7767480564:AAGwzQ1wDQ8Qkdd9vktp8zW8aUOitT9fAFc")

# 🔹 Bot Initialization
bot = Client("session_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

@bot.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📲 Generate Pyrogram Session", callback_data="pyrogram")],
        [InlineKeyboardButton("📞 Generate Telethon Session", callback_data="telethon")],
        [InlineKeyboardButton("🔳 QR Code Login", callback_data="qr_login")],
        [InlineKeyboardButton("🔍 Check Session Validity", callback_data="check_session")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])
    await message.reply_text("🔹 Select an option to generate a session:", reply_markup=keyboard)

@bot.on_callback_query()
async def callback_query_handler(client, callback_query):
    if callback_query.data == "pyrogram":
        await generate_pyrogram_session(callback_query.message)
    elif callback_query.data == "telethon":
        await generate_telethon_session(callback_query.message)
    elif callback_query.data == "qr_login":
        await qr_code_login(callback_query.message)
    elif callback_query.data == "check_session":
        await callback_query.message.reply_text("🔹 Send your session string to check validity.")
    elif callback_query.data == "help":
        await help_command(client, callback_query.message)

# 🔹 Pyrogram Session Generator
async def generate_pyrogram_session(message):
    await message.reply_text("📲 Enter your phone number (e.g., +911234567890)")

    phone_number = await bot.listen(filters.private & filters.text)
    
    async with Client("my_session", api_id=API_ID, api_hash=API_HASH) as app:
        try:
            await app.send_code(phone_number.text.strip())
            await message.reply_text("🔹 Enter the OTP received on your phone.")

            otp = await bot.listen(filters.private & filters.text)

            await app.sign_in(phone_number.text.strip(), otp.text.strip())

            session_string = await app.export_session_string()
            await message.reply_text(f"✅ Your Pyrogram Session String:\n```\n{session_string}\n```", quote=True)

        except SessionPasswordNeeded:
            await message.reply_text("🔑 Two-Step Password Required! Enter your password.")
            password = await bot.listen(filters.private & filters.text)

            await app.check_password(password.text.strip())

            session_string = await app.export_session_string()
            await message.reply_text(f"✅ Your Pyrogram Session String:\n```\n{session_string}\n```", quote=True)

        except Exception as e:
            await message.reply_text(f"❌ Session Generation Failed: {str(e)}")

# 🔹 Telethon Session Generator
async def generate_telethon_session(message):
    await message.reply_text("📞 Enter your phone number (e.g., +911234567890)")

    phone_number = await bot.listen(filters.private & filters.text)

    with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        try:
            client.send_code_request(phone_number.text.strip())
            await message.reply_text("🔹 Enter the OTP received on your phone.")

            otp = await bot.listen(filters.private & filters.text)

            client.sign_in(phone_number.text.strip(), otp.text.strip())
            session_string = client.session.save()
            await message.reply_text(f"✅ Your Telethon Session String:\n```\n{session_string}\n```", quote=True)

        except SessionPasswordNeededError:
            await message.reply_text("🔑 Two-Step Password Required! Enter your password.")
            password = await bot.listen(filters.private & filters.text)

            client.sign_in(password=password.text.strip())
            session_string = client.session.save()
            await message.reply_text(f"✅ Your Telethon Session String:\n```\n{session_string}\n```", quote=True)

        except Exception as e:
            await message.reply_text(f"❌ Session Generation Failed: {str(e)}")

# 🔹 QR Code Login
async def qr_code_login(message):
    async with Client("qr_session", api_id=API_ID, api_hash=API_HASH) as app:
        qr_code = await app.export_login_qr()
        qr_image = qrcode.make(qr_code)
        qr_image_path = "qr_code.png"
        qr_image.save(qr_image_path)
        await message.reply_photo(qr_image_path, caption="📷 Scan this QR Code to log in.")

# 🔹 Check Session Validity
@bot.on_message(filters.text)
async def check_session_validity(client, message):
    session_string = message.text.strip()
    if len(session_string) < 50:
        await message.reply_text("❌ This does not look like a valid session string.")
        return

    try:
        async with Client("check_session", session_string=session_string, api_id=API_ID, api_hash=API_HASH) as app:
            await app.get_me()
            await message.reply_text("✅ This session string is valid!")
    except Exception as e:
        await message.reply_text(f"❌ Invalid session! Error: {str(e)}")

bot.run()
