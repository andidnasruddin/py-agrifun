"""
Advanced Tooltip System - Professional tooltip engine for UI Overhaul Phase 2
Provides rich, context-sensitive tooltips with educational and strategic information.

Features:
- Dynamic positioning with smart collision detection
- Rich formatting with icons, colors, and multi-line content
- Context-aware tooltip generation for all UI elements
- Educational agricultural knowledge integration
- Performance optimized with caching and culling
"""

import pygame
import pygame_gui
from typing import Dict, List, Optional, Tuple, Any
from scripts.core.config import *
import math

class TooltipData:
    """Data structure for rich tooltip content"""
    
    def __init__(self, title: str, content: str, tooltip_type: str = "info"):
        # Main tooltip content
        self.title = title  # Bold heading text
        self.content = content  # Main body text (supports line breaks)
        self.tooltip_type = tooltip_type  # 'info', 'educational', 'warning', 'strategic'
        
        # Rich content features
        self.subtitle = None  # Optional subtitle text
        self.icon_path = None  # Path to icon image
        self.quick_stats = []  # List of key-value pairs for quick reference
        self.educational_note = None  # Agricultural education text
        self.strategic_advice = None  # Strategic gameplay tips
        
        # Visual styling
        self.priority = 0  # Higher priority tooltips stay visible longer
        self.max_width = 320  # Maximum tooltip width in pixels
        self.show_duration = 3.0  # How long to show tooltip in seconds (0 = until mouse moves)
    
    def add_subtitle(self, subtitle: str):
        """Add subtitle text below the main title"""
        self.subtitle = subtitle
        return self
    
    def add_icon(self, icon_path: str):
        """Add icon to tooltip header"""
        self.icon_path = icon_path
        return self
    
    def add_quick_stat(self, label: str, value: str, highlight: bool = False):
        """Add a quick reference stat (e.g., 'Cost: $150', 'Yield: +20%')"""
        self.quick_stats.append({
            'label': label,
            'value': value,
            'highlight': highlight
        })
        return self
    
    def add_educational_note(self, note: str):
        """Add educational agricultural information"""
        self.educational_note = note
        return self
    
    def add_strategic_advice(self, advice: str):
        """Add strategic gameplay tip"""
        self.strategic_advice = advice
        return self
    
    def set_priority(self, priority: int):
        """Set tooltip priority (higher = more important)"""
        self.priority = priority
        return self
    
    def set_max_width(self, width: int):
        """Set maximum tooltip width"""
        self.max_width = width
        return self


