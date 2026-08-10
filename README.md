# Order Management API

A simple REST API for managing products and orders — built with **FastAPI**,
**PostgreSQL** (through an async SQLAlchemy ORM), and **Redis** for caching.
Runs in Docker, so you don't need anything installed locally except Docker
itself.

## Project layout

```
app/
├── main.py       # creates the FastAPI app, wires up the routes
├── core/         # config, DB session, Redis client
├── models/       # SQLAlchemy models (Product, Order, OrderItem)
├── schemas/      # Pydantic models for request/response validation
├── services/     # the actual business logic (stock checks, caching, etc.)
└── routers/      # the HTTP endpoints — kept thin on purpose
```

The routes don't talk to the database or Redis directly — they call into
`services`, which is where all the real logic lives. That keeps each layer
easy to reason about on its own.

## A few things worth knowing about how it works

- **One DB transaction per request.** If creating an order fails partway
  through (say, one of the products is out of stock), everything gets rolled
  back — you never end up with a half-finished order.
- **Stock never goes negative, even under load.** Decrementing stock is done
  as a single `UPDATE ... WHERE stock_qty >= qty` query, so two orders hitting
  the same product at the same time can't both succeed and push stock below
  zero.
- **Product reads are cached in Redis.** `GET /products` and
  `GET /products/{id}` check Redis first before hitting Postgres. Any write
  that changes product data (creating/updating a product, or placing an
  order) clears the relevant cache entries right away.

## Running it

```bash
cp .env.example .env   # already done in this repo for local dev
docker compose up --build
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

## Endpoints

| Method | Path             | What it does                              |
|--------|------------------|--------------------------------------------|
| POST   | /products        | create a product                          |
| GET    | /products        | list products (cached)                    |
| GET    | /products/{id}   | get one product (cached)                  |
| PUT    | /products/{id}   | update a product (clears its cache)       |
| POST   | /orders          | place an order (checks/decrements stock)  |
| GET    | /orders          | list orders                               |
| GET    | /orders/{id}     | get one order                             |
