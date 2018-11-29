import keyboards
from config import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from logger import worker_logger


# создание меню сообщения
def build_menu(buttons,
               n_cols=2,
               header_buttons=None,
               footer_buttons=None):
    buttons = [InlineKeyboardButton(buttons[0][k], callback_data=buttons[1][k]) for k in range(len(buttons[0]))]
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return InlineKeyboardMarkup(menu)


# FUNCTIONS FOR TEXT WORKERS
def get_chat_id(update):
    try:
        chat_id = update.message.chat_id
    except AttributeError:
        chat_id = update.callback_query.message.chat_id
    return chat_id


def get_first_name(update):
    try:
        first_name = update.message.chat.first_name
    except AttributeError:
        first_name = update.callback_query.message.first_name
    return first_name


def get_username(update):
    try:
        username = update.message.chat.username
    except AttributeError:
        username = update.callback_query.message.chat.username
    return username


def get_message_text(update):
    try:
        message = update.callback_query.data.strip()
    except AttributeError:
        message = update.message.text.strip()
    return message


def no_wait(bot, update, user_data):
    chat_id = get_chat_id(update)
    user_data[chat_id]['wait'] = None


def standard_message(update, text):
    update.message.reply_text(text=text,
                              reply_markup=keyboards.reply_markup_keyboard_standard)


def message_for_not_registered(bot, update):
    chat_id = get_chat_id(update)
    username = get_username(update)
    last_name = update.message.chat.last_name
    first_name = update.message.chat.first_name
    update.message.reply_text('''Извините, вы не зарегистрированный пользователь. Отправьте запрос на %s
Укажите следующие сведения:
Ваш id: %s
Ваш логин: %s
Пользователь: %s''' % (administrator_email, chat_id, username, ' '.join([last_name, first_name])),
                              reply_markup=keyboards.reply_markup_keyboard_off)


def send_about(bot, update):
    chat_id = get_chat_id(update)
    username = get_username(update)
    update.message.reply_text(text='''<b>Bender telegram bot</b>
  Версия: %s
  Никнейм: @%s
-----------------------------------------
Контакты для связи с администратором:
  Email: %s
Обязательно укажите:
  Id: %s
  Login: %s
    ''' % (bot_version, bot_nickname, administrator_email, chat_id, username),
                              parse_mode=ParseMode.HTML)
    worker_logger(username, chat_id)


def send_message_by_parts(bot, chat_id, text):
    while text:
        text_part = text[0:message_max_len]
        bot.send_message(text=text_part,
                         chat_id=chat_id
                         )
        text = text[message_max_len:]


def dialog(bot, update, user_data, function, dialog_message, text_on_no):
    chat_id = get_chat_id(update)
    dialog_menu = build_menu([['Да', 'Нет'], ['dialog_yes', 'dialog_no']])

    bot.send_message(text=dialog_message,
                     chat_id=chat_id,
                     reply_markup=dialog_menu)

    user_data[chat_id]['dialog_function'] = function
    user_data[chat_id]['dialog_answer_on_no'] = text_on_no


