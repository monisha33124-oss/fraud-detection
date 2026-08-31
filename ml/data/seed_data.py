import os
import sys
import random
from datetime import datetime, timedelta
# Add backend directory to sys.path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.db.database import SessionLocal, engine, Base
from app.db.models import (
    User, RoleEnum, Customer, Account, Transaction, 
    FraudPrediction, PredictionResult, RiskLevel, 
    ShapExplanation, FraudAlert, InvestigationCase, CaseStatus, CaseDecision
)
from app.core.security import get_password_hash

def seed_database():
    print("Dropping existing tables to start fresh...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Create users
        admin = db.query(User).filter(User.email == "admin@bank.com").first()
        if not admin:
            admin = User(
                email="admin@bank.com",
                hashed_password=get_password_hash("AdminPass123!"),
                full_name="System Admin",
                role=RoleEnum.ADMIN
            )
            db.add(admin)

        investigator = db.query(User).filter(User.email == "investigator@bank.com").first()
        if not investigator:
            investigator = User(
                email="investigator@bank.com",
                hashed_password=get_password_hash("Investigate123!"),
                full_name="Alice Investigator",
                role=RoleEnum.INVESTIGATOR
            )
            db.add(investigator)
            
        db.commit()
        if admin: db.refresh(admin)
        if investigator: db.refresh(investigator)

        # Create customers
        customers = []
        for i in range(10):
            customer = Customer(
                customer_id=f"CUST{i:04d}",
                name=f"Customer {i}",
                email=f"customer{i}@example.com",
                phone=f"+1555010{i:03d}",
                risk_history_score=random.uniform(0, 100)
            )
            db.add(customer)
            customers.append(customer)
        db.commit()

        # Create accounts
        accounts = []
        for i, customer in enumerate(customers):
            account = Account(
                account_number=f"ACC{i:06d}",
                customer_id=customer.id
            )
            db.add(account)
            accounts.append(account)
        db.commit()

        # Create transactions and predictions
        locations = ["New York, USA", "London, UK", "Tokyo, Japan", "Paris, France"]
        merchants = ["Amazon", "Walmart", "Apple", "Uber", "Netflix"]
        types = ["POS", "ONLINE", "ATM", "WIRE"]
        devices = ["iPhone 13", "MacBook Pro", "Android", "Windows PC"]
        
        now = datetime.utcnow()
        transactions = []
        for i in range(200):
            acc = random.choice(accounts)
            is_fraud = random.random() < 0.1 # 10% fraud rate
            amount = random.uniform(5000, 15000) if is_fraud else random.uniform(10, 500)
            
            tx = Transaction(
                transaction_id=f"TXN{i:06d}",
                customer_id=acc.customer_id,
                account_id=acc.id,
                amount=amount,
                date_time=now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
                location=random.choice(locations),
                merchant=random.choice(merchants),
                payment_method="CREDIT_CARD",
                transaction_type=random.choice(types),
                device_info=random.choice(devices),
                ip_address=f"192.168.1.{random.randint(1, 255)}"
            )
            db.add(tx)
            db.commit()
            db.refresh(tx)
            
            # Add Prediction
            risk_score = random.uniform(80, 100) if is_fraud else random.uniform(0, 49)
            risk_level = RiskLevel.CRITICAL if risk_score >= 80 else RiskLevel.HIGH if risk_score >= 60 else RiskLevel.MEDIUM if risk_score >= 30 else RiskLevel.LOW
            prediction_val = PredictionResult.FRAUDULENT if is_fraud else PredictionResult.LEGITIMATE
            
            pred = FraudPrediction(
                transaction_id=tx.id,
                prediction=prediction_val,
                risk_score=risk_score,
                risk_level=risk_level
            )
            db.add(pred)
            db.commit()
            db.refresh(pred)
            
            # Add SHAP
            shap = ShapExplanation(
                prediction_id=pred.id,
                feature_name="amount",
                feature_value=amount,
                shap_value=2.5 if is_fraud else -0.5
            )
            db.add(shap)
            db.commit()
            
            # Create alerts and cases for high risk
            if is_fraud:
                alert = FraudAlert(
                    alert_id=f"ALT{i:04d}",
                    transaction_id=tx.id,
                    customer_id=tx.customer_id,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    reason="High amount anomalous transaction"
                )
                db.add(alert)
                db.commit()
                
                case = InvestigationCase(
                    case_id=f"CASE{i:04d}",
                    transaction_id=tx.id,
                    customer_id=tx.customer_id,
                    priority=risk_level
                )
                db.add(case)
                db.commit()

        print("Database seeded successfully with default accounts and 200 transactions.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
