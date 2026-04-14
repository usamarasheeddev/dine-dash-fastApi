from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    companyId: int

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    name: str
    price: float = 0.00
    cost: float = 0.00
    stock_quantity: int = 0
    categoryId: Optional[int] = None
    image: Optional[str] = None
    isFavourite: bool = False
    companyId: int
    inventoryItemId: Optional[int] = None
    variations: List[Dict] = []
    addons: List[Dict] = []
    active: bool = True

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
