import pytest
from app.db.models import FraudAlert, Transaction, Customer

def test_unauthorized_alerts(client):
    response = client.get("/api/v1/alerts/")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data

def test_get_alerts(client, admin_headers):
    response = client.get("/api/v1/alerts/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_alert_lifecycle(client, db_session, admin_headers):
    # Manually create a dummy alert for testing
    from datetime import datetime
    import uuid
    uid = uuid.uuid4().hex[:8]
    cust = Customer(customer_id=f"C-ALERT-{uid}", name="Cust", email=f"c{uid}@alert.com")
    db_session.add(cust)
    db_session.commit()
    
    tx = Transaction(transaction_id=f"TX-ALERT-{uid}", customer_id=cust.id, account_id=1, amount=100.0, date_time=datetime.utcnow())
    db_session.add(tx)
    db_session.commit()
    
    alert = FraudAlert(
        alert_id=f"ALT-{uid}",
        transaction_id=tx.id,
        customer_id=cust.id,
        risk_score=95.0,
        risk_level="CRITICAL",
        status="OPEN"
    )
    db_session.add(alert)
    db_session.commit()
    
    # 1. Get alert
    resp = client.get(f"/api/v1/alerts/{alert.alert_id}", headers=admin_headers)
    assert resp.status_code == 200
    
    # 2. Update status
    resp = client.patch(f"/api/v1/alerts/{alert.alert_id}/status", params={"status": "REVIEWING"}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "REVIEWING"
    
    # 3. Add review note
    resp = client.patch(f"/api/v1/alerts/{alert.alert_id}/review", params={"note": "Looks suspicious"}, headers=admin_headers)
    assert resp.status_code == 200
    assert "Looks suspicious" in resp.json()["reason"]
    
    # 4. Investigate (promotes to case)
    resp = client.post(f"/api/v1/alerts/{alert.alert_id}/investigate", headers=admin_headers)
    assert resp.status_code == 200
    assert "case_id" in resp.json()
    
    # Verify alert status changed to UNDER_INVESTIGATION
    db_session.refresh(alert)
    assert alert.status == "UNDER_INVESTIGATION"
