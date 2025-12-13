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
    """Handle user login - TEMPORARILY DISABLED"""
    # Login is temporarily disabled
    if request.is_json:
        return jsonify({
            'error': 'Login is temporarily disabled. Please check back later.',
            'status': 'maintenance'
        }), 503
    
    # Return maintenance page for web requests
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login Temporarily Unavailable</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                max-width: 500px;
            }
            h1 { margin-top: 0; }
            p { font-size: 18px; line-height: 1.6; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔒 Login Temporarily Unavailable</h1>
            <p>Login functionality is currently disabled for maintenance.</p>
            <p>Please check back later.</p>
        </div>
    </body>
    </html>
    """, 503


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

