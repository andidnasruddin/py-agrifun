"""
Employee Management System - Advanced Workforce AI for AgriFun Agricultural Simulation

This system provides comprehensive employee management with intelligent AI, skill progression,
task assignment, and workforce coordination. Integrates with Time Management for work schedules
and Economy System for payroll and hiring costs.

Key Features:
- Advanced employee AI with state machines and pathfinding
- Comprehensive skill system with specializations and progression
- Intelligent task assignment and work coordination
- Employee needs management (hunger, thirst, rest, morale)
- Dynamic hiring system with applicant generation
- Performance tracking and efficiency calculations
- Seasonal workforce adjustments
- Multi-employee coordination and collision avoidance
"""

import time
import math
import random
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

# Import foundation systems
from ..core.event_system import get_global_event_system, EventPriority
from ..core.entity_component_system import get_entity_manager
from ..core.configuration_system import get_configuration_manager
from ..core.state_management import get_state_manager
from ..core.advanced_grid_system import get_grid_system, GridLayer
from ..systems.time_system import get_time_system, Season, TimeOfDay
from ..systems.economy_system import get_economy_system, TransactionType


class EmployeeState(Enum):
    """Employee AI states"""
    IDLE = "idle"
    MOVING = "moving"
    WORKING = "working"
    RESTING = "resting"
    EATING = "eating"
    UNAVAILABLE = "unavailable"
    OFF_DUTY = "off_duty"


class TaskType(Enum):
    """Types of tasks employees can perform"""
    TILL_FIELD = "till_field"
    PLANT_CROPS = "plant_crops"
    WATER_CROPS = "water_crops"
    HARVEST_CROPS = "harvest_crops"
    TEND_CROPS = "tend_crops"
    OPERATE_EQUIPMENT = "operate_equipment"
    TRANSPORT_GOODS = "transport_goods"
    MAINTAIN_BUILDINGS = "maintain_buildings"
    GENERAL_LABOR = "general_labor"


class SkillType(Enum):
    """Employee skill categories"""
    FARMING = "farming"
    EQUIPMENT_OPERATION = "equipment"
    CROP_MANAGEMENT = "crops"
    LIVESTOCK = "livestock"
    MANAGEMENT = "management"
    MAINTENANCE = "maintenance"
    QUALITY_CONTROL = "quality"
    EFFICIENCY = "efficiency"


class EmployeeTrait(Enum):
    """Natural employee traits affecting performance"""
    HARDWORKING = "hardworking"
    METICULOUS = "meticulous"
    QUICK_LEARNER = "quick_learner"
    TEAM_PLAYER = "team_player"
    WEATHER_RESISTANT = "weather_resistant"
    EARLY_RISER = "early_riser"
    NIGHT_OWL = "night_owl"
    INNOVATIVE = "innovative"
    RELIABLE = "reliable"
    PERFECTIONIST = "perfectionist"


@dataclass
class EmployeeSkill:
    """Employee skill with experience and level"""
    skill_type: SkillType
    level: int = 1
    experience: float = 0.0
    experience_to_next: float = 100.0
    
    def add_experience(self, points: float) -> bool:
        """Add experience points, return True if leveled up"""
        self.experience += points
        
        if self.experience >= self.experience_to_next:
            self.level += 1
            self.experience -= self.experience_to_next
            self.experience_to_next = self.level * 100.0
            return True
        
        return False
    
    def get_efficiency_modifier(self) -> float:
        """Get efficiency modifier from skill level"""
        return 1.0 + (self.level - 1) * 0.1


