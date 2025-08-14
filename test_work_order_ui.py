#!/usr/bin/env python3
"""
Quick test to see if work orders are showing up in UI
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

import pygame
import pygame_gui
from scripts.core.config import *
from scripts.core.event_system import EventSystem
from scripts.core.grid_manager import GridManager
from scripts.employee.employee_manager import EmployeeManager
from scripts.tasks.task_integration import TaskSystemIntegration
from scripts.ui.task_assignment_modal import TaskAssignmentModal

def test_work_order_ui_connection():
    """Test if work orders flow from creation to UI display"""
    print("=== TESTING WORK ORDER UI CONNECTION ===")
    
    # Initialize minimal systems
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    gui_manager = pygame_gui.UIManager((800, 600))
    
    event_system = EventSystem()
    grid_manager = GridManager(event_system)
    employee_manager = EmployeeManager(event_system, grid_manager)
    task_integration = TaskSystemIntegration(event_system, grid_manager, employee_manager)
    task_modal = TaskAssignmentModal(gui_manager, event_system, 800, 600)
    
    # Connect task integration to modal (simulate game manager connection)
    task_modal.set_task_integration(task_integration)
    
    print(f"1. Systems initialized")
    print(f"   Work order manager exists: {task_integration.work_order_manager is not None}")
    print(f"   Active orders: {len(task_integration.work_order_manager.active_orders) if task_integration.work_order_manager else 'None'}")
    
    # Create a test work order directly
    if task_integration.work_order_manager:
        from scripts.tasks.task_models import TaskType, TaskPriority
        
        test_plots = [(5, 5), (5, 6), (6, 5)]
        work_order = task_integration.work_order_manager.create_work_order(
            task_type=TaskType.TILLING,
            plots=test_plots,
            priority=TaskPriority.NORMAL,
            notes="Test work order for UI",
            auto_assign=False
        )
        
        print(f"2. Created test work order: {work_order.id if work_order else 'Failed'}")
        print(f"   Active orders after creation: {len(task_integration.work_order_manager.active_orders)}")
    
    # Test UI data retrieval
    work_orders_from_ui = task_modal._get_work_orders_data()
    print(f"3. UI retrieved work orders: {len(work_orders_from_ui)}")
    
    if work_orders_from_ui:
        for order in work_orders_from_ui:
            print(f"   - {order}")
    else:
        print("   No work orders retrieved by UI!")
    
    # Test direct access
    work_orders_direct = task_integration.get_active_work_orders()
    print(f"4. Direct access work orders: {len(work_orders_direct)}")
    
    if work_orders_direct:
        for order in work_orders_direct:
            print(f"   - {order}")
    
    # Cleanup
    pygame.quit()
    print("=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_work_order_ui_connection()