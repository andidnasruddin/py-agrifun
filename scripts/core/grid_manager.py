"""
Grid Manager - Handles the 16x16 tile grid system
Manages tile states, rendering, and interactions for the farming simulation.
"""

import pygame
from typing import List, Tuple, Optional, Dict
from scripts.core.config import *


class Tile:
    """Individual tile in the farming grid"""
    
    def __init__(self, x: int, y: int):
        """Initialize a tile at grid position (x, y)"""
        self.x = x
        self.y = y
        
        # Tile properties
        self.terrain_type = 'soil'  # 'soil', 'tilled', 'planted'
        self.soil_quality = 5  # 1-10 scale
        self.water_level = 100  # 0-100 scale
        
        # Crop information - now supports multiple crop types
        self.current_crop = None  # crop type string or None
        self.growth_stage = 0  # 0-4 for all crops
        self.days_growing = 0
        
        # Task assignment
        self.task_assignment = None  # 'till', 'plant', 'harvest', or None
        self.task_assigned_to = None  # Employee ID
        
        # Visual properties
        self.highlight = False  # For UI selection
        self.rect = pygame.Rect(
            x * TILE_SIZE, 
            y * TILE_SIZE + 70,  # Offset for UI panel
            TILE_SIZE, 
            TILE_SIZE
        )
    
    def can_till(self) -> bool:
        """Check if tile can be tilled"""
        return self.terrain_type == 'soil' and self.current_crop is None
    
    def can_plant(self, crop_type: str = 'corn') -> bool:
        """Check if tile can be planted with a crop"""
        return (self.terrain_type == 'tilled' and 
                self.current_crop is None and 
                crop_type in CROP_TYPES)  # Support all defined crop types
    
    def can_harvest(self) -> bool:
        """Check if tile can be harvested"""
        return (self.current_crop is not None and 
                self.growth_stage >= len(GROWTH_STAGES) - 1)
    
    def till(self):
        """Till the soil"""
        if self.can_till():
            self.terrain_type = 'tilled'
            return True
        return False
    
    def plant(self, crop_type: str = 'corn'):
        """Plant a crop"""
        if self.can_plant(crop_type):
            self.current_crop = crop_type
            self.terrain_type = 'planted'
            self.growth_stage = 0
            self.days_growing = 0
            print(f"Planted {crop_type} at ({self.x}, {self.y})")
            return True
        return False
    
    def harvest(self) -> Tuple[str, int]:
        """Harvest the crop and return (crop_type, yield)"""
        if self.can_harvest():
            crop_type = self.current_crop
            crop_data = CROP_TYPES[crop_type]
            
            # Calculate yield based on soil quality and care
            base_yield = crop_data['base_yield']
            quality_modifier = self.soil_quality / 10.0
            water_modifier = self.water_level / 100.0
            
            yield_amount = int(base_yield * quality_modifier * water_modifier)
            
            # Reset tile after harvest
            self.current_crop = None
            self.terrain_type = 'tilled'  # Stays tilled for next crop
            self.growth_stage = 0
            self.days_growing = 0
            
            return crop_type, max(1, yield_amount)  # Return crop type and amount
        
        return None, 0
    
    def update_growth(self, days_passed: float):
        """Update crop growth for any crop type"""
        if self.current_crop and self.current_crop in CROP_TYPES:
            self.days_growing += days_passed
            crop_data = CROP_TYPES[self.current_crop]
            
            # Calculate growth stage based on days
            days_per_stage = crop_data['growth_time'] / len(GROWTH_STAGES)
            new_stage = min(
                len(GROWTH_STAGES) - 1,
                int(self.days_growing / days_per_stage)
            )
            
            if new_stage > self.growth_stage:
                old_stage = self.growth_stage
                self.growth_stage = new_stage
                print(f"{crop_data['name']} at ({self.x}, {self.y}) grew from stage {old_stage} to {new_stage} ({GROWTH_STAGES[new_stage]}) - days: {self.days_growing:.2f}")
                return True  # Growth stage changed
        
        return False
    
    def get_color(self) -> Tuple[int, int, int]:
        """Get the color for rendering this tile"""
        if self.highlight:
            # Add highlight effect
            base_color = self._get_base_color()
            return tuple(min(255, c + 50) for c in base_color)
        
        return self._get_base_color()
    
    def _get_base_color(self) -> Tuple[int, int, int]:
        """Get base color based on tile state and crop type"""
        if self.current_crop:
            # Different colors for different crop types
            if self.current_crop == 'corn':
                # Green shades for corn growth stages
                green_intensity = 50 + (self.growth_stage * 40)
                return (0, min(255, green_intensity), 0)
            elif self.current_crop == 'tomatoes':
                # Red shades for tomato growth stages  
                red_intensity = 50 + (self.growth_stage * 40)
                return (min(255, red_intensity), 20, 0)
            elif self.current_crop == 'wheat':
                # Golden shades for wheat growth stages
                gold_intensity = 80 + (self.growth_stage * 35)
                return (min(255, gold_intensity), min(200, gold_intensity - 20), 0)
            else:
                # Default green for unknown crops
                green_intensity = 50 + (self.growth_stage * 40)
                return (0, min(255, green_intensity), 0)
        elif self.terrain_type == 'tilled':
            return COLORS['tile_tilled']
        else:
            return COLORS['tile_soil']


