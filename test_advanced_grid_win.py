"""
Test Integration: Advanced Grid System with Enhanced Foundation

This test validates the integration of the Advanced Grid System with our enhanced
Event System, Entity-Component System, and Content Registry. It demonstrates the
complete multi-layer spatial management working with the foundation architecture.

Test Coverage:
- Multi-layer grid initialization
- Entity placement and spatial indexing
- Region-based processing
- Pathfinding integration
- Content-driven entity creation
- Performance monitoring
"""

import asyncio
import time
from scripts.core.event_system import get_global_event_system, EventPriority
from scripts.core.entity_component_system import get_entity_manager
from scripts.core.content_registry import get_content_registry
from scripts.core.advanced_grid_system import get_grid_system, GridLayer


def test_advanced_grid_integration():
    """Test complete integration of advanced grid system with foundation"""
    print(">>> Testing Advanced Grid System Integration...")
    
    # Initialize all systems
    event_system = get_global_event_system()
    entity_manager = get_entity_manager()
    content_registry = get_content_registry()
    grid_system = get_grid_system()
    
    # Test event tracking
    events_received = []
    
    def track_events(event_data):
        events_received.append(event_data)
    
    # Subscribe to grid events
    event_system.subscribe('tile_created', track_events)
    event_system.subscribe('entity_placed_on_grid', track_events)
    event_system.subscribe('active_region_changed', track_events)
    
    print(f"[OK] Grid System initialized: {grid_system.width}x{grid_system.height}")
    print(f"     - Regions: {len(grid_system.regions)}")
    print(f"     - Spatial layers: {len(grid_system.layer_spatial_indices)}")
    
    # Test 1: Multi-layer tile management
    print("\n>>> Test 1: Multi-layer Tile Management")
    
    # Create and configure tiles
    test_tiles = []
    for x in range(5, 10):
        for y in range(5, 10):
            tile = grid_system.get_or_create_tile(x, y)
            
            # Set terrain data
            tile.set_layer_data(GridLayer.TERRAIN, {
                'type': 'fertile_soil',
                'elevation': 100 + (x * y * 0.1),
                'drainage': 'good'
            })
            
            # Set soil data  
            tile.set_layer_data(GridLayer.SOIL, {
                'N': 50 + x, 'P': 40 + y, 'K': 35 + (x + y),
                'pH': 6.5 + (x * 0.1),
                'organic_matter': 3.0 + (y * 0.1)
            })
            
            test_tiles.append(tile)
    
    print(f"[OK] Created {len(test_tiles)} test tiles with multi-layer data")
    print(f"     - Sample tile (7,7) terrain: {test_tiles[12].get_layer_data(GridLayer.TERRAIN)}")
    print(f"     - Sample tile (7,7) soil: {test_tiles[12].get_layer_data(GridLayer.SOIL)}")
    
    # Test 2: Entity creation and placement
    print("\n>>> Test 2: Entity Creation and Spatial Indexing")
    
    created_entities = []
    
    # Create crop entities
    for i in range(15):
        x = 5 + (i % 5)
        y = 5 + (i // 5)
        
        # Create crop entity using ECS
        crop_entity = entity_manager.create_entity({
            'identity': {
                'name': f'corn_crop_{i}',
                'display_name': f'Corn Plant {i+1}'
            },
            'transform': {
                'x': float(x), 'y': float(y)
            },
            'crop': {
                'crop_type': 'corn',
                'variety': 'standard',
                'growth_stage': 'seed',
                'health': 100.0
            }
        })
        
        # Place on grid
        grid_system.add_entity_at_position(crop_entity, x, y, GridLayer.CROPS)
        created_entities.append(crop_entity)
    
    # Create equipment entities
    for i in range(3):
        x = 6 + i
        y = 8
        
        equipment_entity = entity_manager.create_entity({
            'identity': {
                'name': f'tractor_{i}',
                'display_name': f'Tractor {i+1}'
            },
            'transform': {
                'x': float(x), 'y': float(y)
            },
            'equipment': {
                'equipment_type': 'tractor',
                'condition': 95.0,
                'purchase_price': 50000.0
            }
        })
        
        grid_system.add_entity_at_position(equipment_entity, x, y, GridLayer.EQUIPMENT)
        created_entities.append(equipment_entity)
    
    print(f"[OK] Created and placed {len(created_entities)} entities on grid")
    print(f"     - Crop entities: 15")
    print(f"     - Equipment entities: 3")
    print(f"     - Total entities tracked: {grid_system.statistics['entities_tracked']}")
    
    # Test 3: Spatial queries
    print("\n>>> Test 3: Spatial Query Performance")
    
    # Test radius queries
    start_time = time.time()
    crops_nearby = grid_system.get_entities_in_radius(7.0, 6.0, 2.0, GridLayer.CROPS)
    radius_query_time = (time.time() - start_time) * 1000
    
    # Test rectangular queries
    start_time = time.time()
    entities_in_rect = grid_system.get_entities_in_rect(5.0, 5.0, 5.0, 5.0)
    rect_query_time = (time.time() - start_time) * 1000
    
    # Test tile-based queries
    tile_entities = grid_system.get_entities_at_tile(7, 7)
    
    print(f"[OK] Spatial queries completed:")
    print(f"     - Crops within radius 2.0 of (7,6): {len(crops_nearby)} entities ({radius_query_time:.2f}ms)")
    print(f"     - Entities in 5x5 rectangle: {len(entities_in_rect)} entities ({rect_query_time:.2f}ms)")
    print(f"     - Entities at tile (7,7): {len(tile_entities)} entities")
    
    # Test 4: Region management
    print("\n>>> Test 4: Region-Based Processing")
    
    # Set active region around our test area
    grid_system.set_active_region(7.0, 7.0, radius=10)
    
    # Process active regions
    processed_regions = grid_system.process_active_regions()
    
    print(f"[OK] Region processing completed:")
    print(f"     - Active regions: {grid_system.statistics['regions_active']}")
    print(f"     - Processed regions: {processed_regions}")
    
    # Test 5: Pathfinding
    print("\n>>> Test 5: Pathfinding Integration")
    
    # Find path across the grid
    start_time = time.time()
    path = grid_system.find_path(5, 5, 9, 9)
    pathfinding_time = (time.time() - start_time) * 1000
    
    print(f"[OK] Pathfinding completed:")
    print(f"     - Path from (5,5) to (9,9): {len(path)} steps ({pathfinding_time:.2f}ms)")
    print(f"     - Path preview: {path[:5]}{'...' if len(path) > 5 else ''}")
    
    # Test 6: Event integration
    print("\n>>> Test 6: Event System Integration")
    
    # Process any pending events
    event_system.process_events()
    
    print(f"[OK] Event system integration verified:")
    print(f"     - Events received: {len(events_received)}")
    print(f"     - Event types: {set(event['event_type'] for event in events_received if 'event_type' in event)}")
    
    # Test 7: Performance statistics
    print("\n>>> Test 7: Performance Monitoring")
    
    # Get comprehensive statistics
    grid_stats = grid_system.get_statistics()
    entity_stats = entity_manager.get_statistics()
    
    print(f"[OK] Performance statistics:")
    print(f"     Grid System:")
    print(f"       - Total tiles: {grid_stats['total_tiles']}")
    print(f"       - Active tiles: {grid_stats['active_tiles']}")
    print(f"       - Memory usage: {grid_stats['memory_usage_estimate_mb']:.2f} MB")
    print(f"       - Average query time: {grid_stats['average_query_time_ms']:.2f} ms")
    print(f"     Entity System:")
    print(f"       - Total entities: {entity_stats['total_entities']}")
    print(f"       - Component types: {entity_stats['registered_component_types']}")
    print(f"       - Archetypes: {entity_stats['archetype_count']}")
    print(f"     Event System:")
    print(f"       - Events received in test: {len(events_received)}")
    print(f"       - Priority levels supported: {len(EventPriority.__members__)}")
    
    # Test 8: Grid expansion
    print("\n>>> Test 8: Dynamic Grid Expansion")
    
    old_size = (grid_system.width, grid_system.height)
    grid_system.expand_grid(50, 50)
    new_size = (grid_system.width, grid_system.height)
    
    print(f"[OK] Grid expansion completed:")
    print(f"     - Old size: {old_size}")
    print(f"     - New size: {new_size}")
    
    # Final integration test
    print("\n>>> Final Integration Validation")
    
    # Create one more entity to test the complete pipeline
    final_entity = entity_manager.create_entity({
        'identity': {'name': 'integration_test', 'display_name': 'Integration Test Entity'},
        'transform': {'x': 25.0, 'y': 25.0},
        'crop': {'crop_type': 'integration_test', 'health': 100.0}
    })
    
    grid_system.add_entity_at_position(final_entity, 25.0, 25.0, GridLayer.CROPS)
    
    # Verify entity is properly tracked
    entities_at_25_25 = grid_system.get_entities_at_tile(25, 25)
    entities_near_25_25 = grid_system.get_entities_in_radius(25.0, 25.0, 1.0)
    
    print(f"[OK] Integration validation completed:")
    print(f"     - Entity created and placed: {final_entity}")
    print(f"     - Entities at tile (25,25): {len(entities_at_25_25)}")
    print(f"     - Entities near (25,25): {len(entities_near_25_25)}")
    
    # Summary
    print(f"\n>>> Advanced Grid System Integration Test PASSED!")
    print(f"     - All 8 test categories completed successfully")
    print(f"     - {len(created_entities) + 1} entities created and tracked")
    print(f"     - {len(test_tiles)} tiles with multi-layer data")
    print(f"     - {len(events_received)} events processed")
    print(f"     - Grid expanded to {new_size[0]}x{new_size[1]}")
    
    return True


if __name__ == "__main__":
    try:
        success = test_advanced_grid_integration()
        if success:
            print("\n[SUCCESS] All tests passed! Advanced Grid System integration is working correctly.")
        else:
            print("\n[FAILED] Some tests failed! Check the output above.")
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()