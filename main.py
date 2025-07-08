#!/usr/bin/env python3
"""
Lasjector - Clean Base for Custom Effects
A minimal foundation for building your own projector laser effects
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import numpy as np
import threading
import time
import math
import random
import pyaudio
from scipy.fft import fft
import sys
import os
import json
import librosa
from effects.effects_registry import effects_registry
from colors.colors_registry import colors_registry

class AudioProcessor:
    """Advanced audio processor with librosa BPM detection"""
    
    def __init__(self, chunk_size=1024, sample_rate=44100):
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.running = False
        self.beat_detected = False
        self.volume = 0.0
        self.frequencies = np.zeros(chunk_size // 2)
        
        # Librosa BPM detection
        self.bpm = 120.0
        self.bpm_confidence = 0.0
        self.beat_times = []
        self.last_beat_time = 0
        self.beat_interval = 0.5  # seconds between beats
        
        # Audio buffer for librosa analysis
        self.audio_buffer = []
        self.buffer_duration = 3.0  # seconds of audio to analyze
        self.buffer_samples = int(self.buffer_duration * self.sample_rate)
        
        # Audio components
        self.audio = None
        self.stream = None
        self.current_device_name = "Default"
        
    def start_audio(self, device_index=None):
        """Start audio capture"""
        try:
            print("Starting audio capture...")
            print(f"Requested device index: {device_index}")
            
            self.audio = pyaudio.PyAudio()
            
            # Use provided device_index if available
            device_to_use = device_index
            
            if device_to_use is None:
                print("No device index provided, using default logic...")
                # Try to find default input device
                try:
                    device_info = self.audio.get_default_input_device_info()
                    device_to_use = device_info['index']
                    self.current_device_name = device_info['name']
                    print(f"Using default device: {self.current_device_name} (index: {device_to_use})")
                except:
                    print("No default device found, searching for first available device...")
                    # Fallback to first available device
                    for i in range(self.audio.get_device_count()):
                        try:
                            device_info = self.audio.get_device_info_by_index(i)
                            if device_info['maxInputChannels'] > 0:
                                device_to_use = i
                                self.current_device_name = device_info['name']
                                print(f"Using first available device: {self.current_device_name} (index: {device_to_use})")
                                break
                        except:
                            continue
            else:
                print(f"Using provided device index: {device_to_use}")
            
            if device_to_use is None:
                print("No audio input devices found")
                return False
            
            # Get device name for the selected device
            if device_to_use is not None:
                try:
                    device_info = self.audio.get_device_info_by_index(device_to_use)
                    self.current_device_name = device_info['name']
                    print(f"Selected device: {self.current_device_name} (index: {device_to_use})")
                except:
                    self.current_device_name = f"Device {device_to_use}"
                    print(f"Could not get device name for index {device_to_use}")
            
            # Open audio stream
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_to_use,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.running = True
            self.stream.start_stream()
            print(f"✅ Audio started on: {self.current_device_name}")
            return True
            
        except Exception as e:
            print(f"Audio start failed: {e}")
            return False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Process audio data with librosa BPM detection"""
        try:
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            current_time = time.time()
            
            # Calculate volume
            self.volume = np.sqrt(np.mean(audio_data**2))
            
            # FFT for frequency analysis
            fft_data = np.abs(fft(audio_data))
            self.frequencies = fft_data[:len(fft_data)//2]
            
            # Add to audio buffer for librosa analysis
            self.audio_buffer.extend(audio_data)
            
            # Keep buffer size manageable
            if len(self.audio_buffer) > self.buffer_samples:
                self.audio_buffer = self.audio_buffer[-self.buffer_samples:]
            
            # Analyze BPM when we have enough data
            if len(self.audio_buffer) >= self.buffer_samples:
                self.analyze_bpm_with_librosa()
            
            # Simple beat detection for immediate response
            bass_energy = np.sum(self.frequencies[:20])
            threshold = np.mean(self.frequencies) * 2.0
            old_beat = self.beat_detected
            self.beat_detected = bass_energy > threshold
            
            if self.beat_detected and not old_beat:
                self.last_beat_time = current_time
                print(f"🎵 Beat detected! BPM: {self.bpm:.1f} (confidence: {self.bpm_confidence:.2f})")
            
            return (None, pyaudio.paContinue)
            
        except Exception as e:
            print(f"Audio callback error: {e}")
            return (None, pyaudio.paContinue)
    
    def analyze_bpm_with_librosa(self):
        """Analyze BPM using librosa beat tracking"""
        try:
            if len(self.audio_buffer) < self.buffer_samples:
                return
            
            # Convert buffer to numpy array
            audio_array = np.array(self.audio_buffer, dtype=np.float32)
            
            # Use librosa to detect tempo and beats
            tempo, beats = librosa.beat.beat_track(y=audio_array, sr=self.sample_rate)
            
            # Update BPM with smoothing
            tempo_value = float(tempo.item() if hasattr(tempo, 'item') else tempo)
            if 60 <= tempo_value <= 200:  # Reasonable BPM range
                self.bpm = self.bpm * 0.8 + tempo_value * 0.2
                self.beat_interval = 60.0 / self.bpm
                
                # Calculate confidence based on beat consistency
                if len(beats) > 1:
                    beat_intervals = np.diff(beats)
                    interval_std = np.std(beat_intervals)
                    interval_mean = np.mean(beat_intervals)
                    
                    # Confidence based on regularity (lower std = higher confidence)
                    if interval_mean > 0:
                        regularity = 1.0 - min(1.0, interval_std / interval_mean)
                        self.bpm_confidence = max(0.0, min(1.0, regularity))
            else:
                self.bpm_confidence = 0.0
        except Exception as e:
            print(f"Librosa BPM analysis error: {e}")
    
    def get_beat_progress(self):
        """Get progress through current beat (0.0 to 1.0)"""
        current_time = time.time()
        time_since_last_beat = current_time - self.last_beat_time
        
        if time_since_last_beat > self.beat_interval:
            # Reset if we've missed a beat
            self.last_beat_time = current_time
            return 0.0
        
        return time_since_last_beat / self.beat_interval
    
    def is_on_beat(self, tolerance=0.1):
        """Check if we're currently on a beat"""
        progress = self.get_beat_progress()
        return progress <= tolerance or progress >= (1.0 - tolerance)
    
    def stop_audio(self):
        """Stop audio capture"""
        self.running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()

# Effects are now imported from the effects package

class ProjectorRenderer:
    """Handles rendering to the projector (second monitor)"""
    
    def __init__(self):
        self.screen = None
        self.running = False
        self.color_effect = None
        self.overlay_effect = None
        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.initialized = False
        
    def initialize_projector(self):
        """Initialize pygame and projector window"""
        try:
            pygame.init()
            
            # Get displays
            displays = pygame.display.get_desktop_sizes()
            if len(displays) < 2:
                messagebox.showwarning("Display Warning", 
                    "Only one display detected. Connect your projector and extend display.")
                return False
                
            # Use second display
            projector_size = displays[1] if len(displays) > 1 else displays[0]
            
            # Create window on second monitor
            os.environ['SDL_VIDEO_WINDOW_POS'] = f'{displays[0][0]},0'
            self.screen = pygame.display.set_mode(projector_size, pygame.NOFRAME)
            pygame.display.set_caption("Lasjector")
            
            self.initialized = True
            
            print(f"✅ Projector initialized: {projector_size}")
            return True
            
        except Exception as e:
            print(f"Projector initialization failed: {e}")
            return False
            
    def render_frame(self, audio_data=None):
        """Render one frame with layered effects"""
        if not self.screen:
            return
            
        time_elapsed = time.time() - self.start_time
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
        
        # Render color layer first (background)
        if self.color_effect:
            self.color_effect.render(self.screen, time_elapsed, audio_data)
        
        # Render overlay effect on top
        if self.overlay_effect:
            self.overlay_effect.render(self.screen, time_elapsed, audio_data)
        
        pygame.display.flip()
        self.clock.tick(60)
    
    def cleanup(self):
        """Clean up"""
        self.running = False
        if self.screen:
            pygame.quit()

class ControlDashboard:
    """Control dashboard for the primary monitor"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lasjector Control")
        self.root.geometry("700x600")
        
        self.renderer = ProjectorRenderer()
        self.audio_processor = AudioProcessor()
        
        self.running = False
        self.render_thread = None
        self.audio_devices = []  # Store available audio devices
        self.preview_running = False
        self.preview_thread = None
        self.config_file = "lasjector_config.json"
        self.default_device = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the control dashboard UI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎪 Lasjector - Custom Effects Base", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Control buttons
        self.start_button = ttk.Button(main_frame, text="🚀 Start Show", 
                                      command=self.start_system)
        self.start_button.grid(row=1, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(main_frame, text="⏹️ Stop", 
                                     command=self.stop_system, state="disabled")
        self.stop_button.grid(row=1, column=1, padx=(0, 10))
        
        # Audio checkbox
        self.audio_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="🎵 Audio Sync", 
                       variable=self.audio_enabled).grid(row=1, column=2)
        
        # Audio device selection
        ttk.Label(main_frame, text="Audio Device:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(20, 5))
        
        self.audio_device_var = tk.StringVar(value="Auto")
        self.audio_device_combo = ttk.Combobox(main_frame, textvariable=self.audio_device_var, 
                                              state="readonly", width=50)
        self.audio_device_combo.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Audio device controls
        audio_controls_frame = ttk.Frame(main_frame)
        audio_controls_frame.grid(row=3, column=2, sticky=(tk.W, tk.E), padx=(10, 0))
        
        ttk.Button(audio_controls_frame, text="🔄 Restart Audio", 
                  command=self.restart_audio).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(audio_controls_frame, text="💾 Set as Default", 
                  command=self.set_default_device).grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(audio_controls_frame, text="🗑️ Clear Default", 
                  command=self.clear_default_device).grid(row=0, column=2)
        
        # Audio preview section
        ttk.Label(main_frame, text="Audio Preview:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(20, 5))
        
        preview_frame = ttk.Frame(main_frame)
        preview_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Preview controls
        self.preview_button = ttk.Button(preview_frame, text="🎵 Start Preview", 
                                        command=self.toggle_audio_preview)
        self.preview_button.grid(row=0, column=0, padx=(0, 10))
        
        # Volume meter
        ttk.Label(preview_frame, text="Volume:").grid(row=0, column=1, padx=(10, 5))
        self.volume_meter = ttk.Progressbar(preview_frame, length=200, mode='determinate')
        self.volume_meter.grid(row=0, column=2, padx=(0, 10))
        
        # Volume label
        self.volume_label = ttk.Label(preview_frame, text="0.000")
        self.volume_label.grid(row=0, column=3, padx=(0, 10))
        
        # Beat indicator
        ttk.Label(preview_frame, text="Beat:").grid(row=0, column=4, padx=(10, 5))
        self.beat_indicator = ttk.Label(preview_frame, text="●", foreground="gray")
        self.beat_indicator.grid(row=0, column=5, padx=(0, 10))
        
        # BPM display
        ttk.Label(preview_frame, text="BPM:").grid(row=0, column=6, padx=(10, 5))
        self.bpm_label = ttk.Label(preview_frame, text="120.0")
        self.bpm_label.grid(row=0, column=7, padx=(0, 10))
        
        # BPM confidence
        ttk.Label(preview_frame, text="Conf:").grid(row=0, column=8, padx=(10, 5))
        self.confidence_label = ttk.Label(preview_frame, text="0.00")
        self.confidence_label.grid(row=0, column=9, padx=(0, 10))
        
        # Frequency bars (simplified)
        freq_frame = ttk.Frame(main_frame)
        freq_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(freq_frame, text="Frequency Response:").grid(row=0, column=0, sticky=tk.W)
        
        # Create frequency bars
        self.freq_bars = []
        freq_bar_frame = ttk.Frame(freq_frame)
        freq_bar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        for i in range(8):  # 8 frequency bands
            bar = ttk.Progressbar(freq_bar_frame, length=60, mode='determinate', maximum=100)
            bar.grid(row=0, column=i, padx=2)
            self.freq_bars.append(bar)
        
        # Effect selection - split into Effects and Colors sections
        ttk.Label(main_frame, text="Effects & Colors:", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky=tk.W, pady=(20, 5))
        
        # Define a custom style for the selected effect button
        style = ttk.Style()
        style.configure('SelectedEffect.TButton', background='#aee1fb')
        style.map('SelectedEffect.TButton', background=[('active', '#7ec8e3')])
        
        # Effects section
        effects_frame = ttk.LabelFrame(main_frame, text="Effects", padding="5")
        effects_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.effect_buttons = {}
        for i, effect_name in enumerate(["Default", "Pulse", "Spinning Square"]):
            button_frame = ttk.Frame(effects_frame)
            button_frame.grid(row=0, column=i, padx=5, pady=5)
            btn = ttk.Button(button_frame, 
                           text=effect_name, 
                           command=lambda name=effect_name: self.select_effect(name),
                           width=12)
            btn.grid(row=0, column=0)
            self.effect_buttons[effect_name] = btn
        
        # Colors section
        colors_frame = ttk.LabelFrame(main_frame, text="Colors", padding="5")
        colors_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.color_buttons = {}
        for i, color_name in enumerate(colors_registry.get_available_colors()):
            button_frame = ttk.Frame(colors_frame)
            button_frame.grid(row=0, column=i, padx=5, pady=5)
            btn = ttk.Button(button_frame, 
                           text=color_name, 
                           command=lambda name=color_name: self.select_color(name),
                           width=12)
            btn.grid(row=0, column=0)
            self.color_buttons[color_name] = btn
        
        # Set initial selections
        self.current_effect = "Default"
        self.current_color = "Base Color"
        self.highlight_selected_effect()
        self.highlight_selected_color()
        
        # Status display
        ttk.Label(main_frame, text="Status:", font=("Arial", 10, "bold")).grid(row=10, column=0, sticky=tk.W, pady=(20, 5))
        
        self.status_text = tk.Text(main_frame, height=8, width=80)
        self.status_text.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=11, column=3, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Load default device and populate audio devices
        self.load_default_device()
        self.populate_audio_devices()
        
    def populate_audio_devices(self):
        """Populate the audio device dropdown"""
        try:
            import pyaudio
            audio = pyaudio.PyAudio()
            
            devices = ["Auto - Let app choose best option"]
            device_info_list = [{"name": "Auto", "index": -1}]
            
            # Get all input devices
            for i in range(audio.get_device_count()):
                try:
                    device_info = audio.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        device_name = device_info['name']
                        devices.append(f"🎤 {device_name}")
                        device_info_list.append({
                            "name": device_name,
                            "index": i,
                            "info": device_info
                        })
                except Exception as e:
                    continue
            
            # Store device info for later use
            self.audio_devices = device_info_list
            
            # Update combobox
            self.audio_device_combo['values'] = devices
            
            # Set default device if available
            if self.default_device:
                # Find the default device in the list
                default_found = False
                for device in self.audio_devices:
                    if device['name'] == self.default_device:
                        self.audio_device_var.set(f"🎤 {device['name']}")
                        default_found = True
                        self.log_status(f"✅ Set to default device: {device['name']}")
                        break
                
                if not default_found:
                    self.log_status(f"⚠️ Default device '{self.default_device}' not found, using Auto")
                    self.audio_device_var.set("Auto - Let app choose best option")
            else:
                self.audio_device_var.set("Auto - Let app choose best option")
            
            if len(devices) > 1:
                self.log_status(f"Found {len(devices)-1} audio input devices")
            else:
                self.log_status("No audio input devices found")
                
            audio.terminate()
            
        except Exception as e:
            self.log_status(f"Error loading audio devices: {e}")
            self.audio_device_combo['values'] = ["Auto - Let app choose best option"]
    
    def restart_audio(self):
        """Restart audio capture"""
        if self.running:
            self.log_status("Restarting audio capture...")
            
            # Stop current audio
            self.audio_processor.stop_audio()
            
            # Get selected device
            selected_device = self.audio_device_var.get()
            device_index = None
            
            self.log_status(f"Selected device from UI: {selected_device}")
            
            # Find the selected device index
            if selected_device != "Auto - Let app choose best option":
                for device in self.audio_devices:
                    if device['name'] in selected_device:
                        device_index = device['index']
                        self.log_status(f"Found device: {device['name']} (index: {device_index})")
                        break
                if device_index is None:
                    self.log_status(f"⚠️ Could not find device index for: {selected_device}")
            else:
                # Use default device if available
                device_index = self.get_default_device_index()
                if device_index is not None:
                    self.log_status(f"Using default device index: {device_index}")
                else:
                    self.log_status("No default device set, will use auto selection")
            
            # Start audio capture
            if self.audio_enabled.get():
                if self.audio_processor.start_audio(device_index):
                    self.log_status(f"✅ Audio restarted: {self.audio_processor.current_device_name}")
                else:
                    self.log_status("⚠️ Audio restart failed")
            else:
                self.log_status("Audio sync is disabled")
        else:
            self.log_status("System not running - start the show first")
    
    def load_default_device(self):
        """Load default device from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.default_device = config.get('default_audio_device')
                    if self.default_device:
                        self.log_status(f"📁 Loaded default device: {self.default_device}")
        except Exception as e:
            self.log_status(f"⚠️ Could not load config: {e}")
            self.default_device = None
    
    def save_default_device(self):
        """Save default device to config file"""
        try:
            config = {'default_audio_device': self.default_device}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.log_status(f"💾 Saved default device: {self.default_device}")
        except Exception as e:
            self.log_status(f"❌ Could not save config: {e}")
    
    def set_default_device(self):
        """Set currently selected device as default"""
        selected_device = self.audio_device_var.get()
        
        if selected_device == "Auto - Let app choose best option":
            self.log_status("⚠️ Cannot set 'Auto' as default device")
            return
        
        # Extract device name from the display text
        device_name = selected_device.replace("🎤 ", "").replace("🎵 ", "")
        
        self.default_device = device_name
        self.save_default_device()
        self.log_status(f"✅ Set default device: {device_name}")
    
    def clear_default_device(self):
        """Clear the default device setting"""
        self.default_device = None
        self.save_default_device()
        self.log_status("🗑️ Cleared default device")
        
        # Reset dropdown to Auto
        self.audio_device_var.set("Auto - Let app choose best option")
    
    def get_default_device_index(self):
        """Get the device index for the default device"""
        if not self.default_device:
            return None
            
        for device in self.audio_devices:
            if device['name'] == self.default_device:
                return device['index']
        return None
    
    def select_effect(self, effect_name):
        """Select an effect and update the UI"""
        self.current_effect = effect_name
        self.highlight_selected_effect()
        
        # Update the overlay effect if the system is running
        if self.running and self.renderer.overlay_effect:
            if effect_name != "None":
                self.renderer.overlay_effect = effects_registry.get_effect(effect_name, self.renderer.screen.get_size())
            else:
                self.renderer.overlay_effect = None
            self.log_status(f"🎨 Switched to {effect_name} effect")
        else:
            self.log_status(f"🎨 Selected {effect_name} effect (will apply when show starts)")
    
    def highlight_selected_effect(self):
        """Highlight the currently selected effect button"""
        for effect_name, button in self.effect_buttons.items():
            if effect_name == self.current_effect:
                button.config(style='SelectedEffect.TButton')
            else:
                button.config(style='TButton')
    
    def select_color(self, color_name):
        """Select a color and update the UI"""
        self.current_color = color_name
        self.highlight_selected_color()
        
        # Update the color effect if the system is running
        if self.running and self.renderer.color_effect:
            self.renderer.color_effect = colors_registry.get_color(color_name, self.renderer.screen.get_size())
            self.log_status(f"🎨 Switched to {color_name} color")
        else:
            self.log_status(f"🎨 Selected {color_name} color (will apply when show starts)")
    
    def highlight_selected_color(self):
        """Highlight the currently selected color button"""
        for color_name, button in self.color_buttons.items():
            if color_name == self.current_color:
                button.config(style='SelectedEffect.TButton')
            else:
                button.config(style='TButton')
    
    def toggle_audio_preview(self):
        """Toggle audio preview on/off"""
        if not self.preview_running:
            self.start_audio_preview()
        else:
            self.stop_audio_preview()
    
    def start_audio_preview(self):
        """Start audio preview"""
        if self.preview_running:
            return
            
        # Get selected device
        selected_device = self.audio_device_var.get()
        device_index = None
        
        # Find the selected device index
        if selected_device != "Auto - Let app choose best option":
            for device in self.audio_devices:
                if device['name'] in selected_device:
                    device_index = device['index']
                    break
        else:
            # Use default device if available
            device_index = self.get_default_device_index()
        
        # Start audio capture for preview
        if self.audio_processor.start_audio(device_index):
            self.preview_running = True
            self.preview_button.config(text="⏹️ Stop Preview")
            self.log_status(f"🎵 Audio preview started: {self.audio_processor.current_device_name}")
            
            # Start preview update thread
            self.preview_thread = threading.Thread(target=self.preview_update_loop, daemon=True)
            self.preview_thread.start()
        else:
            self.log_status("❌ Failed to start audio preview")
    
    def stop_audio_preview(self):
        """Stop audio preview"""
        if not self.preview_running:
            return
            
        self.preview_running = False
        self.audio_processor.stop_audio()
        self.preview_button.config(text="🎵 Start Preview")
        
        # Reset UI elements
        self.volume_meter['value'] = 0
        self.volume_label.config(text="0.000")
        self.beat_indicator.config(text="●", foreground="gray")
        self.bpm_label.config(text="120.0")
        self.confidence_label.config(text="0.00")
        for bar in self.freq_bars:
            bar['value'] = 0
        
        self.log_status("🛑 Audio preview stopped")
    
    def preview_update_loop(self):
        """Update audio preview UI elements"""
        while self.preview_running:
            try:
                # Update volume meter
                volume = self.audio_processor.volume
                volume_percent = min(100, volume * 1000)  # Scale for display
                
                # Update UI (must be done in main thread)
                self.root.after(0, self.update_preview_ui, volume, volume_percent)
                
                time.sleep(0.05)  # Update 20 times per second
            except Exception as e:
                print(f"Preview update error: {e}")
                break
    
    def update_preview_ui(self, volume, volume_percent):
        """Update preview UI elements (called from main thread)"""
        try:
            # Update volume meter
            self.volume_meter['value'] = volume_percent
            self.volume_label.config(text=f"{volume:.3f}")
            
            # Update beat indicator
            if self.audio_processor.beat_detected:
                self.beat_indicator.config(text="●", foreground="red")
            else:
                self.beat_indicator.config(text="●", foreground="gray")
            
            # Update BPM display
            bpm_value = float(self.audio_processor.bpm.item() if hasattr(self.audio_processor.bpm, 'item') else self.audio_processor.bpm)
            confidence_value = float(self.audio_processor.bpm_confidence.item() if hasattr(self.audio_processor.bpm_confidence, 'item') else self.audio_processor.bpm_confidence)
            self.bpm_label.config(text=f"{bpm_value:.1f}")
            self.confidence_label.config(text=f"{confidence_value:.2f}")
            
            # Update frequency bars
            frequencies = self.audio_processor.frequencies
            if len(frequencies) > 0:
                # Divide frequencies into 8 bands
                band_size = len(frequencies) // 8
                for i in range(8):
                    start_idx = i * band_size
                    end_idx = start_idx + band_size
                    band_energy = np.mean(frequencies[start_idx:end_idx]) if end_idx <= len(frequencies) else 0
                    bar_value = min(100, band_energy * 100)  # Scale for display
                    self.freq_bars[i]['value'] = bar_value
                    
        except Exception as e:
            print(f"UI update error: {e}")
    
    def log_status(self, message):
        """Add message to status display"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_system(self):
        """Start the laser show"""
        self.log_status("Starting custom effects show...")
        
        # Initialize projector with layered effects
        if not self.renderer.initialize_projector():
            self.log_status("❌ Failed to initialize projector")
            return
            
        # Set up color layer (background)
        self.renderer.color_effect = colors_registry.get_color(self.current_color, self.renderer.screen.get_size())
        
        # Set up overlay effect (transparent layer on top)
        if self.current_effect != "None":
            self.renderer.overlay_effect = effects_registry.get_effect(self.current_effect, self.renderer.screen.get_size())
        
        self.log_status(f"✅ Projector initialized with {self.current_color} color and {self.current_effect} effect")
        
        # Initialize audio if enabled
        if self.audio_enabled.get():
            # Get selected device
            selected_device = self.audio_device_var.get()
            device_index = None
            
            # Find the selected device index
            if selected_device != "Auto - Let app choose best option":
                for device in self.audio_devices:
                    if device['name'] in selected_device:
                        device_index = device['index']
                        break
            else:
                # Use default device if available
                device_index = self.get_default_device_index()
            
            if self.audio_processor.start_audio(device_index):
                self.log_status(f"✅ Audio started: {self.audio_processor.current_device_name}")
            else:
                self.log_status("⚠️ Audio failed - continuing without audio")
        
        # Start render thread
        self.running = True
        self.renderer.running = True
        self.render_thread = threading.Thread(target=self.render_loop, daemon=True)
        self.render_thread.start()
        
        # Update UI
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        self.log_status("🎉 Show started! Press ESC on projector to stop.")
        self.log_status("💡 Override EffectRenderer.render() to create your own effects!")
    
    def render_loop(self):
        """Main rendering loop"""
        while self.running and self.renderer.running:
            try:
                audio_data = self.audio_processor if self.audio_enabled.get() else None
                self.renderer.render_frame(audio_data)
                time.sleep(0.001)
            except Exception as e:
                self.log_status(f"❌ Render error: {e}")
                break
                
        self.log_status("🛑 Rendering stopped")
    
    def stop_system(self):
        """Stop the laser show"""
        self.log_status("Stopping show...")
        
        self.running = False
        self.renderer.running = False
        
        if self.render_thread and self.render_thread.is_alive():
            self.render_thread.join(timeout=2)
            
        # Stop preview if running
        if self.preview_running:
            self.stop_audio_preview()
            
        self.audio_processor.stop_audio()
        self.renderer.cleanup()
        
        # Update UI
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        self.log_status("✅ System stopped")
        
    def run(self):
        """Start the dashboard"""
        self.log_status("🎪 Welcome to Lasjector!")
        self.log_status("Connect your projector and click 'Start Show' to begin")
        self.log_status("💡 Override EffectRenderer.render() to create your own effects!")
        self.log_status("🎵 Use 'Start Preview' to test audio input before starting the show!")
        self.log_status("💾 Use 'Set as Default' to save your preferred audio device!")
        self.log_status("🎼 Professional BPM detection using librosa beat tracking!")
        self.log_status("🌈 Try the new 'Pulse' effect with radial rainbow gradients!")
        
        try:
            self.root.mainloop()
        finally:
            self.stop_system()

def main():
    """Main entry point"""
    try:
        # Check dependencies
        required_modules = ['pygame', 'numpy', 'pyaudio', 'scipy', 'librosa', 'matplotlib']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
                
        if missing_modules:
            print("❌ Missing required modules:")
            for module in missing_modules:
                print(f"  - {module}")
            print("\n📦 Install with: pip install pygame numpy pyaudio scipy librosa matplotlib")
            return
            
        # Start application
        app = ControlDashboard()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Application error: {e}")

if __name__ == "__main__":
    main()