class GridManager:
    """Manages the 16x16 tile grid"""
    
    def __init__(self, event_system):
        """Initialize the grid manager"""
        self.event_system = event_system
        
        # Create the grid
        self.grid: List[List[Tile]] = []
        self._create_grid()
        
        # Selection state
        self.selected_tiles: List[Tile] = []
        self.drag_start_pos: Optional[Tuple[int, int]] = None
        self.drag_current_pos: Optional[Tuple[int, int]] = None
        
        # Register for events
        self.event_system.subscribe('day_passed', self._handle_day_passed)
        self.event_system.subscribe('task_assigned', self._handle_task_assignment)
        
        print(f"Grid Manager initialized with {GRID_WIDTH}x{GRID_HEIGHT} tiles")
    
    def _create_grid(self):
        """Create the initial tile grid"""
        for y in range(GRID_HEIGHT):
            row = []
            for x in range(GRID_WIDTH):
                tile = Tile(x, y)
                # Randomize soil quality slightly
                import random
                tile.soil_quality = random.randint(3, 8)
                row.append(tile)
            self.grid.append(row)
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at grid position"""
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            return self.grid[y][x]
        return None
    
    def get_tile_at_pixel(self, px: int, py: int) -> Optional[Tile]:
        """Get tile at pixel position"""
        # Account for UI offset
        py -= 70
        
        if py < 0:  # Click in UI area
            return None
            
        grid_x = px // TILE_SIZE
        grid_y = py // TILE_SIZE
        
        return self.get_tile(grid_x, grid_y)
    
    def handle_mouse_down(self, pos: Tuple[int, int], button: int):
        """Handle mouse button down for tile selection"""
        if button == 1:  # Left click
            self.drag_start_pos = pos
            tile = self.get_tile_at_pixel(*pos)
            if tile:
                self._clear_selection()
                self.selected_tiles = [tile]
                tile.highlight = True
    
    def handle_mouse_drag(self, pos: Tuple[int, int]):
        """Handle mouse drag for area selection"""
        if self.drag_start_pos:
            self.drag_current_pos = pos
            self._update_drag_selection()
    
    def handle_mouse_up(self, pos: Tuple[int, int], button: int):
        """Handle mouse button up"""
        if button == 1:  # Left click
            if self.drag_start_pos and self.drag_current_pos:
                # Finalize selection
                pass
            
            self.drag_start_pos = None
            self.drag_current_pos = None
    
    def _update_drag_selection(self):
        """Update tile selection based on drag area"""
        if not (self.drag_start_pos and self.drag_current_pos):
            return
        
        # Calculate selection rectangle
        start_x, start_y = self.drag_start_pos
        end_x, end_y = self.drag_current_pos
        
        # Adjust for UI offset
        start_y -= 70
        end_y -= 70
        
        # Ensure valid bounds
        if start_y < 0 or end_y < 0:
            return
        
        # Convert to grid coordinates
        start_gx = start_x // TILE_SIZE
        start_gy = start_y // TILE_SIZE
        end_gx = end_x // TILE_SIZE
        end_gy = end_y // TILE_SIZE
        
        # Ensure correct order
        min_x = min(start_gx, end_gx)
        max_x = max(start_gx, end_gx)
        min_y = min(start_gy, end_gy)
        max_y = max(start_gy, end_gy)
        
        # Clear and rebuild selection
        self._clear_selection()
        
        for y in range(max(0, min_y), min(GRID_HEIGHT, max_y + 1)):
            for x in range(max(0, min_x), min(GRID_WIDTH, max_x + 1)):
                tile = self.grid[y][x]
                self.selected_tiles.append(tile)
                tile.highlight = True
    
    def _clear_selection(self):
        """Clear current tile selection"""
        for tile in self.selected_tiles:
            tile.highlight = False
        self.selected_tiles.clear()
    
    def assign_task_to_selection(self, task_type: str, employee_id: str):
        """Assign a task to all selected tiles"""
        assigned_count = 0
        
        for tile in self.selected_tiles:
            if self._can_assign_task(tile, task_type):
                tile.task_assignment = task_type
                tile.task_assigned_to = employee_id
                assigned_count += 1
        
        if assigned_count > 0:
            self.event_system.emit('task_assigned', {
                'task_type': task_type,
                'employee_id': employee_id,
                'tile_count': assigned_count,
                'tiles': self.selected_tiles.copy()
            })
        
        return assigned_count
    
    def _can_assign_task(self, tile: Tile, task_type: str) -> bool:
        """Check if a task can be assigned to a tile"""
        if task_type == 'till':
            return tile.can_till()
        elif task_type == 'plant':
            return tile.can_plant()
        elif task_type == 'harvest':
            return tile.can_harvest()
        
        return False
    
    def update(self, dt: float):
        """Update grid state"""
        # Update crop growth based on game time progression
        # Get time speed from time manager if available
        if hasattr(self, 'time_manager') and self.time_manager:
            time_speed = getattr(self.time_manager, 'time_speed', 1)
            # Apply time speed to growth: faster game time = faster crop growth
            game_time_dt = dt * time_speed
        else:
            game_time_dt = dt
            
        # Convert real seconds to game time (20 minutes real = 1 game day)
        days_per_frame = game_time_dt / (20 * 60)
        
        for row in self.grid:
            for tile in row:
                if tile.current_crop:
                    tile.update_growth(days_per_frame)
    
    def render(self, screen: pygame.Surface):
        """Render the grid"""
        # Render tiles
        for row in self.grid:
            for tile in row:
                color = tile.get_color()
                pygame.draw.rect(screen, color, tile.rect)
                
                # Draw grid lines
                pygame.draw.rect(screen, COLORS['grid_line'], tile.rect, 1)
                
                # Draw task assignment indicator
                if tile.task_assignment:
                    self._render_task_indicator(screen, tile)
        
        # Render selection rectangle if dragging
        if self.drag_start_pos and self.drag_current_pos:
            self._render_selection_rectangle(screen)
    
    def _render_task_indicator(self, screen: pygame.Surface, tile: Tile):
        """Render task assignment indicator on tile"""
        center_x = tile.rect.centerx
        center_y = tile.rect.centery
        
        color_map = {
            'till': (255, 255, 0),   # Yellow
            'plant': (0, 255, 0),    # Green
            'harvest': (255, 165, 0) # Orange
        }
        
        color = color_map.get(tile.task_assignment, (255, 255, 255))
        pygame.draw.circle(screen, color, (center_x, center_y), 4)
    
    def _render_selection_rectangle(self, screen: pygame.Surface):
        """Render drag selection rectangle"""
        start_x, start_y = self.drag_start_pos
        end_x, end_y = self.drag_current_pos
        
        # Create rectangle
        rect_x = min(start_x, end_x)
        rect_y = min(start_y, end_y)
        rect_w = abs(end_x - start_x)
        rect_h = abs(end_y - start_y)
        
        selection_rect = pygame.Rect(rect_x, rect_y, rect_w, rect_h)
        pygame.draw.rect(screen, (255, 255, 255), selection_rect, 2)
    
    def _handle_day_passed(self, event_data):
        """Handle day passing for crop growth"""
        days_passed = event_data.get('days', 1)
        print(f"Grid Manager: Day passed, updating crop growth by {days_passed} days")
        
        crops_updated = 0
        for row in self.grid:
            for tile in row:
                if tile.update_growth(days_passed):
                    crops_updated += 1
        
        if crops_updated > 0:
            print(f"Updated growth for {crops_updated} crops")
    
    def _handle_task_assignment(self, event_data):
        """Handle task assignment events"""
        # Tasks are assigned by this manager, so just log for now
        task_type = event_data.get('task_type')
        tile_count = event_data.get('tile_count')
        print(f"Assigned {task_type} task to {tile_count} tiles")