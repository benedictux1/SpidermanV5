"""
Contact Service
Business logic for contact management
"""

import logging
from typing import Optional, List, Dict, Any
from app.models import Contact, SynthesizedEntry
from app.utils.database import DatabaseManager
import uuid

logger = logging.getLogger(__name__)


class ContactService:
    """Service for contact management operations"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def create_contact(self, user_id: int, full_name: str, tier: int = 2) -> Contact:
        """Create a new contact"""
        with self.db_manager.get_session() as session:
            vector_collection_id = f"contact_{uuid.uuid4().hex[:8]}"
            contact = Contact(
                user_id=user_id,
                full_name=full_name.strip(),
                tier=tier,
                vector_collection_id=vector_collection_id
            )
            session.add(contact)
            session.flush()
            # Get the ID before session closes
            contact_id = contact.id
            contact_name = contact.full_name
            contact_tier = contact.tier
            # Expunge to detach from session (allows access after context)
            session.expunge(contact)
            logger.info(f"Created contact {contact_id}: {contact_name}")
            # Return the contact object (now detached, but we have the values)
            return contact
    
    def get_contact(self, contact_id: int, user_id: int) -> Optional[Contact]:
        """Get contact by ID (with ownership check)"""
        with self.db_manager.get_session() as session:
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == user_id
            ).first()
            return contact
    
    def get_all_contacts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all contacts for a user"""
        with self.db_manager.get_session() as session:
            contacts = session.query(Contact).filter(
                Contact.user_id == user_id
            ).order_by(Contact.tier.asc(), Contact.full_name.asc()).all()
            
            # Extract data while session is still active
            result = []
            for contact in contacts:
                result.append({
                    'id': contact.id,
                    'full_name': contact.full_name,
                    'tier': contact.tier,
                    'created_at': contact.created_at.isoformat() if contact.created_at else None
                })
            return result
    
    def get_contact_with_categories(self, contact_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get contact with all categories grouped"""
        with self.db_manager.get_session() as session:
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == user_id
            ).first()
            
            if not contact:
                return None
            
            entries = session.query(SynthesizedEntry).filter(
                SynthesizedEntry.contact_id == contact_id
            ).order_by(SynthesizedEntry.category.asc(), SynthesizedEntry.created_at.desc()).all()
            
            categorized_data = {}
            for entry in entries:
                if entry.category not in categorized_data:
                    categorized_data[entry.category] = []
                categorized_data[entry.category].append({
                    'id': entry.id,  # Include entry ID for editing
                    'content': entry.content,
                    'confidence': entry.confidence_score,
                    'created_at': entry.created_at.isoformat() if entry.created_at else None
                })
            
            return {
                'id': contact.id,
                'full_name': contact.full_name,
                'tier': contact.tier,
                'created_at': contact.created_at.isoformat() if contact.created_at else None,
                'categorized_data': categorized_data
            }
    
    def delete_contact(self, contact_id: int, user_id: int) -> bool:
        """Delete a contact (cascade handled by SQLAlchemy relationships)
        
        Args:
            contact_id: ID of contact to delete
            user_id: ID of user (for ownership verification)
            
        Returns:
            bool: True if deleted successfully, False if contact not found or not owned by user
        """
        try:
            with self.db_manager.get_session() as session:
                # Verify ownership
                contact = session.query(Contact).filter(
                    Contact.id == contact_id,
                    Contact.user_id == user_id
                ).first()
                
                if not contact:
                    logger.warning(f"Delete attempt failed: Contact {contact_id} not found or not owned by user {user_id}")
                    return False
                
                contact_name = contact.full_name
                vector_collection_id = contact.vector_collection_id
                
                # Delete (cascade deletes notes, entries, tags)
                session.delete(contact)
                session.commit()
                logger.info(f"Deleted contact {contact_id}: {contact_name}")
                
                # Clean up ChromaDB collection (non-blocking)
                try:
                    from app.utils.chromadb_client import delete_contact_collection
                    delete_contact_collection(contact_id)
                except Exception as e:
                    logger.error(f"ChromaDB collection cleanup failed for contact {contact_id}: {e}")
                    # Continue - database deletion succeeded
                
                return True
                
        except Exception as e:
            logger.error(f"Error deleting contact {contact_id}: {e}", exc_info=True)
            return False

