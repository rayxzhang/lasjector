"""
Green Color Effect - Solid green background
"""

import pygame
from effects.base_effect import EffectRenderer


class GreenColorEffect(EffectRenderer):
    """Solid green background effect"""
    
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.color = (0, 255, 0)  # Green
        
    def render(self, surface, time_elapsed, audio_data=None):
        """Render a solid green background"""
        surface.fill(self.color) 