# Order Management API

A simple REST API for managing products and orders built with **FastAPI**,
**PostgreSQL** (through an async SQLAlchemy ORM), and **Redis** for caching.
Runs in Docker

## Project layout

```
app/
├── main.py       # creates the FastAPI app, wires up the routes
├── core/         # config, DB session, Redis client
├── models/       # SQLAlchemy models (Product, Order, OrderItem)
├── schemas/      # Pydantic models for request/response validation
├── services/     # the actual business logic (stock checks, caching, etc.)
└── routers/      # the HTTP endpoints
```

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
