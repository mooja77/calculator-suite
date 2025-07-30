import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    print("Testing UK VAT Calculator import...")
    from calculators.uk_vat import UkVatCalculator
    print("✅ UK VAT Calculator imported successfully")
    
    calc = UkVatCalculator()
    print("✅ UK VAT Calculator instantiated")
    
    result = calc.calculate({
        'amount': 100,
        'calculation_type': 'add_vat',
        'vat_rate_type': 'standard'
    })
    print(f"✅ Calculation result: {result}")
    
except Exception as e:
    import traceback
    print(f"❌ Error: {e}")
    traceback.print_exc()