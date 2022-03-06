from telegram import *

# handles sending the message to the user
def send_message(updater, chat_id, message):

    if (type(message) == list):
            for n in message:
                if (type(n) != str):
                    updater.bot.sendMessage(chat_id,
                                            text=f'<pre>{n}</pre>', parse_mode=ParseMode.HTML)
                else:
                    updater.bot.send_message(chat_id,
                                            text=n, disable_web_page_preview=1)
        
    elif (type(message) != str):
        updater.bot.sendMessage(chat_id,
                                text=f'<pre>{message}</pre>', parse_mode=ParseMode.HTML)
    else:
        updater.bot.send_message(
            chat_id, text=message, disable_web_page_preview=1)