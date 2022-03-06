def seasoncheck(chat_id_set, autonotify):
    """
        checks if the nhl is currently in season by seening if there are any games this month
    """
    a_month_from_now = todays_date + relativedelta(months=1)
    api_url = f'https://statsapi.web.nhl.com/api/v1/schedule?startDate={todays_date}&endDate={a_month_from_now}'
    r = requests.get(api_url)
    json = r.json()
    numofgame = json['totalItems']
    if numofgame == 0:
        if autonotify == 1:
            return False
        else:
            game_check_msg = ("The NHL season has ended, come back next year!")
            updater.bot.sendMessage(chat_id=chat_id_set, text=game_check_msg)
            return False
    else:
        return True