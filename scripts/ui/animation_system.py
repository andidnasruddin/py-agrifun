"""
Animation System - Visual polish and smooth transitions for UI elements
Provides professional animations and visual feedback for enhanced user experience.

This system implements:
- Smooth UI element transitions (fade in/out, slide, scale)
- Button hover and click animations
- Panel entrance and exit animations
- Progress indicators and loading animations
- Notification animations with easing
- Achievement and feedback animations
"""

import pygame
import math
from typing import Dict, Any, List, Optional, Tuple, Callable
from scripts.core.config import *


class Animation:
    """Individual animation instance with easing and callbacks"""
    
    def __init__(self, target, property_name: str, start_value: float, end_value: float,
                 duration: float, easing_function: str = 'linear', callback: Optional[Callable] = None):
        """Initialize animation"""
        self.target = target  # Object to animate
        self.property_name = property_name  # Property to animate (e.g., 'alpha', 'x', 'y')
        self.start_value = start_value  # Starting value
        self.end_value = end_value  # Target value
        self.duration = duration  # Animation duration in seconds
        self.elapsed_time = 0.0  # Time elapsed since start
        self.is_complete = False  # Whether animation has finished
        self.callback = callback  # Function to call when animation completes
        
        # Get easing function
        self.easing_function = self._get_easing_function(easing_function)
        
        # Store original value to handle relative animations
        self.original_value = getattr(target, property_name, start_value)
    
    def _get_easing_function(self, easing_name: str):
        """Get easing function by name"""
        easing_functions = {
            'linear': lambda t: t,
            'ease_in': lambda t: t * t,
            'ease_out': lambda t: 1 - (1 - t) * (1 - t),
            'ease_in_out': lambda t: 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2,
            'bounce_out': self._bounce_out,
            'elastic_out': self._elastic_out,
            'back_out': self._back_out
        }
        return easing_functions.get(easing_name, easing_functions['linear'])
    
    def _bounce_out(self, t: float) -> float:
        """Bounce easing out"""
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            return 7.5625 * (t - 1.5/2.75) * (t - 1.5/2.75) + 0.75
        elif t < 2.5/2.75:
            return 7.5625 * (t - 2.25/2.75) * (t - 2.25/2.75) + 0.9375
        else:
            return 7.5625 * (t - 2.625/2.75) * (t - 2.625/2.75) + 0.984375
    
    def _elastic_out(self, t: float) -> float:
        """Elastic easing out"""
        if t == 0 or t == 1:
            return t
        p = 0.3
        s = p / 4
        return pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / p) + 1
    
    def _back_out(self, t: float) -> float:
        """Back easing out (slight overshoot)"""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    def update(self, dt: float) -> bool:
        """Update animation and return True if still running"""
        if self.is_complete:
            return False
        
        self.elapsed_time += dt
        progress = min(self.elapsed_time / self.duration, 1.0)
        
        # Apply easing
        eased_progress = self.easing_function(progress)
        
        # Calculate current value
        current_value = self.start_value + (self.end_value - self.start_value) * eased_progress
        
        # Set the property value
        setattr(self.target, self.property_name, current_value)
        
        # Check if animation is complete
        if progress >= 1.0:
            self.is_complete = True
            if self.callback:
                self.callback()
        
        return not self.is_complete


class UIAnimationEffect:
    """Reusable UI animation effect"""
    
    def __init__(self, element, effect_type: str, duration: float = 0.3):
        """Initialize UI animation effect"""
        self.element = element
        self.effect_type = effect_type
        self.duration = duration
        self.is_playing = False
        self.start_time = 0.0
    
    def play(self):
        """Start playing the animation effect"""
        self.is_playing = True
        self.start_time = 0.0
    
    def update(self, dt: float):
        """Update the animation effect"""
        if not self.is_playing:
            return
        
        self.start_time += dt
        progress = min(self.start_time / self.duration, 1.0)
        
        # Apply effect based on type
        if self.effect_type == 'pulse':
            scale = 1.0 + 0.1 * math.sin(progress * math.pi * 4)
            self._apply_scale(scale)
        elif self.effect_type == 'shake':
            offset_x = 5 * math.sin(progress * math.pi * 20) * (1 - progress)
            self._apply_offset(offset_x, 0)
        elif self.effect_type == 'glow':
            glow_intensity = 0.5 + 0.5 * math.sin(progress * math.pi * 2)
            self._apply_glow(glow_intensity)
        
        if progress >= 1.0:
            self.is_playing = False
    
    def _apply_scale(self, scale: float):
        """Apply scaling effect to element"""
        # This would be implemented based on the UI element type
        pass
    
    def _apply_offset(self, x: float, y: float):
        """Apply position offset to element"""
        # This would be implemented based on the UI element type
        pass
    
    def _apply_glow(self, intensity: float):
        """Apply glow effect to element"""
        # This would be implemented based on the UI element type
        pass


