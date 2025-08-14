"""
Work Order Management System - Phase 2B
Handles dynamic work order creation, prioritization, and assignment.
Transforms static task assignment into intelligent agricultural operations management.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from scripts.core.config import *
from scripts.tasks.task_models import WorkOrder, TaskType, TaskPriority, EmployeeRole


@dataclass
class WorkOrderMetrics:
    """Metrics for tracking work order performance"""
    total_created: int = 0
    total_completed: int = 0
    total_cancelled: int = 0
    average_completion_time: float = 0.0
    urgent_orders_missed: int = 0
    efficiency_rating: float = 1.0


class WorkOrderManager:
    """
    Advanced work order management system for agricultural operations
    Handles dynamic task creation, intelligent prioritization, and deadline management
    """
    
    def __init__(self, event_system, time_manager=None):
        """Initialize the work order management system"""
        self.event_system = event_system  # Event system for communication
        self.time_manager = time_manager  # Time manager for deadline calculations
        
        # Work order storage
        self.active_orders: List[WorkOrder] = []  # Currently active work orders
        self.completed_orders: List[WorkOrder] = []  # Completed work orders history
        self.cancelled_orders: List[WorkOrder] = []  # Cancelled work orders
        
        # Assignment tracking
        self.employee_assignments: Dict[str, List[str]] = {}  # employee_id -> [work_order_ids]
        self.plot_assignments: Dict[Tuple[int, int], str] = {}  # (x, y) -> work_order_id
        
        # Performance metrics
        self.metrics = WorkOrderMetrics()
        
        # Configuration
        self.max_active_orders = 50  # Maximum active work orders
        self.auto_cleanup_days = 7  # Auto-remove completed orders after N days
        
        # Subscribe to relevant events
        if self.event_system:
            self._setup_event_handlers()
        
        print("Work Order Management System initialized")
        print(f"  Max active orders: {self.max_active_orders}")
        print(f"  Auto cleanup: {self.auto_cleanup_days} days")
    
    def _setup_event_handlers(self):
        """Set up event handlers for work order management"""
        # Game time events for deadline management
        self.event_system.subscribe('day_passed', self._handle_day_passed)
        self.event_system.subscribe('time_updated', self._handle_time_update)
        
        # Task completion events
        self.event_system.subscribe('task_completed', self._handle_task_completed)
        self.event_system.subscribe('employee_task_finished', self._handle_employee_task_finished)
        self.event_system.subscribe('employee_task_completed', self._handle_employee_task_finished)
        
        # Agricultural events for automatic work order generation
        self.event_system.subscribe('crop_ready_for_harvest', self._handle_crop_ready)
        self.event_system.subscribe('weather_warning', self._handle_weather_warning)
        self.event_system.subscribe('pest_outbreak', self._handle_pest_outbreak)
        
        # Employee events
        self.event_system.subscribe('employee_hired', self._handle_employee_hired)
        self.event_system.subscribe('employee_fired', self._handle_employee_fired)
        
        # Multi-employee assignment events
        self.event_system.subscribe('multi_employee_work_order_assignment', self._handle_multi_employee_assignment)
    
    def create_work_order(self, 
                         task_type: TaskType, 
                         plots: List[Tuple[int, int]], 
                         priority: TaskPriority = TaskPriority.NORMAL,
                         deadline_hours: Optional[float] = None,
                         required_role: Optional[EmployeeRole] = None,
                         notes: str = "",
                         auto_assign: bool = True) -> Optional[WorkOrder]:
        """
        Create a new work order for agricultural operations
        
        Args:
            task_type: Type of agricultural task
            plots: List of (x, y) plot coordinates
            priority: Priority level for the work order
            deadline_hours: Hours until deadline (None = no deadline)
            required_role: Specific employee role required (None = any suitable)
            notes: Additional notes or context
            auto_assign: Whether to automatically assign to best employee
        
        Returns:
            WorkOrder object if created successfully, None if failed
        """
        if not ENABLE_WORK_ORDERS:
            print("Work orders disabled - falling back to legacy task assignment")
            return None
        
        # Check if we're at max capacity
        if len(self.active_orders) >= self.max_active_orders:
            print(f"Cannot create work order: Maximum active orders ({self.max_active_orders}) reached")
            return None
        
        # Check for plot conflicts
        conflicted_plots = []
        for plot in plots:
            if plot in self.plot_assignments:
                conflicted_plots.append(plot)
        
        if conflicted_plots:
            print(f"Warning: Plots {conflicted_plots} already have work orders assigned")
        
        # Calculate deadline
        deadline = None
        if deadline_hours and self.time_manager:
            current_time = getattr(self.time_manager, 'current_datetime', datetime.now())
            deadline = current_time + timedelta(hours=deadline_hours)
        
        # Create work order
        work_order = WorkOrder(
            task_type=task_type,
            assigned_plots=plots,
            priority=priority,
            deadline=deadline,
            notes=notes
        )
        
        # Estimate duration based on task type and plot count
        work_order.estimate_duration()
        
        # Add to active orders
        self.active_orders.append(work_order)
        self.metrics.total_created += 1
        
        # Assign plots to this work order
        for plot in plots:
            self.plot_assignments[plot] = work_order.id
        
        # Auto-assign to best employee if requested
        if auto_assign:
            assigned_employee = self._auto_assign_work_order(work_order)
            if assigned_employee:
                print(f"Work order auto-assigned to {assigned_employee}")
        
        # Emit event for UI updates
        self.event_system.emit('work_order_created', {
            'work_order_id': work_order.id,
            'task_type': task_type.value,
            'plot_count': len(plots),
            'priority': priority.value,
            'estimated_duration': work_order.estimated_duration
        })
        
        print(f"Created work order: {task_type.value} for {len(plots)} plots (Priority: {priority.name})")
        if deadline:
            print(f"  Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}")
        if notes:
            print(f"  Notes: {notes}")
        
        return work_order
    
    def _get_available_employees_direct(self, work_order: WorkOrder) -> List[Dict]:
        """
        Get available employees directly without going through event system
        This avoids recursion issues during event processing
        """
        if not hasattr(self, 'task_integration') or not self.task_integration.employee_manager:
            return []
        
        available_employees = []
        for emp_id, employee in self.task_integration.employee_manager.employees.items():
            if self.task_integration._is_employee_available(employee):
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
        
        return available_employees
    
    def _auto_assign_work_order(self, work_order: WorkOrder) -> Optional[str]:
        """
        Automatically assign work order to the best available employee
        Uses employee specializations to find optimal assignment
        """
        # Get available employees directly (bypass event system for synchronous access)
        available_employees = self._get_available_employees_direct(work_order)
        
        # Debug: Check what we received (can be removed in production)
        if available_employees:
            print(f"Auto-assigning work order to {available_employees[0].get('name', 'Unknown')}")
        
        if not available_employees:
            print(f"No available employees for work order {work_order.id}")
            return None
        
        # Score employees based on specialization and current workload
        employee_scores = []
        for employee in available_employees:
            score = self._calculate_employee_score(employee, work_order)
            employee_scores.append((employee, score))
        
        # Sort by score (highest first)
        employee_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Assign to best employee
        best_employee = employee_scores[0][0]
        self.assign_work_order(work_order.id, best_employee['id'])
        
        return best_employee['name']
    
    def _calculate_employee_score(self, employee: Dict, work_order: WorkOrder) -> float:
        """Calculate suitability score for employee-work order pairing"""
        base_score = 1.0
        
        # Factor 1: Task efficiency (from specialization)
        task_efficiency = employee.get('task_efficiency', {}).get(work_order.task_type.value, 1.0)
        efficiency_score = task_efficiency * 2.0  # Weight efficiency heavily
        
        # Factor 2: Current workload (fewer assignments = higher score)
        current_assignments = len(self.employee_assignments.get(employee['id'], []))
        workload_score = max(0.1, 2.0 - (current_assignments * 0.5))
        
        # Factor 3: Priority match (urgent tasks get best employees)
        priority_multiplier = {
            TaskPriority.CRITICAL: 2.0,
            TaskPriority.HIGH: 1.5,
            TaskPriority.NORMAL: 1.0,
            TaskPriority.LOW: 0.8,
            TaskPriority.MINIMAL: 0.6
        }.get(work_order.priority, 1.0)
        
        # Calculate final score
        final_score = (efficiency_score + workload_score) * priority_multiplier
        
        return final_score
    
    def assign_work_order(self, work_order_id: str, employee_id: str) -> bool:
        """Assign a work order to a specific employee"""
        # Find work order
        work_order = self.get_work_order(work_order_id)
        if not work_order:
            print(f"Work order {work_order_id} not found")
            return False
        
        if work_order.is_assigned:
            print(f"Work order {work_order_id} already assigned to {work_order.assigned_employee_id}")
            return False
        
        # Assign work order
        work_order.assigned_employee_id = employee_id
        work_order.assigned_at = datetime.now()
        
        # Track assignment
        if employee_id not in self.employee_assignments:
            self.employee_assignments[employee_id] = []
        self.employee_assignments[employee_id].append(work_order_id)
        
        # Emit assignment event
        self.event_system.emit('work_order_assigned', {
            'work_order_id': work_order_id,
            'employee_id': employee_id,
            'task_type': work_order.task_type.value,
            'plot_count': len(work_order.assigned_plots),
            'priority': work_order.priority.value
        })
        
        print(f"Assigned work order {work_order_id} to employee {employee_id}")
        return True
    
    def assign_employee_to_work_order(self, work_order_id: str, employee_id: str, employee_skills: Dict = None) -> bool:
        """Assign an additional employee to a work order (multi-employee support)"""
        work_order = self.get_work_order(work_order_id)
        if not work_order:
            print(f"Work order {work_order_id} not found for multi-employee assignment")
            return False
        
        # Use the new multi-employee assignment method from WorkOrder
        success = work_order.assign_employee(employee_id)
        if not success:
            print(f"Employee {employee_id} already assigned to work order {work_order_id}")
            return False
        
        # Update tracking
        if employee_id not in self.employee_assignments:
            self.employee_assignments[employee_id] = []
        if work_order_id not in self.employee_assignments[employee_id]:
            self.employee_assignments[employee_id].append(work_order_id)
        
        # Distribute plots based on skills if multiple employees
        if len(work_order.assigned_employee_ids) > 1 and employee_skills:
            skill_levels = {emp_id: employee_skills.get(emp_id, 1.0) 
                           for emp_id in work_order.assigned_employee_ids}
            work_order.distribute_plots_by_skill(skill_levels)
            
        # Emit multi-employee assignment event
        self.event_system.emit('work_order_multi_assigned', {
            'work_order_id': work_order_id,
            'employee_id': employee_id,
            'total_employees': len(work_order.assigned_employee_ids),
            'task_type': work_order.task_type.value
        })
        
        print(f"Added employee {employee_id} to work order {work_order_id} ({len(work_order.assigned_employee_ids)} total employees)")
        return True
    
    def remove_employee_from_work_order(self, work_order_id: str, employee_id: str) -> bool:
        """Remove an employee from a work order"""
        work_order = self.get_work_order(work_order_id)
        if not work_order:
            return False
        
        success = work_order.remove_employee(employee_id)
        if not success:
            return False
        
        # Update tracking
        if employee_id in self.employee_assignments:
            if work_order_id in self.employee_assignments[employee_id]:
                self.employee_assignments[employee_id].remove(work_order_id)
        
        # Redistribute plots among remaining employees
        if len(work_order.assigned_employee_ids) > 0:
            # Would need employee skill data for redistribution
            # For now, just emit event for external handling
            pass
        
        print(f"Removed employee {employee_id} from work order {work_order_id}")
        return True
    
    def complete_work_order(self, work_order_id: str) -> bool:
        """Mark a work order as completed"""
        work_order = self.get_work_order(work_order_id)
        if not work_order:
            return False
        
        # Mark as completed
        work_order.completed_at = datetime.now()
        work_order.progress = 1.0
        
        # Calculate completion time
        if work_order.started_at:
            completion_time = (work_order.completed_at - work_order.started_at).total_seconds() / 3600.0
            self._update_completion_metrics(completion_time)
        
        # Move to completed orders
        if work_order in self.active_orders:
            self.active_orders.remove(work_order)
        self.completed_orders.append(work_order)
        self.metrics.total_completed += 1
        
        # Free up assigned plots
        for plot in work_order.assigned_plots:
            if plot in self.plot_assignments:
                del self.plot_assignments[plot]
        
        # Remove from all employee assignments (support multi-employee work orders)
        employees_to_clean = set()
        
        # Add primary assigned employee
        if work_order.assigned_employee_id:
            employees_to_clean.add(work_order.assigned_employee_id)
        
        # Add all multi-assigned employees
        if hasattr(work_order, 'assigned_employee_ids'):
            employees_to_clean.update(work_order.assigned_employee_ids)
        
        # Clean up assignments for all employees
        for employee_id in employees_to_clean:
            employee_orders = self.employee_assignments.get(employee_id, [])
            if work_order_id in employee_orders:
                employee_orders.remove(work_order_id)
                print(f"Removed work order {work_order_id} from employee {employee_id} assignments")
        
        # Emit completion event
        self.event_system.emit('work_order_completed', {
            'work_order_id': work_order_id,
            'task_type': work_order.task_type.value,
            'completion_time': completion_time if work_order.started_at else None,
            'efficiency_rating': self._calculate_order_efficiency(work_order)
        })
        
        print(f"Work order {work_order_id} completed")
        return True
    
    def cancel_work_order(self, work_order_id: str, reason: str = "") -> bool:
        """Cancel an active work order"""
        work_order = self.get_work_order(work_order_id)
        if not work_order:
            return False
        
        # Move to cancelled orders
        if work_order in self.active_orders:
            self.active_orders.remove(work_order)
        self.cancelled_orders.append(work_order)
        self.metrics.total_cancelled += 1
        
        # Free up resources
        for plot in work_order.assigned_plots:
            if plot in self.plot_assignments:
                del self.plot_assignments[plot]
        
        if work_order.assigned_employee_id:
            employee_orders = self.employee_assignments.get(work_order.assigned_employee_id, [])
            if work_order_id in employee_orders:
                employee_orders.remove(work_order_id)
        
        # Emit cancellation event
        self.event_system.emit('work_order_cancelled', {
            'work_order_id': work_order_id,
            'reason': reason,
            'task_type': work_order.task_type.value
        })
        
        print(f"Work order {work_order_id} cancelled: {reason}")
        return True
    
    def get_work_order(self, work_order_id: str) -> Optional[WorkOrder]:
        """Get work order by ID"""
        for order in self.active_orders:
            if order.id == work_order_id:
                return order
        return None
    
    def get_employee_work_orders(self, employee_id: str) -> List[WorkOrder]:
        """Get all active work orders for an employee"""
        order_ids = self.employee_assignments.get(employee_id, [])
        return [self.get_work_order(order_id) for order_id in order_ids if self.get_work_order(order_id)]
    
    def get_urgent_work_orders(self) -> List[WorkOrder]:
        """Get work orders that need immediate attention"""
        urgent_orders = []
        current_time = datetime.now()
        
        for order in self.active_orders:
            # Check deadline urgency
            if order.deadline and order.deadline <= current_time + timedelta(hours=2):
                urgent_orders.append(order)
            # Check critical priority
            elif order.priority == TaskPriority.CRITICAL:
                urgent_orders.append(order)
        
        # Sort by urgency
        urgent_orders.sort(key=lambda x: (x.priority.value, x.deadline or datetime.max))
        return urgent_orders
    
    def _update_completion_metrics(self, completion_time: float):
        """Update performance metrics with completion data"""
        if self.metrics.total_completed == 0:
            self.metrics.average_completion_time = completion_time
        else:
            # Running average
            total_time = self.metrics.average_completion_time * (self.metrics.total_completed - 1)
            self.metrics.average_completion_time = (total_time + completion_time) / self.metrics.total_completed
    
    def _calculate_order_efficiency(self, work_order: WorkOrder) -> float:
        """Calculate efficiency rating for completed work order"""
        if not work_order.started_at or not work_order.completed_at:
            return 1.0
        
        actual_time = (work_order.completed_at - work_order.started_at).total_seconds() / 3600.0
        estimated_time = work_order.estimated_duration
        
        if estimated_time <= 0:
            return 1.0
        
        # Efficiency = estimated / actual (higher is better)
        efficiency = estimated_time / actual_time
        return max(0.1, min(2.0, efficiency))  # Clamp between 0.1 and 2.0
    
    # Event handlers
    def _handle_day_passed(self, event_data):
        """Handle day passed event for deadline management"""
        current_time = datetime.now()
        
        # Check for overdue work orders
        overdue_orders = []
        for order in self.active_orders:
            if order.deadline and order.deadline < current_time:
                overdue_orders.append(order)
        
        if overdue_orders:
            print(f"Warning: {len(overdue_orders)} work orders are overdue!")
            for order in overdue_orders:
                # Escalate priority
                if order.priority != TaskPriority.CRITICAL:
                    old_priority = order.priority
                    order.priority = TaskPriority.CRITICAL
                    print(f"  Escalated work order {order.id} from {old_priority.name} to CRITICAL")
        
        # Auto-cleanup old completed orders
        cutoff_date = current_time - timedelta(days=self.auto_cleanup_days)
        old_completed = [order for order in self.completed_orders if order.completed_at < cutoff_date]
        for order in old_completed:
            self.completed_orders.remove(order)
        
        if old_completed:
            print(f"Cleaned up {len(old_completed)} old completed work orders")
    
    def _handle_time_update(self, event_data):
        """Handle time updates for work order progress tracking"""
        # Update work order progress based on employee task completion
        # This will be implemented when we integrate with the employee task system
        pass
    
    def _handle_task_completed(self, event_data):
        """Handle individual task completion"""
        # Find work orders that include this task
        # This will be expanded as we integrate with the task system
        pass
    
    def _handle_employee_task_finished(self, event_data):
        """Handle employee finishing a task"""
        work_order_id = event_data.get('work_order_id')
        employee_id = event_data.get('employee_id')
        completed_tiles = event_data.get('completed_tiles', 0)
        
        if not work_order_id:
            return  # Not a work order task
        
        work_order = self.get_work_order(work_order_id)
        if not work_order:
            print(f"Work order {work_order_id} not found for completion")
            return
        
        print(f"Employee {employee_id} completed their portion of work order {work_order_id} ({completed_tiles} tiles)")
        
        # Check if ALL plots in the work order are actually completed by checking the grid
        if self._is_work_order_fully_completed(work_order):
            print(f"All plots completed - marking work order {work_order_id} as complete")
            if self.complete_work_order(work_order_id):
                print(f"Work order {work_order_id} fully completed")
                
                # Emit completion event for UI refresh
                self.event_system.emit('work_order_completed', {
                    'work_order_id': work_order_id,
                    'employee_id': employee_id
                })
            else:
                print(f"✗ Failed to complete work order {work_order_id}")
        else:
            print(f"Work order {work_order_id} still has uncompleted plots - keeping active")
    
    def _handle_crop_ready(self, event_data):
        """Handle crops becoming ready for harvest - auto-generate work orders"""
        if not ENABLE_DYNAMIC_TASK_GENERATION:
            return
        
        # This will auto-create harvest work orders when crops are ready
        # Implementation will come in dynamic generation phase
        pass
    
    def _handle_weather_warning(self, event_data):
        """Handle weather warnings - create urgent work orders"""
        # Create urgent work orders for weather-sensitive tasks
        # Implementation will come in weather integration phase
        pass
    
    def _handle_pest_outbreak(self, event_data):
        """Handle pest outbreaks - create critical work orders"""
        # Create critical priority pest control work orders
        # Implementation will come in pest management integration
        pass
    
    def _handle_employee_hired(self, event_data):
        """Handle new employee being hired"""
        employee_id = event_data.get('employee_id')
        if employee_id:
            self.employee_assignments[employee_id] = []
            print(f"Initialized work order tracking for new employee {employee_id}")
    
    def _handle_employee_fired(self, event_data):
        """Handle employee being fired"""
        employee_id = event_data.get('employee_id')
        if employee_id in self.employee_assignments:
            # Reassign their work orders
            orphaned_orders = self.employee_assignments[employee_id].copy()
            del self.employee_assignments[employee_id]
            
            for order_id in orphaned_orders:
                order = self.get_work_order(order_id)
                if order:
                    order.assigned_employee_id = None
                    order.assigned_at = None
                    print(f"Work order {order_id} needs reassignment (employee fired)")
    
    def _handle_multi_employee_assignment(self, event_data):
        """Handle multi-employee work order assignment events"""
        work_order_id = event_data.get('work_order_id')
        employee_id = event_data.get('employee_id')
        action = event_data.get('action', 'assign')
        
        if not work_order_id or not employee_id:
            print("Invalid multi-employee assignment event data")
            return
        
        if action == 'assign':
            # Get employee skill data for plot distribution
            employee_skills = self._get_employee_skills_for_distribution(work_order_id)
            success = self.assign_employee_to_work_order(work_order_id, employee_id, employee_skills)
            
            if success:
                # Emit work order assignment for task integration
                work_order = self.get_work_order(work_order_id)
                if work_order:
                    self.event_system.emit('work_order_assigned', {
                        'work_order_id': work_order_id,
                        'employee_id': employee_id,
                        'task_type': work_order.task_type.value
                    })
        elif action == 'remove':
            self.remove_employee_from_work_order(work_order_id, employee_id)
    
    def _get_employee_skills_for_distribution(self, work_order_id: str) -> Dict[str, float]:
        """Get employee skill levels for plot distribution"""
        work_order = self.get_work_order(work_order_id)
        if not work_order:
            return {}
        
        # Request skill data from employee system
        # For now, return default values - this would be enhanced with actual skill data
        skill_levels = {}
        for emp_id in work_order.assigned_employee_ids:
            # Default skill level - would be replaced with actual skill query
            skill_levels[emp_id] = 1.0
        
        return skill_levels
    
    def _is_work_order_fully_completed(self, work_order: WorkOrder) -> bool:
        """Check if all plots in a work order have been completed"""
        if not work_order or not work_order.assigned_plots:
            return True  # No plots means complete
        
        # Get grid manager to check actual plot status
        grid_manager = None
        if hasattr(self, 'task_integration') and self.task_integration:
            grid_manager = self.task_integration.grid_manager
        
        if not grid_manager:
            print(f"Cannot verify work order completion: No grid manager available")
            return False  # Cannot verify, keep work order active
        
        completed_plots = 0
        total_plots = len(work_order.assigned_plots)
        
        for plot_coord in work_order.assigned_plots:
            x, y = plot_coord
            if 0 <= x < 16 and 0 <= y < 16:  # GRID_WIDTH/HEIGHT validation
                tile = grid_manager.get_tile(x, y)
                if tile and self._is_plot_work_completed(tile, work_order.task_type.value):
                    completed_plots += 1
        
        print(f"Work order completion check: {completed_plots}/{total_plots} plots completed")
        return completed_plots == total_plots
    
    def _is_plot_work_completed(self, tile, task_type: str) -> bool:
        """Check if a specific plot has the required work completed"""
        try:
            # Convert enhanced task type to legacy for checking
            from .task_models import TaskType, convert_to_legacy_task
            if task_type in [tt.value for tt in TaskType]:
                # Convert enhanced task type back to legacy
                task_enum = TaskType(task_type)
                legacy_task = convert_to_legacy_task(task_enum)
            else:
                legacy_task = task_type.lower()
            
            # Use the same logic as employee collision detection
            if legacy_task == 'till' or legacy_task == 'tilling':
                return tile.terrain_type == 'tilled' or tile.current_crop is not None
            elif legacy_task == 'plant' or legacy_task == 'planting':
                return tile.current_crop is not None
            elif legacy_task == 'harvest' or legacy_task == 'harvesting':
                return tile.current_crop is None or tile.growth_stage < 4
            else:
                return False  # Unknown task type
                
        except Exception as e:
            print(f"Error checking plot completion: {e}")
            return False
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary for UI display"""
        urgent_orders = self.get_urgent_work_orders()
        
        return {
            'active_orders': len(self.active_orders),
            'completed_orders': len(self.completed_orders),
            'urgent_orders': len(urgent_orders),
            'total_created': self.metrics.total_created,
            'completion_rate': self.metrics.total_completed / max(1, self.metrics.total_created),
            'average_completion_time': self.metrics.average_completion_time,
            'efficiency_rating': self.metrics.efficiency_rating,
            'next_urgent': urgent_orders[0] if urgent_orders else None
        }
    
    def cleanup(self):
        """Clean up work order manager"""
        if self.event_system:
            # Unsubscribe from all events
            self.event_system.unsubscribe('day_passed', self._handle_day_passed)
            self.event_system.unsubscribe('time_updated', self._handle_time_update)
            # ... other unsubscribes
        
        print("Work Order Management System cleaned up")