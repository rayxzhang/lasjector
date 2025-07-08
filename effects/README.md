# Lasjector Effects

This folder contains all the visual effects for Lasjector. Each effect is in its own file for better organization and modularity.

## Structure

- `__init__.py` - Makes this a Python package
- `base_effect.py` - Base class that all effects inherit from
- `pulse_effect.py` - Pulse effect with radial gradient
- `effects_registry.py` - Registry to manage all available effects
- `README.md` - This documentation file

## Adding a New Effect

To add a new effect:

1. **Create a new effect file** (e.g., `my_effect.py`):
```python
"""
My Effect - Description of what this effect does
"""

import pygame
from .base_effect import EffectRenderer

class MyEffect(EffectRenderer):
    """My custom effect"""
    
    def __init__(self, screen_size):
        super().__init__(screen_size)
        # Initialize your effect here
        
    def render(self, surface, time_elapsed, audio_data=None):
        """Render your effect"""
        # Fill background
        surface.fill((5, 5, 10))
        
        # Your effect code here
        # Use audio_data for audio responsiveness:
        # - audio_data.volume: Current volume (0.0 to 1.0)
        # - audio_data.beat_detected: True when beat is detected
        # - audio_data.bpm: Current BPM
        # - audio_data.bpm_confidence: Confidence in BPM detection (0.0 to 1.0)
        # - audio_data.get_beat_progress(): Progress through current beat (0.0 to 1.0)
        # - audio_data.is_on_beat(): True if currently on a beat
```

2. **Register the effect** in `effects_registry.py`:
```python
from .my_effect import MyEffect

class EffectsRegistry:
    def __init__(self):
        self.effects = {
            "Default": EffectRenderer,
            "Pulse": PulseEffect,
            "My Effect": MyEffect,  # Add your effect here
        }
```

3. **Test your effect** by running the application and selecting it from the dropdown.

## Available Effects

### Default
- Basic pulsing circle effect
- Responds to audio with color changes and size scaling
- Good starting point for understanding the system

### Pulse
- Smooth radial rainbow gradient
- Uses matplotlib colormap for professional color transitions
- Red in center, cycling through rainbow to edges
- Circular gradient that fits within the smallest screen dimension
- Maintains perfect circle shape on any aspect ratio



## Audio Data Available

All effects receive an `audio_data` object with these properties:

- `volume`: Current audio volume (0.0 to 1.0)
- `beat_detected`: True when a beat is detected
- `bpm`: Current detected BPM
- `bpm_confidence`: Confidence in BPM detection (0.0 to 1.0)
- `frequencies`: Array of frequency data for spectrum analysis
- `get_beat_progress()`: Returns progress through current beat (0.0 to 1.0)
- `is_on_beat(tolerance=0.1)`: Returns True if currently on a beat

## Tips for Creating Effects

1. **Always call `super().__init__(screen_size)`** in your effect's `__init__`
2. **Fill the background** with `surface.fill((5, 5, 10))` for consistency
3. **Use `self.center_x` and `self.center_y`** for screen center coordinates
4. **Handle `audio_data=None`** gracefully for when no audio is available
5. **Use `time_elapsed`** for time-based animations
6. **Keep effects performant** - they run at 60 FPS
7. **Test on different resolutions** - effects should scale properly 