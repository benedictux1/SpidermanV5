"""
Application Entry Point
Supports both development and production modes
Run with: python main.py (development)
Production: gunicorn main:app (via Procfile)
"""

import os
from app import create_app

# Get environment from FLASK_ENV or default to development
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Development mode only
    port = int(os.environ.get('PORT', 5001))  # Use 5001 to avoid AirPlay conflict
    debug = config_name == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)

