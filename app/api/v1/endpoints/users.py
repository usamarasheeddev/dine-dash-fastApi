from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.core import User
from app.schemas.core import User as UserSchema, UserCreate
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/staff", response_model=List[UserSchema])
async def get_staff(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(select(User).where(User.companyId == current_user.companyId))
    return result.scalars().all()

@router.post("/staff", response_model=UserSchema)
async def create_staff(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    user_in: UserCreate
) -> Any:
    # Check if exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")
        
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password=get_password_hash(user_in.password or "123456"),
        role=user_in.role or "cashier",
        companyId=current_user.companyId,
        branchId=user_in.branchId
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.put("/staff/{id}", response_model=UserSchema)
async def update_staff(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    user_in: dict
) -> Any:
    result = await db.execute(select(User).where(User.id == id, User.companyId == current_user.companyId))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
        
    if "email" in user_in and user_in["email"] != staff.email:
        res = await db.execute(select(User).where(User.email == user_in["email"]))
        if res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already exists")
            
    for field, value in user_in.items():
        if field == "password" and value:
            setattr(staff, "password", get_password_hash(value))
        elif hasattr(staff, field):
            setattr(staff, field, value)
            
    db.add(staff)
    await db.commit()
    await db.refresh(staff)
    return staff

@router.delete("/staff/{id}")
async def delete_staff(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int
) -> Any:
    result = await db.execute(select(User).where(User.id == id, User.companyId == current_user.companyId))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
        
    await db.delete(staff)
    await db.commit()
    return {"message": "Staff member removed successfully"}
