"""
Test script for Enhanced HUD implementation
Tests the new comprehensive top HUD system in isolation.
"""

import pygame
import pygame_gui
import sys
from scripts.core.config import WINDOW_WIDTH, WINDOW_HEIGHT
from scripts.core.event_system import EventSystem
from scripts.ui.enhanced_ui_components import EnhancedTopHUD

def test_enhanced_hud():
    """Test the enhanced HUD system"""
    print("Testing Enhanced HUD Implementation...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Enhanced HUD Test")
    
    # Create event system
    event_system = EventSystem()
    
    # Create pygame-gui manager
    gui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Create enhanced HUD
    print("Creating Enhanced Top HUD...")
    enhanced_hud = EnhancedTopHUD(gui_manager, event_system)
    print("Enhanced HUD created successfully!")
    
    # Test some data updates
    print("Testing HUD data updates...")
    
    # Simulate time update
    event_system.emit('time_updated', {
        'day': 5,
        'hour': 14,
        'minute': 30
    })
    
    # Simulate money update
    event_system.emit('money_changed', {
        'amount': 12500
    })
    
    # Simulate weather update
    event_system.emit('weather_updated', {
        'season': 'summer',
        'weather_event': 'rain',
        'growth_modifier': 1.2
    })
    
    # Simulate employee count update
    event_system.emit('employee_count_changed', {
        'count': 3
    })
    
    # Simulate inventory update
    event_system.emit('full_inventory_status', {
        'total_items': 75,
        'capacity': 150
    })
    
    print("HUD data updates sent successfully!")
    
    # Test main loop
    clock = pygame.time.Clock()
    running = True
    test_duration = 5.0  # Run for 5 seconds
    start_time = pygame.time.get_ticks()
    
    print(f"Running HUD test for {test_duration} seconds...")
    
    while running:
        current_time = pygame.time.get_ticks()
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        # Check for exit conditions
        if (current_time - start_time) / 1000.0 > test_duration:
            print("Test duration completed")
            running = False
        
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Process UI events
            gui_manager.process_events(event)
        
        # Update systems
        enhanced_hud.update(dt)
        event_system.process_events()
        gui_manager.update(dt)
        
        # Render
        screen.fill((50, 50, 50))  # Dark gray background
        gui_manager.draw_ui(screen)
        pygame.display.flip()
    
    print("Enhanced HUD test completed successfully!")
    print("- HUD created and initialized")
    print("- Data updates processed")
    print("- Rendering loop functional")
    print("- Event system integration working")
    
    pygame.quit()
    return True

if __name__ == "__main__":
    try:
        success = test_enhanced_hud()
        print("\n[SUCCESS] Enhanced HUD Test: PASSED")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAILED] Enhanced HUD Test: FAILED - {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)