class NotificationAnimation:
    """Animated notification with slide-in and fade-out effects"""
    
    def __init__(self, text: str, notification_type: str = 'info', duration: float = 3.0):
        """Initialize notification animation"""
        self.text = text
        self.notification_type = notification_type
        self.duration = duration
        self.elapsed_time = 0.0
        
        # Animation properties
        self.alpha = 0.0  # Start transparent
        self.y_offset = -50.0  # Start above screen
        self.scale = 0.8  # Start smaller
        
        # Animation phases
        self.phase = 'slide_in'  # slide_in -> display -> fade_out
        self.slide_in_duration = 0.4
        self.fade_out_duration = 0.6
        
        # Visual properties
        self.colors = {
            'info': (100, 150, 255),
            'success': (100, 255, 100),
            'warning': (255, 200, 100),
            'error': (255, 100, 100)
        }
        self.background_color = self.colors.get(notification_type, self.colors['info'])
        
        self.is_complete = False
    
    def update(self, dt: float):
        """Update notification animation"""
        if self.is_complete:
            return False
        
        self.elapsed_time += dt
        
        if self.phase == 'slide_in':
            # Slide in and fade in
            progress = min(self.elapsed_time / self.slide_in_duration, 1.0)
            eased_progress = self._ease_out_back(progress)
            
            self.alpha = progress * 255
            self.y_offset = -50 + eased_progress * 50
            self.scale = 0.8 + eased_progress * 0.2
            
            if progress >= 1.0:
                self.phase = 'display'
                self.elapsed_time = 0.0
        
        elif self.phase == 'display':
            # Hold steady
            display_time = self.duration - self.slide_in_duration - self.fade_out_duration
            if self.elapsed_time >= display_time:
                self.phase = 'fade_out'
                self.elapsed_time = 0.0
        
        elif self.phase == 'fade_out':
            # Fade out and slide up
            progress = min(self.elapsed_time / self.fade_out_duration, 1.0)
            
            self.alpha = (1 - progress) * 255
            self.y_offset = progress * -30
            
            if progress >= 1.0:
                self.is_complete = True
        
        return not self.is_complete
    
    def _ease_out_back(self, t: float) -> float:
        """Easing function with slight overshoot"""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    def render(self, screen: pygame.Surface, x: int, y: int):
        """Render the animated notification"""
        if self.is_complete:
            return
        
        # Create notification surface
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, (255, 255, 255))
        
        # Calculate dimensions with padding
        padding = 15
        width = text_surface.get_width() + padding * 2
        height = text_surface.get_height() + padding * 2
        
        # Apply scale
        scaled_width = int(width * self.scale)
        scaled_height = int(height * self.scale)
        
        # Create background surface
        notification_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        
        # Draw background with rounded corners effect
        background_color = (*self.background_color, int(self.alpha * 0.9))
        pygame.draw.rect(notification_surface, background_color, 
                        notification_surface.get_rect(), border_radius=8)
        
        # Draw border
        border_color = (*self.background_color, int(self.alpha))
        pygame.draw.rect(notification_surface, border_color, 
                        notification_surface.get_rect(), width=2, border_radius=8)
        
        # Scale and alpha text
        if self.scale != 1.0:
            scaled_text = pygame.transform.scale(text_surface, 
                                               (int(text_surface.get_width() * self.scale),
                                                int(text_surface.get_height() * self.scale)))
        else:
            scaled_text = text_surface
        
        # Apply alpha to text
        scaled_text.set_alpha(int(self.alpha))
        
        # Center text on notification
        text_x = (scaled_width - scaled_text.get_width()) // 2
        text_y = (scaled_height - scaled_text.get_height()) // 2
        notification_surface.blit(scaled_text, (text_x, text_y))
        
        # Render to screen at final position
        final_y = y + self.y_offset
        screen.blit(notification_surface, (x, final_y))


