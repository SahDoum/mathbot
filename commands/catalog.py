from utils import bot
from text_messages import text_messages
from models import Catalog, User

import telebot.types
from peewee import DoesNotExist


def cmd_lib(message: telebot.types.Message):
    reply_keyboard = None
    bot.reply_to(message, 'Список каталогов:', reply_markup=reply_keyboard)


def cmd_add_catalog(message):
    try:
        user = User.get(user_id=message.from_user.id)
    except DoesNotExist:
        return

    if not user.can_edit():
        return

    if len(message.text.split(' ')) < 2:
        return

    cat_name = message.text.split(' ', maxsplit=1)[1]

    if cat_name:
        Catalog.get_or_create(name=cat_name)
        bot.reply_to(message, 'Новый каталог добавлен')


def callback_inline(callback_query):
    if callback_query.message:
        catalog_id = int(callback_query.data.split(' ', maxsplit=1)[1])
        dsc = Catalog.get_catalog_description(catalog_id)
        dsc += text_messages['inline_mode']
        bot.edit_message_text(chat_id=callback_query.message.chat.id,
                              message_id=callback_query.message.message_id,
                              text=dsc, parse_mode='Markdown',
                              disable_web_page_preview=True)
