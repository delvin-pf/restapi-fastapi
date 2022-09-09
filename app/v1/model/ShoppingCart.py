from datetime import datetime

from peewee import Model, ForeignKeyField, DateTimeField

from .User import User
from .Product import Product
from ..utils.database import dbSql


class ShoppingCart(Model):
	user = ForeignKeyField(User, column_name='user', backref='user')
	product = ForeignKeyField(Product, column_name='product', backref='product')
	createdAt = DateTimeField(default=datetime.now)
	updatedAt = DateTimeField(default=datetime.now)
	
	class Meta:
		database = dbSql
		table_name = 'shoppingCart'
		primary_key = False
		