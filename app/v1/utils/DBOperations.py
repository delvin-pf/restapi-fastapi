import os
import sys
sys.path.insert(0, f'{os.getcwd()}')
from app.v1.model.index import User, Category, CategoryProduct, Product, ShoppingCart
from app.v1.utils.database import dbSql
from random import random, randint


def create_tables():
	with dbSql.atomic():
		try:
			dbSql.create_tables([User, Category, CategoryProduct, Product, ShoppingCart])
			print('Tables created')
		except Exception as e:
			print('ERROR:', e)


def drop_tables():
	with dbSql.atomic():
		try:
			dbSql.drop_tables([User, Category, CategoryProduct, Product, ShoppingCart])
			print('Tables dropped')
		except Exception as e:
			print('ERROR:', e)


def insert_categories():
	categories = [
		{'name': 'Skin Care', 'description': 'Skin care and health'},
		{'name': 'Capilar Care', 'description': 'Capilar care and health'},
		{'name': 'Mobile', 'description': 'Mobile devices'}
	]
	with dbSql.atomic():
		Category.insert_many(categories).execute()
	print('Categories inserted')


def insert_product():

	products = []
	for i in range(10):
		product = Product(
			name=f'Product {i}',
			description=f'Description for product {i}',
			price=round(random() * 5, 2),
			quantity=randint(10, 500),
			manufacturer=randint(1, 2)
		)
		products.append(product)

	with dbSql.atomic():
		Product.bulk_create(products)
	print('Product inserted. Now setting it´s categories...')

	categories_instances = []
	for product in products:
		categories = list({randint(1, 3) for x in range(3)})
		for c_id in categories:
			link = CategoryProduct(
				productId=product,
				categoryId=c_id
			)
			categories_instances.append(link)
	with dbSql.atomic():
		CategoryProduct.bulk_create(categories_instances)
	print('Categories added')


def recreate(test_data: bool = False):
	drop_tables()
	print('Wait...')
	create_tables()
	print('Wait...')
	if test_data:
		insert_categories()
		print('Wait...')
		insert_product()
		print('Ready! Database restarted')


