from telegram import *
from telegram.ext import *
import pandas as pd

import database_functions

def setup(update, context, updater, chat_database):

    team_ids = []

    chat_id = update.effective_chat.id

    if chat_id > 0:
        chatname = update.message.chat.username
    if chat_id < 0:
        chatname = update.message.chat.title

    def message(update, context: CallbackContext):

        reply_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Penguins", callback_data=5),
                InlineKeyboardButton("Leafs", callback_data=10)
            ],
            [
                InlineKeyboardButton("Devils", callback_data=1),
                InlineKeyboardButton("Islanders", callback_data=2),
                InlineKeyboardButton("Rangers", callback_data=3),
                InlineKeyboardButton("Flyers", callback_data=4),
                InlineKeyboardButton("Bruins", callback_data=6)
            ],
            [
                InlineKeyboardButton("Sabres", callback_data=7),
                InlineKeyboardButton("Habs", callback_data=8),
                InlineKeyboardButton("Senators", callback_data=9),
                InlineKeyboardButton("Canes", callback_data=12),
                InlineKeyboardButton("Panthers", callback_data=13)
            ],
            [
                InlineKeyboardButton("Bolts", callback_data=14),
                InlineKeyboardButton("Capitals", callback_data=15),
                InlineKeyboardButton("Hawks", callback_data=16),
                InlineKeyboardButton("Wings", callback_data=17),
                InlineKeyboardButton("Predators", callback_data=18)
            ],
            [
                InlineKeyboardButton("Blues", callback_data=19),
                InlineKeyboardButton("Flames", callback_data=20),
                InlineKeyboardButton("Avs", callback_data=21),
                InlineKeyboardButton("Oilers", callback_data=22),
                InlineKeyboardButton("Canucks", callback_data=23)
            ],
            [
                InlineKeyboardButton("Ducks", callback_data=24),
                InlineKeyboardButton("Stars", callback_data=25),
                InlineKeyboardButton("Kings", callback_data=26),
                InlineKeyboardButton("Sharks", callback_data=28),
                InlineKeyboardButton("Jackets", callback_data=29)
            ],
            [
                InlineKeyboardButton("Wild", callback_data=30),
                InlineKeyboardButton("Jets", callback_data=52),
                InlineKeyboardButton("Coyotes", callback_data=53),
                InlineKeyboardButton("Knights", callback_data=54),
                InlineKeyboardButton("Kraken", callback_data=55)
            ],
            [
                InlineKeyboardButton("Done", callback_data='done'),
            ]
        ])
        updater.bot.sendMessage(update.effective_chat.id, text=(
            f'Hello {update.effective_user.first_name}, What teams would you like notifications for?'
            + "\n" + "When all teams have been added, click Done"),
            reply_markup=reply_buttons)

    def setup_button(update, context: CallbackContext):
        """
            This is the handler for the buttons called in other funtions
            When the buttons are clicked this function receives the output
        """
        
        # The button handler for pressing done when setting up the teams a user wants to follow
        if update.callback_query.data == 'done':
            update.callback_query.answer()
            # removes the buttons after selection
            update.callback_query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([])
            )
            # removes the text sent with the buttons and replaces it with a new message
            context.bot.deleteMessage(
                update.callback_query.message.chat.id, update.callback_query.message.message_id)
            setup_msg = ('Your team preferences have been updated!')
    
            context.bot.send_message(update.callback_query.message.chat.id, text=setup_msg)
            database_functions.update_teams(chat_database, chatname, team_ids, update.callback_query.message.chat.id)
            team_ids.clear()
            # game(update, context)
            notifications(update, context)

        # The button handler for turning on notifications for a user
        if update.callback_query.data == 'yes':
            notification_prefrence = 1
            update.callback_query.answer()
            update.callback_query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([])
            )
            context.bot.deleteMessage(
                update.callback_query.message.chat.id, update.callback_query.message.message_id)
            updater.bot.sendMessage(update.callback_query.message.chat.id, text="You will receive Notifications!")
            database_functions.update_notifications(chat_database, update.callback_query.message.chat.id, notification_prefrence)

        # The button handler for turning off notifications for a user
        if update.callback_query.data == 'no':
            notification_prefrence = 0
            update.callback_query.answer()
            update.callback_query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([])
            )
            context.bot.deleteMessage(
                update.callback_query.message.chat.id, update.callback_query.message.message_id)
            updater.bot.sendMessage(update.callback_query.message.chat.id, text="You will not receive Notifications!")
            database_functions.update_notifications(chat_database, update.callback_query.message.chat.id, notification_prefrence)

        # adds the users team selection to their list of followed teams
        other_buttons = ['done', 'yes', 'no']
        if update.callback_query.data not in other_buttons:
            update.callback_query.answer()
            button_value = update.callback_query.data
            team_ids.append(button_value)
    
    def notifications(update, context: CallbackContext):
        """
            Allows the user to select whether or not they want daily notifications
        """
        # this needs to be global because the handler for the buttons cant be passed variables
        chats_dataframe = pd.read_csv(chat_database)
        user_is_in_database = chats_dataframe.index[chats_dataframe['ChatID'] == update.callback_query.message.chat.id].values
        if user_is_in_database.size > 0:
            reply_buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Yes", callback_data='yes'),
                    InlineKeyboardButton("No", callback_data='no')
                ],
            ])
            updater.bot.sendMessage(update.callback_query.message.chat.id, text=(
                'Would you like daily game notifications?' + "\n" + "Notifications are sent at 8am est."), reply_markup=reply_buttons
            )
            return False
        updater.bot.sendMessage(update.callback_query.message.chat.id,
                                text="Please run /setup first!")

    dispatcher = updater.dispatcher
    # adds the handler for all callback data except bye or stay
    dispatcher.add_handler(CallbackQueryHandler(setup_button, pattern='^((?!bye|stay).)*$'))

    message(update, context)



        
