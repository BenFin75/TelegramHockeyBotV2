from handle_messages import send

def command(updater):
    """
        stop the bot through a telegram command
    """
    updater.stop()
    updater.is_idle = False