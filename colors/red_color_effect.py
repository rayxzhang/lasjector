"""
Red Color Effect - Solid red background
"""

import pygame
from effects.base_effect import EffectRenderer


class RedColorEffect(EffectRenderer):
    """Solid red background effect"""
    
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.color = (255, 0, 0)  # Red
        
    def render(self, surface, time_elapsed, audio_data=None):
        """Render a solid red background"""
        surface.fill(self.color) 