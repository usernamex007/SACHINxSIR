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

user_inputs = {}

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
    chat_id = callback_query.message.chat.id
    if callback_query.data == "pyrogram":
        await callback_query.message.reply_text("📲 Enter your phone number (e.g., +911234567890).")
        user_inputs[chat_id] = {"step": "get_phone"}
    elif callback_query.data == "telethon":
        await callback_query.message.reply_text("📞 Enter your phone number (e.g., +911234567890).")
        user_inputs[chat_id] = {"step": "get_phone_telethon"}
    elif callback_query.data == "qr_login":
        await qr_code_login(callback_query.message)
    elif callback_query.data == "check_session":
        await callback_query.message.reply_text("🔹 Send your session string to check validity.")
    elif callback_query.data == "help":
        await callback_query.message.reply_text("ℹ️ Use this bot to generate Telegram session strings.")

@bot.on_message(filters.text & filters.private)
async def handle_user_input(client, message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id in user_inputs:
        step = user_inputs[chat_id].get("step")

        if step == "get_phone":
            user_inputs[chat_id]["phone"] = text
            await process_pyrogram_session(message)

        elif step == "get_phone_telethon":
            user_inputs[chat_id]["phone"] = text
            await process_telethon_session(message)

async def process_pyrogram_session(message):
    chat_id = message.chat.id
    phone_number = user_inputs[chat_id]["phone"]

    async with Client("my_session", api_id=API_ID, api_hash=API_HASH) as app:
        try:
            sent_code = await app.send_code(phone_number)
            await message.reply_text("🔹 Check your Telegram app for the OTP.")

            await asyncio.sleep(10)  # 10 सेकंड तक OTP आने का वेट करो

            await app.sign_in(phone_number, sent_code.phone_code_hash)
            session_string = await app.export_session_string()
            await message.reply_text(f"✅ Your Pyrogram Session String:\n```\n{session_string}\n```", quote=True)

        except SessionPasswordNeeded:
            await message.reply_text("🔑 Two-Step Password Required! Enter your password.")
            user_inputs[chat_id]["step"] = "get_password"

        except Exception as e:
            await message.reply_text(f"❌ Session Generation Failed: {str(e)}")

async def process_telethon_session(message):
    chat_id = message.chat.id
    phone_number = user_inputs[chat_id]["phone"]

    with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        try:
            sent_code = client.send_code_request(phone_number)
            await message.reply_text("🔹 Check your Telegram app for the OTP.")

            await asyncio.sleep(10)  # 10 सेकंड का वेट OTP के लिए

            client.sign_in(phone_number, sent_code.phone_code_hash)
            session_string = client.session.save()
            await message.reply_text(f"✅ Your Telethon Session String:\n```\n{session_string}\n```", quote=True)

        except SessionPasswordNeededError:
            await message.reply_text("🔑 Two-Step Password Required! Enter your password.")
            user_inputs[chat_id]["step"] = "get_password_telethon"

        except Exception as e:
            await message.reply_text(f"❌ Session Generation Failed: {str(e)}")

async def qr_code_login(message):
    async with Client("qr_session", api_id=API_ID, api_hash=API_HASH) as app:
        qr_code = await app.export_login_qr()
        qr_image = qrcode.make(qr_code)
        qr_image_path = "qr_code.png"
        qr_image.save(qr_image_path)
        await message.reply_photo(qr_image_path, caption="📷 Scan this QR Code to log in.")

bot.run()
