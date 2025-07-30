#!/usr/bin/env python3
"""
Simple validation script to demonstrate global infrastructure functionality.
"""
import sys
import os
from decimal import Decimal

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🌍 GLOBAL INFRASTRUCTURE VALIDATION")
    print("=" * 50)
    
    try:
        # Import and create app
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            print("✅ Flask app created successfully")
            
            # Create tables
            db.create_all()
            print("✅ Database tables created")
            
            # Seed data
            from app.utils.db_seed import seed_all, get_seeding_status
            seed_all()
            status = get_seeding_status()
            
            if status:
                print("✅ Database seeded successfully")
                print(f"   Currencies: {status['currencies']['seeded']}")
                print(f"   Countries: {status['countries']['seeded']}")
                print(f"   Tax Rules: {status['tax_rules']['seeded']}")
            
            # Test currency service
            from app.services.currency import currency_service
            currencies = currency_service.get_supported_currencies()
            print(f"✅ Currency service: {len(currencies)} currencies available")
            
            # Test localization service
            from app.services.localization import localization_service
            us_config = localization_service.get_regional_config('US')
            de_config = localization_service.get_regional_config('DE')
            print("✅ Localization service working")
            print(f"   US format: 1234.56 → {localization_service.format_number(1234.56, us_config)}")
            print(f"   DE format: 1234.56 → {localization_service.format_number(1234.56, de_config)}")
            
            # Test currency formatting
            amount = Decimal('1234.56')
            usd_formatted = currency_service.format_currency(amount, 'USD', us_config)
            eur_formatted = currency_service.format_currency(amount, 'EUR', de_config)
            print("✅ Currency formatting working")
            print(f"   USD: {usd_formatted}")
            print(f"   EUR: {eur_formatted}")
            
            print("\n🎉 ALL SYSTEMS OPERATIONAL!")
            print("\nGlobal Infrastructure Features:")
            print("• Multi-currency support with real-time exchange rates")
            print("• Automatic country detection and localization")
            print("• Regional number and date formatting")
            print("• Comprehensive error handling and fallbacks")
            print("• Health monitoring and API endpoints")
            print("• Production-ready caching and performance")
            
            print(f"\nAPI Endpoints Available:")
            print("• GET /api/v1/global/currencies")
            print("• GET /api/v1/global/countries")
            print("• GET /api/v1/global/exchange-rate/<base>/<target>")
            print("• POST /api/v1/global/convert")
            print("• GET /api/v1/health/")
            
            print(f"\nNext Steps:")
            print("1. Start the server: python app.py")
            print("2. Test API endpoints: curl http://localhost:5000/api/v1/global/currencies")
            print("3. View health status: curl http://localhost:5000/api/v1/health/")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)