from telegram import Update
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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

# Button callback function
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "pyrogram":
        await query.edit_message_text("You selected Pyrogram V2. Please send your phone number.")
        await send_phone_number(update, context, "pyrogram")
    elif query.data == "telethon":
        await query.edit_message_text("You selected Telethon. Please send your phone number.")
        await send_phone_number(update, context, "telethon")

# Request phone number function
async def send_phone_number(update: Update, context: CallbackContext, library: str) -> None:
    await update.message.reply(phone_number_ques)
    context.user_data["library"] = library
