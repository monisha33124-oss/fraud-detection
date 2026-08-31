from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.db.models import AuditLog
from app.api.deps import get_current_active_admin
from app.schemas.schemas import PaginatedAuditLogResponse

router = APIRouter()

@router.get("/", response_model=PaginatedAuditLogResponse)
def get_audit_logs(
    page: int = Query(1, ge=1), 
    page_size: int = Query(50, ge=1, le=100),
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_active_admin)
):
    """Retrieve audit logs (admin access only)."""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if role:
        query = query.filter(AuditLog.role == role)
        
    total = query.count()
    
    skip = (page - 1) * page_size
    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(page_size).all()
    
    items = []
    for log in logs:
        items.append({
            "id": log.id,
            "user_id": log.user_id,
            "role": log.role,
            "action": log.action,
            "resource": log.resource,
            "status": log.status,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp
        })
        
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }
