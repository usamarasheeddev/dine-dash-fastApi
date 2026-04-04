import sys
sys.path.append('c:\\Users\\usama\\Desktop\\Projects\\dine-dash\\fastapi-backend')

from app.schemas.inventory import InventoryItemOut
from pydantic import ValidationError
from decimal import Decimal
from datetime import datetime

# Mimic the database object structure that SQLAlchemy returns
class MockLinkedProduct:
    def __init__(self):
        self.id = 1
        self.name = "Mock Product"
        self.price = Decimal("10.00")

class MockInventoryItem:
    def __init__(self):
        self.id = 1
        self.name = "Mock Item"
        self.category = "mock cat"
        self.unit = "piece"
        self.current_stock = Decimal("5.00")
        self.min_stock = Decimal("2.00")
        self.cost_price = Decimal("3.00")
        self.supplier = "mock supplier"
        self.product_id = 1
        self.company_id = 1
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # SQLAlchemy one-to-many relationship returns a list!
        self.products = [MockLinkedProduct()]

item = MockInventoryItem()

print("Attempting to parse MockInventoryItem with InventoryItemOut...")
try:
    parsed = InventoryItemOut.model_validate(item)
    print("Success:")
    print(parsed.model_dump())
except ValidationError as e:
    print("ValidationError:")
    print(e)
