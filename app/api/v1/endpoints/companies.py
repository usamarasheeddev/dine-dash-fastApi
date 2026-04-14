from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api import deps
from app.models.core import Company, User, ServiceRequest
from app.schemas.core import Company as CompanySchema, CompanyCreate
from app.core.security import get_password_hash

router = APIRouter()

@router.post("/create", response_model=CompanySchema)
async def create_company(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    company_in: dict # Simplified to handle the mixed payload from Node controller
) -> Any:
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Replicating companyController.createCompany logic
    # ... logic omitted for brevity in this scratch, but I will implement fully
    pass

@router.get("/all", response_model=List[CompanySchema])
async def get_all_companies(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(select(Company).order_by(Company.created_at.desc()))
    return result.scalars().all()

@router.get("/my-settings", response_model=CompanySchema)
async def get_my_settings(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    result = await db.execute(select(Company).where(Company.id == current_user.companyId))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/my-settings", response_model=CompanySchema)
async def update_my_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    company_in: dict
) -> Any:
    # Allow cashier as well since it's the default role for testing (matches Node controller line 171)
    if current_user.role not in ["admin", "superadmin", "cashier"]:
        raise HTTPException(status_code=403, detail="Not authorized to update company settings")
        
    result = await db.execute(select(Company).where(Company.id == current_user.companyId))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    allowed_fields = [
        'name', 'address', 'phone', 'phone2',
        'currency', 'timezone', 'taxRate',
        'receiptHeader', 'receiptFooter',
        'orderTypes', 'kitchenEnabled'
    ]
    
    for field in allowed_fields:
        if field in company_in:
            setattr(company, field, company_in[field])
            
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Replicating stats logic
    total_companies = await db.scalar(select(func.count(Company.id)))
    active_companies = await db.scalar(select(func.count(Company.id)).where(Company.status == 'active'))
    disabled_companies = await db.scalar(select(func.count(Company.id)).where(Company.status == 'disabled'))
    total_revenue = await db.scalar(select(func.sum(Company.subscriptionPrice))) or 0
    total_users = await db.scalar(select(func.count(User.id)).where(User.role != 'superadmin'))
    pending_requests = await db.scalar(select(func.count(ServiceRequest.id)).where(ServiceRequest.status == 'pending'))
    
    return {
        "totalCompanies": total_companies,
        "activeCompanies": active_companies,
        "disabledCompanies": disabled_companies,
        "totalRevenue": float(total_revenue),
        "totalUsers": total_users,
        "pendingRequests": pending_requests,
        "expiringSoon": 0 # Logic for date filter can be added
    }
