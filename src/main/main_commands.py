# Import required classes from the library
import asyncio, os
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from ..model.crud import get_user_by_id, create_user, update_moethod
from ..info.address_info import get_account_info
from ..info.scanner import get_scanner_general_result, get_scanner_issues_result, get_scanner_liquidity_result, get_scanner_holders_result
from ..info.code_auditor import code_auditor
from .admin_commands import admin_notify, log_function
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

admin = int(os.getenv('ADMIN'))

# Convert numbers in standard numeric display format
def format_number(num):
    suffixes = ['T', 'B', 'M', 'K']
    
    for i, suf in enumerate(suffixes):
        n = 10**(3*(4-i))
        if num >= n:
            return f'{num/n:.1f}{suf}'
    rounded_number = round(num, 3)
    return rounded_number

# Measures the similarity between two strings
def levenshtein_distance(s, t):
    m, n = len(s), len(t)
    if m < n:
        s, t = t, s
        m, n = n, m
    d = [list(range(n + 1))] + [[i] + [0] * n for i in range(1, m + 1)]
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1]) + 1
    return d[m][n]
 
def compute_similarity(input_string, reference_string):
    distance = levenshtein_distance(input_string, reference_string)
    max_length = max(len(input_string), len(reference_string))
    similarity = 1 - (distance / max_length)
    return similarity

