import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from app.db.database import SessionLocal
from app.db.models import User

def check():
    db = SessionLocal()
    users = db.query(User).all()
    for u in users:
        print(f"Email: {u.email} | Hash: {u.hashed_password[:20]}... | Active: {u.is_active}")

if __name__ == "__main__":
    check()
