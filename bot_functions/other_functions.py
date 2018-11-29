from datetime import datetime
from config import ds_log_file
from os.path import normpath


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


def write_ds_log(operation_type, user, chat_id, procedure_number, request_id,  inn, amount, account, bank_id, guid):
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(normpath(ds_log_file), mode='a', encoding='utf8') as o_ds_log:
        o_ds_log.write('%s | %-9s > %s %-12s %-12s # user: %s, chat: %s, request_id: %s, account: %s, bank_id: %s # %s\n' %
                       (date, operation_type, procedure_number, inn, amount, user, chat_id,
                        request_id, account, bank_id, guid))





