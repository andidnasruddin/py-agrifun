"""
Employee - Individual worker with AI, needs, and task execution
Represents a single farm worker with pathfinding, needs system, and work capabilities.
"""

import pygame
import math
from typing import List, Tuple, Optional, Dict
from enum import Enum
from scripts.core.config import *
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
        
        # Visual
        self.color = COLORS['employee']
        self.radius = 8
        
        print(f"Employee {self.name} ({self.id}) created at ({x}, {y})")
    
    def add_trait(self, trait_name: str):
        """Add a trait to the employee"""
        if trait_name not in self.traits:
            self.traits.append(trait_name)
            self._apply_trait_effects(trait_name)
    
    def _apply_trait_effects(self, trait_name: str):
        """Apply trait effects to employee stats"""
        if trait_name == "hard_worker":
            self.work_efficiency *= 1.1  # +10% efficiency
            # Note: -5% stamina drain implemented in update_needs
        elif trait_name == "runner":
            self.walking_speed *= 1.1  # +10% speed
            self.speed = self.walking_speed
    
    def assign_task(self, task_type: str, target_tiles: List, **kwargs):
        """Assign a new task to the employee with optional parameters"""
        task = {
            'type': task_type,
            'tiles': target_tiles,
            'completed_tiles': [],
            'status': 'pending',
            **kwargs  # Allow additional task parameters like crop_type
        }
        self.assigned_tasks.append(task)
        
        # Start working on this task if idle
        if self.state == EmployeeState.IDLE and not self.current_task:
            self._start_next_task()
    
    def _start_next_task(self):
        """Start working on the next available task"""
        if not self.assigned_tasks:
            self.current_task = None
            self.state = EmployeeState.IDLE
            return
        
        # Find first incomplete task
        for task in self.assigned_tasks:
            if task['status'] == 'pending':
                remaining_tiles = [t for t in task['tiles'] 
                                 if t not in task['completed_tiles']]
                if remaining_tiles:
                    self.current_task = task
                    task['status'] = 'in_progress'
                    
                    # Move to first tile that needs work
                    target_tile = remaining_tiles[0]
                    self._move_to_tile(target_tile.x, target_tile.y)
                    return
                else:
                    task['status'] = 'completed'
        
        # No tasks available
        self.current_task = None
        self.state = EmployeeState.IDLE
    
    def _move_to_tile(self, grid_x: int, grid_y: int):
        """Start moving to a specific grid tile using efficient direct movement"""
        if abs(self.x - grid_x) < 0.1 and abs(self.y - grid_y) < 0.1:
            # Already at target (within tolerance)
            self.state = EmployeeState.WORKING
            self.state_timer = 0.0
            return
        
        # Simple, efficient direct movement
        self.target_x = grid_x
        self.target_y = grid_y
        self.state = EmployeeState.MOVING
        self.state_timer = 0.0
        
        print(f"Employee {self.name}: Moving to ({grid_x}, {grid_y})")
    
    def update(self, dt: float, grid_manager):
        """Update employee AI and needs"""
        # Clean up completed tasks first
        self._cleanup_completed_tasks()
        
        # Update needs
        self.update_needs(dt)
        
        # Check for critical needs
        if self._has_critical_needs():
            self._handle_critical_needs()
            return
        
        # Update AI state
        self.update_ai(dt, grid_manager)
    
    def update_needs(self, dt: float):
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
        elif self.state == EmployeeState.RESTING:
            rest_decay = -REST_DECAY_RATE * 2 * hours_passed  # Restore rest
        else:
            rest_decay = REST_DECAY_RATE * 0.5 * hours_passed  # Slow decay
        
        # Apply decay
        self.hunger = max(0, self.hunger - hunger_decay)
        self.thirst = max(0, self.thirst - thirst_decay)
        self.rest = max(0, min(MAX_REST, self.rest - rest_decay))
    
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
            # For now, just rest in place (amenities not implemented)
            self.state = EmployeeState.RESTING
            self.state_timer = 0.0
    
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
        
        # Work takes time based on efficiency
        work_time_needed = 3.0 / self.work_efficiency  # Base 3 seconds per task
        
        if self.state_timer >= work_time_needed:
            # Complete the work on this tile
            if self._perform_work_on_tile(tile):
                self._complete_current_tile()
            else:
                # Work failed, skip tile
                self._complete_current_tile()
    
    def _perform_work_on_tile(self, tile) -> bool:
        """Perform the assigned work on a tile"""
        if not self.current_task:
            return False
        
        task_type = self.current_task['type']
        
        if task_type == 'till' and tile.can_till():
            return tile.till()
        elif task_type == 'plant' and tile.can_plant():
            # Get crop type from current task, default to corn for backward compatibility
            crop_type = self.current_task.get('crop_type', DEFAULT_CROP_TYPE)
            return tile.plant(crop_type)
        elif task_type == 'harvest' and tile.can_harvest():
            crop_type, yield_amount = tile.harvest()  # Updated to handle new tuple return
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
        
        # Find next tile to work on
        remaining_tiles = [t for t in self.current_task['tiles'] 
                          if t not in self.current_task['completed_tiles']]
        
        if remaining_tiles:
            # Move to next tile
            next_tile = remaining_tiles[0]
            self._move_to_tile(next_tile.x, next_tile.y)
        else:
            # Task completed
            self.current_task['status'] = 'completed'
            self.current_task = None
            self._start_next_task()
    
    def _cleanup_completed_tasks(self):
        """Remove completed tasks from the assigned_tasks list to prevent queue buildup"""
        initial_count = len(self.assigned_tasks)
        
        # Remove tasks marked as completed
        self.assigned_tasks = [task for task in self.assigned_tasks 
                              if task['status'] != 'completed']
        
        removed_count = initial_count - len(self.assigned_tasks)
        if removed_count > 0:
            print(f"Employee {self.name}: Cleaned up {removed_count} completed tasks ({len(self.assigned_tasks)} remaining)")
    
    def get_pixel_position(self) -> Tuple[int, int]:
        """Get employee position in screen pixels"""
        pixel_x = int(self.x * TILE_SIZE + TILE_SIZE // 2)
        pixel_y = int(self.y * TILE_SIZE + TILE_SIZE // 2 + 70)  # UI offset
        return (pixel_x, pixel_y)
    
    def render(self, screen: pygame.Surface):
        """Render the employee with enhanced visual indicators"""
        pixel_x, pixel_y = self.get_pixel_position()
        
        # Draw movement direction line when moving
        if self.state == EmployeeState.MOVING:
            self._render_movement_line(screen, pixel_x, pixel_y)
        
        # Draw employee background circle (larger for better visibility)
        pygame.draw.circle(screen, (255, 255, 255), (pixel_x, pixel_y), self.radius + 2)  # White outline
        pygame.draw.circle(screen, self.color, (pixel_x, pixel_y), self.radius)
        
        # Draw state indicator
        self._render_state_indicator(screen, pixel_x, pixel_y)
        
        # Draw employee name
        self._render_employee_name(screen, pixel_x, pixel_y)
        
        # Draw needs bars above employee
        self._render_needs_bars(screen, pixel_x, pixel_y - self.radius - 35)
    
    def _render_employee_name(self, screen: pygame.Surface, x: int, y: int):
        """Render employee name below the sprite"""
        font = pygame.font.Font(None, 20)
        name_surface = font.render(self.name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(x, y + self.radius + 12))
        
        # Draw background rectangle for better readability
        bg_rect = name_rect.inflate(4, 2)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
        
        screen.blit(name_surface, name_rect)
    
    def _render_state_indicator(self, screen: pygame.Surface, x: int, y: int):
        """Render current state indicator with better visibility"""
        indicator_colors = {
            EmployeeState.IDLE: (128, 128, 128),
            EmployeeState.MOVING: (0, 150, 255),
            EmployeeState.WORKING: (0, 255, 0),
            EmployeeState.RESTING: (255, 255, 0),
            EmployeeState.SEEKING_AMENITY: (255, 0, 255)
        }
        
        color = indicator_colors.get(self.state, (255, 255, 255))
        # Draw larger, more visible state indicator
        pygame.draw.circle(screen, (0, 0, 0), (x + 8, y - 8), 5)  # Black outline
        pygame.draw.circle(screen, color, (x + 8, y - 8), 4)
    
    def _render_needs_bars(self, screen: pygame.Surface, x: int, y: int):
        """Render needs bars above employee"""
        bar_width = 30
        bar_height = 4
        bar_spacing = 2
        
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
    
    def _render_movement_line(self, screen: pygame.Surface, current_x: int, current_y: int):
        """Render movement direction line for direct movement"""
        target_pixel_x = int(self.target_x * TILE_SIZE + TILE_SIZE // 2)
        target_pixel_y = int(self.target_y * TILE_SIZE + TILE_SIZE // 2 + 70)
        
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