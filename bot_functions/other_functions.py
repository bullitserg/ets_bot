from datetime import datetime


# получение диапазона для запроса mysql вида "2017-07-01 00:00:00" AND "2017-08-31 23:59:59" (прошлый квартал)
def last_decade_for_mysql():
    year = datetime.date(datetime.now()).year
    month = datetime.date(datetime.now()).month

    if month == 1:
        year, start_decade, end_decade = year - 1, '10', '12'
    elif 2 <= month <= 4:
        year, start_decade, end_decade = year, '01', '03'
    elif 5 <= month <= 7:
        year, start_decade, end_decade = year, '04', '06'
    elif 8 <= month <= 10:
        year, start_decade, end_decade = year, '07', '09'
    elif 11 <= month <= 12:
        year, start_decade, end_decade = year, '10', '12'
    else:
        raise Exception('Bad month: %s' % month)

    return '''"%s-%s-01 00:00:00" AND "%s-%s-31 23:59:59"''' % (year, start_decade, year, end_decade)


