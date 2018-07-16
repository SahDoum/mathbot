from .admin import cmd_set_admin, cmd_set_moder
from .book import cmd_add_book, inline_search_book
from .catalog import cmd_lib, cmd_add_catalog
from .courses import cmd_add_course
from .default import cmd_welcome, cmd_links

from .subscriptions import cmd_set, cb_subscription_menu, cb_subscription_menu_close, \
    cb_subscription_menu_set_pressed, cb_subscription_menu_unset_pressed, cb_set_subscription, \
    cb_unset_subscription

__all__ = [
           # Simple administartion commands
           'cmd_set_admin', 'cmd_set_moder',
           # Cmds for adding books and inline search handler
           'cmd_add_book', 'inline_search_book',
           # Cmds for adding catalogs and launching catalog menu
           'cmd_lib', 'cmd_add_catalog',
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
