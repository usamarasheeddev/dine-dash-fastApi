from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, create_db_and_tables
from app.routes import auth, branches, companies, customers, products, inventory, ledgers, orders, tables, waiters, service_requests, users, dashboard
from app import models  # Ensure all models are registered
import uvicorn
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    await create_db_and_tables()
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(branches.router, prefix="/api/branches", tags=["branches"])
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(ledgers.router, prefix="/api/ledgers", tags=["ledgers"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(tables.router, prefix="/api/tables", tags=["tables"])
app.include_router(waiters.router, prefix="/api/waiters", tags=["waiters"])
app.include_router(service_requests.router, prefix="/api/service-requests", tags=["service-requests"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "Welcome to Dine-Dash API"}

if __name__ == "__main__":
    import sys
    if getattr(sys, 'frozen', False):
        # Running as a bundled executable
        uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
    else:
        # Running in development mode
        uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
