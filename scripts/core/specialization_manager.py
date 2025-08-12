"""
Farm Specialization Manager - Handles farm specialization tracks and progression
Manages specialization unlocks, bonuses, and stat tracking for the farming simulation.
"""

from typing import Dict, Any, List, Optional
from scripts.core.config import FARM_SPECIALIZATIONS, SPECIALIZATION_PROGRESSION


class SpecializationManager:
    """Manages farm specialization tracks, unlocks, and bonuses"""
    
    def __init__(self, event_system):
        """Initialize the specialization manager with event system connection"""
        self.event_system = event_system  # Connect to the game's event system
        
        # Current farm specialization state
        self.current_specialization = 'none'  # Start as unspecialized farm
        self.specialization_unlocked_date = None  # Track when specialization was chosen
        
        # Stat tracking for specialization requirements
        self.farm_stats = {
            'wheat_harvested': 0,       # Total wheat units harvested
            'tomatoes_harvested': 0,    # Total tomato units harvested
            'corn_harvested': 0,        # Total corn units harvested
            'rotation_cycles_completed': 0,  # Number of complete rotation cycles
            'total_crops_sold': 0,      # Total crop units sold
            'storage_capacity_purchased': 100,  # Current storage capacity
            'soil_health_average': 100, # Average soil health across all tiles
            'average_crop_quality': 1.0 # Average quality multiplier of harvested crops
        }
        
        # Specialization availability tracking
        self.available_specializations = ['none']  # Specializations player can choose
        self.notified_specializations = set()     # Don't spam notifications
        
        # Bonus calculation cache for performance
        self.active_bonuses = {}  # Cache of current specialization bonuses
        self._update_active_bonuses()  # Initialize bonus cache
        
        # Subscribe to relevant game events for stat tracking
        self._setup_event_subscriptions()
        
        # Subscribe to UI events for specialization selection
        self.event_system.subscribe('choose_specialization_requested', self._handle_specialization_choice)
        self.event_system.subscribe('get_specialization_info_for_ui', self._handle_specialization_info_request)
        
        print("Specialization Manager initialized - tracking farm progression")
    
    def _setup_event_subscriptions(self):
        """Subscribe to game events for automatic stat tracking"""
        # Track crop harvests for specialization requirements
        self.event_system.subscribe('crop_harvested', self._on_crop_harvested)
        
        # Track crop sales for market specialization
        self.event_system.subscribe('crops_sold', self._on_crops_sold)
        
        # Track building purchases for grain specialization
        self.event_system.subscribe('building_purchased', self._on_building_purchased)
        
        # Track soil health changes for diversified specialization
        self.event_system.subscribe('soil_health_updated', self._on_soil_health_updated)
        
        # Track rotation cycle completion for diversified specialization
        self.event_system.subscribe('rotation_cycle_completed', self._on_rotation_cycle_completed)
        
        print("Event subscriptions established for specialization tracking")
    
    def _on_crop_harvested(self, event_data: Dict[str, Any]):
        """Handle crop harvest events for stat tracking"""
        crop_type = event_data.get('crop_type', '')
        quantity = event_data.get('quantity', 0)
        quality_multiplier = event_data.get('quality_multiplier', 1.0)
        
        # Update crop-specific harvest stats
        if crop_type == 'wheat':
            self.farm_stats['wheat_harvested'] += quantity
        elif crop_type == 'tomatoes':
            self.farm_stats['tomatoes_harvested'] += quantity
        elif crop_type == 'corn':
            self.farm_stats['corn_harvested'] += quantity
        
        # Update average crop quality
        total_quality = self.farm_stats['average_crop_quality'] * self.farm_stats['total_crops_sold']
        total_quality += quality_multiplier * quantity
        self.farm_stats['total_crops_sold'] += quantity
        
        if self.farm_stats['total_crops_sold'] > 0:
            self.farm_stats['average_crop_quality'] = total_quality / self.farm_stats['total_crops_sold']
        
        # Check for newly available specializations
        self._check_specialization_unlocks()
        
        print(f"Tracked harvest: {quantity} {crop_type} (quality: {quality_multiplier:.2f})")
    
    def _on_crops_sold(self, event_data: Dict[str, Any]):
        """Handle crop sale events (already tracked in harvest)"""
        # Sales are already counted in harvest tracking
        # This could track additional sale-specific metrics if needed
        pass
    
    def _on_building_purchased(self, event_data: Dict[str, Any]):
        """Handle building purchase events for storage capacity tracking"""
        building_type = event_data.get('building_type', '')
        
        # Update storage capacity for grain specialization requirements
        if building_type == 'storage_silo':
            self.farm_stats['storage_capacity_purchased'] += 50  # Each silo adds 50 capacity
            self._check_specialization_unlocks()
            print(f"Storage capacity updated: {self.farm_stats['storage_capacity_purchased']}")
    
    def _on_soil_health_updated(self, event_data: Dict[str, Any]):
        """Handle soil health updates for diversified specialization"""
        average_health = event_data.get('average_soil_health', 100)
        self.farm_stats['soil_health_average'] = average_health
        self._check_specialization_unlocks()
    
    def _on_rotation_cycle_completed(self, event_data: Dict[str, Any]):
        """Handle rotation cycle completion for diversified specialization"""
        self.farm_stats['rotation_cycles_completed'] += 1
        self._check_specialization_unlocks()
        print(f"Rotation cycles completed: {self.farm_stats['rotation_cycles_completed']}")
    
    def _handle_specialization_choice(self, event_data: Dict[str, Any]):
        """Handle specialization selection from UI"""
        specialization_id = event_data.get('specialization_id', '')
        
        # We need to get current cash from the economy manager
        # For now, emit an event to request the specialization change
        self.event_system.emit('process_specialization_choice', {
            'specialization_id': specialization_id,
            'manager': self  # Pass reference to this manager
        })
    
    def _handle_specialization_info_request(self, event_data: Dict[str, Any]):
        """Handle request for current specialization info from UI"""
        current_info = self.get_current_specialization_info()
        available_specs = self.get_available_specializations()
        
        self.event_system.emit('specialization_info_response', {
            'current_specialization': current_info,
            'available_specializations': available_specs,
            'farm_stats': self.get_farm_stats()
        })
    
    def _check_specialization_unlocks(self):
        """Check if any new specializations have been unlocked"""
        for spec_id, thresholds in SPECIALIZATION_PROGRESSION['notification_thresholds'].items():
            if spec_id.replace('_available', '') in self.available_specializations:
                continue  # Already unlocked
            
            if spec_id in self.notified_specializations:
                continue  # Already notified about this
            
            # Check if all requirements are met
            requirements_met = True
            for stat_name, required_value in thresholds.items():
                current_value = self.farm_stats.get(stat_name, 0)
                if current_value < required_value:
                    requirements_met = False
                    break
            
            if requirements_met:
                # Unlock the specialization
                spec_type = spec_id.replace('_available', '')
                self.available_specializations.append(spec_type)
                self.notified_specializations.add(spec_id)
                
                # Notify the player
                spec_info = FARM_SPECIALIZATIONS[spec_type]
                self.event_system.emit('specialization_unlocked', {
                    'specialization_id': spec_type,
                    'specialization_name': spec_info['name'],
                    'cost': spec_info['cost']
                })
                
                print(f"Specialization unlocked: {spec_info['name']}")
    
    def can_specialize(self, specialization_id: str) -> bool:
        """Check if the player can choose a specific specialization"""
        if specialization_id not in FARM_SPECIALIZATIONS:
            return False
        
        if specialization_id not in self.available_specializations:
            return False
        
        # Check requirements
        spec_data = FARM_SPECIALIZATIONS[specialization_id]
        requirements = spec_data.get('requirements', {})
        
        for stat_name, required_value in requirements.items():
            current_value = self.farm_stats.get(stat_name, 0)
            if current_value < required_value:
                return False
        
        return True
    
    def choose_specialization(self, specialization_id: str, current_cash: int) -> Dict[str, Any]:
        """Attempt to choose a farm specialization"""
        if not self.can_specialize(specialization_id):
            return {'success': False, 'reason': 'Requirements not met'}
        
        spec_data = FARM_SPECIALIZATIONS[specialization_id]
        cost = spec_data['cost']
        
        if current_cash < cost:
            return {'success': False, 'reason': 'Insufficient funds', 'cost': cost}
        
        # Apply the specialization
        old_specialization = self.current_specialization
        self.current_specialization = specialization_id
        self._update_active_bonuses()
        
        # Emit specialization change event
        self.event_system.emit('specialization_changed', {
            'old_specialization': old_specialization,
            'new_specialization': specialization_id,
            'cost': cost,
            'bonuses': self.active_bonuses
        })
        
        print(f"Farm specialized: {spec_data['name']} (Cost: ${cost})")
        
        return {'success': True, 'cost': cost, 'specialization': spec_data}
    
    def _update_active_bonuses(self):
        """Update the cache of active specialization bonuses"""
        if self.current_specialization in FARM_SPECIALIZATIONS:
            self.active_bonuses = FARM_SPECIALIZATIONS[self.current_specialization]['bonuses'].copy()
        else:
            self.active_bonuses = {}
    
    def get_bonus_multiplier(self, bonus_type: str, base_value: float = 1.0) -> float:
        """Get the current bonus multiplier for a specific bonus type"""
        return self.active_bonuses.get(bonus_type, base_value)
    
    def has_bonus(self, bonus_type: str) -> bool:
        """Check if the current specialization provides a specific bonus"""
        return bonus_type in self.active_bonuses
    
    def get_current_specialization_info(self) -> Dict[str, Any]:
        """Get information about the current specialization"""
        if self.current_specialization in FARM_SPECIALIZATIONS:
            return FARM_SPECIALIZATIONS[self.current_specialization].copy()
        return FARM_SPECIALIZATIONS['none'].copy()
    
    def get_available_specializations(self) -> List[Dict[str, Any]]:
        """Get list of available specializations with their information"""
        available = []
        for spec_id in self.available_specializations:
            if spec_id in FARM_SPECIALIZATIONS:
                spec_info = FARM_SPECIALIZATIONS[spec_id].copy()
                spec_info['id'] = spec_id
                spec_info['can_choose'] = self.can_specialize(spec_id)
                available.append(spec_info)
        return available
    
    def get_farm_stats(self) -> Dict[str, Any]:
        """Get current farm statistics"""
        return self.farm_stats.copy()
    
    def get_save_data(self) -> Dict[str, Any]:
        """Get specialization data for save file"""
        return {
            'current_specialization': self.current_specialization,
            'specialization_unlocked_date': self.specialization_unlocked_date,
            'farm_stats': self.farm_stats.copy(),
            'available_specializations': self.available_specializations.copy(),
            'notified_specializations': list(self.notified_specializations)
        }
    
    def load_save_data(self, save_data: Dict[str, Any]):
        """Load specialization data from save file"""
        self.current_specialization = save_data.get('current_specialization', 'none')
        self.specialization_unlocked_date = save_data.get('specialization_unlocked_date')
        self.farm_stats.update(save_data.get('farm_stats', {}))
        self.available_specializations = save_data.get('available_specializations', ['none'])
        self.notified_specializations = set(save_data.get('notified_specializations', []))
        
        # Update active bonuses after loading
        self._update_active_bonuses()
        
        print(f"Specialization data loaded: {self.get_current_specialization_info()['name']}")