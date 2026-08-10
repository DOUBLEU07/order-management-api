import json
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import redis_client
from app.models.product import Product

LIST_CACHE_KEY = "products:all"


def product_cache_key(product_id: int) -> str:
    return f"product:{product_id}"


def _serialize(product: Product) -> dict:
    return {"id": product.id, "name": product.name, "price": product.price, "stock_qty": product.stock_qty}


class ProductService:


    def __init__(self, db: AsyncSession):
        self.db = db

    async def _invalidate_cache(self, product_id: Optional[int] = None) -> None:
        await redis_client.delete(LIST_CACHE_KEY)
        if product_id is not None:
            await redis_client.delete(product_cache_key(product_id))

    async def create_product(self, name: str, price: float, stock_qty: int) -> Product:
        product = Product(name=name, price=price, stock_qty=stock_qty)
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        await self._invalidate_cache()
        return product

    async def get_products(self) -> List[Product]:
        cached = await redis_client.get(LIST_CACHE_KEY)
        if cached is not None:
            return [Product(**row) for row in json.loads(cached)]

        result = await self.db.execute(select(Product))
        products = list(result.scalars().all())

        await redis_client.set(
            LIST_CACHE_KEY,
            json.dumps([_serialize(p) for p in products]),
            ex=settings.PRODUCT_CACHE_TTL_SECONDS,
        )
        return products

    async def get_product(self, product_id: int) -> Optional[Product]:
        cache_key = product_cache_key(product_id)

        cached = await redis_client.get(cache_key)
        if cached is not None:
            return Product(**json.loads(cached))

        product = await self.db.get(Product, product_id)

        if product is not None:
            await redis_client.set(
                cache_key, json.dumps(_serialize(product)), ex=settings.PRODUCT_CACHE_TTL_SECONDS
            )

        return product

    async def update_product(
        self, product_id: int, name: str, price: float, stock_qty: int
    ) -> Optional[Product]:
        product = await self.db.get(Product, product_id)
        if product is None:
            return None

        product.name = name
        product.price = price
        product.stock_qty = stock_qty
        await self.db.flush()
        await self.db.refresh(product)
        await self._invalidate_cache(product_id)
        return product
