from datetime import datetime

from peewee import Model, ForeignKeyField, DateTimeField, IntegerField, AutoField

from .User import User
from .Product import Product
from ..utils.database import dbSql


class ShoppingCart(Model):
	id = AutoField()
	user = ForeignKeyField(User, column_name='user', backref='user', on_delete='CASCADE')
	product = ForeignKeyField(Product, column_name='product', backref='product', on_delete='CASCADE')
	quantity = IntegerField()
	createdAt = DateTimeField(default=datetime.now)
	updatedAt = DateTimeField(default=datetime.now)
	
	class Meta:
		database = dbSql
		table_name = 'shoppingCart'
		