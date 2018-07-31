import datetime
import time
from math import ceil

from models import IUMCourse, Subscription, SubscriptionChat, Book, Catalog
from settings import IUMURL, API_TOKEN, LOGGING_LEVEL, CHANNEL_NAME

import telebot
from telebot import types

bot = telebot.TeleBot(API_TOKEN, threaded=False)
logger = telebot.logger
logger.setLevel(LOGGING_LEVEL)


# Reply markup constructors
def get_subscription_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    set_button = types.InlineKeyboardButton(
        text='Добавить подписку',
        callback_data='menu_set'
    )
    unset_button = types.InlineKeyboardButton(
        text='Отписаться от рассылки',
        callback_data='menu_unset'
    )
    close_button = types.InlineKeyboardButton(
        text='Завершить',
        callback_data='menu_close'
    )

    keyboard.row(set_button)
    keyboard.row(unset_button)
    keyboard.row(close_button)

    return keyboard


def get_subscriptions_submenu_keyboard(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    courses = IUMCourse.select()
    for cr in courses:
        subs = Subscription.select()\
                           .join(IUMCourse)\
                           .switch(Subscription)\
                           .join(SubscriptionChat)\
                           .where(SubscriptionChat.chat_id == chat_id, Subscription.course == cr)
        if len(subs) == 0:
            title = 'Подписатся на '
            callback = 'set ' + str(cr.id)

            button = types.InlineKeyboardButton(text=title + cr.name, callback_data=callback)
            keyboard.add(button)

    back_button = types.InlineKeyboardButton(text='Вернуться', callback_data='menu')
    keyboard.add(back_button)

    return keyboard


def get_unsubscriptions_submenu_keyboard(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    courses = IUMCourse.select()
    for cr in courses:
        subs = Subscription.select()\
                           .join(IUMCourse)\
                           .switch(Subscription)\
                           .join(SubscriptionChat)\
                           .where(SubscriptionChat.chat_id == chat_id, Subscription.course == cr)
        if len(subs) > 0:
            title = 'Отписаться от '
            callback = 'unset ' + str(cr.id)

            button = types.InlineKeyboardButton(text=title + cr.name, callback_data=callback)
            keyboard.add(button)

    button = types.InlineKeyboardButton(text='Вернуться', callback_data='menu')
    keyboard.add(button)

    return keyboard


def get_show_books_keyboard(page, limit=5):
    books = Book.select()
    books_on_page = books.paginate(page, limit)
    pages_count = int(ceil(books.count()/limit))
    keyboard = types.InlineKeyboardMarkup()

    text = f'Количество книг: {books.count()}\n\n'
    for i, book in enumerate(books_on_page):
        try:
            catalog_name = book.catalog.name
        except Catalog.DoesNotExist:
            catalog_name = 'Без каталога'
        text += f'Каталог: {catalog_name}\n{book.get_book_description_md()}\n'

    text += f'Страница: {page}'
    # Add buttons with page numbers
    buttons = []
    for page_number in range(1, pages_count+1):
        callback_data = f'book:{page_number}' + (':current' if page_number == page else '')
        buttons.append(types.InlineKeyboardButton(text=str(page_number), callback_data=callback_data))
    keyboard.add(*buttons)

    return text, keyboard


def get_delete_book_keyboard(book_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Удалить книгу', callback_data=f'delete_book:{book_id}'))
    return keyboard


def get_show_catalogs_keyboard(page, limit=15):
    catalogs = Catalog.select()
    catalogs_on_page = catalogs.paginate(page, limit)
    pages_count = int(ceil(catalogs.count()/limit))
    keyboard = types.InlineKeyboardMarkup()

    text = f'Количество каталогов: {catalogs.count()}\n\n'
    for i, catalog in enumerate(catalogs_on_page):
        text += f'{i+1}. {catalog.name} | Кол-во книг: {catalog.books.count()}\n'

    text += f'\nСтраница: {page}'
    # Add buttons with page numbers
    buttons = []
    for page_number in range(1, pages_count+1):
        callback_data = f'catalog:{page_number}' + (':current' if page_number == page else '')
        buttons.append(types.InlineKeyboardButton(text=str(page_number), callback_data=callback_data))

    keyboard.add(*buttons)
    return text, keyboard


# Model creation args validators
def get_course_args(lines):
    def check_timetable(timetable):
        # TODO: Clarify all related to timetable field and make input validation
        return bool(timetable)

    if len(lines) == 6:
        url, name, lecturers, place, program_url, timetable = lines

        if not all((url.startswith(IUMURL), name, lecturers, place, program_url, check_timetable(timetable))):
            return
        else:
            return {'url': url, 'name': name, 'lecturers': lecturers, 'place': place,
                    'program_url': program_url, 'timetable': timetable, 'last_subscription': ''}


def get_book_args(lines):
    if len(lines) >= 3:
        name, author, *comments = lines
        if not all((name, author, comments)):
            return
        else:
            comments_string = '\n'.join(comments)
            return {'name': name, 'author': author, 'comments': comments_string}


# Separate thread sheet updater
def sheets_updater():
    while True:
        send_new_sheets()
        t = datetime.datetime.now()
        time_str = t.strftime('%H/%M/')
        print(time_str + ' Sheets updated')
        time.sleep(60*60)


def send_new_sheets():
    courses = IUMCourse.select()
    for cr in courses:
        cr.update_homework()
        sheet = cr.get_last_homework()
        last_sheet = cr.last_subscription.rsplit('/')[-1]

        if last_sheet == sheet[1]:
            continue

        t = datetime.datetime.now()
        cr.last_subscription = t.strftime('%Y/%m/%d/%H/%M/') + sheet[1]
        cr.save()

        subscriptions = Subscription.select(Subscription, SubscriptionChat)\
                                    .join(SubscriptionChat)\
                                    .where(Subscription.course == cr)
        for sub in subscriptions:
            print('Subscription:')
            print(sub.chat_id)
            send_sheet_to(sub.chat.chat_id, cr, extra_caption='Новый листочек по предмету:\n')  # (link, name)


def send_sheet_to(chat_id, course, extra_caption=''):
    last_homework = course.get_last_homework()
    caption = extra_caption + course.name + ': ' + last_homework[1]
    bot.send_document(chat_id, last_homework[0], caption=caption)


def upload_book(message, book):
    book_description = book.get_book_description_md()

    bot.send_message(CHANNEL_NAME, book_description, parse_mode='Markdown', disable_notification=True)
    result = bot.forward_message(CHANNEL_NAME, message.chat.id, message.message_id, disable_notification=True)

    link = f'https://t.me/{CHANNEL_NAME[1:]}/{result.message_id}'
    return link


# Handler decorators
def forward_required(message_handler):
    def wrapper(message, *args, **kwargs):
        if not message.forward_from:
            bot.reply_to(message, 'Вы должны зафорвардить сообщение!')
        else:
            message_handler(message, *args, **kwargs)

    return wrapper


def private_required(message_handler):
    def wrapper(message, *args, **kwargs):
        if not message.chat.type == 'private':
            bot.reply_to(message, 'Доступно только в приватном чате!')
        else:
            message_handler(message, *args, **kwargs)

    return wrapper
