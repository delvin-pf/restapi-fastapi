from datetime import datetime

from peewee import Model, ForeignKeyField, DateTimeField

from .Category import Category
from .Product import Product
from app.v1.utils.database import dbSql


class CategoryProduct(Model):
    productId = ForeignKeyField(Product, column_name='productId', backref='categories', on_delete='CASCADE')
    categoryId = ForeignKeyField(Category, column_name='categoryId', backref='products', on_delete='CASCADE')
    createdAt = DateTimeField(default=datetime.now)
    updatedAt = DateTimeField(default=datetime.now)

    class Meta:
        database = dbSql
        table_name = 'categoryProduct'
        primary_key = False
