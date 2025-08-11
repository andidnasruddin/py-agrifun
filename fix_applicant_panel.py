"""
Fix script to ensure the applicant panel is never shown unless explicitly requested by the user
"""

import sys
import os

# Add project root to path
sys.path.insert(0, r'C:\Users\dirha\Documents\GameCreator\agrifun')

def apply_fix():
    """Apply the fix to ensure applicant panel doesn't auto-show"""
    
    ui_manager_path = r'C:\Users\dirha\Documents\GameCreator\agrifun\scripts\ui\ui_manager.py'
    
    print("Applying fix to prevent auto-showing of applicant panel...")
    print("=" * 60)
    
    # Read the file
    with open(ui_manager_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Ensure _handle_applicants_generated doesn't show the panel
    # It should only store the applicants, not show the panel
    if '_handle_applicants_generated' in content:
        print("[OK] Found _handle_applicants_generated method")
        
        # Check if it's showing the panel
        if 'self.applicant_panel.visible = 1' in content and '_handle_applicants_generated' in content:
            print("  [WARNING] _handle_applicants_generated might be showing the panel!")
            print("  This method should ONLY store applicants, not show the panel.")
    
    # Fix 2: Make sure the panel starts hidden
    if 'self.applicant_panel.visible = 0' in content:
        print("[OK] Panel is set to hidden on creation")
    
    # Fix 3: Add extra protection to _populate_applicant_panel
    # This method should NEVER make the panel visible
    fix_needed = False
    
    lines = content.split('\n')
    fixed_lines = []
    in_populate_method = False
    
    for i, line in enumerate(lines):
        if 'def _populate_applicant_panel' in line:
            in_populate_method = True
            fixed_lines.append(line)
            # Add a comment to clarify this method's purpose
            fixed_lines.append('        """Populate the applicant panel with current applicants in table format')
            fixed_lines.append('        NOTE: This method ONLY populates content, it does NOT make the panel visible."""')
            continue
        elif in_populate_method and 'def ' in line and not line.strip().startswith('#'):
            in_populate_method = False
        
        # Check if this line is trying to show the panel in _populate_applicant_panel
        if in_populate_method and ('self.applicant_panel.visible = 1' in line or 'self.applicant_panel.show()' in line):
            print(f"  [WARNING] Found panel visibility change in _populate_applicant_panel at line {i+1}")
            print(f"    Commenting out: {line.strip()}")
            fixed_lines.append('        # ' + line.lstrip())  # Comment it out
            fix_needed = True
        else:
            fixed_lines.append(line)
    
    # Fix 4: Ensure _handle_applicants_generated doesn't show the panel
    final_lines = []
    in_handle_method = False
    
    for i, line in enumerate(fixed_lines):
        if 'def _handle_applicants_generated' in line:
            in_handle_method = True
            final_lines.append(line)
            continue
        elif in_handle_method and 'def ' in line and not line.strip().startswith('#'):
            in_handle_method = False
        
        # Remove any panel showing in this method
        if in_handle_method and ('self._show_applicant_panel()' in line or 'self.applicant_panel.visible = 1' in line):
            print(f"  [WARNING] Found panel showing in _handle_applicants_generated at line {i+1}")
            print(f"    Commenting out: {line.strip()}")
            final_lines.append('        # AUTO-SHOW DISABLED: ' + line.lstrip())
            fix_needed = True
        else:
            final_lines.append(line)
    
    if fix_needed:
        # Write the fixed content
        with open(ui_manager_path, 'w') as f:
            f.write('\n'.join(final_lines))
        print("\n[FIXED] Panel auto-showing has been disabled")
        print("The applicant panel will now ONLY show when the user clicks 'View Applicants'")
    else:
        print("\n[OK] No auto-showing issues found in the code")
        print("The panel should already only show when explicitly requested")
    
    print("\n" + "=" * 60)
    print("ADDITIONAL CHECKS:")
    print("=" * 60)
    
    # Check for any test code that might be generating applicants
    simple_hiring_path = r'C:\Users\dirha\Documents\GameCreator\agrifun\scripts\employee\simple_hiring_system.py'
    with open(simple_hiring_path, 'r') as f:
        hiring_content = f.read()
    
    if 'generate_applicants(' in hiring_content or 'self._generate_test' in hiring_content:
        print("[WARNING] Found potential auto-generation in simple_hiring_system.py")
    else:
        print("[OK] No auto-generation found in simple_hiring_system.py")
    
    # Check game_manager
    game_manager_path = r'C:\Users\dirha\Documents\GameCreator\agrifun\scripts\core\game_manager.py'
    with open(game_manager_path, 'r') as f:
        gm_content = f.read()
    
    if 'generate_applicants' in gm_content and 'emit(' in gm_content:
        print("[WARNING] Found potential auto-generation trigger in game_manager.py")
    else:
        print("[OK] No auto-generation triggers found in game_manager.py")
    
    print("\n" + "=" * 60)
    print("FIX COMPLETE")
    print("=" * 60)
    print("\nThe applicant panel should now:")
    print("1. Start hidden when the game launches")
    print("2. Stay hidden when applicants are generated")
    print("3. ONLY show when user clicks 'View Applicants' button")
    print("\nPlease restart the game to test the fix!")

if __name__ == "__main__":
    apply_fix()
