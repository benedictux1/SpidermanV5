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
    """Handle user login"""
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return render_template('login.html')
    
    try:
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            if request.is_json:
                return jsonify({'error': 'Username and password are required'}), 400
            return render_template('login.html', error='Username and password are required')
        
        db_manager = DatabaseManager()
        with db_manager.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            
            if user and check_password_hash(user.password_hash, password):
                from flask_login import UserMixin
                class AuthUser(UserMixin):
                    def __init__(self, user):
                        self.id = user.id
                        self.username = user.username
                        self.role = user.role
                
                auth_user = AuthUser(user)
                login_user(auth_user, remember=True)
                
                if request.is_json:
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'role': user.role
                        }
                    }), 200
                else:
                    return redirect(url_for('index'))
            else:
                logger.warning(f"Invalid login attempt for user: {username}")
                if request.is_json:
                    return jsonify({'error': 'Invalid credentials'}), 401
                return render_template('login.html', error='Invalid credentials')
                
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        if request.is_json:
            return jsonify({'error': 'Login failed'}), 500
        return render_template('login.html', error='Login failed')


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

