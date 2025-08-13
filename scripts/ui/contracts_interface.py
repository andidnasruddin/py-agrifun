"""
Contracts Interface - Professional contract management modal matching reference design
Provides dual-panel layout showing Available Contracts and Ongoing Contracts.

Features:
- Dual-panel layout (Available | Ongoing) matching reference design
- Contract cards with company name, crop details, price, quality, and deadline
- "Accept Contract" buttons for available contracts
- "In Progress" status for ongoing contracts
- Integration with existing contract management system
- Professional styling with green theme matching reference
"""

import pygame
import pygame_gui
from typing import Dict, Any, Optional, List
from scripts.core.config import *


class ContractsInterface:
    """Professional contracts interface modal with dual-panel card layout"""
    
    def __init__(self, gui_manager, event_system, screen_width: int, screen_height: int):
        """Initialize the contracts interface modal"""
        self.gui_manager = gui_manager  # pygame_gui manager for UI elements
        self.event_system = event_system  # Event system for communication
        self.screen_width = screen_width  # Screen width for positioning
        self.screen_height = screen_height  # Screen height for positioning
        
        # Modal configuration
        self.modal_width = 800  # Width of contracts modal
        self.modal_height = 600  # Height of contracts modal
        self.modal_x = (screen_width - self.modal_width) // 2  # Center horizontally
        self.modal_y = (screen_height - self.modal_height) // 2  # Center vertically
        
        # UI elements storage
        self.window = None  # Main modal window
        self.available_panel = None  # Available contracts panel
        self.ongoing_panel = None  # Ongoing contracts panel
        self.available_contracts = []  # List of available contracts
        self.ongoing_contracts = []  # List of ongoing contracts
        self.contract_cards = []  # List of contract card UI elements
        
        # Panel configuration
        self.panel_width = 360  # Width of each panel (Available/Ongoing)
        self.panel_height = 500  # Height of each panel
        self.panel_margin = 20  # Margin around panels
        self.card_height = 120  # Height of each contract card
        self.card_spacing = 10  # Space between contract cards
        
        # Set up event subscriptions
        self._setup_event_handlers()
        
        print("Contracts Interface initialized with dual-panel layout")
    
    def _setup_event_handlers(self):
        """Set up event handlers for contracts interface interactions"""
        # Subscribe to contract system events
        self.event_system.subscribe('contract_data_for_ui', self._handle_contracts_data)
        self.event_system.subscribe('contract_accepted_successfully', self._handle_contract_accepted)
        self.event_system.subscribe('contract_action_failed', self._handle_contract_action_failed)
    
    def show_modal(self):
        """Show the contracts interface modal"""
        if self.window:
            return  # Already open
        
        try:
            # Create main modal window with green theme
            self.window = pygame_gui.elements.UIWindow(
                rect=pygame.Rect(self.modal_x, self.modal_y, self.modal_width, self.modal_height),
                manager=self.gui_manager,
                window_display_title="Contracts"
            )
            
            # Create dual panel layout
            self._create_panel_layout()
            
            # Request current contract data from contract system
            self.event_system.emit('get_contract_data_for_ui', {})
            
            print("Contracts interface modal opened")
            
        except Exception as e:
            print(f"Error opening contracts interface: {e}")
            self._cleanup_modal()
            # Re-raise the exception so the submenu knows it failed
            raise e
    
    def _create_panel_layout(self):
        """Create the dual-panel layout (Available | Ongoing)"""
        # Available Contracts Panel (Left Side)
        available_x = self.panel_margin
        available_y = 50  # Leave space for title
        
        # Available Contracts Title
        available_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(available_x, 20, self.panel_width, 25),
            text="Available Contracts",
            manager=self.gui_manager,
            container=self.window
        )
        
        # Available Contracts Scrollable Panel
        self.available_panel = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(available_x, available_y, self.panel_width, self.panel_height),
            manager=self.gui_manager,
            container=self.window
        )
        
        # Ongoing Contracts Panel (Right Side)
        ongoing_x = self.panel_margin + self.panel_width + self.panel_margin
        ongoing_y = 50  # Leave space for title
        
        # Ongoing Contracts Title
        ongoing_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(ongoing_x, 20, self.panel_width, 25),
            text="Ongoing Contracts",
            manager=self.gui_manager,
            container=self.window
        )
        
        # Ongoing Contracts Scrollable Panel
        self.ongoing_panel = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(ongoing_x, ongoing_y, self.panel_width, self.panel_height),
            manager=self.gui_manager,
            container=self.window
        )
    
    def _handle_contracts_data(self, event_data: Dict[str, Any]):
        """Handle contract data from the contract management system"""
        if not self.window:
            return  # Modal not open
        
        # Store contract data (using correct field names from contract manager)
        self.available_contracts = event_data.get('available_contracts', [])
        self.ongoing_contracts = event_data.get('active_contracts', [])  # Contract manager uses 'active_contracts'
        
        # Refresh both panels
        self._refresh_contract_panels()
        
        print(f"Received contract data: {len(self.available_contracts)} available, {len(self.ongoing_contracts)} ongoing")
    
    def _refresh_contract_panels(self):
        """Refresh both contract panels with current data"""
        # Clear existing cards
        self._clear_contract_cards()
        
        # Create cards for available contracts
        for i, contract in enumerate(self.available_contracts):
            self._create_available_contract_card(contract, i)
        
        # Create cards for ongoing contracts
        for i, contract in enumerate(self.ongoing_contracts):
            self._create_ongoing_contract_card(contract, i)
    
    def _clear_contract_cards(self):
        """Clear all existing contract cards"""
        for card_elements in self.contract_cards:
            for element in card_elements:
                element.kill()  # Remove from pygame_gui
        
        self.contract_cards.clear()  # Clear the list
    
    def _create_available_contract_card(self, contract, card_index: int):
        """Create a contract card for an available contract"""
        card_y = card_index * (self.card_height + self.card_spacing)
        
        # Create card background panel with dark styling
        card_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, card_y, self.panel_width - 20, self.card_height),
            manager=self.gui_manager,
            container=self.available_panel
        )
        
        # Apply dark styling to match reference
        try:
            card_panel.background_colour = pygame.Color("#404040")  # Dark gray background
            card_panel.border_colour = pygame.Color("#606060")  # Medium gray border
            card_panel.border_width = 1
        except AttributeError:
            print("Warning: Could not apply dark styling to contract card")
        
        # Company name and contract type
        company_text = f"{contract.buyer_name} - {contract.contract_type.value.upper()}"
        company_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 5, self.panel_width - 40, 20),
            text=company_text,
            manager=self.gui_manager,
            container=card_panel
        )
        
        # Crop details (quantity, crop type, price per unit, total)
        crop_type = contract.crop_type
        quantity = contract.quantity_required
        price_per_unit = contract.price_per_unit
        total_value = quantity * price_per_unit
        
        crop_details = f"{quantity} {crop_type} @ ${price_per_unit:.2f}/unit (Total: ${total_value:.2f})"
        crop_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 25, self.panel_width - 40, 20),
            text=crop_details,
            manager=self.gui_manager,
            container=card_panel
        )
        
        # Quality and deadline requirements
        min_quality = int(contract.quality_requirement * 100)  # Convert 0.0-1.0 to percentage
        deadline_days = contract.deadline_days
        
        requirements = f"Quality: {min_quality}%+ | Deadline: {deadline_days} days"
        requirements_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 45, self.panel_width - 40, 20),
            text=requirements,
            manager=self.gui_manager,
            container=card_panel
        )
        
        # Accept Contract button
        accept_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 75, 120, 30),
            text="Accept Contract",
            manager=self.gui_manager,
            container=card_panel
        )
        
        # Store contract ID in button for event handling
        accept_button.contract_id = contract.id
        accept_button.action_type = 'accept'
        
        # Store all card elements for cleanup
        card_elements = [card_panel, company_label, crop_label, requirements_label, accept_button]
        self.contract_cards.append(card_elements)
    
    def _create_ongoing_contract_card(self, contract, card_index: int):
        """Create a contract card for an ongoing contract"""
        card_y = card_index * (self.card_height + self.card_spacing)
        
        # Create card background panel with dark styling
        card_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, card_y, self.panel_width - 20, self.card_height),
            manager=self.gui_manager,
            container=self.ongoing_panel
        )
        
        # Apply dark styling to match reference
        try:
            card_panel.background_colour = pygame.Color("#404040")  # Dark gray background
            card_panel.border_colour = pygame.Color("#606060")  # Medium gray border
            card_panel.border_width = 1
        except AttributeError:
            print("Warning: Could not apply dark styling to ongoing contract card")
        
        # Company name and contract type
        company_text = f"{contract.buyer_name} - {contract.contract_type.value.upper()}"
        company_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 5, self.panel_width - 40, 20),
            text=company_text,
            manager=self.gui_manager,
            container=card_panel
        )
        
        # Crop details (quantity, crop type, price per unit, total)
        crop_type = contract.crop_type
        quantity = contract.quantity_required
        price_per_unit = contract.price_per_unit
        total_value = quantity * price_per_unit
        
        crop_details = f"{quantity} {crop_type} @ ${price_per_unit:.2f}/unit (Total: ${total_value:.2f})"
        crop_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 25, self.panel_width - 40, 20),
            text=crop_details,
            manager=self.gui_manager,
            container=card_panel
        )
        
        # Quality and deadline requirements
        min_quality = int(contract.quality_requirement * 100)  # Convert 0.0-1.0 to percentage
        deadline_days = contract.deadline_days
        
        requirements = f"Quality: {min_quality}%+ | Deadline: {deadline_days} days"
        requirements_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 45, self.panel_width - 40, 20),
            text=requirements,
            manager=self.gui_manager,
            container=card_panel
        )
        
        # In Progress status (instead of Accept button)
        progress_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 75, 120, 30),
            text="In Progress",
            manager=self.gui_manager,
            container=card_panel
        )
        
        # Store all card elements for cleanup
        card_elements = [card_panel, company_label, crop_label, requirements_label, progress_label]
        self.contract_cards.append(card_elements)
    
    def handle_button_click(self, button_element) -> bool:
        """Handle button clicks within the contracts interface"""
        # Check if it's a contract action button (Accept)
        if hasattr(button_element, 'contract_id') and hasattr(button_element, 'action_type'):
            contract_id = button_element.contract_id
            action_type = button_element.action_type
            
            if action_type == 'accept':
                # Request to accept this contract
                self.event_system.emit('accept_contract_requested', {'contract_id': contract_id})
                print(f"Accept Contract button clicked for contract: {contract_id}")
                return True
        
        return False  # Button not handled by this interface
    
    def _handle_contract_accepted(self, event_data: Dict[str, Any]):
        """Handle successful contract acceptance"""
        contract_id = event_data.get('contract_id', 'Unknown')
        
        print(f"Contract {contract_id} accepted successfully")
        
        # Request updated contract data to refresh the panels
        self.event_system.emit('get_contract_data_for_ui', {})
    
    def _handle_contract_action_failed(self, event_data: Dict[str, Any]):
        """Handle failed contract actions"""
        contract_id = event_data.get('contract_id', 'Unknown')
        error = event_data.get('error', 'Unknown error')
        
        print(f"Failed to accept contract {contract_id}: {error}")
        
        # Could show an error message to the user here
        # For now, just log the error
    
    def close_modal(self):
        """Close the contracts interface modal"""
        self._cleanup_modal()
    
    def _cleanup_modal(self):
        """Clean up all modal UI elements"""
        try:
            # Clear contract cards first
            self._clear_contract_cards()
            
            # Clear panels
            if self.available_panel:
                self.available_panel.kill()
                self.available_panel = None
            
            if self.ongoing_panel:
                self.ongoing_panel.kill()
                self.ongoing_panel = None
            
            # Close main window
            if self.window:
                self.window.kill()
                self.window = None
            
            # Clear contract data
            self.available_contracts.clear()
            self.ongoing_contracts.clear()
            
            print("Contracts interface modal closed and cleaned up")
            
        except Exception as e:
            print(f"Error during contracts interface cleanup: {e}")
    
    def is_open(self) -> bool:
        """Check if the contracts interface modal is currently open"""
        return self.window is not None
    
    def handle_window_close(self, window_element) -> bool:
        """Handle window close events"""
        if window_element == self.window:
            self.close_modal()
            return True
        return False