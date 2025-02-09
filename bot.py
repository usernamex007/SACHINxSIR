import os
import asyncio
import qrcode
from io import BytesIO
from telethon import events
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession as TelethonSession
from telethon.errors import SessionPasswordNeededError
from pyrogram import Client as PyroClient
from pyrogram.errors import SessionPasswordNeeded

# 🔹 Load API credentials from .env
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔹 Telethon Client (Bot)
bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def generate_telethon_session(user_id, phone_number):
    """ Generate Telethon session string """
    client = TelegramClient(TelethonSession(), API_ID, API_HASH)
    await client.connect()

    sent_code = await client.send_code_request(phone_number)
    await bot.send_message(user_id, "🔹 OTP भेज दिया गया है, कृपया दर्ज करें:")

    otp = await wait_for_response(user_id)

    try:
        await client.sign_in(phone_number, otp)
    except SessionPasswordNeededError:
        await bot.send_message(user_id, "🔐 2FA इनेबल है, कृपया पासवर्ड दर्ज करें:")
        password = await wait_for_response(user_id)
        await client.sign_in(password=password)

    session_string = client.session.save()
    await bot.send_message(user_id, f"✅ आपकी Telethon Session String:\n`{session_string}`\n🔒 इसे सुरक्षित रखें!")

    qr_buffer = generate_qr_code(session_string)
    await bot.send_file(user_id, qr_buffer, caption="📌 QR Code - Scan करके सुरक्षित रखें")

    await client.disconnect()

async def generate_pyrogram_session(user_id, phone_number):
    """ Generate Pyrogram session string """
    client = PyroClient("my_account", api_id=API_ID, api_hash=API_HASH)
    await client.connect()

    sent_code = await client.send_code(phone_number)
    await bot.send_message(user_id, "🔹 OTP भेज दिया गया है, कृपया दर्ज करें:")

    otp = await wait_for_response(user_id)

    try:
        await client.sign_in(phone_number, otp)
    except SessionPasswordNeeded:
        await bot.send_message(user_id, "🔐 2FA इनेबल है, कृपया पासवर्ड दर्ज करें:")
        password = await wait_for_response(user_id)
        await client.sign_in(password=password)

    session_string = client.export_session_string()
    await bot.send_message(user_id, f"✅ आपकी Pyrogram Session String:\n`{session_string}`\n🔒 इसे सुरक्षित रखें!")

    qr_buffer = generate_qr_code(session_string)
    await bot.send_file(user_id, qr_buffer, caption="📌 QR Code - Scan करके सुरक्षित रखें")

    await client.disconnect()

def generate_qr_code(data):
    """ Generate a QR Code for session string """
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

async def wait_for_response(user_id):
    """ Wait for user response in private chat """
    while True:
        msg = await bot.get_messages(user_id, limit=1)
        if msg:
            return msg[0].message

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    """ Handle /start command """
    user_id = event.sender_id

    msg_text = "🔹 *Telegram Session String Generator*\n\n" \
               "✅ *Features:* \n" \
               "- Telethon & Pyrogram Session Generate\n" \
               "- OTP & 2FA Support\n" \
               "- QR Code for Safety\n\n" \
               "📌 *Select an option below:*"

    # बटन जोड़ने के लिए अलग तरीका
    buttons = [
        [("📲 Telethon Session", "telethon")],
        [("📲 Pyrogram Session", "pyrogram")]
    ]

    await bot.send_message(user_id, msg_text, buttons=buttons, parse_mode="Markdown")

@bot.on(events.NewMessage(pattern="📲 Telethon Session"))
async def telethon_session_handler(event):
    user_id = event.sender_id
    await bot.send_message(user_id, "📱 अपना Telegram फ़ोन नंबर दर्ज करें (जैसे: `+919876543210`):")
    phone_number = await wait_for_response(user_id)
    await generate_telethon_session(user_id, phone_number)

@bot.on(events.NewMessage(pattern="📲 Pyrogram Session"))
async def pyrogram_session_handler(event):
    user_id = event.sender_id
    await bot.send_message(user_id, "📱 अपना Telegram फ़ोन नंबर दर्ज करें (जैसे: `+919876543210`):")
    phone_number = await wait_for_response(user_id)
    await generate_pyrogram_session(user_id, phone_number)

if __name__ == "__main__":
    bot.run_until_disconnected()
