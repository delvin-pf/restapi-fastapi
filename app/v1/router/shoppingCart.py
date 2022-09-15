from fastapi import APIRouter, Query, Path, status, Depends, UploadFile

from ..controller.ShoppingCartController import ShoppingCartController
from ..schema.product import ProductResponse, ProductUpdate, ProductFullResponse
from ..security.authorization import JWTAuthorization, oauth2_scheme


router = APIRouter(
	prefix='/cart',
	tags=['cart']
)

SC = ShoppingCartController()


@router.get('', response_model=list[ProductResponse])
def getCart(token=Depends(oauth2_scheme)):
	"""Get cart"""
	user = JWTAuthorization.verify_token(token)
	return SC.get_cart(user)


@router.post('')
def addCart(token=Depends(oauth2_scheme), product_id: int =Query(title='ID of product'), quantity: int = Query(title='Quantity of products')):
	user = JWTAuthorization.verify_token(token)
	return SC.add_or_update_to_cart(user, product_id, quantity)


@router.delete('/{product_id}')
def deleteCart(token=Depends(oauth2_scheme), product_id=Path(title='ID of product to remove from cart')):
	user = JWTAuthorization.verify_token(token)
	return SC.remove_from_cart(user, product_id)