class AnimationSystem:
    """Main animation system managing all UI animations"""
    
    def __init__(self, event_system):
        """Initialize animation system"""
        self.event_system = event_system
        
        # Active animations
        self.active_animations: List[Animation] = []
        self.ui_effects: List[UIAnimationEffect] = []
        self.notifications: List[NotificationAnimation] = []
        
        # Animation presets
        self.animation_presets = {
            'fade_in': {'duration': 0.3, 'easing': 'ease_out'},
            'fade_out': {'duration': 0.3, 'easing': 'ease_in'},
            'slide_in': {'duration': 0.4, 'easing': 'ease_out'},
            'slide_out': {'duration': 0.3, 'easing': 'ease_in'},
            'bounce_in': {'duration': 0.6, 'easing': 'bounce_out'},
            'scale_in': {'duration': 0.4, 'easing': 'back_out'}
        }
        
        # Subscribe to events
        self.event_system.subscribe('play_ui_animation', self._handle_ui_animation)
        self.event_system.subscribe('show_animated_notification', self._handle_animated_notification)
        
        print("Animation System initialized with smooth transitions and effects")
    
    def animate(self, target, property_name: str, end_value: float, 
                duration: float = 0.3, easing: str = 'ease_out', 
                callback: Optional[Callable] = None) -> Animation:
        """Create and start a new animation"""
        start_value = getattr(target, property_name, 0.0)
        animation = Animation(target, property_name, start_value, end_value, 
                            duration, easing, callback)
        self.active_animations.append(animation)
        return animation
    
    def animate_preset(self, target, property_name: str, end_value: float, 
                      preset: str, callback: Optional[Callable] = None) -> Animation:
        """Create animation using preset configuration"""
        preset_config = self.animation_presets.get(preset, self.animation_presets['fade_in'])
        return self.animate(target, property_name, end_value, 
                          preset_config['duration'], preset_config['easing'], callback)
    
    def fade_in(self, target, duration: float = 0.3, callback: Optional[Callable] = None):
        """Convenience method for fade in animation"""
        return self.animate(target, 'alpha', 255, duration, 'ease_out', callback)
    
    def fade_out(self, target, duration: float = 0.3, callback: Optional[Callable] = None):
        """Convenience method for fade out animation"""
        return self.animate(target, 'alpha', 0, duration, 'ease_in', callback)
    
    def slide_in(self, target, direction: str = 'up', distance: float = 100, 
                duration: float = 0.4, callback: Optional[Callable] = None):
        """Slide element in from specified direction"""
        property_name = 'y' if direction in ['up', 'down'] else 'x'
        current_value = getattr(target, property_name, 0)
        
        if direction == 'up':
            start_value = current_value + distance
        elif direction == 'down':
            start_value = current_value - distance
        elif direction == 'left':
            start_value = current_value + distance
        else:  # right
            start_value = current_value - distance
        
        setattr(target, property_name, start_value)
        return self.animate(target, property_name, current_value, duration, 'ease_out', callback)
    
    def add_ui_effect(self, element, effect_type: str, duration: float = 0.3):
        """Add a UI effect to an element"""
        effect = UIAnimationEffect(element, effect_type, duration)
        effect.play()
        self.ui_effects.append(effect)
        return effect
    
    def show_notification(self, text: str, notification_type: str = 'info', duration: float = 3.0):
        """Show an animated notification"""
        notification = NotificationAnimation(text, notification_type, duration)
        self.notifications.append(notification)
        return notification
    
    def update(self, dt: float):
        """Update all active animations"""
        # Update property animations
        self.active_animations = [anim for anim in self.active_animations if anim.update(dt)]
        
        # Update UI effects
        for effect in self.ui_effects[:]:
            effect.update(dt)
            if not effect.is_playing:
                self.ui_effects.remove(effect)
        
        # Update notifications
        self.notifications = [notif for notif in self.notifications if notif.update(dt)]
    
    def render_notifications(self, screen: pygame.Surface):
        """Render all active notifications"""
        notification_x = WINDOW_WIDTH - 320  # Right side of screen
        notification_y = 100  # Start below HUD
        
        for i, notification in enumerate(self.notifications):
            y_position = notification_y + i * 80  # Stack notifications
            notification.render(screen, notification_x, y_position)
    
    def clear_all_animations(self):
        """Clear all active animations"""
        self.active_animations.clear()
        self.ui_effects.clear()
        self.notifications.clear()
    
    def _handle_ui_animation(self, event_data: Dict[str, Any]):
        """Handle UI animation requests from events"""
        target = event_data.get('target')
        property_name = event_data.get('property', 'alpha')
        end_value = event_data.get('end_value', 255)
        duration = event_data.get('duration', 0.3)
        easing = event_data.get('easing', 'ease_out')
        
        if target:
            self.animate(target, property_name, end_value, duration, easing)
    
    def _handle_animated_notification(self, event_data: Dict[str, Any]):
        """Handle animated notification requests"""
        text = event_data.get('text', 'Notification')
        notification_type = event_data.get('type', 'info')
        duration = event_data.get('duration', 3.0)
        
        self.show_notification(text, notification_type, duration)