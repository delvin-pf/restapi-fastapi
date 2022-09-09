from fastapi import APIRouter, status
from ..controller.CategoryController import CategoryController as CC
from ..schema.category import CategoryResponse, CategoryCreate

router = APIRouter(
	prefix='/categories',
	tags=['categories']
)

CategoryController = CC()


@router.get('/', response_model=list[CategoryResponse])
def getCategories():
	"""Get a list of categories"""
	return CategoryController.store()


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=CategoryResponse)
def createCategory(body: CategoryCreate):
	"""Create a new category"""
	return CategoryController.create(body)
