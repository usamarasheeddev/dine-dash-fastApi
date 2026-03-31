from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class CustomerLedgerBase(BaseModel):
    type: str # credit, debit, payment
    amount: Decimal
    note: Optional[str] = None
    date: Optional[datetime] = None

class CustomerLedgerCreate(CustomerLedgerBase):
    pass

class CustomerLedgerOut(CustomerLedgerBase):
    id: int
    customer_id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    initial_balance: Decimal = Decimal("0.00")

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None

class CustomerOut(CustomerBase):
    id: int
    current_balance: Decimal
    orders: int = 0
    ledger: List[CustomerLedgerOut] = []
    created_at: datetime

    class Config:
        from_attributes = True
