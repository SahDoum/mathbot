from peewee import *
from playhouse.sqlite_ext import *

database = SqliteExtDatabase('database.db', **{})


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class Book(BaseModel):
    name = SearchField()
    author = SearchField()
    catalog = SearchField()
    comments = SearchField()
    link = SearchField(unindexed=True)

    class Meta:
        db_table = 'bot_math_books'


class BookIndex(FTSModel):
    name = SearchField()
    author = SearchField()
    comments = SearchField()

    class Meta:
        database = database
        # Use the porter stemming algorithm to tokenize content.
        extension_options = {'tokenize': 'porter'}


class Catalog(BaseModel):
    name = CharField(null=True, unique=True)

    class Meta:
        db_table = 'bot_math_catalogs'


class ProposeBook(BaseModel):
    author = CharField(null=True)
    catalog = CharField(null=True)
    comments = TextField(null=True)
    link = CharField(null=True)
    name = CharField(null=True)
    usr = IntegerField(db_column='usr_id', null=True, unique=True)
    usr_name = CharField(null=True)

    class Meta:
        db_table = 'bot_math_propose_books'


# MathUsers for adding books


class MathUser(BaseModel):
    name = CharField(null=True)
    status = CharField(null=True)
    usr_id = IntegerField(db_column='usr_id', null=True, unique=True)

    class Meta:
        db_table = 'bot_math_users'

    @staticmethod
    def logUser(usr_id):
        usr = MathUser.get(usr_id == usr_id)
        if usr:
            return usr
        else:
            return MathUser(usr_id)

    @staticmethod
    def log_by_message(message):
        if message.chat.type == 'private':
            try:
                usr = MathUser.get(MathUser.usr_id == message.from_user.id)
                return usr
            except:
                pass

        return MathUser(message.from_user.id)

    @staticmethod
    def log_by_callback(callback):
        try:
            usr = MathUser.get(MathUser.usr_id == callback.from_user.id)
            return usr
        except:
            return MathUser(callback.from_user.id)

    def register_user(self):
        self.save()

    def can_edit(self):
        return (self.status in ['Admin', 'Moder', 'Creator'])

    def can_add(self):
        return (self.status != 'Ban')

    def can_affirm_books(self):
        return (self.status in ['Admin', 'Moder', 'Creator'])

    def can_delete_catalog(self):
        return (self.status in ['Admin', 'Creator'])

    def can_assign_admin(self):
        return (self.status == 'Creator')

    def can_ban_user(self):
        return (self.status in ['Admin', 'Creator'])

    def can_browse_commands(self):
        return (self.status in ['Admin', 'Moder', 'Creator'])

'''
def store_document(book):
    BookIndex.insert({
        BookIndex.docid: book.id,
        BookIndex.name: fn.lower(book.name),
        BookIndex.author: fn.lower(book.author),
        BookIndex.comments: fn.lower(book.comments)}).execute()

BookIndex.drop_table()
database.create_tables([BookIndex])

for book in Book.select():
    store_document(book)
'''
