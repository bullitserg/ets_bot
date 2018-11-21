from logger import worker_logger
from bot_functions.bot_functions import get_chat_id, get_message_text
from bot_functions.bot_functions import no_wait, standard_message, get_username, send_message_by_parts
from bot_functions.mysql_functions import Sql44DbFunctions, SqlEdoFunctions


# ВОРКЕРЫ
# ОПРЕДЕЛЯЮТСЯ ОБЯЗАТЕЛЬНО ЧЕРЕЗ (bot, update, user_data)


# проверка существования пользователя
def text_checks_user_exists(bot, update, user_data):
    bot_answer = ''
    username = get_username(update)
    chat_id = get_chat_id(update)
    login = get_message_text(update).strip()

    worker_logger(username, chat_id, text=login)

    if Sql44DbFunctions().get_user_exists(login):
        bot_answer += 'Пользователь "%s" уже существует' % login
    else:
        bot_answer += 'Пользователь "%s" не найден на секции' % login

    worker_logger(username, chat_id, text=bot_answer)
    standard_message(update, text=bot_answer)
    no_wait(bot, update, user_data)


# проверка существования аккаунта
def text_checks_account_exists(bot, update, user_data):
    bot_answer = ''
    username = get_username(update)
    chat_id = get_chat_id(update)
    inn = get_message_text(update).strip()

    worker_logger(username, chat_id, text=inn)

    info = SqlEdoFunctions().get_account_exists(inn)

    if info:
        if info[0][0] is None:
            bot_answer += 'Сведения о счете ИНН %s отсутствуют' % inn
        else:
            bot_answer += 'Сведения о счете:\n'
            bot_answer += info[0][0]
    else:
        bot_answer += 'Сведения о счете ИНН %s отсутствуют' % inn

    worker_logger(username, chat_id, text=bot_answer)
    send_message_by_parts(bot, chat_id, bot_answer)
    no_wait(bot, update, user_data)


# проверка существования аккаунта
def text_checks_account_error(bot, update, user_data):
    bot_answer = ''
    bot_answer_2 = ''
    username = get_username(update)
    chat_id = get_chat_id(update)
    inn = get_message_text(update).strip()

    worker_logger(username, chat_id, text=inn)

    info = SqlEdoFunctions().get_account_error(inn)

    if info:
        if info[0][0] is None:
            bot_answer += 'Сведения об ответах банка на запрос спецсчета по ИНН %s отсутствуют' % inn
        else:
            bot_answer += 'Последний ответ банка на запрос спецсчета по ИНН %s:\n' % inn
            bot_answer += info[0][0]
            bot_answer_2 = info[0][1]
    else:
        bot_answer += 'Сведения об ответах банка на запрос спецсчета по ИНН %s отсутствуют' % inn

    worker_logger(username, chat_id, text=bot_answer)
    send_message_by_parts(bot, chat_id, bot_answer)

    if bot_answer_2:
        worker_logger(username, chat_id, text=bot_answer_2)
        standard_message(update, text=bot_answer_2)

    no_wait(bot, update, user_data)
