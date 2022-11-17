import pandas as pd

import api_checks
import game_check

def message(chat_database, chat_id, todays_date, time_zone, utc_tz):
    """
        Runs the gamecheck funtion for the teams being followed by the user
    """
    chats_dataframe = pd.read_csv(chat_database)
    chat_index = int(chats_dataframe.index[chats_dataframe['ChatID'] == chat_id].values)
    chat_team_ids = chats_dataframe.loc[[chat_index], ['TeamIDs']].values
    if str(chat_team_ids) == '[[nan]]':
        message = "you are not following any teams" + "\n" + "You can use start following teams using /setup"
    elif not api_checks.season(todays_date):
        message = "The NHL season has ended, come back next year!"
    else:
        team_ids = str(chat_team_ids)[3:-3]
        list_of_playing_teams = api_checks.postponed(team_ids, todays_date)
        number_of_teams = len(list_of_playing_teams)

        if number_of_teams > 0:
            string_of_playing_teams = ','.join(list_of_playing_teams)
            team_data = api_checks.schedule_call(f'teamId={string_of_playing_teams}&date={todays_date}')
            message = game_check.check(number_of_teams, team_data, time_zone, utc_tz)
        else:
            message = 'There is not a game today'
    
    return message