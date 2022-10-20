def message():

    """
        Help command giving a list of the bots command, what they do, and how to use them
    """
    help_message = (
        "Here is a list of my commands:" + "\n" + "\n" +
        "/setup" + "\n" + "select which teams you would like notifications for" + "\n" + "\n" +
        "/game" + "\n" + "manually check if a team you selected has a game today" + "\n" + "\n" +
        "/nextgame <team name>" + "\n" + "find the time of the next game for a team. e.g. /nextgame Penguins" + "\n" + "\n" +
        "/lastgame <team name>" + "\n" + "find the score of the last game for a team. e.g /lastgame Penguins" + "\n" + "\n" +
        "/notifications" + "\n" + "enable and disable daily game notifications" + "\n" + "\n" +
        "/status" + "\n" + "get a list of the teams you are following" + "\n" + "and your notification preferences" + "\n" + "\n" +
        "/roster <team name>" + "\n" + "get the active roster for a given team e.g /roster Penguins" + "\n" + "\n" +
        "/player <team name> <player>" + "\n" + "get the numer, full name, and position for a player" + "\n" + " e.g /player Penguins 87 or /player Penguins Crosby" + "\n" + "\n" +
        "/stats <team name>" + "\n" + "/stats <team name> <player>" + "\n" + "get the regular season stats for a given team or player" + "\n" + " e.g /stats Penguins, /stats Penguins 87, or /stats Penguins Crosby" + "\n" + "\n" +
        "/standings <division name>" + "\n" + "get the standings for a given division e.g /standings Pacific" + "\n" + "If left blank /standings will retrun all division stnadings" "\n" + "\n" +
        "/cupcheck" + "\n" + "Important stats" + "\n" + "\n" +
        "/f1next" + "\n" + "get date and location of next F1 race" + "\n" + "\n" +
        "/f1last" + "\n" + "get the results of the last F1 race" + "\n" + "\n" +
        "/f1standings" + "\n" + "get the season standings for F1" + "\n" + "\n" +
        "/removeMe" + "\n" + "Delete your teams and notification data." + "\n" + "\n" +
        "/help" + "\n" + "opens this list of commands" + "\n" + "\n" +
        "Thank you for using my bot!" + "\n" + "\n" +
        "Made by Ben Finley" + "\n" +
        "The code for this bot is avalible at: https://github.com/BenFin75/TelegramNHLNotifcationBot"
    )
    return help_message