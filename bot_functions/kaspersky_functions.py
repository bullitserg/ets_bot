import re
from logger import logger
from ets.etsKasperskyAPI import KasperskyWorker
from bot_functions.bot_functions import *


def kaspersky_ip_add_and_delete(bot, update, user_data, kaspersky_function, list_type):
    max_ip_count = 20
    bot_answer = ''
    username = get_username(update)
    chat_id = get_chat_id(update)
    message_text = get_message_text(update).replace(' ', '').replace('\n', ',')
    worker_logger(username, chat_id, text=message_text)
    ip_list = message_text.split(',')

    if ip_list:
        if len(ip_list) > max_ip_count:
            bot_answer = 'Превышен лимит в %s ip адресов' % max_ip_count
            return bot_answer

        ok_ip_list = set(filter(
            lambda ip: re.fullmatch(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$', ip),
            ip_list))
        bad_ip_list = list(set(ip_list).symmetric_difference(ok_ip_list))

        if ok_ip_list:
            # обрабатываем адреса
            k_work = KasperskyWorker()
            k_function = getattr(k_work, kaspersky_function)
            ip_status = k_function(ok_ip_list, list_type=list_type)

            if isinstance(ip_status, tuple):
                bot_answer = 'Ошибка обработки пакета'
                standard_message(update, bot_answer)
                logger.error(ip_status)
                return False

            bot_answer += 'Обработаны адреса (%s): ' % len(ok_ip_list) + ', '.join(ok_ip_list) + '\n'
        if bad_ip_list:
            bot_answer += 'Некорректные адреса: ' + ', '.join(bad_ip_list)

    else:
        bot_answer = 'Некорректный разделитель'
    return bot_answer