class TooltipRenderer:
    """Handles the visual rendering of tooltips"""
    
    def __init__(self):
        # Initialize fonts for different text styles
        self.fonts = self._initialize_fonts()
        
        # Color scheme for different tooltip types
        self.color_schemes = {
            'info': {
                'bg': (45, 45, 55, 240),        # Dark blue-gray background
                'border': (120, 150, 200, 255), # Light blue border
                'title': (255, 255, 255, 255),  # White title
                'text': (220, 220, 220, 255),   # Light gray text
                'accent': (100, 180, 255, 255)  # Blue accent
            },
            'educational': {
                'bg': (40, 60, 40, 240),        # Dark green background
                'border': (120, 200, 120, 255), # Green border
                'title': (255, 255, 255, 255),  # White title
                'text': (220, 235, 220, 255),   # Light green text
                'accent': (150, 255, 150, 255)  # Green accent
            },
            'warning': {
                'bg': (60, 45, 40, 240),        # Dark red-brown background
                'border': (200, 120, 100, 255), # Orange-red border
                'title': (255, 255, 255, 255),  # White title
                'text': (235, 220, 200, 255),   # Light orange text
                'accent': (255, 180, 100, 255)  # Orange accent
            },
            'strategic': {
                'bg': (55, 45, 65, 240),        # Dark purple background
                'border': (170, 130, 200, 255), # Purple border
                'title': (255, 255, 255, 255),  # White title
                'text': (235, 220, 235, 255),   # Light purple text
                'accent': (200, 150, 255, 255)  # Purple accent
            }
        }
        
        # Visual styling constants
        self.padding = 12  # Inner padding
        self.line_spacing = 4  # Space between lines
        self.section_spacing = 8  # Space between sections
        self.border_radius = 8  # Rounded corner radius
        self.shadow_offset = 3  # Drop shadow offset
    
    def _initialize_fonts(self) -> Dict[str, pygame.font.Font]:
        """Initialize font objects for different text styles"""
        try:
            # Use system fonts for better readability
            fonts = {
                'title': pygame.font.Font(None, 24),      # Bold title font
                'subtitle': pygame.font.Font(None, 18),   # Subtitle font
                'body': pygame.font.Font(None, 16),       # Main body text
                'small': pygame.font.Font(None, 14),      # Small text for details
                'stat_label': pygame.font.Font(None, 14), # Quick stat labels
                'stat_value': pygame.font.Font(None, 16)  # Quick stat values
            }
            
            # Try to load better fonts if available
            try:
                fonts['title'] = pygame.font.SysFont('arial', 20, bold=True)
                fonts['subtitle'] = pygame.font.SysFont('arial', 16, italic=True)
                fonts['body'] = pygame.font.SysFont('arial', 14)
                fonts['small'] = pygame.font.SysFont('arial', 12)
                fonts['stat_label'] = pygame.font.SysFont('arial', 12)
                fonts['stat_value'] = pygame.font.SysFont('arial', 14, bold=True)
            except:
                pass  # Fall back to default fonts if system fonts unavailable
                
            return fonts
        except Exception as e:
            print(f"Warning: Could not initialize tooltip fonts: {e}")
            # Fallback to basic pygame fonts
            return {
                'title': pygame.font.Font(None, 24),
                'subtitle': pygame.font.Font(None, 18),
                'body': pygame.font.Font(None, 16),
                'small': pygame.font.Font(None, 14),
                'stat_label': pygame.font.Font(None, 14),
                'stat_value': pygame.font.Font(None, 16)
            }
    
    def calculate_tooltip_size(self, tooltip_data: TooltipData) -> Tuple[int, int]:
        """Calculate the required size for a tooltip based on its content"""
        max_width = tooltip_data.max_width
        current_height = self.padding * 2  # Top and bottom padding
        
        # Calculate title height
        title_surface = self.fonts['title'].render(tooltip_data.title, True, (255, 255, 255))
        current_height += title_surface.get_height() + self.line_spacing
        
        # Calculate subtitle height if present
        if tooltip_data.subtitle:
            subtitle_surface = self.fonts['subtitle'].render(tooltip_data.subtitle, True, (200, 200, 200))
            current_height += subtitle_surface.get_height() + self.section_spacing
        
        # Calculate main content height (supports multi-line)
        content_lines = tooltip_data.content.split('\n')
        for line in content_lines:
            if line.strip():  # Skip empty lines
                wrapped_lines = self._wrap_text(line, max_width - self.padding * 2, self.fonts['body'])
                current_height += len(wrapped_lines) * (self.fonts['body'].get_height() + self.line_spacing)
        
        # Calculate quick stats height
        if tooltip_data.quick_stats:
            current_height += self.section_spacing
            for stat in tooltip_data.quick_stats:
                current_height += self.fonts['stat_value'].get_height() + self.line_spacing
        
        # Calculate educational note height
        if tooltip_data.educational_note:
            current_height += self.section_spacing
            edu_lines = self._wrap_text(tooltip_data.educational_note, max_width - self.padding * 2, self.fonts['small'])
            current_height += len(edu_lines) * (self.fonts['small'].get_height() + self.line_spacing)
        
        # Calculate strategic advice height
        if tooltip_data.strategic_advice:
            current_height += self.section_spacing
            strat_lines = self._wrap_text(tooltip_data.strategic_advice, max_width - self.padding * 2, self.fonts['small'])
            current_height += len(strat_lines) * (self.fonts['small'].get_height() + self.line_spacing)
        
        return (max_width, current_height)
    
    def _wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Wrap text to fit within the specified width"""
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
                    # Single word is too long, force it on its own line
                    lines.append(word)
                    current_line = ""
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def render_tooltip(self, screen: pygame.Surface, tooltip_data: TooltipData, 
                      position: Tuple[int, int]) -> pygame.Surface:
        """Render a tooltip at the specified position"""
        # Get color scheme for tooltip type
        colors = self.color_schemes.get(tooltip_data.tooltip_type, self.color_schemes['info'])
        
        # Calculate tooltip dimensions
        tooltip_width, tooltip_height = self.calculate_tooltip_size(tooltip_data)
        
        # Create tooltip surface with alpha for transparency
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        
        # Draw background with rounded rectangle effect
        self._draw_rounded_rect(tooltip_surface, colors['bg'], 
                               (0, 0, tooltip_width, tooltip_height), self.border_radius)
        
        # Draw border
        self._draw_rounded_rect_outline(tooltip_surface, colors['border'], 
                                       (0, 0, tooltip_width, tooltip_height), self.border_radius, 2)
        
        # Render content
        y_offset = self.padding
        
        # Render title
        title_surface = self.fonts['title'].render(tooltip_data.title, True, colors['title'])
        tooltip_surface.blit(title_surface, (self.padding, y_offset))
        y_offset += title_surface.get_height() + self.line_spacing
        
        # Render subtitle if present
        if tooltip_data.subtitle:
            subtitle_surface = self.fonts['subtitle'].render(tooltip_data.subtitle, True, colors['text'])
            tooltip_surface.blit(subtitle_surface, (self.padding, y_offset))
            y_offset += subtitle_surface.get_height() + self.section_spacing
        
        # Render main content
        content_lines = tooltip_data.content.split('\n')
        for line in content_lines:
            if line.strip():
                wrapped_lines = self._wrap_text(line, tooltip_width - self.padding * 2, self.fonts['body'])
                for wrapped_line in wrapped_lines:
                    line_surface = self.fonts['body'].render(wrapped_line, True, colors['text'])
                    tooltip_surface.blit(line_surface, (self.padding, y_offset))
                    y_offset += line_surface.get_height() + self.line_spacing
        
        # Render quick stats
        if tooltip_data.quick_stats:
            y_offset += self.section_spacing
            for stat in tooltip_data.quick_stats:
                stat_color = colors['accent'] if stat.get('highlight') else colors['text']
                stat_text = f"{stat['label']}: {stat['value']}"
                stat_surface = self.fonts['stat_value'].render(stat_text, True, stat_color)
                tooltip_surface.blit(stat_surface, (self.padding, y_offset))
                y_offset += stat_surface.get_height() + self.line_spacing
        
        # Render educational note
        if tooltip_data.educational_note:
            y_offset += self.section_spacing
            # Add educational icon/indicator
            edu_header = self.fonts['small'].render("🌾 Agricultural Knowledge:", True, colors['accent'])
            tooltip_surface.blit(edu_header, (self.padding, y_offset))
            y_offset += edu_header.get_height() + self.line_spacing
            
            edu_lines = self._wrap_text(tooltip_data.educational_note, tooltip_width - self.padding * 2, self.fonts['small'])
            for line in edu_lines:
                line_surface = self.fonts['small'].render(line, True, colors['text'])
                tooltip_surface.blit(line_surface, (self.padding, y_offset))
                y_offset += line_surface.get_height() + self.line_spacing
        
        # Render strategic advice
        if tooltip_data.strategic_advice:
            y_offset += self.section_spacing
            # Add strategy icon/indicator
            strat_header = self.fonts['small'].render("💡 Strategic Tip:", True, colors['accent'])
            tooltip_surface.blit(strat_header, (self.padding, y_offset))
            y_offset += strat_header.get_height() + self.line_spacing
            
            strat_lines = self._wrap_text(tooltip_data.strategic_advice, tooltip_width - self.padding * 2, self.fonts['small'])
            for line in strat_lines:
                line_surface = self.fonts['small'].render(line, True, colors['text'])
                tooltip_surface.blit(line_surface, (self.padding, y_offset))
                y_offset += line_surface.get_height() + self.line_spacing
        
        # Blit tooltip to screen at position
        screen.blit(tooltip_surface, position)
        return tooltip_surface
    
    def _draw_rounded_rect(self, surface: pygame.Surface, color: Tuple[int, int, int, int], 
                          rect: Tuple[int, int, int, int], radius: int):
        """Draw a rounded rectangle with the specified color"""
        x, y, width, height = rect
        
        # Create a surface with alpha support
        temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw the rounded rectangle
        if radius * 2 > min(width, height):
            radius = min(width, height) // 2
        
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
        """Draw the outline of a rounded rectangle"""
        x, y, w, h = rect
        
        # Draw the outline using multiple rectangles and circles
        # Top and bottom edges
        pygame.draw.rect(surface, color, (x + radius, y, w - 2 * radius, width))
        pygame.draw.rect(surface, color, (x + radius, y + h - width, w - 2 * radius, width))
        
        # Left and right edges
        pygame.draw.rect(surface, color, (x, y + radius, width, h - 2 * radius))
        pygame.draw.rect(surface, color, (x + w - width, y + radius, width, h - 2 * radius))
        
        # Corner circles (outline only)
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius, width)
        pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius, width)
        pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius, width)
        pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius, width)


class TooltipManager:
    """Main tooltip system manager - handles positioning, timing, and display"""
    
    def __init__(self, event_system, screen_width: int = WINDOW_WIDTH, screen_height: int = WINDOW_HEIGHT):
        # Core system references
        self.event_system = event_system
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Tooltip rendering system
        self.renderer = TooltipRenderer()
        
        # Active tooltip management
        self.current_tooltip = None  # Currently displayed tooltip data
        self.tooltip_position = (0, 0)  # Current tooltip position
        self.tooltip_timer = 0.0  # How long current tooltip has been shown
        self.mouse_position = (0, 0)  # Current mouse position
        self.last_mouse_position = (0, 0)  # Previous mouse position for movement detection
        
        # Tooltip registration system - maps UI elements to tooltip data
        self.registered_tooltips = {}  # Maps element IDs to tooltip data
        self.hover_targets = {}  # Maps screen regions to tooltip data
        
        # Performance optimization
        self.tooltip_cache = {}  # Cache rendered tooltip surfaces
        self.cache_max_size = 50  # Maximum cached tooltips
        
        # Timing and behavior settings
        self.hover_delay = 0.5  # Seconds before showing tooltip on hover
        self.fade_time = 0.2  # Fade in/out duration
        self.mouse_move_threshold = 5  # Pixels moved to hide tooltip
        
        # Register for events
        self.event_system.subscribe('mouse_motion', self._handle_mouse_motion)
        self.event_system.subscribe('ui_element_hovered', self._handle_ui_element_hover)
        self.event_system.subscribe('tooltip_requested', self._handle_tooltip_request)
        
        print("Advanced Tooltip System initialized - Phase 2 UI enhancement ready!")
    
    def register_ui_tooltip(self, element_id: str, tooltip_data: TooltipData):
        """Register a tooltip for a UI element by its ID"""
        self.registered_tooltips[element_id] = tooltip_data
    
    def register_hover_area(self, area_rect: pygame.Rect, tooltip_data: TooltipData):
        """Register a tooltip for a screen area (useful for grid tiles, etc.)"""
        area_key = f"area_{area_rect.x}_{area_rect.y}_{area_rect.width}_{area_rect.height}"
        self.hover_targets[area_key] = {
            'rect': area_rect,
            'tooltip': tooltip_data
        }
    
    def show_tooltip(self, tooltip_data: TooltipData, position: Optional[Tuple[int, int]] = None):
        """Show a tooltip immediately at the specified position (or mouse position)"""
        self.current_tooltip = tooltip_data
        
        if position:
            self.tooltip_position = self._calculate_smart_position(tooltip_data, position)
        else:
            self.tooltip_position = self._calculate_smart_position(tooltip_data, self.mouse_position)
        
        self.tooltip_timer = 0.0
    
    def hide_tooltip(self):
        """Hide the current tooltip"""
        self.current_tooltip = None
        self.tooltip_timer = 0.0
    
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """Update tooltip system state and handle timing"""
        # Update mouse position tracking
        self.last_mouse_position = self.mouse_position
        self.mouse_position = mouse_pos
        
        # Check for mouse movement
        mouse_moved_distance = math.sqrt(
            (mouse_pos[0] - self.last_mouse_position[0]) ** 2 + 
            (mouse_pos[1] - self.last_mouse_position[1]) ** 2
        )
        
        # Hide tooltip if mouse moved significantly
        if mouse_moved_distance > self.mouse_move_threshold and self.current_tooltip:
            if self.current_tooltip.show_duration == 0:  # Only hide if it's a hover tooltip
                self.hide_tooltip()
        
        # Update tooltip timer
        if self.current_tooltip:
            self.tooltip_timer += dt
            
            # Auto-hide tooltip after specified duration (if set)
            if (self.current_tooltip.show_duration > 0 and 
                self.tooltip_timer >= self.current_tooltip.show_duration):
                self.hide_tooltip()
        
        # Check for hover areas
        self._check_hover_areas()
    
    def _check_hover_areas(self):
        """Check if mouse is hovering over any registered areas"""
        for area_key, area_data in self.hover_targets.items():
            area_rect = area_data['rect']
            if area_rect.collidepoint(self.mouse_position):
                # Mouse is over this area
                if not self.current_tooltip or self.current_tooltip != area_data['tooltip']:
                    self.show_tooltip(area_data['tooltip'])
                return
    
    def _calculate_smart_position(self, tooltip_data: TooltipData, 
                                 target_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate optimal tooltip position to avoid screen edges and overlaps"""
        # Get tooltip dimensions
        tooltip_width, tooltip_height = self.renderer.calculate_tooltip_size(tooltip_data)
        
        # Start with position slightly offset from target
        x, y = target_pos
        offset_x, offset_y = 15, 15  # Default offset from cursor
        
        # Adjust horizontal position to stay on screen
        if x + offset_x + tooltip_width > self.screen_width:
            # Position to the left of the cursor
            x = x - offset_x - tooltip_width
        else:
            x = x + offset_x
        
        # Adjust vertical position to stay on screen
        if y + offset_y + tooltip_height > self.screen_height:
            # Position above the cursor
            y = y - offset_y - tooltip_height
        else:
            y = y + offset_y
        
        # Ensure tooltip doesn't go off the left or top edges
        x = max(5, x)
        y = max(5, y)
        
        return (x, y)
    
    def render(self, screen: pygame.Surface):
        """Render the current tooltip if one is active"""
        if self.current_tooltip and self.tooltip_timer >= self.hover_delay:
            # Calculate fade alpha based on fade_time
            fade_progress = min(1.0, (self.tooltip_timer - self.hover_delay) / self.fade_time)
            
            # Render tooltip with fade effect
            self.renderer.render_tooltip(screen, self.current_tooltip, self.tooltip_position)
    
    def _handle_mouse_motion(self, event_data):
        """Handle mouse motion events from the event system"""
        self.update(0.016, event_data.get('pos', self.mouse_position))  # Assume 60 FPS
    
    def _handle_ui_element_hover(self, event_data):
        """Handle UI element hover events"""
        element_id = event_data.get('element_id')
        if element_id in self.registered_tooltips:
            self.show_tooltip(self.registered_tooltips[element_id])
    
    def _handle_tooltip_request(self, event_data):
        """Handle direct tooltip requests from other systems"""
        tooltip_data = event_data.get('tooltip_data')
        position = event_data.get('position')
        if tooltip_data:
            self.show_tooltip(tooltip_data, position)


