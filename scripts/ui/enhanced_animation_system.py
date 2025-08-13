"""
Enhanced Animation Framework - Phase 2.3 UI Overhaul
Professional animation system with easing functions, timelines, and visual effects.

Features:
- Advanced easing functions for smooth, natural motion
- Timeline-based animation sequencing and choreography
- Property animation system for any object attribute
- UI transition system with coordinated effects
- Particle system for visual effects
- Performance optimized with object pooling
"""

import pygame
import math
import time
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from scripts.core.config import *
from enum import Enum
import random

class EasingType(Enum):
    """Easing function types for natural animation curves"""
    LINEAR = "linear"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    EASE_IN_QUART = "ease_in_quart"
    EASE_OUT_QUART = "ease_out_quart"
    EASE_IN_OUT_QUART = "ease_in_out_quart"
    EASE_OUT_BOUNCE = "ease_out_bounce"
    EASE_OUT_ELASTIC = "ease_out_elastic"
    EASE_IN_BACK = "ease_in_back"
    EASE_OUT_BACK = "ease_out_back"

class AnimationType(Enum):
    """Types of animations for visual effects"""
    POSITION = "position"
    SCALE = "scale"
    ROTATION = "rotation"
    ALPHA = "alpha"
    COLOR = "color"
    SIZE = "size"
    CUSTOM = "custom"

class AnimationState(Enum):
    """Animation lifecycle states"""
    PENDING = "pending"      # Waiting to start
    RUNNING = "running"      # Currently animating
    PAUSED = "paused"        # Temporarily stopped
    COMPLETED = "completed"  # Finished successfully
    CANCELLED = "cancelled"  # Stopped before completion

class EasingFunctions:
    """Collection of easing functions for smooth animations"""
    
    @staticmethod
    def linear(t: float) -> float:
        """Linear interpolation - constant speed"""
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease in - slow start, accelerating"""
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease out - fast start, decelerating"""
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease in/out - slow start and end"""
        if t < 0.5:
            return 2 * t * t
        return 1 - pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease in - very slow start"""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease out - very fast start, slow end"""
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease in/out - smooth acceleration and deceleration"""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def ease_in_quart(t: float) -> float:
        """Quartic ease in - extremely slow start"""
        return t * t * t * t
    
    @staticmethod
    def ease_out_quart(t: float) -> float:
        """Quartic ease out - extremely fast start"""
        return 1 - pow(1 - t, 4)
    
    @staticmethod
    def ease_in_out_quart(t: float) -> float:
        """Quartic ease in/out - very smooth curve"""
        if t < 0.5:
            return 8 * t * t * t * t
        return 1 - pow(-2 * t + 2, 4) / 2
    
    @staticmethod
    def ease_out_bounce(t: float) -> float:
        """Bounce ease out - bouncing effect at end"""
        n1 = 7.5625
        d1 = 2.75
        
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t = t - 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t = t - 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t = t - 2.625 / d1
            return n1 * t * t + 0.984375
    
    @staticmethod
    def ease_out_elastic(t: float) -> float:
        """Elastic ease out - spring-like oscillation"""
        c4 = (2 * math.pi) / 3
        
        if t == 0:
            return 0
        elif t == 1:
            return 1
        else:
            return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1
    
    @staticmethod
    def ease_in_back(t: float) -> float:
        """Back ease in - slight overshoot at start"""
        c1 = 1.70158
        c3 = c1 + 1
        
        return c3 * t * t * t - c1 * t * t
    
    @staticmethod
    def ease_out_back(t: float) -> float:
        """Back ease out - slight overshoot at end"""
        c1 = 1.70158
        c3 = c1 + 1
        
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    @classmethod
    def get_function(cls, easing_type: EasingType) -> Callable[[float], float]:
        """Get easing function by type"""
        function_map = {
            EasingType.LINEAR: cls.linear,
            EasingType.EASE_IN_QUAD: cls.ease_in_quad,
            EasingType.EASE_OUT_QUAD: cls.ease_out_quad,
            EasingType.EASE_IN_OUT_QUAD: cls.ease_in_out_quad,
            EasingType.EASE_IN_CUBIC: cls.ease_in_cubic,
            EasingType.EASE_OUT_CUBIC: cls.ease_out_cubic,
            EasingType.EASE_IN_OUT_CUBIC: cls.ease_in_out_cubic,
            EasingType.EASE_IN_QUART: cls.ease_in_quart,
            EasingType.EASE_OUT_QUART: cls.ease_out_quart,
            EasingType.EASE_IN_OUT_QUART: cls.ease_in_out_quart,
            EasingType.EASE_OUT_BOUNCE: cls.ease_out_bounce,
            EasingType.EASE_OUT_ELASTIC: cls.ease_out_elastic,
            EasingType.EASE_IN_BACK: cls.ease_in_back,
            EasingType.EASE_OUT_BACK: cls.ease_out_back
        }
        return function_map.get(easing_type, cls.linear)

