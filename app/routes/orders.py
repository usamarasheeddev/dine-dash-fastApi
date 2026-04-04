from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import or_, and_, update
from typing import List, Optional, Dict, Any
from datetime import datetime, time
import json
from app.core.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.customer import Customer
from app.models.inventory_item import InventoryItem
from app.models.inventory_ledger import InventoryLedger
from app.models.table import Table
from app.models.user import User
from app.schemas.order import (
    OrderCreate, OrderOut, OrderUpdateStatus, OrderPay, OrderReportOut, OrdersResponse
)
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=OrdersResponse)
async def get_orders(
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * limit
    
    query = select(Order).where(Order.company_id == current_user.company_id)
    if status:
        query = query.where(Order.status == status)
        
    if search:
        # Complex search for ID or Customer Name
        # Note: Customer name search requires a join or subquery
        query = query.outerjoin(Customer).where(
            or_(
                Order.id.cast(status).like(f"%{search}%"), # cast to string if needed, or stick to simpler
                Customer.name.ilike(f"%{search}%")
            )
        )
        
    # Get count and rows
    # We can do two queries for simplicity in async
    total_count_result = await db.execute(select(Order.id).where(Order.company_id == current_user.company_id))
    total_count = len(total_count_result.scalars().all()) # Simplified count
    
    result = await db.execute(
        query.options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.customer),
            selectinload(Order.table),
            selectinload(Order.waiter)
        )
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    orders = result.scalars().all()
    
    return {
        "orders": orders,
        "total_count": total_count,
        "total_pages": (total_count + limit - 1) // limit if limit > 0 else 1,
        "current_page": page
    }

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        new_order = Order(
            order_type=order_data.order_type,
            sub_total=order_data.sub_total,
            discount=order_data.discount,
            tax=order_data.tax,
            final_total=order_data.final_total,
            status=order_data.status or "pending",
            payment_method=order_data.payment_method,
            waiter_id=order_data.waiter_id,
            table_id=order_data.table_id,
            customer_id=order_data.customer_id,
            branch_id=order_data.branch_id,
            company_id=current_user.company_id,
            is_uploaded=True
        )
        db.add(new_order)
        await db.flush() # Get new_order.id
        
        for item in order_data.items:
            new_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                total=item.total,
                variations=item.variations,
                addons=item.addons
            )
            db.add(new_item)
            
            # Update product stock
            # (In-place update is better but here we fetch and update)
            prod_result = await db.execute(select(Product).where(Product.id == item.product_id))
            product = prod_result.scalars().first()
            if product:
                product.stock_quantity = (product.stock_quantity or 0) - item.quantity
                
                if product.inventory_item_id:
                    inv_result = await db.execute(
                        select(InventoryItem).where(
                            InventoryItem.id == product.inventory_item_id,
                            InventoryItem.company_id == current_user.company_id
                        )
                    )
                    inv_item = inv_result.scalars().first()
                    if inv_item:
                        previous_stock = float(inv_item.current_stock or 0)
                        new_stock = previous_stock - float(item.quantity)
                        inv_item.current_stock = new_stock
                    
                        ledger = InventoryLedger(
                            inventory_item_id=inv_item.id,
                            company_id=current_user.company_id,
                            user_id=current_user.id,
                            type="deduction",
                            quantity_change=-float(item.quantity),
                            previous_stock=previous_stock,
                            new_stock=new_stock,
                            note=f"Auto-deducted for POS Order (Product: {product.name})"
                        )
                        db.add(ledger)
                    
        # Update Table status
        if order_data.order_type == "dine-in" and order_data.table_id:
            await db.execute(
                update(Table)
                .where(Table.id == order_data.table_id, Table.company_id == current_user.company_id)
                .values(status="occupied")
            )
            
        await db.commit()
        
        # Reload for response
        res_query = select(Order).where(Order.id == new_order.id).options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.customer),
            selectinload(Order.table),
            selectinload(Order.waiter)
        )
        final_order = await db.execute(res_query)
        return final_order.scalars().first()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")

