"""
Employee Management System - Advanced AI & Skills System for AgriFun Agricultural Simulation

This system provides comprehensive employee management with advanced AI, skill systems,
task assignment, and performance tracking. Integrates with the Time Management System
for realistic work schedules and the Economy System for payroll management.

Key Features:
- Advanced AI behavior with state machines and pathfinding
- Skill-based specialization system with experience tracking
- Dynamic task assignment with priority management
- Employee needs system (hunger, thirst, rest, morale)
- Performance analytics and efficiency tracking
- Hiring system with trait-based candidate generation
- Payroll management with skill-based compensation
- Career progression and promotion system

AI Features:
- Multi-state behavior (Idle, Moving, Working, Resting, Breaking)
- A* pathfinding with dynamic obstacle avoidance
- Smart task selection based on skills and proximity
- Collaborative work coordination to prevent conflicts
- Weather-aware behavior adaptations
- Learning system that improves efficiency over time

Integration Features:
- Time-based work schedules with seasonal adjustments
- Economic integration for payroll and hiring costs
- Event-driven communication with other systems
- ECS component-based architecture for flexibility
- Performance optimization for large employee counts

Usage Example:
    # Initialize employee system
    employee_system = EmployeeSystem()
    await employee_system.initialize()
    
    # Hire employees
    candidate_id = employee_system.generate_candidate()
    employee_id = await employee_system.hire_employee(candidate_id)
    
    # Assign tasks
    task_id = await employee_system.assign_task(employee_id, 'harvest', grid_positions)
    
    # Monitor performance
    performance = employee_system.get_employee_performance(employee_id)
"""

import time
import math
import random
import heapq
from typing import Dict, List, Set, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

# Import Phase 1 architecture
from scripts.core.entity_component_system import System, Entity, Component
from scripts.core.advanced_event_system import get_event_system, EventPriority
from scripts.core.time_management import get_time_manager, Season, WeatherType
from scripts.core.advanced_config_system import get_configuration_manager
from scripts.systems.economy_system import get_economy_system


class EmployeeState(Enum):
    """Employee AI states"""
    IDLE = "idle"
    MOVING = "moving"
    WORKING = "working"
    RESTING = "resting"
    BREAKING = "breaking"
    SLEEPING = "sleeping"
    EATING = "eating"
    UNAVAILABLE = "unavailable"


class TaskType(Enum):
    """Types of agricultural tasks"""
    TILL = "till"
    PLANT = "plant"
    WATER = "water"
    HARVEST = "harvest"
    WEED = "weed"
    FERTILIZE = "fertilize"
    INSPECT = "inspect"
    REPAIR = "repair"
    TRANSPORT = "transport"


class SkillType(Enum):
    """Employee skill specializations"""
    FIELD_OPERATIONS = "field_operations"
    CROP_MANAGEMENT = "crop_management"
    EQUIPMENT_OPERATION = "equipment_operation"
    QUALITY_CONTROL = "quality_control"
    MAINTENANCE = "maintenance"
    LOGISTICS = "logistics"
    LEADERSHIP = "leadership"
    SUSTAINABILITY = "sustainability"


class EmployeeTrait(Enum):
    """Employee personality traits"""
    HARDWORKING = "hardworking"
    EFFICIENT = "efficient"
    DETAIL_ORIENTED = "detail_oriented"
    TEAM_PLAYER = "team_player"
    INNOVATIVE = "innovative"
    RELIABLE = "reliable"
    QUICK_LEARNER = "quick_learner"
    WEATHER_RESISTANT = "weather_resistant"
    EARLY_RISER = "early_riser"
    PROBLEM_SOLVER = "problem_solver"


@dataclass
class EmployeeSkill:
    """Individual skill with experience tracking"""
    skill_type: SkillType
    level: int = 1  # 1-10 skill level
    experience: float = 0.0  # Experience points
    efficiency_bonus: float = 0.0  # Efficiency multiplier
    learning_rate: float = 1.0  # How quickly skill improves
    
    def get_efficiency_multiplier(self) -> float:
        """Calculate efficiency multiplier based on skill level"""
        base_efficiency = 0.5 + (self.level * 0.1)  # 0.6 to 1.5
        return base_efficiency + self.efficiency_bonus
    
    def add_experience(self, amount: float):
        """Add experience and potentially level up"""
        self.experience += amount * self.learning_rate
        
        # Check for level up (exponential experience requirements)
        required_exp = (self.level ** 2) * 100
        if self.experience >= required_exp and self.level < 10:
            self.level += 1
            self.efficiency_bonus += 0.05  # 5% bonus per level
            return True  # Leveled up
        return False  # No level up


@dataclass
class EmployeeNeeds:
    """Employee physiological and psychological needs"""
    hunger: float = 100.0  # 0-100, decreases over time
    thirst: float = 100.0  # 0-100, decreases faster than hunger
    rest: float = 100.0    # 0-100, decreases during work
    morale: float = 75.0   # 0-100, affects all performance
    comfort: float = 75.0  # 0-100, affected by weather/conditions
    
    # Need decay rates (per hour)
    hunger_decay_rate: float = 8.0
    thirst_decay_rate: float = 12.0
    rest_decay_rate: float = 15.0
    morale_decay_rate: float = 2.0
    comfort_decay_rate: float = 5.0
    
    def update_needs(self, hours_passed: float, working: bool = False, weather_factor: float = 1.0):
        """Update needs based on time and activity"""
        work_multiplier = 1.5 if working else 1.0
        
        self.hunger = max(0, self.hunger - (self.hunger_decay_rate * hours_passed * work_multiplier))
        self.thirst = max(0, self.thirst - (self.thirst_decay_rate * hours_passed * work_multiplier))
        self.rest = max(0, self.rest - (self.rest_decay_rate * hours_passed * work_multiplier))
        
        # Weather affects comfort and morale
        self.comfort = max(0, min(100, self.comfort - (self.comfort_decay_rate * hours_passed * weather_factor)))
        
        # Low needs affect morale
        need_average = (self.hunger + self.thirst + self.rest + self.comfort) / 4
        if need_average < 50:
            self.morale = max(0, self.morale - (self.morale_decay_rate * hours_passed))
        elif need_average > 80:
            self.morale = min(100, self.morale + (self.morale_decay_rate * hours_passed * 0.5))
    
    def get_effectiveness_multiplier(self) -> float:
        """Calculate how needs affect work effectiveness"""
        # Critical needs have major impact
        critical_factor = 1.0
        if self.hunger < 20: critical_factor *= 0.6
        if self.thirst < 20: critical_factor *= 0.5
        if self.rest < 20: critical_factor *= 0.7
        
        # General needs affect performance
        avg_needs = (self.hunger + self.thirst + self.rest) / 3
        needs_factor = 0.4 + (avg_needs / 100) * 0.6  # 0.4 to 1.0
        
        # Morale affects everything
        morale_factor = 0.5 + (self.morale / 100) * 0.5  # 0.5 to 1.0
        
        return critical_factor * needs_factor * morale_factor


