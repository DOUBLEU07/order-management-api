from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.exceptions import InsufficientStockError, ProductNotFoundError
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    items = [(item.product_id, item.qty) for item in order.items]
    try:
        return await OrderService(db).create_order(order.customer_name, items)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientStockError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("", response_model=List[OrderResponse])
async def get_orders(db: AsyncSession = Depends(get_db)):
    return await OrderService(db).get_orders()


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await OrderService(db).get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
