from models import User, Action
from utils import bot, forward_required, private_required, user_required

from telebot import types


@private_required
@user_required('Creator')
def cmd_set_admin(message: types.Message, user):
    Action.create(action='Called /set_admin', user=user)
    bot.reply_to(message, 'Перешлите сообщение назначаемого админа')
    bot.register_next_step_handler(message, set_admin, user)


@private_required
@user_required('Creator')
def cmd_set_moder(message: types.Message, user):
    Action.create(action='Called /set_moder', user=user)
    bot.reply_to(message, 'Перешлите сообщение назначаемого модератора')
    bot.register_next_step_handler(message, set_moder, user)


# Next step handlers
@forward_required
def set_admin(message: types.Message, user):
    user_id = message.forward_from.id
    first_name = message.forward_from.first_name
    username = message.forward_from.username
    User.insert(user_id=user_id, username=username,
                first_name=first_name, role='Admin').on_conflict_replace().execute()

    action_body = f'| Added Admin {user_id} {"(@%s)" % username if username else ""}'
    Action.create(action='Set admin', user=user, body=action_body)

    bot.reply_to(message, 'Админ добавлен')


@forward_required
def set_moder(message: types.Message, user):
    user_id = message.forward_from.id
    first_name = message.forward_from.first_name
    username = message.forward_from.username

    User.insert(user_id=user_id, username=username,
                first_name=first_name, role='Moder').on_conflict_replace().execute()

    action_body = f'| Added Moder {user_id} {"(@%s)" % username if username else ""}'
    Action.create(action='Set moder', user=user, body=action_body)

    bot.reply_to(message, 'Модератор добавлен')
