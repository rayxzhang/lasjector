"""
Base effect class for Lasjector effects
All effects should inherit from this class
"""

import pygame
import math
import time


class EffectRenderer:
    """Base class for rendering effects - OVERRIDE THIS TO CREATE YOUR OWN EFFECTS"""
    
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.width, self.height = screen_size
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.time_elapsed = 0
        
    def render(self, surface, time_elapsed, audio_data=None):
        """
        Override this method to create your own effects!
        
        Args:
            surface: pygame surface to draw on
            time_elapsed: time since start in seconds
            audio_data: AudioProcessor object with volume, beat_detected, frequencies, bpm, bpm_confidence
        """
        # Default effect: transparent overlay with audio-reactive circle
        # Note: This effect should be rendered on top of a color background
        
        # Example: draw a circle that pulses with BPM
        if audio_data:
            # Use BPM to create rhythmic pulsing
            beat_progress = audio_data.get_beat_progress()
            pulse_intensity = abs(math.sin(beat_progress * math.pi * 2))
            
            # Color based on beat detection and BPM confidence
            if audio_data.beat_detected:
                color = (255, 100, 100)  # Bright red on beat
            elif audio_data.bpm_confidence > 0.5:
                # Use BPM-based color cycling
                hue = (time_elapsed * audio_data.bpm / 60.0) % 360
                # Simple HSV to RGB conversion
                h = hue / 60.0
                i = int(h)
                f = h - i
                if i == 0:
                    color = (255, int(255 * f), 0)
                elif i == 1:
                    color = (int(255 * (1 - f)), 255, 0)
                elif i == 2:
                    color = (0, 255, int(255 * f))
                elif i == 3:
                    color = (0, int(255 * (1 - f)), 255)
                elif i == 4:
                    color = (int(255 * f), 0, 255)
                else:
                    color = (255, 0, int(255 * (1 - f)))
            else:
                color = (100, 100, 100)  # Gray when no clear rhythm
            
            # Size based on volume and beat progress
            base_radius = 30
            volume_scale = min(2.0, audio_data.volume * 10)
            beat_scale = 1.0 + pulse_intensity * 0.5
            radius = int(base_radius * volume_scale * beat_scale)
        else:
            color = (100, 100, 100)
            radius = 30
            
        pygame.draw.circle(surface, color, (self.center_x, self.center_y), radius) 