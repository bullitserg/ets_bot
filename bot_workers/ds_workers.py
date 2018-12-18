from logger import worker_logger
from bot_functions.bot_functions import get_chat_id, get_message_text
from bot_functions.bot_functions import no_wait, standard_message, get_username, send_message_by_parts
from bot_functions.mysql_functions import Sql44DbFunctions, SqlEdoFunctions
from ets.ets_excel_creator import Excel
from config import ds_status_dir, ds_status_by_guid_dir, ds_commission_dir, ds_inn_status_dir
from bot_functions.other_functions import write_ds_log
from config import ds_log_file
from os.path import normpath, getsize
import re
import ets.ets_ds_lib as ds
from bot_functions.bot_functions import dialog


# ВОРКЕРЫ
# ОПРЕДЕЛЯЮТСЯ ОБЯЗАТЕЛЬНО ЧЕРЕЗ (bot, update, user_data)

# проверка статуса денег по процедуре
def text_get_request_ds_status_info(bot, update, user_data):
    bot_answer = ''

    username = get_username(update)
    chat_id = get_chat_id(update)
    message_text = get_message_text(update).strip()

    procedure_number = re.findall(r'^([0-9]{11,19})[\s$]?', message_text)
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

    if not inn:
        excel_f = Excel()
        excel_l = excel_f.create_list('Статус ДС')
        excel_l.write_data_from_iter([[d['inn'],
                                       d['operation_datetime'],
                                       d['amount'],
                                       d['operation_status_text'],
                                       d['description_text'],
                                       d['bank_code'],
                                       d['account'],
                                       d['operation_status_id'],
                                       d['guid']] for d in request_ds_status_info],
                                     ['ИНН', 'Дата операции', 'Сумма', 'Статус',
                                      'Описание', 'Банк', 'Аккаунт', 'Код статуса', 'GUID'])
        excel_l.set_column_width(100, 75, 150, 250, 250, 75, 160, 50, 300)
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


# проверка статуса списания комиссий по процедуре
def text_get_commission_status_info(bot, update, user_data):
    bot_answer = ''

    username = get_username(update)
    chat_id = get_chat_id(update)
    message_text = get_message_text(update).strip()

    procedure_number = re.findall(r'^([0-9]{19})$', message_text)

    if procedure_number:
        procedure_number = procedure_number[0]
    else:
        bot_answer += 'Не указан номер процедуры'
        worker_logger(username, chat_id, text=bot_answer)
        standard_message(update, text=bot_answer)
        no_wait(bot, update, user_data)
        return

    commission_status_info = SqlEdoFunctions().get_commission_status_info(procedure_number)

    if not commission_status_info:
        bot_answer += 'Сведений по указанным данным не найдено'
        worker_logger(username, chat_id, text=bot_answer)
        standard_message(update, text=bot_answer)
        no_wait(bot, update, user_data)
        return

    excel_f = Excel()
    excel_l = excel_f.create_list('Статус ДС')
    excel_l.write_data_from_iter([[d['inn'],
                                   d['operation_datetime'],
                                   d['amount'],
                                   d['operation_status_text'],
                                   d['description_text'],
                                   d['bank_code'],
                                   d['account'],
                                   d['operation_status_id'],
                                   d['guid']] for d in commission_status_info],
                                 ['ИНН', 'Дата операции', 'Сумма', 'Статус',
                                  'Описание', 'Банк', 'Аккаунт', 'Код статуса', 'GUID'])
    excel_l.set_column_width(100, 75, 150, 250, 250, 75, 160, 50, 300)
    excel_doc = excel_f.save_file(save_dir=ds_commission_dir, file_name='COMMISSION_report_' + str(procedure_number))
    bot.send_document(chat_id=chat_id,
                      document=open(excel_doc, 'rb'),
                      caption='Отчет по процедуре %s' % procedure_number)

    for c in commission_status_info:
        line = 'ИНН %(inn)s: %(operation_status_text)s %(amount)s (%(operation_datetime)s)\n' % c
        bot_answer += line

    worker_logger(username, chat_id, text=bot_answer)
    send_message_by_parts(bot, chat_id, bot_answer)
    no_wait(bot, update, user_data)


