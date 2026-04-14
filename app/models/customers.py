from sqlalchemy import String, Boolean, Integer, ForeignKey, JSON, DECIMAL, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
from .base import Base, TimestampMixin

class Customer(Base, TimestampMixin):
    __tablename__ = "Customers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)
    address: Mapped[Optional[str]] = mapped_column(Text)
    initial_balance: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.00)
    current_balance: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0.00)
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))

    ledger_entries = relationship("CustomerLedger", back_populates="customer")

class CustomerLedger(Base, TimestampMixin):
    __tablename__ = "CustomerLedgers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customerId: Mapped[int] = mapped_column(Integer, ForeignKey("Customers.id"))
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    type: Mapped[str] = mapped_column(String) # debit, credit, payment
    amount: Mapped[float] = mapped_column(DECIMAL(12, 2))
    note: Mapped[Optional[str]] = mapped_column(Text)

    customer = relationship("Customer", back_populates="ledger_entries")
    
class Voucher(Base, TimestampMixin):
    __tablename__ = "Vouchers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    voucherNo: Mapped[str] = mapped_column(String)
    customerId: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("Customers.id"))
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))
    type: Mapped[str] = mapped_column(String) # receipt, payment
    amount: Mapped[float] = mapped_column(DECIMAL(12, 2))
    paymentMethod: Mapped[str] = mapped_column(String)
    note: Mapped[Optional[str]] = mapped_column(Text)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
