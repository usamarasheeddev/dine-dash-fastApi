from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, literal_column, text
from sqlalchemy.orm import selectinload, joinedload
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.inventory_item import InventoryItem
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    timeframe: str = Query("daily"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        company_id = current_user.company_id
        
        # 1. Today Stats
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1, microseconds=-1)
        
        today_query = select(
            func.count(Order.id).label("count"),
            func.sum(Order.final_total).label("revenue")
        ).where(
            Order.company_id == company_id,
            Order.status == "completed",
            Order.created_at.between(today_start, today_end)
        )
        today_res = await db.execute(today_query)
        today_stats = today_res.mappings().first()
        
        today_revenue = float(today_stats["revenue"] or 0)
        today_orders_count = int(today_stats["count"] or 0)
        
        # 2. All Time Stats
        all_time_query = select(
            func.count(Order.id).label("count"),
            func.sum(Order.final_total).label("revenue")
        ).where(
            Order.company_id == company_id,
            Order.status == "completed"
        )
        all_time_res = await db.execute(all_time_query)
        all_time_stats = all_time_res.mappings().first()
        
        total_revenue = float(all_time_stats["revenue"] or 0)
        total_completed_count = int(all_time_stats["count"] or 0)
        
        total_orders_count_res = await db.execute(select(func.count(Order.id)).where(Order.company_id == company_id))
        total_orders_count = total_orders_count_res.scalar() or 0
        
        avg_order_value = total_revenue / total_completed_count if total_completed_count > 0 else 0
        
        # 3. Orders by Status
        status_query = select(
            Order.status, func.count(Order.id).label("count")
        ).where(Order.company_id == company_id).group_by(Order.status)
        status_res = await db.execute(status_query)
        status_groups = status_res.mappings().all()
        
        orders_by_status = {"new": 0, "preparing": 0, "pending": 0, "completed": 0, "cancelled": 0}
        for g in status_groups:
            if g["status"] in orders_by_status:
                orders_by_status[g["status"]] = g["count"]
                
        # 4. Inventory Stats
        low_stock_query = select(InventoryItem).where(
            InventoryItem.company_id == company_id,
            InventoryItem.quantity > 0,
            InventoryItem.quantity <= InventoryItem.min_stock
        )
        low_stock_res = await db.execute(low_stock_query)
        low_stock_items = low_stock_res.scalars().all()
        
        out_of_stock_query = select(InventoryItem).where(
            InventoryItem.company_id == company_id,
            InventoryItem.quantity <= 0
        )
        out_of_stock_res = await db.execute(out_of_stock_query)
        out_of_stock_items = out_of_stock_res.scalars().all()
        
        inventory_summary_query = select(
            func.sum(InventoryItem.quantity * InventoryItem.cost_per_unit).label("totalValue"),
            func.count(InventoryItem.id).label("count")
        ).where(InventoryItem.company_id == company_id)
        inv_summary_res = await db.execute(inventory_summary_query)
        inv_summary = inv_summary_res.mappings().first()
        
        total_stock_value = float(inv_summary["totalValue"] or 0)
        total_inventory_items = int(inv_summary["count"] or 0)
        
        # 5. Top Selling Products
        top_products_query = select(
            Product.name,
            func.sum(OrderItem.quantity).label("qty"),
            func.sum(OrderItem.total).label("revenue")
        ).join(OrderItem.product).join(OrderItem.order).where(
            Order.company_id == company_id,
            Order.status == "completed"
        ).group_by(Product.id, Product.name).order_by(text("revenue DESC")).limit(5)
        
        top_products_res = await db.execute(top_products_query)
        top_products = top_products_res.mappings().all()
        
        # 6. Graph Data (Simplified version for SQLite compatibility if needed, but we targeting Postgres patterns)
        graph_data = []
        if timeframe == "daily":
            since = datetime.utcnow() - timedelta(hours=24)
            trunc = "hour"
        elif timeframe == "weekly":
            since = datetime.utcnow() - timedelta(days=7)
            trunc = "day"
        else: # monthly
            since = datetime.utcnow() - timedelta(days=30)
            trunc = "day"
            
        # Using raw SQL for date_trunc to ensure precision or simple grouping
        graph_query = select(
            func.date_trunc(trunc, Order.created_at).label("time"),
            func.sum(Order.final_total).label("revenue")
        ).where(
            Order.company_id == company_id,
            Order.status == "completed",
            Order.created_at >= since
        ).group_by(func.date_trunc(trunc, Order.created_at)).order_by(text("time ASC"))
        
        graph_res = await db.execute(graph_query)
        raw_graph = graph_res.mappings().all()
        
        # Formatting graph data for frontend parity
        for g in raw_graph:
            if timeframe == "daily":
                label = g["time"].strftime("%I %p") # e.g. 02 PM
            elif timeframe == "weekly":
                label = g["time"].strftime("%a") # Sat
            else:
                label = g["time"].strftime("%b %d") # Oct 12
            graph_data.append({"day": label, "revenue": float(g["revenue"] or 0)})
            
        # 7. Recent Orders
        recent_orders_query = select(Order).where(
            Order.company_id == company_id
        ).options(joinedload(Order.customer)).order_by(Order.created_at.desc()).limit(8)
        recent_orders_res = await db.execute(recent_orders_query)
        recent_orders = recent_orders_res.scalars().all()
        
        return {
            "stats": {
                "todayRevenue": today_revenue,
                "todayOrdersCount": today_orders_count,
                "totalRevenue": total_revenue,
                "totalOrdersCount": total_orders_count,
                "totalCompletedCount": total_completed_count,
                "avgOrderValue": avg_order_value
            },
            "ordersByStatus": orders_by_status,
            "inventory": {
                "lowStockItems": low_stock_items,
                "outOfStockItems": out_of_stock_items,
                "totalStockValue": total_stock_value,
                "totalInventoryItems": total_inventory_items
            },
            "topProducts": top_products,
            "graphData": graph_data,
            "recentOrders": recent_orders
        }
        
    except Exception as e:
        # Better error logging
        raise HTTPException(status_code=500, detail=f"Dashboard Stats Error: {str(e)}")
