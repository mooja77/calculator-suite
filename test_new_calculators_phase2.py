#!/usr/bin/env python3
"""
Comprehensive test suite for Phase 2 calculators:
- UK VAT Calculator
- Canada GST/HST Calculator
- Australia GST Calculator
- Zakat Calculator
- Murabaha Calculator
- Takaful Calculator
"""

import sys
import os
import traceback
from decimal import Decimal

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_uk_vat_calculator():
    """Test UK VAT Calculator functionality"""
    print("=== Testing UK VAT Calculator ===")
    
    try:
        from calculators.uk_vat import UkVatCalculator
        calc = UkVatCalculator()
        
        # Test 1: Add standard VAT (20%)
        result = calc.calculate({
            'amount': 100,
            'calculation_type': 'add_vat',
            'vat_rate_type': 'standard'
        })
        
        assert 'net_amount' in result
        assert 'vat_amount' in result
        assert 'gross_amount' in result
        assert result['vat_amount'] == 20.0  # 20% of 100
        assert result['gross_amount'] == 120.0
        print("✓ Standard VAT addition test passed")
        
        # Test 2: Remove VAT from gross amount
        result = calc.calculate({
            'amount': 120,
            'calculation_type': 'remove_vat',
            'vat_rate_type': 'standard'
        })
        
        assert abs(result['net_amount'] - 100.0) < 0.01
        assert abs(result['vat_amount'] - 20.0) < 0.01
        print("✓ VAT removal test passed")
        
        # Test 3: VAT registration check
        result = calc.calculate({
            'amount': 90000,
            'calculation_type': 'registration_check'
        })
        
        assert result['must_register'] == True
        print("✓ VAT registration check test passed")
        
        # Test 4: Reduced rate VAT (5%)
        result = calc.calculate({
            'amount': 100,
            'calculation_type': 'add_vat',
            'vat_rate_type': 'reduced'
        })
        
        assert result['vat_amount'] == 5.0
        print("✓ Reduced VAT rate test passed")
        
        print("✓ All UK VAT Calculator tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ UK VAT Calculator test failed: {e}")
        traceback.print_exc()
        return False

def test_canada_gst_calculator():
    """Test Canada GST/HST Calculator functionality"""
    print("=== Testing Canada GST/HST Calculator ===")
    
    try:
        from calculators.canada_gst import CanadaGstCalculator
        calc = CanadaGstCalculator()
        
        # Test 1: HST province (Ontario - 13%)
        result = calc.calculate({
            'amount': 100,
            'calculation_type': 'add_tax',
            'province': 'ON'
        })
        
        assert 'hst_amount' in result
        assert result['hst_amount'] == 13.0
        assert result['gross_amount'] == 113.0
        print("✓ Ontario HST test passed")
        
        # Test 2: GST + PST province (British Columbia)
        result = calc.calculate({
            'amount': 100,
            'calculation_type': 'add_tax',
            'province': 'BC'
        })
        
        assert 'gst_amount' in result
        assert 'pst_amount' in result
        assert result['gst_amount'] == 5.0  # 5% GST
        assert result['pst_amount'] == 7.0  # 7% PST
        assert result['total_tax'] == 12.0
        print("✓ British Columbia GST+PST test passed")
        
        # Test 3: GST only province (Alberta)
        result = calc.calculate({
            'amount': 100,
            'calculation_type': 'add_tax',
            'province': 'AB'
        })
        
        assert result['gst_amount'] == 5.0
        assert result['pst_amount'] == 0.0
        assert result['total_tax'] == 5.0
        print("✓ Alberta GST only test passed")
        
        # Test 4: Quebec QST calculation (compound)
        result = calc.calculate({
            'amount': 100,
            'calculation_type': 'add_tax',
            'province': 'QC'
        })
        
        # QST is calculated on GST-inclusive amount
        expected_qst = (100 + 5) * 0.09975  # QST on net + GST
        assert abs(result['pst_amount'] - expected_qst) < 0.01
        print("✓ Quebec compound QST test passed")
        
        print("✓ All Canada GST/HST Calculator tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Canada GST/HST Calculator test failed: {e}")
        traceback.print_exc()
        return False

