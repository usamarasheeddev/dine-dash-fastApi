from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.core import User, ServiceRequest
from app.schemas.core import Token, LoginRequest, UserUpdate
from app.schemas.business import ServiceRequestCreate

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(deps.get_db),
    login_data: LoginRequest = None
) -> Any:
    """
    OAuth2 compatible token login, retrieve a JWT token for future requests
    """
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not security.verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )

    # Check User Status
    if user.status == "inactive":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact your administrator."
        )

    # Check Company Status (Exempt superadmins)
    if user.role != 'superadmin' and user.companyId:
        from app.models.core import Company
        from datetime import datetime, timezone
        res = await db.execute(select(Company).where(Company.id == user.companyId))
        company = res.scalar_one_or_none()
        
        if not company or company.status != 'active':
            status_label = company.status if company else 'inactive'
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Login blocked: Your company account is {status_label}. Please contact support."
            )
            
        if company.expiryDate and datetime.now(timezone.utc).replace(tzinfo=None) > company.expiryDate:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Login blocked: Your subscription has expired. Please renew to continue."
            )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_details": {
            "id": user.id,
            "username": user.name,
            "email": user.email,
            "user_role": user.role,
            "companyId": user.companyId
        }
    }

@router.post("/register")
async def register(
    db: AsyncSession = Depends(deps.get_db),
    *,
    req_company_name: str,
    req_email: str,
    req_number: str = None,
    req_address: str = None
) -> Any:
    """
    Create a new service request for registration
    """
    # Equivalent to Node.js authController.register
    result = await db.execute(select(ServiceRequest).where(ServiceRequest.email == req_email))
    existing_request = result.scalar_one_or_none()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration request with this email already exists"
        )
    
    # Defaults password to 'password123' as per Node controller line 67
    new_request = ServiceRequest(
        companyName=req_company_name,
        email=req_email,
        password=security.get_password_hash("password123"),
        phone=req_number,
        address=req_address
    )
    db.add(new_request)
    await db.commit()
    
    return {"success": True, "message": "Registration submitted successfully. Please wait for admin approval."}

@router.put("/update-profile")
async def update_profile(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    username: Optional[str] = None,
    email: Optional[str] = None,
    currentPassword: Optional[str] = None,
    newPassword: Optional[str] = None,
    fullName: Optional[str] = None,
    phone: Optional[str] = None
) -> Any:
    """
    Update current user profile
    """
    if newPassword:
        if not currentPassword:
            raise HTTPException(status_code=400, detail="Current password required")
        if not security.verify_password(currentPassword, current_user.password):
            raise HTTPException(status_code=400, detail="Incorrect current password")
        current_user.password = security.get_password_hash(newPassword)
        
    if username:
        current_user.name = username
    if fullName:
        current_user.name = fullName # Mapping name to fullName
    if email:
        result = await db.execute(select(User).where(User.email == email, User.id != current_user.id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = email
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "username": current_user.name,
            "email": current_user.email,
            "user_role": current_user.role,
            "companyId": current_user.companyId
        }
    }

@router.get("/me")
async def get_me(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get current user details
    """
    return {
        "success": True,
        "data": {
            "user_details": {
                "id": current_user.id,
                "username": current_user.name,
                "fullName": current_user.name, # Node uses fullName
                "phone": "", # Add phone to User model if needed
                "email": current_user.email,
                "user_role": current_user.role,
                "companyId": current_user.companyId
            }
        }
    }
