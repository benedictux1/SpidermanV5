"""
Note Service
Business logic for note processing with AI analysis and RAG
"""

import logging
from typing import Dict, Any
from datetime import datetime
from app.models import Contact, RawNote, SynthesizedEntry
from app.services.ai_service import AIService
from app.utils.database import DatabaseManager
from app.utils.chromadb_client import store_note_in_chromadb, get_relevant_history

logger = logging.getLogger(__name__)


class NoteService:
    """Service for note processing and AI analysis"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.ai_service = AIService()
    
    def process_note(self, contact_id: int, content: str, user_id: int) -> Dict[str, Any]:
        """Process a note with AI analysis and RAG context"""
        with self.db_manager.get_session() as session:
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == user_id
            ).first()
            
            if not contact:
                raise ValueError("Contact not found")
            
            raw_note = RawNote(
                contact_id=contact_id,
                content=content.strip(),
                source='manual',
                created_at=datetime.utcnow()
            )
            session.add(raw_note)
            session.flush()
            
            try:
                store_note_in_chromadb(contact_id, content, raw_note.id)
            except Exception as e:
                logger.warning(f"Failed to store note in ChromaDB: {e}")
            
            retrieved_history = "No relevant history found."
            try:
                query_text = " ".join(content.split()[:30])
                retrieved_history = get_relevant_history(contact_id, query_text, n_results=3)
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")
            
            try:
                analysis_result = self.ai_service.analyze_note(
                    content=content,
                    contact_name=contact.full_name,
                    context=retrieved_history
                )
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                analysis_result = self.ai_service._fallback_analysis(content, contact.full_name)
            
            synthesis_results = []
            categories = analysis_result.get('categories', {})
            
            # If AI returned no categories, use fallback
            if not categories or len(categories) == 0:
                logger.warning(f"No categories extracted by AI, using fallback analysis")
                analysis_result = self.ai_service._fallback_analysis(content, contact.full_name)
                categories = analysis_result.get('categories', {})
            
            # Post-process: Remove "Others" if any other category exists (safety check)
            if 'Others' in categories:
                other_categories = [k for k in categories.keys() if k != 'Others']
                if other_categories:
                    logger.info(f"Removing 'Others' category because other categories exist: {other_categories}")
                    del categories['Others']
            
            for category, data in categories.items():
                content_text = data.get('content', '')
                confidence = float(data.get('confidence', 0.0))
                
                # Lower threshold to 5 characters to catch short notes like "likes fish"
                if content_text and len(content_text.strip()) > 5:
                    entry = SynthesizedEntry(
                        contact_id=contact_id,
                        raw_note_id=raw_note.id,
                        category=category,
                        content=content_text.strip(),
                        confidence_score=confidence,
                        created_at=datetime.utcnow()
                    )
                    session.add(entry)
                    synthesis_results.append({
                        'category': category,
                        'content': content_text,
                        'confidence': confidence
                    })
            
            session.commit()
            logger.info(f"Processed note {raw_note.id} for contact {contact_id}: {len(synthesis_results)} categories")
            
            return {
                'success': True,
                'raw_note_id': raw_note.id,
                'contact_id': contact_id,
                'contact_name': contact.full_name,
                'synthesis': synthesis_results,
                'categories_count': len(synthesis_results),
                'rag_context_used': retrieved_history != "No relevant history found."
            }
    
    def get_notes_for_contact(self, contact_id: int, user_id: int) -> Dict[str, Any]:
        """Get all notes and synthesized entries for a contact"""
        with self.db_manager.get_session() as session:
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == user_id
            ).first()
            
            if not contact:
                raise ValueError("Contact not found")
            
            raw_notes = session.query(RawNote).filter(
                RawNote.contact_id == contact_id
            ).order_by(RawNote.created_at.desc()).all()
            
            synthesized_entries = session.query(SynthesizedEntry).filter(
                SynthesizedEntry.contact_id == contact_id
            ).order_by(SynthesizedEntry.created_at.desc()).all()
            
            return {
                'contact_id': contact_id,
                'contact_name': contact.full_name,
                'raw_notes': [{
                    'id': n.id,
                    'content': n.content,
                    'source': n.source,
                    'created_at': n.created_at.isoformat() if n.created_at else None
                } for n in raw_notes],
                'synthesized_entries': [{
                    'id': e.id,
                    'raw_note_id': e.raw_note_id,
                    'category': e.category,
                    'content': e.content,
                    'confidence': e.confidence_score,
                    'created_at': e.created_at.isoformat() if e.created_at else None
                } for e in synthesized_entries]
            }

