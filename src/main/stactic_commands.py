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

# Define the help command callback function
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "🦾 How to use the bot\n\n"
        
        "👜 wallet command\n"
        "The `/wallet` command searches for a wallet with a given address and displays the wallet status.\n\n"
        
        "🔬 aduit command\n"
        "The `/aduit` command is for token auditors. This command will search contract address with user's given address and analyze contract and display detailed information of contract.\n\n"
        
        "🔭 code\n"
        "The `/code` command is for code auditors. This command analyzes the user's code and reports the problems and potential risks of the code.\n\n"
        
        "🍀 P.S. Using bot in group\n"
        "In group, many people chat with each other. So to use bot in group, you need to do the following:\n"
        "1. Use commands\n"
        "Please enter address with commands, e.g. `/wallet 0xaf6f2...`\n"

        "2. Enter Bot Name\n"
        "Please enter the bot name first, followed by your address or code. e.g. `@AIRMAuditorBOT 0xaf6f25B9...`\n"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)