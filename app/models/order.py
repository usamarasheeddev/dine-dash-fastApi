from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_type = Column(String)
    sub_total = Column(DECIMAL(10, 2))
    discount = Column(DECIMAL(10, 2), default=0.00)
    tax = Column(DECIMAL(10, 2), default=0.00)
    final_total = Column(DECIMAL(10, 2))
    status = Column(String, default="pending")
    payment_method = Column(String, nullable=True)
    waiter_id = Column(Integer, ForeignKey("waiters.id"), nullable=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    is_uploaded = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company")
    branch = relationship("Branch", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    waiter = relationship("Waiter", back_populates="orders")
    table = relationship("Table", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
