from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.core import Waiter, User
from app.schemas.core import Waiter as WaiterSchema, WaiterCreate

router = APIRouter()

@router.get("/", response_model=List[WaiterSchema])
async def get_waiters(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    branchId: Optional[int] = Query(None)
) -> Any:
    query = select(Waiter).where(Waiter.companyId == current_user.companyId)
    if branchId:
        query = query.where(Waiter.branchId == branchId)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=WaiterSchema)
async def create_waiter(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    waiter_in: WaiterCreate
) -> Any:
    new_waiter = Waiter(
        name=waiter_in.name,
        phone=waiter_in.phone,
        active=waiter_in.active,
        companyId=current_user.companyId
    )
    db.add(new_waiter)
    await db.commit()
    await db.refresh(new_waiter)
    return new_waiter

@router.put("/{id}", response_model=WaiterSchema)
async def update_waiter(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    waiter_in: dict
) -> Any:
    result = await db.execute(select(Waiter).where(Waiter.id == id, Waiter.companyId == current_user.companyId))
    waiter = result.scalar_one_or_none()
    if not waiter:
        raise HTTPException(status_code=404, detail="Waiter not found")
        
    for field, value in waiter_in.items():
        if hasattr(waiter, field):
            setattr(waiter, field, value)
            
    db.add(waiter)
    await db.commit()
    await db.refresh(waiter)
    return waiter

@router.delete("/{id}")
async def delete_waiter(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int
) -> Any:
    result = await db.execute(select(Waiter).where(Waiter.id == id, Waiter.companyId == current_user.companyId))
    waiter = result.scalar_one_or_none()
    if not waiter:
        raise HTTPException(status_code=404, detail="Waiter not found")
        
    await db.delete(waiter)
    await db.commit()
    return {"message": "Waiter deleted"}
