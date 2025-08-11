"""
Simple Hiring System - Basic employee hiring without interviews

This system provides a streamlined hiring interface that generates simple applicants
and allows direct hiring without the complexity of the interview system. It integrates
with the existing employee manager and UI systems.

Key Features:
- Generate simple applicants with basic traits
- Direct hiring with cost deduction  
- Integration with economy system for payment
- Clean UI integration via events

Usage:
    hiring_system = SimpleHiringSystem(event_system, economy_manager, employee_manager)
    # System responds to 'generate_applicants_requested' and 'hire_applicant_requested' events
"""

import random
from typing import List, Dict, Any
from dataclasses import dataclass, field
from scripts.core.config import BASE_EMPLOYEE_WAGE


@dataclass
class SimpleApplicant:
    """Simple applicant data structure for basic hiring"""
    id: str  # Unique identifier for this applicant
    name: str  # Employee name (e.g., "Alice Johnson")
    age: int  # Age of the applicant (affects nothing, just for display)
    traits: List[str]  # List of trait names (e.g., ["hard_worker", "runner"])
    hiring_cost: int  # One-time cost to hire this employee
    daily_wage: int  # Daily wage cost for this employee
    personality_type: str  # Personality descriptor for flavor text
    previous_job: str  # Previous work experience for display


