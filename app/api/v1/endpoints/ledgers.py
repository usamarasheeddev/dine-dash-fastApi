from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.api import deps
from app.models.customers import Voucher, Customer
from app.models.core import User

router = APIRouter()

@router.get("/")
async def get_vouchers(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    customerId: Optional[int] = Query(None)
) -> Any:
    query = select(Voucher).where(Voucher.companyId == current_user.companyId).options(
        joinedload(Voucher.customer)
    )
    if customerId:
        query = query.where(Voucher.customerId == customerId)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/")
async def add_voucher(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    voucher_in: dict
) -> Any:
    # Logic from ledgerController.addVoucher
    customer_id = voucher_in.get("customerId")
    amount = float(voucher_in.get("amount", 0))
    v_type = voucher_in.get("type") # credit or debit
    
    async with db.begin():
        new_voucher = Voucher(
            customerId=customer_id,
            amount=amount,
            type=v_type,
            note=voucher_in.get("description") or voucher_in.get("note"),
            date=datetime.utcnow(),
            companyId=current_user.companyId
        )
        db.add(new_voucher)
        
        # Update Customer Balance
        res = await db.execute(select(Customer).where(
            Customer.id == customer_id, 
            Customer.companyId == current_user.companyId
        ))
        customer = res.scalar_one_or_none()
        if customer:
            if v_type == 'credit':
                customer.current_balance = float(customer.current_balance) - amount
            elif v_type == 'debit':
                customer.current_balance = float(customer.current_balance) + amount
            db.add(customer)
            
    await db.commit()
    return new_voucher

@router.delete("/{id}")
async def delete_voucher(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int
) -> Any:
    async with db.begin():
        res = await db.execute(select(Voucher).where(
            Voucher.id == id, 
            Voucher.companyId == current_user.companyId
        ))
        voucher = res.scalar_one_or_none()
        if not voucher:
            raise HTTPException(status_code=404, detail="Voucher not found")
            
        # Revert balance
        cus_res = await db.execute(select(Customer).where(
            Customer.id == voucher.customerId, 
            Customer.companyId == current_user.companyId
        ))
        customer = cus_res.scalar_one_or_none()
        if customer:
            if voucher.type == 'credit':
                customer.current_balance = float(customer.current_balance) + float(voucher.amount)
            elif voucher.type == 'debit':
                customer.current_balance = float(customer.current_balance) - float(voucher.amount)
            db.add(customer)
            
        await db.delete(voucher)
        
    await db.commit()
    return {"message": "Voucher deleted"}
