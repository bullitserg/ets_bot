from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

custom_keyboard_standard = [['/menu', '/repeat'], ['/about', '/help', '/exit']]

# KEYBOARDS
reply_markup_keyboard_standard = ReplyKeyboardMarkup(custom_keyboard_standard, resize_keyboard=True)
reply_markup_keyboard_off = ReplyKeyboardRemove()