# проверка статуса по guid
def text_check_operation_status_by_guid(bot, update, user_data):
    bot_answer = ''

    username = get_username(update)
    chat_id = get_chat_id(update)
    message_text = get_message_text(update).strip()

    guid = re.findall(r'^(.{32})$', message_text)
    if guid:
        guid = guid[0]
    else:
        bot_answer += 'Указан некорректный GUID'
        worker_logger(username, chat_id, text=bot_answer)
        standard_message(update, text=bot_answer)
        no_wait(bot, update, user_data)
        return

    operation_status_by_guid = SqlEdoFunctions().check_operation_status_by_guid(guid)
    package_info_by_guid = SqlEdoFunctions().get_package_info_by_guid(guid)

    if package_info_by_guid:
        excel_f = Excel()
        excel_l = excel_f.create_list('GUID info')
        excel_l.write_data_from_iter(package_info_by_guid, top_line=['id', 'msg_id', 'correlation_id', 'create_date',
                                                                     'exchange_date', 'source', 'raw_body',
                                                                     'destination', 'document_type', 'document',
                                                                     'signature', 'response_date', 'response_code',
                                                                     'response_text', 'status', 'error_text'])
        excel_l.set_column_width(50, 260, 260, 100, 100, 120, 300, 120, 120, 300, 300, 100, 120, 200, 50, 200)
        excel_doc = excel_f.save_file(save_dir=ds_status_by_guid_dir, file_name=str(guid))
        bot.send_document(chat_id=chat_id,
                          document=open(excel_doc, 'rb'),
                          caption='Отчет по GUID %s' % guid)

    if not operation_status_by_guid:
        bot_answer += 'Платежная информация не найдена'
    else:
        for info in operation_status_by_guid:
            bot_answer += info[0]

    worker_logger(username, chat_id, text=bot_answer)
    standard_message(update, text=bot_answer)
    no_wait(bot, update, user_data)


# блокировка ДС
def text_blocking_ds(bot, update, user_data):
    bot_answer = ''

    username = get_username(update)
    chat_id = get_chat_id(update)
    message_text = get_message_text(update).strip()

    purchase_inn_data = re.findall(r'^([0-9]{11,19})\s([0-9]{6,})$', message_text)

    if not purchase_inn_data:
        bot_answer += 'Указаны некорректные данные'
        worker_logger(username, chat_id, text=bot_answer)
        standard_message(update, text=bot_answer)
        no_wait(bot, update, user_data)
        return

    procedure_number, inn = purchase_inn_data[0]
    request_ds_data = SqlEdoFunctions().get_block_info(procedure_number, inn)

    if not request_ds_data:
        bot_answer += 'Не найдено данных для блокировки'
        worker_logger(username, chat_id, text=bot_answer)
        standard_message(update, text=bot_answer)
        no_wait(bot, update, user_data)
        return

    request_ds_data = request_ds_data[0]

    bot_answer += 'Сведения о блокировке:\nAppID: %s\nСчет: %s (%s)\nСумма: %s' % (
        request_ds_data['app_id'],
        request_ds_data['account'],
        request_ds_data['bank_id'],
        request_ds_data['amount'])

    worker_logger(username, chat_id, text=bot_answer)
    standard_message(update, text=bot_answer)
    no_wait(bot, update, user_data)

    def block_dialog():
        answer = ''
        guid, error = ds.block(request_ds_data['account'],
                               request_ds_data['bank_id'],
                               request_ds_data['amount'],
                               request_ds_data['app_id'])

        if not error:
            answer += 'Блокировка проведена. GUID: %s' % guid
            write_ds_log('BLOCK', username, chat_id, procedure_number, request_ds_data['request_id'], inn,
                         request_ds_data['amount'], request_ds_data['account'],
                         request_ds_data['bank_id'], guid)
        else:
            answer += 'Ошибка блокировки: %s' % error
        return answer

    dialog(bot, update, user_data, block_dialog, 'Заблокировать ДС?', 'Блокировка отменена')


# разблокировка ДС
def text_unlocking_ds(bot, update, user_data):
    bot_answer = ''

    username = get_username(update)
    chat_id = get_chat_id(update)
    message_text = get_message_text(update).strip()

    purchase_inn_data = re.findall(r'^([0-9]{11,19})\s([0-9]{6,})$', message_text)

    if not purchase_inn_data:
        bot_answer += 'Указаны некорректные данные'
        worker_logger(username, chat_id, text=bot_answer)
        standard_message(update, text=bot_answer)
        no_wait(bot, update, user_data)
        return

    procedure_number, inn = purchase_inn_data[0]
    request_ds_data = SqlEdoFunctions().get_block_info(procedure_number, inn)

    if not request_ds_data:
        bot_answer += 'Не найдено данных для разблокировки'
        worker_logger(username, chat_id, text=bot_answer)
        standard_message(update, text=bot_answer)
        no_wait(bot, update, user_data)
        return

    request_ds_data = request_ds_data[0]

    bot_answer += 'Сведения о разблокировке:\nAppID: %s\nСчет: %s (%s)\nСумма: %s' % (
        request_ds_data['app_id'],
        request_ds_data['account'],
        request_ds_data['bank_id'],
        request_ds_data['amount'])

    worker_logger(username, chat_id, text=bot_answer)
    standard_message(update, text=bot_answer)
    no_wait(bot, update, user_data)

    def unlock_dialog():
        answer = ''

        guid, error = ds.unlock(request_ds_data['account'],
                                request_ds_data['bank_id'],
                                request_ds_data['amount'],
                                request_ds_data['app_id'])

        if not error:
            answer += 'Разблокировка проведена. GUID: %s' % guid
            write_ds_log('UNLOCK', username, chat_id, procedure_number, request_ds_data['request_id'], inn,
                         request_ds_data['amount'], request_ds_data['account'],
                         request_ds_data['bank_id'], guid)
        else:
            answer += 'Ошибка разблокировки: %s' % error
        return answer

    dialog(bot, update, user_data, unlock_dialog, 'Разблокировать ДС?', 'Разблокировка отменена')


