import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix
import joblib
import os
import sys
import shap

# Add backend to path for DB access
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from app.db.database import SessionLocal
from app.db.models import MLModel, ModelMetric

# Ensure output directory exists
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred
    
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "pr_auc": float(average_precision_score(y_test, y_prob)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
    }

def save_metrics_to_db(name, version, metrics, is_active=False):
    db = SessionLocal()
    try:
        if is_active:
            db.query(MLModel).update({MLModel.is_active: False})
            
        model_record = MLModel(name=name, version=version, is_active=is_active)
        db.add(model_record)
        db.commit()
        db.refresh(model_record)
        
        metric_record = ModelMetric(
            model_id=model_record.id,
            accuracy=metrics['accuracy'],
            precision=metrics['precision'],
            recall=metrics['recall'],
            f1_score=metrics['f1_score'],
            roc_auc=metrics['roc_auc'],
            pr_auc=metrics.get('pr_auc', 0.0)
        )
        db.add(metric_record)
        db.commit()
    finally:
        db.close()

def train_and_compare_models(X: pd.DataFrame, y: pd.Series, output_dir: str = '../artifacts'):
    ensure_dir(output_dir)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Calculate scale_pos_weight for imbalance
    pos_count = sum(y_train)
    neg_count = len(y_train) - pos_count
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0
    
    print("Training Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
    lr_model.fit(X_train, y_train)
    lr_metrics = evaluate_model(lr_model, X_test, y_test)
    save_metrics_to_db("Logistic Regression", "2.0", lr_metrics, is_active=False)
    
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, class_weight='balanced')
    rf_model.fit(X_train, y_train)
    rf_metrics = evaluate_model(rf_model, X_test, y_test)
    save_metrics_to_db("Random Forest", "2.0", rf_metrics, is_active=False)
    
    print("Training XGBoost...")
    xgb_model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42, eval_metric="logloss", scale_pos_weight=scale_pos_weight)
    xgb_model.fit(X_train, y_train)
    xgb_metrics = evaluate_model(xgb_model, X_test, y_test)
    save_metrics_to_db("XGBoost", "2.0", xgb_metrics, is_active=True)
    
    # Save Champion Model (XGBoost)
    champion_path = os.path.join(output_dir, "champion_model.joblib")
    joblib.dump(xgb_model, champion_path)
    
    # Pre-fit SHAP Explainer
    explainer = shap.TreeExplainer(xgb_model)
    explainer_path = os.path.join(output_dir, "shap_explainer.joblib")
    joblib.dump(explainer, explainer_path)
    
    print(f"Models trained and artifacts saved to {output_dir}")
    return xgb_metrics
