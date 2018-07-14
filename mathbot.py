import sys
import time
import threading
import telebot
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout

from telebot import types

from __init__ import bot, commands_handler, BOT_NAME, statistics
from catalog_manager import CatalogManager
from models.users import MathUser

# from catalog import engine
# import time

'''
# Handle all
@bot.message_handler(content_types=['text'])
def send_welcome(message):
    print('1')
'''

import models.course

CHANNEL_NAME = '@mathcatalog'

text_messages = {
    'help':
        'Мне надоело каждый раз, когда спрашивают, что почитать по матану или линейке, '
        'скидывать одни и те же книги, поэтому я запилил этого бота и каталог @mathcatalog\n\n'
        'Для того, чтобы начать пользоваться — вызовите любую команду: /lib /lit /catalog\n'
        'Или набирайте @sosiska_v_teste_bot в inline-режиме и затем ищите нужную вам книгу.\n'
        'Если вы готовы помочь с наполнением каталога, пишите мне: @AChekhonte\n',

    'admin':
        'Используйте следующие команды:\n'
        '/addcatalog <название каталога> — для добавления нового каталога (все названия уникальны)\n'
        '/add — для добавления новой книги \n'
        '/edit — для редактирования \n',

    'links':
        'Список чатов в Телеграм:\n'
        '1. [НМУ 2017+]'
        '(https://t.me/ium2017)\n'
        '2. [НМУ Геометрия-1]'
        '(https://t.me/ium_geom)\n'
        '3. [НМУ Матан-1]'
        '(https://t.me/ium_analysis)\n'
        '4. [НМУ Алгебра-1]'
        '(https://t.me/ium_algebra)\n'
        '5. [НМУ Топология-1]'
        '(https://t.me/joinchat/A5wx2gxJoquD_1JuCLAr7w)\n'
        '6. [НМУ Задачи и только задачи]'
        '(https://t.me/ium_zadachi)\n'
        '7. [Discord Конференция по задачам]'
        '(https://discord.gg/kHSBukP)\n\n'
        '8. [Infernal Math]'
        '(https://t.me/joinchat/AAAAAEFHT_BkBsc_HgiTvg)\n'
        '9. [Канал МЦНМО]'
        '(https://t.me/cme_channel)\n'
        '10. [Геометрия-канал]'
        '(https://t.me/geometrykanal)\n'
        '11. [Геометрический чатик]'
        '(https://t.me/geometrychat)\n'
        '12. [Флудилка Мехмата]'
        '(https://t.me/mechmath)\n'
        '13. [МехМат МГУ 2017]'
        '(https://t.me/mechmath2017)\n'
        '14. [Канал Сосиска в тесте]'
        '(https://t.me/mathcatalog)\n',

    'inline_mode':
        '_Попробуйте набрать в поле для сообщения_ @sosiska\_v\_teste\_bot '
        '_и название/автора/раздел книги, чтобы быстро скинуть её в чат._'
}


    # ---- ---- ---- ---- ----
    # ---- BASIC COMMANDS ----
    # ---- ---- ---- ---- ----


# Handle '/start'
@bot.message_handler(func=commands_handler(['/start', '/help']))
def send_welcome(message):
    bot.send_message(message.chat.id, text_messages['help'])


# Handle '/links'
@bot.message_handler(func=commands_handler(['/links']))
def links(message):
    bot.send_message(message.chat.id, text_messages['links'], disable_web_page_preview=True, parse_mode='Markdown')


# Handle '/admin'
@bot.message_handler(commands=['admin'])
def admininfo(message):
    usr = MathUser.log_by_message(message)
    if not usr.can_browse_commands():
        return
    bot.send_message(message.chat.id, text_messages['admin'])


"""
@bot.message_handler(commands=['gif'])
def gif(message):
    bot.send_document(message.chat.id, 'https://t.me/mechmath/118524', reply_to_message_id=message.message_id)

@bot.message_handler(content_types=["document"])
def doc(message):
    bot.send_message(message.from_user.id, str(message))

@bot.message_handler(content_types=["text"])
def msg(message):
    bot.send_message(message.from_user.id, str(message.entities[0].type))

"""

    # ---- ---- ---- ---- ----
    # ---- SUBSCRIPTIONS ----
    # ---- ---- ---- ---- ----

# ---- ---- ---- ----
    # ---- Просмотр ----
    # ---- ---- ---- ----


# Handle '/lit'
@bot.message_handler(func=commands_handler(['/lib', '/catalog', '/lit']))
def catalog_list(message):
    keyboard = CatalogManager.catalogs_button_keyboard()
    bot.reply_to(message, "Список каталогов:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'catalog')
def callback_inline(call):
    if call.message:
        cat_id = int(call.data.split(' ', maxsplit=1)[1])
        dsc = CatalogManager.catalog_dsc(cat_id)
        dsc += text_messages['inline_mode']
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=dsc, parse_mode='Markdown',
                              disable_web_page_preview=True)

    # ---- ---- ----
    # ---- EDIT ----
    # ---- ---- ----