@dataclass
class TaskAssignment:
    """Individual task assignment for an employee"""
    task_id: str
    task_type: TaskType
    grid_positions: List[Tuple[int, int]]
    priority: int = 1  # 1-10, higher is more urgent
    deadline_hours: Optional[float] = None
    assigned_time: int = 0  # Game time when assigned
    started_time: Optional[int] = None
    estimated_duration: float = 1.0  # Hours to complete
    
    # Task progress
    positions_completed: Set[Tuple[int, int]] = field(default_factory=set)
    total_progress: float = 0.0  # 0.0 to 1.0
    quality_score: float = 0.0  # 0.0 to 1.0
    
    # Task requirements
    required_skills: List[SkillType] = field(default_factory=list)
    minimum_skill_level: int = 1
    equipment_required: List[str] = field(default_factory=list)
    
    def get_completion_percentage(self) -> float:
        """Get task completion as percentage"""
        if not self.grid_positions:
            return self.total_progress * 100
        return (len(self.positions_completed) / len(self.grid_positions)) * 100
    
    def is_complete(self) -> bool:
        """Check if task is complete"""
        if self.grid_positions:
            return len(self.positions_completed) >= len(self.grid_positions)
        return self.total_progress >= 1.0


@dataclass
class PathNode:
    """A* pathfinding node"""
    x: int
    y: int
    g_cost: float = 0.0  # Cost from start
    h_cost: float = 0.0  # Heuristic cost to end
    f_cost: float = 0.0  # Total cost
    parent: Optional['PathNode'] = None
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost


@dataclass
class EmployeeCandidate:
    """Job candidate for hiring"""
    candidate_id: str
    name: str
    age: int
    experience_years: int
    
    # Skills (1-10 levels)
    skills: Dict[SkillType, int]
    traits: List[EmployeeTrait]
    
    # Employment terms
    base_wage: float  # Per hour
    signing_bonus: float = 0.0
    contract_length_days: int = 365
    
    # Background
    previous_jobs: List[str] = field(default_factory=list)
    education_level: str = "high_school"
    certifications: List[str] = field(default_factory=list)
    
    def get_overall_rating(self) -> float:
        """Calculate overall candidate rating (0-10)"""
        skill_average = sum(self.skills.values()) / len(self.skills) if self.skills else 1
        trait_bonus = len(self.traits) * 0.2  # 0.2 per trait
        experience_bonus = min(2.0, self.experience_years * 0.2)  # Max 2.0 bonus
        
        return min(10.0, skill_average + trait_bonus + experience_bonus)