# wallet info response generate function
async def wallet_final_response(message: Update.message, context: ContextTypes.DEFAULT_TYPE, user_input:str):
    # Searching the wallet with the address
    wallet_info = get_account_info(address=user_input)
    if wallet_info:
        # Check if the result is correct
        if user_input.lower() != wallet_info["address"].lower():
            similarity = compute_similarity(user_input.lower(), wallet_info["address"].lower())
        else:
            similarity = 1
        
        if similarity > 0.8:
            if similarity != 1:
                await message.edit_text(
                    f'⚠ The address `{user_input}` is not valid. Do you mean `{wallet_info["address"]}`.',
                    parse_mode=ParseMode.MARKDOWN
                )
            table = [(wallet_info["contain_crypto"][i]["name"], wallet_info["contain_crypto"][i]["amount"]) for i in wallet_info["contain_crypto"]]
            reply_text = f'This wallet has the following networks:\n<pre>'
            first_col_width = 15 if max(len(key) for key in [i[0] for i  in table]) < 12 else max(len(key) for key in [i[0] for i  in table]) + 3
            second_col_width = 15 if len(f"$ {"{:,}".format(table[0][1])}") < 12 else len(f"$ {"{:,}".format(table[0][1])}") + 3
            for i in table:
                formatted_amount = f"$ {"{:,}".format(i[1])}"  # Formatting as float with 2 decimal places
                percent = f'{"{:,.2f}".format((i[1]/wallet_info["wallet"])*100)}%'
                reply_text = reply_text +f"{i[0]:<{first_col_width}}{formatted_amount:<{second_col_width}}{percent}\n"
            reply_text = reply_text +"</pre>"
            await message.delete()
            await context.bot.send_message(
                text= f'Wallet Address: <code>{wallet_info["address"]}</code>\n\n'
                f'💰 Total Amount: $ {"{:,}".format(wallet_info["wallet"])}\n\n'
                f'{reply_text}', 
                chat_id=message.chat_id, 
                parse_mode=ParseMode.HTML
            )
            # Add to log
            log_function(chat_id=message.chat_id, request_type="wallet", user_input=user_input, result="Successful")
        else:
            # Add to log
            log_function(chat_id=message.chat_id, request_type="wallet", user_input=user_input, result="Failed")
            await message.edit_text(f'❌ This address `{user_input}` you entered is either not available or could not be matched to a wallet by our search algorithm. If you know more details, please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(5)
            await message.delete()
    else:
        # Add to log
        log_function(chat_id=message.chat_id, request_type="wallet", user_input=user_input, result="Failed")
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, user_input=user_input, result_code="Wallet: wallet scraping failed")
        await message.edit_text(f'❌ This address `{user_input}` you entered is either not available or could not be matched to a wallet by our search algorithm. If you know more details, please contact me directly @fieryfox617',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await message.delete()

# /wallet handling functions
async def wallet_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message or update.callback_query.message
    text = update.message.text or update.callback_query.data

    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    # Check current user default method and update the method
    if not user:
        create_user(chat_id)
    if user.method != "wallet":
        update_moethod(user.id, "wallet")

    # extract address from user input
    if text.strip() == "/wallet":
        i_text = (
            "💡 The `/wallet` command requires a ticker. For example: `/wallet 0x2170ed0880ac9a755fd29b2688956bd959f933f8`. "
            "Or: type `/help` for assistance."
        )
        # Save the sent message object into a variable `sent_message`
        sent_message = await message.reply_text(i_text, parse_mode=ParseMode.MARKDOWN)
        # Wait for 5 seconds
        await asyncio.sleep(5)
        # Use `sent_message.message_id` to reference the correct message ID
        await sent_message.delete()
        return None

    user_input = text.split("/wallet ")[-1]

    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        create_user(chat_id)

    sent_message = await message.reply_text(f'Searching info of `{user_input}`', parse_mode=ParseMode.MARKDOWN)
    await wallet_final_response(message=sent_message, context=context, user_input=user_input)

# audit final response generate function
async def auditor_final_response(message: Update.message, context: ContextTypes.DEFAULT_TYPE, address:str, chain_id:int):
    # Analysing the contract with address and chainid
    analysis_data = get_scanner_general_result(address=address, chain_id=chain_id)
    if analysis_data:
        keyboard = []

        if len(analysis_data["issues"]) == 0:
            insight = f'After a detailed inspection, I didn\'t spot any warning signs.\nThis means the token is safe.\nHowever, the security level is subject to change and may change to either 🟢 or 🔴 in the future.\nSo make sure you do your research before you buy.\nYour decision to invest should depend on your confidence in the project managers.\n\n'
            warning = ""
        else:
            insight = f'After a detailed inspection, I spotted {len(analysis_data["issues"])} cautionary signals.\nThis does not imply the token is unsafe. It suggests certain features/parameters might inadvertently cause issues.\nEnsure you comprehend the below warnings thoroughly before making a purchase.\nThe security level is subject to change, potentially shifting to either 🟢 or 🔴 going forward.\nYour choice to invest should hinge on the confidence you place in the project\'s leaders.\n\n'
            warning = "⚠️Here are the warnings I found:\n"
            for i in analysis_data["issues"]:
                warning = warning + f'- {i["scwTitle"]}: {i["scwDescription"]}\n'
            warning += "AI verdict: Make sure you understand the warnings before you buy (if you'd like more details, please click the 'Issues' button).\n\n"
            keyboard.append(InlineKeyboardButton(text="⚠️ Issues", callback_data=f'issues_{address}_{chain_id}'))

        if analysis_data["owner"]:
            owner = f'👑I detected that the owner of the contract is : <code>{analysis_data["owner"]}</code>\n'
            owner += f'The owner holds {"{:.3f}".format(analysis_data["ownerbalance"])} tokens.' if analysis_data["ownerbalance"] else "The creator doesn't hold any tokens. "
            owner += f'Which is {"{:.3f}".format(analysis_data["ownerBalancePercentage"])}% of the supply.\n\n' if analysis_data["ownerBalancePercentage"] else "Which is a good safety point.\n\n"
        else:
            owner = ""

        if analysis_data["creator"]:
            creator = f'👑I detected that the creator of the contract is : <code>{analysis_data["creator"]}</code>\n'
            creator += f'The creator holds {"{:.3f}".format(analysis_data["creatorbalance"])} tokens.' if analysis_data["creatorbalance"] else "The creator doesn't hold any tokens. "
            creator += f'Which is {"{:.3f}".format(analysis_data["creatorBalancePercentage"])}% of the supply.\n\n' if analysis_data["creatorBalancePercentage"] else "Which is a good safety point.\n\n"
        else:
            creator = ""

        keyboard.append(InlineKeyboardButton(text="💧 Liquidity", callback_data=f'liquidity_{address}_{chain_id}'))
        keyboard.append(InlineKeyboardButton(text="💰 Holders", callback_data=f'holder_{address}_{chain_id}'))
        reply_markup = InlineKeyboardMarkup([keyboard])
        
        await message.delete()
        await context.bot.send_message(
            text= f'{analysis_data["project_name"]}\n'
            f'AIRM Score {analysis_data["airealm_score"]}/100\n'
            f'<code>--------------------------------------</code>\n'
            f'{insight}'
            f'{warning}'
            f'🔗I detected a {analysis_data["contractname"]} contract address : <code>{address}</code>\n\n'
            f'{owner}'
            f'{creator}'
            f'💧The current liquidity is $ {"{:,.3f}".format(analysis_data["iiquidity"])}.\n\n'
            f'💰The current total supply is {"{:,.3f}".format(analysis_data["supply"])}.\n\n', 
            chat_id=message.chat_id, 
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        # Add to log
        log_function(chat_id=message.chat_id, request_type="audit", user_input=address, result="Successful")
    else:
        # Add to log
        log_function(chat_id=message.chat_id, request_type="audit", user_input=address, result="Failed")
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, user_input=address, result_code="Audit: token audit failed")
        await message.edit_text(f'❌ This address `{address}` you entered is either not available or could not be matched to any contract by our search algorithm. If you want to know more details, please contact me directly @fieryfox617.',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await message.delete()

# /auditor handling functions
async def auditor_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message or update.callback_query.message
    text = update.message.text or update.callback_query.data

    chat_id = message.chat_id
    user = get_user_by_id(chat_id)

    # Check the current user default method and update the method
    if not user:
        create_user(chat_id)
    if user.method != "audit":
        update_moethod(user.id, "audit")

    if text.strip() == "/audit":
        i_text = (
            "💡 The `/audit` command requires a ticker. For example: `/audit 0x2170ed0880ac9a755fd29b2688956bd959f933f8`. "
            "Or: type `/help` for assistance."
        )
        # Save the sent message object into a variable `sent_message`
        sent_message = await message.reply_text(i_text, parse_mode=ParseMode.MARKDOWN)
        # Wait for 5 seconds
        await asyncio.sleep(5)
        # Use `sent_message.message_id` to reference the correct message ID
        await sent_message.delete()
        return None

    user_input = text.split("/audit ")[-1]

    sent_message = await message.reply_text(f'Analysing details of the contract of `{user_input}`', parse_mode=ParseMode.MARKDOWN)

    # Find the chain id with contract address
    wallet_info = get_account_info(address=user_input)
    if wallet_info:
        main_network = list(wallet_info["contain_crypto"].keys())[0]
        # Check if the chain id is correct
        if user_input.lower() != wallet_info["address"].lower():
            similarity = compute_similarity(user_input.lower(), wallet_info["address"].lower())
        else:
            similarity = 1
        
        if similarity > 0.8:
            if similarity != 1:
                await sent_message.edit_text(
                    f'⚠ The address `{user_input}` is not valid. Do you mean `{wallet_info["address"]}`?',
                    parse_mode=ParseMode.MARKDOWN
                )
            await auditor_final_response(message=sent_message, context=context, address=wallet_info["address"], chain_id=wallet_info["contain_crypto"][main_network]["chainid"])

        else:
            # Add to log
            log_function(chat_id=message.chat_id, request_type="audit", user_input=user_input, result="Failed")
            await sent_message.edit_text(f'❌ This address `{user_input}` you entered is either not available or could not be matched to any contract by our search algorithm. If you want to know more details, please contact me directly @fieryfox617.',parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(5)
            await sent_message.delete()
    else:
        # Add to log
        log_function(chat_id=message.chat_id, request_type="audit", user_input=user_input, result="Failed")
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, user_input=user_input, result_code="Wallet: wallet scraping failed")
        await sent_message.edit_text(f'❌ This address `{user_input}` you entered is either not available or could not be matched to any contract by our search algorithm. If you want to know more details, please contact me directly @fieryfox617.',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await sent_message.delete()

# /issues callback handling functions
async def issues_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.callback_query.message
    text = update.callback_query.data
    
    user_input = text.split("_")[1]
    chain_id = int(text.split("_")[2])

    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        create_user(chat_id)

    # await message.delete()
    sent_message = await message.edit_text(f'Advanced analysing of issues of `{user_input}`', parse_mode=ParseMode.MARKDOWN)
    
    # Advanced analysis of issues in contract analysis with address and chain id
    analysis_data = get_scanner_issues_result(address=user_input, chain_id=chain_id)
    if analysis_data:
        keyboard = [
            InlineKeyboardButton(text="⬅ Back", callback_data=f'audit_{user_input}_{chain_id}'),
            InlineKeyboardButton(text="✖ Close Auditor", callback_data=f'close'),
            ]

        if len(analysis_data["issues"]) == 0:
            reply_text = f'After a detailed inspection, I didn\'t spot any warning signs.'
        else:
            reply_text = f"Advanced view about issues of <code>{user_input}</code>\n\n"
            for i, issue in enumerate(analysis_data["issues"]):
                reply_text += f'<b>{i + 1}. {issue["scwTitle"]}</b> {"❗" if issue["issues"][0]["impact"] == "Critical" else "❕"}\n'
                reply_text += f'<i>{issue["scwDescription"]}</i>\n\n'
                for y, subissue in enumerate(issue["issues"]):
                    reply_text += f'<code>Issues: {y + 1}</code>\n'
                    reply_text += f'<pre>{subissue["description"]}</pre>'

                    if subissue.get("additionalData"):
                        for k in subissue["additionalData"]:
                            reply_text += f'<b>{k["title"]}: </b>{k["description"]}\n'
                    
                    if subissue["snippet"]:
                        reply_text += f'<b>Relevant Function Snippet: </b>\n'
                        reply_text += f'<pre>{subissue["snippet"]}</pre>'

                reply_text += "\n\n"       
        reply_markup = InlineKeyboardMarkup([keyboard])
        await sent_message.delete()
        await context.bot.send_message(
            text= f'{reply_text}', 
            chat_id=message.chat_id,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        # Add to log
        log_function(chat_id=message.chat_id, request_type="audit", user_input=user_input, result="Successful")
    else:
        # Add to log
        log_function(chat_id=message.chat_id, request_type="audit", user_input=user_input, result="Failed")
        # Notify bot administrator
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, user_input=user_input, result_code="Audit: Advanced analysis about Issues failed")
        await sent_message.edit_text(f'❌ This address `{user_input}` you entered is either not available or could not be matched to any contract by our search algorithm. If you want to know more details, please contact me directly @fieryfox617.',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await sent_message.delete()  

# /liquidity callback handling functions
async def liquidity_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.callback_query.message
    text = update.callback_query.data
    
    user_input = text.split("_")[1]
    chain_id = int(text.split("_")[2])

    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        create_user(chat_id)

    # await message.delete()
    sent_message = await message.edit_text(f'Advanced analysis of the liquidity of `{user_input}`', parse_mode=ParseMode.MARKDOWN)
    # Advanced analysis of liquidity information of contracts, by address and chain ID
    analysis_data = get_scanner_liquidity_result(address=user_input, chain_id=chain_id)
    if analysis_data:
        keyboard = [
            InlineKeyboardButton(text="⬅ Back", callback_data=f'audit_{user_input}_{chain_id}'),
            InlineKeyboardButton(text="✖ Close Auditor", callback_data=f'close'),
            ]

        reply_text =  f"Advanced liqudity analysis of <code>{user_input}</code>\n\n"

        reply_text += f'🌊 Total Liquidity: $ {"{:,.2f}".format(float(analysis_data["totalLiquidity"]))}\n\n'

        reply_text += f'🔐 Lock / 🔓 Unlock: {"{:,.2f}".format(analysis_data["totalLockedPercent"])}% / {"{:,.2f}".format(analysis_data["totalUnlockedPercent"])} %\n\n'

        reply_text += f'💯 Top LiquidityPools:\n<pre>'
        reply_text += f"{"Address":<{15}}{"Name":<{10}}{"Source":<{13}}{"LP USD"}\n"
        reply_text += f"{"-"*15}{"-"*10}{"-"*13}{"-"*10}\n"
        for i, pool in enumerate(analysis_data["liquidityPools"]):
            address = f'{pool["address"][0:5]}...{pool["address"][-5::]}'
            name = f'{pool["name"]}'
            source = f'{pool["source"]}'
            # liquidityUsd = f'$ {"{:,.2f}".format(float(pool["liquidityUsd"]))}'
            reply_text = reply_text +f"{address:<{15}}{name:<{10}}{source:<{13}}{format_number(float(pool["liquidityUsd"]))}\n"
            # reply_text = reply_text +f"<tr><td>{address}</td><td>{name}</td><td>{source}</td><td>{format_number(float(pool["liquidityUsd"]))}</td></tr>\n"
        reply_text +="</pre>\n"
        reply_text += "🏆 Top LP Token Holders\n<pre>"

        holder_lp_size = len(f"{"{:,.2f}".format(float(analysis_data["lpHolders"][0]["tokensAmount"]))}") + 3
        reply_text += f"{"Address":<{16}}{"Tokens":<{holder_lp_size}}{"LP USD":<{8}}{"Percent"}\n"
        reply_text += f"{"-"*16}{"-"*holder_lp_size}{"-"*8}{"-"*10}\n"
        for i, holder in enumerate(analysis_data["lpHolders"]):
            address = f'{holder["address"][0:5]}...{holder["address"][-5::]}'
            tokens = f'{"{:,.2f}".format(float(holder["tokensAmount"]))}'
            # liquidityUsd = f'$ {"{:,.2f}".format(holder["liquidityUsd"])}'
            percentage = f'{"{:,.2f}".format(holder["percentage"])}%'
            reply_text = reply_text +f"{address:<{16}}{tokens:<{holder_lp_size}}{format_number(holder["liquidityUsd"]):<{8}}{percentage}\n"
        reply_text +="</pre>\n\n"
        
        reply_markup = InlineKeyboardMarkup([keyboard])
        await sent_message.delete()
        await context.bot.send_message(
            text= f'{reply_text}', 
            chat_id=message.chat_id,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        # Add to log
        log_function(chat_id=message.chat_id, request_type="audit", user_input=user_input, result="Successful")
    else:
        # Add to log
        log_function(chat_id=message.chat_id, request_type="audit", user_input=user_input, result="Failed")
        # Notify bot admin
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, user_input=user_input, result_code="Audit: Advanced analysis about Liquidity failed")
        await sent_message.edit_text(f'❌ This address `{user_input}` you entered is either not available or could not be matched to any contract by our search algorithm. If you want to know more details, please contact me directly @fieryfox617.', parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await sent_message.delete()  

# /holder callback handling functions
async def holder_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.callback_query.message
    text = update.callback_query.data
    
    user_input = text.split("_")[1]
    chain_id = int(text.split("_")[2])

    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        create_user(chat_id)

    # await message.delete()
    sent_message = await message.edit_text(f'Advanced analysis of the holders of `{user_input}`', parse_mode=ParseMode.MARKDOWN)
    # Advanced analysis of holders information of contracts, by address and chain ID
    analysis_data = get_scanner_holders_result(address=user_input, chain_id=chain_id)
    if analysis_data:
        keyboard = [
            InlineKeyboardButton(text="⬅ Back", callback_data=f'audit_{user_input}_{chain_id}'),
            InlineKeyboardButton(text="✖ Close Auditor", callback_data=f'close'),
            ]

        reply_text = f"Advanced holder analysis of <code>{user_input}</code>\n\n"
        
        reply_text += f'💰 Total Supply: {"{:,.2f}".format(analysis_data["tokenTotalSupply"])}\n\n'
        flag = True
        if analysis_data["owner"] and analysis_data["ownerBalance"]:
            reply_text += f'🗝 Owner Balance/Percent: {"{:,.3f}".format(analysis_data["ownerBalance"])}/{"{:,.3f}".format(analysis_data["ownerBalancePercentage"])}%\n'
            flag = False
        if analysis_data["creator"] and analysis_data["creatorBalance"]:
            reply_text += f'🛠 Creator Balance/Percent: {"{:,.3f}".format(analysis_data["creatorBalance"])}/{"{:,.3f}".format(analysis_data["creatorBalancePercentage"])}%\n'
            flag = False
        if flag == False:
            reply_text += "\n"
        
        reply_text += f'🏆 Top Holders:\n<pre>'
        reply_text += f"{"Address":<{18}}{"Balance":<{13}}{"Percent"}\n"
        reply_text += f"{"-"*15}{"-"*10}{"-"*15}\n"
        for i, holder in enumerate(analysis_data["topHolders"]):
            address = f'{holder["address"][0:5]}...{holder["address"][-5::]}'
            balance = f'{format_number(float(holder["balance"]))}'
            percent = f'{"{:,.2f}".format(holder["percent"])}%'
            # liquidityUsd = f'$ {"{:,.2f}".format(float(pool["liquidityUsd"]))}'
            reply_text = reply_text +f"{address:<{18}}{balance:<{13}}{percent}\n"
            # reply_text = reply_text +f"<tr><td>{address}</td><td>{name}</td><td>{source}</td><td>{format_number(float(pool["liquidityUsd"]))}</td></tr>\n"
        reply_text +="</pre>\n"

        reply_markup = InlineKeyboardMarkup([keyboard])
        await sent_message.delete()
        await context.bot.send_message(
            text= f'{reply_text}', 
            chat_id=message.chat_id,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        # Add to log
        log_function(chat_id=message.chat_id, request_type="audit", user_input=user_input, result="Scuccessful")
    else:
        # Add to log
        log_function(chat_id=message.chat_id, request_type="audit", user_input=user_input, result="Failed")
        # Notify bot admin
        await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, user_input=user_input, result_code="Audit: Advanced analysis about Holders failed")
        await sent_message.edit_text(f'❌ This address `{user_input}` you entered is either not available or could not be matched to any contract by our search algorithm. If you want to know more details, please contact me directly @fieryfox617.',parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)
        await sent_message.delete()  

# /auditor callback handling functions
async def auditor_callback_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.callback_query.message
    text = update.callback_query.data
    
    user_input = text.split("_")[1]
    chain_id = int(text.split("_")[2])

    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        create_user(chat_id)

    # await message.delete()
    sent_message = await message.edit_text(f'Analysing details of the contract of `{user_input}`', parse_mode=ParseMode.MARKDOWN)

    await auditor_final_response(message=sent_message, context=context, address=user_input, chain_id=chain_id)

# /code handling functions
async def code_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the response message and buttons
    message = update.message or update.callback_query.message

    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if not user:
        create_user(chat_id)
    
    if user.method != "code":
        update_moethod(user.id, "code")
    
    await message.reply_text(f'Pleaes input your code.', parse_mode=ParseMode.MARKDOWN)

# general chat handler function
async def general_chat_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message or update.callback_query.message
    text = update.message.text or update.callback_query.data
    if "@AIRMAuditorBOT" in text:
        text = text.replace("@AIRMAuditorBOT", "").strip()
    
    chat_id = message.chat_id
    user = get_user_by_id(chat_id)
    if user.method == "wallet":
        sent_message = await message.reply_text(f'Searching info of `{text}`', parse_mode=ParseMode.MARKDOWN)
        await wallet_final_response(message=sent_message, context=context, user_input=text)
    elif user.method == "audit":
        sent_message = await message.reply_text(f'Analysing details of the contract of `{text}`', parse_mode=ParseMode.MARKDOWN)

        wallet_info = get_account_info(address=text)
        if wallet_info:
            main_network = list(wallet_info["contain_crypto"].keys())[0]
            if text.lower() != wallet_info["address"].lower():
                similarity = compute_similarity(text.lower(), wallet_info["address"].lower())
            else:
                similarity = 1
            
            if similarity > 0.8:
                if similarity != 1:
                    await sent_message.edit_text(
                        f'⚠ The address `{text}` is not valid. Do you mean `{wallet_info["address"]}`.',
                        parse_mode=ParseMode.MARKDOWN
                    )
                await auditor_final_response(message=sent_message, context=context, address=wallet_info["address"], chain_id=wallet_info["contain_crypto"][main_network]["chainid"])

            else:
                log_function(chat_id=message.chat_id, request_type="audit", user_input=text, result="Failed")
                await sent_message.edit_text(f'❌ This address `{text}` you entered is either not available or could not be matched to any contract by our search algorithm. If you want to know more details, please contact me directly @fieryfox617.',parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(5)
                await sent_message.delete()
        else:
            log_function(chat_id=message.chat_id, request_type="audit", user_input=text, result="Failed")
            await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, user_input=text, result_code="Wallet: wallet scraping failed")
            await sent_message.edit_text(f'❌ This address `{text}` you entered is either not available or could not be matched to any contract by our search algorithm. If you want to know more details, please contact me directly @fieryfox617.',parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(5)
            await sent_message.delete()
    elif user.method == "code":
        sent_message = await message.reply_text(f'Analysing the your code', parse_mode=ParseMode.MARKDOWN)
        code_audit = code_auditor(usercode=text)
        if code_audit:
            await sent_message.delete()
            for i in code_audit:
                await context.bot.send_message(
                    text= i, 
                    chat_id=message.chat_id,
                    parse_mode=ParseMode.HTML
                )
            log_function(chat_id=message.chat_id, request_type="code", user_input="Code Auditor", result="Successful")
        else:
            log_function(chat_id=message.chat_id, request_type="code", user_input="Code Auditor", result="Failed")
            await admin_notify(context=context, admin_chat_id=admin, user_chat_id=message.chat_id, user_input=text, result_code="Error in code Auditor request")
            await sent_message.edit_text(f'❌ You code is invaild code. If you want to know more details, please contact me directly @fieryfox617.',parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(5)
            await sent_message.delete()
