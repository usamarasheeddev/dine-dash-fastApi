from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer
from pydantic.alias_generators import to_camel
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal

class InventoryLedgerBase(BaseModel):
    type: str # addition, deduction, adjustment
    quantity_change: float
    previous_stock: float
    new_stock: float
    note: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class InventoryLedgerCreate(BaseModel):
    type: str
    quantity: float
    note: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )

class InventoryLedgerOut(InventoryLedgerBase):
    id: int
    inventory_item_id: int
    company_id: int
    user_id: int
    created_at: datetime
    
    class UserOut(BaseModel):
        id: int
        full_name: str = Field(..., alias="name")
    
    user: Optional[UserOut] = None

    @field_serializer("created_at")
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat() + "Z" if dt.tzinfo is None else dt.isoformat()

class InventoryItemBase(BaseModel):
    name: str
    category: Optional[str] = ""
    unit: str = "piece"
    # Map current_stock from model to quantity in schema/frontend
    quantity: float = Field(0, validation_alias="current_stock", alias="quantity")
    min_stock: float = Field(0, validation_alias="min_stock", alias="minStock")
    # Map cost_price from model to costPerUnit in schema/frontend
    cost_per_unit: Decimal = Field(Decimal("0.00"), validation_alias="cost_price", alias="costPerUnit")
    supplier: Optional[str] = ""
    # Map product_id (if any)
    product_id: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = Field(None, alias="quantity")
    min_stock: Optional[float] = Field(None, alias="minStock")
    cost_per_unit: Optional[Decimal] = Field(None, alias="costPerUnit")
    supplier: Optional[str] = None
    product_id: Optional[int] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )

class InventoryItemOut(InventoryItemBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class LinkedProductOut(BaseModel):
        id: int
        name: str
        price: Decimal
        
    linked_product: Optional[LinkedProductOut] = Field(None, validation_alias="products", alias="linkedProduct")

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat() + "Z" if dt.tzinfo is None else dt.isoformat()

    @field_validator("linked_product", mode="before")
    @classmethod
    def extract_first_product(cls, v: Any) -> Any:
        # SQLAlchemy returns a list of products for the 'products' relationship
        if isinstance(v, list):
            return v[0] if v else None
        return v
