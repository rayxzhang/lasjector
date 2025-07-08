"""
Spinning Square Effect - Rotating square outline
"""

import pygame
import math
from effects.base_effect import EffectRenderer


class SpinningSquareEffect(EffectRenderer):
    """Spinning square outline effect"""
    
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.rotation_speed = 90  # degrees per second
        self.square_size = 750
        self.line_thickness = 3
        
    def render(self, surface, time_elapsed, audio_data=None):
        """Render a spinning square outline"""
        # Calculate current rotation angle
        rotation_angle = (time_elapsed * self.rotation_speed) % 360
        
        # Create a temporary surface for the mask
        temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Fill everything with black
        temp_surface.fill((0, 0, 0, 255))
        
        # Calculate square corners
        half_size = self.square_size // 2
        square_points = [
            (-half_size, -half_size),  # top-left
            (half_size, -half_size),   # top-right
            (half_size, half_size),    # bottom-right
            (-half_size, half_size)    # bottom-left
        ]
        
        # Rotate the square points
        rotated_points = []
        for point in square_points:
            x, y = point
            # Rotate around origin
            cos_a = math.cos(math.radians(rotation_angle))
            sin_a = math.sin(math.radians(rotation_angle))
            rotated_x = x * cos_a - y * sin_a
            rotated_y = x * sin_a + y * cos_a
            # Translate to center of screen
            rotated_points.append((rotated_x + self.center_x, rotated_y + self.center_y))
        
        # Draw the square outline as transparent (cutout)
        if len(rotated_points) >= 4:
            # Draw transparent square outline
            pygame.draw.polygon(temp_surface, (0, 0, 0, 0), rotated_points, self.line_thickness)
        
        # Blit the mask onto the main surface
        surface.blit(temp_surface, (0, 0)) 