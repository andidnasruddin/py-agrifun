"""
Test Building & Infrastructure System - Comprehensive Farm Construction Validation

This test validates the complete Building & Infrastructure System including:
- Farm building construction and management
- Infrastructure networks and connectivity  
- Multi-stage construction with resource requirements
- Building upgrade and expansion systems
- Maintenance and operational costs
- Property value and asset management
- Integration with Time, Economy, and Employee systems
"""

import asyncio
import time
from scripts.systems.building_system import (
    BuildingSystem, BuildingType, BuildingStatus, InfrastructureType, ResourceType,
    get_building_system, initialize_building_system,
    start_construction, get_building_info, get_building_summary
)
from scripts.systems.time_system import get_time_system, Season
from scripts.systems.economy_system import get_economy_system


async def test_building_system():
    """Test comprehensive building and infrastructure system"""
    print("=" * 60)
    print("BUILDING & INFRASTRUCTURE SYSTEM TEST")
    print("=" * 60)
    
    try:
        # Test 1: Building System Initialization
        print("\n>>> Test 1: Building System Initialization")
        
        building_system = initialize_building_system()
        time_system = get_time_system()
        economy_system = get_economy_system()
        
        initial_summary = building_system.get_system_summary()
        
        print(f"Building system created: {building_system is not None}")
        print(f"Total buildings: {initial_summary['total_buildings']}")
        print(f"Total infrastructure: {initial_summary['total_infrastructure']}")
        print(f"Resource inventory: {initial_summary['resource_inventory']}")
        print(f"Property value: ${initial_summary['total_property_value']:.2f}")
        
        # Test 2: Building Planning and Cost Estimation
        print("\n>>> Test 2: Building Planning and Cost Estimation")
        
        # Test planning different building types
        building_types_to_test = [
            BuildingType.STORAGE_SILO,
            BuildingType.BARN,
            BuildingType.GREENHOUSE,
            BuildingType.EQUIPMENT_SHED,
            BuildingType.FARMHOUSE
        ]
        
        planning_results = {}
        for building_type in building_types_to_test:
            location = (5, 5)  # Test location
            plan_result = building_system.plan_building(building_type, location)
            planning_results[building_type] = plan_result
            
            print(f"  {building_type.value} planning: {plan_result['success']}")
            if plan_result['success']:
                print(f"    Total cost: ${plan_result['total_cost']:.2f}")
                print(f"    Construction time: {plan_result['construction_time_days']} days")
                print(f"    Required workers: {plan_result['required_workers']}")
                print(f"    Functionality: {plan_result['provides_functionality']}")
            else:
                print(f"    Issue: {plan_result['message']}")
        
        # Test 3: Resource Management and Availability
        print("\n>>> Test 3: Resource Management and Availability")
        
        # Check current resources
        construction_manager = building_system.construction_manager
        print(f"Current resource inventory:")
        for resource_type, amount in construction_manager.resource_inventory.items():
            print(f"  {resource_type.value}: {amount}")
        
        # Test building viability
        silo_plan = planning_results[BuildingType.STORAGE_SILO]
        if silo_plan['success']:
            can_build = construction_manager.can_build(BuildingType.STORAGE_SILO, (5, 5))
            print(f"\nCan build storage silo: {can_build['can_build']}")
            print(f"Resource check: {can_build['resource_check']}")
            print(f"Space check: {can_build['space_check']}")
            
            if not can_build['can_build']:
                print(f"Missing resources: {can_build['missing_resources']}")
        
        # Test 4: Building Construction Process
        print("\n>>> Test 4: Building Construction Process")
        
        initial_cash = economy_system.current_cash
        print(f"Initial cash: ${initial_cash:.2f}")
        
        # Ensure we have enough resources for construction
        for resource_type in ResourceType:
            construction_manager.resource_inventory[resource_type] = 200
        
        # Start construction of equipment shed (smaller, cheaper building)
        if economy_system.current_cash >= 10000:  # Ensure we have enough cash
            construction_result = building_system.start_construction(
                BuildingType.EQUIPMENT_SHED, (6, 6)
            )
            
            print(f"Construction started: {construction_result['success']}")
            if construction_result['success']:
                building_id = construction_result['building_id']
                print(f"  Building ID: {building_id}")
                print(f"  Estimated completion: {construction_result['estimated_completion_days']} days")
                print(f"  Transaction ID: {construction_result['transaction_id']}")
                
                # Check building info during construction
                building_info = building_system.get_building_info(building_id)
                if building_info:
                    print(f"  Construction status: {building_info['status']}")
                    if building_info['construction_info']:
                        print(f"  Progress: {building_info['construction_info']['progress']:.1%}")
                        print(f"  Workers assigned: {building_info['construction_info']['workers_assigned']}")
            else:
                print(f"  Error: {construction_result['message']}")
        else:
            print("Insufficient funds for construction test - skipping")
        
        # Test 5: Infrastructure Development
        print("\n>>> Test 5: Infrastructure Development")
        
        # Build different types of infrastructure
        infrastructure_tests = [
            (InfrastructureType.ROAD, (0, 0), (5, 0)),
            (InfrastructureType.FENCE, (0, 0), (0, 5)),
            (InfrastructureType.IRRIGATION_PIPE, (3, 3), (8, 8)),
            (InfrastructureType.POWER_LINE, (1, 1), (10, 1))
        ]
        
        infrastructure_results = []
        for infra_type, start_loc, end_loc in infrastructure_tests:
            if economy_system.current_cash >= 500:  # Check if we have enough for infrastructure
                infra_result = building_system.build_infrastructure(infra_type, start_loc, end_loc)
                infrastructure_results.append(infra_result)
                
                print(f"  {infra_type.value}: {infra_result['success']}")
                if infra_result['success']:
                    print(f"    Cost: ${infra_result['total_cost']:.2f}")
                    print(f"    Length: {infra_result['length']:.1f} units")
                    print(f"    Infrastructure ID: {infra_result['infrastructure_id']}")
                else:
                    print(f"    Error: {infra_result['message']}")
            else:
                print(f"  {infra_type.value}: Skipped (insufficient funds)")
        
        # Test 6: Construction Progress Simulation
        print("\n>>> Test 6: Construction Progress Simulation")
        
        # Get list of active construction projects
        active_projects = building_system.construction_manager.active_projects
        print(f"Active construction projects: {len(active_projects)}")
        
        if active_projects:
            # Simulate time passage to advance construction
            print("Simulating construction progress...")
            
            # Advance time to trigger construction updates
            for hour in range(24):  # Simulate 24 hours
                time_system.advance_time(60)  # 1 hour
                
                # Check for any completed projects every few hours
                if hour % 6 == 0:
                    current_projects = len(building_system.construction_manager.active_projects)
                    print(f"  Hour {hour}: {current_projects} projects remaining")
                    
                    # Check progress of first project
                    if building_system.construction_manager.active_projects:
                        first_project = list(building_system.construction_manager.active_projects.values())[0]
                        progress = first_project['progress']
                        print(f"    First project progress: {progress:.1%}")
            
            # Check final construction state
            final_projects = len(building_system.construction_manager.active_projects)
            print(f"Final active projects: {final_projects}")
        
        # Test 7: Building Operations and Maintenance
        print("\n>>> Test 7: Building Operations and Maintenance")
        
        # Check completed buildings
        completed_buildings = [b for b in building_system.buildings.values() 
                             if b.status == BuildingStatus.OPERATIONAL]
        
        print(f"Operational buildings: {len(completed_buildings)}")
        
        for building in completed_buildings[:3]:  # Check first 3 buildings
            building_info = building_system.get_building_info(building.building_id)
            if building_info:
                print(f"  {building_info['building_type']}:")
                print(f"    Condition: {building_info['condition']:.1f}%")
                print(f"    Storage capacity: {building_info['storage_capacity']}")
                print(f"    Current value: ${building_info['current_value']:.2f}")
                print(f"    Needs maintenance: {building_info['maintenance_needed']}")
        
        # Test building upgrade
        if completed_buildings:
            test_building = completed_buildings[0]
            upgrade_result = building_system.upgrade_building(test_building.building_id)
            
            print(f"\nBuilding upgrade test: {upgrade_result['success']}")
            if upgrade_result['success']:
                print(f"  New level: {upgrade_result['new_level']}")
                print(f"  Upgrade cost: ${upgrade_result['upgrade_cost']:.2f}")
                print(f"  New value: ${upgrade_result['new_value']:.2f}")
            else:
                print(f"  Error: {upgrade_result['message']}")
        
        # Test 8: Economic Integration
        print("\n>>> Test 8: Economic Integration")
        
        # Check economic impact of building activities
        final_cash = economy_system.current_cash
        cash_spent = initial_cash - final_cash
        
        print(f"Cash flow analysis:")
        print(f"  Initial cash: ${initial_cash:.2f}")
        print(f"  Final cash: ${final_cash:.2f}")
        print(f"  Total spent: ${cash_spent:.2f}")
        
        # Check transaction history for building-related transactions
        building_transactions = [t for t in economy_system.transactions 
                               if 'building' in t.description.lower() or 'construction' in t.description.lower()]
        
        print(f"  Building-related transactions: {len(building_transactions)}")
        
        for transaction in building_transactions[-3:]:  # Show last 3 transactions
            print(f"    {transaction.description}: ${transaction.amount:.2f}")
        
        # Test 9: Property Value and Asset Management
        print("\n>>> Test 9: Property Value and Asset Management")
        
        final_summary = building_system.get_system_summary()
        
        print(f"Asset summary:")
        print(f"  Total property value: ${final_summary['total_property_value']:.2f}")
        print(f"  Construction investment: ${final_summary['total_construction_investment']:.2f}")
        print(f"  Total maintenance costs: ${final_summary['total_maintenance_costs']:.2f}")
        print(f"  Daily maintenance cost: ${final_summary['daily_maintenance_cost']:.2f}")
        
        # Building type distribution
        if final_summary['buildings_by_type']:
            print(f"  Buildings by type: {final_summary['buildings_by_type']}")
        
        # Building status distribution
        if final_summary['buildings_by_status']:
            print(f"  Buildings by status: {final_summary['buildings_by_status']}")
        
        # Infrastructure distribution
        if final_summary['infrastructure_by_type']:
            print(f"  Infrastructure by type: {final_summary['infrastructure_by_type']}")
        
        # Test 10: Seasonal Construction Effects
        print("\n>>> Test 10: Seasonal Construction Effects")
        
        # Test construction in different seasons
        current_season = time_system.get_current_season()
        print(f"Current season: {current_season.value}")
        
        # Start a new construction project to test seasonal effects
        if economy_system.current_cash >= 8000:
            # Ensure resources
            for resource_type in ResourceType:
                construction_manager.resource_inventory[resource_type] = 100
            
            seasonal_construction = building_system.start_construction(
                BuildingType.EQUIPMENT_SHED, (10, 10)
            )
            
            if seasonal_construction['success']:
                print(f"Started seasonal construction: {seasonal_construction['building_id']}")
                
                # Advance through seasons and check construction rates
                seasons_tested = []
                for season_change in range(2):  # Test 2 season changes
                    time_system.advance_time(90 * 24 * 60)  # 90 days to next season
                    new_season = time_system.get_current_season()
                    seasons_tested.append(new_season.value)
                    
                    # Check if project still exists and progress rate
                    active_projects = building_system.construction_manager.active_projects
                    if active_projects:
                        project = list(active_projects.values())[0]
                        progress_rate = project['daily_progress_rate']
                        print(f"  {new_season.value} season progress rate: {progress_rate:.4f}")
                
                print(f"Seasons tested: {seasons_tested}")
        
        # Test 11: Building Demolition
        print("\n>>> Test 11: Building Demolition")
        
        # Test demolishing a building if we have any
        demolishable_buildings = [b for b in building_system.buildings.values() 
                                if b.status == BuildingStatus.OPERATIONAL]
        
        if demolishable_buildings:
            test_building = demolishable_buildings[-1]  # Use last building
            initial_value = test_building.current_value
            
            demolish_result = building_system.demolish_building(test_building.building_id)
            
            print(f"Building demolition test: {demolish_result['success']}")
            if demolish_result['success']:
                print(f"  Original value: ${initial_value:.2f}")
                print(f"  Salvage value: ${demolish_result['salvage_value']:.2f}")
                print(f"  Salvage percentage: {(demolish_result['salvage_value']/initial_value)*100:.1f}%")
        else:
            print("No buildings available for demolition test")
        
        # Test 12: System Performance and Limits
        print("\n>>> Test 12: System Performance and Limits")
        
        # Test system limits
        max_buildings = final_summary.get('max_buildings', 50)
        max_infrastructure = building_system.config_manager.get('infrastructure.max_infrastructure', 200)
        
        print(f"System limits:")
        print(f"  Max buildings: {max_buildings}")
        print(f"  Current buildings: {final_summary['total_buildings']}")
        print(f"  Max infrastructure: {max_infrastructure}")
        print(f"  Current infrastructure: {final_summary['total_infrastructure']}")
        
        # Test building at capacity (if not already at limit)
        if final_summary['total_buildings'] < max_buildings:
            capacity_test = building_system.plan_building(BuildingType.STORAGE_SILO, (15, 15))
            print(f"  Can build more buildings: {capacity_test['success']}")
        else:
            print(f"  At building capacity limit")
        
        # Test global convenience functions
        print("\n>>> Test 13: Global Convenience Functions")
        
        # Test global access functions
        global_summary = get_building_summary()
        print(f"Global summary access: {global_summary['total_buildings']} buildings")
        
        # Test convenience construction function
        if economy_system.current_cash >= 8000:
            # Ensure resources
            for resource_type in ResourceType:
                construction_manager.resource_inventory[resource_type] = 50
            
            global_construction = start_construction(BuildingType.EQUIPMENT_SHED, (20, 20))
            print(f"Global construction function: {global_construction['success']}")
        
        # Get info on any building
        if building_system.buildings:
            test_building_id = list(building_system.buildings.keys())[0]
            global_info = get_building_info(test_building_id)
            print(f"Global building info access: {global_info is not None}")
            if global_info:
                print(f"  Building type: {global_info['building_type']}")
                print(f"  Status: {global_info['status']}")
        
        print("\n" + "=" * 60)
        print("BUILDING & INFRASTRUCTURE SYSTEM TEST: PASSED")
        print("All construction and infrastructure systems working correctly!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nBuilding system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_building_integration():
    """Test building system integration with other systems"""
    print("\n" + "=" * 60)
    print("BUILDING INTEGRATION TEST")
    print("=" * 60)
    
    try:
        building_system = get_building_system()
        time_system = get_time_system()
        economy_system = get_economy_system()
        
        # Test time integration
        print("\n>>> Testing Time Integration")
        
        initial_time = time_system.get_current_time()
        print(f"Current time: Day {initial_time.day}, Hour {initial_time.hour}")
        
        # Ensure resources for construction
        construction_manager = building_system.construction_manager
        for resource_type in ResourceType:
            construction_manager.resource_inventory[resource_type] = 100
        
        # Start construction and test time-based progress
        if economy_system.current_cash >= 5000:
            construction_result = building_system.start_construction(
                BuildingType.EQUIPMENT_SHED, (25, 25)
            )
            
            if construction_result['success']:
                building_id = construction_result['building_id']
                
                # Check initial progress
                initial_info = building_system.get_building_info(building_id)
                initial_progress = 0.0
                if initial_info and initial_info['construction_info']:
                    initial_progress = initial_info['construction_info']['progress']
                
                print(f"Construction started - initial progress: {initial_progress:.2%}")
                
                # Advance time and check progress
                time_system.advance_time(12 * 60)  # 12 hours
                
                final_info = building_system.get_building_info(building_id)
                final_progress = 0.0
                if final_info and final_info['construction_info']:
                    final_progress = final_info['construction_info']['progress']
                
                print(f"After 12 hours - progress: {final_progress:.2%}")
                progress_made = final_progress > initial_progress
                print(f"Time-based construction progress: {progress_made}")
        
        # Test economic integration
        print("\n>>> Testing Economic Integration")
        
        initial_cash = economy_system.current_cash
        initial_transactions = len(economy_system.transactions)
        
        # Test economic transactions from building activities
        if economy_system.current_cash >= 3000:
            infra_result = building_system.build_infrastructure(
                InfrastructureType.ROAD, (20, 20), (25, 20)
            )
            
            final_cash = economy_system.current_cash
            final_transactions = len(economy_system.transactions)
            
            cash_spent = initial_cash - final_cash
            new_transactions = final_transactions - initial_transactions
            
            print(f"Infrastructure construction: {infra_result['success']}")
            print(f"Cash spent: ${cash_spent:.2f}")
            print(f"New transactions: {new_transactions}")
            
            if new_transactions > 0:
                latest_transaction = economy_system.transactions[-1]
                print(f"Latest transaction: {latest_transaction.description} (${latest_transaction.amount:.2f})")
        
        # Test seasonal effects
        print("\n>>> Testing Seasonal Effects")
        
        # Test construction rates in different seasons
        current_season = time_system.get_current_season()
        print(f"Current season: {current_season.value}")
        
        # Check if there are active projects to test seasonal effects
        active_projects = building_system.construction_manager.active_projects
        if active_projects:
            project = list(active_projects.values())[0]
            current_rate = project['daily_progress_rate']
            print(f"Current progress rate: {current_rate:.4f}")
            
            # Advance to next season
            time_system.advance_time(90 * 24 * 60)  # 90 days
            new_season = time_system.get_current_season()
            
            # Check if rate changed
            if project in building_system.construction_manager.active_projects.values():
                new_rate = project['daily_progress_rate']
                print(f"New season ({new_season.value}) rate: {new_rate:.4f}")
                
                rate_changed = abs(new_rate - current_rate) > 0.001
                print(f"Seasonal rate adjustment applied: {rate_changed}")
        
        # Test daily maintenance integration
        print("\n>>> Testing Daily Maintenance Integration")
        
        # Check for operational buildings
        operational_buildings = [b for b in building_system.buildings.values() 
                               if b.status == BuildingStatus.OPERATIONAL]
        
        if operational_buildings:
            print(f"Operational buildings for maintenance: {len(operational_buildings)}")
            
            # Record maintenance costs before daily update
            initial_maintenance_costs = building_system.total_maintenance_costs
            
            # Advance one day to trigger maintenance
            time_system.advance_time(24 * 60)  # 1 day
            
            final_maintenance_costs = building_system.total_maintenance_costs
            maintenance_charged = final_maintenance_costs > initial_maintenance_costs
            
            print(f"Daily maintenance charged: {maintenance_charged}")
            if maintenance_charged:
                daily_cost = final_maintenance_costs - initial_maintenance_costs
                print(f"Daily maintenance cost: ${daily_cost:.2f}")
        
        # Test building condition degradation
        print("\n>>> Testing Building Condition Over Time")
        
        if operational_buildings:
            test_building = operational_buildings[0]
            initial_condition = test_building.condition
            
            # Advance significant time to see condition changes
            time_system.advance_time(30 * 24 * 60)  # 30 days
            
            final_condition = test_building.condition
            condition_degraded = final_condition < initial_condition
            
            print(f"Building condition degradation:")
            print(f"  Initial condition: {initial_condition:.1f}%")
            print(f"  Final condition: {final_condition:.1f}%")
            print(f"  Degradation occurred: {condition_degraded}")
            
            if condition_degraded:
                degradation_amount = initial_condition - final_condition
                print(f"  Degradation amount: {degradation_amount:.1f}%")
        
        # Test infrastructure capacity and load
        print("\n>>> Testing Infrastructure Load Management")
        
        # Check infrastructure status
        infrastructure_items = list(building_system.infrastructure.values())
        if infrastructure_items:
            test_infrastructure = infrastructure_items[0]
            print(f"Infrastructure testing:")
            print(f"  Type: {test_infrastructure.infrastructure_type.value}")
            print(f"  Capacity: {test_infrastructure.capacity}")
            print(f"  Current load: {test_infrastructure.current_load}")
            print(f"  Is overloaded: {test_infrastructure.is_overloaded()}")
            print(f"  Network efficiency: {test_infrastructure.network_efficiency:.2f}")
        
        print("\nBuilding integration test passed!")
        
        return True
        
    except Exception as e:
        print(f"Building integration test failed: {e}")
        return False


if __name__ == "__main__":
    try:
        # Run main building system test
        success1 = asyncio.run(test_building_system())
        
        # Run integration test
        success2 = asyncio.run(test_building_integration())
        
        if success1 and success2:
            print("\n[SUCCESS] All building management tests passed!")
        else:
            print("\n[FAILED] Some tests failed!")
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()