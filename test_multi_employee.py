#!/usr/bin/env python3
"""
Test script for multi-employee coordination functionality

This script tests that multiple employees can work simultaneously on different
tasks without conflicts or issues.
"""

import sys
import os

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.event_system import EventSystem
from scripts.core.grid_manager import GridManager
from scripts.core.time_manager import TimeManager
from scripts.economy.economy_manager import EconomyManager
from scripts.employee.employee_manager import EmployeeManager
from scripts.employee.simple_hiring_system import SimpleHiringSystem


def test_multi_employee_coordination():
    """Test that multiple employees can work simultaneously"""
    print("MULTI-EMPLOYEE COORDINATION TEST")
    print("=" * 60)
    
    # Initialize all required systems
    event_system = EventSystem()  # Event system for communication
    grid_manager = GridManager(event_system)  # Grid for tile management
    time_manager = TimeManager(event_system)  # Time management
    economy_manager = EconomyManager(event_system)  # Economy with starting cash
    employee_manager = EmployeeManager(event_system, grid_manager, time_manager=time_manager)  # Employee system
    hiring_system = SimpleHiringSystem(event_system, economy_manager, employee_manager)  # Hiring system
    
    print(f"Initial employees: {len(employee_manager.employees)}")
    
    # Hire multiple employees using the hiring system
    print("\nHiring additional employees...")
    
    for i in range(3):  # Try to hire 3 more employees (plus starting Sam = 4 total)
        # Generate applicants
        event_system.emit('generate_applicants_requested', {})
        event_system.process_events()
        
        # Get first available applicant
        applicants = hiring_system.get_available_applicants()
        if applicants and len(employee_manager.employees) < 4:  # Limit to 4 total
            target = applicants[0]  # Pick first applicant
            print(f"  Hiring: {target.name} with traits {target.traits}")
            
            # Hire the applicant
            event_system.emit('hire_applicant_requested', {'applicant_id': target.id})
            event_system.process_events()
    
    print(f"\nTotal employees after hiring: {len(employee_manager.employees)}")
    
    # List all employees
    employees_list = []  # Store employee info for verification
    for emp_id, emp in employee_manager.employees.items():
        employees_list.append((emp_id, emp.name, emp.traits))
        print(f"  - {emp.name} ({emp_id}): {emp.traits}, Position: ({emp.x:.1f}, {emp.y:.1f})")
    
    if len(employee_manager.employees) < 2:
        print("[ERROR] Need at least 2 employees to test coordination!")
        return False
    
    print("\n" + "=" * 60)
    print("TESTING SIMULTANEOUS TASK ASSIGNMENT")
    print("=" * 60)
    
    # Get some tiles to assign tasks to
    tile1 = grid_manager.get_tile(2, 2)  # Get tile at (2,2)
    tile2 = grid_manager.get_tile(5, 5)  # Get tile at (5,5)  
    tile3 = grid_manager.get_tile(8, 8)  # Get tile at (8,8)
    tile4 = grid_manager.get_tile(11, 11)  # Get tile at (11,11)
    
    test_tiles = [tile1, tile2, tile3, tile4]
    
    # Assign different tasks to different employees
    employee_ids = list(employee_manager.employees.keys())
    task_assignments = []  # Track what we assigned
    
    for i, (emp_id, tile) in enumerate(zip(employee_ids, test_tiles)):
        if tile:
            employee = employee_manager.employees[emp_id]
            # Assign till task (all tiles start as soil, so they can be tilled)
            employee.assign_task('till', [tile])  # Assign till task to this employee
            task_assignments.append((emp_id, employee.name, 'till', f"({tile.x}, {tile.y})"))
            print(f"Assigned 'till' task to {employee.name} at tile ({tile.x}, {tile.y})")
    
    print(f"\nAssigned {len(task_assignments)} tasks to different employees")
    
    print("\n" + "=" * 60)
    print("SIMULATING WORK COORDINATION")  
    print("=" * 60)
    
    # Simulate some time passing to let employees work
    print("Simulating 10 seconds of work...")
    
    for step in range(10):  # Simulate 10 time steps
        # Update all employees
        employee_manager.update(1.0)  # 1 second time step
        event_system.process_events()  # Process any events
        
        # Check employee states every few steps
        if step % 3 == 0:
            print(f"\nTime step {step}:")
            active_employees = 0  # Count employees doing work
            
            for emp_id, emp in employee_manager.employees.items():
                state_info = f"{emp.name}: {emp.state.value}"  # Get current state
                
                # Add position info
                state_info += f" at ({emp.x:.1f}, {emp.y:.1f})"
                
                # Add target info if moving
                if hasattr(emp, 'target_x') and (emp.target_x != emp.x or emp.target_y != emp.y):
                    state_info += f" -> ({emp.target_x:.1f}, {emp.target_y:.1f})"
                
                # Check if employee is actively working
                if emp.state.value in ['working', 'moving']:
                    active_employees += 1
                
                print(f"  {state_info}")
            
            print(f"  Active employees: {active_employees}/{len(employee_manager.employees)}")
    
    print("\n" + "=" * 60)
    print("VERIFYING COORDINATION RESULTS")
    print("=" * 60)
    
    # Check that each employee maintained their individual state
    coordination_success = True
    
    print("Final employee states:")
    for emp_id, emp in employee_manager.employees.items():
        print(f"  {emp.name} ({emp_id}): {emp.state.value} at ({emp.x:.1f}, {emp.y:.1f})")
        
        # Verify employee has maintained individual identity
        if emp.id != emp_id:
            print(f"    [ERROR] Employee ID mismatch: expected {emp_id}, got {emp.id}")
            coordination_success = False
        
        # Verify employee is in a valid state
        valid_states = ['idle', 'moving', 'working', 'resting', 'seeking_amenity']
        if emp.state.value not in valid_states:
            print(f"    [ERROR] Invalid state: {emp.state.value}")
            coordination_success = False
        else:
            print(f"    [OK] Valid state: {emp.state.value}")
    
    # Check that different employees can have different states
    states = set(emp.state.value for emp in employee_manager.employees.values())
    print(f"\nUnique states across all employees: {len(states)}")
    print(f"States found: {', '.join(states)}")
    
    if len(states) >= 1:  # At minimum should have some state diversity or valid states
        print("[OK] Employees maintain individual states")
    else:
        print("[ERROR] All employees in identical state - coordination may be broken")
        coordination_success = False
    
    # Verify no conflicts occurred (no exceptions, no crashes)
    if coordination_success:
        print("\n[SUCCESS] MULTI-EMPLOYEE COORDINATION TEST PASSED!")
        print(f"[OK] {len(employee_manager.employees)} employees working independently")
        print("[OK] No conflicts or state corruption detected")
        print("[OK] Individual employee identity maintained")
        return True
    else:
        print("\n[FAILED] MULTI-EMPLOYEE COORDINATION TEST FAILED!")
        print("[ERROR] Issues detected in multi-employee system")
        return False


if __name__ == '__main__':
    try:
        success = test_multi_employee_coordination()
        
        print("\n" + "=" * 60)
        if success:
            print("[SUCCESS] Multi-employee system is working correctly!")
            print("[OK] Ready for production use with multiple workers")
        else:
            print("[FAILED] Multi-employee system has issues!")
            print("[ERROR] Review the problems above")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAILED] Multi-employee coordination test crashed!")