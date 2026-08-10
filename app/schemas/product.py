from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(ge=0)
    stock_qty: int = Field(ge=0)

    model_config = {"from_attributes": True}


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
