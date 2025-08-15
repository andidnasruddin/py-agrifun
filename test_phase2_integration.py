#!/usr/bin/env python3
"""
Phase 2 Integration Test - Verify Phase 2 Systems Work with New Phase 1 Architecture

This test verifies that all Phase 2 systems can properly import and initialize
with the new Phase 1 architectural foundation. It checks for import conflicts,
initialization errors, and basic system functionality.

Phase 1 Systems (Foundation):
- Advanced Event System
- Entity-Component System  
- Content Registry
- Advanced Grid System
- Plugin System
- State Management
- Configuration System
- Testing Framework

Phase 2 Systems (Core Game Systems):
- Time Management System
- Economy & Market System
- Employee Management System
- Crop Growth & Agricultural Systems
- Building & Infrastructure System
- Save/Load System

This test ensures seamless integration between Phase 1 and Phase 2 systems.
"""

import sys
import os
import traceback
from typing import Dict, List, Any, Optional

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_phase1_imports():
    """Test that all Phase 1 systems can be imported successfully"""
    print("[Phase 1] Testing System Imports...")
    
    phase1_systems = {
        "advanced_event_system": "scripts.core.advanced_event_system",
        "entity_component_system": "scripts.core.entity_component_system", 
        "content_registry": "scripts.core.content_registry",
        "advanced_grid_system": "scripts.core.advanced_grid_system",
        "plugin_system": "scripts.core.plugin_system",
        "state_management": "scripts.core.state_management",
        "advanced_config_system": "scripts.core.advanced_config_system",
        "testing_framework": "scripts.core.testing_framework",
        "time_management": "scripts.core.time_management"
    }
    
    results = {}
    
    for system_name, module_path in phase1_systems.items():
        try:
            module = __import__(module_path, fromlist=[''])
            results[system_name] = {
                "status": "SUCCESS",
                "module": module,
                "error": None
            }
            print(f"  ✅ {system_name}: Import successful")
        except Exception as e:
            results[system_name] = {
                "status": "FAILED", 
                "module": None,
                "error": str(e)
            }
            print(f"  ❌ {system_name}: Import failed - {e}")
    
    return results

def test_phase2_imports():
    """Test that all Phase 2 systems can be imported successfully"""
    print("\n🎮 Testing Phase 2 System Imports...")
    
    phase2_systems = {
        "economy_system": "scripts.systems.economy_system",
        "employee_system": "scripts.systems.employee_system",
        "crop_system": "scripts.systems.crop_system", 
        "building_system": "scripts.systems.building_system",
        "save_load_system": "scripts.systems.save_load_system",
        "temporal_system": "scripts.systems.temporal_system"
    }
    
    results = {}
    
    for system_name, module_path in phase2_systems.items():
        try:
            module = __import__(module_path, fromlist=[''])
            results[system_name] = {
                "status": "SUCCESS",
                "module": module,
                "error": None  
            }
            print(f"  ✅ {system_name}: Import successful")
        except Exception as e:
            results[system_name] = {
                "status": "FAILED",
                "module": None,
                "error": str(e)
            }
            print(f"  ❌ {system_name}: Import failed - {e}")
            print(f"     Error details: {traceback.format_exc()}")
    
    return results

def test_phase3_imports():
    """Test that completed Phase 3 systems can be imported successfully"""
    print("\n🌾 Testing Phase 3 System Imports...")
    
    phase3_systems = {
        "multicrop_framework": "scripts.systems.multicrop_framework",
        "advanced_growth_system": "scripts.systems.advanced_growth_system",
        "soil_health_system": "scripts.systems.soil_health_system"
    }
    
    results = {}
    
    for system_name, module_path in phase3_systems.items():
        try:
            module = __import__(module_path, fromlist=[''])
            results[system_name] = {
                "status": "SUCCESS",
                "module": module,
                "error": None
            }
            print(f"  ✅ {system_name}: Import successful")
        except Exception as e:
            results[system_name] = {
                "status": "FAILED",
                "module": None,
                "error": str(e)
            }
            print(f"  ❌ {system_name}: Import failed - {e}")
            print(f"     Error details: {traceback.format_exc()}")
    
    return results

