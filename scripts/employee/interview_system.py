"""
Interview System - Handles employee recruitment and hiring decisions

This system provides strategic hiring decisions with costs, traits, and applicant variety.
Players must choose between different applicants based on traits, costs, and farm needs.

Key Features:
- Generate random applicants with different traits and costs
- Interview questions that reveal personality
- Strategic hiring decisions with limited budget
- Different employee archetypes (fast, efficient, cheap, etc.)

Design Goals:
- Meaningful hiring choices with tradeoffs
- Personality-based traits that affect gameplay
- Economic decision making (cost vs benefit)
- Replayability through varied applicants

Usage:
    interview_system = InterviewSystem(event_system, economy_manager)
    applicants = interview_system.generate_applicants(3)  # Generate 3 candidates
    interview_system.hire_applicant(applicant_id, employee_manager)
"""

import random
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from scripts.core.config import *


@dataclass
class Applicant:
    """Job applicant with traits, hiring cost, and interview system"""
    id: str
    name: str
    age: int
    traits: List[str]
    hiring_cost: int
    daily_wage: int
    interview_responses: Dict[str, str]
    personality_type: str  # "efficient", "fast", "cheap", "balanced"
    
    # New fields for strategic hiring system
    previous_job: str = "Student"
    applied_for_farm: str = "Farm 1"
    interview_status: str = "not_scheduled"  # not_scheduled, scheduled, completed
    interview_cost: int = 100
    revealed_traits: List[str] = field(default_factory=list)  # Traits revealed through interview
    hidden_traits: List[str] = field(default_factory=list)   # Traits not yet revealed
    cost_multiplier: float = 1.0       # Applied after interview (1.05 = 5% increase)
    expiration_day: int = 0             # Day when candidate leaves (0 = no expiration set)
    interview_scheduled_day: int = 0    # Day interview was scheduled
    
    def __post_init__(self):
        """Initialize field defaults after creation"""
        # Initialize trait hiding system if not already set
        if not self.revealed_traits and not self.hidden_traits:
            # Initially, show only 1-2 traits, hide the rest
            num_to_reveal = min(2, len(self.traits))
            self.revealed_traits = self.traits[:num_to_reveal]
            self.hidden_traits = self.traits[num_to_reveal:]


