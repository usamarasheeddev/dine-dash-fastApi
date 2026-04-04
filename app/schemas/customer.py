from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class CustomerLedgerBase(BaseModel):
    type: str # credit, debit, payment
    amount: Decimal
    note: Optional[str] = None
    date: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class CustomerLedgerCreate(CustomerLedgerBase):
    pass

class CustomerLedgerOut(CustomerLedgerBase):
    id: int
    customer_id: int
    company_id: int
    created_at: datetime
    
    class Config:
        pass

class CustomerBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    initial_balance: Decimal = Decimal("0.00")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )

class CustomerOut(CustomerBase):
    id: int
    current_balance: Decimal
    orders: int = 0
    ledger: List[CustomerLedgerOut] = []
    created_at: datetime

    class Config:
        pass
