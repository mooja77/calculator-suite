#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Calculator Suite tests
"""

import pytest
import sys
import os

# Add the parent directory to sys.path to import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_simple_fixed import app, calculation_logs


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture(autouse=True)
def clear_logs():
    """Clear calculation logs before each test"""
    calculation_logs.clear()
    yield
    calculation_logs.clear()


@pytest.fixture
def sample_loan_inputs():
    """Sample valid loan calculator inputs"""
    return {
        'loan_amount': '100000',
        'annual_rate': '5.0',
        'loan_term_years': '30',
        'loan_type': 'mortgage'
    }


@pytest.fixture
def sample_mortgage_inputs():
    """Sample valid mortgage calculator inputs"""
    return {
        'home_price': '400000',
        'down_payment_percent': '20',
        'annual_rate': '6.5',
        'loan_term_years': '30'
    }


@pytest.fixture
def sample_retirement_inputs():
    """Sample valid retirement calculator inputs"""
    return {
        'current_age': '35',
        'retirement_age': '65',
        'current_savings': '50000',
        'monthly_contribution': '1000',
        'annual_return': '7'
    }


@pytest.fixture
def sample_investment_inputs():
    """Sample valid investment calculator inputs"""
    return {
        'calculation_type': 'future_value',
        'initial_investment': '10000',
        'annual_return': '8',
        'years': '10',
        'additional_contributions': '500'
    }