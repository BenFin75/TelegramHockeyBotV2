import pandas as pd

def team_check(team_name, teams_database):
    """
        Sends a message if the user submits an unsupported team name
    """
    team_dataframe = pd.read_csv(teams_database, index_col=None)
    if team_name not in team_dataframe.TeamName.values:
        return False
    else:
        return True

def update_teams (chat_database, chatname, team_ids, userid):

    chats_dataframe = pd.read_csv(chat_database)
    exists = userid in chats_dataframe.ChatID.values
    string_of_team_ids = ','.join(team_ids)

    if exists is True:
        chat_index = chats_dataframe.index[chats_dataframe['ChatID'] == userid]
        chats_dataframe.loc[chat_index, 'TeamIDs'] = string_of_team_ids
        chats_dataframe.to_csv(chat_database, index=False, header=True)
    if exists is False:
        newchat_dataframe = pd.DataFrame({"ChatName": [chatname], "ChatID": [
                                 userid], "TeamIDs": [string_of_team_ids]})
        updated_dataframe = chats_dataframe.append(newchat_dataframe, ignore_index=True)
        updated_dataframe.to_csv(chat_database, index=False, header=True)

    
def update_notifications (chat_database, userid, notification_prefrence):
    chats_dataframe = pd.read_csv(chat_database)
    chat_index = chats_dataframe.index[chats_dataframe['ChatID'] == userid]
    chats_dataframe.loc[chat_index, 'Notifications'] = notification_prefrence
    chats_dataframe.to_csv(chat_database, index=False, header=True)