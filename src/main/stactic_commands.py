# Import required classes from the library
import json
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from telegram.constants import ParseMode
from ..model.crud import get_user_by_id, create_user, count_groups, count_individual_user

# Define the start command callback function
async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    chat_id = update.message.chat_id
    if not get_user_by_id(chat_id):
        create_user(chat_id)
    keyboard = [[
        InlineKeyboardButton("➕ Add me to your group", url="https://t.me/AIRMAuditorBOT?startgroup=true"),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome aboard!\n"
        "Introducing Telegram's AI Auditor Bot.\n\n"
        "👜 Explore information about any account you desire!\n\n"
        "🔬 Generates AI analysis about any contract address.\n\n"
        "🔭 Generates AI analysis about user's code.\n\n", reply_markup=reply_markup
    )

# Define the stats command callback function
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get today's date in the format YYYY-MM-DD
    today_date = datetime.now().strftime("%Y-%m-%d")
    user_count = count_individual_user()
    group_count = count_groups()

    with open("log.txt", 'r', encoding='utf-8') as f:
        imporession_count = len(f.readlines())
        f.close()
    # Define the stats message with the current date
    stats_message = (f'📊 *AIRM Auditor Bot stats for {today_date}:*\n\n'
                     f'💬 Groups using AIRM Auditor Bot: *{group_count}*\n'
                     f'👤 Unique users: *{user_count}*\n'
                     f'👁️ User impressions: *{imporession_count}*')
    # Send the stats message
    await update.message.reply_text(stats_message, parse_mode=ParseMode.MARKDOWN)