from models.models import Catalog, Book, FTSBook, ProposeBook
from peewee import fn

from telebot import types


class CatalogManager:
    edit_list = {}
    catalog_list = {}

    def __repr__(self):
        return '<Catalog>'

    # ---- ---- ---- ----
    # ---- CATALOG VIEW ----
    # ---- ---- ---- ----

    @staticmethod
    def get_catalog_name(cat_id):
        cat = Catalog.get(id == cat_id)
        return cat.name

    @staticmethod
    def catalogs_button_keyboard(tag='catalog'):
        catalogs = Catalog.select()
        keyboard = types.InlineKeyboardMarkup()
        for cat in catalogs:
            callback = tag+' '+str(cat.id)
            button = types.InlineKeyboardButton(text=cat.name,
                                                callback_data=callback)
            keyboard.add(button)
        return keyboard

    @staticmethod
    def get_catalogs_keyboard():
        catalogs = Catalog.select()

        keyboard = types.ReplyKeyboardMarkup()
        for cat in catalogs:
            button = types.KeyboardButton(text=cat.name)
            keyboard.add(button)
        return keyboard

    # ---- ---- ---- ----
    # ---- DESCRIPTIONS ----
    # ---- ---- ---- ----

    @staticmethod
    def catalog_dsc(cat_id):
        cat = Catalog.get(Catalog.id == cat_id)
        books = Book.select().where(Book.catalog == cat.name)

        if not books:
            return "``` В этом разделе пока нет книг. ```"

        dsc = "``` Список книг в разделе '%s':```\n\n" % cat.name
        i = 1
        for book in books:
            dsc += '{}. {}\n'.format(i, CatalogManager.book_dsc(book))
            i += 1
        return dsc

    @staticmethod
    def book_dsc(book):
        if book.link:
            book_name = '"[{}]({})"'.format(book.name, book.link)
        else:
            book_name = '*"{}"*'.format(book.name)
        dsc = '{} {}\n'.format(book_name, book.author)

        if book.comments:
            dsc += '_'+book.comments+'_\n'
        return dsc

    @staticmethod
    def book_dsc_no_markdown(book):
        dsc = '{} {}\n'.format(book.name, book.author)

        if book.comments:
            dsc += book.comments+'\n'
        if book.link:
            dsc += '{}'.format(book.link)
        return dsc

    # ---- ---- ----
    # ---- EDIT ----
    # ---- ---- ----

    @staticmethod
    def add_catalog(cat_name):
        try:
            Catalog.get(Catalog.name == cat_name)
            return False
        except Catalog.DoesNotExist:
            Catalog.create(name=cat_name)
            return True

    @staticmethod
    def is_catalog_name(cat_name):
        try:
            Catalog.get(Catalog.name == cat_name)
            return True
        except Catalog.DoesNotExist:
            return False

    @staticmethod
    def save_cat_id(cat_id, usr_id):
        CatalogManager.catalog_list[usr_id] = cat_id

    @staticmethod
    def get_cat_id(usr_id):
        return CatalogManager.catalog_list[usr_id]

    @staticmethod
    def rename_catalog(cat_id, new_name):
        cat = Catalog.get(id == cat_id)
        books = Book.select().where(Book.catalog == cat.name)

        cat.name = new_name
        for book in books:
            book.catalog = new_name

        # db.session.commit()

    # ---- book adding ----

    @staticmethod
    def get_edit_book(usr_id, book_id='None'):
        if usr_id not in CatalogManager.edit_list:
            if book_id != 'None':
                CatalogManager.edit_list[usr_id] = Book.get(Book.id == book_id)
            else:
                CatalogManager.edit_list[usr_id] = Book()
        return CatalogManager.edit_list[usr_id]

    @staticmethod
    def save_edit(usr_id):
        CatalogManager.edit_list[usr_id].save()
        CatalogManager.edit_list.pop(usr_id)

    @staticmethod
    def save_propose_edit(usr_id, usr_name):
        propose_book = ProposeBook(CatalogManager.edit_list[usr_id],
                                   usr_id, usr_name)
        propose_book.save()
        CatalogManager.edit_list.pop(usr_id)

    # ---- catalog edit ----

    @staticmethod
    def edit_catalogs_generator():
        catalogs = Catalog.select()

        for cat in catalogs:
            keyboard = types.InlineKeyboardMarkup()
            open_button = types.InlineKeyboardButton(
                text=u"Открыть",
                callback_data='edit '+str(cat.id)
                )
            del_button = types.InlineKeyboardButton(
                text=u"Удалить",
                callback_data='deletecatalog '+str(cat.id)
                )
            add_button = types.InlineKeyboardButton(
                text=u"Переименовать",
                callback_data='editcatalog '+str(cat.id)
                )
            keyboard.row(open_button, del_button, add_button)

            dsc = '*{}*'.format(cat.name)

            yield {'text': dsc, 'buttons': keyboard}

    @staticmethod
    def delete_catalog(cat_id):
        cat = Catalog.get(Catalog.id == cat_id)
        books = Book.select().where(Book.catalog == cat.name)
        for book in books:
            book.delete_instance()
        cat.delete_instance()

    # ---- book edit ----

    @staticmethod
    def edit_books_generator(cat_id):
        cat = Catalog.get(Catalog.id == cat_id)
        books = Book.select().where(Book.catalog == cat.name)

        if not books:
            return

        for book in books:
            keyboard = types.InlineKeyboardMarkup()
            del_button = types.InlineKeyboardButton(
                text=u"Удалить",
                callback_data='deletebook '+str(book.id)
                )
            add_button = types.InlineKeyboardButton(
                text=u"Редактировать",
                callback_data='editbook '+str(book.id)
                )
            cat_button = types.InlineKeyboardButton(
                text=u"Каталог",
                callback_data='catalogbook '+str(book.id)
                )
            keyboard.row(add_button, del_button, cat_button)

            dsc = '*{}*\n{} \n'.format(book.name, book.author)
            if book.comments:
                dsc += '_'+book.comments+'_\n'

            yield {'text': dsc, 'buttons': keyboard}

    @staticmethod
    def delete_book(book_id):
        Book.get(Book.id == book_id).delete_instance()


    '''

    # ---- ---- ---- ---- ----
    # ---- PROPOSE BOOK MENU ----
    # ---- ---- ---- ---- ----

    # надо переделать офк
    @staticmethod
    def propose_books_menu_generator():
        books = ProposeBook.query.all.order_by(ProposeBook.usr_id)

        if not books:
            return

        for book in books:
            keyboard = types.InlineKeyboardMarkup()
            del_button = types.InlineKeyboardButton(
                text=u"Удалить",
                callback_data='delprop '+str(book.id)
                )
            edit_button = types.InlineKeyboardButton(
                text=u"Редактировать",
                callback_data='editprop '+str(book.id)
                )
            add_button = types.InlineKeyboardButton(
                text=u"Добавить",
                callback_data='addprop '+str(book.id)
                )
            keyboard.row(add_button, del_button, edit_button)

            dsc = '*{}*\n{} \n'.format(book.name, book.author)
            if book.comments:
                dsc += '_'+book.comments+'_\n'

            yield {'text': dsc, 'buttons': keyboard}

    @staticmethod
    def add_propose_book(book_id):
        return

    @staticmethod
    def delete_propose_book(book_id):
        return
        
    '''

    # ---- ---- ---- ----
    # ---- INLINE MODE ----
    # ---- ---- ---- ----

    @staticmethod
    def get_books_by_query(query):
        books = FTSBook.search_bm25(query.query)
        return books

    @staticmethod
    def get_catalog_inline(query):
        books = CatalogManager.get_books_by_query(query)

        if len(books):
            answer = []
            print('\n\n\nРУН РУН РУН')
            # генерим инлайновые панельки для книг
            for fts_book in books:
                print('Book: {}\n'.format(fts_book.docid))
                book = Book.get(Book.id == fts_book.origin_id)
                title = '"{}" {}'.format(book.name, book.author)
                if book.link:
                    result = types.InlineQueryResultDocument(
                        id='book'+str(book.id),
                        title=title,
                        description=book.comments,
                        document_url=book.link, mime_type='application/pdf',
                        caption=CatalogManager.book_dsc_no_markdown(book)
                    )
                else:
                    book_dsc = types.InputTextMessageContent(
                        message_text=CatalogManager.book_dsc(book),
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    result = types.InlineQueryResultArticle(
                        id='book'+str(book.id),
                        title=title,
                        description=book.comments,
                        input_message_content=book_dsc
                    )
                answer.append(result)
            return (answer, None) # str(next_offset))

        return (None, None)

    @staticmethod
    def get_catalog_list_inline(cat_name):
        catalogs = Catalog.select()

        if catalogs:
            answer = []
            for cat in catalogs:
                # title = '{} {}'.format(book.name, book.author)
                cat_dsc = types.InputTextMessageContent(
                    message_text=CatalogManager.catalog_dsc(cat.id),
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                result = types.InlineQueryResultArticle(
                    id='catalog'+str(cat.id),
                    title=cat.name,
                    # description=cat.name,
                    input_message_content=cat_dsc
                )
                answer.append(result)
            return answer

        return None

    # ---- ----
