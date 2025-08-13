"""
Advanced Notification & Alert System - Phase 2.2 UI Overhaul
Professional notification center with animations, priorities, and rich content.

Features:
- Notification Center with message history and filtering
- Priority-based alert system with visual hierarchy
- Rich notification content with icons and actions
- Smooth animations and transitions
- Category organization and smart grouping
- Achievement celebrations and milestone tracking
"""

import pygame
import pygame_gui
from typing import Dict, List, Optional, Tuple, Any, Callable
from scripts.core.config import *
import time
import math
from enum import Enum

class NotificationPriority(Enum):
    """Priority levels for notifications"""
    LOW = 1        # Minor updates, background information
    NORMAL = 2     # Standard notifications, general updates
    HIGH = 3       # Important information requiring attention
    CRITICAL = 4   # Urgent alerts requiring immediate action
    CELEBRATION = 5 # Achievements and positive milestones

class NotificationType(Enum):
    """Categories of notifications for filtering and styling"""
    ECONOMY = "economy"           # Financial transactions, market changes
    EMPLOYEE = "employee"         # Hiring, employee status, productivity
    WEATHER = "weather"           # Season changes, weather events
    AGRICULTURE = "agriculture"   # Crop growth, harvest, soil health
    BUILDING = "building"         # Construction, upgrades, maintenance
    ACHIEVEMENT = "achievement"   # Milestones, goals, progress
    SYSTEM = "system"            # Game mechanics, save/load, errors
    TUTORIAL = "tutorial"        # Educational tips and guidance

class NotificationData:
    """Data structure for rich notification content"""
    
    def __init__(self, title: str, message: str, notification_type: NotificationType, 
                 priority: NotificationPriority = NotificationPriority.NORMAL):
        # Core notification data
        self.id = f"notif_{int(time.time() * 1000)}_{id(self)}"  # Unique identifier
        self.title = title
        self.message = message
        self.type = notification_type
        self.priority = priority
        
        # Timing information
        self.created_time = time.time()
        self.display_duration = self._get_default_duration()  # Seconds to show (0 = permanent)
        self.dismiss_time = None  # When notification was dismissed
        
        # Visual styling
        self.icon_path = None  # Path to notification icon
        self.color_override = None  # Override default color scheme
        self.size_multiplier = 1.0  # Scale factor for visual importance
        
        # Interaction
        self.is_dismissible = True  # Can be manually dismissed
        self.action_callback = None  # Function to call when clicked
        self.action_text = None  # Text for action button
        
        # Animation state
        self.animation_state = "entering"  # entering, visible, exiting, dismissed
        self.animation_progress = 0.0  # 0.0 to 1.0
        
        # Status tracking
        self.is_read = False  # Has user acknowledged this notification
        self.is_pinned = False  # Pinned notifications stay visible longer
        
    def _get_default_duration(self) -> float:
        """Get default display duration based on priority"""
        duration_map = {
            NotificationPriority.LOW: 3.0,
            NotificationPriority.NORMAL: 5.0,
            NotificationPriority.HIGH: 8.0,
            NotificationPriority.CRITICAL: 0.0,  # Permanent until dismissed
            NotificationPriority.CELEBRATION: 6.0
        }
        return duration_map.get(self.priority, 5.0)
    
    def set_icon(self, icon_path: str):
        """Set notification icon"""
        self.icon_path = icon_path
        return self
    
    def set_action(self, action_text: str, callback: Callable):
        """Add an action button to the notification"""
        self.action_text = action_text
        self.action_callback = callback
        return self
    
    def set_duration(self, duration: float):
        """Set custom display duration"""
        self.display_duration = duration
        return self
    
    def pin(self):
        """Pin notification to prevent auto-dismissal"""
        self.is_pinned = True
        self.display_duration = 0.0  # Permanent
        return self
    
    def set_color(self, color: Tuple[int, int, int, int]):
        """Override default color scheme"""
        self.color_override = color
        return self
    
    def mark_read(self):
        """Mark notification as read"""
        self.is_read = True
    
    def dismiss(self):
        """Dismiss the notification"""
        self.dismiss_time = time.time()
        self.animation_state = "exiting"
    
    def is_expired(self) -> bool:
        """Check if notification should be auto-dismissed"""
        if self.is_pinned or self.display_duration <= 0:
            return False
        return time.time() - self.created_time >= self.display_duration

