from ets.ets_mysql_lib import get_query_top, MysqlConnection as Mc
from bot_functions.bot_functions import *
from bot_functions.other_functions import last_decade_for_mysql
from bot_queries import bot_queries
from bot_queries import user_queries
from bot_queries import ds_queries


class BotDbFunctions:
    def __init__(self):
        self.BOT_DB_CONNECTION = Mc(connection=Mc.MS_BOT_CONNECT).connect()

    # Функция получения пароля
    def get_password(self, chat_id):
        user_password = self.BOT_DB_CONNECTION.execute_query(bot_queries.get_user_password_query % chat_id)[0][0]
        return user_password

    # Функция получения help страницы
    def get_help(self, chat_id):
        help_page = '''<b>ОСНОВНОЕ МЕНЮ</b>
        /menu    меню
        /repeat   повтор последней команды
        /help    список доступных команд
        /exit    выход'''
        help_page += '''\n\n<b>ПОЛЬЗОВАТЕЛЬСКОЕ МЕНЮ</b>\n'''
        try:
            help_page += self.BOT_DB_CONNECTION.execute_query(bot_queries.get_help_query % chat_id)[0][0]
        except TypeError:
            help_page += '  Извините, пользовательские команды отсутствуют'
        return help_page

    # Проверка регистрации пользователя
    def is_registered(self, chat_id):
        try:
            self.BOT_DB_CONNECTION.execute_query(bot_queries.check_registration_query % chat_id)[0][0]
        except IndexError:
            is_registered_b = False
        else:
            is_registered_b = True
        return is_registered_b

    # Получение сведений о меню для пользователя и их создание
    def get_menu(self, chat_id):
        user_menu_data = self.BOT_DB_CONNECTION.execute_query(bot_queries.get_menu_query % {'chat_id': chat_id})
        if user_menu_data[0][1]:
            # собираем данные меню из данных mysql
            user_menu = {}
            for menu in user_menu_data:
                # если есть доступные команды

                user_menu[menu[0]] = {
                    'buttons': [menu[1].split(';'),
                                menu[2].split(';')],
                    'message':
                        dict(zip(menu[2].split(';'), menu[3].split(';')))
                }

            # если не заполнен message, то вместо него в запросе UNDEFINED, их надо заменить на None
            # и сразу же создаем меню в формате InlineKeyboard
            for menu in user_menu.keys():
                for message in user_menu[menu]['message'].keys():
                    if user_menu[menu]['message'][message] == 'UNDEFINED':
                        user_menu[menu]['message'][message] = None
                user_menu[menu]['buttons'] = build_menu(user_menu[menu]['buttons'])
        else:
            # если данных по меню нет, значит меню для пользователя не назначено
            user_menu = False
        return user_menu


class Sql44DbFunctions:
    def __init__(self):
        self.SQL_44_DB_CONNECTION = Mc(connection=Mc.MS_44_2_CONNECT).connect()

    def get_reports_procedure_requests(self, procedure_number):
        # возвращаем tuple (top, data)
        return get_query_top(user_queries.reports_procedure_requests_query), \
               self.SQL_44_DB_CONNECTION.execute_query(user_queries.reports_procedure_requests_query % procedure_number)

    def get_reports_fine_check(self, inn):
        # возвращаем tuple (top, data)
        return get_query_top(user_queries.reports_fine_check_query), \
               self.SQL_44_DB_CONNECTION.execute_query(user_queries.reports_fine_check_query %
                                                       (last_decade_for_mysql(),
                                                        inn))

    def get_user_exists(self, login):
        return self.SQL_44_DB_CONNECTION.execute_query(user_queries.reports_user_exists_query % login)


class SqlEdoFunctions:
    def __init__(self):
        self.SQL_EDO_CONNECTION = Mc(connection=Mc.MS_EDO_CONNECT).connect()

    def get_account_exists(self, inn):
        return self.SQL_EDO_CONNECTION.execute_query(user_queries.reports_account_exists_query % str(inn))

    def get_account_error(self, inn):
        return self.SQL_EDO_CONNECTION.execute_query(user_queries.report_inn_get_account_error_query % str(inn))

    def get_request_ds_status_info(self, procedure_number, inn_str):
        procedure_number = str(procedure_number)
        return self.SQL_EDO_CONNECTION.execute_query(ds_queries.get_request_ds_status_info_query %
                                                     (procedure_number, inn_str),
                                                     dicted=True)

    def check_operation_status_by_guid(self, guid):
        guid = str(guid)
        return self.SQL_EDO_CONNECTION.execute_query(ds_queries.check_operation_status_by_guid_query % guid)

    def get_package_info_by_guid(self, guid):
        guid = str(guid)
        return self.SQL_EDO_CONNECTION.execute_query(ds_queries.get_package_info_by_guid_query % (guid, guid))

    def get_block_info(self, purchase_number, inn):
        return self.SQL_EDO_CONNECTION.execute_query(ds_queries.get_block_info_query % (str(purchase_number),
                                                                                        str(inn)),
                                                     dicted=True)



