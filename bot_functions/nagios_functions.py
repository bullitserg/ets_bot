from config import *
import requests as requests
import re
import os
import sys
from functools import reduce
from itertools import count, cycle
import lxml.html as html
from collections import OrderedDict


def nagios_error_class_list(html_file, class_name):
    """Функция для получения листа ошибок по классу ошибки"""
    """
    Пример вывода
    [{
    'host': 'sng2-etp',
    'attempt': '2/2',
    'duration': '0d 14h 59m 47s',
    'service': 'Check BFT Integration',
    'statusInformation': 'bft-integration problem. The record is not exist.',
    'lastCheck': '09-22-2017 08:23:54'}]
    """

    def list_from_indexes_and_period(in_list, *indexes, period=2):
        """Функция выделяет из набора данных значения по индексу в заданном порядке, в рамках определенного периода
        in_list -- входящий лист данных
        indexes -- индексы через запятую (с 1) в требуемом порядке
        period -- длина периода обработки (по умолчанию period=2)
        Результатом функции является набор вида [[2,3],[5,6],...]
        """
        in_list = list(in_list)
        in_list_len = len(in_list)
        if not in_list_len % period == 0:
            raise Exception('Недопустимый период %s для листа длиной %s' % (period, in_list_len))
        for index in indexes:
            if index > period:
                raise Exception('Индекс=%s выходит за пределы периода %s' % (index, period))

        out_list = []
        while in_list:
            period_list = map(lambda index: in_list[index - 1], indexes)
            out_list.append(list(period_list))
            in_list = in_list[period:]

        return out_list

    # переход в домашнюю директорию
    os.chdir(os.path.realpath(os.path.dirname(sys.argv[0])))

    # Скачиваем страницу и кладем ее в файл _nagios_local_page
    nagios_web_page_file = requests.get(nagios_web_page, auth=(nagios_login, nagios_password))
    with open(nagios_local_page, mode='wb') as web_str:
        web_str.write(nagios_web_page_file.content)
    # функция для разбора страницы нагиос на лист со словарем данных
    # парсим странички
    page = html.parse(html_file)
    class_root = page.getroot().find_class(class_name)

    # отбор строк с нужным классом из всех строк
    separated_class_lists = list_from_indexes_and_period(class_root, 2, 4, 5, 6, 7, period=7)
    # лист для записи всех проблемных метрик
    class_out_list = []
    for critical_list in separated_class_lists:
        # лист для метрики
        class_metric_list = []
        for class_data in critical_list:
            # находим и добавляем название сервера в лист
            for iterData in class_data.iterlinks():
                class_metric_list.append(re.search('host=(.*)&', iterData[2]).group(1))
            class_metric_list.append(class_data.text_content())
        # добавляем список по метрике в criticalOutList
        class_out_list.append(class_metric_list)

    # Формируем лист со словарями
    class_dict_list = []
    for class_data in class_out_list:
        service_dict = OrderedDict([
            ('host', class_data[0].strip()),
            ('service', class_data[1].strip()),
            ('last_check', class_data[2].strip()),
            ('duration', class_data[3].strip()),
            ('attempt', class_data[4].strip()),
            ('status_information', re.sub(r'\xa0', '', class_data[5])
             .encode('ISO-8859-1', errors='ignore')
             .decode(errors='ignore'))
        ])
        class_dict_list.append(service_dict)

    # собираем конечный набор
    class_out_dict_list = [dict for dict in class_dict_list
                           # если не указано игнорировать хост
                           if (dict['host'] not in bad_hosts
                               # если не указано игнорировать сервис
                               and dict['service'] not in bad_service
                               )]
    return class_out_dict_list


def get_nagios_info(**kwargs):
    # 'both', 'warning', 'critical'
    bot_answer = ''
    separator = ') ========================='

    mode = kwargs.get('mode', 'both')

    def create_answer_part(n_list):
        counter = count(start=1, step=1)
        answer_part = ''
        for metric in n_list:
            d = str(next(counter)) + separator + '\n' + \
                reduce(lambda x, y: x + '\n' + y,
                       map(lambda x: x.capitalize().replace('_', ' ') + ': ' + metric[x], metric)
                       ) + '\n'
            answer_part += d
        return answer_part

    if mode == 'critical':
        data = nagios_error_class_list(nagios_local_page, critical_class)
        if data:
            bot_answer += '========== CRITICAL ==========\n' + create_answer_part(data)
        else:
            bot_answer += 'Ошибки отсутствуют'

    elif mode == 'warning':
        data = nagios_error_class_list(nagios_local_page, warning_class)
        if data:
            bot_answer += '=========== WARNING ==========\n' + create_answer_part(data)
        else:
            bot_answer += 'Ошибки отсутствуют'

    else:
        data = nagios_error_class_list(nagios_local_page, critical_class)
        if data:
            bot_answer += '========== CRITICAL ==========\n' + create_answer_part(data)
        else:
            bot_answer += 'Критические ошибки отсутствуют'
        bot_answer += '\n'
        data = nagios_error_class_list(nagios_local_page, warning_class)
        if data:
            bot_answer += '=========== WARNING ==========\n' + create_answer_part(data)
        else:
            bot_answer += 'Предупреждения отсутствуют'

    return bot_answer
