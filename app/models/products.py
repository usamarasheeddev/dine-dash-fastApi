from sqlalchemy import String, Boolean, Integer, ForeignKey, JSON, DECIMAL, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from .base import Base, TimestampMixin

class ProductCategory(Base, TimestampMixin):
    __tablename__ = "ProductCategories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))
    
    products = relationship("Product", back_populates="category")

class Product(Base, TimestampMixin):
    __tablename__ = "Products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    cost: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    categoryId: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ProductCategories.id"))
    image: Mapped[Optional[str]] = mapped_column(String)
    isFavourite: Mapped[bool] = mapped_column(Boolean, default=False)
    companyId: Mapped[int] = mapped_column(Integer, ForeignKey("Companies.id"))
    inventoryItemId: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("InventoryItems.id"))
    variations: Mapped[list] = mapped_column(JSON, default=[])
    addons: Mapped[list] = mapped_column(JSON, default=[])
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    category = relationship("ProductCategory", back_populates="products")
