from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await ProductService(db).create_product(product.name, product.price, product.stock_qty)


@router.get("", response_model=List[ProductResponse])
async def get_products(db: AsyncSession = Depends(get_db)):
    return await ProductService(db).get_products()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await ProductService(db).get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int, product: ProductCreate, db: AsyncSession = Depends(get_db)
):
    updated_product = await ProductService(db).update_product(
        product_id, product.name, product.price, product.stock_qty
    )
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product
