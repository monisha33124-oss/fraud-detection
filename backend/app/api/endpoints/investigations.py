from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid

from app.db.database import get_db
from app.db.models import InvestigationCase, InvestigationNote, CaseHistory, AuditLog, Transaction, Customer, User, CaseStatus, CaseDecision, RoleEnum
from app.schemas.schemas import InvestigationCaseResponse, InvestigationCaseDetailResponse, PaginatedInvestigationCaseResponse, InvestigationNoteResponse, InvestigationNoteCreate
from app.api.deps import get_current_active_user, get_current_active_admin

router = APIRouter()

def check_case_access(case: InvestigationCase, user: User):
    if user.role != RoleEnum.ADMIN and case.BANK_EMPLOYEE_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this case")

@router.get("/", response_model=PaginatedInvestigationCaseResponse)
def get_cases(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None
):
    query = db.query(InvestigationCase)
    
    # BANK_EMPLOYEEs only see their own cases, Admins see all
    if current_user.role != RoleEnum.ADMIN:
        query = query.filter(InvestigationCase.BANK_EMPLOYEE_id == current_user.id)
        
    if status:
        query = query.filter(InvestigationCase.status == status)
        
    if priority:
        query = query.filter(InvestigationCase.priority == priority)
        
    total = query.count()
    items = query.order_by(InvestigationCase.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return PaginatedInvestigationCaseResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )

@router.get("/{case_id}", response_model=InvestigationCaseDetailResponse)
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    case = db.query(InvestigationCase).filter(InvestigationCase.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    check_case_access(case, current_user)
        
    response_data = InvestigationCaseDetailResponse.model_validate(case)
    response_data.transaction = case.transaction
    
    if case.customer:
        response_data.customer_name = case.customer.name
        
    if case.BANK_EMPLOYEE:
        response_data.BANK_EMPLOYEE_name = case.BANK_EMPLOYEE.full_name
        
    notes = []
    for n in case.notes:
        notes.append(InvestigationNoteResponse(
            note=n.note,
            id=n.id,
            author_id=n.author_id,
            created_at=n.created_at
        ))
    response_data.notes = notes
    
    history_list = []
    for h in case.history:
        history_list.append({
            "id": h.id,
            "case_id": h.case_id,
            "action": h.action,
            "performed_by": h.performed_by,
            "timestamp": h.timestamp
        })
    response_data.history = history_list
    
    return response_data

@router.post("/", response_model=InvestigationCaseResponse)
def create_case(
    transaction_id: uuid.UUID = Body(...),
    priority: str = Body(...),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_active_admin)
):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    case_id = f"CAS-{uuid.uuid4().hex[:8].upper()}"
    new_case = InvestigationCase(
        case_id=case_id,
        transaction_id=tx.id,
        customer_id=tx.customer_id,
        priority=priority,
        status=CaseStatus.NEW
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    # Audit log
    audit = AuditLog(
        user_id=current_admin.id,
        role=current_admin.role.value if current_admin.role else "UNKNOWN",
        action="INVESTIGATION_CREATED_MANUAL",
        resource=f"InvestigationCase:{new_case.case_id}",
        status="SUCCESS",
        ip_address="system"
    )
    db.add(audit)
    db.commit()
    
    return new_case

@router.patch("/{case_id}", response_model=InvestigationCaseResponse)
def update_case(
    case_id: str,
    status: Optional[str] = Body(None),
    priority: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    case = db.query(InvestigationCase).filter(InvestigationCase.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    check_case_access(case, current_user)
    
    changes = []
    if status and case.status != status:
        changes.append(f"Status changed to {status}")
        case.status = status
    if priority and current_user.role == RoleEnum.ADMIN and case.priority != priority:
        changes.append(f"Priority changed to {priority}")
        case.priority = priority
        
    case.updated_at = datetime.utcnow()
    
    for change in changes:
        history = CaseHistory(
            case_id=case.id,
            action=change,
            performed_by=current_user.id
        )
        db.add(history)
        
    db.commit()
    db.refresh(case)
    return case

@router.post("/{case_id}/assign")
def assign_case(
    case_id: str,
    BANK_EMPLOYEE_id: uuid.UUID = Body(...),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_active_admin)
):
    case = db.query(InvestigationCase).filter(InvestigationCase.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    BANK_EMPLOYEE = db.query(User).filter(User.id == BANK_EMPLOYEE_id, User.role == RoleEnum.BANK_EMPLOYEE).first()
    if not BANK_EMPLOYEE:
        raise HTTPException(status_code=404, detail="BANK_EMPLOYEE not found")
        
    case.BANK_EMPLOYEE_id = BANK_EMPLOYEE.id
    if case.status == CaseStatus.NEW:
        case.status = CaseStatus.ASSIGNED
    case.updated_at = datetime.utcnow()
    
    # Add history
    history = CaseHistory(
        case_id=case.id,
        action=f"Assigned to {BANK_EMPLOYEE.full_name}",
        performed_by=current_admin.id
    )
    db.add(history)
    db.commit()
    
    return {"message": "Case assigned successfully"}

@router.post("/{case_id}/notes", response_model=InvestigationNoteResponse)
def add_note(
    case_id: str,
    note_in: InvestigationNoteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    case = db.query(InvestigationCase).filter(InvestigationCase.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    check_case_access(case, current_user)
    
    note = InvestigationNote(
        case_id=case.id,
        author_id=current_user.id,
        note=note_in.note
    )
    db.add(note)
    
    if case.status in [CaseStatus.ASSIGNED, CaseStatus.NEW]:
        case.status = CaseStatus.UNDER_INVESTIGATION
        case.updated_at = datetime.utcnow()
        
    db.commit()
    db.refresh(note)
    return note

@router.post("/{case_id}/decision")
def submit_decision(
    case_id: str,
    decision: str = Body(...),
    reason: str = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    case = db.query(InvestigationCase).filter(InvestigationCase.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    check_case_access(case, current_user)
    
    try:
        case_decision = CaseDecision(decision)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid decision")
        
    case.decision = case_decision
    case.resolution_reason = reason
    case.updated_at = datetime.utcnow()
    
    history = CaseHistory(
        case_id=case.id,
        action=f"Decision submitted: {decision}",
        performed_by=current_user.id
    )
    db.add(history)
    db.commit()
    
    return {"message": "Decision submitted successfully"}

@router.post("/{case_id}/close")
def close_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_active_admin)
):
    case = db.query(InvestigationCase).filter(InvestigationCase.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if not case.decision:
        raise HTTPException(status_code=400, detail="Cannot close a case without a decision")
        
    case.status = CaseStatus.CLOSED
    case.closed_at = datetime.utcnow()
    case.updated_at = datetime.utcnow()
    
    history = CaseHistory(
        case_id=case.id,
        action="Case closed",
        performed_by=current_admin.id
    )
    db.add(history)
    db.commit()
    
    return {"message": "Case closed successfully"}
