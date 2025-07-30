from app import db
from datetime import datetime
import json

class CalculationLog(db.Model):
    """Log calculations for analytics"""
    id = db.Column(db.Integer, primary_key=True)
    calculator_type = db.Column(db.String(50), nullable=False)
    inputs = db.Column(db.Text)
    result = db.Column(db.Text)
    user_ip = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(128))  # User session for preferences
    country_code = db.Column(db.String(2))  # User's country
    currency_code = db.Column(db.String(3))  # Currency used
    language_code = db.Column(db.String(5))  # Language preference
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CalculationLog {self.calculator_type}>'

class PerformanceLog(db.Model):
    """Log performance metrics"""
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    @classmethod
    def create(cls, action, duration, timestamp=None):
        log = cls(action=action, duration=duration)
        if timestamp:
            log.timestamp = timestamp
        db.session.add(log)
        db.session.commit()
        return log

class Currency(db.Model):
    """Supported currencies with metadata"""
    __tablename__ = 'currencies'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True, nullable=False)  # ISO 4217
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    decimal_places = db.Column(db.Integer, default=2)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Currency {self.code}>'
    
    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'symbol': self.symbol,
            'decimal_places': self.decimal_places
        }

class ExchangeRate(db.Model):
    """Real-time exchange rates"""
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    base_currency = db.Column(db.String(3), nullable=False)
    target_currency = db.Column(db.String(3), nullable=False)
    rate = db.Column(db.Numeric(15, 8), nullable=False)
    source = db.Column(db.String(50), nullable=False)  # API source
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('base_currency', 'target_currency', name='_currency_pair'),
        db.Index('idx_exchange_rates_pair', 'base_currency', 'target_currency'),
        db.Index('idx_exchange_rates_expires', 'expires_at')
    )
    
    def __repr__(self):
        return f'<ExchangeRate {self.base_currency}/{self.target_currency}: {self.rate}>'
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at

class Country(db.Model):
    """Country and regional configuration"""
    __tablename__ = 'countries'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(2), unique=True, nullable=False)  # ISO 3166-1 alpha-2
    name = db.Column(db.String(100), nullable=False)
    currency_code = db.Column(db.String(3), nullable=False)
    decimal_separator = db.Column(db.String(1), default='.')
    thousands_separator = db.Column(db.String(1), default=',')
    date_format = db.Column(db.String(20), default='MM/DD/YYYY')
    time_format = db.Column(db.String(20), default='HH:mm')
    timezone = db.Column(db.String(50))
    language_code = db.Column(db.String(5), default='en')
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Country {self.code}: {self.name}>'
    
    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'currency_code': self.currency_code,
            'decimal_separator': self.decimal_separator,
            'thousands_separator': self.thousands_separator,
            'date_format': self.date_format,
            'time_format': self.time_format,
            'timezone': self.timezone,
            'language_code': self.language_code
        }

class UserPreference(db.Model):
    """User localization preferences"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(128), nullable=False)  # Anonymous sessions
    country_code = db.Column(db.String(2))
    currency_code = db.Column(db.String(3))
    language_code = db.Column(db.String(5))
    decimal_separator = db.Column(db.String(1))
    thousands_separator = db.Column(db.String(1))
    date_format = db.Column(db.String(20))
    timezone = db.Column(db.String(50))
    preferences_json = db.Column(db.Text)  # Additional custom preferences
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_user_preferences_session', 'session_id'),
    )
    
    def __repr__(self):
        return f'<UserPreference {self.session_id}>'
    
    @property
    def preferences(self):
        if self.preferences_json:
            return json.loads(self.preferences_json)
        return {}
    
    @preferences.setter
    def preferences(self, value):
        self.preferences_json = json.dumps(value) if value else None
    
    def to_dict(self):
        return {
            'country_code': self.country_code,
            'currency_code': self.currency_code,
            'language_code': self.language_code,
            'decimal_separator': self.decimal_separator,
            'thousands_separator': self.thousands_separator,
            'date_format': self.date_format,
            'timezone': self.timezone,
            'preferences': self.preferences
        }

class TaxRule(db.Model):
    """Regional tax rules for calculators"""
    __tablename__ = 'tax_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(2), nullable=False)
    region_code = db.Column(db.String(10))  # State/province code
    tax_type = db.Column(db.String(50), nullable=False)  # sales, vat, gst, etc.
    rate = db.Column(db.Numeric(5, 4), nullable=False)  # Tax rate as decimal
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    effective_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    
    __table_args__ = (
        db.Index('idx_tax_rules_location', 'country_code', 'region_code'),
        db.Index('idx_tax_rules_type', 'tax_type'),
        db.Index('idx_tax_rules_active', 'is_active', 'effective_date')
    )
    
    def __repr__(self):
        return f'<TaxRule {self.country_code} {self.tax_type}: {self.rate}>'
    
    def to_dict(self):
        return {
            'country_code': self.country_code,
            'region_code': self.region_code,
            'tax_type': self.tax_type,
            'rate': float(self.rate),
            'description': self.description,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None
        }