from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, AuditLog
from app.core import security
from app.core.config import settings
from app.schemas.schemas import Token, UserResponse
from app.api import deps

router = APIRouter()

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

@router.post("/login", response_model=Token)
def login_access_token(
    request: Request,
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Audit setup
    ip_address = request.client.host if request.client else "unknown"
    
    if not user:
        # We can't log the user_id since user doesn't exist, but we can log the attempt
        audit = AuditLog(
            action="LOGIN_FAILED",
            resource=f"AttemptedEmail:{form_data.username}",
            status="FAILURE",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    # Check lockout
    if user.locked_until and user.locked_until > datetime.utcnow():
        audit = AuditLog(
            user_id=user.id,
            role=user.role.value if user.role else "UNKNOWN",
            action="LOGIN_BLOCKED",
            resource="UserAccount",
            status="LOCKED",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        raise HTTPException(status_code=429, detail="Account is temporarily locked due to too many failed attempts")
    
    if not security.verify_password(form_data.password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            
        audit = AuditLog(
            user_id=user.id,
            role=user.role.value if user.role else "UNKNOWN",
            action="LOGIN_FAILED",
            resource="UserAccount",
            status="FAILURE",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    if not user.is_active:
        audit = AuditLog(
            user_id=user.id,
            role=user.role.value if user.role else "UNKNOWN",
            action="LOGIN_FAILED",
            resource="UserAccount",
            status="INACTIVE",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # Reset failed attempts on success
    user.failed_login_attempts = 0
    user.locked_until = None
    
    audit = AuditLog(
        user_id=user.id,
        role=user.role.value if user.role else "UNKNOWN",
        action="LOGIN_SUCCESS",
        resource="UserAccount",
        status="SUCCESS",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            {"sub": user.email}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return current_user

@router.post("/change-password")
def change_password(
    request: Request,
    current_password: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    ip_address = request.client.host if request.client else "unknown"
    
    if not security.verify_password(current_password, current_user.hashed_password):
        audit = AuditLog(
            user_id=current_user.id,
            role=current_user.role.value if current_user.role else "UNKNOWN",
            action="PASSWORD_CHANGE_FAILED",
            resource="UserAccount",
            status="FAILURE",
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        raise HTTPException(status_code=400, detail="Incorrect current password")
        
    current_user.hashed_password = security.get_password_hash(new_password)
    
    audit = AuditLog(
        user_id=current_user.id,
        role=current_user.role.value if current_user.role else "UNKNOWN",
        action="PASSWORD_CHANGED",
        resource="UserAccount",
        status="SUCCESS",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Password changed successfully"}
