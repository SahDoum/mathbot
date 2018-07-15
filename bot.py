import threading

from settings import API_TOKEN, LOGGING_LEVEL
from text_messages import text_messages
from models import SubscriptionChat, Subscription, IUMCourse
from utils import get_subscription_menu_keyboard, get_subscriptions_keyboard, get_unsubscriptions_keyboard, \
    get_course_args, sheets_updater

import telebot
from telebot import types
from peewee import DoesNotExist

bot = telebot.TeleBot(API_TOKEN)
logger = telebot.logger
logger.setLevel(LOGGING_LEVEL)


@bot.message_handler(commands=['start', 'help'])
def cmd_welcome(message: telebot.types.Message):
    bot.reply_to(message, text_messages['help'])


@bot.message_handler(commands=['links'])
def cmd_links(message: telebot.types.Message):
    bot.reply_to(message, text_messages['help'])


@bot.message_handler(commands=['lib'])
def cmd_lib(message: telebot.types.Message):
    reply_keyboard = None
    bot.reply_to(message, 'Список каталогов:', reply_markup=reply_keyboard)


@bot.message_handler(commands=['set'])
def cmd_set(message):
    chat_id = message.chat.id

    try:
        SubscriptionChat.get(id=chat_id)
    except DoesNotExist:
        if hasattr(message.chat, 'title') and message.chat.title is not None:
            chat_title = message.chat.title
        else:
            chat_title = message.from_user.first_name

        SubscriptionChat.create(chat_id=chat_id, chat_title=chat_title)

    keyboard = get_subscription_menu_keyboard()
    bot.reply_to(message, 'Выберите действие с подписками на листочки в *этом* чате:',
                 parse_mode='Markdown', reply_markup=keyboard)


@bot.message_handler(commands=['add_course'])
def cmd_add_course(message):
    text = 'Формат:\n' \
           'url\n' \
           'name\n' \
           'lecturers\n' \
           'place\n' \
           'program_url\n' \
           'timetable wday|hs|ms|he|me'

    bot.reply_to(message, text)
    bot.register_next_step_handler(message, add_course)


def add_course(message):
    lines = message.text.splitlines()
    course_args = get_course_args(lines)
    if course_args:
        IUMCourse.create(**course_args)
    else:
        bot.reply_to(message, 'Извините, неправильный формат данных')


@bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu')
def subscription_menu(callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    text = 'Выберите действие с подписками на листочки в *этом* чате:'
    keyboard = get_subscription_menu_keyboard()

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu_close')
def menu_close(callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    text = 'Завершено.'

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu_set')
def set_subscription(callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    text = 'Выберите курс на листочки которого вы хотите подписаться в *этом* чате:'
    keyboard = get_subscriptions_keyboard(chat_id)

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu_unset')
def set_subscription(callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    text = 'Выберите курс на листочки которого вы хотите отписаться в *этом* чате:'
    keyboard = get_unsubscriptions_keyboard(chat_id)

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.split(' ')[0] == 'set')
def set_subscription(callback_query):
    course_id = int(callback_query.data.split(' ')[1])
    message = callback_query.message
    chat_id = message.chat.id
    course = IUMCourse.get(IUMCourse.id == course_id)
    chat = SubscriptionChat.get(SubscriptionChat.chat_id == chat_id)
    sub = Subscription()
    sub.chat = chat
    sub.course=course
    sub.save(force_insert=True)

    keyboard = types.InlineKeyboardMarkup()
    button_menu = types.InlineKeyboardButton(
        text='Вернуться в меню',
        callback_data='menu'
    )
    keyboard.add(button_menu)
    bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text='Подписка успешно установлена!')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message.message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.split(' ')[0] == 'unset')
def unset_subscription(callback_query):
    course_id = int(callback_query.data.split(' ')[1])
    message = callback_query.message
    chat_id = message.chat.id
    subs = Subscription.select()\
                       .join(IUMCourse)\
                       .switch(Subscription)\
                       .join(SubscriptionChat)\
                       .where(SubscriptionChat.chat_id == chat_id, IUMCourse.id == course_id)

    for sub in subs:
        sub.delete_instance()

    keyboard = types.InlineKeyboardMarkup()
    button_menu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    keyboard.add(button_menu)

    bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text='Подписка удалена!')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message.message_id, reply_markup=keyboard)


if __name__ == '__main__':
    t = threading.Thread(target=sheets_updater, args=(bot,))
    t.daemon = True
    t.start()

    bot.polling()


