from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Boolean, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(DECIMAL(10, 2), default=0.00)
    cost = Column(DECIMAL(10, 2), default=0.00)
    stock_quantity = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    image = Column(String, nullable=True)
    is_favourite = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey("companies.id"))
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    variations = Column(JSONB, default=[])
    addons = Column(JSONB, default=[])
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="products")
    category = relationship("ProductCategory", back_populates="products")
    linked_inventory = relationship("InventoryItem", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
