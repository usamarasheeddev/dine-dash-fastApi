from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class InventoryLedgerBase(BaseModel):
    type: str # addition, deduction, adjustment
    quantity_change: float
    previous_stock: float
    new_stock: float
    note: Optional[str] = None

class InventoryLedgerCreate(BaseModel):
    type: str
    quantity: float
    note: Optional[str] = None

class InventoryLedgerOut(InventoryLedgerBase):
    id: int
    inventory_item_id: int
    company_id: int
    user_id: int
    created_at: datetime
    
    class UserOut(BaseModel):
        id: int
        username: str
        email: str
    
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True

class InventoryItemBase(BaseModel):
    name: str
    category: Optional[str] = ""
    unit: str = "piece"
    quantity: float = 0
    min_stock: float = 0
    cost_per_unit: Decimal = Decimal("0.00")
    supplier: Optional[str] = ""
    product_id: Optional[int] = None

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = None
    min_stock: Optional[float] = None
    cost_per_unit: Optional[Decimal] = None
    supplier: Optional[str] = None
    product_id: Optional[int] = None

class InventoryItemOut(InventoryItemBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class LinkedProductOut(BaseModel):
        id: int
        name: str
        price: Decimal
        
    linked_product: Optional[LinkedProductOut] = None

    class Config:
        from_attributes = True
