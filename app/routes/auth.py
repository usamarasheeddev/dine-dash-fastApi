from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta, datetime
import hashlib
import secrets
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models.user import User
from app.models.company import Company
from app.models.service_request import ServiceRequest
from app.schemas.auth import (
    LoginRequest, Token, RegisterRequest, UserUpdate, 
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.api.deps import get_current_user
from app.utils.email import sendEmail

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalars().first()
    
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"id": user.id, "role": user.role, "companyId": user.company_id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_details": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "user_role": user.role,
            "companyId": user.company_id
        }
    }

@router.post("/register")
async def register(reg_data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if request already exists
    result = await db.execute(select(ServiceRequest).where(ServiceRequest.email == reg_data.req_email))
    existing_request = result.scalars().first()
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration request with this email already exists"
        )
    
    new_request = ServiceRequest(
        company_name=reg_data.req_company_name,
        email=reg_data.req_email,
        password=get_password_hash("password123"),
        phone=reg_data.req_number,
        address=reg_data.req_address
    )
    db.add(new_request)
    await db.commit()
    
    return {"success": True, "message": "Registration submitted successfully. Please wait for admin approval."}

@router.get("/getUser")
async def get_user(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": {
            "user_details": {
                "id": current_user.id,
                "username": current_user.username,
                "fullName": current_user.full_name or '',
                "phone": current_user.phone or '',
                "email": current_user.email,
                "user_role": current_user.role,
                "companyId": current_user.company_id
            }
        }
    }

@router.put("/update")
async def update_profile(
    update_data: UserUpdate, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if update_data.new_password:
        if not update_data.current_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password required")
        if not verify_password(update_data.current_password, current_user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")
        current_user.password = get_password_hash(update_data.new_password)
    
    if update_data.username:
        current_user.username = update_data.username
    if update_data.full_name:
        current_user.full_name = update_data.full_name
    if update_data.phone:
        current_user.phone = update_data.phone
    if update_data.email:
        current_user.email = update_data.email
        
    await db.commit()
    return {
        "message": "Profile updated successfully", 
        "user": {
            "id": current_user.id, 
            "username": current_user.username, 
            "fullName": current_user.full_name, 
            "phone": current_user.phone, 
            "email": current_user.email
        }
    }

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no user with that email address.")
    
    reset_token = secrets.token_hex(32)
    hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()
    
    user.reset_password_token = hashed_token
    user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)
    await db.commit()
    
    origin = request.headers.get("origin", "http://localhost:5173")
    reset_url = f"{origin}/reset-password/{reset_token}"
    
    message = f"You are receiving this email because you (or someone else) have requested the reset of a password. Please make a PUT request to: \n\n {reset_url}"
    html = f"<p>You requested a password reset</p><p>Click this <a href='{reset_url}'>link</a> to set a new password.</p><p>This link is valid for 1 hour.</p>"
    
    try:
        await sendEmail({"email": user.email, "subject": "Password Reset Token", "message": message, "html": html})
        return {"success": True, "message": "Email sent"}
    except Exception:
        user.reset_password_token = None
        user.reset_password_expires = None
        await db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email could not be sent")

@router.put("/reset-password/{token}")
async def reset_password(token: str, data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    
    result = await db.execute(
        select(User).where(
            User.reset_password_token == hashed_token,
            User.reset_password_expires > datetime.utcnow()
        )
    )
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is invalid or has expired")
    
    user.password = get_password_hash(data.password)
    user.reset_password_token = None
    user.reset_password_expires = None
    await db.commit()
    
    return {"success": True, "message": "Password reset successfully"}
