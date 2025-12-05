"""
Note Models
RawNote: Original notes from user
SynthesizedEntry: AI-extracted categories (one row per category)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from app.utils.database import Base
from datetime import datetime


class RawNote(Base):
    """Raw note model - stores original notes"""
    __tablename__ = 'raw_notes'
    
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(50), default='manual')  # 'manual', 'telegram', 'voice', 'file', 'ui_edit'
    metadata_tags = Column(JSON, nullable=True)  # For audit trail and metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contact = relationship("Contact", back_populates="raw_notes")
    synthesized_entries = relationship("SynthesizedEntry", back_populates="raw_note", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RawNote {self.id} for Contact {self.contact_id}>"


class SynthesizedEntry(Base):
    """Synthesized entry model - one row per category"""
    __tablename__ = 'synthesized_entries'
    
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    raw_note_id = Column(Integer, ForeignKey('raw_notes.id'), nullable=True)
    category = Column(String(100), nullable=False)  # e.g., 'Goals', 'Actionable', 'Social'
    content = Column(Text, nullable=False)  # The extracted content for this category
    confidence_score = Column(Float, default=0.0)  # AI confidence (0.0 to 1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contact = relationship("Contact", back_populates="synthesized_entries")
    raw_note = relationship("RawNote", back_populates="synthesized_entries")
    
    def __repr__(self):
        return f"<SynthesizedEntry {self.category} for Contact {self.contact_id}>"

