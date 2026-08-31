from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid

from app.db.database import get_db
from app.db.models import Transaction, Customer, FraudPrediction, ShapExplanation, FraudAlert, AuditLog, RiskLevel, PredictionResult
from app.schemas.schemas import TransactionCreate, TransactionUpdate, TransactionResponse, TransactionDetailResponse, PaginatedTransactionResponse, PredictionResponse, FraudExplanation
from app.api.deps import get_current_user, get_current_active_user
from app.services.ml_service import MLService

router = APIRouter()

@router.get("/", response_model=PaginatedTransactionResponse)
def get_transactions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    customer_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    fraud_status: Optional[str] = None,
    payment_method: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(Transaction)
    
    if customer_id:
        query = query.filter(Transaction.customer_id == customer_id)
    if payment_method:
        query = query.filter(Transaction.payment_method == payment_method)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if start_date:
        query = query.filter(Transaction.date_time >= start_date)
    if end_date:
        query = query.filter(Transaction.date_time <= end_date)
        
    if search:
        query = query.join(Customer).filter(
            (Transaction.transaction_id.ilike(f"%{search}%")) |
            (Customer.name.ilike(f"%{search}%"))
        )
        
    if risk_level or fraud_status:
        query = query.join(FraudPrediction)
        if risk_level:
            query = query.filter(FraudPrediction.risk_level == risk_level)
        if fraud_status:
            query = query.filter(FraudPrediction.prediction == fraud_status)

    total = query.count()
    items = query.order_by(Transaction.date_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedTransactionResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )

@router.get("/{transaction_id}", response_model=TransactionDetailResponse)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    customer = transaction.customer
    prediction = transaction.prediction
    
    tx_dict = {
        "id": transaction.id,
        "transaction_id": transaction.transaction_id,
        "customer_id": transaction.customer_id,
        "account_id": transaction.account_id,
        "amount": transaction.amount,
        "location": transaction.location,
        "merchant": transaction.merchant,
        "payment_method": transaction.payment_method,
        "transaction_type": transaction.transaction_type,
        "device_info": transaction.device_info,
        "ip_address": transaction.ip_address,
        "date_time": transaction.date_time,
        "created_at": transaction.created_at,
        "updated_at": transaction.updated_at,
    }
    
    response_data = TransactionDetailResponse(**tx_dict)
    if customer:
        response_data.customer_name = customer.name
        
    if prediction:
        explanations = [
            FraudExplanation(
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
        
    alert = db.query(FraudAlert).filter(FraudAlert.transaction_id == transaction.id).first()
    response_data.has_alert = alert is not None
    
    from app.db.models import InvestigationCase
    investigation = db.query(InvestigationCase).filter(InvestigationCase.transaction_id == transaction.id).first()
    if investigation:
        response_data.investigation_status = investigation.status.value
        
    return response_data

@router.patch("/{transaction_id}", response_model=TransactionDetailResponse)
def update_transaction(
    transaction_id: str,
    transaction_in: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    update_data = transaction_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
        
    db.commit()
    db.refresh(transaction)
    
    audit = AuditLog(
        user_id=current_user.id,
        role=current_user.role.value if current_user.role else "UNKNOWN",
        action="TRANSACTION_UPDATED",
        resource=f"Transaction:{transaction.id}",
        status="SUCCESS",
        ip_address="system"
    )
    db.add(audit)
    db.commit()
    
    return get_transaction(transaction_id, db, current_user)

@router.post("/", response_model=TransactionDetailResponse)
def create_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    customer = db.query(Customer).filter(Customer.id == transaction_in.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    new_tx_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow()
    
    transaction = Transaction(
        transaction_id=new_tx_id,
        customer_id=transaction_in.customer_id,
        account_id=transaction_in.account_id,
        amount=transaction_in.amount,
        date_time=now,
        location=transaction_in.location,
        merchant=transaction_in.merchant,
        payment_method=transaction_in.payment_method,
        transaction_type=transaction_in.transaction_type,
        device_info=transaction_in.device_info,
        ip_address=transaction_in.ip_address
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    audit_tx = AuditLog(
        user_id=current_user.id,
        role=current_user.role.value if current_user.role else "UNKNOWN",
        action="TRANSACTION_CREATED",
        resource=f"Transaction:{transaction.id}",
        status="SUCCESS",
        ip_address="system"
    )
    db.add(audit_tx)
    
    ml_input = {
        "customer_id": str(transaction.customer_id),
        "amount": transaction.amount,
        "date_time": str(transaction.date_time),
        "location": transaction.location,
        "merchant": transaction.merchant,
        "payment_method": transaction.payment_method,
        "transaction_type": transaction.transaction_type,
        "device_info": transaction.device_info,
        "ip_address": transaction.ip_address
    }
    
    try:
        ml_result = MLService.evaluate_transaction(ml_input)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"ML Service Error: {str(e)}")
        
    prediction = FraudPrediction(
        transaction_id=transaction.id,
        prediction=PredictionResult.FRAUDULENT if ml_result["prediction"] == "FRAUDULENT" else PredictionResult.LEGITIMATE,
        risk_score=ml_result["risk_score"],
        risk_level=RiskLevel(ml_result["risk_level"])
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    for expl in ml_result["explanations"]:
        shap_record = ShapExplanation(
            prediction_id=prediction.id,
            feature_name=expl["feature_name"],
            feature_value=expl["feature_value"],
            shap_value=expl["shap_value"]
        )
        db.add(shap_record)
        
    audit_pred = AuditLog(
        user_id=current_user.id,
        role=current_user.role.value if current_user.role else "UNKNOWN",
        action="PREDICTION_RUN",
        resource=f"FraudPrediction:{prediction.id}",
        status="SUCCESS",
        ip_address="system"
    )
    db.add(audit_pred)
    
    alert = None
    if prediction.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        # Prevent duplicate alerts for the same transaction
        existing_alert = db.query(FraudAlert).filter(FraudAlert.transaction_id == transaction.id).first()
        if not existing_alert:
            alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
            alert = FraudAlert(
                alert_id=alert_id,
                transaction_id=transaction.id,
                customer_id=transaction.customer_id,
                risk_score=prediction.risk_score,
                risk_level=prediction.risk_level,
                reason=ml_result.get("summary", f"High risk score detected: {prediction.risk_score}"),
                status="OPEN"
            )
            db.add(alert)
            
            audit_alert = AuditLog(
                user_id=current_user.id,
                role=current_user.role.value if current_user.role else "UNKNOWN",
                action="ALERT_CREATED",
                resource=f"FraudAlert:{alert_id}",
                status="SUCCESS",
                ip_address="system"
            )
            db.add(audit_alert)
        else:
            alert = existing_alert
            
    db.commit()
    
    return get_transaction(transaction.transaction_id, db, current_user)
