import os
import sys
import random
from datetime import datetime, timedelta
import string

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.db.database import SessionLocal, engine, Base
from app.db.models import User, RoleEnum, Customer, Account, Transaction

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def generate_string(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def seed_data():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    # 1. Create Users
    if not db.query(User).first():
        print("Creating users...")
        admin = User(
            email="admin@fraudshield.ai",
            hashed_password=get_password_hash("admin123"),
            full_name="System Admin",
            role=RoleEnum.ADMIN
        )
        BANK_EMPLOYEE = User(
            email="BANK_EMPLOYEE@fraudshield.ai",
            hashed_password=get_password_hash("inv123"),
            full_name="Jane BANK_EMPLOYEE",
            role=RoleEnum.BANK_EMPLOYEE
        )
        db.add(admin)
        db.add(BANK_EMPLOYEE)
        db.commit()

    # 2. Create Customers & Accounts
    if not db.query(Customer).first():
        print("Creating customers & accounts...")
        locations = ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ"]
        merchants = ["Amazon", "Walmart", "Target", "Starbucks", "Uber", "Apple", "Best Buy"]
        
        for i in range(50):
            customer = Customer(
                customer_id=f"CUST-{generate_string(6)}",
                name=f"Customer {i+1}",
                email=f"customer{i+1}@example.com",
                phone=f"555-01{str(i).zfill(2)}",
                risk_history_score=random.uniform(0, 100)
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)
            
            account = Account(
                account_number=f"ACCT-{generate_string(8)}",
                customer_id=customer.id
            )
            db.add(account)
            db.commit()
            db.refresh(account)
            
            # 3. Create Transactions
            num_transactions = random.randint(10, 50)
            start_date = datetime.now() - timedelta(days=90)
            
            for j in range(num_transactions):
                tx_date = start_date + timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
                amount = round(random.uniform(10.0, 500.0), 2)
                
                # Introduce some fraud-like high amount transactions occasionally
                if random.random() > 0.95:
                    amount = round(random.uniform(1000.0, 10000.0), 2)
                    
                transaction = Transaction(
                    transaction_id=f"TXN-{generate_string(10)}",
                    customer_id=customer.id,
                    account_id=account.id,
                    amount=amount,
                    date_time=tx_date,
                    location=random.choice(locations),
                    merchant=random.choice(merchants),
                    payment_method=random.choice(["CREDIT_CARD", "DEBIT_CARD", "BANK_TRANSFER"]),
                    transaction_type=random.choice(["ONLINE", "POS", "ATM"]),
                    device_info=random.choice(["Mobile App", "Web Browser", "Physical POS"]),
                    ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
                )
                db.add(transaction)
                db.commit()
                db.refresh(transaction)
                
                # Add Prediction using MLService
                try:
                    from app.services.ml_service import MLService
                    from app.db.models import FraudPrediction, ShapExplanation, FraudAlert, RiskLevel, PredictionResult
                    import uuid
                    
                    ml_input = {
                        "amount": transaction.amount,
                        "date_time": str(transaction.date_time),
                        "location": transaction.location,
                        "merchant": transaction.merchant,
                        "payment_method": transaction.payment_method,
                        "transaction_type": transaction.transaction_type,
                        "device_info": transaction.device_info,
                        "ip_address": transaction.ip_address
                    }
                    ml_result = MLService.evaluate_transaction(ml_input)
                    
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
                        
                    if prediction.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
                        alert = FraudAlert(
                            alert_id=alert_id,
                            transaction_id=transaction.id,
                            customer_id=transaction.customer_id,
                            risk_score=prediction.risk_score,
                            risk_level=prediction.risk_level,
                            reason=f"High risk score detected: {prediction.risk_score}",
                            status="OPEN"
                        )
                        db.add(alert)
                except Exception as e:
                    print(f"Error during ML prediction for seed data: {e}")
            
        db.commit()
        print("Synthetic data seeded successfully!")
    else:
        print("Database already contains data, skipping seed.")
        
    db.close()

if __name__ == "__main__":
    seed_data()
