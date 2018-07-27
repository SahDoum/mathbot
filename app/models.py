from settings import IUMURL

import requests
from lxml import etree
from playhouse.sqlite_ext import SqliteExtDatabase, CharField, Model, TextField, ForeignKeyField, \
    FTSModel, SearchField, IntegerField, RowIDField, DateTimeField, DoesNotExist


db = SqliteExtDatabase('data.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField(unique=True)
    first_name = CharField()
    role = CharField()

    def can_edit(self):
        return self.role in ['Admin', 'Moder', 'Creator']

    def can_add(self):
        return self.role != 'Ban'

    def can_affirm_books(self):
        return self.role in ['Admin', 'Moder', 'Creator']

    def can_delete_catalog(self):
        return self.role in ['Admin', 'Creator']

    def can_assign_admin(self):
        return self.role == 'Creator'

    def can_ban_user(self):
        return self.role in ['Admin', 'Creator']

    def can_browse_commands(self):
        return self.role in ['Admin', 'Moder', 'Creator']


# Book related models1
class Catalog(BaseModel):
    name = CharField(null=True, unique=True)

    @classmethod
    def get_catalog_description(cls, catalog_id):
        try:
            catalog = cls.get(id=catalog_id)
        except DoesNotExist:
            return

        books = catalog.books
        if books:
            dsc = f'`Список книг в разделе "{catalog.name}":`\n\n'
            for i, book in enumerate(books):
                dsc += f'{i}. {book.get_book_description()}\n'
            return dsc


class Book(BaseModel):
    author = CharField()
    name = CharField()
    comments = TextField()
    added_by = ForeignKeyField(User, backref='books')
    catalog = ForeignKeyField(Catalog, backref='books', null=True)
    link = CharField(null=True)

    @classmethod
    def delete_book(cls, book_id):
        book = cls.get(id=book_id)
        book_index = BookIndex.get(rowid=book_id)
        book.delete_instance()
        book_index.delete_instance()

    def create_fts_index(self):
        BookIndex.store_book(self)

    def get_book_description_md(self):
        if self.link:
            book_name = f'"[{self.name}]({self.link})"'
        else:
            book_name = f'*"{self.name}"*'
        dsc = f'{book_name} {self.author}\n'

        if self.comments:
            dsc += '_'+self.comments+'_\n'
        return dsc

    def get_book_description(self):
        dsc = '{} {}\n'.format(self.name, self.author)

        if self.comments:
            dsc += self.comments + '\n'
        if self.link:
            dsc += '{}'.format(self.link)
        return dsc


class BookIndex(FTSModel):
    rowid = RowIDField()
    author = SearchField()
    name = SearchField()
    catalog = SearchField()
    comments = SearchField()

    class Meta:
        database = db

    @classmethod
    def store_book(cls, book):
        cls.insert({
            cls.rowid: book.id,
            cls.author: book.author,
            cls.name: book.name,
            cls.catalog: book.catalog.name,
            cls.comments: book.comments
        }).execute()


# Course related models1
class IUMCourse(BaseModel):
    url = CharField()
    name = CharField()
    lecturers = CharField()
    place = CharField()
    program_url = CharField()
    timetable = DateTimeField()
    last_subscription = DateTimeField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.homework_list = []

    def get_homework_list(self):
        return self.homework_list

    def get_last_homework(self):
        return self.homework_list[-1]

    def update_homework(self):
        r = requests.get(self.url)
        if r.ok:
            r.encoding = 'koi8-r'
            html = r.text
            parser = etree.HTMLParser()
            tree = etree.fromstring(html, parser)
            exercise_sheet_paths = [(a.get('href').replace('..', ''), a.text.strip())
                                    for a in tree.xpath('//p[@align="center"]/a')]

            if exercise_sheet_paths:
                for exercise_sheet_path in exercise_sheet_paths:
                    self.homework_list.append((IUMURL + exercise_sheet_path))


class SubscriptionChat(BaseModel):
    chat_id = IntegerField()
    chat_title = CharField()


class Subscription(BaseModel):
    chat = ForeignKeyField(SubscriptionChat)
    course = ForeignKeyField(IUMCourse)


db.create_tables([User, Catalog, Book, BookIndex, IUMCourse, SubscriptionChat, Subscription], safe=True)
