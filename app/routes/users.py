from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserStaffCreate, UserStaffUpdate, UserStaffOut
from app.api.deps import get_current_user, RoleChecker
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/", response_model=List[UserStaffOut])
async def get_staff(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.company_id == current_user.company_id)
    )
    return result.scalars().all()

@router.post("/", response_model=UserStaffOut, status_code=status.HTTP_201_CREATED)
async def create_staff(
    staff_data: UserStaffCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if email exists
    result = await db.execute(select(User).where(User.email == staff_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already exists")
        
    new_staff = User(
        username=staff_data.username,
        email=staff_data.email,
        password=get_password_hash(staff_data.password),
        role=staff_data.role,
        fullName=staff_data.fullName,
        phone=staff_data.phone,
        company_id=current_user.company_id
    )
    db.add(new_staff)
    await db.commit()
    await db.refresh(new_staff)
    return new_staff

@router.put("/{id}", response_model=UserStaffOut)
async def update_staff(
    id: int,
    staff_data: UserStaffUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == id, User.company_id == current_user.company_id)
    )
    staff = result.scalars().first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
        
    if staff_data.email and staff_data.email != staff.email:
        email_check = await db.execute(select(User).where(User.email == staff_data.email))
        if email_check.scalars().first():
            raise HTTPException(status_code=400, detail="Email already exists")
            
    update_dict = staff_data.dict(exclude_unset=True)
    if "password" in update_dict and update_dict["password"]:
        update_dict["password"] = get_password_hash(update_dict["password"])
    elif "password" in update_dict:
        del update_dict["password"]
        
    for key, value in update_dict.items():
        setattr(staff, key, value)
        
    await db.commit()
    await db.refresh(staff)
    return staff

@router.delete("/{id}")
async def delete_staff(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == id, User.company_id == current_user.company_id)
    )
    staff = result.scalars().first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
        
    await db.delete(staff)
    await db.commit()
    return {"message": "Staff member removed successfully"}
