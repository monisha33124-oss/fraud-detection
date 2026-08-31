import enum
import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text, Enum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base

class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    BANK_EMPLOYEE = "BANK_EMPLOYEE"

class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class PredictionResult(str, enum.Enum):
    LEGITIMATE = "LEGITIMATE"
    FRAUDULENT = "FRAUDULENT"

class CaseStatus(str, enum.Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    PENDING_INFORMATION = "PENDING_INFORMATION"
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class CaseDecision(str, enum.Enum):
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    LEGITIMATE_TRANSACTION = "LEGITIMATE_TRANSACTION"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    NEEDS_FURTHER_REVIEW = "NEEDS_FURTHER_REVIEW"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.BANK_EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Customer(Base):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    risk_history_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    accounts = relationship("Account", back_populates="customer", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    account_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    account_status = Column(String, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    customer = relationship("Customer", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    date_time = Column(DateTime(timezone=True), nullable=False, index=True)
    location = Column(String)
    merchant = Column(String)
    payment_method = Column(String)
    transaction_type = Column(String)
    device_info = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    customer = relationship("Customer", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    prediction = relationship("FraudPrediction", back_populates="transaction", uselist=False, cascade="all, delete-orphan")
    alert = relationship("FraudAlert", back_populates="transaction", uselist=False, cascade="all, delete-orphan")
    investigation_case = relationship("InvestigationCase", back_populates="transaction", uselist=False, cascade="all, delete-orphan")

class FraudPrediction(Base):
    __tablename__ = "fraud_predictions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), unique=True)
    prediction = Column(Enum(PredictionResult), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    transaction = relationship("Transaction", back_populates="prediction")
    explanations = relationship("ShapExplanation", back_populates="prediction", cascade="all, delete-orphan")

class ShapExplanation(Base):
    __tablename__ = "shap_explanations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("fraud_predictions.id", ondelete="CASCADE"), index=True)
    feature_name = Column(String, nullable=False)
    feature_value = Column(Float, nullable=False)
    shap_value = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    prediction = relationship("FraudPrediction", back_populates="explanations")

class FraudAlert(Base):
    __tablename__ = "fraud_alerts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    alert_id = Column(String, unique=True, index=True, nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False, index=True)
    reason = Column(Text)
    status = Column(String, default="OPEN", index=True) # OPEN, CLOSED
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    transaction = relationship("Transaction", back_populates="alert")
    customer = relationship("Customer")

class InvestigationCase(Base):
    __tablename__ = "investigation_cases"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    case_id = Column(String, unique=True, index=True, nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    investigator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    priority = Column(Enum(RiskLevel), nullable=False, index=True)
    status = Column(Enum(CaseStatus), default=CaseStatus.NEW, index=True)
    decision = Column(Enum(CaseDecision), nullable=True)
    resolution_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    transaction = relationship("Transaction", back_populates="investigation_case")
    customer = relationship("Customer")
    investigator = relationship("User")
    notes = relationship("InvestigationNote", back_populates="case", cascade="all, delete-orphan")
    history = relationship("CaseHistory", back_populates="case", cascade="all, delete-orphan")

class InvestigationNote(Base):
    __tablename__ = "investigation_notes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    case_id = Column(UUID(as_uuid=True), ForeignKey("investigation_cases.id", ondelete="CASCADE"), index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    note = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    case = relationship("InvestigationCase", back_populates="notes")
    author = relationship("User")

class CaseHistory(Base):
    __tablename__ = "case_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    case_id = Column(UUID(as_uuid=True), ForeignKey("investigation_cases.id", ondelete="CASCADE"), index=True)
    action = Column(String, nullable=False)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    case = relationship("InvestigationCase", back_populates="history")
    user = relationship("User")

class MLModel(Base):
    __tablename__ = "ml_models"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    trained_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ModelMetric(Base):
    __tablename__ = "model_metrics"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_models.id", ondelete="CASCADE"))
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)
    pr_auc = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    model = relationship("MLModel")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    role = Column(String)
    action = Column(String, nullable=False, index=True)
    resource = Column(String)
    status = Column(String)
    ip_address = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
