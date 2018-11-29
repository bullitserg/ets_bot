import decorators
from config import *
from bot_functions.mysql_functions import BotDbFunctions
import keyboards
import bot_workers.checks_workers as checks_workers
import bot_workers.kaspersky_workers as kaspersky_workers
import bot_workers.nagios_workers as nagios_workers
import bot_workers.reports_workers as reports_workers
import bot_workers.ds_workers as ds_workers
from logger import logger, chat_info_logger
import re


# обработка авторизации
@decorators.only_registered
@decorators.is_activity(USER_DATA)
@decorators.drop_dialog(USER_DATA)
def authorisation_handler(bot, update):
    chat_id = update.message.chat_id
    username = update.message.chat.username
    first_name = update.message.chat.first_name
    if USER_DATA[chat_id]['authorized']:
        update.message.reply_text('Повторная авторизация не требуется',
                                  reply_markup=keyboards.reply_markup_keyboard_standard)
        return

    password = re.search(r'[0-9]{4}$', update.message.text).group()

    original_password = USER_DATA[chat_id]['password']
    if not original_password:
        original_password = USER_DATA[chat_id]['password'] = BotDbFunctions().get_password(chat_id)

    if password == original_password:
        chat_info_logger(username, chat_id, 'Authorized successful')
        update.message.reply_text('%s, вы успешно авторизованы' % first_name,
                                  reply_markup=keyboards.reply_markup_keyboard_standard)
        # устанавливаем метку авторизации
        USER_DATA[chat_id]['authorized'] = True
        # пишем данные меню в USER_DATA
        USER_DATA[chat_id]['menu'] = BotDbFunctions().get_menu(chat_id)
        USER_DATA[chat_id]['help'] = BotDbFunctions().get_help(chat_id)
    else:
        chat_info_logger(username, chat_id, 'Not correct password')
        update.message.reply_text('Введен некорректный пароль',
                                  reply_markup=keyboards.reply_markup_keyboard_off)


# обработка текстовых сообщений
@decorators.only_registered
@decorators.only_authorised(USER_DATA)
@decorators.is_activity(USER_DATA)
def text_handler(bot, update):
    chat_id = update.message.chat_id
    username = update.message.chat.username
    message_text = update.message.text
    worker = USER_DATA[chat_id]['wait']
    # обнуляем wait
    USER_DATA[chat_id]['wait'] = None
    # если определен воркер - вызываем его
    if worker:
        # указываем, что воркер текстовый и пишем в last_command его наименование и сообщение (в этом случае пустое)
        # USER_DATA[chat_id]['last_command'] = (worker, message_text)

        worker_type = 'text'
        sh_worker = '_'.join([worker_type, worker])
        if hasattr(checks_workers, sh_worker):
            worker_call = getattr(checks_workers, sh_worker)
            return worker_call(bot, update, USER_DATA)

        elif hasattr(kaspersky_workers, sh_worker):
            worker_call = getattr(kaspersky_workers, sh_worker)
            return worker_call(bot, update, USER_DATA)

        elif hasattr(nagios_workers, sh_worker):
            worker_call = getattr(nagios_workers, sh_worker)
            return worker_call(bot, update, USER_DATA)

        elif hasattr(reports_workers, sh_worker):
            worker_call = getattr(reports_workers, sh_worker)
            return worker_call(bot, update, USER_DATA)

        elif hasattr(ds_workers, sh_worker):
            worker_call = getattr(ds_workers, sh_worker)
            return worker_call(bot, update, USER_DATA)

        else:
            logger.info('%s: Worker %s not exists' % (__name__, sh_worker))
    else:
        pass
        # если воркера нет, значит не ожидается никакого текста
        update.message.reply_text('Неизвестная команда.\n /help для справки',
                                  reply_markup=keyboards.reply_markup_keyboard_standard)



