from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.models.customer import Customer
from app.models.customer_ledger import CustomerLedger
from app.models.order import Order
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut, CustomerLedgerCreate
from app.api.deps import get_current_user
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[CustomerOut])
async def get_customers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Customer)
        .where(Customer.company_id == current_user.company_id)
        .options(selectinload(Customer.ledgers), selectinload(Customer.orders))
        .order_by(Customer.created_at.desc())
    )
    customers = result.scalars().all()
    
    # Matching the formatting logic from Node.js
    formatted = []
    for c in customers:
        formatted.append({
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "email": c.email or '',
            "address": c.address,
            "initial_balance": c.initial_balance,
            "current_balance": c.current_balance,
            "orders": len(c.orders),
            "ledger": c.ledgers,
            "created_at": c.created_at
        })
    return formatted

@router.post("/", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
async def add_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_customer = Customer(
        name=customer_data.name,
        phone=customer_data.phone,
        address=customer_data.address,
        email=customer_data.email,
        initial_balance=customer_data.initial_balance,
        current_balance=customer_data.initial_balance,
        company_id=current_user.company_id
    )
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    
    # Return formatted to match CustomerOut
    return {
        "id": new_customer.id,
        "name": new_customer.name,
        "phone": new_customer.phone,
        "email": new_customer.email or '',
        "address": new_customer.address,
        "initial_balance": new_customer.initial_balance,
        "current_balance": new_customer.current_balance,
        "orders": 0,
        "ledger": [],
        "created_at": new_customer.created_at
    }

@router.put("/{id}", response_model=CustomerOut)
async def update_customer(
    id: int,
    customer_data: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Customer).where(Customer.id == id, Customer.company_id == current_user.company_id)
        .options(selectinload(Customer.ledgers), selectinload(Customer.orders))
    )
    customer = result.scalars().first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if customer_data.name is not None:
        customer.name = customer_data.name
    if customer_data.phone is not None:
        customer.phone = customer_data.phone
    if customer_data.address is not None:
        customer.address = customer_data.address
    if customer_data.email is not None:
        customer.email = customer_data.email
        
    await db.commit()
    await db.refresh(customer)
    
    return {
        "id": customer.id,
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email or '',
        "address": customer.address,
        "initial_balance": customer.initial_balance,
        "current_balance": customer.current_balance,
        "orders": len(customer.orders),
        "ledger": customer.ledgers,
        "created_at": customer.created_at
    }

@router.delete("/{id}")
async def delete_customer(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Customer).where(Customer.id == id, Customer.company_id == current_user.company_id)
    )
    customer = result.scalars().first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    await db.delete(customer)
    await db.commit()
    return {"message": "Customer deleted"}

@router.post("/{id}/ledger")
async def add_ledger_entry(
    id: int,
    entry_data: CustomerLedgerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Customer).where(Customer.id == id, Customer.company_id == current_user.company_id)
    )
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if entry_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
        
    new_entry = CustomerLedger(
        customer_id=customer.id,
        company_id=current_user.company_id,
        type=entry_data.type,
        amount=entry_data.amount,
        note=entry_data.note,
        date=datetime.utcnow()
    )
    db.add(new_entry)
    
    # Balance logic from Node.js
    balance_change = 0
    if entry_data.type == "payment":
        balance_change = -entry_data.amount
    else:
        balance_change = entry_data.amount
        
    customer.current_balance = float(customer.current_balance or 0) + float(balance_change)
    if customer.current_balance < 0:
        customer.current_balance = 0
        
    await db.commit()
    await db.refresh(customer)
    await db.refresh(new_entry)
    
    return {"customer": customer, "entry": new_entry}
