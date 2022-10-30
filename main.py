# required libraries
from telegram import *
from telegram.ext import *
import pandas as pd
from pathlib import Path, PureWindowsPath
import os
from datetime import datetime, date, time, timedelta, tzinfo
import pytz
import sys

# my scripts
from handle_messages import send
import api_checks
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
import f1_for_the_fans
import daily_notifications
import game_time_notifications
import stop_bot
import unknown_message

# global variables for the bot
time_zone = pytz.timezone('US/Eastern')
todays_date = datetime.now(time_zone).date()
dst_check = bool(datetime.now(time_zone))

# gets the bot token and admin ID from environment variable
admin_chat_id = os.getenv("BOT_ADMIN_ID")
if admin_chat_id:
    admin_chat_id=int(admin_chat_id)
else:
    sys.exit("no admin chat id found. Please set $BOT_ADMIN_ID")
    
bot_token = os.getenv("HOCKEY_BOT_KEY")
if bot_token:
    bot = Bot(bot_token)
else:
    sys.exit("no bot key found. Please set $HOCKEY_BOT_KEY")

# initilizes the bot updater to handle messages
defaults = Defaults(tzinfo=time_zone)
updater = Updater(bot_token, use_context=True, defaults=defaults)

jobs = updater.job_queue
jobs.start

# set the database paths so the bot works on any OS.
chat_database_win = PureWindowsPath('.\database\chat_database.csv')
teams_database_win = PureWindowsPath('.\database\\team_names.csv')
todays_games_database_win = PureWindowsPath('.\database\\todays_games.csv')

# OS-independent paths
chat_database = Path(chat_database_win)
teams_database = Path(teams_database_win)
todays_games_database = Path(todays_games_database_win)

# ran when bot if first added, returns instructions for setting the bot up
def start(update, context):
    chat_id = update.effective_chat.id
    message = start_bot.message()
    send(updater, chat_id, message)

# returns a list of commands and bot info
def help(update, context):
    chat_id = update.effective_chat.id
    message = help_bot.message()
    send(updater, chat_id, message)

# sets up the teams a user is following and their notification status
def user_setup(update, context):
    setup_user.setup(update, context, updater, chat_database)

# returns a list of the teams a user is following and weither they are receiving notifications or not
def user_status(update, context):
    chat_id = update.effective_chat.id
    message = status.message(chat_id, chat_database, teams_database)
    send(updater, chat_id, message)

def user_remove(update, context):
    remove_user.remove(update, context, updater, chat_database)

def check_game(update, context):
    chat_id = update.effective_chat.id
    message = game_check_request.message(chat_database, chat_id, todays_date, dst_check)
    send(updater, chat_id, message)

def check_next_game(update, context):
    chat_id = update.effective_chat.id
    user_request = update.message.text[10:].lower()
    message = next_game_check.message(user_request, teams_database, dst_check, todays_date)
    send(updater, chat_id, message)

def check_last_game(update, context):
    chat_id = update.effective_chat.id
    user_request = update.message.text[10:].lower()
    message = last_game_check.message(user_request, teams_database)
    send(updater, chat_id, message)
    
# returns the division standings for one or all divisions as requested by the user
def check_standings(update, context):
    chat_id = update.effective_chat.id
    user_request = update.message.text[11:].lower()
    messages = standings.message(user_request)
    send(updater, chat_id, messages)

# returns the roster for a requested team
def check_roster(update, context):
    chat_id = update.effective_chat.id
    user_request = update.message.text[8:].lower()
    message = roster.message(user_request, teams_database)
    send(updater, chat_id, message)

# returns a players name and position based on their jersey number
def check_player(update, context):
    chat_id = update.effective_chat.id
    user_request = update.message.text[8:].lower()
    message = player.message(user_request, teams_database)
    send(updater, chat_id, message)

