#!/usr/bin/python3

'''
IUMCourse class which holds all information of course and implements
homework updating.
'''
import urllib.request
from peewee import *
from models import BaseModel
from __init__ import bot, commands_handler
from telebot import types
import datetime
import time

IUMURL = "http://ium.mccme.ru/"


class SubscriptionChat(BaseModel):
    chat_id = IntegerField()
    chat_title = CharField()


class IUMCourse(BaseModel):
    url = CharField()
    name = CharField()
    lecturers = CharField()
    place = CharField()
    program_url = CharField()
    timetable = CharField() # Хранится в формате wday|hs|ms|he|me
    last_subscription = CharField() # В формате %Y/%m/%d/%H/%M/Название листочка

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hwlist = []

    def getHWList(self):
        return self.hwlist

    def getLastHW(self):
        return self.hwlist[-1]

    def updateHW(self):
        opener = urllib.request.FancyURLopener({})
        f = opener.open(self.url)
        content = f.read()
        content = content.decode('koi8-r')

        ls = content.rfind("[<a")
        le = content.rfind("a>]")
        if ls == -1 or le == -1: return
        l = content[ls + 1:le + 2]
        l = l.replace('\n', ' ')

        self.hwlist = []
        rawlist = l.split("|")
        for rs in rawlist:
            rslist = rs.split('"')
            self.hwlist.append((IUMURL + rslist[1][2:], rslist[2][1:-4])) # убираем лишние символы


class Subscription(BaseModel):
    chat = ForeignKeyField(SubscriptionChat)
    course = ForeignKeyField(IUMCourse)


def listochki_updater():
    while(True):
        send_new_listochki()
        t = datetime.datetime.now()
        time_str = t.strftime('%H/%M/')
        print(time_str + ' Listochki updated')
        time.sleep(60*60)


# @bot.message_handler(func=commands_handler(['/newsecret'])) # '/otveti_na_listo4ki'
def send_new_listochki():
    courses = IUMCourse.select()
    for cr in courses:
        cr.updateHW()
        listochek = cr.getLastHW()
        last_listochek = cr.last_subscription.rsplit('/')[-1]

        if last_listochek == listochek[1]: continue
        t = datetime.datetime.now()
        cr.last_subscription = t.strftime('%Y/%m/%d/%H/%M/') + listochek[1]
        cr.save()

        subscriptions = Subscription.select(Subscription, SubscriptionChat)\
                                    .join(SubscriptionChat)\
                                    .where(Subscription.course == cr)
        for sub in subscriptions:
            print('Subscription:')
            print(sub.chat_id)
            send_listochek_to(sub.chat.chat_id, cr, extra_caption='Новый листочек по предмету:\n') # <- (ссылка, название)


'''
@bot.message_handler(func=commands_handler(['/otveti_na_listo4ki'])) # '/otveti_na_listo4ki'
def send_last_listochek(message):
    chat_id = message.chat.id
    subscriptions = Subscription.select(Subscription) \
                    .join(SubscriptionChat)\
                    .switch(Subscription)\
                    .join(IUMCourse) \
                    .where(SubscriptionChat.chat_id == chat_id)\
                    .order_by(IUMCourse.last_subscription)

    if len(subscriptions) == 0: return
    subscription = subscriptions[-1]

    if not subscription: return

    course = subscription.course
    course.updateHW()
    send_listochek_to(chat_id, course, extra_caption='Последний листочек из подписок чата:\n')
'''


def send_listochek_to(chat_id, course, extra_caption=''):
    lastHW = course.getLastHW()
    caption = extra_caption + course.name + ': ' + lastHW[1]
    bot.send_document(chat_id, lastHW[0], caption=caption)


    # ---- ----
    # SUBSCRIPTIONS
    # ---- ----


