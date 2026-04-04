from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, List
from datetime import datetime

class TableBase(BaseModel):
    table_no: str
    capacity: int = 2
    location: Optional[str] = ""
    branch_id: int
    status: str = "available"

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class TableCreate(TableBase):
    pass

class TableUpdate(BaseModel):
    table_no: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    branch_id: Optional[int] = None
    status: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )

class TableOut(TableBase):
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
