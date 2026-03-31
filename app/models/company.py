from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    status = Column(String, default="active")
    subscription_plan = Column(String, default="basic")
    expiry_date = Column(DateTime, nullable=True)
    subscription_price = Column(DECIMAL(10, 2), default=0.00)
    address = Column(String)
    phone = Column(String)
    phone2 = Column(String)
    currency = Column(String, default="USD")
    timezone = Column(String, default="America/New_York")
    tax_rate = Column(DECIMAL(5, 2), default=10.00)
    receipt_header = Column(Text)
    receipt_footer = Column(Text)
    order_types = Column(JSON, default={"dineIn": True, "takeaway": True, "delivery": True})
    kitchen_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="company")
    branches = relationship("Branch", back_populates="company")
    products = relationship("Product", back_populates="company")
    inventory_items = relationship("InventoryItem", back_populates="company")
