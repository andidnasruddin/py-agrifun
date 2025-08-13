"""
Enhanced Task System Data Models
New data structures for the enhanced task assignment system.
These work alongside the existing system without modifying current behavior.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid
from datetime import datetime


class TaskType(Enum):
    """Enhanced task types for agricultural operations"""
    TILLING = "tilling"
    FERTILIZING = "fertilizing" 
    PLANTING = "planting"
    WATERING = "watering"
    CULTIVATING = "cultivating"
    PEST_CONTROL = "pest_control"
    HARVESTING = "harvesting"
    PROCESSING = "processing"
    STORING = "storing"


class TaskPriority(Enum):
    """Task priority levels (1 = highest, 5 = lowest)"""
    CRITICAL = 1    # Immediate attention required
    HIGH = 2        # Important tasks
    NORMAL = 3      # Standard operations
    LOW = 4         # Can be delayed
    MINIMAL = 5     # Lowest priority


class EmployeeRole(Enum):
    """Employee specialization roles"""
    FIELD_OPERATOR = "field_operator"       # Tilling, planting, cultivation
    HARVEST_SPECIALIST = "harvest_specialist"  # Harvesting, quality assessment
    MAINTENANCE_TECH = "maintenance_tech"    # Equipment, irrigation, buildings
    CROP_MANAGER = "crop_manager"           # Fertilizing, pest control, monitoring
    GENERAL_LABORER = "general_laborer"     # Can do basic tasks but less efficiently


class SkillLevel(Enum):
    """Skill proficiency levels"""
    NOVICE = 1      # 50% efficiency
    BASIC = 2       # 75% efficiency  
    COMPETENT = 3   # 100% efficiency (baseline)
    EXPERT = 4      # 125% efficiency
    MASTER = 5      # 150% efficiency


@dataclass
class EmployeeSpecialization:
    """Employee specialization and skill data"""
    primary_role: EmployeeRole
    skill_levels: Dict[TaskType, SkillLevel] = field(default_factory=dict)
    certifications: List[str] = field(default_factory=list)
    task_preferences: Dict[TaskType, TaskPriority] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default skill levels based on primary role"""
        if not self.skill_levels:
            self._initialize_default_skills()
        if not self.task_preferences:
            self._initialize_default_preferences()
    
    def _initialize_default_skills(self):
        """Set default skill levels based on primary role"""
        # Initialize all skills at novice level
        for task_type in TaskType:
            self.skill_levels[task_type] = SkillLevel.NOVICE
        
        # Set specialized skills based on role
        if self.primary_role == EmployeeRole.FIELD_OPERATOR:
            self.skill_levels[TaskType.TILLING] = SkillLevel.COMPETENT
            self.skill_levels[TaskType.PLANTING] = SkillLevel.COMPETENT
            self.skill_levels[TaskType.CULTIVATING] = SkillLevel.BASIC
        elif self.primary_role == EmployeeRole.HARVEST_SPECIALIST:
            self.skill_levels[TaskType.HARVESTING] = SkillLevel.EXPERT
            self.skill_levels[TaskType.PROCESSING] = SkillLevel.COMPETENT
            self.skill_levels[TaskType.STORING] = SkillLevel.BASIC
        elif self.primary_role == EmployeeRole.MAINTENANCE_TECH:
            self.skill_levels[TaskType.WATERING] = SkillLevel.COMPETENT
            self.skill_levels[TaskType.FERTILIZING] = SkillLevel.BASIC
        elif self.primary_role == EmployeeRole.CROP_MANAGER:
            self.skill_levels[TaskType.FERTILIZING] = SkillLevel.EXPERT
            self.skill_levels[TaskType.PEST_CONTROL] = SkillLevel.COMPETENT
            self.skill_levels[TaskType.WATERING] = SkillLevel.BASIC
    
    def _initialize_default_preferences(self):
        """Set default task preferences based on skills"""
        for task_type in TaskType:
            skill_level = self.skill_levels.get(task_type, SkillLevel.NOVICE)
            # Higher skill = higher preference for that task
            if skill_level.value >= 4:  # Expert/Master
                self.task_preferences[task_type] = TaskPriority.HIGH
            elif skill_level.value >= 3:  # Competent
                self.task_preferences[task_type] = TaskPriority.NORMAL
            else:  # Novice/Basic
                self.task_preferences[task_type] = TaskPriority.LOW
    
    def get_efficiency_for_task(self, task_type: TaskType) -> float:
        """Get efficiency multiplier for a specific task"""
        skill_level = self.skill_levels.get(task_type, SkillLevel.NOVICE)
        efficiency_map = {
            SkillLevel.NOVICE: 0.5,
            SkillLevel.BASIC: 0.75,
            SkillLevel.COMPETENT: 1.0,
            SkillLevel.EXPERT: 1.25,
            SkillLevel.MASTER: 1.5
        }
        return efficiency_map[skill_level]


