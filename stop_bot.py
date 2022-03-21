from handle_messages import send

def command(update, updater, admin_chat_id):
    """
        stop the bot through a telegram command
    """
    if update.effective_chat.id == admin_chat_id:
        send(admin_chat_id, 'Shuting Down')
        updater.stop()
        updater.is_idle = False