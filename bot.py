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
        await callback_query.message.reply_text("ℹ️ Use this bot to generate Telegram session strings.")

# 🔹 Pyrogram Session Generator
async def generate_pyrogram_session(message):
    await message.reply_text("📲 Enter your phone number (e.g., +911234567890)")

    phone_number = await bot.listen_for_text(message.chat.id)
    
    async with Client("my_session", api_id=API_ID, api_hash=API_HASH) as app:
        try:
            await app.send_code(phone_number)
            await message.reply_text("🔹 Enter the OTP received on your phone.")

            otp = await bot.listen_for_text(message.chat.id)

            await app.sign_in(phone_number, otp)

            session_string = await app.export_session_string()
            await message.reply_text(f"✅ Your Pyrogram Session String:\n```\n{session_string}\n```", quote=True)

        except SessionPasswordNeeded:
            await message.reply_text("🔑 Two-Step Password Required! Enter your password.")
            password = await bot.listen_for_text(message.chat.id)

            await app.check_password(password)

            session_string = await app.export_session_string()
            await message.reply_text(f"✅ Your Pyrogram Session String:\n```\n{session_string}\n```", quote=True)

        except Exception as e:
            await message.reply_text(f"❌ Session Generation Failed: {str(e)}")

# 🔹 Listen for Text Messages
async def listen_for_text(chat_id):
    response = None
    while response is None:
        try:
            response = await bot.wait_for(filters.text & filters.private, timeout=60)
            return response.text.strip()
        except asyncio.TimeoutError:
            await bot.send_message(chat_id, "⏳ You took too long to respond. Try again!")
            return None

bot.listen_for_text = listen_for_text

bot.run()
