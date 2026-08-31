from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.database import get_db
from app.db.models import MLModel, ModelMetric, User, RoleEnum
from app.api.deps import get_current_active_admin

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from ml.run_training import fetch_data
from ml.pipeline import FraudDetectionModel

router = APIRouter()

@router.get("/metrics")
def get_model_metrics(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_admin)):
    """Fetch the latest evaluation metrics for all trained models."""
    
    # Get all models, optionally fetch the latest by version/trained_at
    models = db.query(MLModel).all()
    
    if not models:
        return []
        
    results = []
    for model in models:
        metric = db.query(ModelMetric).filter(ModelMetric.model_id == model.id).first()
        if metric:
            results.append({
                "name": model.name,
                "version": model.version,
                "is_active": model.is_active,
                "trained_at": model.trained_at,
                "accuracy": metric.accuracy,
                "precision": metric.precision,
                "recall": metric.recall,
                "f1": metric.f1_score,
                "auc": metric.roc_auc,
                "pr_auc": metric.pr_auc
            })
            
    return results

def retrain_model_task():
    try:
        print("Starting background retraining task...")
        df = fetch_data()
        if len(df) < 10:
            print("Not enough data to retrain.")
            return
            
        pipeline = FraudDetectionModel()
        pipeline.train(df, target_col="is_fraud")
        print("Retraining completed successfully.")
    except Exception as e:
        print(f"Retraining failed: {e}")

@router.post("/retrain")
def trigger_retraining(background_tasks: BackgroundTasks, current_user: User = Depends(get_current_active_admin)):
    """Triggers an asynchronous ML model retraining job."""
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can trigger model retraining.")
        
    background_tasks.add_task(retrain_model_task)
    return {"message": "Model retraining job has been queued in the background."}
