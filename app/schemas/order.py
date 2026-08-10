from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: int
    qty: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1)
    items: List[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    qty: int
    price_at_order_time: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    status: str
    created_at: datetime
    items: List[OrderItemResponse]
    total_price: float

    model_config = {"from_attributes": True}