@dataclass
class WorkOrder:
    """Enhanced work order system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = TaskType.TILLING
    assigned_plots: List[tuple] = field(default_factory=list)  # List of (x, y) coordinates
    priority: TaskPriority = TaskPriority.NORMAL
    
    # Requirements
    required_skills: List[TaskType] = field(default_factory=list)
    required_certifications: List[str] = field(default_factory=list)
    required_equipment: List[str] = field(default_factory=list)
    
    # Assignment
    assigned_employee_id: Optional[str] = None
    assigned_at: Optional[datetime] = None
    
    # Progress tracking
    estimated_duration: float = 0.0  # Hours
    progress: float = 0.0  # 0.0 to 1.0
    completed_plots: List[tuple] = field(default_factory=list)
    
    # Status
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Additional metadata
    crop_type: Optional[str] = None  # For planting tasks
    weather_dependent: bool = False
    deadline: Optional[datetime] = None
    notes: str = ""
    
    @property
    def is_assigned(self) -> bool:
        """Check if work order is assigned to an employee"""
        return self.assigned_employee_id is not None
    
    @property
    def is_in_progress(self) -> bool:
        """Check if work order is currently being worked on"""
        return self.started_at is not None and self.completed_at is None
    
    @property
    def is_completed(self) -> bool:
        """Check if work order is completed"""
        return self.completed_at is not None
    
    @property
    def completion_percentage(self) -> int:
        """Get completion percentage as integer"""
        return int(self.progress * 100)
    
    def estimate_duration(self, employee_specialization: Optional[EmployeeSpecialization] = None) -> float:
        """Estimate duration based on plots and employee efficiency"""
        base_time_per_plot = {
            TaskType.TILLING: 0.5,      # 30 minutes per plot
            TaskType.FERTILIZING: 0.25,  # 15 minutes per plot
            TaskType.PLANTING: 0.33,     # 20 minutes per plot
            TaskType.WATERING: 0.17,     # 10 minutes per plot
            TaskType.CULTIVATING: 0.33,  # 20 minutes per plot
            TaskType.PEST_CONTROL: 0.25, # 15 minutes per plot
            TaskType.HARVESTING: 0.5,    # 30 minutes per plot
            TaskType.PROCESSING: 0.17,   # 10 minutes per plot
            TaskType.STORING: 0.17       # 10 minutes per plot
        }
        
        base_time = base_time_per_plot.get(self.task_type, 0.5) * len(self.assigned_plots)
        
        if employee_specialization:
            efficiency = employee_specialization.get_efficiency_for_task(self.task_type)
            self.estimated_duration = base_time / efficiency
        else:
            self.estimated_duration = base_time
        
        return self.estimated_duration


@dataclass
class TaskAssignmentPreferences:
    """Global preferences for task assignment system"""
    auto_assign_enabled: bool = True
    respect_employee_preferences: bool = True
    consider_skill_levels: bool = True
    allow_cross_training: bool = True
    emergency_override_preferences: bool = True
    
    # Priority weighting (used for auto-assignment)
    priority_weights: Dict[TaskPriority, float] = field(default_factory=lambda: {
        TaskPriority.CRITICAL: 5.0,
        TaskPriority.HIGH: 3.0,
        TaskPriority.NORMAL: 1.0,
        TaskPriority.LOW: 0.5,
        TaskPriority.MINIMAL: 0.1
    })


# Legacy compatibility - maintains existing task system structure
LEGACY_TASK_MAPPING = {
    'till': TaskType.TILLING,
    'plant': TaskType.PLANTING, 
    'harvest': TaskType.HARVESTING
}

def convert_legacy_task(legacy_task: str) -> TaskType:
    """Convert legacy task strings to new TaskType enum"""
    return LEGACY_TASK_MAPPING.get(legacy_task, TaskType.TILLING)

def convert_to_legacy_task(task_type: TaskType) -> str:
    """Convert new TaskType back to legacy string for existing system"""
    reverse_mapping = {v: k for k, v in LEGACY_TASK_MAPPING.items()}
    return reverse_mapping.get(task_type, 'till')