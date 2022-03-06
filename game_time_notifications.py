import pandas as pd

import main

def create_csv(todays_games, todays_dataframe, todays_games_database):
    
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
    else:
        return


def game_check():
    now = datetime.now() + timedelta(minutes=10)
    now -= timedelta(minutes=now.minute % 10)
    current_time = now.strftime('%H:%M')
    todays_df = pd.read_csv(todays_db)
    teamid_inx = list(todays_df.index[todays_df['Time'] == current_time])
    for i in teamid_inx:
        teamid_home = str(todays_df.loc[i, 'HomeIDs'])
        teamid_away = str(todays_df.loc[i, 'AwayIDs'])
        teamid_now = teamid_home + ',' + teamid_away
        gametimenotif(teamid_now)
    dailynotiftimer()


def gametimenotif(teamid_now):
    teamids = list(teamid_now.split(','))
    chatdf = pd.read_csv(chatdb)
    notif_ids = []
    for i in teamids:
        notif_chats = chatdf[(chatdf['Notifications'] == 1) & (
            chatdf['TeamIDs'].str.contains(i))]
        for i in notif_chats.index:
            if notif_chats.loc[i, 'ChatID'] not in notif_ids:
                notif_ids.append(notif_chats.loc[i, 'ChatID'])
    api_url = f'https://statsapi.web.nhl.com/api/v1/schedule?teamId={teamid_now}&date={todays_date}'
    r = requests.get(api_url)
    game_notif = r.json()
    # the encoding is so that Montréal has its é, can't forget that
    away_team = json.dumps(game_notif['dates'][0]['games'][0]['teams']
                           ['away']['team']['name'], ensure_ascii=False).encode('utf8')
    away_team_fin = away_team[1:-1]
    away_team_dec = str(away_team_fin.decode("utf8"))
    home_team = json.dumps(game_notif['dates'][0]['games'][0]['teams']
                           ['home']['team']['name'], ensure_ascii=False).encode('utf8')
    home_team_fin = home_team[1:-1]
    home_team_dec = str(home_team_fin.decode("utf8"))

    # create the url for watching the game on streameast.io
    hometeam = int(json.dumps(game_notif['dates'][0]['games'][0]['teams']
                              ['home']['team']['id']))
    awayteam = int(json.dumps(game_notif['dates'][0]['games'][0]['teams']
                              ['away']['team']['id']))
    team_names_df = pd.read_csv(teamsdb, encoding="ISO-8859-1")
    formatted_teams_df = team_names_df.loc[team_names_df['Formatted'] == 1]
    home_team_name = formatted_teams_df.loc[formatted_teams_df['TeamID']
                                            == hometeam, 'TeamName'].values
    away_team_name = formatted_teams_df.loc[formatted_teams_df['TeamID']
                                            == awayteam, 'TeamName'].values

    home_name_str = str(home_team_name[0])
    away_name_str = str(away_team_name[0])

    teams_space = home_name_str + ' ' + away_name_str
    teams_hyphen = teams_space.replace(" ", "-")

    url = "https://www.streameast.io/nhl/" + teams_hyphen + "/"
    urlformat = str("<a href='" + url + "'>Click here to watch the game</a>")

    # get the game start time
    game_fulltime = json.dumps(game_notif['dates'][0]['games'][0]['gameDate'])
    game_time = game_fulltime[12:-2]
    if dst_check == True:
        game_time_obj = datetime.strptime(
            game_time, '%H:%M:%S') - timedelta(hours=4)
    if dst_check == False:
        game_time_obj = datetime.strptime(
            game_time, '%H:%M:%S') - timedelta(hours=5)
    game_time_est = datetime.strftime(game_time_obj, '%-I:%M%p')

    game_time_msg = ('Game Time!' + '\n' + '\n' + 'The ' + home_team_dec + '\n' +
                     'Host' + '\n' + 'The ' + away_team_dec + '\n' + '@ ' + game_time_est + 
                     ' est!' + '\n' + '\n' + urlformat)

    for i in notif_ids:
        id = int(i)
        updater.bot.sendMessage(
            chat_id=id, text=game_time_msg, parse_mode=ParseMode.HTML, disable_web_page_preview=1)
        
def test(chat_id, admin_chat_id, chat_database, from_timer, todays_games_database):
    """
    DEBUGING FUCTION  
        runs the daily notifications on command
    """
    if chat_id == admin_chat_id:
        main.send_message(chat_id, 'Testing Game Time Notifications')
        gametimecheck()
    else:
        return