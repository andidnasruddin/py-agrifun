"""
UI Manager - Handles all user interface elements and interactions
Uses pygame-gui for advanced UI components with fallback to custom implementation.
"""

import pygame
import pygame_gui
from scripts.core.config import *


class UIManager:
    """Main UI controller"""
    
    def __init__(self, event_system, screen):
        """Initialize the UI manager"""
        self.event_system = event_system
        self.screen = screen
        self.screen_rect = screen.get_rect()
        
        # Initialize pygame-gui manager
        self.gui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # UI state
        self.show_debug = True
        
        # Applicant panel state
        self.current_applicants = []
        
        # Interview system removed - using Simple Hiring System for direct hiring
        
        # Notification system
        self.notifications = []
        self.notification_timer = 0.0
        
        # Initialize UI elements
        self._create_ui_elements()  # Create basic UI components like buttons and panels
        # Note: Applicant panel will be created dynamically when needed
        
        # Register for events
        self.event_system.subscribe('time_updated', self._handle_time_update)
        self.event_system.subscribe('money_changed', self._handle_money_update)
        self.event_system.subscribe('inventory_updated', self._handle_inventory_update)
        self.event_system.subscribe('task_assigned_feedback', self._handle_task_feedback)
        self.event_system.subscribe('task_assignment_failed', self._handle_task_failure)
        self.event_system.subscribe('building_purchased', self._handle_building_purchase)
        self.event_system.subscribe('purchase_failed', self._handle_purchase_failure)
        self.event_system.subscribe('storage_upgraded', self._handle_storage_upgrade)
        # Re-enable hiring system event handlers
        self.event_system.subscribe('applicants_generated', self._handle_applicants_generated)  # Handle when applicants are available
        self.event_system.subscribe('employee_hired_successfully', self._handle_employee_hired)  # Handle successful hire
        self.event_system.subscribe('hire_failed', self._handle_hire_failure)  # Handle hiring failures
        
        self.event_system.subscribe('show_employee_roster_requested', self._handle_roster_request)
        self.event_system.subscribe('roster_displayed', self._handle_roster_displayed)
        self.event_system.subscribe('employee_hired', self._handle_employee_count_change)
        self.event_system.subscribe('employee_fired', self._handle_employee_count_change)
        self.event_system.subscribe('employee_count_update', self._handle_employee_count_update)
        self.event_system.subscribe('employee_status_update', self._handle_employee_status_update)
        self.event_system.subscribe('day_passed', self._handle_day_passed)
        self.event_system.subscribe('get_current_crop_type_requested', self._handle_crop_type_request)
        
        # Track current day for expiration calculations
        self._current_day = 1
        
        # Panel state management
        self._applicant_panel_exists = False  # Track if applicant panel is created
        
        print("UI Manager initialized with pygame-gui")
    
    def _create_ui_elements(self):
        """Create the main UI elements"""
        # Resource bar at top
        self.resource_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, WINDOW_WIDTH, 60),
            manager=self.gui_manager
        )
        
        # Money display
        self.money_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, 150, 40),
            text=f"Cash: ${STARTING_CASH}",
            manager=self.gui_manager,
            container=self.resource_panel
        )
        
        # Inventory display
        self.inventory_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(165, 10, 150, 40),
            text="Corn: 0/100",
            manager=self.gui_manager,
            container=self.resource_panel
        )
        
        # Time display
        self.time_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(320, 10, 150, 40),
            text="Day 1 - 5:00 AM",
            manager=self.gui_manager,
            container=self.resource_panel
        )
        
        # Employee count display
        self.employee_count_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(475, 10, 100, 40),
            text="Workers: 1",
            manager=self.gui_manager,
            container=self.resource_panel
        )
        
        # Speed controls with tooltips for better user experience
        self.pause_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(WINDOW_WIDTH-160, 10, 40, 40),
            text="||",
            manager=self.gui_manager,
            container=self.resource_panel,
            tool_tip_text="Pause/Resume game time"
        )
        
        self.speed_1x_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(WINDOW_WIDTH-115, 10, 30, 40),
            text="1x",
            manager=self.gui_manager,
            container=self.resource_panel,
            tool_tip_text="Normal speed (20 min = 1 game day)"
        )
        
        self.speed_2x_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(WINDOW_WIDTH-80, 10, 30, 40),
            text="2x", 
            manager=self.gui_manager,
            container=self.resource_panel,
            tool_tip_text="Double speed (10 min = 1 game day)"
        )
        
        self.speed_4x_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(WINDOW_WIDTH-45, 10, 30, 40),
            text="4x",
            manager=self.gui_manager,
            container=self.resource_panel,
            tool_tip_text="Fast speed (5 min = 1 game day)"
        )
        
        # Main control panel on right side (taller to accommodate save/load buttons)
        self.control_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(WINDOW_WIDTH-250, 70, 240, 450),
            manager=self.gui_manager
        )
        
        self.control_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, 220, 25),
            text="Farm Controls",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        # Economy section
        economy_section_y = 40
        self.economy_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, economy_section_y, 220, 20),
            text="Economy",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.sell_corn_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, economy_section_y + 25, 100, 25),
            text="Sell 10 Corn",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Sell 10 corn units at current market price. Uses FIFO inventory."
        )
        
        self.buy_silo_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(115, economy_section_y + 25, 115, 25),
            text="Buy Storage Silo",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Purchase storage silo (+50 capacity). Cost increases with each purchase."
        )
        
        # Save/Load section
        save_section_y = 100
        self.save_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, save_section_y, 220, 20),
            text="Game State",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.quick_save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, save_section_y + 25, 100, 25),
            text="Quick Save",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Save current game to quicksave slot"
        )
        
        self.quick_load_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(115, save_section_y + 25, 115, 25),
            text="Quick Load",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Load from quicksave slot"
        )
        
        self.save_menu_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, save_section_y + 55, 220, 25),
            text="Save/Load Menu",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Open save/load menu with multiple slots"
        )
        
        # Employee section
        employee_section_y = 190
        self.employee_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, employee_section_y, 220, 20),
            text="Employees",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.hire_employee_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, employee_section_y + 25, 100, 25),
            text="Hire Employee",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Generate job applicants to hire new workers ($80/day wage)"
        )
        
        self.view_applicants_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(115, employee_section_y + 25, 115, 25),
            text="View Applicants",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Review and hire from available job applicants"
        )
        
        self.view_payroll_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, employee_section_y + 55, 220, 25),
            text="View Employee Roster & Payroll",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        # Real-time employee status display
        status_section_y = 280
        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, status_section_y, 220, 15),
            text="Live Status",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.employee_status_display = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(10, status_section_y + 20, 220, 60),
            html_text="<font size=2>No employees</font>",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        # Keyboard shortcuts section (within main panel)
        shortcuts_section_y = 395
        self.shortcuts_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, shortcuts_section_y, 220, 20),
            text="Keyboard Shortcuts",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        
        # Crop selection section
        crop_section_y = shortcuts_section_y - 85
        self.crop_selection_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, crop_section_y, 220, 15),
            text="Crop Selection",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        # Current selected crop display and dropdown
        self.current_crop_type = DEFAULT_CROP_TYPE  # Track currently selected crop type
        crop_data = CROP_TYPES[self.current_crop_type]
        self.selected_crop_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(10, crop_section_y + 20, 150, 25),
            options_list=[f"{CROP_TYPES[crop]['name']} (${CROP_TYPES[crop]['seed_cost']})" for crop in CROP_TYPES],
            starting_option=f"{crop_data['name']} (${crop_data['seed_cost']})",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        # Crop info button
        self.crop_info_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(165, crop_section_y + 20, 55, 25),
            text="Info",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="View detailed crop information and growth times"
        )

        # Task control buttons
        task_controls_y = shortcuts_section_y - 35
        self.task_controls_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, task_controls_y, 220, 15),
            text="Task Controls",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.cancel_tasks_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, task_controls_y + 20, 220, 25),
            text="Cancel Selected Tasks (X)",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        # Create shortcut labels (compact layout within main panel)
        shortcut_texts = [
            "T - Till selected tiles",
            "P - Plant selected tiles", 
            "H - Harvest selected tiles",
            "C - Clear selection",
            "X - Cancel selected tasks",
            "F1 - Toggle debug info",
            "1-3 - Hire applicant #"
        ]
        
        self.shortcut_labels = []
        for i, text in enumerate(shortcut_texts):
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, shortcuts_section_y + 25 + i * 18, 220, 16),
                text=text,
                manager=self.gui_manager,
                container=self.control_panel
            )
            self.shortcut_labels.append(label)
    
    def _create_applicant_panel(self):
        """Create the strategic hiring panel dynamically when needed"""
        if self._applicant_panel_exists:
            return  # Already created
        
        # Strategic hiring panel (center screen) - expanded for table view including expiration
        panel_width = 900
        panel_height = 500
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        self.applicant_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            manager=self.gui_manager
        )
        
        # Panel title
        self.applicant_panel_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            text="Strategic Hiring - Available Candidates",
            manager=self.gui_manager,
            container=self.applicant_panel
        )
        
        # Sort controls
        self.sort_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 45, 80, 25),
            text="Sort by:",
            manager=self.gui_manager,
            container=self.applicant_panel
        )
        
        self.sort_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(95, 45, 120, 25),
            options_list=["Cost (Low-High)", "Cost (High-Low)", "Name (A-Z)", "Age (Young-Old)"],
            starting_option="Cost (Low-High)",
            manager=self.gui_manager,
            container=self.applicant_panel
        )
        
        # Table header
        self.table_header_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, 80, panel_width - 20, 30),
            manager=self.gui_manager,
            container=self.applicant_panel
        )
        
        # Table header labels
        header_columns = [
            ("Name", 0, 95),
            ("Age", 95, 45),
            ("Skills", 140, 110),
            ("Traits", 250, 90),
            ("Previous Job", 340, 90),
            ("Applied For", 430, 75),
            ("Cost", 505, 65),
            ("Expires", 570, 70),
            ("Actions", 640, 150)
        ]
        
        self.header_labels = []
        for header_text, x_pos, width in header_columns:
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x_pos + 5, 5, width - 10, 20),
                text=header_text,
                manager=self.gui_manager,
                container=self.table_header_panel
            )
            self.header_labels.append(label)
        
        # Applicant table area (scrollable)
        self.applicant_table_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 115, panel_width - 20, 320),
            manager=self.gui_manager,
            container=self.applicant_panel
        )
        
        # Close button (adjusted for new panel size)
        self.close_applicant_panel_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 70, 450, 60, 30),
            text="Close",
            manager=self.gui_manager,
            container=self.applicant_panel,
            object_id="close_applicant_panel"
        )
        
        # Storage for applicant table rows (created dynamically)
        self.applicant_table_rows = []
        self.applicant_buttons = []  # Keep for compatibility
        
        # Table configuration
        self.current_sort_mode = "cost_low_high"
        
        # Mark panel as created
        self._applicant_panel_exists = True
        print("DEBUG: Applicant panel created dynamically")
    
    def handle_event(self, event):
        """Handle pygame events"""
        # Direct hiring system - no modal dialogs to block UI events
        
        # Let pygame-gui process the event first
        self.gui_manager.process_events(event)
        
        # Handle our custom events
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.pause_button:
                self.event_system.emit('time_speed_change', {'speed': 0})
            elif event.ui_element == self.speed_1x_button:
                self.event_system.emit('time_speed_change', {'speed': 1})
            elif event.ui_element == self.speed_2x_button:
                self.event_system.emit('time_speed_change', {'speed': 2})
            elif event.ui_element == self.speed_4x_button:
                self.event_system.emit('time_speed_change', {'speed': 4})
            elif event.ui_element == self.sell_corn_button:
                # Test selling corn from inventory
                self.event_system.emit('sell_crops_requested', {
                    'crop_type': 'corn',
                    'quantity': 10,
                    'price_per_unit': 5.0  # Use average price for testing
                })
            elif event.ui_element == self.buy_silo_button:
                # Purchase storage silo
                self.event_system.emit('purchase_building_requested', {
                    'building_id': 'storage_silo'
                })
            elif event.ui_element == self.hire_employee_button:
                # Request generation of new applicants for hiring
                print("DEBUG: Hire Employee button clicked - requesting applicant generation")
                self.event_system.emit('generate_applicants_requested', {})  # Request new applicants
            elif event.ui_element == self.view_applicants_button:
                # Show the applicant panel with current applicants
                print("DEBUG: View Applicants button clicked")
                self._show_applicant_panel()  # Create and display the applicant selection UI
            elif event.ui_element == self.view_payroll_button:
                # Request employee roster and payroll info
                self.event_system.emit('show_employee_roster_requested', {})
            elif (hasattr(self, 'close_applicant_panel_button') and 
                  event.ui_element == self.close_applicant_panel_button):
                print("DEBUG: Close applicant panel button clicked")  # Debug logging for panel close
                self._destroy_applicant_panel()  # Destroy the applicant selection panel
            elif event.ui_element == self.cancel_tasks_button:
                # Cancel tasks on selected tiles
                self.event_system.emit('cancel_tasks_requested', {})
            elif event.ui_element == self.crop_info_button:
                # Show crop information dialog
                self._show_crop_info_dialog()
            elif event.ui_element == self.quick_save_button:
                # Quick save current game
                self.event_system.emit('manual_save_requested', {
                    'save_name': f"Quick Save - Day {self._current_day}",
                    'slot': 0
                })
            elif event.ui_element == self.quick_load_button:
                # Quick load game
                self.event_system.emit('load_game_requested', {
                    'slot': 0
                })
            elif event.ui_element == self.save_menu_button:
                # Open save/load menu
                self._show_save_load_menu()
            # Handle applicant hire buttons (direct hire only)
            elif hasattr(event.ui_element, 'applicant_id') and hasattr(event.ui_element, 'action_type'):
                applicant_id = event.ui_element.applicant_id
                action_type = event.ui_element.action_type
                
                if action_type == 'direct_hire':
                    # Direct hire the selected applicant
                    self.event_system.emit('hire_applicant_requested', {'applicant_id': applicant_id})
                    self._destroy_applicant_panel()
            # Handle legacy applicant hire buttons (for backward compatibility)
            elif hasattr(event.ui_element, 'applicant_id'):
                # Legacy direct hire
                applicant_id = event.ui_element.applicant_id
                self.event_system.emit('hire_applicant_requested', {'applicant_id': applicant_id})
                self._destroy_applicant_panel()
            # Handle save/load slot buttons
            elif hasattr(event.ui_element, 'slot_id') and hasattr(event.ui_element, 'action_type'):
                slot_id = event.ui_element.slot_id
                action_type = event.ui_element.action_type
                
                if action_type == 'save':
                    self.event_system.emit('manual_save_requested', {
                        'save_name': f"Save Slot {slot_id} - Day {self._current_day}",
                        'slot': slot_id
                    })
                    self._destroy_save_load_menu()
                elif action_type == 'load':
                    self.event_system.emit('load_game_requested', {
                        'slot': slot_id
                    })
                    self._destroy_save_load_menu()
            # Handle save/load menu close button
            elif (hasattr(self, 'save_load_close_button') and 
                  event.ui_element == self.save_load_close_button):
                self._destroy_save_load_menu()
        
        # Handle dropdown selection changes
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.selected_crop_dropdown:
                # Update current crop selection based on dropdown choice
                selected_text = event.text
                for crop_id, crop_data in CROP_TYPES.items():
                    expected_text = f"{crop_data['name']} (${crop_data['seed_cost']})"
                    if selected_text == expected_text:
                        self.current_crop_type = crop_id
                        print(f"Selected crop type changed to: {crop_data['name']}")
                        break
        
        # Handle keyboard shortcuts
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.toggle_debug()
        
        # Forward mouse events to employee manager for tile selection
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # This will be handled by employee manager through game manager
            pass
    
    def update(self, dt):
        """Update UI elements"""
        self.gui_manager.update(dt)  # Update pygame-gui elements
        
        # No complex startup protection needed - panels are created dynamically
        
        # Update notifications
        self._update_notifications(dt)  # Handle notification display and timing
    
    def render(self, screen):
        """Render the UI"""
        # Render pygame-gui elements
        # No safety checks needed - panels are managed through creation/destruction
        
        self.gui_manager.draw_ui(screen)
        
        # Render debug info if enabled
        if self.show_debug:
            self._render_debug_info(screen)
        
        # Render notifications
        self._render_notifications(screen)
    
    def _render_debug_info(self, screen):
        """Render debug information overlay"""
        font = pygame.font.Font(None, 24)
        
        debug_lines = [
            f"FPS: {int(pygame.time.Clock().get_fps())}",
            f"Events queued: {self.event_system.get_queue_size()}",
            f"Grid size: {GRID_WIDTH}x{GRID_HEIGHT}",
            "Movement: Direct movement (performance optimized)",
            "Green lines = movement direction",
            "Yellow circles = movement targets",
        ]
        
        y_offset = WINDOW_HEIGHT - (len(debug_lines) * 25) - 10
        for i, line in enumerate(debug_lines):
            text_surface = font.render(line, True, COLORS['ui_text'])
            screen.blit(text_surface, (10, y_offset + i * 25))
    
    def _handle_time_update(self, event_data):
        """Handle time update events"""
        day = event_data.get('day', 1)
        hour = event_data.get('hour', 5)
        minute = event_data.get('minute', 0)
        
        # Format time display
        time_str = f"Day {day} - {hour:02d}:{minute:02d}"
        self.time_label.set_text(time_str)
    
    def _handle_money_update(self, event_data):
        """Handle money change events"""
        amount = event_data.get('amount', 0)
        color = 'money_positive' if amount >= 0 else 'money_negative'
        self.money_label.set_text(f"Cash: ${amount:,}")
    
    def _handle_inventory_update(self, event_data):
        """Handle inventory change events"""
        crop_type = event_data.get('crop_type', 'corn')
        total_quantity = event_data.get('total_quantity', 0)
        storage_capacity = event_data.get('storage_capacity', 100)
        
        if crop_type == 'corn':
            self.inventory_label.set_text(f"Corn: {total_quantity}/{storage_capacity}")
    
    def toggle_debug(self):
        """Toggle debug info display"""
        self.show_debug = not self.show_debug
    
    def _show_crop_info_dialog(self):
        """Show detailed crop information dialog"""
        crop_data = CROP_TYPES[self.current_crop_type]
        
        # Create crop info text with detailed stats
        info_text = f"<b>{crop_data['name']}</b><br>"
        info_text += f"{crop_data['description']}<br><br>"
        info_text += f"<b>Stats:</b><br>"
        info_text += f"Growth Time: {crop_data['growth_time'] * 24:.1f} hours<br>"
        info_text += f"Seed Cost: ${crop_data['seed_cost']}<br>"
        info_text += f"Base Yield: {crop_data['base_yield']} units/tile<br>"
        info_text += f"Price Range: ${crop_data['price_min']}-${crop_data['price_max']}/unit<br><br>"
        info_text += f"<b>Profitability:</b><br>"
        min_profit = (crop_data['base_yield'] * crop_data['price_min']) - crop_data['seed_cost']
        max_profit = (crop_data['base_yield'] * crop_data['price_max']) - crop_data['seed_cost']
        info_text += f"Potential Profit: ${min_profit}-${max_profit}/tile"
        
        # Create temporary info window
        if not hasattr(self, 'crop_info_window'):
            self.crop_info_window = pygame_gui.elements.UIWindow(
                rect=pygame.Rect(WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 - 150, 400, 300),
                window_display_title=f"{crop_data['name']} Information",
                manager=self.gui_manager
            )
            
            self.crop_info_textbox = pygame_gui.elements.UITextBox(
                relative_rect=pygame.Rect(10, 10, 380, 230),
                html_text=info_text,
                manager=self.gui_manager,
                container=self.crop_info_window
            )
            
            self.crop_info_close_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(300, 250, 80, 30),
                text="Close",
                manager=self.gui_manager,
                container=self.crop_info_window
            )
    
    def _show_save_load_menu(self):
        """Show save/load menu with multiple slots"""
        if hasattr(self, 'save_load_window'):
            return  # Already open
        
        self.save_load_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect(WINDOW_WIDTH//2 - 300, WINDOW_HEIGHT//2 - 200, 600, 400),
            window_display_title="Save/Load Game",
            manager=self.gui_manager
        )
        
        # Create save slots
        self.save_slots = []
        for i in range(5):  # 5 save slots
            slot_y = 50 + i * 60
            
            # Slot label
            slot_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, slot_y, 80, 25),
                text=f"Slot {i+1}:",
                manager=self.gui_manager,
                container=self.save_load_window
            )
            
            # Save button
            save_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(100, slot_y, 80, 25),
                text="Save",
                manager=self.gui_manager,
                container=self.save_load_window
            )
            save_button.slot_id = i + 1
            save_button.action_type = 'save'
            
            # Load button  
            load_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(185, slot_y, 80, 25),
                text="Load",
                manager=self.gui_manager,
                container=self.save_load_window
            )
            load_button.slot_id = i + 1
            load_button.action_type = 'load'
            
            # Save info label
            info_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(275, slot_y, 250, 25),
                text="Empty Slot",
                manager=self.gui_manager,
                container=self.save_load_window
            )
            
            self.save_slots.append({
                'save_button': save_button,
                'load_button': load_button,
                'info_label': info_label
            })
        
        # Close button
        self.save_load_close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(520, 350, 60, 30),
            text="Close",
            manager=self.gui_manager,
            container=self.save_load_window
        )
        
        # Load save information
        self._update_save_slot_info()
    
    def _update_save_slot_info(self):
        """Update save slot information display"""
        # This would get save info from the save manager
        # For now, just show placeholder text
        for i, slot in enumerate(self.save_slots):
            slot['info_label'].set_text("Empty Slot")
    
    def _destroy_save_load_menu(self):
        """Close and destroy save/load menu"""
        if hasattr(self, 'save_load_window'):
            self.save_load_window.kill()
            delattr(self, 'save_load_window')
            delattr(self, 'save_slots')
            delattr(self, 'save_load_close_button')
    
    def _handle_crop_type_request(self, event_data):
        """Handle request for current crop type selection"""
        self.event_system.emit('crop_type_provided', {
            'crop_type': self.current_crop_type
        })
    
    def _add_notification(self, message: str, notification_type: str = "info"):
        """Add a notification to display"""
        self.notifications.append({
            'message': message,
            'type': notification_type,
            'timer': 3.0,  # Show for 3 seconds
            'alpha': 255
        })
        
        # Limit to 5 notifications max
        if len(self.notifications) > 5:
            self.notifications.pop(0)
    
    def _update_notifications(self, dt: float):
        """Update notification timers and fade"""
        for notification in self.notifications[:]:
            notification['timer'] -= dt
            
            # Start fading in last 0.5 seconds
            if notification['timer'] < 0.5:
                notification['alpha'] = int((notification['timer'] / 0.5) * 255)
            
            # Remove expired notifications
            if notification['timer'] <= 0:
                self.notifications.remove(notification)
    
    def _render_notifications(self, screen):
        """Render notifications on screen"""
        if not self.notifications:
            return
        
        font = pygame.font.Font(None, 28)
        
        for i, notification in enumerate(self.notifications):
            # Choose color based on type
            if notification['type'] == 'success':
                color = (100, 255, 100)
            elif notification['type'] == 'error':
                color = (255, 100, 100)
            else:  # info
                color = (100, 200, 255)
            
            # Create text surface with alpha
            text_surface = font.render(notification['message'], True, color)
            text_surface.set_alpha(notification['alpha'])
            
            # Position notification
            x = WINDOW_WIDTH // 2 - text_surface.get_width() // 2
            y = 80 + i * 35
            
            # Background with alpha
            bg_rect = pygame.Rect(x - 10, y - 5, text_surface.get_width() + 20, text_surface.get_height() + 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(notification['alpha'] // 3)
            bg_surface.fill((0, 0, 0))
            screen.blit(bg_surface, bg_rect)
            
            # Text
            screen.blit(text_surface, (x, y))
    
    def _handle_task_feedback(self, event_data):
        """Handle successful task assignment feedback"""
        task_type = event_data.get('task_type', 'task')
        assigned_count = event_data.get('assigned_count', 0)
        employee_name = event_data.get('employee_name', 'Employee')
        
        if task_type == 'cancel':
            message = f"[CANCELLED] {employee_name}: {assigned_count} tasks cancelled"
        else:
            message = f"[SUCCESS] {employee_name}: {task_type.title()} assigned to {assigned_count} tiles"
        self._add_notification(message, "success")
    
    def _handle_task_failure(self, event_data):
        """Handle failed task assignment feedback"""
        reason = event_data.get('reason', 'unknown')
        message = event_data.get('message', 'Task assignment failed')
        
        # Customize message based on reason
        if reason == 'no_selection':
            display_message = "[WARNING] Select tiles first, then use T/P/H keys"
        elif reason == 'no_available_employees':
            display_message = "[WARNING] No available employees for task"
        elif reason == 'no_valid_tiles':
            task_type = event_data.get('task_type', 'task')
            display_message = f"[WARNING] No tiles are ready for {task_type} task"
        else:
            display_message = f"[WARNING] {message}"
        
        self._add_notification(display_message, "error")
    
    def _handle_building_purchase(self, event_data):
        """Handle successful building purchase feedback"""
        building_name = event_data.get('building_name', 'Building')
        cost = event_data.get('cost', 0)
        total_owned = event_data.get('total_owned', 1)
        
        message = f"[SUCCESS] Purchased {building_name} for ${cost} (Total: {total_owned})"
        self._add_notification(message, "success")
    
    def _handle_purchase_failure(self, event_data):
        """Handle failed building purchase feedback"""
        reason = event_data.get('reason', 'unknown')
        building_id = event_data.get('building_id', 'building')
        
        if reason == 'insufficient_funds':
            message = "[WARNING] Not enough money for storage silo"
        elif reason == 'max_quantity_reached':
            message = "[WARNING] Maximum storage silos already built"
        else:
            message = f"[WARNING] Cannot purchase {building_id}"
        
        self._add_notification(message, "error")
    
    def _handle_storage_upgrade(self, event_data):
        """Handle storage capacity upgrades"""
        new_capacity = event_data.get('new_capacity', 100)
        # Update display to show new capacity (with current corn count)
        current_text = self.inventory_label.text
        if ':' in current_text:
            corn_part = current_text.split('/')[0]  # Get "Corn: X" part
            self.inventory_label.set_text(f"{corn_part}/{new_capacity}")
    
    def _handle_applicants_generated(self, event_data):
        """Handle when job applicants are generated"""
        applicants = event_data.get('applicants', [])
        count = event_data.get('count', 0)
        
        print(f"DEBUG: _handle_applicants_generated called with {count} applicants")
        
        # No startup protection needed with dynamic panel creation
        
        # Store applicants for in-game UI
        self.current_applicants = applicants
        
        if applicants:
            self._add_notification(f"[APPLICANTS] {count} job applicants available! Use 'View Applicants' to hire.", "info")
            
            # Optional: Still print to console for debug purposes (with safe encoding)
            try:
                print(f"\n=== JOB APPLICANTS ({count}) ===")
                for i, app in enumerate(applicants, 1):
                    trait_display = ', '.join([trait.replace('_', ' ').title() for trait in app.traits])
                    print(f"{i}. {app.name} (Age {app.age}) - ${app.hiring_cost} hiring, ${app.daily_wage}/day")
                    print(f"   Traits: {trait_display}, Type: {app.personality_type.title()}")
                print("Use 'View Applicants' button to hire via in-game UI!\n")
            except UnicodeEncodeError:
                print(f"\n=== {count} JOB APPLICANTS AVAILABLE === (Use 'View Applicants' button to hire)\n")
    
    def _handle_employee_hired(self, event_data):
        """Handle successful employee hiring"""
        name = event_data.get('applicant_name', 'Employee')
        hiring_cost = event_data.get('hiring_cost', 0)
        daily_wage = event_data.get('daily_wage', 0)
        traits = event_data.get('traits', [])
        
        traits_text = f" ({', '.join(traits)})" if traits else ""
        message = f"[HIRED] {name} for ${hiring_cost}! Wage: ${daily_wage}/day{traits_text}"
        self._add_notification(message, "success")
    
    def _handle_hire_failure(self, event_data):
        """Handle failed hiring attempts"""
        reason = event_data.get('reason', 'unknown')
        name = event_data.get('applicant_name', 'applicant')
        
        if reason == 'insufficient_funds':
            required = event_data.get('required_cost', 0)
            available = event_data.get('current_balance', 0)
            message = f"[FUNDS] Cannot hire {name} - Need ${required}, have ${available}"
        else:
            message = f"[ERROR] Failed to hire {name}"
        
        self._add_notification(message, "error")
    
    def _handle_roster_request(self, event_data):
        """Handle request to show employee roster and payroll"""
        # Request employee info from the employee manager
        self.event_system.emit('get_employee_roster', {'include_payroll': True})
    
    def _handle_roster_displayed(self, event_data):
        """Handle when employee roster is displayed"""
        employee_count = event_data.get('employee_count', 0)
        total_cost = event_data.get('total_daily_cost', 0)
        
        if employee_count == 0:
            message = "[ROSTER] No employees hired yet - Use 'Hire Employee' to recruit workers!"
        else:
            message = f"[ROSTER] {employee_count} employees - ${total_cost}/day payroll (Check console for details)"
        
        self._add_notification(message, "info")
    
    def _handle_employee_count_change(self, event_data):
        """Handle changes in employee count for UI display"""
        # Request updated count from employee manager
        self.event_system.emit('get_employee_count_for_ui', {})
    
    def _handle_employee_count_update(self, event_data):
        """Update employee count display in UI"""
        count = event_data.get('count', 0)
        self.employee_count_label.set_text(f"Workers: {count}")
    
    def _show_applicant_panel(self):
        """Create and show the applicant selection panel"""
        print("DEBUG: _show_applicant_panel called - checking applicants")
            
        if not self.current_applicants:
            self._add_notification("[INFO] No applicants available - Use 'Hire Employee' to generate candidates", "info")
            print("DEBUG: No applicants available, not showing panel")
            return
        
        print(f"DEBUG: Creating applicant panel with {len(self.current_applicants)} applicants")
        self._create_applicant_panel()
        self._populate_applicant_panel()
    
    def _destroy_applicant_panel(self):
        """Completely destroy the applicant selection panel"""
        if self._applicant_panel_exists and hasattr(self, 'applicant_panel'):
            # Clear all table data first
            self._clear_applicant_table()
            
            # Destroy all child elements
            if hasattr(self, 'header_labels'):
                for label in self.header_labels:
                    label.kill()
                self.header_labels.clear()
            
            # Destroy major child panels and elements
            if hasattr(self, 'applicant_panel_title'):
                self.applicant_panel_title.kill()
            if hasattr(self, 'sort_label'):
                self.sort_label.kill()
            if hasattr(self, 'sort_dropdown'):
                self.sort_dropdown.kill()
            if hasattr(self, 'table_header_panel'):
                self.table_header_panel.kill()
            if hasattr(self, 'applicant_table_container'):
                self.applicant_table_container.kill()
            if hasattr(self, 'close_applicant_panel_button'):
                self.close_applicant_panel_button.kill()
            
            # Finally destroy the main panel
            self.applicant_panel.kill()
            self.applicant_panel = None
            
            # Reset state flags
            self._applicant_panel_exists = False
            print("DEBUG: Applicant panel destroyed completely")
        else:
            print("DEBUG: Warning - applicant_panel doesn't exist when trying to destroy")
    
    def _populate_applicant_panel(self):
        """Populate the applicant panel with current applicants in table format"""
        self._clear_applicant_table()
        
        if not self.current_applicants:
            return
        
        # Sort applicants based on current sort mode
        sorted_applicants = self._sort_applicants(self.current_applicants)
        
        # Create table rows for each applicant
        row_height = 60
        for i, applicant in enumerate(sorted_applicants):
            y_pos = i * (row_height + 5)
            
            # Create row panel
            row_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(0, y_pos, 770, row_height),
                manager=self.gui_manager,
                container=self.applicant_table_container
            )
            
            # Create table cells
            self._create_table_row(row_panel, applicant, i)
            self.applicant_table_rows.append(row_panel)
    
    def _create_table_row(self, row_panel, applicant, row_index):
        """Create individual table row with applicant data"""
        # Name column (position: 0, width: 95)
        name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 5, 90, 25),
            text=applicant.name,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Age column (position: 95, width: 45)
        age_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(100, 5, 40, 25),
            text=str(applicant.age),
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Skills column (position: 140, width: 110)
        skills_text = ', '.join([trait.replace('_', ' ').title() for trait in applicant.traits[:2]])
        skills_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(145, 5, 105, 25),
            text=skills_text,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Traits column (position: 250, width: 90) - show ??? for hidden traits
        traits_display = self._format_traits_for_table(applicant)
        traits_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(255, 5, 85, 25),
            text=traits_display,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Previous Job column (position: 340, width: 90)
        prev_job = getattr(applicant, 'previous_job', 'Student')
        job_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(345, 5, 85, 25),
            text=prev_job,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Applied For column (position: 430, width: 75)
        farm_name = getattr(applicant, 'applied_for_farm', 'Farm 1')
        farm_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(435, 5, 70, 25),
            text=farm_name,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Cost column (position: 505, width: 65)
        cost_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(510, 5, 60, 25),
            text=f"${applicant.hiring_cost}",
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Expires column (position: 570, width: 70) - NEW
        expires_text = self._format_expiration_for_table(applicant)
        expires_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(575, 5, 65, 25),
            text=expires_text,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Action button (position: 640, width: 150) - Direct hiring only
        hire_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(645, 5, 140, 25),
            text="Hire Now",
            manager=self.gui_manager,
            container=row_panel
        )
        hire_button.applicant_id = applicant.id
        hire_button.action_type = 'direct_hire'
        
        # Store button for event handling
        self.applicant_buttons.append(hire_button)
    
    def _clear_applicant_table(self):
        """Clear all applicant table rows and buttons"""
        for row in self.applicant_table_rows:
            row.kill()
        self.applicant_table_rows.clear()
        
        for button in self.applicant_buttons:
            button.kill()
        self.applicant_buttons.clear()
    
    def _clear_applicant_buttons(self):
        """Compatibility method - calls new table clearing method"""
        self._clear_applicant_table()
    
    def _format_traits_for_table(self, applicant):
        """Format traits for table display with ??? for hidden traits"""
        # Use the new trait hiding system
        revealed_traits = getattr(applicant, 'revealed_traits', [])
        hidden_traits = getattr(applicant, 'hidden_traits', [])
        
        # Format revealed traits
        revealed_text = ', '.join([trait.replace('_', ' ').title() for trait in revealed_traits[:2]])
        
        # Add ??? for hidden traits
        if hidden_traits:
            if revealed_text:
                return revealed_text + ', ???'
            else:
                return '???'
        else:
            return revealed_text if revealed_text else 'None'
    
    def _sort_applicants(self, applicants):
        """Sort applicants based on current sort mode"""
        if self.current_sort_mode == "cost_low_high":
            return sorted(applicants, key=lambda a: a.hiring_cost)
        elif self.current_sort_mode == "cost_high_low":
            return sorted(applicants, key=lambda a: a.hiring_cost, reverse=True)
        elif self.current_sort_mode == "name_a_z":
            return sorted(applicants, key=lambda a: a.name)
        elif self.current_sort_mode == "age_young_old":
            return sorted(applicants, key=lambda a: a.age)
        else:
            return applicants
    
    def _handle_sort_change(self):
        """Handle sort dropdown selection change"""
        selected = self.sort_dropdown.selected_option
        sort_mapping = {
            "Cost (Low-High)": "cost_low_high",
            "Cost (High-Low)": "cost_high_low",
            "Name (A-Z)": "name_a_z",
            "Age (Young-Old)": "age_young_old"
        }
        
        self.current_sort_mode = sort_mapping.get(selected, "cost_low_high")
        self._populate_applicant_panel()  # Refresh table with new sorting
    
    # Interview system removed - using Simple Hiring System for direct hiring
    
    def _format_applicant_info(self, applicant):
        """Format applicant information for display button"""
        traits_text = ', '.join([trait.replace('_', ' ').title() for trait in applicant.traits])
        return f"{applicant.name} (Age {applicant.age}) - ${applicant.hiring_cost} hiring, ${applicant.daily_wage}/day\nTraits: {traits_text}\nType: {applicant.personality_type.title()}"
    
    def _handle_employee_status_update(self, event_data):
        """Handle real-time employee status updates"""
        employees = event_data.get('employees', [])
        
        if not employees:
            self.employee_status_display.set_text("<font size=2>No employees</font>")
            return
        
        status_lines = []
        for emp in employees[:4]:  # Show up to 4 employees
            state = emp.get('state', 'idle').replace('_', ' ').title()
            task = emp.get('current_task', 'None')
            if task and task != 'None':
                task = task.title()
            else:
                task = 'Idle'
            
            status_lines.append(f"<b>{emp.get('name', 'Unknown')}</b>: {task}")
        
        if len(employees) > 4:
            status_lines.append(f"<i>...and {len(employees) - 4} more</i>")
        
        status_html = f"<font size=2>{'<br>'.join(status_lines)}</font>"
        self.employee_status_display.set_text(status_html)
    
    # Interview system completely removed - using Simple Hiring System
    
    def _refresh_applicant_panel(self):
        """Refresh the applicant panel to show updated information"""
        if self._applicant_panel_exists and self.current_applicants:
            # Clear existing table and regenerate with updated data
            self._clear_applicant_table()  # Clear existing table rows and buttons
            self._populate_applicant_panel()  # Regenerate table with current applicant data
            print("Applicant panel refreshed with latest data")
    
    def _handle_day_passed(self, event_data):
        """Handle day progression for UI updates"""
        self._current_day = event_data.get('new_day', self._current_day + 1)
        
        # Refresh applicant panel if it exists to update expiration times
        if self._applicant_panel_exists and self.current_applicants:
            self._refresh_applicant_panel()
    
    def _format_expiration_for_table(self, applicant):
        """Format expiration information for table display"""
        if not hasattr(applicant, 'expiration_day') or applicant.expiration_day <= 0:
            return "No limit"
        
        days_left = applicant.expiration_day - self._current_day
        
        if days_left <= 0:
            return "Expired"
        elif days_left == 1:
            return "1 day"
        else:
            return f"{days_left} days"
    
    # All old startup protection and consistency checking methods removed
    # Panel management is now handled through dynamic creation/destruction