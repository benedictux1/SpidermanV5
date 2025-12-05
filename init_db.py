"""
Database Initialization Script
Run this script to create all database tables and optionally create an admin user.

Usage:
    python init_db.py                    # Create tables only
    python init_db.py --create-admin     # Create tables and admin user
"""

import sys
import os
import argparse
from werkzeug.security import generate_password_hash

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.utils.database import DatabaseManager
from app.models import User, Contact, RawNote, SynthesizedEntry


def create_tables():
    """Create all database tables"""
    print("Initializing database...")
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        db = DatabaseManager()
        db.create_all_tables()
        print("✅ Database tables created successfully!")


def create_admin_user(username='admin', password=None):
    """Create an admin user"""
    if not password:
        import secrets
        password = secrets.token_urlsafe(16)
        print(f"\n⚠️  No password provided. Generated password: {password}")
        print("⚠️  Please save this password securely!")
    
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        db = DatabaseManager()
        with db.get_session() as session:
            # Check if admin exists
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                print(f"❌ User '{username}' already exists!")
                return False
            
            admin = User(
                username=username,
                password_hash=generate_password_hash(password),
                role='admin'
            )
            session.add(admin)
            print(f"✅ Admin user '{username}' created successfully!")
            return True


def main():
    parser = argparse.ArgumentParser(description='Initialize Kith Platform database')
    parser.add_argument('--create-admin', action='store_true',
                       help='Create an admin user after initializing tables')
    parser.add_argument('--username', default='admin',
                       help='Admin username (default: admin)')
    parser.add_argument('--password',
                       help='Admin password (if not provided, a random one will be generated)')
    
    args = parser.parse_args()
    
    try:
        # Create tables
        create_tables()
        
        # Create admin user if requested
        if args.create_admin:
            create_admin_user(args.username, args.password)
        
        print("\n✅ Database initialization complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

