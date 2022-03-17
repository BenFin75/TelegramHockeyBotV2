import pandas as pd
import json

import database_functions
import api_checks

def message(user_request, teams_database):
    """
    Returns the score of the last game for the team submitted by the user
    If the game is a playoff game the seiers standings will be returned as well
    """

    if len(user_request) == 0:
        message = "Please indicate the team you want the last game for." + '\n' + "e.g. /lastgame Pens"
    
    elif user_request.count(' ') > 0:
        message = "Please submit one team at a time"
        
    else:
        last_dataframe = pd.read_csv(teams_database, index_col=None)

        if not database_functions.team_check(user_request, teams_database):
            message = "Sorry I don't konw that team."

        else:
            teamid_last = int(
                last_dataframe.loc[last_dataframe.TeamName == user_request, 'TeamID'].values)

            last_game = api_checks.team_call(f'{teamid_last}?expand=team.schedule.previous')

            game_pk = json.dumps(
                last_game['teams'][0]['previousGameSchedule']['dates'][0]['games'][0]['gamePk'])
            
            last_game_stats = api_checks.game_call(f'{game_pk}/feed/live')

            # the encoding is so that Montréal has its é, can't forget that
            home_team = json.dumps(last_game_stats['liveData']['linescore']['teams']
                                ['home']['team']['name'], ensure_ascii=False).encode('utf8')
            home_team_fin = home_team[1:-1]
            home_team_dec = str(home_team_fin.decode("utf8"))
            away_team = json.dumps(last_game_stats['liveData']['linescore']['teams']
                                ['away']['team']['name'], ensure_ascii=False).encode('utf8')
            away_team_fin = away_team[1:-1]
            away_team_dec = str(away_team_fin.decode("utf8"))
            away_team_score = json.dumps(
                last_game_stats['liveData']['linescore']['teams']['away']['goals'])
            home_team_score = json.dumps(
                last_game_stats['liveData']['linescore']['teams']['home']['goals'])
            overtime_check = int(json.dumps(
                last_game_stats['liveData']['linescore']['currentPeriod']))
            playoff_check = json.dumps(
                last_game['teams'][0]['previousGameSchedule']['dates'][0]['games'][0]['gameType']).strip('\"')

            if playoff_check == 'P':
                if overtime_check == 3:
                    overtime_msg = ''
                if overtime_check > 3:
                    overtime_check -= 3
                    overtime_check_str = str(overtime_check)
                    overtime_msg = 'In Overtime ' + overtime_check_str + '!'
            elif overtime_check == 3:
                overtime_msg = ''
            elif overtime_check == 4:
                overtime_msg = 'In Overtime!'
            elif overtime_check == 5:
                overtime_msg = 'In a Shootout!'
            if away_team_score > home_team_score:
                message = ("The " + away_team_dec + ":    " + away_team_score + "\n" +
                                " The " + home_team_dec + ":    " + home_team_score + "\n" + overtime_msg)
            if home_team_score > away_team_score:
                message = ("The " + home_team_dec + ":    " + home_team_score + "\n" +
                                " The " + away_team_dec + ":    " + away_team_score + "\n" + overtime_msg)

    return message