import pandas as pd
import json
from datetime import datetime, timedelta
import pytz
from unidecode import unidecode

from handle_messages import send
import api_checks

time_zone = pytz.timezone('US/Eastern')
todays_date = datetime.now(time_zone).date()
dst_check = bool(datetime.now(time_zone))


def create_notification(context):
    """
    Create the notification for each game 
    ran at game time
    """
    updater, both_teams, chats_to_notify, todays_date =  context.job.context
    print(both_teams) # debug to help get this working
    game_notif = api_checks.schedule_call(f'teamId={both_teams}&date={todays_date}')
    # the encoding is so that Montréal has its é, can't forget that
    away_team = json.dumps(game_notif['dates'][0]['games'][0]['teams']['away']['team']['name'], ensure_ascii=False).encode('utf8')
    away_team_stripped = away_team[1:-1]
    away_team_utf = str(away_team_stripped.decode("utf8"))
    # away_team_unicode = unidecode(away_team_utf)
    
    home_team = json.dumps(game_notif['dates'][0]['games'][0]['teams']['home']['team']['name'], ensure_ascii=False).encode('utf8')
    home_team_stripped = home_team[1:-1]
    home_team_utf = str(home_team_stripped.decode("utf8"))
    # home_team_unicode = unidecode(home_team_utf)

    # teams_space = home_team_unicode + '-' + away_team_unicode
    # teams_hyphen = teams_space.replace(" ", "-")

    # url = "https://www.streameast.io/nhl/" + teams_hyphen + "/"

    message = ('Game Time!' + '\n' + '\n' + 'The ' + home_team_utf + '\n' +
                     'Host' + '\n' + 'The ' + away_team_utf)

    for i in chats_to_notify:
        chat_id = int(i)
        send(updater, chat_id, message)
    # return schedule.CancelJob

def start_today(context):
    """
     Queue up the list of jobs for messages to send each day
    """
    updater, todays_date, jobs, chat_database = context.job.context
    current_time = datetime.now(time_zone).replace(tzinfo=None)
    todays_games = api_checks.schedule_call(f'date={todays_date}')

    games = []

    if todays_games['totalItems'] >= 1:
        for i in todays_games['dates'][0]['games']:
            home_team = i['teams']['home']['team']['id']
            away_team = i['teams']['away']['team']['id']
            game_fulltime = i['gameDate']
            if dst_check == True:
                game_time_obj = datetime.strptime(
                    game_fulltime, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=4, minutes=10)
            if dst_check == False:
                game_time_obj = datetime.strptime(
                    game_fulltime, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=5, minutes=10)
            this_game = {'home': home_team, 'away':away_team, 'time':round((game_time_obj - current_time).total_seconds())}
            games.append(this_game)

    #check games against chat db
    #if todays games has games that match chats with notifs on

    chats_dataframe = pd.read_csv(chat_database)
    chat_with_notifications = chats_dataframe.index[chats_dataframe['Notifications'] == 1].tolist()
    games_to_notify = []
    #for chats in db
    for i in chat_with_notifications:

        #if a teams are in the chats teams 
        chat_team_ids = chats_dataframe.loc[[i], ['TeamIDs']].values.tolist()
        chat_team_ids = list(map(int, chat_team_ids[0][0].split(',')))
        chat_id = chats_dataframe.loc[[i], ['ChatID']].values
        chat_id = int(chat_id)
        for game in games:
            if game['home'] in chat_team_ids or game['away'] in chat_team_ids:
                already_added = False
                # check if game is in games_to_notify
                for added_game in games_to_notify:
                    # yes
                    if added_game['home'] == game['home']:

                        # add chat id to game obj in chats_to_notify
                        added_game['chats'].append(chat_id)
                        already_added = True
                #no
                if not already_added:
                    #add game to chats_to_notify
                    game['chats'].append(chat_id)

                    # add chat id to game obj in chats_to_notify
                    games_to_notify.append(game)
    print(games_to_notify) #debug to help get this working
    for game in games_to_notify:
        both_teams = str(game['home']) + ',' + str(game['away'])
        runtime = game['time']
        chats_to_notify = game['chats']
        jobs.run_once(create_notification, runtime, context=(updater, both_teams, chats_to_notify, todays_date))

def timer(updater, todays_date, jobs, chat_database, runtime):
    """
        Send notification at 8am every day
    """
    
    jobs.run_daily(start_today, runtime, context=(updater, todays_date, jobs, chat_database))

def test(updater, todays_date, jobs):
    """
    DEBUGING FUCTION  
        runs the game time notifications on command
    """
    
    # games_to_notify = [{'home':4, 'away':13, "time":10,'chats':[110799848]}, {'home':9, 'away':30, "time":10,'chats':[110799848]}]
    # for game in games_to_notify:
    #     both_teams = str(game['home']) + ',' + str(game['away'])
    #     runtime = game['time']
    #     chats_to_notify = game['chats']
    #     jobs.run_once(create_notification, runtime, context=(updater, both_teams, chats_to_notify, todays_date))