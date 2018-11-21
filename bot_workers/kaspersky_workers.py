from logger import logger, worker_logger
from bot_functions.bot_functions import get_chat_id, get_message_text, no_wait, standard_message, get_username
from bot_functions.kaspersky_functions import kaspersky_ip_add_and_delete
import re
from ets.etsKasperskyAPI import KasperskyWorker
from keyboards import reply_markup_keyboard_standard

# ВОРКЕРЫ
# ОПРЕДЕЛЯЮТСЯ ОБЯЗАТЕЛЬНО ЧЕРЕЗ (bot, update, user_data)


# получение статуса IP
def text_kaspersky_ip_status(bot, update, user_data):
    username = get_username(update)
    chat_id = get_chat_id(update)
    message_text = get_message_text(update)
    worker_logger(username, chat_id, text=message_text)
    if re.fullmatch(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$', message_text):
        k_work = KasperskyWorker()
        ip_status = k_work.show_resource_ip_status(message_text, out_type='text')

        if isinstance(ip_status, str):
            ip_status += ''.join([' (', message_text, ')'])
            standard_message(update, ip_status)
        else:
            standard_message(update, 'Ошибка обработки пакета')
            logger.error(ip_status)
    else:
        standard_message(update, 'Введен некорректный ip')
    no_wait(bot, update, user_data)


# добавление в белый лист касперского
def text_kaspersky_ip_add_white(bot, update, user_data):
    username = get_username(update)
    chat_id = get_chat_id(update)
    bot_answer = kaspersky_ip_add_and_delete(bot, update, user_data, 'add_ip_list', 'white')
    if bot_answer:
        update.message.reply_text(text=bot_answer,
                                  reply_markup=reply_markup_keyboard_standard,
                                  disable_web_page_preview=True)
        worker_logger(username, chat_id, text=bot_answer)
    no_wait(bot, update, user_data)


# удаление из белого листа касперского
def text_kaspersky_ip_del_white(bot, update, user_data):
    username = get_username(update)
    chat_id = get_chat_id(update)
    bot_answer = kaspersky_ip_add_and_delete(bot, update, user_data, 'delete_ip_list', 'white')
    if bot_answer:
        standard_message(update, bot_answer)
        worker_logger(username, chat_id, text=bot_answer)
    no_wait(bot, update, user_data)


# добавление в блэк лист касперского
def text_kaspersky_ip_add_black(bot, update, user_data):
    username = get_username(update)
    chat_id = get_chat_id(update)
    bot_answer = kaspersky_ip_add_and_delete(bot, update, user_data, 'add_ip_list', 'black')
    if bot_answer:
        standard_message(update, bot_answer)
        worker_logger(username, chat_id, text=bot_answer)
    no_wait(bot, update, user_data)


# удаление из блэк листа касперского
def text_kaspersky_ip_del_black(bot, update, user_data):
    username = get_username(update)
    chat_id = get_chat_id(update)
    bot_answer = kaspersky_ip_add_and_delete(bot, update, user_data, 'delete_ip_list', 'black')
    if bot_answer:
        standard_message(update, bot_answer)
        worker_logger(username, chat_id, text=bot_answer)
    no_wait(bot, update, user_data)
