"""
Task System Integration - Phase 2B
Bridges the work order system with existing task assignment and employee management.
Provides seamless integration while maintaining backward compatibility.
"""

from typing import List, Dict, Optional, Any
from scripts.core.config import *
from scripts.tasks.work_order_manager import WorkOrderManager
from scripts.tasks.dynamic_work_orders import DynamicWorkOrderGenerator
from scripts.tasks.task_models import TaskType, TaskPriority, convert_legacy_task


class TaskSystemIntegration:
    """
    Integration layer between work order system and existing task management
    Provides unified interface for task assignment regardless of which system is active
    """
    
    def __init__(self, event_system, grid_manager=None, employee_manager=None):
        """Initialize task system integration"""
        self.event_system = event_system  # Event system for communication
        self.grid_manager = grid_manager  # Grid manager reference
        self.employee_manager = employee_manager  # Employee manager reference
        
        # Work order system components (Phase 2B)
        self.work_order_manager = None
        self.dynamic_generator = None
        
        # Initialize enhanced systems if enabled
        if ENABLE_WORK_ORDERS:
            self._initialize_work_order_system()
        
        # Set up event handlers for integration
        self._setup_integration_handlers()
        
        print("Task System Integration initialized")
        print(f"  Work orders enabled: {ENABLE_WORK_ORDERS}")
        print(f"  Employee specializations enabled: {ENABLE_EMPLOYEE_SPECIALIZATIONS}")
        print(f"  Dynamic generation enabled: {ENABLE_DYNAMIC_TASK_GENERATION}")
    
    def _initialize_work_order_system(self):
        """Initialize work order management components"""
        try:
            # Create work order manager
            self.work_order_manager = WorkOrderManager(self.event_system)
            # Inject reference to task integration for direct employee access
            self.work_order_manager.task_integration = self
            
            # Create dynamic work order generator if enabled
            if ENABLE_DYNAMIC_TASK_GENERATION:
                self.dynamic_generator = DynamicWorkOrderGenerator(
                    self.work_order_manager, self.event_system
                )
            
            print("Work order system components initialized successfully")
            
        except Exception as e:
            print(f"Error initializing work order system: {e}")
            # Note: Work order initialization failed
            # In production, this would be handled by feature flag management
            print("Work order initialization failed - check system configuration")
    
    def _setup_integration_handlers(self):
        """Set up event handlers for system integration"""
        # Legacy system events
        self.event_system.subscribe('task_assignment_requested', self._handle_legacy_task_request)
        self.event_system.subscribe('assign_task_to_selection', self._handle_selection_assignment)
        
        # Work order system events
        if ENABLE_WORK_ORDERS:
            self.event_system.subscribe('get_available_employees_for_work_order', self._handle_employee_request)
            self.event_system.subscribe('work_order_assigned', self._handle_work_order_assignment)
            self.event_system.subscribe('request_grid_for_analysis', self._handle_grid_analysis_request)
            self.event_system.subscribe('work_order_cancelled', self._handle_work_order_cancelled)
        
        # UI integration events
        self.event_system.subscribe('get_work_orders_for_ui', self._handle_work_orders_ui_request)
        self.event_system.subscribe('get_employee_assignments_for_ui', self._handle_employee_assignments_ui_request)
    
    def assign_task(self, task_type: str, selected_tiles: List, employee_id: str = None) -> bool:
        """
        Unified task assignment interface
        Routes to appropriate system based on configuration
        """
        if not selected_tiles:
            return False
        
        # Convert tiles to coordinate format
        plot_coords = [(tile.x, tile.y) for tile in selected_tiles]
        
        # Route to appropriate system
        if ENABLE_WORK_ORDERS:
            return self._assign_via_work_orders(task_type, plot_coords, employee_id)
        else:
            return self._assign_via_legacy_system(task_type, selected_tiles, employee_id)
    
    def _assign_via_work_orders(self, task_type: str, plot_coords: List, employee_id: str = None) -> bool:
        """Assign task using work order system"""
        
        if not self.work_order_manager:
            return False
        
        try:
            # Convert legacy task type to enhanced task type
            enhanced_task_type = convert_legacy_task(task_type)
            
            # Validate agricultural workflow before creating work order
            valid_plots = self._validate_agricultural_workflow(task_type, plot_coords)
            if not valid_plots:
                print(f"Cannot create {task_type} work order: No plots meet agricultural requirements")
                return False
            
            # Update plot_coords to only include valid plots
            plot_coords = valid_plots
            print(f"Work order validation: {len(valid_plots)} plots ready for {task_type}")
            
            # Determine priority based on task type and context
            priority = self._determine_task_priority(enhanced_task_type, len(plot_coords))
            
            # Create work order
            work_order = self.work_order_manager.create_work_order(
                task_type=enhanced_task_type,
                plots=plot_coords,
                priority=priority,
                notes=f"Player-assigned {task_type} task",
                auto_assign=(employee_id is None)  # Auto-assign if no specific employee
            )
            
            # Mark tiles with task assignments for visual overlay
            if work_order and self.grid_manager:
                for plot_coord in plot_coords:
                    x, y = plot_coord
                    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                        tile = self.grid_manager.grid[y][x]
                        tile.task_assignment = task_type  # Mark tile for visual overlay
                        print(f"Marked tile ({x}, {y}) with {task_type} task assignment")
            
            # Manually assign to specific employee if requested
            if work_order and employee_id:
                success = self.work_order_manager.assign_work_order(work_order.id, employee_id)
                if not success:
                    print(f"Failed to assign work order to employee {employee_id}")
            
            return work_order is not None
            
        except Exception as e:
            print(f"Error creating work order: {e}")
            return False
    
    def _assign_via_legacy_system(self, task_type: str, selected_tiles: List, employee_id: str = None) -> bool:
        """Assign task using legacy system"""
        if not self.employee_manager:
            return False
        
        try:
            # Use existing employee manager assignment
            if employee_id:
                return self.employee_manager.assign_task_to_employee(employee_id, task_type, selected_tiles)
            else:
                return self.employee_manager.assign_task_to_selection(task_type)
                
        except Exception as e:
            print(f"Error in legacy task assignment: {e}")
            return False
    
    def _determine_task_priority(self, task_type: TaskType, plot_count: int) -> TaskPriority:
        """Determine appropriate priority for task"""
        # Priority mapping based on task urgency
        priority_map = {
            TaskType.HARVESTING: TaskPriority.HIGH,      # Time-sensitive
            TaskType.PEST_CONTROL: TaskPriority.HIGH,   # Prevent damage
            TaskType.WATERING: TaskPriority.NORMAL,     # Regular maintenance
            TaskType.FERTILIZING: TaskPriority.NORMAL,  # Soil improvement
            TaskType.PLANTING: TaskPriority.NORMAL,     # Seasonal activity
            TaskType.TILLING: TaskPriority.LOW,         # Preparation work
            TaskType.PROCESSING: TaskPriority.LOW,      # Post-harvest
            TaskType.STORING: TaskPriority.LOW          # Organization
        }
        
        base_priority = priority_map.get(task_type, TaskPriority.NORMAL)
        
        # Escalate priority for large operations
        if plot_count > 20:
            # Large operations get higher priority
            if base_priority == TaskPriority.LOW:
                return TaskPriority.NORMAL
            elif base_priority == TaskPriority.NORMAL:
                return TaskPriority.HIGH
        
        return base_priority
    
    def _validate_agricultural_workflow(self, task_type: str, plot_coords: List) -> List:
        """Validate that plots meet agricultural workflow requirements and return valid plots"""
        if not self.grid_manager:
            return plot_coords  # No validation possible without grid manager
        
        valid_plots = []
        invalid_count = 0
        
        for plot_coord in plot_coords:
            x, y = plot_coord
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                tile = self.grid_manager.grid[y][x]
                is_valid = False
                
                # Agricultural workflow validation
                if task_type == 'till':
                    # Tilling requires soil terrain (not already tilled)
                    is_valid = tile.can_till()
                    if not is_valid:
                        print(f"Cannot till plot ({x}, {y}): {tile.terrain_type}, has crop: {tile.current_crop is not None}")
                        
                elif task_type == 'plant':
                    # Planting requires tilled soil
                    is_valid = tile.can_plant()
                    if not is_valid:
                        print(f"Cannot plant on plot ({x}, {y}): terrain is {tile.terrain_type}, needs to be tilled first")
                        
                elif task_type == 'harvest':
                    # Harvesting requires mature crops
                    is_valid = tile.can_harvest()
                    if not is_valid:
                        if tile.current_crop:
                            print(f"Cannot harvest plot ({x}, {y}): {tile.current_crop} not ready (stage {tile.growth_stage})")
                        else:
                            print(f"Cannot harvest plot ({x}, {y}): no crop planted")
                        
                else:
                    # For other task types, assume valid for now
                    is_valid = True
                
                if is_valid:
                    valid_plots.append(plot_coord)
                else:
                    invalid_count += 1
        
        if invalid_count > 0:
            print(f"Agricultural workflow validation: {invalid_count} plots invalid for {task_type} task")
            
            # Provide helpful feedback to player
            if task_type == 'plant' and invalid_count > 0:
                print("Tip: Plants need tilled soil. Till the plots first (T key), then plant (P key)")
            elif task_type == 'harvest' and invalid_count > 0:
                print("Tip: Only mature crops can be harvested. Wait for crops to grow or select different plots")
        
        return valid_plots
    
    def get_active_work_orders(self) -> List[Dict]:
        """Get active work orders for UI display"""
        if not ENABLE_WORK_ORDERS or not self.work_order_manager:
            return []
        
        work_orders = []
        for order in self.work_order_manager.active_orders:
            # Get assigned employees in the format expected by UI (support multi-employee)
            assigned_employees = []
            
            # Check for multi-employee assignments first
            if hasattr(order, 'assigned_employee_ids') and order.assigned_employee_ids:
                for emp_id in order.assigned_employee_ids:
                    employee_name = self._get_employee_name(emp_id)
                    if employee_name:
                        # Get individual employee progress if available
                        emp_progress = order.employee_assignments.get(emp_id, {}).get('progress', order.progress)
                        assigned_employees.append({
                            'name': employee_name,
                            'progress': emp_progress
                        })
            # Fall back to single employee assignment
            elif order.assigned_employee_id:
                employee_name = self._get_employee_name(order.assigned_employee_id)
                if employee_name:
                    assigned_employees.append({
                        'name': employee_name,
                        'progress': order.progress
                    })
            
            work_orders.append({
                'id': order.id,
                'task_type': order.task_type.value,
                'plot_count': len(order.assigned_plots),
                'priority': order.priority.name,
                'status': 'Assigned' if (order.assigned_employee_id or (hasattr(order, 'assigned_employee_ids') and order.assigned_employee_ids)) else 'Unassigned',
                'assigned_employees': assigned_employees,
                'deadline': self._format_deadline(order.deadline),
                'progress': order.progress,
                'estimated_duration': order.estimated_duration
            })
        
        return work_orders
    
    def get_employee_workloads(self) -> Dict[str, int]:
        """Get current workload for each employee"""
        workloads = {}
        
        if ENABLE_WORK_ORDERS and self.work_order_manager:
            # Count work orders per employee
            for employee_id, order_ids in self.work_order_manager.employee_assignments.items():
                workloads[employee_id] = len(order_ids)
        else:
            # Legacy system - get task counts from employee manager
            if self.employee_manager:
                for emp_id, employee in self.employee_manager.employees.items():
                    workloads[emp_id] = len(getattr(employee, 'assigned_tasks', []))
        
        return workloads
    
    def _get_employee_name(self, employee_id: str) -> str:
        """Get employee name from ID"""
        if not employee_id:
            return "Unassigned"
        
        if self.employee_manager and employee_id in self.employee_manager.employees:
            return self.employee_manager.employees[employee_id].name
        
        return f"Employee {employee_id}"
    
    def _format_deadline(self, deadline) -> str:
        """Format deadline for display"""
        if not deadline:
            return "No deadline"
        
        # Calculate time remaining (simplified)
        from datetime import datetime
        current_time = datetime.now()
        
        if deadline < current_time:
            return "OVERDUE"
        
        time_diff = deadline - current_time
        hours = time_diff.total_seconds() / 3600
        
        if hours < 1:
            return f"{int(time_diff.total_seconds() / 60)} minutes"
        elif hours < 24:
            return f"{int(hours)} hours"
        else:
            return f"{int(hours / 24)} days"
    
    # Event handlers
    def _handle_legacy_task_request(self, event_data):
        """Handle legacy task assignment requests"""
        task_type = event_data.get('task_type')
        tiles = event_data.get('tiles', [])
        employee_id = event_data.get('employee_id')
        
        success = self.assign_task(task_type, tiles, employee_id)
        
        if success:
            self.event_system.emit('task_assigned_successfully', {
                'task_type': task_type,
                'tile_count': len(tiles),
                'employee_id': employee_id
            })
        else:
            self.event_system.emit('task_assignment_failed', {
                'task_type': task_type,
                'reason': 'assignment_failed'
            })
    
    def _handle_selection_assignment(self, event_data):
        """Handle assignment to selected tiles"""
        try:
            task_type = event_data.get('task_type')
            
            if self.grid_manager and hasattr(self.grid_manager, 'selected_tiles'):
                success = self.assign_task(task_type, self.grid_manager.selected_tiles)
                
                if success:
                    print(f"Successfully assigned {task_type} to {len(self.grid_manager.selected_tiles)} selected tiles")
                else:
                    print(f"Failed to assign {task_type} to selected tiles")
            else:
                print("No grid manager or selected_tiles available")
        except Exception as e:
            print(f"Exception in _handle_selection_assignment: {e}")
            import traceback
            traceback.print_exc()
    
    def _handle_employee_request(self, event_data):
        """Handle requests for available employees"""
        callback = event_data.get('callback')
        
        if not callback or not self.employee_manager:
            return
        
        # Get available employees with specialization data
        available_employees = []
        for emp_id, employee in self.employee_manager.employees.items():
            if self._is_employee_available(employee):
                emp_data = {
                    'id': emp_id,
                    'name': employee.name,
                    'task_efficiency': {}
                }
                
                # Add specialization data if available
                if ENABLE_EMPLOYEE_SPECIALIZATIONS and hasattr(employee, 'get_task_efficiency'):
                    for task_type in TaskType:
                        emp_data['task_efficiency'][task_type.value] = employee.get_task_efficiency(task_type.value)
                
                available_employees.append(emp_data)
        
        # Call the callback with employee data
        callback(available_employees)
    
    def _is_employee_available(self, employee) -> bool:
        """Check if employee is available for new work assignments"""
        # Simple availability check - can be enhanced
        if hasattr(employee, 'assigned_tasks'):
            return len(employee.assigned_tasks) < 3  # Max 3 concurrent tasks
        return True
    
    def _execute_work_order_assignment(self, work_order_id: str, employee_id: str, task_type: str):
        """Convert work order assignment to actual employee task execution"""
        if not self.work_order_manager or not self.employee_manager:
            print(f"Cannot execute work order: Missing managers")
            return
        
        # Get the work order details
        work_order = self.work_order_manager.get_work_order(work_order_id)
        if not work_order:
            print(f"Cannot execute: Work order {work_order_id} not found")
            return
        
        # Get employee's allocated plots (if distributed) or all plots (if single employee)
        employee_plots = work_order.assigned_plots  # Default to all plots
        
        # Check if this employee has specific allocated plots from distribution
        if hasattr(work_order, 'employee_assignments') and employee_id in work_order.employee_assignments:
            allocated_plots = work_order.employee_assignments[employee_id].get('allocated_plots')
            if allocated_plots:
                employee_plots = allocated_plots
                print(f"Using distributed plots for {employee_id}: {len(allocated_plots)} plots")
            else:
                print(f"No allocated plots found for {employee_id}, using all plots")
        
        # Convert plot coordinates to tile objects for employee manager
        tiles = []
        if self.grid_manager:
            for plot_coord in employee_plots:
                x, y = plot_coord
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    tile = self.grid_manager.get_tile(x, y)
                    if tile:
                        tiles.append(tile)
        
        if not tiles:
            print(f"Cannot execute: No valid tiles found for work order {work_order_id}")
            return
        
        # Assign the actual task to the employee using the legacy task system
        plot_coords_str = ", ".join([f"({tile.x},{tile.y})" for tile in tiles])
        print(f"Executing work order: Assigning {task_type} task to employee {employee_id} for {len(tiles)} tiles: {plot_coords_str}")
        success = self.employee_manager.assign_task_to_employee(employee_id, task_type, tiles, work_order_id=work_order_id)
        
        if success:
            print(f"Work order {work_order_id} successfully converted to employee task")
            # Mark work order as started
            if hasattr(work_order, 'started_at') and not work_order.started_at:
                from datetime import datetime
                work_order.started_at = datetime.now()
        else:
            print(f"✗ Failed to assign {task_type} task to employee {employee_id}")
    
    def _handle_work_order_assignment(self, event_data):
        """Handle work order assignment events"""
        work_order_id = event_data.get('work_order_id')
        employee_id = event_data.get('employee_id')
        task_type = event_data.get('task_type')
        
        print(f"Work order {work_order_id} assigned to employee {employee_id} for {task_type}")
        
        # Convert work order assignment to actual employee task
        self._execute_work_order_assignment(work_order_id, employee_id, task_type)
        
        # Emit notification for UI update
        self.event_system.emit('work_assignment_updated', {
            'work_order_id': work_order_id,
            'employee_id': employee_id
        })
    
    def _handle_grid_analysis_request(self, event_data):
        """Handle requests for grid analysis"""
        callback = event_data.get('callback')
        
        if callback and self.grid_manager:
            # Call the analysis function with grid manager
            result = callback(self.grid_manager)
            
            if result:
                print(f"Grid analysis completed, generated {result} work orders")
    
    def _handle_work_orders_ui_request(self, event_data):
        """Handle UI requests for work order data"""
        callback = event_data.get('callback')
        
        if callback:
            work_orders = self.get_active_work_orders()
            print(f"UI requested work orders - found {len(work_orders)} active orders")
            for order in work_orders:
                print(f"  - {order['task_type']}: {order['plot_count']} plots, {order['assigned_to']}")
            callback(work_orders)
    
    def _handle_employee_assignments_ui_request(self, event_data):
        """Handle UI requests for employee assignment data"""
        callback = event_data.get('callback')
        
        if callback and self.employee_manager:
            # Get employee assignment data
            assignments = []
            workloads = self.get_employee_workloads()
            
            for emp_id, employee in self.employee_manager.employees.items():
                # Get current task safely
                current_task = getattr(employee, 'current_task', None)
                if current_task and hasattr(current_task, 'get'):
                    task_type = current_task.get('type', 'Idle')
                else:
                    task_type = 'Idle'
                
                emp_data = {
                    'id': emp_id,
                    'name': employee.name,
                    'current_task': task_type,
                    'workload': workloads.get(emp_id, 0)
                }
                
                # Add specialization data if available
                if ENABLE_EMPLOYEE_SPECIALIZATIONS and hasattr(employee, 'get_specialization_summary'):
                    summary = employee.get_specialization_summary()
                    emp_data['role'] = summary['role']
                    emp_data['efficiency'] = 1.0  # Can be enhanced with current task efficiency
                else:
                    emp_data['role'] = 'General Worker'
                    emp_data['efficiency'] = 1.0
                
                assignments.append(emp_data)
            
            callback(assignments)
    
    def _handle_work_order_cancelled(self, event_data):
        """Handle work order cancellation - clear visual tile assignments"""
        work_order_id = event_data.get('work_order_id')
        enhanced_task_type = event_data.get('task_type', '')
        reason = event_data.get('reason', 'Cancelled')
        
        # Convert enhanced task type back to legacy format for tile assignment comparison
        from .task_models import TaskType, convert_to_legacy_task
        try:
            # Parse the enhanced task type string back to enum
            task_enum = TaskType(enhanced_task_type) if enhanced_task_type else TaskType.TILLING
            legacy_task_type = convert_to_legacy_task(task_enum)
        except ValueError:
            # Fallback if task type parsing fails
            legacy_task_type = enhanced_task_type.lower()
        
        print(f"Clearing tile assignments for cancelled work order {work_order_id} (enhanced: {enhanced_task_type}, legacy: {legacy_task_type})")
        
        # Clear task assignments from tiles for visual overlay
        if self.grid_manager:
            cleared_count = 0
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    tile = self.grid_manager.grid[y][x]
                    # Clear task assignment if it matches the cancelled task type (legacy format)
                    if (hasattr(tile, 'task_assignment') and 
                        tile.task_assignment and 
                        tile.task_assignment == legacy_task_type):
                        tile.task_assignment = None
                        cleared_count += 1
                        
            print(f"Cleared {cleared_count} tile assignments for cancelled {legacy_task_type} work order")
    
    def cleanup(self):
        """Clean up task system integration"""
        if self.work_order_manager:
            self.work_order_manager.cleanup()
        
        if self.dynamic_generator:
            self.dynamic_generator.cleanup()
        
        print("Task System Integration cleaned up")