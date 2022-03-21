import requests
import json
import xmltodict
from dateutil.relativedelta import relativedelta

def schedule_call(url_ending):
    base_url = f'https://statsapi.web.nhl.com/api/v1/schedule?'
    final_url = base_url + url_ending
    request = requests.get(final_url)
    json = request.json()
    return json

def team_call(url_ending):
    base_url = f'https://statsapi.web.nhl.com/api/v1/teams/'
    final_url = base_url + url_ending
    request = requests.get(final_url)
    json = request.json()
    return json

def game_call(url_ending):
    base_url = f'https://statsapi.web.nhl.com/api/v1/game/'
    final_url = base_url + url_ending
    request = requests.get(final_url)
    json = request.json()
    return json

def player_call(url_ending):
    base_url = f'https://statsapi.web.nhl.com/api/v1/people/'
    final_url = base_url + url_ending
    request = requests.get(final_url)
    json = request.json()
    return json


def standings_call():
    final_url = f'https://statsapi.web.nhl.com/api/v1/standings'
    request = requests.get(final_url)
    json = request.json()
    return json


def f1_current(url_ending):
    base_url = f'http://ergast.com/api/f1/current'
    final_url = base_url + url_ending
    request = requests.get(final_url)
    json = xmltodict.parse(request.content)
    return json

def season(todays_date):
    """
        checks if the nhl is currently in season by seening if there are any games this month
    """
    a_month_from_now = todays_date + relativedelta(months=1)
    json = schedule_call(f'startDate={todays_date}&endDate={a_month_from_now}')
    numofgame = json['totalItems']
    if numofgame == 0:
        return False
    else:
        return True

def postponed(teams_to_check, todays_date):
    playing_teams = []
    teams_list = teams_to_check.split(',')
    for team in teams_list:
        team_data = schedule_call(f'teamId={team}&date={todays_date}')
        if json.dumps(team_data['dates']) != '[]':
            postponed_check = str(json.dumps(
                team_data['dates'][0]['games'][0]['status']['detailedState']))
            if postponed_check != '"Postponed"':
                playing_teams.append(team)
    return playing_teams