@dataclass
class EmployeeStats:
    """Employee physical and mental statistics"""
    hunger: float = 100.0
    thirst: float = 100.0
    rest: float = 100.0
    morale: float = 100.0
    energy: float = 100.0
    health: float = 100.0
    work_speed_modifier: float = 1.0
    quality_modifier: float = 1.0
    
    def update_needs(self, delta_time: float, working: bool = False):
        """Update employee needs over time"""
        time_factor = delta_time / 3600.0
        
        if working:
            self.hunger -= 15.0 * time_factor
            self.thirst -= 20.0 * time_factor
            self.energy -= 25.0 * time_factor
            self.rest -= 10.0 * time_factor
        else:
            self.hunger -= 8.0 * time_factor
            self.thirst -= 12.0 * time_factor
            self.energy -= 5.0 * time_factor
            self.rest += 20.0 * time_factor
        
        # Clamp values
        self.hunger = max(0.0, min(100.0, self.hunger))
        self.thirst = max(0.0, min(100.0, self.thirst))
        self.rest = max(0.0, min(100.0, self.rest))
        self.energy = max(0.0, min(100.0, self.energy))
        
        # Update morale and performance
        avg_needs = (self.hunger + self.thirst + self.rest + self.energy) / 4.0
        self.morale = (self.morale * 0.9) + (avg_needs * 0.1)
        
        need_factor = avg_needs / 100.0
        self.work_speed_modifier = 0.5 + (need_factor * 0.5)
        self.quality_modifier = 0.7 + (need_factor * 0.3)
    
    def can_work_effectively(self) -> bool:
        """Check if employee can work at reasonable efficiency"""
        return self.energy > 20.0 and self.hunger > 15.0 and self.thirst > 15.0
    
    def needs_break(self) -> bool:
        """Check if employee urgently needs a break"""
        return (self.hunger < 30.0 or self.thirst < 25.0 or 
                self.energy < 15.0 or self.rest < 20.0)


@dataclass
class EmployeeTask:
    """Task assigned to an employee"""
    task_id: str
    task_type: TaskType
    target_location: Tuple[int, int]
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    estimated_duration: float = 60.0
    progress: float = 0.0
    assigned_time: int = 0
    
    def is_complete(self) -> bool:
        """Check if task is complete"""
        return self.progress >= 1.0
    
    def get_completion_percentage(self) -> int:
        """Get completion as percentage"""
        return int(self.progress * 100)


@dataclass
class Employee:
    """Complete employee with AI, skills, and stats"""
    employee_id: str
    name: str
    
    # Position and movement
    x: float = 8.0
    y: float = 8.0
    target_x: float = 8.0
    target_y: float = 8.0
    movement_speed: float = 2.0
    
    # AI state
    state: EmployeeState = EmployeeState.IDLE
    current_task: Optional[EmployeeTask] = None
    task_queue: List[EmployeeTask] = field(default_factory=list)
    
    # Skills and traits
    skills: Dict[SkillType, EmployeeSkill] = field(default_factory=dict)
    traits: List[EmployeeTrait] = field(default_factory=list)
    
    # Statistics
    stats: EmployeeStats = field(default_factory=EmployeeStats)
    
    # Employment details
    daily_wage: float = 50.0
    hire_date: int = 0
    last_payment_date: int = 0
    performance_rating: float = 1.0
    
    # Work tracking
    hours_worked_today: float = 0.0
    tasks_completed_today: int = 0
    last_work_time: int = 0
    
    def get_skill_level(self, skill_type: SkillType) -> int:
        """Get skill level for specific skill"""
        if skill_type in self.skills:
            return self.skills[skill_type].level
        return 0
    
    def has_trait(self, trait: EmployeeTrait) -> bool:
        """Check if employee has specific trait"""
        return trait in self.traits
    
    def get_work_efficiency(self) -> float:
        """Calculate overall work efficiency"""
        base_efficiency = 1.0
        base_efficiency *= self.stats.work_speed_modifier
        
        if self.has_trait(EmployeeTrait.HARDWORKING):
            base_efficiency *= 1.2
        if self.has_trait(EmployeeTrait.PERFECTIONIST):
            base_efficiency *= 0.9
        
        base_efficiency *= self.performance_rating
        return base_efficiency
    
    def get_work_quality(self) -> float:
        """Calculate work quality output"""
        base_quality = 1.0
        base_quality *= self.stats.quality_modifier
        
        if self.has_trait(EmployeeTrait.METICULOUS):
            base_quality *= 1.15
        if self.has_trait(EmployeeTrait.PERFECTIONIST):
            base_quality *= 1.25
        
        return base_quality
    
    def add_skill_experience(self, skill_type: SkillType, points: float):
        """Add experience to a skill"""
        if skill_type not in self.skills:
            self.skills[skill_type] = EmployeeSkill(skill_type)
        
        if self.has_trait(EmployeeTrait.QUICK_LEARNER):
            points *= 1.5
        
        leveled_up = self.skills[skill_type].add_experience(points)
        return leveled_up
    
    def can_work_now(self, current_time_of_day: TimeOfDay) -> bool:
        """Check if employee can work at current time"""
        work_hours = [TimeOfDay.MORNING, TimeOfDay.MID_MORNING, 
                     TimeOfDay.AFTERNOON, TimeOfDay.LATE_AFTERNOON]
        
        if self.has_trait(EmployeeTrait.EARLY_RISER):
            work_hours.append(TimeOfDay.EARLY_MORNING)
        
        if self.has_trait(EmployeeTrait.NIGHT_OWL):
            work_hours.append(TimeOfDay.EVENING)
        
        return current_time_of_day in work_hours and self.stats.can_work_effectively()
    
    def get_distance_to(self, x: float, y: float) -> float:
        """Calculate distance to target location"""
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
    
    def move_towards(self, target_x: float, target_y: float, delta_time: float) -> bool:
        """Move towards target, return True if reached"""
        distance = self.get_distance_to(target_x, target_y)
        
        if distance < 0.1:
            self.x = target_x
            self.y = target_y
            return True
        
        move_distance = self.movement_speed * delta_time
        if move_distance >= distance:
            self.x = target_x
            self.y = target_y
            return True
        else:
            direction_x = (target_x - self.x) / distance
            direction_y = (target_y - self.y) / distance
            
            self.x += direction_x * move_distance
            self.y += direction_y * move_distance
            return False


