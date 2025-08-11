"""
Final diagnostic to understand the stuck hiring popup issue
"""

import pygame
import sys
import os
import time

# Add project root to path
sys.path.insert(0, r'C:\Users\dirha\Documents\GameCreator\agrifun')

# Patch the UIManager to trace panel visibility changes
original_setattr = object.__setattr__

def trace_setattr(self, name, value):
    """Trace attribute changes on applicant_panel"""
    if hasattr(self, '__class__') and 'UIPanel' in str(self.__class__):
        if name == 'visible' and value == 1:
            import traceback
            print(f"\n[PANEL VISIBILITY CHANGE] Panel.visible set to 1")
            print("Call stack:")
            for line in traceback.format_stack()[-5:-1]:
                print(line.strip())
    return original_setattr(self, name, value)

# Apply the patch
object.__setattr__ = trace_setattr

def main():
    # Initialize pygame
    pygame.init()
    
    from scripts.core.game_manager import GameManager
    
    print("\n" + "="*60)
    print("TRACING PANEL VISIBILITY CHANGES")
    print("="*60)
    print("\nRunning game and monitoring for panel visibility changes...")
    print("="*60)
    
    # Create game instance
    game = GameManager()
    
    clock = pygame.time.Clock()
    start_time = time.time()
    
    print("\nMonitoring for 10 seconds...")
    
    while time.time() - start_time < 10:  # Run for 10 seconds
        delta_time = clock.tick(60) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    break
            # Pass events to UI manager
            if hasattr(game, 'ui_manager'):
                game.ui_manager.handle_event(event)
        
        # Update game
        game._handle_events()
        game._update(delta_time)
        game._render()
        
        pygame.display.flip()
    
    # Final check
    print("\n" + "="*60)
    print("FINAL CHECK:")
    print("="*60)
    
    ui = game.ui_manager
    if hasattr(ui, 'applicant_panel'):
        if ui.applicant_panel.visible == 1:
            print("[ISSUE FOUND] Applicant panel IS visible!")
            print(f"Current applicants: {len(ui.current_applicants) if hasattr(ui, 'current_applicants') else 0}")
        else:
            print("[OK] Applicant panel is hidden")
    
    pygame.quit()
    print("\nDiagnostic complete.")

if __name__ == "__main__":
    main()
