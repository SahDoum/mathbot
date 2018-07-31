from models import User
from utils import bot, forward_required, private_required

from telebot import types
from peewee import DoesNotExist


@private_required
def cmd_set_admin(message: types.Message):
    try:
        user = User.get(message.from_user.id)
    except DoesNotExist:
        return

    if not user.can_assign_admin():
        return

    bot.reply_to(message, 'Перешлите сообщение назначаемого админа')
    bot.register_next_step_handler(message, set_admin)


@private_required
def cmd_set_moder(message: types.Message):
    try:
        user = User.get(message.from_user.id)
    except DoesNotExist:
        return

    if not user.can_assign_admin():
        return

    bot.reply_to(message, 'Перешлите сообщение назначаемого модератора')
    bot.register_next_step_handler(message, set_moder)


# Next step handlers
@forward_required
def set_admin(message: types.Message):
    user_id = message.forward_from.id
    first_name = message.forward_from.first_name
    User.insert(user_id=user_id, first_name=first_name, role='Admin').on_conflict_replace().execute()
    bot.reply_to(message, 'Админ добавлен')


@forward_required
def set_moder(message: types.Message):
    user_id = message.forward_from.id
    first_name = message.forward_from.first_name
    User.insert(user_id=user_id, first_name=first_name, role='Moder').on_conflict_replace().execute()
    bot.reply_to(message, 'Модератор добавлен')
