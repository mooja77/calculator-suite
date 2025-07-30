import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

# Create the Flask application instance
app = create_app()

# This ensures the app is available for Gunicorn as 'app:app'
if __name__ == '__main__':
    app.run(debug=True)

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized.')

@app.cli.command()
def seed_global_data():
    """Seed global infrastructure data."""
    from app.utils.db_seed import seed_all
    if seed_all():
        print('Global infrastructure data seeded successfully.')
    else:
        print('Warning: Some seeding operations failed.')

@app.cli.command()
def show_seed_status():
    """Show seeding status."""
    from app.utils.db_seed import get_seeding_status
    status = get_seeding_status()
    if status:
        print('Global Infrastructure Seeding Status:')
        for table, info in status.items():
            print(f'  {table}: {info["seeded"]}/{info["total"]} seeded, {info["active"]} active')
    else:
        print('Error getting seeding status.')

@app.cli.command()
def refresh_exchange_rates():
    """Refresh currency exchange rates."""
    from app.services.currency import currency_service
    stats = currency_service.refresh_all_rates()
    print(f'Exchange rates refresh: {stats["success"]} success, {stats["failed"]} failed, {stats["skipped"]} skipped')

if __name__ == '__main__':
    app.run(debug=True)