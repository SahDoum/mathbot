from utils import bot
from text_messages import text_messages
from models import User

import telebot.types


def cmd_welcome(message: telebot.types.Message):
    User.insert(user_id=message.from_user.id, first_name=message.from_user.first_name,
                role='User').on_conflict_ignore().execute()
    bot.reply_to(message, text_messages['help'])


def cmd_links(message: telebot.types.Message):
    bot.reply_to(message, text_messages['help'])
