# Global Infrastructure Implementation Guide

## Overview

This document describes the global infrastructure implementation for the Calculator App, transforming it from a single-region application into a worldwide platform with multi-currency support, localization, and regional preferences.

## Architecture Components

### 1. Multi-Currency System

#### Database Models
- **Currency**: Supported currencies with metadata (code, name, symbol, decimal places)
- **ExchangeRate**: Real-time exchange rates with caching and expiration
- **TaxRule**: Regional tax rules for different calculation types

#### Currency Service (`app/services/currency.py`)
- Exchange rate fetching from multiple APIs with fallbacks
- Currency conversion with proper decimal handling
- Currency formatting according to locale preferences
- Comprehensive caching strategy (Redis + Database)

#### Features
- Support for 20+ major currencies (USD, EUR, GBP, JPY, etc.)
- Real-time exchange rates with 1-hour cache
- Fallback rates for API failures
- Locale-aware currency formatting

### 2. Localization Framework

#### Database Models
- **Country**: Regional configurations (decimal/thousands separators, date formats, timezones)
- **UserPreference**: User-specific preferences stored by session

#### Localization Service (`app/services/localization.py`)
- GeoIP-based country detection
- Regional configuration management
- Number and date formatting
- User preference storage and retrieval

#### Features
- Automatic country detection from IP address
- 23+ country/region configurations
- Customizable number formatting (US: 1,234.56 vs EU: 1.234,56)
- Date format preferences (MM/DD/YYYY vs DD/MM/YYYY)
- Timezone-aware operations

### 3. Database Infrastructure

#### Enhanced Models
- **CalculationLog**: Extended with localization context (country, currency, language)
- **PerformanceLog**: Unchanged, maintains existing functionality

#### Migrations
- `migrations/versions/global_infrastructure.py`: Creates all new tables with proper indexes
- Preserves existing data and functionality

### 4. API Layer

#### Global API (`app/api/global_routes.py`)
- `/api/v1/global/currencies` - List supported currencies
- `/api/v1/global/exchange-rate/<base>/<target>` - Get exchange rates
- `/api/v1/global/convert` - Currency conversion
- `/api/v1/global/countries` - List supported countries
- `/api/v1/global/locale-config/<country>` - Get regional configuration
- `/api/v1/global/user-preferences` - Get/set user preferences

#### Health API (`app/api/health.py`)
- `/api/v1/health/` - Overall system health
- `/api/v1/health/currency` - Currency service status
- `/api/v1/health/localization` - Localization service status
- `/api/v1/health/database` - Database connectivity

### 5. Middleware & Context

#### Localization Middleware (`app/middleware/localization.py`)
- Automatic request context setup
- Country detection and regional config loading
- User preference merging
- Flask `g` object population for templates

#### Request Context Variables
- `g.locale_config` - Complete localization configuration
- `g.currency_code` - Active currency
- `g.country_code` - Detected/preferred country
- `g.decimal_separator` - Number formatting preference
- Template injection for easy access

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `requests==2.31.0` - API calls for exchange rates
- `babel==2.13.1` - Internationalization support
- `pytz==2023.3` - Timezone handling
- `geoip2==4.7.0` - IP geolocation (requires GeoLite2 database)
- `pycountry==22.3.13` - Country code validation

### 2. Database Setup

```bash
# Initialize database and run migrations
flask db init
flask db migrate -m "Global infrastructure"
flask db upgrade

# Seed with default data
flask seed-global-data

# Check seeding status
flask show-seed-status
```

### 3. Configuration

#### Environment Variables
```bash
# Required
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///calculator.db  # or PostgreSQL URL
REDIS_URL=redis://localhost:6379/0

# Optional
GEOIP_DB_PATH=data/GeoLite2-Country.mmdb
FIXER_API_KEY=your-fixer-api-key  # For enhanced exchange rates
```

#### GeoIP Database (Optional)
Download GeoLite2-Country.mmdb from MaxMind for IP-based country detection.

