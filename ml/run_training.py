import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from pipeline import FraudDetectionModel
from app.db.database import SessionLocal, engine
from app.db.models import Transaction, FraudPrediction

def fetch_data():
    db = SessionLocal()
    try:
        # Fetch transactions and join with fraud predictions
        query = db.query(Transaction, FraudPrediction).outerjoin(FraudPrediction, Transaction.id == FraudPrediction.transaction_id)
        
        data = []
        for t, p in query.all():
            if p:
                data.append({
                    "amount": t.amount,
                    "date_time": t.date_time,
                    "location": t.location,
                    "merchant": t.merchant,
                    "payment_method": t.payment_method,
                    "transaction_type": t.transaction_type,
                    "device_info": t.device_info,
                    "is_fraud": 1 if p.prediction == "FRAUDULENT" else 0
                })
        return pd.DataFrame(data)
    finally:
        db.close()

if __name__ == "__main__":
    print("Fetching data from database for training...")
    df = fetch_data()
    
    if len(df) < 50:
        print("Not enough data to train. Please seed the database first.")
        sys.exit(1)
        
    print(f"Loaded {len(df)} transactions.")
    
    pipeline = FraudDetectionModel()
    pipeline.train(df, target_col="is_fraud")
    print("Training complete and metrics saved to database!")