@router.put("/{id}/status", response_model=OrderOut)
async def update_order_status(
    id: int,
    status_data: OrderUpdateStatus,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order).where(Order.id == id, Order.company_id == current_user.company_id)
    )
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.status = status_data.status
    
    if (status_data.status == "completed" or status_data.status == "cancelled") and order.table_id:
        await db.execute(
            update(Table)
            .where(Table.id == order.table_id, Table.company_id == current_user.company_id)
            .values(status="available")
        )
        
    await db.commit()
    await db.refresh(order)
    
    # Reload for response
    res_query = select(Order).where(Order.id == order.id).options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.customer),
        selectinload(Order.table),
        selectinload(Order.waiter)
    )
    final_order = await db.execute(res_query)
    return final_order.scalars().first()

@router.put("/{id}/pay", response_model=OrderOut)
async def pay_order(
    id: int,
    pay_data: OrderPay,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order).where(Order.id == id, Order.company_id == current_user.company_id)
    )
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.payment_method = pay_data.payment_method
    if pay_data.discount is not None: order.discount = pay_data.discount
    if pay_data.final_total is not None: order.final_total = pay_data.final_total
    order.status = pay_data.status or "completed"
    
    if (order.status == "completed" or order.status == "cancelled") and order.table_id:
        await db.execute(
            update(Table)
            .where(Table.id == order.table_id, Table.company_id == current_user.company_id)
            .values(status="available")
        )
        
    await db.commit()
    await db.refresh(order)
    
    # Reload for response
    res_query = select(Order).where(Order.id == order.id).options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.customer),
        selectinload(Order.table),
        selectinload(Order.waiter)
    )
    final_order = await db.execute(res_query)
    return final_order.scalars().first()

# --- Report Implementation ---
# This is complex, will implement simplified version for now matching logic
@router.get("/report")
async def get_report(
    startDate: str,
    endDate: str,
    search: Optional[str] = None,
    status: Optional[str] = None,
    orderType: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Date filtering logic
        start_dt = datetime.fromisoformat(startDate.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(endDate.replace("Z", "+00:00"))
        
        query = select(Order).where(
            Order.company_id == current_user.company_id,
            Order.created_at >= start_dt,
            Order.created_at <= end_dt
        )
        
        if status: query = query.where(Order.status == status)
        if orderType: query = query.where(Order.order_type == orderType)
        
        # Join customer for stats and search
        query = query.outerjoin(Customer)
        if search:
            query = query.where(
                or_(
                    Order.id.cast(Order.status).like(f"%{search}%"),
                    Customer.name.ilike(f"%{search}%")
                )
            )
            
        result = await db.execute(
            query.options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.customer)
            ).order_by(Order.created_at.desc())
        )
        all_orders = result.scalars().all()
        
        # Aggregations
        completed_orders = [o for o in all_orders if o.status == "completed"]
        
        total_revenue = sum(float(o.final_total or o.sub_total or 0) for o in completed_orders)
        total_tax = sum(float(o.tax or 0) for o in completed_orders)
        total_discount = sum(float(o.discount or 0) for o in completed_orders)
        avg_order_value = total_revenue / len(completed_orders) if completed_orders else 0
        
        # Product Stats
        product_map = {}
        for o in completed_orders:
            for i in o.items:
                name = i.product.name if i.product else "Unknown Product"
                if name not in product_map:
                    product_map[name] = {"name": name, "qty": 0, "revenue": 0, "variations": [], "addons": []}
                product_map[name]["qty"] += float(i.quantity)
                product_map[name]["revenue"] += float(i.total)
                
        product_stats = sorted(
            [{"name": k, **v} for k, v in product_map.items()],
            key=lambda x: x["revenue"], reverse=True
        )
        
        # Pagination
        offset = (page - 1) * limit
        paginated_orders = all_orders[offset : offset + limit]
        
        return {
            "summary": {
                "totalRevenue": total_revenue,
                "totalOrders": len(all_orders),
                "completedOrders": len(completed_orders),
                "avgOrderValue": avg_order_value,
                "totalTax": total_tax,
                "totalDiscount": total_discount
            },
            "orders": paginated_orders,
            "productStats": product_stats,
            "categoryStats": [], # Placeholder for orderType stats
            "customerStats": [], # Placeholder
            "ledger": {"entries": [], "totalCredit": 0, "totalCount": 0},
            "pagination": {
                "totalCount": len(all_orders),
                "totalPages": (len(all_orders) + limit - 1) // limit,
                "currentPage": page,
                "limit": limit
            }
        }
        
    except Exception as e:
        print(f"Reports API Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error retrieving reports")