@bot.message_handler(func=commands_handler(['/set']))
def set_subscription(message):
    print('1')
    chat_id = message.chat.id

    try:
        SubscriptionChat.get(SubscriptionChat.id == chat_id)
    except DoesNotExist:
        if hasattr(message.chat, 'title') and message.chat.title is not None:
            chat_title = message.chat.title
        else:
            chat_title = message.from_user.first_name
        SubscriptionChat.create(chat_id=chat_id, chat_title=chat_title)

    keyboard = menu_keyboard(chat_id)
    bot.reply_to(message,
                 'Выберите действие с подписками на листочки в *этом* чате:',
                 parse_mode='Markdown',
                 reply_markup=keyboard
                 )


@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def menu(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    text = 'Выберите действие с подписками на листочки в *этом* чате:'
    keyboard = menu_keyboard(chat_id)

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'menu_close')
def menu_close(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    text = 'Завершено.'

    # bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)


@bot.callback_query_handler(func=lambda call: call.data == 'menu_set')
def set_subscription(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    text = 'Выберите курс на листочки которого вы хотите подписаться в *этом* чате:'
    keyboard = subscriptions_keyboard(chat_id)

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'menu_unset')
def set_subscription(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    text = 'Выберите курс на листочки которого вы хотите отписаться в *этом* чате:'
    keyboard = unsubscriptions_keyboard(chat_id)

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode='Markdown')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'set')
def set_subscription(call):
    course_id = int(call.data.split(' ')[1])
    message = call.message
    chat_id = message.chat.id
    course = IUMCourse.get(IUMCourse.id == course_id)
    chat = SubscriptionChat.get(SubscriptionChat.chat_id == chat_id)
    sub = Subscription()
    sub.chat = chat
    sub.course=course
    sub.save(force_insert=True)

    keyboard = types.InlineKeyboardMarkup()
    button_menu = types.InlineKeyboardButton(
        text='Вернуться в меню',
        callback_data='menu'
    )
    keyboard.add(button_menu)
    bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text='Подписка успешно установлена!')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message.message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'unset')
def unset_subscription(call):
    course_id = int(call.data.split(' ')[1])
    message = call.message
    chat_id = message.chat.id
    subs = Subscription.select()\
                       .join(IUMCourse)\
                       .switch(Subscription)\
                       .join(SubscriptionChat)\
                       .where(SubscriptionChat.chat_id == chat_id, IUMCourse.id == course_id)

    for sub in subs:
        sub.delete_instance()

    keyboard = types.InlineKeyboardMarkup()
    button_menu = types.InlineKeyboardButton(
        text='Вернуться в меню',
        callback_data='menu'
    )
    keyboard.add(button_menu)
    bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text='Подписка удалена!')
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message.message_id, reply_markup=keyboard)


    # ---- ----
    # KEYBOARDS
    # ---- ----


def menu_keyboard(chat_id):
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

    keyboard.add(set_button)
    keyboard.add(unset_button)
    keyboard.add(close_button)

    return keyboard


def subscriptions_keyboard(chat_id):
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

            button = types.InlineKeyboardButton(
                text=title + cr.name,
                callback_data=callback
            )
            keyboard.add(button)

    button = types.InlineKeyboardButton(
        text='Вернуться',
        callback_data='menu'
    )
    keyboard.add(button)

    return keyboard


def unsubscriptions_keyboard(chat_id):
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

            button = types.InlineKeyboardButton(
                text=title + cr.name,
                callback_data=callback
            )
            keyboard.add(button)

    button = types.InlineKeyboardButton(
        text='Вернуться',
        callback_data='menu'
    )
    keyboard.add(button)

    return keyboard

    # ---- ----
    # ADD COURSE
    # ---- ----


@bot.message_handler(func=commands_handler(['/addcoursetososiska']))
def add_course_command_handler(message):
    text = 'Формат:\n' \
           'url\n' \
           'name\n' \
           'lecturers\n' \
           'place\n' \
           'program_url\n' \
           'timetable wday|hs|ms|he|me'

    bot.reply_to(message, text)
    bot.register_next_step_handler(message, add_course)


def add_course(message):
    lines = message.text.splitlines()

    course = IUMCourse()
    course.url = lines[0]
    course.name = lines[1]
    course.lecturers = lines[2]
    course.place = lines[3]
    course.program_url = lines[4]
    course.timetable = lines[5]
    course.last_subscription = ''
    course.save(force_insert=True)
