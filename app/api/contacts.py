"""
Contacts API
API endpoints for contact management
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.services.contact_service import ContactService
from app.utils.database import DatabaseManager
from app.models import Contact, RawNote, SynthesizedEntry
import logging

logger = logging.getLogger(__name__)

contacts_bp = Blueprint('contacts', __name__)


@contacts_bp.route('/', methods=['POST'])
@login_required
def create_contact():
    """Create a new contact"""
    try:
        data = request.get_json()
        if not data or not data.get('full_name'):
            return jsonify({'error': 'Full name is required'}), 400
        
        full_name = data.get('full_name', '').strip()
        tier = data.get('tier', 2)
        
        if not full_name:
            return jsonify({'error': 'Full name cannot be empty'}), 400
        
        if tier not in [1, 2, 3]:
            tier = 2
        
        contact_service = ContactService()
        contact = contact_service.create_contact(
            user_id=current_user.id,
            full_name=full_name,
            tier=tier
        )
        
        # Access attributes before they become detached
        contact_id = contact.id
        contact_name = contact.full_name
        contact_tier = contact.tier
        
        return jsonify({
            'id': contact_id,
            'full_name': contact_name,
            'tier': contact_tier,
            'message': f"Contact '{contact_name}' created successfully"
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating contact: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create contact'}), 500


@contacts_bp.route('/', methods=['GET'])
@login_required
def get_contacts():
    """Get all contacts for current user"""
    try:
        contact_service = ContactService()
        contacts = contact_service.get_all_contacts(current_user.id)
        
        # contacts is already a list of dicts from the service
        return jsonify(contacts), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting contacts: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve contacts'}), 500


@contacts_bp.route('/<int:contact_id>', methods=['GET'])
@login_required
def get_contact(contact_id):
    """Get contact details with categories"""
    try:
        contact_service = ContactService()
        result = contact_service.get_contact_with_categories(contact_id, current_user.id)
        
        if not result:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting contact {contact_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve contact'}), 500


@contacts_bp.route('/<int:contact_id>/logs', methods=['GET'])
@login_required
def get_contact_logs(contact_id):
    """Get audit trail (raw notes and synthesized entries) for a contact"""
    try:
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == current_user.id
            ).first()
            
            if not contact:
                return jsonify({"error": "Contact not found"}), 404
            
            raw_notes = session.query(RawNote).filter(
                RawNote.contact_id == contact_id
            ).order_by(RawNote.created_at.desc()).all()
            
            synthesized_entries = session.query(SynthesizedEntry).filter(
                SynthesizedEntry.contact_id == contact_id
            ).order_by(SynthesizedEntry.created_at.desc()).all()
            
            formatted_notes = []
            for note in raw_notes:
                note_data = {
                    'id': note.id,
                    'content': note.content,
                    'source': note.source,
                    'created_at': note.created_at.isoformat() if note.created_at else None,
                    'metadata': note.metadata_tags
                }
                
                associated_entries = [e for e in synthesized_entries if e.raw_note_id == note.id]
                note_data['synthesized_entries'] = [{
                    'category': e.category,
                    'content': e.content,
                    'confidence': e.confidence_score,
                    'created_at': e.created_at.isoformat() if e.created_at else None
                } for e in associated_entries]
                
                formatted_notes.append(note_data)
            
            return jsonify({
                'contact_id': contact_id,
                'contact_name': contact.full_name,
                'raw_notes': formatted_notes,
                'total_notes': len(formatted_notes)
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"Error getting logs for contact {contact_id}: {e}", exc_info=True)
        return jsonify({"error": f"Failed to retrieve logs: {str(e)}"}), 500


@contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    """Delete a contact and all associated data (cascade delete)"""
    try:
        contact_service = ContactService()
        success = contact_service.delete_contact(contact_id, current_user.id)
        
        if success:
            return jsonify({'message': 'Contact deleted successfully'}), 200
        else:
            return jsonify({'error': 'Contact not found'}), 404
            
    except Exception as e:
        current_app.logger.error(f"Error deleting contact {contact_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete contact'}), 500

