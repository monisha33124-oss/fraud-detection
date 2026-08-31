import sys
import os
import random
import uuid
from datetime import datetime, timedelta

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker

from app.db.database import Base
from app.db.models import (
    User, RoleEnum, Customer, Account, Transaction, FraudPrediction,
    PredictionResult, RiskLevel, ShapExplanation, FraudAlert,
    InvestigationCase, CaseStatus, CaseDecision, InvestigationNote,
    AuditLog
)
from app.core.config import settings
from passlib.context import CryptContext

fake = Faker()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def seed_database():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    # Create tables (if running without migrations for testing)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Clearing existing data...")
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()

        print("Seeding Users...")
        admin = User(
            email="admin@fraudshield.ai",
            hashed_password=get_password_hash("admin123"),
            full_name="System Admin",
            role=RoleEnum.ADMIN
        )
        db.add(admin)
        
        BANK_EMPLOYEEs = []
        for i in range(3):
            inv = User(
                email=f"BANK_EMPLOYEE{i+1}@fraudshield.ai",
                hashed_password=get_password_hash("BANK_EMPLOYEE123"),
                full_name=fake.name(),
                role=RoleEnum.BANK_EMPLOYEE
            )
            BANK_EMPLOYEEs.append(inv)
            db.add(inv)
            
        db.commit()
        db.refresh(admin)
        for inv in BANK_EMPLOYEEs:
            db.refresh(inv)

        print("Seeding Customers & Accounts...")
        customers = []
        for _ in range(50):
            cust = Customer(
                customer_id=f"CUST-{fake.unique.random_number(digits=6)}",
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number(),
                risk_history_score=random.uniform(0, 100)
            )
            customers.append(cust)
            db.add(cust)
            
        db.commit()
        
        accounts = []
        for cust in customers:
            num_accounts = random.randint(1, 3)
            for _ in range(num_accounts):
                acc = Account(
                    account_number=fake.unique.bban(),
                    customer_id=cust.id
                )
                accounts.append(acc)
                db.add(acc)
                
        db.commit()

        print("Seeding Transactions, Predictions, and Alerts...")
        for _ in range(200):
            acc = random.choice(accounts)
            tx = Transaction(
                transaction_id=f"TXN-{fake.unique.random_number(digits=8)}",
                customer_id=acc.customer_id,
                account_id=acc.id,
                amount=round(random.uniform(10.0, 5000.0), 2),
                date_time=fake.date_time_between(start_date="-30d", end_date="now"),
                location=fake.city(),
                merchant=fake.company(),
                payment_method=random.choice(["CREDIT_CARD", "DEBIT_CARD", "BANK_TRANSFER"]),
                transaction_type=random.choice(["ONLINE", "IN_STORE", "INTERNATIONAL"]),
                device_info=fake.user_agent(),
                ip_address=fake.ipv4()
            )
            db.add(tx)
            db.commit()
            db.refresh(tx)
            
            # Prediction
            is_fraud = random.random() < 0.1
            risk_score = random.uniform(80, 100) if is_fraud else random.uniform(0, 30)
            risk_level = RiskLevel.CRITICAL if risk_score > 90 else (RiskLevel.HIGH if risk_score > 60 else RiskLevel.LOW)
            
            pred = FraudPrediction(
                transaction_id=tx.id,
                prediction=PredictionResult.FRAUDULENT if is_fraud else PredictionResult.LEGITIMATE,
                risk_score=risk_score,
                risk_level=risk_level
            )
            db.add(pred)
            db.commit()
            db.refresh(pred)
            
            # SHAP
            for feature in ["amount", "location", "velocity"]:
                shap = ShapExplanation(
                    prediction_id=pred.id,
                    feature_name=feature,
                    feature_value=random.uniform(0, 1),
                    shap_value=random.uniform(-1, 1)
                )
                db.add(shap)
            
            # Alert & Case
            if is_fraud:
                alert = FraudAlert(
                    alert_id=f"ALT-{fake.unique.random_number(digits=6)}",
                    transaction_id=tx.id,
                    customer_id=tx.customer_id,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    reason="High risk score detected"
                )
                db.add(alert)
                db.commit()
                
                case = InvestigationCase(
                    case_id=f"CAS-{fake.unique.random_number(digits=6)}",
                    transaction_id=tx.id,
                    customer_id=tx.customer_id,
                    BANK_EMPLOYEE_id=random.choice(BANK_EMPLOYEEs).id if random.random() > 0.5 else None,
                    priority=risk_level,
                    status=CaseStatus.ASSIGNED if random.random() > 0.5 else CaseStatus.NEW
                )
                db.add(case)
                db.commit()
                db.refresh(case)
                
                if case.BANK_EMPLOYEE_id:
                    note = InvestigationNote(
                        case_id=case.id,
                        author_id=case.BANK_EMPLOYEE_id,
                        note="Started investigation."
                    )
                    db.add(note)
                    
                    history = CaseHistory(
                        case_id=case.id,
                        action="Assigned to BANK_EMPLOYEE",
                        performed_by=admin.id
                    )
                    db.add(history)
                    
        db.commit()
        
        print("Seeding Audit Logs...")
        for _ in range(50):
            log = AuditLog(
                user_id=admin.id,
                role=RoleEnum.ADMIN,
                action=random.choice(["LOGIN", "VIEW_CASE", "UPDATE_CONFIG"]),
                status="SUCCESS",
                ip_address=fake.ipv4()
            )
            db.add(log)
            
        db.commit()
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
