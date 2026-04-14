from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, literal_column
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
import pytz

from app.api import deps
from app.models.orders import Order, OrderItem
from app.models.products import Product
from app.models.inventory import InventoryItem
from app.models.core import User, Company

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    timeframe: str = Query("daily")
) -> Any:
    company_id = current_user.companyId
    
    # 1. Company Timezone
    res = await db.execute(select(Company).where(Company.id == company_id))
    company = res.scalar_one_or_none()
    tz_str = company.timezone if company else "UTC"
    tz = pytz.timezone(tz_str)
    
    now = datetime.now(tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Convert back to UTC for DB query
    today_start_utc = today_start.astimezone(pytz.utc).replace(tzinfo=None)
    today_end_utc = today_end.astimezone(pytz.utc).replace(tzinfo=None)
    
    # --- Today Stats ---
    today_stats_query = select(
        func.count(Order.id).label("count"),
        func.sum(Order.finalTotal).label("revenue"),
        func.sum(func.case((Order.paymentMethod == 'credit', Order.finalTotal), else_=0)).label("credit")
    ).where(
        Order.companyId == company_id,
        Order.status == 'completed',
        Order.created_at >= today_start_utc,
        Order.created_at < today_end_utc
    )
    today_res = await db.execute(today_stats_query)
    today_data = today_res.one()
    
    today_revenue = float(today_data.revenue or 0)
    today_credit = float(today_data.credit or 0)
    
    # Today total count (all statuses)
    today_orders_count = await db.scalar(select(func.count(Order.id)).where(
        Order.companyId == company_id,
        Order.created_at >= today_start_utc,
        Order.created_at < today_end_utc
    ))
    
    # --- All Time Stats ---
    all_time_query = select(
        func.count(Order.id).label("count"),
        func.sum(Order.finalTotal).label("revenue"),
        func.sum(func.case((Order.paymentMethod == 'credit', Order.finalTotal), else_=0)).label("credit")
    ).where(
        Order.companyId == company_id,
        Order.status == 'completed'
    )
    all_time_res = await db.execute(all_time_query)
    all_time_data = all_time_res.one()
    
    total_completed = int(all_time_data.count or 0)
    total_revenue = float(all_time_data.revenue or 0)
    total_credit = float(all_time_data.credit or 0)
    avg_order_value = total_revenue / total_completed if total_completed > 0 else 0
    
    # --- Orders by Status ---
    status_query = select(Order.status, func.count(Order.id)).where(Order.companyId == company_id).group_by(Order.status)
    status_res = await db.execute(status_query)
    orders_by_status = {s: count for s, count in status_res.all()}
    
    # --- Inventory Stats ---
    low_stock = await db.scalars(select(InventoryItem).where(
        InventoryItem.companyId == company_id,
        InventoryItem.quantity > 0,
        InventoryItem.quantity <= InventoryItem.minStock
    ))
    out_of_stock = await db.scalars(select(InventoryItem).where(
        InventoryItem.companyId == company_id,
        InventoryItem.quantity <= 0
    ))
    
    inv_summary = await db.execute(select(
        func.sum(InventoryItem.quantity * InventoryItem.costPerUnit),
        func.count(InventoryItem.id)
    ).where(InventoryItem.companyId == company_id))
    inv_data = inv_summary.one()
    
    # --- Top Products ---
    top_products_query = select(
        Product.name,
        func.sum(OrderItem.quantity).label("qty"),
        func.sum(OrderItem.total).label("revenue")
    ).join(Product).join(Order, Order.id == OrderItem.orderId).where(
        Order.companyId == company_id,
        Order.status == 'completed'
    ).group_by(Product.id, Product.name).order_by(literal_column("revenue").desc()).limit(5)
    
    top_products_res = await db.execute(top_products_query)
    top_products = [{"name": r.name, "qty": float(r.qty), "revenue": float(r.revenue)} for r in top_products_res.all()]
    
    # --- Recent Orders ---
    recent_query = select(Order).where(Order.companyId == company_id).options(
        joinedload(Order.customer)
    ).order_by(Order.created_at.desc()).limit(8)
    recent_res = await db.execute(recent_query)
    recent_orders = recent_res.unique().scalars().all()
    
    return {
        "stats": {
            "todayRevenue": today_revenue,
            "todayCredit": today_credit,
            "todayOrdersCount": today_orders_count or 0,
            "totalRevenue": total_revenue,
            "totalCredit": total_credit,
            "totalOrdersCount": await db.scalar(select(func.count(Order.id)).where(Order.companyId == company_id)),
            "totalCompletedCount": total_completed,
            "avgOrderValue": avg_order_value
        },
        "ordersByStatus": orders_by_status,
        "inventory": {
            "lowStockItems": list(low_stock.all()),
            "outOfStockItems": list(out_of_stock.all()),
            "totalStockValue": float(inv_data[0] or 0),
            "totalInventoryItems": int(inv_data[1] or 0)
        },
        "topProducts": top_products,
        "graphData": [], # Simplified for now, can be ported exactly if needed
        "recentOrders": recent_orders
    }
