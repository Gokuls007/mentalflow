from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.security.auth import hash_password, verify_password

class UserService:
    """Business logic for User management."""
    
    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def create_user(self, db: Session, user_in: UserCreate) -> User:
        """Create a new user with hashed password."""
        db_user = User(
            email=user_in.email,
            password_hash=hash_password(user_in.password),
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            age=user_in.age,
            anxiety_trigger=user_in.anxiety_trigger
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password."""
        user = self.get_user_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
    
    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user profile fields."""
        db_user = self.get_user(db, user_id)
        if not db_user:
            return None
            
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
            
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update_last_login(self, db: Session, user_id: int):
        """Update last login timestamp."""
        db_user = self.get_user(db, user_id)
        if db_user:
            db_user.last_login = datetime.utcnow()
            db.commit()

    def update_password(self, db: Session, user_id: int, new_password: str):
        """Update user password."""
        db_user = self.get_user(db, user_id)
        if db_user:
            db_user.password_hash = hash_password(new_password)
            db.commit()
            
    def delete_user(self, db: Session, user_id: int):
        """Perform soft-delete by deactivating user."""
        db_user = self.get_user(db, user_id)
        if db_user:
            db_user.is_active = False
            db.commit()
