"""
Notes API
API endpoints for note processing and analysis
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
from app.services.note_service import NoteService
import logging

logger = logging.getLogger(__name__)

notes_bp = Blueprint('notes', __name__)


def get_user_id():
    """Get user ID - use current user if authenticated, otherwise default to 1"""
    if current_user.is_authenticated:
        return current_user.id
    # Default to user_id 1 if no authentication
    return 1


@notes_bp.route('/process-note', methods=['POST'])
def process_note():
    """Process a note with AI analysis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        raw_note_text = data.get('note') or data.get('note_text') or ''
        contact_id = data.get('contact_id')
        
        if not raw_note_text or not raw_note_text.strip():
            return jsonify({"error": "Valid note text is required"}), 400
        
        if not contact_id:
            return jsonify({"error": "Valid contact_id is required"}), 400
        
        try:
            contact_id = int(contact_id)
        except (ValueError, TypeError):
            return jsonify({"error": "contact_id must be a valid integer"}), 400
        
        note_service = NoteService()
        result = note_service.process_note(
            contact_id=contact_id,
            content=raw_note_text.strip(),
            user_id=get_user_id()
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error processing note: {e}", exc_info=True)
        return jsonify({"error": "Failed to process note"}), 500


@notes_bp.route('/contact/<int:contact_id>', methods=['GET'])
def get_notes(contact_id):
    """Get all notes for a contact"""
    try:
        note_service = NoteService()
        result = note_service.get_notes_for_contact(contact_id, get_user_id())
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting notes for contact {contact_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve notes"}), 500

