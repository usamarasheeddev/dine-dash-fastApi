from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.product import Product
from app.models.product_category import ProductCategory
from app.models.inventory_item import InventoryItem
from app.models.user import User
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductOut,
    ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryOut
)
from app.api.deps import get_current_user

router = APIRouter()

# --- Categories ---

@router.get("/categories", response_model=List[ProductCategoryOut])
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ProductCategory).where(ProductCategory.company_id == current_user.company_id))
    return result.scalars().all()

@router.post("/categories", response_model=ProductCategoryOut, status_code=status.HTTP_201_CREATED)
async def add_category(
    category_data: ProductCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_category = ProductCategory(
        name=category_data.name,
        image=category_data.image,
        company_id=current_user.company_id
    )
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category

@router.put("/categories/{id}", response_model=ProductCategoryOut)
async def update_category(
    id: int,
    category_data: ProductCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ProductCategory).where(ProductCategory.id == id, ProductCategory.company_id == current_user.company_id)
    )
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category_data.name is not None:
        category.name = category_data.name
    if category_data.image is not None:
        category.image = category_data.image
        
    await db.commit()
    await db.refresh(category)
    return category

@router.delete("/categories/{id}")
async def delete_category(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ProductCategory).where(ProductCategory.id == id, ProductCategory.company_id == current_user.company_id)
    )
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    await db.delete(category)
    await db.commit()
    return {"message": "Category deleted successfully"}

# --- Products ---

@router.get("/", response_model=List[ProductOut])
async def get_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Product)
        .where(Product.company_id == current_user.company_id)
        .options(selectinload(Product.category))
    )
    products = result.scalars().all()
    return products

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def add_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_product = Product(
        name=product_data.name,
        price=product_data.price,
        cost=product_data.cost,
        stock_quantity=product_data.stock_quantity,
        category_id=product_data.category_id,
        inventory_item_id=product_data.inventory_item_id,
        image=product_data.image,
        is_favourite=product_data.is_favourite,
        variations=product_data.variations,
        addons=product_data.addons,
        active=product_data.active,
        company_id=current_user.company_id
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    
    # Reload to include category for response
    result = await db.execute(
        select(Product).where(Product.id == new_product.id).options(selectinload(Product.category))
    )
    return result.scalars().first()

@router.put("/{id}", response_model=ProductOut)
async def update_product(
    id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Product).where(Product.id == id, Product.company_id == current_user.company_id)
        .options(selectinload(Product.category))
    )
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_dict = product_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(product, key, value)
        
    await db.commit()
    await db.refresh(product)
    return product

@router.delete("/{id}")
async def delete_product(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Product).where(Product.id == id, Product.company_id == current_user.company_id)
    )
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    await db.delete(product)
    await db.commit()
    return {"message": "Product deleted"}
