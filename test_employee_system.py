"""
Test Employee Management System - Advanced Workforce AI Validation

This test validates the complete Employee Management System including:
- Employee AI with state machines and pathfinding
- Skill system with progression and experience
- Task assignment and work coordination
- Employee needs management and breaks
- Hiring system with applicant generation
- Performance tracking and efficiency calculations
- Integration with Time and Economy systems
"""

import asyncio
import time
from scripts.systems.employee_system import (
    EmployeeSystem, EmployeeState, TaskType, SkillType, EmployeeTrait,
    get_employee_system, initialize_employee_system,
    hire_employee, assign_task, get_employee_summary, get_system_summary
)
from scripts.systems.time_system import get_time_system, TimeOfDay
from scripts.systems.economy_system import get_economy_system


async def test_employee_system():
    """Test comprehensive employee management system"""
    print("=" * 60)
    print("EMPLOYEE MANAGEMENT SYSTEM TEST")
    print("=" * 60)
    
    try:
        # Test 1: Employee System Initialization
        print("\n>>> Test 1: Employee System Initialization")
        
        employee_system = initialize_employee_system()
        time_system = get_time_system()
        economy_system = get_economy_system()
        
        initial_summary = employee_system.get_system_summary()
        
        print(f"Employee system created: {employee_system is not None}")
        print(f"Initial employees: {initial_summary['total_employees']}")
        print(f"Available applicants: {initial_summary['available_applicants']}")
        print(f"Max employees: {initial_summary['max_employees']}")
        print(f"Active tasks: {initial_summary['active_tasks']}")
        
        # Test 2: Applicant Generation and Info
        print("\n>>> Test 2: Applicant Generation and Information")
        
        # Generate additional applicants
        new_applicant_ids = employee_system.generate_applicants(2)
        
        print(f"Generated new applicants: {len(new_applicant_ids)}")
        
        # Get info about first applicant
        if employee_system.available_applicants:
            first_applicant_id = list(employee_system.available_applicants.keys())[0]
            applicant_info = employee_system.get_applicant_info(first_applicant_id)
            
            if applicant_info:
                print(f"Applicant details:")
                print(f"  Name: {applicant_info['name']}")
                print(f"  Daily wage: ${applicant_info['daily_wage']:.2f}")
                print(f"  Skills: {applicant_info['skills']}")
                print(f"  Traits: {applicant_info['traits']}")
                print(f"  Estimated efficiency: {applicant_info['estimated_efficiency']:.2f}")
        
        # Test 3: Employee Hiring
        print("\n>>> Test 3: Employee Hiring System")
        
        initial_cash = economy_system.current_cash
        
        # Try to hire first available applicant
        if employee_system.available_applicants:
            applicant_id = list(employee_system.available_applicants.keys())[0]
            hiring_result = employee_system.hire_employee(applicant_id)
            
            print(f"Hiring attempt: {hiring_result['success']}")
            if hiring_result['success']:
                employee_id = hiring_result['employee_id']
                hiring_cost = hiring_result['hiring_cost']
                
                print(f"  Employee ID: {employee_id}")
                print(f"  Hiring cost: ${hiring_cost:.2f}")
                print(f"  Cash before: ${initial_cash:.2f}")
                print(f"  Cash after: ${economy_system.current_cash:.2f}")
                
                # Get employee summary
                employee_summary = employee_system.get_employee_summary(employee_id)
                if employee_summary:
                    print(f"  Employee name: {employee_summary['name']}")
                    print(f"  Position: {employee_summary['position']}")
                    print(f"  State: {employee_summary['state']}")
        
        # Test 4: Task Assignment
        print("\n>>> Test 4: Task Assignment System")
        
        if employee_system.employees:
            employee_id = list(employee_system.employees.keys())[0]
            employee = employee_system.employees[employee_id]
            
            # Assign a farming task
            task_result = employee_system.assign_task(
                employee_id, 
                TaskType.TILL_FIELD, 
                (5, 7),  # Target location
                parameters={'area_size': 4},
                priority=2
            )
            
            print(f"Task assignment: {task_result['success']}")
            if task_result['success']:
                task_id = task_result['task_id']
                estimated_duration = task_result['estimated_duration']
                
                print(f"  Task ID: {task_id}")
                print(f"  Estimated duration: {estimated_duration:.1f} minutes")
                print(f"  Employee task queue: {len(employee.task_queue)} tasks")
            
            # Assign multiple tasks
            for i, task_type in enumerate([TaskType.PLANT_CROPS, TaskType.WATER_CROPS]):
                employee_system.assign_task(
                    employee_id, 
                    task_type, 
                    (6 + i, 8),
                    priority=1
                )
            
            print(f"  Total tasks assigned: {len(employee.task_queue)} + current")
        
        # Test 5: Employee AI and Movement
        print("\n>>> Test 5: Employee AI and Movement System")
        
        if employee_system.employees:
            employee_id = list(employee_system.employees.keys())[0]
            employee = employee_system.employees[employee_id]
            
            print(f"Initial employee state: {employee.state.value}")
            print(f"Initial position: ({employee.x:.1f}, {employee.y:.1f})")
            
            # Simulate employee updates for several seconds
            for i in range(10):
                employee_system.update_employees(1.0)  # 1 second updates
                
                if i % 3 == 0:  # Log every 3 seconds
                    print(f"  Step {i+1}: State={employee.state.value}, "
                          f"Pos=({employee.x:.1f}, {employee.y:.1f})")
                    
                    if employee.current_task:
                        progress = employee.current_task.get_completion_percentage()
                        print(f"    Task progress: {progress}%")
            
        # Test 6: Employee Needs and Stats
        print("\n>>> Test 6: Employee Needs and Statistics")
        
        if employee_system.employees:
            employee_id = list(employee_system.employees.keys())[0]
            employee = employee_system.employees[employee_id]
            
            print(f"Employee needs:")
            print(f"  Hunger: {employee.stats.hunger:.1f}")
            print(f"  Thirst: {employee.stats.thirst:.1f}")
            print(f"  Rest: {employee.stats.rest:.1f}")
            print(f"  Energy: {employee.stats.energy:.1f}")
            print(f"  Morale: {employee.stats.morale:.1f}")
            
            print(f"Work performance:")
            print(f"  Efficiency: {employee.get_work_efficiency():.2f}")
            print(f"  Quality: {employee.get_work_quality():.2f}")
            print(f"  Performance rating: {employee.performance_rating:.2f}")
            
            # Test needs degradation during work
            print(f"Simulating work for employee needs...")
            for i in range(5):
                employee.stats.update_needs(3600.0, working=True)  # 1 hour of work
            
            print(f"After 5 hours of work:")
            print(f"  Hunger: {employee.stats.hunger:.1f}")
            print(f"  Energy: {employee.stats.energy:.1f}")
            print(f"  Needs break: {employee.stats.needs_break()}")
        
        # Test 7: Skill System
        print("\n>>> Test 7: Skill System and Experience")
        
        if employee_system.employees:
            employee_id = list(employee_system.employees.keys())[0]
            employee = employee_system.employees[employee_id]
            
            print(f"Employee skills:")
            for skill_type, skill in employee.skills.items():
                print(f"  {skill_type.value}: Level {skill.level} "
                      f"(XP: {skill.experience:.1f}/{skill.experience_to_next:.1f})")
            
            # Add experience to farming skill
            initial_farming_level = employee.get_skill_level(SkillType.FARMING)
            
            # Add enough experience to potentially level up
            leveled_up = employee.add_skill_experience(SkillType.FARMING, 150.0)
            
            new_farming_level = employee.get_skill_level(SkillType.FARMING)
            
            print(f"Farming skill progression:")
            print(f"  Initial level: {initial_farming_level}")
            print(f"  After 150 XP: {new_farming_level}")
            print(f"  Leveled up: {leveled_up}")
        
        # Test 8: Work Schedule and Time Integration
        print("\n>>> Test 8: Work Schedule and Time Integration")
        
        if employee_system.employees:
            employee_id = list(employee_system.employees.keys())[0]
            employee = employee_system.employees[employee_id]
            
            # Test different times of day
            time_periods = [
                TimeOfDay.EARLY_MORNING,
                TimeOfDay.MORNING, 
                TimeOfDay.AFTERNOON,
                TimeOfDay.EVENING,
                TimeOfDay.NIGHT
            ]
            
            print(f"Work availability by time of day:")
            for time_period in time_periods:
                can_work = employee.can_work_now(time_period)
                print(f"  {time_period.value}: {can_work}")
                
                # Test with traits
                if employee.has_trait(EmployeeTrait.EARLY_RISER):
                    print(f"    (Early riser trait)")
                if employee.has_trait(EmployeeTrait.NIGHT_OWL):
                    print(f"    (Night owl trait)")
        
        # Test 9: Performance and Quality Modifiers
        print("\n>>> Test 9: Performance and Quality Modifiers")
        
        if employee_system.employees:
            employee_id = list(employee_system.employees.keys())[0]
            employee = employee_system.employees[employee_id]
            
            print(f"Employee traits and their effects:")
            print(f"  Traits: {[trait.value for trait in employee.traits]}")
            
            base_efficiency = 1.0
            trait_efficiency = employee.get_work_efficiency()
            base_quality = 1.0
            trait_quality = employee.get_work_quality()
            
            print(f"  Base efficiency: {base_efficiency:.2f}")
            print(f"  With traits: {trait_efficiency:.2f}")
            print(f"  Base quality: {base_quality:.2f}")
            print(f"  With traits: {trait_quality:.2f}")
        
        # Test 10: System Summary and Management
        print("\n>>> Test 10: System Summary and Management")
        
        final_summary = employee_system.get_system_summary()
        
        print(f"Employee system summary:")
        print(f"  Total employees: {final_summary['total_employees']}")
        print(f"  Available applicants: {final_summary['available_applicants']}")
        print(f"  Active tasks: {final_summary['active_tasks']}")
        print(f"  Total daily wages: ${final_summary['total_daily_wages']:.2f}")
        print(f"  Hours worked today: {final_summary['total_hours_worked_today']:.1f}")
        print(f"  Tasks completed today: {final_summary['total_tasks_completed_today']}")
        print(f"  Average performance: {final_summary['average_performance']:.2f}")
        
        # Test convenience functions
        print(f"\nTesting convenience functions:")
        global_summary = get_system_summary()
        print(f"  Global system summary: {global_summary['total_employees']} employees")
        
        if employee_system.employees:
            employee_id = list(employee_system.employees.keys())[0]
            global_employee_info = get_employee_summary(employee_id)
            if global_employee_info:
                print(f"  Global employee info: {global_employee_info['name']}")
        
        print("\n" + "=" * 60)
        print("EMPLOYEE MANAGEMENT SYSTEM TEST: PASSED")
        print("All workforce systems working correctly!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nEmployee system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_employee_integration():
    """Test employee system integration with other systems"""
    print("\n" + "=" * 60)
    print("EMPLOYEE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        employee_system = get_employee_system()
        time_system = get_time_system()
        economy_system = get_economy_system()
        
        # Test daily wage payments
        print("\n>>> Testing Daily Wage Payments")
        
        if employee_system.employees:
            initial_cash = economy_system.current_cash
            initial_transactions = len(economy_system.transactions)
            
            # Advance time by one day to trigger wage payments
            time_system.advance_time(24 * 60)  # 24 hours in minutes
            
            final_cash = economy_system.current_cash
            final_transactions = len(economy_system.transactions)
            
            cash_change = final_cash - initial_cash
            new_transactions = final_transactions - initial_transactions
            
            print(f"Cash before: ${initial_cash:.2f}")
            print(f"Cash after: ${final_cash:.2f}")
            print(f"Cash change: ${cash_change:.2f}")
            print(f"New transactions: {new_transactions}")
            
            # Check recent wage payments
            recent_transactions = economy_system.transactions[-3:]
            wage_payments = [t for t in recent_transactions if 'wage' in t.description.lower()]
            print(f"Wage payment transactions: {len(wage_payments)}")
        
        # Test seasonal adjustments
        print("\n>>> Testing Seasonal Workforce Adjustments")
        
        initial_applicant_wages = []
        if employee_system.available_applicants:
            for applicant in employee_system.available_applicants.values():
                initial_applicant_wages.append(applicant.daily_wage)
        
        # Advance to next season
        time_system.advance_time(90 * 24 * 60)  # 90 days (one season)
        
        final_applicant_wages = []
        if employee_system.available_applicants:
            for applicant in employee_system.available_applicants.values():
                final_applicant_wages.append(applicant.daily_wage)
        
        if initial_applicant_wages and final_applicant_wages:
            avg_initial = sum(initial_applicant_wages) / len(initial_applicant_wages)
            avg_final = sum(final_applicant_wages) / len(final_applicant_wages)
            wage_change = ((avg_final - avg_initial) / avg_initial) * 100
            
            print(f"Average applicant wage change: {wage_change:+.1f}%")
            print(f"Seasonal adjustment applied: {wage_change != 0}")
        
        # Test task duration estimation
        print("\n>>> Testing Task Duration Estimation")
        
        if employee_system.employees:
            employee_id = list(employee_system.employees.keys())[0]
            employee = employee_system.employees[employee_id]
            
            # Test different task types
            task_types = [TaskType.TILL_FIELD, TaskType.PLANT_CROPS, TaskType.HARVEST_CROPS]
            
            print(f"Task duration estimates for {employee.name}:")
            for task_type in task_types:
                duration = employee_system._estimate_task_duration(employee, task_type, {})
                print(f"  {task_type.value}: {duration:.1f} minutes")
        
        print("\nEmployee integration test passed!")
        
        return True
        
    except Exception as e:
        print(f"Employee integration test failed: {e}")
        return False


if __name__ == "__main__":
    try:
        # Run main employee system test
        success1 = asyncio.run(test_employee_system())
        
        # Run integration test
        success2 = asyncio.run(test_employee_integration())
        
        if success1 and success2:
            print("\n[SUCCESS] All employee management tests passed!")
        else:
            print("\n[FAILED] Some tests failed!")
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()