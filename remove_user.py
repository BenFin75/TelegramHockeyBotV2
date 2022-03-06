from pyexpat.errors import messages
from telegram import *
from telegram.ext import *
import pandas as pd

def remove(update, context, updater, chat_database):

    def message(update, context: CallbackContext):
        chat_id = update.effective_chat.id

        chats_dataframe = pd.read_csv(chat_database)
        notiexists = chats_dataframe.index[chats_dataframe['ChatID'] == chat_id].values
        if notiexists.size > 0:
            reply_buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Yes", callback_data='bye'),
                    InlineKeyboardButton("No", callback_data='stay')
                ],
            ])
            updater.bot.sendMessage(chat_id,
                                    text='Are you sure you would like to delete your team and notifications data?', reply_markup=reply_buttons)
            return
        updater.bot.sendMessage(chat_id, text="You have no data! Run /Setup to start!")
        return


    def remove_button(update, context: CallbackContext):
        """
            This is the handler for the buttons called in other funtions
            When the buttons are clicked this function receives the output
        """
        chat_id = update.effective_chat.id

        if update.callback_query.data == 'bye':
            chats_dataframe = pd.read_csv(chat_database)
            chats_dataframe_without_user = chats_dataframe[chats_dataframe['ChatID'] != chat_id]
            chats_dataframe_without_user.to_csv(chat_database, index=False, header=True)
            update.callback_query.answer()
            update.callback_query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([])
            )
            context.bot.deleteMessage(
                update.callback_query.message.chat.id, update.callback_query.message.message_id)
            updater.bot.sendMessage(chat_id, text="Your team and notification data has been deleted." +
                                    "\n" + "You can run /setup to start again." + "\n" + "Thanks for using my bot, bye!")

        if update.callback_query.data == 'stay':
            update.callback_query.answer()
            update.callback_query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([])
            )
            context.bot.deleteMessage(
                update.callback_query.message.chat.id, update.callback_query.message.message_id)
            updater.bot.sendMessage(
                chat_id, text="Your team and notification data are safe")
    
    dispatcher = updater.dispatcher
    #adds the handler only for the callback data of bye or stay
    dispatcher.add_handler(CallbackQueryHandler(remove_button, pattern='^(bye|stay)$'))

    message(update, context)