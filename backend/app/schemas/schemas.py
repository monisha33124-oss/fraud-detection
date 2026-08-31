from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime
from app.db.models import RoleEnum

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: RoleEnum

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID4
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True

class TransactionCreate(BaseModel):
    customer_id: UUID4
    account_id: UUID4
    amount: float
    location: str
    merchant: str
    payment_method: str
    transaction_type: str
    device_info: str
    ip_address: str

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    location: Optional[str] = None
    merchant: Optional[str] = None
    payment_method: Optional[str] = None
    transaction_type: Optional[str] = None
    device_info: Optional[str] = None
    ip_address: Optional[str] = None

class TransactionResponse(TransactionCreate):
    id: UUID4
    transaction_id: str
    date_time: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class FraudExplanation(BaseModel):
    feature_name: str
    feature_value: float
    shap_value: float

class PredictionResponse(BaseModel):
    prediction: str
    risk_score: float
    risk_level: str
    explanations: List[FraudExplanation]

class TransactionDetailResponse(TransactionResponse):
    customer_name: Optional[str] = None
    prediction: Optional[PredictionResponse] = None
    has_alert: bool = False
    investigation_status: Optional[str] = None

class PaginatedTransactionResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[TransactionResponse]

class FraudAlertBase(BaseModel):
    alert_id: str
    transaction_id: UUID4
    customer_id: UUID4
    risk_score: float
    risk_level: str
    reason: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

class FraudAlertResponse(FraudAlertBase):
    id: UUID4
    
    class Config:
        from_attributes = True

class FraudAlertDetailResponse(FraudAlertResponse):
    transaction: Optional[TransactionResponse] = None
    prediction: Optional[PredictionResponse] = None

class PaginatedFraudAlertResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[FraudAlertResponse]

class InvestigationNoteBase(BaseModel):
    note: str

class InvestigationNoteCreate(InvestigationNoteBase):
    pass

class InvestigationNoteResponse(InvestigationNoteBase):
    id: UUID4
    author_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InvestigationCaseBase(BaseModel):
    case_id: str
    transaction_id: UUID4
    customer_id: UUID4
    investigator_id: Optional[UUID4] = None
    priority: str
    status: str
    decision: Optional[str] = None
    resolution_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

class CaseHistoryResponse(BaseModel):
    id: UUID4
    case_id: UUID4
    action: str
    performed_by: Optional[UUID4] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

class InvestigationCaseResponse(InvestigationCaseBase):
    id: UUID4

    class Config:
        from_attributes = True

class InvestigationCaseDetailResponse(InvestigationCaseResponse):
    transaction: Optional[TransactionDetailResponse] = None
    notes: List[InvestigationNoteResponse] = []
    history: List[CaseHistoryResponse] = []
    investigator_name: Optional[str] = None
    customer_name: Optional[str] = None

class PaginatedInvestigationCaseResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[InvestigationCaseResponse]

class AuditLogResponse(BaseModel):
    id: UUID4
    user_id: Optional[UUID4] = None
    role: Optional[str] = None
    action: str
    resource: Optional[str] = None
    status: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

class PaginatedAuditLogResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AuditLogResponse]
