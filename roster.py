import prettytable as pt
import pandas as pd
import json

import database_functions
import api_checks

def message(team_name, teams_database):
    """
        returns the roster for a given team
    """
    # gets the team name the user submitted
    if len(team_name) == 0:
            return_message = "Please indicate the team you want the roster of." + '\n' + "e.g. /roster Pens"


    # check if the user submitted a supported team name
    if not database_functions.team_check(team_name, teams_database):
        return_message = "Sorry I don't know that team."
    else:
        return_message = build_response(teams_database, team_name)

    return return_message

def build_response(teams_database, team_name):

    # searches the api for the team name
    teamdf = pd.read_csv(teams_database, index_col=None)
    teamID = int(teamdf.loc[teamdf.TeamName == team_name, 'TeamID'])
    team_data = api_checks.team_call(f'{teamID}?expand=team.roster')

    roster = team_data['teams'][0]['roster']['roster']
    team = json.dumps(team_data['teams'][0]['name'],
                      ensure_ascii=False).encode('utf8')
    team_name = team[1:-1]
    team_decoded = str(team_name.decode("utf8"))

    # setup formatting for table
    table = pt.PrettyTable(['Number', 'Full Name', 'Position'])
    table.align['Position'] = 'l'
    for player in roster:
        name = player['person']['fullName']
        number = int(player['jerseyNumber'])
        position = player['position']['name']
        table.add_row([number, name, position])
    table.title = 'Team Roster For The ' + team_decoded
    table.sortby='Number'

    return table