class EmployeeSystem(System):
    """Comprehensive employee management and AI system"""
    
    def __init__(self):
        super().__init__()
        self.system_name = "employee_system"
        
        # Core system references
        self.event_system = get_event_system()
        self.time_manager = get_time_manager()
        self.config_manager = get_configuration_manager()
        self.economy_system = get_economy_system()
        
        # Employee data storage
        self.employees: Dict[str, Entity] = {}  # employee_id -> Entity
        self.employee_skills: Dict[str, Dict[SkillType, EmployeeSkill]] = {}
        self.employee_needs: Dict[str, EmployeeNeeds] = {}
        self.employee_states: Dict[str, EmployeeState] = {}
        self.task_assignments: Dict[str, List[TaskAssignment]] = {}  # employee_id -> tasks
        
        # Hiring system
        self.job_candidates: Dict[str, EmployeeCandidate] = {}
        self.hiring_budget: float = 0.0
        self.total_payroll: float = 0.0
        
        # Pathfinding and movement
        self.employee_positions: Dict[str, Tuple[float, float]] = {}
        self.employee_paths: Dict[str, List[Tuple[int, int]]] = {}
        self.movement_speed: float = 2.0  # tiles per second
        self.grid_size: Tuple[int, int] = (16, 16)
        
        # Task coordination
        self.active_tasks: Dict[str, TaskAssignment] = {}  # task_id -> task
        self.task_queue: List[TaskAssignment] = []
        self.occupied_positions: Set[Tuple[int, int]] = set()
        
        # Performance tracking
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        self.daily_productivity: Dict[str, float] = {}
        self.employee_count = 0
        self.tasks_completed_today = 0
        
        # AI configuration
        self.pathfinding_cache: Dict[Tuple[int, int, int, int], List[Tuple[int, int]]] = {}
        self.cache_expiry_time = 0
        self.decision_frequency = 2.0  # Seconds between AI decisions
        self.last_ai_update = 0.0
        
        # Work schedule
        self.work_start_hour = 6  # 6 AM
        self.work_end_hour = 14   # 2 PM (8-hour day)
        self.break_duration = 0.5  # 30 minutes
        self.lunch_hour = 12      # Noon
    
    async def initialize(self):
        """Initialize the employee system"""
        # Load configuration
        await self._load_employee_configuration()
        
        # Subscribe to time events
        self.event_system.subscribe('time_hour_passed', self._on_hour_passed)
        self.event_system.subscribe('time_day_passed', self._on_day_passed)
        self.event_system.subscribe('time_season_changed', self._on_season_changed)
        self.event_system.subscribe('weather_changed', self._on_weather_changed)
        
        # Subscribe to game events
        self.event_system.subscribe('task_created', self._on_task_created)
        self.event_system.subscribe('crop_planted', self._on_crop_planted)
        self.event_system.subscribe('crop_harvested', self._on_crop_harvested)
        
        # Initialize hiring system
        await self._initialize_hiring_system()
        
        self.logger.info("Employee System initialized successfully")
    
    async def _load_employee_configuration(self):
        """Load employee system configuration"""
        try:
            employee_config = self.config_manager.get_section('employees')
            
            # Load AI parameters
            self.movement_speed = employee_config.get('movement_speed', 2.0)
            self.decision_frequency = employee_config.get('decision_frequency', 2.0)
            
            # Load work schedule
            schedule_config = employee_config.get('work_schedule', {})
            self.work_start_hour = schedule_config.get('start_hour', 6)
            self.work_end_hour = schedule_config.get('end_hour', 14)
            self.break_duration = schedule_config.get('break_duration', 0.5)
            
            # Load hiring parameters
            hiring_config = employee_config.get('hiring', {})
            self.hiring_budget = hiring_config.get('initial_budget', 5000.0)
            
        except Exception as e:
            self.logger.warning(f"Failed to load employee configuration: {e}")
    
    async def _initialize_hiring_system(self):
        """Initialize the employee hiring system"""
        # Generate initial job candidates
        await self.generate_candidates(5)
        
        self.logger.info("Hiring system initialized with initial candidates")
    
    async def generate_candidates(self, count: int = 3) -> List[str]:
        """Generate new job candidates"""
        candidate_ids = []
        
        for _ in range(count):
            candidate_id = f"candidate_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Generate candidate data
            candidate = self._generate_random_candidate(candidate_id)
            self.job_candidates[candidate_id] = candidate
            candidate_ids.append(candidate_id)
        
        # Emit candidate generation event
        self.event_system.emit('candidates_generated', {
            'candidate_ids': candidate_ids,
            'total_candidates': len(self.job_candidates)
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Generated {count} new job candidates")
        return candidate_ids
    
    def _generate_random_candidate(self, candidate_id: str) -> EmployeeCandidate:
        """Generate a random job candidate"""
        # Random names
        first_names = [
            "John", "Mary", "James", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
            "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica"
        ]
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"
        ]
        
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        age = random.randint(18, 65)
        experience_years = random.randint(0, min(age - 18, 20))
        
        # Generate skills (higher chance for related skills)
        skills = {}
        primary_skill = random.choice(list(SkillType))
        skills[primary_skill] = random.randint(3, 8)
        
        # Add 2-4 additional skills
        other_skills = [s for s in SkillType if s != primary_skill]
        for skill in random.sample(other_skills, random.randint(2, 4)):
            level = random.randint(1, 6)
            # Related skills tend to be higher
            if self._skills_are_related(primary_skill, skill):
                level += random.randint(0, 2)
            skills[skill] = min(10, level)
        
        # Generate traits (0-3 traits)
        trait_count = random.choices([0, 1, 2, 3], weights=[20, 40, 30, 10])[0]
        traits = random.sample(list(EmployeeTrait), trait_count)
        
        # Calculate base wage based on skills and experience
        skill_avg = sum(skills.values()) / len(skills)
        base_wage = 8.0 + (skill_avg * 2.0) + (experience_years * 0.5)
        base_wage += len(traits) * 1.0  # Trait bonus
        
        # Signing bonus for high-skill candidates
        signing_bonus = 0.0
        if skill_avg > 6:
            signing_bonus = random.randint(500, 2000)
        
        return EmployeeCandidate(
            candidate_id=candidate_id,
            name=name,
            age=age,
            experience_years=experience_years,
            skills=skills,
            traits=traits,
            base_wage=round(base_wage, 2),
            signing_bonus=signing_bonus,
            previous_jobs=self._generate_job_history(experience_years),
            education_level=random.choice(["high_school", "associate", "bachelor", "master"])
        )
    
    def _skills_are_related(self, skill1: SkillType, skill2: SkillType) -> bool:
        """Check if two skills are related"""
        related_groups = [
            {SkillType.FIELD_OPERATIONS, SkillType.CROP_MANAGEMENT, SkillType.EQUIPMENT_OPERATION},
            {SkillType.QUALITY_CONTROL, SkillType.CROP_MANAGEMENT, SkillType.SUSTAINABILITY},
            {SkillType.MAINTENANCE, SkillType.EQUIPMENT_OPERATION},
            {SkillType.LEADERSHIP, SkillType.LOGISTICS}
        ]
        
        for group in related_groups:
            if skill1 in group and skill2 in group:
                return True
        return False
    
    def _generate_job_history(self, years: int) -> List[str]:
        """Generate job history for candidate"""
        if years == 0:
            return []
        
        jobs = [
            "Farm Hand", "Agricultural Technician", "Crop Specialist", "Farm Manager",
            "Equipment Operator", "Quality Inspector", "Logistics Coordinator",
            "Agricultural Consultant", "Maintenance Technician", "Team Lead"
        ]
        
        job_count = min(years // 2, 4)  # Max 4 previous jobs
        return random.sample(jobs, min(job_count, len(jobs)))
    
    async def hire_employee(self, candidate_id: str) -> Optional[str]:
        """Hire a job candidate"""
        if candidate_id not in self.job_candidates:
            self.logger.error(f"Candidate {candidate_id} not found")
            return None
        
        candidate = self.job_candidates[candidate_id]
        
        # Check hiring budget
        total_cost = candidate.signing_bonus
        if total_cost > self.hiring_budget:
            self.logger.warning(f"Insufficient hiring budget for {candidate.name}")
            return None
        
        # Create employee entity
        employee_id = f"employee_{int(time.time())}_{random.randint(1000, 9999)}"
        employee_entity = Entity(employee_id)
        
        # Add basic information to entity
        employee_entity.add_data('name', candidate.name)
        employee_entity.add_data('age', candidate.age)
        employee_entity.add_data('experience_years', candidate.experience_years)
        employee_entity.add_data('base_wage', candidate.base_wage)
        employee_entity.add_data('traits', candidate.traits)
        employee_entity.add_data('hire_date', self.time_manager.get_current_time().total_minutes)
        
        # Convert candidate skills to employee skills
        employee_skills = {}
        for skill_type, level in candidate.skills.items():
            employee_skills[skill_type] = EmployeeSkill(
                skill_type=skill_type,
                level=level,
                experience=level * 50.0,  # Start with some experience
                learning_rate=1.0 + (0.1 * len([t for t in candidate.traits if t == EmployeeTrait.QUICK_LEARNER]))
            )
        
        # Initialize employee data
        self.employees[employee_id] = employee_entity
        self.employee_skills[employee_id] = employee_skills
        self.employee_needs[employee_id] = EmployeeNeeds()
        self.employee_states[employee_id] = EmployeeState.IDLE
        self.task_assignments[employee_id] = []
        self.performance_metrics[employee_id] = {
            'tasks_completed': 0,
            'average_quality': 0.0,
            'efficiency_rating': 1.0,
            'total_hours_worked': 0.0
        }
        
        # Set initial position (near farmhouse)
        self.employee_positions[employee_id] = (8.0, 8.0)  # Center of grid
        self.employee_paths[employee_id] = []
        
        # Process hiring costs
        self.hiring_budget -= total_cost
        self.economy_system.player_cash -= total_cost
        self.employee_count += 1
        
        # Remove from candidates
        del self.job_candidates[candidate_id]
        
        # Emit hiring event
        self.event_system.emit('employee_hired', {
            'employee_id': employee_id,
            'candidate_name': candidate.name,
            'signing_bonus': candidate.signing_bonus,
            'base_wage': candidate.base_wage
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Hired {candidate.name} as {employee_id}")
        return employee_id
    
    async def assign_task(self, employee_id: str, task_type: TaskType, 
                         grid_positions: List[Tuple[int, int]], priority: int = 1) -> Optional[str]:
        """Assign a task to an employee"""
        if employee_id not in self.employees:
            self.logger.error(f"Employee {employee_id} not found")
            return None
        
        task_id = f"task_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create task assignment
        task = TaskAssignment(
            task_id=task_id,
            task_type=task_type,
            grid_positions=grid_positions,
            priority=priority,
            assigned_time=self.time_manager.get_current_time().total_minutes,
            required_skills=self._get_required_skills(task_type),
            estimated_duration=self._estimate_task_duration(task_type, len(grid_positions))
        )
        
        # Add to employee's task list
        self.task_assignments[employee_id].append(task)
        self.active_tasks[task_id] = task
        
        # Sort tasks by priority
        self.task_assignments[employee_id].sort(key=lambda t: t.priority, reverse=True)
        
        # Emit task assignment event
        self.event_system.emit('task_assigned', {
            'employee_id': employee_id,
            'task_id': task_id,
            'task_type': task_type.value,
            'position_count': len(grid_positions),
            'priority': priority
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Assigned {task_type.value} task {task_id} to {employee_id}")
        return task_id
    
    def _get_required_skills(self, task_type: TaskType) -> List[SkillType]:
        """Get required skills for a task type"""
        skill_requirements = {
            TaskType.TILL: [SkillType.FIELD_OPERATIONS, SkillType.EQUIPMENT_OPERATION],
            TaskType.PLANT: [SkillType.CROP_MANAGEMENT, SkillType.FIELD_OPERATIONS],
            TaskType.WATER: [SkillType.CROP_MANAGEMENT],
            TaskType.HARVEST: [SkillType.CROP_MANAGEMENT, SkillType.QUALITY_CONTROL],
            TaskType.WEED: [SkillType.CROP_MANAGEMENT, SkillType.FIELD_OPERATIONS],
            TaskType.FERTILIZE: [SkillType.CROP_MANAGEMENT, SkillType.SUSTAINABILITY],
            TaskType.INSPECT: [SkillType.QUALITY_CONTROL, SkillType.CROP_MANAGEMENT],
            TaskType.REPAIR: [SkillType.MAINTENANCE, SkillType.EQUIPMENT_OPERATION],
            TaskType.TRANSPORT: [SkillType.LOGISTICS, SkillType.EQUIPMENT_OPERATION]
        }
        return skill_requirements.get(task_type, [])
    
    def _estimate_task_duration(self, task_type: TaskType, position_count: int) -> float:
        """Estimate task duration in hours"""
        base_times = {
            TaskType.TILL: 0.2,
            TaskType.PLANT: 0.15,
            TaskType.WATER: 0.1,
            TaskType.HARVEST: 0.25,
            TaskType.WEED: 0.3,
            TaskType.FERTILIZE: 0.2,
            TaskType.INSPECT: 0.1,
            TaskType.REPAIR: 1.0,
            TaskType.TRANSPORT: 0.5
        }
        
        base_time = base_times.get(task_type, 0.2)
        return base_time * position_count
    
    def get_employee_info(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive employee information"""
        if employee_id not in self.employees:
            return None
        
        employee = self.employees[employee_id]
        skills = self.employee_skills[employee_id]
        needs = self.employee_needs[employee_id]
        state = self.employee_states[employee_id]
        tasks = self.task_assignments[employee_id]
        performance = self.performance_metrics[employee_id]
        position = self.employee_positions[employee_id]
        
        return {
            'employee_id': employee_id,
            'name': employee.get_data('name'),
            'age': employee.get_data('age'),
            'experience_years': employee.get_data('experience_years'),
            'base_wage': employee.get_data('base_wage'),
            'traits': [trait.value for trait in employee.get_data('traits', [])],
            'current_state': state.value,
            'position': position,
            'skills': {skill.value: {
                'level': skill_data.level,
                'experience': skill_data.experience,
                'efficiency': skill_data.get_efficiency_multiplier()
            } for skill, skill_data in skills.items()},
            'needs': {
                'hunger': needs.hunger,
                'thirst': needs.thirst,
                'rest': needs.rest,
                'morale': needs.morale,
                'comfort': needs.comfort,
                'effectiveness': needs.get_effectiveness_multiplier()
            },
            'tasks': [{
                'task_id': task.task_id,
                'task_type': task.task_type.value,
                'priority': task.priority,
                'completion': task.get_completion_percentage()
            } for task in tasks],
            'performance': performance
        }
    
    def get_all_employees(self) -> List[Dict[str, Any]]:
        """Get information for all employees"""
        return [self.get_employee_info(emp_id) for emp_id in self.employees.keys()]
    
    def get_available_candidates(self) -> List[Dict[str, Any]]:
        """Get all available job candidates"""
        candidates = []
        for candidate in self.job_candidates.values():
            candidates.append({
                'candidate_id': candidate.candidate_id,
                'name': candidate.name,
                'age': candidate.age,
                'experience_years': candidate.experience_years,
                'skills': {skill.value: level for skill, level in candidate.skills.items()},
                'traits': [trait.value for trait in candidate.traits],
                'base_wage': candidate.base_wage,
                'signing_bonus': candidate.signing_bonus,
                'overall_rating': candidate.get_overall_rating(),
                'previous_jobs': candidate.previous_jobs,
                'education_level': candidate.education_level
            })
        return candidates
    
    async def update(self, delta_time: float):
        """Update employee AI and behaviors"""
        current_time = time.time()
        
        # Update AI at specified frequency
        if current_time - self.last_ai_update >= self.decision_frequency:
            await self._update_employee_ai(delta_time)
            self.last_ai_update = current_time
        
        # Update employee movement
        await self._update_employee_movement(delta_time)
        
        # Update employee needs
        await self._update_employee_needs(delta_time)
    
    async def _update_employee_ai(self, delta_time: float):
        """Update AI decisions for all employees"""
        game_time = self.time_manager.get_current_time()
        current_hour = game_time.hour
        is_work_time = self.work_start_hour <= current_hour < self.work_end_hour
        
        for employee_id in self.employees.keys():
            current_state = self.employee_states[employee_id]
            needs = self.employee_needs[employee_id]
            tasks = self.task_assignments[employee_id]
            
            # Determine next action based on state and conditions
            next_action = await self._decide_employee_action(
                employee_id, current_state, needs, tasks, is_work_time, current_hour
            )
            
            # Execute the decided action
            if next_action != current_state:
                await self._transition_employee_state(employee_id, current_state, next_action)
    
    async def _decide_employee_action(self, employee_id: str, current_state: EmployeeState,
                                    needs: EmployeeNeeds, tasks: List[TaskAssignment],
                                    is_work_time: bool, current_hour: int) -> EmployeeState:
        """Decide the next action for an employee"""
        # Critical needs override work
        if needs.hunger < 15 or needs.thirst < 15:
            return EmployeeState.EATING
        
        if needs.rest < 10:
            return EmployeeState.RESTING
        
        # Work schedule management
        if not is_work_time:
            if current_hour < self.work_start_hour or current_hour >= 22:  # Night time
                return EmployeeState.SLEEPING
            else:
                return EmployeeState.RESTING
        
        # Lunch break
        if current_hour == self.lunch_hour and current_state != EmployeeState.EATING:
            if needs.hunger < 70:
                return EmployeeState.EATING
        
        # Work task selection
        if tasks and is_work_time:
            # Find highest priority incomplete task
            for task in sorted(tasks, key=lambda t: t.priority, reverse=True):
                if not task.is_complete():
                    if current_state == EmployeeState.WORKING:
                        return EmployeeState.WORKING  # Continue current task
                    else:
                        return EmployeeState.MOVING   # Move to task location
        
        # Default to idle if no tasks
        return EmployeeState.IDLE
    
    async def _transition_employee_state(self, employee_id: str, 
                                       from_state: EmployeeState, to_state: EmployeeState):
        """Transition employee from one state to another"""
        self.employee_states[employee_id] = to_state
        
        # Handle state-specific actions
        if to_state == EmployeeState.WORKING:
            await self._start_work_task(employee_id)
        elif to_state == EmployeeState.MOVING:
            await self._start_movement_to_task(employee_id)
        elif to_state == EmployeeState.EATING:
            await self._start_eating_break(employee_id)
        elif to_state == EmployeeState.RESTING:
            await self._start_resting(employee_id)
        
        # Emit state change event
        self.event_system.emit('employee_state_changed', {
            'employee_id': employee_id,
            'from_state': from_state.value,
            'to_state': to_state.value
        }, priority=EventPriority.LOW)
    
    async def _start_work_task(self, employee_id: str):
        """Start working on the current task"""
        tasks = self.task_assignments[employee_id]
        if not tasks:
            return
        
        # Find current task (highest priority incomplete)
        current_task = None
        for task in sorted(tasks, key=lambda t: t.priority, reverse=True):
            if not task.is_complete():
                current_task = task
                break
        
        if not current_task:
            return
        
        # Record task start time
        if current_task.started_time is None:
            current_task.started_time = self.time_manager.get_current_time().total_minutes
        
        # Find next position to work on
        position = self.employee_positions[employee_id]
        next_work_pos = self._find_nearest_work_position(current_task, position)
        
        if next_work_pos:
            # Work on this position
            await self._perform_task_at_position(employee_id, current_task, next_work_pos)
    
    def _find_nearest_work_position(self, task: TaskAssignment, 
                                  current_pos: Tuple[float, float]) -> Optional[Tuple[int, int]]:
        """Find the nearest incomplete work position"""
        incomplete_positions = [pos for pos in task.grid_positions 
                               if pos not in task.positions_completed]
        
        if not incomplete_positions:
            return None
        
        # Find nearest position
        min_distance = float('inf')
        nearest_pos = None
        
        for pos in incomplete_positions:
            if pos not in self.occupied_positions:  # Avoid collision
                distance = math.sqrt((pos[0] - current_pos[0])**2 + (pos[1] - current_pos[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_pos = pos
        
        return nearest_pos
    
    async def _perform_task_at_position(self, employee_id: str, task: TaskAssignment, 
                                      position: Tuple[int, int]):
        """Perform task work at a specific position"""
        skills = self.employee_skills[employee_id]
        needs = self.employee_needs[employee_id]
        
        # Calculate work efficiency
        efficiency = self._calculate_work_efficiency(employee_id, task.task_type, skills, needs)
        
        # Simulate work progress (this would be more complex in a real implementation)
        work_time = 2.0  # Base 2 seconds per position
        work_time /= efficiency  # Efficiency reduces time
        
        # Add position to completed (this would be done after the actual work time)
        task.positions_completed.add(position)
        self.occupied_positions.add(position)
        
        # Update task progress
        if task.grid_positions:
            task.total_progress = len(task.positions_completed) / len(task.grid_positions)
        
        # Calculate quality based on skills and care
        quality = self._calculate_work_quality(employee_id, task.task_type, skills, needs)
        task.quality_score = (task.quality_score + quality) / 2  # Average quality
        
        # Give experience to relevant skills
        for skill_type in task.required_skills:
            if skill_type in skills:
                skills[skill_type].add_experience(5.0)  # 5 XP per task position
        
        # Update performance metrics
        performance = self.performance_metrics[employee_id]
        performance['tasks_completed'] += 1
        performance['average_quality'] = (performance['average_quality'] + quality) / 2
        
        # Check if task is complete
        if task.is_complete():
            await self._complete_task(employee_id, task)
        
        # Remove from occupied positions after work
        if position in self.occupied_positions:
            self.occupied_positions.remove(position)
    
    def _calculate_work_efficiency(self, employee_id: str, task_type: TaskType,
                                 skills: Dict[SkillType, EmployeeSkill], needs: EmployeeNeeds) -> float:
        """Calculate work efficiency for an employee"""
        base_efficiency = 1.0
        
        # Skill-based efficiency
        relevant_skills = self._get_required_skills(task_type)
        if relevant_skills:
            skill_multipliers = []
            for skill_type in relevant_skills:
                if skill_type in skills:
                    skill_multipliers.append(skills[skill_type].get_efficiency_multiplier())
                else:
                    skill_multipliers.append(0.5)  # Penalty for missing skill
            skill_efficiency = sum(skill_multipliers) / len(skill_multipliers)
        else:
            skill_efficiency = 1.0
        
        # Needs-based efficiency
        needs_efficiency = needs.get_effectiveness_multiplier()
        
        # Trait-based efficiency
        employee = self.employees[employee_id]
        traits = employee.get_data('traits', [])
        trait_efficiency = 1.0
        
        if EmployeeTrait.HARDWORKING in traits:
            trait_efficiency *= 1.2
        if EmployeeTrait.EFFICIENT in traits:
            trait_efficiency *= 1.15
        if EmployeeTrait.DETAIL_ORIENTED in traits:
            trait_efficiency *= 1.1
        
        # Weather efficiency (this would use actual weather data)
        weather_efficiency = 1.0
        current_weather = self.time_manager.get_current_weather()
        if current_weather.weather_type in [WeatherType.EXTREME_HEAT, WeatherType.EXTREME_COLD]:
            weather_efficiency = 0.8
            if EmployeeTrait.WEATHER_RESISTANT in traits:
                weather_efficiency = 0.95
        
        return base_efficiency * skill_efficiency * needs_efficiency * trait_efficiency * weather_efficiency
    
    def _calculate_work_quality(self, employee_id: str, task_type: TaskType,
                              skills: Dict[SkillType, EmployeeSkill], needs: EmployeeNeeds) -> float:
        """Calculate work quality (0.0 to 1.0)"""
        base_quality = 0.7
        
        # Skill-based quality
        relevant_skills = self._get_required_skills(task_type)
        if relevant_skills:
            avg_skill_level = sum(skills.get(skill, EmployeeSkill(skill)).level 
                                for skill in relevant_skills) / len(relevant_skills)
            skill_quality = 0.3 + (avg_skill_level / 10) * 0.7  # 0.3 to 1.0
        else:
            skill_quality = 0.7
        
        # Needs affect quality
        needs_quality = 0.5 + (needs.get_effectiveness_multiplier() * 0.5)
        
        # Traits affect quality
        employee = self.employees[employee_id]
        traits = employee.get_data('traits', [])
        trait_quality = 1.0
        
        if EmployeeTrait.DETAIL_ORIENTED in traits:
            trait_quality *= 1.3
        if EmployeeTrait.PROBLEM_SOLVER in traits:
            trait_quality *= 1.2
        
        final_quality = base_quality * skill_quality * needs_quality * trait_quality
        return min(1.0, max(0.0, final_quality))
    
    async def _complete_task(self, employee_id: str, task: TaskAssignment):
        """Handle task completion"""
        # Remove from active tasks
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
        
        # Remove from employee's task list
        if employee_id in self.task_assignments:
            self.task_assignments[employee_id] = [t for t in self.task_assignments[employee_id] 
                                                 if t.task_id != task.task_id]
        
        # Update daily productivity
        if employee_id not in self.daily_productivity:
            self.daily_productivity[employee_id] = 0.0
        self.daily_productivity[employee_id] += len(task.grid_positions)
        
        self.tasks_completed_today += 1
        
        # Emit task completion event
        self.event_system.emit('task_completed', {
            'employee_id': employee_id,
            'task_id': task.task_id,
            'task_type': task.task_type.value,
            'quality_score': task.quality_score,
            'positions_completed': len(task.positions_completed),
            'completion_time': self.time_manager.get_current_time().total_minutes
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Employee {employee_id} completed task {task.task_id}")
    
    async def _start_movement_to_task(self, employee_id: str):
        """Start movement toward the next task"""
        tasks = self.task_assignments[employee_id]
        if not tasks:
            return
        
        # Find current task
        current_task = None
        for task in sorted(tasks, key=lambda t: t.priority, reverse=True):
            if not task.is_complete():
                current_task = task
                break
        
        if not current_task:
            return
        
        # Find path to task
        current_pos = self.employee_positions[employee_id]
        target_pos = self._find_nearest_work_position(current_task, current_pos)
        
        if target_pos:
            path = await self._find_path(
                (int(current_pos[0]), int(current_pos[1])),
                target_pos
            )
            if path:
                self.employee_paths[employee_id] = path
    
    async def _find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """A* pathfinding algorithm"""
        # Check cache first
        cache_key = (start[0], start[1], goal[0], goal[1])
        if cache_key in self.pathfinding_cache:
            return self.pathfinding_cache[cache_key]
        
        if start == goal:
            return [start]
        
        # A* algorithm
        open_set = []
        heapq.heappush(open_set, PathNode(start[0], start[1]))
        
        closed_set = set()
        g_scores = {start: 0}
        
        start_node = PathNode(start[0], start[1])
        start_node.g_cost = 0
        start_node.h_cost = self._heuristic_distance(start, goal)
        start_node.f_cost = start_node.h_cost
        
        open_nodes = {start: start_node}
        
        while open_set:
            current_node = heapq.heappop(open_set)
            current_pos = (current_node.x, current_node.y)
            
            if current_pos == goal:
                # Reconstruct path
                path = []
                node = current_node
                while node:
                    path.append((node.x, node.y))
                    node = node.parent
                path.reverse()
                
                # Cache the path
                self.pathfinding_cache[cache_key] = path
                return path
            
            closed_set.add(current_pos)
            
            # Check neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                neighbor_x = current_node.x + dx
                neighbor_y = current_node.y + dy
                neighbor_pos = (neighbor_x, neighbor_y)
                
                # Check bounds
                if (neighbor_x < 0 or neighbor_x >= self.grid_size[0] or
                    neighbor_y < 0 or neighbor_y >= self.grid_size[1]):
                    continue
                
                # Check if already processed
                if neighbor_pos in closed_set:
                    continue
                
                # Check if occupied (basic obstacle avoidance)
                if neighbor_pos in self.occupied_positions and neighbor_pos != goal:
                    continue
                
                # Calculate costs
                movement_cost = 1.4 if abs(dx) + abs(dy) == 2 else 1.0  # Diagonal cost
                tentative_g = current_node.g_cost + movement_cost
                
                # Create or update neighbor node
                if neighbor_pos not in open_nodes or tentative_g < g_scores.get(neighbor_pos, float('inf')):
                    neighbor_node = PathNode(neighbor_x, neighbor_y)
                    neighbor_node.g_cost = tentative_g
                    neighbor_node.h_cost = self._heuristic_distance(neighbor_pos, goal)
                    neighbor_node.f_cost = neighbor_node.g_cost + neighbor_node.h_cost
                    neighbor_node.parent = current_node
                    
                    g_scores[neighbor_pos] = tentative_g
                    open_nodes[neighbor_pos] = neighbor_node
                    heapq.heappush(open_set, neighbor_node)
        
        # No path found
        return []
    
    def _heuristic_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate heuristic distance between two positions"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    async def _update_employee_movement(self, delta_time: float):
        """Update employee movement along paths"""
        for employee_id, path in list(self.employee_paths.items()):
            if not path:
                continue
            
            current_pos = self.employee_positions[employee_id]
            target_pos = path[0]
            
            # Calculate movement
            dx = target_pos[0] - current_pos[0]
            dy = target_pos[1] - current_pos[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 0.1:  # Reached target
                self.employee_positions[employee_id] = (float(target_pos[0]), float(target_pos[1]))
                path.pop(0)  # Remove reached waypoint
                
                if not path:  # Reached final destination
                    del self.employee_paths[employee_id]
                    # Check if we should start working
                    if self.employee_states[employee_id] == EmployeeState.MOVING:
                        self.employee_states[employee_id] = EmployeeState.WORKING
            else:
                # Move toward target
                move_distance = self.movement_speed * delta_time
                move_ratio = min(1.0, move_distance / distance)
                
                new_x = current_pos[0] + (dx * move_ratio)
                new_y = current_pos[1] + (dy * move_ratio)
                self.employee_positions[employee_id] = (new_x, new_y)
    
    async def _update_employee_needs(self, delta_time: float):
        """Update employee needs over time"""
        hours_passed = delta_time / 3600.0  # Convert seconds to hours
        
        for employee_id, needs in self.employee_needs.items():
            state = self.employee_states[employee_id]
            
            # Update needs based on activity
            is_working = state == EmployeeState.WORKING
            weather_factor = self._get_weather_comfort_factor()
            
            needs.update_needs(hours_passed, working=is_working, weather_factor=weather_factor)
            
            # Handle need satisfaction
            if state == EmployeeState.EATING:
                needs.hunger = min(100, needs.hunger + 30 * hours_passed)
                needs.thirst = min(100, needs.thirst + 20 * hours_passed)
            elif state == EmployeeState.RESTING:
                needs.rest = min(100, needs.rest + 25 * hours_passed)
                needs.morale = min(100, needs.morale + 5 * hours_passed)
            elif state == EmployeeState.SLEEPING:
                needs.rest = min(100, needs.rest + 40 * hours_passed)
    
    def _get_weather_comfort_factor(self) -> float:
        """Get weather comfort factor for needs calculation"""
        current_weather = self.time_manager.get_current_weather()
        comfort_factors = {
            WeatherType.CLEAR: 1.0,
            WeatherType.PARTLY_CLOUDY: 1.0,
            WeatherType.CLOUDY: 1.1,
            WeatherType.LIGHT_RAIN: 1.2,
            WeatherType.HEAVY_RAIN: 1.5,
            WeatherType.STORM: 2.0,
            WeatherType.EXTREME_HEAT: 1.8,
            WeatherType.EXTREME_COLD: 1.7,
            WeatherType.DROUGHT: 1.3,
            WeatherType.SNOW: 1.4,
            WeatherType.FOG: 1.1
        }
        return comfort_factors.get(current_weather.weather_type, 1.0)
    
    async def _start_eating_break(self, employee_id: str):
        """Handle employee eating break"""
        # Move to eating area (simplified - would be a specific location)
        pass
    
    async def _start_resting(self, employee_id: str):
        """Handle employee resting"""
        # Move to rest area
        pass
    
    # Event handlers
    async def _on_hour_passed(self, event_data):
        """Handle hourly updates"""
        # Process payroll
        await self._process_hourly_payroll()
    
    async def _on_day_passed(self, event_data):
        """Handle daily updates"""
        # Reset daily productivity tracking
        self.daily_productivity.clear()
        self.tasks_completed_today = 0
        
        # Generate new candidates occasionally
        if random.random() < 0.3:  # 30% chance per day
            await self.generate_candidates(random.randint(1, 3))
    
    async def _on_season_changed(self, event_data):
        """Handle seasonal changes"""
        new_season = Season(event_data.get('new_season'))
        
        # Adjust work schedules for season
        if new_season in [Season.SPRING, Season.SUMMER]:
            self.work_start_hour = 6
            self.work_end_hour = 16  # Longer summer days
        else:
            self.work_start_hour = 7
            self.work_end_hour = 15  # Shorter winter days
    
    async def _on_weather_changed(self, event_data):
        """Handle weather changes affecting work"""
        weather_type = WeatherType(event_data.get('weather_type'))
        
        # Extreme weather affects all employees
        if weather_type in [WeatherType.STORM, WeatherType.EXTREME_HEAT, WeatherType.EXTREME_COLD]:
            for employee_id in self.employees.keys():
                state = self.employee_states[employee_id]
                if state == EmployeeState.WORKING:
                    # Move to shelter
                    self.employee_states[employee_id] = EmployeeState.RESTING
    
    async def _on_task_created(self, event_data):
        """Handle new task creation events"""
        task_type = event_data.get('task_type')
        grid_positions = event_data.get('grid_positions', [])
        priority = event_data.get('priority', 1)
        
        # Auto-assign to best available employee
        best_employee = self._find_best_employee_for_task(TaskType(task_type))
        if best_employee:
            await self.assign_task(best_employee, TaskType(task_type), grid_positions, priority)
    
    async def _on_crop_planted(self, event_data):
        """Handle crop planting events"""
        # Track planting for experience
        pass
    
    async def _on_crop_harvested(self, event_data):
        """Handle crop harvest events"""
        # Track harvesting for experience
        pass
    
    def _find_best_employee_for_task(self, task_type: TaskType) -> Optional[str]:
        """Find the best available employee for a task"""
        if not self.employees:
            return None
        
        required_skills = self._get_required_skills(task_type)
        best_employee = None
        best_score = 0.0
        
        for employee_id in self.employees.keys():
            # Check availability
            state = self.employee_states[employee_id]
            if state not in [EmployeeState.IDLE, EmployeeState.WORKING]:
                continue
            
            # Check current task load
            current_tasks = len(self.task_assignments[employee_id])
            if current_tasks >= 3:  # Max 3 tasks per employee
                continue
            
            # Calculate skill score
            skills = self.employee_skills[employee_id]
            skill_score = 0.0
            
            if required_skills:
                for skill_type in required_skills:
                    if skill_type in skills:
                        skill_score += skills[skill_type].get_efficiency_multiplier()
                    else:
                        skill_score += 0.3  # Penalty for missing skill
                skill_score /= len(required_skills)
            else:
                skill_score = 1.0
            
            # Factor in needs and availability
            needs = self.employee_needs[employee_id]
            availability_score = needs.get_effectiveness_multiplier()
            
            # Penalize for existing tasks
            task_penalty = current_tasks * 0.2
            
            total_score = (skill_score * availability_score) - task_penalty
            
            if total_score > best_score:
                best_score = total_score
                best_employee = employee_id
        
        return best_employee
    
    async def _process_hourly_payroll(self):
        """Process hourly wage payments"""
        game_time = self.time_manager.get_current_time()
        is_work_time = self.work_start_hour <= game_time.hour < self.work_end_hour
        
        total_wages = 0.0
        
        for employee_id, employee in self.employees.items():
            base_wage = employee.get_data('base_wage', 10.0)
            state = self.employee_states[employee_id]
            
            # Pay for work time
            if is_work_time and state in [EmployeeState.WORKING, EmployeeState.MOVING, 
                                         EmployeeState.BREAKING, EmployeeState.EATING]:
                total_wages += base_wage
                
                # Update performance tracking
                performance = self.performance_metrics[employee_id]
                performance['total_hours_worked'] += 1.0
        
        # Deduct from economy
        if total_wages > 0:
            self.economy_system.player_cash -= total_wages
            self.economy_system.total_expenses += total_wages
            self.total_payroll += total_wages
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive employee system summary"""
        return {
            'total_employees': len(self.employees),
            'available_candidates': len(self.job_candidates),
            'active_tasks': len(self.active_tasks),
            'tasks_completed_today': self.tasks_completed_today,
            'total_payroll': self.total_payroll,
            'hiring_budget': self.hiring_budget,
            'employee_states': {
                state.value: len([emp for emp, emp_state in self.employee_states.items() if emp_state == state])
                for state in EmployeeState
            }
        }
    
    async def shutdown(self):
        """Shutdown the employee system"""
        self.logger.info("Shutting down Employee System")
        
        # Save final performance data
        final_summary = self.get_system_summary()
        
        self.event_system.emit('employee_system_shutdown', {
            'final_summary': final_summary,
            'total_employees': len(self.employees)
        }, priority=EventPriority.HIGH)
        
        self.logger.info("Employee System shutdown complete")


# Global employee system instance
_global_employee_system: Optional[EmployeeSystem] = None

def get_employee_system() -> EmployeeSystem:
    """Get the global employee system instance"""
    global _global_employee_system
    if _global_employee_system is None:
        _global_employee_system = EmployeeSystem()
    return _global_employee_system

def initialize_employee_system() -> EmployeeSystem:
    """Initialize the global employee system"""
    global _global_employee_system
    _global_employee_system = EmployeeSystem()
    return _global_employee_system