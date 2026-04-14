from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

# --- Customers ---
class CustomerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    current_balance: float = 0.00
    companyId: int

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class LedgerBase(BaseModel):
    customerId: int
    companyId: int
    type: str
    amount: float
    note: Optional[str] = None
    date: datetime = datetime.utcnow()

class Ledger(LedgerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Inventory ---
class InventoryBase(BaseModel):
    companyId: int
    productId: Optional[int] = None
    name: str
    category: Optional[str] = None
    unit: str
    quantity: float = 0.00
    minStock: float = 0.00
    costPerUnit: float = 0.00
    supplier: Optional[str] = None

class InventoryCreate(InventoryBase):
    pass

class Inventory(InventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InventoryLedgerBase(BaseModel):
    inventoryItemId: int
    companyId: int
    userId: int
    type: str
    quantityChange: float
    previousStock: float
    newStock: float
    note: Optional[str] = None
    date: datetime = datetime.utcnow()

class InventoryLedger(InventoryLedgerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Orders ---
class OrderItemBase(BaseModel):
    productId: int
    quantity: float
    price: float
    total: float
    variations: Optional[List[Dict]] = None
    addons: Optional[List[Dict]] = None

class OrderItem(OrderItemBase):
    id: int
    orderId: int
    model_config = ConfigDict(from_attributes=True)

class OrderBase(BaseModel):
    orderType: str
    subTotal: float
    discount: float = 0.00
    tax: float = 0.00
    finalTotal: float
    status: str = "pending"
    paymentMethod: str = "pending"
    waiterId: Optional[int] = None
    tableId: Optional[int] = None
    customerId: Optional[int] = None
    branchId: Optional[int] = None
    companyId: int
    isUploaded: bool = False
    editHistory: List[Dict] = []

class OrderCreate(OrderBase):
    items: List[OrderItemBase]

class OrderUpdate(BaseModel):
    items: List[OrderItemBase]
    subTotal: float
    tax: float
    finalTotal: float
    changes: List[str]

class Order(OrderBase):
    id: int
    items: List[OrderItem]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Service Requests ---
class ServiceRequestBase(BaseModel):
    tableId: int
    companyId: int
    type: str
    status: str = "pending"
    note: Optional[str] = None

class ServiceRequestCreate(ServiceRequestBase):
    pass

class ServiceRequest(ServiceRequestBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
