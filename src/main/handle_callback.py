# Import required classes from the library
from telegram.ext import ContextTypes
from telegram import Update
# from .stactic_commands import bot_commands
from .main_commands import *

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    # Make sure to answer the callback query to give feedback to the user
    await query.answer()

    # Check if the callback_data matches 'commands'
    # if query.data == 'features':
    #     await bot_commands(update, context)

    # Below is a placeholder for how you could handle the 'close_heatmap' button press
    if query.data == 'close':
        await query.message.delete()
    # If the "Close settings" button is pressed, delete the message
    elif query.data == 'close_settings':
        await query.message.delete()

    elif query.data.startswith('issues_'):
        # Call settings function directly when "Settings" button is pressed
        await issues_callback_handle(update, context)
    
    elif query.data.startswith('liquidity_'):
        # Call settings function directly when "Settings" button is pressed
        await liquidity_callback_handle(update, context)
    
    elif query.data.startswith('holder_'):
        # Call settings function directly when "Settings" button is pressed
        await holder_callback_handle(update, context)
    
    elif query.data.startswith('audit_'):
        # Call settings function directly when "Settings" button is pressed
        await auditor_callback_handle(update, context)
    # elif query.data.startswith('heatmap_'):
    #     # Call settings function directly when "Settings" button is pressed
    #     await heatmap_callback_handle(update, context)

    # elif query.data.startswith('dx_'):
    #     # Call settings function directly when "Settings" button is pressed
    #     await dx_callback_handle(update, context)
    
    # elif query.data.startswith('i_'):
    #     # Call settings function directly when "Settings" button is pressed
    #     await i_callback_handle(update, context)

    # elif query.data.startswith('chart_'):
    #     # Call settings function directly when "Settings" button is pressed
    #     await chart_callback_handle(update, context)
    
    # elif query.data.startswith('cx_'):
    #     # Call settings function directly when "Settings" button is pressed
    #     await cx_callback_handle(update, context)