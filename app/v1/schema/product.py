from pydantic import BaseModel, Field, root_validator, validator

from .category import CategoryResponse
from .user import UserResponse


class ProductCreate(BaseModel):
	name: str = Field(title='Product name', min_length=3, example='Soap')
	description: str = Field(title='Product description', min_length=3, example='Soap with glicerine')
	price: float = Field(title='Product price', example=1.09)
	stock: int = Field(title='Product quantity', example=190)
	minStock: int = Field(title='Product minimum stock', example=20)
	isAvaliable: bool = Field(title='Product is avaliable', example=True)
	categories: set[int] = Field(title='Array of ID of categories', min_items=1, example=[1, 2, 3])
	
	@validator('name')
	def name_must_be_string(cls, name):
		if name is not None and name.isnumeric():
			raise ValueError('"name" could not be number into a string')
		return name
	
	@validator('description')
	def description_must_be_string(cls, description):
		if description is not None and description.isnumeric():
			raise ValueError('"description" could not be number into a string')
		return description


class ProductResponse(BaseModel):
	id: int = Field(title='ID of product', example=1)
	name: str = Field(title='Product name', min_length=3, example='Soap')
	image: str | None = Field(default=None,  title='Image path')
	price: float = Field(title='Product price', example=1.09)
	isAvaliable: bool = Field(title='Product is avaliable', example=True)
	
	class Config:
		schema_extra = {
			'example': {
				'id': 1,
				'name': 'Shampoo',
				'description': 'Shampoo with Aloe',
				'price': 4.39,
				'stock': 100,
				'categories': [
					{
						'id': 1,
						'name': 'Capilar',
						'description': 'Hair care'
					}
				]
			}
		}


class ProductFullResponse(ProductResponse):
	description: str = Field(title='Product description', min_length=3, example='Soap with glicerine')
	stock: int = Field(title='Product quantity', example=190)
	vendor: UserResponse
	categories: list[CategoryResponse]


class ProductUpdate(BaseModel):
	name: str | None = Field(default=None, title='Name of product', min_length=3, example='Shampoo')
	description: str | None = Field(default=None, title='Description of product', min_length=3,
	                                example='Shampoo with Aloe')
	stock: int | None = Field(default=None, title='Quantity of product in stock', gt=0, example=100)
	minStock: int | None = Field(default=None, title='Minimum stock for product', gt=0, example=20)
	price: float | None = Field(default=None, title='Price of product', gt=0, example=4.29)
	isAvaliable: bool | None = Field(default=None, title='Is product avaliable', example=False)
	categories: set[int] | None = Field(default=None, title='List with ID of categories of products', min_items=1,
	                                    example=[1, 2, 3])
	
	@root_validator(pre=True)
	def recuse_empty(cls, values):
		if not values:
			raise ValueError('body can`t be empty')
		return values
	
	@validator('name')
	def name_must_be_string(cls, name):
		if name is not None and name.isnumeric():
			raise ValueError('"name" could not be number into a string')
		return name
	
	@validator('description')
	def description_must_be_string(cls, description):
		if description is not None and description.isnumeric():
			raise ValueError('"description" could not be number into a string')
		return description
