from datetime import date

def message(todays_date):
    """
        Returns the days since the Flyers and the Penguins have won the cup
        Lets Go Pens!
    """

    flyers_Date = date(1975, 5, 27)
    flyers_delta_since_cup = flyers_Date - todays_date
    flyers_days_since_cup = str(flyers_delta_since_cup.days)[1:]

    pens_Date = date(2017, 6, 11)
    pens_delta_since_cup = pens_Date - todays_date
    pens_days_since_cup = str(pens_delta_since_cup.days)[1:]

    delta = flyers_delta_since_cup / pens_delta_since_cup

    message = ('Days since the Flyers won the cup:        ' + flyers_days_since_cup + '\n' +
               'Days since the Penguins won the cup:    ' + pens_days_since_cup + '\n' + 'thats ' + str(round(delta, 1)) + ' times longer, ' + 'Lets Go Pens!')
    
    return message
    