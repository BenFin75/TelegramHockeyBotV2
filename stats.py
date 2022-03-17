import prettytable as pt
import pandas as pd
import json

import database_functions
import api_checks

def message(user_request, teams_database):

    #check if the request is valid
    if len(user_request) == 0:
        return_message = "Please indicate a team and/or player." + '\n' + "e.g. /stats Pens " + " "*3 + "or" + " " * 3 + "/stats Pens Crosby"
    elif user_request.count(' ') > 2:
        return_message = "One player or team at a time please."
    else:
        team_name, player_info, teamstats = parse_request(user_request, teams_database)
    
        # send parsed data to have the response be built
        if not database_functions.team_check(team_name, teams_database):
            return_message = "Sorry I don't know that team."
        elif teamstats == 0:
            return_message = player_request(team_name, player_info, teams_database)
        else:
            return_message = team_request(team_name, teams_database)

    return return_message

# if the request if valid parse the request and build a response
def parse_request(user_request, teams_database):

    # split out message based on how the request was worded
    if user_request.count(' ') == 2:
        team_name, fname, lname = user_request.split(' ')
        player_info = fname + ' ' + lname
        teamstats = 0
    if user_request.count(' ') == 1:
        team_name, player_info = user_request.split(' ')
        teamstats = 0
    if user_request.count(' ') == 0:
        player_info = ''
        team_name = user_request
        teamstats = 1
    
    return [team_name, player_info, teamstats]


#if a player's stats are requested
def player_request(team_name, player_info, teams_database):
    teamdf = pd.read_csv(teams_database, index_col=None)
    teamID = int(teamdf.loc[teamdf.TeamName == team_name, 'TeamID'])

    if player_info.isnumeric():
        player_info = int(player_info)

    player_data = api_checks.team_call(f'{teamID}?expand=team.roster')

    team = json.dumps(
        player_data['teams'][0]['name'], ensure_ascii=False).encode('utf8')
    team_name = team[1:-1]
    team_decoded = str(team_name.decode("utf8"))

    if not check_if_player_exists(player_data, player_info):
        player_info = str(player_info)
        if player_info.isnumeric():
            message = 'I cant find number ' + player_info + ' on The ' + team_decoded
        else:
            player_name = player_info.title()
            message = 'I cant find anyone named ' + player_name + ' on The ' + team_decoded
        return message

    else:
        player_id, player_name, position = check_if_player_exists(player_data, player_info)
        return build_response(player_id, player_name, position)


def check_if_player_exists(player_data, player_info):
    for n in player_data['teams'][0]['roster']['roster']:
        number = int(n['jerseyNumber'])
        name = n['person']['fullName']
        first, last = name.split(' ')
        if number == player_info or first.lower() == player_info or last.lower() == player_info or name.lower() == player_info:
            player_id = n['person']['id']
            player_name = n['person']['fullName']
            position = n['position']['code']
            return [player_id, player_name, position]
    return False


def build_response(player_id, player_name, position):

    player_stats = api_checks.player_call(f'{player_id}/stats?stats=statsSingleSeason')
    
    if position == "G":
        table = pt.PrettyTable(
            ['Games Played', 'Games Started', 'Wins', 'Losses',
                'Shutouts', 'Save %', 'Average Goals Against']
        )

        games = player_stats['stats'][0]['splits'][0]['stat']['games']
        games_started = player_stats['stats'][0]['splits'][0]['stat']['gamesStarted']
        wins = player_stats['stats'][0]['splits'][0]['stat']['wins']
        regulation_losses = player_stats['stats'][0]['splits'][0]['stat']['losses']
        ot_losses = player_stats['stats'][0]['splits'][0]['stat']['ot']
        shutouts = player_stats['stats'][0]['splits'][0]['stat']['shutouts']
        save_pct = player_stats['stats'][0]['splits'][0]['stat']['savePercentage']
        goals_against_avg = player_stats['stats'][0]['splits'][0]['stat']['goalAgainstAverage']
        full_losses = str(int(regulation_losses) + int(ot_losses))

        table.add_row(
            [games, games_started, wins, full_losses, shutouts, save_pct, goals_against_avg]
        )
        table.title = player_name + "'s Regular Season Stats"
    else:
        table = pt.PrettyTable(
            ['Games Played', 'Goals', 'Assists',
                'Points', 'Penalty Minutes', '+/-']
            )

        games = player_stats['stats'][0]['splits'][0]['stat']['games']
        goals = player_stats['stats'][0]['splits'][0]['stat']['goals']
        assists = player_stats['stats'][0]['splits'][0]['stat']['assists']
        points = player_stats['stats'][0]['splits'][0]['stat']['games']
        penalty_minutes = player_stats['stats'][0]['splits'][0]['stat']['pim']
        plus_minus = player_stats['stats'][0]['splits'][0]['stat']['plusMinus']

        if int(plus_minus) > 0:
            plus_minus = '+' + str(plus_minus)
        table.add_row(
            [games, goals, assists, points, penalty_minutes, plus_minus]
        )
        table.title = player_name + "'s Regular Season Stats"

    return table

# if a team's stats are requested
def team_request(team_name, teams_database):

    team_dataframe = pd.read_csv(teams_database, index_col=None)
    team_id = int(team_dataframe.loc[team_dataframe.TeamName == team_name, 'TeamID'])

    team_data = api_checks.team_call(f'{team_id}/stats')
    
    team = json.dumps(team_data['stats'][0]['splits'][0]
                        ['team']['name'], ensure_ascii=False).encode('utf8')
    team_name = team[1:-1]
    team_name_decoded = str(team_name.decode("utf8"))

    games_played = json.dumps(team_data['stats'][0]['splits'][0]['stat']['gamesPlayed'])
    wins = json.dumps(team_data['stats'][0]['splits'][0]['stat']['wins'])
    losses = json.dumps(team_data['stats'][0]['splits'][0]['stat']['losses'])
    ot_losses = json.dumps(team_data['stats'][0]['splits'][0]['stat']['ot'])
    points = json.dumps(team_data['stats'][0]['splits'][0]['stat']['pts'])


    team_standings = api_checks.standings_call()

    for n in team_standings['records']:
        for x in n['teamRecords']:
            team_id = x['team']['id']
            if int(team_id) == team_id:
                division = n['division']['name']
                standing = x['divisionRank']
                
    table = pt.PrettyTable(
    ['Games Played', 'Wins', 'Losses', 'OT Losses',
        'Points', 'Division', 'Standings']
    )
    table.add_row(
        [games_played, wins, losses, ot_losses, points, division, standing]
    )
    table.title = 'The ' + team_name_decoded + "'s Regular Season Stats"

    return table