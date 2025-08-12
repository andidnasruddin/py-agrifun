#!/usr/bin/env python3
"""
Quick test script for the soil information panel system
"""

import pygame
import sys
import os

# Add the scripts directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.config import *
from scripts.core.grid_manager import Tile

def test_soil_panel_functionality():
    """Test that soil panel functionality works correctly"""
    print("Testing Soil Information Panel System")
    print("=" * 50)
    
    # Test 1: Create a tilled tile with crop history
    tile = Tile(5, 5)
    tile.terrain_type = 'tilled'  # Make it tilled so it can show soil info
    tile.soil_nutrients = {'nitrogen': 75, 'phosphorus': 60, 'potassium': 85}
    tile.crop_history = ['corn', 'wheat']
    tile.seasons_rested = 0
    
    print("[OK] Test 1: Tile creation with soil data")
    print(f"   Tile location: ({tile.x}, {tile.y})")
    print(f"   Terrain type: {tile.terrain_type}")
    print(f"   Soil nutrients: {tile.soil_nutrients}")
    print(f"   Crop history: {tile.crop_history}")
    
    # Test 2: Verify soil health methods exist
    try:
        health_level = tile.get_soil_health_level()
        health_color = tile.get_soil_health_color()
        print("[OK] Test 2: Soil health methods working")
        print(f"   Health level: {health_level}")
        print(f"   Health color: {health_color}")
    except AttributeError as e:
        print("[FAIL] Test 2: Soil health methods missing")
        print(f"   Error: {e}")
        return False
    
    # Test 3: Test rotation bonus calculations
    try:
        for crop_type in CROP_TYPES.keys():
            bonuses = tile.calculate_rotation_bonuses(crop_type)
            print(f"[OK] Test 3: Rotation bonuses for {crop_type}")
            print(f"   Yield bonus: {bonuses['yield']*100:.1f}%")
            print(f"   Quality bonus: {bonuses['quality']*100:.1f}%")
    except Exception as e:
        print("[FAIL] Test 3: Rotation bonus calculation failed")
        print(f"   Error: {e}")
        return False
    
    # Test 4: Verify soil configuration constants
    required_constants = ['SOIL_NUTRIENTS', 'CROP_SOIL_EFFECTS', 'ROTATION_BONUSES', 'SOIL_HEALTH_LEVELS']
    for const in required_constants:
        if const in globals():
            print(f"[OK] Test 4: Configuration constant {const} exists")
        else:
            print(f"[FAIL] Test 4: Configuration constant {const} missing")
            return False
    
    print("\n[SUCCESS] All soil panel tests passed!")
    print("\nInstructions for manual testing:")
    print("1. Run: python main.py")
    print("2. Select tiles with drag selection (left mouse)")
    print("3. Press 'T' to till the selected tiles")
    print("4. Click on a tilled tile to open the soil information panel")
    print("5. Verify the panel shows:")
    print("   - Soil health status")
    print("   - Nutrient levels with visual bars")
    print("   - Crop history")
    print("   - Planting recommendations with bonuses")
    print("   - Close button functionality")
    
    return True

if __name__ == "__main__":
    success = test_soil_panel_functionality()
    if success:
        print("\n[READY] Ready to test in game!")
    else:
        print("\n[ERROR] Tests failed - check implementation")
        sys.exit(1)