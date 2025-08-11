#!/usr/bin/env python3
"""
Quick test script for the hiring system functionality

This script tests the hiring system without launching the full game,
verifying that applicants can be generated and hired properly.
"""

import sys
import os

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.event_system import EventSystem
from scripts.economy.economy_manager import EconomyManager  
from scripts.employee.employee_manager import EmployeeManager
from scripts.employee.simple_hiring_system import SimpleHiringSystem


def test_hiring_system():
    """Test the basic hiring system functionality"""
    print("Testing Simple Hiring System...")
    print("=" * 50)
    
    # Initialize required systems
    event_system = EventSystem()  # Event system for communication
    economy_manager = EconomyManager(event_system)  # Economy system with starting loan
    employee_manager = EmployeeManager(event_system, None, create_starting_employee=True)  # Employee system with Sam
    hiring_system = SimpleHiringSystem(event_system, economy_manager, employee_manager)  # Hiring system
    
    # Check initial state
    print(f"Initial cash: ${economy_manager.get_current_balance():.2f}")
    print(f"Initial employees: {len(employee_manager.employees)}")
    for emp_id, emp in employee_manager.employees.items():
        print(f"  - {emp.name} ({emp_id}) with traits: {emp.traits}")
    
    print("\n" + "=" * 50)
    print("STEP 1: Generate Applicants")
    print("=" * 50)
    
    # Test applicant generation
    event_system.emit('generate_applicants_requested', {})  # Request applicant generation
    event_system.process_events()  # Process the event
    
    # Check available applicants
    applicants = hiring_system.get_available_applicants()
    print(f"Generated {len(applicants)} applicants:")
    for i, applicant in enumerate(applicants, 1):
        print(f"{i}. {applicant.name} (Age {applicant.age})")
        print(f"   Traits: {', '.join(applicant.traits)}")
        print(f"   Cost: ${applicant.hiring_cost}, Daily wage: ${applicant.daily_wage}")
        print(f"   Background: {applicant.previous_job}, {applicant.personality_type}")
        print()
    
    if not applicants:
        print("ERROR: No applicants generated!")
        return False
    
    print("=" * 50)
    print("STEP 2: Test Hiring")
    print("=" * 50)
    
    # Try to hire the first applicant
    target_applicant = applicants[0]
    print(f"Attempting to hire: {target_applicant.name}")
    print(f"Required cost: ${target_applicant.hiring_cost}")
    print(f"Current cash: ${economy_manager.get_current_balance():.2f}")
    
    # Attempt the hire
    event_system.emit('hire_applicant_requested', {'applicant_id': target_applicant.id})
    event_system.process_events()  # Process all hiring events
    
    # Check results
    print(f"\nAfter hiring attempt:")
    print(f"Cash remaining: ${economy_manager.get_current_balance():.2f}")
    print(f"Total employees: {len(employee_manager.employees)}")
    
    new_employee_found = False
    for emp_id, emp in employee_manager.employees.items():
        if emp.name == target_applicant.name:
            new_employee_found = True
            print(f"[OK] Successfully hired: {emp.name} ({emp_id})")
            print(f"   Traits: {emp.traits}")
            print(f"   Daily wage: ${emp.daily_wage}")
        else:
            print(f"   Existing: {emp.name} ({emp_id}) with traits: {emp.traits}")
    
    if new_employee_found:
        print("\n[SUCCESS] HIRING TEST PASSED!")
        remaining_applicants = hiring_system.get_available_applicants()
        print(f"Remaining applicants: {len(remaining_applicants)}")
        return True
    else:
        print("\n[FAILED] HIRING TEST FAILED - Employee not found!")
        return False


def test_insufficient_funds():
    """Test hiring when player doesn't have enough money"""
    print("\n" + "=" * 50)
    print("STEP 3: Test Insufficient Funds")
    print("=" * 50)
    
    # Create systems with very little money
    event_system = EventSystem()
    economy_manager = EconomyManager(event_system)
    
    # Drain most of the money to test insufficient funds scenario
    current_cash = economy_manager.get_current_balance()
    economy_manager.spend_money(current_cash - 50, "Test money drain", "expense")  # Leave only $50
    
    employee_manager = EmployeeManager(event_system, None, create_starting_employee=False)  
    hiring_system = SimpleHiringSystem(event_system, economy_manager, employee_manager)
    
    print(f"Cash available: ${economy_manager.get_current_balance():.2f}")
    
    # Generate applicants 
    event_system.emit('generate_applicants_requested', {})
    event_system.process_events()
    
    applicants = hiring_system.get_available_applicants()
    if applicants:
        expensive_applicant = applicants[0]
        print(f"Attempting to hire: {expensive_applicant.name} for ${expensive_applicant.hiring_cost}")
        
        # This should fail due to insufficient funds
        event_system.emit('hire_applicant_requested', {'applicant_id': expensive_applicant.id})
        event_system.process_events()
        
        print(f"Cash after failed hire: ${economy_manager.get_current_balance():.2f}")
        print(f"Employees after failed hire: {len(employee_manager.employees)}")
        
        if len(employee_manager.employees) == 0:
            print("[SUCCESS] INSUFFICIENT FUNDS TEST PASSED - No hiring occurred!")
            return True
        else:
            print("[FAILED] INSUFFICIENT FUNDS TEST FAILED - Hiring should not have succeeded!")
            return False
    else:
        print("[ERROR] Could not test insufficient funds - no applicants generated")
        return False


if __name__ == '__main__':
    print("HIRING SYSTEM TEST SUITE")
    print("=" * 60)
    
    success = True
    
    # Test 1: Basic hiring functionality
    try:
        success &= test_hiring_system()
    except Exception as e:
        print(f"[ERROR] Basic hiring test failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    # Test 2: Insufficient funds handling
    try:
        success &= test_insufficient_funds()
    except Exception as e:
        print(f"[ERROR] Insufficient funds test failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] ALL HIRING TESTS PASSED!")
        print("[OK] Hiring system is working correctly")
        print("[OK] Multi-employee functionality is ready")
    else:
        print("[FAILED] SOME TESTS FAILED!")
        print("[ERROR] Check the error messages above")
    
    print("=" * 60)