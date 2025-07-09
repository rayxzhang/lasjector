"""
Radial Gradient Effect - Smooth radial gradient using matplotlib colormap
"""

import pygame
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from effects.base_effect import EffectRenderer


class RadialGradientEffect(EffectRenderer):
    """Smooth radial gradient effect using matplotlib colormap"""
    
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.max_radius = min(self.width, self.height) // 2
        self.cached_surface = None
        self.cached_size = None
        
        # Define custom colormap for smooth radial gradient
        colors = [
            (1, 0, 0),     # red
            (1, 0.5, 0),   # orange
            (1, 1, 0),     # yellow
            (0, 1, 0),     # green
            (0, 1, 1),     # cyan
            (0, 0, 1),     # blue
            (1, 0, 1)      # magenta
        ]
        positions = [0, 0.15, 0.3, 0.45, 0.6, 0.75, 1.0]  # Normalized radial positions
        
        # Create custom radial gradient colormap
        self.cmap = LinearSegmentedColormap.from_list("radial_gradient", list(zip(positions, colors)))
    
    def generate_radial_gradient_circular(self, height, width, zoom_factor=1):
        """
        Generates a smooth radial (circular) gradient that fits within the smallest dimension.
        The outermost ring fills the remaining space.

        Args:
            height (int): Height of the image.
            width (int): Width of the image.
            zoom_factor (float): Zoom factor for the gradient (higher = more zoomed in).

        Returns:
            np.ndarray: RGB image array of the gradient.
        """
        # Create coordinate grid centered at (0,0)
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        xx, yy = np.meshgrid(x, y)

        # Normalize radius using the smaller dimension to keep it circular
        min_dim = min(width, height)
        norm_xx = xx * (width / min_dim)
        norm_yy = yy * (height / min_dim)
        radius = np.sqrt(norm_xx**2 + norm_yy**2)
        
        # Apply zoom factor
        radius = radius * zoom_factor
        radius = np.clip(radius, 0, 1)

        # Apply colormap to get RGB values
        gradient_rgb = self.cmap(radius)
        
        return gradient_rgb

    def render(self, surface, time_elapsed, audio_data=None):
        """Render a static smooth radial gradient using matplotlib colormap"""
        # Get actual surface dimensions
        surface_width, surface_height = surface.get_size()
        current_size = (surface_width, surface_height)
        
        # Check if we need to regenerate the cached surface
        if self.cached_surface is None or self.cached_size != current_size:
            # Generate the circular gradient (static)
            # Height is expected before width when generating the gradient.
            # Passing the dimensions in this order keeps the circular
            # gradient oriented correctly on any aspect ratio.
            gradient_rgb = self.generate_radial_gradient_circular(
                surface_height,
                surface_width,
                0.65,
            )
            
            # Convert to pygame surface format (0-255, integer)
            gradient_rgb_255 = (gradient_rgb[:, :, :3] * 255).astype(np.uint8) 
            
            # Create pygame surface from numpy array
            self.cached_surface = pygame.surfarray.make_surface(gradient_rgb_255)
            self.cached_size = current_size
        
        # Blit the cached gradient onto the main surface        surface.blit(self.cached_surface, (0, 0)) 