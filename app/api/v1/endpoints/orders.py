from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
import json

from app.api import deps
from app.models.orders import Order, OrderItem
from app.models.products import Product
from app.models.customers import Customer, CustomerLedger
from app.models.inventory import InventoryItem, InventoryLedger
from app.models.core import Table, User, Company
from app.schemas.business import Order as OrderSchema, OrderCreate, OrderUpdate

router = APIRouter()

@router.get("/", response_model=dict)
async def get_orders(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: Optional[str] = None,
    status: Optional[str] = None
) -> Any:
    offset = (page - 1) * limit
    
    query = select(Order).where(Order.companyId == current_user.companyId)
    
    if status:
        query = query.where(Order.status == status)
        
    if search:
        # Complex search matching Node Controller logic
        # join with customer to search by name
        query = query.outerjoin(Customer).where(
            or_(
                Order.id.cast(str).like(f"%{search}%"),
                Customer.name.like(f"%{search}%")
            )
        )
        
    # include associations
    query = query.options(
        joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.customer),
        joinedload(Order.waiter),
        joinedload(Order.table)
    ).order_by(Order.created_at.desc())
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_count = await db.scalar(count_query)
    
    # Get rows
    result = await db.execute(query.offset(offset).limit(limit))
    orders = result.unique().scalars().all()
    
    return {
        "orders": orders,
        "totalCount": total_count,
        "totalPages": (total_count + limit - 1) // limit,
        "currentPage": page
    }

@router.post("/", response_model=OrderSchema)
async def create_order(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    order_in: OrderCreate
) -> Any:
    # Replicating createOrder logic with transactions
    async with db.begin():
        new_order = Order(
            orderType=order_in.orderType,
            subTotal=order_in.subTotal,
            discount=order_in.discount,
            tax=order_in.tax,
            finalTotal=order_in.finalTotal,
            status=order_in.status or "pending",
            paymentMethod=order_in.paymentMethod,
            waiterId=order_in.waiterId,
            tableId=order_in.tableId,
            customerId=order_in.customerId,
            branchId=order_in.branchId,
            companyId=current_user.companyId,
            isUploaded=True
        )
        db.add(new_order)
        await db.flush() # Get order ID
        
        for item in order_in.items:
            order_item = OrderItem(
                orderId=new_order.id,
                productId=item.productId,
                quantity=item.quantity,
                price=item.price,
                total=item.total,
                variations=item.variations,
                addons=item.addons
            )
            db.add(order_item)
            
            # Stock & Inventory management
            product_res = await db.execute(select(Product).where(Product.id == item.productId))
            product = product_res.scalar_one_or_none()
            if product:
                product.stock_quantity -= item.quantity
                db.add(product)
                
                # Inventory auto-deduction
                inv_res = await db.execute(select(InventoryItem).where(
                    InventoryItem.productId == product.id, 
                    InventoryItem.companyId == current_user.companyId
                ))
                inv_item = inv_res.scalar_one_or_none()
                if inv_item:
                    prev_stock = float(inv_item.quantity or 0)
                    new_stock = prev_stock - float(item.quantity)
                    inv_item.quantity = new_stock
                    db.add(inv_item)
                    
                    ledger = InventoryLedger(
                        inventoryItemId=inv_item.id,
                        companyId=current_user.companyId,
                        userId=current_user.id,
                        type='deduction',
                        quantityChange=-float(item.quantity),
                        previousStock=prev_stock,
                        new_stock=new_stock,
                        note=f"Auto-deducted for POS Order (Product: {product.name})",
                        date=datetime.utcnow()
                    )
                    db.add(ledger)
                    
        # Dine-in table status
        if order_in.orderType == 'dine-in' and order_in.tableId:
            table_res = await db.execute(select(Table).where(
                Table.id == order_in.tableId, 
                Table.companyId == current_user.companyId
            ))
            table = table_res.scalar_one_or_none()
            if table:
                table.status = 'reserved'
                db.add(table)
                
    # Fetch complete order with items
    res = await db.execute(select(Order).where(Order.id == new_order.id).options(joinedload(Order.items)))
    return res.unique().scalar_one()

