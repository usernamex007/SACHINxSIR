import logging
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError
)
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

API_ID = '28795512'  # Replace with your API ID
API_HASH = 'c17e4eb6d994c9892b8a8b6bfea4042a'  # Replace with your API HASH
BOT_TOKEN = '7767480564:AAGwzQ1wDQ8Qkdd9vktp8zW8aUOitT9fAFc'  # Replace with your bot token

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Ask for phone number
phone_number_ques = "Please send your phone number with country code, e.g., +19876543210"

# Start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply(
        "Welcome to the Telegram Session String Generator Bot!\n"
        "Please send your phone number to generate your session string."
    )

# Request phone number
async def send_phone_number(update: Update, context: CallbackContext) -> None:
    await update.message.reply(phone_number_ques)

# Handle phone number and create session string
async def handle_phone_number(update: Update, context: CallbackContext) -> None:
    phone_number = update.message.text.strip()
    context.user_data["phone_number"] = phone_number
    
    await update.message.reply("Please wait while we generate your session string...")
    await generate_telethon_session(update, context)

# Generate Telethon session string
async def generate_telethon_session(update: Update, context: CallbackContext) -> None:
    phone_number = context.user_data["phone_number"]
    try:
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.start(phone_number)

        # OTP request for Telethon
        await update.message.reply("Please check your Telegram app for the OTP. Send the OTP here after you receive it.")
        
        phone_code = await update.message.reply("Enter OTP: Please send it in the format '12345'.")
        await client.sign_in(phone_number, phone_code.text)

        # Two-step verification password (if enabled)
        if client.is_user_authorized() is False:  # Check if 2FA is enabled
            two_step_password = await update.message.reply("Please enter your two-step verification password.")
            await client.sign_in(password=two_step_password.text)

        # Get session string and send to user
        session_string = client.session.save()
        await update.message.reply(f"Your Telegram session string:\n`{session_string}`")
    except PhoneCodeInvalidError:
        await update.message.reply("OTP is invalid. Please try again.")
    except PhoneCodeExpiredError:
        await update.message.reply("OTP has expired. Please try again.")
    except SessionPasswordNeededError:
        await update.message.reply("Your account has 2FA enabled. Please provide your 2FA password.")
    except Exception as e:
        await update.message.reply(f"An error occurred: {str(e)}")
    finally:
        await client.disconnect()

# Main function to handle messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    if update.message.text:
        await update.message.reply("Please send your phone number to generate your session string.")

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Commands and Message Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error handler
    application.add_error_handler(error)

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