# Handle '/edit'
@bot.message_handler(func=commands_handler(['/edit']))
def edit(message):
    usr = MathUser.log_by_message(message)
    if not usr.can_edit():
        return

    bot.send_message(message.chat.id, "Редактирование:")

    gen = CatalogManager.edit_catalogs_generator()
    for m in gen:
        bot.send_message(message.chat.id, m['text']+' ', parse_mode='Markdown', reply_markup=m['buttons'])

    # ---- catalogs edit ----


# Handle deletecatalog button
@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'deletecatalog')
def deletecatalog_callback_inline(call):
    if call.message:
        usr = MathUser.log_by_callback(call)
        if not usr.can_delete_catalog():
            return
        cat_id = call.data.split(' ', maxsplit=1)[1]
        keyboard = types.InlineKeyboardMarkup()
        del_button = types.InlineKeyboardButton(text=u"Удалить", callback_data='confirmdeletebatalog '+cat_id)
        keyboard.add(del_button)
        bot.send_message(call.message.chat.id, 'Подтвердите удаление каталога', reply_markup=keyboard)


# Handle confirm_deletebcatalog button
@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'confirmdeletebatalog')
def confirm_deletecatalog_callback_inline(call):
    if call.message:
        cat_id = int(call.data.split(' ', maxsplit=1)[1])
        CatalogManager.delete_catalog(cat_id)
        bot.send_message(call.message.chat.id, 'Каталог удален')


# Handle editcatalog button
@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'editcatalog')
def editcatalog_callback_inline(call):
    if call.message:
        cat_id = int(call.data.split(' ', maxsplit=1)[1])
        CatalogManager.save_cat_id(cat_id, call.message.chat.id)
        bot.send_message(call.message.chat.id, 'Введите новое название каталога или прервите командой /break:')
        bot.register_next_step_handler(call.message, rename_catalog)


def rename_catalog(message):
    if message.text[0] == '/':
        return
    cat_id = CatalogManager.get_cat_id(message.chat.id)
    new_name = message.text
    CatalogManager.rename_catalog(cat_id, new_name)
    bot.reply_to(message, 'Каталог переименован')


# Handle opencatalog button
@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'edit')
def edit_callback_inline(call):
    if call.message:
        cat_id = int(call.data.split(' ', maxsplit=1)[1])
        gen = CatalogManager.edit_books_generator(cat_id)

        for m in gen:
            bot.send_message(call.message.chat.id, m['text'], parse_mode='Markdown', reply_markup=m['buttons'])

    # ---- books edit ----


# Handle deletebook button
@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'deletebook')
def del_book_callback_inline(call):
    book_id = int(call.data.split(' ')[1])
    CatalogManager.delete_book(book_id)
    bot.edit_message_text('Книга удалена', call.message.chat.id, call.message.message_id, reply_markup=None)


# Handle editbook button
@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'editbook')
def edit_book_callback_inline(call):
    #bot.send_message(call.message.chat.id, '')
    book_id = int(call.data.split(' ')[1])
    CatalogManager.get_edit_book(call.message.chat.id, book_id=book_id)

    text = ('Введите описание книги в следующем формате:\n'
            'Название книги(перенос строки)\n'
            'Автор или пустая строка(перенос строки)\n'
            'Комментарии(переносы допускаются)\n\n'
            'Или прервите запись командой /break')

    bot.send_message(call.message.chat.id, text)
    bot.register_next_step_handler(call.message, set_description2)


# Просто продублировал код как свинья
def set_description2(message):
    if message.text[0] == '/':
        return

    book = CatalogManager.get_edit_book(message.from_user.id)
    dsc = message.text.split('\n', maxsplit=2)
    book.name = dsc[0]
    if len(dsc) >= 2:
        book.author = dsc[1]
        if len(dsc) >= 3:
            book.comments = dsc[2]

    preview = '*"{}"*\n{}\n'.format(book.name, book.author)
    if book.comments:
        preview += '\t_'+book.comments+'_\n'
    bot.send_message(message.chat.id, 'Описание книги:\n'+preview, parse_mode='Markdown')
    CatalogManager.save_edit(message.from_user.id)
    bot.send_message(message.chat.id, 'Книга успешно изменена!')

    # ---- ----


# Вот сейчас мне стыдно
# Handle catalogbook button
@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'catalogbook')
def catalog_book_callback_inline(call):
    book_id = int(call.data.split(' ')[1])
    CatalogManager.get_edit_book(call.message.chat.id, book_id=book_id)

    keyboard = CatalogManager.get_catalogs_keyboard()
    bot.send_message(call.message.chat.id, 'Напишите каталог, в который нужно поместить книгу или прервите командой /break', reply_markup=keyboard)
    bot.register_next_step_handler(call.message, set_catalog2)


