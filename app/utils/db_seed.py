"""
Database seeding utilities for global infrastructure.
"""
from datetime import datetime, date
import logging

from app import db
from app.models import Currency, Country, TaxRule
from app.config.regional_defaults import CURRENCIES, COUNTRIES, TAX_RULES

logger = logging.getLogger(__name__)

def seed_currencies():
    """Seed the currencies table with default data."""
    try:
        for currency_data in CURRENCIES:
            existing = Currency.query.filter_by(code=currency_data['code']).first()
            if not existing:
                currency = Currency(**currency_data)
                db.session.add(currency)
                logger.info(f"Added currency: {currency_data['code']}")
        
        db.session.commit()
        logger.info("Currency seeding completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error seeding currencies: {e}")
        db.session.rollback()
        return False

def seed_countries():
    """Seed the countries table with default data."""
    try:
        for country_data in COUNTRIES:
            existing = Country.query.filter_by(code=country_data['code']).first()
            if not existing:
                country = Country(**country_data)
                db.session.add(country)
                logger.info(f"Added country: {country_data['code']}")
        
        db.session.commit()
        logger.info("Country seeding completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error seeding countries: {e}")
        db.session.rollback()
        return False

def seed_tax_rules():
    """Seed the tax_rules table with default data."""
    try:
        for tax_data in TAX_RULES:
            # Add effective date if not present
            if 'effective_date' not in tax_data:
                tax_data['effective_date'] = date.today()
            
            existing = TaxRule.query.filter_by(
                country_code=tax_data['country_code'],
                region_code=tax_data.get('region_code'),
                tax_type=tax_data['tax_type']
            ).first()
            
            if not existing:
                tax_rule = TaxRule(**tax_data)
                db.session.add(tax_rule)
                logger.info(f"Added tax rule: {tax_data['country_code']} {tax_data['tax_type']}")
        
        db.session.commit()
        logger.info("Tax rules seeding completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error seeding tax rules: {e}")
        db.session.rollback()
        return False

def seed_all():
    """Seed all global infrastructure tables."""
    logger.info("Starting database seeding for global infrastructure")
    
    success_count = 0
    total_operations = 3
    
    if seed_currencies():
        success_count += 1
    
    if seed_countries():
        success_count += 1
    
    if seed_tax_rules():
        success_count += 1
    
    if success_count == total_operations:
        logger.info("All seeding operations completed successfully")
        return True
    else:
        logger.warning(f"Seeding partially completed: {success_count}/{total_operations} operations successful")
        return False

def update_currency_status(currency_code: str, is_active: bool):
    """Update currency active status."""
    try:
        currency = Currency.query.filter_by(code=currency_code).first()
        if currency:
            currency.is_active = is_active
            db.session.commit()
            logger.info(f"Updated currency {currency_code} status to {is_active}")
            return True
        else:
            logger.warning(f"Currency {currency_code} not found")
            return False
    except Exception as e:
        logger.error(f"Error updating currency status: {e}")
        db.session.rollback()
        return False

def update_country_status(country_code: str, is_active: bool):
    """Update country active status."""
    try:
        country = Country.query.filter_by(code=country_code).first()
        if country:
            country.is_active = is_active
            db.session.commit()
            logger.info(f"Updated country {country_code} status to {is_active}")
            return True
        else:
            logger.warning(f"Country {country_code} not found")
            return False
    except Exception as e:
        logger.error(f"Error updating country status: {e}")
        db.session.rollback()
        return False

def get_seeding_status():
    """Get current seeding status."""
    try:
        status = {
            'currencies': {
                'total': len(CURRENCIES),
                'seeded': Currency.query.count(),
                'active': Currency.query.filter_by(is_active=True).count()
            },
            'countries': {
                'total': len(COUNTRIES),
                'seeded': Country.query.count(),
                'active': Country.query.filter_by(is_active=True).count()
            },
            'tax_rules': {
                'total': len(TAX_RULES),
                'seeded': TaxRule.query.count(),
                'active': TaxRule.query.filter_by(is_active=True).count()
            }
        }
        return status
    except Exception as e:
        logger.error(f"Error getting seeding status: {e}")
        return None