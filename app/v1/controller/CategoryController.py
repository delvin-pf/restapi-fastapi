from app.v1.model.index import Category
from playhouse.shortcuts import model_to_dict
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class CategoryController:

    def __init__(self):
        self.exclude = [Category.createdAt, Category.updatedAt]
    
    def store(self):
        categories = list(Category.select(
            Category.id, Category.name, Category.description).objects().dicts())

        categories_list = jsonable_encoder(categories)

        return JSONResponse(status_code=200, content=categories_list)

    def create(self, body):
        category, created = Category.get_or_create(
            name=body.name,
            defaults={
                'name': body.name,
                'description': body.description
            }
        )

        if not created:
            return JSONResponse(status_code=400, content={
                'error': 'category with same name already exists'
            })

        return JSONResponse(status_code=201, content=jsonable_encoder(model_to_dict(category, exclude=self.exclude)))
