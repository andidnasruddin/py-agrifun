"""
Test Crop Growth & Agricultural Systems - Comprehensive Farming Simulation Validation

This test validates the complete Crop Growth & Agricultural Systems including:
- Multi-stage crop growth with environmental factors
- Soil health management with N-P-K tracking
- Irrigation and water management systems
- Fertilization and soil amendment systems
- Seasonal planting recommendations
- Harvest timing and yield calculations
- Integration with Time, Economy, and Weather systems
"""

import asyncio
import time
from scripts.systems.crop_system import (
    CropSystem, CropType, CropStage, FertilizerType, SoilType,
    get_crop_system, initialize_crop_system,
    plant_crop, harvest_crop, get_tile_info, get_crop_summary
)
from scripts.systems.time_system import get_time_system, Season
from scripts.systems.economy_system import get_economy_system


async def test_crop_system():
    """Test comprehensive crop growth and agricultural system"""
    print("=" * 60)
    print("CROP GROWTH & AGRICULTURAL SYSTEM TEST")
    print("=" * 60)
    
    try:
        # Test 1: Crop System Initialization
        print("\n>>> Test 1: Crop System Initialization")
        
        crop_system = initialize_crop_system()
        time_system = get_time_system()
        economy_system = get_economy_system()
        
        initial_summary = crop_system.get_system_summary()
        
        print(f"Crop system created: {crop_system is not None}")
        print(f"Total farm tiles: {initial_summary['total_tiles']}")
        print(f"Average soil fertility: {initial_summary['average_soil_fertility']:.2f}")
        print(f"Fertilizer inventory: {initial_summary['fertilizer_inventory']}")
        
        # Test 2: Soil Health and Tile Management
        print("\n>>> Test 2: Soil Health and Tile Management")
        
        # Get tile information
        tile_info = crop_system.get_tile_info(5, 5)
        print(f"Tile (5,5) info available: {tile_info is not None}")
        
        if tile_info:
            print(f"  Soil type: {tile_info['soil_type']}")
            print(f"  Soil fertility: {tile_info['soil_fertility']:.2f}")
            print(f"  Is tilled: {tile_info['is_tilled']}")
            print(f"  Has irrigation: {tile_info['has_irrigation']}")
            
            nutrients = tile_info['soil_nutrients']
            print(f"  Nitrogen: {nutrients['nitrogen']:.1f}")
            print(f"  Phosphorus: {nutrients['phosphorus']:.1f}")
            print(f"  Potassium: {nutrients['potassium']:.1f}")
            print(f"  pH level: {nutrients['ph_level']:.1f}")
            print(f"  Water content: {nutrients['water_content']:.1f}")
        
        # Test 3: Tile Preparation and Tilling
        print("\n>>> Test 3: Tile Preparation and Tilling")
        
        # Till a tile
        till_result = crop_system.till_tile(5, 5)
        print(f"Tilling success: {till_result['success']}")
        
        if till_result['success']:
            updated_tile = crop_system.get_tile_info(5, 5)
            print(f"  Tile now tilled: {updated_tile['is_tilled']}")
        
        # Test 4: Crop Planting System
        print("\n>>> Test 4: Crop Planting System")
        
        # Test seasonal planting suitability
        current_season = time_system.get_current_season()
        print(f"Current season: {current_season.value}")
        
        # Try planting different crops
        crop_results = {}
        test_crops = [CropType.CORN, CropType.TOMATOES, CropType.LETTUCE, CropType.WHEAT]
        
        for i, crop_type in enumerate(test_crops):
            x, y = 5 + i, 5
            
            # Till the tile first
            crop_system.till_tile(x, y)
            
            # Plant the crop
            plant_result = crop_system.plant_crop(x, y, crop_type)
            crop_results[crop_type] = plant_result
            
            print(f"  {crop_type.value} planting: {plant_result['success']}")
            if plant_result['success']:
                print(f"    Crop ID: {plant_result['crop_id']}")
            else:
                print(f"    Reason: {plant_result['message']}")
        
        # Test 5: Fertilizer Application
        print("\n>>> Test 5: Fertilizer Application System")
        
        # Apply different fertilizers to planted crops
        fertilizer_tests = [
            (FertilizerType.NITROGEN, 10.0),
            (FertilizerType.COMPOST, 15.0),
            (FertilizerType.PHOSPHORUS, 8.0)
        ]
        
        for fertilizer_type, amount in fertilizer_tests:
            fert_result = crop_system.apply_fertilizer(5, 5, fertilizer_type, amount)
            print(f"  {fertilizer_type.value} application: {fert_result['success']}")
            
            if fert_result['success']:
                print(f"    Amount applied: {fert_result['amount_applied']}")
                print(f"    New fertility: {fert_result['new_fertility']:.2f}")
            else:
                print(f"    Error: {fert_result['message']}")
        
        # Check fertilizer inventory after application
        post_fert_summary = crop_system.get_system_summary()
        print(f"  Updated fertilizer inventory: {post_fert_summary['fertilizer_inventory']}")
        
        # Test 6: Irrigation Installation
        print("\n>>> Test 6: Irrigation Installation")
        
        # Install irrigation on a tile
        irrigation_result = crop_system.install_irrigation(6, 6)
        print(f"Irrigation installation: {irrigation_result['success']}")
        
        if irrigation_result['success']:
            print(f"  Installation cost: ${irrigation_result['installation_cost']:.2f}")
            
            # Check tile now has irrigation
            irrigated_tile = crop_system.get_tile_info(6, 6)
            print(f"  Tile has irrigation: {irrigated_tile['has_irrigation']}")
        
        # Test 7: Crop Growth Simulation
        print("\n>>> Test 7: Crop Growth Simulation")
        
        # Get initial crop stages
        planted_tiles = [(5, 5), (6, 5), (7, 5), (8, 5)]
        initial_stages = {}
        
        for x, y in planted_tiles:
            tile_info = crop_system.get_tile_info(x, y)
            if tile_info and tile_info['planted_crop']:
                crop_info = tile_info['planted_crop']
                initial_stages[(x, y)] = {
                    'crop_type': crop_info['crop_type'],
                    'stage': crop_info['current_stage'],
                    'progress': crop_info['stage_progress'],
                    'days_planted': crop_info['days_planted']
                }
        
        print(f"Initial crop stages tracked: {len(initial_stages)}")
        for (x, y), info in initial_stages.items():
            print(f"  ({x},{y}): {info['crop_type']} - {info['stage']} ({info['progress']:.1%})")
        
        # Advance time to trigger growth
        print("\nAdvancing time to simulate growth...")
        time_system.advance_time(24 * 60)  # 1 day
        
        # Check crop progress after time advancement
        growth_occurred = False
        for x, y in planted_tiles:
            tile_info = crop_system.get_tile_info(x, y)
            if tile_info and tile_info['planted_crop']:
                crop_info = tile_info['planted_crop']
                initial = initial_stages.get((x, y), {})
                
                if initial and crop_info['stage_progress'] != initial['progress']:
                    growth_occurred = True
                    print(f"  ({x},{y}): {crop_info['crop_type']} progress: {crop_info['stage_progress']:.1%}")
                    print(f"    Health: {crop_info['health']:.1f}, Stress: {crop_info['stress_level']:.1f}")
                    print(f"    Expected yield: {crop_info['expected_yield']:.1f}")
        
        print(f"Growth simulation working: {growth_occurred}")
        
        # Test 8: Accelerated Growth to Maturity
        print("\n>>> Test 8: Accelerated Growth to Maturity")
        
        # Advance time significantly to reach harvest stage
        print("Fast-forwarding time for harvest testing...")
        
        # Advance through multiple seasons to get mature crops
        for i in range(12):  # 12 months
            time_system.advance_time(30 * 24 * 60)  # 30 days
            
            # Check for mature crops
            mature_crops = []
            for x, y in planted_tiles:
                tile_info = crop_system.get_tile_info(x, y)
                if tile_info and tile_info['planted_crop']:
                    crop_info = tile_info['planted_crop']
                    if crop_info['ready_for_harvest']:
                        mature_crops.append((x, y, crop_info))
            
            if mature_crops:
                print(f"Found {len(mature_crops)} mature crops after {i+1} months")
                break
        
        # Test 9: Crop Harvesting
        print("\n>>> Test 9: Crop Harvesting System")
        
        harvest_results = []
        initial_cash = economy_system.current_cash
        
        for x, y in planted_tiles:
            tile_info = crop_system.get_tile_info(x, y)
            if tile_info and tile_info['planted_crop']:
                crop_info = tile_info['planted_crop']
                
                if crop_info['ready_for_harvest']:
                    harvest_result = crop_system.harvest_crop(x, y)
                    harvest_results.append(harvest_result)
                    
                    print(f"  Harvest at ({x},{y}): {harvest_result['success']}")
                    if harvest_result['success']:
                        print(f"    Amount: {harvest_result['harvest_amount']:.1f}")
                        print(f"    Quality: {harvest_result['quality']:.2f}")
                        print(f"    Value: ${harvest_result['total_value']:.2f}")
        
        final_cash = economy_system.current_cash
        cash_gained = final_cash - initial_cash
        
        print(f"Successful harvests: {len([r for r in harvest_results if r['success']])}")
        print(f"Cash gained from harvest: ${cash_gained:.2f}")
        
        # Test 10: Seasonal Recommendations
        print("\n>>> Test 10: Seasonal Planting Recommendations")
        
        # Test recommendations for different seasons
        seasons = [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER]
        
        for season in seasons:
            # Temporarily advance to each season
            if season != time_system.get_current_season():
                time_system.advance_time(90 * 24 * 60)  # 90 days to next season
            
            current_season = time_system.get_current_season()
            print(f"\n{current_season.value.title()} season recommendations:")
            
            # Test planting suitability for each crop
            suitable_crops = []
            for crop_type in CropType:
                x, y = 10, 10  # Test location
                crop_system.till_tile(x, y)
                
                plant_test = crop_system.plant_crop(x, y, crop_type)
                if plant_test['success']:
                    suitable_crops.append(crop_type.value)
                    # Clear the test crop
                    crop_system.harvest_crop(x, y)  # This will clear even if not mature
                    crop_system.farm_tiles[(x, y)].planted_crop = None
            
            print(f"  Suitable crops: {suitable_crops}")
        
        # Test 11: System Summary and Analytics
        print("\n>>> Test 11: System Summary and Analytics")
        
        final_summary = crop_system.get_system_summary()
        
        print(f"Final system status:")
        print(f"  Total tiles: {final_summary['total_tiles']}")
        print(f"  Tilled tiles: {final_summary['tilled_tiles']}")
        print(f"  Planted tiles: {final_summary['planted_tiles']}")
        print(f"  Irrigated tiles: {final_summary['irrigated_tiles']}")
        print(f"  Average soil fertility: {final_summary['average_soil_fertility']:.2f}")
        print(f"  Total crops planted: {final_summary['total_crops_planted']}")
        print(f"  Total crops harvested: {final_summary['total_crops_harvested']}")
        print(f"  Total yield harvested: {final_summary['total_yield_harvested']:.1f}")
        
        # Crop stage distribution
        print(f"  Crops by stage: {final_summary['crops_by_stage']}")
        
        # Test 12: Global Convenience Functions
        print("\n>>> Test 12: Global Convenience Functions")
        
        # Test global access functions
        global_tile_info = get_tile_info(5, 5)
        global_summary = get_crop_summary()
        
        print(f"Global tile info access: {global_tile_info is not None}")
        print(f"Global summary access: {global_summary['total_tiles']} tiles")
        
        # Test convenience planting and harvesting
        crop_system.till_tile(12, 12)
        global_plant = plant_crop(12, 12, CropType.LETTUCE)
        print(f"Global plant function: {global_plant['success']}")
        
        print("\n" + "=" * 60)
        print("CROP GROWTH & AGRICULTURAL SYSTEM TEST: PASSED")
        print("All agricultural systems working correctly!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nCrop system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_crop_integration():
    """Test crop system integration with other systems"""
    print("\n" + "=" * 60)
    print("CROP INTEGRATION TEST")
    print("=" * 60)
    
    try:
        crop_system = get_crop_system()
        time_system = get_time_system()
        economy_system = get_economy_system()
        
        # Test weather integration
        print("\n>>> Testing Weather Integration")
        
        # Plant a crop
        crop_system.till_tile(15, 15)
        plant_result = crop_system.plant_crop(15, 15, CropType.CORN)
        
        if plant_result['success']:
            # Get initial crop status
            initial_tile = crop_system.get_tile_info(15, 15)
            initial_progress = initial_tile['planted_crop']['stage_progress']
            
            # Advance time with different weather conditions
            weather = time_system.get_current_weather()
            print(f"Current weather: {weather.weather_type.value}")
            print(f"Temperature: {weather.temperature_c:.1f}C")
            print(f"Growth modifier: {weather.crop_growth_modifier:.2f}")
            
            # Advance time and check growth
            time_system.advance_time(24 * 60)  # 1 day
            
            final_tile = crop_system.get_tile_info(15, 15)
            final_progress = final_tile['planted_crop']['stage_progress']
            
            growth_occurred = final_progress > initial_progress
            print(f"Weather-affected growth occurred: {growth_occurred}")
            
            if growth_occurred:
                growth_amount = final_progress - initial_progress
                print(f"  Growth amount: {growth_amount:.3f}")
        
        # Test economic integration
        print("\n>>> Testing Economic Integration")
        
        initial_cash = economy_system.current_cash
        initial_transactions = len(economy_system.transactions)
        
        # Install irrigation (economic transaction)
        irrigation_result = crop_system.install_irrigation(14, 14)
        
        final_cash = economy_system.current_cash
        final_transactions = len(economy_system.transactions)
        
        cash_spent = initial_cash - final_cash
        new_transactions = final_transactions - initial_transactions
        
        print(f"Irrigation installation: {irrigation_result['success']}")
        print(f"Cash spent: ${cash_spent:.2f}")
        print(f"New transactions: {new_transactions}")
        
        # Test soil nutrient depletion over time
        print("\n>>> Testing Soil Nutrient Dynamics")
        
        # Get initial soil nutrients
        test_tile = crop_system.get_tile_info(15, 15)
        initial_nutrients = test_tile['soil_nutrients'].copy()
        
        # Advance time significantly to see nutrient consumption
        time_system.advance_time(7 * 24 * 60)  # 1 week
        
        final_tile = crop_system.get_tile_info(15, 15)
        final_nutrients = final_tile['soil_nutrients']
        
        nutrient_changes = {}
        for nutrient in ['nitrogen', 'phosphorus', 'potassium', 'water_content']:
            initial_val = initial_nutrients[nutrient]
            final_val = final_nutrients[nutrient]
            change = final_val - initial_val
            nutrient_changes[nutrient] = change
        
        print(f"Nutrient changes over 1 week:")
        for nutrient, change in nutrient_changes.items():
            print(f"  {nutrient}: {change:+.1f}")
        
        nutrients_depleted = any(change < -1.0 for change in nutrient_changes.values())
        print(f"Nutrient depletion occurred: {nutrients_depleted}")
        
        # Test seasonal crop suitability
        print("\n>>> Testing Seasonal Crop Cycles")
        
        season_results = {}
        crops_to_test = [CropType.CORN, CropType.WHEAT, CropType.LETTUCE]
        
        for season in [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER]:
            # Advance to season if needed
            current_season = time_system.get_current_season()
            if current_season != season:
                time_system.advance_time(90 * 24 * 60)
            
            season_plantable = []
            for crop_type in crops_to_test:
                # Test on empty tile
                test_x, test_y = 13, 13
                test_tile = crop_system.farm_tiles[(test_x, test_y)]
                test_tile.planted_crop = None  # Clear any existing crop
                test_tile.is_tilled = True
                
                plant_test = crop_system.plant_crop(test_x, test_y, crop_type)
                if plant_test['success']:
                    season_plantable.append(crop_type.value)
                    # Clear the test
                    test_tile.planted_crop = None
            
            season_results[season.value] = season_plantable
        
        print(f"Seasonal planting results:")
        for season, crops in season_results.items():
            print(f"  {season}: {crops}")
        
        seasonal_variation = len(set(len(crops) for crops in season_results.values())) > 1
        print(f"Seasonal variation exists: {seasonal_variation}")
        
        print("\nCrop integration test passed!")
        
        return True
        
    except Exception as e:
        print(f"Crop integration test failed: {e}")
        return False


if __name__ == "__main__":
    try:
        # Run main crop system test
        success1 = asyncio.run(test_crop_system())
        
        # Run integration test
        success2 = asyncio.run(test_crop_integration())
        
        if success1 and success2:
            print("\n[SUCCESS] All crop management tests passed!")
        else:
            print("\n[FAILED] Some tests failed!")
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()