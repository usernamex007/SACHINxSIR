import logging
import asyncio
from pyrogram import Client as PyroClient, errors as pyro_errors
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError
)
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler  # Fix for CallbackQueryHandler import
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


API_ID = '28795512'  # यहाँ अपना API ID डालें
API_HASH = 'c17e4eb6d994c9892b8a8b6bfea4042a'  # यहाँ अपना API Hash डालें
BOT_TOKEN = '7767480564:AAGwzQ1wDQ8Qkdd9vktp8zW8aUOitT9fAFc'


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Ask user to choose which library they want to generate the session string for
ask_ques = "Please choose the Python library you want to generate the string session for:"
buttons_ques = [
    [
        InlineKeyboardButton("Pyrogram V2", callback_data="pyrogram"),
        InlineKeyboardButton("Telethon", callback_data="telethon"),
    ],
]

# Ask for phone number after choosing library
phone_number_ques = "Please send your phone number with country code, e.g., +19876543210"

# Start command
async def start(update: Update, context: CallbackContext) -> None:
    if update.message:
        await update.message.reply(
            "Welcome to the Session String Generator Bot!\n"
            "Please choose the library for which you want to generate the session string.",
            reply_markup=InlineKeyboardMarkup(buttons_ques),
        )
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "Welcome to the Session String Generator Bot!\n"
            "Please choose the library for which you want to generate the session string.",
            reply_markup=InlineKeyboardMarkup(buttons_ques),
        )


# Button callback
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "pyrogram":
        await query.edit_message_text("You selected Pyrogram V2. Please send your phone number.")
        await send_phone_number(update, context, "pyrogram")
    elif query.data == "telethon":
        await query.edit_message_text("You selected Telethon. Please send your phone number.")
        await send_phone_number(update, context, "telethon")

# Request phone number
async def send_phone_number(update: Update, context: CallbackContext, library: str) -> None:
    await update.message.reply(phone_number_ques)
    context.user_data["library"] = library

# Handle phone number
async def handle_phone_number(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    phone_number = update.message.text.strip()
    context.user_data["phone_number"] = phone_number

    library = context.user_data.get("library")
    
    if library == "pyrogram":
        await update.message.reply("Please wait while we generate your Pyrogram V2 session...")
        await generate_pyrogram_session(update, context)
    elif library == "telethon":
        await update.message.reply("Please wait while we generate your Telethon session...")
        await generate_telethon_session(update, context)

# Pyrogram V2 session generation
async def generate_pyrogram_session(update: Update, context: CallbackContext) -> None:
    phone_number = context.user_data["phone_number"]
    try:
        client = PyroClient("session_v2", API_ID, API_HASH)
        await client.start(phone_number)

        # OTP request for Pyrogram V2
        await update.message.reply("Please check your Telegram app for the OTP. Send the OTP here after you receive it.")
        phone_code = await update.message.reply("Enter OTP: Please send it in the format '12345'.")
        phone_code_text = phone_code.text.strip()  # Ensure we are using the text input
        await client.sign_in(phone_number, phone_code_text)

        # Two-step verification password (if enabled)
        if client.is_user_authorized() is False:  # Check if 2FA is enabled
            two_step_password = await update.message.reply("Please enter your two-step verification password.")
            await client.check_password(two_step_password.text.strip())

        session_string = await client.export_session_string()
        await update.message.reply(f"Your Pyrogram V2 session string:\n`{session_string}`")
    except pyro_errors.FloodWait as e:
        await update.message.reply(f"Please wait for {e.x} seconds before trying again.")
    except Exception as e:
        await update.message.reply(f"An error occurred: {str(e)}")
    finally:
        await client.stop()

# Telethon session generation
async def generate_telethon_session(update: Update, context: CallbackContext) -> None:
    phone_number = context.user_data["phone_number"]
    try:
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.start(phone_number)

        # OTP request for Telethon
        await update.message.reply("Please check your Telegram app for the OTP. Send the OTP here after you receive it.")
        phone_code = await update.message.reply("Enter OTP: Please send it in the format '12345'.")
        phone_code_text = phone_code.text.strip()  # Ensure we are using the text input
        await client.sign_in(phone_number, phone_code_text)

        # Two-step verification password (if enabled)
        if client.is_user_authorized() is False:  # Check if 2FA is enabled
            two_step_password = await update.message.reply("Please enter your two-step verification password.")
            await client.sign_in(password=two_step_password.text.strip())

        session_string = client.session.save()
        await update.message.reply(f"Your Telethon session string:\n`{session_string}`")
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
        await update.message.reply("Please choose an option using the buttons below.", reply_markup=InlineKeyboardMarkup(buttons_ques))

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Commands and Message Handlers
    application.add_handler(CommandHandler("start", start))  # Using the start function from callbacks
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error handler
    application.add_error_handler(error)

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
