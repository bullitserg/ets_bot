from logger import worker_logger
from bot_functions.bot_functions import get_chat_id, get_message_text, no_wait, standard_message, get_username
from bot_functions.mysql_functions import Sql44DbFunctions
import re
import ets.etsExcelCreator as etsExcelCreator
from config import *
import shutil
import os


# ВОРКЕРЫ
# ОПРЕДЕЛЯЮТСЯ ОБЯЗАТЕЛЬНО ЧЕРЕЗ (bot, update, user_data)


# формирование отчета по заявкам
def text_reports_procedure_requests(bot, update, user_data):
    max_procedure_count = 5
    bot_answer = ''
    username = get_username(update)
    chat_id = get_chat_id(update)
    message_text = get_message_text(update).replace(' ', '').replace('\n', ',')
    procedure_list = message_text.split(',')

    worker_logger(username, chat_id, text=message_text)

    if procedure_list:
        if len(procedure_list) > max_procedure_count:
            bot_answer += 'Превышен лимит в %s номеров процедур' % max_procedure_count

        else:
            ok_procedure_list = set(filter(
                lambda p: re.fullmatch(r'^[0-9]{19}$', p) or re.fullmatch(r'^ПО[0-9]{17}$', p),
                procedure_list))

            if ok_procedure_list:
                for procedure in ok_procedure_list:

                    procedure_data = Sql44DbFunctions().get_reports_procedure_requests(procedure)
                    procedure_top = list(procedure_data[0])
                    procedure_info = list(procedure_data[1])

                    if procedure_info:
                        excel = etsExcelCreator.Excel()
                        excel_list = excel.createList(sheetName=procedure)
                        excel_list.writeDataFromIter(procedure_info, topLine=procedure_top)
                        excel_list.setDefaultColumnWidth(200)
                        excel.saveFile(reports_procedure_requests_dir, fileName=procedure)

                        excel_doc = '/'.join([reports_procedure_requests_dir, procedure]) + '.xls'
                        bot.send_document(chat_id=chat_id,
                                          document=open(excel_doc, 'rb'),
                                          caption='Отчет по процедуре %s' % procedure)
                    else:
                        standard_message(update, 'Нет сведений о процедуре %s. Возможно, отсутствует на площадке. Пожалуйста, проверьте номер еще раз.' % procedure)

                bot_answer += 'Обработаны процедуры: %s' % ', '.join(ok_procedure_list)
            else:
                bot_answer += 'Извините, не указано корректных номеров процедур'

            bad_procedure_list = list(set(procedure_list).symmetric_difference(ok_procedure_list))

            if bad_procedure_list:
                bot_answer += '\nПроцедуры с некорректными номерами: %s' % ', '.join(bad_procedure_list)

    else:
        bot_answer += 'Не указано номеров процедур. Попробуйте еще раз'

    worker_logger(username, chat_id, text=bot_answer)
    standard_message(update, text=bot_answer)
    no_wait(bot, update, user_data)


def text_reports_fine_check(bot, update, user_data):
    max_inn_count = 20
    bot_answer = ''
    username = get_username(update)
    chat_id = get_chat_id(update)
    message_text = get_message_text(update).replace(' ', '').replace('\n', ',')
    inn_list = message_text.split(',')

    worker_logger(username, chat_id, text=message_text)

    if inn_list:
        if len(inn_list) > max_inn_count:
            bot_answer += 'Превышен лимит в %s номеров процедур' % max_inn_count

        else:
            ok_inn_list = set(filter(
                lambda i: re.fullmatch(r'^(\d{10}|\d{12})$', i),
                inn_list))

            if ok_inn_list:
                worked_inns = []
                worked_docs = []
                for inn in ok_inn_list:

                    inn_data = Sql44DbFunctions().get_reports_fine_check(inn)
                    inn_top = list(inn_data[0])
                    inn_info = list(inn_data[1])

                    excel = etsExcelCreator.Excel()
                    excel_list = excel.createList(sheetName=inn)
                    excel_list.writeDataFromIter(inn_info, topLine=inn_top)
                    excel_list.setDefaultColumnWidth(180)
                    excel.saveFile(reports_fine_check_dir, fileName=inn)

                    excel_doc = '/'.join([reports_fine_check_dir, inn]) + '.xls'
                    worked_inns.append(inn)
                    worked_docs.append(excel_doc)

                if len(worked_docs) == 1:
                    bot.send_document(chat_id=chat_id,
                                      document=open(worked_docs[0], 'rb'),
                                      caption='Проверка списания штрафов по организации %s' % worked_inns[0])

                else:
                    tmp_dir = '/'.join([reports_fine_check_dir, 'tmp'])
                    if not os.path.isdir(tmp_dir):
                        os.mkdir(tmp_dir)
                    for doc in worked_docs:
                        shutil.copy(doc, tmp_dir)

                    archive = shutil.make_archive('Fines', 'zip', tmp_dir)

                    bot.send_document(chat_id=chat_id,
                                      document=open(archive, 'rb'),
                                      caption='Проверка списания штрафов')

                    shutil.rmtree(tmp_dir)

                bot_answer += 'Обработаны организации: %s' % ', '.join(worked_inns)
            else:
                bot_answer += 'Извините, не указано корректных ИНН'

            bad_inn_list = list(set(inn_list).symmetric_difference(ok_inn_list))

            if bad_inn_list:
                bot_answer += '\nНекорректные ИНН: %s' % ', '.join(bad_inn_list)

    else:
        bot_answer += 'Не указано ИНН. Попробуйте еще раз'

    worker_logger(username, chat_id, text=bot_answer)
    standard_message(update, text=bot_answer)
    no_wait(bot, update, user_data)