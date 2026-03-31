from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TableBase(BaseModel):
    table_no: str
    capacity: int = 2
    location: Optional[str] = ""
    branch_id: int
    status: str = "available"

class TableCreate(TableBase):
    pass

class TableUpdate(BaseModel):
    table_no: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    branch_id: Optional[int] = None
    status: Optional[str] = None

class TableOut(TableBase):
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
