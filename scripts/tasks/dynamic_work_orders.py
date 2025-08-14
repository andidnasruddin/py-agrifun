"""
Dynamic Work Order Generation System - Phase 2B
Automatically creates intelligent work orders based on farm conditions, crop status, and events.
Transforms reactive gameplay into proactive agricultural management.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from scripts.core.config import *
from scripts.tasks.task_models import TaskType, TaskPriority, EmployeeRole
from scripts.tasks.work_order_manager import WorkOrderManager


class DynamicWorkOrderGenerator:
    """
    Intelligent work order generation system
    Analyzes farm conditions and automatically creates appropriate work orders
    """
    
    def __init__(self, work_order_manager: WorkOrderManager, event_system):
        """Initialize the dynamic work order generator"""
        self.work_order_manager = work_order_manager  # Work order manager instance
        self.event_system = event_system  # Event system for communication
        
        # Analysis configuration
        self.scan_interval = 60.0  # Seconds between farm analysis scans
        self.last_scan_time = 0.0  # Last time we scanned the farm
        
        # Smart generation settings
        self.min_plots_for_order = 3  # Minimum plots to create a work order
        self.max_lookahead_days = 5  # Days to look ahead for planning
        self.batch_similar_tasks = True  # Combine similar adjacent tasks
        
        # Condition tracking
        self.last_analysis = {}  # Store last analysis results
        self.pending_conditions = {}  # Track conditions that need work orders
        
        # Subscribe to relevant events
        self._setup_event_handlers()
        
        print("Dynamic Work Order Generator initialized")
        print(f"  Scan interval: {self.scan_interval}s")
        print(f"  Min plots per order: {self.min_plots_for_order}")
        print(f"  Lookahead planning: {self.max_lookahead_days} days")
    
    def _setup_event_handlers(self):
        """Set up event handlers for dynamic generation"""
        # Time-based scanning
        self.event_system.subscribe('time_updated', self._handle_time_update)
        self.event_system.subscribe('day_passed', self._handle_day_passed)
        
        # Crop condition events
        self.event_system.subscribe('crop_growth_stage_changed', self._handle_crop_growth)
        self.event_system.subscribe('crop_ready_for_harvest', self._handle_crop_ready)
        self.event_system.subscribe('soil_depleted', self._handle_soil_depletion)
        
        # Environmental events
        self.event_system.subscribe('weather_forecast', self._handle_weather_forecast)
        self.event_system.subscribe('season_changed', self._handle_season_change)
        self.event_system.subscribe('pest_risk_detected', self._handle_pest_risk)
        
        # Player action events
        self.event_system.subscribe('plots_selected', self._handle_plots_selected)
        self.event_system.subscribe('field_designated', self._handle_field_designated)
    
    def analyze_farm_conditions(self, grid_manager) -> Dict[str, List[Tuple[int, int]]]:
        """
        Analyze current farm conditions and identify work order opportunities
        
        Returns:
            Dictionary mapping condition types to lists of plot coordinates
        """
        if not ENABLE_WORK_ORDERS or not ENABLE_DYNAMIC_TASK_GENERATION:
            return {}
        
        conditions = {
            'needs_tilling': [],
            'ready_for_planting': [],
            'needs_watering': [],
            'ready_for_harvest': [],
            'needs_fertilizing': [],
            'pest_control_needed': [],
            'processing_ready': [],
            'storage_needed': []
        }
        
        # Analyze each tile in the grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = grid_manager.grid[y][x]
                plot_coords = (x, y)
                
                # Skip if tile is occupied by buildings or already has work orders
                if tile.is_occupied or plot_coords in self.work_order_manager.plot_assignments:
                    continue
                
                # Analyze tile conditions
                self._analyze_tile_conditions(tile, plot_coords, conditions)
        
        # Filter out conditions with insufficient plots
        filtered_conditions = {}
        for condition, plots in conditions.items():
            if len(plots) >= self.min_plots_for_order:
                filtered_conditions[condition] = plots
                
        self.last_analysis = filtered_conditions
        return filtered_conditions
    
    def _analyze_tile_conditions(self, tile, coords: Tuple[int, int], conditions: Dict):
        """Analyze individual tile and categorize its needs"""
        
        # Check for tilling needs
        if tile.terrain_type == 'soil' and not tile.current_crop:
            # Soil that could be tilled for planting
            conditions['needs_tilling'].append(coords)
        
        # Check for planting opportunities
        elif tile.terrain_type == 'tilled' and not tile.current_crop:
            # Tilled soil ready for planting
            conditions['ready_for_planting'].append(coords)
        
        # Check crop conditions
        elif tile.current_crop:
            crop_stage = tile.growth_stage
            days_growing = tile.days_growing
            
            # Check if ready for harvest
            if crop_stage >= 4:  # Harvestable stage
                conditions['ready_for_harvest'].append(coords)
            
            # Check watering needs (simplified logic)
            elif tile.water_level < 30 and not tile.has_irrigation:
                conditions['needs_watering'].append(coords)
            
            # Check fertilizing needs (soil nutrients)
            elif self._needs_fertilizing(tile):
                conditions['needs_fertilizing'].append(coords)
            
            # Check pest control needs (simplified logic)
            elif self._needs_pest_control(tile, days_growing):
                conditions['pest_control_needed'].append(coords)
    
    def _needs_fertilizing(self, tile) -> bool:
        """Check if tile needs fertilizing based on soil nutrients"""
        if not hasattr(tile, 'soil_nutrients'):
            return False
        
        # Check if any nutrient is below threshold
        nutrient_threshold = 40  # Below 40% needs fertilizing
        for nutrient, level in tile.soil_nutrients.items():
            if level < nutrient_threshold:
                return True
        
        return False
    
    def _needs_pest_control(self, tile, days_growing: int) -> bool:
        """Check if tile needs pest control (simplified logic)"""
        # Simplified pest control logic
        # In reality, this would be based on pest pressure, crop type, etc.
        
        # Crops are vulnerable to pests during middle growth stages
        if 2 <= tile.growth_stage <= 3 and days_growing > 1:
            # Simplified risk: 10% chance per day after day 1 in vulnerable stages
            risk_factor = days_growing * 0.1
            return risk_factor > 0.5  # Simplified threshold
        
        return False
    
    def generate_work_orders_from_analysis(self, conditions: Dict[str, List[Tuple[int, int]]]) -> List[str]:
        """
        Generate work orders based on analyzed farm conditions
        
        Returns:
            List of work order IDs that were created
        """
        created_orders = []
        
        # Priority order for work order generation
        priority_mapping = {
            'ready_for_harvest': (TaskType.HARVESTING, TaskPriority.HIGH),
            'pest_control_needed': (TaskType.PEST_CONTROL, TaskPriority.HIGH),
            'needs_watering': (TaskType.WATERING, TaskPriority.NORMAL),
            'needs_fertilizing': (TaskType.FERTILIZING, TaskPriority.NORMAL),
            'ready_for_planting': (TaskType.PLANTING, TaskPriority.NORMAL),
            'needs_tilling': (TaskType.TILLING, TaskPriority.LOW),
            'processing_ready': (TaskType.PROCESSING, TaskPriority.LOW),
            'storage_needed': (TaskType.STORING, TaskPriority.LOW)
        }
        
        # Generate work orders in priority order
        for condition, (task_type, priority) in priority_mapping.items():
            if condition in conditions and conditions[condition]:
                plots = conditions[condition]
                
                # Batch similar adjacent plots together
                if self.batch_similar_tasks:
                    plot_batches = self._batch_adjacent_plots(plots)
                else:
                    plot_batches = [plots]
                
                # Create work orders for each batch
                for batch in plot_batches:
                    if len(batch) >= self.min_plots_for_order:
                        order_id = self._create_condition_work_order(
                            task_type, batch, priority, condition
                        )
                        if order_id:
                            created_orders.append(order_id)
        
        return created_orders
    
    def _batch_adjacent_plots(self, plots: List[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
        """Group adjacent plots into batches for efficient work orders"""
        if not plots:
            return []
        
        batches = []
        remaining_plots = set(plots)
        
        while remaining_plots:
            # Start new batch with an arbitrary remaining plot
            current_batch = []
            to_process = [remaining_plots.pop()]
            
            # Expand batch by finding adjacent plots
            while to_process:
                current_plot = to_process.pop(0)
                current_batch.append(current_plot)
                
                # Check adjacent plots
                x, y = current_plot
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    adj_plot = (x + dx, y + dy)
                    if adj_plot in remaining_plots:
                        remaining_plots.remove(adj_plot)
                        to_process.append(adj_plot)
            
            batches.append(current_batch)
        
        return batches
    
    def _create_condition_work_order(self, 
                                   task_type: TaskType, 
                                   plots: List[Tuple[int, int]], 
                                   priority: TaskPriority,
                                   condition: str) -> Optional[str]:
        """Create a work order for a specific farm condition"""
        
        # Calculate deadline based on task urgency
        deadline_hours = self._calculate_deadline(task_type, condition, len(plots))
        
        # Determine required employee role
        required_role = self._get_preferred_role(task_type)
        
        # Generate descriptive notes
        notes = self._generate_work_order_notes(task_type, condition, len(plots))
        
        # Create the work order
        work_order = self.work_order_manager.create_work_order(
            task_type=task_type,
            plots=plots,
            priority=priority,
            deadline_hours=deadline_hours,
            required_role=required_role,
            notes=notes,
            auto_assign=True
        )
        
        if work_order:
            print(f"Generated work order: {task_type.value} for {len(plots)} plots ({condition})")
            return work_order.id
        
        return None
    
    def _calculate_deadline(self, task_type: TaskType, condition: str, plot_count: int) -> Optional[float]:
        """Calculate appropriate deadline for work order"""
        
        # Deadline mappings (hours)
        deadline_map = {
            TaskType.HARVESTING: 48,  # 2 days (crops can overripen)
            TaskType.PEST_CONTROL: 24,  # 1 day (pest damage spreads)
            TaskType.WATERING: 12,  # 12 hours (plants need water)
            TaskType.FERTILIZING: 72,  # 3 days (nutrient deficiency develops slowly)
            TaskType.PLANTING: 96,  # 4 days (planting season window)
            TaskType.TILLING: 120,  # 5 days (preparation task)
            TaskType.PROCESSING: 48,  # 2 days (harvested crops should be processed)
            TaskType.STORING: 24   # 1 day (processed goods need storage)
        }
        
        base_deadline = deadline_map.get(task_type, 72)
        
        # Adjust deadline based on plot count (more plots = more time)
        if plot_count > 10:
            base_deadline *= 1.5
        elif plot_count > 5:
            base_deadline *= 1.2
        
        return base_deadline
    
    def _get_preferred_role(self, task_type: TaskType) -> Optional[EmployeeRole]:
        """Get preferred employee role for task type"""
        role_mapping = {
            TaskType.TILLING: EmployeeRole.FIELD_OPERATOR,
            TaskType.PLANTING: EmployeeRole.FIELD_OPERATOR,
            TaskType.CULTIVATING: EmployeeRole.FIELD_OPERATOR,
            TaskType.HARVESTING: EmployeeRole.HARVEST_SPECIALIST,
            TaskType.PROCESSING: EmployeeRole.HARVEST_SPECIALIST,
            TaskType.STORING: EmployeeRole.HARVEST_SPECIALIST,
            TaskType.FERTILIZING: EmployeeRole.CROP_MANAGER,
            TaskType.PEST_CONTROL: EmployeeRole.CROP_MANAGER,
            TaskType.WATERING: EmployeeRole.MAINTENANCE_TECH
        }
        
        return role_mapping.get(task_type)
    
    def _generate_work_order_notes(self, task_type: TaskType, condition: str, plot_count: int) -> str:
        """Generate descriptive notes for work order"""
        
        notes_templates = {
            'ready_for_harvest': f"Harvest {plot_count} plots - crops at optimal ripeness",
            'pest_control_needed': f"Pest control required for {plot_count} plots - prevent crop damage",
            'needs_watering': f"Irrigation needed for {plot_count} plots - soil moisture low",
            'needs_fertilizing': f"Fertilize {plot_count} plots - soil nutrients depleted",
            'ready_for_planting': f"Plant seeds in {plot_count} prepared plots - optimal timing",
            'needs_tilling': f"Prepare {plot_count} plots for planting - soil conditioning",
            'processing_ready': f"Process harvested crops from {plot_count} plots",
            'storage_needed': f"Store processed goods from {plot_count} plots"
        }
        
        base_note = notes_templates.get(condition, f"{task_type.value} work for {plot_count} plots")
        
        # Add auto-generation note
        return f"{base_note} (Auto-generated)"
    
    def scan_and_generate(self, grid_manager) -> int:
        """
        Perform full farm scan and generate needed work orders
        
        Returns:
            Number of work orders created
        """
        if not ENABLE_WORK_ORDERS or not ENABLE_DYNAMIC_TASK_GENERATION:
            return 0
        
        # Analyze farm conditions
        conditions = self.analyze_farm_conditions(grid_manager)
        
        if not conditions:
            return 0
        
        # Generate work orders
        created_orders = self.generate_work_orders_from_analysis(conditions)
        
        if created_orders:
            print(f"Dynamic generation created {len(created_orders)} work orders:")
            for condition, plots in conditions.items():
                if plots:
                    print(f"  {condition}: {len(plots)} plots")
        
        return len(created_orders)
    
    # Event handlers
    def _handle_time_update(self, event_data):
        """Handle time updates for periodic scanning"""
        current_time = event_data.get('total_time', 0.0)
        
        if current_time - self.last_scan_time >= self.scan_interval:
            self.last_scan_time = current_time
            
            # Request grid manager for analysis
            self.event_system.emit('request_grid_for_analysis', {
                'callback': self.scan_and_generate
            })
    
    def _handle_day_passed(self, event_data):
        """Handle day passed for major condition changes"""
        # Force a full scan when day passes (major condition changes likely)
        self.event_system.emit('request_grid_for_analysis', {
            'callback': self.scan_and_generate
        })
    
    def _handle_crop_growth(self, event_data):
        """Handle crop growth stage changes"""
        # Crops changing growth stage might need new work orders
        plot_coords = event_data.get('plot_coords')
        new_stage = event_data.get('new_stage')
        
        if new_stage == 4:  # Harvestable
            # Create urgent harvest work order for single plot if not batched
            self._create_urgent_harvest_order(plot_coords)
    
    def _handle_crop_ready(self, event_data):
        """Handle crops becoming ready for harvest"""
        plot_coords = event_data.get('plot_coords')
        if plot_coords:
            self._create_urgent_harvest_order(plot_coords)
    
    def _create_urgent_harvest_order(self, plot_coords: Tuple[int, int]):
        """Create urgent harvest work order for specific plot"""
        # Check if plot is already assigned
        if plot_coords in self.work_order_manager.plot_assignments:
            return
        
        # Create urgent harvest order
        work_order = self.work_order_manager.create_work_order(
            task_type=TaskType.HARVESTING,
            plots=[plot_coords],
            priority=TaskPriority.HIGH,
            deadline_hours=24,  # 1 day deadline
            notes="Urgent harvest - crop at peak ripeness (Auto-generated)",
            auto_assign=True
        )
        
        if work_order:
            print(f"Created urgent harvest order for plot {plot_coords}")
    
    def _handle_soil_depletion(self, event_data):
        """Handle soil nutrient depletion"""
        # Create fertilizing work orders for depleted soil
        pass
    
    def _handle_weather_forecast(self, event_data):
        """Handle weather forecast for planning"""
        # Adjust work order priorities based on weather
        pass
    
    def _handle_season_change(self, event_data):
        """Handle season changes"""
        # Generate seasonal work orders (spring planting, fall harvest, etc.)
        pass
    
    def _handle_pest_risk(self, event_data):
        """Handle pest risk detection"""
        # Create immediate pest control work orders
        pass
    
    def _handle_plots_selected(self, event_data):
        """Handle player selecting plots - suggest work orders"""
        selected_plots = event_data.get('plots', [])
        if len(selected_plots) >= self.min_plots_for_order:
            # Analyze selected plots and suggest appropriate work orders
            self._suggest_work_orders_for_plots(selected_plots)
    
    def _suggest_work_orders_for_plots(self, plots: List[Tuple[int, int]]):
        """Suggest appropriate work orders for selected plots"""
        # This will be implemented to suggest work orders when player selects plots
        pass
    
    def _handle_field_designated(self, event_data):
        """Handle player designating field areas"""
        # Create work orders for newly designated fields
        pass
    
    def cleanup(self):
        """Clean up dynamic work order generator"""
        if self.event_system:
            # Unsubscribe from events
            self.event_system.unsubscribe('time_updated', self._handle_time_update)
            # ... other unsubscribes
        
        print("Dynamic Work Order Generator cleaned up")