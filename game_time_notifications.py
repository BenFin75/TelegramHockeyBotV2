import pandas as pd
import json
from datetime import datetime, timedelta
from unidecode import unidecode
import schedule
import time

from handle_messages import send
import api_checks

def create_notification(updater, both_teams, chat_database, todays_date):
    todays_date = '2022-03-15'
    team_ids = list(both_teams.split(','))
    chat_dataframe = pd.read_csv(chat_database)
    chat_ids = []
    for i in team_ids:
        chats_to_notify = chat_dataframe[(chat_dataframe['Notifications'] == 1) & (
            chat_dataframe['TeamIDs'].str.contains(i))]
        for i in chats_to_notify.index:
            if chats_to_notify.loc[i, 'ChatID'] not in chat_ids:
                chat_ids.append(chats_to_notify.loc[i, 'ChatID'])
    game_notif = api_checks.schedule_call(f'teamId={both_teams}&date={todays_date}')
    # the encoding is so that Montréal has its é, can't forget that
    away_team = json.dumps(game_notif['dates'][0]['games'][0]['teams']['away']['team']['name'], ensure_ascii=False).encode('utf8')
    away_team_stripped = away_team[1:-1]
    away_team_utf = str(away_team_stripped.decode("utf8"))
    away_team_unicode = unidecode(away_team_utf)
    
    home_team = json.dumps(game_notif['dates'][0]['games'][0]['teams']['home']['team']['name'], ensure_ascii=False).encode('utf8')
    home_team_stripped = home_team[1:-1]
    home_team_utf = str(home_team_stripped.decode("utf8"))
    home_team_unicode = unidecode(home_team_utf)

    teams_space = home_team_unicode + '-' + away_team_unicode
    teams_hyphen = teams_space.replace(" ", "-")

    url = "https://www.streameast.io/nhl/" + teams_hyphen + "/"

    message = ('Game Time!' + '\n' + '\n' + 'The ' + home_team_utf + '\n' +
                     'Host' + '\n' + 'The ' + away_team_utf + '\n' + '\n' + 'Watch the game at:' + '\n' + url)

    for i in chat_ids:
        chat_id = int(i)
        send(updater, chat_id, message)
        
        

def start_notifications(updater, todays_games_database, chat_database, todays_date):
  todays_games_dataframe = pd.read_csv(todays_games_database)
  for game in todays_games_dataframe.iterrows():
      home_team = str(game[1]["HomeIDs"])
      away_team = str(game[1]["AwayIDs"])
      both_teams = home_team + ',' + away_team
      game_time = game[1]["Time"]
      schedule.every().day.at(game_time).do(create_notification, updater, both_teams, chat_database, todays_date)
  while True:
    schedule.run_pending()
    time.sleep(1)

def create_csv(updater, todays_games, todays_games_database, chat_database, todays_date, dst_check):
    
    todays_dataframe = pd.DataFrame(columns=('HomeIDs', 'AwayIDs', 'Time'))
    index = 0
    if todays_games['totalItems'] >= 1:
        for i in todays_games['dates'][0]['games']:
            home_team = i['teams']['home']['team']['id']
            away_team = i['teams']['away']['team']['id']
            if dst_check == False:
                game_fulltime = i['gameDate']
                game_time = game_fulltime[12:-2]
                if dst_check == True:
                    game_time_obj = datetime.strptime(
                        game_time, '%H:%M:%S') - timedelta(hours=4)
                if dst_check == False:
                    game_time_obj = datetime.strptime(
                        game_time, '%H:%M:%S') - timedelta(hours=5)
                    game_time_obj - \
                        timedelta(minutes=game_time_obj.minute % 10)
                game_start = str(datetime.strftime(game_time_obj, '%H:%M'))
            todays_dataframe.loc[index] = [home_team, away_team, game_start]
            index += 1
        todays_dataframe.to_csv(todays_games_database, index=False, header=True)
        start_notifications(updater, todays_games_database, chat_database, todays_date)
    else:
        return

def test(updater, chat_id, admin_chat_id, todays_games_database, chat_database, todays_date):
    """
    DEBUGING FUCTION  
        runs the game time notifications on command
    """
    if chat_id == admin_chat_id:
        send(updater, chat_id, 'Testing Game Time Notifications')
        todays_games_dataframe = pd.read_csv('./Database/testinggames.csv')
        for game in todays_games_dataframe.iterrows():
            home_team = str(game[1]["HomeIDs"])
            away_team = str(game[1]["AwayIDs"])
            both_teams = home_team + ',' + away_team
            create_notification(updater, both_teams, chat_database, todays_date)
    else:
        return