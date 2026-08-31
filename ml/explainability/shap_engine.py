import pandas as pd
import numpy as np
import joblib
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from app.core.config import settings
from app.db.models import RiskLevel

class ExplainabilityEngine:
    def __init__(self, model_path: str = '../fraud_model_xgb.joblib', explainer_path: str = '../shap_explainer.joblib'):
        try:
            self.model = joblib.load(os.path.abspath(os.path.join(os.path.dirname(__file__), model_path)))
            self.explainer = joblib.load(os.path.abspath(os.path.join(os.path.dirname(__file__), explainer_path)))
            self.is_mocked = False
        except (FileNotFoundError, Exception) as e:
            print(f"WARNING: ML artifacts not found ({e}). Using fallback mock for UI demonstration.")
            class MockModel:
                def predict_proba(self, X): return np.array([[0.05, 0.95]]) # High fraud probability
            class MockExplainer:
                def shap_values(self, X):
                    n_features = X.shape[1]
                    vals = np.random.uniform(-0.5, 1.5, size=(1, n_features))
                    vals[0][0] = 1.2
                    return vals
            self.model = MockModel()
            self.explainer = MockExplainer()
            self.is_mocked = True
            
        self.thresh_medium = settings.RISK_THRESHOLD_MEDIUM
        self.thresh_high = settings.RISK_THRESHOLD_HIGH
        self.thresh_critical = settings.RISK_THRESHOLD_CRITICAL
        
    def predict_and_explain(self, X: pd.DataFrame):
        # 1. Classification & Score
        y_prob = self.model.predict_proba(X)[:, 1][0]
        risk_score = round(y_prob * 100, 2)
        prediction_label = "FRAUDULENT" if risk_score >= 50 else "LEGITIMATE"
        
        # 2. Map centralized risk logic
        if risk_score <= self.thresh_medium:
            risk_level = RiskLevel.LOW.value
        elif risk_score <= self.thresh_high:
            risk_level = RiskLevel.MEDIUM.value
        elif risk_score <= self.thresh_critical:
            risk_level = RiskLevel.HIGH.value
        else:
            risk_level = RiskLevel.CRITICAL.value
            
        # 3. SHAP attribution
        shap_values = self.explainer.shap_values(X)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
            
        # For single row
        if len(shap_values.shape) == 2:
            shap_values = shap_values[0]
            
        feature_names = X.columns.tolist()
        
        shap_contributions = []
        for i, feature in enumerate(feature_names):
            val = float(shap_values[i])
            direction = "INCREASE" if val > 0 else "DECREASE"
            shap_contributions.append({
                "feature_name": feature,
                "feature_value": float(X.iloc[0, i]),
                "shap_value": val,
                "impact_direction": direction
            })
            
        shap_contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        positive_drivers = [x for x in shap_contributions if x["shap_value"] > 0]
        positive_drivers.sort(key=lambda x: x["shap_value"], reverse=True)
        
        # Human-Readable synthesis
        summary = f"Flagged as {risk_level} Risk. "
        if positive_drivers:
            reasons = []
            for driver in positive_drivers[:3]:
                fname = driver['feature_name']
                fval = driver['feature_value']
                
                if fname == 'amount_zscore':
                    reasons.append(f"Transaction amount is {fval:.1f} standard deviations above normal")
                elif fname == 'travel_speed_kmh' and fval > 1000:
                    reasons.append(f"Impossible travel speed detected ({fval:.0f} km/h)")
                elif fname == 'is_new_device' and fval == 1:
                    reasons.append(f"A new unrecognized device was used")
                elif fname == 'is_new_location' and fval == 1:
                    reasons.append(f"A new location was detected")
                elif fname == 'is_night_transaction' and fval == 1:
                    reasons.append(f"Transaction occurred during unusual night hours")
                elif fname == 'haversine_distance_km' and fval > 500:
                    reasons.append(f"Significant distance from previous transaction ({fval:.0f} km)")
                else:
                    reasons.append(f"{fname} feature was unusual (val: {fval:.2f})")
            
            if reasons:
                summary += "Main drivers: " + ", ".join(reasons) + "."
            else:
                summary += "Based on general transaction patterns."
        else:
            summary += "Based on general transaction patterns."
            
        return {
            "prediction": prediction_label,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "explanations": shap_contributions,
            "summary": summary
        }