class InterviewSystem:
    """Manages employee recruitment and hiring"""
    
    def __init__(self, event_system, economy_manager):
        """Initialize interview system"""
        self.event_system = event_system
        self.economy_manager = economy_manager
        
        # Available applicant names
        self.first_names = [
            "Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah",
            "Ivan", "Julia", "Kevin", "Luna", "Marcus", "Nina", "Oliver", "Petra",
            "Quinn", "Rosa", "Steve", "Tara", "Ulrich", "Vera", "Will", "Xara", "Yuki", "Zoe"
        ]
        
        # Trait definitions with gameplay effects
        self.trait_definitions = {
            "hard_worker": {
                "name": "Hard Worker",
                "description": "10% more efficient, 5% less stamina drain",
                "hiring_cost_modifier": 1.3,
                "wage_modifier": 1.2
            },
            "runner": {
                "name": "Runner",
                "description": "10% faster movement speed",
                "hiring_cost_modifier": 1.2,
                "wage_modifier": 1.15
            },
            "cheap_labor": {
                "name": "Budget Worker",
                "description": "Lower wages but 10% slower work",
                "hiring_cost_modifier": 0.7,
                "wage_modifier": 0.8
            },
            "experienced": {
                "name": "Experienced",
                "description": "15% work efficiency, higher cost",
                "hiring_cost_modifier": 1.5,
                "wage_modifier": 1.3
            },
            "young_energy": {
                "name": "Energetic",
                "description": "20% less rest decay, slightly faster",
                "hiring_cost_modifier": 1.1,
                "wage_modifier": 1.1
            },
            "steady_worker": {
                "name": "Steady",
                "description": "Balanced stats, reliable performance",
                "hiring_cost_modifier": 1.0,
                "wage_modifier": 1.0
            }
        }
        
        # Current applicant pool
        self.current_applicants: List[Applicant] = []
        self.next_applicant_id = 1
        
        # Register for events
        self.event_system.subscribe('generate_applicants_requested', self._handle_generate_request)
        self.event_system.subscribe('hire_applicant_requested', self._handle_hire_request)
        self.event_system.subscribe('hire_applicant_by_index', self._handle_hire_by_index)
        self.event_system.subscribe('interview_applicant_requested', self._handle_interview_request)
        self.event_system.subscribe('day_passed', self._handle_day_passed)
        
        # Time integration
        self.current_day = 1  # Will be synced with TimeManager
        
        print("Interview System initialized - Ready to generate job applicants")
    
    def generate_applicants(self, count: int = 3) -> List[Applicant]:
        """Generate a pool of job applicants"""
        print(f"DEBUG: generate_applicants called with count={count}")
        self.current_applicants = []
        
        # Create diverse applicant types for strategic choice
        applicant_types = ["efficient", "fast", "cheap", "balanced"]
        
        for i in range(count):
            applicant_id = f"applicant_{self.next_applicant_id:03d}"
            self.next_applicant_id += 1
            
            # Choose personality type (with some randomization)
            if i < len(applicant_types):
                personality = applicant_types[i]
            else:
                personality = random.choice(applicant_types)
            
            applicant = self._create_applicant(applicant_id, personality)
            self.current_applicants.append(applicant)
        
        # Emit event for UI
        self.event_system.emit('applicants_generated', {
            'applicants': self.current_applicants,
            'count': len(self.current_applicants)
        })
        
        print(f"Generated {count} job applicants for interview")
        return self.current_applicants
    
    def _create_applicant(self, applicant_id: str, personality_type: str) -> Applicant:
        """Create a single applicant with personality-based traits"""
        name = random.choice(self.first_names)
        age = random.randint(18, 55)
        
        # Define personality-based trait combinations
        personality_traits = {
            "efficient": ["hard_worker", "experienced"],
            "fast": ["runner", "young_energy"], 
            "cheap": ["cheap_labor", "steady_worker"],
            "balanced": ["steady_worker", "young_energy"]
        }
        
        # Select traits based on personality (2-4 traits for strategic depth)
        available_traits = personality_traits.get(personality_type, ["steady_worker"])
        # Add some random traits from other categories for variety
        all_trait_keys = list(self.trait_definitions.keys())
        extra_traits = [t for t in all_trait_keys if t not in available_traits]
        
        # Select 2-4 total traits: guaranteed personality traits + random extras
        num_base_traits = len(available_traits)
        num_extra_traits = random.randint(0, min(2, len(extra_traits)))
        
        traits = available_traits.copy()
        if extra_traits and num_extra_traits > 0:
            traits.extend(random.sample(extra_traits, num_extra_traits))
        
        # Calculate costs based on traits
        base_hiring_cost = 200  # Base hiring cost
        base_wage = BASE_EMPLOYEE_WAGE
        
        hiring_cost_multiplier = 1.0
        wage_multiplier = 1.0
        
        for trait in traits:
            trait_data = self.trait_definitions[trait]
            hiring_cost_multiplier *= trait_data["hiring_cost_modifier"]
            wage_multiplier *= trait_data["wage_modifier"]
        
        hiring_cost = int(base_hiring_cost * hiring_cost_multiplier)
        daily_wage = int(base_wage * wage_multiplier)
        
        # Generate interview responses
        responses = self._generate_interview_responses(personality_type, traits)
        
        # Generate previous job based on age and personality
        previous_job = self._generate_previous_job(age, personality_type)
        
        # Set expiration day (candidates stay for 3-5 days)
        days_available = random.randint(3, 5)
        expiration_day = self.current_day + days_available
        
        return Applicant(
            id=applicant_id,
            name=name,
            age=age,
            traits=traits,
            hiring_cost=hiring_cost,
            daily_wage=daily_wage,
            interview_responses=responses,
            personality_type=personality_type,
            previous_job=previous_job,
            applied_for_farm="Farm 1",
            interview_status="not_scheduled",
            interview_cost=100,
            cost_multiplier=1.0,
            expiration_day=expiration_day,
            interview_scheduled_day=0
        )
    
    def _generate_interview_responses(self, personality: str, traits: List[str]) -> Dict[str, str]:
        """Generate personality-consistent interview responses"""
        responses = {}
        
        # Question: Why do you want to work on a farm?
        motivation_responses = {
            "efficient": "I believe in maximizing productivity and doing quality work.",
            "fast": "I love staying active and getting things done quickly!",
            "cheap": "I need steady work and am willing to start at a fair wage.",
            "balanced": "I enjoy outdoor work and want to contribute to the farm's success."
        }
        responses["motivation"] = motivation_responses.get(personality, "I'm looking for honest work.")
        
        # Question: How do you handle hard work?
        work_attitude_responses = {
            "efficient": "I focus on working smart, not just hard. Efficiency is key.",
            "fast": "I thrive on physical challenges and like to stay busy.",
            "cheap": "I'm reliable and will put in the effort needed.",
            "balanced": "I pace myself to maintain consistent quality work."
        }
        responses["work_attitude"] = work_attitude_responses.get(personality, "I do my best every day.")
        
        return responses
    
    def _generate_previous_job(self, age: int, personality: str) -> str:
        """Generate realistic previous job based on age and personality"""
        # Job categories by age ranges
        if age <= 22:
            young_jobs = ["Student", "Intern", "Part-time Retail", "Food Service"]
            return random.choice(young_jobs)
        elif age <= 30:
            entry_jobs = ["Farm Worker", "Construction", "Retail Manager", "Office Assistant", "Factory Worker"]
            return random.choice(entry_jobs)
        elif age <= 45:
            mid_jobs = ["Farm Supervisor", "Equipment Operator", "Small Business Owner", "Factory Supervisor", "Truck Driver"]
            return random.choice(mid_jobs)
        else:
            senior_jobs = ["Retired Farmer", "Former Manager", "Consultant", "Semi-Retired", "Career Change"]
            return random.choice(senior_jobs)
    
    def hire_applicant(self, applicant_id: str, employee_manager) -> bool:
        """Hire a specific applicant if affordable"""
        applicant = None
        for app in self.current_applicants:
            if app.id == applicant_id:
                applicant = app
                break
        
        if not applicant:
            return False
        
        # Check if affordable
        if self.economy_manager.get_current_balance() < applicant.hiring_cost:
            self.event_system.emit('hire_failed', {
                'reason': 'insufficient_funds',
                'applicant_name': applicant.name,
                'required_cost': applicant.hiring_cost,
                'current_balance': self.economy_manager.get_current_balance()
            })
            return False
        
        # Pay hiring cost
        if self.economy_manager.spend_money(applicant.hiring_cost, 
                                          f"Hired {applicant.name}", "hiring"):
            
            # Create new employee through employee manager
            employee_id = employee_manager.hire_employee(applicant.name, applicant.traits)
            
            # Update the employee's wage
            employee = employee_manager.get_employee(employee_id)
            if employee:
                employee.daily_wage = applicant.daily_wage
            
            # Clear applicant pool after hiring
            self.current_applicants = []
            
            # Emit hire success event
            self.event_system.emit('employee_hired_successfully', {
                'applicant_name': applicant.name,
                'employee_id': employee_id,
                'traits': applicant.traits,
                'hiring_cost': applicant.hiring_cost,
                'daily_wage': applicant.daily_wage,
                'remaining_balance': self.economy_manager.get_current_balance()
            })
            
            print(f"Successfully hired {applicant.name} for ${applicant.hiring_cost}")
            return True
        
        return False
    
    def get_current_applicants(self) -> List[Applicant]:
        """Get current applicant pool"""
        return self.current_applicants.copy()
    
    def get_trait_info(self, trait_name: str) -> Dict:
        """Get information about a trait"""
        return self.trait_definitions.get(trait_name, {})
    
    def can_afford_applicant(self, applicant_id: str) -> bool:
        """Check if player can afford to hire an applicant"""
        applicant = None
        for app in self.current_applicants:
            if app.id == applicant_id:
                applicant = app
                break
        
        if not applicant:
            return False
        
        return self.economy_manager.get_current_balance() >= applicant.hiring_cost
    
    def _handle_generate_request(self, event_data):
        """Handle request to generate new applicants"""
        count = event_data.get('count', 3)
        print(f"DEBUG: _handle_generate_request called with count={count}")
        print("DEBUG: This was triggered by 'generate_applicants_requested' event")
        self.generate_applicants(count)
    
    def _handle_hire_request(self, event_data):
        """Handle request to hire a specific applicant"""
        applicant_id = event_data.get('applicant_id')
        
        # For now, emit an event that will be handled by game manager to connect systems
        # This avoids passing managers through events
        if applicant_id:
            self.event_system.emit('hire_applicant_confirmed', {
                'applicant_id': applicant_id
            })
    
    def _handle_hire_by_index(self, event_data):
        """Handle hiring by applicant index (keyboard shortcut)"""
        index = event_data.get('index', 0)
        
        if 0 <= index < len(self.current_applicants):
            applicant = self.current_applicants[index]
            print(f"Hiring applicant #{index + 1}: {applicant.name}")
            
            self.event_system.emit('hire_applicant_confirmed', {
                'applicant_id': applicant.id
            })
        else:
            print(f"No applicant at index {index + 1}. Generate applicants first!")
    
    def _handle_interview_request(self, event_data):
        """Handle request to schedule an interview"""
        applicant_id = event_data.get('applicant_id')
        
        if not applicant_id:
            return
        
        # Find the applicant
        applicant = None
        for app in self.current_applicants:
            if app.id == applicant_id:
                applicant = app
                break
        
        if not applicant:
            print(f"Applicant {applicant_id} not found for interview")
            return
        
        # Check if interview can be afforded
        if self.economy_manager.get_current_balance() < applicant.interview_cost:
            self.event_system.emit('hire_failed', {
                'reason': 'insufficient_funds',
                'applicant_name': applicant.name,
                'required_cost': applicant.interview_cost,
                'current_balance': self.economy_manager.get_current_balance()
            })
            return
        
        # Pay interview cost
        if self.economy_manager.spend_money(applicant.interview_cost, 
                                          f"Interview with {applicant.name}", "interview"):
            # Schedule the interview
            applicant.interview_status = "scheduled"
            applicant.interview_scheduled_day = self.current_day
            
            print(f"Interview scheduled with {applicant.name} for $100 - results tomorrow at 6 AM")
            
            # Emit success event
            self.event_system.emit('interview_scheduled', {
                'applicant_name': applicant.name,
                'interview_cost': applicant.interview_cost,
                'results_available_day': self.current_day + 1,
                'scheduled_day': self.current_day
            })
        else:
            print(f"Failed to pay for interview with {applicant.name}")
    
    def update(self, dt: float):
        """Update interview system (future: applicant refresh, etc.)"""
        # Future implementation: periodic new applicants, seasonal hiring bonuses
        pass
    
    def get_save_data(self) -> Dict:
        """Get interview system state for saving"""
        save_data = {
            'next_applicant_id': self.next_applicant_id,
            'current_applicants': []
        }
        
        # Convert current applicants to dict format for JSON serialization
        for applicant in self.current_applicants:
            save_data['current_applicants'].append(asdict(applicant))
        
        return save_data
    
    def load_save_data(self, save_data: Dict):
        """Load interview system state from save data"""
        if not save_data:
            return
        
        # Restore applicant ID counter
        self.next_applicant_id = save_data.get('next_applicant_id', self.next_applicant_id)
        
        # Restore current applicants
        self.current_applicants = []
        for applicant_data in save_data.get('current_applicants', []):
            # Convert dict back to Applicant object
            applicant = Applicant(**applicant_data)
            self.current_applicants.append(applicant)
        
        print(f"Interview system loaded: {len(self.current_applicants)} applicants, next ID: {self.next_applicant_id}")
    
    def save_to_file(self, filepath: str):
        """Save interview system state to file"""
        try:
            save_data = self.get_save_data()
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            print(f"Interview system saved to {filepath}")
        except Exception as e:
            print(f"Failed to save interview system: {e}")
    
    def load_from_file(self, filepath: str):
        """Load interview system state from file"""
        try:
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            self.load_save_data(save_data)
        except FileNotFoundError:
            print(f"No interview save file found at {filepath} - starting fresh")
        except Exception as e:
            print(f"Failed to load interview system: {e}")
    
    def clear_expired_applicants(self, current_day: int):
        """Remove applicants who have expired"""
        initial_count = len(self.current_applicants)
        self.current_applicants = [
            app for app in self.current_applicants 
            if app.expiration_day == 0 or app.expiration_day > current_day
        ]
        
        removed_count = initial_count - len(self.current_applicants)
        if removed_count > 0:
            print(f"Removed {removed_count} expired applicants")
            
            # Emit event for UI update
            self.event_system.emit('applicants_expired', {
                'removed_count': removed_count,
                'remaining_count': len(self.current_applicants)
            })
    
    def _handle_day_passed(self, event_data):
        """Handle day progression for interview scheduling"""
        new_day = event_data.get('day', self.current_day + 1)
        self.current_day = new_day
        
        # Process scheduled interviews that are ready
        interviews_ready = []
        for applicant in self.current_applicants:
            if (applicant.interview_status == "scheduled" and 
                applicant.interview_scheduled_day > 0 and
                new_day > applicant.interview_scheduled_day):
                interviews_ready.append(applicant)
        
        if interviews_ready:
            self._process_ready_interviews(interviews_ready)
        
        # Clear expired applicants
        self.clear_expired_applicants(new_day)
    
    def _process_ready_interviews(self, ready_applicants):
        """Process interviews that are ready (next day at 6 AM)"""
        for applicant in ready_applicants:
            # Mark interview as completed
            applicant.interview_status = "completed"
            
            # Reveal all hidden traits and increase cost by 5%
            if applicant.hidden_traits:
                # Move all hidden traits to revealed traits
                applicant.revealed_traits.extend(applicant.hidden_traits)
                applicant.hidden_traits.clear()
                
                # Increase cost by 5% for the interview
                applicant.cost_multiplier = 1.05
                applicant.hiring_cost = int(applicant.hiring_cost * 1.05)
                applicant.daily_wage = int(applicant.daily_wage * 1.05)
                
                print(f"Interview complete for {applicant.name}: All traits revealed, costs increased by 5%")
            
            # Emit event for UI notification
            self.event_system.emit('interview_results_ready', {
                'applicant_name': applicant.name,
                'applicant_id': applicant.id,
                'traits_revealed': len(applicant.traits) - len(applicant.revealed_traits) if hasattr(applicant, 'revealed_traits') else 0
            })
        
        if ready_applicants:
            print(f"{len(ready_applicants)} interview results are now available!")
    
    def set_current_day(self, day: int):
        """Sync current day with TimeManager"""
        self.current_day = day