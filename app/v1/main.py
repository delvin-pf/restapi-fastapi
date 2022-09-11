from time import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.v1.utils.database import dbSql
# Routers
from .router.users import router as users_router
from .router.products import router as products_router
from .router.categories import router as categories_router
from .router.shoppingCart import router as cart_router


app = FastAPI()


@app.middleware('http')
async def process_time(request: Request, call_next):
	start = time()
	response = await call_next(request)
	stop = time()
	print(f'> Processing time: {stop - start}')
	return response


@app.on_event('startup')
def startup():
	dbSql.connect()


@app.on_event('shutdown')
def shutdown():
	if not dbSql.is_closed():
		dbSql.close()


app.include_router(users_router)
app.include_router(products_router)
app.include_router(categories_router)
app.include_router(cart_router)


@app.get('/')
def app_init():
	return JSONResponse(status_code=200, content={
		'name': 'RestApi with FastApi in Python',
		'description': 'RestApi example to shop',
		'version': 'v1',
		'developed_by': 'Delvin Pérez'
	})
