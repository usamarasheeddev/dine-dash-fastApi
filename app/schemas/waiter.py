from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WaiterBase(BaseModel):
    name: str
    phone: Optional[str] = None
    cnic: Optional[str] = None
    address: Optional[str] = None
    branch_id: int

class WaiterCreate(WaiterBase):
    pass

class WaiterUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    cnic: Optional[str] = None
    address: Optional[str] = None
    branch_id: Optional[int] = None

class WaiterOut(WaiterBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class BranchOut(BaseModel):
        id: int
        name: str
        
    branch: Optional[BranchOut] = None

    class Config:
        from_attributes = True
