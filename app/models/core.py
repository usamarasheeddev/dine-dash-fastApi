from sqlalchemy import String, Boolean, Integer, ForeignKey, JSON, DECIMAL, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
from .base import Base, TimestampMixin

class Company(Base, TimestampMixin):
    __tablename__ = "Companies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="active")
    subscriptionPlan: Mapped[str] = mapped_column(String, default="basic")
    expiryDate: Mapped[Optional[datetime]] = mapped_column(DateTime)
    subscriptionPrice: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    address: Mapped[Optional[str]] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)
    phone2: Mapped[Optional[str]] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String, default="USD")
    timezone: Mapped[str] = mapped_column(String, default="America/New_York")
    taxRate: Mapped[float] = mapped_column(DECIMAL(5, 2), default=10.00)
    receiptHeader: Mapped[Optional[str]] = mapped_column(Text)
    receiptFooter: Mapped[Optional[str]] = mapped_column(Text)
    orderTypes: Mapped[dict] = mapped_column(JSON, default={"dineIn": True, "takeaway": True, "delivery": True})
    kitchenEnabled: Mapped[bool] = mapped_column(Boolean, default=False)

    users = relationship("User", back_populates="company")
    branches = relationship("Branch", back_populates="company")

class Branch(Base, TimestampMixin):
    __tablename__ = "Branches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    address: Mapped[Optional[str]] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String)
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))
    
    company = relationship("Company", back_populates="branches")

class User(Base, TimestampMixin):
    __tablename__ = "Users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="user")
    branchId: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("Branches.id"))
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))
    resetPasswordToken: Mapped[Optional[str]] = mapped_column(String)
    resetPasswordExpires: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String, default="active")
    
    company = relationship("Company", back_populates="users")

class Waiter(Base, TimestampMixin):
    __tablename__ = "Waiters"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))

class Table(Base, TimestampMixin):
    __tablename__ = "Tables"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tableNo: Mapped[str] = mapped_column(String)
    capacity: Mapped[int] = mapped_column(Integer, default=2)
    status: Mapped[str] = mapped_column(String, default="available") # available, occupied, reserved
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))

class ServiceRequest(Base, TimestampMixin):
    __tablename__ = "ServiceRequests"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    companyName: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)
    address: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="pending") # pending, approved, rejected

