import requests
import prettytable as pt

def message(user_request):

    # get the division standings from API
    standings = requests.get('https://statsapi.web.nhl.com/api/v1/standings').json()
    
    #initiate return_message as a list so it can be appended to
    return_message = []

    # if no division is specified return all divisions
    if len(user_request) == 0:
        for n in standings['records']:
            division_name = n['division']['name'].lower()
            return_message.append(build_table(division_name, standings))

    # if division is specified create response
    else:
        return_message = build_message(user_request, standings)

    return return_message

def build_message (user_request, standings):
    """
        Check if the user submitted a valid request
    """
    
    # if multiple division were requested
    if user_request.count(' ') >= 1:
        return "One division at a time please."

    # check if the division requested is valid
    found = 0
    for n in standings['records']:
        division = n['division']['name'].lower()
        if user_request == 'metro':
            user_request = 'metropolitan'
        if division == user_request:
            found = 1

    # if valid build the response table
    if (found == 1):
        return build_table(user_request, standings)

    # if invalid return message that it is invalid
    else:
        return "That is not a division I know." + "\n" + "The divisions are Central, Metropolitan, Pacific, and Atlantic"

# build response table
def build_table(user_request, standings):
    """
        Returns the regular season standings
        for a given division or for all divisions
    """
    for n in standings['records']:
        division = n['division']['name'].lower()
        if division == user_request:
            
            table = pt.PrettyTable(
                ['Standings', 'Teams', 'Points', 'Wins', 'Losses', 'OT Losses']
            )
            table.title = division.title() + ' Division Standings'
            for x in n['teamRecords']:
                standings = x['divisionRank']
                team_name = x['team']['name']
                points = x['points']
                wins = x['leagueRecord']['wins']
                losses = x['leagueRecord']['losses']
                ot_losses = x['leagueRecord']['ot']
                table.add_row(
                    [standings, team_name, points, wins, losses, ot_losses]
                )
            return table
