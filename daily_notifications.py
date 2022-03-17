import pandas as pd
from datetime import date
import json
import schedule
import time

from handle_messages import send_message
import api_checks
# import game_time_notifications
import game_check

def run(updater, chat_database, todays_games_database, dst_check):
    """
        Handles the inital data for the daily notifications
        and restarts the timer for the next day at 8am
    """
    todays_date = date.today()
    chat_dataframe = pd.read_csv(chat_database)
    chats_to_notify = list(
        chat_dataframe.loc[chat_dataframe['Notifications'] == 1, 'ChatID'])

    todays_games = api_checks.schedule_call(f'date={todays_date}')

    while len(chats_to_notify) > 0:
        chat_id = chats_to_notify[0]
        message = get_notification(chat_id, todays_games, chat_dataframe, todays_date, dst_check)
        if message:
            send_message(updater, chat_id, message)
        del chats_to_notify[0]
    # create csv for game time notifications
    # game_time_notifications.create_csv(todays_games, todays_games_database)

def get_notification(chat_id, todays_games, chat_dataframe, todays_date, dst_check):
    """
        Handles sending the daily notifications
    """
    
    
    chat_index = int(chat_dataframe.index[chat_dataframe['ChatID'] == chat_id].values)
    chat_team_ids = chat_dataframe.loc[[chat_index], ['TeamIDs']].values
    team_ids = str(chat_team_ids)[3:-3]
    list_of_team_ids = team_ids.split(',')
    list_of_playing_teams = []
    for game in todays_games['dates'][0]['games']:
        home_team_id = str(game['teams']['home']['team']['id'])
        away_team_id = str(game['teams']['away']['team']['id'])
        if home_team_id in list_of_team_ids:
            list_of_playing_teams.append(home_team_id)
        elif away_team_id in list_of_team_ids:
            list_of_playing_teams.append(away_team_id)
    string_of_playing_teams = ','.join(list_of_playing_teams)
    
    non_postponed_teams = (',').join(api_checks.postponed(string_of_playing_teams, todays_date))
    if not non_postponed_teams:
        return False
    team_data = api_checks.schedule_call(f'teamId={non_postponed_teams}&date={todays_date}')
    number_of_teams = int(json.dumps(team_data['totalGames']))
    
    if api_checks.season(todays_date):

        # send game day notifications
        if number_of_teams > 0:
            return game_check.check(number_of_teams, team_data, dst_check)
        else:
            return False
    else:
        return False

def timer(updater, chat_database, todays_games_database, dst_check):
    """
        Send notification at 8am every day
    """
    schedule.every().day.at("23:32").do(run, updater, chat_database, todays_games_database, dst_check)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    
def start_timer(updater, chat_database, todays_games_database, dst_check):
    timer(updater, chat_database, todays_games_database, dst_check)
    
    
    
def test(updater, chat_id, admin_chat_id, chat_database, todays_games_database, dst_check):
    """
    DEBUGING FUCTION  
        runs the daily notifications on command
    """
    if chat_id == admin_chat_id:
        send_message(updater, chat_id, 'Testing Automatic Notifications')
        run(updater, chat_database, todays_games_database, dst_check)
    else:
        return