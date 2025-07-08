"""
Colors Registry - Manages all available color effects
"""

from .base_color_effect import BaseColorEffect
from .radial_gradient_effect import RadialGradientEffect
from .horizontal_rainbow_effect import HorizontalRainbowEffect


class ColorsRegistry:
    """Registry for all available color effects"""
    
    def __init__(self):
        self.colors = {
            "Base Color": BaseColorEffect,
            "Radial Gradient": RadialGradientEffect,
            "Horizontal Rainbow": HorizontalRainbowEffect,
        }
    
    def get_color(self, color_name, screen_size):
        """Get a color effect instance by name"""
        if color_name in self.colors:
            return self.colors[color_name](screen_size)
        else:
            # Fallback to base color
            return self.colors["Base Color"](screen_size)
    
    def get_available_colors(self):
        """Get list of available color names"""
        return list(self.colors.keys())
    
    def register_color(self, name, color_class):
        """Register a new color effect"""
        self.colors[name] = color_class


# Global registry instance
colors_registry = ColorsRegistry() 