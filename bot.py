import asyncio
import os
import qrcode
from io import BytesIO
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession as TelethonSession
from telethon.errors import SessionPasswordNeededError
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# 🔹 Load API credentials from .env
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔹 Initialize bot & dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# 🔹 Start Image
START_IMAGE = "https://files.catbox.moe/iuoj6u.jpg"

async def generate_telethon_session(phone_number, message):
    """ Generate Telethon session string via bot """
    client = TelegramClient(TelethonSession(), API_ID, API_HASH)
    await client.connect()

    sent_code = await client.send_code_request(phone_number)
    await message.answer("🔹 OTP भेज दिया गया है, कृपया दर्ज करें:")
    
    otp = await bot.wait_for("message")

    try:
        await client.sign_in(phone_number, otp.text)
    except SessionPasswordNeededError:
        await message.answer("🔐 2FA इनेबल है, कृपया पासवर्ड दर्ज करें:")
        password = await bot.wait_for("message")
        await client.sign_in(password=password.text)

    session_string = client.session.save()
    await message.answer(f"✅ आपकी Telethon Session String:\n`{session_string}`\n🔒 इसे सुरक्षित रखें!")

    qr_buffer = generate_qr_code(session_string)
    await message.answer_photo(photo=qr_buffer, caption="📌 QR Code - Scan करके सुरक्षित रखें")

    await client.disconnect()

async def generate_pyrogram_session(phone_number, message):
    """ Generate Pyrogram session string via bot """
    client = Client("my_account", api_id=API_ID, api_hash=API_HASH)
    await client.connect()

    sent_code = await client.send_code(phone_number)
    await message.answer("🔹 OTP भेज दिया गया है, कृपया दर्ज करें:")

    otp = await bot.wait_for("message")

    try:
        await client.sign_in(phone_number, otp.text)
    except SessionPasswordNeeded:
        await message.answer("🔐 2FA इनेबल है, कृपया पासवर्ड दर्ज करें:")
        password = await bot.wait_for("message")
        await client.sign_in(password=password.text)

    session_string = client.export_session_string()
    await message.answer(f"✅ आपकी Pyrogram Session String:\n`{session_string}`\n🔒 इसे सुरक्षित रखें!")

    qr_buffer = generate_qr_code(session_string)
    await message.answer_photo(photo=qr_buffer, caption="📌 QR Code - Scan करके सुरक्षित रखें")

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

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    """ Handle /start command """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📲 Telethon Session"), KeyboardButton("📲 Pyrogram Session"))

    await message.answer_photo(START_IMAGE, caption="🔹 *Telegram Session String Generator*\n\n"
                                                    "✅ *Features:* \n"
                                                    "- Telethon & Pyrogram Session Generate\n"
                                                    "- OTP & 2FA Support\n"
                                                    "- QR Code for Safety\n\n"
                                                    "📌 *Select an option below:*",
                               reply_markup=keyboard, parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == "📲 Telethon Session")
async def telethon_session_handler(message: types.Message):
    await message.answer("📱 अपना Telegram फ़ोन नंबर दर्ज करें (जैसे: `+919876543210`):")
    phone_number = await bot.wait_for("message")
    await generate_telethon_session(phone_number.text, message)

@dp.message_handler(lambda message: message.text == "📲 Pyrogram Session")
async def pyrogram_session_handler(message: types.Message):
    await message.answer("📱 अपना Telegram फ़ोन नंबर दर्ज करें (जैसे: `+919876543210`):")
    phone_number = await bot.wait_for("message")
    await generate_pyrogram_session(phone_number.text, message)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
