from pydantic import BaseModel, Field, StrictStr, validator


class CategoryResponse(BaseModel):
    id: int = Field(title='Category ID', example=15)
    name: str = Field(title='Category name', example='Mobile')
    description: str = Field(title='Category description', example='Mobile devices')


class CategoryCreate(BaseModel):
    name: StrictStr = Field(title='Name of category', min_length=3, example='Capilar')
    description: StrictStr = Field(title='Description of category', min_length=5, example='Capilar health and care')

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
