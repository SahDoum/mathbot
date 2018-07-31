from .admin import cmd_set_admin, cmd_set_moder
from .book import cmd_add_book, cmd_show_books, inline_search_book, cb_books_page, cb_delete_book
from .catalog import cmd_lib, cmd_add_catalog, cmd_delete_catalog, cb_catalogs_page
from .courses import cmd_add_course
from .default import cmd_welcome, cmd_links

from .subscriptions import cmd_set, cb_subscription_menu, cb_subscription_menu_close, \
    cb_subscription_menu_set_pressed, cb_subscription_menu_unset_pressed, cb_set_subscription, \
    cb_unset_subscription

__all__ = [
           # Simple administartion commands
           'cmd_set_admin', 'cmd_set_moder',
           # Cmds for adding books, inline search and callback handler
           'cmd_add_book', 'cmd_show_books', 'inline_search_book', 'cb_books_page', 'cb_delete_book',
           # Cmds for adding catalogs and launching catalog menu
           'cmd_lib', 'cmd_add_catalog', 'cmd_delete_catalog', 'cb_catalogs_page',
           # Course adding cmd
           'cmd_add_course',
           # Simple "static" cmds
           'cmd_welcome', 'cmd_links',
           # Cmd to launch subscriptions menu
           'cmd_set',
           # Callback handlers for subscriptions menu
           'cb_subscription_menu', 'cb_subscription_menu_unset_pressed', 'cb_subscription_menu_set_pressed',
           'cb_subscription_menu_close', 'cb_set_subscription', 'cb_unset_subscription'
           ]
