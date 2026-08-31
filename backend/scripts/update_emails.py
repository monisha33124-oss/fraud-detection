import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.database import SessionLocal
from app.db.models import User

def update_emails():
    db = SessionLocal()
    
    admin = db.query(User).filter(User.email == "admin@bank.com").first()
    if admin:
        admin.email = "admin@fraudshield.ai"
        print("Updated Admin email")

    inv = db.query(User).filter(User.email == "investigator@bank.com").first()
    if inv:
        inv.email = "investigator@fraudshield.ai"
        print("Updated Investigator email")
        
    db.commit()
    db.close()
    print("Done")

if __name__ == "__main__":
    update_emails()
