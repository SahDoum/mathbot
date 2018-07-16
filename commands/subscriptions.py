from models import SubscriptionChat, IUMCourse, Subscription
from utils import get_subscription_menu_keyboard, get_subscriptions_submenu_keyboard, \
    get_unsubscriptions_submenu_keyboard, bot

from peewee import DoesNotExist
from telebot import types


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


# Callback handlers
def cb_subscription_menu(callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    text = 'Выберите действие с подписками на листочки в *этом* чате:'
    keyboard = get_subscription_menu_keyboard()

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


def cb_subscription_menu_close(callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    text = 'Завершено.'

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)


def cb_subscription_menu_set_pressed(callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    text = 'Выберите курс на листочки которого вы хотите подписаться в *этом* чате:'
    keyboard = get_subscriptions_submenu_keyboard(chat_id)

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


def cb_subscription_menu_unset_pressed(callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    text = 'Выберите курс на листочки которого вы хотите отписаться в *этом* чате:'
    keyboard = get_unsubscriptions_submenu_keyboard(chat_id)

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


def cb_set_subscription(callback_query):
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


def cb_unset_subscription(callback_query):
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
