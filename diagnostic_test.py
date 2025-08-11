"""
Interactive test to see if we can reproduce and fix the stuck hiring panel issue
"""

import pygame
import sys
import os
import time

# Add project root to path
sys.path.insert(0, r'C:\Users\dirha\Documents\GameCreator\agrifun')

def main():
    # Initialize pygame
    pygame.init()
    
    from scripts.core.game_manager import GameManager
    
    print("\n" + "="*60)
    print("FARMING GAME DIAGNOSTIC TEST")
    print("="*60)
    print("\nStarting game with diagnostic monitoring...")
    print("Press ESC to exit")
    print("Press SPACE to check UI state")
    print("Press H to attempt to hide applicant panel")
    print("Press V to check panel visibility")
    print("\n" + "="*60)
    
    # Create game instance
    game = GameManager()
    
    # Override the main loop for diagnostic purposes
    clock = pygame.time.Clock()
    running = True
    frame_count = 0
    last_check = 0
    
    while running:
        delta_time = clock.tick(60) / 1000.0
        frame_count += 1
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Check UI state
                    print(f"\n[Frame {frame_count}] UI State Check:")
                    ui = game.ui_manager
                    if hasattr(ui, 'applicant_panel'):
                        print(f"  - Applicant panel visible: {ui.applicant_panel.visible}")
                        print(f"  - Show flag: {ui.show_applicant_panel}")
                        print(f"  - Startup complete: {ui._is_startup_complete if hasattr(ui, '_is_startup_complete') else 'N/A'}")
                elif event.key == pygame.K_h:
                    # Try to hide applicant panel
                    print(f"\n[Frame {frame_count}] Attempting to hide applicant panel...")
                    ui = game.ui_manager
                    if hasattr(ui, '_hide_applicant_panel'):
                        ui._hide_applicant_panel()
                        print("  - Called _hide_applicant_panel()")
                    if hasattr(ui, 'applicant_panel'):
                        ui.applicant_panel.visible = 0
                        ui.applicant_panel.hide()
                        ui.show_applicant_panel = False
                        print("  - Forced panel to hidden state")
                elif event.key == pygame.K_v:
                    # Verbose visibility check
                    print(f"\n[Frame {frame_count}] Verbose Panel Check:")
                    ui = game.ui_manager
                    if hasattr(ui, 'applicant_panel'):
                        panel = ui.applicant_panel
                        print(f"  - Panel object: {panel}")
                        print(f"  - Visible attribute: {panel.visible}")
                        print(f"  - Is alive: {panel.alive() if hasattr(panel, 'alive') else 'N/A'}")
                        print(f"  - Rect: {panel.rect if hasattr(panel, 'rect') else 'N/A'}")
                        # Try to find if it's in any container
                        if hasattr(ui, 'gui_manager'):
                            print(f"  - GUI Manager has panel: {panel in ui.gui_manager.get_root_container().elements if hasattr(ui.gui_manager, 'get_root_container') else 'N/A'}")
            
            # Pass event to game's ui_manager and other systems
            if hasattr(game, 'ui_manager'):
                game.ui_manager.handle_event(event)
            if hasattr(game, 'grid_manager'):
                game.grid_manager.handle_event(event)
        
        # Update game
        game.update(delta_time)
        
        # Render game
        game.render()
        
        # Auto-check every 5 seconds
        current_time = time.time()
        if current_time - last_check > 5:
            last_check = current_time
            ui = game.ui_manager
            if hasattr(ui, 'applicant_panel') and ui.applicant_panel.visible:
                print(f"\n[AUTO-CHECK Frame {frame_count}] WARNING: Applicant panel is visible!")
                print(f"  - Show flag: {ui.show_applicant_panel}")
                print(f"  - Startup complete: {ui._is_startup_complete if hasattr(ui, '_is_startup_complete') else 'N/A'}")
        
        pygame.display.flip()
    
    pygame.quit()
    print("\nDiagnostic test completed.")

if __name__ == "__main__":
    main()
