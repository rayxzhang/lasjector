"""
Base Color Effect - Simple solid color background
"""

import pygame
import numpy as np
from effects.base_effect import EffectRenderer


class BaseColorEffect(EffectRenderer):
    """Simple solid color background effect"""
    
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.base_color = (50, 50, 100)  # Default blue-gray
        
    def render(self, surface, time_elapsed, audio_data=None):
        """Render a solid color background"""
        # Fill with base color
        surface.fill(self.base_color)
        
        # Optionally add subtle audio reactivity
        if audio_data and hasattr(audio_data, 'volume'):
            # Slightly brighten based on volume
            brightness_factor = 1.0 + (audio_data.volume * 0.3)
            reactive_color = tuple(int(c * brightness_factor) for c in self.base_color)
            surface.fill(reactive_color) 