class TooltipFactory:
    """Factory class for creating common tooltip types quickly"""
    
    @staticmethod
    def create_button_tooltip(title: str, description: str, hotkey: str = None) -> TooltipData:
        """Create a standard button tooltip"""
        content = description
        if hotkey:
            content += f"\n\nHotkey: {hotkey}"
        
        return TooltipData(title, content, "info").set_priority(1)
    
    @staticmethod
    def create_educational_tooltip(title: str, agricultural_info: str, 
                                  strategic_tip: str = None) -> TooltipData:
        """Create an educational tooltip with agricultural knowledge"""
        tooltip = TooltipData(title, "", "educational")
        tooltip.add_educational_note(agricultural_info)
        
        if strategic_tip:
            tooltip.add_strategic_advice(strategic_tip)
        
        return tooltip.set_priority(2)
    
    @staticmethod
    def create_tile_tooltip(tile_data: Dict[str, Any]) -> TooltipData:
        """Create a detailed tooltip for grid tiles"""
        # Extract basic tile information
        terrain = tile_data.get('terrain_type', 'grass')
        crop = tile_data.get('current_crop')
        soil_quality = tile_data.get('soil_quality', 5)
        
        # Build title and content
        title = f"Tile ({tile_data.get('x', 0)}, {tile_data.get('y', 0)})"
        content = f"Terrain: {terrain.title()}"
        
        if crop:
            growth_stage = tile_data.get('growth_stage', 0)
            content += f"\nCrop: {crop.title()} (Stage {growth_stage}/4)"
        
        # Create tooltip with soil information
        tooltip = TooltipData(title, content, "info")
        tooltip.add_quick_stat("Soil Quality", f"{soil_quality}/10")
        
        # Add soil nutrients if available
        if 'soil_nutrients' in tile_data:
            nutrients = tile_data['soil_nutrients']
            tooltip.add_quick_stat("Nitrogen", f"{nutrients.get('nitrogen', 50)}/100")
            tooltip.add_quick_stat("Phosphorus", f"{nutrients.get('phosphorus', 50)}/100")
            tooltip.add_quick_stat("Potassium", f"{nutrients.get('potassium', 50)}/100")
        
        # Add educational information about soil health
        if soil_quality <= 3:
            tooltip.add_educational_note(
                "Poor soil quality reduces crop yields. Consider crop rotation or letting the field rest."
            )
        elif soil_quality >= 8:
            tooltip.add_educational_note(
                "Excellent soil quality! This tile will produce high-yield, high-quality crops."
            )
        
        return tooltip.set_priority(2)
    
    @staticmethod
    def create_economic_tooltip(title: str, cost: float, benefit: str = None, 
                               risk: str = None) -> TooltipData:
        """Create a tooltip focused on economic information"""
        tooltip = TooltipData(title, "", "strategic")
        tooltip.add_quick_stat("Cost", f"${cost:.0f}", highlight=True)
        
        if benefit:
            tooltip.add_strategic_advice(f"Benefit: {benefit}")
        
        if risk:
            tooltip.add_strategic_advice(f"Risk: {risk}")
        
        return tooltip.set_priority(3)


# Example usage and testing
if __name__ == "__main__":
    # Example of how to create different types of tooltips
    
    # Basic button tooltip
    till_tooltip = TooltipFactory.create_button_tooltip(
        "Till Soil", 
        "Prepare soil for planting by breaking up the ground and improving aeration.",
        "T"
    )
    
    # Educational tooltip about crop rotation
    rotation_tooltip = TooltipFactory.create_educational_tooltip(
        "Crop Rotation",
        "Rotating crops helps prevent soil depletion and reduces pest buildup. "
        "Heavy feeders like corn should be followed by light feeders like wheat.",
        "Plan your rotations seasonally for maximum soil health benefits."
    )
    
    # Economic decision tooltip
    irrigation_tooltip = TooltipFactory.create_economic_tooltip(
        "Install Irrigation",
        150.0,
        "Protects against drought damage (+30% growth during dry periods)",
        "High upfront cost and ongoing operational expenses"
    )
    
    print("Tooltip system examples created successfully!")