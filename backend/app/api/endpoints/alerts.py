from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid

from app.db.database import get_db
from app.db.models import FraudAlert, InvestigationCase, CaseStatus, AuditLog, Transaction, FraudPrediction, Customer, RiskLevel, PredictionResult, ShapExplanation
from app.schemas.schemas import FraudAlertResponse, FraudAlertDetailResponse, PaginatedFraudAlertResponse, PredictionResponse, FraudExplanation as SchemaFraudExplanation
from app.api.deps import get_current_user, get_current_active_user, get_current_active_admin

router = APIRouter()

@router.get("/", response_model=PaginatedFraudAlertResponse)
def get_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(FraudAlert)
    
    if status:
        query = query.filter(FraudAlert.status == status)
    
    if risk_level:
        query = query.filter(FraudAlert.risk_level == risk_level)
        
    if start_date:
        query = query.filter(FraudAlert.created_at >= start_date)
        
    if end_date:
        query = query.filter(FraudAlert.created_at <= end_date)
        
    if search:
        query = query.join(Transaction).join(Customer).filter(
            (FraudAlert.alert_id.ilike(f"%{search}%")) |
            (Transaction.transaction_id.ilike(f"%{search}%")) |
            (Customer.name.ilike(f"%{search}%"))
        )

    total = query.count()
    items = query.order_by(FraudAlert.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedFraudAlertResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )

@router.get("/{alert_id}", response_model=FraudAlertDetailResponse)
def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    alert = db.query(FraudAlert).filter(FraudAlert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    response_data = FraudAlertDetailResponse.model_validate(alert)
    response_data.transaction = alert.transaction
    
    # Get prediction
    prediction = db.query(FraudPrediction).filter(FraudPrediction.transaction_id == alert.transaction_id).first()
    if prediction:
        explanations = [
            SchemaFraudExplanation(
                feature_name=e.feature_name,
                feature_value=e.feature_value,
                shap_value=e.shap_value
            ) for e in prediction.explanations
        ]
        response_data.prediction = PredictionResponse(
            prediction=prediction.prediction.value,
            risk_score=prediction.risk_score,
            risk_level=prediction.risk_level.value,
            explanations=explanations
        )
        
    return response_data

@router.patch("/{alert_id}/status", response_model=FraudAlertResponse)
def update_alert_status(
    alert_id: str,
    status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    alert = db.query(FraudAlert).filter(FraudAlert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.status = status
    db.commit()
    db.refresh(alert)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        role=current_user.role.value if current_user.role else "UNKNOWN",
        action="ALERT_STATUS_UPDATED",
        resource=f"FraudAlert:{alert.alert_id}",
        status="SUCCESS",
        ip_address="system"
    )
    db.add(audit)
    db.commit()
    
    return alert

@router.patch("/{alert_id}/review", response_model=FraudAlertResponse)
def review_alert(
    alert_id: str,
    note: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    alert = db.query(FraudAlert).filter(FraudAlert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    # Append review note to reason or handle appropriately
    if alert.reason:
        alert.reason += f"\n[Review by {current_user.full_name}]: {note}"
    else:
        alert.reason = f"[Review by {current_user.full_name}]: {note}"
        
    db.commit()
    db.refresh(alert)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        role=current_user.role.value if current_user.role else "UNKNOWN",
        action="ALERT_REVIEWED",
        resource=f"FraudAlert:{alert.alert_id}",
        status="SUCCESS",
        ip_address="system"
    )
    db.add(audit)
    db.commit()
    
    return alert

@router.post("/{alert_id}/investigate")
def investigate_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    alert = db.query(FraudAlert).filter(FraudAlert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    # Check if a case already exists
    existing_case = db.query(InvestigationCase).filter(InvestigationCase.transaction_id == alert.transaction_id).first()
    if existing_case:
        raise HTTPException(status_code=400, detail="An investigation case already exists for this transaction")
        
    # Create Investigation Case
    case_id = f"CAS-{uuid.uuid4().hex[:8].upper()}"
    new_case = InvestigationCase(
        case_id=case_id,
        transaction_id=alert.transaction_id,
        customer_id=alert.customer_id,
        priority=alert.risk_level,
        status=CaseStatus.NEW
    )
    db.add(new_case)
    
    # Update alert status
    alert.status = "UNDER_INVESTIGATION"
    
    db.commit()
    db.refresh(new_case)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        role=current_user.role.value if current_user.role else "UNKNOWN",
        action="INVESTIGATION_CREATED",
        resource=f"InvestigationCase:{new_case.case_id}",
        status="SUCCESS",
        ip_address="system"
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Investigation case created", "case_id": new_case.case_id}
