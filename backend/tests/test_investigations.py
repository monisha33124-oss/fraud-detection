import pytest
from app.db.models import InvestigationCase, Transaction, Customer, CaseStatus, CaseDecision

def test_investigation_lifecycle(client, db_session, admin_headers, BANK_EMPLOYEE_user, BANK_EMPLOYEE_headers):
    # Setup dummy data
    from datetime import datetime
    import uuid
    cust = Customer(customer_id="C-INV", name="Cust", email="c@inv.com")
    db_session.add(cust)
    db_session.commit()
    
    tx = Transaction(transaction_id="TX-INV", customer_id=cust.id, account_id=1, amount=500.0, date_time=datetime.utcnow())
    db_session.add(tx)
    db_session.commit()
    
    # 1. Create case manually
    payload = {"transaction_id": tx.id, "priority": "HIGH"}
    resp = client.post("/api/v1/investigations/", json=payload, headers=admin_headers)
    assert resp.status_code == 200
    case_id = resp.json()["case_id"]
    
    # 2. Assign case
    resp = client.post(f"/api/v1/investigations/{case_id}/assign", json=BANK_EMPLOYEE_user.id, headers=admin_headers)
    assert resp.status_code == 200
    
    # 3. Add note as BANK_EMPLOYEE
    note_payload = {"note": "Investigating this case now."}
    resp = client.post(f"/api/v1/investigations/{case_id}/notes", json=note_payload, headers=BANK_EMPLOYEE_headers)
    assert resp.status_code == 200
    
    # 4. Submit decision
    decision_payload = {"decision": "CONFIRMED_FRAUD", "reason": "Matched signatures"}
    resp = client.post(f"/api/v1/investigations/{case_id}/decision", json=decision_payload, headers=BANK_EMPLOYEE_headers)
    assert resp.status_code == 200
    
    # 5. Close case as admin
    resp = client.post(f"/api/v1/investigations/{case_id}/close", headers=admin_headers)
    assert resp.status_code == 200
    
    # 6. Verify case closed
    resp = client.get(f"/api/v1/investigations/{case_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == CaseStatus.CLOSED.value

def test_unauthorized_BANK_EMPLOYEE_access(client, db_session, admin_headers, BANK_EMPLOYEE_headers):
    # Setup case assigned to a different user
    from app.db.models import User, RoleEnum, Customer, Transaction
    import uuid
    from datetime import datetime
    
    cust = Customer(customer_id="C-OTHER", name="Other", email="other_c@inv.com")
    db_session.add(cust)
    db_session.commit()
    
    tx = Transaction(transaction_id="TX-OTHER", customer_id=cust.id, account_id=1, amount=100.0, date_time=datetime.utcnow())
    db_session.add(tx)
    db_session.commit()
    
    other_inv = User(email="other@bank.com", hashed_password="h", full_name="O", role=RoleEnum.BANK_EMPLOYEE)
    db_session.add(other_inv)
    db_session.commit()
    
    case = InvestigationCase(
        case_id=f"CAS-{uuid.uuid4().hex[:8]}",
        transaction_id=tx.id,
        customer_id=cust.id,
        BANK_EMPLOYEE_id=other_inv.id,
        priority="HIGH",
        status=CaseStatus.ASSIGNED
    )
    db_session.add(case)
    db_session.commit()
    
    # BANK_EMPLOYEE trying to access someone else's case
    resp = client.get(f"/api/v1/investigations/{case.case_id}", headers=BANK_EMPLOYEE_headers)
    assert resp.status_code == 403

def test_get_investigations(client, BANK_EMPLOYEE_headers):
    response = client.get("/api/v1/investigations/", headers=BANK_EMPLOYEE_headers)
    assert response.status_code == 200
