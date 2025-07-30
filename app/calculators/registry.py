class CalculatorRegistry:
    """Registry for all calculator classes"""
    
    def __init__(self):
        self._calculators = {}
    
    def register(self, calculator_class):
        """Register a calculator class"""
        instance = calculator_class()
        self._calculators[instance.slug] = calculator_class
        return calculator_class
    
    def get(self, slug):
        """Get calculator class by slug"""
        return self._calculators.get(slug)
    
    def get_all(self):
        """Get all registered calculators"""
        return self._calculators
    
    def list_slugs(self):
        """Get list of all calculator slugs"""
        return list(self._calculators.keys())

# Global registry instance
calculator_registry = CalculatorRegistry()

# Decorator for easy registration
def register_calculator(calculator_class):
    """Decorator to register calculator classes"""
    return calculator_registry.register(calculator_class)