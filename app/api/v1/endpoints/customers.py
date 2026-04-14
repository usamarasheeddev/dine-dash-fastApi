from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api import deps
from app.models.customers import Customer, CustomerLedger
from app.models.orders import Order
from app.models.core import User
from app.schemas.customers import Customer as CustomerSchema, CustomerCreate, Ledger as LedgerSchema

router = APIRouter()

@router.get("/", response_model=List[dict]) # Use dict for the custom formatted response
async def get_customers(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # Matching Node logic: include ledger and orders
    query = select(Customer).where(Customer.companyId == current_user.companyId).options(
        joinedload(Customer.ledger_entries),
        joinedload(Customer.orders)
    ).order_by(Customer.created_at.desc())
    
    result = await db.execute(query)
    customers = result.unique().scalars().all()
    
    formatted = []
    for c in customers:
        formatted.append({
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "email": c.email or '',
            "address": c.address,
            "balance": float(c.current_balance),
            "orders": len(c.orders),
            "ledger": [
                {
                    "id": l.id,
                    "type": l.type,
                    "amount": float(l.amount),
                    "note": l.note,
                    "date": l.date
                } for l in c.ledger_entries
            ],
            "createdAt": c.created_at
        })
    
    return formatted

@router.post("/", response_model=CustomerSchema)
async def create_customer(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    customer_in: dict
) -> Any:
    new_customer = Customer(
        name=customer_in.get("name"),
        phone=customer_in.get("phone"),
        email=customer_in.get("email"),
        address=customer_in.get("address"),
        initial_balance=customer_in.get("initial_balance", 0),
        current_balance=customer_in.get("initial_balance", 0),
        companyId=current_user.companyId
    )
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    return new_customer

@router.put("/{id}", response_model=CustomerSchema)
async def update_customer(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    customer_in: dict
) -> Any:
    result = await db.execute(select(Customer).where(Customer.id == id, Customer.companyId == current_user.companyId))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    for field, value in customer_in.items():
        if hasattr(customer, field):
            setattr(customer, field, value)
            
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer

@router.post("/{id}/ledger")
async def add_ledger_entry(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    entry_in: dict
) -> Any:
    result = await db.execute(select(Customer).where(Customer.id == id, Customer.companyId == current_user.companyId))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    amount = float(entry_in.get("amount", 0))
    entry_type = entry_in.get("type") # debit, credit, payment
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
        
    # Create entry
    entry = CustomerLedger(
        customerId=customer.id,
        companyId=current_user.companyId,
        type=entry_type,
        amount=amount,
        note=entry_in.get("note", ""),
        date=datetime.utcnow()
    )
    
    # Balance logic matching Node controller lines 129-141
    if entry_type == 'debit':
        balance_change = amount
    else:
        balance_change = -amount
        
    customer.current_balance = float(customer.current_balance) + balance_change
    if customer.current_balance < 0:
        customer.current_balance = 0
        
    db.add(entry)
    db.add(customer)
    await db.commit()
    await db.refresh(entry)
    await db.refresh(customer)
    
    return {"customer": customer, "entry": entry}