class AnimationKeyframe:
    """Single keyframe in an animation timeline"""
    
    def __init__(self, time_offset: float, value: Any, easing: EasingType = EasingType.LINEAR):
        self.time_offset = time_offset  # Time offset from animation start (0.0 to 1.0)
        self.value = value  # Target value at this keyframe
        self.easing = easing  # Easing function to reach this keyframe

class PropertyAnimation:
    """Animates a specific property of an object over time"""
    
    def __init__(self, target_object: Any, property_name: str, start_value: Any, 
                 end_value: Any, duration: float, easing: EasingType = EasingType.LINEAR,
                 delay: float = 0.0):
        # Animation target
        self.target_object = target_object
        self.property_name = property_name
        self.start_value = start_value
        self.end_value = end_value
        
        # Timing
        self.duration = duration
        self.delay = delay
        self.start_time = None
        
        # Animation settings
        self.easing = easing
        self.easing_function = EasingFunctions.get_function(easing)
        
        # State
        self.state = AnimationState.PENDING
        self.current_progress = 0.0
        
        # Callbacks
        self.on_start = None
        self.on_update = None
        self.on_complete = None
        
        # Keyframes for complex animations
        self.keyframes = []  # List of AnimationKeyframe objects
        
        # Animation ID for tracking
        self.animation_id = f"anim_{int(time.time() * 1000)}_{id(self)}"
    
    def add_keyframe(self, time_offset: float, value: Any, easing: EasingType = EasingType.LINEAR):
        """Add a keyframe for complex multi-stage animations"""
        keyframe = AnimationKeyframe(time_offset, value, easing)
        self.keyframes.append(keyframe)
        # Sort keyframes by time offset
        self.keyframes.sort(key=lambda k: k.time_offset)
        return self
    
    def set_callback(self, event: str, callback: Callable):
        """Set animation event callbacks"""
        if event == "start":
            self.on_start = callback
        elif event == "update":
            self.on_update = callback
        elif event == "complete":
            self.on_complete = callback
        return self
    
    def start(self):
        """Start the animation"""
        self.start_time = time.time()
        self.state = AnimationState.RUNNING
        if self.on_start:
            self.on_start(self)
    
    def update(self, current_time: float) -> bool:
        """Update animation state and return True if still running"""
        if self.state != AnimationState.RUNNING:
            return False
        
        if self.start_time is None:
            return False
        
        # Calculate elapsed time accounting for delay
        elapsed = current_time - self.start_time - self.delay
        
        if elapsed < 0:
            # Still in delay period
            return True
        
        # Calculate progress (0.0 to 1.0)
        if self.duration <= 0:
            progress = 1.0
        else:
            progress = min(1.0, elapsed / self.duration)
        
        self.current_progress = progress
        
        # Calculate current value
        if self.keyframes:
            current_value = self._interpolate_keyframes(progress)
        else:
            # Simple start to end interpolation
            eased_progress = self.easing_function(progress)
            current_value = self._interpolate_values(self.start_value, self.end_value, eased_progress)
        
        # Apply value to target object
        try:
            if hasattr(self.target_object, self.property_name):
                setattr(self.target_object, self.property_name, current_value)
            elif isinstance(self.target_object, dict):
                self.target_object[self.property_name] = current_value
        except Exception as e:
            print(f"Animation error: Could not set {self.property_name} on {self.target_object}: {e}")
        
        # Trigger update callback
        if self.on_update:
            self.on_update(self, current_value, progress)
        
        # Check if animation is complete
        if progress >= 1.0:
            self.state = AnimationState.COMPLETED
            if self.on_complete:
                self.on_complete(self)
            return False
        
        return True
    
    def _interpolate_keyframes(self, progress: float) -> Any:
        """Interpolate between keyframes for complex animations"""
        if not self.keyframes:
            return self.start_value
        
        # Find the current keyframe segment
        prev_keyframe = None
        next_keyframe = None
        
        for keyframe in self.keyframes:
            if keyframe.time_offset <= progress:
                prev_keyframe = keyframe
            else:
                next_keyframe = keyframe
                break
        
        # Determine interpolation values
        if prev_keyframe is None:
            # Before first keyframe
            start_val = self.start_value
            end_val = self.keyframes[0].value
            segment_start = 0.0
            segment_end = self.keyframes[0].time_offset
            easing_func = EasingFunctions.get_function(self.keyframes[0].easing)
        elif next_keyframe is None:
            # After last keyframe
            start_val = prev_keyframe.value
            end_val = self.end_value
            segment_start = prev_keyframe.time_offset
            segment_end = 1.0
            easing_func = self.easing_function
        else:
            # Between keyframes
            start_val = prev_keyframe.value
            end_val = next_keyframe.value
            segment_start = prev_keyframe.time_offset
            segment_end = next_keyframe.time_offset
            easing_func = EasingFunctions.get_function(next_keyframe.easing)
        
        # Calculate segment progress
        if segment_end <= segment_start:
            segment_progress = 1.0
        else:
            segment_progress = (progress - segment_start) / (segment_end - segment_start)
        
        # Apply easing and interpolate
        eased_progress = easing_func(segment_progress)
        return self._interpolate_values(start_val, end_val, eased_progress)
    
    def _interpolate_values(self, start: Any, end: Any, progress: float) -> Any:
        """Interpolate between two values based on their types"""
        if isinstance(start, (int, float)) and isinstance(end, (int, float)):
            # Numeric interpolation
            return start + (end - start) * progress
        elif isinstance(start, tuple) and isinstance(end, tuple):
            # Tuple interpolation (for colors, positions, etc.)
            if len(start) == len(end):
                return tuple(start[i] + (end[i] - start[i]) * progress for i in range(len(start)))
        elif isinstance(start, pygame.Color) and isinstance(end, pygame.Color):
            # Color interpolation
            r = start.r + (end.r - start.r) * progress
            g = start.g + (end.g - start.g) * progress
            b = start.b + (end.b - start.b) * progress
            a = start.a + (end.a - start.a) * progress
            return pygame.Color(int(r), int(g), int(b), int(a))
        
        # Fallback: discrete transition at 50% progress
        return end if progress >= 0.5 else start
    
    def pause(self):
        """Pause the animation"""
        self.state = AnimationState.PAUSED
    
    def resume(self):
        """Resume the animation"""
        if self.state == AnimationState.PAUSED:
            self.state = AnimationState.RUNNING
    
    def cancel(self):
        """Cancel the animation"""
        self.state = AnimationState.CANCELLED

