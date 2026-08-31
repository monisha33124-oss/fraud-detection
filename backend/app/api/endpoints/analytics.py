from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any

from app.db.database import get_db
from app.db.models import Transaction, FraudPrediction, FraudAlert, InvestigationCase, CaseStatus, RiskLevel, User
from app.api.deps import get_current_active_BANK_EMPLOYEE, get_current_active_user

router = APIRouter()

@router.get("/overview")
def get_analytics_overview(db: Session = Depends(get_db), current_user=Depends(get_current_active_BANK_EMPLOYEE)):
    """Get high level analytics overview."""
    total_volume = db.query(func.sum(Transaction.amount)).scalar() or 0.0
    total_transactions = db.query(Transaction).count()
    fraud_predictions = db.query(FraudPrediction).filter(FraudPrediction.prediction == "FRAUDULENT").count()
    legitimate_count = db.query(FraudPrediction).filter(FraudPrediction.prediction == "LEGITIMATE").count()
    
    # If some transactions don't have predictions yet, legit = total - fraud
    legitimate_count = max(legitimate_count, total_transactions - fraud_predictions)
    
    fraud_rate = (fraud_predictions / total_transactions * 100) if total_transactions > 0 else 0
    
    active_alerts = db.query(FraudAlert).filter(FraudAlert.status == "OPEN").count()
    
    return {
        "total_volume": float(total_volume),
        "total_transactions": total_transactions,
        "fraud_count": fraud_predictions,
        "legitimate_count": legitimate_count,
        "fraud_rate": round(fraud_rate, 2),
        "active_alerts": active_alerts
    }

@router.get("/risk-distribution")
def get_risk_distribution(db: Session = Depends(get_db), current_user=Depends(get_current_active_BANK_EMPLOYEE)):
    """Get distribution of transactions by risk level."""
    distribution = db.query(
        FraudPrediction.risk_level, 
        func.count(FraudPrediction.id)
    ).group_by(FraudPrediction.risk_level).all()
    
    result = {level.value: 0 for level in RiskLevel}
    for level, count in distribution:
        result[level.value] = count
        
    return result

@router.get("/fraud-trends")
def get_fraud_trends(db: Session = Depends(get_db), current_user=Depends(get_current_active_BANK_EMPLOYEE)):
    """Get fraud trends over time grouped by day."""
    # Using PostgreSQL date_trunc for day
    fraud_trend = db.query(
        func.date_trunc('day', Transaction.date_time).label('date'),
        func.count(Transaction.id).label('fraudulent')
    ).join(FraudPrediction).filter(
        FraudPrediction.prediction == "FRAUDULENT"
    ).group_by(func.date_trunc('day', Transaction.date_time)).all()
    
    legit_trend = db.query(
        func.date_trunc('day', Transaction.date_time).label('date'),
        func.count(Transaction.id).label('legitimate')
    ).join(FraudPrediction).filter(
        FraudPrediction.prediction == "LEGITIMATE"
    ).group_by(func.date_trunc('day', Transaction.date_time)).all()
    
    # Merge the trends
    merged = {}
    for row in fraud_trend:
        date_str = row.date.strftime("%Y-%m-%d")
        merged[date_str] = {"date": date_str, "fraudulent": row.fraudulent, "legitimate": 0}
        
    for row in legit_trend:
        date_str = row.date.strftime("%Y-%m-%d")
        if date_str not in merged:
            merged[date_str] = {"date": date_str, "fraudulent": 0, "legitimate": row.legitimate}
        else:
            merged[date_str]["legitimate"] = row.legitimate
            
    # Sort by date
    result = [merged[k] for k in sorted(merged.keys())]
    return result

@router.get("/fraud-by-location")
def get_fraud_by_location(db: Session = Depends(get_db), current_user=Depends(get_current_active_BANK_EMPLOYEE)):
    distribution = db.query(
        Transaction.location,
        func.count(Transaction.id)
    ).join(FraudPrediction).filter(
        FraudPrediction.prediction == "FRAUDULENT"
    ).group_by(Transaction.location).order_by(func.count(Transaction.id).desc()).limit(10).all()
    
    return [{"location": loc, "count": count} for loc, count in distribution]

@router.get("/fraud-by-payment-method")
def get_fraud_by_payment_method(db: Session = Depends(get_db), current_user=Depends(get_current_active_BANK_EMPLOYEE)):
    distribution = db.query(
        Transaction.payment_method,
        func.count(Transaction.id)
    ).join(FraudPrediction).filter(
        FraudPrediction.prediction == "FRAUDULENT"
    ).group_by(Transaction.payment_method).all()
    
    return [{"payment_method": method, "count": count} for method, count in distribution]

@router.get("/fraud-by-type")
def get_fraud_by_type(db: Session = Depends(get_db), current_user=Depends(get_current_active_BANK_EMPLOYEE)):
    distribution = db.query(
        Transaction.transaction_type,
        func.count(Transaction.id)
    ).join(FraudPrediction).filter(
        FraudPrediction.prediction == "FRAUDULENT"
    ).group_by(Transaction.transaction_type).all()
    
    return [{"transaction_type": t_type, "count": count} for t_type, count in distribution]

@router.get("/investigation-status")
def get_investigation_status(db: Session = Depends(get_db), current_user=Depends(get_current_active_BANK_EMPLOYEE)):
    distribution = db.query(
        InvestigationCase.status,
        func.count(InvestigationCase.id)
    ).group_by(InvestigationCase.status).all()
    
    result = {status.value: 0 for status in CaseStatus}
    for status, count in distribution:
        result[status.value] = count
        
    return result

@router.get("/employee-stats")
def get_employee_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_BANK_EMPLOYEE)):
    """Get personal statistics for the logged in bank employee."""
    assigned_cases = db.query(InvestigationCase).filter(
        InvestigationCase.investigator_id == current_user.id,
        InvestigationCase.status != "CLOSED"
    ).count()
    
    resolved_cases = db.query(InvestigationCase).filter(
        InvestigationCase.investigator_id == current_user.id,
        InvestigationCase.status == "CLOSED"
    ).count()
    
    high_risk_alerts = db.query(FraudAlert).filter(
        FraudAlert.status == "OPEN",
        FraudAlert.risk_level.in_(["HIGH", "CRITICAL"])
    ).count()
    
    return {
        "assigned_cases": assigned_cases,
        "resolved_cases": resolved_cases,
        "high_risk_alerts": high_risk_alerts,
        "total_cases_handled": assigned_cases + resolved_cases
    }
