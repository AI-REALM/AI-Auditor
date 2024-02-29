# Import required classes from the library
import os
from telegram.ext import ContextTypes
from datetime import datetime
from telegram.constants import ParseMode

# Admin Notify Function
async def admin_notify(context: ContextTypes.DEFAULT_TYPE, admin_chat_id: int, user_chat_id: int, user_input: str, result_code: str) -> None:
    # Get today's date in the format YYYY-MM-DD
    today_date = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    # Define the error message for amdin and maintain the bot
    stats_message = (f'⏰ Time: {today_date}\n'
                     f'🧍‍♂ User: *{user_chat_id}*\n'
                     f'📤 User input: *{user_input}*\n'
                     f'🧨 Result: *{result_code}*')
    
    # Send the error message to admin
    await context.bot.send_message(
            text= stats_message, 
            chat_id=admin_chat_id,
            parse_mode=ParseMode.HTML
        )

# AIRM Auditor bot log function
def log_function(chat_id, request_type, user_input, result):
    log_path = "log.txt"
    time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    with open(log_path, 'a+', encoding='utf-8') as f:
        f.write(f'{time}--------{chat_id}--------{request_type}--------{user_input}--------{result}\n')
        f.close()