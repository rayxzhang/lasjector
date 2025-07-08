"""
Blue Color Effect - Solid blue background
"""

import pygame
from effects.base_effect import EffectRenderer


class BlueColorEffect(EffectRenderer):
    """Solid blue background effect"""
    
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.color = (0, 0, 255)  # Blue
        
    def render(self, surface, time_elapsed, audio_data=None):
        """Render a solid blue background"""
        surface.fill(self.color) 