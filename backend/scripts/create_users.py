import os
import sys

# Append the current directory (backend) to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.db.models import User, RoleEnum
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def create_users():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # BANK_EMPLOYEE User
    email = "BANK_EMPLOYEE@fraudshield.ai"
    password = "inv123"
    hashed = pwd_context.hash(password)
    
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.hashed_password = hashed
        print(f"Password reset for {email}")
    else:
        user = User(
            email=email,
            hashed_password=hashed,
            full_name="Senior BANK_EMPLOYEE",
            role=RoleEnum.BANK_EMPLOYEE
        )
        db.add(user)
        print(f"Created user {email}")
        
    db.commit()
    db.close()

if __name__ == "__main__":
    create_users()
