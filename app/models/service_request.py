from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    phone = Column(String)
    address = Column(Text)
    status = Column(String, default="pending") # pending, approved, rejected
    
    # Keeping the original fields if they were used for something else, 
    # but based on authController.js, these are the ones used for registration.
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)
    waiter_id = Column(Integer, ForeignKey("waiters.id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    request_type = Column(String, nullable=True) # for maintenance/service
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    table = relationship("Table")
    waiter = relationship("Waiter")
    branch = relationship("Branch")
