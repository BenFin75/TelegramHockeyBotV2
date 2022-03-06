import pandas as pd
from datetime import date
import requests
import json

import main
import api_checks
import game_time_notifications
import game_check

def run(chat_database, from_timer, todays_games_database):
    """
        Handles the inital data for the daily notifications
        and restarts the timer for the next day at 8am
    """
    
    todays_date = date.today()
    chat_dataframe = pd.read_csv(chat_database)
    chats_to_notify = list(
        chat_dataframe.loc[chat_dataframe['Notifications'] == 1, 'ChatID'])

    todays_games = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?date={todays_date}').json()

    while len(chats_to_notify) > 0:
        chat_id = chats_to_notify[0]
        message = get_notification(chat_id, todays_games, chat_dataframe, todays_date)
        if message:
            main.send_message(chat_id, message)
        del chats_to_notify[0]
    # create csv for game time notifications
    game_time_notifications.create_csv(todays_games, todays_games_database)
    
    # if from_timer:
    #     main.timer()

def get_notification(chat_id, todays_games, chat_dataframe, todays_date):
    """
        Handles sending the daily notifications
    """
    
    
    chat_index = int(chat_dataframe.index[chat_dataframe['ChatID'] == chat_id].values)
    chat_team_ids = chat_dataframe.loc[[chat_index], ['TeamIDs']].values
    team_ids = str(chat_team_ids)[3:-3]
    list_of_playing_teams = []
    for game in todays_games['dates'][0]['games']:
        home_team_id = game['teams']['home']['team']['id']
        away_team_id = game['teams']['away']['team']['id']
        if home_team_id in team_ids:
            list_of_playing_teams.append(home_team_id)
        elif away_team_id in team_ids:
            list_of_playing_teams.append(away_team_id)
    string_of_playing_teams = ','.join(list_of_playing_teams)
    non_postponed_teams = api_checks.postponed(string_of_playing_teams, todays_date)
    team_data = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?teamId={non_postponed_teams}&date={todays_date}').json()
    number_of_teams = int(json.dumps(team_data['totalGames']))
    
    if api_checks.season(todays_date):

        # send game day notifications
        if number_of_teams > 0:
            return game_check.check(chat_id, number_of_teams, team_data)
        else:
            return False
    else:
        return False
    
def test(chat_id, admin_chat_id, chat_database, from_timer, todays_games_database):
    """
    DEBUGING FUCTION  
        runs the daily notifications on command
    """
    if chat_id == admin_chat_id:
        main.send_message(chat_id, 'Testing Automatic Notifications')
        run(chat_database, from_timer, todays_games_database)
    else:
        return