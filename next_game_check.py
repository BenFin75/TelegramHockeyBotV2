import pandas as pd
import json
from datetime import datetime, timedelta, date


todays_date = date.today()

import database_functions
import api_checks



def message(user_request, teams_database, time_zone, utc_tz, todays_date):
    if len(user_request) == 0:
        return_message = "Please indicate the team you want the next game for." + '\n' + "e.g. /nextgame Pens"

    else:
        if not database_functions.team_check(user_request, teams_database):
            return_message = "Sorry I don't know that team."
        else:
            team_dataframe = pd.read_csv(teams_database, index_col=None)
            team_id = int(team_dataframe.loc[team_dataframe.TeamName == user_request, 'TeamID'].values)
            next_game = api_checks.team_call(f'{team_id}?expand=team.schedule.next')
            last_game = api_checks.team_call(f'{team_id}?expand=team.schedule.previous')

            playoff_check = json.dumps(
                last_game['teams'][0]['previousGameSchedule']['dates'][0]['games'][0]['gameType']).strip('\"')
            elimcheck = json.dumps(next_game['teams'][0])

            if not api_checks.season(todays_date):
                return_message = ("The NHL season has ended, come back next year!")
            elif 'nextGameSchedule' not in elimcheck:
                return_message = eliminated(team_dataframe, team_id, last_game, playoff_check)
            else:
                return_message = build_message(next_game,  time_zone, utc_tz)

    return return_message

def eliminated(team_dataframe, team_id, last_game, playoff_check):
    formatted_teams_df = team_dataframe.loc[team_dataframe['Formatted'] == 1]
    teamid_name_form = str(
        formatted_teams_df.loc[formatted_teams_df.TeamID == team_id, 'TeamName'].values).strip("'[]")
    away_team_score = int(json.dumps(
        last_game['teams'][0]['previousGameSchedule']['dates'][0]['games'][0]['teams']['away']['score']))
    home_team_score = int(json.dumps(
        last_game['teams'][0]['previousGameSchedule']['dates'][0]['games'][0]['teams']['home']['score']))
    away_team_id = int(json.dumps(
        last_game['teams'][0]['previousGameSchedule']['dates'][0]['games'][0]['teams']['away']['team']['id']))
    home_team_id = int(json.dumps(
        last_game['teams'][0]['previousGameSchedule']['dates'][0]['games'][0]['teams']['home']['team']['id']))
    if away_team_score > home_team_score and away_team_id == team_id and playoff_check == 'P' or home_team_score > away_team_score and home_team_id == team_id and playoff_check == 'P':
        message = (
            "The " + teamid_name_form + " have won their playoff series." + "\n" + "The next game has yet to be scheduled." + "\n" + "\n" +
            "This is probably due to the next opponent still playing their series." + "\n" +
            "Please check back later."
        )
    else:
        message = ("Ha, The " + teamid_name_form + " have been eliminated from Stanley Cup Contention. Sucks to suck")
    return message