def set_catalog2(message):
    if message.text[0] == '/':
        return

    if not CatalogManager.is_catalog_name(message.text):
        text = 'Это не название каталога. Повторите попытку или прервите командой /break'
        bot.reply_to(
                    message,
                    text,
                    reply_markup=types.ReplyKeyboardRemove()
                    )
        bot.register_next_step_handler(message, set_catalog2)
        return

    book = CatalogManager.get_edit_book(message.from_user.id)
    if not book.name:
        bot.send_message(message.chat.id, 'Всё плохо!')
        return
    book.catalog = message.text
    CatalogManager.save_edit(message.from_user.id)
    bot.send_message(message.chat.id, 'Каталог успешно изменен!')

    # ---- ---- ----
    # ---- ADDING ----
    # ---- ---- ----


# Handle '/addcatalog'
@bot.message_handler(func=commands_handler(['/addcatalog']))
def add_new_catalog(message):
    usr = MathUser.log_by_message(message)
    if not usr.can_edit():
        return
    if len(message.text.split(' ')) < 2:
        return
    cat_name = message.text.split(' ', maxsplit=1)[1]
    if cat_name:
        if CatalogManager.add_catalog(cat_name):
            bot.reply_to(message, 'Новый каталог добавлен')
        else:
            bot.reply_to(message, 'Ошибка')


# Handle '/addbook'
@bot.message_handler(func=commands_handler(['/addbook', '/add']))
def add_book(message):
    usr = MathUser.log_by_message(message)
    if not usr.can_add():
        return

    text = ('Введите описание книги в следующем формате:\n'
            'Название книги(перенос строки)\n'
            'Автор или пустая строка(перенос строки)\n'
            'Комментарии(переносы допускаются)\n\n'
            'Или прервите запись командой /break')

    bot.reply_to(message, text)
    bot.register_next_step_handler(message, set_description)


def set_description(message):
    if message.text[0] == '/':
        return

    book = CatalogManager.get_edit_book(message.from_user.id)

    dsc = message.text.split('\n', maxsplit=2)
    book.name = dsc[0]
    if len(dsc) >= 2:
        book.author = dsc[1]
        if len(dsc) >= 3:
            book.comments = dsc[2]
    """
    preview = '*"{}"*\n{}\n'.format(book.name, book.author)
    if book.comments:
        preview += '\t_'+book.comments+'_\n'
    bot.reply_to(message, 'Описание книги:\n'+preview, parse_mode='Markdown')
    """
    keyboard = CatalogManager.get_catalogs_keyboard()
    bot.send_message(message.chat.id, 'Теперь напишите каталог, в который нужно поместить книгу или прервите командой /break', reply_markup=keyboard)
    bot.register_next_step_handler(message, set_catalog)


def set_catalog(message):
    if message.text[0] == '/':
        return

    if not CatalogManager.is_catalog_name(message.text):
        bot.reply_to(message, 'Это не название каталога. Повторите попытку или прервите командой /break', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, set_catalog)
        return

    book = CatalogManager.get_edit_book(message.from_user.id)
    book.catalog = message.text

    bot.send_message(message.chat.id, 'Загрузите теперь файл, напишите на него ссылку, пропустите этот шаг командой /skip или прервите командой /break', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, set_file)


def set_file(message):
    book = CatalogManager.get_edit_book(message.from_user.id)
    if message.document:
        link = upload_book(message)
        bot.send_message(message.chat.id, 'Ссылка:'+link, disable_web_page_preview=True)
        book.link = link
        set_book(message)
    else:
        if message.text[0] == '/':
            if message.text.split(' ')[0] == '/skip':
                dsc = channel_book_description(book)
                bot.send_message(CHANNEL_NAME, dsc, parse_mode='Markdown')
                set_book(message)
            return

        book.link = message.text

        dsc = channel_book_description(book)
        bot.send_message(CHANNEL_NAME, dsc,
                         parse_mode='Markdown', disable_notification=True)
        set_book(message)


def set_book(message):
    CatalogManager.save_edit(message.from_user.id)
    bot.reply_to(message, 'Книга успешно добавлена!')


def upload_book(message):
    book = CatalogManager.get_edit_book(message.from_user.id)
    if message.document.file_size >= 20*1024*1024:
        dsc = channel_book_description(book)
        bot.send_message(CHANNEL_NAME, dsc,
                         parse_mode='Markdown', disable_notification=True)
        result = bot.forward_message(CHANNEL_NAME, message.chat.id,
                                     message.message_id,
                                     disable_notification=True)
    else:
        dsc = channel_book_description_no_markdown(book)
        file_info = bot.get_file(message.document.file_id)
        result = bot.send_document(CHANNEL_NAME, file_info.file_id,
                                   caption=dsc, disable_notification=True)
    link = 'https://t.me/mathcatalog/%r' % result.message_id
    return link


