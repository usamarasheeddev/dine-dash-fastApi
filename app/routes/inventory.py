from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.inventory_item import InventoryItem
from app.models.inventory_ledger import InventoryLedger
from app.models.product import Product
from app.models.user import User
from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemOut,
    InventoryLedgerCreate, InventoryLedgerOut
)
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[InventoryItemOut])
async def get_items(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.company_id == current_user.company_id)
        .options(selectinload(InventoryItem.linked_product))
        .order_by(InventoryItem.created_at.desc())
    )
    return result.scalars().all()

@router.post("/", response_model=InventoryItemOut, status_code=status.HTTP_201_CREATED)
async def add_item(
    item_data: InventoryItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_item = InventoryItem(
        company_id=current_user.company_id,
        name=item_data.name,
        unit=item_data.unit or "piece",
        current_stock=item_data.quantity,
        min_stock=item_data.min_stock,
        cost_price=item_data.cost_per_unit,
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    
    # Reload for response
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == new_item.id).options(selectinload(InventoryItem.linked_product))
    )
    return result.scalars().first()

@router.put("/{id}", response_model=InventoryItemOut)
async def update_item(
    id: int,
    item_data: InventoryItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == id, InventoryItem.company_id == current_user.company_id)
        .options(selectinload(InventoryItem.linked_product))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    update_dict = item_data.dict(exclude_unset=True)
    # Map schema field names to model column names
    field_map = {
        "quantity": "current_stock",
        "cost_per_unit": "cost_price",
    }
    for key, value in update_dict.items():
        model_key = field_map.get(key, key)
        if hasattr(item, model_key):
            setattr(item, model_key, value)
        
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{id}")
async def delete_item(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == id, InventoryItem.company_id == current_user.company_id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
        
    await db.delete(item)
    await db.commit()
    return {"message": "Inventory item deleted"}

@router.post("/{id}/movement")
async def add_stock_movement(
    id: int,
    movement_data: InventoryLedgerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == id, InventoryItem.company_id == current_user.company_id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    parsed_quantity = abs(movement_data.quantity)
    if parsed_quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid quantity")
        
    previous_stock = float(item.current_stock or 0)
    new_stock = previous_stock
    quantity_change = 0
    
    if movement_data.type == "addition":
        quantity_change = parsed_quantity
        new_stock = previous_stock + parsed_quantity
    elif movement_data.type == "deduction":
        quantity_change = -parsed_quantity
        new_stock = previous_stock - parsed_quantity
        if new_stock < 0: new_stock = 0
    elif movement_data.type == "adjustment":
        new_stock = parsed_quantity
        quantity_change = new_stock - previous_stock
    else:
        raise HTTPException(status_code=400, detail="Invalid movement type")
        
    item.current_stock = new_stock
    
    ledger = InventoryLedger(
        inventory_item_id=item.id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        type=movement_data.type,
        quantity_change=quantity_change,
        previous_stock=previous_stock,
        new_stock=new_stock,
        note=movement_data.note or ""
    )
    db.add(ledger)
    await db.commit()
    await db.refresh(item)
    await db.refresh(ledger)
    
    return {"item": item, "ledger": ledger}

@router.get("/{id}/ledger", response_model=List[InventoryLedgerOut])
async def get_inventory_ledger(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify item belongs to company
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == id, InventoryItem.company_id == current_user.company_id)
    )
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Inventory item not found")
        
    result = await db.execute(
        select(InventoryLedger)
        .where(InventoryLedger.inventory_item_id == id, InventoryLedger.company_id == current_user.company_id)
        .options(selectinload(InventoryLedger.user))
        .order_by(InventoryLedger.created_at.desc())
    )
    return result.scalars().all()
