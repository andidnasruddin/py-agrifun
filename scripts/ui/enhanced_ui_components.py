"""
Enhanced UI Components - Professional UI system for farming simulation
Provides comprehensive farm information display and management interface.

This module implements the UI overhaul with:
- Professional top HUD with real-time farm data integration
- Dynamic right panel system for context-sensitive information
- Enhanced visual design and layout management
- Integration with all existing game systems (weather, employees, economy, etc.)
"""

import pygame
import pygame_gui
from typing import Dict, Any, Optional, List
from scripts.core.config import *


class EnhancedTopHUD:
    """Professional top HUD showing comprehensive farm information"""
    
    def __init__(self, gui_manager, event_system, screen_width=WINDOW_WIDTH):
        """Initialize the enhanced top HUD system"""
        self.gui_manager = gui_manager  # Reference to pygame-gui manager
        self.event_system = event_system  # Reference to game event system
        self.screen_width = screen_width  # Screen width for responsive layout
        
        # Data state for real-time updates
        self.farm_data = {
            'farm_name': 'My Farm',  # Default farm name
            'date': 'Day 1',        # Current game date
            'time': '5:00 AM',      # Current game time
            'season': 'Spring',     # Current season
            'weather': 'Clear',     # Current weather condition
            'weather_effect': '0%', # Weather growth effect
            'employee_count': 1,    # Number of employees
            'cash': 0,             # Current cash amount
            'cash_trend': '±0',    # Cash change indicator
            'inventory_summary': 'Empty'  # Inventory quick summary
        }
        
        # HUD layout configuration
        self.hud_height = 80  # Increased height for comprehensive information
        self.section_spacing = 15  # Space between information sections
        
        # Create the enhanced HUD elements
        self._create_enhanced_hud()
        
        # Subscribe to relevant events for real-time updates
        self._setup_event_subscriptions()
        
        print("Enhanced Top HUD initialized with comprehensive farm information display")
    
    def _create_enhanced_hud(self):
        """Create the comprehensive top HUD with all farm information"""
        # Main HUD panel with professional styling
        self.hud_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, self.screen_width, self.hud_height),
            manager=self.gui_manager
        )
        
        # Set professional styling for the HUD panel
        try:
            self.hud_panel.background_colour = pygame.Color(20, 20, 20)  # Dark professional background
            self.hud_panel.border_colour = pygame.Color(80, 80, 80)      # Subtle border
            self.hud_panel.border_width = 2
        except AttributeError:
            pass  # Use pygame-gui defaults if direct styling unavailable
        
        # Calculate section widths for responsive layout
        total_sections = 6  # Farm name, date/time, season/weather, employees, cash, inventory
        section_width = (self.screen_width - (total_sections + 1) * self.section_spacing) // total_sections
        
        # Section 1: Farm Name and Identity
        x_pos = self.section_spacing
        self.farm_name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x_pos, 10, section_width, 25),
            text=self.farm_data['farm_name'],
            manager=self.gui_manager,
            container=self.hud_panel
        )
        
        # Section 2: Date and Time Information
        x_pos += section_width + self.section_spacing
        self.date_time_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x_pos, 10, section_width, 25),
            text=f"{self.farm_data['date']} - {self.farm_data['time']}",
            manager=self.gui_manager,
            container=self.hud_panel
        )
        
        # Section 3: Season and Weather Information
        x_pos += section_width + self.section_spacing
        self.season_weather_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x_pos, 10, section_width, 25),
            text=f"{self.farm_data['season']} | {self.farm_data['weather']}",
            manager=self.gui_manager,
            container=self.hud_panel
        )
        
        # Weather effect indicator (second line for season/weather section)
        self.weather_effect_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x_pos, 35, section_width, 20),
            text=f"Growth: {self.farm_data['weather_effect']}",
            manager=self.gui_manager,
            container=self.hud_panel
        )
        
        # Section 4: Employee Information
        x_pos += section_width + self.section_spacing
        self.employee_info_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x_pos, 10, section_width, 25),
            text=f"Employees: {self.farm_data['employee_count']}",
            manager=self.gui_manager,
            container=self.hud_panel
        )
        
        # Section 5: Financial Information
        x_pos += section_width + self.section_spacing
        self.cash_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x_pos, 10, section_width, 25),
            text=f"Cash: ${self.farm_data['cash']:,}",
            manager=self.gui_manager,
            container=self.hud_panel
        )
        
        # Cash trend indicator (second line for financial section)
        self.cash_trend_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x_pos, 35, section_width, 20),
            text=self.farm_data['cash_trend'],
            manager=self.gui_manager,
            container=self.hud_panel
        )
        
        # Section 6: Inventory Quick Summary
        x_pos += section_width + self.section_spacing
        self.inventory_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x_pos, 10, section_width, 25),
            text=f"Storage: {self.farm_data['inventory_summary']}",
            manager=self.gui_manager,
            container=self.hud_panel
        )
        
        print("Enhanced Top HUD elements created with comprehensive farm information display")
    
    def _setup_event_subscriptions(self):
        """Subscribe to relevant game events for real-time HUD updates"""
        # Time and date updates
        self.event_system.subscribe('time_updated', self._handle_time_update)
        
        # Financial updates
        self.event_system.subscribe('money_changed', self._handle_money_update)
        self.event_system.subscribe('transaction_added', self._handle_transaction_update)
        
        # Weather and season updates
        self.event_system.subscribe('weather_updated', self._handle_weather_update)
        self.event_system.subscribe('season_changed', self._handle_season_update)
        
        # Employee updates
        self.event_system.subscribe('employee_hired', self._handle_employee_update)
        self.event_system.subscribe('employee_count_changed', self._handle_employee_count_update)
        
        # Inventory updates
        self.event_system.subscribe('inventory_updated', self._handle_inventory_update)
        self.event_system.subscribe('full_inventory_status', self._handle_full_inventory_update)
        
        # Farm identity updates (for future farm naming features)
        self.event_system.subscribe('farm_name_changed', self._handle_farm_name_update)
        
        print("Enhanced Top HUD event subscriptions established")
    
    def _handle_time_update(self, event_data):
        """Handle time and date updates from the time manager"""
        # Extract time information from event data
        day = event_data.get('day', 1)
        hour = event_data.get('hour', 5)
        minute = event_data.get('minute', 0)
        
        # Format time display (12-hour format with AM/PM)
        if hour == 0:
            time_str = f"12:{minute:02d} AM"
        elif hour < 12:
            time_str = f"{hour}:{minute:02d} AM"
        elif hour == 12:
            time_str = f"12:{minute:02d} PM"
        else:
            time_str = f"{hour-12}:{minute:02d} PM"
        
        # Update internal data
        self.farm_data['date'] = f"Day {day}"
        self.farm_data['time'] = time_str
        
        # Update HUD display
        self.date_time_label.set_text(f"{self.farm_data['date']} - {self.farm_data['time']}")
    
    def _handle_money_update(self, event_data):
        """Handle cash amount updates from the economy manager"""
        new_amount = event_data.get('amount', 0)
        old_amount = self.farm_data['cash']
        
        # Calculate trend indicator
        change = new_amount - old_amount
        if change > 0:
            trend = f"+${change:,}"
        elif change < 0:
            trend = f"-${abs(change):,}"
        else:
            trend = "±$0"
        
        # Update internal data
        self.farm_data['cash'] = new_amount
        self.farm_data['cash_trend'] = trend
        
        # Update HUD display with formatted cash amount
        self.cash_label.set_text(f"Cash: ${new_amount:,}")
        self.cash_trend_label.set_text(trend)
    
    def _handle_transaction_update(self, event_data):
        """Handle individual transaction updates for trend calculation"""
        # This provides more granular cash change tracking
        amount = event_data.get('amount', 0)
        transaction_type = event_data.get('type', 'unknown')
        
        # Update trend based on transaction type
        if amount > 0:
            self.farm_data['cash_trend'] = f"+${amount:,} ({transaction_type})"
        else:
            self.farm_data['cash_trend'] = f"-${abs(amount):,} ({transaction_type})"
        
        # Update trend display
        self.cash_trend_label.set_text(self.farm_data['cash_trend'])
    
    def _handle_weather_update(self, event_data):
        """Handle weather and season updates from the weather manager"""
        # Extract weather information
        season = event_data.get('season', 'Spring')
        weather_event = event_data.get('weather_event', 'clear')
        growth_modifier = event_data.get('growth_modifier', 1.0)
        
        # Format weather display
        weather_display = weather_event.replace('_', ' ').title()
        growth_effect = f"{(growth_modifier - 1.0) * 100:+.0f}%"
        
        # Update internal data
        self.farm_data['season'] = season.title()
        self.farm_data['weather'] = weather_display
        self.farm_data['weather_effect'] = growth_effect
        
        # Update HUD display
        self.season_weather_label.set_text(f"{self.farm_data['season']} | {self.farm_data['weather']}")
        self.weather_effect_label.set_text(f"Growth: {self.farm_data['weather_effect']}")
    
    def _handle_season_update(self, event_data):
        """Handle season change events"""
        new_season = event_data.get('new_season', 'Spring')
        self.farm_data['season'] = new_season.title()
        
        # Update display (weather will be updated separately by weather_updated event)
        self.season_weather_label.set_text(f"{self.farm_data['season']} | {self.farm_data['weather']}")
    
    def _handle_employee_update(self, event_data):
        """Handle employee hiring and management updates"""
        # This could include more detailed employee information in the future
        self._request_employee_count_update()
    
    def _handle_employee_count_update(self, event_data):
        """Handle employee count changes"""
        count = event_data.get('count', 1)
        self.farm_data['employee_count'] = count
        
        # Update HUD display
        self.employee_info_label.set_text(f"Employees: {count}")
    
    def _handle_inventory_update(self, event_data):
        """Handle inventory updates for storage summary"""
        # Extract inventory information for summary display
        self._update_inventory_summary(event_data)
    
    def _handle_full_inventory_update(self, event_data):
        """Handle comprehensive inventory status updates"""
        # Process full inventory data for complete summary
        self._update_inventory_summary(event_data)
    
    def _update_inventory_summary(self, event_data):
        """Update the inventory summary display"""
        # Extract key inventory metrics
        total_items = event_data.get('total_items', 0)
        capacity = event_data.get('capacity', 100)
        
        # Create summary text
        if total_items == 0:
            summary = "Empty"
        else:
            percentage = (total_items / capacity) * 100
            summary = f"{total_items}/{capacity} ({percentage:.0f}%)"
        
        # Update internal data and display
        self.farm_data['inventory_summary'] = summary
        self.inventory_label.set_text(f"Storage: {summary}")
    
    def _handle_farm_name_update(self, event_data):
        """Handle farm name changes (future feature)"""
        new_name = event_data.get('name', 'My Farm')
        self.farm_data['farm_name'] = new_name
        
        # Update HUD display
        self.farm_name_label.set_text(new_name)
    
    def _request_employee_count_update(self):
        """Request current employee count from employee manager"""
        self.event_system.emit('get_employee_count', {})
    
    def update(self, dt):
        """Update the enhanced top HUD (called each frame)"""
        # HUD updates are primarily event-driven
        # This method available for future real-time updates if needed
        pass
    
    def get_hud_height(self):
        """Get the height of the HUD for layout calculations"""
        return self.hud_height


