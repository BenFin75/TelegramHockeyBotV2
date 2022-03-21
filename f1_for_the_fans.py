from xml.etree.ElementInclude import include
import prettytable as pt
import json
from datetime import datetime, timedelta

import api_checks

def next(todays_date, dst_check):
  todays_date = str(todays_date)
  parsed_data = api_checks.f1_current('')
  next_data = parsed_data["MRData"]['RaceTable']['Race']
  
  for race in next_data:
    race_date = race['Date']
    if race_date >= todays_date:
      track_name = race['Circuit']['CircuitName']
      start_time = json.dumps(race['Time'])
      start_time = start_time[1:9]
      if dst_check == True:
          start_time_obj = datetime.strptime(
              start_time, '%H:%M:%S') - timedelta(hours=4)
      if dst_check == False:
          start_time_obj = datetime.strptime(
              start_time, '%H:%M:%S') - timedelta(hours=5)
      start_time_est = datetime.strftime(start_time_obj, '%-I:%M%p')
      
      race_day_obj = datetime.strptime(race_date, '%Y-%m-%d')
      race_day_str = datetime.strftime(race_day_obj, '%d')
      race_day_of_week = datetime.strftime(race_day_obj, '%A')
      race_day_int = int(race_day_str)
      race_day_txt = str(race_day_int)

      if 4 <= race_day_int <= 20 or 24 <= race_day_int <= 30:
        race_day_txt += "th"
      else:
        race_day_txt += ["st", "nd", "rd"][race_day_int % 10 - 1]
          
      race_month = race_day_obj.strftime("%B")
          
      
      message = f"The next F1 race is at {track_name}" + '\n' + '\n' + f"The race starts at {start_time_est} on {race_day_of_week} the {race_day_txt} of {race_month}"
      
      return message


def last():
  parsed_data = api_checks.f1_current('/last/results')
  last_data = parsed_data["MRData"]
  
  race_number = last_data['RaceTable']['@round']
  gp = last_data['RaceTable']['Race']['RaceName']
  track = last_data['RaceTable']['Race']['Circuit']['CircuitName']
  drivers = last_data['RaceTable']['Race']['ResultsList']['Result']
  
  table = pt.PrettyTable()

  table.title = f'{gp} at {track} race #: {race_number}'
  table.field_names = ['Pos.', 'Driver', 'Team', 'Grid pos.', 'Laps', 'Fastest Lap', 'Points']
  table.align['Driver Name'] = "l"
  table.align['Team'] = "l"
  table.align['Fastest Lap'] = "r"
  table.align['Points'] = "r"
  
  for driver in drivers:
    position = driver['@positionText']
    name = driver['Driver']['FamilyName']
    team = driver['Constructor']['Name']
    if " F1 Team" in team:
      team = team.replace(' F1 Team', '')
    grid = driver['Grid']
    laps = driver['Laps']
    fastest = driver['FastestLap']['Time']
    fastest_rank = driver['FastestLap']['@rank']
    if fastest_rank == '1':
      fastest = '* ' + fastest
    points = driver['@points']
  
    table.add_row([position, name, team, grid, laps, fastest, points])
  
  return table

def standings():
  
  parsed_data = api_checks.f1_current('/driverStandings')
  standings_data = parsed_data["MRData"]['StandingsTable']
    
  table = pt.PrettyTable()

  season = standings_data['@season']
  table.title = f'{season} Season Standings'
  table.field_names = ['Pos.', 'Driver Name', 'Team', 'Points', 'Wins']
  table.align['Driver Name'] = "l"
  table.align['Team'] = "l"
  table.align['Points'] = "r"
  table.align['Wins'] = "r"
  
  for driver in standings_data['StandingsList']['DriverStanding']:
    
    position = driver['@position']
    fname = driver['Driver']['GivenName']
    lname = driver['Driver']['FamilyName']
    full_name = fname + ' ' + lname
    team = driver['Constructor']['Name']
    if " F1 Team" in team:
      team = team.replace(' F1 Team', '')
    points = driver['@points']
    wins = driver['@wins']
    
    table.add_row([position, full_name, team, points, wins])
  
  return table