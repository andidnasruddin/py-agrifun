"""
Test script to check if the hiring popup is stuck in UI
"""

import pygame
import sys
import os

# Add project root to path
sys.path.insert(0, r'C:\Users\dirha\Documents\GameCreator\agrifun')

# Initialize pygame
pygame.init()

# Try to import and check UI manager
try:
    from scripts.ui.ui_manager import UIManager
    from scripts.core.event_system import EventSystem
    
    # Create minimal setup
    screen = pygame.display.set_mode((800, 600))
    event_system = EventSystem()
    
    # Create UI manager (only needs event_system and screen)
    ui_manager = UIManager(event_system, screen)
    
    print("\n" + "="*50)
    print("UI MANAGER STATE CHECK")
    print("="*50)
    
    # Check applicant panel state
    if hasattr(ui_manager, 'applicant_panel'):
        print(f"[OK] Applicant panel exists")
        print(f"  - Visible: {ui_manager.applicant_panel.visible}")
        print(f"  - Show flag: {ui_manager.show_applicant_panel}")
    else:
        print("[X] No applicant panel found")
    
    # Check for stuck panels
    if hasattr(ui_manager, 'applicant_panel') and ui_manager.applicant_panel.visible:
        print("\n[WARNING] Applicant panel is visible on startup!")
        print("This is the stuck hiring popup bug.")
    else:
        print("\n[OK] No stuck panels detected on startup")
    
    # Check startup protection
    if hasattr(ui_manager, '_is_startup_complete'):
        print(f"\nStartup protection status: {ui_manager._is_startup_complete}")
    
    print("\n" + "="*50)
    
except Exception as e:
    print(f"Error loading UI Manager: {e}")
    import traceback
    traceback.print_exc()

pygame.quit()
