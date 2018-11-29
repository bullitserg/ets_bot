# python-telegram-bot

from telegram.ext import Updater, CommandHandler, RegexHandler, CallbackQueryHandler, MessageHandler, Filters
from config import *
from bot_handlers import command_handlers, callback_handlers, text_handlers, error_handlers
import jobs


def main():
    updater = Updater(TOKEN, base_url='https://api.aglnn.ru/bot')
    job_queue = updater.job_queue

    # ADD HANDLERS
    updater.dispatcher.add_error_handler(error_handlers.error_handler)
    updater.dispatcher.add_handler(RegexHandler(authorisation_regexp, text_handlers.authorisation_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, text_handlers.text_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_handlers.callback_dialog_handler, pattern='dialog_.*'))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_handlers.callback_query_handler))
    updater.dispatcher.add_handler(CommandHandler('start', command_handlers.start_handler))
    updater.dispatcher.add_handler(CommandHandler('exit', command_handlers.exit_handler))
    updater.dispatcher.add_handler(CommandHandler('help', command_handlers.help_handler))
    updater.dispatcher.add_handler(CommandHandler('menu', command_handlers.menu_handler))
    updater.dispatcher.add_handler(CommandHandler('repeat', command_handlers.repeat_handler))
    updater.dispatcher.add_handler(CommandHandler('about', command_handlers.about_handler))

    # ADD JOBS
#    job_queue.run_repeating(jobs.check_nagios, interval=nagios_check_interval, first=0)
#    job_queue.run_repeating(jobs.check_monitoring, interval=monitoring_check_interval, first=0)
    job_queue.run_repeating(jobs.unlogin_by_timeout, interval=unlogin_timeout, first=0)
    updater.start_polling(poll_interval=poll_interval)
    updater.idle()

if __name__ == '__main__':
    main()
