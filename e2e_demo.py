import httpx
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"

def run_e2e_simulation():
    print("🚀 Starting End-to-End Simulation...\n")
    
    with httpx.Client() as client:
        # 1. Login as Admin
        print("🔐 Logging in as Admin...")
        login_res = client.post(f"{BASE_URL}/auth/login", data={"username": "admin@fraudshield.ai", "password": "admin123"})
        if login_res.status_code != 200:
            print(f"Failed to login: {login_res.text}")
            sys.exit(1)
        admin_token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}
        print("✅ Admin Login Successful.\n")

        # 2. Get a valid customer
        print("🔍 Fetching a valid customer...")
        cust_res = client.get(f"{BASE_URL}/customers/?page_size=1", headers=headers)
        customers = cust_res.json().get("items", [])
        if not customers:
            print("No customers found.")
            sys.exit(1)
        customer = customers[0]
        customer_id = customer["id"]
        
        # 3. Create a high-risk transaction
        print(f"💳 Submitting a HIGH-RISK transaction for customer {customer_id}...")
        tx_payload = {
            "customer_id": customer_id,
            "account_id": 1,
            "amount": 95000.00,  # High amount
            "location": "Unknown/Foreign IP",
            "merchant": "Crypto Exchange",
            "payment_method": "CREDIT_CARD",
            "transaction_type": "ONLINE",
            "device_info": "New Device",
            "ip_address": "192.168.1.100"
        }
        tx_res = client.post(f"{BASE_URL}/transactions/", json=tx_payload, headers=headers)
        tx_data = tx_res.json()
        print(f"✅ Transaction {tx_data.get('transaction_id')} submitted.")
        print(f"🧠 ML Prediction: {tx_data['prediction']['prediction']} (Risk Score: {tx_data['prediction']['risk_score']})")
        print(f"🚩 Alert Generated: {'Yes' if tx_data['has_alert'] else 'No'}\n")

        # 4. Fetch the Alert
        print("🚨 Fetching the generated fraud alert...")
        alerts_res = client.get(f"{BASE_URL}/alerts/?page_size=5", headers=headers)
        alerts = alerts_res.json().get("items", [])
        alert = next((a for a in alerts if a["transaction_id"] == tx_data["id"]), None)
        if not alert:
            print("Alert not found.")
            sys.exit(1)
        print(f"✅ Found Alert {alert['alert_id']} with Risk Level: {alert['risk_level']}\n")

        # 5. Escalate to Case
        print(f"📂 Escalating Alert {alert['alert_id']} to an Investigation Case...")
        case_payload = {"transaction_id": tx_data["id"], "priority": "HIGH"}
        case_res = client.post(f"{BASE_URL}/investigations/", json=case_payload, headers=headers)
        case_data = case_res.json()
        case_id = case_data["case_id"]
        print(f"✅ Case {case_id} created.\n")
        
        # 6. Login as Investigator
        print("🔐 Logging in as Investigator...")
        inv_login = client.post(f"{BASE_URL}/auth/login", data={"username": "investigator@fraudshield.ai", "password": "inv123"})
        inv_token = inv_login.json()["access_token"]
        inv_headers = {"Authorization": f"Bearer {inv_token}"}
        
        inv_me = client.get(f"{BASE_URL}/auth/me", headers=inv_headers)
        investigator_user_id = inv_me.json()["id"]
        print("✅ Investigator Login Successful.\n")

        # 7. Assign Case
        print(f"👤 Assigning Case {case_id} to Investigator...")
        assign_res = client.post(f"{BASE_URL}/investigations/{case_id}/assign", json=investigator_user_id, headers=headers)
        print(f"✅ Case Assigned. Status: {assign_res.status_code}\n")

        # 8. Add Investigation Note
        print("📝 Adding Investigation Note...")
        note_res = client.post(f"{BASE_URL}/investigations/{case_id}/notes", json={"note": "Reviewed SHAP explanations. High amount to unknown crypto exchange confirms fraud."}, headers=inv_headers)
        print(f"✅ Note Added. Status: {note_res.status_code}\n")

        # 9. Submit Decision
        print("⚖️ Submitting Final Decision...")
        decision_res = client.post(f"{BASE_URL}/investigations/{case_id}/decision", json={"decision": "CONFIRMED_FRAUD", "reason": "Confirmed via phone call with customer."}, headers=inv_headers)
        print(f"✅ Decision Submitted. Status: {decision_res.status_code}\n")

        # 10. Close Case
        print("🔒 Admin Closing Case...")
        close_res = client.post(f"{BASE_URL}/investigations/{case_id}/close", headers=headers)
        print(f"✅ Case Closed. Status: {close_res.status_code}\n")
        
        print("🎉 End-to-End Workflow Completed Successfully!")

if __name__ == "__main__":
    run_e2e_simulation()
