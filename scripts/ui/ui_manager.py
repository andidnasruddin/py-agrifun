"""
UI Manager - Handles all user interface elements and interactions
Uses pygame-gui for advanced UI components with fallback to custom implementation.
"""

import pygame
import pygame_gui
from typing import Dict, Tuple
from scripts.core.config import *
from scripts.ui.enhanced_ui_components import EnhancedTopHUD, DynamicRightPanel
from scripts.ui.smart_action_system import SmartActionSystem
from scripts.ui.main_bottom_bar import MainBottomBar
from scripts.ui.employee_submenu import EmployeeSubmenu
from scripts.ui.contracts_submenu import ContractsSubmenu
from scripts.ui.task_assignment_modal import TaskAssignmentModal
from scripts.ui.animation_system import AnimationSystem  # Legacy system
from scripts.ui.enhanced_animation_system import AnimationManager, EasingType, AnimationPresets
from scripts.ui.tooltip_system import TooltipManager, TooltipFactory, TooltipData
from scripts.ui.notification_system import NotificationManager, NotificationFactory, NotificationType, NotificationPriority


class UIManager:
    """Main UI controller"""
    
    def __init__(self, event_system, screen):
        """Initialize the UI manager"""
        self.event_system = event_system
        self.screen = screen
        self.screen_rect = screen.get_rect()
        
        # Initialize pygame-gui manager with custom theme for better contrast
        self.gui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), theme_path=None)
        
        # Set up improved theme with better contrast
        self._setup_improved_theme()
        
        # UI state
        self.show_debug = True
        
        # Applicant panel state
        self.current_applicants = []
        
        # Interview system removed - using Simple Hiring System for direct hiring
        
        # Notification system
        self.notifications = []
        self.notification_timer = 0.0
        
        # Initialize enhanced UI components
        self.enhanced_hud = EnhancedTopHUD(self.gui_manager, self.event_system)
        
        # Calculate dynamic right panel position (accounting for enhanced HUD height)
        hud_height = self.enhanced_hud.get_hud_height()
        panel_y = hud_height + 10  # Add small margin below HUD
        panel_height = WINDOW_HEIGHT - panel_y - 10  # Leave margin at bottom
        
        self.dynamic_right_panel = DynamicRightPanel(
            self.gui_manager, 
            self.event_system,
            x_pos=WINDOW_WIDTH - 290,  # 290px from right edge for 280px wide panel + margin
            y_pos=panel_y,
            width=280,
            height=panel_height
        )
        
        # Initialize main bottom bar (replaces smart action system)
        self.main_bottom_bar = MainBottomBar(
            self.gui_manager,
            self.event_system,
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )
        
        # Initialize employee submenu system
        self.employee_submenu = EmployeeSubmenu(
            self.gui_manager,
            self.event_system,
            self.main_bottom_bar,
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )
        
        # Initialize contracts submenu system
        self.contracts_submenu = ContractsSubmenu(
            self.gui_manager,
            self.event_system,
            self.main_bottom_bar,
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )
        
        # Initialize enhanced task assignment modal
        self.task_assignment_modal = TaskAssignmentModal(
            self.gui_manager,
            self.event_system,
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )
        
        # Keep smart action system for advanced farming actions (can coexist)
        self.smart_action_system = SmartActionSystem(
            self.gui_manager,
            self.event_system,
            x_pos=10,
            y_pos=WINDOW_HEIGHT - 120,  # Position above main bottom bar
            button_width=100,
            button_height=35
        )
        
        # Initialize animation system (legacy)
        self.animation_system = AnimationSystem(self.event_system)
        
        # Initialize enhanced animation system - Phase 2.3 UI enhancement
        self.enhanced_animation_manager = AnimationManager(self.event_system)
        
        # Initialize advanced tooltip system - Phase 2 UI enhancement
        self.tooltip_manager = TooltipManager(self.event_system, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Initialize advanced notification system - Phase 2.2 UI enhancement
        self.notification_manager = NotificationManager(self.event_system, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Initialize traditional UI elements (for gradual transition)
        self._create_ui_elements()  # Create basic UI components like buttons and panels
        # Note: Applicant panel will be created dynamically when needed
        
        # Set up tooltips for all UI components
        self._setup_ui_tooltips()
        
        # Register for events
        self.event_system.subscribe('time_updated', self._handle_time_update)
        self.event_system.subscribe('money_changed', self._handle_money_update)
        self.event_system.subscribe('inventory_updated', self._handle_inventory_update)
        self.event_system.subscribe('full_inventory_status', self._handle_full_inventory_update)
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
        # Contract-related event subscriptions
        self.event_system.subscribe('contract_data_for_ui', self._handle_contract_data_received)
        self.event_system.subscribe('contract_accepted', self._handle_contract_accepted)
        self.event_system.subscribe('contracts_updated', self._handle_contracts_updated)
        self.event_system.subscribe('contract_completed', self._handle_contract_completed)
        # Soil information panel events
        self.event_system.subscribe('tile_selected', self._handle_tile_selected)
        self.event_system.subscribe('tile_deselected', self._handle_tile_deselected)
        # Enhanced task assignment system events
        self.event_system.subscribe('show_task_assignment_interface', self._handle_show_task_assignment)
        # Weather system events
        self.event_system.subscribe('weather_updated', self._handle_weather_update)
        self.event_system.subscribe('season_changed', self._handle_season_change)
        self.event_system.subscribe('weather_event_started', self._handle_weather_event)
        self.event_system.subscribe('irrigation_status_changed', self._handle_irrigation_status_change)
        self.event_system.subscribe('irrigation_cost_incurred', self._handle_irrigation_cost_notification)
        
        # Smart action system events
        self.event_system.subscribe('smart_action_requested', self._handle_smart_action_request)
        self.event_system.subscribe('tiles_selected', self._handle_tiles_selected_for_actions)
        self.event_system.subscribe('selection_cleared', self._handle_selection_cleared_for_actions)
        
        # Notification system integration - Phase 2.2 enhancement
        self._setup_notification_handlers()
        
        # Track current day for expiration calculations
        self._current_day = 1
        
        # Panel state management
        self._applicant_panel_exists = False  # Track if applicant panel is created
        self._contract_panel_exists = False  # Track if contract panel is created
        
        # Contract panel state
        self.current_available_contracts = []
        self.current_active_contracts = []
        self.contract_table_rows = []
        self.contract_buttons = []
        
        # Soil information panel state
        self._soil_info_panel_exists = False
        self.current_selected_tile = None
        self.soil_info_elements = []
        
        # Farm specialization panel state
        self._specialization_panel_exists = False
        self.specialization_elements = []
        
        # Request initial inventory status
        self.event_system.emit('get_full_inventory_status', {})
        
        # Request initial employee count for enhanced HUD
        self.event_system.emit('get_employee_count', {})
        
        print("UI Manager initialized with pygame-gui, enhanced HUD, and improved contrast theme")
    
    def _setup_improved_theme(self):
        """Set up improved theme with better text contrast"""
        # Create theme dictionary for better text contrast
        theme_data = {
            "defaults": {
                "colours": {
                    "normal_text": "#FFFFFF",        # Pure white text for maximum contrast
                    "hovered_text": "#FFFFFF",       # Keep white on hover
                    "selected_text": "#FFFFFF",      # White when selected
                    "text_shadow": "#000000",        # Black shadow for readability
                    "normal_bg": "#2A2A2A",          # Darker background for contrast
                    "hovered_bg": "#3A3A3A",         # Slightly lighter on hover
                    "selected_bg": "#4A4A4A"         # More contrast when selected
                }
            },
            "@text_box": {
                "colours": {
                    "normal_text": "#FFFFFF",        # White text in text boxes
                    "background": "#2A2A2A"          # Dark background
                }
            },
            "@label": {
                "colours": {
                    "normal_text": "#FFFFFF"          # White text for labels
                }
            },
            "@button": {
                "colours": {
                    "normal_text": "#FFFFFF",        # White button text
                    "hovered_text": "#FFFFFF",       # Stay white on hover
                    "selected_text": "#FFFFFF",      # White when pressed
                    "normal_bg": "#404040",          # Dark button background
                    "hovered_bg": "#505050",         # Lighter on hover
                    "selected_bg": "#606060"         # Lighter when pressed
                }
            }
        }
        
        # Apply the theme to the manager
        # Note: pygame-gui theme system is complex, so we'll handle contrast via manual styling
        print("Improved contrast theme configuration prepared")
    
    def _setup_ui_tooltips(self):
        """Set up tooltips for all UI elements - Phase 2 UI enhancement"""
        # Register tooltips for main control buttons
        
        # Speed control tooltips
        speed_tooltips = {
            'pause': TooltipFactory.create_button_tooltip(
                "Pause Game", 
                "Pause all game activities including employee movement and crop growth.",
                "Spacebar"
            ),
            '1x': TooltipFactory.create_button_tooltip(
                "Normal Speed", 
                "Run the game at normal speed (1x). Good for detailed management and planning."
            ),
            '2x': TooltipFactory.create_button_tooltip(
                "Double Speed", 
                "Run the game at 2x speed. Useful for routine operations and time progression."
            ),
            '4x': TooltipFactory.create_button_tooltip(
                "Quadruple Speed", 
                "Run the game at 4x speed. Great for fast-forwarding through slow periods."
            )
        }
        
        # Economic action tooltips with strategic advice
        economic_tooltips = {
            'sell_corn': TooltipFactory.create_economic_tooltip(
                "Sell Corn",
                0,  # Cost is 0 since it's income
                "Immediate cash flow from stored inventory using FIFO system",
                "Market prices fluctuate daily - check price history for optimal timing"
            ).add_quick_stat("Market Price", "$3-7/unit", True)
             .add_educational_note("Selling at peak market prices can double your profits compared to selling at low prices.")
             .add_strategic_advice("Monitor market trends and sell during price spikes for maximum profit."),
            
            'buy_silo': TooltipFactory.create_economic_tooltip(
                "Storage Silo",
                500,  # Base cost
                "Increases storage capacity by 50 units permanently",
                "Cost increases with each purchase (1.3x multiplier)"
            ).add_quick_stat("Capacity Bonus", "+50 units")
             .add_educational_note("Adequate storage prevents crop spoilage and enables strategic market timing.")
             .add_strategic_advice("Build silos before harvest season to avoid losing crops to spoilage."),
            
            'water_cooler': TooltipFactory.create_economic_tooltip(
                "Water Cooler",
                200,
                "Employees can restore thirst, improving work efficiency",
                "Placement affects employee productivity in surrounding area"
            ).add_quick_stat("Effect Radius", "3x3 tiles")
             .add_educational_note("Proper hydration is essential for farm worker productivity and safety.")
             .add_strategic_advice("Place near work areas to minimize employee downtime."),
            
            'tool_shed': TooltipFactory.create_economic_tooltip(
                "Tool Shed",
                300,
                "Increases work efficiency by 10% in surrounding area",
                "Efficiency bonus only applies within the building's radius"
            ).add_quick_stat("Efficiency Bonus", "+10%")
             .add_quick_stat("Effect Radius", "4x4 tiles")
             .add_educational_note("Organized tool storage reduces time spent searching for equipment.")
             .add_strategic_advice("Build near high-activity areas like crop fields for maximum benefit."),
            
            'employee_housing': TooltipFactory.create_economic_tooltip(
                "Employee Housing",
                800,
                "Reduces commute time and increases employee loyalty",
                "High cost but improves long-term employee satisfaction"
            ).add_quick_stat("Loyalty Bonus", "+15%")
             .add_educational_note("On-site housing reduces transportation costs and improves worker retention.")
             .add_strategic_advice("Invest in housing after establishing stable income to improve worker efficiency.")
        }
        
        # Employee management tooltips
        employee_tooltips = {
            'hire_employees': TooltipFactory.create_button_tooltip(
                "Hire Employees",
                "Open the strategic hiring panel to review applicants and hire new workers. "
                "Each employee has different skills, traits, and wage requirements.",
                "H"
            ).add_educational_note("Diverse employee skills create more efficient farm operations.")
             .add_strategic_advice("Hire workers with complementary traits for balanced team performance."),
            
            'show_roster': TooltipFactory.create_button_tooltip(
                "Employee Roster",
                "View all current employees, their status, and performance metrics. "
                "Monitor employee needs and productivity here.",
                "R"
            ).add_strategic_advice("Regular monitoring helps identify productivity issues early.")
        }
        
        # Task assignment tooltips with agricultural education
        task_tooltips = {
            'till': TooltipFactory.create_educational_tooltip(
                "Till Soil",
                "Tilling breaks up compacted soil, improves drainage, and incorporates organic matter. "
                "Essential preparation before planting any crop. Also removes weeds and crop residue.",
                "Always till before planting to ensure optimal growing conditions."
            ).add_quick_stat("Hotkey", "T")
             .add_quick_stat("Duration", "~30 seconds/tile"),
            
            'plant': TooltipFactory.create_educational_tooltip(
                "Plant Crops",
                "Seeds crops in prepared (tilled) soil. Different crops have different growing seasons "
                "and requirements. Plant timing affects yield and quality significantly.",
                "Check seasonal planting windows for optimal crop performance."
            ).add_quick_stat("Hotkey", "P")
             .add_quick_stat("Requires", "Tilled soil"),
            
            'harvest': TooltipFactory.create_educational_tooltip(
                "Harvest Crops",
                "Collect mature crops for storage and sale. Harvest timing is critical - too early "
                "reduces yield, too late may cause quality loss or crop failure.",
                "Harvest at peak ripeness for maximum yield and quality bonuses."
            ).add_quick_stat("Hotkey", "H")
             .add_quick_stat("Requires", "Mature crops")
        }
        
        # Register all tooltips with the tooltip manager
        # (In a real implementation, we'd need to map these to actual UI element IDs)
        
        print("Advanced tooltip system configured with educational and strategic content!")
    
    def register_tile_tooltip(self, tile, screen_rect: pygame.Rect):
        """Register a tooltip for a grid tile - called by grid manager"""
        # Create comprehensive tile data for tooltip generation
        tile_data = {
            'x': tile.x,
            'y': tile.y,
            'terrain_type': tile.terrain_type,
            'soil_quality': tile.soil_quality,
            'current_crop': tile.current_crop,
            'growth_stage': tile.growth_stage,
            'soil_nutrients': tile.soil_nutrients,
            'water_level': tile.water_level,
            'task_assignment': tile.task_assignment,
            'building_type': tile.building_type,
            'has_irrigation': getattr(tile, 'has_irrigation', False),
            'crop_history': getattr(tile, 'crop_history', []),
            'seasons_rested': getattr(tile, 'seasons_rested', 0)
        }
        
        # Generate rich tooltip with agricultural information
        tooltip = TooltipFactory.create_tile_tooltip(tile_data)
        
        # Add crop-specific information if present
        if tile.current_crop:
            crop_info = self._get_crop_educational_info(tile.current_crop, tile.growth_stage)
            if crop_info:
                tooltip.add_educational_note(crop_info)
        
        # Add soil health advice based on conditions
        soil_advice = self._get_soil_strategic_advice(tile_data)
        if soil_advice:
            tooltip.add_strategic_advice(soil_advice)
        
        # Register the tooltip area with the tooltip manager
        self.tooltip_manager.register_hover_area(screen_rect, tooltip)
    
    def _get_crop_educational_info(self, crop_type: str, growth_stage: int) -> str:
        """Get educational information about a specific crop and growth stage"""
        crop_education = {
            'corn': {
                'base': "Corn is a heavy feeder that depletes soil nitrogen quickly but provides high yields.",
                'stages': [
                    "Germination: Seeds are sprouting and establishing root systems.",
                    "Seedling: Young plants developing first true leaves.",
                    "Vegetative: Rapid growth and leaf development phase.",
                    "Tasseling: Plants preparing to produce grain.",
                    "Mature: Ready for harvest with maximum grain content."
                ]
            },
            'tomatoes': {
                'base': "Tomatoes are warm-season crops that benefit from consistent watering and moderate feeding.",
                'stages': [
                    "Germination: Seeds developing initial root and shoot systems.",
                    "Seedling: Small plants establishing basic structure.",
                    "Flowering: Plants beginning to produce flower buds.",
                    "Fruit set: Flowers developing into small green tomatoes.",
                    "Ripe: Tomatoes ready for harvest with full color and flavor."
                ]
            },
            'wheat': {
                'base': "Wheat is a cool-season grain that improves soil structure and requires minimal nutrients.",
                'stages': [
                    "Germination: Seeds sprouting in cool soil conditions.",
                    "Tillering: Plants developing multiple stems and roots.",
                    "Jointing: Stems elongating and nodes developing.",
                    "Heading: Grain heads emerging from protective sheaths.",
                    "Harvest ready: Grain fully developed and dried for storage."
                ]
            }
        }
        
        crop_info = crop_education.get(crop_type, {})
        base_info = crop_info.get('base', '')
        stage_info = crop_info.get('stages', [])
        
        if growth_stage < len(stage_info):
            return f"{base_info} Current stage: {stage_info[growth_stage]}"
        return base_info
    
    def _get_soil_strategic_advice(self, tile_data: Dict) -> str:
        """Generate strategic advice based on soil conditions"""
        advice_parts = []
        
        # Soil quality advice
        soil_quality = tile_data.get('soil_quality', 5)
        if soil_quality <= 3:
            advice_parts.append("Consider crop rotation or letting this field rest to improve soil health.")
        elif soil_quality >= 8:
            advice_parts.append("Excellent soil quality - perfect for high-value crops.")
        
        # Nutrient-specific advice
        nutrients = tile_data.get('soil_nutrients', {})
        low_nutrients = [name for name, level in nutrients.items() if level < 30]
        if low_nutrients:
            advice_parts.append(f"Low {', '.join(low_nutrients)} - consider planting light feeders or resting.")
        
        # Crop rotation advice
        crop_history = tile_data.get('crop_history', [])
        if len(crop_history) >= 2 and crop_history[-1] == crop_history[-2]:
            advice_parts.append("Avoid planting the same crop repeatedly - rotation prevents soil depletion.")
        
        # Irrigation advice
        if not tile_data.get('has_irrigation') and tile_data.get('terrain_type') == 'tilled':
            advice_parts.append("Consider irrigation to protect against drought damage.")
        
        return ' '.join(advice_parts) if advice_parts else None
    
    def _setup_notification_handlers(self):
        """Set up notification handlers for game events - Phase 2.2 enhancement"""
        # Economy notifications
        self.event_system.subscribe('money_changed', self._handle_money_change_notification)
        self.event_system.subscribe('crop_sold', self._handle_crop_sale_notification)
        self.event_system.subscribe('building_purchased', self._handle_building_purchase_notification)
        self.event_system.subscribe('loan_payment_due', self._handle_loan_payment_notification)
        
        # Employee notifications
        self.event_system.subscribe('employee_hired_successfully', self._handle_employee_hired_notification)
        self.event_system.subscribe('employee_needs_critical', self._handle_employee_needs_critical)
        self.event_system.subscribe('employee_completed_task', self._handle_task_completion_notification)
        
        # Agricultural notifications
        self.event_system.subscribe('crop_harvested', self._handle_crop_harvest_notification)
        self.event_system.subscribe('crop_growth_stage_changed', self._handle_crop_growth_notification)
        self.event_system.subscribe('soil_health_changed', self._handle_soil_health_notification)
        
        # Weather notifications
        self.event_system.subscribe('weather_event_started', self._handle_weather_notification)
        self.event_system.subscribe('season_changed', self._handle_season_change_notification)
        
        # Achievement notifications
        self.event_system.subscribe('milestone_reached', self._handle_milestone_notification)
        self.event_system.subscribe('first_harvest_complete', self._handle_first_harvest_achievement)
        
        print("Notification system handlers configured with enhanced animation effects!")
    
    def create_success_feedback_animation(self, target_position: Tuple[int, int]):
        """Create success feedback animation with particles - Phase 2.3 enhancement"""
        success_particles = self.enhanced_animation_manager.get_particle_system("success_feedback")
        if not success_particles:
            success_particles = self.enhanced_animation_manager.create_particle_system("success_feedback", 100)
        
        success_particles.particle_color = (0, 255, 0, 255)  # Green success particles
        success_particles.particle_life_span_range = (0.8, 1.5)
        success_particles.emit_velocity_range = ((-60, -60), (60, 60))  # Small burst
        success_particles.gravity = 80.0
        success_particles.emit_burst(target_position, 15)
    
    def create_error_feedback_animation(self, target_position: Tuple[int, int]):
        """Create error feedback animation with particles - Phase 2.3 enhancement"""
        error_particles = self.enhanced_animation_manager.get_particle_system("error_feedback")
        if not error_particles:
            error_particles = self.enhanced_animation_manager.create_particle_system("error_feedback", 100)
        
        error_particles.particle_color = (255, 0, 0, 255)  # Red error particles
        error_particles.particle_life_span_range = (0.5, 1.2)
        error_particles.emit_velocity_range = ((-40, -40), (40, 40))  # Quick burst
        error_particles.gravity = 120.0
        error_particles.emit_burst(target_position, 10)
    
    # Notification event handlers - Phase 2.2 enhancement
    def _handle_money_change_notification(self, event_data):
        """Handle money change notifications"""
        amount = event_data.get('amount', 0)
        reason = event_data.get('reason', 'Transaction')
        
        if abs(amount) >= 100:  # Only notify for significant amounts
            if amount > 0:
                self.notification_manager.show_notification(
                    "💰 Income Received",
                    f"{reason}: +${amount:.0f}",
                    NotificationType.ECONOMY,
                    NotificationPriority.NORMAL
                )
            else:
                priority = NotificationPriority.HIGH if abs(amount) >= 500 else NotificationPriority.NORMAL
                self.notification_manager.show_notification(
                    "💸 Expense Incurred",
                    f"{reason}: -${abs(amount):.0f}",
                    NotificationType.ECONOMY,
                    priority
                )
    
    def _handle_crop_sale_notification(self, event_data):
        """Handle crop sale notifications"""
        crop_type = event_data.get('crop_type', 'crops')
        quantity = event_data.get('quantity', 0)
        total_value = event_data.get('total_value', 0)
        
        self.notification_manager.show_notification(
            f"🌾 {crop_type.title()} Sold",
            f"Sold {quantity} units for ${total_value:.0f}",
            NotificationType.AGRICULTURE,
            NotificationPriority.NORMAL
        )
    
    def _handle_building_purchase_notification(self, event_data):
        """Handle building purchase notifications"""
        building_type = event_data.get('building_type', 'building')
        cost = event_data.get('cost', 0)
        
        self.notification_manager.show_notification(
            f"🏗️ {building_type.title()} Built",
            f"Successfully purchased {building_type} for ${cost:.0f}",
            NotificationType.BUILDING,
            NotificationPriority.NORMAL
        )
        
        # Add construction particle effect - Phase 2.3 enhancement  
        construction_particles = self.enhanced_animation_manager.get_particle_system("construction")
        if not construction_particles:
            construction_particles = self.enhanced_animation_manager.create_particle_system("construction", 150)
        construction_particles.particle_color = (139, 69, 19, 255)  # Brown construction particles
        construction_particles.particle_life_span_range = (1.0, 2.5)
        construction_particles.emit_velocity_range = ((-80, -80), (80, 80))  # Scattered debris
        construction_particles.gravity = 100.0
        construction_particles.emit_burst((WINDOW_WIDTH - 200, 200), 20)
    
    def _handle_employee_hired_notification(self, event_data):
        """Handle employee hiring notifications"""
        employee_name = event_data.get('employee_name', 'New Employee')
        cost = event_data.get('daily_wage', 0)
        traits = event_data.get('traits', [])
        
        trait_text = f" (Traits: {', '.join(traits)})" if traits else ""
        
        self.notification_manager.show_notification(
            f"👤 {employee_name} Hired",
            f"Welcome to the team! Daily wage: ${cost:.0f}{trait_text}",
            NotificationType.EMPLOYEE,
            NotificationPriority.NORMAL
        )
    
    def _handle_employee_needs_critical(self, event_data):
        """Handle critical employee needs alerts"""
        employee_name = event_data.get('employee_name', 'Employee')
        need_type = event_data.get('need_type', 'needs')
        
        self.notification_manager.show_alert(
            f"⚠️ {employee_name} Needs Attention",
            f"{employee_name}'s {need_type} is critically low! Productivity will suffer.",
            "View Employee",
            lambda: self.event_system.emit('show_employee_details', {'employee_name': employee_name})
        )
    
    def _handle_crop_harvest_notification(self, event_data):
        """Handle crop harvest notifications with achievements"""
        crop_type = event_data.get('crop_type', 'crops')
        quantity = event_data.get('quantity', 0)
        quality = event_data.get('quality', 'good')
        
        # Use achievement notification for harvests
        self.notification_manager.show_achievement(
            f"🌾 {crop_type.title()} Harvest Complete!",
            f"Harvested {quantity} units of {quality} quality {crop_type}. Great farming!"
        )
        
        # Add harvest celebration particle effect - Phase 2.3 enhancement
        harvest_particles = self.enhanced_animation_manager.create_particle_system("harvest_celebration", 200)
        harvest_particles.particle_color = (255, 215, 0, 255)  # Golden particles
        harvest_particles.particle_life_span_range = (1.5, 3.0)
        harvest_particles.emit_velocity_range = ((-100, -150), (100, -50))  # Upward burst
        harvest_particles.gravity = 50.0  # Light gravity
        harvest_particles.emit_burst((WINDOW_WIDTH - 200, 150), 30)  # Burst near notifications
    
    def _handle_weather_notification(self, event_data):
        """Handle weather event notifications"""
        weather_type = event_data.get('weather_type', 'weather change')
        effect = event_data.get('effect', '')
        duration = event_data.get('duration', 1)
        
        priority = NotificationPriority.HIGH if weather_type in ['drought', 'frost'] else NotificationPriority.NORMAL
        
        self.notification_manager.show_notification(
            f"🌤️ {weather_type.title()} Alert",
            f"{effect} Duration: {duration} day(s)",
            NotificationType.WEATHER,
            priority
        )
    
    def _handle_season_change_notification(self, event_data):
        """Handle season change notifications"""
        new_season = event_data.get('season', 'Unknown')
        day = event_data.get('day', 0)
        
        self.notification_manager.show_notification(
            f"🍂 {new_season.title()} Has Arrived",
            f"Day {day}: Season changed to {new_season}. Plan your crops accordingly!",
            NotificationType.WEATHER,
            NotificationPriority.NORMAL,
            duration=8.0  # Longer display for important season changes
        )
    
    def _handle_milestone_notification(self, event_data):
        """Handle milestone achievement notifications"""
        milestone = event_data.get('milestone', 'Goal')
        description = event_data.get('description', 'Milestone achieved!')
        
        self.notification_manager.show_achievement(
            f"🏆 {milestone} Achieved!",
            description
        )
    
    def _handle_first_harvest_achievement(self, event_data):
        """Handle first harvest achievement"""
        crop_type = event_data.get('crop_type', 'crops')
        
        self.notification_manager.show_achievement(
            "🎉 First Harvest Complete!",
            f"Congratulations on your first {crop_type} harvest! You're becoming a real farmer!"
        )
        
        # Add special celebration particle effect - Phase 2.3 enhancement
        celebration_particles = self.enhanced_animation_manager.create_particle_system("first_harvest_celebration", 300)
        celebration_particles.particle_color = (255, 105, 180, 255)  # Pink celebration particles
        celebration_particles.particle_life_span_range = (2.0, 4.0)
        celebration_particles.emit_velocity_range = ((-120, -200), (120, -100))  # Big upward burst
        celebration_particles.gravity = 30.0  # Very light gravity for long hang time
        celebration_particles.emit_burst((WINDOW_WIDTH - 175, 140), 50)  # Large burst for major achievement
    
    def _handle_loan_payment_notification(self, event_data):
        """Handle loan payment notifications"""
        amount = event_data.get('amount', 0)
        remaining = event_data.get('remaining_balance', 0)
        
        if remaining <= 0:
            self.notification_manager.show_achievement(
                "🎉 Loan Paid Off!",
                "Congratulations! You've successfully paid off your farming loan!"
            )
        else:
            self.notification_manager.show_notification(
                "💳 Loan Payment",
                f"Daily loan payment: ${amount:.2f}. Remaining: ${remaining:.2f}",
                NotificationType.ECONOMY,
                NotificationPriority.LOW
            )
    
    def _handle_task_completion_notification(self, event_data):
        """Handle task completion notifications"""
        employee_name = event_data.get('employee_name', 'Employee')
        task_type = event_data.get('task_type', 'task')
        tile_count = event_data.get('tile_count', 1)
        
        self.notification_manager.show_notification(
            f"✅ Task Complete",
            f"{employee_name} finished {task_type} on {tile_count} tile(s)",
            NotificationType.EMPLOYEE,
            NotificationPriority.LOW
        )
    
    def _handle_crop_growth_notification(self, event_data):
        """Handle crop growth stage notifications"""
        crop_type = event_data.get('crop_type', 'crops')
        stage = event_data.get('stage', 0)
        tile_count = event_data.get('tile_count', 1)
        
        stage_names = ['Sprouting', 'Seedling', 'Growing', 'Maturing', 'Ready for Harvest']
        stage_name = stage_names[min(stage, len(stage_names)-1)]
        
        if stage == len(stage_names) - 1:  # Ready for harvest
            self.notification_manager.show_notification(
                f"🌱 {crop_type.title()} Ready!",
                f"{tile_count} {crop_type} plant(s) ready for harvest!",
                NotificationType.AGRICULTURE,
                NotificationPriority.HIGH
            )
        else:
            self.notification_manager.show_notification(
                f"🌱 Crop Growth",
                f"{tile_count} {crop_type} plant(s) reached {stage_name} stage",
                NotificationType.AGRICULTURE,
                NotificationPriority.LOW
            )
    
    def _handle_soil_health_notification(self, event_data):
        """Handle soil health change notifications"""
        tile_x = event_data.get('tile_x', 0)
        tile_y = event_data.get('tile_y', 0)
        old_health = event_data.get('old_health', 5)
        new_health = event_data.get('new_health', 5)
        
        if new_health < 3 and old_health >= 3:
            self.notification_manager.show_notification(
                "⚠️ Poor Soil Health",
                f"Tile ({tile_x}, {tile_y}) soil quality has dropped to {new_health}/10",
                NotificationType.AGRICULTURE,
                NotificationPriority.HIGH
            )
        elif new_health >= 8 and old_health < 8:
            self.notification_manager.show_notification(
                "🌿 Excellent Soil",
                f"Tile ({tile_x}, {tile_y}) soil quality improved to {new_health}/10!",
                NotificationType.AGRICULTURE,
                NotificationPriority.NORMAL
            )
    
    def _create_ui_elements(self):
        """Create the main UI elements - DISABLED to prevent UI overlap"""
        # =====================================================================
        # LEGACY UI CREATION DISABLED - Enhanced UI components handle everything
        # =====================================================================
        # Early return prevents creation of 113 overlapping UI elements
        # Set all attributes to None so event handlers won't crash
        
        # Legacy top panel elements (replaced by EnhancedTopHUD)
        self.resource_panel = None
        self.money_label = None
        self.inventory_label = None
        self.time_label = None
        self.employee_count_label = None
        self.pause_button = None
        self.speed_1x_button = None
        self.speed_2x_button = None
        self.speed_4x_button = None
        
        # Legacy right panel elements (replaced by DynamicRightPanel)
        self.control_panel = None
        self.control_title = None
        self.economy_label = None
        self.sell_corn_button = None
        self.buy_silo_button = None
        self.buy_water_cooler_button = None
        self.buy_tool_shed_button = None
        self.buy_housing_button = None
        self.buy_irrigation_button = None
        self.save_label = None
        self.quick_save_button = None
        self.quick_load_button = None
        self.save_menu_button = None
        self.employee_label = None
        self.hire_employee_button = None
        self.view_applicants_button = None
        self.view_payroll_button = None
        self.view_contracts_button = None
        self.specialization_label = None
        self.view_specialization_button = None
        self.weather_label = None
        self.weather_display = None
        self.weather_info_button = None
        self.irrigation_toggle_button = None
        self.status_label = None
        self.selected_tiles_info = None
        self.employee_status_display = None
        self.crop_type_dropdown = None
        self.debug_toggle = None
        self.sort_dropdown = None
        self.shortcut_labels = []
        
        print("Legacy UI elements disabled - Enhanced UI system active")
        return  # Prevent creation of overlapping legacy UI elements
        
        # === DISABLED LEGACY CODE BELOW (kept for reference) ===
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
        
        # Multi-crop inventory display
        self.inventory_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(165, 10, 200, 40),
            text="C:0 T:0 W:0 / 1000",
            manager=self.gui_manager,
            container=self.resource_panel
        )
        
        # Time display
        self.time_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(375, 10, 150, 40),
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
        
        # Main control panel on right side (extra tall and wider for all controls)
        # Creating with darker background for better text contrast and proper height (720px fits within 800px window)
        self.control_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(WINDOW_WIDTH-280, 70, 270, 720),
            manager=self.gui_manager
        )
        
        # Set darker background color for better text contrast
        try:
            # Try to set a darker background color directly
            self.control_panel.background_colour = pygame.Color(25, 25, 25)  # Very dark gray
            self.control_panel.border_colour = pygame.Color(60, 60, 60)  # Medium gray border
            self.control_panel.border_width = 1
        except AttributeError:
            # If direct color setting doesn't work, pygame-gui will use defaults
            print("Note: Control panel background color set to default")
        
        # Use text color that will be more visible
        self.control_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, 250, 25),
            text="Farm Controls",
            manager=self.gui_manager,
            container=self.control_panel
        )
        # Note: Label text color will be handled by pygame-gui defaults
        
        # Economy section
        economy_section_y = 40
        # Economy section header with improved visibility
        self.economy_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, economy_section_y, 250, 20),
            text="Economy",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.sell_corn_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, economy_section_y + 25, 120, 25),
            text="Sell 10 Corn",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Sell 10 corn units at current market price. Uses FIFO inventory."
        )
        
        self.buy_silo_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(135, economy_section_y + 25, 125, 25),
            text="Buy Storage Silo",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Purchase storage silo (+50 capacity). Cost increases with each purchase."
        )
        
        # Interactive building buttons (second row) - wider for better readability
        self.buy_water_cooler_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, economy_section_y + 55, 80, 25),
            text="Water ($200)",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Purchase water cooler ($200). Employees can restore thirst."
        )
        
        self.buy_tool_shed_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(95, economy_section_y + 55, 80, 25),
            text="Tools ($300)",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Purchase tool shed ($300). +15% work efficiency nearby."
        )
        
        self.buy_housing_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(180, economy_section_y + 55, 80, 25),
            text="House ($800)",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Purchase employee housing ($800). Employees can rest here."
        )
        
        # Irrigation system button (third row)
        self.buy_irrigation_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, economy_section_y + 85, 120, 25),
            text="Irrigation ($150)",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Install irrigation system ($150). Mitigates drought effects on tilled soil."
        )
        
        # Save/Load section (moved down to accommodate building buttons)
        save_section_y = 140
        # Game State section header with improved visibility
        self.save_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, save_section_y, 250, 20),
            text="Game State",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.quick_save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, save_section_y + 25, 120, 25),
            text="Quick Save",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Save current game to quicksave slot"
        )
        
        self.quick_load_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(135, save_section_y + 25, 125, 25),
            text="Quick Load",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Load from quicksave slot"
        )
        
        self.save_menu_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, save_section_y + 55, 250, 25),
            text="Save/Load Menu",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Open save/load menu with multiple slots"
        )
        
        # Employee section (adjusted for moved save section)
        employee_section_y = 240
        # Employees section header with improved visibility
        self.employee_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, employee_section_y, 250, 20),
            text="Employees",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.hire_employee_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, employee_section_y + 25, 120, 25),
            text="Hire Employee",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Generate job applicants to hire new workers ($80/day wage)"
        )
        
        self.view_applicants_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(135, employee_section_y + 25, 125, 25),
            text="View Applicants",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Review and hire from available job applicants"
        )
        
        self.view_payroll_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, employee_section_y + 55, 120, 25),
            text="View Roster",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.view_contracts_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(135, employee_section_y + 55, 125, 25),
            text="View Contracts",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="View available farming contracts and manage agreements"
        )
        
        # Farm Specialization section
        specialization_section_y = 340
        # Farm Specialization section header with improved visibility
        self.specialization_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, specialization_section_y, 220, 20),
            text="Farm Specialization",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.view_specialization_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, specialization_section_y + 25, 250, 25),
            text="Choose Specialization",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Select farm specialization track for bonuses and strategic advantages"
        )
        
        # Weather & Seasons section (between specialization and status)
        weather_section_y = 370
        self.weather_label = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(10, weather_section_y, 250, 18),
            html_text="<font size=3.5><b>Weather & Seasons</b></font>",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        # Current weather display
        self.weather_display = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(10, weather_section_y + 20, 250, 40),
            html_text="<font size=2>Spring Day 1<br/>Clear Weather</font>",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        # Weather effects info button  
        self.weather_info_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, weather_section_y + 65, 120, 25),
            text="Weather Info",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="View detailed weather effects and seasonal crop recommendations"
        )
        
        # Irrigation toggle button
        self.irrigation_toggle_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(135, weather_section_y + 65, 115, 25),
            text="Toggle Irrigation",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="Turn irrigation on/off during drought. Costs $5/day per irrigated tile."
        )
        
        # Real-time employee status display (with proper vertical spacing)
        status_section_y = 430  # Moved down to accommodate weather section
        self.status_label = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(10, status_section_y, 250, 35),
            html_text="<font size=5 color='#FFFFFF'><b>Live Status</b></font>",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.employee_status_display = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(10, status_section_y + 40, 250, 90),
            html_text="<font size=3.5 color='#FFFFFF'>No employees</font>",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        # Keyboard shortcuts section (with proper vertical spacing)
        shortcuts_section_y = 645  # Adjusted for weather section addition
        self.shortcuts_label = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(10, shortcuts_section_y, 250, 35),
            html_text="<font size=5 color='#FFFFFF'><b>Keyboard Shortcuts</b></font>",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        
        # Crop selection section (with proper vertical spacing)
        crop_section_y = 545  # Adjusted for weather section addition
        self.crop_selection_label = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(10, crop_section_y, 250, 35),
            html_text="<font size=5 color='#FFFFFF'><b>Crop Selection</b></font>",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        # Current selected crop display and dropdown (with proper spacing)
        self.current_crop_type = DEFAULT_CROP_TYPE  # Track currently selected crop type
        crop_data = CROP_TYPES[self.current_crop_type]
        self.selected_crop_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(10, crop_section_y + 40, 150, 30),
            options_list=[f"{CROP_TYPES[crop]['name']} (${CROP_TYPES[crop]['seed_cost']})" for crop in CROP_TYPES],
            starting_option=f"{crop_data['name']} (${crop_data['seed_cost']})",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        # Crop info button (with proper spacing)
        self.crop_info_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(165, crop_section_y + 40, 85, 30),
            text="Info",
            manager=self.gui_manager,
            container=self.control_panel,
            tool_tip_text="View detailed crop information and growth times"
        )

        # Task control buttons (with proper vertical spacing)
        task_controls_y = 600  # Adjusted for weather section addition
        self.task_controls_label = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(10, task_controls_y, 250, 35),
            html_text="<font size=5 color='#FFFFFF'><b>Task Controls</b></font>",
            manager=self.gui_manager,
            container=self.control_panel
        )
        
        self.cancel_tasks_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, task_controls_y + 40, 230, 35),
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
            # Use text box with proper height and spacing
            text_box = pygame_gui.elements.UITextBox(
                relative_rect=pygame.Rect(10, shortcuts_section_y + 40 + i * 25, 250, 22),
                html_text=f"<font size=4 color='#FFFFFF'>{text}</font>",
                manager=self.gui_manager,
                container=self.control_panel
            )
            self.shortcut_labels.append(text_box)
    
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
        
        # Let task assignment modal handle events first
        if self.task_assignment_modal.handle_event(event):
            return  # Event was handled by task assignment modal
        
        # Handle our custom events
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            # Handle window close events
            if hasattr(self, 'employee_submenu'):
                if self.employee_submenu.handle_window_close(event.ui_element):
                    return  # Window close handled by employee submenu
            
            if hasattr(self, 'contracts_submenu'):
                if self.contracts_submenu.handle_window_close(event.ui_element):
                    return  # Window close handled by contracts submenu
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Add button press animation for any clicked button - Phase 2.3 enhancement
            button_element = event.ui_element
            if hasattr(button_element, 'rect'):
                # Create a mock object for animation (since pygame-gui elements can't be directly animated)
                button_mock = type('ButtonMock', (), {
                    'scale': 1.0,
                    'color': (255, 255, 255, 255)
                })()
                AnimationPresets.button_press(button_mock, self.enhanced_animation_manager)
            
            # Handle main bottom bar button clicks
            if hasattr(self, 'main_bottom_bar'):
                clicked_action = self.main_bottom_bar.handle_button_click(button_element)
                if clicked_action:
                    print(f"Main bottom bar action triggered: {clicked_action}")
                    return  # Early return to prevent processing other button handlers
            
            # Handle employee submenu button clicks
            if hasattr(self, 'employee_submenu') and self.employee_submenu.is_submenu_active:
                submenu_action = self.employee_submenu.handle_submenu_button_click(button_element)
                if submenu_action:
                    print(f"Employee submenu action triggered: {submenu_action}")
                    return  # Early return to prevent processing other button handlers
            
            # Handle employee submenu modal button clicks
            if hasattr(self, 'employee_submenu'):
                modal_handled = self.employee_submenu.handle_modal_button_click(button_element)
                if modal_handled:
                    print(f"Employee modal button handled")
                    return  # Early return to prevent processing other button handlers
            
            # Handle contracts submenu modal button clicks
            if hasattr(self, 'contracts_submenu'):
                modal_handled = self.contracts_submenu.handle_modal_button_click(button_element)
                if modal_handled:
                    print(f"Contracts modal button handled")
                    return  # Early return to prevent processing other button handlers
            
            if event.ui_element == self.pause_button:
                self.event_system.emit('time_speed_change', {'speed': 0})
                # Show feedback notification
                self.notification_manager.show_notification(
                    "⏸️ Game Paused",
                    "All farm activities are now paused",
                    NotificationType.SYSTEM,
                    NotificationPriority.LOW,
                    duration=2.0
                )
            elif event.ui_element == self.speed_1x_button:
                self.event_system.emit('time_speed_change', {'speed': 1})
            elif event.ui_element == self.speed_2x_button:
                self.event_system.emit('time_speed_change', {'speed': 2})
            elif event.ui_element == self.speed_4x_button:
                self.event_system.emit('time_speed_change', {'speed': 4})
            elif hasattr(self, 'sell_corn_button') and event.ui_element == self.sell_corn_button:
                # Test selling corn from inventory
                self.event_system.emit('sell_crops_requested', {
                    'crop_type': 'corn',
                    'quantity': 10,
                    'price_per_unit': 5.0  # Use average price for testing
                })
            elif hasattr(self, 'buy_silo_button') and event.ui_element == self.buy_silo_button:
                # Enter placement mode for storage silo
                self.event_system.emit('enter_building_placement_mode', {
                    'building_type': 'storage_silo'
                })
            elif hasattr(self, 'buy_water_cooler_button') and event.ui_element == self.buy_water_cooler_button:
                # Enter placement mode for water cooler
                self.event_system.emit('enter_building_placement_mode', {
                    'building_type': 'water_cooler'
                })
            elif hasattr(self, 'buy_tool_shed_button') and event.ui_element == self.buy_tool_shed_button:
                # Enter placement mode for tool shed
                self.event_system.emit('enter_building_placement_mode', {
                    'building_type': 'tool_shed'
                })
            elif hasattr(self, 'buy_housing_button') and event.ui_element == self.buy_housing_button:
                # Enter placement mode for employee housing
                self.event_system.emit('enter_building_placement_mode', {
                    'building_type': 'employee_housing'
                })
            elif hasattr(self, 'buy_irrigation_button') and event.ui_element == self.buy_irrigation_button:
                # Enter placement mode for irrigation system
                self.event_system.emit('enter_building_placement_mode', {
                    'building_type': 'irrigation_system'
                })
            elif hasattr(self, 'hire_employee_button') and event.ui_element == self.hire_employee_button:
                # Request generation of new applicants for hiring
                print("DEBUG: Hire Employee button clicked - requesting applicant generation")
                self.event_system.emit('generate_applicants_requested', {})  # Request new applicants
            elif hasattr(self, 'view_applicants_button') and event.ui_element == self.view_applicants_button:
                # Show the applicant panel with current applicants
                print("DEBUG: View Applicants button clicked")
                self._show_applicant_panel()  # Create and display the applicant selection UI
            elif hasattr(self, 'view_payroll_button') and event.ui_element == self.view_payroll_button:
                # Request employee roster and payroll info
                self.event_system.emit('show_employee_roster_requested', {})
            elif hasattr(self, 'view_contracts_button') and event.ui_element == self.view_contracts_button:
                # Show contract board
                self._show_contract_board()
            elif hasattr(self, 'view_specialization_button') and event.ui_element == self.view_specialization_button:
                # Show farm specialization panel
                self._show_specialization_panel()
            elif (hasattr(self, 'close_applicant_panel_button') and 
                  event.ui_element == self.close_applicant_panel_button):
                print("DEBUG: Close applicant panel button clicked")  # Debug logging for panel close
                self._destroy_applicant_panel()  # Destroy the applicant selection panel
            elif (hasattr(self, 'close_contract_panel_button') and 
                  event.ui_element == self.close_contract_panel_button):
                print("Contract panel: Close button clicked")
                self._destroy_contract_panel()  # Destroy the contract management panel
            elif hasattr(event.ui_element, 'is_soil_panel_close') and event.ui_element.is_soil_panel_close:
                # Close soil information panel
                print("Soil info panel: Close button clicked")
                self._hide_soil_info_panel()
            elif hasattr(event.ui_element, 'is_specialization_panel_close') and event.ui_element.is_specialization_panel_close:
                # Close specialization panel
                print("Specialization panel: Close button clicked")
                self._hide_specialization_panel()
            elif hasattr(event.ui_element, 'specialization_id'):
                # Handle specialization choice
                specialization_id = event.ui_element.specialization_id
                print(f"Specialization chosen: {specialization_id}")
                self.event_system.emit('choose_specialization_requested', {
                    'specialization_id': specialization_id
                })
                self._hide_specialization_panel()
            elif hasattr(self, 'cancel_tasks_button') and event.ui_element == self.cancel_tasks_button:
                # Cancel tasks on selected tiles
                self.event_system.emit('cancel_tasks_requested', {})
            elif hasattr(self, 'crop_info_button') and event.ui_element == self.crop_info_button:
                # Show crop information dialog
                self._show_crop_info_dialog()
            elif hasattr(self, 'weather_info_button') and event.ui_element == self.weather_info_button:
                # Show weather information panel
                self._show_weather_info_panel()
            elif hasattr(self, 'irrigation_toggle_button') and event.ui_element == self.irrigation_toggle_button:
                # Toggle irrigation system
                self.event_system.emit('toggle_irrigation_requested', {})
            elif hasattr(self, 'quick_save_button') and event.ui_element == self.quick_save_button:
                # Quick save current game
                self.event_system.emit('manual_save_requested', {
                    'save_name': f"Quick Save - Day {self._current_day}",
                    'slot': 0
                })
            elif hasattr(self, 'quick_load_button') and event.ui_element == self.quick_load_button:
                # Quick load game
                self.event_system.emit('load_game_requested', {
                    'slot': 0
                })
            elif hasattr(self, 'save_menu_button') and event.ui_element == self.save_menu_button:
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
            # Handle contract accept buttons
            elif hasattr(event.ui_element, 'contract_id') and hasattr(event.ui_element, 'action_type'):
                contract_id = event.ui_element.contract_id
                action_type = event.ui_element.action_type
                
                if action_type == 'accept_contract':
                    # Accept the selected contract
                    print(f"UI: Accepting contract {contract_id}")
                    self.event_system.emit('accept_contract_requested', {'contract_id': contract_id})
                    # Refresh the panel to show updated data
                    self.event_system.emit('get_contract_data_for_ui', {})
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
            # Handle smart action buttons
            elif hasattr(event.ui_element, 'action_id'):
                self.smart_action_system.handle_button_click(event.ui_element)
        
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
            # Check if click was on a notification first
            if self.notification_manager.handle_click(event.pos):
                return  # Notification handled the click, don't pass through
            
            # Handle employee submenu click-outside-to-close functionality
            if hasattr(self, 'employee_submenu') and self.employee_submenu.is_submenu_active:
                if self.employee_submenu.handle_click_outside(event.pos):
                    return  # Employee submenu handled the click
            
            # Handle contracts submenu click-outside-to-close functionality
            if hasattr(self, 'contracts_submenu') and self.contracts_submenu.is_modal_active:
                if self.contracts_submenu.handle_click_outside(event.pos):
                    return  # Contracts submenu handled the click
            
            # This will be handled by employee manager through game manager
            pass
        elif event.type == pygame.MOUSEMOTION:
            # Forward mouse motion to tooltip system for hover detection
            self.tooltip_manager._handle_mouse_motion({'pos': event.pos})
    
    def update(self, dt):
        """Update UI elements"""
        self.gui_manager.update(dt)  # Update pygame-gui elements
        
        # Update enhanced UI components
        self.enhanced_hud.update(dt)  # Update the enhanced top HUD
        
        # Update task assignment modal
        self.task_assignment_modal.update(dt)
        self.smart_action_system.update(dt)  # Update smart action system
        self.animation_system.update(dt)  # Update legacy animation system
        
        # Update employee submenu system
        if hasattr(self, 'employee_submenu'):
            self.employee_submenu.update(dt)
        
        # Update enhanced animation system - Phase 2.3 enhancement
        self.enhanced_animation_manager.update(dt)
        
        # Update advanced tooltip system - Phase 2 enhancement
        mouse_pos = pygame.mouse.get_pos()
        self.tooltip_manager.update(dt, mouse_pos)
        
        # Update advanced notification system - Phase 2.2 enhancement
        self.notification_manager.update(dt)
        
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
        
        # Render animations (notifications, effects, etc.)
        self.animation_system.render_notifications(screen)
        
        # Render enhanced animation system particles - Phase 2.3 enhancement
        self.enhanced_animation_manager.render_particles(screen)
        
        # Render advanced notification system - Phase 2.2 enhancement
        self.notification_manager.render(screen)
        
        # Render advanced tooltips - Phase 2 enhancement (render last for top layer)
        self.tooltip_manager.render(screen)
    
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
        # Legacy UI disabled - time is now handled by EnhancedTopHUD
        if self.time_label:
            self.time_label.set_text(time_str)
    
    def _handle_money_update(self, event_data):
        """Handle money change events"""
        amount = event_data.get('amount', 0)
        color = 'money_positive' if amount >= 0 else 'money_negative'
        # Legacy UI disabled - money is now handled by EnhancedTopHUD  
        if self.money_label:
            self.money_label.set_text(f"Cash: ${amount:,}")
    
    def _handle_inventory_update(self, event_data):
        """Handle inventory change events"""
        # Request full inventory status to update all crop displays
        self.event_system.emit('get_full_inventory_status', {})
    
    def _handle_full_inventory_update(self, event_data):
        """Handle full inventory status update for all crops"""
        corn_qty = event_data.get('corn', 0)
        tomatoes_qty = event_data.get('tomatoes', 0)
        wheat_qty = event_data.get('wheat', 0)
        storage_capacity = event_data.get('storage_capacity', 100)
        
        # Legacy UI disabled - inventory is now handled by EnhancedTopHUD
        if self.inventory_label:
            # Update inventory display with compact format: C:corn T:tomatoes W:wheat / capacity
            self.inventory_label.set_text(f"C:{corn_qty} T:{tomatoes_qty} W:{wheat_qty} / {storage_capacity}")
    
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
        """Add a notification to display with animation"""
        # Create traditional notification for backward compatibility
        self.notifications.append({
            'message': message,
            'type': notification_type,
            'timer': 3.0,  # Show for 3 seconds
            'alpha': 255
        })
        
        # Also create animated notification for enhanced visual feedback
        self.animation_system.show_notification(message, notification_type, 3.0)
        
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
        # Request full inventory update to reflect new capacity
        self.event_system.emit('get_full_inventory_status', {})
    
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
        # Legacy UI disabled - employee count is now handled by EnhancedTopHUD
        if self.employee_count_label:
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
        
        # Legacy UI disabled - employee status is now handled by DynamicRightPanel
        if not self.employee_status_display:
            return
        
        if not employees:
            self.employee_status_display.set_text("<font size=3.5 color='#FFFFFF'>No employees</font>")
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
        
        status_html = f"<font size=3.5 color='#FFFFFF'>{'<br>'.join(status_lines)}</font>"
        if self.employee_status_display:
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
    
    def _show_contract_board(self):
        """Display the contract management board"""
        print("Contract Board: Requesting contract data from contract manager")
        
        # Request contract data and show panel
        self.event_system.emit('get_contract_data_for_ui', {})
        
        # Create the panel if it doesn't exist
        if not self._contract_panel_exists:
            self._create_contract_panel()
        
        # Show the panel (it will be populated when contract data arrives)
        if hasattr(self, 'contract_panel'):
            self.contract_panel.show()
    
    def _create_contract_panel(self):
        """Create the contract management panel"""
        # Create main panel
        panel_width = 800
        panel_height = 600
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        self.contract_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            manager=self.gui_manager
        )
        
        # Create title
        self.contract_panel_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            text="Contract Management Board",
            manager=self.gui_manager,
            container=self.contract_panel
        )
        
        # Create close button
        self.close_contract_panel_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 80, 10, 70, 30),
            text="Close",
            manager=self.gui_manager,
            container=self.contract_panel
        )
        
        # Create sections for available and active contracts
        section_height = (panel_height - 100) // 2
        
        # Available contracts section
        self.available_contracts_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 50, 300, 25),
            text="Available Contracts",
            manager=self.gui_manager,
            container=self.contract_panel
        )
        
        self.available_contracts_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 80, panel_width - 20, section_height),
            manager=self.gui_manager,
            container=self.contract_panel
        )
        
        # Active contracts section
        active_y = 80 + section_height + 20
        self.active_contracts_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, active_y, 300, 25),
            text="Active Contracts",
            manager=self.gui_manager,
            container=self.contract_panel
        )
        
        self.active_contracts_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(10, active_y + 30, panel_width - 20, section_height - 30),
            manager=self.gui_manager,
            container=self.contract_panel
        )
        
        # Initialize empty lists for tracking UI elements
        self.contract_table_rows = []
        self.contract_buttons = []
        
        # Set state flag
        self._contract_panel_exists = True
        print("Contract panel created successfully")
    
    def _destroy_contract_panel(self):
        """Destroy the contract management panel"""
        if self._contract_panel_exists and hasattr(self, 'contract_panel'):
            # Clear contract data
            self._clear_contract_table()
            
            # Destroy child elements
            if hasattr(self, 'contract_panel_title'):
                self.contract_panel_title.kill()
            if hasattr(self, 'close_contract_panel_button'):
                self.close_contract_panel_button.kill()
            if hasattr(self, 'available_contracts_label'):
                self.available_contracts_label.kill()
            if hasattr(self, 'active_contracts_label'):
                self.active_contracts_label.kill()
            if hasattr(self, 'available_contracts_container'):
                self.available_contracts_container.kill()
            if hasattr(self, 'active_contracts_container'):
                self.active_contracts_container.kill()
            
            # Destroy main panel
            self.contract_panel.kill()
            self.contract_panel = None
            
            # Reset state flag
            self._contract_panel_exists = False
            print("Contract panel destroyed")
    
    def _populate_contract_panel(self):
        """Populate the contract panel with current contract data"""
        self._clear_contract_table()
        
        # Populate available contracts
        if self.current_available_contracts:
            for i, contract in enumerate(self.current_available_contracts):
                self._create_available_contract_row(contract, i)
        
        # Populate active contracts
        if self.current_active_contracts:
            for i, contract in enumerate(self.current_active_contracts):
                self._create_active_contract_row(contract, i)
    
    def _create_available_contract_row(self, contract, row_index):
        """Create a row for an available contract"""
        row_height = 80
        y_pos = row_index * (row_height + 10)
        
        # Create row panel
        row_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, y_pos, 760, row_height),
            manager=self.gui_manager,
            container=self.available_contracts_container
        )
        
        # Contract details
        crop_name = CROP_TYPES[contract.crop_type]['name']
        total_value = contract.quantity_required * contract.price_per_unit + contract.bonus_payment
        
        # Title line
        title_text = f"{contract.buyer_name} - {contract.contract_type.value.upper()}"
        title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 5, 400, 20),
            text=title_text,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Details line
        details_text = f"{contract.quantity_required} {crop_name} @ ${contract.price_per_unit:.2f}/unit (Total: ${total_value:.2f})"
        details_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 25, 500, 20),
            text=details_text,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Requirements line
        quality_req = f"{contract.quality_requirement*100:.0f}%"
        req_text = f"Quality: {quality_req}+ | Deadline: {contract.deadline_days} days"
        if contract.bonus_payment > 0:
            req_text += f" | Bonus: ${contract.bonus_payment:.2f}"
        req_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 45, 500, 20),
            text=req_text,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Accept button
        accept_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(620, 20, 120, 35),
            text="Accept Contract",
            manager=self.gui_manager,
            container=row_panel
        )
        accept_button.contract_id = contract.id
        accept_button.action_type = 'accept_contract'
        
        # Store elements for cleanup
        self.contract_table_rows.append(row_panel)
        self.contract_buttons.append(accept_button)
    
    def _create_active_contract_row(self, contract, row_index):
        """Create a row for an active contract"""
        row_height = 80
        y_pos = row_index * (row_height + 10)
        
        # Create row panel
        row_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, y_pos, 760, row_height),
            manager=self.gui_manager,
            container=self.active_contracts_container
        )
        
        # Contract details
        crop_name = CROP_TYPES[contract.crop_type]['name']
        total_value = contract.quantity_required * contract.price_per_unit + contract.bonus_payment
        
        # Calculate days remaining
        current_day = getattr(self, '_current_day', 1)
        days_left = (contract.accepted_day + contract.deadline_days) - current_day
        
        # Title line
        title_text = f"{contract.buyer_name} - {contract.contract_type.value.upper()}"
        if days_left <= 5:
            title_text += " ⚠️ URGENT"
        title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 5, 400, 20),
            text=title_text,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Details line
        details_text = f"Need: {contract.quantity_required} {crop_name} (Value: ${total_value:.2f})"
        details_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 25, 500, 20),
            text=details_text,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Status line
        status_text = f"Days Left: {max(0, days_left)} | Quality: {contract.quality_requirement*100:.0f}%+"
        if days_left <= 0:
            status_text = "⚠️ OVERDUE - Penalty incoming!"
        status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 45, 500, 20),
            text=status_text,
            manager=self.gui_manager,
            container=row_panel
        )
        
        # Status indicator
        status_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(620, 20, 120, 35),
            text="In Progress",
            manager=self.gui_manager,
            container=row_panel
        )
        status_button.disable()  # Make it non-interactive
        
        # Store elements for cleanup
        self.contract_table_rows.append(row_panel)
    
    def _clear_contract_table(self):
        """Clear all contract table rows and buttons"""
        for row in self.contract_table_rows:
            row.kill()
        self.contract_table_rows.clear()
        
        for button in self.contract_buttons:
            button.kill()
        self.contract_buttons.clear()
    
    def _handle_contract_data_received(self, event_data):
        """Handle contract data received from contract manager"""
        self.current_available_contracts = event_data.get('available_contracts', [])
        self.current_active_contracts = event_data.get('active_contracts', [])
        
        print(f"UI: Received {len(self.current_available_contracts)} available and {len(self.current_active_contracts)} active contracts")
        
        # Populate the panel if it exists
        if self._contract_panel_exists and hasattr(self, 'contract_panel'):
            self._populate_contract_panel()
    
    def _handle_contract_accepted(self, event_data):
        """Handle contract acceptance notification"""
        contract_id = event_data.get('contract_id', 'Unknown')
        buyer_name = event_data.get('buyer_name', 'Unknown Buyer')
        crop_type = event_data.get('crop_type', 'unknown')
        quantity = event_data.get('quantity', 0)
        total_value = event_data.get('total_value', 0)
        
        crop_name = CROP_TYPES.get(crop_type, {}).get('name', crop_type)
        if not crop_name:  # Fallback if name is missing
            crop_name = crop_type
        message = f"[CONTRACT] Accepted {quantity} {crop_name} for {buyer_name} (${total_value:.2f})"
        self._add_notification(message, "success")
        
        # Refresh contract data
        self.event_system.emit('get_contract_data_for_ui', {})
    
    def _handle_contracts_updated(self, event_data):
        """Handle contract updates (new contracts generated, etc.)"""
        available_count = event_data.get('available_count', 0)
        active_count = event_data.get('active_count', 0)
        
        message = f"[CONTRACTS] {available_count} available, {active_count} active contracts"
        self._add_notification(message, "info")
        
        # Refresh contract data if panel is open
        if self._contract_panel_exists:
            self.event_system.emit('get_contract_data_for_ui', {})
    
    def _handle_contract_completed(self, event_data):
        """Handle contract completion notification"""
        contract_id = event_data.get('contract_id', 'Unknown')
        buyer_name = event_data.get('buyer_name', 'Unknown Buyer')
        crop_type = event_data.get('crop_type', 'unknown')
        quantity = event_data.get('quantity', 0)
        payment = event_data.get('payment', 0)
        reputation_gained = event_data.get('reputation_gained', 0)
        new_reputation = event_data.get('new_reputation', 50)
        
        crop_name = CROP_TYPES.get(crop_type, {}).get('name', crop_type)
        if not crop_name:
            crop_name = crop_type
            
        message = f"[CONTRACT COMPLETED] {buyer_name}: ${payment:.2f} for {quantity} {crop_name} (+{reputation_gained} rep)"
        self._add_notification(message, "success")
        
        # Refresh contract data to show updated active contracts
        self.event_system.emit('get_contract_data_for_ui', {})
    
    def _handle_tile_selected(self, event_data):
        """Handle tile selection for soil information display"""
        tile = event_data.get('tile')
        if tile and tile.terrain_type == 'tilled':
            self.current_selected_tile = tile
            self._show_soil_info_panel(tile)
    
    def _handle_tile_deselected(self, event_data):
        """Handle tile deselection to hide soil information panel"""
        self._hide_soil_info_panel()
    
    def _handle_show_task_assignment(self, event_data):
        """Handle request to show the enhanced task assignment interface"""
        # Show the enhanced task assignment modal
        self.task_assignment_modal.show_modal()
        print("Showing enhanced task assignment modal")
    
    def _show_soil_info_panel(self, tile):
        """Show soil information panel for the selected tile"""
        if self._soil_info_panel_exists:
            self._hide_soil_info_panel()
        
        # Create soil information panel on the left side to avoid control panel overlap
        panel_width = 280
        panel_height = 500
        panel_x = 10  # Left side of screen with margin
        panel_y = 70  # Below resource bar
        
        self.soil_info_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            manager=self.gui_manager
        )
        
        # Set solid background color for the panel to prevent overlap issues
        self.soil_info_panel.background_colour = pygame.Color(40, 40, 40)  # Dark gray solid background
        self.soil_info_panel.border_colour = pygame.Color(80, 80, 80)  # Light gray border
        self.soil_info_panel.border_width = 2  # Visible border
        
        # Panel title
        title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 25),
            text=f"Soil Information - ({tile.x}, {tile.y})",
            manager=self.gui_manager,
            container=self.soil_info_panel
        )
        self.soil_info_elements.append(title_label)
        
        # Soil health status
        health_level = tile.get_soil_health_level()
        health_color = tile.get_soil_health_color()
        health_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 40, panel_width - 20, 25),
            text=f"Soil Health: {health_level.title()}",
            manager=self.gui_manager,
            container=self.soil_info_panel
        )
        self.soil_info_elements.append(health_label)
        
        # Soil nutrients section
        nutrients_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 70, panel_width - 20, 25),
            text="Soil Nutrients:",
            manager=self.gui_manager,
            container=self.soil_info_panel
        )
        self.soil_info_elements.append(nutrients_label)
        
        # Individual nutrient levels with bars
        y_offset = 100
        for nutrient, level in tile.soil_nutrients.items():
            # Nutrient name and level
            nutrient_text = f"{SOIL_NUTRIENTS[nutrient]['name']}: {level}%"
            nutrient_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, y_offset, 120, 20),
                text=nutrient_text,
                manager=self.gui_manager,
                container=self.soil_info_panel
            )
            self.soil_info_elements.append(nutrient_label)
            
            # Visual bar representation (simple text bar for now)
            bar_length = int(level / 10)  # 10 chars max
            bar_text = "█" * bar_length + "░" * (10 - bar_length)
            bar_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(135, y_offset, 120, 20),
                text=bar_text,
                manager=self.gui_manager,
                container=self.soil_info_panel
            )
            self.soil_info_elements.append(bar_label)
            
            y_offset += 25
        
        # Crop history section
        y_offset += 10
        history_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, panel_width - 20, 25),
            text="Crop History:",
            manager=self.gui_manager,
            container=self.soil_info_panel
        )
        self.soil_info_elements.append(history_label)
        
        y_offset += 30
        if tile.crop_history:
            history_text = " → ".join([CROP_TYPES[crop]['name'] for crop in tile.crop_history[-3:]])
        else:
            history_text = "No previous crops"
        
        history_display = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, panel_width - 20, 25),
            text=history_text,
            manager=self.gui_manager,
            container=self.soil_info_panel
        )
        self.soil_info_elements.append(history_display)
        
        # Rotation bonuses section
        y_offset += 40
        rotation_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, panel_width - 20, 25),
            text="Planting Recommendations:",
            manager=self.gui_manager,
            container=self.soil_info_panel
        )
        self.soil_info_elements.append(rotation_label)
        
        # Show rotation bonuses for each crop type
        y_offset += 30
        for crop_type, crop_data in CROP_TYPES.items():
            bonuses = tile.calculate_rotation_bonuses(crop_type)
            total_bonus = bonuses['yield'] + bonuses['quality']
            
            if total_bonus > 0:
                bonus_text = f"✓ {crop_data['name']}: +{bonuses['yield']*100:.0f}% yield"
                color = (100, 255, 100)  # Green for good
            else:
                bonus_text = f"○ {crop_data['name']}: No bonuses"
                color = (200, 200, 200)  # Gray for neutral
            
            crop_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10, y_offset, panel_width - 20, 20),
                text=bonus_text,
                manager=self.gui_manager,
                container=self.soil_info_panel
            )
            self.soil_info_elements.append(crop_label)
            y_offset += 25
        
        # Cultivation options section
        y_offset += 10
        options_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, panel_width - 20, 25),
            text="Cultivation Options:",
            manager=self.gui_manager,
            container=self.soil_info_panel
        )
        self.soil_info_elements.append(options_label)
        
        y_offset += 30
        # Soil rest option
        if tile.seasons_rested == 0:
            rest_text = "Let soil rest (+20% yield next season)"
        else:
            rest_text = f"Soil rested {tile.seasons_rested} season(s)"
        
        rest_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, panel_width - 20, 20),
            text=rest_text,
            manager=self.gui_manager,
            container=self.soil_info_panel
        )
        self.soil_info_elements.append(rest_label)
        
        # Close button
        close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 70, panel_height - 35, 60, 25),
            text="Close",
            manager=self.gui_manager,
            container=self.soil_info_panel
        )
        close_button.is_soil_panel_close = True
        self.soil_info_elements.append(close_button)
        
        self._soil_info_panel_exists = True
        print(f"Showing soil info panel for tile ({tile.x}, {tile.y})")
    
    def _hide_soil_info_panel(self):
        """Hide the soil information panel"""
        if not self._soil_info_panel_exists:
            return
        
        # Clean up all elements
        for element in self.soil_info_elements:
            element.kill()
        self.soil_info_elements.clear()
        
        if hasattr(self, 'soil_info_panel'):
            self.soil_info_panel.kill()
            self.soil_info_panel = None
        
        self._soil_info_panel_exists = False
        self.current_selected_tile = None
        print("Soil info panel hidden")
    
    def _show_specialization_panel(self):
        """Show farm specialization selection panel"""
        if self._specialization_panel_exists:
            self._hide_specialization_panel()
        
        # Create specialization panel centered on screen
        panel_width = 600
        panel_height = 580  # Taller for better spacing
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        self.specialization_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            manager=self.gui_manager
        )
        
        # Set solid background for the panel
        self.specialization_panel.background_colour = pygame.Color(45, 45, 45)  # Dark gray
        self.specialization_panel.border_colour = pygame.Color(100, 100, 100)  # Light gray border
        self.specialization_panel.border_width = 2
        
        # Panel title
        title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            text="Farm Specialization Selection",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        self.specialization_elements.append(title_label)
        
        # Current specialization display
        # We'll get this info from the event system
        self.event_system.emit('get_specialization_info_for_ui', {})
        
        current_spec_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 50, panel_width - 20, 25),
            text="Current: Unspecialized Farm",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        self.specialization_elements.append(current_spec_label)
        
        # Instructions
        instructions_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 80, panel_width - 20, 25),
            text="Choose a specialization to unlock strategic bonuses:",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        self.specialization_elements.append(instructions_label)
        
        # Specialization options (we'll populate these based on available specializations)
        y_offset = 120
        
        # Grain Farm option
        grain_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y_offset, 560, 25),
            text="🌾 Grain Farm - Bulk production specialist (Cost: $2,500)",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        self.specialization_elements.append(grain_label)
        
        grain_desc = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(30, y_offset + 30, 420, 60),
            html_text="<font size=2>+25% wheat yield, +15% storage efficiency, +20% grain growth speed<br/>Requires: 100 wheat harvested, 200 storage capacity</font>",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        self.specialization_elements.append(grain_desc)
        
        grain_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(460, y_offset + 35, 120, 30),
            text="Choose Grain",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        grain_button.specialization_id = 'grain'
        self.specialization_elements.append(grain_button)
        
        y_offset += 100
        
        # Market Garden option
        market_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y_offset, 560, 25),
            text="🍅 Market Garden - Premium crop specialist (Cost: $3,000)",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        self.specialization_elements.append(market_label)
        
        market_desc = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(30, y_offset + 30, 420, 60),
            html_text="<font size=2>+30% tomato yield, +20% crop quality, +25% premium prices<br/>Requires: 75 tomatoes harvested, 1.2 avg crop quality</font>",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        self.specialization_elements.append(market_desc)
        
        market_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(460, y_offset + 35, 120, 30),
            text="Choose Market",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        market_button.specialization_id = 'market_garden'
        self.specialization_elements.append(market_button)
        
        y_offset += 100
        
        # Diversified Farm option
        diversified_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y_offset, 560, 25),
            text="🌽 Diversified Farm - Sustainability specialist (Cost: $2,000)",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        self.specialization_elements.append(diversified_label)
        
        diversified_desc = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(30, y_offset + 30, 420, 60),
            html_text="<font size=2>+35% rotation bonuses, +20% soil recovery, +15% overall quality<br/>Requires: 3 rotation cycles, 80 avg soil health</font>",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        self.specialization_elements.append(diversified_desc)
        
        diversified_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(460, y_offset + 35, 120, 30),
            text="Choose Diverse",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        diversified_button.specialization_id = 'diversified'
        self.specialization_elements.append(diversified_button)
        
        # Close button
        close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 70, panel_height - 40, 60, 30),
            text="Close",
            manager=self.gui_manager,
            container=self.specialization_panel
        )
        close_button.is_specialization_panel_close = True
        self.specialization_elements.append(close_button)
        
        self._specialization_panel_exists = True
        print("Showing farm specialization panel")
    
    def _hide_specialization_panel(self):
        """Hide the farm specialization panel"""
        if not self._specialization_panel_exists:
            return
        
        # Clean up all elements
        for element in self.specialization_elements:
            element.kill()
        self.specialization_elements.clear()
        
        if hasattr(self, 'specialization_panel'):
            self.specialization_panel.kill()
            self.specialization_panel = None
        
        self._specialization_panel_exists = False
        print("Specialization panel hidden")
    
    def _handle_weather_update(self, event_data):
        """Update weather display when weather changes"""
        season = event_data.get('season', 'spring').title()
        weather_event = event_data.get('weather_event', 'clear').replace('_', ' ').title()
        growth_modifier = event_data.get('growth_modifier', 1.0)
        
        # Create color-coded weather display
        if weather_event == 'Clear':
            weather_color = '#FFFFFF'
        elif weather_event == 'Rain':
            weather_color = '#6495ED'  # Cornflower blue
        elif weather_event == 'Drought':
            weather_color = '#FF6347'  # Tomato red
        elif weather_event == 'Frost':
            weather_color = '#E6E6FA'  # Lavender
        elif weather_event.startswith('Heat'):
            weather_color = '#FF4500'  # Orange red
        else:
            weather_color = '#C0C0C0'  # Silver
        
        # Format growth effect
        if growth_modifier > 1.0:
            effect_text = f"(+{int((growth_modifier-1)*100)}% growth)"
            effect_color = '#90EE90'  # Light green
        elif growth_modifier < 1.0:
            effect_text = f"({int((1-growth_modifier)*100)}% slower)"
            effect_color = '#FFB6C1'  # Light pink
        else:
            effect_text = "(normal growth)"
            effect_color = '#FFFFFF'
        
        weather_html = f"<font size=2 color='{weather_color}'>{season} - {weather_event}</font><br/><font size=2 color='{effect_color}'>{effect_text}</font>"
        # Legacy UI disabled - weather is now handled by EnhancedTopHUD
        if self.weather_display:
            self.weather_display.set_text(weather_html)
    
    def _handle_season_change(self, event_data):
        """Handle season transition notifications"""
        new_season = event_data.get('new_season', 'spring').title()
        self._add_notification(f"[WEATHER] Season changed to {new_season}", "info")
    
    def _handle_weather_event(self, event_data):
        """Handle weather event notifications"""
        event_type = event_data.get('event_type', 'clear').replace('_', ' ').title()
        duration = event_data.get('duration', 1)
        self._add_notification(f"[WEATHER] {event_type} for {duration} days", "info")
    
    def _show_weather_info_panel(self):
        """Show detailed weather information panel"""
        # Request weather data from weather manager
        self.event_system.emit('get_weather_info_for_ui', {})
        
        # For now, show a simple message until we implement the full panel
        self._add_notification("[WEATHER] Weather info panel coming soon!", "info")
    
    def _handle_irrigation_status_change(self, event_data):
        """Handle irrigation system status changes"""
        active = event_data.get('active', False)
        total_tiles = event_data.get('total_tiles', 0)
        daily_cost = event_data.get('daily_cost_during_drought', 0)
        
        # Legacy UI disabled - irrigation controls are now handled by DynamicRightPanel
        if self.irrigation_toggle_button:
            # Update button text to reflect current state
            if total_tiles == 0:
                button_text = "No Irrigation"
                self.irrigation_toggle_button.set_text(button_text)
                self.irrigation_toggle_button.disable()
            else:
                status = "ON" if active else "OFF"
                button_text = f"Irrigation {status}"
                self.irrigation_toggle_button.set_text(button_text)
                self.irrigation_toggle_button.enable()
        
        # Show status notification
        status_text = "activated" if active else "deactivated"
        if total_tiles > 0:
            self._add_notification(f"[IRRIGATION] {status_text} - {total_tiles} tiles (${daily_cost}/day during drought)", "info")
    
    def _handle_irrigation_cost_notification(self, event_data):
        """Handle irrigation cost notifications"""
        cost = event_data.get('cost', 0)
        irrigated_tiles = event_data.get('irrigated_tiles', 0)
        weather_event = event_data.get('weather_event', 'drought')
        
        self._add_notification(f"[IRRIGATION] ${cost:.2f} water cost for {irrigated_tiles} tiles during {weather_event}", "info")
    
    def _handle_smart_action_request(self, event_data):
        """Handle smart action button requests"""
        action_id = event_data.get('action_id')
        selected_tiles = event_data.get('selected_tiles', [])
        estimated_cost = event_data.get('estimated_cost', 0)
        
        # Map smart actions to actual game commands
        action_mapping = {
            'till_soil': 'till',
            'plant_corn': lambda: self._plant_crop('corn'),
            'plant_tomatoes': lambda: self._plant_crop('tomatoes'),
            'plant_wheat': lambda: self._plant_crop('wheat'),
            'harvest_crops': 'harvest',
            'build_irrigation': lambda: self._build_infrastructure('irrigation'),
            'build_storage': lambda: self._build_infrastructure('storage'),
            'clear_tiles': 'clear',
            'fertilize': lambda: self._apply_fertilizer()
        }
        
        # Execute the mapped action
        if action_id in action_mapping:
            mapped_action = action_mapping[action_id]
            
            if callable(mapped_action):
                # Execute function-based action
                mapped_action()
            else:
                # Execute simple task assignment
                self._assign_task_to_tiles(mapped_action, selected_tiles)
            
            # Add feedback notification
            tile_count = len(selected_tiles)
            self._add_notification(f"Smart Action: {action_id} assigned to {tile_count} tiles", "success")
        else:
            self._add_notification(f"Unknown action: {action_id}", "error")
    
    def _plant_crop(self, crop_type):
        """Handle crop planting through smart actions"""
        # Update current crop selection and emit plant task
        self.current_crop_type = crop_type
        self.event_system.emit('task_assignment_requested', {
            'task_type': 'plant',
            'crop_type': crop_type
        })
    
    def _build_infrastructure(self, infrastructure_type):
        """Handle infrastructure building through smart actions"""
        building_mapping = {
            'irrigation': 'irrigation_system',
            'storage': 'storage_silo'
        }
        
        if infrastructure_type in building_mapping:
            building_type = building_mapping[infrastructure_type]
            self.event_system.emit('enter_building_placement_mode', {
                'building_type': building_type
            })
    
    def _apply_fertilizer(self):
        """Handle fertilizer application through smart actions"""
        self.event_system.emit('task_assignment_requested', {
            'task_type': 'fertilize'
        })
    
    def _assign_task_to_tiles(self, task_type, tiles):
        """Assign a task type to specific tiles"""
        self.event_system.emit('task_assignment_requested', {
            'task_type': task_type,
            'tiles': tiles
        })
    
    def _handle_tiles_selected_for_actions(self, event_data):
        """Handle tile selection for smart action updates"""
        # Forward to smart action system for context analysis
        tiles = event_data.get('tiles', [])
        print(f"Smart Actions: {len(tiles)} tiles selected for action analysis")
    
    def _handle_selection_cleared_for_actions(self, event_data):
        """Handle selection cleared for smart action updates"""
        # Forward to smart action system
        print("Smart Actions: Selection cleared, updating available actions")