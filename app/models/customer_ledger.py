from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class CustomerLedger(Base):
    __tablename__ = "customer_ledgers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    type = Column(String) # 'credit', 'debit', 'payment'
    amount = Column(DECIMAL(10, 2), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="ledgers")
    company = relationship("Company")
    order = relationship("Order")
