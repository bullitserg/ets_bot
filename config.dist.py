from collections import defaultdict

CONFIG = 'config.conf'
MESSAGE_PREFIX = {'OK': '✅'}

TOKEN = '***:******'
administrator_email = 'belim@etpz.ru'
bot_version = '0.5'
bot_nickname = 'ets_bender_bot'
authorisation_regexp = "^pass [0-9]{4}$"
registered_chat_id = [********]
log_format = '[%(asctime)s]# %(levelname)-8s   %(message)s'
nagios_check_interval = 10
monitoring_check_interval = 15
clear_waits_time = 1
unlogin_timeout = 60
message_max_len = 500

nagios_web_page = '''http://nagios-m1.etp-micex.ru/nagios/cgi-bin/status.cgi?hostgroup=all&style=detail&servicestatustypes=28&hoststatustypes=15'''
nagios_local_page = 'C:/Users/belim/PycharmProjects/nagios.html'
nagios_login = 'monitoring'
nagios_password = 'monitoring'
critical_class = 'statusBGCRITICAL'
warning_class = 'statusBGWARNING'
bad_hosts = []
bad_service = ['Check NETIS Integration']

reports_procedure_requests_dir = 'C:/Users/belim/PycharmProjects/ets_bot/data/reports/reports_procedure_requests'
reports_fine_check_dir = 'C:/Users/belim/PycharmProjects/ets_bot/data/reports/reports_fine_check'
ds_status_dir = 'C:/Users/belim/PycharmProjects/ets_bot/data/reports/ds_status'

# создаем словари, заполняемые на любую глубину по вызову ключа
tree = lambda: defaultdict(tree)
USER_DATA = defaultdict(tree)
