from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

class CompanyBase(BaseModel):
    name: str
    email: EmailStr
    status: str = "active"
    subscription_plan: str = "basic"
    expiry_date: Optional[datetime] = None
    subscription_price: Decimal = Decimal("0.00")
    address: Optional[str] = None
    phone: Optional[str] = None
    phone2: Optional[str] = None
    currency: str = "USD"
    timezone: str = "America/New_York"
    tax_rate: Decimal = Decimal("10.00")
    receipt_header: Optional[str] = None
    receipt_footer: Optional[str] = None
    order_types: Dict[str, bool] = {"dineIn": True, "takeaway": True, "delivery": True}
    kitchen_enabled: bool = False

class CompanyCreate(BaseModel):
    companyName: str
    companyEmail: EmailStr
    subscriptionPlan: str = "basic"
    adminName: str
    adminEmail: EmailStr
    adminPassword: str

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[str] = None
    subscription_plan: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    phone2: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    tax_rate: Optional[Decimal] = None
    receipt_header: Optional[str] = None
    receipt_footer: Optional[str] = None
    order_types: Optional[Dict[str, bool]] = None
    kitchen_enabled: Optional[bool] = None

class CompanyOut(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    totalCompanies: int
    activeCompanies: int
    disabledCompanies: int
    totalRevenue: float
    expiringSoon: int
    pendingRequests: int
    totalUsers: int
