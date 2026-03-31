from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class ServiceRequestBase(BaseModel):
    company_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class ServiceRequestCreate(ServiceRequestBase):
    password: str

class ServiceRequestUpdateStatus(BaseModel):
    status: str # approved or rejected

class ServiceRequestOut(ServiceRequestBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
