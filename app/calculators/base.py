from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
from app.cache import cache_calculation

class BaseCalculator(ABC):
    """Base class for all calculators"""
    
    def __init__(self):
        self.slug = self.__class__.__name__.lower().replace('calculator', '')
        self.errors = []
    
    @abstractmethod
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the calculation"""
        pass
    
    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate input data"""
        pass
    
    @abstractmethod
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data"""
        pass
    
    @abstractmethod
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup"""
        pass
    
    def get_content_blocks(self) -> List[str]:
        """Return content block IDs to render"""
        return [f"{self.slug}_intro", f"{self.slug}_guide", f"{self.slug}_faq"]
    
    def to_json(self, result: Dict[str, Any]) -> str:
        """Convert result to JSON for API responses"""
        return json.dumps(result, ensure_ascii=False)
    
    def clear_errors(self):
        """Clear validation errors"""
        self.errors = []
    
    def add_error(self, message: str):
        """Add validation error"""
        self.errors.append(message)
    
    def validate_number(self, value, field_name: str, min_val=None, max_val=None) -> float:
        """Validate and convert a number input"""
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                self.add_error(f"{field_name} must be at least {min_val}")
                return None
            if max_val is not None and num > max_val:
                self.add_error(f"{field_name} must be at most {max_val}")
                return None
            return num
        except (ValueError, TypeError):
            self.add_error(f"{field_name} must be a valid number")
            return None