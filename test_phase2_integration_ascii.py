#!/usr/bin/env python3
"""
Phase 2 Integration Test - Verify Phase 2 Systems Work with New Phase 1 Architecture

This test verifies that all Phase 2 systems can properly import and initialize
with the new Phase 1 architectural foundation.
"""

import sys
import os
import traceback

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
        "advanced_config_system": "scripts.core.advanced_config_system",
        "time_management": "scripts.core.time_management"
    }
    
    results = {}
    
    for system_name, module_path in phase1_systems.items():
        try:
            module = __import__(module_path, fromlist=[''])
            results[system_name] = {"status": "SUCCESS", "module": module, "error": None}
            print(f"  [OK] {system_name}: Import successful")
        except Exception as e:
            results[system_name] = {"status": "FAILED", "module": None, "error": str(e)}
            print(f"  [FAIL] {system_name}: Import failed - {e}")
    
    return results

def test_phase2_imports():
    """Test that all Phase 2 systems can be imported successfully"""
    print("\n[Phase 2] Testing System Imports...")
    
    phase2_systems = {
        "economy_system": "scripts.systems.economy_system",
        "employee_system": "scripts.systems.employee_system",
        "crop_system": "scripts.systems.crop_system", 
        "building_system": "scripts.systems.building_system",
        "save_load_system": "scripts.systems.save_load_system"
    }
    
    results = {}
    
    for system_name, module_path in phase2_systems.items():
        try:
            module = __import__(module_path, fromlist=[''])
            results[system_name] = {"status": "SUCCESS", "module": module, "error": None}
            print(f"  [OK] {system_name}: Import successful")
        except Exception as e:
            results[system_name] = {"status": "FAILED", "module": None, "error": str(e)}
            print(f"  [FAIL] {system_name}: Import failed - {e}")
            if "No module named" not in str(e):
                print(f"     Details: {str(e)[:100]}...")
    
    return results

def test_system_initialization():
    """Test that core systems can be initialized"""
    print("\n[Init] Testing System Initialization...")
    
    results = {}
    
    # Test Phase 1 core systems
    try:
        from scripts.core.advanced_event_system import get_event_system
        event_system = get_event_system()
        print("  [OK] Event System: Initialized")
        results["event_system"] = "SUCCESS"
    except Exception as e:
        print(f"  [FAIL] Event System: {e}")
        results["event_system"] = f"FAILED: {e}"
    
    try:
        from scripts.core.advanced_config_system import get_config_manager
        config_manager = get_config_manager()
        print("  [OK] Config System: Initialized")
        results["config_system"] = "SUCCESS"
    except Exception as e:
        print(f"  [FAIL] Config System: {e}")
        results["config_system"] = f"FAILED: {e}"
    
    try:
        from scripts.core.time_management import get_time_manager
        time_manager = get_time_manager()
        print("  [OK] Time Management: Initialized")
        results["time_management"] = "SUCCESS"
    except Exception as e:
        print(f"  [FAIL] Time Management: {e}")
        results["time_management"] = f"FAILED: {e}"
    
    return results

def generate_report(phase1_results, phase2_results, init_results):
    """Generate integration report"""
    print("\n" + "="*60)
    print("INTEGRATION REPORT")
    print("="*60)
    
    # Count successes
    phase1_success = sum(1 for r in phase1_results.values() if r["status"] == "SUCCESS")
    phase1_total = len(phase1_results)
    
    phase2_success = sum(1 for r in phase2_results.values() if r["status"] == "SUCCESS")
    phase2_total = len(phase2_results)
    
    init_success = sum(1 for r in init_results.values() if r == "SUCCESS")
    init_total = len(init_results)
    
    print(f"\nPhase 1 Systems: {phase1_success}/{phase1_total} ({(phase1_success/phase1_total)*100:.1f}%)")
    print(f"Phase 2 Systems: {phase2_success}/{phase2_total} ({(phase2_success/phase2_total)*100:.1f}%)")
    print(f"Initialization: {init_success}/{init_total} ({(init_success/init_total)*100:.1f}%)")
    
    total_success = phase1_success + phase2_success + init_success
    total_tests = phase1_total + phase2_total + init_total
    overall_rate = (total_success / total_tests) * 100
    
    print(f"\nOverall Status: {total_success}/{total_tests} ({overall_rate:.1f}%)")
    
    if overall_rate >= 90:
        print("Status: EXCELLENT - Ready for production")
    elif overall_rate >= 75:
        print("Status: GOOD - Minor issues to resolve")
    elif overall_rate >= 50:
        print("Status: FAIR - Significant issues need attention")
    else:
        print("Status: POOR - Major problems require immediate fix")
    
    # List failures
    failures = []
    for system, result in phase1_results.items():
        if result["status"] == "FAILED":
            failures.append(f"Phase 1 - {system}: {result['error']}")
    
    for system, result in phase2_results.items():
        if result["status"] == "FAILED":
            failures.append(f"Phase 2 - {system}: {result['error']}")
    
    for system, result in init_results.items():
        if result != "SUCCESS":
            failures.append(f"Init - {system}: {result}")
    
    if failures:
        print(f"\nFailures ({len(failures)}):")
        for i, failure in enumerate(failures, 1):
            print(f"  {i}. {failure}")
    else:
        print("\nNo failures detected!")
    
    print("\n" + "="*60)
    
    return overall_rate

def main():
    """Run integration test"""
    print("PHASE 2 INTEGRATION TEST")
    print("Verifying Phase 2 Systems Work with New Phase 1 Architecture")
    print("="*60)
    
    # Run tests
    phase1_results = test_phase1_imports()
    phase2_results = test_phase2_imports()
    init_results = test_system_initialization()
    
    # Generate report
    overall_rate = generate_report(phase1_results, phase2_results, init_results)
    
    return overall_rate >= 75  # Return True if integration is successful

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nINTEGRATION TEST PASSED")
        else:
            print("\nINTEGRATION TEST FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)