"""
Kith Platform - Flask Application Factory
Main application initialization with blueprints and configuration
"""

from flask import Flask
from flask_login import LoginManager
import os
import logging
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'

# Configure session lifetime
login_manager.remember_cookie_duration = timedelta(days=7)


def create_app(config_name=None):
    """Create and configure Flask application"""
    # Get the project root directory (parent of app/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_folder = os.path.join(project_root, 'templates')
    static_folder = os.path.join(project_root, 'static')
    
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    
    if config_name == 'production':
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', os.urandom(32).hex())
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    else:
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
        app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
        app.config['SESSION_COOKIE_SECURE'] = False
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Render.com provides postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Development: use SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kith_platform.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if config_name == 'production' else logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Auto-initialize database tables on startup (safe - only creates if they don't exist)
    # This runs when the app is created, before any requests
    with app.app_context():
        try:
            from app.utils.database import DatabaseManager
            from sqlalchemy import inspect
            
            db_manager = DatabaseManager()
            inspector = inspect(db_manager.engine)
            existing_tables = inspector.get_table_names()
            
            if not existing_tables:
                # No tables exist, create them
                db_manager.create_all_tables()
                app.logger.info("✅ Database tables created on startup")
            else:
                app.logger.info(f"✅ Database tables already exist: {len(existing_tables)} tables found")
        except Exception as e:
            # Log warning but don't fail - tables might already exist or DB might not be ready yet
            app.logger.warning(f"Database initialization check: {e} (this is OK if tables already exist)")
    
    # Register blueprints
    from app.api import contacts, notes, auth
    app.register_blueprint(auth.auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contacts.contacts_bp, url_prefix='/api/contacts')
    app.register_blueprint(notes.notes_bp, url_prefix='/api/notes')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Basic health check endpoint"""
        try:
            from app.utils.database import DatabaseManager
            from sqlalchemy import text
            
            db_manager = DatabaseManager()
            with db_manager.get_session() as session:
                session.execute(text("SELECT 1"))
            
            return {
                'status': 'healthy',
                'timestamp': __import__('datetime').datetime.utcnow().isoformat()
            }, 200
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': __import__('datetime').datetime.utcnow().isoformat()
            }, 503
    
    # Login route (redirect to auth blueprint)
    @app.route('/login')
    def login_route():
        """Login page route"""
        from flask import render_template, redirect, url_for
        from flask_login import current_user
        # If already logged in, redirect to main app
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return render_template('login.html')
    
    # Main route - serve SPA
    @app.route('/')
    def index():
        """Serve main SPA"""
        from flask import render_template
        return render_template('index.html')
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        try:
            from app.models import User
            from app.utils.database import DatabaseManager
            
            db_manager = DatabaseManager()
            with db_manager.get_session() as session:
                user = session.query(User).filter(User.id == int(user_id)).first()
                if user:
                    # Return lightweight user object for session
                    from flask_login import UserMixin
                    class AuthUser(UserMixin):
                        def __init__(self, user):
                            self.id = user.id
                            self.username = user.username
                            self.role = user.role
                    return AuthUser(user)
            return None
        except Exception as e:
            app.logger.error(f"Error loading user {user_id}: {e}")
            return None
    
    return app

