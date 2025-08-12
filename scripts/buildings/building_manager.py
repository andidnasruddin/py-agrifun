"""
Building Manager - Handles purchasable buildings and upgrades

This system manages farm buildings that provide strategic benefits.
Currently supports storage silos for increased crop storage capacity.

Key Features:
- Purchase buildings with money
- Buildings provide ongoing benefits
- Strategic choice between money and capacity
- Integration with existing systems

Design Goals:
- Simple but meaningful building choices
- Clear cost/benefit tradeoffs
- Extensible for future building types
- Integration with economy system

Usage:
    building_manager = BuildingManager(event_system, economy_manager, inventory_manager)
    building_manager.purchase_building('storage_silo')
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from scripts.core.config import *


@dataclass
class BuildingType:
    """Definition of a building type"""
    id: str
    name: str
    description: str
    base_cost: int
    benefit_description: str
    max_quantity: int = 10  # Maximum number that can be built


@dataclass
class Building:
    """Individual building instance"""
    building_type: BuildingType
    x: int = 0  # Grid X coordinate
    y: int = 0  # Grid Y coordinate
    level: int = 1
    purchase_day: int = 1


class BuildingManager:
    """Manages farm buildings and upgrades"""
    
    def __init__(self, event_system, economy_manager, inventory_manager, grid_manager=None):
        """Initialize building manager"""
        self.event_system = event_system
        self.economy_manager = economy_manager
        self.inventory_manager = inventory_manager
        self.grid_manager = grid_manager
        
        # Building definitions
        self.building_types = {
            'storage_silo': BuildingType(
                id='storage_silo',
                name='Storage Silo',
                description='Increases crop storage capacity',
                base_cost=500,  # $500 for first silo
                benefit_description='+50 storage capacity',
                max_quantity=5  # Can build up to 5 silos
            ),
            'water_cooler': BuildingType(
                id='water_cooler',
                name='Water Cooler',
                description='Employees can restore thirst here',
                base_cost=200,  # $200 for water cooler
                benefit_description='Employees can restore thirst',
                max_quantity=10  # Can build multiple water coolers
            ),
            'tool_shed': BuildingType(
                id='tool_shed',
                name='Tool Shed',
                description='Boosts work efficiency in surrounding area',
                base_cost=300,  # $300 for tool shed
                benefit_description='+15% work efficiency nearby',
                max_quantity=8  # Can build multiple tool sheds
            ),
            'employee_housing': BuildingType(
                id='employee_housing',
                name='Employee Housing',
                description='Employees can rest and restore energy',
                base_cost=800,  # $800 for housing
                benefit_description='Employees can rest here',
                max_quantity=5  # Can build multiple housing units
            )
        }
        
        # Owned buildings
        self.owned_buildings: List[Building] = []
        
        # Register for events
        self.event_system.subscribe('purchase_building_requested', self._handle_purchase_request)
        
        print("Building Manager initialized - 4 building types available:")
        print("  Storage Silo ($500), Water Cooler ($200), Tool Shed ($300), Employee Housing ($800)")
    
    def can_purchase_building(self, building_id: str) -> bool:
        """Check if a building can be purchased"""
        if building_id not in self.building_types:
            return False
        
        building_type = self.building_types[building_id]
        
        # Check quantity limit
        current_count = sum(1 for b in self.owned_buildings 
                          if b.building_type.id == building_id)
        if current_count >= building_type.max_quantity:
            return False
        
        # Check cost
        cost = self._calculate_building_cost(building_id, current_count)
        return self.economy_manager.get_current_balance() >= cost
    
    def _calculate_building_cost(self, building_id: str, current_count: int) -> int:
        """Calculate cost for building based on current count"""
        building_type = self.building_types[building_id]
        
        # Progressive cost increase: base_cost * (1.3 ^ current_count) - reduced from 1.5 for better balance
        multiplier = 1.3 ** current_count  # Reduced multiplier makes expansion more viable
        return int(building_type.base_cost * multiplier)
    
    def purchase_building_at(self, building_id: str, x: int, y: int) -> bool:
        """Purchase a building at specific grid coordinates"""
        if not self.can_purchase_building(building_id):
            return False
        
        # Check if grid manager is available and location is valid
        if not self.grid_manager:
            print("Error: Grid manager not available for building placement")
            return False
        
        tile = self.grid_manager.get_tile(x, y)
        if not tile or not tile.can_place_building():
            print(f"Cannot place building at ({x}, {y}) - tile not available")
            return False
        
        building_type = self.building_types[building_id]
        current_count = sum(1 for b in self.owned_buildings 
                          if b.building_type.id == building_id)
        cost = self._calculate_building_cost(building_id, current_count)
        
        # Try to spend money
        if self.economy_manager.spend_money(cost, f"Purchase {building_type.name}", "building"):
            # Create building with grid coordinates
            building = Building(
                building_type=building_type,
                x=x,
                y=y,
                level=1,
                purchase_day=1  # TODO: Get actual day from time manager
            )
            self.owned_buildings.append(building)
            
            # Place building on grid
            if self.grid_manager.place_building_at(x, y, building_id, building):
                # Apply building benefits
                self._apply_building_benefits(building)
                
                # Emit purchase event
                self.event_system.emit('building_purchased', {
                    'building_id': building_id,
                    'building_name': building_type.name,
                    'cost': cost,
                    'x': x,
                    'y': y,
                    'total_owned': current_count + 1,
                    'remaining_balance': self.economy_manager.get_current_balance()
                })
                
                print(f"Purchased {building_type.name} for ${cost} at ({x}, {y})")
                return True
            else:
                # Failed to place on grid, refund money
                self.owned_buildings.remove(building)
                self.economy_manager.add_money(cost, f"Refund {building_type.name}", "refund")
                print(f"Failed to place {building_type.name} on grid, refunded ${cost}")
                return False
        
        return False
    
    def purchase_building(self, building_id: str) -> bool:
        """Legacy method - purchase building without specific location (deprecated)"""
        print("Warning: purchase_building() without location is deprecated. Use purchase_building_at()")
        return False
    
    def _apply_building_benefits(self, building: Building):
        """Apply the benefits of a building"""
        # Apply immediate benefits (like storage capacity increases)
        if building.building_type.id == 'storage_silo':
            # Increase storage capacity by 50 units
            self.inventory_manager.upgrade_storage(50)
            print(f"Storage capacity increased by 50 units")
        
        # Spatial benefits are handled dynamically in get_spatial_benefits_at()
        # This ensures real-time calculation of effects based on building proximity
    
    def get_building_info(self, building_id: str) -> Dict:
        """Get information about a building type"""
        if building_id not in self.building_types:
            return {}
        
        building_type = self.building_types[building_id]
        current_count = sum(1 for b in self.owned_buildings 
                          if b.building_type.id == building_id)
        
        return {
            'id': building_id,
            'name': building_type.name,
            'description': building_type.description,
            'benefit_description': building_type.benefit_description,
            'current_count': current_count,
            'max_count': building_type.max_quantity,
            'can_purchase': self.can_purchase_building(building_id),
            'next_cost': self._calculate_building_cost(building_id, current_count) if current_count < building_type.max_quantity else 0,
            'total_spent': sum(self._calculate_building_cost(building_id, i) 
                             for i in range(current_count))
        }
    
    def get_all_buildings_info(self) -> Dict:
        """Get information about all available buildings"""
        return {building_id: self.get_building_info(building_id) 
                for building_id in self.building_types.keys()}
    
    def get_owned_buildings_summary(self) -> Dict:
        """Get summary of owned buildings"""
        summary = {}
        for building in self.owned_buildings:
            building_id = building.building_type.id
            if building_id not in summary:
                summary[building_id] = {
                    'name': building.building_type.name,
                    'count': 0,
                    'total_benefit': ''
                }
            summary[building_id]['count'] += 1
        
        # Add benefit descriptions
        if 'storage_silo' in summary:
            silo_count = summary['storage_silo']['count']
            summary['storage_silo']['total_benefit'] = f'+{silo_count * 50} storage capacity'
        
        return summary
    
    def _find_suitable_location(self) -> tuple:
        """Find a suitable location for placing a building"""
        if not self.grid_manager:
            return (0, 0)  # Default location if no grid manager
        
        # Try to find an empty tile, starting from corners and working inward
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = self.grid_manager.get_tile(x, y)
                if tile and tile.can_place_building():
                    return (x, y)
        
        # If no suitable location found, return default
        return (0, 0)
    
    def _handle_purchase_request(self, event_data):
        """Handle building purchase requests from UI"""
        building_id = event_data.get('building_id')
        
        if building_id:
            # Try to find a suitable location for the building
            x = event_data.get('x', self._find_suitable_location()[0])
            y = event_data.get('y', self._find_suitable_location()[1])
            success = self.purchase_building_at(building_id, x, y)
            
            if success:
                self.event_system.emit('purchase_successful', {
                    'building_id': building_id,
                    'building_name': self.building_types[building_id].name
                })
            else:
                reason = 'insufficient_funds'
                if not self.can_purchase_building(building_id):
                    current_count = sum(1 for b in self.owned_buildings 
                                      if b.building_type.id == building_id)
                    if current_count >= self.building_types[building_id].max_quantity:
                        reason = 'max_quantity_reached'
                
                self.event_system.emit('purchase_failed', {
                    'building_id': building_id,
                    'reason': reason
                })
    
    def get_spatial_benefits_at(self, x: int, y: int) -> Dict:
        """Get all spatial benefits that apply at a specific grid coordinate"""
        # Dictionary to store cumulative effects at this location
        benefits = {
            'crop_yield_multiplier': 1.0,  # Multiplicative bonus to crop yield (1.0 = no bonus)
            'work_efficiency_multiplier': 1.0,  # Multiplicative bonus to work speed
            'rest_decay_multiplier': 1.0,  # Multiplicative modifier to rest decay rate
            'trait_effectiveness_multiplier': 1.0,  # Bonus to employee trait effects
            'has_water_cooler': False,  # Can employees restore thirst here?
            'has_housing': False  # Can employees rest here?
        }
        
        # Check each owned building for spatial effects
        for building in self.owned_buildings:
            # Calculate distance from building to target coordinate
            distance = abs(building.x - x) + abs(building.y - y)  # Manhattan distance
            
            # Apply building-specific spatial benefits based on proximity
            if building.building_type.id == 'storage_silo':
                # Storage silos provide +10% crop yield within 4 tiles radius
                if distance <= 4:
                    benefits['crop_yield_multiplier'] *= 1.10  # +10% yield bonus
            
            elif building.building_type.id == 'tool_shed':
                # Tool sheds provide +15% work efficiency within 3 tiles radius
                if distance <= 3:
                    benefits['work_efficiency_multiplier'] *= 1.15  # +15% efficiency bonus
            
            elif building.building_type.id == 'water_cooler':
                # Water coolers reduce rest decay by 20% within 2 tiles radius
                # Also allow employees to restore thirst at this exact location
                if distance <= 2:
                    benefits['rest_decay_multiplier'] *= 0.80  # -20% rest decay (80% of normal)
                if distance == 0:  # Exact location only
                    benefits['has_water_cooler'] = True  # Can restore thirst here
            
            elif building.building_type.id == 'employee_housing':
                # Employee housing provides +25% trait effectiveness within 2 tiles radius
                # Also allows employees to rest at this exact location  
                if distance <= 2:
                    benefits['trait_effectiveness_multiplier'] *= 1.25  # +25% trait effectiveness
                if distance == 0:  # Exact location only
                    benefits['has_housing'] = True  # Can rest here
        
        return benefits
    
    def get_buildings_in_radius(self, center_x: int, center_y: int, radius: int) -> List[Building]:
        """Get all buildings within a specific radius of a coordinate"""
        # List to store buildings within the specified radius
        nearby_buildings = []
        
        # Check each owned building's distance from the center point
        for building in self.owned_buildings:
            # Calculate Manhattan distance (sum of horizontal and vertical distance)
            distance = abs(building.x - center_x) + abs(building.y - center_y)
            
            # Add building to list if within radius
            if distance <= radius:
                nearby_buildings.append(building)
        
        return nearby_buildings
    
    def calculate_crop_yield_at(self, x: int, y: int, base_yield: int) -> int:
        """Calculate final crop yield at a location including building bonuses"""
        # Get spatial benefits for this location
        benefits = self.get_spatial_benefits_at(x, y)
        
        # Apply yield multiplier to base yield
        final_yield = int(base_yield * benefits['crop_yield_multiplier'])
        
        return final_yield
    
    def calculate_work_efficiency_at(self, x: int, y: int, base_efficiency: float) -> float:
        """Calculate work efficiency at a location including building bonuses"""
        # Get spatial benefits for this location
        benefits = self.get_spatial_benefits_at(x, y)
        
        # Apply efficiency multiplier to base efficiency
        final_efficiency = base_efficiency * benefits['work_efficiency_multiplier']
        
        return final_efficiency
    
    def can_restore_thirst_at(self, x: int, y: int) -> bool:
        """Check if employees can restore thirst at this location"""
        # Get spatial benefits to check for water cooler availability
        benefits = self.get_spatial_benefits_at(x, y)
        return benefits['has_water_cooler']
    
    def can_rest_at(self, x: int, y: int) -> bool:
        """Check if employees can rest at this location"""
        # Get spatial benefits to check for housing availability
        benefits = self.get_spatial_benefits_at(x, y)
        return benefits['has_housing']
    
    def get_spatial_effects_summary(self, x: int, y: int) -> str:
        """Get a human-readable summary of all spatial effects at a location"""
        # Get all benefits for this location
        benefits = self.get_spatial_benefits_at(x, y)
        effects = []  # List to store effect descriptions
        
        # Add descriptions for active bonuses
        if benefits['crop_yield_multiplier'] > 1.0:
            bonus_percent = int((benefits['crop_yield_multiplier'] - 1.0) * 100)
            effects.append(f"+{bonus_percent}% crop yield")
        
        if benefits['work_efficiency_multiplier'] > 1.0:
            bonus_percent = int((benefits['work_efficiency_multiplier'] - 1.0) * 100)
            effects.append(f"+{bonus_percent}% work efficiency")
        
        if benefits['rest_decay_multiplier'] < 1.0:
            reduction_percent = int((1.0 - benefits['rest_decay_multiplier']) * 100)
            effects.append(f"-{reduction_percent}% rest decay")
        
        if benefits['trait_effectiveness_multiplier'] > 1.0:
            bonus_percent = int((benefits['trait_effectiveness_multiplier'] - 1.0) * 100)
            effects.append(f"+{bonus_percent}% trait effectiveness")
        
        if benefits['has_water_cooler']:
            effects.append("Thirst restoration available")
        
        if benefits['has_housing']:
            effects.append("Employee rest area")
        
        # Return comma-separated list or default message
        return ", ".join(effects) if effects else "No building effects"
    
    def update(self, dt: float):
        """Update building systems (future: maintenance, etc.)"""
        # Future implementation: building maintenance, decay, etc.
        pass