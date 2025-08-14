#!/usr/bin/env python3
"""
Debug Task Assignment System
Shows exactly what's happening when you press T/P/H keys
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.config import *

def show_current_configuration():
    """Show current system configuration"""
    print("=" * 60)
    print("CURRENT TASK SYSTEM CONFIGURATION")
    print("=" * 60)
    
    print(f"ENABLE_ENHANCED_TASK_SYSTEM = {ENABLE_ENHANCED_TASK_SYSTEM}")
    print(f"ENABLE_EMPLOYEE_SPECIALIZATIONS = {ENABLE_EMPLOYEE_SPECIALIZATIONS}")
    print(f"ENABLE_WORK_ORDERS = {ENABLE_WORK_ORDERS}")
    print(f"ENABLE_DYNAMIC_TASK_GENERATION = {ENABLE_DYNAMIC_TASK_GENERATION}")
    
    print("\n" + "=" * 60)
    print("WHAT THIS MEANS:")
    print("=" * 60)
    
    if ENABLE_ENHANCED_TASK_SYSTEM and ENABLE_WORK_ORDERS:
        print("[OK] Work Order System ACTIVE")
        print("  - T/P/H should create work orders")
        print("  - Sam should NOT work immediately")
        print("  - Tasks should appear in Assign interface")
        print("  - You manage assignments manually")
    elif ENABLE_WORK_ORDERS and not ENABLE_ENHANCED_TASK_SYSTEM:
        print("[WARNING] CONFLICT DETECTED!")
        print("  - Both systems are partially active")
        print("  - This causes the problem you're experiencing")
        print("  - Sam works immediately (legacy) + work orders created (new)")
    else:
        print("[OK] Legacy System ACTIVE")
        print("  - T/P/H causes immediate work")
        print("  - Sam starts working right away")
        print("  - No work order management")
    
    print("\n" + "=" * 60)
    print("KEYBOARD SHORTCUT STATUS:")
    print("=" * 60)
    
    # Check if keyboard shortcuts are actually implemented
    try:
        from scripts.ui.ui_manager import UIManager
        print("[OK] UI Manager found")
        
        # Check if there are keyboard event handlers
        import inspect
        ui_methods = inspect.getmembers(UIManager, predicate=inspect.ismethod)
        keyboard_methods = [m for m in ui_methods if 'key' in m[0].lower() or 'keyboard' in m[0].lower()]
        
        if keyboard_methods:
            print(f"[OK] Found {len(keyboard_methods)} keyboard-related methods")
            for method_name, method in keyboard_methods:
                print(f"  - {method_name}")
        else:
            print("[WARNING] NO keyboard event handlers found in UI Manager")
            print("  This means T/P/H shortcuts might not be implemented!")
            
    except Exception as e:
        print(f"[ERROR] Error checking UI Manager: {e}")

def check_event_subscriptions():
    """Check what systems are listening to task events"""
    print("\n" + "=" * 60)
    print("EVENT SYSTEM ANALYSIS:")
    print("=" * 60)
    
    try:
        from scripts.core.event_system import EventSystem
        from scripts.tasks.task_integration import TaskSystemIntegration
        from scripts.employee.employee_manager import EmployeeManager
        
        print("[OK] Event system components found")
        print("\nSystems that handle task assignment:")
        print("- TaskSystemIntegration: listens to 'task_assignment_requested'")
        print("- EmployeeManager: listens to 'task_assigned' (after assignment)")
        print("\nIf T/P/H creates 'task_assignment_requested' events:")
        print("→ TaskSystemIntegration should handle them")
        print("→ Should create work orders when ENABLE_WORK_ORDERS = True")
        
    except Exception as e:
        print(f"[ERROR] Error checking event systems: {e}")

if __name__ == "__main__":
    print("DEBUG: TASK ASSIGNMENT SYSTEM ANALYSIS")
    print("This will help identify why Sam works automatically\n")
    
    show_current_configuration()
    check_event_subscriptions()
    
    print("\n" + "=" * 60)
    print("RECOMMENDED TESTING:")
    print("=" * 60)
    print("1. Launch the game: python main.py")
    print("2. Select some tiles")
    print("3. Press T, P, or H")
    print("4. Watch console output for:")
    print("   - 'task_assignment_requested' events")
    print("   - 'Created work order:' messages")
    print("   - Work order assignment messages")
    print("5. Check Assign interface for work orders")
    print("\nIf Sam works immediately, there's a legacy system bypass!")