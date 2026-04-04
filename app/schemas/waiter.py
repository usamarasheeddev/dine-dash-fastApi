from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
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

        model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            alias_generator=to_camel
        )
        
    branch: Optional[BranchOut] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )
