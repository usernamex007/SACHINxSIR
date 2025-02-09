from pyrogram import Client, filters
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("session_bot")

# Telegram API credentials
api_id = '28795512'  # Replace with your own API ID
api_hash = 'c17e4eb6d994c9892b8a8b6bfea4042a'  # Replace with your own API hash
bot_token = '7767480564:AAGwzQ1wDQ8Qkdd9vktp8zW8aUOitT9fAFc'  # Replace with your Bot Token
logger_group_id = '-1002477750706'  # Replace with your Logger Group ID

# Define your Pyrogram client with the bot token
app = Client("session_bot", api_id, api_hash, bot_token=bot_token)

# This will store OTPs and user details
otp_dict = {}

# Helper function to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Start command with a button to generate session string
@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    button = [
        [
            ("Generate Session String", "generate_session")
        ]
    ]
    await message.reply("Welcome! Please choose an option below.", reply_markup={"inline_keyboard": button})
    logger.info(f"New user started bot: {user_id}")
    # Notify the logger group about the new user starting the bot
    await app.send_message(logger_group_id, f"New user started the bot: {user_id}")

# Handle the button press for session string generation
@app.on_callback_query(filters.regex("generate_session"))
async def generate_session_string(client, callback_query):
    user_id = callback_query.from_user.id
    await callback_query.message.reply("Please enter your phone number (in international format).")
    logger.info(f"User {user_id} pressed the button to generate session string.")

# Get phone number from user
@app.on_message(filters.text & filters.regex(r'^\+?\d{10,15}$'))
async def handle_phone_number(client, message):
    user_id = message.from_user.id
    phone_number = message.text
    otp = generate_otp()
    otp_dict[user_id] = otp
    # Send OTP to user's telegram account (as a message)
    await message.reply(f"OTP sent: {otp}. Please enter the OTP to proceed.")
    logger.info(f"OTP sent to user {user_id}: {otp}")

# Handle OTP input
@app.on_message(filters.text & filters.regex(r'^\d{6}$'))
async def handle_otp(client, message):
    user_id = message.from_user.id
    entered_otp = message.text
    if otp_dict.get(user_id) == entered_otp:
        # OTP is correct, now check for two-step password
        await message.reply("OTP verified successfully!")
        logger.info(f"OTP verified for user {user_id}. Checking two-step password.")

        # Here, check if user has set a two-step password (you can use some logic or external check for this)
        two_step_password_set = False  # For now assuming they haven't set it, change as needed

        if two_step_password_set:
            await message.reply("Please enter your two-step password.")
            logger.info(f"Requesting two-step password from user {user_id}")
        else:
            # Generate session string
            session_string = client.export_session_string()
            await message.reply(f"Here is your session string: {session_string}")
            logger.info(f"Session string generated for user {user_id}")
    else:
        await message.reply("Incorrect OTP! Please try again.")
        logger.info(f"Incorrect OTP entered for user {user_id}")

# Handle two-step password (if set)
@app.on_message(filters.text & ~filters.command())
async def handle_two_step_password(client, message):
    user_id = message.from_user.id
    entered_password = message.text

    # Check the entered password with the actual password (replace with your logic)
    correct_password = "your_password"  # Placeholder for actual two-step password check

    if entered_password == correct_password:
        session_string = client.export_session_string()
        await message.reply(f"Two-step password verified! Here is your session string: {session_string}")
        logger.info(f"Session string generated for user {user_id} after two-step password verification.")
    else:
        await message.reply("Incorrect two-step password! Please try again.")
        logger.info(f"Incorrect two-step password entered for user {user_id}")

# Run the bot
app.run()
