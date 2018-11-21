from logger import logger
from time import time
from config import *


def unlogin_by_timeout(bot, job):
    # через лист, поскольку иначе не даст удалять из словаря
    for chat_id in list(USER_DATA):
        last_active = USER_DATA[chat_id]['last_active']
        try:
            if last_active + unlogin_timeout < time():
                USER_DATA.pop(chat_id)
                bot.send_message(text='''Извините, вы разлогинены, поскольку превысили время бездействия.
Для повторного входа необходимо ввести пароль вида "pass xxxx"''',
                                 chat_id=chat_id)
                logger.info('%s unlogin by timeout' % chat_id)
        # если выполнить действие незалогиненным, то впишется пустой defaultdict и удалить не получится
        except TypeError:
            continue


