from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api import deps
from app.models.core import Table, User, Branch
from app.schemas.core import Table as TableSchema, TableCreate

router = APIRouter()

@router.get("/", response_model=List[TableSchema])
async def get_tables(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    branchId: Optional[int] = Query(None)
) -> Any:
    query = select(Table).where(Table.companyId == current_user.companyId)
    if branchId:
        query = query.where(Table.branchId == branchId)
    
    # Matching include: [{ model: Branch, as: 'branch' }]
    # Note: Table model needs branchId and relationship added if missing.
    # I will check Table model in core.py.
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=TableSchema)
async def create_table(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    table_in: TableCreate
) -> Any:
    new_table = Table(
        tableNo=table_in.tableNo,
        capacity=table_in.capacity,
        status="available",
        companyId=current_user.companyId
    )
    db.add(new_table)
    await db.commit()
    await db.refresh(new_table)
    return new_table

@router.put("/{id}", response_model=TableSchema)
async def update_table(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    table_in: dict
) -> Any:
    result = await db.execute(select(Table).where(Table.id == id, Table.companyId == current_user.companyId))
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
        
    for field, value in table_in.items():
        if hasattr(table, field):
            setattr(table, field, value)
            
    db.add(table)
    await db.commit()
    await db.refresh(table)
    return table

@router.delete("/{id}")
async def delete_table(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int
) -> Any:
    result = await db.execute(select(Table).where(Table.id == id, Table.companyId == current_user.companyId))
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
        
    await db.delete(table)
    await db.commit()
    return {"message": "Table deleted"}
