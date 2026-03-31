from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.core.database import get_db
from app.models.waiter import Waiter
from app.models.user import User
from app.schemas.waiter import WaiterCreate, WaiterUpdate, WaiterOut
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[WaiterOut])
async def get_waiters(
    branch_id: Optional[int] = Query(None, alias="branchId"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Waiter).where(Waiter.company_id == current_user.company_id)
    if branch_id:
        query = query.where(Waiter.branch_id == branch_id)
        
    result = await db.execute(query.options(selectinload(Waiter.branch)))
    return result.scalars().all()

@router.post("/", response_model=WaiterOut, status_code=status.HTTP_201_CREATED)
async def add_waiter(
    waiter_data: WaiterCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_waiter = Waiter(
        name=waiter_data.name,
        phone=waiter_data.phone,
        cnic=waiter_data.cnic,
        address=waiter_data.address,
        branch_id=waiter_data.branch_id,
        company_id=current_user.company_id
    )
    db.add(new_waiter)
    await db.commit()
    await db.refresh(new_waiter)
    
    # Reload for response
    result = await db.execute(
        select(Waiter).where(Waiter.id == new_waiter.id).options(selectinload(Waiter.branch))
    )
    return result.scalars().first()

@router.put("/{id}", response_model=WaiterOut)
async def update_waiter(
    id: int,
    waiter_data: WaiterUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Waiter).where(Waiter.id == id, Waiter.company_id == current_user.company_id)
        .options(selectinload(Waiter.branch))
    )
    waiter = result.scalars().first()
    if not waiter:
        raise HTTPException(status_code=404, detail="Waiter not found")
    
    update_dict = waiter_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(waiter, key, value)
        
    await db.commit()
    await db.refresh(waiter)
    return waiter

@router.delete("/{id}")
async def delete_waiter(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Waiter).where(Waiter.id == id, Waiter.company_id == current_user.company_id)
    )
    waiter = result.scalars().first()
    if not waiter:
        raise HTTPException(status_code=404, detail="Waiter not found")
        
    await db.delete(waiter)
    await db.commit()
    return {"message": "Waiter deleted"}
