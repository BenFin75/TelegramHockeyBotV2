import pandas as pd

from standings import build_message

def message(chatid, chat_database, teams_database):

    chats_dataframe = pd.read_csv(chat_database)
    team_names_dataframe = pd.read_csv(teams_database, encoding="ISO-8859-1")
    users_team_ids = list(chats_dataframe.loc[chats_dataframe['ChatID'] == chatid, 'TeamIDs'].values)
    users_team_ids_formatted = str(users_team_ids)[2:-2]
    list_of_users_team_ids = [int(x) for x in users_team_ids_formatted.split(',')]
    formatted_teams_df = team_names_dataframe.loc[team_names_dataframe['Formatted'] == 1]

    if users_team_ids == []:
        return_message = "You have no data, please run /setup first!"
    else:
        return_message = build_message(list_of_users_team_ids, formatted_teams_df, chats_dataframe, chatid)
    
    return return_message

def build_message(list_of_users_team_ids, formatted_teams_df, chats_dataframe, chatid):
    users_teams = ''
    teams_list = ''
    while len(list_of_users_team_ids) > 0:
        team = list_of_users_team_ids[0]
        users_teams = formatted_teams_df.loc[formatted_teams_df['TeamID'] == team, 'TeamName'].values
        teams_list = teams_list + users_teams + '?The '
        list_of_users_team_ids.remove(team)
    user_notification_status = chats_dataframe.loc[chats_dataframe['ChatID']
                               == chatid, 'Notifications'].values
    if user_notification_status == 0:
        notification_status = 'are not'
    if user_notification_status == 1:
        notification_status = 'are'
    finalteamslist = str(teams_list)[2:-7]
    
    return 'You are following:' + '\n' + 'The ' + finalteamslist.replace('?', '\n') + '\n' + '\n' + 'You ' + notification_status + ' receiving daily notifications.'