class NotificationRenderer:
    """Handles visual rendering of notifications with animations"""
    
    def __init__(self):
        # Initialize fonts for notification text
        self.fonts = self._initialize_fonts()
        
        # Color schemes for different notification types
        self.color_schemes = {
            NotificationType.ECONOMY: {
                'bg': (45, 65, 45, 240),        # Dark green
                'border': (120, 200, 120, 255),
                'title': (255, 255, 255, 255),
                'text': (220, 235, 220, 255),
                'accent': (150, 255, 150, 255)
            },
            NotificationType.EMPLOYEE: {
                'bg': (65, 45, 65, 240),        # Dark purple
                'border': (200, 120, 200, 255),
                'title': (255, 255, 255, 255),
                'text': (235, 220, 235, 255),
                'accent': (255, 150, 255, 255)
            },
            NotificationType.WEATHER: {
                'bg': (45, 55, 75, 240),        # Dark blue
                'border': (120, 150, 220, 255),
                'title': (255, 255, 255, 255),
                'text': (220, 230, 245, 255),
                'accent': (150, 180, 255, 255)
            },
            NotificationType.AGRICULTURE: {
                'bg': (55, 70, 45, 240),        # Earth green
                'border': (140, 180, 120, 255),
                'title': (255, 255, 255, 255),
                'text': (230, 240, 220, 255),
                'accent': (180, 220, 150, 255)
            },
            NotificationType.BUILDING: {
                'bg': (70, 60, 45, 240),        # Brown/tan
                'border': (180, 150, 120, 255),
                'title': (255, 255, 255, 255),
                'text': (240, 230, 220, 255),
                'accent': (220, 180, 150, 255)
            },
            NotificationType.ACHIEVEMENT: {
                'bg': (70, 55, 25, 240),        # Golden brown
                'border': (220, 180, 80, 255),
                'title': (255, 255, 255, 255),
                'text': (245, 235, 200, 255),
                'accent': (255, 220, 100, 255)
            },
            NotificationType.SYSTEM: {
                'bg': (55, 55, 55, 240),        # Gray
                'border': (150, 150, 150, 255),
                'title': (255, 255, 255, 255),
                'text': (230, 230, 230, 255),
                'accent': (200, 200, 200, 255)
            },
            NotificationType.TUTORIAL: {
                'bg': (45, 60, 70, 240),        # Blue-gray
                'border': (120, 160, 200, 255),
                'title': (255, 255, 255, 255),
                'text': (220, 235, 245, 255),
                'accent': (150, 200, 255, 255)
            }
        }
        
        # Priority visual modifiers
        self.priority_modifiers = {
            NotificationPriority.LOW: {
                'size_scale': 0.9,
                'border_width': 1,
                'glow_intensity': 0.0
            },
            NotificationPriority.NORMAL: {
                'size_scale': 1.0,
                'border_width': 2,
                'glow_intensity': 0.0
            },
            NotificationPriority.HIGH: {
                'size_scale': 1.1,
                'border_width': 3,
                'glow_intensity': 0.3
            },
            NotificationPriority.CRITICAL: {
                'size_scale': 1.2,
                'border_width': 4,
                'glow_intensity': 0.8
            },
            NotificationPriority.CELEBRATION: {
                'size_scale': 1.15,
                'border_width': 3,
                'glow_intensity': 0.5
            }
        }
        
        # Animation settings
        self.base_width = 350
        self.base_height = 80
        self.padding = 12
        self.margin = 8
        self.corner_radius = 8
        
    def _initialize_fonts(self) -> Dict[str, pygame.font.Font]:
        """Initialize font objects for notification text"""
        try:
            fonts = {
                'title': pygame.font.Font(None, 20),
                'message': pygame.font.Font(None, 16),
                'action': pygame.font.Font(None, 14),
                'timestamp': pygame.font.Font(None, 12)
            }
            
            # Try to load system fonts for better appearance
            try:
                fonts['title'] = pygame.font.SysFont('arial', 18, bold=True)
                fonts['message'] = pygame.font.SysFont('arial', 14)
                fonts['action'] = pygame.font.SysFont('arial', 12, bold=True)
                fonts['timestamp'] = pygame.font.SysFont('arial', 10)
            except:
                pass  # Fall back to default fonts
                
            return fonts
        except Exception as e:
            print(f"Warning: Could not initialize notification fonts: {e}")
            return {
                'title': pygame.font.Font(None, 20),
                'message': pygame.font.Font(None, 16),
                'action': pygame.font.Font(None, 14),
                'timestamp': pygame.font.Font(None, 12)
            }
    
    def calculate_notification_size(self, notification: NotificationData) -> Tuple[int, int]:
        """Calculate required size for notification"""
        # Get priority scaling
        scale = self.priority_modifiers[notification.priority]['size_scale']
        scale *= notification.size_multiplier
        
        # Base size calculation
        width = int(self.base_width * scale)
        height = int(self.base_height * scale)
        
        # Adjust for content length
        title_surface = self.fonts['title'].render(notification.title, True, (255, 255, 255))
        message_lines = self._wrap_text(notification.message, width - self.padding * 2, self.fonts['message'])
        
        # Calculate actual height needed
        content_height = (title_surface.get_height() + 4 +  # Title + spacing
                         len(message_lines) * (self.fonts['message'].get_height() + 2))  # Message lines
        
        if notification.action_text:
            content_height += self.fonts['action'].get_height() + 8  # Action button
        
        height = max(height, content_height + self.padding * 2)
        
        return (width, height)
    
    def _wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Wrap text to fit within specified width"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " " if current_line else word + " "
            test_surface = font.render(test_line.strip(), True, (255, 255, 255))
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                    current_line = word + " "
                else:
                    lines.append(word)
                    current_line = ""
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def render_notification(self, screen: pygame.Surface, notification: NotificationData, 
                          position: Tuple[int, int], animation_offset: float = 0.0) -> pygame.Rect:
        """Render a notification with animation effects"""
        # Calculate size and position
        width, height = self.calculate_notification_size(notification)
        x, y = position
        
        # Apply animation offset (for slide-in/out effects)
        x += int(animation_offset)
        
        # Get color scheme
        colors = self.color_schemes.get(notification.type, self.color_schemes[NotificationType.SYSTEM])
        if notification.color_override:
            colors = dict(colors)  # Copy and override
            colors['bg'] = notification.color_override
        
        # Get priority modifiers
        modifiers = self.priority_modifiers[notification.priority]
        
        # Create notification surface
        notification_rect = pygame.Rect(x, y, width, height)
        
        # Draw background with transparency
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self._draw_rounded_rect(bg_surface, colors['bg'], (0, 0, width, height), self.corner_radius)
        
        # Add glow effect for high priority notifications
        glow_intensity = modifiers['glow_intensity']
        if glow_intensity > 0:
            glow_color = (*colors['accent'][:3], int(100 * glow_intensity))
            glow_size = int(6 * glow_intensity)
            for i in range(glow_size):
                glow_alpha = int((glow_intensity * 50) * (1 - i / glow_size))
                glow_rect = pygame.Rect(-i, -i, width + i*2, height + i*2)
                pygame.draw.rect(bg_surface, (*colors['accent'][:3], glow_alpha), glow_rect, 1)
        
        # Draw border
        border_width = modifiers['border_width']
        self._draw_rounded_rect_outline(bg_surface, colors['border'], 
                                       (0, 0, width, height), self.corner_radius, border_width)
        
        # Apply pulsing effect for critical notifications
        if notification.priority == NotificationPriority.CRITICAL:
            pulse_factor = (math.sin(time.time() * 4) + 1) / 2  # 0 to 1
            pulse_alpha = int(50 + pulse_factor * 30)
            pulse_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pulse_surface.fill((*colors['accent'][:3], pulse_alpha))
            bg_surface.blit(pulse_surface, (0, 0))
        
        # Render content
        self._render_notification_content(bg_surface, notification, colors, width, height)
        
        # Apply fade effect based on animation state
        if notification.animation_state in ["entering", "exiting"]:
            fade_alpha = notification.animation_progress if notification.animation_state == "entering" else 1.0 - notification.animation_progress
            fade_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            fade_surface.fill((255, 255, 255, int(255 * fade_alpha)))
            bg_surface.blit(fade_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Blit to screen
        screen.blit(bg_surface, (x, y))
        
        return notification_rect
    
    def _render_notification_content(self, surface: pygame.Surface, notification: NotificationData, 
                                   colors: Dict, width: int, height: int):
        """Render the text content of a notification"""
        y_offset = self.padding
        
        # Render title
        title_surface = self.fonts['title'].render(notification.title, True, colors['title'])
        surface.blit(title_surface, (self.padding, y_offset))
        y_offset += title_surface.get_height() + 4
        
        # Render message (wrapped)
        message_lines = self._wrap_text(notification.message, width - self.padding * 2, self.fonts['message'])
        for line in message_lines:
            line_surface = self.fonts['message'].render(line, True, colors['text'])
            surface.blit(line_surface, (self.padding, y_offset))
            y_offset += line_surface.get_height() + 2
        
        # Render action button if present
        if notification.action_text:
            action_surface = self.fonts['action'].render(f"[{notification.action_text}]", True, colors['accent'])
            surface.blit(action_surface, (width - action_surface.get_width() - self.padding, 
                                        height - action_surface.get_height() - self.padding))
        
        # Render timestamp
        elapsed = time.time() - notification.created_time
        if elapsed < 60:
            timestamp_text = f"{int(elapsed)}s ago"
        elif elapsed < 3600:
            timestamp_text = f"{int(elapsed // 60)}m ago"
        else:
            timestamp_text = f"{int(elapsed // 3600)}h ago"
        
        timestamp_surface = self.fonts['timestamp'].render(timestamp_text, True, colors['text'])
        surface.blit(timestamp_surface, (self.padding, height - timestamp_surface.get_height() - 4))
        
        # Render priority indicator
        priority_text = f"[{notification.priority.name}]"
        priority_surface = self.fonts['timestamp'].render(priority_text, True, colors['accent'])
        surface.blit(priority_surface, (width - priority_surface.get_width() - self.padding, 4))
    
    def _draw_rounded_rect(self, surface: pygame.Surface, color: Tuple[int, int, int, int], 
                          rect: Tuple[int, int, int, int], radius: int):
        """Draw a rounded rectangle"""
        x, y, width, height = rect
        if radius * 2 > min(width, height):
            radius = min(width, height) // 2
        
        # Create temporary surface
        temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw main rectangle
        pygame.draw.rect(temp_surface, color, (radius, 0, width - 2 * radius, height))
        pygame.draw.rect(temp_surface, color, (0, radius, width, height - 2 * radius))
        
        # Draw corner circles
        pygame.draw.circle(temp_surface, color, (radius, radius), radius)
        pygame.draw.circle(temp_surface, color, (width - radius, radius), radius)
        pygame.draw.circle(temp_surface, color, (radius, height - radius), radius)
        pygame.draw.circle(temp_surface, color, (width - radius, height - radius), radius)
        
        surface.blit(temp_surface, (x, y))
    
    def _draw_rounded_rect_outline(self, surface: pygame.Surface, color: Tuple[int, int, int, int], 
                                  rect: Tuple[int, int, int, int], radius: int, width: int):
        """Draw rounded rectangle outline"""
        x, y, w, h = rect
        # Draw outline using rectangles and circles
        pygame.draw.rect(surface, color, (x + radius, y, w - 2 * radius, width))
        pygame.draw.rect(surface, color, (x + radius, y + h - width, w - 2 * radius, width))
        pygame.draw.rect(surface, color, (x, y + radius, width, h - 2 * radius))
        pygame.draw.rect(surface, color, (x + w - width, y + radius, width, h - 2 * radius))
        
        # Corner circles
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius, width)
        pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius, width)
        pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius, width)
        pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius, width)

