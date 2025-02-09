from telegram import Update
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Handler for button presses
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "pyrogram":
        await query.edit_message_text("You selected Pyrogram V2. Please send your phone number.")
        # You can call a function to ask for phone number
    elif query.data == "telethon":
        await query.edit_message_text("You selected Telethon. Please send your phone number.")
        # You can call a function to ask for phone number
