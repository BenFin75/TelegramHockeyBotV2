import requests
import json

todays_date = '2022-03-08'

todays_games = requests.get(f'https://statsapi.web.nhl.com/api/v1/schedule?date={todays_date}').json()
for game in todays_games['dates'][0]['games']:
    team_name = game['teams']['away']['team']['name']
    print(team_name)
