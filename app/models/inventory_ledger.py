from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class InventoryLedger(Base):
    __tablename__ = "inventory_ledgers"

    id = Column(Integer, primary_key=True, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(DECIMAL(10, 2))
    type = Column(String) # 'in' or 'out'
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    inventory_item = relationship("InventoryItem", back_populates="ledgers")
    user = relationship("User", back_populates="inventory_ledgers")
