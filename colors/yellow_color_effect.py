"""
Yellow Color Effect - Solid yellow background
"""

import pygame
from effects.base_effect import EffectRenderer


class YellowColorEffect(EffectRenderer):
    """Solid yellow background effect"""
    
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.color = (255, 255, 0)  # Yellow
        
    def render(self, surface, time_elapsed, audio_data=None):
        """Render a solid yellow background"""
        surface.fill(self.color) 