def test_system_initialization(import_results: Dict[str, Any]):
    """Test that systems can be initialized properly"""
    print("\n🔧 Testing System Initialization...")
    
    initialization_results = {}
    
    # Test Phase 1 system initialization
    print("  Phase 1 System Initialization:")
    
    # Try to get global system instances
    try:
        from scripts.core.advanced_event_system import get_event_system
        event_system = get_event_system()
        print(f"    ✅ Event System: Initialized successfully")
        initialization_results["event_system"] = "SUCCESS"
    except Exception as e:
        print(f"    ❌ Event System: Failed to initialize - {e}")
        initialization_results["event_system"] = f"FAILED: {e}"
    
    try:
        from scripts.core.entity_component_system import get_entity_manager
        entity_manager = get_entity_manager()
        print(f"    ✅ Entity Component System: Initialized successfully")
        initialization_results["entity_system"] = "SUCCESS"
    except Exception as e:
        print(f"    ❌ Entity Component System: Failed to initialize - {e}")
        initialization_results["entity_system"] = f"FAILED: {e}"
    
    try:
        from scripts.core.content_registry import get_content_registry
        content_registry = get_content_registry()
        print(f"    ✅ Content Registry: Initialized successfully")
        initialization_results["content_registry"] = "SUCCESS"
    except Exception as e:
        print(f"    ❌ Content Registry: Failed to initialize - {e}")
        initialization_results["content_registry"] = f"FAILED: {e}"
    
    try:
        from scripts.core.advanced_config_system import get_config_manager
        config_manager = get_config_manager()
        print(f"    ✅ Configuration System: Initialized successfully")
        initialization_results["config_system"] = "SUCCESS"
    except Exception as e:
        print(f"    ❌ Configuration System: Failed to initialize - {e}")
        initialization_results["config_system"] = f"FAILED: {e}"
    
    try:
        from scripts.core.time_management import get_time_manager
        time_manager = get_time_manager()
        print(f"    ✅ Time Management: Initialized successfully")
        initialization_results["time_management"] = "SUCCESS"
    except Exception as e:
        print(f"    ❌ Time Management: Failed to initialize - {e}")
        initialization_results["time_management"] = f"FAILED: {e}"
    
    # Test Phase 2 system class instantiation
    print("\n  Phase 2 System Class Instantiation:")
    
    if "economy_system" in import_results and import_results["economy_system"]["status"] == "SUCCESS":
        try:
            module = import_results["economy_system"]["module"]
            economy_system = module.EconomySystem()
            print(f"    ✅ Economy System: Class instantiated successfully")
            initialization_results["economy_system_class"] = "SUCCESS"
        except Exception as e:
            print(f"    ❌ Economy System: Class instantiation failed - {e}")
            initialization_results["economy_system_class"] = f"FAILED: {e}"
    
    if "employee_system" in import_results and import_results["employee_system"]["status"] == "SUCCESS":
        try:
            module = import_results["employee_system"]["module"]
            employee_system = module.EmployeeSystem()
            print(f"    ✅ Employee System: Class instantiated successfully")
            initialization_results["employee_system_class"] = "SUCCESS"
        except Exception as e:
            print(f"    ❌ Employee System: Class instantiation failed - {e}")
            initialization_results["employee_system_class"] = f"FAILED: {e}"
    
    if "crop_system" in import_results and import_results["crop_system"]["status"] == "SUCCESS":
        try:
            module = import_results["crop_system"]["module"] 
            crop_system = module.CropSystem()
            print(f"    ✅ Crop System: Class instantiated successfully")
            initialization_results["crop_system_class"] = "SUCCESS"
        except Exception as e:
            print(f"    ❌ Crop System: Class instantiation failed - {e}")
            initialization_results["crop_system_class"] = f"FAILED: {e}"
    
    if "building_system" in import_results and import_results["building_system"]["status"] == "SUCCESS":
        try:
            module = import_results["building_system"]["module"]
            building_system = module.BuildingSystem() 
            print(f"    ✅ Building System: Class instantiated successfully")
            initialization_results["building_system_class"] = "SUCCESS"
        except Exception as e:
            print(f"    ❌ Building System: Class instantiation failed - {e}")
            initialization_results["building_system_class"] = f"FAILED: {e}"
    
    return initialization_results

