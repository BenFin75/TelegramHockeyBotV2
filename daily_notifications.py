import pandas as pd
from datetime import date
import json

from handle_messages import send
import api_checks
import game_check

def run(context):
    """
        Handles the inital data for the daily notifications
        and restarts the timer for the next day at 8am
    """
    updater, chat_database, time_zone, utc_tz, jobs = context.job.context
    todays_date = date.today()
    chat_dataframe = pd.read_csv(chat_database)
    chats_to_notify = list(
        chat_dataframe.loc[chat_dataframe['Notifications'] == 1, 'ChatID'])

    todays_games = api_checks.schedule_call(f'date={todays_date}')

    while len(chats_to_notify) > 0:
        chat_id = chats_to_notify[0]
        message = get_notification(chat_id, todays_games, chat_dataframe, todays_date, time_zone, utc_tz)
        if message:
            send(updater, chat_id, message)
        del chats_to_notify[0]

def get_notification(chat_id, todays_games, chat_dataframe, todays_date, time_zone, utc_tz):
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
            return game_check.check(number_of_teams, team_data, time_zone, utc_tz)
        else:
            return False
    else:
        return False
    
def timer(updater, chat_database, time_zone, utc_tz, jobs, runtime):
    """
        Send notification at 8am every day
    """
    
    jobs.run_daily(run, runtime, context=(updater, chat_database, time_zone, utc_tz, jobs))
    
    
def start_timer(updater, chat_database, time_zone, utc_tz):
    timer(updater, chat_database, time_zone, utc_tz)
    
    
def test(updater, chat_database, time_zone, utc_tz, jobs, runtime):
    """
    DEBUGING FUCTION  
        runs the daily notifications on command
    """
    jobs.run_once(run, runtime, context=(updater, chat_database, time_zone, utc_tz, jobs))