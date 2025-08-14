"""
Employee Manager - Handles all employees and workforce coordination
Manages hiring, firing, task assignment, and employee coordination.
"""

import pygame
from typing import List, Dict, Optional
from scripts.employee.employee import Employee
# Pathfinding removed - using direct movement for performance
from scripts.core.config import *


class EmployeeManager:
    """Manages all farm employees"""
    
    def __init__(self, event_system, grid_manager, inventory_manager=None, time_manager=None, create_starting_employee=True):
        """Initialize employee manager"""
        self.event_system = event_system
        self.grid_manager = grid_manager
        self.inventory_manager = inventory_manager
        self.time_manager = time_manager
        
        # Employee storage
        self.employees: Dict[str, Employee] = {}
        self.next_employee_id = 1
        
        # Direct movement system (pathfinding removed for performance)
        
        # UI status update timer
        self.ui_status_timer = 0.0
        self.ui_status_update_interval = 1.0  # Update UI every 1 second
        
        # Register for events
        self.event_system.subscribe('task_assigned', self._handle_task_assignment)
        self.event_system.subscribe('day_passed', self._handle_day_passed)
        self.event_system.subscribe('get_employee_roster', self._handle_roster_request)
        self.event_system.subscribe('get_employee_count_for_ui', self._handle_ui_count_request)
        self.event_system.subscribe('get_employee_count', self._handle_employee_count_request)
        self.event_system.subscribe('cancel_tasks_requested', self._handle_cancel_tasks_request)
        self.event_system.subscribe('crop_type_provided', self._handle_crop_type_for_planting)
        self.event_system.subscribe('work_order_cancelled', self._handle_work_order_cancelled)
        
        # Create starting employee for MVP (can be disabled for pure hiring system)
        if create_starting_employee:
            self._create_starting_employee()
            print("Employee Manager initialized with starting employee Sam")
        else:
            print("Employee Manager initialized - No employees (hiring required)")
        
        # Set up task completion callbacks for work order integration
        self._setup_task_completion_callbacks()
        
        print("Employee Manager: Direct movement system active")
    
    def _setup_task_completion_callbacks(self):
        """Set up task completion callbacks for all employees"""
        for employee in self.employees.values():
            employee.set_completion_callback(self._handle_employee_task_completion)
    
    def _handle_employee_task_completion(self, employee_id: str, completed_task: dict):
        """Handle employee task completion and notify work order system"""
        work_order_id = completed_task.get('work_order_id')
        if work_order_id:
            print(f"Employee {employee_id} completed task for work order {work_order_id}")
            # Emit event for work order system to handle completion
            self.event_system.emit('employee_task_completed', {
                'employee_id': employee_id,
                'work_order_id': work_order_id,
                'task_type': completed_task.get('type'),
                'completed_tiles': len(completed_task.get('completed_tiles', []))
            })
    
    def set_inventory_manager(self, inventory_manager):
        """Set inventory manager for synchronous harvest processing"""
        self.inventory_manager = inventory_manager
        print("Employee Manager: Inventory manager connected for synchronous harvests")
    
    def _create_starting_employee(self):
        """Create the initial employee for MVP"""
        # Use the standard hiring system for consistent ID management
        employee_id = f"emp_{self.next_employee_id:03d}"
        self.next_employee_id += 1
        
        employee = Employee(
            employee_id=employee_id,
            name="Sam",
            x=8.0,  # Center of 16x16 grid
            y=8.0
        )
        
        # Add some basic traits
        employee.add_trait("hard_worker")
        
        # Direct movement (no pathfinding setup needed)
        
        self.employees[employee_id] = employee
        print(f"Created starting employee: {employee.name} ({employee_id}) with pathfinding enabled")
    
    def hire_employee(self, name: str, traits: List[str] = None) -> str:
        """Hire a new employee"""
        employee_id = f"emp_{self.next_employee_id:03d}"
        self.next_employee_id += 1
        
        # Place new employee at farm center
        employee = Employee(
            employee_id=employee_id,
            name=name,
            x=8.0,
            y=8.0
        )
        
        # Apply traits if provided
        if traits:
            for trait in traits:
                employee.add_trait(trait)
        
        # Direct movement (no pathfinding setup needed)
        
        # Set up task completion callback
        employee.set_completion_callback(self._handle_employee_task_completion)
        
        self.employees[employee_id] = employee
        
        # Emit hiring event
        self.event_system.emit('employee_hired', {
            'employee_id': employee_id,
            'name': name,
            'traits': traits or []
        })
        
        print(f"Hired employee: {name} ({employee_id})")
        return employee_id
    
    def fire_employee(self, employee_id: str) -> bool:
        """Fire an employee"""
        if employee_id in self.employees:
            employee = self.employees[employee_id]
            
            # Clear any assigned tasks
            self._clear_employee_tasks(employee_id)
            
            # Remove employee
            del self.employees[employee_id]
            
            # Emit firing event
            self.event_system.emit('employee_fired', {
                'employee_id': employee_id,
                'name': employee.name
            })
            
            print(f"Fired employee: {employee.name} ({employee_id})")
            return True
        
        return False
    
    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        return self.employees.get(employee_id)
    
    def get_all_employees(self) -> List[Employee]:
        """Get list of all employees"""
        return list(self.employees.values())
    
    def get_available_employee(self) -> Optional[Employee]:
        """Get first available employee for task assignment"""
        for employee in self.employees.values():
            if len(employee.assigned_tasks) < 3:  # Max 3 pending tasks
                return employee
        return None
    
    def get_available_employees(self) -> List[Employee]:
        """Get all available employees for task assignment"""
        available = []
        for employee in self.employees.values():
            if len(employee.assigned_tasks) < 3:  # Max 3 pending tasks
                available.append(employee)
        return available
    
    def _distribute_tiles_among_employees(self, tiles: List, task_type: str, employees: List[Employee]) -> bool:
        """Distribute tiles among multiple employees for efficient parallel work"""
        if not tiles or not employees:
            return False
        
        # Enhanced Task System - Sort employees by skill for this task (Phase 2A)
        if ENABLE_EMPLOYEE_SPECIALIZATIONS:
            # Sort employees by task efficiency (best skilled first)
            employees_with_skill = []
            for employee in employees:
                efficiency = employee.get_task_efficiency(task_type)
                employees_with_skill.append((employee, efficiency))
            
            # Sort by efficiency (highest first)
            employees_with_skill.sort(key=lambda x: x[1], reverse=True)
            employees = [emp[0] for emp in employees_with_skill]
            
            print(f"Task assignment for {task_type}:")
            for emp, eff in employees_with_skill:
                print(f"  {emp.name}: {eff:.2f}x efficiency")
        
        # Sort tiles by position for logical distribution (top-left to bottom-right)
        tiles.sort(key=lambda t: (t.y, t.x))
        
        # Enhanced distribution - give more tiles to more skilled employees
        if ENABLE_EMPLOYEE_SPECIALIZATIONS and len(employees) > 1:
            # Calculate weighted distribution based on skill levels
            total_efficiency = sum(emp.get_task_efficiency(task_type) for emp in employees)
            tile_assignments = []
            
            remaining_tiles = len(tiles)
            for i, employee in enumerate(employees):
                if i == len(employees) - 1:  # Last employee gets remaining tiles
                    tiles_for_employee = remaining_tiles
                else:
                    # Proportional assignment based on efficiency
                    efficiency_ratio = employee.get_task_efficiency(task_type) / total_efficiency
                    tiles_for_employee = max(1, int(len(tiles) * efficiency_ratio))
                    tiles_for_employee = min(tiles_for_employee, remaining_tiles)
                
                tile_assignments.append(tiles_for_employee)
                remaining_tiles -= tiles_for_employee
                
                if remaining_tiles <= 0:
                    break
        else:
            # Legacy distribution - equal distribution
            tiles_per_employee = len(tiles) // len(employees)
            remainder = len(tiles) % len(employees)
            tile_assignments = []
            
            for i in range(len(employees)):
                tiles_for_employee = tiles_per_employee + (1 if i < remainder else 0)
                tile_assignments.append(tiles_for_employee)
        
        total_assigned = 0
        employee_assignments = []
        
        # Distribute tiles using calculated assignments
        start_idx = 0
        for i, employee in enumerate(employees):
            if i >= len(tile_assignments):
                break
                
            tiles_for_this_employee = tile_assignments[i]
            
            if tiles_for_this_employee == 0:
                break  # No more tiles to assign
            
            # Get tiles for this employee
            employee_tiles = tiles[start_idx:start_idx + tiles_for_this_employee]
            start_idx += tiles_for_this_employee
            
            if employee_tiles:
                # Assign tiles to employee through grid manager
                assigned_count = 0
                for tile in employee_tiles:
                    if self.grid_manager._can_assign_task(tile, task_type) and not tile.task_assigned_to:
                        tile.task_assignment = task_type
                        tile.task_assigned_to = employee.id
                        assigned_count += 1
                
                if assigned_count > 0:
                    # Emit task assignment event for this employee
                    self.event_system.emit('task_assigned', {
                        'task_type': task_type,
                        'employee_id': employee.id,
                        'tile_count': assigned_count,
                        'tiles': employee_tiles
                    })
                    
                    total_assigned += assigned_count
                    employee_assignments.append({
                        'employee': employee,
                        'tiles': assigned_count
                    })
                    
                    # Enhanced logging with efficiency information
                    if ENABLE_EMPLOYEE_SPECIALIZATIONS:
                        efficiency = employee.get_task_efficiency(task_type)
                        print(f"Assigned {task_type} task to {assigned_count} tiles for employee {employee.name} (efficiency: {efficiency:.2f}x)")
                    else:
                        print(f"Assigned {task_type} task to {assigned_count} tiles for employee {employee.name}")
        
        # Emit collective feedback
        if total_assigned > 0:
            employee_names = [assign['employee'].name for assign in employee_assignments]
            self.event_system.emit('task_assigned_feedback', {
                'task_type': task_type,
                'assigned_count': total_assigned,
                'employee_name': f"{len(employee_assignments)} employees: {', '.join(employee_names)}",
                'employee_count': len(employee_assignments)
            })
            return True
        
        return False
    
    def cancel_tasks_on_selection(self) -> bool:
        """Cancel tasks on selected tiles and remove from employee task queues"""
        if not self.grid_manager.selected_tiles:
            # Emit feedback about no selection
            self.event_system.emit('task_assignment_failed', {
                'reason': 'no_selection',
                'message': 'No tiles selected for task cancellation',
                'task_type': 'cancel'
            })
            return False
        
        cancelled_tasks = {}
        cancelled_count = 0
        
        for tile in self.grid_manager.selected_tiles:
            if tile.task_assignment and tile.task_assigned_to:
                # Track which employee and task type
                employee_id = tile.task_assigned_to
                task_type = tile.task_assignment
                
                # Remove task assignment from tile
                tile.task_assignment = None
                tile.task_assigned_to = None
                cancelled_count += 1
                
                # Track cancellations by employee
                if employee_id not in cancelled_tasks:
                    cancelled_tasks[employee_id] = []
                cancelled_tasks[employee_id].append((tile, task_type))
        
        if cancelled_count == 0:
            self.event_system.emit('task_assignment_failed', {
                'reason': 'no_tasks_to_cancel',
                'message': 'No tasks found on selected tiles to cancel',
                'task_type': 'cancel'
            })
            return False
        
        # Remove cancelled tiles from employee task queues
        affected_employees = []
        for employee_id, cancelled_tiles in cancelled_tasks.items():
            employee = self.get_employee(employee_id)
            if employee:
                removed_count = self._remove_tiles_from_employee_tasks(employee, [tile for tile, _ in cancelled_tiles])
                if removed_count > 0:
                    affected_employees.append(employee.name)
                    print(f"Cancelled {len(cancelled_tiles)} tasks for employee {employee.name}")
        
        # Emit success feedback
        employee_list = ', '.join(affected_employees) if affected_employees else 'employees'
        self.event_system.emit('task_assigned_feedback', {
            'task_type': 'cancel',
            'assigned_count': cancelled_count,
            'employee_name': f"Cancelled for {employee_list}",
            'employee_count': len(affected_employees)
        })
        
        print(f"Cancelled {cancelled_count} tasks across {len(affected_employees)} employees")
        return True
    
    def _remove_tiles_from_employee_tasks(self, employee: Employee, tiles_to_remove: List) -> int:
        """Remove specific tiles from an employee's task queue"""
        removed_count = 0
        tiles_to_remove_set = set(tiles_to_remove)
        
        # Check current task
        if employee.current_task:
            original_tiles = employee.current_task['tiles']
            remaining_tiles = [t for t in original_tiles if t not in tiles_to_remove_set]
            
            if len(remaining_tiles) != len(original_tiles):
                removed_count += len(original_tiles) - len(remaining_tiles)
                
                if remaining_tiles:
                    # Update current task with remaining tiles
                    employee.current_task['tiles'] = remaining_tiles
                else:
                    # No tiles left, cancel current task and move to next
                    employee.current_task['status'] = 'completed'
                    employee.current_task = None
                    employee._start_next_task()
        
        # Check assigned tasks queue
        for task in employee.assigned_tasks:
            if 'tiles' in task:
                original_tiles = task['tiles']
                remaining_tiles = [t for t in original_tiles if t not in tiles_to_remove_set]
                
                if len(remaining_tiles) != len(original_tiles):
                    removed_count += len(original_tiles) - len(remaining_tiles)
                    
                    if remaining_tiles:
                        task['tiles'] = remaining_tiles
                    else:
                        # Mark task as completed if no tiles left
                        task['status'] = 'completed'
        
        # Clean up any completed tasks
        employee._cleanup_completed_tasks()
        
        return removed_count
    
    def assign_task_to_employee(self, employee_id: str, task_type: str, tiles: List, **kwargs):
        """Assign a task to a specific employee"""
        employee = self.get_employee(employee_id)
        if employee:
            employee.assign_task(task_type, tiles, **kwargs)
            return True
        return False
    
    def _clear_employee_tasks(self, employee_id: str):
        """Clear all tasks for an employee"""
        employee = self.get_employee(employee_id)
        if employee:
            # Clear task assignments from tiles
            for task in employee.assigned_tasks:
                for tile in task.get('tiles', []):
                    if tile.task_assigned_to == employee_id:
                        tile.task_assignment = None
                        tile.task_assigned_to = None
            
            # Clear employee tasks
            employee.assigned_tasks.clear()
            employee.current_task = None
    
    def update(self, dt: float):
        """Update all employees"""
        # Apply time speed multiplier to employee updates
        if self.time_manager and hasattr(self.time_manager, 'time_speed'):
            effective_dt = dt * self.time_manager.time_speed
        else:
            effective_dt = dt
            
        for employee in self.employees.values():
            employee.update(effective_dt, self.grid_manager)
            
            # Check if employee should seek buildings for their needs
            employee.check_and_seek_building()
            
            # Process harvest events synchronously to avoid race conditions
            if hasattr(employee, '_pending_harvest') and employee._pending_harvest:
                harvest_data = employee._pending_harvest
                
                # Process harvest directly through inventory manager
                if self.inventory_manager:
                    success = self.inventory_manager.add_crop(
                        harvest_data['crop_type'],
                        harvest_data['quantity'],
                        harvest_data['quality'],
                        1  # TODO: Get actual day from time manager
                    )
                    
                    if success:
                        # Emit harvest completion event for UI updates
                        self.event_system.emit('harvest_completed', {
                            'crop_type': harvest_data['crop_type'],
                            'quantity': harvest_data['quantity'],
                            'quality': harvest_data['quality'],
                            'employee_id': employee.id,
                            'stored_successfully': True
                        })
                    else:
                        # Storage full - emit warning
                        self.event_system.emit('harvest_storage_failed', {
                            'crop_type': harvest_data['crop_type'],
                            'quantity': harvest_data['quantity'],
                            'employee_id': employee.id,
                            'reason': 'storage_full'
                        })
                else:
                    # Fallback: emit old-style event if no inventory manager
                    self.event_system.emit('crop_harvested', {
                        'crop_type': harvest_data['crop_type'],
                        'quantity': harvest_data['quantity'],
                        'quality': harvest_data['quality'],
                        'employee_id': employee.id,
                        'day': 1
                    })
                
                # Clear the harvest data
                employee._pending_harvest = None
        
        # Update UI status periodically
        self.ui_status_timer += effective_dt
        if self.ui_status_timer >= self.ui_status_update_interval:
            self._emit_status_update()
            self.ui_status_timer = 0.0
    
    def render(self, screen: pygame.Surface):
        """Render all employees with grid transformations"""
        # Get grid transformation parameters from enhanced grid renderer
        if hasattr(self.grid_manager, 'enhanced_renderer'):
            renderer = self.grid_manager.enhanced_renderer
            zoom_factor = renderer.zoom_factor
            pan_offset_x = renderer.pan_offset_x
            pan_offset_y = renderer.pan_offset_y
            hud_height = renderer.hud_height
        else:
            # Fallback to default values if enhanced renderer not available
            zoom_factor = 1.0
            pan_offset_x = 0.0
            pan_offset_y = 0.0
            hud_height = 70
        
        # Render all employees with transformation parameters
        for employee in self.employees.values():
            employee.render(screen, zoom_factor, pan_offset_x, pan_offset_y, hud_height)
    
    def handle_mouse_click(self, pos: tuple, button: int):
        """Handle mouse clicks for employee interaction"""
        # For now, just handle grid interaction through grid manager
        if button == 1:  # Left click
            self.grid_manager.handle_mouse_down(pos, button)
        
        # Add employee-specific click handling later
    
    def handle_mouse_motion(self, pos: tuple):
        """Handle mouse motion for building placement preview"""
        self.grid_manager.handle_mouse_motion(pos)
    
    def handle_mouse_drag(self, pos: tuple):
        """Handle mouse drag for tile selection"""
        self.grid_manager.handle_mouse_drag(pos)
    
    def handle_mouse_up(self, pos: tuple, button: int):
        """Handle mouse button release"""
        if button == 1:  # Left click
            self.grid_manager.handle_mouse_up(pos, button)
    
    def assign_task_to_selection(self, task_type: str) -> bool:
        """Assign task to selected tiles distributing among available employees"""
        # Check if enhanced task system is enabled - if so, skip legacy assignment
        if ENABLE_ENHANCED_TASK_SYSTEM or ENABLE_WORK_ORDERS:
            print(f"Legacy task assignment bypassed for {task_type} - using enhanced task system")
            return True  # Return success but don't actually assign
        
        if not self.grid_manager.selected_tiles:
            # Emit feedback about no selection
            self.event_system.emit('task_assignment_failed', {
                'reason': 'no_selection',
                'message': f'No tiles selected for {task_type} task',
                'task_type': task_type
            })
            return False
        
        # Get all available employees
        available_employees = self.get_available_employees()
        if not available_employees:
            print("No available employees for task assignment")
            
            # Emit feedback about no available employees
            self.event_system.emit('task_assignment_failed', {
                'reason': 'no_available_employees',
                'message': 'No available employees for task assignment',
                'selected_tiles': len(self.grid_manager.selected_tiles)
            })
            
            return False
        
        # Filter tiles that can actually perform this task
        valid_tiles = []
        for tile in self.grid_manager.selected_tiles:
            if self.grid_manager._can_assign_task(tile, task_type) and not tile.task_assigned_to:
                valid_tiles.append(tile)
        
        if not valid_tiles:
            self.event_system.emit('task_assignment_failed', {
                'reason': 'no_valid_tiles',
                'message': f'No tiles are valid for {task_type} task',
                'task_type': task_type,
                'selected_count': len(self.grid_manager.selected_tiles)
            })
            return False
        
        # Distribute tiles among available employees
        return self._distribute_tiles_among_employees(valid_tiles, task_type, available_employees)
    
    def get_employee_status_summary(self) -> List[Dict]:
        """Get status summary for all employees"""
        return [emp.get_status_info() for emp in self.employees.values()]
    
    def _handle_task_assignment(self, event_data):
        """Handle task assignment events from grid manager"""
        task_type = event_data.get('task_type')
        employee_id = event_data.get('employee_id')
        tiles = event_data.get('tiles', [])
        
        # Assign task to the specified employee
        employee = self.get_employee(employee_id)
        if employee:
            employee.assign_task(task_type, tiles)
    
    def _handle_day_passed(self, event_data):
        """Handle day passing for employee payroll and status"""
        day = event_data.get('day', 1)
        
        # Calculate total wages due (individual wages)
        total_wages = sum(emp.daily_wage for emp in self.employees.values())
        
        # Emit payroll event
        self.event_system.emit('payroll_due', {
            'day': day,
            'employee_count': len(self.employees),
            'total_wages': total_wages,
            'employee_details': [
                {
                    'id': emp.id,
                    'name': emp.name,
                    'wage': emp.daily_wage,
                    'efficiency': emp.work_efficiency,
                    'traits': emp.traits
                }
                for emp in self.employees.values()
            ]
        })
        
        print(f"Day {day}: Payroll due for {len(self.employees)} employees: ${total_wages}")
    
    def handle_keyboard_input(self, key: int):
        """Handle keyboard input for task assignment shortcuts"""
        if not self.grid_manager.selected_tiles:
            return
        
        # Task assignment shortcuts
        if key == pygame.K_t:  # T for Till
            self.assign_task_to_selection('till')
        elif key == pygame.K_p:  # P for Plant
            # Get current crop selection from UI and assign planting task
            self.event_system.emit('get_current_crop_type_requested', {})
        elif key == pygame.K_h:  # H for Harvest
            self.assign_task_to_selection('harvest')
        elif key == pygame.K_x:  # X for Cancel tasks
            self.cancel_tasks_on_selection()
        elif key == pygame.K_c:  # C for Clear selection
            self.grid_manager._clear_selection()
        elif key == pygame.K_1:  # 1 for Hire first applicant
            self.event_system.emit('hire_applicant_by_index', {'index': 0})
        elif key == pygame.K_2:  # 2 for Hire second applicant  
            self.event_system.emit('hire_applicant_by_index', {'index': 1})
        elif key == pygame.K_3:  # 3 for Hire third applicant
            self.event_system.emit('hire_applicant_by_index', {'index': 2})
    
    def _handle_roster_request(self, event_data):
        """Handle request for employee roster and payroll information"""
        include_payroll = event_data.get('include_payroll', False)
        
        if not self.employees:
            print("\n=== EMPLOYEE ROSTER ===")
            print("No employees currently hired.")
            print("Use 'Hire Employee' button to recruit workers!")
            return
        
        total_daily_cost = sum(emp.daily_wage for emp in self.employees.values())
        
        print(f"\n=== EMPLOYEE ROSTER ({len(self.employees)} employees) ===")
        
        for i, (emp_id, employee) in enumerate(self.employees.items(), 1):
            trait_display = ', '.join([trait.replace('_', ' ').title() for trait in employee.traits])
            current_task = employee.current_task['type'] if employee.current_task else 'Idle'
            
            print(f"{i}. {employee.name} ({emp_id})")
            print(f"   Status: {employee.state.value.title()}")
            print(f"   Current Task: {current_task.title()}")
            print(f"   Daily Wage: ${employee.daily_wage}")
            print(f"   Traits: {trait_display}")
            print(f"   Work Efficiency: {employee.work_efficiency:.1f}x")
            print(f"   Pending Tasks: {len(employee.assigned_tasks)}")
            print()
        
        print(f"[PAYROLL] TOTAL DAILY COST: ${total_daily_cost}")
        print(f"[AVERAGE] Per employee: ${total_daily_cost / len(self.employees):.2f}")
        print()
        
        # Also show in UI notification
        self.event_system.emit('roster_displayed', {
            'employee_count': len(self.employees),
            'total_daily_cost': total_daily_cost,
            'employees': [
                {
                    'name': emp.name,
                    'id': emp_id,
                    'wage': emp.daily_wage,
                    'traits': emp.traits,
                    'efficiency': emp.work_efficiency
                }
                for emp_id, emp in self.employees.items()
            ]
        })
    
    def _handle_ui_count_request(self, event_data):
        """Handle UI request for current employee count"""
        self.event_system.emit('employee_count_update', {
            'count': len(self.employees)
        })
    
    def _handle_employee_count_request(self, event_data):
        """Handle generic employee count request for enhanced HUD"""
        self.event_system.emit('employee_count_changed', {
            'count': len(self.employees)
        })
    
    def _emit_status_update(self):
        """Emit real-time employee status for UI display"""
        if not self.employees:
            self.event_system.emit('employee_status_update', {'employees': []})
            return
        
        employee_status = []
        for emp in self.employees.values():
            status = {
                'name': emp.name,
                'id': emp.id,
                'state': emp.state.value,
                'current_task': emp.current_task['type'] if emp.current_task else None,
                'position': (emp.x, emp.y)
            }
            employee_status.append(status)
        
        self.event_system.emit('employee_status_update', {
            'employees': employee_status
        })
    
    def _handle_cancel_tasks_request(self, event_data):
        """Handle request to cancel tasks on selected tiles"""
        self.cancel_tasks_on_selection()
    
    def _handle_crop_type_for_planting(self, event_data):
        """Handle crop type selection for planting task"""
        crop_type = event_data.get('crop_type', DEFAULT_CROP_TYPE)
        print(f"Assigning planting task with crop type: {crop_type}")
        self.assign_planting_task_to_selection(crop_type)
    
    def assign_planting_task_to_selection(self, crop_type: str = DEFAULT_CROP_TYPE) -> bool:
        """Assign planting task with specific crop type to selected tiles"""
        # Check if enhanced task system is enabled - if so, skip legacy assignment
        if ENABLE_ENHANCED_TASK_SYSTEM or ENABLE_WORK_ORDERS:
            print(f"Legacy planting assignment bypassed for {crop_type} - using enhanced task system")
            return True  # Return success but don't actually assign
        
        if not self.grid_manager.selected_tiles:
            self.event_system.emit('task_assignment_failed', {
                'reason': 'no_selection',
                'message': f'No tiles selected for planting {CROP_TYPES[crop_type]["name"]}',
                'task_type': 'plant'
            })
            return False
        
        available_employees = self.get_available_employees()
        if not available_employees:
            self.event_system.emit('task_assignment_failed', {
                'reason': 'no_available_employees',
                'message': 'No available employees for planting task',
                'selected_tiles': len(self.grid_manager.selected_tiles)
            })
            return False
        
        # Filter tiles that can be planted
        valid_tiles = []
        for tile in self.grid_manager.selected_tiles:
            if tile.can_plant(crop_type) and not tile.task_assigned_to:
                valid_tiles.append(tile)
        
        if not valid_tiles:
            crop_name = CROP_TYPES[crop_type]['name']
            self.event_system.emit('task_assignment_failed', {
                'reason': 'no_valid_tiles',
                'message': f'No tiles can be planted with {crop_name}. Ensure tiles are tilled first.',
                'task_type': 'plant'
            })
            return False
        
        # Distribute planting tasks among employees
        assigned_count = 0
        for i, tile in enumerate(valid_tiles):
            employee = available_employees[i % len(available_employees)]
            
            # Create task with crop type information
            task_data = {
                'type': 'plant',
                'crop_type': crop_type,
                'target_tile': (tile.x, tile.y)
            }
            
            employee.assign_task(task_data['type'], [tile], crop_type=crop_type)
            tile.task_assignment = 'plant'
            tile.task_assigned_to = employee.id
            assigned_count += 1
        
        crop_name = CROP_TYPES[crop_type]['name']
        print(f"Assigned {assigned_count} {crop_name} planting tasks among {len(available_employees)} employees")
        
        self.event_system.emit('task_assigned_feedback', {
            'task_type': 'plant',
            'crop_type': crop_type,
            'crop_name': crop_name,
            'tiles_assigned': assigned_count,
            'employees_involved': len(available_employees)
        })
        
        return True
    
    def _handle_work_order_cancelled(self, event_data):
        """Handle work order cancellation - stop employees from working on cancelled tasks"""
        work_order_id = event_data.get('work_order_id')
        task_type = event_data.get('task_type')
        reason = event_data.get('reason', 'Work order cancelled')
        
        print(f"Work order cancellation received: {work_order_id} ({task_type}) - {reason}")
        
        # Stop all employees working on tasks related to this work order
        cancelled_count = 0
        for employee_id, employee in self.employees.items():
            # Check if employee has current task
            if employee.current_task:
                current_task_type = employee.current_task.get('type', '')
                # For now, cancel all tasks of the same type - can be enhanced with work order ID tracking
                if current_task_type == task_type.lower():
                    print(f"Cancelling {task_type} task for employee {employee.name}")
                    # Clear current task
                    employee.current_task = None
                    # Return to idle state
                    employee.state = employee.EmployeeState.IDLE
                    employee.state_timer = 0.0
                    cancelled_count += 1
                    
                    # Clear task assignments from tiles
                    if hasattr(employee, 'assigned_tasks'):
                        for task in employee.assigned_tasks[:]:
                            if task.get('type') == task_type.lower():
                                # Clear tile assignments
                                for tile in task.get('tiles', []):
                                    if hasattr(tile, 'task_assignment'):
                                        tile.task_assignment = None
                                        tile.task_assigned_to = None
                                # Remove from assigned tasks
                                employee.assigned_tasks.remove(task)
        
        if cancelled_count > 0:
            print(f"Successfully stopped {cancelled_count} employee(s) from working on cancelled {task_type} tasks")
        else:
            print(f"No employees were working on {task_type} tasks to cancel")