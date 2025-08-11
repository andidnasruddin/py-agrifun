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
    level: int = 1
    purchase_day: int = 1


class BuildingManager:
    """Manages farm buildings and upgrades"""
    
    def __init__(self, event_system, economy_manager, inventory_manager):
        """Initialize building manager"""
        self.event_system = event_system
        self.economy_manager = economy_manager
        self.inventory_manager = inventory_manager
        
        # Building definitions
        self.building_types = {
            'storage_silo': BuildingType(
                id='storage_silo',
                name='Storage Silo',
                description='Increases crop storage capacity',
                base_cost=500,  # $500 for first silo
                benefit_description='+50 storage capacity',
                max_quantity=5  # Can build up to 5 silos
            )
        }
        
        # Owned buildings
        self.owned_buildings: List[Building] = []
        
        # Register for events
        self.event_system.subscribe('purchase_building_requested', self._handle_purchase_request)
        
        print("Building Manager initialized - Storage Silo available for $500")
    
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
    
    def purchase_building(self, building_id: str) -> bool:
        """Purchase a building if possible"""
        if not self.can_purchase_building(building_id):
            return False
        
        building_type = self.building_types[building_id]
        current_count = sum(1 for b in self.owned_buildings 
                          if b.building_type.id == building_id)
        cost = self._calculate_building_cost(building_id, current_count)
        
        # Try to spend money
        if self.economy_manager.spend_money(cost, f"Purchase {building_type.name}", "building"):
            # Create building
            building = Building(
                building_type=building_type,
                level=1,
                purchase_day=1  # TODO: Get actual day from time manager
            )
            self.owned_buildings.append(building)
            
            # Apply building benefits
            self._apply_building_benefits(building)
            
            # Emit purchase event
            self.event_system.emit('building_purchased', {
                'building_id': building_id,
                'building_name': building_type.name,
                'cost': cost,
                'total_owned': current_count + 1,
                'remaining_balance': self.economy_manager.get_current_balance()
            })
            
            print(f"Purchased {building_type.name} for ${cost}")
            return True
        
        return False
    
    def _apply_building_benefits(self, building: Building):
        """Apply the benefits of a building"""
        if building.building_type.id == 'storage_silo':
            # Increase storage capacity by 50
            self.inventory_manager.upgrade_storage(50)
            print(f"Storage capacity increased by 50 units")
    
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
    
    def _handle_purchase_request(self, event_data):
        """Handle building purchase requests from UI"""
        building_id = event_data.get('building_id')
        
        if building_id:
            success = self.purchase_building(building_id)
            
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
    
    def update(self, dt: float):
        """Update building systems (future: maintenance, etc.)"""
        # Future implementation: building maintenance, decay, etc.
        pass