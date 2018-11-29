import keyboards
from functools import wraps
from bot_functions.bot_functions import message_for_not_registered
from bot_functions.mysql_functions import BotDbFunctions
from logger import chat_info_logger
from time import time


# DECORATORS
# действия только для зарегистрированных пользователей
def only_registered(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        try:
            chat_id = update.message.chat_id
            username = update.message.chat.username
        except AttributeError:
            chat_id = update.callback_query.message.chat.id
            username = update.callback_query.message.chat.username
        if not BotDbFunctions().is_registered(chat_id):
            chat_info_logger(username, chat_id, 'Not registered user connected')
            message_for_not_registered(bot, update)
            return

        return func(bot, update, *args, **kwargs)
    return wrapped


# действия только для authorised пользователей
def only_authorised(user_data):
    def decorator(func):
        @wraps(func)
        def wrapped(bot, update, *args, **kwargs):
            try:
                chat_id = update.message.chat_id
                username = update.message.chat.username
            except AttributeError:
                chat_id = update.callback_query.message.chat.id
                username = update.callback_query.message.chat.username
            if not user_data[chat_id]['authorized']:
                chat_info_logger(username, chat_id, 'Not authorized message')
                update.message.reply_text(
                    'Здравствуйте, %s. Вы не авторизованы. Введите ваш пароль в формате "pass xxxx"' % username,
                    reply_markup=keyboards.reply_markup_keyboard_off)
                return
            return func(bot, update, *args, **kwargs)
        return wrapped
    return decorator


# считать событие проявлением активности пользователя
def is_activity(user_data):
    def decorator(func):
        @wraps(func)
        def wrapped(bot, update, *args, **kwargs):
            try:
                chat_id = update.message.chat_id
            except AttributeError:
                chat_id = update.callback_query.message.chat.id
            user_data[chat_id]['last_active'] = time()
            return func(bot, update, *args, **kwargs)
        return wrapped
    return decorator


# сброс данных по диалогу
def drop_dialog(user_data):
    def decorator(func):
        @wraps(func)
        def wrapped(bot, update, *args, **kwargs):
            try:
                chat_id = update.message.chat_id
            except AttributeError:
                chat_id = update.callback_query.message.chat.id
            f = func(bot, update, *args, **kwargs)
            try:
                del user_data[chat_id]['dialog_function']
                del user_data[chat_id]['dialog_answer_on_no']
            except KeyError:
                pass
            return f
        return wrapped
    return decorator


