#!/usr/bin/env python3
"""
UI Test Diagnostics Script for Farming Simulation Game
Tests the interview dialog bug and captures visual evidence
"""
import time
import pygame
import pyautogui
import os
from datetime import datetime

class UIBugDiagnostics:
    def __init__(self):
        self.screenshots_dir = "test_screenshots"
        self.create_screenshots_dir()
        
    def create_screenshots_dir(self):
        """Create directory for test screenshots"""
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
        print(f"Screenshot directory: {self.screenshots_dir}")
    
    def capture_screenshot(self, filename_suffix=""):
        """Capture a screenshot of the current screen"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ui_test_{timestamp}_{filename_suffix}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            print(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            return None
    
    def wait_for_game_startup(self, wait_time=3):
        """Wait for game to fully initialize"""
        print(f"Waiting {wait_time} seconds for game startup...")
        time.sleep(wait_time)
    
    def test_startup_ui_state(self):
        """Test 1: Capture initial UI state at startup"""
        print("\n=== TEST 1: Startup UI State ===")
        self.wait_for_game_startup()
        
        # Capture initial state
        screenshot_path = self.capture_screenshot("startup_initial")
        
        # Try to find the game window and capture it specifically
        try:
            # Look for pygame window (this may vary based on window title)
            game_window = pyautogui.getWindowsWithTitle("Farm Simulation Game")
            if game_window:
                window = game_window[0]
                window.activate()
                time.sleep(0.5)  # Wait for activation
                
                # Capture focused window
                self.capture_screenshot("startup_focused")
                print("Game window found and focused")
                return True
            else:
                print("Game window not found - may have different title")
                return False
        except Exception as e:
            print(f"Error finding game window: {e}")
            return False
    
    def test_dialog_visibility(self):
        """Test 2: Check if interview dialog is visible on startup"""
        print("\n=== TEST 2: Dialog Visibility Test ===")
        
        # Take screenshot to analyze dialog state
        screenshot_path = self.capture_screenshot("dialog_visibility_check")
        
        # Try to detect UI elements that shouldn't be visible
        # This is a visual test - we'll analyze the screenshot
        print("Dialog visibility screenshot captured for analysis")
        
        return screenshot_path
    
    def test_close_button_functionality(self):
        """Test 3: Test if Close buttons are functional"""
        print("\n=== TEST 3: Close Button Functionality ===")
        
        # Try to interact with potential close buttons
        # First capture current state
        self.capture_screenshot("before_close_test")
        
        # Test clicking in areas where close buttons might be
        # (This would need to be adjusted based on actual UI layout)
        test_positions = [
            # Typical close button positions for dialogs
            (700, 400),  # Top right of potential dialog
            (800, 500),  # Alternative close button position
        ]
        
        for i, pos in enumerate(test_positions):
            try:
                print(f"Testing click at position {pos}")
                pyautogui.click(pos)
                time.sleep(0.5)  # Wait for response
                self.capture_screenshot(f"after_click_test_{i+1}")
            except Exception as e:
                print(f"Click test {i+1} failed: {e}")
        
        print("Close button tests completed")
    
    def test_applicant_panel_workflow(self):
        """Test 4: Test normal applicant panel workflow"""
        print("\n=== TEST 4: Applicant Panel Workflow ===")
        
        # Try to access applicant panel through UI
        self.capture_screenshot("before_workflow_test")
        
        # Look for "View Applicants" button and try to click it
        try:
            # This would be in the control panel on the right side
            # Based on UI layout, estimate button position
            view_applicants_pos = (1150, 230)  # Right side panel, Employee section
            
            print("Attempting to click 'View Applicants' button")
            pyautogui.click(view_applicants_pos)
            time.sleep(1)
            
            self.capture_screenshot("after_view_applicants_click")
            
            # Try to generate applicants first
            hire_employee_pos = (1100, 230)  # "Hire Employee" button
            print("Attempting to click 'Hire Employee' button to generate applicants")
            pyautogui.click(hire_employee_pos)
            time.sleep(1)
            
            self.capture_screenshot("after_hire_employee_click")
            
        except Exception as e:
            print(f"Workflow test failed: {e}")
        
        print("Applicant panel workflow test completed")
    
    def run_full_diagnostic(self):
        """Run complete UI diagnostic suite"""
        print("Starting UI Bug Diagnostic Suite for Farming Simulation Game")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Startup UI State
        results['startup'] = self.test_startup_ui_state()
        
        # Test 2: Dialog Visibility
        results['dialog_visibility'] = self.test_dialog_visibility()
        
        # Test 3: Close Button Functionality
        self.test_close_button_functionality()
        
        # Test 4: Applicant Panel Workflow
        self.test_applicant_panel_workflow()
        
        # Final screenshot
        self.capture_screenshot("final_state")
        
        print("\n" + "=" * 60)
        print("UI Diagnostic Suite Completed")
        print(f"Screenshots saved to: {os.path.abspath(self.screenshots_dir)}")
        
        return results

if __name__ == "__main__":
    # Run diagnostics
    diagnostics = UIBugDiagnostics()
    results = diagnostics.run_full_diagnostic()