# required libraries
from telegram import *
from telegram.ext import *
import pandas as pd
from pathlib import Path, PureWindowsPath
import os
from datetime import datetime, timedelta, date
from threading import Timer
import pytz

# my scripts
import start_bot
import help_bot
import setup_user
import status
import remove_user
import game_check_request
import next_game_check
import last_game_check
import standings
import roster
import player
import stats
import cupcheck
import daily_notifications
import game_time_notifications
import stop_bot
import unknown_message

# gets the bot token from remote database so the code can be made public
bot_token_dataframe = pd.read_csv((os.path.join(os.path.dirname(os.getcwd()), "TelegramBotTokens.csv")))
bot_index = int(bot_token_dataframe.index[bot_token_dataframe['Bot Name'] == 'Hockey Bot testing'].values)
bot_token = str(bot_token_dataframe.loc[[bot_index], ['Bot Token']].values).strip("'[]")
bot = Bot(bot_token)

# initilizes the bot updater to handle messages
updater = Updater(bot_token, use_context=True)

# set the database paths so the bot works on any OS.
chat_database_win = PureWindowsPath('.\Database\ChatDatabase.csv')
teams_database_win = PureWindowsPath('.\Database\TeamNames.csv')
todays_games_database_win = PureWindowsPath('.\Database\\todaysgames.csv')

# OS-independent paths
chat_database = Path(chat_database_win)
teams_database = Path(teams_database_win)
todays_games_database = Path(todays_games_database_win)

# global variables for the bot
admin_chat_id = 110799848
todays_date = date.today()
time_zone = 'US/Eastern'
dst_check = bool(datetime.now(pytz.timezone(time_zone)).dst())


# handles sending the message to the user
def send_message(chat_id, message):

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

# ran when bot if first added, returns instructions for setting the bot up
def start(update, context):
    chat_id=update.effective_chat.id
    message = start_bot.message()
    send_message(chat_id, message)

# returns a list of commands and bot info
def help(update, context):
    chat_id=update.effective_chat.id
    message = help_bot.message()
    send_message(chat_id, message)

# sets up the teams a user is following and their notification status
def user_setup(update, context):
    setup_user.setup(update, context, updater, chat_database)

# returns a list of the teams a user is following and weither they are receiving notifications or not
def user_status(update, context):
    chat_id = update.effective_chat.id
    message = status.message(chat_id, chat_database, teams_database)
    send_message(chat_id, message)

def user_remove(update, context):
    remove_user.remove(update, context, updater, chat_database)

def check_game(update, context):
    chat_id = update.effective_chat.id
    message = game_check_request.message(chat_database, chat_id, todays_date, dst_check)
    send_message(chat_id, message)

def check_next_game(update, context):
    chat_id=update.effective_chat.id
    user_request = update.message.text[10:].lower()
    message = next_game_check.message(user_request, teams_database, dst_check, todays_date)
    send_message(chat_id, message)

def check_last_game(update, context):
    chat_id=update.effective_chat.id
    user_request = update.message.text[10:].lower()
    message = last_game_check.message(user_request, teams_database)
    send_message(chat_id, message)
    
# returns the division standings for one or all divisions as requested by the user
def check_standings(update, context):
    chat_id=update.effective_chat.id
    user_request = update.message.text[11:].lower()
    messages = standings.message(user_request)
    send_message(chat_id, messages)

# returns the roster for a requested team
def check_roster(update, context):
    chat_id=update.effective_chat.id
    user_request = update.message.text[8:].lower()
    message = roster.message(user_request, teams_database)
    send_message(chat_id, message)

# returns a players name and position based on their jersey number
def check_player(update, context):
    chat_id=update.effective_chat.id
    user_request = update.message.text[8:].lower()
    message = player.message(user_request, teams_database)
    send_message(chat_id, message)

# returns the stats or a player or team as requested by the user
def check_stats(update, context):
    chat_id=update.effective_chat.id
    user_request = update.message.text[7:].lower()
    message = stats.message(user_request, teams_database)
    send_message(chat_id, message)

# returns the days since the flyers and pens have won the cup, LGP!
def check_cupcheck(update, context):
    chat_id=update.effective_chat.id
    message = cupcheck.message(todays_date)
    send_message(chat_id, message)

#### ADMIN COMMANDS ###

# runs the daily notification command for testing
def test_daily_notifications(update, context):
    chat_id = update.effective_chat.id
    from_timer = False
    daily_notifications.run(chat_id, admin_chat_id, chat_database, from_timer, todays_games_database)

def test_gametime_notifications(update, context):
    chat_id = update.effective_chat.id
    from_timer = False
    game_time_notifications.test(chat_id, admin_chat_id, chat_database, from_timer, todays_games_database)

# creates the list of games for the day for testing
# def create_game_list(update, context):

# stops the bot program
def stop(update, context):
    stop_bot.command(update, updater, admin_chat_id)

# handles unknown commands submitted to the bot
def unknown(update, context):
    chat_id=update.effective_chat.id
    message = unknown_message.message()
    send_message(chat_id, message)

### Automation Functions ###

def timer():
    """
        Send notification at 8am every day
    """
    x = datetime.today()
    y = x.replace(day=x.day, hour=8, minute=0, second=0,
                  microsecond=0) + timedelta(days=1)
    delta_t = y-x

    secs = delta_t.total_seconds()

    from_timer = True
    t = Timer(secs, daily_notifications.run(chat_database, from_timer, todays_games_database))
    t.start()


# def dailynotiftimer():
#     """
#         Checks if there is a game in the next ten minutes every ten minutes
#     """
#     x = datetime.today()
#     secs = 600
#     current_hour = int(x.strftime('%H'))
#     if current_hour >= 9 and current_hour <= 24:
#         t = Timer(secs, game_time_notifications.game_check(todays_games_database))
#         t.start()
#     else:
#         t = Timer(secs, dailynotiftimer)
#         t.start()

# dispatcher for the bot to look for each command
dispatcher = updater.dispatcher
# commands that starts the bot
dispatcher.add_handler(CommandHandler('start', start))
# command that calls the bot help menu
dispatcher.add_handler(CommandHandler('help', help))

# commands that deal with editing user data 
dispatcher.add_handler(CommandHandler('setup', user_setup))
dispatcher.add_handler(CommandHandler('status', user_status))
dispatcher.add_handler(CommandHandler('removeme', user_remove))

# commands that check game times and scores
dispatcher.add_handler(CommandHandler('game', check_game))
dispatcher.add_handler(CommandHandler('nextgame', check_next_game))
dispatcher.add_handler(CommandHandler('lastgame', check_last_game))

# commands that check season long information
dispatcher.add_handler(CommandHandler('standings', check_standings))
dispatcher.add_handler(CommandHandler('roster', check_roster))
dispatcher.add_handler(CommandHandler('player', check_player))
dispatcher.add_handler(CommandHandler('stats', check_stats))
dispatcher.add_handler(CommandHandler('cupcheck', check_cupcheck))

# admin/debugging commands
dispatcher.add_handler(CommandHandler('testdaily', test_daily_notifications))
# dispatcher.add_handler(CommandHandler('testautonotify', test_gametime_notifications))
# dispatcher.add_handler(CommandHandler('creategamelist', create_game_list))
dispatcher.add_handler(CommandHandler('stop', stop))

# handles unknown messages
dispatcher.add_handler(MessageHandler(Filters.command, unknown))


# starts the bot
updater.start_polling()

# stop the bot with Ctrl-C
updater.idle()