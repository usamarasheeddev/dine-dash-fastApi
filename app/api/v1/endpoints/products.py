from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api import deps
from app.models.products import Product, ProductCategory
from app.models.inventory import InventoryItem
from app.models.core import User
from app.schemas.products import Product as ProductSchema, ProductCreate, Category as CategorySchema, CategoryCreate

router = APIRouter()

# --- Categories ---
@router.get("/categories", response_model=List[CategorySchema])
async def get_categories(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(select(ProductCategory).where(ProductCategory.companyId == current_user.companyId))
    return result.scalars().all()

@router.post("/categories", response_model=CategorySchema)
async def create_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    category_in: CategoryCreate
) -> Any:
    new_category = ProductCategory(
        name=category_in.name,
        companyId=current_user.companyId
    )
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category

@router.put("/categories/{id}", response_model=CategorySchema)
async def update_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    category_in: dict
) -> Any:
    result = await db.execute(select(ProductCategory).where(ProductCategory.id == id, ProductCategory.companyId == current_user.companyId))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    for field, value in category_in.items():
        if hasattr(category, field):
            setattr(category, field, value)
            
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

@router.delete("/categories/{id}")
async def delete_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int
) -> Any:
    result = await db.execute(select(ProductCategory).where(ProductCategory.id == id, ProductCategory.companyId == current_user.companyId))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    await db.delete(category)
    await db.commit()
    return {"message": "Category deleted successfully"}

# --- Products ---
@router.get("/", response_model=List[ProductSchema])
async def get_products(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # Matching include logic from Node: category and linkedInventory
    query = select(Product).where(Product.companyId == current_user.companyId).options(
        joinedload(Product.category)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=ProductSchema)
async def create_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    product_in: ProductCreate
) -> Any:
    new_product = Product(
        name=product_in.name,
        price=product_in.price,
        cost=product_in.cost,
        stock_quantity=product_in.stock_quantity,
        categoryId=product_in.categoryId,
        inventoryItemId=product_in.inventoryItemId,
        image=product_in.image,
        isFavourite=product_in.isFavourite,
        variations=product_in.variations,
        addons=product_in.addons,
        active=product_in.active,
        companyId=current_user.companyId
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@router.put("/{id}", response_model=ProductSchema)
async def update_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int,
    product_in: dict
) -> Any:
    result = await db.execute(select(Product).where(Product.id == id, Product.companyId == current_user.companyId))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    for field, value in product_in.items():
        if hasattr(product, field):
            setattr(product, field, value)
            
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

@router.delete("/{id}")
async def delete_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: int
) -> Any:
    result = await db.execute(select(Product).where(Product.id == id, Product.companyId == current_user.companyId))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    await db.delete(product)
    await db.commit()
    return {"message": "Product deleted"}