def test_australia_gst_calculator():
    """Test Australia GST Calculator functionality"""
    print("=== Testing Australia GST Calculator ===")
    
    try:
        from calculators.australia_gst import AustraliaGstCalculator
        calc = AustraliaGstCalculator()
        
        # Test 1: Add GST (10%)
        result = calc.calculate({
            'amount': 100,
            'calculation_type': 'add_gst',
            'supply_type': 'taxable'
        })
        
        assert result['gst_amount'] == 10.0
        assert result['gross_amount'] == 110.0
        print("✓ Standard GST addition test passed")
        
        # Test 2: Remove GST
        result = calc.calculate({
            'amount': 110,
            'calculation_type': 'remove_gst',
            'supply_type': 'taxable'
        })
        
        assert abs(result['net_amount'] - 100.0) < 0.01
        print("✓ GST removal test passed")
        
        # Test 3: GST-free supply
        result = calc.calculate({
            'amount': 100,
            'calculation_type': 'add_gst',
            'supply_type': 'gst_free'
        })
        
        assert result['gst_amount'] == 0.0
        assert result['gross_amount'] == 100.0
        print("✓ GST-free supply test passed")
        
        # Test 4: BAS calculation
        result = calc.calculate({
            'amount': 1000,  # sales
            'purchases_amount': 500,
            'calculation_type': 'bas_calculation',
            'supply_type': 'taxable'
        })
        
        assert result['gst_collected'] == 100.0  # 10% of sales
        assert result['gst_credits'] == 50.0   # 10% of purchases
        assert result['net_gst_liability'] == 50.0
        print("✓ BAS calculation test passed")
        
        # Test 5: Registration check
        result = calc.calculate({
            'amount': 80000,
            'calculation_type': 'registration_check'
        })
        
        assert result['must_register'] == True
        print("✓ GST registration check test passed")
        
        print("✓ All Australia GST Calculator tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Australia GST Calculator test failed: {e}")
        traceback.print_exc()
        return False

def test_zakat_calculator():
    """Test Zakat Calculator functionality"""
    print("=== Testing Zakat Calculator ===")
    
    try:
        from calculators.zakat import ZakatCalculator
        calc = ZakatCalculator()
        
        # Test 1: Total Zakat calculation
        result = calc.calculate({
            'calculation_type': 'total_zakat',
            'cash_amount': 10000,
            'gold_amount': 5000,
            'investments_amount': 3000,
            'debts': 1000,
            'holding_period_days': 354,
            'currency': 'USD'
        })
        
        assert 'total_zakatable_wealth' in result
        assert 'zakat_due' in result
        assert result['total_zakatable_wealth'] == 18000.0
        assert result['net_zakatable_wealth'] == 17000.0  # After debts
        expected_zakat = 17000 * 0.025  # 2.5%
        assert abs(result['zakat_due'] - expected_zakat) < 0.01
        print("✓ Total Zakat calculation test passed")
        
        # Test 2: Nisab check
        result = calc.calculate({
            'calculation_type': 'nisab_check',
            'current_wealth': 5000,
            'currency': 'USD'
        })
        
        assert 'meets_nisab' in result
        assert 'nisab_threshold' in result
        print("✓ Nisab check test passed")
        
        # Test 3: Asset-specific calculation
        result = calc.calculate({
            'calculation_type': 'asset_specific',
            'asset_type': 'cash',
            'asset_amount': 1000
        })
        
        assert result['zakat_amount'] == 25.0  # 2.5% of 1000
        print("✓ Asset-specific Zakat test passed")
        
        # Test 4: Lunar adjustment
        result = calc.calculate({
            'calculation_type': 'lunar_adjustment',
            'gregorian_days': 365,
            'amount': 1000
        })
        
        lunar_factor = 354 / 365
        expected_adjusted = 1000 * lunar_factor
        assert abs(result['adjusted_amount'] - expected_adjusted) < 0.01
        print("✓ Lunar year adjustment test passed")
        
        print("✓ All Zakat Calculator tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Zakat Calculator test failed: {e}")
        traceback.print_exc()
        return False

