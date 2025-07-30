"""
WSGI entry point for production deployment.
This file is specifically for Gunicorn to import the Flask application.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create the Flask application instance
application = create_app()

# For Gunicorn compatibility
app = application

if __name__ == "__main__":
    application.run()