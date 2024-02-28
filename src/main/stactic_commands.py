# Import required classes from the library
import json
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from telegram.constants import ParseMode
from ..model.crud import get_user_by_id, create_user

# Define the start command callback function
async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    chat_id = update.message.chat_id
    if not get_user_by_id(chat_id):
        create_user(chat_id)
    keyboard = [[
        InlineKeyboardButton("➕ Add me to your group", url="https://t.me/AIRMCHARTBOT?startgroup=true"),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome aboard!\n"
        "Introducing Telegram's AI Auditor Bot.\n\n"
        "👜 Explore information about any account you desire!\n\n"
        "🔬 Generates AI analysis about any contract address.\n\n", reply_markup=reply_markup
    )
