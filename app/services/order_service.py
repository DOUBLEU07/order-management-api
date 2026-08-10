from typing import List, Optional, Tuple

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.exceptions import InsufficientStockError, ProductNotFoundError
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.services.product_service import LIST_CACHE_KEY, product_cache_key


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, customer_name: str, items: List[Tuple[int, int]]) -> Order:

        order_items = []

        for product_id, qty in items:
            product = await self.db.get(Product, product_id)
            if product is None:
                raise ProductNotFoundError(product_id)

            stmt = (
                update(Product)
                .where(Product.id == product_id, Product.stock_qty >= qty)
                .values(stock_qty=Product.stock_qty - qty)
                .returning(Product.id)
            )
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none() is None:
                raise InsufficientStockError(product_id, qty)

            order_items.append(
                OrderItem(product_id=product_id, qty=qty, price_at_order_time=product.price)
            )

        order = Order(customer_name=customer_name, items=order_items, status="CONFIRMED")
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order, attribute_names=["items", "created_at"])

        for product_id, _ in items:
            await redis_client.delete(product_cache_key(product_id))
        await redis_client.delete(LIST_CACHE_KEY)

        return order

    async def get_orders(self) -> List[Order]:
        result = await self.db.execute(select(Order))
        return list(result.scalars().all())

    async def get_order(self, order_id: int) -> Optional[Order]:
        return await self.db.get(Order, order_id)