def test_system_integration():
    """Test basic system integration functionality"""
    print("\n🔗 Testing System Integration...")
    
    integration_results = {}
    
    try:
        # Test event system can publish/subscribe
        from scripts.core.advanced_event_system import get_event_system
        event_system = get_event_system()
        
        test_event_received = False
        def test_handler(event_data):
            nonlocal test_event_received
            test_event_received = True
        
        event_system.subscribe("test_event", test_handler)
        event_system.publish("test_event", {"test": "data"})
        
        if test_event_received:
            print("  ✅ Event System: Publish/subscribe working")
            integration_results["event_pub_sub"] = "SUCCESS"
        else:
            print("  ❌ Event System: Publish/subscribe not working")
            integration_results["event_pub_sub"] = "FAILED"
    
    except Exception as e:
        print(f"  ❌ Event System Integration: Failed - {e}")
        integration_results["event_pub_sub"] = f"FAILED: {e}"
    
    try:
        # Test entity system can create entities
        from scripts.core.entity_component_system import get_entity_manager
        entity_manager = get_entity_manager()
        
        entity_id = entity_manager.create_entity()
        if entity_id:
            print("  ✅ Entity System: Entity creation working")
            integration_results["entity_creation"] = "SUCCESS"
        else:
            print("  ❌ Entity System: Entity creation failed")
            integration_results["entity_creation"] = "FAILED"
    
    except Exception as e:
        print(f"  ❌ Entity System Integration: Failed - {e}")
        integration_results["entity_creation"] = f"FAILED: {e}"
    
    try:
        # Test time system basic functionality
        from scripts.core.time_management import get_time_manager
        time_manager = get_time_manager()
        
        current_time = time_manager.get_current_time()
        if current_time:
            print("  ✅ Time System: Time retrieval working")
            integration_results["time_retrieval"] = "SUCCESS"
        else:
            print("  ❌ Time System: Time retrieval failed")
            integration_results["time_retrieval"] = "FAILED"
    
    except Exception as e:
        print(f"  ❌ Time System Integration: Failed - {e}")
        integration_results["time_retrieval"] = f"FAILED: {e}"
    
    return integration_results

