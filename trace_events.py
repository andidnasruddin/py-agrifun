"""
Debug script to trace the applicant panel issue
"""

import pygame
import sys
import os

# Add project root to path
sys.path.insert(0, r'C:\Users\dirha\Documents\GameCreator\agrifun')

# Monkey patch the event system to trace all events
original_emit = None

def trace_emit(self, event_name, event_data=None):
    """Trace all events being emitted"""
    if 'applicant' in event_name.lower() or 'hire' in event_name.lower():
        print(f"[EVENT EMITTED] {event_name}: {event_data}")
    return original_emit(self, event_name, event_data)

# Initialize pygame
pygame.init()

from scripts.core.event_system import EventSystem

# Patch the emit method
original_emit = EventSystem.emit
EventSystem.emit = trace_emit

# Now import and run the game
from scripts.core.game_manager import GameManager

print("\n" + "="*60)
print("TRACING APPLICANT-RELATED EVENTS")
print("="*60)
print("\nStarting game with event tracing...")
print("Looking for any applicant generation at startup...")
print("\n" + "="*60)

# Create and run game briefly
game = GameManager()

# Run for just a few frames to see initialization
clock = pygame.time.Clock()
for i in range(60):  # Run for 1 second at 60 FPS
    delta_time = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break
    
    game._handle_events()
    game._update(delta_time)
    game._render()
    pygame.display.flip()

# Check the UI state after initialization
print("\n" + "="*60)
print("CHECKING UI STATE AFTER 1 SECOND:")
print("="*60)

ui = game.ui_manager
if hasattr(ui, 'applicant_panel'):
    print(f"Applicant panel visible: {ui.applicant_panel.visible}")
    print(f"Show applicant panel flag: {ui.show_applicant_panel}")
    print(f"Current applicants: {len(ui.current_applicants) if hasattr(ui, 'current_applicants') else 'N/A'}")
    if hasattr(ui, 'current_applicants') and ui.current_applicants:
        print(f"Applicants present: {[app.name for app in ui.current_applicants]}")

pygame.quit()
print("\nTrace complete.")
