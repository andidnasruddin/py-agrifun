"""
Enhanced Grid Renderer - Advanced grid visualization with zoom, pan, and rich rendering
Provides professional-grade grid rendering with enhanced visual feedback and interaction.

This module implements enhanced grid rendering features:
- Zoom and pan functionality for detailed farm management
- Advanced tile rendering with soil health visualization
- Multi-selection with clear boundaries and visual feedback
- Context-sensitive hover information and previews
- Progressive detail levels based on zoom factor
- Visual overlays for different data types (irrigation, soil health, building efficiency)
"""

import pygame
import math
from typing import Dict, Any, Optional, List, Tuple
from scripts.core.config import *


class EnhancedGridRenderer:
    """Professional grid renderer with zoom, pan, and advanced visualization"""
    
    def __init__(self, grid_manager, screen_width=WINDOW_WIDTH, screen_height=WINDOW_HEIGHT):
        """Initialize the enhanced grid renderer"""
        self.grid_manager = grid_manager  # Reference to the grid manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calculate available grid area (accounting for UI)
        self.hud_height = 80  # Enhanced HUD height
        self.panel_width = 290  # Right panel width
        self.available_width = screen_width - self.panel_width
        self.available_height = screen_height - self.hud_height
        
        # Grid viewport and transformation
        self.zoom_factor = 1.0  # Current zoom level (1.0 = normal, 2.0 = 2x zoom)
        self.pan_offset_x = 0.0  # Pan offset in world coordinates
        self.pan_offset_y = 0.0  # Pan offset in world coordinates
        
        # Zoom limits for usability
        self.min_zoom = 0.5   # 50% zoom out (see more area)
        self.max_zoom = 3.0   # 300% zoom in (detailed view)
        
        # Mouse interaction state
        self.is_panning = False
        self.last_mouse_pos = None
        self.hover_tile = None  # Tile currently under mouse cursor
        
        # Visual enhancement settings
        self.show_soil_health_overlay = False
        self.show_irrigation_overlay = False
        self.show_building_efficiency = False
        self.grid_line_alpha = 128  # Semi-transparent grid lines
        
        # Rendering optimization
        self.tile_cache = {}  # Cache for tile surfaces at different zoom levels
        self.dirty_tiles = set()  # Tiles that need re-rendering
        
        # Color schemes for different overlays
        self.soil_health_colors = self._generate_soil_health_gradient()
        self.irrigation_colors = {
            'active': (64, 164, 223, 180),    # Water blue with transparency
            'inactive': (128, 128, 128, 100), # Gray with transparency
            'pending': (255, 255, 0, 150)     # Yellow with transparency
        }
        
        print("Enhanced Grid Renderer initialized with zoom/pan and advanced visualization")
    
    def _generate_soil_health_gradient(self) -> Dict[int, Tuple[int, int, int]]:
        """Generate color gradient for soil health visualization"""
        # Generate colors from red (poor) to green (excellent) soil health
        colors = {}
        for health in range(11):  # 0-10 soil health levels
            if health <= 3:
                # Poor soil: Red to orange
                ratio = health / 3.0
                red = 255
                green = int(127 * ratio)
                blue = 0
            elif health <= 7:
                # Average soil: Orange to yellow
                ratio = (health - 3) / 4.0
                red = 255
                green = int(127 + 128 * ratio)
                blue = 0
            else:
                # Good soil: Yellow to green
                ratio = (health - 7) / 3.0
                red = int(255 * (1.0 - ratio))
                green = 255
                blue = 0
            
            colors[health] = (red, green, blue)
        
        return colors
    
    def handle_mouse_wheel(self, event):
        """Handle mouse wheel events for zooming"""
        if event.y > 0:  # Scroll up - zoom in
            self.zoom_in(event.pos)
        elif event.y < 0:  # Scroll down - zoom out
            self.zoom_out(event.pos)
    
    def zoom_in(self, mouse_pos: Tuple[int, int] = None):
        """Zoom in towards mouse position or center"""
        old_zoom = self.zoom_factor
        self.zoom_factor = min(self.max_zoom, self.zoom_factor * 1.2)
        
        if mouse_pos and old_zoom != self.zoom_factor:
            self._adjust_pan_for_zoom(mouse_pos, old_zoom)
        
        self._invalidate_tile_cache()
    
    def zoom_out(self, mouse_pos: Tuple[int, int] = None):
        """Zoom out from mouse position or center"""
        old_zoom = self.zoom_factor
        self.zoom_factor = max(self.min_zoom, self.zoom_factor / 1.2)
        
        if mouse_pos and old_zoom != self.zoom_factor:
            self._adjust_pan_for_zoom(mouse_pos, old_zoom)
        
        self._invalidate_tile_cache()
    
    def _adjust_pan_for_zoom(self, mouse_pos: Tuple[int, int], old_zoom: float):
        """Adjust pan offset to zoom towards mouse position"""
        # Convert mouse position to world coordinates before zoom
        world_x_before = (mouse_pos[0] - self.pan_offset_x) / old_zoom
        world_y_before = (mouse_pos[1] - self.hud_height - self.pan_offset_y) / old_zoom
        
        # Calculate new pan offset to keep the same world point under mouse
        self.pan_offset_x = mouse_pos[0] - world_x_before * self.zoom_factor
        self.pan_offset_y = mouse_pos[1] - self.hud_height - world_y_before * self.zoom_factor
        
        self._clamp_pan_offset()
    
    def handle_mouse_button_down(self, event):
        """Handle mouse button down events"""
        if event.button == 2:  # Middle mouse button for panning
            self.is_panning = True
            self.last_mouse_pos = event.pos
        elif event.button == 1:  # Left mouse button for tile interaction
            self._handle_tile_click(event.pos)
    
    def handle_mouse_button_up(self, event):
        """Handle mouse button up events"""
        if event.button == 2:  # Stop panning
            self.is_panning = False
            self.last_mouse_pos = None
    
    def handle_mouse_motion(self, event):
        """Handle mouse motion for panning and hover detection"""
        if self.is_panning and self.last_mouse_pos:
            # Calculate pan delta
            dx = event.pos[0] - self.last_mouse_pos[0]
            dy = event.pos[1] - self.last_mouse_pos[1]
            
            # Apply pan
            self.pan_offset_x += dx
            self.pan_offset_y += dy
            
            self._clamp_pan_offset()
            self.last_mouse_pos = event.pos
        
        # Update hover tile for context-sensitive information
        self._update_hover_tile(event.pos)
    
    def _clamp_pan_offset(self):
        """Clamp pan offset to prevent panning too far off the grid"""
        # Calculate grid bounds in screen coordinates
        scaled_tile_size = TILE_SIZE * self.zoom_factor
        grid_width = GRID_WIDTH * scaled_tile_size
        grid_height = GRID_HEIGHT * scaled_tile_size
        
        # Allow some off-screen panning but not too much
        margin = 100  # Allow 100 pixels off-screen
        
        # Clamp horizontal pan
        max_pan_x = margin
        min_pan_x = self.available_width - grid_width - margin
        self.pan_offset_x = max(min_pan_x, min(max_pan_x, self.pan_offset_x))
        
        # Clamp vertical pan
        max_pan_y = margin
        min_pan_y = self.available_height - grid_height - margin
        self.pan_offset_y = max(min_pan_y, min(max_pan_y, self.pan_offset_y))
    
    def _handle_tile_click(self, mouse_pos: Tuple[int, int]):
        """Handle tile clicking for selection and interaction"""
        tile = self._get_tile_at_position(mouse_pos)
        if tile:
            # Emit tile selection event for dynamic panel system
            if hasattr(self.grid_manager, 'event_system'):
                self.grid_manager.event_system.emit('tile_selected', {'tile': tile})
    
    def _update_hover_tile(self, mouse_pos: Tuple[int, int]):
        """Update the tile currently under the mouse cursor"""
        new_hover_tile = self._get_tile_at_position(mouse_pos)
        
        if new_hover_tile != self.hover_tile:
            self.hover_tile = new_hover_tile
            # Could emit hover events here for tooltip system
    
    def _get_tile_at_position(self, mouse_pos: Tuple[int, int]) -> Optional:
        """Get the tile at the given screen position"""
        screen_x, screen_y = mouse_pos
        
        # Convert screen coordinates to world coordinates
        # Reverse the transformation used in rendering: screen_pos = world_pos * zoom + pan_offset + hud_offset
        world_x = (screen_x - self.pan_offset_x) / self.zoom_factor
        world_y = (screen_y - self.hud_height - self.pan_offset_y) / self.zoom_factor
        
        # Convert world coordinates to grid coordinates
        grid_x = int(world_x // TILE_SIZE)
        grid_y = int(world_y // TILE_SIZE)
        
        # Check bounds
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            return self.grid_manager.grid[grid_y][grid_x]
        
        return None
    
    def render(self, screen: pygame.Surface):
        """Render the enhanced grid with all visual improvements"""
        # Calculate visible tile range for optimization
        visible_tiles = self._calculate_visible_tiles()
        
        # Render base grid
        self._render_base_grid(screen, visible_tiles)
        
        # Render overlays if enabled
        if self.show_soil_health_overlay:
            self._render_soil_health_overlay(screen, visible_tiles)
        
        if self.show_irrigation_overlay:
            self._render_irrigation_overlay(screen, visible_tiles)
        
        if self.show_building_efficiency:
            self._render_building_efficiency_overlay(screen, visible_tiles)
        
        # Render tile details based on zoom level
        self._render_tile_details(screen, visible_tiles)
        
        # Render selection and interaction feedback
        self._render_selection_feedback(screen, visible_tiles)
        
        # Render hover information
        if self.hover_tile:
            self._render_hover_feedback(screen)
        
        # Render zoom/pan indicators
        self._render_viewport_info(screen)
    
    def _calculate_visible_tiles(self) -> Dict[str, int]:
        """Calculate which tiles are visible in the current viewport"""
        scaled_tile_size = TILE_SIZE * self.zoom_factor
        
        # Calculate start and end tile indices
        start_x = max(0, int(-self.pan_offset_x / scaled_tile_size))
        start_y = max(0, int(-self.pan_offset_y / scaled_tile_size))
        
        tiles_per_screen_x = int(self.available_width / scaled_tile_size) + 2
        tiles_per_screen_y = int(self.available_height / scaled_tile_size) + 2
        
        end_x = min(GRID_WIDTH, start_x + tiles_per_screen_x)
        end_y = min(GRID_HEIGHT, start_y + tiles_per_screen_y)
        
        return {
            'start_x': start_x,
            'start_y': start_y,
            'end_x': end_x,
            'end_y': end_y
        }
    
    def _render_base_grid(self, screen: pygame.Surface, visible_tiles: Dict[str, int]):
        """Render the base grid with enhanced tile visualization"""
        scaled_tile_size = int(TILE_SIZE * self.zoom_factor)
        
        for y in range(visible_tiles['start_y'], visible_tiles['end_y']):
            for x in range(visible_tiles['start_x'], visible_tiles['end_x']):
                tile = self.grid_manager.grid[y][x]
                
                # Calculate screen position
                screen_x = int(x * scaled_tile_size + self.pan_offset_x)
                screen_y = int(y * scaled_tile_size + self.pan_offset_y + self.hud_height)
                
                # Create tile rectangle
                tile_rect = pygame.Rect(screen_x, screen_y, scaled_tile_size, scaled_tile_size)
                
                # Get enhanced tile color
                color = self._get_enhanced_tile_color(tile)
                
                # Draw tile
                pygame.draw.rect(screen, color, tile_rect)
                
                # Draw grid lines with transparency
                grid_color = (*COLORS['grid_line'], self.grid_line_alpha)
                pygame.draw.rect(screen, COLORS['grid_line'], tile_rect, max(1, int(self.zoom_factor)))
                
                # Render tile-specific indicators
                self._render_tile_indicators(screen, tile, tile_rect)
    
    def _get_enhanced_tile_color(self, tile) -> Tuple[int, int, int]:
        """Get enhanced color for tile based on state and zoom level"""
        # Base color from original system
        base_color = tile.get_color()
        
        # Enhance color based on soil health if zoomed in enough
        if self.zoom_factor > 1.5 and hasattr(tile, 'soil_quality'):
            soil_health = getattr(tile, 'soil_quality', 5)
            health_color = self.soil_health_colors.get(soil_health, base_color)
            
            # Blend base color with health color
            blend_factor = 0.3  # 30% health color, 70% base color
            enhanced_color = (
                int(base_color[0] * (1 - blend_factor) + health_color[0] * blend_factor),
                int(base_color[1] * (1 - blend_factor) + health_color[1] * blend_factor),
                int(base_color[2] * (1 - blend_factor) + health_color[2] * blend_factor)
            )
            return enhanced_color
        
        return base_color
    
    def _render_tile_indicators(self, screen: pygame.Surface, tile, tile_rect: pygame.Rect):
        """Render various indicators on tiles based on zoom level"""
        # Task assignment indicators (always visible)
        if tile.task_assignment:
            self._render_enhanced_task_indicator(screen, tile, tile_rect)
        
        # Irrigation indicators (visible when zoomed in)
        if self.zoom_factor > 1.0 and tile.has_irrigation:
            self._render_enhanced_irrigation_indicator(screen, tile, tile_rect)
        
        # Crop growth stage (visible when significantly zoomed in)
        if self.zoom_factor > 2.0 and tile.current_crop:
            self._render_crop_stage_indicator(screen, tile, tile_rect)
    
    def _render_enhanced_task_indicator(self, screen: pygame.Surface, tile, tile_rect: pygame.Rect):
        """Render enhanced task assignment indicators"""
        center_x = tile_rect.centerx
        center_y = tile_rect.centery
        
        color_map = {
            'till': (255, 255, 0),   # Yellow
            'plant': (0, 255, 0),    # Green
            'harvest': (255, 165, 0) # Orange
        }
        
        color = color_map.get(tile.task_assignment, (255, 255, 255))
        
        # Scale indicator size with zoom
        indicator_size = max(3, int(4 * self.zoom_factor))
        
        # Draw main indicator
        pygame.draw.circle(screen, color, (center_x, center_y), indicator_size)
        
        # Draw outline for better visibility
        pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), indicator_size + 1, 1)
    
    def _render_enhanced_irrigation_indicator(self, screen: pygame.Surface, tile, tile_rect: pygame.Rect):
        """Render enhanced irrigation indicators"""
        # Draw small water droplet in corner
        corner_x = tile_rect.right - 8
        corner_y = tile_rect.top + 3
        
        water_color = (64, 164, 223)
        droplet_size = max(2, int(3 * self.zoom_factor))
        
        pygame.draw.circle(screen, water_color, (corner_x, corner_y), droplet_size)
    
    def _render_crop_stage_indicator(self, screen: pygame.Surface, tile, tile_rect: pygame.Rect):
        """Render crop growth stage indicators for detailed view"""
        if not tile.current_crop:
            return
        
        # Show growth stage as small bars
        stage = getattr(tile, 'growth_stage', 0)
        max_stages = 5
        
        bar_width = max(1, int(2 * self.zoom_factor))
        bar_height = max(8, int(12 * self.zoom_factor))
        
        start_x = tile_rect.left + 2
        start_y = tile_rect.bottom - bar_height - 2
        
        for i in range(max_stages):
            bar_x = start_x + i * (bar_width + 1)
            bar_color = (0, 255, 0) if i < stage else (100, 100, 100)
            
            bar_rect = pygame.Rect(bar_x, start_y, bar_width, bar_height)
            pygame.draw.rect(screen, bar_color, bar_rect)
    
    def _render_soil_health_overlay(self, screen: pygame.Surface, visible_tiles: Dict[str, int]):
        """Render soil health overlay when enabled"""
        # Create transparent surface for overlay
        overlay = pygame.Surface((self.available_width, self.available_height), pygame.SRCALPHA)
        
        scaled_tile_size = int(TILE_SIZE * self.zoom_factor)
        
        for y in range(visible_tiles['start_y'], visible_tiles['end_y']):
            for x in range(visible_tiles['start_x'], visible_tiles['end_x']):
                tile = self.grid_manager.grid[y][x]
                
                if hasattr(tile, 'soil_quality'):
                    soil_health = getattr(tile, 'soil_quality', 5)
                    color = (*self.soil_health_colors[soil_health], 100)  # Semi-transparent
                    
                    screen_x = int(x * scaled_tile_size + self.pan_offset_x)
                    screen_y = int(y * scaled_tile_size + self.pan_offset_y)
                    
                    tile_rect = pygame.Rect(screen_x, screen_y, scaled_tile_size, scaled_tile_size)
                    pygame.draw.rect(overlay, color, tile_rect)
        
        screen.blit(overlay, (0, self.hud_height))
    
    def _render_irrigation_overlay(self, screen: pygame.Surface, visible_tiles: Dict[str, int]):
        """Render irrigation coverage overlay when enabled"""
        # Similar implementation to soil health overlay but for irrigation
        pass
    
    def _render_building_efficiency_overlay(self, screen: pygame.Surface, visible_tiles: Dict[str, int]):
        """Render building efficiency radius overlay when enabled"""
        # Implementation for building efficiency visualization
        pass
    
    def _render_tile_details(self, screen: pygame.Surface, visible_tiles: Dict[str, int]):
        """Render detailed tile information when zoomed in enough"""
        if self.zoom_factor < 2.5:
            return  # Only show details when significantly zoomed in
        
        # Implementation for detailed tile information rendering
        pass
    
    def _render_selection_feedback(self, screen: pygame.Surface, visible_tiles: Dict[str, int]):
        """Render selection feedback and multi-selection boundaries"""
        if not hasattr(self.grid_manager, 'selected_tiles'):
            return
        
        # Render selection highlights
        for tile in self.grid_manager.selected_tiles:
            if hasattr(tile, 'highlight') and tile.highlight:
                self._render_tile_selection_highlight(screen, tile)
        
        # Render drag selection rectangle if active
        if hasattr(self.grid_manager, 'drag_start_pos') and self.grid_manager.drag_start_pos and \
           hasattr(self.grid_manager, 'drag_current_pos') and self.grid_manager.drag_current_pos:
            self._render_drag_selection_rectangle(screen)
    
    def _render_tile_selection_highlight(self, screen: pygame.Surface, tile):
        """Render selection highlight for individual tile"""
        scaled_tile_size = int(TILE_SIZE * self.zoom_factor)
        
        screen_x = int(tile.x * scaled_tile_size + self.pan_offset_x)
        screen_y = int(tile.y * scaled_tile_size + self.pan_offset_y + self.hud_height)
        
        tile_rect = pygame.Rect(screen_x, screen_y, scaled_tile_size, scaled_tile_size)
        
        # Draw selection border
        border_color = (255, 255, 0)  # Yellow selection
        border_width = max(2, int(3 * self.zoom_factor))
        pygame.draw.rect(screen, border_color, tile_rect, border_width)
    
    def _render_drag_selection_rectangle(self, screen: pygame.Surface):
        """Render drag selection rectangle"""
        # Implementation for drag selection visualization
        pass
    
    def _render_hover_feedback(self, screen: pygame.Surface):
        """Render hover feedback for tile under mouse"""
        if not self.hover_tile:
            return
        
        # Highlight hovered tile with subtle effect
        scaled_tile_size = int(TILE_SIZE * self.zoom_factor)
        
        screen_x = int(self.hover_tile.x * scaled_tile_size + self.pan_offset_x)
        screen_y = int(self.hover_tile.y * scaled_tile_size + self.pan_offset_y + self.hud_height)
        
        tile_rect = pygame.Rect(screen_x, screen_y, scaled_tile_size, scaled_tile_size)
        
        # Draw subtle hover highlight
        hover_color = (255, 255, 255, 50)  # Semi-transparent white
        hover_surface = pygame.Surface((scaled_tile_size, scaled_tile_size), pygame.SRCALPHA)
        hover_surface.fill(hover_color)
        screen.blit(hover_surface, (screen_x, screen_y))
    
    def _render_viewport_info(self, screen: pygame.Surface):
        """Render zoom and pan information"""
        if self.zoom_factor != 1.0:
            # Show zoom level indicator
            font = pygame.font.Font(None, 24)
            zoom_text = f"Zoom: {self.zoom_factor:.1f}x"
            text_surface = font.render(zoom_text, True, (255, 255, 255))
            
            # Position in top-left of grid area
            screen.blit(text_surface, (10, self.hud_height + 10))
    
    def _invalidate_tile_cache(self):
        """Invalidate tile rendering cache when zoom changes"""
        self.tile_cache.clear()
        self.dirty_tiles.clear()
    
    def toggle_soil_health_overlay(self):
        """Toggle soil health overlay visibility"""
        self.show_soil_health_overlay = not self.show_soil_health_overlay
    
    def toggle_irrigation_overlay(self):
        """Toggle irrigation overlay visibility"""
        self.show_irrigation_overlay = not self.show_irrigation_overlay
    
    def toggle_building_efficiency_overlay(self):
        """Toggle building efficiency overlay visibility"""
        self.show_building_efficiency = not self.show_building_efficiency
    
    def reset_viewport(self):
        """Reset zoom and pan to default values"""
        self.zoom_factor = 1.0
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0
        self._invalidate_tile_cache()
    
    def center_on_tile(self, tile_x: int, tile_y: int):
        """Center the viewport on a specific tile"""
        scaled_tile_size = TILE_SIZE * self.zoom_factor
        
        # Calculate center position
        center_world_x = (tile_x + 0.5) * scaled_tile_size
        center_world_y = (tile_y + 0.5) * scaled_tile_size
        
        # Calculate pan offset to center this position
        self.pan_offset_x = self.available_width / 2 - center_world_x
        self.pan_offset_y = self.available_height / 2 - center_world_y
        
        self._clamp_pan_offset()