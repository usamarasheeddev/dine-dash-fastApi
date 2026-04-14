from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.api import deps
from app.models.inventory import InventoryItem, InventoryLedger
from app.models.products import Product
from app.models.core import User
from app.schemas.business import Inventory as InventorySchema, InventoryCreate, InventoryLedger as LedgerSchema

router = APIRouter()

@router.get("/", response_model=List[InventorySchema])
async def get_items(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # Matching Node logic: include linkedProduct
    query = select(InventoryItem).where(InventoryItem.companyId == current_user.companyId).options(
        joinedload(InventoryItem.linkedProduct) # Note: Need to verify relationship name in model
    ).order_by(InventoryItem.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=InventorySchema)
async def create_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    item_in: InventoryCreate
) -> Any:
    new_item = InventoryItem(
        **item_in.model_dump(),
        companyId=current_user.companyId
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

@router.put("/{id}", response_model=InventorySchema)
async def update_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    item_in: dict
) -> Any:
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == id, InventoryItem.companyId == current_user.companyId))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
        
    for field, value in item_in.items():
        if hasattr(item, field):
            setattr(item, field, value)
            
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.post("/{id}/movement")
async def add_stock_movement(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    movement_in: dict
) -> Any:
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == id, InventoryItem.companyId == current_user.companyId))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
        
    m_type = movement_in.get("type") # addition, deduction, adjustment
    quantity = abs(float(movement_in.get("quantity", 0)))
    
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid quantity")
        
    previous_stock = float(item.quantity or 0)
    quantity_change = 0
    new_stock = previous_stock
    
    if m_type == 'addition':
        quantity_change = quantity
        new_stock = previous_stock + quantity
    elif m_type == 'deduction':
        quantity_change = -quantity
        new_stock = previous_stock - quantity
        if new_stock < 0: new_stock = 0
    elif m_type == 'adjustment':
        new_stock = quantity
        quantity_change = new_stock - previous_stock
    else:
        raise HTTPException(status_code=400, detail="Invalid movement type")
        
    item.quantity = new_stock
    
    ledger = InventoryLedger(
        inventoryItemId=item.id,
        companyId=current_user.companyId,
        userId=current_user.id,
        type=m_type,
        quantityChange=quantity_change,
        previousStock=previous_stock,
        newStock=new_stock,
        note=movement_in.get("note", ""),
        date=datetime.utcnow()
    )
    
    db.add(item)
    db.add(ledger)
    await db.commit()
    await db.refresh(item)
    await db.refresh(ledger)
    
    return {"item": item, "ledger": ledger}

@router.get("/{id}/ledger", response_model=List[LedgerSchema])
async def get_inventory_ledger(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int
) -> Any:
    # Verify item access
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == id, InventoryItem.companyId == current_user.companyId))
    if not result.scalar_one_or_none():
         raise HTTPException(status_code=404, detail="Inventory item not found")
         
    query = select(InventoryLedger).where(
        InventoryLedger.inventoryItemId == id, 
        InventoryLedger.companyId == current_user.companyId
    ).options(joinedload(InventoryLedger.user)).order_by(InventoryLedger.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()
