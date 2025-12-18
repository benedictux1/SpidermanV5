"""
Contacts API
API endpoints for contact management
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
from app.services.contact_service import ContactService
from app.utils.database import DatabaseManager
from app.models import Contact, RawNote, SynthesizedEntry
import logging

logger = logging.getLogger(__name__)

contacts_bp = Blueprint('contacts', __name__)

# Cache for default user ID to avoid repeated database queries
_default_user_id = None


def get_user_id():
    """Get user ID - use current user if authenticated, otherwise get or create default user"""
    global _default_user_id
    
    if current_user.is_authenticated:
        return current_user.id
    
    # Use cached user ID if available
    if _default_user_id is not None:
        logger.debug(f"Using cached default user_id={_default_user_id}")
        return _default_user_id
    
    # For guest mode: get first user or create one
    db_manager = DatabaseManager()
    try:
        # Ensure tables exist first (fallback if startup initialization failed)
        try:
            from sqlalchemy import inspect
            inspector = inspect(db_manager.engine)
            existing_tables = inspector.get_table_names()
            if 'users' not in existing_tables:
                logger.warning("Users table doesn't exist! Creating all tables now...")
                # Import models first
                from app.models import User, Contact, RawNote, SynthesizedEntry
                db_manager.create_all_tables()
                logger.info("✅ Tables created on-demand")
        except Exception as table_check_error:
            logger.warning(f"Could not check/create tables: {table_check_error}")
        
        with db_manager.get_session() as session:
            from app.models import User
            from werkzeug.security import generate_password_hash
            
            # Try to get any existing user first
            user = session.query(User).first()
            
            if not user:
                # No users exist - create a default guest user
                logger.info("No users found, creating default guest user...")
                try:
                    # Try to create with username 'guest'
                    guest_user = User(
                        username='guest',
                        password_hash=generate_password_hash('guest'),
                        role='user'
                    )
                    session.add(guest_user)
                    # Flush to get the ID, but don't commit yet (context manager will commit)
                    session.flush()
                    user_id = guest_user.id
                    logger.info(f"✅ Created default guest user with id={user_id}")
                    # Cache it
                    _default_user_id = user_id
                    return user_id
                except Exception as create_error:
                    # If 'guest' username already exists, try a different one
                    logger.warning(f"Could not create 'guest' user: {create_error}")
                    session.rollback()
                    # Try with a unique username
                    import time
                    unique_username = f'guest_{int(time.time())}'
                    guest_user = User(
                        username=unique_username,
                        password_hash=generate_password_hash('guest'),
                        role='user'
                    )
                    session.add(guest_user)
                    session.flush()
                    user_id = guest_user.id
                    logger.info(f"✅ Created default guest user with id={user_id} (username={unique_username})")
                    _default_user_id = user_id
                    return user_id
            else:
                # User exists, use its ID
                logger.info(f"Using existing user with id={user.id}, username={user.username}")
                _default_user_id = user.id
                return user.id
                
    except Exception as e:
        logger.error(f"Error getting/creating default user: {e}", exc_info=True)
        # Last resort: try to get any user one more time
        try:
            with db_manager.get_session() as session:
                from app.models import User
                any_user = session.query(User).first()
                if any_user:
                    logger.warning(f"Fallback: Using user id={any_user.id}")
                    _default_user_id = any_user.id
                    return any_user.id
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}", exc_info=True)
        
        # If all else fails, raise an error with helpful message
        raise Exception(f"Could not get or create a user. Database error: {e}")


@contacts_bp.route('/', methods=['POST'])
def create_contact():
    """Create a new contact"""
    try:
        data = request.get_json()
        logger.info(f"Create contact request: {data}")
        
        if not data or not data.get('full_name'):
            return jsonify({'error': 'Full name is required'}), 400
        
        full_name = data.get('full_name', '').strip()
        tier = data.get('tier', 2)
        
        if not full_name:
            return jsonify({'error': 'Full name cannot be empty'}), 400
        
        if tier not in [1, 2, 3]:
            tier = 2
        
        # Get user_id - this will create a user if needed
        try:
            user_id = get_user_id()
            logger.info(f"Using user_id={user_id} for contact creation")
        except Exception as user_error:
            current_app.logger.error(f"Failed to get user_id: {user_error}", exc_info=True)
            return jsonify({
                'error': 'Database error: Could not get or create a user account',
                'details': str(user_error)
            }), 500
        
        # Verify user exists before creating contact
        try:
            db_manager = DatabaseManager()
            with db_manager.get_session() as session:
                from app.models import User
                verify_user = session.query(User).filter(User.id == user_id).first()
                if not verify_user:
                    logger.error(f"User {user_id} does not exist in database!")
                    return jsonify({
                        'error': f'Database error: User {user_id} does not exist',
                        'details': 'The user account was not found. Please try again.'
                    }), 500
                logger.info(f"Verified user {user_id} exists (username={verify_user.username})")
        except Exception as verify_error:
            logger.error(f"Error verifying user: {verify_error}", exc_info=True)
            return jsonify({
                'error': 'Database error: Could not verify user account',
                'details': str(verify_error)
            }), 500
        
        # Create the contact
        contact_service = ContactService()
        contact = contact_service.create_contact(
            user_id=user_id,
            full_name=full_name,
            tier=tier
        )
        
        # Access attributes before they become detached
        contact_id = contact.id
        contact_name = contact.full_name
        contact_tier = contact.tier
        
        logger.info(f"✅ Successfully created contact id={contact_id}, name={contact_name}, tier={contact_tier}")
        
        return jsonify({
            'id': contact_id,
            'full_name': contact_name,
            'tier': contact_tier,
            'message': f"Contact '{contact_name}' created successfully"
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating contact: {e}", exc_info=True)
        import traceback
        error_traceback = traceback.format_exc()
        current_app.logger.error(f"Full traceback: {error_traceback}")
        
        # Return more detailed error for debugging
        error_message = str(e)
        if 'foreign key constraint' in error_message.lower() or 'user_id' in error_message.lower():
            return jsonify({
                'error': 'Database error: User does not exist. Please ensure a default user is created.',
                'details': error_message,
                'traceback': error_traceback if current_app.config.get('DEBUG') else None
            }), 500
        return jsonify({
            'error': 'Failed to create contact',
            'details': error_message,
            'traceback': error_traceback if current_app.config.get('DEBUG') else None
        }), 500


@contacts_bp.route('/', methods=['GET'])
def get_contacts():
    """Get all contacts for current user"""
    try:
        user_id = get_user_id()
        logger.debug(f"Getting contacts for user_id={user_id}")
        contact_service = ContactService()
        contacts = contact_service.get_all_contacts(user_id)
        logger.debug(f"Found {len(contacts)} contacts")
        return jsonify(contacts), 200
    except Exception as e:
        current_app.logger.error(f"Error getting contacts: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve contacts', 'details': str(e)}), 500


@contacts_bp.route('/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get contact details with categories"""
    try:
        user_id = get_user_id()
        contact_service = ContactService()
        result = contact_service.get_contact_with_categories(contact_id, user_id)
        
        if not result:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error getting contact {contact_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve contact', 'details': str(e)}), 500


@contacts_bp.route('/<int:contact_id>/logs', methods=['GET'])
def get_contact_logs(contact_id):
    """Get audit trail (raw notes and synthesized entries) for a contact"""
    try:
        user_id = get_user_id()
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == user_id
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
def delete_contact(contact_id):
    """Delete a contact and all associated data (cascade delete)"""
    try:
        user_id = get_user_id()
        contact_service = ContactService()
        success = contact_service.delete_contact(contact_id, user_id)
        
        if success:
            return jsonify({'message': 'Contact deleted successfully'}), 200
        else:
            return jsonify({'error': 'Contact not found'}), 404
            
    except Exception as e:
        current_app.logger.error(f"Error deleting contact {contact_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete contact', 'details': str(e)}), 500


@contacts_bp.route('/<int:contact_id>/categories', methods=['PUT'])
def update_categories(contact_id):
    """Update categories for a contact (bulk edit)"""
    try:
        from datetime import datetime
        
        user_id = get_user_id()
        data = request.get_json()
        
        if not data or 'updates' not in data:
            return jsonify({'error': 'Updates array is required'}), 400
        
        updates = data.get('updates', [])
        if not isinstance(updates, list):
            return jsonify({'error': 'Updates must be an array'}), 400
        
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            # Verify contact ownership
            contact = session.query(Contact).filter(
                Contact.id == contact_id,
                Contact.user_id == user_id
            ).first()
            
            if not contact:
                return jsonify({'error': 'Contact not found'}), 404
            
            updated_categories = []
            categories_changed = []
            detailed_changes = []  # Store detailed change information
            
            # Helper function to generate diff-like change description
            def generate_change_description(category_name, old_content, new_content, action):
                """Generate a detailed description of what changed"""
                old_content = (old_content or '').strip()
                new_content = (new_content or '').strip()
                
                if action == 'deleted':
                    return f"**{category_name}** - Deleted: {old_content[:100]}{'...' if len(old_content) > 100 else ''}"
                elif action == 'added':
                    return f"**{category_name}** - Added: {new_content[:100]}{'...' if len(new_content) > 100 else ''}"
                elif action == 'updated':
                    # Show what was removed and what was added
                    old_lines = set(old_content.split('\n')) if old_content else set()
                    new_lines = set(new_content.split('\n')) if new_content else set()
                    
                    removed = old_lines - new_lines
                    added = new_lines - old_lines
                    
                    parts = []
                    if removed:
                        removed_text = ' | '.join(list(removed)[:3])  # Show first 3 removed items
                        if len(removed) > 3:
                            removed_text += f" (+{len(removed) - 3} more)"
                        parts.append(f"Removed: {removed_text}")
                    
                    if added:
                        added_text = ' | '.join(list(added)[:3])  # Show first 3 added items
                        if len(added) > 3:
                            added_text += f" (+{len(added) - 3} more)"
                        parts.append(f"Added: {added_text}")
                    
                    if not parts:
                        # Content changed but hard to diff (maybe reordered or reformatted)
                        return f"**{category_name}** - Updated (content changed)"
                    
                    return f"**{category_name}** - {', '.join(parts)}"
                else:
                    return f"**{category_name}** - {action}"
            
            # Process each update
            for update in updates:
                category_name = update.get('category', '').strip()
                content = update.get('content', '').strip()
                entry_id = update.get('entry_id')
                # Convert entry_id to int if it's a string number, or None if empty/None
                if entry_id is not None:
                    try:
                        entry_id = int(entry_id) if entry_id else None
                    except (ValueError, TypeError):
                        entry_id = None
                
                if not category_name:
                    continue
                
                if not content:
                    # If content is empty, delete all entries for this category
                    old_content = None
                    if entry_id:
                        # Delete specific entry
                        entry = session.query(SynthesizedEntry).filter(
                            SynthesizedEntry.id == entry_id,
                            SynthesizedEntry.contact_id == contact_id
                        ).first()
                        if entry:
                            old_content = entry.content
                            session.delete(entry)
                            change_desc = generate_change_description(category_name, old_content, '', 'deleted')
                            categories_changed.append(category_name)
                            detailed_changes.append(change_desc)
                    else:
                        # Delete all entries for this category
                        entries_to_delete = session.query(SynthesizedEntry).filter(
                            SynthesizedEntry.contact_id == contact_id,
                            SynthesizedEntry.category == category_name
                        ).all()
                        if entries_to_delete:
                            # Get content from first entry for audit trail
                            old_content = entries_to_delete[0].content if entries_to_delete else None
                            for entry in entries_to_delete:
                                session.delete(entry)
                            change_desc = generate_change_description(category_name, old_content, '', 'deleted')
                            categories_changed.append(category_name)
                            detailed_changes.append(change_desc)
                    continue
                
                if entry_id:
                    # Update existing entry
                    entry = session.query(SynthesizedEntry).filter(
                        SynthesizedEntry.id == entry_id,
                        SynthesizedEntry.contact_id == contact_id
                    ).first()
                    
                    if entry:
                        old_content = entry.content
                        
                        # Delete other entries for this category (if multiple exist)
                        other_entries = session.query(SynthesizedEntry).filter(
                            SynthesizedEntry.contact_id == contact_id,
                            SynthesizedEntry.category == category_name,
                            SynthesizedEntry.id != entry_id
                        ).all()
                        for other_entry in other_entries:
                            session.delete(other_entry)
                        
                        # Check if content actually changed
                        if entry.content != content:
                            entry.content = content
                            entry.created_at = datetime.utcnow()  # Update timestamp
                            change_desc = generate_change_description(category_name, old_content, content, 'updated')
                            categories_changed.append(category_name)
                            detailed_changes.append(change_desc)
                            updated_categories.append({
                                'id': entry.id,
                                'category': entry.category,
                                'content': entry.content,
                                'confidence': entry.confidence_score
                            })
                        else:
                            # Content didn't change, but still return it
                            updated_categories.append({
                                'id': entry.id,
                                'category': entry.category,
                                'content': entry.content,
                                'confidence': entry.confidence_score
                            })
                else:
                    # Check if category already exists (might have been created without entry_id)
                    existing_entry = session.query(SynthesizedEntry).filter(
                        SynthesizedEntry.contact_id == contact_id,
                        SynthesizedEntry.category == category_name
                    ).first()
                    
                    if existing_entry:
                        old_content = existing_entry.content
                        # Update existing entry instead of creating new one
                        existing_entry.content = content
                        existing_entry.created_at = datetime.utcnow()
                        change_desc = generate_change_description(category_name, old_content, content, 'updated')
                        categories_changed.append(category_name)
                        detailed_changes.append(change_desc)
                        updated_categories.append({
                            'id': existing_entry.id,
                            'category': existing_entry.category,
                            'content': existing_entry.content,
                            'confidence': existing_entry.confidence_score
                        })
                    else:
                        # Create new entry
                        new_entry = SynthesizedEntry(
                            contact_id=contact_id,
                            raw_note_id=None,  # Manual edit, no raw note
                            category=category_name,
                            content=content,
                            confidence_score=1.0,  # Manual edits have full confidence
                            created_at=datetime.utcnow()
                        )
                        session.add(new_entry)
                        session.flush()
                        change_desc = generate_change_description(category_name, '', content, 'added')
                        categories_changed.append(category_name)
                        detailed_changes.append(change_desc)
                        updated_categories.append({
                            'id': new_entry.id,
                            'category': new_entry.category,
                            'content': new_entry.content,
                            'confidence': new_entry.confidence_score
                        })
            
            # Create audit trail entry (RawNote) for manual edit with detailed changes
            if categories_changed:
                # Create detailed summary
                summary_parts = [f"Manual edit: {len(categories_changed)} categor{'y' if len(categories_changed) == 1 else 'ies'} changed"]
                summary_parts.extend(detailed_changes)
                edit_summary = '\n\n'.join(summary_parts)
                
                raw_note = RawNote(
                    contact_id=contact_id,
                    content=edit_summary,
                    source='manual_edit',
                    created_at=datetime.utcnow()
                )
                session.add(raw_note)
                session.commit()
                
                logger.info(f"Updated {len(categories_changed)} categories for contact {contact_id}")
                
                return jsonify({
                    'success': True,
                    'message': f'Updated {len(categories_changed)} categories',
                    'updated_categories': updated_categories,
                    'changes': categories_changed
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'message': 'No changes made',
                    'updated_categories': []
                }), 200
            
    except Exception as e:
        current_app.logger.error(f"Error updating categories for contact {contact_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update categories', 'details': str(e)}), 500


@contacts_bp.route('/search', methods=['GET'])
def search_contacts():
    """Search contacts by name, category content, or audit trail"""
    try:
        from sqlalchemy import or_, func
        
        user_id = get_user_id()
        query = request.args.get('q', '').strip()
        
        if not query or len(query) < 1:
            return jsonify({'results': [], 'query': query}), 200
        
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            # Search pattern (case-insensitive)
            search_pattern = f'%{query}%'
            
            # 1. Search by contact name (highest priority)
            name_matches = session.query(Contact).filter(
                Contact.user_id == user_id,
                Contact.full_name.ilike(search_pattern)
            ).all()
            
            # 2. Search in category content
            category_matches = session.query(Contact).join(
                SynthesizedEntry, Contact.id == SynthesizedEntry.contact_id
            ).filter(
                Contact.user_id == user_id,
                SynthesizedEntry.content.ilike(search_pattern)
            ).distinct().all()
            
            # 3. Search in audit trail (raw notes)
            note_matches = session.query(Contact).join(
                RawNote, Contact.id == RawNote.contact_id
            ).filter(
                Contact.user_id == user_id,
                RawNote.content.ilike(search_pattern)
            ).distinct().all()
            
            # Combine all matches and build results with match context
            contact_results = {}
            
            # Process name matches (score: 100)
            for contact in name_matches:
                if contact.id not in contact_results:
                    contact_results[contact.id] = {
                        'contact': contact,
                        'matches': [],
                        'score': 0
                    }
                contact_results[contact.id]['matches'].append({
                    'type': 'name',
                    'category': None,
                    'snippet': contact.full_name
                })
                contact_results[contact.id]['score'] += 100
            
            # Process category matches (score: 50)
            for contact in category_matches:
                if contact.id not in contact_results:
                    contact_results[contact.id] = {
                        'contact': contact,
                        'matches': [],
                        'score': 0
                    }
                
                # Get matching entries for this contact
                matching_entries = session.query(SynthesizedEntry).filter(
                    SynthesizedEntry.contact_id == contact.id,
                    SynthesizedEntry.content.ilike(search_pattern)
                ).all()
                
                for entry in matching_entries:
                    # Create snippet (50 chars before and after match)
                    content = entry.content
                    match_pos = content.lower().find(query.lower())
                    if match_pos >= 0:
                        start = max(0, match_pos - 30)
                        end = min(len(content), match_pos + len(query) + 30)
                        snippet = content[start:end]
                        if start > 0:
                            snippet = '...' + snippet
                        if end < len(content):
                            snippet = snippet + '...'
                    else:
                        snippet = content[:80] + '...' if len(content) > 80 else content
                    
                    contact_results[contact.id]['matches'].append({
                        'type': 'category',
                        'category': entry.category,
                        'snippet': snippet
                    })
                    contact_results[contact.id]['score'] += 50
            
            # Process audit trail matches (score: 25)
            for contact in note_matches:
                if contact.id not in contact_results:
                    contact_results[contact.id] = {
                        'contact': contact,
                        'matches': [],
                        'score': 0
                    }
                
                # Get matching notes for this contact
                matching_notes = session.query(RawNote).filter(
                    RawNote.contact_id == contact.id,
                    RawNote.content.ilike(search_pattern)
                ).all()
                
                for note in matching_notes:
                    # Create snippet
                    content = note.content
                    match_pos = content.lower().find(query.lower())
                    if match_pos >= 0:
                        start = max(0, match_pos - 30)
                        end = min(len(content), match_pos + len(query) + 30)
                        snippet = content[start:end]
                        if start > 0:
                            snippet = '...' + snippet
                        if end < len(content):
                            snippet = snippet + '...'
                    else:
                        snippet = content[:80] + '...' if len(content) > 80 else content
                    
                    contact_results[contact.id]['matches'].append({
                        'type': 'note',
                        'category': None,
                        'snippet': snippet,
                        'source': note.source
                    })
                    contact_results[contact.id]['score'] += 25
            
            # Sort by score (descending), then by name
            sorted_results = sorted(
                contact_results.values(),
                key=lambda x: (-x['score'], x['contact'].full_name.lower())
            )
            
            # Format results
            results = []
            for result in sorted_results:
                contact = result['contact']
                results.append({
                    'id': contact.id,
                    'full_name': contact.full_name,
                    'tier': contact.tier,
                    'matches': result['matches'],
                    'score': result['score']
                })
            
            logger.info(f"Search '{query}' found {len(results)} contacts")
            return jsonify({
                'results': results,
                'query': query,
                'count': len(results)
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"Error searching contacts: {e}", exc_info=True)
        return jsonify({'error': 'Failed to search contacts', 'details': str(e)}), 500


@contacts_bp.route('/export/csv', methods=['GET'])
def export_contacts_csv():
    """Export all contacts, categories, and audit trail to CSV"""
    try:
        import csv
        import io
        from datetime import datetime
        from flask import Response
        
        user_id = get_user_id()
        db_manager = DatabaseManager()
        
        with db_manager.get_session() as session:
            # Get all contacts for the user
            contacts = session.query(Contact).filter(
                Contact.user_id == user_id
            ).order_by(Contact.full_name.asc()).all()
            
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header row
            writer.writerow([
                'Contact ID',
                'Contact Name',
                'Tier',
                'Created At',
                'Category',
                'Category Content',
                'Confidence',
                'Raw Note ID',
                'Raw Note Content',
                'Raw Note Source',
                'Raw Note Created At'
            ])
            
            # Write data rows
            for contact in contacts:
                # Get all synthesized entries (categories) for this contact
                entries = session.query(SynthesizedEntry).filter(
                    SynthesizedEntry.contact_id == contact.id
                ).order_by(SynthesizedEntry.category.asc(), SynthesizedEntry.created_at.desc()).all()
                
                # Get all raw notes (audit trail) for this contact
                raw_notes = session.query(RawNote).filter(
                    RawNote.contact_id == contact.id
                ).order_by(RawNote.created_at.desc()).all()
                
                # Create a mapping of raw_note_id to note content for reference
                note_map = {note.id: note for note in raw_notes}
                
                # If contact has categories, write one row per category
                if entries:
                    for entry in entries:
                        raw_note = note_map.get(entry.raw_note_id)
                        writer.writerow([
                            contact.id,
                            contact.full_name,
                            contact.tier,
                            contact.created_at.isoformat() if contact.created_at else '',
                            entry.category,
                            entry.content,
                            entry.confidence_score,
                            entry.raw_note_id if entry.raw_note_id else '',
                            raw_note.content if raw_note else '',
                            raw_note.source if raw_note else '',
                            raw_note.created_at.isoformat() if raw_note and raw_note.created_at else ''
                        ])
                else:
                    # If no categories, still write contact info with empty category fields
                    writer.writerow([
                        contact.id,
                        contact.full_name,
                        contact.tier,
                        contact.created_at.isoformat() if contact.created_at else '',
                        '',  # No category
                        '',  # No category content
                        '',  # No confidence
                        '',  # No raw note ID
                        '',  # No raw note content
                        '',  # No raw note source
                        ''   # No raw note created at
                    ])
                
                # Write raw notes that don't have synthesized entries (if any)
                entries_note_ids = {entry.raw_note_id for entry in entries if entry.raw_note_id}
                for note in raw_notes:
                    if note.id not in entries_note_ids:
                        # This note doesn't have categories yet
                        writer.writerow([
                            contact.id,
                            contact.full_name,
                            contact.tier,
                            contact.created_at.isoformat() if contact.created_at else '',
                            '',  # No category
                            '',  # No category content
                            '',  # No confidence
                            note.id,
                            note.content,
                            note.source,
                            note.created_at.isoformat() if note.created_at else ''
                        ])
            
            # Get CSV content
            csv_content = output.getvalue()
            output.close()
            
            # Create response with CSV
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f'kith_platform_export_{timestamp}.csv'
            
            response = Response(
                csv_content,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename={filename}',
                    'Content-Type': 'text/csv; charset=utf-8'
                }
            )
            
            logger.info(f"CSV export completed: {len(contacts)} contacts exported")
            return response
            
    except Exception as e:
        current_app.logger.error(f"Error exporting CSV: {e}", exc_info=True)
        return jsonify({'error': 'Failed to export CSV', 'details': str(e)}), 500
