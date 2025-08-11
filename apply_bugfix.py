"""
Create a simple fix that forcefully hides the applicant panel after initialization
"""

import sys
import os

# Add project root to path  
sys.path.insert(0, r'C:\Users\dirha\Documents\GameCreator\agrifun')

def create_fixed_ui_manager():
    """Create a patched version of ui_manager that ensures panel stays hidden"""
    
    ui_manager_path = r'C:\Users\dirha\Documents\GameCreator\agrifun\scripts\ui\ui_manager.py'
    
    print("Creating fixed UI Manager...")
    print("="*60)
    
    # Read the current file
    with open(ui_manager_path, 'r') as f:
        lines = f.readlines()
    
    # Find the update method and add panel hiding logic
    fixed_lines = []
    for i, line in enumerate(lines):
        fixed_lines.append(line)
        
        # After the startup protection ends, force hide the panel
        if 'self._is_startup_complete = True' in line:
            print(f"Found startup completion at line {i+1}")
            # Add forced hiding after startup
            fixed_lines.append('                # BUGFIX: Force hide applicant panel after startup\n')
            fixed_lines.append('                if hasattr(self, "applicant_panel"):\n')
            fixed_lines.append('                    self.applicant_panel.visible = 0\n')
            fixed_lines.append('                    self.applicant_panel.hide()\n')
            fixed_lines.append('                    self.show_applicant_panel = False\n')
            fixed_lines.append('                    print("BUGFIX: Forced applicant panel to hidden after startup")\n')
    
    # Also add a safety check in the render method
    render_found = False
    for i, line in enumerate(fixed_lines):
        if 'def render(self' in line:
            render_found = True
            print(f"Found render method at line {i+1}")
            
        # Add check at the beginning of render
        if render_found and 'self.gui_manager.draw_ui' in line:
            # Insert safety check before drawing
            idx = i
            indent = '        '  # Proper indentation for inside render method
            fixed_lines.insert(idx, f'{indent}# BUGFIX: Safety check to prevent stuck panel\n')
            fixed_lines.insert(idx+1, f'{indent}if hasattr(self, "applicant_panel") and self.applicant_panel.visible and not self.show_applicant_panel:\n')
            fixed_lines.insert(idx+2, f'{indent}    self.applicant_panel.visible = 0\n')
            fixed_lines.insert(idx+3, f'{indent}    self.applicant_panel.hide()\n')
            fixed_lines.insert(idx+4, f'{indent}    print("BUGFIX: Detected and fixed stuck applicant panel")\n')
            fixed_lines.insert(idx+5, f'{indent}\n')
            render_found = False  # Only do this once
            print("Added safety check in render method")
            break
    
    # Write the fixed version
    with open(ui_manager_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print("\n[FIXED] UI Manager has been patched with:")
    print("1. Forced hiding after startup protection ends")
    print("2. Safety check in render to detect and fix stuck panels")
    print("\nPlease run the game to test the fix!")
    
    return True

if __name__ == "__main__":
    create_fixed_ui_manager()
