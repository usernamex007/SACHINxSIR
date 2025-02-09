import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import API_ID, API_HASH, BOT_TOKEN  # Importing API credentials from config.py
from ss.callbacks import button, send_phone_number  # Importing functions from callbacks.py

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

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
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))  # Using button from callbacks.py
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error handler
    application.add_error_handler(error)

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
