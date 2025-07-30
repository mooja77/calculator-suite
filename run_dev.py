#!/usr/bin/env python3
"""
Development server runner for Calculator Suite
"""
import os
from app import create_app, db

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        print("Database tables created (if they didn't exist)")
    
    print("Starting Calculator Suite development server...")
    print("Visit: http://localhost:5000")
    print("Available calculators:")
    
    from app.calculators.registry import calculator_registry
    for slug in calculator_registry.list_slugs():
        print(f"  - http://localhost:5000/calculators/{slug}/")
    
    # Run the development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )