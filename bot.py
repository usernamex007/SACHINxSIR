import asyncio
import os
import qrcode
from pyrogram import Client, filters
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Credentials
API_ID=28795512
API_HASH="c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7767480564:AAGwzQ1wDQ8Qkdd9vktp8zW8aUOitT9fAFc"

# Welcome Photo (इसे अपनी मनचाही फोटो से बदल सकते हैं)
WELCOME_PHOTO = "welcome.jpg"

bot = Client("session_bot", bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📲 Generate Pyrogram Session", callback_data="pyrogram")],
        [InlineKeyboardButton("📞 Generate Telethon Session", callback_data="telethon")],
        [InlineKeyboardButton("🔳 QR Code से लॉगिन करें", callback_data="qr_login")],
        [InlineKeyboardButton("🔍 Check Session Validity", callback_data="check_session")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])
    await message.reply_photo(WELCOME_PHOTO, caption="🔹 Session Generate करने के लिए ऑप्शन चुनें:", reply_markup=keyboard)

@bot.on_message(filters.command("help"))
async def help_command(client, message):
    help_text = (
        "**🤖 Telegram Session Generator Bot**\n\n"
        "🔹 **Pyrogram Session:** Telegram पर Pyrogram के लिए Session String बनाता है।\n"
        "🔹 **Telethon Session:** Telethon के लिए Session String बनाता है।\n"
        "🔹 **QR Code Login:** QR Code स्कैन करके लॉगिन करें।\n"
        "🔹 **Session Expiry Checker:** यह चेक करता है कि आपका Session Active है या Expired।\n\n"
        "✅ **स्टार्ट करने के लिए:** `/start`\n"
        "✅ **मदद के लिए:** `/help`"
    )
    await message.reply_text(help_text)

@bot.on_callback_query()
async def callback_query_handler(client, callback_query):
    if callback_query.data == "pyrogram":
        await callback_query.message.reply_text("🔹 Pyrogram Session Generate किया जा रहा है...")
        await pyrogram_session(callback_query.message)
    elif callback_query.data == "telethon":
        await callback_query.message.reply_text("🔹 Telethon Session Generate किया जा रहा है...")
        await telethon_session(callback_query.message)
    elif callback_query.data == "qr_login":
        await callback_query.message.reply_text("🔹 QR Code लॉगिन स्टार्ट हो रहा है...")
        await qr_code_login(callback_query.message)
    elif callback_query.data == "check_session":
        await callback_query.message.reply_text("🔹 कृपया अपनी Session String भेजें ताकि हम उसकी वैधता जांच सकें।")
    elif callback_query.data == "help":
        await help_command(client, callback_query.message)

async def pyrogram_session(message):
    async with Client("my_session", api_id=API_ID, api_hash=API_HASH) as app:
        session_string = await app.export_session_string()
        await message.reply_text(f"✅ आपकी Pyrogram Session String:\n```\n{session_string}\n```", quote=True)

async def telethon_session(message):
    with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        session_string = client.session.save()
        await message.reply_text(f"✅ आपकी Telethon Session String:\n```\n{session_string}\n```", quote=True)

async def qr_code_login(message):
    async with Client("qr_session", api_id=API_ID, api_hash=API_HASH) as app:
        qr_code = await app.export_login_qr()
        qr_image = qrcode.make(qr_code)
        qr_image_path = "qr_code.png"
        qr_image.save(qr_image_path)
        await message.reply_photo(qr_image_path, caption="📷 QR Code स्कैन करें और लॉगिन करें।")

@bot.on_message(filters.text)
async def check_session_validity(client, message):
    session_string = message.text.strip()
    if len(session_string) < 50:
        await message.reply_text("❌ यह एक वैध Session String नहीं लगती। कृपया सही Session भेजें।")
        return

    try:
        async with Client("check_session", session_string=session_string, api_id=API_ID, api_hash=API_HASH) as app:
            await app.get_me()
            await message.reply_text("✅ यह Session String वैध है!")
    except Exception as e:
        await message.reply_text(f"❌ Session Invalid है! Error: {str(e)}")

bot.run()
