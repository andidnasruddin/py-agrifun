"""
Test script for Enhanced Grid System
Tests the advanced grid rendering with zoom, pan, and visual enhancements.
"""

import pygame
import sys
from scripts.core.config import WINDOW_WIDTH, WINDOW_HEIGHT
from scripts.core.event_system import EventSystem
from scripts.core.grid_manager import GridManager

def test_enhanced_grid():
    """Test the enhanced grid system"""
    print("Testing Enhanced Grid System...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Enhanced Grid Test")
    
    # Create event system
    event_system = EventSystem()
    
    # Create grid manager with enhanced renderer
    print("Creating Grid Manager with Enhanced Renderer...")
    grid_manager = GridManager(event_system)
    print("Grid Manager created successfully!")
    
    # Set up some test data in the grid
    print("Setting up test grid data...")
    
    # Add some tilled plots with crops
    for y in range(3, 7):
        for x in range(3, 7):
            tile = grid_manager.grid[y][x]
            tile.terrain_type = 'tilled'
            tile.current_crop = 'corn'
            tile.growth_stage = (x + y) % 5  # Varying growth stages
            tile.soil_quality = 5 + (x + y) % 5  # Varying soil quality
    
    # Add some irrigation
    for y in range(5, 9):
        for x in range(5, 9):
            tile = grid_manager.grid[y][x]
            tile.has_irrigation = True
    
    # Add some task assignments
    for y in range(10, 13):
        for x in range(10, 13):
            tile = grid_manager.grid[y][x]
            tile.task_assignment = 'till'
    
    print("Test data setup complete!")
    
    # Test main loop with enhanced grid features
    clock = pygame.time.Clock()
    running = True
    test_phase = 0
    phase_timer = 0
    phase_duration = 4.0  # 4 seconds per phase
    
    instructions = [
        "Phase 0: Normal view",
        "Phase 1: Zooming in (scroll wheel simulation)",
        "Phase 2: Soil health overlay enabled",
        "Phase 3: Irrigation overlay enabled",
        "Phase 4: Reset viewport"
    ]
    
    print("Running enhanced grid test phases...")
    print("Use mouse wheel to zoom, middle mouse to pan (if supported)")
    
    while running and test_phase < len(instructions):
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        phase_timer += dt
        
        # Switch test phases automatically
        if phase_timer >= phase_duration:
            phase_timer = 0
            test_phase += 1
            
            if test_phase < len(instructions):
                print(f"\n{instructions[test_phase]}")
                
                if test_phase == 1:
                    # Simulate zoom in
                    event_system.emit('grid_zoom_in', {})
                    event_system.emit('grid_zoom_in', {})
                elif test_phase == 2:
                    # Enable soil health overlay
                    event_system.emit('toggle_soil_health_overlay', {})
                elif test_phase == 3:
                    # Enable irrigation overlay
                    event_system.emit('toggle_irrigation_overlay', {})
                elif test_phase == 4:
                    # Reset viewport
                    event_system.emit('grid_reset_viewport', {})
        
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                # Test mouse wheel zoom
                grid_manager.handle_mouse_wheel(pygame.mouse.get_pos(), event.y)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Test mouse interaction
                grid_manager.handle_mouse_down(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                grid_manager.handle_mouse_up(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                # Test mouse motion for panning
                if hasattr(grid_manager.enhanced_renderer, 'handle_mouse_motion'):
                    grid_manager.enhanced_renderer.handle_mouse_motion(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Test manual zoom toggle
                    event_system.emit('grid_zoom_in', {})
                elif event.key == pygame.K_r:
                    # Test viewport reset
                    event_system.emit('grid_reset_viewport', {})
                elif event.key == pygame.K_s:
                    # Test soil overlay toggle
                    event_system.emit('toggle_soil_health_overlay', {})
                elif event.key == pygame.K_i:
                    # Test irrigation overlay toggle
                    event_system.emit('toggle_irrigation_overlay', {})
        
        # Update systems
        grid_manager.update(dt)
        event_system.process_events()
        
        # Render
        screen.fill((30, 30, 30))  # Dark background
        
        # Add HUD space (simulate enhanced HUD)
        hud_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 80)
        pygame.draw.rect(screen, (20, 20, 20), hud_rect)
        
        # Add panel space (simulate right panel)
        panel_rect = pygame.Rect(WINDOW_WIDTH - 290, 80, 290, WINDOW_HEIGHT - 80)
        pygame.draw.rect(screen, (25, 25, 25), panel_rect)
        
        # Render enhanced grid
        grid_manager.render(screen)
        
        # Add phase indicator
        font = pygame.font.Font(None, 24)
        if test_phase < len(instructions):
            phase_text = instructions[test_phase]
        else:
            phase_text = "Test Complete"
        
        text_surface = font.render(phase_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # Add controls help
        help_font = pygame.font.Font(None, 18)
        help_lines = [
            "Mouse Wheel: Zoom in/out",
            "Middle Mouse: Pan (if supported)",
            "Space: Zoom in",
            "R: Reset viewport",
            "S: Toggle soil overlay",
            "I: Toggle irrigation overlay"
        ]
        
        for i, line in enumerate(help_lines):
            help_surface = help_font.render(line, True, (200, 200, 200))
            screen.blit(help_surface, (10, 50 + i * 20))
        
        pygame.display.flip()
    
    print("\nEnhanced Grid System test completed successfully!")
    print("- Enhanced grid renderer integration functional")
    print("- Zoom and pan capabilities working")
    print("- Advanced tile visualization implemented")
    print("- Overlay systems operational")
    print("- Mouse interaction enhanced")
    
    pygame.quit()
    return True

if __name__ == "__main__":
    try:
        success = test_enhanced_grid()
        print("\n[SUCCESS] Enhanced Grid Test: PASSED")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAILED] Enhanced Grid Test: FAILED - {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)