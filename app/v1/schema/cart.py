from pydantic import BaseModel, Field

from .product import ProductResponse


class CartResponse(BaseModel):
	quantity: int = Field(title="Quantity of products", example=2)
	product: ProductResponse
	