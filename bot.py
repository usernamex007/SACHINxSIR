from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import random
import time
import logging

# Telegram API ID और API Hash (अपनी जानकारी यहाँ डालें)
API_ID = '28795512'  # यहाँ अपना API ID डालें
API_HASH = 'c17e4eb6d994c9892b8a8b6bfea4042a'  # यहाँ अपना API Hash डालें

# Bot Token (अपना बॉट टोकन यहाँ डालें)
BOT_TOKEN = '7610510597:AAFX2uCDdl48UTOHnIweeCMms25xOKF9PoA'

# OTP वेरिफिकेशन के लिए इन-मेमोरी स्टोर
otp_store = {}

# Logging सेटअप
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# OTP जनरेट करने का फंक्शन (अब 5 अंकों का OTP जनरेट करेगा)
def generate_otp() -> str:
    return str(random.randint(10000, 99999))  # 5-digit OTP

# OTP भेजने के लिए कमांड
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Please send your phone number in this format: +<country_code><number>")

# OTP जनरेट और वेरिफिकेशन
def send_otp(update: Update, context: CallbackContext) -> None:
    phone_number = update.message.text.strip()

    if phone_number.startswith('+'):
        # OTP जनरेट करें और भेजें
        otp = generate_otp()
        otp_store[phone_number] = {
            'otp': otp,
            'time': time.time()  # OTP एक्सपायरी टाइम
        }

        # OTP को उपयोगकर्ता को भेजें
        update.message.reply_text(f"Your OTP is: {otp}\nPlease enter it to verify.")

    else:
        update.message.reply_text("Please enter a valid phone number in the format: +<country_code><number>")

# OTP वेरीफाई करने के लिए फंक्शन
def verify_otp(update: Update, context: CallbackContext) -> None:
    user_input_otp = update.message.text.strip()
    phone_number = context.user_data.get('phone_number', None)

    if phone_number and phone_number in otp_store:
        stored_otp_data = otp_store[phone_number]
        stored_otp = stored_otp_data['otp']
        otp_time = stored_otp_data['time']

        # 5 मिनट तक वैलिड OTP चेक करें
        if time.time() - otp_time < 300:
            if user_input_otp == stored_otp:
                update.message.reply_text("OTP verified successfully! You are now authenticated.")
                del otp_store[phone_number]  # OTP को समाप्त करें
            else:
                update.message.reply_text("Invalid OTP. Please try again.")
        else:
            update.message.reply_text("OTP expired. Please request a new OTP.")
            del otp_store[phone_number]  # OTP को समाप्त करें
    else:
        update.message.reply_text("Please enter your phone number first by typing: +<country_code><number>")

# OTP वेरिफिकेशन के लिए वेरिफाई कमांड
def verify(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Please send the OTP you received after submitting your phone number.")

# Main function to start the bot
def main() -> None:
    """Start the bot."""
    updater = Updater(BOT_TOKEN)

    dispatcher = updater.dispatcher

    # बॉट के कमांड्स जोड़ें
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("verify", verify))

    # यूज़र द्वारा फोन नंबर भेजने पर OTP जनरेट करने के लिए
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_otp))

    # OTP वेरिफिकेशन के लिए
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, verify_otp))

    # बॉट को शुरू करें
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
