#!/usr/bin/python3

'''
IUMCourse class which holds all information of course and implements
homework updating.
'''
import urllib.request
from peewee import *
from __init__ import bot, commands_handler
from telebot import types
import datetime
import time

IUMURL = "http://ium.mccme.ru/"
database = SqliteDatabase('database.db', **{})


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


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

''' 
def main():
    analiz = IUMCourse()
    analiz.url = 'http://ium.mccme.ru/f17/f17-analiz1.html'
    analiz.name = 'Анализ-1'
    analiz.updateHW()

    print(analiz.getLastHW()[0])

    return 0


if __name__ == "__main__":
    main()
    
if __name__ == "__main__":
    courses = IUMCourse.select()
    for cr in courses:
        print('S')
        print(cr.name)
        print(cr.last_subscription)
        cr.last_subscription = ''
        cr.save()
'''


def listochki_updater():
    while(True):
        send_new_listochki()
        time.sleep(60*60)
        print('Listochki updated')


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
            send_listochek_to(sub.chat.chat_id, cr) # <- (ссылка, название)


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
    send_listochek_to(chat_id, course)


def send_listochek_to(chat_id, course):
    lastHW = course.getLastHW()
    caption = course.name + ': ' + lastHW[1]
    bot.send_document(chat_id, lastHW[0], caption=caption)


@bot.message_handler(func=commands_handler(['/set']))
def set_subscription(message):
    chat_id = message.chat.id

    try:
        SubscriptionChat.get(SubscriptionChat.id == chat_id)
    except DoesNotExist:
        if hasattr(message.chat, 'title') and message.chat.title is not None:
            chat_title = message.chat.title
        else:
            chat_title = message.from_user.first_name
        SubscriptionChat.create(chat_id=chat_id, chat_title=chat_title)

    keyboard = subscription_keyboard(chat_id)
    bot.reply_to(message, 'Оформите подписки на листочки НМУшных курсов:', reply_markup=keyboard)


def subscription_keyboard(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    courses = IUMCourse.select()
    for cr in courses:
        subs = Subscription.select()\
                           .join(IUMCourse)\
                           .switch(Subscription)\
                           .join(SubscriptionChat)\
                           .where(SubscriptionChat.chat_id == chat_id, Subscription.course == cr)
        if len(subs) > 0:
            title = '✅'
            callback = 'unset ' + str(cr.id)
        else:
            title = ''
            callback = 'set ' + str(cr.id)
        # print('callback:')
        # print(chat_id)
        # print(cr.id)

        button = types.InlineKeyboardButton(
            text=title + cr.name,
            callback_data=callback
        )
        keyboard.add(button)
    return keyboard


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
    keyboard = subscription_keyboard(chat_id)
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

    keyboard = subscription_keyboard(chat_id)
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message.message_id, reply_markup=keyboard)


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
