"""
Grid Manager - Handles the 16x16 tile grid system
Manages tile states, rendering, and interactions for the farming simulation.
"""

import pygame
from typing import List, Tuple, Optional, Dict
from scripts.core.config import *
from scripts.ui.enhanced_grid_renderer import EnhancedGridRenderer


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
        
        # Soil Health System - nutrient levels for crop rotation
        self.soil_nutrients = {
            'nitrogen': 100,    # Nitrogen level (0-100)
            'phosphorus': 100,  # Phosphorus level (0-100) 
            'potassium': 100    # Potassium level (0-100)
        }
        
        # Crop History for rotation bonuses
        self.crop_history = []  # List of previous crops grown on this tile
        self.seasons_rested = 0  # Seasons since last crop (for soil rest bonus)
        
        # Crop information - now supports multiple crop types
        self.current_crop = None  # crop type string or None
        self.growth_stage = 0  # 0-4 for all crops
        self.days_growing = 0
        
        # Task assignment
        self.task_assignment = None  # 'till', 'plant', 'harvest', or None
        self.task_assigned_to = None  # Employee ID
        
        # Building information
        self.building = None  # Building object if this tile has a building
        self.building_type = None  # Building type ID for rendering
        self.is_occupied = False  # True if tile has building or is unusable
        
        # Irrigation system
        self.has_irrigation = False  # True if tile has irrigation infrastructure
        
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
        return (self.terrain_type == 'soil' and 
                self.current_crop is None and 
                not self.is_occupied)
    
    def can_place_building(self) -> bool:
        """Check if a building can be placed on this tile"""
        return (self.terrain_type == 'soil' and 
                self.current_crop is None and 
                not self.is_occupied and 
                self.building is None)
    
    def place_building(self, building_type_id: str, building_object=None):
        """Place a building on this tile"""
        if self.can_place_building():
            self.building_type = building_type_id
            self.building = building_object
            self.is_occupied = True
            self.terrain_type = 'building'
            return True
        return False
    
    def remove_building(self):
        """Remove building from this tile"""
        if self.building:
            self.building_type = None
            self.building = None
            self.is_occupied = False
            self.terrain_type = 'soil'
            return True
        return False
    
    def can_interact_with_building(self) -> bool:
        """Check if this tile's building can be interacted with"""
        return self.building is not None and self.building_type is not None
    
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
        print(f"Tile.till() called on ({self.x}, {self.y}) - terrain: {self.terrain_type}, can_till: {self.can_till()}")
        if self.can_till():
            print(f"Tile ({self.x}, {self.y}): Changing terrain from {self.terrain_type} to tilled")
            self.terrain_type = 'tilled'
            print(f"Tile ({self.x}, {self.y}): Terrain changed to {self.terrain_type}")
            return True
        else:
            print(f"Tile ({self.x}, {self.y}): Cannot till - terrain: {self.terrain_type}, crop: {self.current_crop}, occupied: {self.is_occupied}")
            return False
    
    def plant(self, crop_type: str = 'corn'):
        """Plant a crop with soil health effects and rotation bonuses"""
        if self.can_plant(crop_type):
            # Calculate rotation bonuses before planting
            rotation_bonuses = self.calculate_rotation_bonuses(crop_type)
            
            # Apply soil effects from planting this crop
            self.apply_crop_soil_effects(crop_type)
            
            # Plant the crop
            self.current_crop = crop_type
            self.terrain_type = 'planted'
            self.growth_stage = 0
            self.days_growing = 0
            
            # Store rotation bonuses for later use in harvest
            self.rotation_bonuses = rotation_bonuses
            
            # Print planting info with bonuses
            crop_name = CROP_TYPES[crop_type]['name']
            print(f"Planted {crop_name} at ({self.x}, {self.y})")
            
            if rotation_bonuses['descriptions']:
                print(f"  Rotation bonuses: +{rotation_bonuses['yield']*100:.0f}% yield, +{rotation_bonuses['quality']*100:.0f}% quality")
                for desc in rotation_bonuses['descriptions']:
                    print(f"    - {desc}")
            
            return True
        return False
    
    def harvest(self, grid_manager=None) -> Tuple[str, int]:
        """Harvest the crop and return (crop_type, yield)"""
        if self.can_harvest():
            crop_type = self.current_crop
            crop_data = CROP_TYPES[crop_type]
            
            # Calculate yield based on soil quality and care
            base_yield = crop_data['base_yield']
            quality_modifier = self.soil_quality / 10.0
            water_modifier = self.water_level / 100.0
            
            # Calculate base yield
            yield_amount = base_yield * quality_modifier * water_modifier
            
            # Apply crop rotation bonuses if available
            rotation_yield_bonus = 0.0
            rotation_quality_bonus = 0.0
            if hasattr(self, 'rotation_bonuses') and self.rotation_bonuses:
                rotation_yield_bonus = self.rotation_bonuses.get('yield', 0.0)
                rotation_quality_bonus = self.rotation_bonuses.get('quality', 0.0)
                yield_amount *= (1.0 + rotation_yield_bonus)
                
                if rotation_yield_bonus > 0:
                    print(f"  Crop rotation bonuses: +{rotation_yield_bonus*100:.0f}% yield")
            
            # Apply soil health effects to quality and yield
            soil_health_level = self.get_soil_health_level()
            soil_health_multiplier = SOIL_HEALTH_LEVELS[soil_health_level]['bonus_multiplier']
            yield_amount *= soil_health_multiplier
            
            if soil_health_multiplier != 1.0:
                effect = "bonus" if soil_health_multiplier > 1.0 else "penalty"
                print(f"  Soil health ({soil_health_level}): {soil_health_multiplier*100:.0f}% {effect}")
            
            # Apply specialization bonuses if grid manager and specialization manager available
            specialization_bonus_applied = False
            if (grid_manager and hasattr(grid_manager, 'game_manager') and 
                hasattr(grid_manager.game_manager, 'specialization_manager')):
                spec_manager = grid_manager.game_manager.specialization_manager
                
                # Apply crop-specific yield bonuses
                if crop_type == 'wheat':
                    wheat_bonus = spec_manager.get_bonus_multiplier('wheat_yield_multiplier', 1.0)
                    if wheat_bonus > 1.0:
                        yield_amount *= wheat_bonus
                        bonus_percent = int((wheat_bonus - 1.0) * 100)
                        print(f"  Grain specialization: +{bonus_percent}% wheat yield")
                        specialization_bonus_applied = True
                        
                elif crop_type == 'tomatoes':
                    tomato_bonus = spec_manager.get_bonus_multiplier('tomato_yield_multiplier', 1.0)
                    if tomato_bonus > 1.0:
                        yield_amount *= tomato_bonus
                        bonus_percent = int((tomato_bonus - 1.0) * 100)
                        print(f"  Market garden specialization: +{bonus_percent}% tomato yield")
                        specialization_bonus_applied = True
                
                # Apply overall crop quality bonus from diversified specialization
                overall_bonus = spec_manager.get_bonus_multiplier('overall_crop_quality', 1.0)
                if overall_bonus > 1.0:
                    yield_amount *= overall_bonus
                    bonus_percent = int((overall_bonus - 1.0) * 100)
                    print(f"  Diversified specialization: +{bonus_percent}% overall quality")
                    specialization_bonus_applied = True
                
                # Apply rotation bonus multiplier from diversified specialization
                if rotation_yield_bonus > 0:
                    rotation_multiplier = spec_manager.get_bonus_multiplier('rotation_bonus_multiplier', 1.0)
                    if rotation_multiplier > 1.0:
                        additional_rotation_bonus = (rotation_multiplier - 1.0) * rotation_yield_bonus
                        yield_amount *= (1.0 + additional_rotation_bonus)
                        bonus_percent = int(additional_rotation_bonus * 100)
                        print(f"  Enhanced rotation bonus: +{bonus_percent}% from diversified specialization")
                        specialization_bonus_applied = True
            
            # Apply building-based yield bonuses if grid manager available
            if grid_manager and hasattr(grid_manager, 'building_manager') and grid_manager.building_manager:
                # Use the unified spatial benefits system from building manager
                final_yield = grid_manager.building_manager.calculate_crop_yield_at(self.x, self.y, int(yield_amount))
                if final_yield > yield_amount:
                    bonus_percent = int(((final_yield / yield_amount) - 1.0) * 100)
                    print(f"  Building bonuses: +{bonus_percent}% yield at ({self.x}, {self.y})")
                yield_amount = final_yield
            else:
                # Fallback to legacy storage silo bonus system for compatibility
                silo_bonus = self._calculate_storage_silo_bonus(grid_manager)
                yield_amount *= (1.0 + silo_bonus)
                if silo_bonus > 0:
                    print(f"  Storage silo bonus: +{silo_bonus*100:.0f}% yield at ({self.x}, {self.y})")
            
            # Reset tile after harvest
            self.current_crop = None
            self.terrain_type = 'tilled'  # Stays tilled for next crop
            self.growth_stage = 0
            self.days_growing = 0
            
            return crop_type, max(1, int(yield_amount))  # Return crop type and amount
        
        return None, 0
    
    def _calculate_storage_silo_bonus(self, grid_manager) -> float:
        """Calculate yield bonus from nearby storage silos"""
        # Check for storage silos within 4 tiles (Manhattan distance)
        storage_silos = grid_manager.find_buildings_of_type('storage_silo')
        
        for silo_x, silo_y in storage_silos:
            # Calculate Manhattan distance to storage silo
            distance = abs(self.x - silo_x) + abs(self.y - silo_y)
            if distance <= 4:  # Within 4 tiles
                return 0.10  # +10% yield bonus
        
        return 0.0  # No bonus
    
    def get_soil_health_level(self) -> str:
        """Get overall soil health level based on nutrient levels"""
        # Calculate average soil nutrient level
        avg_nutrients = sum(self.soil_nutrients.values()) / len(self.soil_nutrients)
        
        # Determine health level based on average
        for level, data in SOIL_HEALTH_LEVELS.items():
            if avg_nutrients >= data['min']:
                return level
        return 'depleted'
    
    def get_soil_health_color(self) -> tuple:
        """Get color for soil health visualization"""
        health_level = self.get_soil_health_level()
        return SOIL_HEALTH_LEVELS[health_level]['color']
    
    def apply_crop_soil_effects(self, crop_type: str):
        """Apply soil nutrient changes when a crop is planted"""
        if crop_type not in CROP_SOIL_EFFECTS:
            return
        
        effects = CROP_SOIL_EFFECTS[crop_type]
        
        # Apply nutrient depletion
        for nutrient, amount in effects['depletes'].items():
            if nutrient in self.soil_nutrients:
                self.soil_nutrients[nutrient] = max(0, self.soil_nutrients[nutrient] - amount)
        
        # Apply nutrient restoration (for future nitrogen-fixing crops)
        for nutrient, amount in effects['restores'].items():
            if nutrient in self.soil_nutrients:
                self.soil_nutrients[nutrient] = min(100, self.soil_nutrients[nutrient] + amount)
        
        # Update crop history
        self.crop_history.append(crop_type)
        # Keep only last 3 crops for rotation analysis
        if len(self.crop_history) > 3:
            self.crop_history.pop(0)
        
        # Reset resting seasons
        self.seasons_rested = 0
        
        print(f"Tile ({self.x}, {self.y}): Applied {crop_type} soil effects - Nutrients now N:{self.soil_nutrients['nitrogen']} P:{self.soil_nutrients['phosphorus']} K:{self.soil_nutrients['potassium']}")
    
    def calculate_rotation_bonuses(self, crop_type: str) -> dict:
        """Calculate rotation bonuses for planting this crop type"""
        bonuses = {'yield': 0.0, 'quality': 0.0, 'descriptions': []}
        
        if not crop_type or crop_type not in CROP_TYPES:
            return bonuses
        
        # Check for soil rest bonus
        if self.seasons_rested >= 1:  # At least one season of rest
            rest_bonus = ROTATION_BONUSES['soil_rest']
            if crop_type in rest_bonus['applicable_to']:
                bonuses['yield'] += rest_bonus['yield_bonus']
                bonuses['quality'] += rest_bonus['quality_bonus']
                bonuses['descriptions'].append(rest_bonus['description'])
        
        # Check for crop rotation bonuses
        if len(self.crop_history) >= 1:
            last_crop = self.crop_history[-1]
            last_crop_category = CROP_SOIL_EFFECTS.get(last_crop, {}).get('category', '')
            
            # After heavy feeder bonus
            if last_crop_category == 'heavy_feeder':
                rotation_bonus = ROTATION_BONUSES['after_heavy_feeder']
                if crop_type in rotation_bonus['applicable_to']:
                    bonuses['yield'] += rotation_bonus['yield_bonus']
                    bonuses['quality'] += rotation_bonus['quality_bonus']
                    bonuses['descriptions'].append(rotation_bonus['description'])
        
        # Check for diverse rotation bonus
        if len(self.crop_history) >= 2:
            recent_crops = set(self.crop_history[-2:])  # Last 2 crops
            if crop_type not in recent_crops:  # Different from recent crops
                diverse_bonus = ROTATION_BONUSES['diverse_rotation']
                if crop_type in diverse_bonus['applicable_to']:
                    bonuses['yield'] += diverse_bonus['yield_bonus']
                    bonuses['quality'] += diverse_bonus['quality_bonus']
                    bonuses['descriptions'].append(diverse_bonus['description'])
        
        return bonuses
    
    def rest_soil(self):
        """Let soil rest for a season (called when tile is not planted)"""
        # Gradually restore nutrients when soil rests
        for nutrient in self.soil_nutrients:
            self.soil_nutrients[nutrient] = min(100, self.soil_nutrients[nutrient] + 5)
        
        self.seasons_rested += 1
    
    def update_growth(self, days_passed: float, weather_growth_modifier: float = 1.0):
        """Update crop growth for any crop type with weather effects"""
        if self.current_crop and self.current_crop in CROP_TYPES:
            # Apply weather modifier to growth rate
            effective_days_passed = days_passed * weather_growth_modifier
            self.days_growing += effective_days_passed
            
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
                weather_info = f" (weather: {weather_growth_modifier:.2f}x)" if weather_growth_modifier != 1.0 else ""
                print(f"{crop_data['name']} at ({self.x}, {self.y}) grew from stage {old_stage} to {new_stage} ({GROWTH_STAGES[new_stage]}) - days: {self.days_growing:.2f}{weather_info}")
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
        """Get base color based on tile state, crop type, and buildings"""
        # Buildings take priority over everything else
        if self.building_type:
            # Different colors for different building types
            if self.building_type == 'storage_silo':
                return (128, 128, 128)  # Gray for storage silos
            elif self.building_type == 'water_cooler':
                return (100, 150, 255)  # Light blue for water cooler
            elif self.building_type == 'tool_shed':
                return (139, 69, 19)    # Brown for tool shed
            elif self.building_type == 'employee_housing':
                return (255, 200, 100)  # Light orange for housing
            elif self.building_type == 'irrigation_system':
                return (64, 164, 223)   # Water blue for irrigation system
            else:
                return (80, 80, 80)     # Dark gray for unknown buildings
        elif self.current_crop:
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
        
        # Building placement preview state
        self.building_placement_preview = False
        self.preview_building_type = None
        self.preview_tile = None
        
        # Enhanced rendering system
        self.enhanced_renderer = EnhancedGridRenderer(self)
        
        # Subscribe to enhanced renderer events
        self._setup_enhanced_renderer_events()
        
        # Register for events
        self.event_system.subscribe('day_passed', self._handle_day_passed)
        self.event_system.subscribe('day_passed_with_weather', self._handle_day_passed)  # Weather-enhanced day events
        self.event_system.subscribe('task_assigned', self._handle_task_assignment)
        self.event_system.subscribe('building_placement_preview_start', self._handle_preview_start)
        self.event_system.subscribe('building_placement_preview_stop', self._handle_preview_stop)
        
        print(f"Grid Manager initialized with {GRID_WIDTH}x{GRID_HEIGHT} tiles and enhanced rendering")
    
    def _setup_enhanced_renderer_events(self):
        """Setup event subscriptions for enhanced renderer"""
        # Subscribe to zoom and pan control events
        self.event_system.subscribe('grid_zoom_in', self._handle_zoom_in)
        self.event_system.subscribe('grid_zoom_out', self._handle_zoom_out)
        self.event_system.subscribe('grid_reset_viewport', self._handle_reset_viewport)
        self.event_system.subscribe('toggle_soil_health_overlay', self._handle_toggle_soil_overlay)
        self.event_system.subscribe('toggle_irrigation_overlay', self._handle_toggle_irrigation_overlay)
        
        print("Enhanced grid renderer events configured")
    
    def _handle_zoom_in(self, event_data):
        """Handle zoom in request"""
        if hasattr(self.enhanced_renderer, 'zoom_in'):
            self.enhanced_renderer.zoom_in()
    
    def _handle_zoom_out(self, event_data):
        """Handle zoom out request"""
        if hasattr(self.enhanced_renderer, 'zoom_out'):
            self.enhanced_renderer.zoom_out()
    
    def _handle_reset_viewport(self, event_data):
        """Handle viewport reset request"""
        if hasattr(self.enhanced_renderer, 'reset_viewport'):
            self.enhanced_renderer.reset_viewport()
    
    def _handle_toggle_soil_overlay(self, event_data):
        """Handle soil health overlay toggle"""
        if hasattr(self.enhanced_renderer, 'toggle_soil_health_overlay'):
            self.enhanced_renderer.toggle_soil_health_overlay()
    
    def _handle_toggle_irrigation_overlay(self, event_data):
        """Handle irrigation overlay toggle"""
        if hasattr(self.enhanced_renderer, 'toggle_irrigation_overlay'):
            self.enhanced_renderer.toggle_irrigation_overlay()
    
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
        """Get tile at pixel position with enhanced grid transformation support"""
        # Use enhanced renderer's transformation logic if available
        if hasattr(self, 'enhanced_renderer') and self.enhanced_renderer:
            return self.enhanced_renderer._get_tile_at_position((px, py))
        
        # Fallback to legacy calculation for compatibility
        # Account for UI offset
        py -= 70
        
        if py < 0:  # Click in UI area
            return None
            
        grid_x = px // TILE_SIZE
        grid_y = py // TILE_SIZE
        
        return self.get_tile(grid_x, grid_y)
    
    def handle_mouse_down(self, pos: Tuple[int, int], button: int):
        """Handle mouse button down for tile selection, building placement, or enhanced grid interaction"""
        # Forward to enhanced renderer for zoom/pan handling
        if hasattr(self.enhanced_renderer, 'handle_mouse_button_down'):
            mouse_event = type('MouseEvent', (), {'pos': pos, 'button': button})()
            self.enhanced_renderer.handle_mouse_button_down(mouse_event)
        if button == 1:  # Left click
            tile = self.get_tile_at_pixel(*pos)
            
            if self.building_placement_preview and tile and self.preview_building_type:
                # Handle building placement
                if tile.can_place_building():
                    # Emit building placement confirmed event
                    self.event_system.emit('building_placement_confirmed', {
                        'x': tile.x,
                        'y': tile.y
                    })
                else:
                    print(f"Cannot place {self.preview_building_type} at ({tile.x}, {tile.y}) - tile not suitable")
            else:
                # Normal tile selection
                self.drag_start_pos = pos
                if tile:
                    # Check if this is a single tile click on a tilled plot for soil info panel
                    if tile.terrain_type == 'tilled' and len(self.selected_tiles) <= 1:
                        # Emit tile selected event for soil info panel
                        self.event_system.emit('tile_selected', {
                            'tile': tile,
                            'x': tile.x,
                            'y': tile.y
                        })
                    else:
                        # Emit tile deselected to close any open panels
                        self.event_system.emit('tile_deselected', {})
                    
                    self._clear_selection()
                    self.selected_tiles = [tile]
                    tile.highlight = True
                else:
                    # Clicked on empty area - deselect and close panels
                    self.event_system.emit('tile_deselected', {})
                    self._clear_selection()
    
    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """Handle mouse motion for building placement preview"""
        if self.building_placement_preview:
            tile = self.get_tile_at_pixel(*pos)
            self.preview_tile = tile
    
    def handle_mouse_drag(self, pos: Tuple[int, int]):
        """Handle mouse drag for area selection"""
        if self.building_placement_preview:
            # Skip drag selection during building placement
            return
            
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
    
    def handle_mouse_wheel(self, pos: Tuple[int, int], direction: int):
        """Handle mouse wheel events for zoom functionality"""
        if hasattr(self.enhanced_renderer, 'handle_mouse_wheel'):
            # Create mock event object for enhanced renderer
            wheel_event = type('WheelEvent', (), {'pos': pos, 'y': direction})()
            self.enhanced_renderer.handle_mouse_wheel(wheel_event)
    
    def _update_drag_selection(self):
        """Update tile selection based on drag area with enhanced grid transformation support"""
        if not (self.drag_start_pos and self.drag_current_pos):
            return
        
        # Use enhanced renderer coordinate transformation if available
        if hasattr(self, 'enhanced_renderer') and self.enhanced_renderer:
            start_tile = self.enhanced_renderer._get_tile_at_position(self.drag_start_pos)
            end_tile = self.enhanced_renderer._get_tile_at_position(self.drag_current_pos)
            
            if not (start_tile and end_tile):
                return
            
            # Get grid coordinates from tiles
            start_gx, start_gy = start_tile.x, start_tile.y
            end_gx, end_gy = end_tile.x, end_tile.y
        else:
            # Fallback to legacy calculation
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
        """Render the grid using enhanced rendering system"""
        # Use enhanced renderer for professional grid visualization
        self.enhanced_renderer.render(screen)
        
        # Fallback: Render selection rectangle if dragging (enhanced renderer will handle this better)
        if self.drag_start_pos and self.drag_current_pos:
            self._render_selection_rectangle(screen)
        
        # Render building placement preview (enhanced renderer integration can be added later)
        if self.building_placement_preview and self.preview_tile:
            self._render_building_preview(screen)
    
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
    
    def _render_irrigation_indicator(self, screen: pygame.Surface, tile: Tile):
        """Render irrigation system indicator on irrigated tiles"""
        # Draw small water droplet indicators in corners
        tile_x = tile.rect.x
        tile_y = tile.rect.y
        tile_size = tile.rect.width
        
        # Water blue color for irrigation indicators
        water_color = (64, 164, 223)
        
        # Draw small circles in the corners to indicate irrigation coverage
        indicator_size = 3
        margin = 4
        
        # Top-left and bottom-right corners
        pygame.draw.circle(screen, water_color, 
                         (tile_x + margin, tile_y + margin), indicator_size)
        pygame.draw.circle(screen, water_color, 
                         (tile_x + tile_size - margin, tile_y + tile_size - margin), indicator_size)
    
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
        """Handle day passing for crop growth with weather effects"""
        days_passed = event_data.get('days', 1)
        
        # Get weather growth modifier from event data (provided by weather manager)
        weather_growth_modifier = event_data.get('weather_growth_modifier', 1.0)
        weather_event = event_data.get('weather_event', 'clear')
        
        print(f"Grid Manager: Day passed, updating crop growth by {days_passed} days (weather: {weather_event}, modifier: {weather_growth_modifier:.2f}x)")
        
        crops_updated = 0
        for row in self.grid:
            for tile in row:
                # Calculate tile-specific growth modifier considering irrigation
                tile_growth_modifier = weather_growth_modifier
                
                # Apply irrigation bonus during drought if tile has irrigation
                if (weather_event == 'drought' and tile.has_irrigation and 
                    weather_growth_modifier < 1.0):
                    # Irrigation provides 30% boost during drought (from config)
                    irrigation_boost = IRRIGATION_DROUGHT_MITIGATION
                    tile_growth_modifier = min(1.0, weather_growth_modifier + irrigation_boost)
                    
                if tile.update_growth(days_passed, tile_growth_modifier):
                    crops_updated += 1
        
        if crops_updated > 0:
            print(f"Updated growth for {crops_updated} crops with weather effects")
    
    def _handle_task_assignment(self, event_data):
        """Handle task assignment events"""
        # Tasks are assigned by this manager, so just log for now
        task_type = event_data.get('task_type')
        tile_count = event_data.get('tile_count')
        print(f"Assigned {task_type} task to {tile_count} tiles")
    
    def place_building_at(self, x: int, y: int, building_type_id: str, building_object=None) -> bool:
        """Place a building at the specified grid coordinates"""
        tile = self.get_tile(x, y)
        if tile and tile.can_place_building():
            success = tile.place_building(building_type_id, building_object)
            if success:
                # Emit building placed event
                self.event_system.emit('building_placed', {
                    'x': x,
                    'y': y,
                    'building_type': building_type_id,
                    'building': building_object
                })
                print(f"Placed {building_type_id} at ({x}, {y})")
            return success
        return False
    
    def remove_building_at(self, x: int, y: int) -> bool:
        """Remove building at the specified grid coordinates"""
        tile = self.get_tile(x, y)
        if tile and tile.building:
            building_type = tile.building_type
            success = tile.remove_building()
            if success:
                # Emit building removed event
                self.event_system.emit('building_removed', {
                    'x': x,
                    'y': y,
                    'building_type': building_type
                })
                print(f"Removed {building_type} from ({x}, {y})")
            return success
        return False
    
    def get_building_at(self, x: int, y: int):
        """Get building object at the specified coordinates"""
        tile = self.get_tile(x, y)
        return tile.building if tile else None
    
    def find_buildings_of_type(self, building_type_id: str) -> List[Tuple[int, int]]:
        """Find all buildings of a specific type and return their coordinates"""
        buildings = []
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = self.grid[y][x]
                if tile.building_type == building_type_id:
                    buildings.append((x, y))
        return buildings
    
    def find_nearest_building(self, from_x: int, from_y: int, building_type_id: str) -> Optional[Tuple[int, int]]:
        """Find the nearest building of a specific type"""
        buildings = self.find_buildings_of_type(building_type_id)
        if not buildings:
            return None
        
        min_distance = float('inf')
        nearest = None
        
        for bx, by in buildings:
            distance = abs(from_x - bx) + abs(from_y - by)  # Manhattan distance
            if distance < min_distance:
                min_distance = distance
                nearest = (bx, by)
        
        return nearest
    
    def get_building_interaction_tiles(self, building_x: int, building_y: int) -> List[Tuple[int, int]]:
        """Get adjacent tiles where employees can interact with a building"""
        interaction_tiles = []
        # Check all 8 adjacent tiles (including diagonals)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:  # Skip the building tile itself
                    continue
                
                x, y = building_x + dx, building_y + dy
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    tile = self.get_tile(x, y)
                    # Employee can interact if tile is not occupied
                    if tile and not tile.is_occupied:
                        interaction_tiles.append((x, y))
        
        return interaction_tiles
    
    def _handle_preview_start(self, event_data):
        """Handle start of building placement preview"""
        building_type = event_data.get('building_type')
        if building_type:
            self.building_placement_preview = True
            self.preview_building_type = building_type
            print(f"Grid Manager: Started building placement preview for {building_type}")
    
    def _handle_preview_stop(self, event_data):
        """Handle end of building placement preview"""
        self.building_placement_preview = False
        self.preview_building_type = None
        self.preview_tile = None
        print("Grid Manager: Stopped building placement preview")
    
    def _render_building_preview(self, screen: pygame.Surface):
        """Render building placement preview overlay"""
        if not (self.preview_tile and self.preview_building_type):
            return
        
        # Get building colors based on type
        building_colors = {
            'storage_silo': (200, 200, 200, 128),      # Light gray
            'water_cooler': (100, 200, 255, 128),     # Light blue  
            'tool_shed': (255, 200, 100, 128),        # Light orange
            'employee_housing': (200, 255, 200, 128)  # Light green
        }
        
        color = building_colors.get(self.preview_building_type, (255, 255, 255, 128))
        
        # Check if placement is valid
        can_place = self.preview_tile.can_place_building()
        if not can_place:
            color = (255, 100, 100, 128)  # Red for invalid placement
        
        # Create semi-transparent surface for preview
        preview_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        preview_surface.fill(color)
        
        # Draw preview overlay
        screen.blit(preview_surface, self.preview_tile.rect.topleft)
        
        # Draw border
        border_color = (0, 255, 0) if can_place else (255, 0, 0)
        pygame.draw.rect(screen, border_color, self.preview_tile.rect, 2)
        
        # Draw building effect radius if placement is valid
        if can_place:
            self._render_building_effect_radius(screen, self.preview_tile.x, self.preview_tile.y, self.preview_building_type)
    
    def _render_building_effect_radius(self, screen: pygame.Surface, center_x: int, center_y: int, building_type: str):
        """Render visual indicator of building effect radius"""
        # Define building effect radius and colors for different building types
        building_effects = {
            'storage_silo': {
                'radius': 4,  # Storage silos affect tiles within 4 tiles (Manhattan distance)
                'color': (255, 255, 0, 60),  # Semi-transparent yellow for crop yield bonus
                'border_color': (255, 255, 0, 120),  # More opaque yellow border
                'description': 'Crop Yield +10%'
            },
            'tool_shed': {
                'radius': 3,  # Tool sheds affect tiles within 3 tiles
                'color': (255, 150, 0, 60),  # Semi-transparent orange for work efficiency
                'border_color': (255, 150, 0, 120),  # More opaque orange border
                'description': 'Work Efficiency +15%'
            },
            'water_cooler': {
                'radius': 2,  # Water coolers affect tiles within 2 tiles
                'color': (0, 150, 255, 60),  # Semi-transparent blue for rest decay reduction
                'border_color': (0, 150, 255, 120),  # More opaque blue border
                'description': 'Rest Decay -20%'
            },
            'employee_housing': {
                'radius': 2,  # Employee housing affects tiles within 2 tiles
                'color': (0, 255, 0, 60),  # Semi-transparent green for trait effectiveness
                'border_color': (0, 255, 0, 120),  # More opaque green border
                'description': 'Trait Effectiveness +25%'
            }
        }
        
        # Get building effect properties or skip if not defined
        if building_type not in building_effects:
            return
        
        effect = building_effects[building_type]
        radius = effect['radius']
        color = effect['color']
        border_color = effect['border_color']
        
        # Create surface for effect radius visualization
        effect_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        # Draw effect area using Manhattan distance (diamond shape)
        # Loop through all tiles within the maximum possible radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # Calculate Manhattan distance from building center
                manhattan_distance = abs(dx) + abs(dy)
                
                # Skip tiles outside the effect radius
                if manhattan_distance > radius:
                    continue
                
                # Calculate grid coordinates for this tile
                tile_x = center_x + dx
                tile_y = center_y + dy
                
                # Skip tiles outside the grid boundaries
                if tile_x < 0 or tile_x >= GRID_WIDTH or tile_y < 0 or tile_y >= GRID_HEIGHT:
                    continue
                
                # Calculate screen pixel coordinates for this tile
                screen_x = tile_x * TILE_SIZE
                screen_y = tile_y * TILE_SIZE + 70  # Add UI offset
                
                # Draw effect overlay on this tile
                tile_rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                effect_tile_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                
                # Use different opacity based on distance (closer = more opaque)
                distance_opacity = max(30, int(color[3] * (1.0 - manhattan_distance / (radius + 1))))
                tile_color = (color[0], color[1], color[2], distance_opacity)
                effect_tile_surface.fill(tile_color)
                
                # Draw the effect tile
                effect_surface.blit(effect_tile_surface, (screen_x, screen_y))
                
                # Draw border for tiles at the edge of effect radius
                if manhattan_distance == radius:
                    border_rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(effect_surface, border_color, border_rect, 1)
        
        # Blit the complete effect surface to the main screen
        screen.blit(effect_surface, (0, 0))