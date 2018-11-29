import logging
from inspect import stack
from config import log_format

logging.basicConfig(format=log_format,
                    level=logging.INFO)

logging.getLogger("requests").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


def chat_info_logger(username, chat_id, message, worker=''):
    if worker:
        worker = str(worker).capitalize() + '. '
    logger.info('%s%s (%s / %s)' % (worker, message, username, chat_id))


def worker_logger(username, chat_id, text=''):
    worker = stack()[1][3].capitalize()
    if text:
        logger.info('%s run with message "%s" (%s / %s)' % (worker, text.replace('\n', ' || '), username, chat_id))
    else:
        logger.info('%s (%s / %s)' % (worker, username, chat_id))

