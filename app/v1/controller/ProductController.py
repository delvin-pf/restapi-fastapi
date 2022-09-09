from uuid import uuid4
from datetime import datetime
from os import remove

from playhouse.shortcuts import model_to_dict
from peewee import prefetch
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi import HTTPException, status, UploadFile

from app.v1.model.index import Category, CategoryProduct, Product, User
from ..schema.product import ProductResponse, ProductFullResponse


class ProductController:
	
	def __init__(self):
		self.images_path = 'app/v1/static/images/'
		
		self.min_product_selector = [Product.id, Product.name, Product.isAvaliable, Product.price]
		self.complete_product_selector = [*self.min_product_selector, Product.stock, Product.description]
		self.category_selector = [Category.id, Category.name, Category.description]
		self.vendor_selector = [User.id, User.name]
		self.full_query_product = [*self.complete_product_selector, *self.vendor_selector, *self.category_selector]
		
		self.PRODUCT_NOT_FOUND = HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail='product not found'
		)
		self.ALREADY_EXISTS = HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail='Product with same name already exists'
		)
		self.CATEGORY_ERROR = HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail='Some category in categories no exists'
		)
		self.NO_OWNED_PRODUCT = HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail='can´t modify this product'
		)
	
	def store(self, page, qt):
		products = Product.select(*self.min_product_selector).where(Product.isAvaliable == bool(True)) \
			.paginate(page, qt).order_by(Product.id)
		
		products_list = self.__organize_products([product for product in products])
		
		return JSONResponse(status_code=200, content=jsonable_encoder(products_list))
	
	def index(self, p_id):
		query = prefetch(
			Product.select(*self.complete_product_selector, *self.vendor_selector).join(User).where(Product.id == p_id),
			CategoryProduct.select(CategoryProduct.productId, *self.category_selector).join(Category)
		)
		if not query:
			raise self.PRODUCT_NOT_FOUND
		
		product = query[0]
		categories = [p.categoryId for p in product.categories]
		product.categories = categories
		
		response = ProductFullResponse.parse_obj(model_to_dict(product, backrefs=True))
		
		return JSONResponse(status_code=200, content=jsonable_encoder(response, exclude_none=True))
	
	def search(self, word: str, page: int, qt: int):
		filter_by_words = (Product.name.contains(word)) | (Product.description.contains(word))
		
		query = Product.select(*self.min_product_selector).where(filter_by_words & Product.isAvaliable == bool(True)) \
			.paginate(page, qt)
		
		products_dict = self.__organize_products([product for product in query])
		
		return JSONResponse(status_code=200, content=jsonable_encoder(products_dict))
	
	def create(self, body, user):
		if not user['isVendor']:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail='To create a product, must be a vendor'
			)
		product_exist = Product.get_or_none(Product.name == body.name)
		if product_exist:
			raise self.ALREADY_EXISTS
		
		self.__verify_categories(body.categories)
		product = Product.create(
			name=body.name,
			description=body.description,
			price=body.price,
			stock=body.stock,
			minStock=body.minStock,
			isAvaliable=body.isAvaliable,
			vendor=user['id']
		)
		self.__set_categories(product, body.categories)
		
		#### REvisar
		product = ProductResponse.parse_obj(model_to_dict(product, backrefs=True))
		
		return JSONResponse(status_code=201, content=jsonable_encoder(product))
	
	def update(self, p_id, body, user):
		product = Product.get_or_none(Product.id == p_id)
		
		if not product:
			raise self.PRODUCT_NOT_FOUND
		
		if product.vendor.id != user['id']:
			raise self.NO_OWNED_PRODUCT
		
		if body.name and Product.get_or_none((Product.name == body.name) & (Product.id != p_id)):
			raise self.ALREADY_EXISTS
		
		if body.categories:
			self.__verify_categories(body.categories)
		
		product.name = body.name if body.name else product.name
		product.description = body.description if body.description else product.description
		product.stock = body.stock if body.stock else product.stock
		product.minStock = body.minStock if body.minStock else product.minStock
		product.price = body.price if body.price else product.price
		product.isAvaliable = body.isAvaliable if body.isAvaliable else product.isAvaliable
		product.save()
		
		if body.categories:
			self.__set_categories(product, body.categories)
		
		return Response(status_code=204)
	
	def delete(self, p_id, user):
		product = Product.get_or_none(Product.id == p_id)
		
		if not product:
			raise self.PRODUCT_NOT_FOUND
		
		if user['id'] is not product.vendor.id:
			raise self.NO_OWNED_PRODUCT
		
		if product.image:
			image_path = self.images_path + product.image
			try:
				remove(image_path)
			except BaseException:
				pass
		
		product.delete_instance()
		
		return Response(status_code=204)
	
	def add_image(self, user: dict, p_id: int, file: UploadFile):
		product = Product.get_or_none(Product.id == p_id)
		if not product:
			raise self.PRODUCT_NOT_FOUND
		
		if product.vendor.id is not user['id']:
			raise self.NO_OWNED_PRODUCT
		
		file_extension = file.filename.split('.')[-1]
		file_name = f'{str(uuid4().hex)}-{datetime.now().strftime("%d%m%Y%H%M%S")}.{file_extension}'
		
		with open(fr'{self.images_path + file_name}', 'wb') as f:
			f.write(file.file.read())
		
		product.image = file_name
		product.save()
		
		return Response(status_code=204)
	
	def get_image(self, p_id):
		product = Product.select(Product.image).where(Product.id == p_id).get()
		if not product:
			raise self.PRODUCT_NOT_FOUND
		if not product.image:
			raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='No image')
		
		return FileResponse(fr'{self.images_path + product.image}', media_type='image/jpg')
	
	def avaliate(self, p_id: int, score: int):
		product = Product.get_or_none(Product.id == p_id)
		if not product:
			raise self.PRODUCT_NOT_FOUND
		
		actual_score = product.score
		new_score = ((actual_score * product.ratings) + score) / product.ratings + 1
		
		product.score = new_score
		product.ratings += 1
		product.save()
		
		return JSONResponse(status_code=200, content={'score': product.score})
	
	
	def __verify_categories(self, categories: list[int]) -> None:
		"""Verify if all categories exists in database \n
		:param list[int] categories: list of categories
		:return: None
		:raise HTTPException: if some category is not in DB"""
		
		categories_in_db = [item.id for item in list(Category.select(Category.id))]
		if not set(categories).issubset(set(categories_in_db)):
			raise self.CATEGORY_ERROR
	
	@classmethod
	def __set_categories(cls, product: Product, categories: list) -> None:
		"""Delete all associations beetwen category-product and create new associations. \n
		:param product: product to assign categories
		:param categories: list of category to assign in product"""
		
		CategoryProduct.delete().where(CategoryProduct.productId == product.id).execute()
		
		if len(categories) > 1:
			categories_list = [{'productId': product, 'categoryId': category} for category in categories]
			with CategoryProduct._meta.database.atomic():
				CategoryProduct.insert_many(categories_list).execute()
		else:
			[category] = categories
			CategoryProduct.create(
				productId=product,
				categoryId=category
			)
			
	@classmethod
	def __organize_products(cls, products: list[Product] | Product):
		"""Filter the result with pydantic model \n
		:param products: list of products
		:rtype: list[ProductResponse] | ProductResponse
		:return: products filtered
		"""
		if isinstance(products, list):
			return [ProductResponse.parse_obj(model_to_dict(product)) for product in products]
		else:
			return ProductResponse.parse_obj(model_to_dict(products))
		