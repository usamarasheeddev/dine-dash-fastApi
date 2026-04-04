from pydantic.alias_generators import to_camel
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from app.schemas.order import OrderOut
from app.schemas.inventory import InventoryItemOut

class DashboardStatsSub(BaseModel):
    today_revenue: float
    today_orders_count: int
    total_revenue: float
    total_orders_count: int
    total_completed_count: int
    avg_order_value: float

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class InventoryStats(BaseModel):
    low_stock_items: List[InventoryItemOut]
    out_of_stock_items: List[InventoryItemOut]
    total_stock_value: float
    total_inventory_items: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class TopProductStats(BaseModel):
    name: str
    qty: float
    revenue: float

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class GraphDataPoint(BaseModel):
    day: str
    revenue: float

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class DashboardResponse(BaseModel):
    stats: DashboardStatsSub
    orders_by_status: Dict[str, int]
    inventory: InventoryStats
    top_products: List[TopProductStats]
    graph_data: List[GraphDataPoint]
    recent_orders: List[OrderOut]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )
