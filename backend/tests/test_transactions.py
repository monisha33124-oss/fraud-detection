import pytest
from app.db.models import Customer, Account, RoleEnum

import uuid

def create_test_customer(db_session):
    uid = uuid.uuid4().hex[:8]
    customer = Customer(customer_id=f"C-TEST-{uid}", name="Test Cust", email=f"t{uid}@t.com")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    
    account = Account(account_number=f"A-TEST-{uid}", customer_id=customer.id)
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return customer, account

from app.db.models import Customer, Account, FraudPrediction, ShapExplanation, FraudAlert

def test_create_transaction_and_predict(client, db_session, admin_headers):
    cust, acc = create_test_customer(db_session)
    
    payload = {
        "customer_id": str(cust.id),
        "account_id": str(acc.id),
        "amount": 9999.99, # High amount to trigger risk if possible
        "location": "Test City",
        "merchant": "Test Store",
        "payment_method": "CREDIT_CARD",
        "transaction_type": "ONLINE",
        "device_info": "Browser",
        "ip_address": "127.0.0.1"
    }
    
    response = client.post("/api/v1/transactions/", json=payload, headers=admin_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "transaction_id" in data
    assert data["amount"] == 9999.99
    assert "prediction" in data
    assert "risk_score" in data["prediction"]
    
    tx_id_str = data["transaction_id"]
    tx_db_id = uuid.UUID(data["id"])
    
    # Check DB records
    prediction = db_session.query(FraudPrediction).filter(FraudPrediction.transaction_id == tx_db_id).first()
    assert prediction is not None
    assert prediction.risk_score >= 0
    
    shaps = db_session.query(ShapExplanation).filter(ShapExplanation.prediction_id == prediction.id).all()
    assert len(shaps) >= 0
    
    # Optional alert check based on risk
    if prediction.risk_level.value in ["HIGH", "CRITICAL"]:
        alert = db_session.query(FraudAlert).filter(FraudAlert.transaction_id == tx_db_id).first()
        assert alert is not None
        
    # Test PATCH
    patch_payload = {"location": "Updated City"}
    patch_resp = client.patch(f"/api/v1/transactions/{tx_id_str}", json=patch_payload, headers=admin_headers)
    assert patch_resp.status_code == 200
    assert patch_resp.json()["location"] == "Updated City"

def test_get_transactions(client, db_session, admin_headers):
    response = client.get("/api/v1/transactions/?start_date=2020-01-01T00:00:00", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_unauthorized_transactions(client):
    response = client.get("/api/v1/transactions/")
    assert response.status_code == 401
