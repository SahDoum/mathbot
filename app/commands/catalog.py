from utils import bot, private_required, get_show_catalogs_keyboard, user_required
from models import Catalog, User

import telebot.types
from telebot.apihelper import ApiException
from peewee import DoesNotExist


def cmd_lib(message: telebot.types.Message):
    text, reply_keyboard = get_show_catalogs_keyboard(1)
    bot.reply_to(message, text, reply_markup=reply_keyboard)


@private_required
@user_required('Admin', 'Moder', 'Creator')
def cmd_add_catalog(message: telebot.types.Message, user):
    if len(message.text.split(' ')) < 2:
        bot.reply_to(message, 'Неправильный формат ввода')

    cat_name = message.text.split(' ', maxsplit=1)[1]

    if cat_name:
        Catalog.get_or_create(name=cat_name)
        bot.reply_to(message, 'Новый каталог добавлен')


@private_required
@user_required('Admin', 'Moder', 'Creator')
def cmd_delete_catalog(message: telebot.types.Message, user):
    if len(message.text.split(' ')) < 2:
        bot.reply_to(message, 'Неправильный формат ввода')

    cat_name = message.text.split(' ', maxsplit=1)[1]

    try:
        catalog = Catalog.get(name=cat_name)
        catalog.delete_instance()
        bot.reply_to(message, 'Каталог успешно удалён!')
    except Catalog.DoesNotExist:
        bot.reply_to(message, 'Такого каталога не существует. Введите /lib чтобы посмотреть доступные каталоги')


# Callback handler
def cb_catalogs_page(callback_query):
    cb_args = callback_query.data.split(':')
    if len(cb_args) == 2 and cb_args[1].isdigit():
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
        page = int(cb_args[1])
        text, keyboard = get_show_catalogs_keyboard(page)
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=keyboard, parse_mode='Markdown')
        except ApiException:
            pass

    elif len(cb_args) == 3 and cb_args[2] == 'current':
        bot.answer_callback_query(callback_query.id, 'You are already on this page!')
