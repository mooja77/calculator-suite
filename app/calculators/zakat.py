"""
Zakat Calculator

Calculates Zakat (Islamic almsgiving) with support for:
- 2.5% on eligible wealth (lunar year)
- Nisab threshold (gold/silver equivalent)
- Different asset types (cash, gold, business, stocks)
- Multiple currencies (especially Islamic countries)
- Lunar year calculation (354 days)
- Cultural sensitivity and Islamic finance principles
"""

from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from app.calculators.base import BaseCalculator
from app.calculators.registry import register_calculator

@register_calculator
class ZakatCalculator(BaseCalculator):
    """Zakat Calculator following Islamic finance principles"""
    
    # Zakat rate (2.5% or 1/40)
    ZAKAT_RATE = Decimal('0.025')  # 2.5%
    
    # Nisab thresholds (approximate values in USD - should be updated regularly)
    # Based on current gold and silver prices
    NISAB_GOLD_GRAMS = Decimal('87.48')      # 87.48 grams of gold (20 mithqal)
    NISAB_SILVER_GRAMS = Decimal('612.36')   # 612.36 grams of silver (200 dirhams)
    
    # Approximate values in USD (should be updated with current market prices)
    GOLD_PRICE_USD_PER_GRAM = Decimal('65')  # Approximate - should be dynamic
    SILVER_PRICE_USD_PER_GRAM = Decimal('0.8')  # Approximate - should be dynamic
    
    # Asset types subject to Zakat
    ZAKATABLE_ASSETS = {
        'cash': {'rate': ZAKAT_RATE, 'description': 'Cash, bank deposits, savings'},
        'gold': {'rate': ZAKAT_RATE, 'description': 'Gold jewelry, coins, bars (above personal use)'},
        'silver': {'rate': ZAKAT_RATE, 'description': 'Silver jewelry, coins, bars (above personal use)'},
        'business_inventory': {'rate': ZAKAT_RATE, 'description': 'Business stock and inventory'},
        'investments': {'rate': ZAKAT_RATE, 'description': 'Stocks, bonds, mutual funds'},
        'receivables': {'rate': ZAKAT_RATE, 'description': 'Money owed to you (if recoverable)'},
        'livestock': {'rate': 'varies', 'description': 'Cattle, sheep, goats, camels (special rates)'}
    }
    
    # Lunar year in days
    LUNAR_YEAR_DAYS = 354  # Islamic lunar year
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        self.clear_errors()
        
        # Validate calculation type
        calc_type = inputs.get('calculation_type', 'total_zakat')
        if calc_type not in ['total_zakat', 'nisab_check', 'asset_specific', 'lunar_adjustment']:
            self.add_error("Invalid calculation type")
        
        # Validate currency
        currency = inputs.get('currency', 'USD')
        
        # For total zakat calculation, validate all asset amounts
        if calc_type == 'total_zakat':
            total_assets = Decimal('0')
            for asset_type in self.ZAKATABLE_ASSETS.keys():
                if asset_type != 'livestock':  # Livestock has special rules
                    amount = self.validate_number(inputs.get(f'{asset_type}_amount', 0), f'{asset_type.replace("_", " ").title()} amount', min_val=0)
                    if amount is not None:
                        total_assets += Decimal(str(amount))
            
            if total_assets == 0:
                self.add_error("Please enter at least one asset amount")
        
        # Validate holding period
        holding_period_days = self.validate_number(inputs.get('holding_period_days', 354), 'Holding period (days)', min_val=1, max_val=365)
        
        # Validate debts (liabilities)
        debts = self.validate_number(inputs.get('debts', 0), 'Debts/Liabilities', min_val=0)
        
        return len(self.errors) == 0
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Zakat calculations"""
        
        if not self.validate_inputs(inputs):
            return {'error': self.errors}
        
        calc_type = inputs.get('calculation_type', 'total_zakat')
        currency = inputs.get('currency', 'USD')
        holding_period_days = Decimal(str(inputs.get('holding_period_days', 354)))
        debts = Decimal(str(inputs.get('debts', 0)))
        
        result = {
            'calculation_type': calc_type,
            'currency': currency,
            'holding_period_days': float(holding_period_days),
            'zakat_rate_percentage': float(self.ZAKAT_RATE * 100)
        }
        
        if calc_type == 'total_zakat':
            # Calculate total Zakat on all assets
            zakatable_wealth = self._calculate_total_wealth(inputs)
            net_wealth = zakatable_wealth - debts
            
            # Check if net wealth meets Nisab threshold
            nisab_threshold = self._get_nisab_threshold(currency)
            meets_nisab = net_wealth >= nisab_threshold
            
            # Calculate Zakat amount
            if meets_nisab and holding_period_days >= self.LUNAR_YEAR_DAYS:
                zakat_amount = net_wealth * self.ZAKAT_RATE
                
                # Adjust for partial year if needed
                if holding_period_days > self.LUNAR_YEAR_DAYS:
                    year_fraction = self.LUNAR_YEAR_DAYS / holding_period_days
                    zakat_amount = zakat_amount * year_fraction
            else:
                zakat_amount = Decimal('0')
            
            result.update({
                'total_zakatable_wealth': float(zakatable_wealth.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'total_debts': float(debts.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'net_zakatable_wealth': float(net_wealth.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'nisab_threshold': float(nisab_threshold.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'meets_nisab': meets_nisab,
                'holding_period_sufficient': holding_period_days >= self.LUNAR_YEAR_DAYS,
                'zakat_due': float(zakat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'zakat_payable': meets_nisab and holding_period_days >= self.LUNAR_YEAR_DAYS,
                'wealth_breakdown': self._get_wealth_breakdown(inputs)
            })
            
        elif calc_type == 'nisab_check':
            # Check if wealth meets Nisab threshold
            current_wealth = Decimal(str(inputs.get('current_wealth', 0)))
            nisab_threshold = self._get_nisab_threshold(currency)
            
            result.update({
                'current_wealth': float(current_wealth.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'nisab_threshold': float(nisab_threshold.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'meets_nisab': current_wealth >= nisab_threshold,
                'shortfall': float((nisab_threshold - current_wealth).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) if current_wealth < nisab_threshold else 0,
                'excess': float((current_wealth - nisab_threshold).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) if current_wealth >= nisab_threshold else 0
            })
            
        elif calc_type == 'asset_specific':
            # Calculate Zakat for specific asset type
            asset_type = inputs.get('asset_type', 'cash')
            asset_amount = Decimal(str(inputs.get('asset_amount', 0)))
            
            if asset_type in self.ZAKATABLE_ASSETS and asset_type != 'livestock':
                zakat_amount = asset_amount * self.ZAKAT_RATE
                
                result.update({
                    'asset_type': asset_type,
                    'asset_amount': float(asset_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'zakat_amount': float(zakat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'asset_description': self.ZAKATABLE_ASSETS[asset_type]['description']
                })
        
        elif calc_type == 'lunar_adjustment':
            # Calculate lunar year adjustment
            gregorian_days = Decimal(str(inputs.get('gregorian_days', 365)))
            amount = Decimal(str(inputs.get('amount', 0)))
            
            lunar_adjustment = self.LUNAR_YEAR_DAYS / gregorian_days
            adjusted_amount = amount * lunar_adjustment
            
            result.update({
                'gregorian_days': float(gregorian_days),
                'lunar_days': float(self.LUNAR_YEAR_DAYS),
                'original_amount': float(amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'adjusted_amount': float(adjusted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'adjustment_factor': float(lunar_adjustment.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP))
            })
        
        # Add Islamic finance principles and guidance
        result['islamic_guidance'] = self._get_islamic_guidance(calc_type)
        result['nisab_info'] = self._get_nisab_info(currency)
        
        return result
    
    def _calculate_total_wealth(self, inputs: Dict[str, Any]) -> Decimal:
        """Calculate total zakatable wealth from all asset types"""
        total_wealth = Decimal('0')
        
        for asset_type in self.ZAKATABLE_ASSETS.keys():
            if asset_type != 'livestock':  # Livestock has special calculation rules
                amount = Decimal(str(inputs.get(f'{asset_type}_amount', 0)))
                total_wealth += amount
        
        return total_wealth
    
    def _get_wealth_breakdown(self, inputs: Dict[str, Any]) -> Dict[str, float]:
        """Get breakdown of wealth by asset type"""
        breakdown = {}
        
        for asset_type in self.ZAKATABLE_ASSETS.keys():
            if asset_type != 'livestock':
                amount = Decimal(str(inputs.get(f'{asset_type}_amount', 0)))
                if amount > 0:
                    breakdown[asset_type] = float(amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        
        return breakdown
    
    def _get_nisab_threshold(self, currency: str) -> Decimal:
        """Calculate Nisab threshold in specified currency"""
        # Use gold standard (lower threshold is typically preferred)
        gold_nisab_usd = self.NISAB_GOLD_GRAMS * self.GOLD_PRICE_USD_PER_GRAM
        silver_nisab_usd = self.NISAB_SILVER_GRAMS * self.SILVER_PRICE_USD_PER_GRAM
        
        # Use the lower threshold (more favorable to the poor)
        nisab_usd = min(gold_nisab_usd, silver_nisab_usd)
        
        # Convert to requested currency (simplified - in practice would use real exchange rates)
        currency_multipliers = {
            'USD': Decimal('1'),
            'AED': Decimal('3.67'),    # UAE Dirham
            'SAR': Decimal('3.75'),    # Saudi Riyal
            'MYR': Decimal('4.7'),     # Malaysian Ringgit
            'PKR': Decimal('280'),     # Pakistani Rupee
            'BDT': Decimal('110'),     # Bangladeshi Taka
            'IDR': Decimal('15000'),   # Indonesian Rupiah
            'EGP': Decimal('31'),      # Egyptian Pound
            'EUR': Decimal('0.85'),    # Euro
            'GBP': Decimal('0.79'),    # British Pound
        }
        
        multiplier = currency_multipliers.get(currency, Decimal('1'))
        return nisab_usd * multiplier
    
    def _get_nisab_info(self, currency: str) -> Dict[str, Any]:
        """Get information about Nisab thresholds"""
        gold_nisab_usd = self.NISAB_GOLD_GRAMS * self.GOLD_PRICE_USD_PER_GRAM
        silver_nisab_usd = self.NISAB_SILVER_GRAMS * self.SILVER_PRICE_USD_PER_GRAM
        current_nisab = self._get_nisab_threshold(currency)
        
        return {
            'gold_nisab_grams': float(self.NISAB_GOLD_GRAMS),
            'silver_nisab_grams': float(self.NISAB_SILVER_GRAMS),
            'gold_nisab_value_usd': float(gold_nisab_usd.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'silver_nisab_value_usd': float(silver_nisab_usd.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'current_nisab_threshold': float(current_nisab.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'currency': currency,
            'standard_used': 'Lower of gold or silver (more favorable to the poor)',
            'update_frequency': 'Should be updated with current precious metal prices'
        }
    
    def _get_islamic_guidance(self, calc_type: str) -> Dict[str, Any]:
        """Get Islamic guidance and principles for Zakat"""
        
        general_guidance = {
            'purpose': 'Zakat is one of the Five Pillars of Islam, purifying wealth and helping the needy',
            'recipients': ['The poor (fuqara)', 'The needy (masakin)', 'Zakat administrators', 'New Muslims', 'Slaves to be freed', 'Debtors', 'In the path of Allah', 'Travelers in need'],
            'principles': [
                'Zakat purifies wealth and the soul',
                'Based on lunar year (354 days)',
                'Wealth must be held for full lunar year',
                'Must meet Nisab threshold',
                'Debts reduce zakatable wealth'
            ]
        }
        
        specific_guidance = {
            'total_zakat': {
                'advice': 'Calculate all zakatable assets and subtract legitimate debts',
                'timing': 'Choose a consistent date each lunar year for calculation',
                'documentation': 'Keep records of wealth and Zakat payments'
            },
            'nisab_check': {
                'advice': 'Nisab is the minimum threshold for Zakat obligation',
                'fluctuation': 'If wealth falls below Nisab during the year, the lunar year count restarts'
            },
            'asset_specific': {
                'advice': 'Different assets may have different Zakat rules',
                'gold_silver': 'Personal jewelry for daily use may be exempt (scholarly difference of opinion)'
            }
        }
        
        result = general_guidance.copy()
        result.update(specific_guidance.get(calc_type, {}))
        
        return result
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO metadata"""
        return {
            'title': 'Zakat Calculator - Calculate Islamic Zakat (2.5%) | Nisab Threshold',
            'description': 'Free Islamic Zakat calculator. Calculate 2.5% Zakat on wealth, check Nisab threshold, lunar year adjustment. Supports multiple currencies including AED, SAR, MYR.',
            'keywords': 'Zakat calculator, Islamic finance, Nisab threshold, Islamic tax, Muslim charity, Zakat al-mal, Islamic wealth purification',
            'canonical': '/calculators/zakat'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup"""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Zakat Calculator",
            "description": "Calculate Islamic Zakat (almsgiving) with Nisab threshold and lunar year support",
            "url": "https://calculatorapp.com/calculators/zakat",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Web",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "2.5% Zakat calculation",
                "Nisab threshold checking",
                "Multiple asset types",
                "Lunar year adjustment",
                "Islamic finance compliance",
                "Multi-currency support",
                "Debt consideration",
                "Islamic guidance"
            ]
        }