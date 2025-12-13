"""
Authentication API
Simple authentication system with Flask-Login
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from app.utils.database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login - DISABLED, returns success for compatibility"""
    # Login is disabled - return success to allow app to work
    if request.is_json:
        return jsonify({
            'success': True,
            'message': 'Login disabled - app is open access',
            'authenticated': True
        }), 200
    
    # Redirect to main app for web requests
    from flask import redirect, url_for
    return redirect(url_for('index'))


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    if request.is_json:
        return jsonify({'success': True, 'message': 'Logout successful'}), 200
    return redirect(url_for('auth.login'))


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'role': getattr(current_user, 'role', 'user')
            }
        }), 200
    else:
        return jsonify({'authenticated': False}), 401

