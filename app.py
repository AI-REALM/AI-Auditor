# Import required classes from the library
import os, requests
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv

from src.main.stactic_commands import *
from src.main.handle_callback import *
# from src.main.user_settings import *
from src.main.main_commands import *

load_dotenv(dotenv_path='.env')

# Use your own bot token here
TOKEN = os.getenv('TG_TOKEN')
API_URL = f"https://api.telegram.org/bot{TOKEN}/setMyCommands"

commands = [
    {"command": "start", "description": "Displays help text"},
    {"command": "wallet", "description": "Displays information about an wallet based on the given address."},
    {"command": "audit", "description": "Perform AI analysis on the given contract address."},
    {"command": "code", "description": "Perform AI analysis on the given contract code."},
    {"command": "stats", "description": "Displays the bot stats"}
]

response = requests.post(API_URL, json={"commands": commands})

# Main function update
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    # Existing /start handler
    start_handler = CommandHandler('start', bot_start)
    application.add_handler(start_handler)

    # Add the /stats command handler to the application
    wallet_handler = CommandHandler('wallet', wallet_handle)
    application.add_handler(wallet_handler)

    # Add the /stats command handler to the application
    audit_handler = CommandHandler('audit', auditor_handle)
    application.add_handler(audit_handler)

    code_handler = CommandHandler('code', code_handle)
    application.add_handler(code_handler)

    general_handler = MessageHandler(filters=filters.TEXT, callback=general_chat_handle)
    application.add_handler(general_handler)
    # Add the CallbackQueryHandler with a different variable name to avoid conflict
    callback_query_handler_obj = CallbackQueryHandler(callback_query_handler)
    application.add_handler(callback_query_handler_obj)
    
    application.run_polling()

if __name__ == '__main__':
    main()