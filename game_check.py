import requests
import json
from datetime import datetime, timedelta

def check(number_of_teams, team_data, dst_check):
    """
    The core function for returning the game description
    for the teams being followed by the user
    /game and the automatic notifications use this funtion
    for sending messages
    """
    
    game_messages = []
    while number_of_teams > 0:
        number_of_teams = number_of_teams - 1

        # the encoding is so that Montréal has its é, can't forget that
        away_team = json.dumps(team_data['dates'][0]['games'][number_of_teams]
                               ['teams']['away']['team']['name'], ensure_ascii=False).encode('utf8')
        away_team_fin = away_team[1:-1]
        away_team_dec = str(away_team_fin.decode("utf8"))
        away_wins = json.dumps(
            team_data['dates'][0]['games'][number_of_teams]['teams']['away']['leagueRecord']['wins'])
        away_losses = json.dumps(
            team_data['dates'][0]['games'][number_of_teams]['teams']['away']['leagueRecord']['losses'])
        home_team = json.dumps(team_data['dates'][0]['games'][number_of_teams]
                               ['teams']['home']['team']['name'], ensure_ascii=False).encode('utf8')
        home_team_fin = home_team[1:-1]
        home_team_dec = str(home_team_fin.decode("utf8"))
        home_wins = json.dumps(
            team_data['dates'][0]['games'][number_of_teams]['teams']['home']['leagueRecord']['wins'])
        home_losses = json.dumps(
            team_data['dates'][0]['games'][number_of_teams]['teams']['home']['leagueRecord']['losses'])
        game_fulltime = json.dumps(
            team_data['dates'][0]['games'][number_of_teams]['gameDate'])
        game_time = game_fulltime[12:-2]
        if dst_check == True:
            game_time_obj = datetime.strptime(
                game_time, '%H:%M:%S') - timedelta(hours=4)
        if dst_check == False:
            game_time_obj = datetime.strptime(
                game_time, '%H:%M:%S') - timedelta(hours=5)
        game_time_est = datetime.strftime(game_time_obj, '%-I:%M%p')
        playoff_check = json.dumps(
            team_data['dates'][0]['games'][0]['gameType']).strip('\"')
        if playoff_check == 'P':

            away_wins_int = int(away_wins)
            home_wins_int = int(home_wins)
            away_games_won = away_wins_int % 4
            home_games_won = home_wins_int % 4
            if away_games_won > home_games_won:
                leading_team = away_team_dec
                leading_games = str(away_games_won)
                trailing_games = str(home_games_won)
            if away_games_won < home_games_won:
                leading_team = home_team_dec
                leading_games = str(home_games_won)
                trailing_games = str(away_games_won)

            tie_check = away_games_won - home_games_won
            if tie_check != 0:
                if leading_games == 1:
                    message = ("The " + home_team_dec + "\n" + "Host" + "\n" + "The " + away_team_dec + "\n" + "At " + game_time_est + " est!" + "\n" +
                                      "The " + leading_team + " Lead " + leading_games + " game to " + trailing_games + "!")
                else:
                    message = ("The " + home_team_dec + "\n" + "Host" + "\n" + "The " + away_team_dec + "\n" + "At " + game_time_est + " est!" + "\n" +
                                      "The " + leading_team + " Lead " + leading_games + " games to " + trailing_games + "!")
                game_messages.append(message)

            if tie_check == 0:
                home_games_won_str = str(home_games_won)
                if home_games_won == 1:
                    message = ("The " + home_team_dec + "\n" + "Host" + "\n" + "The " + away_team_dec + "\n" + "At " + game_time_est + " est!" + "\n" +
                                      "The series is tied at " + home_games_won_str + " game!")
                else:
                    message = ("The " + home_team_dec + "\n" + "Host" + "\n" + "The " + away_team_dec + "\n" + "At " + game_time_est + " est!" + "\n" +
                                      "The series is tied at " + home_games_won_str + " games!")
                game_messages.append(message)
        if playoff_check == 'R':
            away_ot = json.dumps(
                team_data['dates'][0]['games'][number_of_teams]['teams']['away']['leagueRecord']['ot'])
            home_ot = json.dumps(
                team_data['dates'][0]['games'][number_of_teams]['teams']['home']['leagueRecord']['ot'])
            message = ("The " + home_team_dec + " (" + home_wins + "," + home_losses + "," + home_ot + ")" + "\n" + "Host" + "\n" + "The " + away_team_dec + " (" + away_wins +
                              "," + away_losses + "," + away_ot + ")" + "\n" + "at " + game_time_est + " est!")
            game_messages.append(message)
            
    return game_messages