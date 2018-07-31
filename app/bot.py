import threading
import logging

from utils import sheets_updater, bot
from settings import WEBHOOK_URL, WEBHOOK_URL_PATH, PUB_CERT
from commands import *

from flask import Flask, request, abort, jsonify
from telebot import types

# === Flask settings and routes ===
app = Flask(__name__)


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        logging.error(json_string)
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@app.route(f'{WEBHOOK_URL_PATH}/set', methods=['GET'])
def set_webhook():
    cert = open(PUB_CERT, 'r') if PUB_CERT else None
    response = bot.set_webhook(WEBHOOK_URL, cert)
    return str(response)


@app.route(f'{WEBHOOK_URL_PATH}/delete', methods=['GET'])
def delete_webhook():
    response = bot.delete_webhook()
    return str(response)


@app.route(f'{WEBHOOK_URL_PATH}/info', methods=['GET'])
def get_info():
    return jsonify(str(bot.get_webhook_info()))


@app.before_first_request
def run_sheets_updater():
    t = threading.Thread(target=sheets_updater, args=())
    t.daemon = True
    t.start()


# === Message handlers ===

# Default commands
bot.message_handler(commands=['start', 'help'])(cmd_welcome)
bot.message_handler(commands=['links'])(cmd_links)

# Subscription menu initialization command
bot.message_handler(commands=['set'])(cmd_set)

# Add course command
bot.message_handler(commands=['add_course'])(cmd_add_course)

# Catalog commands
bot.message_handler(commands=['lib', 'lit', 'catalog'])(cmd_lib)
bot.message_handler(commands=['add_catalog'])(cmd_add_catalog)

# Admin commands
bot.message_handler(commands=['set_admin'])(cmd_set_admin)
bot.message_handler(commands=['set_moder'])(cmd_set_moder)

# Book commands
bot.message_handler(commands=['add_book', 'add'])(cmd_add_book)
bot.message_handler(commands=['show_books', 'show'])(cmd_show_books)


# === Callback handlers ===

# Subscriptions
bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu')(
    cb_subscription_menu  # Show subscription menu
)
bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu_close')(
    cb_subscription_menu_close  # Close menu
)
bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu_set')(
    cb_subscription_menu_set_pressed  # Set button pressed in subscription menu
)
bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu_unset')(
    cb_subscription_menu_unset_pressed  # Unset button pressed in subscription menu
)
bot.callback_query_handler(func=lambda callback_query: callback_query.data.split(' ')[0] == 'set')(
    cb_set_subscription  # Entry selected in set subscription submenu
)
bot.callback_query_handler(func=lambda callback_query: callback_query.data.split(' ')[0] == 'unset')(
    cb_unset_subscription  # Entry selected in unset subscription submenu
)

# Books
bot.callback_query_handler(func=lambda callback_query: callback_query.data.split(':')[0] == 'book')(
    cb_books_page  # Show books menu
)

bot.callback_query_handler(func=lambda callback_query: callback_query.data.split(':')[0] == 'delete_book')(
    cb_delete_book  # Delete book
)


# Inline searching handler
bot.inline_handler(lambda query: bool(query.query))(inline_search_book)

if __name__ == '__main__':
    t = threading.Thread(target=sheets_updater)
    t.daemon = True
    t.start()

    bot.polling()
