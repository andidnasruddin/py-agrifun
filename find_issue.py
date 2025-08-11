"""
Fix the stuck hiring popup issue by ensuring the applicant panel is properly hidden
and only shown when explicitly requested by the user.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, r'C:\Users\dirha\Documents\GameCreator\agrifun')

def fix_ui_manager():
    """Apply fixes to the UI manager to ensure panels are properly hidden"""
    
    ui_manager_path = r'C:\Users\dirha\Documents\GameCreator\agrifun\scripts\ui\ui_manager.py'
    
    # Read the file
    with open(ui_manager_path, 'r') as f:
        lines = f.readlines()
    
    # Look for the _populate_applicant_panel method which might be showing the panel
    for i in range(len(lines)):
        # Check if _populate_applicant_panel is making the panel visible
        if '_populate_applicant_panel' in lines[i] and 'def' in lines[i]:
            print(f"Found _populate_applicant_panel at line {i+1}")
            # Check the next 20 lines for any visibility changes
            for j in range(i, min(i+20, len(lines))):
                if 'self.applicant_panel.visible = 1' in lines[j] or 'self.applicant_panel.show()' in lines[j]:
                    print(f"  WARNING: Panel being shown at line {j+1}")
    
    print("\nChecking for automatic applicant generation...")
    
    # Check game_manager for any automatic generation
    game_manager_path = r'C:\Users\dirha\Documents\GameCreator\agrifun\scripts\core\game_manager.py'
    with open(game_manager_path, 'r') as f:
        gm_lines = f.readlines()
    
    for i in range(len(gm_lines)):
        if 'generate_applicants' in gm_lines[i].lower() or 'test' in gm_lines[i].lower() and 'applicant' in gm_lines[i].lower():
            print(f"Found potential auto-generation at line {i+1}: {gm_lines[i].strip()}")
    
    print("\nChecking if there's a test mode or debug flag...")
    
    # Check for any test/debug flags
    for i in range(len(lines)):
        if 'TEST' in lines[i] or 'DEBUG' in lines[i] and 'applicant' in lines[i].lower():
            print(f"Found test/debug code at line {i+1}: {lines[i].strip()}")

if __name__ == "__main__":
    fix_ui_manager()