class EmployeeSystem:
    """Main employee management system"""
    
    def __init__(self):
        # Core systems
        self.event_system = get_global_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_configuration_manager()
        self.state_manager = get_state_manager()
        self.time_system = get_time_system()
        self.economy_system = get_economy_system()
        self.grid_system = get_grid_system()
        
        # Employee management
        self.employees: Dict[str, Employee] = {}
        self.available_applicants: Dict[str, Employee] = {}
        self.employee_counter = 0
        self.applicant_counter = 0
        
        # Task management
        self.active_tasks: Dict[str, EmployeeTask] = {}
        self.task_counter = 0
        
        # Hiring system
        self.hiring_cost_base = 100.0
        self.daily_wage_base = 50.0
        
        self.logger = logging.getLogger('EmployeeSystem')
        
        # Load configuration
        self._load_configuration()
        
        # Subscribe to events
        self._subscribe_to_events()
        
        # Initialize system
        self._initialize_system()
    
    def _load_configuration(self):
        """Load employee system configuration"""
        default_config = {
            'employees.max_employees': 10,
            'employees.base_daily_wage': 50.0,
            'employees.hiring_cost_base': 100.0,
            'employees.skill_gain_rate': 1.0,
            'employees.needs_decay_rate': 1.0,
            'employees.work_hours_per_day': 8.0
        }
        
        for key, value in default_config.items():
            if self.config_manager.get(key) is None:
                self.config_manager.set(key, value)
    
    def _subscribe_to_events(self):
        """Subscribe to relevant system events"""
        self.event_system.subscribe('day_changed', self._on_day_changed)
        self.event_system.subscribe('hour_changed', self._on_hour_changed)
        self.event_system.subscribe('season_changed', self._on_season_changed)
    
    def _initialize_system(self):
        """Initialize employee system"""
        self._generate_applicants(3)
        self.logger.info("Employee system initialized")
    
    def generate_applicants(self, count: int = 3) -> List[str]:
        """Generate new job applicants"""
        return self._generate_applicants(count)
    
    def _generate_applicants(self, count: int) -> List[str]:
        """Internal method to generate applicants"""
        first_names = ["Alex", "Jordan", "Casey", "Taylor", "Morgan", "Riley", "Avery", "Quinn"]
        last_names = ["Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
        
        applicant_ids = []
        
        for _ in range(count):
            self.applicant_counter += 1
            applicant_id = f"applicant_{self.applicant_counter:03d}"
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            
            applicant = Employee(
                employee_id=applicant_id,
                name=name,
                daily_wage=random.uniform(40.0, 80.0),
                movement_speed=random.uniform(1.5, 2.5)
            )
            
            # Generate random skills
            num_skills = random.randint(1, 3)
            for _ in range(num_skills):
                skill_type = random.choice(list(SkillType))
                level = random.randint(1, 5)
                applicant.skills[skill_type] = EmployeeSkill(
                    skill_type=skill_type,
                    level=level,
                    experience=level * 50.0
                )
            
            # Generate random traits
            num_traits = random.randint(0, 2)
            available_traits = list(EmployeeTrait)
            for _ in range(num_traits):
                if available_traits:
                    trait = random.choice(available_traits)
                    applicant.traits.append(trait)
                    available_traits.remove(trait)
            
            self.available_applicants[applicant_id] = applicant
            applicant_ids.append(applicant_id)
        
        self.logger.info(f"Generated {count} new applicants")
        return applicant_ids
    
    def get_applicant_info(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an applicant"""
        if applicant_id not in self.available_applicants:
            return None
        
        applicant = self.available_applicants[applicant_id]
        
        return {
            'applicant_id': applicant_id,
            'name': applicant.name,
            'daily_wage': applicant.daily_wage,
            'skills': {skill.skill_type.value: skill.level for skill in applicant.skills.values()},
            'traits': [trait.value for trait in applicant.traits],
            'estimated_efficiency': applicant.get_work_efficiency(),
            'estimated_quality': applicant.get_work_quality()
        }
    
    def hire_employee(self, applicant_id: str) -> Dict[str, Any]:
        """Hire an applicant as an employee"""
        if applicant_id not in self.available_applicants:
            return {'success': False, 'message': 'Applicant not found'}
        
        max_employees = self.config_manager.get('employees.max_employees', 10)
        if len(self.employees) >= max_employees:
            return {'success': False, 'message': 'Maximum employee capacity reached'}
        
        applicant = self.available_applicants[applicant_id]
        hiring_cost = self.hiring_cost_base + (applicant.daily_wage * 2)
        
        if self.economy_system.current_cash < hiring_cost:
            return {'success': False, 'message': 'Insufficient funds for hiring'}
        
        # Hire the applicant
        self.employee_counter += 1
        employee_id = f"employee_{self.employee_counter:03d}"
        
        employee = applicant
        employee.employee_id = employee_id
        employee.hire_date = self.time_system.get_current_time().total_minutes
        employee.last_payment_date = employee.hire_date
        
        self.employees[employee_id] = employee
        del self.available_applicants[applicant_id]
        
        # Pay hiring cost
        transaction_id = self.economy_system.add_transaction(
            TransactionType.OPERATING_EXPENSE,
            -hiring_cost,
            f"Hired employee: {employee.name}",
            metadata={'employee_id': employee_id, 'hiring_cost': hiring_cost}
        )
        
        self.logger.info(f"Hired employee: {employee.name} for ${hiring_cost:.2f}")
        
        return {
            'success': True,
            'employee_id': employee_id,
            'hiring_cost': hiring_cost,
            'transaction_id': transaction_id
        }
    
    def assign_task(self, employee_id: str, task_type: TaskType, 
                   target_location: Tuple[int, int], 
                   parameters: Dict[str, Any] = None,
                   priority: int = 1) -> Dict[str, Any]:
        """Assign a task to an employee"""
        if employee_id not in self.employees:
            return {'success': False, 'message': 'Employee not found'}
        
        employee = self.employees[employee_id]
        
        self.task_counter += 1
        task_id = f"task_{self.task_counter:06d}"
        
        estimated_duration = self._estimate_task_duration(employee, task_type, parameters or {})
        
        task = EmployeeTask(
            task_id=task_id,
            task_type=task_type,
            target_location=target_location,
            parameters=parameters or {},
            priority=priority,
            estimated_duration=estimated_duration,
            assigned_time=self.time_system.get_current_time().total_minutes
        )
        
        employee.task_queue.append(task)
        employee.task_queue.sort(key=lambda t: t.priority, reverse=True)
        
        self.active_tasks[task_id] = task
        
        self.logger.info(f"Assigned {task_type.value} task to {employee.name}")
        
        return {
            'success': True,
            'task_id': task_id,
            'estimated_duration': estimated_duration
        }
    
    def update_employees(self, delta_time: float):
        """Update all employees (called each game tick)"""
        current_time = self.time_system.get_current_time()
        current_time_of_day = current_time.get_time_of_day()
        
        for employee_id, employee in self.employees.items():
            self._update_employee(employee, delta_time, current_time_of_day)
    
    def _update_employee(self, employee: Employee, delta_time: float, 
                        current_time_of_day: TimeOfDay):
        """Update individual employee"""
        is_working = employee.state == EmployeeState.WORKING
        employee.stats.update_needs(delta_time, is_working)
        
        if employee.stats.needs_break() and employee.state == EmployeeState.WORKING:
            self._send_employee_on_break(employee)
            return
        
        if not employee.can_work_now(current_time_of_day):
            if employee.state not in [EmployeeState.OFF_DUTY, EmployeeState.RESTING]:
                employee.state = EmployeeState.OFF_DUTY
            return
        
        # Employee AI state machine
        if employee.state == EmployeeState.IDLE:
            self._handle_idle_state(employee)
        elif employee.state == EmployeeState.MOVING:
            self._handle_moving_state(employee, delta_time)
        elif employee.state == EmployeeState.WORKING:
            self._handle_working_state(employee, delta_time)
        elif employee.state == EmployeeState.RESTING:
            self._handle_resting_state(employee, delta_time)
        elif employee.state == EmployeeState.EATING:
            self._handle_eating_state(employee, delta_time)
        elif employee.state == EmployeeState.OFF_DUTY:
            employee.stats.rest = min(100.0, employee.stats.rest + 30.0 * (delta_time / 3600.0))
    
    def _handle_idle_state(self, employee: Employee):
        """Handle employee in idle state"""
        if employee.task_queue:
            next_task = employee.task_queue.pop(0)
            employee.current_task = next_task
            
            employee.target_x = next_task.target_location[0]
            employee.target_y = next_task.target_location[1]
            employee.state = EmployeeState.MOVING
    
    def _handle_moving_state(self, employee: Employee, delta_time: float):
        """Handle employee moving to work location"""
        if employee.current_task is None:
            employee.state = EmployeeState.IDLE
            return
        
        reached = employee.move_towards(employee.target_x, employee.target_y, delta_time)
        
        if reached:
            employee.state = EmployeeState.WORKING
    
    def _handle_working_state(self, employee: Employee, delta_time: float):
        """Handle employee working on task"""
        if employee.current_task is None:
            employee.state = EmployeeState.IDLE
            return
        
        task = employee.current_task
        
        efficiency = employee.get_work_efficiency()
        base_progress_rate = 1.0 / (task.estimated_duration * 60.0)
        actual_progress_rate = base_progress_rate * efficiency
        
        task.progress += actual_progress_rate * delta_time
        
        relevant_skill = self._get_relevant_skill_for_task(task.task_type)
        if relevant_skill:
            experience_gain = 2.0 * delta_time
            leveled_up = employee.add_skill_experience(relevant_skill, experience_gain)
            
            if leveled_up:
                self.logger.info(f"{employee.name} leveled up {relevant_skill.value} skill!")
        
        employee.hours_worked_today += delta_time / 3600.0
        employee.last_work_time = self.time_system.get_current_time().total_minutes
        
        if task.is_complete():
            self._complete_task(employee, task)
    
    def _handle_resting_state(self, employee: Employee, delta_time: float):
        """Handle employee resting/taking break"""
        recovery_rate = 50.0 * (delta_time / 3600.0)
        employee.stats.rest = min(100.0, employee.stats.rest + recovery_rate)
        employee.stats.energy = min(100.0, employee.stats.energy + recovery_rate * 0.7)
        
        if employee.stats.rest > 70.0 and employee.stats.energy > 60.0:
            employee.state = EmployeeState.IDLE
    
    def _handle_eating_state(self, employee: Employee, delta_time: float):
        """Handle employee eating/drinking"""
        recovery_rate = 80.0 * (delta_time / 3600.0)
        employee.stats.hunger = min(100.0, employee.stats.hunger + recovery_rate)
        employee.stats.thirst = min(100.0, employee.stats.thirst + recovery_rate)
        
        if employee.stats.hunger > 80.0 and employee.stats.thirst > 80.0:
            employee.state = EmployeeState.IDLE
    
    def _send_employee_on_break(self, employee: Employee):
        """Send employee on appropriate break"""
        if employee.stats.hunger < 30.0 or employee.stats.thirst < 25.0:
            employee.state = EmployeeState.EATING
        else:
            employee.state = EmployeeState.RESTING
    
    def _complete_task(self, employee: Employee, task: EmployeeTask):
        """Complete a task and clean up"""
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
        
        employee.current_task = None
        employee.state = EmployeeState.IDLE
        employee.tasks_completed_today += 1
        
        work_quality = employee.get_work_quality()
        work_efficiency = employee.get_work_efficiency()
        
        performance_score = (work_quality + work_efficiency) / 2.0
        employee.performance_rating = (employee.performance_rating * 0.95) + (performance_score * 0.05)
        
        self.logger.info(f"{employee.name} completed task: {task.task_type.value}")
    
    def _estimate_task_duration(self, employee: Employee, task_type: TaskType, 
                               parameters: Dict[str, Any]) -> float:
        """Estimate how long a task will take for this employee"""
        base_durations = {
            TaskType.TILL_FIELD: 60.0,
            TaskType.PLANT_CROPS: 45.0,
            TaskType.WATER_CROPS: 30.0,
            TaskType.HARVEST_CROPS: 90.0,
            TaskType.TEND_CROPS: 40.0,
            TaskType.OPERATE_EQUIPMENT: 120.0,
            TaskType.TRANSPORT_GOODS: 30.0,
            TaskType.MAINTAIN_BUILDINGS: 180.0,
            TaskType.GENERAL_LABOR: 60.0
        }
        
        base_duration = base_durations.get(task_type, 60.0)
        
        efficiency = employee.get_work_efficiency()
        adjusted_duration = base_duration / efficiency
        
        relevant_skill = self._get_relevant_skill_for_task(task_type)
        if relevant_skill and relevant_skill in employee.skills:
            skill_modifier = employee.skills[relevant_skill].get_efficiency_modifier()
            adjusted_duration /= skill_modifier
        
        return adjusted_duration
    
    def _get_relevant_skill_for_task(self, task_type: TaskType) -> Optional[SkillType]:
        """Get the most relevant skill for a task type"""
        skill_mappings = {
            TaskType.TILL_FIELD: SkillType.FARMING,
            TaskType.PLANT_CROPS: SkillType.FARMING,
            TaskType.WATER_CROPS: SkillType.CROP_MANAGEMENT,
            TaskType.HARVEST_CROPS: SkillType.FARMING,
            TaskType.TEND_CROPS: SkillType.CROP_MANAGEMENT,
            TaskType.OPERATE_EQUIPMENT: SkillType.EQUIPMENT_OPERATION,
            TaskType.TRANSPORT_GOODS: SkillType.EFFICIENCY,
            TaskType.MAINTAIN_BUILDINGS: SkillType.MAINTENANCE,
            TaskType.GENERAL_LABOR: SkillType.EFFICIENCY
        }
        
        return skill_mappings.get(task_type)
    
    def get_employee_summary(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive employee information"""
        if employee_id not in self.employees:
            return None
        
        employee = self.employees[employee_id]
        
        return {
            'employee_id': employee_id,
            'name': employee.name,
            'position': {'x': employee.x, 'y': employee.y},
            'state': employee.state.value,
            'daily_wage': employee.daily_wage,
            'performance_rating': employee.performance_rating,
            'hours_worked_today': employee.hours_worked_today,
            'tasks_completed_today': employee.tasks_completed_today,
            'current_task': {
                'task_type': employee.current_task.task_type.value,
                'progress': employee.current_task.get_completion_percentage(),
                'target_location': employee.current_task.target_location
            } if employee.current_task else None,
            'task_queue_size': len(employee.task_queue),
            'stats': {
                'hunger': employee.stats.hunger,
                'thirst': employee.stats.thirst,
                'rest': employee.stats.rest,
                'energy': employee.stats.energy,
                'morale': employee.stats.morale
            },
            'skills': {skill.skill_type.value: skill.level for skill in employee.skills.values()},
            'traits': [trait.value for trait in employee.traits],
            'work_efficiency': employee.get_work_efficiency(),
            'work_quality': employee.get_work_quality()
        }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get employee system summary"""
        total_wages = sum(emp.daily_wage for emp in self.employees.values())
        total_hours_today = sum(emp.hours_worked_today for emp in self.employees.values())
        total_tasks_today = sum(emp.tasks_completed_today for emp in self.employees.values())
        
        avg_performance = 0.0
        if self.employees:
            avg_performance = sum(emp.performance_rating for emp in self.employees.values()) / len(self.employees)
        
        return {
            'total_employees': len(self.employees),
            'available_applicants': len(self.available_applicants),
            'active_tasks': len(self.active_tasks),
            'total_daily_wages': total_wages,
            'total_hours_worked_today': total_hours_today,
            'total_tasks_completed_today': total_tasks_today,
            'average_performance': avg_performance,
            'max_employees': self.config_manager.get('employees.max_employees', 10)
        }
    
    def _on_day_changed(self, event_data: Dict[str, Any]):
        """Handle daily employee management tasks"""
        current_time = self.time_system.get_current_time().total_minutes
        
        # Pay daily wages
        for employee_id, employee in self.employees.items():
            time_since_payment = current_time - employee.last_payment_date
            if time_since_payment >= (24 * 60):
                
                daily_wage = employee.daily_wage
                performance_bonus = daily_wage * (employee.performance_rating - 1.0) * 0.1
                total_payment = daily_wage + performance_bonus
                
                transaction_id = self.economy_system.add_transaction(
                    TransactionType.OPERATING_EXPENSE,
                    -total_payment,
                    f"Daily wage for {employee.name}",
                    metadata={
                        'employee_id': employee_id,
                        'base_wage': daily_wage,
                        'performance_bonus': performance_bonus
                    }
                )
                
                employee.last_payment_date = current_time
        
        # Reset daily counters
        for employee in self.employees.values():
            employee.hours_worked_today = 0.0
            employee.tasks_completed_today = 0
        
        # Generate new applicants occasionally
        if len(self.available_applicants) < 3 and random.random() < 0.3:
            self._generate_applicants(random.randint(1, 2))
    
    def _on_hour_changed(self, event_data: Dict[str, Any]):
        """Handle hourly employee updates"""
        pass
    
    def _on_season_changed(self, event_data: Dict[str, Any]):
        """Handle seasonal workforce adjustments"""
        new_season = event_data['new_season']
        
        seasonal_wage_modifiers = {
            'spring': 1.1,
            'summer': 1.0,
            'fall': 1.2,
            'winter': 0.8
        }
        
        modifier = seasonal_wage_modifiers.get(new_season, 1.0)
        
        for applicant in self.available_applicants.values():
            applicant.daily_wage *= modifier
        
        self.logger.info(f"Applied seasonal wage adjustment for {new_season}: {modifier:.1%}")


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

# Convenience functions
def hire_employee(applicant_id: str) -> Dict[str, Any]:
    """Hire an employee from applicants"""
    return get_employee_system().hire_employee(applicant_id)

def assign_task(employee_id: str, task_type: TaskType, target_location: Tuple[int, int]) -> Dict[str, Any]:
    """Assign a task to an employee"""
    return get_employee_system().assign_task(employee_id, task_type, target_location)

def get_employee_summary(employee_id: str) -> Optional[Dict[str, Any]]:
    """Get employee information summary"""
    return get_employee_system().get_employee_summary(employee_id)

def get_system_summary() -> Dict[str, Any]:
    """Get employee system summary"""
    return get_employee_system().get_system_summary()
