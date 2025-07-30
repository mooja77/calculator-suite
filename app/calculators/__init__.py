# Calculators package
# Import all calculators to ensure they are registered

from .base import BaseCalculator
from .registry import calculator_registry, register_calculator

# Import all calculator implementations
from .percentage import PercentageCalculator
from .paycheck import PaycheckCalculator
from .sip import SipCalculator
from .rentvsbuy import RentvsbuyCalculator
from .studentloan import StudentloanCalculator
from .retirement401k import Retirement401kCalculator

# Import new regional tax calculators
from .uk_vat import UkVatCalculator
from .canada_gst import CanadaGstCalculator
from .australia_gst import AustraliaGstCalculator

# Import Islamic finance calculators
from .zakat import ZakatCalculator
from .murabaha import MurabahaCalculator
from .takaful import TakafulCalculator

# Import money management calculators
from .budget import BudgetCalculator
from .emergencyfund import EmergencyFundCalculator
from .debtpayoff import DebtPayoffCalculator
from .creditcardpayoff import CreditCardPayoffCalculator

# Import housing calculators
from .houseaffordability import HouseaffordabilityCalculator
from .caraffordability import CaraffordabilityCalculator
from .autoloanvslease import AutoloanvsleaseCalculator

# Import business calculators
from .breakeven import BreakevenCalculator
from .freelancerate import FreelancerateCalculator

__all__ = [
    'BaseCalculator',
    'calculator_registry',
    'register_calculator',
    'PercentageCalculator',
    'PaycheckCalculator',
    'SipCalculator',
    'RentvsbuyCalculator',
    'StudentloanCalculator',
    'Retirement401kCalculator',
    'UkVatCalculator',
    'CanadaGstCalculator',
    'AustraliaGstCalculator',
    'ZakatCalculator',
    'MurabahaCalculator',
    'TakafulCalculator',
    'BudgetCalculator',
    'EmergencyFundCalculator',
    'DebtPayoffCalculator',
    'CreditCardPayoffCalculator',
    'HouseaffordabilityCalculator',
    'CaraffordabilityCalculator',
    'AutoloanvsleaseCalculator',
    'BreakevenCalculator',
    'FreelancerateCalculator'
]