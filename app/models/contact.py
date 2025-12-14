"""
Contact Model
Three-tier contact classification system
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.utils.database import Base
from datetime import datetime


class Contact(Base):
    """Contact model with three-tier classification"""
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    full_name = Column(String(255), nullable=False)
    tier = Column(Integer, default=2, nullable=False)  # 1, 2, or 3
    
    # Telegram fields (for future use)
    telegram_id = Column(String(255), nullable=True)
    telegram_username = Column(String(255), nullable=True)
    telegram_phone = Column(String(255), nullable=True)
    telegram_handle = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    telegram_last_sync = Column(DateTime, nullable=True)
    telegram_metadata = Column(JSON, nullable=True)
    
    # Extensible fields
    custom_fields = Column(JSON, nullable=True)
    
    # ChromaDB collection ID for RAG
    vector_collection_id = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="contacts")
    raw_notes = relationship("RawNote", back_populates="contact", cascade="all, delete-orphan")
    synthesized_entries = relationship("SynthesizedEntry", back_populates="contact", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Contact {self.full_name} (Tier {self.tier})>"


