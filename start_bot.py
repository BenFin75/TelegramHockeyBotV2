def message():
    
    """
        Welcome message explaining the bot.
        The /start command is sent automatically whenever a user begins a new converstation with the bot
        it can also be called at anytiem with the /start command
    """
    welcome_message = (
        "Hello!  Welcome to the NHL game notifications bot!" + "\n" + "\n" +
        "Type /setup to get started, or /help for a list of commands." + "\n" + "\n" +
        "Made by Ben Finley" + "\n" +
        "The code for this bot is avalible at: https://github.com/BenFin75/TelegramNHLNotifcationBot"
    )   

    return welcome_message