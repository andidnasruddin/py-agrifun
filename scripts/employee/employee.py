"""
Employee - Individual worker with AI, needs, and task execution
Represents a single farm worker with pathfinding, needs system, and work capabilities.
"""

import pygame
import math
from typing import List, Tuple, Optional, Dict
from enum import Enum
from scripts.core.config import *

# Import enhanced task system components when specializations are enabled
if ENABLE_EMPLOYEE_SPECIALIZATIONS:
    from scripts.tasks.task_models import EmployeeSpecialization, EmployeeRole, TaskType, SkillLevel
# Pathfinding removed - using direct movement for performance


class EmployeeState(Enum):
    """Employee AI states"""
    IDLE = "idle"
    MOVING = "moving" 
    WORKING = "working"
    RESTING = "resting"
    SEEKING_AMENITY = "seeking_amenity"


class Employee:
    """Individual farm employee with AI and needs"""
    
    def __init__(self, employee_id: str, name: str, x: float, y: float):
        """Initialize employee at grid position"""
        self.id = employee_id
        self.name = name
        
        # Position (in grid coordinates)
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        
        # Direct movement system
        self.speed = EMPLOYEE_SPEED  # tiles per second
        
        # AI State
        self.state = EmployeeState.IDLE
        self.state_timer = 0.0
        
        # Core stats
        self.skill_level = 1.0  # Efficiency modifier
        self.walking_speed = self.speed
        self.max_stamina = 100
        
        # Needs system (0-100)
        self.hunger = MAX_HUNGER
        self.thirst = MAX_THIRST
        self.rest = MAX_REST
        
        # Traits
        self.traits: List[str] = []
        
        # Work assignment
        self.assigned_tasks: List[Dict] = []  # List of task dictionaries
        self.current_task = None
        self.work_efficiency = 1.0
        
        # Employment details
        self.daily_wage = BASE_EMPLOYEE_WAGE  # Can be modified for different employees
        
        # Building usage tracking
        self.housing_recently_used = False  # +25% trait effectiveness if used housing recently
        self.housing_usage_timer = 0.0  # Timer since last housing use
        
        # Enhanced Task System - Employee Specializations (Phase 2A)
        if ENABLE_EMPLOYEE_SPECIALIZATIONS:
            self.specialization = self._initialize_employee_specialization()  # EmployeeSpecialization object
        else:
            self.specialization = None  # Legacy system - no specializations
        
        # Visual
        self.color = COLORS['employee']
        self.radius = 8
        
        print(f"Employee {self.name} ({self.id}) created at ({x}, {y})")
        if ENABLE_EMPLOYEE_SPECIALIZATIONS and self.specialization:
            print(f"  -> Specialization: {self.specialization.primary_role.value}")
    
    def add_trait(self, trait_name: str):
        """Add a trait to the employee"""
        if trait_name not in self.traits:
            self.traits.append(trait_name)
            self._apply_trait_effects(trait_name)
    
    def _apply_trait_effects(self, trait_name: str):
        """Apply base trait effects to employee stats"""
        if trait_name == "hard_worker":
            self.work_efficiency *= 1.1  # +10% efficiency base
            # Note: -5% stamina drain implemented in update_needs
        elif trait_name == "runner":
            self.walking_speed *= 1.1  # +10% speed base
            self.speed = self.walking_speed
    
    def assign_task(self, task_type: str, target_tiles: List, **kwargs):
        """Assign a new task to the employee with optional parameters"""
        from datetime import datetime
        
        task = {
            'type': task_type,
            'tiles': target_tiles,
            'completed_tiles': [],
            'status': 'pending',
            'assigned_at': datetime.now(),  # Track assignment time for FIFO ordering
            **kwargs  # Allow additional task parameters like crop_type
        }
        self.assigned_tasks.append(task)
        print(f"Employee {self.name}: Assigned {task_type} task for {len(target_tiles)} tiles")
        
        # Start working on this task if idle
        if self.state == EmployeeState.IDLE and not self.current_task:
            self._start_next_task()
    
    def _start_next_task(self):
        """Start working on the next available task in FIFO order"""
        if not self.assigned_tasks:
            self.current_task = None
            self.state = EmployeeState.IDLE
            return
        
        # Sort tasks by assignment time to ensure FIFO order (first assigned = first completed)
        pending_tasks = [task for task in self.assigned_tasks if task['status'] == 'pending']
        if not pending_tasks:
            self.current_task = None
            self.state = EmployeeState.IDLE
            return
        
        # Sort by assigned_at timestamp for true FIFO behavior
        pending_tasks.sort(key=lambda t: t.get('assigned_at', t.get('work_order_id', '')))
        print(f"Employee {self.name}: Processing {len(pending_tasks)} pending tasks in FIFO order")
        
        # Find first task with available work
        for task in pending_tasks:
            if task['status'] == 'pending':
                remaining_tiles = [t for t in task['tiles'] 
                                 if t not in task['completed_tiles']]
                if remaining_tiles:
                    self.current_task = task
                    task['status'] = 'in_progress'
                    print(f"Employee {self.name}: Starting {task['type']} task with {len(remaining_tiles)} tiles remaining")
                    
                    # Find first available tile (not occupied by other employees)
                    target_tile = self._find_available_tile(remaining_tiles, self._current_employee_manager)
                    if target_tile:
                        self._move_to_tile(target_tile.x, target_tile.y)
                        return
                    else:
                        # All tiles occupied, wait and retry later
                        print(f"Employee {self.name}: All tiles occupied, waiting...")
                        self.state = EmployeeState.IDLE
                        # Set a retry timer
                        self.task_retry_timer = 2.0  # Retry in 2 seconds
                        return
                else:
                    task['status'] = 'completed'
        
        # No tasks available
        self.current_task = None
        self.state = EmployeeState.IDLE
    
    def _find_available_tile(self, tiles: List, employee_manager=None):
        """Find the first tile not currently occupied by another employee"""
        for tile in tiles:
            if not self._is_tile_occupied(tile, employee_manager):
                return tile
        return None
    
    def _is_tile_occupied(self, tile, employee_manager=None) -> bool:
        """Check if a tile is currently occupied by another employee or already completed for current task"""
        # First check if the work is already completed for the current task type
        if self.current_task and self._is_tile_work_completed(tile, self.current_task.get('type')):
            tile_coord = (int(tile.x), int(tile.y))
            print(f"Employee {self.name}: Tile ({tile_coord[0]},{tile_coord[1]}) work already completed for {self.current_task.get('type')}")
            return True
        
        # Check if tile has a task assignment to another employee
        if hasattr(tile, 'task_assigned_to') and tile.task_assigned_to and tile.task_assigned_to != self.id:
            return True
        
        # Check if any other employee is currently working on this tile
        tile_coord = (int(tile.x), int(tile.y))
        
        if employee_manager:
            # Check all other employees to see if they're working on this tile
            for emp_id, employee in employee_manager.employees.items():
                if emp_id != self.id:  # Don't check ourselves
                    # Check if this employee is working on this coordinate
                    if (employee.state == EmployeeState.WORKING and
                        hasattr(employee, 'target_x') and hasattr(employee, 'target_y') and
                        int(employee.x) == tile_coord[0] and int(employee.y) == tile_coord[1]):
                        print(f"Employee {self.name}: Tile ({tile_coord[0]},{tile_coord[1]}) occupied by {employee.name}")
                        return True
                    
                    # Check occupied tiles set
                    if hasattr(employee, 'occupied_tiles') and tile_coord in employee.occupied_tiles:
                        print(f"Employee {self.name}: Tile ({tile_coord[0]},{tile_coord[1]}) marked as occupied by {employee.name}")
                        return True
        
        return False
    
    def _is_tile_work_completed(self, tile, task_type: str) -> bool:
        """Check if the tile already has the required work completed for the given task type"""
        if not tile or not task_type:
            return False
            
        try:
            # Check based on task type and agricultural workflow
            if task_type == 'till' or task_type == 'tilling':
                # Tilling is complete if terrain is already tilled or has crops
                return tile.terrain_type == 'tilled' or tile.current_crop is not None
                
            elif task_type == 'plant' or task_type == 'planting':
                # Planting is complete if tile already has a crop
                return tile.current_crop is not None
                
            elif task_type == 'harvest' or task_type == 'harvesting':
                # Harvesting is complete if tile has no crop or crop is not mature
                if tile.current_crop is None:
                    return True  # Nothing to harvest
                # Check if crop is mature (growth_stage 4 is harvestable)
                return tile.growth_stage < 4  # Not ready to harvest yet
                
            else:
                # For other task types, assume they need to be done
                return False
                
        except Exception as e:
            print(f"Error checking tile work completion: {e}")
            return False
    
    def _mark_tile_occupied(self, x: int, y: int, occupied: bool):
        """Mark a tile as occupied or released by this employee"""
        # This would ideally be handled by the grid manager
        # For now, we'll track occupation in the employee system
        if not hasattr(self, 'occupied_tiles'):
            self.occupied_tiles = set()
        
        tile_coord = (x, y)
        if occupied:
            self.occupied_tiles.add(tile_coord)
            print(f"Employee {self.name}: Marking tile ({x},{y}) as occupied")
        else:
            self.occupied_tiles.discard(tile_coord)
            print(f"Employee {self.name}: Released tile ({x},{y})")
        
        # Also try to set tile property if accessible
        # This requires grid manager integration
        # TODO: Integrate with grid manager for proper tile occupation tracking
    
    def _move_to_tile(self, grid_x: int, grid_y: int):
        """Start moving to a specific grid tile using efficient direct movement"""
        if abs(self.x - grid_x) < 0.1 and abs(self.y - grid_y) < 0.1:
            # Already at target (within tolerance)
            self.state = EmployeeState.WORKING
            self.state_timer = 0.0
            # Mark tile as occupied
            self._mark_tile_occupied(grid_x, grid_y, True)
            return
        
        # Simple, efficient direct movement
        self.target_x = grid_x
        self.target_y = grid_y
        self.state = EmployeeState.MOVING
        self.state_timer = 0.0
        
        print(f"Employee {self.name}: Moving to ({grid_x}, {grid_y})")
    
    def update(self, dt: float, grid_manager, employee_manager=None):
        """Update employee AI and needs"""
        # Store employee manager reference for collision detection
        self._current_employee_manager = employee_manager
        
        # Clean up completed tasks first
        self._cleanup_completed_tasks()
        
        # Update needs (pass grid_manager for building bonuses)
        self.update_needs(dt, grid_manager)
        
        # Check for critical needs
        if self._has_critical_needs():
            self._handle_critical_needs()
            return
        
        # Update AI state
        self.update_ai(dt, grid_manager)
    
    def update_needs(self, dt: float, grid_manager=None):
        """Update employee needs over time"""
        hours_passed = dt / 3600.0  # Convert seconds to hours
        
        # Decay rates
        hunger_decay = HUNGER_DECAY_RATE * hours_passed
        thirst_decay = THIRST_DECAY_RATE * hours_passed
        
        # Rest decay depends on activity
        if self.state == EmployeeState.WORKING:
            rest_decay = REST_DECAY_RATE * hours_passed
            
            # Hard worker trait effect
            if "hard_worker" in self.traits:
                rest_decay *= 0.95  # 5% less drain
                
            # Apply building-based rest decay bonuses if building manager available
            if grid_manager and hasattr(grid_manager, 'building_manager') and grid_manager.building_manager:
                # Get current tile position for spatial benefits calculation
                current_x = int(round(self.x))
                current_y = int(round(self.y))
                
                # Get spatial benefits including rest decay modifiers
                benefits = grid_manager.building_manager.get_spatial_benefits_at(current_x, current_y)
                rest_decay *= benefits['rest_decay_multiplier']
                
                # Print debug info if rest decay is reduced
                if benefits['rest_decay_multiplier'] < 1.0:
                    reduction_percent = int((1.0 - benefits['rest_decay_multiplier']) * 100)
                    print(f"Employee {self.name}: -{reduction_percent}% rest decay from nearby buildings")
            else:
                # Fallback to legacy water cooler check for compatibility
                if grid_manager and self._has_nearby_water_cooler(grid_manager):
                    rest_decay *= 0.80  # 20% less rest drain (work 20% longer)
                
        elif self.state == EmployeeState.RESTING:
            rest_decay = -REST_DECAY_RATE * 2 * hours_passed  # Restore rest
        else:
            rest_decay = REST_DECAY_RATE * 0.5 * hours_passed  # Slow decay
        
        # Apply decay
        self.hunger = max(0, self.hunger - hunger_decay)
        self.thirst = max(0, self.thirst - thirst_decay)
        self.rest = max(0, min(MAX_REST, self.rest - rest_decay))
        
        # Update housing usage timer
        if self.housing_recently_used:
            self.housing_usage_timer += dt
            if self.housing_usage_timer >= 3600.0:  # 1 hour has passed
                self.housing_recently_used = False
                print(f"Employee {self.name}: Housing bonus expired")
    
    def _has_critical_needs(self) -> bool:
        """Check if employee has critical needs requiring attention"""
        return (self.hunger < 20 or 
                self.thirst < 15 or 
                self.rest < 10)
    
    def _handle_critical_needs(self):
        """Handle critical needs by seeking amenities or resting"""
        if self.thirst < 15:
            # Seek water cooler (not implemented yet)
            self.state = EmployeeState.SEEKING_AMENITY
        elif self.hunger < 20:
            # Seek food source (not implemented yet)  
            self.state = EmployeeState.SEEKING_AMENITY
        elif self.rest < 10:
            # Take a rest break
            self.state = EmployeeState.RESTING
            self.state_timer = 0.0
    
    def update_ai(self, dt: float, grid_manager):
        """Update AI state machine"""
        self.state_timer += dt
        
        if self.state == EmployeeState.IDLE:
            # Look for tasks to do
            if not self.current_task:
                self._start_next_task()
        
        elif self.state == EmployeeState.MOVING:
            self._update_movement(dt)
        
        elif self.state == EmployeeState.WORKING:
            self._update_work(dt, grid_manager)
        
        elif self.state == EmployeeState.RESTING:
            # Rest for at least 30 seconds
            if self.state_timer > 30.0 and self.rest > 50:
                self.state = EmployeeState.IDLE
                self.state_timer = 0.0
        
        elif self.state == EmployeeState.SEEKING_AMENITY:
            self._update_seeking_amenity(dt, grid_manager)
    
    def _update_movement(self, dt: float):
        """Update movement toward target using efficient direct movement"""
        # Calculate direction to target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 0.1:  # Close enough
            self.x = self.target_x
            self.y = self.target_y
            self.state = EmployeeState.WORKING
            self.state_timer = 0.0
            print(f"Employee {self.name}: Reached destination ({self.target_x}, {self.target_y})")
            return
        
        # Move toward target
        move_distance = self.speed * dt
        if move_distance >= distance:
            # Arrive at target this frame
            self.x = self.target_x
            self.y = self.target_y
            self.state = EmployeeState.WORKING
            self.state_timer = 0.0
            # Mark tile as occupied
            self._mark_tile_occupied(self.target_x, self.target_y, True)
        else:
            # Move closer
            self.x += (dx / distance) * move_distance
            self.y += (dy / distance) * move_distance
    
    def _update_work(self, dt: float, grid_manager):
        """Update work progress on current task"""
        if not self.current_task:
            self.state = EmployeeState.IDLE
            return
        
        # Find tile at current position
        tile = grid_manager.get_tile(int(self.x), int(self.y))
        if not tile:
            # Not on a valid tile, move to next task
            self._complete_current_tile()
            return
        
        # Calculate work efficiency including building bonuses and task specialization
        effective_efficiency = self._calculate_work_efficiency(grid_manager, self.current_task)
        
        # Work takes time based on efficiency
        work_time_needed = 3.0 / effective_efficiency  # Base 3 seconds per task
        
        # Debug output - show when close to completion
        if self.state_timer >= work_time_needed - 0.5:  # Show last 0.5 seconds
            print(f"Employee {self.name}: Almost done with {self.current_task['type']} at ({int(self.x)}, {int(self.y)}), timer: {self.state_timer:.1f}s/{work_time_needed:.1f}s")
        
        if self.state_timer >= work_time_needed:
            # Complete the work on this tile
            print(f"Employee {self.name}: Work timer reached {self.state_timer:.1f}s (needed {work_time_needed:.1f}s) - executing work on ({tile.x}, {tile.y})")
            if self._perform_work_on_tile(tile, grid_manager):
                self._complete_current_tile()
            else:
                # Work failed, skip tile
                self._complete_current_tile()
    
    def _perform_work_on_tile(self, tile, grid_manager) -> bool:
        """Perform the assigned work on a tile"""
        if not self.current_task:
            return False
        
        task_type = self.current_task['type']
        print(f"Employee {self.name}: Performing work - task_type: '{task_type}' (type: {type(task_type)})")
        
        # Handle both old format ('till') and new work order format ('tilling')
        if task_type in ['till', 'tilling']:
            if tile.can_till():
                success = tile.till()
                if success:
                    print(f"Employee {self.name}: Successfully tilled plot ({tile.x}, {tile.y}) - terrain now: {tile.terrain_type}")
                else:
                    print(f"Employee {self.name}: Failed to till plot ({tile.x}, {tile.y})")
                return success
            else:
                print(f"Employee {self.name}: Cannot till plot ({tile.x}, {tile.y}) - terrain: {tile.terrain_type}, crop: {tile.current_crop}, occupied: {tile.is_occupied}")
                return False
        elif task_type in ['plant', 'planting'] and tile.can_plant():
            # Get crop type from current task, default to corn for backward compatibility
            crop_type = self.current_task.get('crop_type', DEFAULT_CROP_TYPE)
            success = tile.plant(crop_type)
            if success:
                print(f"Employee {self.name}: Successfully planted {crop_type} at ({tile.x}, {tile.y})")
            return success
        elif task_type in ['harvest', 'harvesting'] and tile.can_harvest():
            crop_type, yield_amount = tile.harvest(grid_manager)  # Pass grid_manager for building bonuses
            if yield_amount > 0:
                # Direct synchronous harvest processing to avoid race conditions
                quality = (tile.soil_quality / 10.0) * (tile.water_level / 100.0)
                harvest_result = {
                    'crop_type': crop_type,  # Now uses actual crop type from harvest
                    'quantity': yield_amount,
                    'quality': quality,
                    'tile_position': (tile.x, tile.y),
                    'employee_id': self.id
                }
                crop_name = CROP_TYPES[crop_type]['name']
                print(f"Employee {self.name}: Harvested {yield_amount} {crop_name.lower()} (quality: {quality:.2f})")
                
                # Return harvest data for immediate processing
                self._pending_harvest = harvest_result
                return True
            return False
        
        return False
    
    def _complete_current_tile(self):
        """Mark current tile as completed and move to next"""
        if not self.current_task:
            return
        
        # Mark current tile as completed
        current_tile = None
        for tile in self.current_task['tiles']:
            if (int(tile.x) == int(self.x) and 
                int(tile.y) == int(self.y)):
                current_tile = tile
                break
        
        if current_tile and current_tile not in self.current_task['completed_tiles']:
            self.current_task['completed_tiles'].append(current_tile)
            # Clear task assignment from tile
            current_tile.task_assignment = None
            current_tile.task_assigned_to = None
            print(f"Employee {self.name}: Completed work on tile ({current_tile.x}, {current_tile.y}), terrain now: {current_tile.terrain_type}")
            
            # Release tile occupation
            self._mark_tile_occupied(current_tile.x, current_tile.y, False)
        
        # Find next tile to work on
        remaining_tiles = [t for t in self.current_task['tiles'] 
                          if t not in self.current_task['completed_tiles']]
        
        if remaining_tiles:
            # Find next available tile (not occupied by other employees)
            next_tile = self._find_available_tile(remaining_tiles, self._current_employee_manager)
            if next_tile:
                self._move_to_tile(next_tile.x, next_tile.y)
            else:
                # All remaining tiles occupied, wait and retry later
                print(f"Employee {self.name}: All remaining tiles occupied, pausing...")
                self.state = EmployeeState.IDLE
                self.state_timer = 0.0
        else:
            # Task completed
            completed_task = self.current_task.copy()  # Store reference before clearing
            self.current_task['status'] = 'completed'
            self.current_task = None
            
            # Notify completion for work order tracking
            self._notify_task_completion(completed_task)
            
            self._start_next_task()
    
    def _notify_task_completion(self, completed_task):
        """Notify external systems about task completion"""
        if hasattr(self, '_completion_callback') and self._completion_callback:
            try:
                self._completion_callback(self.id, completed_task)
            except Exception as e:
                print(f"Employee {self.name}: Task completion notification failed: {e}")
    
    def set_completion_callback(self, callback):
        """Set callback for task completion notifications"""
        self._completion_callback = callback
    
    def _cleanup_completed_tasks(self):
        """Remove completed tasks from the assigned_tasks list to prevent queue buildup"""
        initial_count = len(self.assigned_tasks)
        
        # Remove tasks marked as completed
        self.assigned_tasks = [task for task in self.assigned_tasks 
                              if task['status'] != 'completed']
        
        removed_count = initial_count - len(self.assigned_tasks)
        if removed_count > 0:
            print(f"Employee {self.name}: Cleaned up {removed_count} completed tasks ({len(self.assigned_tasks)} remaining)")
    
    def get_pixel_position(self, zoom_factor: float = 1.0, pan_offset_x: float = 0.0, 
                          pan_offset_y: float = 0.0, hud_height: int = 70) -> Tuple[int, int]:
        """Get employee position in screen pixels with grid transformations"""
        # Apply the same transformations as the enhanced grid renderer
        scaled_tile_size = TILE_SIZE * zoom_factor
        
        # Calculate position with grid center offset and transformations
        world_x = self.x * scaled_tile_size + scaled_tile_size // 2
        world_y = self.y * scaled_tile_size + scaled_tile_size // 2
        
        # Apply pan offset and HUD offset
        pixel_x = int(world_x + pan_offset_x)
        pixel_y = int(world_y + pan_offset_y + hud_height)
        
        return (pixel_x, pixel_y)
    
    def render(self, screen: pygame.Surface, zoom_factor: float = 1.0, pan_offset_x: float = 0.0, 
               pan_offset_y: float = 0.0, hud_height: int = 70):
        """Render the employee with enhanced visual indicators and grid transformations"""
        pixel_x, pixel_y = self.get_pixel_position(zoom_factor, pan_offset_x, pan_offset_y, hud_height)
        
        # Scale employee size based on zoom factor
        scaled_radius = max(3, int(self.radius * zoom_factor))
        
        # Draw movement direction line when moving
        if self.state == EmployeeState.MOVING:
            self._render_movement_line(screen, pixel_x, pixel_y, zoom_factor, pan_offset_x, pan_offset_y, hud_height)
        
        # Draw employee background circle (larger for better visibility)
        pygame.draw.circle(screen, (255, 255, 255), (pixel_x, pixel_y), scaled_radius + 2)  # White outline
        pygame.draw.circle(screen, self.color, (pixel_x, pixel_y), scaled_radius)
        
        # Draw state indicator
        self._render_state_indicator(screen, pixel_x, pixel_y, zoom_factor)
        
        # Draw employee name (only show if zoomed in enough)
        if zoom_factor >= 0.8:
            self._render_employee_name(screen, pixel_x, pixel_y, zoom_factor)
        
        # Draw needs bars above employee (only show if zoomed in enough)
        if zoom_factor >= 1.0:
            self._render_needs_bars(screen, pixel_x, pixel_y - scaled_radius - 35, zoom_factor)
    
    def _render_employee_name(self, screen: pygame.Surface, x: int, y: int, zoom_factor: float = 1.0):
        """Render employee name below the sprite with zoom scaling"""
        scaled_radius = max(3, int(self.radius * zoom_factor))
        font_size = max(16, int(20 * zoom_factor))
        font = pygame.font.Font(None, font_size)
        name_surface = font.render(self.name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(x, y + scaled_radius + int(12 * zoom_factor)))
        
        # Draw background rectangle for better readability
        bg_rect = name_rect.inflate(4, 2)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
        
        screen.blit(name_surface, name_rect)
    
    def _render_state_indicator(self, screen: pygame.Surface, x: int, y: int, zoom_factor: float = 1.0):
        """Render current state indicator with better visibility and zoom scaling"""
        indicator_colors = {
            EmployeeState.IDLE: (128, 128, 128),
            EmployeeState.MOVING: (0, 150, 255),
            EmployeeState.WORKING: (0, 255, 0),
            EmployeeState.RESTING: (255, 255, 0),
            EmployeeState.SEEKING_AMENITY: (255, 0, 255)
        }
        
        color = indicator_colors.get(self.state, (255, 255, 255))
        # Scale indicator size with zoom
        indicator_size = max(2, int(4 * zoom_factor))
        indicator_offset = max(4, int(8 * zoom_factor))
        
        # Draw larger, more visible state indicator
        pygame.draw.circle(screen, (0, 0, 0), (x + indicator_offset, y - indicator_offset), indicator_size + 1)  # Black outline
        pygame.draw.circle(screen, color, (x + indicator_offset, y - indicator_offset), indicator_size)
    
    def _render_needs_bars(self, screen: pygame.Surface, x: int, y: int, zoom_factor: float = 1.0):
        """Render needs bars above employee with zoom scaling"""
        bar_width = max(20, int(30 * zoom_factor))
        bar_height = max(2, int(4 * zoom_factor))
        bar_spacing = max(1, int(2 * zoom_factor))
        
        needs = [
            ('H', self.hunger, MAX_HUNGER, (255, 200, 100)),
            ('T', self.thirst, MAX_THIRST, (100, 200, 255)),
            ('R', self.rest, MAX_REST, (200, 255, 100))
        ]
        
        for i, (label, current, maximum, color) in enumerate(needs):
            bar_y = y + i * (bar_height + bar_spacing)
            
            # Background
            pygame.draw.rect(screen, (50, 50, 50), 
                           (x - bar_width//2, bar_y, bar_width, bar_height))
            
            # Fill based on current value
            fill_width = int((current / maximum) * bar_width)
            if fill_width > 0:
                pygame.draw.rect(screen, color,
                               (x - bar_width//2, bar_y, fill_width, bar_height))
    
    def _render_movement_line(self, screen: pygame.Surface, current_x: int, current_y: int, 
                             zoom_factor: float = 1.0, pan_offset_x: float = 0.0, 
                             pan_offset_y: float = 0.0, hud_height: int = 70):
        """Render movement direction line for direct movement with proper transformations"""
        # Calculate target position using the same transformation logic as employee position
        scaled_tile_size = TILE_SIZE * zoom_factor
        target_world_x = self.target_x * scaled_tile_size + scaled_tile_size // 2
        target_world_y = self.target_y * scaled_tile_size + scaled_tile_size // 2
        
        # Apply pan offset and HUD offset
        target_pixel_x = int(target_world_x + pan_offset_x)
        target_pixel_y = int(target_world_y + pan_offset_y + hud_height)
        
        # Draw simple line to target
        pygame.draw.line(screen, (100, 255, 100), (current_x, current_y), 
                        (target_pixel_x, target_pixel_y), 2)
        
        # Draw target marker
        pygame.draw.circle(screen, (255, 255, 0), (target_pixel_x, target_pixel_y), 4)
    
    def get_status_info(self) -> Dict:
        """Get employee status for UI display"""
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state.value,
            'hunger': self.hunger,
            'thirst': self.thirst,
            'rest': self.rest,
            'position': (self.x, self.y),
            'current_task': self.current_task['type'] if self.current_task else None,
            'traits': self.traits
        }
    
    def needs_building_interaction(self) -> Optional[str]:
        """Check if employee needs to use a building for their needs"""
        # Check thirst first (most urgent)
        if self.thirst < 30:
            return 'water_cooler'
        
        # Check rest (second priority)  
        if self.rest < 25:
            return 'employee_housing'
        
        # Check hunger (can be satisfied through other means later)
        if self.hunger < 20:
            return 'employee_housing'  # For now, housing also satisfies hunger
            
        return None
    
    def _update_seeking_amenity(self, dt: float, grid_manager):
        """Update seeking amenity state - pathfind to and use buildings"""
        # Check what building we need
        needed_building = self.needs_building_interaction()
        
        if not needed_building:
            # No longer need building, return to idle
            self.state = EmployeeState.IDLE
            self.state_timer = 0.0
            return
        
        # Find nearest building of the needed type
        nearest_building = grid_manager.find_nearest_building(
            int(self.x), int(self.y), needed_building
        )
        
        if not nearest_building:
            # No building available, just rest in place
            print(f"Employee {self.name}: No {needed_building} available, resting in place")
            self.state = EmployeeState.RESTING  
            self.state_timer = 0.0
            return
        
        # Get interaction tiles around the building
        building_x, building_y = nearest_building
        interaction_tiles = grid_manager.get_building_interaction_tiles(building_x, building_y)
        
        if not interaction_tiles:
            # No accessible interaction tiles
            self.state = EmployeeState.RESTING
            self.state_timer = 0.0
            return
        
        # Find closest interaction tile
        closest_tile = min(interaction_tiles, 
                          key=lambda pos: abs(self.x - pos[0]) + abs(self.y - pos[1]))
        
        # Move to interaction tile
        target_x, target_y = closest_tile
        distance = abs(self.x - target_x) + abs(self.y - target_y)
        
        if distance > 0.5:
            # Still moving to building
            self.target_x = target_x
            self.target_y = target_y
            self.state = EmployeeState.MOVING
            print(f"Employee {self.name}: Moving to {needed_building} at ({building_x}, {building_y})")
        else:
            # At building, use it
            self._interact_with_building(needed_building, building_x, building_y)
            self.state = EmployeeState.IDLE
            self.state_timer = 0.0
    
    def _interact_with_building(self, building_type: str, building_x: int, building_y: int):
        """Interact with a specific building to satisfy needs"""
        print(f"Employee {self.name}: Using {building_type} at ({building_x}, {building_y})")
        
        if building_type == 'water_cooler':
            # Restore thirst
            old_thirst = self.thirst
            self.thirst = min(100, self.thirst + 50)
            print(f"  Thirst restored: {old_thirst:.1f} → {self.thirst:.1f}")
            
        elif building_type == 'employee_housing':
            # Restore rest and hunger
            old_rest = self.rest
            old_hunger = self.hunger  
            self.rest = min(100, self.rest + 40)
            self.hunger = min(100, self.hunger + 30)
            
            # Set housing usage bonus (lasts for 1 hour of real time)
            self.housing_recently_used = True
            self.housing_usage_timer = 0.0
            
            print(f"  Rest restored: {old_rest:.1f} → {self.rest:.1f}")
            print(f"  Hunger restored: {old_hunger:.1f} → {self.hunger:.1f}")
            print(f"  Housing bonus activated: +25% trait effectiveness for 1 hour")
            
        elif building_type == 'storage_silo':
            # For future: deposit/retrieve crops
            print(f"  Accessed storage silo")
    
    def _has_nearby_water_cooler(self, grid_manager) -> bool:
        """Check if there's a water cooler within range for work duration bonus"""
        # Use unified spatial benefits system if available
        if hasattr(grid_manager, 'building_manager') and grid_manager.building_manager:
            # Get current tile position for spatial benefits calculation
            current_x = int(round(self.x))
            current_y = int(round(self.y))
            
            # Check if spatial benefits include rest decay reduction (indicates water cooler nearby)
            benefits = grid_manager.building_manager.get_spatial_benefits_at(current_x, current_y)
            return benefits['rest_decay_multiplier'] < 1.0
        else:
            # Fallback to legacy system
            if hasattr(grid_manager, 'find_buildings_of_type'):
                water_coolers = grid_manager.find_buildings_of_type('water_cooler')
                for cooler_x, cooler_y in water_coolers:
                    distance = abs(self.x - cooler_x) + abs(self.y - cooler_y)
                    if distance <= 3.0:  # Within 3 tiles
                        return True
            return False
    
    def check_and_seek_building(self):
        """Check if employee should seek a building for their needs"""
        if self.state in [EmployeeState.WORKING, EmployeeState.MOVING]:
            # Don't interrupt important activities
            return
        
        needed_building = self.needs_building_interaction()
        if needed_building and self.state != EmployeeState.SEEKING_AMENITY:
            print(f"Employee {self.name}: Seeking {needed_building} for needs")
            self.state = EmployeeState.SEEKING_AMENITY
            self.state_timer = 0.0
    
    def _calculate_work_efficiency(self, grid_manager, current_task=None) -> float:
        """Calculate effective work efficiency including building bonuses and task specialization"""
        # Start with task-specific efficiency if available (Phase 2A Enhancement)
        if ENABLE_EMPLOYEE_SPECIALIZATIONS and current_task and 'type' in current_task:
            # Use task-specific efficiency that includes specialization
            base_efficiency = self.get_task_efficiency(current_task['type'])
            
            # Debug output for specialization efficiency
            if hasattr(self, 'specialization') and self.specialization:
                task_efficiency = self.get_task_efficiency(current_task['type'])
                base_work_efficiency = self.work_efficiency
                if abs(task_efficiency - base_work_efficiency) > 0.01:  # Show only if different
                    print(f"Employee {self.name}: {current_task['type']} specialization efficiency: {task_efficiency:.2f}x (base: {base_work_efficiency:.2f}x)")
        else:
            # Legacy: Start with base efficiency (includes traits)
            base_efficiency = self.work_efficiency
        
        # Use unified spatial benefits system if building manager is available
        if hasattr(grid_manager, 'building_manager') and grid_manager.building_manager:
            # Get current tile position (rounded to integers for building calculations)
            current_x = int(round(self.x))
            current_y = int(round(self.y))
            
            # Calculate efficiency using spatial benefits system
            final_efficiency = grid_manager.building_manager.calculate_work_efficiency_at(
                current_x, current_y, base_efficiency
            )
            
            # Get spatial benefits for trait effectiveness calculation
            benefits = grid_manager.building_manager.get_spatial_benefits_at(current_x, current_y)
            
            # Apply housing trait effectiveness bonus for hard workers
            if self.housing_recently_used and "hard_worker" in self.traits:
                trait_multiplier = benefits['trait_effectiveness_multiplier']
                if trait_multiplier > 1.0:
                    # Hard worker base gives +10% (1.1x), housing makes it stronger
                    # Calculate additional trait bonus based on building effectiveness
                    additional_trait_bonus = (trait_multiplier - 1.0) * 0.1  # Scale the 10% bonus
                    final_efficiency *= (1.0 + additional_trait_bonus)
                    print(f"Employee {self.name}: +{additional_trait_bonus*100:.1f}% trait effectiveness from housing")
            
            # Print debug info if bonuses are applied
            if final_efficiency > base_efficiency:
                total_bonus_percent = int(((final_efficiency / base_efficiency) - 1.0) * 100)
                print(f"Employee {self.name}: +{total_bonus_percent}% total efficiency from buildings")
            
            return final_efficiency
        else:
            # Fallback to legacy system if building manager not available
            efficiency = base_efficiency
            
            # Housing usage bonus (+25% trait effectiveness for hard workers) - legacy fallback
            if self.housing_recently_used and "hard_worker" in self.traits:
                trait_enhancement = 0.025  # Additional 2.5% on top of base 10%
                efficiency *= (1.0 + trait_enhancement)
                
            # Legacy tool shed check - fallback for compatibility
            if hasattr(grid_manager, 'find_buildings_of_type'):
                tool_sheds = grid_manager.find_buildings_of_type('tool_shed')
                for shed_x, shed_y in tool_sheds:
                    distance = abs(self.x - shed_x) + abs(self.y - shed_y)  # Manhattan distance
                    if distance <= 3.0:  # Within 3 tiles
                        efficiency *= 1.15  # +15% efficiency bonus
                        print(f"Employee {self.name}: +15% efficiency bonus from tool shed (legacy)")
                        break  # Only one tool shed bonus applies
            
            return efficiency
    
    def _initialize_employee_specialization(self):
        """Initialize employee specialization for enhanced task system"""
        if not ENABLE_EMPLOYEE_SPECIALIZATIONS:
            return None
        
        # Import here to avoid circular imports
        from scripts.tasks.task_models import EmployeeSpecialization, EmployeeRole
        
        # Assign employee roles based on name or random assignment
        # This creates variety while being deterministic for testing
        name_lower = self.name.lower()
        
        if 'sam' in name_lower:
            # Sam starts as a Field Operator - good at basic tasks
            primary_role = EmployeeRole.FIELD_OPERATOR
        elif 'barry' in name_lower or 'more' in name_lower:
            # Barry More becomes a Harvest Specialist - focused on harvesting
            primary_role = EmployeeRole.HARVEST_SPECIALIST
        elif 'maria' in name_lower or 'expert' in name_lower:
            # Maria or expert workers become Crop Managers
            primary_role = EmployeeRole.CROP_MANAGER
        elif 'tech' in name_lower or 'maintenance' in name_lower:
            # Technical workers become Maintenance Technicians
            primary_role = EmployeeRole.MAINTENANCE_TECH
        else:
            # Default new employees start as General Laborers
            primary_role = EmployeeRole.GENERAL_LABORER
        
        # Create specialization with automatically generated skills
        specialization = EmployeeSpecialization(primary_role=primary_role)
        
        print(f"  -> Initialized as {primary_role.value} with skills:")
        for task_type, skill_level in specialization.skill_levels.items():
            print(f"     * {task_type.value}: {skill_level.name} ({skill_level.value} stars)")
        
        return specialization
    
    def get_task_efficiency(self, task_type_str: str) -> float:
        """Get efficiency for a specific task type (legacy compatibility + enhanced)"""
        base_efficiency = self.work_efficiency
        
        # Enhanced system - use specialization if available
        if ENABLE_EMPLOYEE_SPECIALIZATIONS and self.specialization:
            # Convert legacy task string to TaskType enum
            from scripts.tasks.task_models import convert_legacy_task, TaskType
            
            # Handle both string and TaskType inputs
            if isinstance(task_type_str, str):
                task_type = convert_legacy_task(task_type_str)
            else:
                task_type = task_type_str
            
            # Get specialization efficiency
            specialization_efficiency = self.specialization.get_efficiency_for_task(task_type)
            
            # Combine base efficiency with specialization
            total_efficiency = base_efficiency * specialization_efficiency
            
            return total_efficiency
        else:
            # Legacy system - return base efficiency
            return base_efficiency
    
    def get_specialization_summary(self) -> Dict:
        """Get summary of employee specialization for UI display"""
        if not ENABLE_EMPLOYEE_SPECIALIZATIONS or not self.specialization:
            return {
                'role': 'General Worker',
                'skills': {},
                'top_skills': []
            }
        
        # Create UI-friendly summary
        skills_summary = {}
        for task_type, skill_level in self.specialization.skill_levels.items():
            skills_summary[task_type.value] = {
                'level': skill_level.value,
                'name': skill_level.name,
                'efficiency': self.specialization.get_efficiency_for_task(task_type)
            }
        
        # Find top 3 skills
        sorted_skills = sorted(
            skills_summary.items(), 
            key=lambda x: x[1]['level'], 
            reverse=True
        )
        top_skills = sorted_skills[:3]
        
        return {
            'role': self.specialization.primary_role.value.replace('_', ' ').title(),
            'skills': skills_summary,
            'top_skills': [{'task': skill[0], 'level': skill[1]['level']} for skill in top_skills]
        }