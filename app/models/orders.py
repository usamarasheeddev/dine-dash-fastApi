from sqlalchemy import String, Boolean, Integer, ForeignKey, JSON, DECIMAL, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
from .base import Base, TimestampMixin

class Order(Base, TimestampMixin):
    __tablename__ = "Orders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    orderType: Mapped[str] = mapped_column(String) # dine-in, takeaway, delivery
    subTotal: Mapped[float] = mapped_column(DECIMAL(12, 2))
    discount: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.00)
    tax: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.00)
    finalTotal: Mapped[float] = mapped_column(DECIMAL(12, 2))
    status: Mapped[str] = mapped_column(String, default="pending") # new, preparing, pending, completed, cancelled
    paymentMethod: Mapped[str] = mapped_column(String, default="pending") # cash, card, credit, paid
    waiterId: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("Waiters.id"))
    tableId: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("Tables.id"))
    customerId: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("Customers.id"))
    branchId: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("Branches.id"))
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))
    isUploaded: Mapped[bool] = mapped_column(Boolean, default=False)
    editHistory: Mapped[list] = mapped_column(JSON, default=[])

    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base, TimestampMixin):
    __tablename__ = "OrderItems"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    orderId: Mapped[int] = mapped_column(Integer, ForeignKey("Orders.id"))
    productId: Mapped[int] = mapped_column(Integer, ForeignKey("Products.id"))
    quantity: Mapped[float] = mapped_column(DECIMAL(10, 2))
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))
    total: Mapped[float] = mapped_column(DECIMAL(12, 2))
    variations: Mapped[Optional[list]] = mapped_column(JSON)
    addons: Mapped[Optional[list]] = mapped_column(JSON)
 
    order = relationship("Order", back_populates="items")
