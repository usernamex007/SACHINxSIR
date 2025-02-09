import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
from ss.callbacks import button  # Import the button function from ss/callbacks.py

# API Details (replace with your own)
API_ID = '28795512'  # Your API ID
API_HASH = 'c17e4eb6d994c9892b8a8b6bfea4042a'  # Your API Hash
BOT_TOKEN = '7610510597:AAFX2uCDdl48UTOHnIweeCMms25xOKF9PoA'  # Your Bot Token

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Buttons for user to select library
buttons_ques = [
    [
        InlineKeyboardButton("Pyrogram V2", callback_data="pyrogram"),
        InlineKeyboardButton("Telethon", callback_data="telethon"),
    ],
]

# Start command to send welcome message
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply(
        "Welcome to the Session String Generator Bot!\n"
        "Please choose the library for which you want to generate the session string.",
        reply_markup=InlineKeyboardMarkup(buttons_ques),
    )

# Main function to run the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))  # Registering button callback from ss/callbacks.py
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
