import threading

from utils import sheets_updater, bot
from commands import *

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
    t = threading.Thread(target=sheets_updater, args=())
    t.daemon = True
    t.start()

    bot.polling()
