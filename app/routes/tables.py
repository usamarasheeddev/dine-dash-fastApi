from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.core.database import get_db
from app.models.table import Table
from app.models.user import User
from app.schemas.table import TableCreate, TableUpdate, TableOut
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TableOut])
async def get_tables(
    branch_id: Optional[int] = Query(None, alias="branchId"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Table).where(Table.company_id == current_user.company_id)
    if branch_id:
        query = query.where(Table.branch_id == branch_id)
        
    result = await db.execute(query.options(selectinload(Table.branch)))
    return result.scalars().all()

@router.post("/", response_model=TableOut, status_code=status.HTTP_201_CREATED)
async def add_table(
    table_data: TableCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_table = Table(
        table_no=table_data.table_no,
        capacity=table_data.capacity,
        location=table_data.location or "",
        branch_id=table_data.branch_id,
        company_id=current_user.company_id,
        status="available"
    )
    db.add(new_table)
    await db.commit()
    await db.refresh(new_table)
    
    # Reload for response
    result = await db.execute(
        select(Table).where(Table.id == new_table.id).options(selectinload(Table.branch))
    )
    return result.scalars().first()

@router.put("/{id}", response_model=TableOut)
async def update_table(
    id: int,
    table_data: TableUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Table).where(Table.id == id, Table.company_id == current_user.company_id)
        .options(selectinload(Table.branch))
    )
    table = result.scalars().first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    update_dict = table_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(table, key, value)
        
    await db.commit()
    await db.refresh(table)
    return table

@router.delete("/{id}")
async def delete_table(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Table).where(Table.id == id, Table.company_id == current_user.company_id)
    )
    table = result.scalars().first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
        
    await db.delete(table)
    await db.commit()
    return {"message": "Table deleted"}
