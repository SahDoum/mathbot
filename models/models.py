from playhouse.sqlite_ext import *

from models import BaseModel, database


class Book(BaseModel):

    author = CharField(null=True)
    catalog = CharField(null=True)
    comments = TextField(null=True)
    link = CharField(null=True)
    name = CharField(null=True)

    class Meta:
        db_table = 'bot_math_books'


class FTSBook(FTSModel):
    author = SearchField()
    name = SearchField()
    catalog = SearchField()
    comments = SearchField()
    catalog = SearchField()

    origin_id = IntegerField()

    class Meta:
        database = database
        db_table = 'bot_math_book_indexes'



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


def store_document(book):
    FTSBook.insert({
        FTSBook.docid: book.id,
        FTSBook.name: book.name,
        FTSBook.author: book.author,
        FTSBook.comments: book.comments,
        FTSBook.catalog: book.catalog,
        FTSBook.origin_id: book.id}).execute()


'''
print('1')
try:
    FTSBook.drop_table()
except:
    pass

database.create_tables([FTSBook])

for book in Book.select():
    store_document(book)

query = FTSBook.search_bm25('Панов', weights=[1, 1, 1, 1, 0.1])
for el in query:
    print(f'{el.name} | {el.catalog}')
'''
