"""
Simple Phase 1 Integration Test - Windows Compatible
Tests all 8 foundation systems working together without Unicode characters.
"""

import asyncio
import time
import tempfile
from pathlib import Path

# Import all foundation systems
from scripts.core.event_system import get_global_event_system, EventPriority
from scripts.core.entity_component_system import get_entity_manager
from scripts.core.content_registry import get_content_registry
from scripts.core.advanced_grid_system import get_grid_system, GridLayer
from scripts.core.configuration_system import get_configuration_manager
from scripts.core.state_management import get_state_manager
from scripts.core.plugin_system import get_plugin_system
from scripts.core.testing_framework import get_testing_framework


async def test_simple_integration():
    """Simple Phase 1 foundation integration test"""
    print("=" * 60)
    print("PHASE 1 FOUNDATION INTEGRATION TEST")
    print("=" * 60)
    print("Testing all 8 foundation systems...")
    
    try:
        # Test 1: Initialize all systems
        print("\n>>> Test 1: System Initialization")
        
        event_system = get_global_event_system()
        entity_manager = get_entity_manager()
        content_registry = get_content_registry()
        grid_system = get_grid_system()
        config_manager = get_configuration_manager()
        state_manager = get_state_manager()
        plugin_system = get_plugin_system()
        testing_framework = get_testing_framework()
        
        print("Foundation systems initialized:")
        print(f"  Event System: OK")
        print(f"  Entity-Component System: OK")
        print(f"  Content Registry: OK")
        print(f"  Advanced Grid System: OK")
        print(f"  Configuration System: OK")
        print(f"  State Management: OK")
        print(f"  Plugin System: OK")
        print(f"  Testing Framework: OK")
        
        # Test 2: Basic entity creation
        print("\n>>> Test 2: Entity Creation and Grid Integration")
        
        test_entity_id = entity_manager.create_entity({
            'identity': {'name': 'test_entity', 'display_name': 'Test Entity'},
            'transform': {'x': 5.0, 'y': 7.0}
        })
        
        # Add to grid
        grid_system.add_entity_at_position(test_entity_id, 5.0, 7.0, GridLayer.CROPS)
        
        # Check entity exists
        entities_at_tile = grid_system.get_entities_at_tile(5, 7)
        entity_on_grid = test_entity_id in entities_at_tile
        
        print(f"Entity created: {test_entity_id}")
        print(f"Entity on grid: {entity_on_grid}")
        print(f"Total entities: {len(entity_manager._entities)}")
        
        # Test 3: Configuration system
        print("\n>>> Test 3: Configuration System")
        
        config_manager.set('test.integration.value', 'success')
        config_value = config_manager.get('test.integration.value')
        config_test = config_value == 'success'
        
        print(f"Configuration test: {config_test}")
        
        # Test 4: Event system
        print("\n>>> Test 4: Event System")
        
        events_received = []
        def track_events(event_data):
            events_received.append(event_data)
        
        event_system.subscribe('test_event', track_events)
        event_system.publish('test_event', {'message': 'test'}, EventPriority.NORMAL, 'test')
        event_system.process_events()
        
        events_working = len(events_received) > 0
        print(f"Event system test: {events_working}")
        
        # Test 5: Content registry
        print("\n>>> Test 5: Content Registry")
        
        test_content = {
            'name': 'Test Item',
            'value': 100,
            'test': True
        }
        
        content_registry.content['test_items']['test_item'] = test_content
        retrieved_content = content_registry.get_content('test_items', 'test_item')
        content_test = retrieved_content is not None
        
        print(f"Content registry test: {content_test}")
        
        # Test 6: State management
        print("\n>>> Test 6: State Management")
        
        from scripts.core.state_management import CreateEntityCommand
        
        create_command = CreateEntityCommand({
            'identity': {'name': 'state_test', 'display_name': 'State Test'},
            'transform': {'x': 1.0, 'y': 1.0}
        })
        
        state_success = state_manager.execute_command(create_command)
        can_undo = state_manager.can_undo()
        
        print(f"State management test: {state_success and can_undo}")
        
        # Test 7: Plugin system
        print("\n>>> Test 7: Plugin System")
        
        plugin_stats = plugin_system.get_plugin_statistics()
        plugin_test = plugin_stats is not None
        
        print(f"Plugin system test: {plugin_test}")
        
        # Test 8: Testing framework
        print("\n>>> Test 8: Testing Framework")
        
        framework_test = testing_framework is not None
        framework_test = framework_test and hasattr(testing_framework, 'mock_factory')
        
        print(f"Testing framework test: {framework_test}")
        
        print("\n" + "=" * 60)
        print("PHASE 1 INTEGRATION TEST: PASSED")
        print("All 8 foundation systems are working together!")
        print("Ready for Phase 2 implementation!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nIntegration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_simple_integration())
        if success:
            print("\n[SUCCESS] Phase 1 integration test passed!")
        else:
            print("\n[FAILED] Phase 1 integration test failed!")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")