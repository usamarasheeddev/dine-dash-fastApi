from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    status: str = "active"
    subscriptionPlan: str = "basic"
    expiryDate: Optional[datetime] = None
    subscriptionPrice: float = 0.00
    address: Optional[str] = None
    phone: Optional[str] = None
    phone2: Optional[str] = None
    currency: str = "USD"
    timezone: str = "America/New_York"
    taxRate: float = 10.00
    receiptHeader: Optional[str] = None
    receiptFooter: Optional[str] = None
    orderTypes: Dict = {"dineIn": True, "takeaway": True, "delivery": True}
    kitchenEnabled: bool = False

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BranchBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    companyId: int

class BranchCreate(BranchBase):
    pass

class Branch(BranchBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "user"
    branchId: Optional[int] = None
    companyId: int

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WaiterBase(BaseModel):
    name: str
    phone: Optional[str] = None
    active: bool = True
    companyId: int

class WaiterCreate(WaiterBase):
    pass

class Waiter(WaiterBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TableBase(BaseModel):
    tableNo: str
    capacity: int = 2
    status: str = "available"
    companyId: int

class TableCreate(TableBase):
    pass

class Table(TableBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_details: dict

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

