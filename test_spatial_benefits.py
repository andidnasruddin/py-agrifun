#!/usr/bin/env python3
"""
Test script to validate spatial building benefits system
"""

import sys
import os

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.event_system import EventSystem
from scripts.core.grid_manager import GridManager
from scripts.core.inventory_manager import InventoryManager
from scripts.economy.economy_manager import EconomyManager
from scripts.buildings.building_manager import BuildingManager

def test_spatial_benefits():
    """Test spatial building benefits system functionality"""
    print("=== Testing Spatial Building Benefits System ===\n")
    
    # Initialize required systems
    event_system = EventSystem()
    grid_manager = GridManager(event_system)
    inventory_manager = InventoryManager(event_system)
    economy_manager = EconomyManager(event_system)
    
    # Initialize building manager with all dependencies
    building_manager = BuildingManager(event_system, economy_manager, inventory_manager, grid_manager)
    
    # Connect grid manager to building manager (as done in game_manager)
    grid_manager.building_manager = building_manager
    
    # Add some money to test building purchases
    economy_manager.add_money(10000, "Test funding", "test")
    
    print("1. Testing Storage Silo Benefits:")
    print("   - Placing storage silo at (8, 8)")
    success = building_manager.purchase_building_at('storage_silo', 8, 8)
    if success:
        print("   [OK] Storage silo placed successfully")
        
        # Test crop yield bonus at various distances
        test_positions = [
            (8, 8),   # Same tile
            (8, 10),  # 2 tiles away
            (8, 12),  # 4 tiles away (edge of effect)
            (8, 14),  # 6 tiles away (outside effect)
        ]
        
        for x, y in test_positions:
            base_yield = 15  # Default corn yield
            final_yield = building_manager.calculate_crop_yield_at(x, y, base_yield)
            distance = abs(x - 8) + abs(y - 8)
            bonus = ((final_yield / base_yield) - 1.0) * 100 if final_yield > base_yield else 0
            print(f"   - Tile ({x}, {y}), distance {distance}: {base_yield} -> {final_yield} units (+{bonus:.0f}%)")
    else:
        print("   [FAIL] Failed to place storage silo")
    
    print("\n2. Testing Tool Shed Benefits:")
    print("   - Placing tool shed at (4, 4)")
    success = building_manager.purchase_building_at('tool_shed', 4, 4)
    if success:
        print("   [OK] Tool shed placed successfully")
        
        # Test work efficiency bonus at various distances
        test_positions = [
            (4, 4),   # Same tile
            (4, 6),   # 2 tiles away
            (4, 7),   # 3 tiles away (edge of effect)
            (4, 8),   # 4 tiles away (outside effect)
        ]
        
        for x, y in test_positions:
            base_efficiency = 1.0
            final_efficiency = building_manager.calculate_work_efficiency_at(x, y, base_efficiency)
            distance = abs(x - 4) + abs(y - 4)
            bonus = ((final_efficiency / base_efficiency) - 1.0) * 100 if final_efficiency > base_efficiency else 0
            print(f"   - Tile ({x}, {y}), distance {distance}: {base_efficiency:.2f} -> {final_efficiency:.2f} efficiency (+{bonus:.0f}%)")
    else:
        print("   [FAIL] Failed to place tool shed")
    
    print("\n3. Testing Water Cooler Benefits:")
    print("   - Placing water cooler at (12, 4)")
    success = building_manager.purchase_building_at('water_cooler', 12, 4)
    if success:
        print("   [OK] Water cooler placed successfully")
        
        # Test rest decay reduction at various distances
        test_positions = [
            (12, 4),  # Same tile
            (12, 5),  # 1 tile away
            (12, 6),  # 2 tiles away (edge of effect)
            (12, 7),  # 3 tiles away (outside effect)
        ]
        
        for x, y in test_positions:
            benefits = building_manager.get_spatial_benefits_at(x, y)
            distance = abs(x - 12) + abs(y - 4)
            reduction = (1.0 - benefits['rest_decay_multiplier']) * 100 if benefits['rest_decay_multiplier'] < 1.0 else 0
            can_restore = "Yes" if benefits['has_water_cooler'] else "No"
            print(f"   - Tile ({x}, {y}), distance {distance}: -{reduction:.0f}% rest decay, thirst restoration: {can_restore}")
    else:
        print("   [FAIL] Failed to place water cooler")
    
    print("\n4. Testing Employee Housing Benefits:")
    print("   - Placing employee housing at (2, 12)")
    success = building_manager.purchase_building_at('employee_housing', 2, 12)
    if success:
        print("   [OK] Employee housing placed successfully")
        
        # Test trait effectiveness bonus at various distances
        test_positions = [
            (2, 12),  # Same tile
            (2, 13),  # 1 tile away
            (2, 14),  # 2 tiles away (edge of effect)
            (2, 15),  # 3 tiles away (outside effect) - but this is off-grid, so use (0, 14)
            (0, 14),  # 3 tiles away (outside effect)
        ]
        
        for x, y in test_positions:
            if x >= 0 and y >= 0 and x < 16 and y < 16:  # Check grid bounds
                benefits = building_manager.get_spatial_benefits_at(x, y)
                distance = abs(x - 2) + abs(y - 12)
                bonus = (benefits['trait_effectiveness_multiplier'] - 1.0) * 100 if benefits['trait_effectiveness_multiplier'] > 1.0 else 0
                can_rest = "Yes" if benefits['has_housing'] else "No"
                print(f"   - Tile ({x}, {y}), distance {distance}: +{bonus:.0f}% trait effectiveness, can rest: {can_rest}")
    else:
        print("   [FAIL] Failed to place employee housing")
    
    print("\n5. Testing Combined Effects:")
    print("   - Checking tile (8, 8) which should have storage silo effect:")
    benefits = building_manager.get_spatial_benefits_at(8, 8)
    summary = building_manager.get_spatial_effects_summary(8, 8)
    print(f"   - Effects summary: {summary}")
    
    print("\n6. Testing Buildings in Radius Query:")
    buildings_near_center = building_manager.get_buildings_in_radius(8, 8, 5)
    print(f"   - Buildings within 5 tiles of (8,8): {len(buildings_near_center)} buildings")
    for building in buildings_near_center:
        distance = abs(building.x - 8) + abs(building.y - 8)
        print(f"     * {building.building_type.name} at ({building.x}, {building.y}), distance {distance}")
    
    print("\n=== Spatial Building Benefits Test Complete ===")
    print(f"Final economy balance: ${economy_manager.get_current_balance()}")

if __name__ == "__main__":
    test_spatial_benefits()