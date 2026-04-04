import sys
sys.path.append('c:\\Users\\usama\\Desktop\\Projects\\dine-dash\\fastapi-backend')

from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional, Any
from datetime import datetime
from decimal import Decimal

class LinkedProductOut(BaseModel):
    id: int
    name: str
    price: Decimal

class InventoryItemOutTest(BaseModel):
    id: int
    name: str
    linked_product: Optional[LinkedProductOut] = Field(None, validation_alias="products", alias="linkedProduct")

    @field_validator("linked_product", mode="before")
    @classmethod
    def extract_first_product(cls, v: Any) -> Any:
        if isinstance(v, list):
            return v[0] if v else None
        return v

    class Config:
        from_attributes = True

class MockLinkedProduct:
    def __init__(self):
        self.id = 1
        self.name = "Mock Product"
        self.price = Decimal("10.00")

class MockInventoryItem:
    def __init__(self):
        self.id = 1
        self.name = "Mock Item"
        self.products = [MockLinkedProduct()]

item = MockInventoryItem()

print("Attempting to parse MockInventoryItem...")
try:
    parsed = InventoryItemOutTest.model_validate(item)
    print("Success:")
    print(parsed.model_dump())
except ValidationError as e:
    print("ValidationError:")
    print(e)