# просмотр лога операций с ДС
def callback_check_ds_log(bot, update, user_data):
    bot_answer = ''

    username = get_username(update)
    chat_id = get_chat_id(update)

    with open(normpath(ds_log_file), mode='r', encoding='utf8') as o_ds_log:
        bot_answer += 'Последние платежные события:\n' + '\n'.join(
            [re.findall(r'(^.*?) #', l)[0] for l in sorted(o_ds_log.readlines()[-3:], reverse=True)]
        )

    if getsize(normpath(ds_log_file)):
        bot.send_document(chat_id=chat_id,
                          document=open(normpath(ds_log_file), 'rb'),
                          caption='Сведения о платежных операциях')

    else:
        bot_answer = 'Сведения о событиях отсутствуют'

    worker_logger(username, chat_id, text=bot_answer)
    send_message_by_parts(bot, chat_id, bot_answer)
    no_wait(bot, update, user_data)
    return


# проверка статуса денег по процедуре
def text_get_inn_ds_status_info(bot, update, user_data):
    bot_answer = ''

    username = get_username(update)
    chat_id = get_chat_id(update)
    message_text = get_message_text(update).strip()

    inn = re.findall(r'^([0-9]{10,12})[\s$]?', message_text)
    procedure_number = re.findall(r'^[0-9]{10,12}\s+([0-9]+)$', message_text)

    if inn:
        inn = inn[0]
    else:
        bot_answer += 'Не указан ИНН'
        worker_logger(username, chat_id, text=bot_answer)
        standard_message(update, text=bot_answer)
        no_wait(bot, update, user_data)
        return

    procedure_number = procedure_number[0] if procedure_number else None
    procedure_number_str = "AND p.purchase_number = '%s'" % procedure_number if procedure_number else ''

    inn_ds_status_info = SqlEdoFunctions().get_inn_ds_status_info(inn, procedure_number_str)

    if not inn_ds_status_info:
        bot_answer += 'Сведений по указанным данным не найдено'
        worker_logger(username, chat_id, text=bot_answer)
        standard_message(update, text=bot_answer)
        no_wait(bot, update, user_data)
        return

    excel_f = Excel()
    excel_l = excel_f.create_list('Реестр ДС')
    excel_l.write_data_from_iter([[d['purchase_number'],
                                   d['request_id'],
                                   d['operation_type'],
                                   d['exchange_date'],
                                   d['response_date'],
                                   d['amount'],
                                   d['info'],
                                   d['guid'],
                                   d['inn'],
                                   d['kpp'],
                                   d['bank_id'],
                                   d['account']] for d in inn_ds_status_info],
                                 ['Закупка', 'Заявка', 'Операция', 'Дата операции',
                                  'Дата ответа', 'Сумма', 'Информация', 'GUID', 'ИНН', 'КПП', 'Банк', 'Спецсчет'])

    excel_l.set_column_width(140, 75, 150, 120, 120, 120, 160, 250, 120, 120, 150, 150)

    excel_doc = excel_f.save_file(save_dir=ds_inn_status_dir, file_name='DS_INN_report_' + str(inn))
    bot.send_document(chat_id=chat_id,
                      document=open(excel_doc, 'rb'),
                      caption='Отчет по ИНН %s' % inn)

    if procedure_number:
        for s in inn_ds_status_info:
            line = '%(exchange_date)s: %(operation_type)s %(amount)s (%(info)s)\n' % s
            bot_answer += line

    worker_logger(username, chat_id, text=bot_answer)
    send_message_by_parts(bot, chat_id, bot_answer)
    no_wait(bot, update, user_data)






