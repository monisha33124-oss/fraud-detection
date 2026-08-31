import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, Any

# Add the parent directory to sys.path to allow importing from ml
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from ml.features.engineer import FeatureEngineer
from ml.explainability.shap_engine import ExplainabilityEngine
from app.db.models import RiskLevel

# Initialize ML Model singletons
try:
    from ml.pipeline import FraudDetectionModel
    pipeline = FraudDetectionModel()
    # Ensure encoders and scaler are loaded properly
    import joblib, os
    model_dir = os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml/pipeline.py")))
    if os.path.exists(os.path.join(model_dir, "encoders.joblib")):
        pipeline.encoders = joblib.load(os.path.join(model_dir, "encoders.joblib"))
    if os.path.exists(os.path.join(model_dir, "scaler.joblib")):
        pipeline.scaler = joblib.load(os.path.join(model_dir, "scaler.joblib"))
        
    engine = ExplainabilityEngine()
except Exception as e:
    print(f"Warning: Failed to load ML models. They may not be trained yet. {e}")
    engine = None
    pipeline = None

# Map engine risk level strings to RiskLevel enum
def map_risk_level(level_str: str) -> RiskLevel:
    if "Low" in level_str:
        return RiskLevel.LOW
    elif "Medium" in level_str:
        return RiskLevel.MEDIUM
    elif "High" in level_str or "Critical" in level_str:
        return RiskLevel.CRITICAL
    return RiskLevel.MEDIUM

class MLService:
    @staticmethod
    def evaluate_transaction(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a transaction and return the risk score, risk level, and explanations.
        """
        if not engine or not pipeline:
            return {
                "prediction": "Genuine",
                "risk_score": 0.0,
                "risk_level": RiskLevel.LOW.value,
                "explanations": []
            }
            
        # Convert dictionary to DataFrame for ML model
        df = pd.DataFrame([transaction_data])
        
        # Preprocess using full pipeline to encode categoricals
        X_model_input = pipeline.preprocess(df, training=False)
        
        # Run engine
        result = engine.predict_and_explain(X_model_input)
        
        risk_score = result["risk_score"]
        risk_level_str = result["risk_level"]
        risk_level = map_risk_level(risk_level_str)
        
        return {
            "prediction": result["prediction"],
            "risk_score": risk_score,
            "risk_level": risk_level.value,
            "explanations": result["explanations"]
        }
