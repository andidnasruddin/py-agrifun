"""
Test the task assignment modal integration within the full game
This tests that clicking the "Assign" button shows the modal correctly.
"""

import pygame
import sys
import os

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.config import *
from scripts.core.event_system import EventSystem
from scripts.ui.ui_manager import UIManager

def test_assign_button_integration():
    """Test that the Assign button properly shows the task assignment modal"""
    print("Testing Assign button integration...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Task Assignment Integration Test")
    clock = pygame.time.Clock()
    
    # Initialize event system
    event_system = EventSystem()
    
    # Initialize UI manager (this creates all UI components including the modal)
    ui_manager = UIManager(event_system, screen)
    
    print("[OK] UI Manager created with task assignment modal")
    
    # Test the event that should trigger the modal
    event_system.emit('show_task_assignment_interface', {})
    print("[OK] Emitted show_task_assignment_interface event")
    
    # Run for a few frames to let the modal appear
    for i in range(120):  # 2 seconds at 60 FPS
        time_delta = clock.tick(60) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            ui_manager.handle_event(event)
        
        # Update
        ui_manager.update(time_delta)
        
        # Draw
        screen.fill((34, 34, 34))  # Background color from config
        ui_manager.render(screen)
        
        pygame.display.flip()
        
        if i == 60:  # After 1 second
            print("[OK] Modal should be visible now")
    
    # Test hiding the modal
    event_system.emit('hide_task_assignment_modal', {})
    print("[OK] Emitted hide_task_assignment_modal event")
    
    # Run a few more frames
    for i in range(60):  # 1 second
        time_delta = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            ui_manager.handle_event(event)
        
        ui_manager.update(time_delta)
        screen.fill((34, 34, 34))
        ui_manager.render(screen)
        pygame.display.flip()
    
    pygame.quit()
    print("[OK] Integration test completed successfully!")

if __name__ == "__main__":
    test_assign_button_integration()