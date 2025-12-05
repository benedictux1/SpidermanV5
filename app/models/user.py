"""
User Model
Simple user model for authentication
"""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.utils.database import Base
from datetime import datetime


class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='user', nullable=False)  # 'admin' or 'user'
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    contacts = relationship("Contact", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"

