"""
Enhanced Task Assignment Modal
Displays the new task assignment interface while maintaining compatibility with existing system.
Initially shows current task data in new format without changing behavior.
"""

import pygame
import pygame_gui
from typing import Dict, List, Optional, Any
from scripts.core.config import *
from scripts.tasks.task_models import TaskType, TaskPriority, EmployeeRole, EmployeeSpecialization


class TaskAssignmentModal:
    """
    Enhanced task assignment modal interface
    Displays current employee and task data in the new enhanced format
    """
    
    def __init__(self, gui_manager, event_system, screen_width: int, screen_height: int):
        """Initialize the task assignment modal"""
        self.gui_manager = gui_manager  # pygame_gui manager for UI elements
        self.event_system = event_system  # Event system for communication
        self.screen_width = screen_width  # Screen width for positioning
        self.screen_height = screen_height  # Screen height for positioning
        
        # Modal state
        self.is_visible = False  # Whether modal is currently shown
        self.modal_elements = []  # List of UI elements to manage
        
        # Data from existing system
        self.current_employees = []  # List of current employees from existing system
        self.current_tasks = []  # List of current tasks from existing system
        
        # Enhanced data (will be populated as we enable features)
        self.employee_specializations = {}  # Dict of employee_id -> EmployeeSpecialization
        self.work_orders = []  # List of WorkOrder objects
        
        # UI dimensions and positioning
        self.modal_width = 1000  # Wide modal to show task grid
        self.modal_height = 600  # Tall enough for employee list and task grid
        self.modal_x = (screen_width - self.modal_width) // 2  # Center horizontally
        self.modal_y = (screen_height - self.modal_height) // 2  # Center vertically
        
        # Task type mapping for display
        self.task_display_names = {
            TaskType.TILLING: "Tilling",
            TaskType.FERTILIZING: "Fertilizing", 
            TaskType.PLANTING: "Planting",
            TaskType.WATERING: "Watering",
            TaskType.CULTIVATING: "Cultivating",
            TaskType.PEST_CONTROL: "Pest Control",
            TaskType.HARVESTING: "Harvesting",
            TaskType.PROCESSING: "Processing",
            TaskType.STORING: "Storing"
        }
        
        # Subscribe to events for data updates
        self.event_system.subscribe('employee_count_update', self._handle_employee_update)
        self.event_system.subscribe('task_assignment_updated', self._handle_task_update)
        self.event_system.subscribe('show_task_assignment_modal', self._handle_show_modal)
        self.event_system.subscribe('hide_task_assignment_modal', self._handle_hide_modal)
    
    def _create_modal_elements(self):
        """Create all UI elements for the modal"""
        # Clear existing elements
        self._cleanup_elements()
        
        # Main modal background panel
        self.background_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(self.modal_x, self.modal_y, self.modal_width, self.modal_height),
            starting_height=10,  # High z-order for modal
            manager=self.gui_manager
        )
        self.modal_elements.append(self.background_panel)
        
        # Modal title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 20, self.modal_width - 40, 40),
            text="Task Assignment - Enhanced System",
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(self.title_label)
        
        # Close button (top-right)
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.modal_width - 80, 20, 60, 30),
            text="X",
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(self.close_button)
        
        # Instructions text
        instructions = ("Click employee names to select. Set task priorities (1=highest, 5=lowest). "
                       "Feature flags currently disabled - showing current system data.")
        self.instructions_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 70, self.modal_width - 40, 40),
            text=instructions,
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(self.instructions_label)
        
        # Create task assignment grid
        self._create_task_grid()
        
        # Create control buttons at bottom
        self._create_control_buttons()
    
    def _create_task_grid(self):
        """Create the main task assignment grid"""
        grid_start_y = 120  # Start below instructions
        grid_height = 350   # Height for the grid area
        
        # Column headers (task types)
        task_types = list(self.task_display_names.keys())
        col_width = (self.modal_width - 200) // len(task_types)  # Leave space for employee names
        header_y = grid_start_y
        
        # Employee name column header
        employee_header = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, header_y, 150, 30),
            text="Employee",
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(employee_header)
        
        # Task type column headers
        for i, task_type in enumerate(task_types):
            header_x = 180 + (i * col_width)
            header_text = self.task_display_names[task_type]
            
            task_header = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(header_x, header_y, col_width - 5, 50),
                text=header_text,
                manager=self.gui_manager,
                container=self.background_panel
            )
            self.modal_elements.append(task_header)
        
        # Employee rows
        self._create_employee_rows(grid_start_y + 60, col_width)
    
    def _create_employee_rows(self, start_y: int, col_width: int):
        """Create rows for each employee with their task priorities"""
        row_height = 60  # Increased height to show specialization info
        
        # Get current employees from existing system
        self._request_current_employee_data()
        
        # Create rows for each employee (or placeholder if no employees)
        if not self.current_employees:
            # Show placeholder employees to demonstrate interface
            placeholder_employees = ["Sam", "Barry More"]
            self.current_employees = placeholder_employees
        
        for i, employee in enumerate(self.current_employees):
            row_y = start_y + (i * row_height)
            
            # Employee name and specialization info
            employee_name = employee if isinstance(employee, str) else getattr(employee, 'name', 'Unknown')
            
            # Get specialization info if available
            specialization_info = self._get_employee_specialization_info(employee)
            display_text = employee_name
            if specialization_info['role'] != 'General Worker':
                display_text = f"{employee_name}\n({specialization_info['role']})"
            
            # Employee name label (increased height for specialization)
            name_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(20, row_y, 150, 50),
                text=display_text,
                manager=self.gui_manager,
                container=self.background_panel
            )
            self.modal_elements.append(name_label)
            
            # Task priority dropdowns for each task type
            task_types = list(self.task_display_names.keys())
            for j, task_type in enumerate(task_types):
                dropdown_x = 180 + (j * col_width)
                
                # Get suggested priority based on employee specialization
                suggested_priority = self._get_suggested_priority(employee, task_type)
                
                # Create enhanced dropdown with skill level indicator
                skill_info = self._get_skill_level_for_task(employee, task_type)
                dropdown_options = self._create_priority_options_with_skill_info(skill_info)
                
                priority_dropdown = pygame_gui.elements.UIDropDownMenu(
                    relative_rect=pygame.Rect(dropdown_x + 5, row_y + 5, col_width - 15, 30),
                    options_list=dropdown_options,
                    starting_option=suggested_priority,
                    manager=self.gui_manager,
                    container=self.background_panel
                )
                self.modal_elements.append(priority_dropdown)
                
                # Store reference for later use
                if not hasattr(self, 'priority_dropdowns'):
                    self.priority_dropdowns = {}
                if employee_name not in self.priority_dropdowns:
                    self.priority_dropdowns[employee_name] = {}
                self.priority_dropdowns[employee_name][task_type] = priority_dropdown
    
    def _create_control_buttons(self):
        """Create control buttons at bottom of modal"""
        button_y = self.modal_height - 80  # Position near bottom
        button_width = 120
        button_height = 40
        
        # Apply button (currently disabled since we're read-only)
        self.apply_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.modal_width - 260, button_y, button_width, button_height),
            text="Apply (Disabled)",
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.apply_button.disable()  # Disabled until we implement assignment logic
        self.modal_elements.append(self.apply_button)
        
        # Reset button
        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.modal_width - 390, button_y, button_width, button_height),
            text="Reset to Defaults",
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(self.reset_button)
        
        # Feature status label
        feature_status = "Enhanced Task System: DISABLED (using legacy system)"
        if ENABLE_ENHANCED_TASK_SYSTEM:
            feature_status = "Enhanced Task System: ENABLED"
        
        self.feature_status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, button_y, 400, 30),
            text=feature_status,
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(self.feature_status_label)
    
    def _request_current_employee_data(self):
        """Request current employee data from existing system"""
        # Emit event to get current employee list
        self.event_system.emit('get_employee_list_for_ui', {})
        
        # For now, we'll work with placeholder data
        # This will be replaced when we get real data from the employee manager
    
    def show_modal(self):
        """Show the task assignment modal"""
        if not self.is_visible:
            self.is_visible = True
            self._create_modal_elements()
            
            # Emit event to notify other systems
            self.event_system.emit('task_assignment_modal_opened', {})
    
    def hide_modal(self):
        """Hide the task assignment modal"""
        if self.is_visible:
            self.is_visible = False
            self._cleanup_elements()
            
            # Emit event to notify other systems
            self.event_system.emit('task_assignment_modal_closed', {})
    
    def _cleanup_elements(self):
        """Clean up all UI elements"""
        for element in self.modal_elements:
            if element and element.alive():
                element.kill()
        self.modal_elements.clear()
        
        # Clear dropdown references
        if hasattr(self, 'priority_dropdowns'):
            self.priority_dropdowns.clear()
    
    def handle_event(self, event):
        """Handle pygame events for the modal"""
        if not self.is_visible:
            return False
        
        # Handle UI button clicks
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if hasattr(self, 'close_button') and event.ui_element == self.close_button:
                self.hide_modal()
                return True
            elif hasattr(self, 'reset_button') and event.ui_element == self.reset_button:
                self._reset_to_defaults()
                return True
            elif hasattr(self, 'apply_button') and event.ui_element == self.apply_button:
                self._apply_task_assignments()
                return True
        
        # Handle dropdown changes
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            self._handle_priority_change(event)
            return True
        
        return False
    
    def _reset_to_defaults(self):
        """Reset all task priorities to default values"""
        if hasattr(self, 'priority_dropdowns'):
            for employee_name in self.priority_dropdowns:
                for task_type in self.priority_dropdowns[employee_name]:
                    dropdown = self.priority_dropdowns[employee_name][task_type]
                    if dropdown and dropdown.alive():
                        dropdown.selected_option = "3"  # Reset to normal priority
    
    def _handle_priority_change(self, event):
        """Handle when a priority dropdown is changed"""
        # For now, just log the change
        # In future phases, this will update the employee specialization data
        print(f"Priority changed: {event.ui_element} -> {event.text}")
    
    def _apply_task_assignments(self):
        """Apply the current task priority settings"""
        # Currently disabled - will be implemented in later phases
        print("Apply task assignments - feature not yet implemented")
    
    # Event handlers
    def _handle_employee_update(self, event_data):
        """Handle employee count/data updates"""
        # Update our employee list and refresh the display if modal is visible
        if self.is_visible:
            self._refresh_employee_data()
    
    def _handle_task_update(self, event_data):
        """Handle task assignment updates"""
        # Update task display if modal is visible
        if self.is_visible:
            self._refresh_task_data()
    
    def _handle_show_modal(self, event_data):
        """Handle request to show the modal"""
        self.show_modal()
    
    def _handle_hide_modal(self, event_data):
        """Handle request to hide the modal"""
        self.hide_modal()
    
    def _refresh_employee_data(self):
        """Refresh employee data display"""
        # Re-request employee data and update display
        self._request_current_employee_data()
        
        # If modal is visible, recreate the grid to show updated data
        if self.is_visible:
            # Recreate just the employee rows
            # For now, keep it simple - full recreation
            self._create_modal_elements()
    
    def _refresh_task_data(self):
        """Refresh task data display"""
        # Update any task-related information in the modal
        pass
    
    def update(self, time_delta: float):
        """Update the modal (called each frame)"""
        # Nothing to update for now
        pass
    
    def cleanup(self):
        """Clean up when the modal is destroyed"""
        self.hide_modal()
        
        # Unsubscribe from events
        self.event_system.unsubscribe('employee_count_update', self._handle_employee_update)
        self.event_system.unsubscribe('task_assignment_updated', self._handle_task_update)
        self.event_system.unsubscribe('show_task_assignment_modal', self._handle_show_modal)
        self.event_system.unsubscribe('hide_task_assignment_modal', self._handle_hide_modal)
    
    # Enhanced Task System Helper Methods (Phase 2A)
    def _get_employee_specialization_info(self, employee):
        """Get specialization information for an employee"""
        if isinstance(employee, str):
            # Placeholder employee - create mock specialization for demo
            return self._create_mock_specialization(employee)
        
        # Real employee object - check if it has specialization
        if hasattr(employee, 'get_specialization_summary'):
            return employee.get_specialization_summary()
        else:
            return {'role': 'General Worker', 'skills': {}, 'top_skills': []}
    
    def _create_mock_specialization(self, employee_name: str):
        """Create mock specialization data for placeholder employees"""
        name_lower = employee_name.lower()
        
        if 'sam' in name_lower:
            return {
                'role': 'Field Operator',
                'skills': {
                    'tilling': {'level': 3, 'name': 'Competent', 'efficiency': 1.0},
                    'planting': {'level': 3, 'name': 'Competent', 'efficiency': 1.0},
                    'harvesting': {'level': 2, 'name': 'Basic', 'efficiency': 0.75}
                },
                'top_skills': [
                    {'task': 'tilling', 'level': 3},
                    {'task': 'planting', 'level': 3}
                ]
            }
        elif 'barry' in name_lower:
            return {
                'role': 'Harvest Specialist', 
                'skills': {
                    'harvesting': {'level': 4, 'name': 'Expert', 'efficiency': 1.25},
                    'processing': {'level': 3, 'name': 'Competent', 'efficiency': 1.0},
                    'storing': {'level': 2, 'name': 'Basic', 'efficiency': 0.75}
                },
                'top_skills': [
                    {'task': 'harvesting', 'level': 4},
                    {'task': 'processing', 'level': 3}
                ]
            }
        else:
            return {'role': 'General Worker', 'skills': {}, 'top_skills': []}
    
    def _get_suggested_priority(self, employee, task_type):
        """Get suggested priority based on employee specialization"""
        specialization_info = self._get_employee_specialization_info(employee)
        
        # Convert TaskType to string for lookup
        task_name = task_type.value if hasattr(task_type, 'value') else str(task_type)
        
        # Check if employee has skills for this task
        if task_name in specialization_info['skills']:
            skill_level = specialization_info['skills'][task_name]['level']
            
            # Suggest priority based on skill level
            if skill_level >= 4:  # Expert/Master
                return "2"  # High priority
            elif skill_level >= 3:  # Competent
                return "3"  # Normal priority  
            elif skill_level >= 2:  # Basic
                return "4"  # Low priority
            else:  # Novice
                return "5"  # Minimal priority
        else:
            # No specific skill info - default to normal
            return "3"
    
    def _get_skill_level_for_task(self, employee, task_type):
        """Get skill level information for a specific task"""
        specialization_info = self._get_employee_specialization_info(employee)
        task_name = task_type.value if hasattr(task_type, 'value') else str(task_type)
        
        if task_name in specialization_info['skills']:
            skill_data = specialization_info['skills'][task_name]
            return {
                'level': skill_data['level'],
                'name': skill_data['name'],
                'efficiency': skill_data.get('efficiency', 1.0)
            }
        else:
            return {'level': 1, 'name': 'Novice', 'efficiency': 0.5}
    
    def _create_priority_options_with_skill_info(self, skill_info):
        """Create priority dropdown options with skill level indicator"""
        base_options = ["1", "2", "3", "4", "5"]
        
        # Add skill level indicator to options if specializations are enabled
        if ENABLE_EMPLOYEE_SPECIALIZATIONS:
            skill_indicator = f" ({skill_info['name']})"
            # Only add to the suggested priority option for clarity
            return base_options
        else:
            return base_options