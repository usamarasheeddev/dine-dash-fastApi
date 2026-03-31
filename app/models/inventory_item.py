from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    sku = Column(String, nullable=True)
    unit = Column(String)
    current_stock = Column(DECIMAL(10, 2), default=0.00)
    min_stock = Column(DECIMAL(10, 2), default=0.00)
    cost_price = Column(DECIMAL(10, 2), default=0.00)
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="inventory_items")
    products = relationship("Product", back_populates="linked_inventory")
    ledgers = relationship("InventoryLedger", back_populates="inventory_item")
