from logger import worker_logger
from bot_functions.bot_functions import get_chat_id, get_message_text, no_wait, get_username, send_message_by_parts
from bot_functions.nagios_functions import get_nagios_info


# ВОРКЕРЫ
# ОПРЕДЕЛЯЮТСЯ ОБЯЗАТЕЛЬНО ЧЕРЕЗ (bot, update, user_data)


# получение данных по критическим параметрам nagios
def callback_nagios_info_critical(bot, update, user_data):
    username = get_username(update)
    chat_id = get_chat_id(update)
    login = get_message_text(update).strip()

    worker_logger(username, chat_id, text=login)

    bot_answer = get_nagios_info(mode='critical')

    worker_logger(username, chat_id, text=bot_answer)
    send_message_by_parts(bot, chat_id, bot_answer)
    no_wait(bot, update, user_data)


# получение данных по предупреждениям nagios
def callback_nagios_info_warning(bot, update, user_data):
    username = get_username(update)
    chat_id = get_chat_id(update)
    login = get_message_text(update).strip()

    worker_logger(username, chat_id, text=login)

    bot_answer = get_nagios_info(mode='warning')

    worker_logger(username, chat_id, text=bot_answer)
    send_message_by_parts(bot, chat_id, bot_answer)
    no_wait(bot, update, user_data)


# получение данных по всем активным параметрам nagios
def callback_nagios_info_all(bot, update, user_data):
    username = get_username(update)
    chat_id = get_chat_id(update)
    login = get_message_text(update).strip()

    worker_logger(username, chat_id, text=login)

    bot_answer = get_nagios_info()

    worker_logger(username, chat_id, text=bot_answer)
    send_message_by_parts(bot, chat_id, bot_answer)
    no_wait(bot, update, user_data)
