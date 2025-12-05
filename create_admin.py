"""
Quick Admin User Creation Script
Simple script to create an admin user - can be run from Render Shell

Usage:
    python create_admin.py
    python create_admin.py --username admin --password MySecurePassword123
"""

import sys
import os
import getpass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User
from app.utils.database import DatabaseManager
from werkzeug.security import generate_password_hash


def create_admin():
    """Create admin user interactively or with command line args"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create admin user for Kith Platform')
    parser.add_argument('--username', default='admin', help='Admin username (default: admin)')
    parser.add_argument('--password', help='Admin password (will prompt if not provided)')
    
    args = parser.parse_args()
    
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        db = DatabaseManager()
        
        # Get password
        password = args.password
        if not password:
            print("Enter admin password (input will be hidden):")
            password = getpass.getpass()
            if not password:
                print("❌ Password cannot be empty!")
                sys.exit(1)
        
        with db.get_session() as session:
            # Check if user already exists
            existing_user = session.query(User).filter(User.username == args.username).first()
            if existing_user:
                print(f"❌ User '{args.username}' already exists!")
                response = input("Do you want to update the password? (y/N): ")
                if response.lower() == 'y':
                    existing_user.password_hash = generate_password_hash(password)
                    print(f"✅ Password updated for user '{args.username}'")
                else:
                    print("Cancelled.")
                return
            
            # Create new admin user
            admin = User(
                username=args.username,
                password_hash=generate_password_hash(password),
                role='admin'
            )
            session.add(admin)
            print(f"✅ Admin user '{args.username}' created successfully!")
            print(f"   You can now log in with username: {args.username}")


if __name__ == '__main__':
    try:
        create_admin()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

