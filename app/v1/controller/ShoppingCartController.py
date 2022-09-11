from playhouse.shortcuts import model_to_dict
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi import HTTPException, status, UploadFile

from app.v1.model.index import Product, ShoppingCart
from ..schema.product import ProductResponse


class ShoppingCartController:
	
	def __init__(self):
		self.min_product_selector = [Product.id, Product.name, Product.isAvaliable, Product.price, Product.image]
	
	def get_cart(self, user):
		"""Get list of products in shopping cart"""
		
		query = ShoppingCart.select(*self.min_product_selector, ShoppingCart.quantity).join(Product)\
			.where(ShoppingCart.user == user['id'])
		
		cart = [model_to_dict(item.product) for item in query]
		
		return cart
	
	def add_or_update_to_cart(self, user: dict, p_id: int, qt: int = 1):
		
		product = Product.select(Product.id).where(Product.id == p_id).get_or_none()
		
		if not product:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='product not found')
		
		item_cart = ShoppingCart.get_or_none((ShoppingCart.user == user['id']) & (ShoppingCart.product == p_id))
	
		if not item_cart:
			ShoppingCart.create(user=user['id'], product=product, quantity=qt)
			return Response(status_code=status.HTTP_201_CREATED)
		
		if item_cart and item_cart.quantity != qt:
			item_cart.quantity = qt
			item_cart.save()
			return Response(status_code=status.HTTP_200_OK)
		
		else:
			return Response(status_code=status.HTTP_200_OK)
	
	def remove_from_cart(self, user: dict, p_id: int):
		
		item: ShoppingCart = ShoppingCart.get_or_none((ShoppingCart.user == user['id']) & (ShoppingCart.product == p_id))
		
		if not item:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item no exists in user cart')
		
		ShoppingCart.delete().where((ShoppingCart.user == user['id']) & (ShoppingCart.product == p_id)).execute()
		
		return Response(status_code=status.HTTP_204_NO_CONTENT)
	