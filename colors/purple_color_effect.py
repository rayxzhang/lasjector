"""
Purple Color Effect - Solid purple background
"""

import pygame
from effects.base_effect import EffectRenderer


class PurpleColorEffect(EffectRenderer):
    """Solid purple background effect"""
    
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.color = (128, 0, 128)  # Purple
        
    def render(self, surface, time_elapsed, audio_data=None):
        """Render a solid purple background"""
        surface.fill(self.color) 