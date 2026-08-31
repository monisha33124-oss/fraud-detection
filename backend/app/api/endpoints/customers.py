from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.db.database import get_db
from app.api import deps
from app.db.models import Customer, User, Transaction, FraudPrediction, FraudAlert, InvestigationCase

router = APIRouter()

@router.get("/")
def get_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    offset = (page - 1) * page_size
    customers = db.query(Customer).offset(offset).limit(page_size).all()
    
    result = []
    for c in customers:
        tx_count = db.query(Transaction).filter(Transaction.customer_id == c.id).count()
        avg_risk = db.query(func.avg(FraudPrediction.risk_score)).join(Transaction).filter(Transaction.customer_id == c.id).scalar()
        
        result.append({
            "id": c.id,
            "customer_id": c.customer_id,
            "name": c.name,
            "email": c.email,
            "risk_score_avg": float(avg_risk) if avg_risk else 0.0,
            "total_transactions": tx_count
        })
        
    return result

@router.get("/{customer_id}")
def get_customer_detail(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    c = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    transactions = db.query(Transaction).filter(Transaction.customer_id == c.id).order_by(Transaction.date_time.desc()).limit(20).all()
    alerts = db.query(FraudAlert).filter(FraudAlert.customer_id == c.id).order_by(FraudAlert.created_at.desc()).limit(10).all()
    cases = db.query(InvestigationCase).filter(InvestigationCase.customer_id == c.id).order_by(InvestigationCase.created_at.desc()).all()
    
    # Risk history over time (last 10 transactions)
    tx_with_preds = db.query(Transaction, FraudPrediction).join(
        FraudPrediction, Transaction.id == FraudPrediction.transaction_id
    ).filter(Transaction.customer_id == c.id).order_by(Transaction.date_time.asc()).limit(50).all()
    
    risk_history = [
        {
            "date": t.date_time.isoformat(),
            "score": p.risk_score
        } for t, p in tx_with_preds
    ]
    
    return {
        "id": c.id,
        "customer_id": c.customer_id,
        "name": c.name,
        "email": c.email,
        "phone": c.phone,
        "address": c.address,
        "created_at": c.created_at,
        "transactions": [
            {
                "id": t.id,
                "transaction_id": t.transaction_id,
                "amount": t.amount,
                "date_time": t.date_time,
                "location": t.location,
                "merchant": t.merchant
            } for t in transactions
        ],
        "alerts": [
            {
                "id": a.id,
                "alert_id": a.alert_id,
                "status": a.status,
                "risk_level": a.risk_level.value,
                "created_at": a.created_at
            } for a in alerts
        ],
        "cases": [
            {
                "id": case.id,
                "case_id": case.case_id,
                "status": case.status,
                "priority": case.priority,
                "created_at": case.created_at
            } for case in cases
        ],
        "risk_history": risk_history
    }
