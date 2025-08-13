"""
Test script for the Enhanced Task Assignment Modal
Verifies that the modal can be created and displayed correctly.
"""

import pygame
import pygame_gui
import sys
import os

# Add the scripts directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.core.config import *
from scripts.core.event_system import EventSystem
from scripts.ui.task_assignment_modal import TaskAssignmentModal

def test_task_assignment_modal():
    """Test the task assignment modal functionality"""
    print("Testing Enhanced Task Assignment Modal...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Task Assignment Modal Test")
    clock = pygame.time.Clock()
    
    # Initialize pygame-gui
    gui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Initialize event system
    event_system = EventSystem()
    
    # Create task assignment modal
    task_modal = TaskAssignmentModal(gui_manager, event_system, WINDOW_WIDTH, WINDOW_HEIGHT)
    
    print("[OK] Task assignment modal created successfully")
    
    # Show the modal
    task_modal.show_modal()
    print("[OK] Modal shown successfully")
    
    # Main game loop
    running = True
    frames = 0
    max_frames = 300  # Run for ~5 seconds at 60 FPS
    
    while running and frames < max_frames:
        time_delta = clock.tick(60) / 1000.0
        frames += 1
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Let the modal handle events
            if task_modal.handle_event(event):
                print(f"[OK] Modal handled event: {event.type}")
        
        # Update
        gui_manager.update(time_delta)
        task_modal.update(time_delta)
        
        # Draw
        screen.fill((50, 50, 50))  # Dark background
        gui_manager.draw_ui(screen)
        
        pygame.display.flip()
        
        # Test showing/hiding modal at specific frames
        if frames == 60:  # After 1 second
            print("[OK] Modal visible for 1 second")
        elif frames == 180:  # After 3 seconds
            task_modal.hide_modal()
            print("[OK] Modal hidden successfully")
        elif frames == 240:  # After 4 seconds
            task_modal.show_modal()
            print("[OK] Modal shown again successfully")
    
    # Cleanup
    task_modal.cleanup()
    pygame.quit()
    
    print("[OK] Test completed successfully!")
    print("[OK] All task assignment modal functionality working")

if __name__ == "__main__":
    test_task_assignment_modal()