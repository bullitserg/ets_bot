from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from logger import logger, chat_info_logger


# ХЭНДЛЕРЫ ОШИБОК
# обработка ошибок
def error_handler(bot, update, error):
    try:
        raise error
    except Unauthorized as e:
        # remove update.message.chat_id from conversation list
        logger.critical(e)
    except BadRequest as e:
        # handle malformed requests - read more below!
        logger.critical(e)
    except TimedOut as e:
        # handle slow connection problems
        logger.critical(e)
    except NetworkError as e:
        # handle other connection problems
        logger.critical(e)
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        logger.critical(e)
    except TelegramError as e:
        # handle all other telegram related errors
        logger.critical(e)
