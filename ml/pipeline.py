import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix
import joblib
import os
import sys
import shap
try:
    from imblearn.over_sampling import SMOTE
    HAS_IMBLEARN = True
except ImportError:
    HAS_IMBLEARN = False
    print("Warning: imbalanced-learn not installed, skipping SMOTE")

# Add backend to path for DB access
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from app.db.database import SessionLocal, engine, Base
from app.db.models import MLModel, ModelMetric

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "fraud_model_xgb.joblib")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.joblib")
ENCODERS_PATH = os.path.join(MODEL_DIR, "encoders.joblib")
EXPLAINER_PATH = os.path.join(MODEL_DIR, "shap_explainer.joblib")

from features.engineer import FeatureEngineer

class FraudDetectionModel:
    def __init__(self):
        self.xgb_model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42, eval_metric="logloss")
        self.rf_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.lr_model = LogisticRegression(max_iter=1000, random_state=42)
        
        self.scaler = StandardScaler()
        self.encoders = {}
        self.explainer = None
        self.engineer = FeatureEngineer()
        
        self.categorical_cols = ['payment_method', 'transaction_type', 'device_info', 'merchant']
        
    def preprocess(self, df: pd.DataFrame, training=False) -> pd.DataFrame:
        df = self.engineer.process_transactions(df)
        
        # Ensure categorical columns exist
        for col in self.categorical_cols:
            if col not in df.columns:
                df[col] = 'UNKNOWN'
        
        for col in self.categorical_cols:
            if training:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.encoders[col] = le
            else:
                le = self.encoders.get(col)
                if le:
                    # Handle unseen labels by mapping to -1 or a specific unknown class if needed
                    df[col] = df[col].apply(lambda x: le.transform([str(x)])[0] if str(x) in le.classes_ else -1)
                else:
                    df[col] = -1
                    
        self.numerical_cols = [c for c in df.columns if c not in self.categorical_cols and df[c].dtype in [np.float64, np.float32, np.int64, np.int32]]
        
        # Drop identifiers
        for col in ['transaction_id', 'customer_id', 'account_id', 'date_time', 'prev_date_time', 'location']:
            if col in self.numerical_cols:
                self.numerical_cols.remove(col)
                
        if training:
            df[self.numerical_cols] = self.scaler.fit_transform(df[self.numerical_cols])
        else:
            df[self.numerical_cols] = self.scaler.transform(df[self.numerical_cols])
            
        return df[self.numerical_cols + self.categorical_cols]

    def evaluate_model(self, model, X_test, y_test):
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

    def save_metrics_to_db(self, name, version, metrics, is_active=False):
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
        except Exception as e:
            print(f"Warning: Failed to save metrics to DB (are tables created?): {e}")
        finally:
            db.close()

    def train(self, df: pd.DataFrame, target_col: str):
        print("Preprocessing data...")
        # Drop columns we don't need for features
        X_raw = df.drop(columns=[target_col])
        y = df[target_col].astype(int)
        
        X = self.preprocess(X_raw, training=True)
        
        # Train/Test Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Handle Imbalance
        if HAS_IMBLEARN and sum(y_train) > 1 and len(y_train) - sum(y_train) > 1:
            print("Applying SMOTE to handle class imbalance...")
            smote = SMOTE(random_state=42)
            X_train, y_train = smote.fit_resample(X_train, y_train)
        else:
            print("Skipping SMOTE due to missing library or insufficient class examples.")
        
        # 1. XGBoost (Production)
        print("Training XGBoost model...")
        self.xgb_model.fit(X_train, y_train)
        xgb_metrics = self.evaluate_model(self.xgb_model, X_test, y_test)
        self.save_metrics_to_db("XGBoost", "1.1", xgb_metrics, is_active=True)
        print(f"XGBoost F1: {xgb_metrics['f1_score']:.4f}, ROC-AUC: {xgb_metrics['roc_auc']:.4f}")
        
        # 2. Random Forest
        print("Training Random Forest model...")
        self.rf_model.fit(X_train, y_train)
        rf_metrics = self.evaluate_model(self.rf_model, X_test, y_test)
        self.save_metrics_to_db("Random Forest", "1.1", rf_metrics, is_active=False)
        
        # 3. Logistic Regression
        print("Training Logistic Regression model...")
        self.lr_model.fit(X_train, y_train)
        lr_metrics = self.evaluate_model(self.lr_model, X_test, y_test)
        self.save_metrics_to_db("Logistic Regression", "1.1", lr_metrics, is_active=False)
        
        # Generate Explainer for champion (XGBoost)
        # Use TreeExplainer for Tree models
        print("Generating SHAP Explainer...")
        # A sample background dataset can speed up SHAP if needed, but TreeExplainer works fine natively
        self.explainer = shap.TreeExplainer(self.xgb_model)
        
        # Save Artifacts
        print("Persisting models...")
        joblib.dump(self.xgb_model, MODEL_PATH)
        joblib.dump(self.scaler, SCALER_PATH)
        joblib.dump(self.encoders, ENCODERS_PATH)
        joblib.dump(self.explainer, EXPLAINER_PATH)
        
        print("Pipeline successfully completed.")
        return xgb_metrics
