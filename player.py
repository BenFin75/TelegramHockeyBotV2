import pandas as pd
import json

import database_functions
import api_checks

def message(user_request, teams_database):
    """
        Returns the 
        jersey number, full name, and position 
        of a given player for a given team
    """
    # formats the users message to search the api for the player
    if len(user_request) == 0:
        return_message = "Please indicate a team and player." + '\n' + "e.g. /player Pens Crosby"
    elif user_request.count(' ') > 3:
        return_message = "One player at a time please."
    else:
        team_name, player_info = parse_request(user_request)

        if not database_functions.team_check(team_name, teams_database):
            return_message = "Sorry I don't know that team."
        else:
            return_message = build_response(teams_database, team_name, player_info)
    
    return return_message


def parse_request(user_request):
    if user_request.count(' ') == 3:
        team_name, fname, lname = user_request.split(' ')
        player_info = fname + ' ' + lname
    if user_request.count(' ') < 3:
        team_name, player_info = user_request.split(' ')
    if player_info.isnumeric():
        player_info = int(player_info)

    return [team_name, player_info]


def build_response(teams_database, team_name, player_info):
    teamdf = pd.read_csv(teams_database, index_col=None)
    teamID = int(teamdf.loc[teamdf.TeamName == team_name, 'TeamID'])

    team_data = api_checks.team_call(f'{teamID}?expand=team.roster')

    roster = team_data['teams'][0]['roster']['roster']
    team = json.dumps(team_data['teams'][0]['name'],
                      ensure_ascii=False).encode('utf8')
    team_name = team[1:-1]
    team_decoded = str(team_name.decode("utf8"))

    if not check_for_player(roster, player_info):
        player_info = str(player_info)
        if player_info.isnumeric():
            return 'I cant find number ' + player_info + ' on The ' + team_decoded
        else:
            player_name = player_info.title()
            return 'I cant find anyone named ' + player_name + ' on The ' + team_decoded
    else:
        number, name, position = check_for_player(roster, player_info)
        return number + '\n' + name + '\n' + position


def check_for_player(roster, player_info):
    for player in roster:
        number = int(player['jerseyNumber'])
        name = player['person']['fullName']
        first, last = name.split(' ')
        if number == player_info or first.lower() == player_info or last.lower() == player_info or name.lower() == player_info:
            number = player['jerseyNumber']
            position = player['position']['name']
            
            return [number, name, position]
    return False