from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.company import Company
from app.models.user import User
from app.models.service_request import ServiceRequest
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut, DashboardStats
from app.api.deps import get_current_user, RoleChecker
from app.core.security import get_password_hash

router = APIRouter()

@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_company(
    reg_data: CompanyCreate,
    current_user: User = Depends(RoleChecker(["superadmin"])),
    db: AsyncSession = Depends(get_db)
):
    # Check if company already exists
    result = await db.execute(select(Company).where(Company.email == reg_data.companyEmail))
    existing_company = result.scalars().first()
    if existing_company:
        raise HTTPException(status_code=400, detail="Company with this email already exists")
    
    # Check if admin user already exists
    result = await db.execute(select(User).where(User.email == reg_data.adminEmail))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    price_map = {"basic": 50, "premium": 150, "enterprise": 500}
    expiry = datetime.utcnow() + timedelta(days=30)
    
    new_company = Company(
        name=reg_data.companyName,
        email=reg_data.companyEmail,
        status="active",
        subscription_plan=reg_data.subscriptionPlan,
        subscription_price=price_map.get(reg_data.subscriptionPlan, 50),
        expiry_date=expiry
    )
    db.add(new_company)
    await db.flush() # To get the company ID
    
    new_user = User(
        username=reg_data.adminName,
        email=reg_data.adminEmail,
        password=get_password_hash(reg_data.adminPassword),
        role="admin",
        company_id=new_company.id
    )
    db.add(new_user)
    await db.commit()
    
    return {
        "message": "Company and Admin created successfully",
        "company": new_company,
        "admin": {"id": new_user.id, "username": new_user.username, "email": new_user.email}
    }

@router.get("/all", response_model=List[CompanyOut])
async def get_all_companies(
    current_user: User = Depends(RoleChecker(["superadmin"])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Company).order_by(Company.created_at.desc()))
    return result.scalars().all()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(RoleChecker(["superadmin"])),
    db: AsyncSession = Depends(get_db)
):
    total_companies = await db.scalar(select(func.count(Company.id)))
    active_companies = await db.scalar(select(func.count(Company.id)).where(Company.status == "active"))
    disabled_companies = await db.scalar(select(func.count(Company.id)).where(Company.status == "disabled"))
    total_revenue = await db.scalar(select(func.sum(Company.subscription_price))) or 0
    
    seven_days_from_now = datetime.utcnow() + timedelta(days=7)
    expiring_soon = await db.scalar(
        select(func.count(Company.id)).where(
            Company.expiry_date <= seven_days_from_now,
            Company.expiry_date >= datetime.utcnow()
        )
    )
    
    pending_requests = await db.scalar(select(func.count(ServiceRequest.id)).where(ServiceRequest.status == "pending"))
    total_users = await db.scalar(select(func.count(User.id)).where(User.role != "superadmin"))
    
    return {
        "totalCompanies": total_companies,
        "activeCompanies": active_companies,
        "disabledCompanies": disabled_companies,
        "totalRevenue": float(total_revenue),
        "expiringSoon": expiring_soon,
        "pendingRequests": pending_requests,
        "totalUsers": total_users
    }

@router.get("/my-settings", response_model=CompanyOut)
async def get_my_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Company).where(Company.id == current_user.company_id))
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/my-settings")
async def update_my_settings(
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Logic: Only admin, superadmin, or cashier (for testing per Node.js controller) can update
    if current_user.role not in ["admin", "superadmin", "cashier"]:
        raise HTTPException(status_code=403, detail="Not authorized to update company settings")
        
    result = await db.execute(select(Company).where(Company.id == current_user.company_id))
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    allowed_fields = [
        "name", "address", "phone", "phone2",
        "currency", "timezone", "taxRate",
        "receiptHeader", "receiptFooter",
        "orderTypes", "kitchenEnabled"
    ]
    
    # Mapping JS camelCase to Python snake_case if needed, 
    # but the model has snake_case. Let's handle both or stick to what's in allowFields.
    # The Node.js code used: taxRate, receiptHeader, receiptFooter, orderTypes, kitchenEnabled
    field_map = {
        "taxRate": "tax_rate",
        "receiptHeader": "receipt_header",
        "receiptFooter": "receipt_footer",
        "orderTypes": "order_types",
        "kitchenEnabled": "kitchen_enabled"
    }

    for field in allowed_fields:
        if field in update_data:
            model_field = field_map.get(field, field)
            setattr(company, model_field, update_data[field])
            
    await db.commit()
    await db.refresh(company)
    return {"message": "Company settings updated successfully", "company": company}

@router.put("/{id}")
async def update_company(
    id: int,
    update_data: Dict[str, Any],
    current_user: User = Depends(RoleChecker(["superadmin"])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Company).where(Company.id == id))
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if "status" in update_data:
        company.status = update_data["status"]
        
    if "subscriptionPlan" in update_data:
        price_map = {"basic": 50, "premium": 150, "enterprise": 500}
        plan = update_data["subscriptionPlan"]
        company.subscription_plan = plan
        company.subscription_price = price_map.get(plan, 50)
        company.expiry_date = datetime.utcnow() + timedelta(days=30)
        
    await db.commit()
    await db.refresh(company)
    return {"message": "Company updated successfully", "company": company}
