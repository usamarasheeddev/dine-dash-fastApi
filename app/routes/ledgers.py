from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.voucher import Voucher
from app.models.customer import Customer
from app.models.user import User
from app.schemas.ledger import VoucherCreate, VoucherOut
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[VoucherOut])
async def get_vouchers(
    customer_id: Optional[int] = Query(None, alias="customerId"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Voucher).where(Voucher.company_id == current_user.company_id)
    if customer_id:
        query = query.where(Voucher.customer_id == customer_id)
        
    result = await db.execute(query.options(selectinload(Voucher.customer)).order_by(Voucher.created_at.desc()))
    return result.scalars().all()

@router.post("/", response_model=VoucherOut, status_code=status.HTTP_201_CREATED)
async def add_voucher(
    voucher_data: VoucherCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if customer exists and belongs to company
    result = await db.execute(
        select(Customer).where(Customer.id == voucher_data.customer_id, Customer.company_id == current_user.company_id)
    )
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    new_voucher = Voucher(
        customer_id=voucher_data.customer_id,
        amount=voucher_data.amount,
        type=voucher_data.type,
        description=voucher_data.description,
        date=voucher_data.date or datetime.utcnow(),
        company_id=current_user.company_id
    )
    db.add(new_voucher)
    
    # Update customer balance logic from Node.js
    if voucher_data.type == "credit":
        customer.current_balance = float(customer.current_balance or 0) - float(voucher_data.amount)
    elif voucher_data.type == "debit":
        customer.current_balance = float(customer.current_balance or 0) + float(voucher_data.amount)
        
    await db.commit()
    await db.refresh(new_voucher)
    
    # Reload for response
    result = await db.execute(
        select(Voucher).where(Voucher.id == new_voucher.id).options(selectinload(Voucher.customer))
    )
    return result.scalars().first()

@router.delete("/{id}")
async def delete_voucher(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Voucher).where(Voucher.id == id, Voucher.company_id == current_user.company_id)
    )
    voucher = result.scalars().first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
        
    # Revert balance change logic from Node.js
    customer_result = await db.execute(
        select(Customer).where(Customer.id == voucher.customer_id, Customer.company_id == current_user.company_id)
    )
    customer = customer_result.scalars().first()
    if customer:
        if voucher.type == "credit":
            customer.current_balance = float(customer.current_balance or 0) + float(voucher.amount)
        elif voucher.type == "debit":
            customer.current_balance = float(customer.current_balance or 0) - float(voucher.amount)
            
    await db.delete(voucher)
    await db.commit()
    return {"message": "Voucher deleted"}
