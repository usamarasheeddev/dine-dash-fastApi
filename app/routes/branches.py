from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.models.branch import Branch
from app.models.user import User
from app.schemas.branch import BranchCreate, BranchUpdate, BranchOut
from app.api.deps import get_current_user, RoleChecker

router = APIRouter()

@router.get("/", response_model=List[BranchOut])
async def get_branches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Branch).where(Branch.company_id == current_user.company_id))
    branches = result.scalars().all()
    return branches

@router.post("/", response_model=BranchOut, status_code=status.HTTP_201_CREATED)
async def add_branch(
    branch_data: BranchCreate,
    current_user: User = Depends(RoleChecker(["admin", "superadmin"])),
    db: AsyncSession = Depends(get_db)
):
    new_branch = Branch(
        name=branch_data.name,
        address=branch_data.address,
        phone=branch_data.phone,
        status=branch_data.status,
        company_id=current_user.company_id
    )
    db.add(new_branch)
    await db.commit()
    await db.refresh(new_branch)
    return new_branch

@router.put("/{id}", response_model=BranchOut)
async def update_branch(
    id: int,
    branch_data: BranchUpdate,
    current_user: User = Depends(RoleChecker(["admin", "superadmin"])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Branch).where(Branch.id == id, Branch.company_id == current_user.company_id)
    )
    branch = result.scalars().first()
    
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
    
    if branch_data.name is not None:
        branch.name = branch_data.name
    if branch_data.address is not None:
        branch.address = branch_data.address
    if branch_data.phone is not None:
        branch.phone = branch_data.phone
    if branch_data.status is not None:
        branch.status = branch_data.status
        
    await db.commit()
    await db.refresh(branch)
    return branch

@router.delete("/{id}")
async def delete_branch(
    id: int,
    current_user: User = Depends(RoleChecker(["admin", "superadmin"])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Branch).where(Branch.id == id, Branch.company_id == current_user.company_id)
    )
    branch = result.scalars().first()
    
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
        
    await db.delete(branch)
    await db.commit()
    return {"message": "Branch deleted"}
