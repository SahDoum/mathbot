from playhouse.sqlite_ext import *

database = SqliteExtDatabase('database.db', **{})


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database