def channel_book_description(book, markdown=True):
    dsc = '*"{}"*\n{}\n'.format(book.name, book.author)

    if book.comments:
        dsc += '_'+book.comments+'_\n'

    if book.link:
        dsc += '{}'.format(book.link)

    return dsc
    #return bot.send_message(CHANNEL_NAME, dsc, parse_mode='Markdown')


def channel_book_description_no_markdown(book, markdown=True):
    dsc = '"{}"\n{}\n'.format(book.name, book.author)

    if book.comments:
        dsc += book.comments+'\n'

    if book.link:
        dsc += '{}'.format(book.link)

    return dsc
    #return bot.send_message(CHANNEL_NAME, dsc, parse_mode='Markdown')

    # ---- ---- ----
    # ---- АДМИНКА ----
    # ---- ---- ----

#@bot.message_handler(commands=['creator'])
#def set_creator(message):
#    usr_id =  message.chat.id
#    usr = User(usr_id, message.from_user.first_name, status='Creator')
#    usr.register_user()
#    bot.reply_to(message, 'Дарова, создатель!')


@bot.message_handler(func=commands_handler(['/setadmin']))
def admin(message):
    usr = MathUser.log_by_message(message)
    if not usr.can_assign_admin():
        return

    bot.reply_to(message, 'Перешлите сообщение назначаемого админа')
    bot.register_next_step_handler(message, set_admin)


def set_admin(message):
    bot.reply_to(message, str(message))
    usr_id = message.forward_from.id
    name = message.forward_from.username
    usr = MathUser(usr_id, name, 'Admin')
    usr.register_user()
    bot.reply_to(message, 'Админ добавлен')


@bot.message_handler(func=commands_handler(['/setmoder']))
def moder(message):
    usr = MathUser.log_by_message(message)
    if not usr.can_assign_admin():
        return

    bot.reply_to(message, 'Перешлите сообщение назначаемого модератора')
    bot.register_next_step_handler(message, set_moder)


def set_moder(message):
    bot.reply_to(message, str(message))
    usr_id = message.forward_from.id
    name = message.forward_from.username
    usr = MathUser(usr_id, name, 'Moder')
    usr.register_user()
    bot.reply_to(message, 'Модератор добавлен')

    # ---- ---- ---- ----
    # ---- INLINE MODE ----
    # ---- ---- ---- ----


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_doc(query):
    answer, next_offset = CatalogManager.get_catalog_inline(query)
    if answer:
        print('ID: ' + query.id)
        bot.answer_inline_query(query.id, answer) # , next_offset=next_offset)
        statistics.track_by_user(BOT_NAME, 'Inline search: ' + query.query, query.from_user)

"""
# Если будешь восстанавливать, поменяй метод, чтобы он передавал не query.query, а сразу query
@bot.inline_handler(func=lambda query: len(query.query) == 0)
def query_lib(query):
    cat_name = query.query
    answer = CatalogManager.get_catalog_list_inline(cat_name)

    bot.answer_inline_query(query.id, answer)
"""

# ---- POLLING ---- #

while __name__ == '__main__':

    t = threading.Thread(target=models.course.listochki_updater, args=())
    t.daemon = True
    t.start()

    try:
        bot.polling(none_stop=True, interval=1)
        time.sleep(1)

    # завершение работы из консоли стандартным Ctrl-C
    except KeyboardInterrupt as e:
        print('\n{0}: Keyboard Interrupt. Good bye.\n'.format(time.time()))
        sys.exit()

    # из-за Telegram API иногда какой-нибудь пакет не доходит
    except ReadTimeout as e:
        print('{0}: Read Timeout. Because of Telegram API.\n '
              'We are offline. Reconnecting in 5 seconds.\n'.format(time.time()))
        time.sleep(5)

    # если пропало соединение, то пытаемся снова через минуту
    except ConnectionError as e:
        print('{0}: Connection Error.\n'
              'We are offline. Reconnecting in 60 seconds.\n'.format(time.time()))
        time.sleep(60)

    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RuntimeError as e:
        print('{0}: Runtime Error.\n'
              'Retrying in 3 seconds.\n'.format(time.time()))
        time.sleep(3)

    # если что-то неизвестное — от греха вырубаем с корнем. Создаём алёрт файл для .sh скрипта
    except Exception as e:
        print('{0}: Unknown Exception:\n'
              '{1}: {2}\n\n'
              'Shutting down.'.format(time.time(), str(e), e.args))