class NotificationManager:
    """Main notification system manager"""
    
    def __init__(self, event_system, screen_width: int = WINDOW_WIDTH, screen_height: int = WINDOW_HEIGHT):
        # Core system references
        self.event_system = event_system
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Notification rendering
        self.renderer = NotificationRenderer()
        
        # Active notifications
        self.active_notifications = []  # Currently displayed notifications
        self.notification_history = []  # All notifications for history panel
        self.max_history = 100  # Maximum notifications to keep in history
        
        # Display settings
        self.max_visible = 5  # Maximum notifications shown at once
        self.stack_direction = "down"  # "up" or "down" stacking
        self.anchor_position = "top_right"  # Screen anchor point
        
        # Animation system
        self.animation_speed = 4.0  # Animation speed multiplier
        self.slide_distance = 400  # Pixels to slide in from
        
        # Notification center state
        self.show_center = False  # Is notification center panel open
        self.center_filter = None  # Current filter (NotificationType or None)
        
        # Register event handlers
        self.event_system.subscribe('show_notification', self._handle_show_notification)
        self.event_system.subscribe('show_alert', self._handle_show_alert)
        self.event_system.subscribe('show_achievement', self._handle_show_achievement)
        self.event_system.subscribe('toggle_notification_center', self._handle_toggle_center)
        
        print("Advanced Notification System initialized - Phase 2.2 enhancement ready!")
    
    def show_notification(self, title: str, message: str, notification_type: NotificationType,
                         priority: NotificationPriority = NotificationPriority.NORMAL,
                         duration: Optional[float] = None) -> NotificationData:
        """Show a standard notification"""
        notification = NotificationData(title, message, notification_type, priority)
        
        if duration is not None:
            notification.set_duration(duration)
        
        self._add_notification(notification)
        return notification
    
    def show_alert(self, title: str, message: str, action_text: str = None, 
                  action_callback: Callable = None) -> NotificationData:
        """Show a critical alert notification"""
        notification = NotificationData(title, message, NotificationType.SYSTEM, NotificationPriority.CRITICAL)
        
        if action_text and action_callback:
            notification.set_action(action_text, action_callback)
        
        self._add_notification(notification)
        return notification
    
    def show_achievement(self, title: str, description: str) -> NotificationData:
        """Show an achievement celebration notification"""
        notification = NotificationData(title, description, NotificationType.ACHIEVEMENT, NotificationPriority.CELEBRATION)
        notification.set_duration(8.0)  # Longer display for celebrations
        self._add_notification(notification)
        return notification
    
    def show_tutorial_tip(self, title: str, tip: str) -> NotificationData:
        """Show an educational tutorial tip"""
        notification = NotificationData(title, tip, NotificationType.TUTORIAL, NotificationPriority.NORMAL)
        notification.set_duration(10.0)  # Longer for educational content
        self._add_notification(notification)
        return notification
    
    def _add_notification(self, notification: NotificationData):
        """Add a notification to the active display"""
        # Add to active notifications
        self.active_notifications.append(notification)
        
        # Add to history
        self.notification_history.append(notification)
        
        # Trim history if too long
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]
        
        # Limit visible notifications
        if len(self.active_notifications) > self.max_visible:
            # Remove oldest non-critical notifications
            for i, notif in enumerate(self.active_notifications[:-1]):  # Don't remove the newest
                if notif.priority != NotificationPriority.CRITICAL:
                    notif.dismiss()
                    break
    
    def update(self, dt: float):
        """Update notification system state and animations"""
        current_time = time.time()
        
        # Update animation states
        for notification in self.active_notifications[:]:
            if notification.animation_state == "entering":
                notification.animation_progress += dt * self.animation_speed
                if notification.animation_progress >= 1.0:
                    notification.animation_progress = 1.0
                    notification.animation_state = "visible"
            
            elif notification.animation_state == "visible":
                # Check for auto-dismissal
                if notification.is_expired() and not notification.is_pinned:
                    notification.dismiss()
            
            elif notification.animation_state == "exiting":
                notification.animation_progress += dt * self.animation_speed
                if notification.animation_progress >= 1.0:
                    notification.animation_state = "dismissed"
        
        # Remove dismissed notifications
        self.active_notifications = [n for n in self.active_notifications if n.animation_state != "dismissed"]
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle clicks on notifications"""
        # Calculate notification positions and check for clicks
        notification_rects = self._calculate_notification_positions()
        
        for i, (notification, rect) in enumerate(zip(self.active_notifications, notification_rects)):
            if rect.collidepoint(mouse_pos):
                # Mark as read
                notification.mark_read()
                
                # Execute action if present
                if notification.action_callback:
                    notification.action_callback()
                
                # Dismiss if dismissible
                if notification.is_dismissible:
                    notification.dismiss()
                
                return True  # Click handled
        
        return False  # Click not handled
    
    def _calculate_notification_positions(self) -> List[pygame.Rect]:
        """Calculate screen positions for all active notifications"""
        positions = []
        
        # Calculate anchor point
        if self.anchor_position == "top_right":
            anchor_x = self.screen_width - 20  # 20px margin from right
            anchor_y = 90  # Below top HUD
        elif self.anchor_position == "top_left":
            anchor_x = 20
            anchor_y = 90
        else:  # Default to top_right
            anchor_x = self.screen_width - 20
            anchor_y = 90
        
        current_y = anchor_y
        
        for notification in self.active_notifications:
            width, height = self.renderer.calculate_notification_size(notification)
            
            # Calculate position (anchor_x is right edge for right-aligned notifications)
            x = anchor_x - width if "right" in self.anchor_position else anchor_x
            y = current_y
            
            positions.append(pygame.Rect(x, y, width, height))
            
            # Update position for next notification
            current_y += height + self.renderer.margin
        
        return positions
    
    def render(self, screen: pygame.Surface):
        """Render all active notifications"""
        notification_rects = self._calculate_notification_positions()
        
        for notification, rect in zip(self.active_notifications, notification_rects):
            # Calculate animation offset for slide-in/out effect
            animation_offset = 0.0
            
            if notification.animation_state == "entering":
                # Slide in from right
                progress = 1.0 - notification.animation_progress
                animation_offset = self.slide_distance * progress
            elif notification.animation_state == "exiting":
                # Slide out to right
                animation_offset = self.slide_distance * notification.animation_progress
            
            # Render the notification
            self.renderer.render_notification(
                screen, 
                notification, 
                (rect.x, rect.y), 
                animation_offset
            )
    
    def _handle_show_notification(self, event_data):
        """Handle notification requests from event system"""
        title = event_data.get('title', 'Notification')
        message = event_data.get('message', '')
        notif_type = event_data.get('type', NotificationType.SYSTEM)
        priority = event_data.get('priority', NotificationPriority.NORMAL)
        duration = event_data.get('duration')
        
        self.show_notification(title, message, notif_type, priority, duration)
    
    def _handle_show_alert(self, event_data):
        """Handle alert requests from event system"""
        title = event_data.get('title', 'Alert')
        message = event_data.get('message', '')
        action_text = event_data.get('action_text')
        action_callback = event_data.get('action_callback')
        
        self.show_alert(title, message, action_text, action_callback)
    
    def _handle_show_achievement(self, event_data):
        """Handle achievement notifications from event system"""
        title = event_data.get('title', 'Achievement!')
        description = event_data.get('description', '')
        
        self.show_achievement(title, description)
    
    def _handle_toggle_center(self, event_data):
        """Handle notification center toggle requests"""
        self.show_center = not self.show_center

class NotificationFactory:
    """Factory for creating common notification types"""
    
    @staticmethod
    def economy_notification(title: str, message: str, amount: float = None) -> NotificationData:
        """Create an economy-related notification"""
        if amount is not None:
            if amount > 0:
                message += f" (+${amount:.0f})"
            else:
                message += f" (-${abs(amount):.0f})"
        
        return NotificationData(title, message, NotificationType.ECONOMY, NotificationPriority.NORMAL)
    
    @staticmethod
    def employee_notification(title: str, message: str, priority: NotificationPriority = NotificationPriority.NORMAL) -> NotificationData:
        """Create an employee-related notification"""
        return NotificationData(title, message, NotificationType.EMPLOYEE, priority)
    
    @staticmethod
    def weather_alert(title: str, message: str) -> NotificationData:
        """Create a weather-related alert"""
        return NotificationData(title, message, NotificationType.WEATHER, NotificationPriority.HIGH)
    
    @staticmethod
    def harvest_celebration(crop_type: str, quantity: int, quality: str = "good") -> NotificationData:
        """Create a harvest achievement notification"""
        title = f"🌾 {crop_type.title()} Harvest Complete!"
        message = f"Harvested {quantity} units of {quality} quality {crop_type}. Great work!"
        return NotificationData(title, message, NotificationType.ACHIEVEMENT, NotificationPriority.CELEBRATION)
    
    @staticmethod
    def critical_alert(title: str, message: str, action_text: str = None, action_callback: Callable = None) -> NotificationData:
        """Create a critical alert requiring immediate attention"""
        notification = NotificationData(title, message, NotificationType.SYSTEM, NotificationPriority.CRITICAL)
        
        if action_text and action_callback:
            notification.set_action(action_text, action_callback)
        
        return notification

# Example usage and integration
if __name__ == "__main__":
    # Example notifications for testing
    
    # Economy notification
    economy_notif = NotificationFactory.economy_notification(
        "Crop Sale Complete", 
        "Successfully sold corn to market", 
        150.0
    )
    
    # Employee notification
    employee_notif = NotificationFactory.employee_notification(
        "New Employee Hired",
        "Welcome Sarah to your farming team! She specializes in crop cultivation.",
        NotificationPriority.NORMAL
    )
    
    # Weather alert
    weather_notif = NotificationFactory.weather_alert(
        "Drought Warning",
        "Extended dry period expected. Consider irrigation to protect crops."
    )
    
    # Achievement celebration
    harvest_notif = NotificationFactory.harvest_celebration("corn", 25, "excellent")
    
    print("Notification system examples created successfully!")