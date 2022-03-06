def command(update, context, updater, admin_chat_id):
    """
        stop the bot through a telegram command
    """
    print(update.effective_chat.id)
    if update.effective_chat.id == admin_chat_id:
        updater.bot.sendMessage(
            chat_id=update.effective_chat.id, text='Shuting Down')
        updater.stop()
        updater.is_idle = False