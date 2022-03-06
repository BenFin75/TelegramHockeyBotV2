import requests
import json
from dateutil.relativedelta import relativedelta

def season(todays_date):
    """
        checks if the nhl is currently in season by seening if there are any games this month
    """
    a_month_from_now = todays_date + relativedelta(months=1)
    json = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?startDate={todays_date}&endDate={a_month_from_now}').json()
    numofgame = json['totalItems']
    if numofgame == 0:
        return False
    else:
        return True

def postponed(teams_to_check, todays_date):
    playing_teams = []
    teams_list = teams_to_check.split(',')
    for team in teams_list:
        team_data = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?teamId={team}&date={todays_date}').json()
        if json.dumps(team_data['dates']) != '[]':
            postponed_check = str(json.dumps(
                team_data['dates'][0]['games'][0]['status']['detailedState']))
            if postponed_check != '"Postponed"':
                playing_teams.append(team)
    return playing_teams