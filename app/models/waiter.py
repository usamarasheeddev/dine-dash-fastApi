from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Waiter(Base):
    __tablename__ = "waiters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    cnic = Column(String, nullable=True)
    address = Column(String, nullable=True)
    status = Column(String, default="active")
    branch_id = Column(Integer, ForeignKey("branches.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    branch = relationship("Branch", back_populates="waiters")
    orders = relationship("Order", back_populates="waiter")
