from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers.order import router as order_router
from app.routers.product import router as product_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Order Management API", lifespan=lifespan)

app.include_router(product_router)
app.include_router(order_router)


@app.get("/")
def root():
    return {"message": "Hello"}
