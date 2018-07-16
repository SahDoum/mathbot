import telebot.types
from utils import bot

from text_messages import text_messages


def cmd_welcome(message: telebot.types.Message):
    bot.reply_to(message, text_messages['help'])


def cmd_links(message: telebot.types.Message):
    bot.reply_to(message, text_messages['help'])


def cmd_lib(message: telebot.types.Message):
    reply_keyboard = None
    bot.reply_to(message, 'Список каталогов:', reply_markup=reply_keyboard)
