from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    companies,
    branches,
    users,
    tables,
    waiters,
    products,
    customers,
    inventory,
    orders,
    ledgers,
    dashboard
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(branches.router, prefix="/branches", tags=["branches"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tables.router, prefix="/tables", tags=["tables"])
api_router.include_router(waiters.router, prefix="/waiters", tags=["waiters"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(ledgers.router, prefix="/ledgers", tags=["ledgers"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
