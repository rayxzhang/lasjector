"""
Horizontal Rainbow Effect - Horizontal rainbow gradient across the screen
"""

import pygame
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from effects.base_effect import EffectRenderer


class HorizontalRainbowEffect(EffectRenderer):
    """Horizontal rainbow gradient effect"""
    
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.cached_surface = None
        self.cached_size = None
        
        # Define rainbow colors for horizontal gradient
        colors = [
            (1, 0, 0),     # red
            (1, 0.5, 0),   # orange
            (1, 1, 0),     # yellow
            (0, 1, 0),     # green
            (0, 1, 1),     # cyan
            (0, 0, 1),     # blue
            (1, 0, 1)      # magenta
        ]
        positions = [0, 0.15, 0.3, 0.45, 0.6, 0.75, 1.0]  # Normalized horizontal positions
        
        # Create custom horizontal rainbow colormap
        self.cmap = LinearSegmentedColormap.from_list("horizontal_rainbow", list(zip(positions, colors)))
    
    def generate_horizontal_rainbow(self, width, height):
        """
        Generates a horizontal rainbow gradient.

        Args:
            width (int): Width of the image.
            height (int): Height of the image.

        Returns:
            np.ndarray: RGB image array of the gradient.
        """
        # Create horizontal coordinate grid (0 to 1)
        x = np.linspace(0, 1, width)
        y = np.linspace(0, 1, height)
        xx, yy = np.meshgrid(x, y)

        # Use x-coordinate for the gradient (horizontal)
        gradient_x = xx

        # Apply colormap to get RGB values
        gradient_rgb = self.cmap(gradient_x)
        
        return gradient_rgb

    def render(self, surface, time_elapsed, audio_data=None):
        """Render a static horizontal rainbow gradient"""
        # Get actual surface dimensions
        surface_width, surface_height = surface.get_size()
        current_size = (surface_width, surface_height)
        
        # Check if we need to regenerate the cached surface
        if self.cached_surface is None or self.cached_size != current_size:
            # Generate the horizontal rainbow gradient
            gradient_rgb = self.generate_horizontal_rainbow(surface_height, surface_width)
            
            # Convert to pygame surface format (0-255, integer)
            gradient_rgb_255 = (gradient_rgb[:, :, :3] * 255).astype(np.uint8) 
            
            # Create pygame surface from numpy array
            self.cached_surface = pygame.surfarray.make_surface(gradient_rgb_255)
            self.cached_size = current_size
        
        # Blit the cached gradient onto the main surface
        surface.blit(self.cached_surface, (0, 0)) 