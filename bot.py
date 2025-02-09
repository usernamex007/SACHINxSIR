import asyncio
import pyqrcode
import io
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from pyrogram import Client
from pyrogram.raw.functions.auth import ExportLoginToken
from pyrogram.raw.functions.auth import ImportLoginToken

# 🔹 Telegram API Credentials
API_ID = 28795512
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7610510597:AAFX2uCDdl48UTOHnIweeCMms25xOKF9PoA"

# 🔹 Initialize the bot
bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 🔹 Store user sessions
user_sessions = {}

# 🔹 Start Command with Image & Buttons
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
        file="https://files.catbox.moe/iuoj6u.jpg",  # URL से इमेज भेजेगा
        message="**🔥 Welcome to Session Bot 🔥**\n\n"
                "🔹 Generate Pyrogram & Telethon Sessions\n"
                "🔹 Generate QR Code Login\n"
                "🔹 Check Session String Validity",
        buttons=[
            [Button.inline("🔑 Generate Pyrogram", b"pyrogram"),
             Button.inline("🔑 Generate Telethon", b"telethon")],
            [Button.inline("📷 Generate QR Code", b"qrcode")],
            [Button.inline("🔍 Check Session Validity", b"checksession")],
        ]
    )

# 🔹 Generate Pyrogram Session
@bot.on(events.CallbackQuery(pattern=b"pyrogram"))
async def pyrogram_session(event):
    await event.respond("**🔹 Enter Your Phone Number with Country Code:**")
    user_sessions[event.sender_id] = {"type": "pyrogram"}

@bot.on(events.NewMessage)
async def handle_pyrogram_login(event):
    user_id = event.sender_id
    if user_id not in user_sessions:
        return
    
    user_type = user_sessions[user_id]["type"]
    phone = event.message.text.strip()
    
    if user_type == "pyrogram":
        client = Client(":memory:", api_id=API_ID, api_hash=API_HASH)
        await client.connect()
        sent_code = await client.send_code(phone)
        user_sessions[user_id]["client"] = client
        user_sessions[user_id]["phone"] = phone
        user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash
        
        await event.respond("🔹 Enter the OTP received on Telegram:")
        user_sessions[user_id]["type"] = "pyrogram_otp"

    elif user_type == "pyrogram_otp":
        otp = event.message.text.strip()
        client = user_sessions[user_id]["client"]
        phone = user_sessions[user_id]["phone"]
        phone_code_hash = user_sessions[user_id]["phone_code_hash"]
        
        try:
            await client.sign_in(phone_number=phone, phone_code_hash=phone_code_hash, phone_code=otp)
            session_string = client.export_session_string()
            await event.respond(f"✅ **Your Pyrogram Session String:**\n`{session_string}`\n\n🔒 Keep it safe!")
        except Exception as e:
            await event.respond(f"❌ **Error:** {e}")
        
        await client.disconnect()
        del user_sessions[user_id]

# 🔹 Generate Telethon Session
@bot.on(events.CallbackQuery(pattern=b"telethon"))
async def telethon_session(event):
    await event.respond("**🔹 Enter Your Phone Number with Country Code:**")
    user_sessions[event.sender_id] = {"type": "telethon"}

@bot.on(events.NewMessage)
async def handle_telethon_login(event):
    user_id = event.sender_id
    if user_id not in user_sessions:
        return
    
    user_type = user_sessions[user_id]["type"]
    phone = event.message.text.strip()
    
    if user_type == "telethon":
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        sent_code = await client.send_code_request(phone)
        user_sessions[user_id]["client"] = client
        user_sessions[user_id]["phone"] = phone
        user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash
        
        await event.respond("🔹 Enter the OTP received on Telegram:")
        user_sessions[user_id]["type"] = "telethon_otp"

    elif user_type == "telethon_otp":
        otp = event.message.text.strip()
        client = user_sessions[user_id]["client"]
        phone = user_sessions[user_id]["phone"]
        phone_code_hash = user_sessions[user_id]["phone_code_hash"]
        
        try:
            await client.sign_in(phone, otp, phone_code_hash=phone_code_hash)
            session_string = client.session.save()
            await event.respond(f"✅ **Your Telethon Session String:**\n`{session_string}`\n\n🔒 Keep it safe!")
        except Exception as e:
            await event.respond(f"❌ **Error:** {e}")
        
        await client.disconnect()
        del user_sessions[user_id]

# 🔹 QR Code Session Generate
@bot.on(events.CallbackQuery(pattern=b"qrcode"))
async def qr_code_session(event):
    await event.respond("🔄 Generating QR Code, please wait...")

    client = Client(":memory:", api_id=API_ID, api_hash=API_HASH)
    await client.connect()
    
    qr_login = await client.invoke(ExportLoginToken(api_id=API_ID, api_hash=API_HASH))
    qr_code = pyqrcode.create(qr_login.token.hex())
    
    buffer = io.BytesIO()
    qr_code.png(buffer, scale=10)
    buffer.seek(0)

    await event.respond("📷 **Scan this QR Code to login!**", file=buffer)

# 🔹 Session String Validity Checker
@bot.on(events.CallbackQuery(pattern=b"checksession"))
async def check_session(event):
    await event.respond("🔹 Send your Session String to check validity:")
    user_sessions[event.sender_id] = {"type": "check"}

@bot.on(events.NewMessage)
async def validate_session(event):
    user_id = event.sender_id
    if user_id not in user_sessions:
        return

    user_type = user_sessions[user_id]["type"]
    session_string = event.message.text.strip()

    if user_type == "check":
        try:
            client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
            await client.connect()
            me = await client.get_me()
            await event.respond(f"✅ **Session is valid!**\n👤 User: {me.first_name} (@{me.username})")
        except:
            await event.respond("❌ **Invalid session string!**")
        
        del user_sessions[user_id]

# 🔹 Run the bot
print("🚀 Bot is running...")
bot.run_until_disconnected()
