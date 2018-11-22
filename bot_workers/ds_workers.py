from logger import worker_logger
from bot_functions.bot_functions import get_chat_id, get_message_text
from bot_functions.bot_functions import no_wait, standard_message, get_username, send_message_by_parts
from bot_functions.mysql_functions import Sql44DbFunctions, SqlEdoFunctions
from ets.ets_excel_creator import Excel
from config import ds_status_dir
import re


# ВОРКЕРЫ
# ОПРЕДЕЛЯЮТСЯ ОБЯЗАТЕЛЬНО ЧЕРЕЗ (bot, update, user_data)

# проверка существования пользователя
def text_get_request_ds_status_info(bot, update, user_data):
    bot_answer = ''

    username = get_username(update)
    chat_id = get_chat_id(update)
    message_text = get_message_text(update).strip()

    procedure_number = re.findall(r'^([0-9]{19})[\s$]?', message_text)
    inn = re.findall(r'^[0-9]{19}\s+([0-9]+)$', message_text)

    if procedure_number:
        procedure_number = procedure_number[0]
    else:
        bot_answer += 'Не указан номер процедуры'
        worker_logger(username, chat_id, text=bot_answer)
        standard_message(update, text=bot_answer)
        no_wait(bot, update, user_data)
        return

    inn = inn[0] if inn else None
    inn_str = "AND p.inn = '%s'" % inn if inn else ''

    request_ds_status_info = SqlEdoFunctions().get_request_ds_status_info(procedure_number, inn_str)

    if not request_ds_status_info:
        bot_answer += 'Сведений по указанным данным не найдено'
        worker_logger(username, chat_id, text=bot_answer)
        standard_message(update, text=bot_answer)
        no_wait(bot, update, user_data)
        return

    if len(request_ds_status_info) > 1:
        excel_f = Excel()
        excel_l = excel_f.create_list('Статус ДС')
        excel_l.write_data_from_iter([[d['inn'],
                                       d['operation_datetime'],
                                       d['amount'],
                                       d['operation_status_text'],
                                       d['description_text'],
                                       d['bank_code'],
                                       d['operation_status_id'],
                                       d['guid']] for d in request_ds_status_info],
                                     ['ИНН', 'Дата операции', 'Сумма', 'Статус',
                                      'Описание', 'Банк', 'Код статуса', 'GUID'])
        excel_l.set_column_width(100, 75, 150, 250, 250, 75, 50, 300)
        excel_doc = excel_f.save_file(save_dir=ds_status_dir, file_name='DS_report_' + str(procedure_number))
        bot.send_document(chat_id=chat_id,
                          document=open(excel_doc, 'rb'),
                          caption='Отчет по процедуре %s' % procedure_number)

    for r in request_ds_status_info:
        line = 'ИНН %(inn)s: %(operation_status_text)s %(amount)s (%(operation_datetime)s)\n' % r
        bot_answer += line

    worker_logger(username, chat_id, text=bot_answer)
    send_message_by_parts(bot, chat_id, bot_answer)
    no_wait(bot, update, user_data)



