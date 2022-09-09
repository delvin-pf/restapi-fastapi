from fastapi import APIRouter, Query, Path, status, Depends, UploadFile

from ..controller.ProductController import ProductController as PC
from ..schema.product import ProductCreate, ProductResponse, ProductUpdate
from ..security.authorization import JWTAuthorization, oauth2_scheme


router = APIRouter(
	prefix='/products',
	tags=['products']
)

ProductController = PC()


@router.get('', status_code=status.HTTP_200_OK, response_model=list[ProductResponse])
def getProducts(page: int = Query(default=...), qt: int = Query(default=10, ge=2, le=25)):
	"""List products"""
	return ProductController.store(page, qt)


@router.get('/search', response_model=list[ProductResponse])
def searchProduct(
	word: str = Query(min_length=3),
	page: int = Query(min=1, max=20),
	qt: int = Query(default=10, min=1, max=50)):
	"""Search a product by words"""
	return ProductController.search(word, page, qt)


@router.get('/{product_id}', status_code=status.HTTP_200_OK)
def getProduct(product_id: int = Path(title='ID of product')):
	"""Get a unique product by ID"""
	return ProductController.index(product_id)


@router.get('/{product_id}/image')
def getImage(product_id: int = Path(title='ID of product')):
	return ProductController.get_image(product_id)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def createProduct(body: ProductCreate, token: str = Depends(oauth2_scheme)):
	"""Create a new product"""
	user = JWTAuthorization.verify_token(token)
	return ProductController.create(body, user)


@router.post('/{product_id}/image')
def setImages(
	file: UploadFile,
	token: str = Depends(oauth2_scheme),
	product_id: int = Path(title='ID of product to add images'),
):
	user = JWTAuthorization.verify_token(token)
	return ProductController.add_image(user, product_id, file)


@router.put('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def updateProduct(
	*,
	product_id: int = Path(title='ID of product to be updated', ge=1),
	body: ProductUpdate,
	token: str = Depends(oauth2_scheme)
):
	"""Update a product"""
	user = JWTAuthorization.verify_token(token)
	return ProductController.update(product_id, body, user)


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def deleteProduct(
	product_id: int = Path(title="ID of product to be deleted", ge=1),
	token: str = Depends(oauth2_scheme)
):
	"""Delete a product"""
	user = JWTAuthorization.verify_token(token)
	return ProductController.delete(product_id, user)




	
	