class SimpleHiringSystem:
    """Simple hiring system that generates applicants and handles direct hiring"""
    
    def __init__(self, event_system, economy_manager, employee_manager):
        """Initialize the simple hiring system"""
        self.event_system = event_system  # For emitting and receiving events
        self.economy_manager = economy_manager  # For handling hiring costs
        self.employee_manager = employee_manager  # For actually hiring employees
        
        # Current applicant pool
        self.available_applicants: List[SimpleApplicant] = []  # List of current applicants
        self.next_applicant_id = 1  # Counter for unique applicant IDs
        
        # Register for hiring-related events
        self.event_system.subscribe('generate_applicants_requested', self._handle_generate_applicants)
        self.event_system.subscribe('hire_applicant_requested', self._handle_hire_request)
        
        # Possible names for randomly generated applicants
        self.first_names = [
            "Alex", "Blake", "Casey", "Drew", "Emery", "Finley", "Harper", "Jamie", 
            "Kennedy", "Logan", "Morgan", "Parker", "Quinn", "Riley", "Sage", "Taylor"
        ]
        self.last_names = [
            "Anderson", "Brown", "Clark", "Davis", "Evans", "Fisher", "Garcia", "Hill",
            "Johnson", "King", "Lee", "Miller", "Nelson", "Parker", "Roberts", "Smith"
        ]
        
        # Possible traits that applicants can have
        self.available_traits = [
            "hard_worker",  # +10% efficiency, -5% stamina drain (already implemented)
            "runner",       # +10% movement speed (ready to implement)
            "green_thumb",  # Crop-related bonus (future feature)  
            "efficient",    # General efficiency bonus (future feature)
            "resilient"     # Slower needs decay (future feature)
        ]
        
        # Possible previous jobs for flavor text
        self.previous_jobs = [
            "Student", "Retail Worker", "Office Assistant", "Delivery Driver", 
            "Restaurant Server", "Factory Worker", "Construction Helper", "Intern",
            "Farm Hand", "Gardener", "Landscaper", "Warehouse Worker"
        ]
        
        print("Simple Hiring System initialized - Ready to generate applicants")
    
    def _handle_generate_applicants(self, event_data):
        """Generate new applicants when requested"""
        print("DEBUG: Generating new applicants...")
        
        # Clear existing applicants (fresh pool each time)
        self.available_applicants.clear()
        
        # Generate 3-5 random applicants
        num_applicants = random.randint(3, 5)  # Random number between 3 and 5
        
        for i in range(num_applicants):
            applicant = self._create_random_applicant()  # Create one random applicant
            self.available_applicants.append(applicant)  # Add to available pool
        
        print(f"Generated {len(self.available_applicants)} new applicants")
        
        # Emit event to notify UI that applicants are available
        self.event_system.emit('applicants_generated', {
            'applicants': self.available_applicants,  # List of all available applicants
            'count': len(self.available_applicants)   # Total number available
        })
    
    def _create_random_applicant(self) -> SimpleApplicant:
        """Create a single random applicant with realistic attributes"""
        
        # Generate unique ID for this applicant
        applicant_id = f"applicant_{self.next_applicant_id:03d}"  # Format: applicant_001, applicant_002, etc.
        self.next_applicant_id += 1  # Increment counter for next applicant
        
        # Generate random name by combining first and last names
        first_name = random.choice(self.first_names)  # Pick random first name
        last_name = random.choice(self.last_names)    # Pick random last name
        full_name = f"{first_name} {last_name}"       # Combine into full name
        
        # Generate random age between 18 and 45
        age = random.randint(18, 45)
        
        # Randomly assign 1-2 traits to this applicant
        num_traits = random.randint(1, 2)  # Either 1 or 2 traits
        traits = random.sample(self.available_traits, num_traits)  # Pick random traits without duplicates
        
        # Calculate hiring cost based on traits (more traits = higher cost)
        base_hiring_cost = 200  # Base cost to hire any employee
        trait_bonus = len(traits) * 50  # Each trait adds $50 to hiring cost
        hiring_cost = base_hiring_cost + trait_bonus + random.randint(-30, 30)  # Add small random variation
        
        # Calculate daily wage (base wage plus small variation)
        daily_wage = BASE_EMPLOYEE_WAGE + random.randint(-10, 20)  # Small random adjustment to base wage
        
        # Pick random personality type for flavor
        personality_types = ["Friendly", "Professional", "Enthusiastic", "Reliable", "Ambitious"]
        personality = random.choice(personality_types)
        
        # Pick random previous job for background
        previous_job = random.choice(self.previous_jobs)
        
        # Create and return the applicant object
        return SimpleApplicant(
            id=applicant_id,
            name=full_name,
            age=age, 
            traits=traits,
            hiring_cost=hiring_cost,
            daily_wage=daily_wage,
            personality_type=personality,
            previous_job=previous_job
        )
    
    def _handle_hire_request(self, event_data):
        """Handle request to hire a specific applicant"""
        applicant_id = event_data.get('applicant_id', '')  # Get the ID of applicant to hire
        print(f"DEBUG: Hire request received for applicant {applicant_id}")
        
        # Find the requested applicant in our available list
        target_applicant = None
        for applicant in self.available_applicants:
            if applicant.id == applicant_id:  # Found the matching applicant
                target_applicant = applicant
                break
        
        if not target_applicant:
            print(f"ERROR: Applicant {applicant_id} not found in available list")
            self.event_system.emit('hire_failed', {
                'applicant_id': applicant_id,
                'error': 'Applicant not found',
                'applicant_name': 'Unknown'
            })
            return
        
        # Check if player has enough money to afford hiring cost
        current_cash = self.economy_manager.get_current_balance()
        if current_cash < target_applicant.hiring_cost:
            print(f"ERROR: Not enough money to hire {target_applicant.name} - Need ${target_applicant.hiring_cost}, have ${current_cash}")
            self.event_system.emit('hire_failed', {
                'applicant_id': applicant_id,
                'error': 'insufficient_funds',
                'required': target_applicant.hiring_cost,
                'available': current_cash,
                'applicant_name': target_applicant.name
            })
            return
        
        # Deduct hiring cost from player's money
        hire_success = self.economy_manager.spend_money(
            target_applicant.hiring_cost,  # Amount to spend
            f"Hired {target_applicant.name}",  # Transaction description
            "expense"  # Transaction type
        )
        
        if not hire_success:
            print(f"ERROR: Failed to deduct hiring cost for {target_applicant.name}")
            self.event_system.emit('hire_failed', {
                'applicant_id': applicant_id,
                'error': 'payment_failed',
                'applicant_name': target_applicant.name
            })
            return
        
        # Actually hire the employee through the employee manager
        try:
            employee_id = self.employee_manager.hire_employee(
                target_applicant.name,  # Employee name
                target_applicant.traits  # List of traits to apply
            )
            
            # Update the hired employee's daily wage to match applicant's wage
            if employee_id in self.employee_manager.employees:
                hired_employee = self.employee_manager.employees[employee_id]  # Get the employee object
                hired_employee.daily_wage = target_applicant.daily_wage  # Set custom daily wage
            
            print(f"Successfully hired {target_applicant.name} as {employee_id}")
            
            # Remove applicant from available list (they're now hired)
            self.available_applicants.remove(target_applicant)
            
            # Emit success event for UI notification
            self.event_system.emit('employee_hired_successfully', {
                'employee_id': employee_id,
                'applicant_id': applicant_id,
                'applicant_name': target_applicant.name,
                'hiring_cost': target_applicant.hiring_cost,
                'daily_wage': target_applicant.daily_wage,
                'traits': target_applicant.traits
            })
            
        except Exception as e:
            print(f"ERROR: Exception during hiring process: {e}")
            
            # Refund the hiring cost since hiring failed
            self.economy_manager.add_money(
                target_applicant.hiring_cost,  # Refund amount
                f"Refund for failed hire of {target_applicant.name}",  # Transaction description
                "income"  # Transaction type
            )
            
            # Emit failure event
            self.event_system.emit('hire_failed', {
                'applicant_id': applicant_id,
                'error': str(e),
                'applicant_name': target_applicant.name
            })
    
    def get_available_applicants(self) -> List[SimpleApplicant]:
        """Get list of currently available applicants"""
        return self.available_applicants.copy()  # Return copy to prevent external modification
    
    def clear_applicants(self):
        """Clear all current applicants (useful for testing or refresh)"""
        self.available_applicants.clear()  # Remove all applicants from the pool
        print("Cleared all available applicants")
    
    def update(self, dt: float):
        """Update hiring system (currently no time-based updates needed)"""
        pass  # Simple hiring system doesn't need regular updates