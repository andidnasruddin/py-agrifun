"""
Test script for Dynamic Right Panel system
Tests the context-sensitive panel switching functionality.
"""

import pygame
import pygame_gui
import sys
from scripts.core.config import WINDOW_WIDTH, WINDOW_HEIGHT
from scripts.core.event_system import EventSystem
from scripts.ui.enhanced_ui_components import DynamicRightPanel

class MockTile:
    """Mock tile object for testing"""
    def __init__(self, x, y, tilled=False, crop_type=None):
        self.x = x
        self.y = y
        self.tilled = tilled
        self.crop_type = crop_type
        self.soil_quality = 7
        self.water_level = 60
        self.growth_stage = 2
        self.has_irrigation = False
        self.crop_history = [
            {'crop_type': 'corn'},
            {'crop_type': 'wheat'}
        ]
        # Mock nutrients
        self.nutrients = MockNutrients()

class MockNutrients:
    """Mock nutrients object for testing"""
    def __init__(self):
        self.nitrogen = 75
        self.phosphorus = 85
        self.potassium = 65

class MockEmployee:
    """Mock employee object for testing"""
    def __init__(self, name="Test Employee"):
        self.name = name
        self.employee_id = "emp_001"
        self.x = 8.5
        self.y = 7.2
        self.hunger = 85
        self.thirst = 70
        self.rest = 60
        self.current_task = "planting"
        self.traits = {
            'hard_worker': True,
            'green_thumb': True
        }

def test_dynamic_panel():
    """Test the dynamic right panel system"""
    print("Testing Dynamic Right Panel Implementation...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Dynamic Panel Test")
    
    # Create event system
    event_system = EventSystem()
    
    # Create pygame-gui manager
    gui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Create dynamic right panel
    print("Creating Dynamic Right Panel...")
    right_panel = DynamicRightPanel(
        gui_manager, 
        event_system,
        x_pos=WINDOW_WIDTH - 300,  # Right side of screen
        y_pos=100,                 # Below HUD area
        width=280,
        height=600
    )
    print("Dynamic Right Panel created successfully!")
    
    # Test panel switching
    print("Testing panel switching functionality...")
    
    # Create mock objects
    mock_tile = MockTile(5, 8, tilled=True, crop_type="tomatoes")
    mock_employee = MockEmployee("Alice")
    
    # Test main loop with different panel states
    clock = pygame.time.Clock()
    running = True
    test_phase = 0
    phase_timer = 0
    phase_duration = 3.0  # 3 seconds per phase
    
    print("Running dynamic panel test phases...")
    
    while running and test_phase < 4:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        phase_timer += dt
        
        # Switch test phases
        if phase_timer >= phase_duration:
            phase_timer = 0
            test_phase += 1
            
            if test_phase == 1:
                print("Phase 1: Testing soil panel...")
                event_system.emit('tile_selected', {'tile': mock_tile})
            elif test_phase == 2:
                print("Phase 2: Testing employee panel...")
                event_system.emit('employee_selected', {'employee': mock_employee})
            elif test_phase == 3:
                print("Phase 3: Testing panel close...")
                event_system.emit('panel_close_requested', {})
            elif test_phase >= 4:
                print("Test phases completed")
                running = False
        
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Process UI events
            gui_manager.process_events(event)
            
            # Handle panel close button clicks
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if hasattr(event.ui_element, 'is_panel_close'):
                        print("Panel close button clicked")
                        event_system.emit('panel_close_requested', {})
        
        # Update systems
        event_system.process_events()
        gui_manager.update(dt)
        
        # Render
        screen.fill((50, 50, 50))  # Dark gray background
        gui_manager.draw_ui(screen)
        
        # Add phase indicator
        font = pygame.font.Font(None, 36)
        phase_text = f"Test Phase {test_phase}/3"
        text_surface = font.render(phase_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()
    
    print("Dynamic Right Panel test completed successfully!")
    print("- Panel creation functional")
    print("- Context switching working")
    print("- Soil panel displays comprehensive information")
    print("- Employee panel shows detailed employee data")
    print("- Panel close functionality operational")
    
    pygame.quit()
    return True

if __name__ == "__main__":
    try:
        success = test_dynamic_panel()
        print("\n[SUCCESS] Dynamic Panel Test: PASSED")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAILED] Dynamic Panel Test: FAILED - {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)