# returns the stats or a player or team as requested by the user
def check_stats(update, context):
    chat_id = update.effective_chat.id
    user_request = update.message.text[7:].lower()
    message = stats.message(user_request, teams_database)
    send(updater, chat_id, message)

# returns the days since the flyers and pens have won the cup, LGP!
def check_cupcheck(update, context):
    chat_id=update.effective_chat.id
    message = cupcheck.message(todays_date)
    send(updater, chat_id, message)

# returns the next F1 race time and location
def f1_next(update, context):
    chat_id = update.effective_chat.id
    message = f1_for_the_fans.next(todays_date, dst_check)
    send(updater, chat_id, message)

# returns the results from the last F1 race
def f1_last(update, context):
    chat_id = update.effective_chat.id
    message = f1_for_the_fans.last()
    send(updater, chat_id, message)

# returns the current F1 standings
def f1_standings(update, context):
    chat_id = update.effective_chat.id
    message = f1_for_the_fans.standings()
    send(updater, chat_id, message)

#### ADMIN COMMANDS ###

# runs the daily notification command for testing
def test_daily_notifications(update, context):
    chat_id = update.effective_chat.id
    if chat_id == admin_chat_id:
        send(updater, chat_id, 'Testing Daily Time Notifications')
        runtime = datetime.now(time_zone) + timedelta(seconds=30)
        daily_notifications.test(updater, chat_database, todays_games_database, dst_check, jobs, runtime)
    else:
        return

def test_gametime_notifications(update, context):
    chat_id = update.effective_chat.id
    if chat_id == admin_chat_id:
        send(updater, chat_id, 'Testing Game Time Notifications')
        game_time_notifications.test(updater, todays_date, jobs)
    else:
        return

# creates the list of games for the day for testing
def create_game_list(update, context):
    chat_id = update.effective_chat.id
    if chat_id == admin_chat_id:
        todays_games = api_checks.schedule_call(f'date={todays_date}')
        game_time_notifications.create_csv(todays_games, todays_games_database, dst_check)
        send(updater, chat_id, 'Generated csv')
    else:
        return

# returns a list of data about the bot's state
def get_info(update, context):
    chat_id = update.effective_chat.id
    if chat_id == admin_chat_id:
        message = 'date: ' + str(todays_date) + '\n' + 'dst: ' + str(dst_check)
        send(updater, chat_id, message)
    else:
        return

# stops the bot program
def stop(update, context):
    chat_id = update.effective_chat.id
    if chat_id == admin_chat_id:
        send(updater, chat_id, 'Stopping Bot')
        stop_bot.command(updater)
    else:
        return

### NO NEW COMMANDS BELOW HERE ###

# handles unknown commands submitted to the bot
def unknown(update, context):
    chat_id=update.effective_chat.id
    message = unknown_message.message()
    send(updater, chat_id, message)


### Start Automatic Notifications ###

def start_notifications():
    runtime = time(8, 00, 00, 0000, tzinfo = time_zone)
    daily_notifications.timer(updater, chat_database, todays_games_database, dst_check, jobs, runtime)
    game_time_notifications.timer(updater, todays_date, jobs, chat_database, runtime)
    
start_notifications()

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

# commands that check F1 information
dispatcher.add_handler(CommandHandler('f1next', f1_next))
dispatcher.add_handler(CommandHandler('f1last', f1_last))
dispatcher.add_handler(CommandHandler('f1standings', f1_standings))

# admin/debugging commands
dispatcher.add_handler(CommandHandler('testdaily', test_daily_notifications))
dispatcher.add_handler(CommandHandler('testgametime', test_gametime_notifications))
dispatcher.add_handler(CommandHandler('creategamelist', create_game_list))
dispatcher.add_handler(CommandHandler('getinfo', get_info))
dispatcher.add_handler(CommandHandler('stop', stop))

# handles unknown messages
dispatcher.add_handler(MessageHandler(Filters.command, unknown))


# starts the bot
updater.start_polling()

# stop the bot with Ctrl-C
updater.idle()