def build_message(next_game, time_zone, utc_tz):
    # the encoding is so that Montréal has its é, can't forget that
    away_team = json.dumps(next_game['teams'][0]['nextGameSchedule']['dates'][0]['games']
                           [0]['teams']['away']['team']['name'], ensure_ascii=False).encode('utf8')
    away_team_name = away_team[1:-1]
    away_team_decoded = str(away_team_name.decode("utf8"))
    away_wins = json.dumps(next_game['teams'][0]['nextGameSchedule']
                           ['dates'][0]['games'][0]['teams']['away']['leagueRecord']['wins'])
    away_losses = json.dumps(next_game['teams'][0]['nextGameSchedule']
                             ['dates'][0]['games'][0]['teams']['away']['leagueRecord']['losses'])
    home_team = json.dumps(next_game['teams'][0]['nextGameSchedule']['dates'][0]['games']
                           [0]['teams']['home']['team']['name'], ensure_ascii=False).encode('utf8')
    home_team_fin = home_team[1:-1]
    home_team_dec = str(home_team_fin.decode("utf8"))
    home_wins = json.dumps(next_game['teams'][0]['nextGameSchedule']
                           ['dates'][0]['games'][0]['teams']['home']['leagueRecord']['wins'])
    home_losses = json.dumps(next_game['teams'][0]['nextGameSchedule']
                             ['dates'][0]['games'][0]['teams']['home']['leagueRecord']['losses'])
    game_fulltime = json.dumps(
        next_game['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['gameDate'])
    game_day_full = json.dumps(
        next_game['teams'][0]['nextGameSchedule']['dates'][0]['date'])
    game_day = game_day_full[1:-1]
    game_day_obj = datetime.strptime(game_day, '%Y-%m-%d')
    game_day_str = datetime.strftime(game_day_obj, '%d')
    game_day_int = int(game_day_str)
    game_day_txt = str(game_day_int)
    game_day_of_week = datetime.strftime(game_day_obj, '%A')
    game_fulltime = game_fulltime.replace('"', '')
    game_fulltime = game_fulltime.replace('T', ' ')
    game_fulltime = game_fulltime.replace('Z', '')
    game_time_obj = datetime.fromisoformat(game_fulltime).replace(tzinfo=utc_tz)
    game_time_est = game_time_obj.astimezone(time_zone).strftime('%#I:%M%p')    

    if 4 <= game_day_int <= 20 or 24 <= game_day_int <= 30:
        game_day_txt += "th"
    else:
        game_day_txt += ["st", "nd", "rd"][game_day_int % 10 - 1]

    playoff_check = json.dumps(
        next_game['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['gameType']).strip('\"')
    if playoff_check == 'P':
        away_games_won = int(away_wins) % 4
        home_games_won = int(home_wins) % 4
        if away_games_won > home_games_won:
            leading_team = away_team_decoded
            leading_games = str(away_games_won)
            trailing_games = str(home_games_won)
        if away_games_won < home_games_won:
            leading_team = home_team_dec
            leading_games = str(home_games_won)
            trailing_games = str(away_games_won)
        tie_check = away_games_won - home_games_won
        if tie_check != 0:
            if leading_games == 1:
                message = ("The " + home_team_dec + "\n" + "Host" + "\n" + "The " + away_team_decoded + "\n" + game_day_of_week + " the " + game_day_txt + " at " + game_time_est + " est!" + "\n"
                                       + "The " + leading_team + " Lead " + leading_games + " game to " + trailing_games + "!")
            else:
                message = ("The " + home_team_dec + "\n" + "Host" + "\n" + "The " + away_team_decoded + "\n" + game_day_of_week + " the " + game_day_txt + " at " + game_time_est + " est!" + "\n"
                                       + "The " + leading_team + " Lead " + leading_games + " games to " + trailing_games + "!")

        if tie_check == 0:
            home_games_won_str = str(home_games_won)
            if home_games_won == 1:
                message = ("The " + home_team_dec + "\n" + "Host" + "\n" + "The " + away_team_decoded + "\n" + game_day_of_week + " the " + game_day_txt + " at " + game_time_est + " est!" + "\n"
                                       + "The series is tied at " + home_games_won_str + " game!")
            else:
                message = ("The " + home_team_dec + "\n" + "Host" + "\n" + "The " + away_team_decoded + "\n" + game_day_of_week + " the " + game_day_txt + " at " + game_time_est + " est!" + "\n"
                                       + "The series is tied at " + home_games_won_str + " games!")

    elif playoff_check == 'R':
        away_ot = json.dumps(next_game['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['away']['leagueRecord']['ot'])
        home_ot = json.dumps(next_game['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['home']['leagueRecord']['ot'])

        message = ("The " + home_team_dec + " (" + home_wins + "," + home_losses + "," + home_ot + ")" + "\n" + "Host" + "\n" + "The " + away_team_decoded + " (" + away_wins +
                               "," + away_losses + "," + away_ot + ")" + "\n" + game_day_of_week + " the " + game_day_txt + " at " + game_time_est + " est!")
    
    return message

