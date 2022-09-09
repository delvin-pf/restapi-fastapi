from datetime import datetime

from peewee import Model, AutoField, CharField, IntegerField, FloatField, BooleanField, DateTimeField, ForeignKeyField

from .User import User
from app.v1.utils.database import dbSql


class Product(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    description = CharField()
    stock = IntegerField()
    minStock = IntegerField()
    price = FloatField()
    isAvaliable = BooleanField(default=True)
    vendor = ForeignKeyField(User, backref='vendor', column_name='vendor', on_delete='CASCADE')
    image = CharField(null=True)
    score = FloatField(null=True)
    ratings = IntegerField(default=0)
    createdAt = DateTimeField(default=datetime.now)
    updatedAt = DateTimeField(default=datetime.now)

    class Meta:
        database = dbSql
        table_name = 'products'

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.now()
        return super(Product, self).save(*args, **kwargs)