@router.put("/{id}/edit", response_model=OrderSchema)
async def edit_order(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    order_update: OrderUpdate
) -> Any:
    # Complex Edit Order logic from controller lines 409-547
    async with db.begin():
        res = await db.execute(select(Order).where(
            Order.id == id, Order.companyId == current_user.companyId
        ).options(joinedload(Order.items)))
        order = res.unique().scalar_one_or_none()
        
        if not order:
             raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status in ["completed", "cancelled"]:
            raise HTTPException(status_code=400, detail="Completed or cancelled orders cannot be edited.")
            
        # 1. Revert stock for old items
        for old_item in order.items:
            product_res = await db.execute(select(Product).where(Product.id == old_item.productId))
            product = product_res.scalar_one_or_none()
            if product:
                product.stock_quantity += float(old_item.quantity)
                db.add(product)
                
                inv_res = await db.execute(select(InventoryItem).where(
                    InventoryItem.productId == product.id, 
                    InventoryItem.companyId == current_user.companyId
                ))
                inv_item = inv_res.scalar_one_or_none()
                if inv_item:
                    prev_stock = float(inv_item.quantity or 0)
                    new_stock = prev_stock + float(old_item.quantity)
                    inv_item.quantity = new_stock
                    db.add(inv_item)
                    
                    ledger = InventoryLedger(
                        inventoryItemId=inv_item.id,
                        companyId=current_user.companyId,
                        userId=current_user.id,
                        type='adjustment',
                        quantityChange=float(old_item.quantity),
                        previousStock=prev_stock,
                        new_stock=new_stock,
                        note=f"Reverted for Order Edit (Order #{order.id})",
                        date=datetime.utcnow()
                    )
                    db.add(ledger)
                    
        # 2. Delete old items
        # Node handles this by Cascade or explicit delete. 
        # I'll explicit delete.
        for old_item in order.items:
            await db.delete(old_item)
            
        # 3. Create new items and deduct stock
        for item in order_update.items:
            new_item = OrderItem(
                orderId=order.id,
                productId=item.productId,
                quantity=item.quantity,
                price=item.price,
                total=item.total,
                variations=item.variations,
                addons=item.addons
            )
            db.add(new_item)
            
            product_res = await db.execute(select(Product).where(Product.id == item.productId))
            product = product_res.scalar_one_or_none()
            if product:
                product.stock_quantity -= float(item.quantity)
                db.add(product)
                
                inv_res = await db.execute(select(InventoryItem).where(
                    InventoryItem.productId == product.id, 
                    InventoryItem.companyId == current_user.companyId
                ))
                inv_item = inv_res.scalar_one_or_none()
                if inv_item:
                   prev_stock = float(inv_item.quantity or 0)
                   new_stock = prev_stock - float(item.quantity)
                   inv_item.quantity = new_stock
                   db.add(inv_item)
                   
                   ledger = InventoryLedger(
                       inventoryItemId=inv_item.id,
                       companyId=current_user.companyId,
                       userId=current_user.id,
                       type='deduction',
                       quantityChange=-float(item.quantity),
                       previousStock=prev_stock,
                       new_stock=new_stock,
                       note=f"Deducted for Order Edit (Order #{order.id})",
                       date=datetime.utcnow()
                   )
                   db.add(ledger)
                   
        # 4. Update order totals and history
        order.subTotal = order_update.subTotal
        order.tax = order_update.tax
        order.finalTotal = order_update.finalTotal
        
        history = list(order.editHistory) if order.editHistory else []
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "changes": order_update.changes
        })
        order.editHistory = history
        db.add(order)
        
    await db.commit()
    # Return fresh state
    res = await db.execute(select(Order).where(Order.id == id).options(joinedload(Order.items)))
    return res.unique().scalar_one()

@router.put("/{id}/status")
async def update_order_status(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    status_in: dict
) -> Any:
    result = await db.execute(select(Order).where(Order.id == id, Order.companyId == current_user.companyId))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    new_status = status_in.get("status")
    order.status = new_status
    
    if (new_status in ["completed", "cancelled"]) and order.tableId:
        table_res = await db.execute(select(Table).where(Table.id == order.tableId, Table.companyId == current_user.companyId))
        table = table_res.scalar_one_or_none()
        if table:
            table.status = 'available'
            db.add(table)
            
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order
