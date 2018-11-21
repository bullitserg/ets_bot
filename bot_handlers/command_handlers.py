from telegram import ParseMode
import decorators
import bot_workers
from config import *
from bot_functions.bot_functions import send_about, standard_message
from logger import logger, chat_info_logger
import keyboards


@decorators.only_registered
@decorators.only_authorised(USER_DATA)
@decorators.is_activity(USER_DATA)
# КНОПКА START
def start_handler(bot, update):
    pass


# КНОПКА ABOUT
def about_handler(bot, update):
    send_about(bot, update)


# КНОПКА HELP
@decorators.only_registered
@decorators.only_authorised(USER_DATA)
@decorators.is_activity(USER_DATA)
def help_handler(bot, update):
    chat_id = update.message.chat_id
    username = update.message.chat.username
    help_text = USER_DATA[chat_id]['help']
    if help_text:
        update.message.reply_text(help_text,
                                  reply_markup=keyboards.reply_markup_keyboard_standard,
                                  parse_mode=ParseMode.HTML)
    else:
        standard_message(update, 'Извините, у вас нет доступных команд')
#    USER_DATA[chat_id]['wait'] = None


# КНОПКА EXIT
@decorators.only_registered
@decorators.only_authorised(USER_DATA)
@decorators.is_activity(USER_DATA)
def exit_handler(bot, update):
    chat_id = update.message.chat_id
    username = update.message.chat.username
    chat_info_logger(username, chat_id, 'Exit chat')
    update.message.reply_text('''Вы успешно разлогинены. Для повторного входа необходимо ввести пароль вида "pass xxxx"
Будьте осторожны: история переписки может содержать конфиденциальные данные. При необходимости удалите ее.''',
                              reply_markup=keyboards.reply_markup_keyboard_off)
    USER_DATA.pop(chat_id)


# КНОПКА MENU
@decorators.only_registered
@decorators.only_authorised(USER_DATA)
@decorators.is_activity(USER_DATA)
def menu_handler(bot, update):
    chat_id = update.message.chat_id

    if USER_DATA[chat_id]['menu']:
        USER_DATA[chat_id]['last_menu'] = 'main'
        update.message.reply_text(text='''Доступные вам команды:''',
                                  reply_markup=USER_DATA[chat_id]['menu']['main']['buttons'])
    else:
        standard_message(update, 'Извините, у вас нет доступных команд')


# КНОПКА REPEAT
@decorators.only_registered
@decorators.only_authorised(USER_DATA)
@decorators.is_activity(USER_DATA)
def repeat_handler(bot, update):
    chat_id = update.message.chat_id
    worker = USER_DATA[chat_id]['last_command']

    # если команда определена, то обрабатываем
    if worker:
        # получаем воркер, его тип и текст сообщения
        sh_worker = worker[0]
        worker_type = worker[1]
        message_text = worker[2]

        # указываем, что ожидать следующей команде
        USER_DATA[chat_id]['wait'] = sh_worker
        # находим что выполнять текущей
        exec_worker = '_'.join([worker_type, sh_worker])
        # пробуем исполнить воркер и отправить сообщение, если оно есть
        if message_text:
            update.message.reply_text(text=message_text)
        if hasattr(bot_workers, exec_worker):
            worker_call = getattr(bot_workers, exec_worker)
            return worker_call(bot, update, USER_DATA)
        else:
            logger.info('%s: Worker %s not exists' % (__name__, exec_worker))

    else:
        update.message.reply_text(text='''У вас отсутствуют выполненные команды''')

