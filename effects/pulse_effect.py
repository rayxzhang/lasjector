"""
Pulse Effect - Growing circle outline that expands from center
"""

import pygame
import math
from effects.base_effect import EffectRenderer


class PulseEffect(EffectRenderer):
    """Growing circle outline effect that expands from center"""
    
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.pulse_radius = 0
        self.pulse_speed = 500  # pixels per second
        self.max_radius = math.sqrt(self.width**1.82 + self.height**1.82)  # Diagonal distance to ensure it goes out of frame
        self.line_thickness = 3
        
    def render(self, surface, time_elapsed, audio_data=None):
        """Render a growing circle outline cutout"""
        # Calculate current pulse radius based on time
        self.pulse_radius = (time_elapsed * self.pulse_speed) % self.max_radius
        
        # Create a temporary surface for the mask
        temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Fill everything with black
        temp_surface.fill((0, 0, 0, 255))
        
        # Draw the circle outline as transparent (cutout)
        if self.pulse_radius > 0:
            # Draw transparent circle outline
            pygame.draw.circle(temp_surface, (0, 0, 0, 0), (self.center_x, self.center_y), 
                             int(self.pulse_radius), self.line_thickness)
        
        # Blit the mask onto the main surface
        surface.blit(temp_surface, (0, 0)) 