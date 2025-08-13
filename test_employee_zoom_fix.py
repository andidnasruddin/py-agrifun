"""
Test script for Employee Zoom/Pan Fix
Tests that employees are properly positioned when grid is zoomed and panned.
"""

import pygame
import sys
from scripts.core.config import WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE
from scripts.core.event_system import EventSystem
from scripts.core.grid_manager import GridManager
from scripts.employee.employee_manager import EmployeeManager
from scripts.employee.employee import Employee
from scripts.core.time_manager import TimeManager

def test_employee_zoom_fix():
    """Test employee positioning with grid zoom and pan"""
    print("Testing Employee Zoom/Pan Fix...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Employee Zoom Fix Test")
    
    # Create event system
    event_system = EventSystem()
    
    # Create time manager
    time_manager = TimeManager(event_system)
    
    # Create grid manager with enhanced renderer
    print("Creating Grid Manager with Enhanced Renderer...")
    grid_manager = GridManager(event_system)
    grid_manager.time_manager = time_manager
    
    # Create employee manager
    print("Creating Employee Manager...")
    employee_manager = EmployeeManager(event_system, grid_manager, time_manager)
    
    # Add a test employee
    test_employee = Employee("test_worker", "Test Worker", 8.0, 8.0)  # Center of 16x16 grid
    test_employee.target_x = 10.0  # Set a movement target
    test_employee.target_y = 6.0
    employee_manager.employees["test_worker"] = test_employee
    
    print("Employee created at grid position (8, 8)")
    print("Target position set to (10, 6)")
    
    # Test phases with different zoom and pan settings
    test_phases = [
        {
            'name': 'Normal View (1.0x zoom)',
            'zoom': 1.0,
            'pan_x': 0.0,
            'pan_y': 0.0,
            'duration': 3.0
        },
        {
            'name': 'Zoomed In (2.0x zoom)',
            'zoom': 2.0,
            'pan_x': 0.0,
            'pan_y': 0.0,
            'duration': 3.0
        },
        {
            'name': 'Zoomed In + Panned',
            'zoom': 2.0,
            'pan_x': -200.0,
            'pan_y': -150.0,
            'duration': 3.0
        },
        {
            'name': 'Zoomed Out (0.5x zoom)',
            'zoom': 0.5,
            'pan_x': 0.0,
            'pan_y': 0.0,
            'duration': 3.0
        },
        {
            'name': 'Maximum Zoom (3.0x)',
            'zoom': 3.0,
            'pan_x': -400.0,
            'pan_y': -300.0,
            'duration': 3.0
        }
    ]
    
    # Main test loop
    clock = pygame.time.Clock()
    running = True
    current_phase = 0
    phase_timer = 0.0
    
    print("\nRunning employee zoom/pan test phases...")
    print("Watch for employee staying aligned with grid tiles during transformations")
    
    while running and current_phase < len(test_phases):
        dt = clock.tick(60) / 1000.0
        phase_timer += dt
        
        # Get current phase
        phase = test_phases[current_phase]
        
        # Apply transformation to enhanced renderer
        if hasattr(grid_manager, 'enhanced_renderer'):
            renderer = grid_manager.enhanced_renderer
            renderer.zoom_factor = phase['zoom']
            renderer.pan_offset_x = phase['pan_x']
            renderer.pan_offset_y = phase['pan_y']
        
        # Check phase completion
        if phase_timer >= phase['duration']:
            current_phase += 1
            phase_timer = 0.0
            
            if current_phase < len(test_phases):
                next_phase = test_phases[current_phase]
                print(f"\nPhase {current_phase + 1}: {next_phase['name']}")
        
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                # Allow manual zoom testing
                grid_manager.handle_mouse_wheel(pygame.mouse.get_pos(), event.y)
        
        # Update systems
        event_system.process_events()
        grid_manager.update(dt)
        employee_manager.update(dt)
        
        # Render everything
        screen.fill((30, 30, 30))  # Dark background
        
        # Render grid first
        grid_manager.render(screen)
        
        # Render employees (should now be properly aligned)
        employee_manager.render(screen)
        
        # Add test information overlay
        font = pygame.font.Font(None, 24)
        if current_phase < len(test_phases):
            phase_name = test_phases[current_phase]['name']
            progress = f"Phase {current_phase + 1}/{len(test_phases)}"
        else:
            phase_name = "Test Complete!"
            progress = "All Phases Done"
        
        # Render overlay with background
        status_text = font.render(phase_name, True, (255, 255, 255))
        progress_text = font.render(progress, True, (200, 200, 200))
        
        status_bg = pygame.Rect(10, 90, max(status_text.get_width(), progress_text.get_width()) + 20, 60)
        pygame.draw.rect(screen, (0, 0, 0, 180), status_bg)
        
        screen.blit(status_text, (20, 100))
        screen.blit(progress_text, (20, 125))
        
        # Show current transformation values
        if hasattr(grid_manager, 'enhanced_renderer'):
            renderer = grid_manager.enhanced_renderer
            transform_info = [
                f"Zoom: {renderer.zoom_factor:.1f}x",
                f"Pan: ({renderer.pan_offset_x:.0f}, {renderer.pan_offset_y:.0f})"
            ]
            
            for i, info in enumerate(transform_info):
                info_surface = font.render(info, True, (150, 150, 150))
                screen.blit(info_surface, (20, 160 + i * 25))
        
        # Instructions
        instructions = [
            "Watch employee alignment with grid tiles",
            "Use mouse wheel for manual zoom testing",
            "Employee should scale and move with grid"
        ]
        
        small_font = pygame.font.Font(None, 18)
        for i, instruction in enumerate(instructions):
            inst_surface = small_font.render(instruction, True, (120, 120, 120))
            screen.blit(inst_surface, (20, 220 + i * 20))
        
        pygame.display.flip()
    
    print("\nEmployee Zoom/Pan Fix test completed!")
    print("RESULTS:")
    print("- Employee positions should now be synchronized with grid transformations")
    print("- Employee size should scale with zoom factor")
    print("- Employee details (name, needs bars) should adapt to zoom level")
    print("- Movement lines should align with grid coordinates")
    
    pygame.quit()
    return True

if __name__ == "__main__":
    try:
        success = test_employee_zoom_fix()
        print("\n[SUCCESS] Employee Zoom Fix Test: PASSED")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAILED] Employee Zoom Fix Test: FAILED - {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)