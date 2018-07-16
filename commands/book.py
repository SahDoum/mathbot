from utils import bot, get_book_args, upload_book
from models import User, Book, BookIndex, Catalog
from settings import CHANNEL_NAME

from peewee import DoesNotExist
from telebot import types


def cmd_add_book(message: types.Message):
    user_id = message.from_user.id
    try:
        user = User.get(user_id)
    except DoesNotExist:
        return

    if not user.can_add():
        return

    text = ('Введите описание книги в следующем формате:\n'
            'Название книги(перенос строки)\n'
            'Автор(перенос строки)\n'
            'Комментарии(переносы допускаются)\n\n'
            'Или прервите запись командой /break')

    bot.reply_to(message, text)
    bot.register_next_step_handler(message, add_book)


# Next step handlers
def add_book(message: types.Message):
    user_id = message.from_user.id
    try:
        user = User.get(user_id)
        if not user.can_add():
            return

    except DoesNotExist:
        return

    lines = message.text.splitlines()
    book_args = get_book_args(lines)
    if book_args:
        book_args['added_by'] = user
        bot.reply_to(message, 'Напишите каталог, в который нужно поместить книгу или прервите командой /break')
        bot.register_next_step_handler(message, set_catalog, book_args)


def set_catalog(message, book_args):
    if message.text.startswith('/break'):
        return

    try:
        catalog = Catalog.get(name=message.text)
    except DoesNotExist:
        bot.reply_to(message, 'Не найдено такого каталога. Попробуйте ещё раз или напишите /break')
        bot.register_next_step_handler(message, set_catalog, book_args)
        return

    book_args['catalog'] = catalog
    bot.reply_to(message, 'Загрузите теперь файл, или отошлите ссылку на него, либо '
                          'пропустите этот шаг командой /skip или прервите командой /break')
    bot.register_next_step_handler(message, set_file, book_args)


def set_file(message, book_args):
    book = Book.create(**book_args)

    if message.document:
        link = upload_book(message, book)
        bot.send_message(message.chat.id, 'Ссылка: '+link, disable_web_page_preview=True)
        book.link = link
        book.save()

    else:
        if message.text[0] == '/':
            if message.text.split(' ')[0] == '/skip':
                dsc = book.get_book_description_md()
                bot.send_message(CHANNEL_NAME, dsc, parse_mode='Markdown')
            else:
                book.delete_instance()
                return

        elif message.text.startswith('https://t.me/'):
            book.link = message.text
            book.save()
            book_description = book.get_book_description_md()
            bot.send_message(CHANNEL_NAME, book_description, parse_mode='Markdown', disable_notification=True)

        else:
            bot.reply_to(message, 'Не распознан файл, попробуйте ещё раз, напишите /skip что-бы пропустить '
                                  'загрузку файла или /break что-бы прервать добавление книги')
            book.delete_instance()
            bot.register_next_step_handler(message, set_file, book_args)
            return

    book.create_fts_index()


def inline_search_book(inline_query: types.InlineQuery):
    books = BookIndex.search_bm25(inline_query.query)

    if len(books):
        answer = []
        # Generate inline book panels
        for book in books:
            book = Book.get(book.rowid)
            title = '"{}" {}'.format(book.name, book.author)
            if book.link:
                result = types.InlineQueryResultDocument(
                    id='book' + str(book.id),
                    title=title,
                    description=book.comments,
                    document_url=book.link, mime_type='application/pdf',
                    caption=book.get_book_description()
                )
            else:
                book_dsc = types.InputTextMessageContent(
                    message_text=book.get_book_description_md(),
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                result = types.InlineQueryResultArticle(
                    id='book' + str(book.id),
                    title=title,
                    description=book.comments,
                    input_message_content=book_dsc
                )
            answer.append(result)

        if answer:
            bot.answer_inline_query(inline_query.id, answer)
