import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# Mock env vars for Pydantic Settings before importing
os.environ["JWT_SECRET"] = "mock_secret"
os.environ["DATABASE_URL"] = "sqlite:///./mock.db"

# Ensure correct path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from features.engineer import FeatureEngineer
from explainability.shap_engine import ExplainabilityEngine
from pipeline import FraudDetectionModel
from app.db.models import RiskLevel
import joblib

def run_test():
    print("--- Starting Engine Verification Test ---")
    
    # 1. Create a synthetic dataset for testing training & engineering
    now = datetime.now()
    transactions = []
    
    # Generate 100 rows
    for i in range(100):
        is_fraud = 1 if i % 10 == 0 else 0
        transactions.append({
            'transaction_id': f'TXN_{i}',
            'customer_id': f'CUST_{i % 5}',
            'amount': 5000.00 if is_fraud else 50.0, 
            'date_time': now.replace(hour=2) if is_fraud else now.replace(hour=14),
            'lat': 40.7128 if is_fraud else 34.0522,
            'lon': -74.0060 if is_fraud else -118.2437,
            'prev_lat': 34.0522, 
            'prev_lon': -118.2437,
            'prev_date_time': now.replace(hour=1) if is_fraud else now.replace(hour=12),
            'is_new_device': 1 if is_fraud else 0,
            'is_new_location': 1 if is_fraud else 0,
            'payment_method': 'CREDIT_CARD',
            'transaction_type': 'ONLINE',
            'device_info': 'Mobile',
            'merchant': 'Unknown',
            'is_fraud': is_fraud
        })
        
    df = pd.DataFrame(transactions)
    
    # 2. Engineer Features Test
    print("\n1. Testing Feature Engineering...")
    engineer = FeatureEngineer()
    
    # Pass user history as itself for test
    X_engineered = engineer.process_transactions(df, df)
    
    print("Engineered Features Sample Columns:")
    print(X_engineered.columns.tolist())
    
    assert 'travel_speed_kmh' in X_engineered.columns, "Missing travel speed"
    assert 'amount_zscore' in X_engineered.columns, "Missing zscore"
    
    # 3. Test Training Pipeline
    print("\n2. Testing Training Pipeline (including SMOTE)...")
    pipeline = FraudDetectionModel()
    # Mock save_metrics_to_db so we don't need a live DB for this test
    pipeline.save_metrics_to_db = lambda name, version, metrics, is_active=False: print(f"Mock saved DB metrics for {name}")
    
    metrics = pipeline.train(df, target_col='is_fraud')
    
    assert 'f1_score' in metrics, "Missing f1 score"
    assert os.path.exists('fraud_model_xgb.joblib'), "Model not saved"
    assert os.path.exists('shap_explainer.joblib'), "Explainer not saved"
    
    # 4. Explainability Engine
    print("\n3. Running Explainability Engine...")
    
    # Use the first row for inference
    single_txn = df.iloc[[0]].drop(columns=['is_fraud'])
    
    X_processed = pipeline.preprocess(single_txn, training=False)
    
    engine_expl = ExplainabilityEngine(
        model_path='fraud_model_xgb.joblib', 
        explainer_path='shap_explainer.joblib'
    )
    result = engine_expl.predict_and_explain(X_processed)
    
    print("\n--- Verification Results ---")
    print(f"Prediction: {result['prediction']}")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Generated Summary: {result['summary']}")
    
    assert result['prediction'] in ["FRAUDULENT", "LEGITIMATE"], "Invalid prediction enum"
    assert "Risk" in result['summary'] or "risk" in result['summary'] or "Flagged" in result['summary']
    
    print("\nSUCCESS: All pipeline assertions passed!")

if __name__ == "__main__":
    run_test()
