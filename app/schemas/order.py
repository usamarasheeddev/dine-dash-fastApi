from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class OrderItemBase(BaseModel):
    product_id: int
    quantity: float
    price: Decimal
    total: Decimal
    variations: Optional[List[Dict[str, Any]]] = []
    addons: Optional[List[Dict[str, Any]]] = []

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemOut(OrderItemBase):
    id: int
    order_id: int
    
    class ProductOut(BaseModel):
        id: int
        name: str
        
    product: Optional[ProductOut] = None

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    order_type: str
    sub_total: Decimal
    discount: Decimal = Decimal("0.00")
    tax: Decimal = Decimal("0.00")
    final_total: Decimal
    status: str = "pending"
    payment_method: Optional[str] = None
    waiter_id: Optional[int] = None
    table_id: Optional[int] = None
    customer_id: Optional[int] = None
    branch_id: Optional[int] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdateStatus(BaseModel):
    status: str

class OrderPay(BaseModel):
    payment_method: str
    discount: Optional[Decimal] = None
    final_total: Optional[Decimal] = None
    status: Optional[str] = "completed"

class OrderOut(OrderBase):
    id: int
    company_id: int
    created_at: datetime
    items: List[OrderItemOut] = []
    
    class CustomerOut(BaseModel):
        id: int
        name: str
    
    class TableOut(BaseModel):
        id: int
        name: str
        
    class WaiterOut(BaseModel):
        id: int
        fullName: str
        
    customer: Optional[CustomerOut] = None
    table: Optional[TableOut] = None
    waiter: Optional[WaiterOut] = None

    class Config:
        from_attributes = True

class OrderReportOut(BaseModel):
    summary: Dict[str, Any]
    orders: List[Dict[str, Any]]
    productStats: List[Dict[str, Any]]
    categoryStats: List[Dict[str, Any]]
    customerStats: List[Dict[str, Any]]
    ledger: Dict[str, Any]
    pagination: Dict[str, Any]