class DynamicRightPanel:
    """Dynamic right panel system for context-sensitive information display"""
    
    def __init__(self, gui_manager, event_system, x_pos, y_pos, width=280, height=600):
        """Initialize the dynamic right panel system"""
        self.gui_manager = gui_manager
        self.event_system = event_system
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        
        # Panel state management
        self.current_panel_type = None  # 'employee', 'soil', 'building', 'contract', None
        self.current_panel = None       # Reference to active panel
        self.current_data = None        # Data for current panel
        
        # Create base panel container
        self._create_base_panel()
        
        # Subscribe to context change events
        self._setup_event_subscriptions()
        
        print("Dynamic Right Panel system initialized")
    
    def _create_base_panel(self):
        """Create the base panel container"""
        self.base_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(self.x_pos, self.y_pos, self.width, self.height),
            manager=self.gui_manager
        )
        
        # Professional styling
        try:
            self.base_panel.background_colour = pygame.Color(25, 25, 25)
            self.base_panel.border_colour = pygame.Color(60, 60, 60)
            self.base_panel.border_width = 1
        except AttributeError:
            pass
    
    def _setup_event_subscriptions(self):
        """Subscribe to context change events"""
        # Selection events that trigger panel changes
        self.event_system.subscribe('employee_selected', self._handle_employee_selection)
        self.event_system.subscribe('tile_selected', self._handle_tile_selection)  # More generic tile selection
        self.event_system.subscribe('building_selected', self._handle_building_selection)
        self.event_system.subscribe('contract_view_requested', self._handle_contract_selection)
        self.event_system.subscribe('panel_close_requested', self._handle_panel_close)
        
        # Additional events for context awareness
        self.event_system.subscribe('tile_deselected', self._handle_tile_deselection)
        self.event_system.subscribe('employee_status_update', self._handle_employee_status_update)
    
    def _handle_employee_selection(self, event_data):
        """Handle employee selection for employee panel display"""
        self._switch_to_panel('employee', event_data)
    
    def _handle_tile_selection(self, event_data):
        """Handle tile selection for appropriate panel display"""
        # Determine what type of panel to show based on tile data
        tile = event_data.get('tile')
        if tile and hasattr(tile, 'tilled') and tile.tilled:
            self._switch_to_panel('soil', event_data)
        elif tile and hasattr(tile, 'building') and tile.building:
            self._switch_to_panel('building', event_data)
        else:
            # Default to general tile information or close panel
            self._switch_to_panel(None, None)
    
    def _handle_tile_deselection(self, event_data):
        """Handle tile deselection to close panels"""
        self._switch_to_panel(None, None)
    
    def _handle_building_selection(self, event_data):
        """Handle building selection for building information panel"""
        self._switch_to_panel('building', event_data)
    
    def _handle_contract_selection(self, event_data):
        """Handle contract view request for contract panel"""
        self._switch_to_panel('contract', event_data)
    
    def _handle_panel_close(self, event_data):
        """Handle panel close requests"""
        self._switch_to_panel(None, None)
    
    def _handle_employee_status_update(self, event_data):
        """Handle employee status updates for real-time panel refresh"""
        if self.current_panel_type == 'employee':
            # Refresh employee panel with new data
            self._create_employee_panel(event_data)
    
    def _switch_to_panel(self, panel_type, data):
        """Switch to a specific panel type with given data"""
        # Clear current panel if it exists
        self._clear_current_panel()
        
        # Create new panel based on type
        if panel_type == 'employee':
            self._create_employee_panel(data)
        elif panel_type == 'soil':
            self._create_soil_panel(data)
        elif panel_type == 'building':
            self._create_building_panel(data)
        elif panel_type == 'contract':
            self._create_contract_panel(data)
        
        # Update panel state
        self.current_panel_type = panel_type
        self.current_data = data
    
    def _clear_current_panel(self):
        """Clear the current panel contents"""
        if self.current_panel:
            # Kill current panel elements
            if hasattr(self.current_panel, 'kill'):
                self.current_panel.kill()
            self.current_panel = None
    
    def _create_employee_panel(self, employee_data):
        """Create comprehensive employee information panel"""
        # Create employee panel with professional layout
        panel_rect = pygame.Rect(10, 10, self.width - 20, self.height - 20)
        self.current_panel = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.gui_manager,
            container=self.base_panel
        )
        
        # Professional panel styling
        try:
            self.current_panel.background_colour = pygame.Color(30, 30, 30)
            self.current_panel.border_colour = pygame.Color(70, 70, 70)
            self.current_panel.border_width = 1
        except AttributeError:
            pass
        
        # Extract employee information
        employee = employee_data.get('employee')
        if not employee:
            # Create "no employee selected" message
            no_selection_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 10, panel_rect.width - 20, 30),
                text="No employee selected",
                manager=self.gui_manager,
                container=self.current_panel
            )
            return
        
        y_pos = 10  # Current Y position for element placement
        element_height = 25
        spacing = 5
        
        # Employee name and ID
        name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text=f"Employee: {getattr(employee, 'name', 'Unknown')}",
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing
        
        # Employee ID
        id_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text=f"ID: {getattr(employee, 'employee_id', 'N/A')}",
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing * 2
        
        # Current task information
        current_task = getattr(employee, 'current_task', None)
        task_text = "Current Task: " + (current_task if current_task else "Idle")
        task_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text=task_text,
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing * 2
        
        # Employee needs section
        needs_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text="Employee Needs:",
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing
        
        # Hunger status
        hunger = getattr(employee, 'hunger', 100)
        hunger_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text=f"Hunger: {hunger:.0f}/100",
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing
        
        # Thirst status
        thirst = getattr(employee, 'thirst', 100)
        thirst_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text=f"Thirst: {thirst:.0f}/100",
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing
        
        # Rest/Energy status
        rest = getattr(employee, 'rest', 100)
        rest_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text=f"Energy: {rest:.0f}/100",
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing * 2
        
        # Employee traits section
        traits = getattr(employee, 'traits', {})
        if traits:
            traits_title = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
                text="Traits:",
                manager=self.gui_manager,
                container=self.current_panel
            )
            y_pos += element_height + spacing
            
            for trait_name in traits.keys():
                trait_label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(20, y_pos, panel_rect.width - 30, element_height),
                    text=f"• {trait_name.replace('_', ' ').title()}",
                    manager=self.gui_manager,
                    container=self.current_panel
                )
                y_pos += element_height + spacing
        
        # Position information
        y_pos += spacing
        position_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text=f"Position: ({getattr(employee, 'x', 0):.1f}, {getattr(employee, 'y', 0):.1f})",
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing * 2
        
        # Close button
        close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_rect.width - 80, y_pos, 70, 30),
            text="Close",
            manager=self.gui_manager,
            container=self.current_panel
        )
        
        # Add close button functionality
        close_button.is_panel_close = True
        
        print(f"Created employee panel for {getattr(employee, 'name', 'Unknown')}")
    
    def _create_soil_panel(self, soil_data):
        """Create comprehensive soil information panel"""
        # Create soil panel with professional layout
        panel_rect = pygame.Rect(10, 10, self.width - 20, self.height - 20)
        self.current_panel = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.gui_manager,
            container=self.base_panel
        )
        
        # Professional panel styling
        try:
            self.current_panel.background_colour = pygame.Color(30, 30, 30)
            self.current_panel.border_colour = pygame.Color(70, 70, 70)
            self.current_panel.border_width = 1
        except AttributeError:
            pass
        
        # Extract tile information
        tile = soil_data.get('tile')
        if not tile:
            # Create "no tile selected" message
            no_selection_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, 10, panel_rect.width - 20, 30),
                text="No soil tile selected",
                manager=self.gui_manager,
                container=self.current_panel
            )
            return
        
        y_pos = 10  # Current Y position for element placement
        element_height = 25
        spacing = 5
        
        # Tile position and basic info
        position_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text=f"Soil Plot ({tile.x}, {tile.y})",
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing * 2
        
        # Soil health information
        soil_quality = getattr(tile, 'soil_quality', 5)
        health_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text=f"Soil Health: {soil_quality}/10",
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing
        
        # Soil nutrients (if available)
        if hasattr(tile, 'nutrients'):
            nutrients_title = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
                text="Soil Nutrients:",
                manager=self.gui_manager,
                container=self.current_panel
            )
            y_pos += element_height + spacing
            
            # Nitrogen
            nitrogen = getattr(tile.nutrients, 'nitrogen', 100)
            nitrogen_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(20, y_pos, panel_rect.width - 30, element_height),
                text=f"Nitrogen (N): {nitrogen:.0f}/100",
                manager=self.gui_manager,
                container=self.current_panel
            )
            y_pos += element_height + spacing
            
            # Phosphorus
            phosphorus = getattr(tile.nutrients, 'phosphorus', 100)
            phosphorus_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(20, y_pos, panel_rect.width - 30, element_height),
                text=f"Phosphorus (P): {phosphorus:.0f}/100",
                manager=self.gui_manager,
                container=self.current_panel
            )
            y_pos += element_height + spacing
            
            # Potassium
            potassium = getattr(tile.nutrients, 'potassium', 100)
            potassium_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(20, y_pos, panel_rect.width - 30, element_height),
                text=f"Potassium (K): {potassium:.0f}/100",
                manager=self.gui_manager,
                container=self.current_panel
            )
            y_pos += element_height + spacing * 2
        
        # Current crop information
        if hasattr(tile, 'crop_type') and tile.crop_type:
            crop_title = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
                text="Current Crop:",
                manager=self.gui_manager,
                container=self.current_panel
            )
            y_pos += element_height + spacing
            
            crop_info = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(20, y_pos, panel_rect.width - 30, element_height),
                text=f"{tile.crop_type.title()} (Stage {getattr(tile, 'growth_stage', 0)})",
                manager=self.gui_manager,
                container=self.current_panel
            )
            y_pos += element_height + spacing * 2
        
        # Water and irrigation status
        water_level = getattr(tile, 'water_level', 50)
        water_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text=f"Water Level: {water_level:.0f}/100",
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing
        
        # Irrigation status
        has_irrigation = getattr(tile, 'has_irrigation', False)
        irrigation_status = "Installed" if has_irrigation else "Not Installed"
        irrigation_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
            text=f"Irrigation: {irrigation_status}",
            manager=self.gui_manager,
            container=self.current_panel
        )
        y_pos += element_height + spacing * 2
        
        # Crop history (if available)
        if hasattr(tile, 'crop_history') and tile.crop_history:
            history_title = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, y_pos, panel_rect.width - 20, element_height),
                text="Recent Crops:",
                manager=self.gui_manager,
                container=self.current_panel
            )
            y_pos += element_height + spacing
            
            # Show last few crops
            recent_crops = tile.crop_history[-3:] if len(tile.crop_history) > 3 else tile.crop_history
            for crop in recent_crops:
                crop_history_label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(20, y_pos, panel_rect.width - 30, element_height),
                    text=f"• {crop.get('crop_type', 'Unknown').title()}",
                    manager=self.gui_manager,
                    container=self.current_panel
                )
                y_pos += element_height + spacing
        
        # Close button
        y_pos += spacing
        close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_rect.width - 80, y_pos, 70, 30),
            text="Close",
            manager=self.gui_manager,
            container=self.current_panel
        )
        
        # Add close button functionality
        close_button.is_panel_close = True
        
        print(f"Created soil panel for tile ({tile.x}, {tile.y})")
    
    def _create_building_panel(self, building_data):
        """Create building information panel"""
        # Placeholder for building panel creation
        pass
    
    def _create_contract_panel(self, contract_data):
        """Create contract information panel"""
        # Placeholder for contract panel creation
        pass