def generate_integration_report(phase1_results: Dict, phase2_results: Dict, phase3_results: Dict,
                               init_results: Dict, integration_results: Dict):
    """Generate comprehensive integration report"""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE INTEGRATION REPORT")
    print("="*80)
    
    # Count successes and failures
    phase1_success = sum(1 for r in phase1_results.values() if r["status"] == "SUCCESS")
    phase1_total = len(phase1_results)
    
    phase2_success = sum(1 for r in phase2_results.values() if r["status"] == "SUCCESS") 
    phase2_total = len(phase2_results)
    
    phase3_success = sum(1 for r in phase3_results.values() if r["status"] == "SUCCESS")
    phase3_total = len(phase3_results)
    
    init_success = sum(1 for r in init_results.values() if r == "SUCCESS")
    init_total = len(init_results)
    
    integration_success = sum(1 for r in integration_results.values() if r == "SUCCESS")
    integration_total = len(integration_results)
    
    print(f"\n🏗️ PHASE 1 (Architectural Foundation): {phase1_success}/{phase1_total} systems")
    print(f"   Success Rate: {(phase1_success/phase1_total)*100:.1f}%")
    
    print(f"\n🎮 PHASE 2 (Core Game Systems): {phase2_success}/{phase2_total} systems")
    print(f"   Success Rate: {(phase2_success/phase2_total)*100:.1f}%")
    
    print(f"\n🌾 PHASE 3 (Agricultural Science): {phase3_success}/{phase3_total} systems")
    print(f"   Success Rate: {(phase3_success/phase3_total)*100:.1f}%")
    
    print(f"\n🔧 SYSTEM INITIALIZATION: {init_success}/{init_total} systems")
    print(f"   Success Rate: {(init_success/init_total)*100:.1f}%")
    
    print(f"\n🔗 SYSTEM INTEGRATION: {integration_success}/{integration_total} tests")
    print(f"   Success Rate: {(integration_success/integration_total)*100:.1f}%")
    
    # Overall status
    total_success = phase1_success + phase2_success + phase3_success + init_success + integration_success
    total_tests = phase1_total + phase2_total + phase3_total + init_total + integration_total
    overall_rate = (total_success / total_tests) * 100
    
    print(f"\n🎯 OVERALL INTEGRATION STATUS: {total_success}/{total_tests} tests passed")
    print(f"   Overall Success Rate: {overall_rate:.1f}%")
    
    if overall_rate >= 90:
        print("   🎉 EXCELLENT - Architecture integration is highly successful!")
    elif overall_rate >= 75:
        print("   ✅ GOOD - Architecture integration is mostly successful with minor issues")
    elif overall_rate >= 50:
        print("   ⚠️  FAIR - Architecture integration has significant issues that need attention")
    else:
        print("   ❌ POOR - Architecture integration has major problems requiring immediate fix")
    
    # Detailed failure analysis
    print(f"\n🔍 DETAILED FAILURE ANALYSIS:")
    
    all_failures = []
    
    for system, result in phase1_results.items():
        if result["status"] == "FAILED":
            all_failures.append(f"Phase 1 - {system}: {result['error']}")
    
    for system, result in phase2_results.items():
        if result["status"] == "FAILED":
            all_failures.append(f"Phase 2 - {system}: {result['error']}")
    
    for system, result in phase3_results.items():
        if result["status"] == "FAILED":
            all_failures.append(f"Phase 3 - {system}: {result['error']}")
    
    for system, result in init_results.items():
        if result != "SUCCESS":
            all_failures.append(f"Initialization - {system}: {result}")
    
    for test, result in integration_results.items():
        if result != "SUCCESS":
            all_failures.append(f"Integration - {test}: {result}")
    
    if all_failures:
        for i, failure in enumerate(all_failures, 1):
            print(f"   {i}. {failure}")
    else:
        print("   No failures detected! 🎉")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if phase2_success < phase2_total:
        print("   - Fix remaining Phase 2 import conflicts")
        print("   - Ensure all Phase 2 systems use correct Phase 1 function names")
    
    if init_success < init_total:
        print("   - Review system initialization dependencies")
        print("   - Check for circular import issues")
    
    if integration_success < integration_total:
        print("   - Test system communication pathways")
        print("   - Verify event system connectivity")
    
    if overall_rate >= 90:
        print("   - Architecture is ready for production use")
        print("   - Continue with remaining Phase 3 systems")
    
    print("\n" + "="*80)

def main():
    """Run comprehensive Phase 2 integration test"""
    print("🧪 PHASE 2 INTEGRATION TEST - Verify Phase 2 Systems Work with New Phase 1 Architecture")
    print("="*80)
    
    # Test Phase 1 imports
    phase1_results = test_phase1_imports()
    
    # Test Phase 2 imports  
    phase2_results = test_phase2_imports()
    
    # Test Phase 3 imports
    phase3_results = test_phase3_imports()
    
    # Test system initialization
    all_import_results = {**phase1_results, **phase2_results, **phase3_results}
    init_results = test_system_initialization(phase2_results)
    
    # Test basic integration
    integration_results = test_system_integration()
    
    # Generate comprehensive report
    generate_integration_report(phase1_results, phase2_results, phase3_results, 
                               init_results, integration_results)
    
    return phase1_results, phase2_results, phase3_results, init_results, integration_results

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during integration testing: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        sys.exit(1)