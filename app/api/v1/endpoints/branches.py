from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.core import Branch, User
from app.schemas.core import Branch as BranchSchema, BranchCreate

router = APIRouter()

@router.get("/", response_model=List[BranchSchema])
async def get_branches(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(select(Branch).where(Branch.companyId == current_user.companyId))
    return result.scalars().all()

@router.post("/", response_model=BranchSchema)
async def create_branch(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    branch_in: BranchCreate
) -> Any:
    new_branch = Branch(
        name=branch_in.name,
        address=branch_in.address,
        phone=branch_in.phone,
        companyId=current_user.companyId
    )
    db.add(new_branch)
    await db.commit()
    await db.refresh(new_branch)
    return new_branch

@router.put("/{id}", response_model=BranchSchema)
async def update_branch(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    branch_in: dict
) -> Any:
    result = await db.execute(select(Branch).where(Branch.id == id, Branch.companyId == current_user.companyId))
    branch = result.scalar_one_or_none()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
        
    for field, value in branch_in.items():
        if hasattr(branch, field):
            setattr(branch, field, value)
            
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch

@router.delete("/{id}")
async def delete_branch(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int
) -> Any:
    result = await db.execute(select(Branch).where(Branch.id == id, Branch.companyId == current_user.companyId))
    branch = result.scalar_one_or_none()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
        
    await db.delete(branch)
    await db.commit()
    return {"message": "Branch deleted"}
