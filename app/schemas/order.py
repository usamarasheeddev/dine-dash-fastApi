from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_serializer
from pydantic.alias_generators import to_camel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class OrderItemBase(BaseModel):
    product_id: int
    quantity: float
    price: Optional[Decimal] = None
    total: Optional[Decimal] = None
    variations: Optional[List[Dict[str, Any]]] = []
    addons: Optional[List[Dict[str, Any]]] = []

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemOut(OrderItemBase):
    id: int
    order_id: int
    
    class ProductOut(BaseModel):
        id: int
        name: str
        
        model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            alias_generator=to_camel
        )
        
    product: Optional[ProductOut] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class OrderBase(BaseModel):
    order_type: str = Field(..., alias="orderType")
    sub_total: Optional[Decimal] = Field(None, alias="subTotal")
    discount: Optional[Decimal] = Decimal("0.00")
    tax: Optional[Decimal] = Decimal("0.00")
    final_total: Optional[Decimal] = Field(None, alias="finalTotal")
    status: str = "pending"
    payment_method: Optional[str] = Field(None, alias="paymentMethod")
    waiter_id: Optional[int] = Field(None, alias="waiterId")
    table_id: Optional[int] = Field(None, alias="tableId")
    customer_id: Optional[int] = Field(None, alias="customerId")
    branch_id: Optional[int] = Field(None, alias="branchId")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdateStatus(BaseModel):
    status: str

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )

class OrderPay(BaseModel):
    payment_method: str
    discount: Optional[Decimal] = None
    final_total: Optional[Decimal] = None
    status: Optional[str] = "completed"

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )

class OrderOut(OrderBase):
    id: int
    company_id: int = Field(..., alias="companyId")
    created_at: datetime = Field(..., alias="createdAt")
    items: List[OrderItemOut] = []
    
    class CustomerOut(BaseModel):
        id: int
        name: str

        model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            alias_generator=to_camel
        )
    
    class TableOut(BaseModel):
        id: int
        table_no: str = Field(..., alias="tableNo")

        model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            alias_generator=to_camel
        )
        
    class WaiterOut(BaseModel):
        id: int
        name: str = Field(..., alias="fullName")

        model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            alias_generator=to_camel
        )
        
    customer: Optional[CustomerOut] = None
    table: Optional[TableOut] = None
    waiter: Optional[WaiterOut] = None

    @field_serializer("created_at")
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat() + "Z" if dt.tzinfo is None else dt.isoformat()

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class OrdersResponse(BaseModel):
    orders: List[OrderOut]
    total_count: int = Field(..., alias="totalCount")
    total_pages: int = Field(..., alias="totalPages")
    current_page: int = Field(..., alias="currentPage")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )

class OrderReportOut(BaseModel):
    summary: Dict[str, Any]
    orders: List[Dict[str, Any]]
    product_stats: List[Dict[str, Any]] = Field(..., alias="productStats")
    category_stats: List[Dict[str, Any]] = Field(..., alias="categoryStats")
    customer_stats: List[Dict[str, Any]] = Field(..., alias="customerStats")
    ledger: Dict[str, Any]
    pagination: Dict[str, Any]

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )
