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
        
        # Button references for event handling
        self.work_order_buttons = {}  # Dict of button -> work_order_id for event handling
        
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
        
        # Task integration reference for direct access
        self.task_integration = None
        
        # Subscribe to events for data updates
        self.event_system.subscribe('employee_count_update', self._handle_employee_update)
        self.event_system.subscribe('task_assignment_updated', self._handle_task_update)
        self.event_system.subscribe('show_task_assignment_modal', self._handle_show_modal)
        self.event_system.subscribe('hide_task_assignment_modal', self._handle_hide_modal)
        self.event_system.subscribe('work_order_completed', self._handle_work_order_completed)
    
    def set_task_integration(self, task_integration):
        """Set the task integration system for direct access to work orders"""
        self.task_integration = task_integration
        print("Task Assignment Modal: Connected to task integration system")
    
    def _create_modal_elements(self):
        """Create all UI elements for the enhanced two-panel assignment interface"""
        # Clear existing elements
        self._cleanup_elements()
        
        # Main modal background panel (larger for two-panel layout)
        panel_width = 1000
        panel_height = 700
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        self.background_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            starting_height=10,  # High z-order for modal
            manager=self.gui_manager
        )
        self.modal_elements.append(self.background_panel)
        
        # Modal title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 15, panel_width - 40, 35),
            text="🚜 Agricultural Operations Management - Multi-Employee Assignment",
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(self.title_label)
        
        # Close button (top-right)
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 80, 15, 60, 30),
            text="✕",
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(self.close_button)
        
        # Assignment mode instructions
        self.instructions_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 55, panel_width - 40, 25),
            text="Assignment Mode: Select employee from pool → Click 'Add Employee' on work order → Multiple employees supported",
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(self.instructions_label)
        
        # Selection state tracker
        self.selected_employee_id = None
        
        # Create the two-panel layout
        self._create_work_orders_panel(panel_width, panel_height)
        self._create_employee_pool_panel(panel_width, panel_height)
    
    def _create_work_orders_panel(self, panel_width: int, panel_height: int):
        """Create the left panel for work orders"""
        # Work Orders Panel (Left side - 60% width)
        work_orders_width = int(panel_width * 0.6) - 30
        work_orders_height = panel_height - 120
        
        self.work_orders_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(20, 90, work_orders_width, work_orders_height),
            starting_height=1,
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(self.work_orders_panel)
        
        # Work Orders Panel Title
        self.work_orders_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, work_orders_width - 20, 30),
            text="📋 WORK ORDERS",
            manager=self.gui_manager,
            container=self.work_orders_panel
        )
        self.modal_elements.append(self.work_orders_title)
        
        # Scrollable container for work orders
        self.work_orders_scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 50, work_orders_width - 20, work_orders_height - 60),
            manager=self.gui_manager,
            container=self.work_orders_panel
        )
        self.modal_elements.append(self.work_orders_scroll)
    
    def _create_employee_pool_panel(self, panel_width: int, panel_height: int):
        """Create the right panel for employee pool"""
        # Employee Pool Panel (Right side - 40% width)
        employee_pool_width = int(panel_width * 0.4) - 30
        employee_pool_height = panel_height - 120
        employee_pool_x = int(panel_width * 0.6) + 10
        
        self.employee_pool_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(employee_pool_x, 90, employee_pool_width, employee_pool_height),
            starting_height=1,
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(self.employee_pool_panel)
        
        # Employee Pool Panel Title
        self.employee_pool_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, employee_pool_width - 20, 30),
            text="👥 EMPLOYEE POOL",
            manager=self.gui_manager,
            container=self.employee_pool_panel
        )
        self.modal_elements.append(self.employee_pool_title)
        
        # Scrollable container for employee cards
        self.employee_pool_scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 50, employee_pool_width - 20, employee_pool_height - 60),
            manager=self.gui_manager,
            container=self.employee_pool_panel
        )
        self.modal_elements.append(self.employee_pool_scroll)
        
        # Load employee and work order data
        self._populate_interface_data()
    
    def _populate_interface_data(self):
        """Load and display work orders and employees in the interface"""
        # Create work order display (Phase 2B) or task assignment grid
        if ENABLE_WORK_ORDERS:
            self._create_work_order_interface()
            self._create_employee_cards_interface()
        else:
            self._create_task_grid()
    
    def _create_employee_cards_interface(self):
        """Create employee cards with skills and availability"""
        
        if not self.task_integration:
            return
        
        # Request employee data
        self.employee_cards = []
        self._request_employee_pool_data()
    
    def _request_employee_pool_data(self):
        """Request current employee data for the pool display"""
        
        def handle_employee_data(employees):
            self._display_employee_cards(employees)
        
        if self.task_integration and hasattr(self.task_integration, 'get_employee_data'):
            self.task_integration.get_employee_data(handle_employee_data)
        else:
            # Use direct access to get employee data
            employees_data = self._get_employees_assignment_data()
            self._display_employee_cards(employees_data)
    
    def _display_employee_cards(self, employees):
        """Display employee cards in the pool panel"""
        # Clear existing cards
        for card in getattr(self, 'employee_cards', []):
            if card in self.modal_elements:
                self.modal_elements.remove(card)
                card.kill()
        
        self.employee_cards = []
        card_y = 10
        card_height = 120
        card_spacing = 10
        
        for i, employee in enumerate(employees):
            # Employee card panel
            # Employee pool scroll container is about 270px wide
            card_width = 260
            card_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(5, card_y, card_width, card_height),
                starting_height=1,
                manager=self.gui_manager,
                container=self.employee_pool_scroll
            )
            self.modal_elements.append(card_panel)
            self.employee_cards.append(card_panel)
            
            # Employee name and role
            name_text = f"👤 {employee.get('name', 'Unknown')}"
            role_text = employee.get('role', 'Field Worker')
            
            name_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 5, card_width - 70, 25),
                text=name_text,
                manager=self.gui_manager,
                container=card_panel
            )
            self.modal_elements.append(name_label)
            self.employee_cards.append(name_label)
            
            role_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 25, card_width - 70, 20),
                text=f"🚜 {role_text}",
                manager=self.gui_manager,
                container=card_panel
            )
            self.modal_elements.append(role_label)
            self.employee_cards.append(role_label)
            
            # Skills display
            skills_text = self._format_employee_skills(employee)
            skills_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 45, card_width - 70, 40),
                text=skills_text,
                manager=self.gui_manager,
                container=card_panel
            )
            self.modal_elements.append(skills_label)
            self.employee_cards.append(skills_label)
            
            # Availability status
            availability = self._get_employee_availability(employee)
            status_color = self._get_availability_color(availability['status'])
            
            status_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 85, card_width - 70, 20),
                text=f"Status: {availability['text']}",
                manager=self.gui_manager,
                container=card_panel
            )
            self.modal_elements.append(status_label)
            self.employee_cards.append(status_label)
            
            # Selection button
            select_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(card_width - 50, 5, 40, 30),
                text="●" if self.selected_employee_id == employee.get('id') else "○",
                manager=self.gui_manager,
                container=card_panel
            )
            select_button.employee_id = employee.get('id')
            select_button.employee_name = employee.get('name')
            self.modal_elements.append(select_button)
            self.employee_cards.append(select_button)
            
            card_y += card_height + card_spacing
        
        # Update scroll container size
        total_height = max(400, card_y)
        self.employee_pool_scroll.set_scrollable_area_dimensions((300, total_height))
    
    def _format_employee_skills(self, employee):
        """Format employee skills for display"""
        specialization = employee.get('specialization', {})
        skills = specialization.get('skills', {})
        
        if not skills:
            return "Skills: Basic Farm Worker"
        
        # Get top 3 skills
        skill_items = list(skills.items())[:3]
        skill_lines = []
        
        for skill_name, skill_data in skill_items:
            skill_level = skill_data.get('level', 1)
            stars = "★" * skill_level + "☆" * (5 - skill_level)
            skill_lines.append(f"{skill_name.title()}: {stars}")
        
        return "\n".join(skill_lines)
    
    def _get_employee_availability(self, employee):
        """Get employee availability status"""
        current_task = employee.get('current_task')
        workload = employee.get('workload', 0)
        
        if not current_task:
            return {'status': 'available', 'text': 'Available'}
        elif workload < 2:
            return {'status': 'busy', 'text': f'Busy ({workload} orders)'}
        else:
            return {'status': 'overloaded', 'text': f'Overloaded ({workload} orders)'}
    
    def _get_availability_color(self, status):
        """Get color for availability status"""
        colors = {
            'available': '#00AA00',
            'busy': '#AAAA00', 
            'overloaded': '#AA0000'
        }
        return colors.get(status, '#888888')
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
            placeholder_employees = ["Worker A", "Worker B"]
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
        if ENABLE_WORK_ORDERS:
            feature_status = "Work Order System: ACTIVE (Phase 2B)"
        elif ENABLE_EMPLOYEE_SPECIALIZATIONS:
            feature_status = "Employee Specializations: ACTIVE (Phase 2A)"
        elif ENABLE_ENHANCED_TASK_SYSTEM:
            feature_status = "Enhanced Task System: ENABLED"
        else:
            feature_status = "Legacy Task System: ACTIVE"
        
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
        
        # Clear work order button references
        self.work_order_buttons.clear()
    
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
            elif event.ui_element in self.work_order_buttons:
                # Handle work order action buttons (Reassign/Cancel)
                action, work_order_id = self.work_order_buttons[event.ui_element]
                self._handle_work_order_action(action, work_order_id)
                return True
            # Handle employee selection buttons
            elif hasattr(event.ui_element, 'employee_id'):
                self._handle_employee_selection(event.ui_element)
                return True
            # Handle enhanced work order buttons (Add Employee, Cancel Order)  
            elif hasattr(event.ui_element, 'work_order_id') and hasattr(event.ui_element, 'action'):
                self._handle_enhanced_work_order_action(event.ui_element)
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
    
    def _handle_employee_selection(self, button):
        """Handle employee selection in the pool"""
        employee_id = button.employee_id
        employee_name = button.employee_name
        
        # Update selection state
        previous_selected = self.selected_employee_id
        self.selected_employee_id = employee_id
        
        print(f"Selected employee: {employee_name} ({employee_id})")
        
        # Update button states - refresh the employee cards
        self._request_employee_pool_data()
        
        # Provide user feedback
        self.event_system.emit('show_notification', {
            'message': f'Selected {employee_name} for assignment',
            'category': 'info'
        })
    
    def _handle_enhanced_work_order_action(self, button):
        """Handle enhanced work order actions (Add Employee, Cancel Order)"""
        work_order_id = button.work_order_id
        action = button.action
        
        if action == 'add_employee':
            if self.selected_employee_id:
                self._assign_employee_to_work_order(work_order_id, self.selected_employee_id)
            else:
                self.event_system.emit('show_notification', {
                    'message': 'Please select an employee from the pool first',
                    'category': 'warning'
                })
        elif action == 'cancel':
            self._cancel_work_order(work_order_id)
    
    def _assign_employee_to_work_order(self, work_order_id: str, employee_id: str):
        """Assign the selected employee to a work order"""
        print(f"Assigning employee {employee_id} to work order {work_order_id}")
        
        # Emit assignment event to work order system
        self.event_system.emit('multi_employee_work_order_assignment', {
            'work_order_id': work_order_id,
            'employee_id': employee_id,
            'action': 'assign'
        })
        
        # Refresh interface
        self._create_work_order_interface()
        self._request_employee_pool_data()
        
        # Show confirmation
        self.event_system.emit('show_notification', {
            'message': f'Employee assigned to work order',
            'category': 'success'
        })
    
    def _cancel_work_order(self, work_order_id: str):
        """Cancel a work order"""
        print(f"Canceling work order {work_order_id}")
        
        # Emit cancellation event
        self.event_system.emit('cancel_work_order', {
            'work_order_id': work_order_id,
            'reason': 'User cancelled from assignment interface'
        })
        
        # Refresh interface
        self._create_work_order_interface()
        
        # Show confirmation
        self.event_system.emit('show_notification', {
            'message': 'Work order cancelled',
            'category': 'info'
        })

    def _handle_work_order_action(self, action: str, work_order_id: str):
        """Handle work order action buttons (Reassign/Cancel)"""
        print(f"Work order action: {action} for order {work_order_id}")
        
        if action == "reassign":
            self._reassign_work_order(work_order_id)
        elif action == "cancel":
            self._cancel_work_order(work_order_id)
    
    def _reassign_work_order(self, work_order_id: str):
        """Reassign a work order to an available employee"""
        if not self.task_integration:
            print("Cannot reassign: No task integration system")
            return
        
        # Get available employees
        employees_data = self._get_employees_assignment_data()
        if not employees_data:
            print("No available employees for reassignment")
            return
        
        # Assign to the first available employee (auto-assignment)
        # In a full implementation, this would show a selection dialog
        target_employee = employees_data[0]  # Get first available employee
        employee_id = target_employee['id']
        
        # Use the task integration system to assign the work order
        if hasattr(self.task_integration, 'work_order_manager'):
            success = self.task_integration.work_order_manager.assign_work_order(work_order_id, employee_id)
            if success:
                print(f"Work order {work_order_id} assigned to {target_employee['name']}")
                # Refresh the modal to show updated assignment
                self._refresh_modal_data()
            else:
                print(f"Failed to assign work order {work_order_id}")
        else:
            print("Cannot assign: No work order manager")
    
    def _cancel_work_order(self, work_order_id: str):
        """Cancel a work order"""
        if not self.task_integration:
            print("Cannot cancel: No task integration system")
            return
        
        if hasattr(self.task_integration, 'work_order_manager'):
            success = self.task_integration.work_order_manager.cancel_work_order(work_order_id, "User cancelled")
            if success:
                print(f"Work order {work_order_id} cancelled")
                # Refresh the modal to remove cancelled order
                self._refresh_modal_data()
            else:
                print(f"Failed to cancel work order {work_order_id}")
        else:
            print("Cannot cancel: No work order manager")
    
    def _refresh_modal_data(self):
        """Refresh the modal to show updated work order data"""
        if self.is_visible:
            # Recreate the modal elements to show updated data
            self._create_modal_elements()
    
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
    
    def _handle_work_order_completed(self, event_data):
        """Handle work order completion - refresh interface to remove completed orders"""
        work_order_id = event_data.get('work_order_id')
        employee_id = event_data.get('employee_id')
        
        if work_order_id:
            print(f"UI: Work order {work_order_id} completed, refreshing interface")
            
            # If modal is visible, refresh to show updated work order list
            if self.is_visible:
                self._create_modal_elements()
    
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
        
        if 'worker a' in name_lower:
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
        elif 'worker b' in name_lower:
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
    
    def _create_work_order_interface(self):
        """Create enhanced work order management interface with multi-employee support"""
        # Get work orders data
        work_orders_data = self._get_work_orders_data()
        
        # Clear existing work order UI elements
        for element in getattr(self, 'work_order_ui_elements', []):
            if element in self.modal_elements:
                self.modal_elements.remove(element)
                element.kill()
        
        self.work_order_ui_elements = []
        
        # Create work order entries in the scroll container
        entry_height = 140  # Increased height for multi-employee display
        entry_spacing = 10
        entry_y = 10
        
        for i, order_data in enumerate(work_orders_data):
            entry_panel = self._create_enhanced_work_order_entry(
                entry_y, entry_height, order_data
            )
            entry_y += entry_height + entry_spacing
        
        # Update scroll container size
        total_height = max(400, entry_y)
        if hasattr(self, 'work_orders_scroll'):
            self.work_orders_scroll.set_scrollable_area_dimensions((580, total_height))
    
    def _create_enhanced_work_order_entry(self, y: int, height: int, order_data: Dict):
        """Create enhanced work order entry with multi-employee support"""
        
        # Work order entry panel
        # Get the actual container width for proper sizing
        container_width = 570  # Work orders scroll container is about 570px wide
        entry_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(5, y, container_width - 10, height),
            starting_height=1,
            manager=self.gui_manager,
            container=self.work_orders_scroll
        )
        self.modal_elements.append(entry_panel)
        self.work_order_ui_elements.append(entry_panel)
        
        # Order header
        task_type = order_data.get('task_type', 'Unknown')
        plot_count = order_data.get('plot_count', 0)
        priority = order_data.get('priority', 'Normal')
        
        title_text = f"📋 {task_type.title()} Work Order ({plot_count} plots)"
        title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 5, container_width - 140, 25),
            text=title_text,
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(title_label)
        self.work_order_ui_elements.append(title_label)
        
        # Priority and status
        priority_text = f"Priority: {priority} | Status: {order_data.get('status', 'Unassigned')}"
        priority_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 25, container_width - 140, 20),
            text=priority_text,
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(priority_label)
        self.work_order_ui_elements.append(priority_label)
        
        # Assigned employees section
        assigned_employees = order_data.get('assigned_employees', [])
        if assigned_employees:
            employees_text = "Assigned: " + ", ".join([f"[{emp['name']} ×]" for emp in assigned_employees])
        else:
            employees_text = "Assigned: None"
        
        employees_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 50, container_width - 140, 40),
            text=employees_text,
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(employees_label)
        self.work_order_ui_elements.append(employees_label)
        
        # Progress bars for each employee (if assigned)
        if assigned_employees and len(assigned_employees) > 0:
            progress_y = 95
            for emp in assigned_employees:
                emp_progress_text = f"{emp['name']}: {emp.get('plots_assigned', 0)} plots - Progress: {emp.get('progress', 0)}%"
                progress_label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(15, progress_y, container_width - 145, 15),
                    text=emp_progress_text,
                    manager=self.gui_manager,
                    container=entry_panel
                )
                self.modal_elements.append(progress_label)
                self.work_order_ui_elements.append(progress_label)
                progress_y += 18
        
        # Action buttons
        button_width = 100
        button_height = 30
        
        # Add Employee button
        add_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(container_width - 110, 10, button_width, button_height),
            text="Add Employee",
            manager=self.gui_manager,
            container=entry_panel
        )
        add_button.work_order_id = order_data.get('id')
        add_button.action = 'add_employee'
        self.modal_elements.append(add_button)
        self.work_order_ui_elements.append(add_button)
        
        # Cancel Work Order button
        cancel_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(container_width - 110, 50, button_width, button_height),
            text="Cancel Order",
            manager=self.gui_manager,
            container=entry_panel
        )
        cancel_button.work_order_id = order_data.get('id')
        cancel_button.action = 'cancel'
        self.modal_elements.append(cancel_button)
        self.work_order_ui_elements.append(cancel_button)
        
        return entry_panel
    
    def _create_work_order_list(self, x: int, y: int, width: int, height: int):
        """Create active work orders list"""
        # Work orders panel
        work_orders_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, height),
            starting_height=1,
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(work_orders_panel)
        
        # Work orders title
        orders_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, width - 20, 25),
            text="Active Work Orders",
            manager=self.gui_manager,
            container=work_orders_panel
        )
        self.modal_elements.append(orders_title)
        
        # Scrollable area for work orders
        orders_scroll_area = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 40, width - 20, height - 60),
            manager=self.gui_manager,
            container=work_orders_panel
        )
        self.modal_elements.append(orders_scroll_area)
        
        # Get work orders data (placeholder for now)
        work_orders_data = self._get_work_orders_data()
        
        # Create work order entries
        entry_height = 80
        for i, order_data in enumerate(work_orders_data):
            entry_y = i * (entry_height + 10)
            self._create_work_order_entry(
                orders_scroll_area, 0, entry_y, width - 40, entry_height, order_data
            )
    
    def _create_work_order_entry(self, container, x: int, y: int, width: int, height: int, order_data: Dict):
        """Create individual work order entry"""
        # Work order background
        entry_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, height),
            starting_height=1,
            manager=self.gui_manager,
            container=container
        )
        self.modal_elements.append(entry_panel)
        
        # Order details
        task_type = order_data.get('task_type', 'Unknown')
        plot_count = order_data.get('plot_count', 0)
        priority = order_data.get('priority', 'Normal')
        assigned_to = order_data.get('assigned_to', 'Unassigned')
        deadline = order_data.get('deadline', 'No deadline')
        
        # Title line
        title_text = f"{task_type.title()} - {plot_count} plots"
        title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 5, width - 20, 20),
            text=title_text,
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(title_label)
        
        # Details line
        details_text = f"Priority: {priority} | Assigned: {assigned_to}"
        details_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 25, width - 20, 15),
            text=details_text,
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(details_label)
        
        # Deadline line
        deadline_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 40, width - 120, 15),
            text=f"Deadline: {deadline}",
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(deadline_label)
        
        # Action buttons
        reassign_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(width - 110, 35, 50, 25),
            text="Reassign",
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(reassign_button)
        
        cancel_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(width - 55, 35, 45, 25),
            text="Cancel",
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(cancel_button)
        
        # Store button references for event handling
        work_order_id = order_data.get('id')
        if work_order_id:
            self.work_order_buttons[reassign_button] = ('reassign', work_order_id)
            self.work_order_buttons[cancel_button] = ('cancel', work_order_id)
    
    def _create_employee_assignment_panel(self, x: int, y: int, width: int, height: int):
        """Create employee assignment management panel"""
        # Employee panel
        employee_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, height),
            starting_height=1,
            manager=self.gui_manager,
            container=self.background_panel
        )
        self.modal_elements.append(employee_panel)
        
        # Employee title
        emp_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, width - 20, 25),
            text="Employee Status & Assignments",
            manager=self.gui_manager,
            container=employee_panel
        )
        self.modal_elements.append(emp_title)
        
        # Get employee data
        employees_data = self._get_employees_assignment_data()
        
        # Create employee entries
        entry_height = 100
        start_y = 40
        for i, emp_data in enumerate(employees_data):
            entry_y = start_y + (i * (entry_height + 10))
            self._create_employee_assignment_entry(
                employee_panel, 10, entry_y, width - 20, entry_height, emp_data
            )
    
    def _create_employee_assignment_entry(self, container, x: int, y: int, width: int, height: int, emp_data: Dict):
        """Create individual employee assignment entry"""
        # Employee background
        entry_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, height),
            starting_height=1,
            manager=self.gui_manager,
            container=container
        )
        self.modal_elements.append(entry_panel)
        
        name = emp_data.get('name', 'Unknown')
        role = emp_data.get('role', 'General Worker')
        current_task = emp_data.get('current_task', 'Idle')
        efficiency = emp_data.get('efficiency', 1.0)
        workload = emp_data.get('workload', 0)
        
        # Employee name and role
        name_text = f"{name} ({role})"
        name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 5, width - 20, 20),
            text=name_text,
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(name_label)
        
        # Current status
        status_text = f"Current: {current_task}"
        status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 25, width - 20, 15),
            text=status_text,
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(status_label)
        
        # Efficiency and workload
        stats_text = f"Efficiency: {efficiency:.1f}x | Workload: {workload} orders"
        stats_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 45, width - 20, 15),
            text=stats_text,
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(stats_label)
        
        # Assign new work button
        assign_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(width - 80, 65, 70, 25),
            text="Assign Work",
            manager=self.gui_manager,
            container=entry_panel
        )
        self.modal_elements.append(assign_button)
    
    def _get_work_orders_data(self) -> List[Dict]:
        """Get work orders data for display"""
        
        # Use direct access if task integration is available
        if self.task_integration:
            work_orders_data = self.task_integration.get_active_work_orders()
            return work_orders_data
        
        # Fallback to event callback (original method)
        work_orders_data = []
        def collect_work_orders(orders):
            work_orders_data.extend(orders)
        
        self.event_system.emit('get_work_orders_for_ui', {
            'callback': collect_work_orders
        })
        
        return work_orders_data
    
    def _get_employees_assignment_data(self) -> List[Dict]:
        """Get employee assignment data for display"""
        
        # Use direct access if task integration is available
        if self.task_integration:
            # Get employee assignment data directly
            employees_data = []
            workloads = self.task_integration.get_employee_workloads()
            
            if hasattr(self.task_integration, 'employee_manager') and self.task_integration.employee_manager:
                
                for emp_id, employee in self.task_integration.employee_manager.employees.items():
                    emp_data = {
                        'id': emp_id,
                        'name': employee.name,
                        'current_task': 'Idle',  # Simplified for now
                        'workload': workloads.get(emp_id, 0),
                        'role': 'General Worker',  # Default
                        'efficiency': 1.0
                    }
                    
                    # Add specialization data if available
                    if hasattr(employee, 'get_specialization_summary'):
                        summary = employee.get_specialization_summary()
                        emp_data['role'] = summary.get('role', 'General Worker')
                    elif hasattr(employee, 'specialization'):
                        # Use specialization string directly
                        emp_data['role'] = employee.specialization.replace('_', ' ').title()
                    
                    employees_data.append(emp_data)
            
            return employees_data
        
        # Fallback to event callback
        employees_data = []
        def collect_employee_data(data):
            employees_data.extend(data)
        
        self.event_system.emit('get_employee_assignments_for_ui', {
            'callback': collect_employee_data
        })
        
        return employees_data