def test_murabaha_calculator():
    """Test Murabaha Calculator functionality"""
    print("=== Testing Murabaha Calculator ===")
    
    try:
        from calculators.murabaha import MurabahaCalculator
        calc = MurabahaCalculator()
        
        # Test 1: Diminishing Musharaka calculation
        result = calc.calculate({
            'property_price': 200000,
            'down_payment': 40000,
            'term_years': 15,
            'profit_rate': 5,
            'structure_type': 'diminishing_musharaka',
            'calculation_type': 'monthly_payment'
        })
        
        assert 'monthly_payment' in result
        assert 'total_payment' in result
        assert 'total_profit' in result
        assert result['financing_amount'] == 160000.0
        assert result['monthly_payment'] > 0
        print("✓ Diminishing Musharaka test passed")
        
        # Test 2: Direct Murabaha calculation
        result = calc.calculate({
            'property_price': 200000,
            'down_payment': 40000,
            'term_years': 15,
            'profit_rate': 5,
            'structure_type': 'direct_murabaha',
            'calculation_type': 'monthly_payment'
        })
        
        assert result['structure_type'] == 'direct_murabaha'
        assert result['monthly_payment'] > 0
        # Direct Murabaha: Total profit = Principal × Rate × Years
        expected_profit = 160000 * 0.05 * 15
        assert abs(result['total_profit'] - expected_profit) < 1.0
        print("✓ Direct Murabaha test passed")
        
        # Test 3: Ijara Muntahia calculation  
        result = calc.calculate({
            'property_price': 200000,
            'down_payment': 40000,
            'term_years': 15,
            'profit_rate': 5,
            'structure_type': 'ijara_muntahia',
            'calculation_type': 'monthly_payment'
        })
        
        assert 'monthly_rent' in result
        assert 'monthly_ownership' in result
        assert result['structure_type'] == 'ijara_muntahia'
        print("✓ Ijara Muntahia test passed")
        
        # Test 4: Payment schedule generation
        result = calc.calculate({
            'property_price': 200000,
            'down_payment': 40000,
            'term_years': 15,
            'profit_rate': 5,
            'structure_type': 'diminishing_musharaka',
            'calculation_type': 'payment_schedule'
        })
        
        assert 'payment_schedule' in result
        assert len(result['payment_schedule']) > 0
        print("✓ Payment schedule generation test passed")
        
        print("✓ All Murabaha Calculator tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Murabaha Calculator test failed: {e}")
        traceback.print_exc()
        return False

