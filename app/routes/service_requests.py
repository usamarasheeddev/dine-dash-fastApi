from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import secrets
import string
from app.core.database import get_db
from app.models.service_request import ServiceRequest
from app.models.company import Company
from app.models.user import User
from app.schemas.service_request import (
    ServiceRequestCreate, ServiceRequestUpdateStatus, ServiceRequestOut
)
from app.api.deps import get_current_user, RoleChecker
from app.core.security import get_password_hash
from datetime import datetime, timedelta

router = APIRouter()

# Public route
@router.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_request(
    request_data: ServiceRequestCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if exists
    result = await db.execute(select(ServiceRequest).where(ServiceRequest.email == request_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Request with this email already exists")
        
    new_request = ServiceRequest(
        company_name=request_data.company_name,
        email=request_data.email,
        password=request_data.password, # Note: Node.js stores plain text here, but we should probably hash? 
        # Actually Node.js seems to store it plain and then use it as a base.
        phone=request_data.phone,
        address=request_data.address,
        status="pending"
    )
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    return {"message": "Service request submitted successfully", "request": new_request}

# Super Admin Routes
@router.get("/", response_model=List[ServiceRequestOut])
async def get_all_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    check_role: None = Depends(RoleChecker(["superadmin"]))
):
    result = await db.execute(select(ServiceRequest).order_by(ServiceRequest.created_at.desc()))
    return result.scalars().all()

@router.put("/{id}/status")
async def update_request_status(
    id: int,
    status_data: ServiceRequestUpdateStatus,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    check_role: None = Depends(RoleChecker(["superadmin"]))
):
    result = await db.execute(select(ServiceRequest).where(ServiceRequest.id == id))
    request = result.scalars().first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if status_data.status == "approved" and request.status != "approved":
        # Transactional logic
        try:
            # 1. Create Company
            price_map = {'basic': 50, 'premium': 150, 'enterprise': 500}
            expiry = datetime.utcnow() + timedelta(days=30)
            
            new_company = Company(
                name=request.company_name,
                email=request.email,
                status="active",
                subscription_plan="basic",
                subscription_price=price_map['basic'],
                expiry_date=expiry
            )
            db.add(new_company)
            await db.flush() # Get ID
            
            # 2. Create User (Admin)
            generated_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
            new_user = User(
                username="Admin",
                email=request.email,
                password=get_password_hash(generated_password),
                role="admin",
                company_id=new_company.id
            )
            db.add(new_user)
            
            # 3. Update Request
            request.status = "approved"
            
            await db.commit()
            
            # 4. Send Email (Background Task)
            # await send_approval_email(request.email, request.company_name, generated_password)
            # For now, just logging or placeholder
            print(f"Approval Email for {request.email}: Pwd: {generated_password}")
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Error approving request: {str(e)}")
            
    elif status_data.status == "rejected":
        request.status = "rejected"
        await db.commit()
    else:
        raise HTTPException(status_code=400, detail="Invalid status transition")
        
    return {"message": f"Request {status_data.status} successfully"}
