"""
Hire Interface - Professional employee hiring modal matching reference design
Integrates with the existing SimpleHiringSystem to provide a comprehensive hiring experience.

Features:
- Professional table layout matching reference design
- Search and filter functionality (Farm 1, Main Skill dropdown)
- Skills and traits display with expandable columns
- Direct integration with SimpleHiringSystem
- "Begin Search" button to generate new applicants
- Individual "Hire" buttons for each applicant
- Professional styling with green theme matching reference
"""

import pygame
import pygame_gui
from typing import Dict, Any, Optional, List
from scripts.core.config import *


class HireInterface:
    """Professional hire interface modal with table layout and search functionality"""
    
    def __init__(self, gui_manager, event_system, screen_width: int, screen_height: int):
        """Initialize the hire interface modal"""
        self.gui_manager = gui_manager  # pygame_gui manager for UI elements
        self.event_system = event_system  # Event system for communication
        self.screen_width = screen_width  # Screen width for positioning
        self.screen_height = screen_height  # Screen height for positioning
        
        # Modal configuration
        self.modal_width = 800  # Width of hire modal
        self.modal_height = 600  # Height of hire modal
        self.modal_x = (screen_width - self.modal_width) // 2  # Center horizontally
        self.modal_y = (screen_height - self.modal_height) // 2  # Center vertically
        
        # UI elements storage
        self.window = None  # Main modal window
        self.search_section = {}  # Search controls (Farm dropdown, Main Skill dropdown, Begin Search button)
        self.table_section = {}  # Table elements (headers, rows, scrollable area)
        self.current_applicants = []  # List of current applicants to display
        
        # Table configuration
        self.table_headers = ["Name", "Age", "Previous Job", "Applied Farm", "Salary", "Expires", "Actions", "List of Skills", "List of Traits"]
        self.table_y_offset = 120  # Space for search section above table
        self.row_height = 35  # Height of each table row
        self.column_widths = [100, 40, 100, 100, 80, 70, 70, 140, 140]  # Width of each column
        
        # Set up event subscriptions
        self._setup_event_handlers()
        
        print("Hire Interface initialized with professional table layout")
    
    def _setup_event_handlers(self):
        """Set up event handlers for hire interface interactions"""
        # Subscribe to hiring system events
        self.event_system.subscribe('applicants_generated', self._handle_applicants_received)
        self.event_system.subscribe('employee_hired_successfully', self._handle_employee_hired)
        self.event_system.subscribe('hire_failed', self._handle_hire_failed)
    
    def show_modal(self):
        """Show the hire interface modal"""
        if self.window:
            return  # Already open
        
        try:
            # Create main modal window with green theme
            self.window = pygame_gui.elements.UIWindow(
                rect=pygame.Rect(self.modal_x, self.modal_y, self.modal_width, self.modal_height),
                manager=self.gui_manager,
                window_display_title="Hire Employees"
            )
            
            # Create search section at top of modal
            self._create_search_section()
            
            # Create table section below search
            self._create_table_section()
            
            # Don't auto-generate applicants - wait for user to click "Begin Search"
            # self.event_system.emit('generate_applicants_requested', {})
            
            print("Hire interface modal opened")
            
        except Exception as e:
            print(f"Error opening hire interface: {e}")
            self._cleanup_modal()
            # Re-raise the exception so the submenu knows it failed
            raise e
    
    def _create_search_section(self):
        """Create the search and filter controls at the top of the modal"""
        # Search label
        search_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 20, 150, 25),
            text="Search for employees:",
            manager=self.gui_manager,
            container=self.window
        )
        
        # Farm dropdown (For Farm: Farm 1)
        farm_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 50, 70, 25),
            text="For Farm:",
            manager=self.gui_manager,
            container=self.window
        )
        
        farm_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(95, 50, 100, 25),
            options_list=["Farm 1"],  # Only Farm 1 available for now
            starting_option="Farm 1",
            manager=self.gui_manager,
            container=self.window
        )
        
        # Main Skill dropdown
        skill_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(210, 50, 70, 25),
            text="Main Skill:",
            manager=self.gui_manager,
            container=self.window
        )
        
        skill_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(285, 50, 120, 25),
            options_list=["Manual Labor", "Agricultural", "Management", "Technical"],
            starting_option="Manual Labor",
            manager=self.gui_manager,
            container=self.window
        )
        
        # Begin Search button
        begin_search_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(420, 50, 100, 25),
            text="Begin Search",
            manager=self.gui_manager,
            container=self.window
        )
        
        # Store references for event handling
        self.search_section = {
            'farm_dropdown': farm_dropdown,
            'skill_dropdown': skill_dropdown,
            'begin_search_button': begin_search_button
        }
    
    def _create_table_section(self):
        """Create the applicant table with headers and scrollable content"""
        # Create table header row
        header_y = self.table_y_offset
        current_x = 20  # Starting X position for first column
        
        header_elements = []
        for i, header_text in enumerate(self.table_headers):
            column_width = self.column_widths[i]
            
            # Create header label with professional styling
            header_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(current_x, header_y, column_width, 30),
                text=header_text,
                manager=self.gui_manager,
                container=self.window
            )
            
            header_elements.append(header_label)
            current_x += column_width + 5  # Move to next column position
        
        # Create scrollable area for table rows
        table_content_y = header_y + 35  # Below header
        table_content_height = self.modal_height - table_content_y - 50  # Leave space at bottom
        
        self.table_scrollable_area = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(20, table_content_y, self.modal_width - 60, table_content_height),
            manager=self.gui_manager,
            container=self.window
        )
        
        # Store references
        self.table_section = {
            'headers': header_elements,
            'scrollable_area': self.table_scrollable_area,
            'rows': []  # Will be populated when applicants are received
        }
    
    def _handle_applicants_received(self, event_data: Dict[str, Any]):
        """Handle new applicants from the hiring system"""
        if not self.window:
            return  # Modal not open
        
        # Store applicants and refresh table
        self.current_applicants = event_data.get('applicants', [])
        self._refresh_table()
        
        print(f"Received {len(self.current_applicants)} applicants for hire interface")
    
    def _refresh_table(self):
        """Refresh the table with current applicants"""
        # Clear existing table rows
        self._clear_table_rows()
        
        # Create new rows for current applicants
        for i, applicant in enumerate(self.current_applicants):
            self._create_applicant_row(applicant, i)
    
    def _clear_table_rows(self):
        """Clear all existing table rows"""
        for row_elements in self.table_section.get('rows', []):
            for element in row_elements:
                element.kill()  # Remove from pygame_gui
        
        self.table_section['rows'] = []  # Clear the list
    
    def _create_applicant_row(self, applicant, row_index: int):
        """Create a table row for a single applicant"""
        row_y = row_index * (self.row_height + 5)  # Position within scrollable area
        current_x = 10  # Starting X position within scrollable container
        
        row_elements = []
        
        # Column data based on applicant information
        column_data = [
            applicant.name,  # Name
            str(applicant.age),  # Age
            applicant.previous_job,  # Previous Job
            "Farm 1",  # Applied Farm (always Farm 1 for now)
            f"${applicant.daily_wage}/day",  # Salary
            "5 days",  # Expires (static for now)
            "",  # Actions (will be hire button)
            ", ".join(applicant.traits),  # List of Skills (using traits)
            applicant.personality_type  # List of Traits (using personality)
        ]
        
        # Create each column element
        for i, (data, width) in enumerate(zip(column_data, self.column_widths)):
            if i == 6:  # Actions column - create hire button
                hire_button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(current_x, row_y, width, self.row_height),
                    text="Hire",
                    manager=self.gui_manager,
                    container=self.table_scrollable_area
                )
                # Store applicant ID in button for event handling
                hire_button.applicant_id = applicant.id
                row_elements.append(hire_button)
            else:
                # Regular text label
                label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(current_x, row_y, width, self.row_height),
                    text=data,
                    manager=self.gui_manager,
                    container=self.table_scrollable_area
                )
                row_elements.append(label)
            
            current_x += width + 5  # Move to next column
        
        # Store row elements for cleanup
        self.table_section['rows'].append(row_elements)
    
    def handle_button_click(self, button_element) -> bool:
        """Handle button clicks within the hire interface"""
        # Check if it's the Begin Search button
        if button_element == self.search_section.get('begin_search_button'):
            # Request new applicants from hiring system
            self.event_system.emit('generate_applicants_requested', {})
            print("Begin Search clicked - requesting new applicants")
            return True
        
        # Check if it's a hire button
        if hasattr(button_element, 'applicant_id'):
            applicant_id = button_element.applicant_id
            # Request to hire this specific applicant
            self.event_system.emit('hire_applicant_requested', {'applicant_id': applicant_id})
            print(f"Hire button clicked for applicant: {applicant_id}")
            return True
        
        return False  # Button not handled by this interface
    
    def _handle_employee_hired(self, event_data: Dict[str, Any]):
        """Handle successful employee hiring"""
        applicant_name = event_data.get('applicant_name', 'Unknown')
        hiring_cost = event_data.get('hiring_cost', 0)
        
        print(f"Employee {applicant_name} hired successfully for ${hiring_cost}")
        
        # Refresh the table to remove the hired applicant
        # (The hiring system automatically removes them from the available list)
        self._refresh_table()
    
    def _handle_hire_failed(self, event_data: Dict[str, Any]):
        """Handle failed hiring attempts"""
        applicant_name = event_data.get('applicant_name', 'Unknown')
        error = event_data.get('error', 'Unknown error')
        
        print(f"Failed to hire {applicant_name}: {error}")
        
        # Could show an error message to the user here
        # For now, just log the error
    
    def close_modal(self):
        """Close the hire interface modal"""
        self._cleanup_modal()
    
    def _cleanup_modal(self):
        """Clean up all modal UI elements"""
        try:
            # Clear table rows first
            self._clear_table_rows()
            
            # Clear search section elements
            for element in self.search_section.values():
                if element:
                    element.kill()
            self.search_section.clear()
            
            # Clear table section elements
            for element in self.table_section.get('headers', []):
                element.kill()
            if 'scrollable_area' in self.table_section:
                self.table_section['scrollable_area'].kill()
            self.table_section.clear()
            
            # Close main window
            if self.window:
                self.window.kill()
                self.window = None
            
            # Clear applicant data
            self.current_applicants.clear()
            
            print("Hire interface modal closed and cleaned up")
            
        except Exception as e:
            print(f"Error during hire interface cleanup: {e}")
    
    def is_open(self) -> bool:
        """Check if the hire interface modal is currently open"""
        return self.window is not None
    
    def handle_window_close(self, window_element) -> bool:
        """Handle window close events"""
        if window_element == self.window:
            self.close_modal()
            return True
        return False