def test_takaful_calculator():
    """Test Takaful Calculator functionality"""
    print("=== Testing Takaful Calculator ===")
    
    try:
        from calculators.takaful import TakafulCalculator
        calc = TakafulCalculator()
        
        # Test 1: Family Takaful contribution calculation
        result = calc.calculate({
            'calculation_type': 'contribution',
            'takaful_type': 'family_life',
            'sum_covered': 100000,
            'age': 30,
            'term_years': 20,
            'takaful_model': 'mudharabah'
        })
        
        assert 'annual_contribution' in result
        assert 'monthly_contribution' in result
        assert result['sum_covered'] == 100000.0
        assert result['annual_contribution'] > 0
        print("✓ Family Takaful contribution test passed")
        
        # Test 2: General Takaful (Motor)
        result = calc.calculate({
            'calculation_type': 'contribution',
            'takaful_type': 'general_motor',
            'sum_covered': 25000,
            'takaful_model': 'mudharabah'
        })
        
        assert result['takaful_type'] == 'general_motor'
        assert result['annual_contribution'] > 0
        print("✓ General Motor Takaful test passed")
        
        # Test 3: Coverage calculation (reverse)
        result = calc.calculate({
            'calculation_type': 'coverage',
            'takaful_type': 'family_life',
            'contribution_amount': 1500,
            'age': 30,
            'term_years': 20
        })
        
        assert 'sum_covered' in result
        assert result['sum_covered'] > 0
        print("✓ Coverage calculation test passed")
        
        # Test 4: Surplus sharing calculation
        result = calc.calculate({
            'calculation_type': 'surplus_sharing',
            'total_contributions': 100000,
            'total_claims': 60000,
            'expenses': 10000,
            'sharing_ratio': 'mudharabah_90_10'
        })
        
        assert 'surplus_deficit' in result
        assert 'participant_share' in result
        assert 'operator_share' in result
        expected_surplus = 100000 - 60000 - 10000  # 30000
        assert result['surplus_deficit'] == expected_surplus
        assert result['participant_share'] == expected_surplus * 0.9
        print("✓ Surplus sharing test passed")
        
        # Test 5: Comparison with conventional insurance
        result = calc.calculate({
            'calculation_type': 'comparison',
            'takaful_type': 'family_life',
            'sum_covered': 100000,
            'conventional_premium': 2000
        })
        
        assert 'takaful_contribution' in result
        assert 'conventional_premium' in result
        assert 'difference' in result
        print("✓ Conventional comparison test passed")
        
        print("✓ All Takaful Calculator tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Takaful Calculator test failed: {e}")
        traceback.print_exc()
        return False

def test_calculator_registry():
    """Test that all new calculators are properly registered"""
    print("=== Testing Calculator Registry ===")
    
    try:
        from calculators.registry import calculator_registry
        
        expected_calculators = [
            'ukvat', 'canadagst', 'australiagst', 
            'zakat', 'murabaha', 'takaful'
        ]
        
        registered_slugs = calculator_registry.list_slugs()
        
        for expected in expected_calculators:
            if expected in registered_slugs:
                print(f"✓ {expected} calculator registered")
            else:
                print(f"✗ {expected} calculator not found in registry")
                return False
        
        print("✓ All new calculators properly registered!\n")
        return True
        
    except Exception as e:
        print(f"✗ Calculator registry test failed: {e}")
        traceback.print_exc()
        return False

def test_meta_data_and_seo():
    """Test that all calculators have proper meta data and SEO"""
    print("=== Testing Meta Data and SEO ===")
    
    try:
        from calculators.uk_vat import UkVatCalculator
        from calculators.zakat import ZakatCalculator
        from calculators.murabaha import MurabahaCalculator
        
        calculators = [
            ('UK VAT', UkVatCalculator()),
            ('Zakat', ZakatCalculator()),
            ('Murabaha', MurabahaCalculator())
        ]
        
        for name, calc in calculators:
            # Test meta data
            meta_data = calc.get_meta_data()
            assert 'title' in meta_data
            assert 'description' in meta_data
            assert 'keywords' in meta_data
            assert 'canonical' in meta_data
            print(f"✓ {name} meta data complete")
            
            # Test schema markup
            schema = calc.get_schema_markup()
            assert '@context' in schema
            assert '@type' in schema
            assert 'name' in schema
            assert 'description' in schema
            print(f"✓ {name} schema markup complete")
        
        print("✓ All meta data and SEO tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Meta data and SEO test failed: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and return overall success status"""
    print("🧪 Starting Phase 2 Calculator Test Suite")
    print("=" * 50)
    
    tests = [
        test_uk_vat_calculator,
        test_canada_gst_calculator,
        test_australia_gst_calculator,
        test_zakat_calculator,
        test_murabaha_calculator,
        test_takaful_calculator,
        test_calculator_registry,
        test_meta_data_and_seo
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Phase 2 calculators are ready for production.")
        return True
    else:
        print("❌ Some tests failed. Please review and fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)