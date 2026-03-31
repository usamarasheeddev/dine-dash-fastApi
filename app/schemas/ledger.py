from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class VoucherBase(BaseModel):
    customer_id: int
    amount: Decimal
    type: str # credit or debit
    description: Optional[str] = None
    date: Optional[datetime] = None

class VoucherCreate(VoucherBase):
    pass

class VoucherOut(VoucherBase):
    id: int
    company_id: int
    created_at: datetime
    
    class CustomerOut(BaseModel):
        id: int
        name: str
        
    customer: Optional[CustomerOut] = None

    class Config:
        from_attributes = True
