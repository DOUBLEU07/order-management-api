# Order Management API

A small order/inventory REST API built with **FastAPI** (async) + **PostgreSQL**
(async SQLAlchemy ORM) + **Redis**, running in Docker.

## How the code is organized

```
app/
├── main.py           # FastAPI app + lifespan (creates tables on startup)
├── core/              # config, DB session, Redis client
├── models/            # SQLAlchemy ORM models (Product, Order, OrderItem)
├── schemas/           # Pydantic request/response models
├── services/          # business logic (ProductService, OrderService) — talks
│                       # to the DB session and Redis directly, no repository
│                       # abstraction layer
└── routers/            # FastAPI routes — thin, just call a service and map
                        # domain exceptions to HTTP status codes
```

`routers` stay thin (HTTP concerns only), `services` hold all the business
logic and are the only place that touches SQLAlchemy/Redis, `models` and
`schemas` are kept separate so the API's public shape (Pydantic) can evolve
independently of the DB table shape (SQLAlchemy).

## What it demonstrates

- **Async stack end-to-end**: FastAPI `async def` routes, SQLAlchemy 2.0 async
  engine + `asyncpg`, `redis.asyncio`.
- **Transaction safety**: one DB session per request (`get_db`), committed once
  at the end — so "create order" (which decrements stock across multiple
  products) either fully succeeds or fully rolls back.
- **Atomic stock decrement**: a single `UPDATE ... WHERE stock_qty >= qty`
  statement, safe under concurrent orders without explicit row locking.
- **Redis cache-aside**: `GET /products` and `GET /products/{id}` are cached
  with a TTL; any write (create/update product, or an order that changes
  stock) invalidates the affected keys.

## How to run it

```bash
cp .env.example .env   # already done in this repo for local dev
docker compose up --build
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Endpoints

| Method | Path             | What it does                              |
|--------|------------------|--------------------------------------------|
| POST   | /products        | create a product                          |
| GET    | /products        | list products (cached)                    |
| GET    | /products/{id}   | get one product (cached)                  |
| PUT    | /products/{id}   | update a product (invalidates cache)      |
| POST   | /orders          | create an order (checks/decrements stock) |
| GET    | /orders          | list orders                               |
| GET    | /orders/{id}     | get one order                             |

## Out of scope

Auth/JWT, rate limiting, Redis pub/sub, and a background job queue were left
out to keep this small.
