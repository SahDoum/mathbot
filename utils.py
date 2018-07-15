import datetime
import time

from models import IUMCourse, Subscription, SubscriptionChat
from settings import IUMURL

from telebot import types


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


def get_subscriptions_keyboard(chat_id):
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


def get_unsubscriptions_keyboard(chat_id):
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


def sheets_updater(bot):
    while True:
        send_new_sheets(bot)
        t = datetime.datetime.now()
        time_str = t.strftime('%H/%M/')
        print(time_str + ' Sheets updated')
        time.sleep(60*60)


def send_new_sheets(bot):
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
            send_sheet_to(bot, sub.chat.chat_id, cr, extra_caption='Новый листочек по предмету:\n')  # (link, name)


def send_sheet_to(bot, chat_id, course, extra_caption=''):
    last_homework = course.get_last_homework()
    caption = extra_caption + course.name + ': ' + last_homework[1]
    bot.send_document(chat_id, last_homework[0], caption=caption)
