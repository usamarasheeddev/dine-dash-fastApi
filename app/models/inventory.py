from sqlalchemy import String, Boolean, Integer, ForeignKey, JSON, DECIMAL, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
from .base import Base, TimestampMixin

class InventoryItem(Base, TimestampMixin):
    __tablename__ = "InventoryItems"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))
    productId: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("Products.id"))
    name: Mapped[str] = mapped_column(String)
    category: Mapped[Optional[str]] = mapped_column(String)
    unit: Mapped[str] = mapped_column(String)
    quantity: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    minStock: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    costPerUnit: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    supplier: Mapped[Optional[str]] = mapped_column(String)

    ledger = relationship("InventoryLedger", back_populates="inventoryItem")

class InventoryLedger(Base, TimestampMixin):
    __tablename__ = "InventoryLedgers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    inventoryItemId: Mapped[int] = mapped_column(Integer, ForeignKey("InventoryItems.id"))
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))
    userId: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id"))
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    type: Mapped[str] = mapped_column(String) # deduction, addition, adjustment
    quantityChange: Mapped[float] = mapped_column(DECIMAL(10, 2))
    previousStock: Mapped[float] = mapped_column(DECIMAL(10, 2))
    newStock: Mapped[float] = mapped_column(DECIMAL(10, 2))
    note: Mapped[Optional[str]] = mapped_column(Text)

    inventoryItem = relationship("InventoryItem", back_populates="ledger")
