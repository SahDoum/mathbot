import threading

from utils import sheets_updater, bot
from commands import *

# Message handlers
# Default commands
bot.message_handler(commands=['start', 'help'])(cmd_welcome)
bot.message_handler(commands=['links'])(cmd_links)
bot.message_handler(commands=['lib'])(cmd_lib)

# Subscription menu initialization command
bot.message_handler(commands=['set'])(cmd_set)

# Add course command
bot.message_handler(commands=['add_course'])(cmd_add_course)


# Callback handlers
bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu')(
    subscription_menu_callback  # Show subscription menu
)
bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu_close')(
    subscription_menu_close_callback  # Close menu
)
bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu_set')(
    subscription_menu_set_pressed_callback  # Set button pressed in subscription menu
)
bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'menu_unset')(
    subscription_menu_unset_pressed_callback  # Unset button pressed in subscription menu
)
bot.callback_query_handler(func=lambda callback_query: callback_query.data.split(' ')[0] == 'set')(
    set_subscription_callback  # Entry selected in set subscription submenu
)
bot.callback_query_handler(func=lambda callback_query: callback_query.data.split(' ')[0] == 'unset')(
    unset_subscription_callback  # Entry selected in unset subscription submenu
)


if __name__ == '__main__':
    t = threading.Thread(target=sheets_updater, args=())
    t.daemon = True
    t.start()

    bot.polling()