### 4. Testing

```bash
# Run comprehensive infrastructure tests
python test_global_infrastructure.py

# Test specific components
pytest tests/ -k "global"
```

## Usage Examples

### Currency Conversion

```python
from app.services.currency import currency_service
from decimal import Decimal

# Convert 100 USD to EUR
amount = currency_service.convert_currency(Decimal('100'), 'USD', 'EUR')

# Format currency with locale preferences
formatted = currency_service.format_currency(amount, 'EUR', locale_config)
```

### Localization

```python
from app.services.localization import localization_service

# Get regional configuration
config = localization_service.get_regional_config('DE')

# Format number according to German preferences
formatted = localization_service.format_number(1234.56, config)
# Result: "1.234,56" (German formatting)
```

### API Usage

```javascript
// Get exchange rate
fetch('/api/v1/global/exchange-rate/USD/EUR')
  .then(response => response.json())
  .then(data => console.log(data.data.rate));

// Convert currency
fetch('/api/v1/global/convert', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    amount: 100,
    from_currency: 'USD',
    to_currency: 'EUR'
  })
})
.then(response => response.json())
.then(data => console.log(data.data.formatted_result));
```

## Performance Considerations

### Caching Strategy
- **Redis Cache**: 1-hour cache for exchange rates and country detection
- **Database Cache**: Persistent storage for exchange rates with expiration
- **Fallback Rates**: Hardcoded rates for critical currency pairs

### Error Handling
- Graceful degradation when services are unavailable
- Comprehensive logging with request context
- Health monitoring for all services
- Fallback to default values (US/USD) when detection fails

## Monitoring & Health Checks

### Health Check Endpoints
- `GET /api/v1/health/` - Overall system status
- `GET /api/v1/health/currency` - Currency service status
- `GET /api/v1/health/localization` - Localization service status
- `GET /api/v1/health/database` - Database connectivity

### CLI Commands
```bash
flask refresh-exchange-rates  # Update all exchange rates
flask show-seed-status       # Check database seeding
flask seed-global-data       # Re-seed if needed
```

## Security Considerations

### Data Protection
- No personal data stored (only session-based preferences)
- IP addresses logged for geolocation (can be anonymized)
- Exchange rates cached securely
- Input validation for all API endpoints

### Rate Limiting
- Existing Flask-Limiter configuration applies to new endpoints
- Exchange rate APIs have built-in rate limiting
- Fallback mechanisms prevent service disruption

## Scalability

### Database
- Proper indexing on frequently queried columns
- Partitioning possible for large calculation logs
- Read replicas supported for high-traffic scenarios

### Services
- Stateless design allows horizontal scaling
- Redis clustering supported for cache layer
- Exchange rate fetching can be distributed

## Next Steps

1. **Phase 2**: Calculator-specific enhancements with currency support
2. **Phase 3**: Advanced localization (translations, RTL support)
3. **Phase 4**: Analytics dashboard with regional insights
4. **Phase 5**: Multi-language content management

## Troubleshooting

### Common Issues

1. **Exchange rates not updating**
   - Check Redis connectivity
   - Verify API limits not exceeded
   - Run `flask refresh-exchange-rates`

2. **Country detection not working**
   - Ensure GeoLite2 database is downloaded
   - Check file permissions
   - Verify IP addresses are public (not localhost)

3. **Database seeding failures**
   - Check database connectivity
   - Verify migration status with `flask db current`
   - Run `flask db upgrade` if needed

### Logs
Check application logs for detailed error messages:
```bash
tail -f logs/app.log | grep -E "(currency|localization|global)"
```

## Conclusion

The global infrastructure provides a solid foundation for worldwide calculator operations with:
- ✅ Multi-currency support with real-time rates
- ✅ Automatic localization and country detection  
- ✅ Scalable architecture with comprehensive caching
- ✅ Production-ready error handling and monitoring
- ✅ Backward compatibility with existing functionality

The implementation maintains all existing security standards while adding robust global capabilities for international users.