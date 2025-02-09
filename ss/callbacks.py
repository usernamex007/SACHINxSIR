from telegram import Update
from telegram.ext import CallbackContext

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
    await update.message.reply("Please send your phone number with country code, e.g., +19876543210")
    context.user_data["library"] = library
