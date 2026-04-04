from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class ProductCategoryBase(BaseModel):
    name: str
    image: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None

class ProductCategoryOut(ProductCategoryBase):
    id: int
    company_id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class ProductBase(BaseModel):
    name: str
    price: Decimal
    cost: Decimal = Decimal("0.00")
    stock_quantity: int = 0
    category_id: Optional[int] = None
    inventory_item_id: Optional[int] = None
    image: Optional[str] = None
    is_favourite: bool = False
    variations: List[Dict[str, Any]] = []
    addons: List[Dict[str, Any]] = []
    active: bool = True

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None
    inventory_item_id: Optional[int] = None
    image: Optional[str] = None
    is_favourite: Optional[bool] = None
    variations: Optional[List[Dict[str, Any]]] = None
    addons: Optional[List[Dict[str, Any]]] = None
    active: Optional[bool] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )

class ProductOut(ProductBase):
    id: int
    company_id: int
    category: Optional[ProductCategoryOut] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )
