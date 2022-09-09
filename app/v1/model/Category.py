from datetime import datetime

from peewee import Model, AutoField, CharField, DateTimeField

from ..utils.database import dbSql


class Category(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    description = CharField()
    createdAt = DateTimeField(default=datetime.now)
    updatedAt = DateTimeField(default=datetime.now)

    class Meta:
        database = dbSql
        table_name = 'categories'
