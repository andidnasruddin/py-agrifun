"""
Smart Action Button System - Intelligent context-sensitive action interface
Provides dynamic action buttons that adapt to current selection and game state.

This system implements intelligent action suggestions based on:
- Currently selected tiles and their states
- Available resources and employee capacity
- Context-aware action prioritization
- Streamlined workflow optimization for farm management
"""

import pygame
import pygame_gui
from typing import Dict, Any, List, Optional, Tuple
from scripts.core.config import *


class SmartActionButton:
    """Individual smart action button with context awareness"""
    
    def __init__(self, action_id: str, label: str, icon: str, priority: int = 0):
        """Initialize smart action button"""
        self.action_id = action_id  # Unique identifier for this action
        self.label = label  # Display text for the button
        self.icon = icon  # Icon identifier for visual representation
        self.priority = priority  # Priority for action ordering (higher = more important)
        self.enabled = True  # Whether the action is currently available
        self.tooltip = ""  # Tooltip text explaining the action
        self.cost = 0  # Resource cost for this action
        self.duration = 0  # Time estimate for completing action
        self.ui_element = None  # pygame_gui button element


class SmartActionSystem:
    """Intelligent action button system that adapts to context"""
    
    def __init__(self, gui_manager, event_system, x_pos=10, y_pos=600, button_width=120, button_height=40):
        """Initialize the smart action system"""
        self.gui_manager = gui_manager  # pygame_gui manager for UI elements
        self.event_system = event_system  # Event system for communication
        
        # Layout configuration
        self.x_pos = x_pos  # X position of action bar
        self.y_pos = y_pos  # Y position of action bar
        self.button_width = button_width  # Width of individual buttons
        self.button_height = button_height  # Height of individual buttons
        self.button_spacing = 10  # Spacing between buttons
        self.max_buttons = 6  # Maximum number of buttons to show
        
        # Current context state
        self.selected_tiles = []  # Currently selected tiles
        self.available_actions = []  # Currently available actions
        self.current_buttons = []  # Currently displayed button elements
        
        # Action definitions with context rules
        self.action_definitions = self._initialize_action_definitions()
        
        # Subscribe to relevant events
        self.event_system.subscribe('tiles_selected', self._handle_tiles_selected)
        self.event_system.subscribe('selection_cleared', self._handle_selection_cleared)
        self.event_system.subscribe('game_state_changed', self._handle_game_state_changed)
        
        print("Smart Action System initialized with context-aware button management")
    
    def _initialize_action_definitions(self) -> Dict[str, SmartActionButton]:
        """Initialize all available action definitions"""
        actions = {}
        
        # Tile preparation actions
        actions['till_soil'] = SmartActionButton(
            'till_soil', 'Till Soil', 'till_icon', priority=100
        )
        actions['till_soil'].tooltip = "Prepare soil for planting (Cost: $0, Time: 2 mins/tile)"
        
        # Planting actions
        actions['plant_corn'] = SmartActionButton(
            'plant_corn', 'Plant Corn', 'corn_icon', priority=90
        )
        actions['plant_corn'].tooltip = "Plant corn crop (Cost: $2/seed, Time: 1 min/tile)"
        actions['plant_corn'].cost = 2
        
        actions['plant_tomatoes'] = SmartActionButton(
            'plant_tomatoes', 'Plant Tomatoes', 'tomato_icon', priority=85
        )
        actions['plant_tomatoes'].tooltip = "Plant tomato crop (Cost: $5/seed, Time: 1 min/tile)"
        actions['plant_tomatoes'].cost = 5
        
        actions['plant_wheat'] = SmartActionButton(
            'plant_wheat', 'Plant Wheat', 'wheat_icon', priority=80
        )
        actions['plant_wheat'].tooltip = "Plant wheat crop (Cost: $1/seed, Time: 1 min/tile)"
        actions['plant_wheat'].cost = 1
        
        # Harvesting actions
        actions['harvest_crops'] = SmartActionButton(
            'harvest_crops', 'Harvest', 'harvest_icon', priority=95
        )
        actions['harvest_crops'].tooltip = "Harvest mature crops (Cost: $0, Time: 3 mins/tile)"
        
        # Infrastructure actions
        actions['build_irrigation'] = SmartActionButton(
            'build_irrigation', 'Add Irrigation', 'irrigation_icon', priority=70
        )
        actions['build_irrigation'].tooltip = "Install irrigation system (Cost: $50/tile, Time: 5 mins/tile)"
        actions['build_irrigation'].cost = 50
        
        actions['build_storage'] = SmartActionButton(
            'build_storage', 'Build Storage', 'storage_icon', priority=60
        )
        actions['build_storage'].tooltip = "Construct storage silo (Cost: $500, Capacity: +50)"
        actions['build_storage'].cost = 500
        
        # Management actions
        actions['clear_tiles'] = SmartActionButton(
            'clear_tiles', 'Clear Tiles', 'clear_icon', priority=50
        )
        actions['clear_tiles'].tooltip = "Clear selected tiles (Cost: $0, Time: 1 min/tile)"
        
        actions['fertilize'] = SmartActionButton(
            'fertilize', 'Fertilize', 'fertilizer_icon', priority=75
        )
        actions['fertilize'].tooltip = "Apply fertilizer to improve soil (Cost: $10/tile, +2 soil quality)"
        actions['fertilize'].cost = 10
        
        return actions
    
    def _handle_tiles_selected(self, event_data: Dict[str, Any]):
        """Handle tile selection event and update available actions"""
        self.selected_tiles = event_data.get('tiles', [])
        print(f"Smart Actions: Received {len(self.selected_tiles)} selected tiles")
        self._update_available_actions()
        print(f"Smart Actions: Updated to {len(self.available_actions)} available actions")
        self._rebuild_action_buttons()
    
    def _handle_selection_cleared(self, event_data: Dict[str, Any]):
        """Handle selection cleared event"""
        self.selected_tiles = []
        self._update_available_actions()
        self._rebuild_action_buttons()
    
    def _handle_game_state_changed(self, event_data: Dict[str, Any]):
        """Handle game state changes that might affect available actions"""
        # Update actions based on current game state (money, resources, etc.)
        self._update_available_actions()
        self._update_button_states()
    
    def _update_available_actions(self):
        """Update the list of available actions based on current context"""
        self.available_actions = []
        
        if not self.selected_tiles:
            # No tiles selected - show general actions
            self.available_actions.append(self.action_definitions['build_storage'])
            return
        
        # Analyze selected tiles to determine appropriate actions
        tile_states = self._analyze_selected_tiles()
        
        # Add actions based on tile analysis
        if tile_states['untilled_count'] > 0:
            self.available_actions.append(self.action_definitions['till_soil'])
        
        if tile_states['tilled_empty_count'] > 0:
            # Can plant on tilled, empty tiles
            self.available_actions.append(self.action_definitions['plant_corn'])
            self.available_actions.append(self.action_definitions['plant_tomatoes'])
            self.available_actions.append(self.action_definitions['plant_wheat'])
        
        if tile_states['harvestable_count'] > 0:
            self.available_actions.append(self.action_definitions['harvest_crops'])
        
        if tile_states['can_irrigate_count'] > 0:
            self.available_actions.append(self.action_definitions['build_irrigation'])
        
        if tile_states['can_fertilize_count'] > 0:
            self.available_actions.append(self.action_definitions['fertilize'])
        
        if tile_states['can_clear_count'] > 0:
            self.available_actions.append(self.action_definitions['clear_tiles'])
        
        # Sort actions by priority (highest first)
        self.available_actions.sort(key=lambda x: x.priority, reverse=True)
        
        # Limit to maximum number of buttons
        self.available_actions = self.available_actions[:self.max_buttons]
    
    def _analyze_selected_tiles(self) -> Dict[str, int]:
        """Analyze selected tiles to determine their states"""
        analysis = {
            'total_count': len(self.selected_tiles),
            'untilled_count': 0,
            'tilled_empty_count': 0,
            'planted_count': 0,
            'harvestable_count': 0,
            'can_irrigate_count': 0,
            'can_fertilize_count': 0,
            'can_clear_count': 0
        }
        
        for tile in self.selected_tiles:
            # Check if tile needs tilling
            if not getattr(tile, 'tilled', False):
                analysis['untilled_count'] += 1
                analysis['can_clear_count'] += 1
            
            # Check if tilled but empty (can plant)
            elif getattr(tile, 'tilled', False) and not getattr(tile, 'current_crop', None):
                analysis['tilled_empty_count'] += 1
                analysis['can_fertilize_count'] += 1
                analysis['can_clear_count'] += 1
            
            # Check if has crop
            elif getattr(tile, 'current_crop', None):
                analysis['planted_count'] += 1
                
                # Check if crop is harvestable
                growth_stage = getattr(tile, 'growth_stage', 0)
                if growth_stage >= 4:  # Assuming 5 growth stages (0-4)
                    analysis['harvestable_count'] += 1
            
            # Check if can add irrigation
            if not getattr(tile, 'has_irrigation', False):
                analysis['can_irrigate_count'] += 1
        
        return analysis
    
    def _rebuild_action_buttons(self):
        """Rebuild the action button UI elements"""
        # Clear existing buttons
        self._clear_buttons()
        
        # Create new buttons for available actions
        for i, action in enumerate(self.available_actions):
            self._create_action_button(action, i)
    
    def _clear_buttons(self):
        """Clear all current action buttons"""
        for button in self.current_buttons:
            if button and hasattr(button, 'kill'):
                button.kill()
        self.current_buttons = []
    
    def _create_action_button(self, action: SmartActionButton, index: int):
        """Create a single action button UI element"""
        # Calculate button position
        button_x = self.x_pos + index * (self.button_width + self.button_spacing)
        button_y = self.y_pos
        
        # Create button rectangle
        button_rect = pygame.Rect(button_x, button_y, self.button_width, self.button_height)
        
        # Create pygame_gui button
        button = pygame_gui.elements.UIButton(
            relative_rect=button_rect,
            text=action.label,
            manager=self.gui_manager
        )
        
        # Store action reference in button for event handling
        button.action_id = action.action_id
        button.action_cost = action.cost
        button.action_tooltip = action.tooltip
        
        # Set button state based on action availability
        if not action.enabled:
            button.disable()
        
        # Store button reference
        action.ui_element = button
        self.current_buttons.append(button)
    
    def _update_button_states(self):
        """Update button enabled/disabled states based on current game state"""
        # This would be called when game state changes (money, resources, etc.)
        for action in self.available_actions:
            if action.ui_element:
                # Check if action is affordable/possible
                can_afford = self._can_afford_action(action)
                
                if can_afford and not action.ui_element.is_enabled:
                    action.ui_element.enable()
                elif not can_afford and action.ui_element.is_enabled:
                    action.ui_element.disable()
    
    def _can_afford_action(self, action: SmartActionButton) -> bool:
        """Check if the player can afford to perform this action"""
        # This would check current money, resources, etc.
        # For now, assume all actions are affordable
        return True
    
    def handle_button_click(self, button_element):
        """Handle action button click events"""
        if hasattr(button_element, 'action_id'):
            action_id = button_element.action_id
            
            # Emit action event with selected tiles and action details
            self.event_system.emit('smart_action_requested', {
                'action_id': action_id,
                'selected_tiles': self.selected_tiles,
                'estimated_cost': getattr(button_element, 'action_cost', 0)
            })
            
            print(f"Smart action requested: {action_id} for {len(self.selected_tiles)} tiles")
    
    def update(self, dt: float):
        """Update the smart action system"""
        # Update button states based on current game conditions
        pass
    
    def render(self, screen: pygame.Surface):
        """Render additional action system elements (if needed)"""
        # Most rendering is handled by pygame_gui
        # Could add custom overlays, tooltips, or cost indicators here
        pass
    
    def get_action_summary(self) -> str:
        """Get a summary of currently available actions"""
        if not self.available_actions:
            return "No actions available"
        
        summary = f"{len(self.available_actions)} actions available: "
        action_names = [action.label for action in self.available_actions[:3]]
        summary += ", ".join(action_names)
        
        if len(self.available_actions) > 3:
            summary += f" and {len(self.available_actions) - 3} more"
        
        return summary
    
    def force_refresh(self):
        """Force a refresh of the action system"""
        self._update_available_actions()
        self._rebuild_action_buttons()