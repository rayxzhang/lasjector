"""
Effects Registry - Manages all available effects
"""

from .base_effect import EffectRenderer
from .pulse_effect import PulseEffect
from .spinning_square_effect import SpinningSquareEffect


class EffectsRegistry:
    """Registry for all available effects"""
    
    def __init__(self):
        self.effects = {
            "Default": EffectRenderer,
            "Pulse": PulseEffect,
            "Spinning Square": SpinningSquareEffect,
        }
    
    def get_effect(self, effect_name, screen_size):
        """Get an effect instance by name"""
        if effect_name in self.effects:
            return self.effects[effect_name](screen_size)
        else:
            # Fallback to default effect
            return self.effects["Default"](screen_size)
    
    def get_available_effects(self):
        """Get list of available effect names"""
        return list(self.effects.keys())
    
    def register_effect(self, name, effect_class):
        """Register a new effect"""
        self.effects[name] = effect_class


# Global registry instance
effects_registry = EffectsRegistry() 