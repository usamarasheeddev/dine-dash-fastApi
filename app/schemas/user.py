from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserStaffBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "cashier"
    fullName: Optional[str] = None
    phone: Optional[str] = None

class UserStaffCreate(UserStaffBase):
    password: str = "123456"

class UserStaffUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    fullName: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None

class UserStaffOut(UserStaffBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