class Particle:
    """Individual particle for visual effects"""
    
    def __init__(self, x: float, y: float, velocity_x: float = 0.0, velocity_y: float = 0.0,
                 life_span: float = 1.0, color: Tuple[int, int, int, int] = (255, 255, 255, 255),
                 size: float = 2.0):
        # Position and movement
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.acceleration_x = 0.0
        self.acceleration_y = 0.0
        
        # Visual properties
        self.color = list(color)  # [R, G, B, A]
        self.size = size
        self.initial_size = size
        
        # Lifecycle
        self.life_span = life_span
        self.age = 0.0
        self.is_alive = True
        
        # Animation properties
        self.fade_rate = 1.0 / life_span  # Alpha reduction per second
        self.size_change_rate = 0.0  # Size change per second
        self.gravity = 0.0  # Downward acceleration
    
    def update(self, dt: float):
        """Update particle state"""
        if not self.is_alive:
            return
        
        # Update age
        self.age += dt
        
        # Update position
        self.velocity_y += self.gravity * dt
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Update visual properties
        self.size = max(0, self.size + self.size_change_rate * dt)
        
        # Fade out over lifetime
        life_progress = self.age / self.life_span
        if life_progress >= 1.0:
            self.is_alive = False
        else:
            # Fade alpha
            self.color[3] = int((1.0 - life_progress) * 255)
    
    def render(self, screen: pygame.Surface):
        """Render the particle"""
        if not self.is_alive or self.size <= 0:
            return
        
        # Create particle surface with alpha
        particle_size = max(1, int(self.size * 2))
        particle_surface = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)
        
        # Draw particle as circle
        center = (particle_size // 2, particle_size // 2)
        radius = max(1, int(self.size))
        pygame.draw.circle(particle_surface, self.color, center, radius)
        
        # Blit to screen
        screen.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    """Manages collections of particles for visual effects"""
    
    def __init__(self, max_particles: int = 1000):
        self.particles = []
        self.max_particles = max_particles
        
        # Emission settings
        self.emission_rate = 10  # Particles per second
        self.emission_accumulator = 0.0
        self.is_emitting = False
        
        # Default particle properties
        self.emit_position = (0, 0)
        self.emit_velocity_range = ((-50, -50), (50, 50))  # ((min_x, min_y), (max_x, max_y))
        self.particle_life_span_range = (1.0, 3.0)  # (min, max)
        self.particle_color = (255, 255, 255, 255)
        self.particle_size_range = (1.0, 3.0)
        self.gravity = 100.0  # Downward acceleration
    
    def start_emission(self, position: Tuple[float, float]):
        """Start emitting particles at the specified position"""
        self.emit_position = position
        self.is_emitting = True
    
    def stop_emission(self):
        """Stop emitting new particles"""
        self.is_emitting = False
    
    def emit_burst(self, position: Tuple[float, float], count: int):
        """Emit a burst of particles instantly"""
        for _ in range(count):
            self._create_particle(position)
    
    def _create_particle(self, position: Tuple[float, float]):
        """Create a new particle with random properties"""
        if len(self.particles) >= self.max_particles:
            return
        
        # Random velocity
        vel_min, vel_max = self.emit_velocity_range
        velocity_x = random.uniform(vel_min[0], vel_max[0])
        velocity_y = random.uniform(vel_min[1], vel_max[1])
        
        # Random life span
        life_span = random.uniform(*self.particle_life_span_range)
        
        # Random size
        size = random.uniform(*self.particle_size_range)
        
        # Create particle
        particle = Particle(position[0], position[1], velocity_x, velocity_y, life_span, self.particle_color, size)
        particle.gravity = self.gravity
        
        self.particles.append(particle)
    
    def update(self, dt: float):
        """Update all particles"""
        # Update existing particles
        for particle in self.particles[:]:  # Copy list to avoid modification during iteration
            particle.update(dt)
            if not particle.is_alive:
                self.particles.remove(particle)
        
        # Emit new particles if active
        if self.is_emitting:
            self.emission_accumulator += dt * self.emission_rate
            while self.emission_accumulator >= 1.0:
                self._create_particle(self.emit_position)
                self.emission_accumulator -= 1.0
    
    def render(self, screen: pygame.Surface):
        """Render all particles"""
        for particle in self.particles:
            particle.render(screen)
    
    def clear(self):
        """Remove all particles"""
        self.particles.clear()

class AnimationManager:
    """Main animation system manager"""
    
    def __init__(self, event_system):
        # Core system references
        self.event_system = event_system
        
        # Animation management
        self.active_animations = []  # Currently running animations
        self.animation_groups = {}  # Named groups of animations
        self.paused = False
        
        # Particle systems
        self.particle_systems = {}  # Named particle systems
        
        # Performance tracking
        self.animation_count = 0
        self.particle_count = 0
        
        # Register for events
        self.event_system.subscribe('pause_animations', self._handle_pause_animations)
        self.event_system.subscribe('resume_animations', self._handle_resume_animations)
        self.event_system.subscribe('clear_animations', self._handle_clear_animations)
        
        print("Enhanced Animation System initialized - Phase 2.3 advancement ready!")
    
    def animate(self, target_object: Any, property_name: str, start_value: Any, 
                end_value: Any, duration: float, easing: EasingType = EasingType.LINEAR,
                delay: float = 0.0, group: str = None) -> PropertyAnimation:
        """Create and start a property animation"""
        animation = PropertyAnimation(target_object, property_name, start_value, end_value, 
                                    duration, easing, delay)
        
        # Add to group if specified
        if group:
            if group not in self.animation_groups:
                self.animation_groups[group] = []
            self.animation_groups[group].append(animation)
        
        # Start animation
        animation.start()
        self.active_animations.append(animation)
        
        return animation
    
    def create_particle_system(self, name: str, max_particles: int = 1000) -> ParticleSystem:
        """Create a named particle system"""
        particle_system = ParticleSystem(max_particles)
        self.particle_systems[name] = particle_system
        return particle_system
    
    def get_particle_system(self, name: str) -> Optional[ParticleSystem]:
        """Get a particle system by name"""
        return self.particle_systems.get(name)
    
    def fade_in(self, target_object: Any, duration: float = 0.5, 
                easing: EasingType = EasingType.EASE_OUT_QUAD) -> PropertyAnimation:
        """Fade in an object (assumes alpha property)"""
        return self.animate(target_object, "alpha", 0, 255, duration, easing)
    
    def fade_out(self, target_object: Any, duration: float = 0.5,
                 easing: EasingType = EasingType.EASE_IN_QUAD) -> PropertyAnimation:
        """Fade out an object (assumes alpha property)"""
        return self.animate(target_object, "alpha", 255, 0, duration, easing)
    
    def slide_in(self, target_object: Any, from_position: Tuple[float, float], 
                 to_position: Tuple[float, float], duration: float = 0.8,
                 easing: EasingType = EasingType.EASE_OUT_BACK) -> PropertyAnimation:
        """Slide an object from one position to another"""
        # Set initial position
        if hasattr(target_object, 'x') and hasattr(target_object, 'y'):
            target_object.x, target_object.y = from_position
            return self.animate(target_object, "position", from_position, to_position, duration, easing)
        return None
    
    def bounce(self, target_object: Any, scale_factor: float = 1.2, duration: float = 0.3) -> PropertyAnimation:
        """Create a bounce effect (assumes scale property)"""
        animation = self.animate(target_object, "scale", 1.0, scale_factor, duration / 2, EasingType.EASE_OUT_QUAD)
        
        # Create return animation
        def on_complete(anim):
            self.animate(target_object, "scale", scale_factor, 1.0, duration / 2, EasingType.EASE_IN_QUAD)
        
        animation.set_callback("complete", on_complete)
        return animation
    
    def pulse(self, target_object: Any, pulse_scale: float = 1.1, duration: float = 1.0,
              repeat_count: int = -1) -> PropertyAnimation:
        """Create a pulsing effect that repeats"""
        # This would need a more complex animation chain system
        # For now, return a simple scale animation
        return self.animate(target_object, "scale", 1.0, pulse_scale, duration / 2, EasingType.EASE_IN_OUT_QUAD)
    
    def stop_animation_group(self, group: str):
        """Stop all animations in a named group"""
        if group in self.animation_groups:
            for animation in self.animation_groups[group]:
                animation.cancel()
            del self.animation_groups[group]
    
    def update(self, dt: float):
        """Update all animations and particle systems"""
        if self.paused:
            return
        
        current_time = time.time()
        
        # Update animations
        for animation in self.active_animations[:]:  # Copy to avoid modification during iteration
            if not animation.update(current_time):
                # Animation finished, remove it
                self.active_animations.remove(animation)
                
                # Remove from groups
                for group_name, group_animations in self.animation_groups.items():
                    if animation in group_animations:
                        group_animations.remove(animation)
        
        # Clean up empty groups
        empty_groups = [name for name, group in self.animation_groups.items() if not group]
        for group_name in empty_groups:
            del self.animation_groups[group_name]
        
        # Update particle systems
        for particle_system in self.particle_systems.values():
            particle_system.update(dt)
        
        # Update performance counters
        self.animation_count = len(self.active_animations)
        self.particle_count = sum(len(ps.particles) for ps in self.particle_systems.values())
    
    def render_particles(self, screen: pygame.Surface):
        """Render all particle systems"""
        for particle_system in self.particle_systems.values():
            particle_system.render(screen)
    
    def _handle_pause_animations(self, event_data):
        """Handle animation pause requests"""
        self.paused = True
        for animation in self.active_animations:
            animation.pause()
    
    def _handle_resume_animations(self, event_data):
        """Handle animation resume requests"""
        self.paused = False
        for animation in self.active_animations:
            animation.resume()
    
    def _handle_clear_animations(self, event_data):
        """Handle clear all animations requests"""
        for animation in self.active_animations:
            animation.cancel()
        self.active_animations.clear()
        self.animation_groups.clear()
        
        # Clear particle systems
        for particle_system in self.particle_systems.values():
            particle_system.clear()

# Convenience functions for common animations
class AnimationPresets:
    """Pre-configured animations for common UI patterns"""
    
    @staticmethod
    def button_press(button_object: Any, animation_manager: AnimationManager) -> PropertyAnimation:
        """Standard button press animation"""
        return animation_manager.bounce(button_object, 0.95, 0.1)
    
    @staticmethod
    def notification_slide_in(notification_object: Any, animation_manager: AnimationManager,
                            from_x: float = 400) -> PropertyAnimation:
        """Notification slide in from right"""
        current_x = getattr(notification_object, 'x', 0)
        return animation_manager.animate(notification_object, 'x', from_x, current_x, 0.6, EasingType.EASE_OUT_BACK)
    
    @staticmethod
    def panel_fade_in(panel_object: Any, animation_manager: AnimationManager) -> PropertyAnimation:
        """Standard panel fade in"""
        return animation_manager.fade_in(panel_object, 0.4, EasingType.EASE_OUT_QUAD)
    
    @staticmethod
    def success_flash(target_object: Any, animation_manager: AnimationManager) -> PropertyAnimation:
        """Green flash for success feedback"""
        original_color = getattr(target_object, 'color', (255, 255, 255, 255))
        flash_color = (100, 255, 100, 255)  # Green flash
        
        animation = animation_manager.animate(target_object, 'color', original_color, flash_color, 0.1, EasingType.EASE_OUT_QUAD)
        
        def return_to_original(anim):
            animation_manager.animate(target_object, 'color', flash_color, original_color, 0.3, EasingType.EASE_IN_QUAD)
        
        animation.set_callback("complete", return_to_original)
        return animation
    
    @staticmethod
    def error_shake(target_object: Any, animation_manager: AnimationManager) -> PropertyAnimation:
        """Shake effect for error feedback"""
        original_x = getattr(target_object, 'x', 0)
        shake_distance = 5
        
        # Create shake sequence
        animation = animation_manager.animate(target_object, 'x', original_x, original_x + shake_distance, 0.05, EasingType.LINEAR)
        
        def shake_sequence(anim):
            # Shake left and right multiple times
            anim1 = animation_manager.animate(target_object, 'x', original_x + shake_distance, original_x - shake_distance, 0.05, EasingType.LINEAR)
            
            def continue_shake(anim):
                anim2 = animation_manager.animate(target_object, 'x', original_x - shake_distance, original_x + shake_distance, 0.05, EasingType.LINEAR)
                
                def final_return(anim):
                    animation_manager.animate(target_object, 'x', original_x + shake_distance, original_x, 0.05, EasingType.LINEAR)
                
                anim2.set_callback("complete", final_return)
            
            anim1.set_callback("complete", continue_shake)
        
        animation.set_callback("complete", shake_sequence)
        return animation

# Example usage and testing
if __name__ == "__main__":
    # Example of creating animations
    
    # Mock object for testing
    class MockObject:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.alpha = 255
            self.scale = 1.0
            self.color = (255, 255, 255, 255)
    
    # Mock event system
    class MockEventSystem:
        def subscribe(self, event, handler):
            pass
    
    # Create animation manager
    anim_manager = AnimationManager(MockEventSystem())
    
    # Create test object
    test_object = MockObject()
    
    # Create various animations
    fade_anim = anim_manager.fade_out(test_object, 2.0)
    bounce_anim = anim_manager.bounce(test_object, 1.5, 0.5)
    
    # Create particle system
    particles = anim_manager.create_particle_system("test_particles", 500)
    particles.emit_burst((100, 100), 50)
    
    print("Enhanced Animation System examples created successfully!")