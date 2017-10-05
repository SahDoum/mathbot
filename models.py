from peewee import *

database = SqliteDatabase('database.db', **{})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Book(BaseModel):
    author = CharField(null=True)
    catalog = CharField(null=True)
    comments = TextField(null=True)
    link = CharField(null=True)
    name = CharField(null=True)

    class Meta:
        db_table = 'bot_math_books'

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
            return MathUser(message.from_user.id)

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