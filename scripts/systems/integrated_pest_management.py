"""
Integrated Pest Management (IPM) System - Comprehensive IPM Strategy for AgriFun Agricultural Game

This system provides realistic integrated pest management coordination including cultural, 
biological, and chemical control methods. It implements IPM decision-making frameworks,
economic thresholds, and sustainable pest management strategies that reflect real-world
agricultural practices and principles.

Key Features:
- Comprehensive IPM decision support system with multi-tactic coordination
- Cultural control integration (crop rotation, resistant varieties, habitat management)
- Biological control optimization (natural enemies, conservation, augmentation)
- Chemical control stewardship (resistance management, selective applications)
- Economic threshold analysis with cost-benefit optimization
- Environmental impact assessment and sustainability metrics
- Resistance management strategies and mode of action rotation

IPM Principles:
1. Prevention: Cultural practices and resistant varieties as foundation
2. Monitoring: Regular scouting and threshold-based decisions
3. Identification: Accurate pest and beneficial identification
4. Economic Thresholds: Treatment only when economically justified
5. Multiple Tactics: Integration of cultural, biological, and chemical methods
6. Evaluation: Continuous assessment and adaptive management

Educational Value:
- Understanding of IPM philosophy and sustainable agriculture
- Economic decision-making in pest management contexts
- Environmental stewardship and pollinator protection
- Resistance management and pesticide stewardship
- Systems thinking in agricultural management

Integration:
- Disease Framework: Coordinated disease and pest management
- Pest Framework: Population dynamics and economic thresholds
- Crop Growth System: Timing of interventions with crop stages
- Equipment System: Application technology and precision targeting
- Economic System: Cost analysis and return on investment

Author: Agricultural Simulation Development Team
Version: 1.0.0 - Comprehensive IPM System Implementation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
import math
import random
from datetime import datetime, timedelta

# Core system imports
from scripts.core.advanced_event_system import EventSystem
from scripts.core.entity_component_system import System
from scripts.core.content_registry import ContentRegistry
from scripts.core.advanced_config_system import ConfigurationManager

class IPMTactic(Enum):
    """IPM tactic categories"""
    CULTURAL = "cultural"           # Crop rotation, resistant varieties, habitat management
    BIOLOGICAL = "biological"       # Natural enemies, conservation, augmentation
    CHEMICAL = "chemical"          # Selective pesticides, targeted applications
    MECHANICAL = "mechanical"      # Physical barriers, traps, cultivation
    REGULATORY = "regulatory"      # Quarantine, certification, area-wide programs

class ControlStrategy(Enum):
    """Overall control strategies"""
    PREVENTION = "prevention"       # Prevent pest establishment
    SUPPRESSION = "suppression"     # Reduce pest populations below economic threshold
    CONTAINMENT = "containment"     # Limit pest spread to new areas
    ERADICATION = "eradication"     # Eliminate pest from area (rarely feasible)

class TreatmentTiming(Enum):
    """Timing strategies for treatments"""
    PROPHYLACTIC = "prophylactic"   # Preventive applications
    THRESHOLD_BASED = "threshold_based"  # Apply when threshold is reached
    PHENOLOGY_BASED = "phenology_based"  # Apply based on pest/crop development
    CALENDAR_BASED = "calendar_based"    # Scheduled applications

class ResistanceRisk(Enum):
    """Pesticide resistance risk levels"""
    LOW = "low"
    MODERATE = "moderate"  
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class IPMTacticData:
    """Data for specific IPM tactic"""
    tactic_id: str
    tactic_name: str
    tactic_type: IPMTactic
    
    # Effectiveness data
    target_pests: List[str] = field(default_factory=list)
    target_diseases: List[str] = field(default_factory=list)
    effectiveness_rating: Dict[str, float] = field(default_factory=dict)  # pest/disease: efficacy
    
    # Implementation requirements
    implementation_cost: float = 0.0
    labor_hours_required: float = 0.0
    equipment_needed: List[str] = field(default_factory=list)
    timing_requirements: List[str] = field(default_factory=list)
    
    # Duration and persistence
    effective_duration_days: int = 30
    residual_effects: bool = False
    
    # Environmental considerations
    environmental_impact_score: float = 0.0  # 0-10, higher = more impact
    pollinator_safety_rating: str = "safe"   # "safe", "caution", "hazardous"
    beneficial_impact: float = 0.0  # Impact on beneficial insects (0-1)
    
    # Compatibility and restrictions
    compatible_tactics: List[str] = field(default_factory=list)
    incompatible_tactics: List[str] = field(default_factory=list)
    application_restrictions: List[str] = field(default_factory=list)
    
    # Resistance considerations
    resistance_risk: ResistanceRisk = ResistanceRisk.LOW
    mode_of_action: str = ""
    resistance_management_notes: str = ""

@dataclass
class IPMProgram:
    """Comprehensive IPM program for specific crop/location"""
    program_id: str
    location_id: str
    crop_id: str
    program_name: str
    
    # Program structure
    active_tactics: List[str] = field(default_factory=list)  # Currently implemented tactics
    planned_tactics: List[str] = field(default_factory=list) # Future planned tactics
    contingency_tactics: List[str] = field(default_factory=list) # Emergency options
    
    # Economic parameters
    total_program_cost: float = 0.0
    cost_per_acre: float = 0.0
    expected_roi: float = 0.0
    break_even_threshold: float = 0.0
    
    # Performance tracking
    pest_control_efficacy: Dict[str, float] = field(default_factory=dict)  # pest: % control
    yield_protection_achieved: float = 0.0  # % yield protected
    treatment_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Sustainability metrics
    pesticide_load_index: float = 0.0       # Environmental load from pesticides
    beneficial_conservation_score: float = 0.0  # Beneficial insect conservation
    resistance_management_score: float = 0.0    # Resistance management effectiveness
    
    # Program evaluation
    program_effectiveness: float = 0.0      # Overall program effectiveness (0-100)
    sustainability_rating: str = "good"     # "poor", "fair", "good", "excellent"
    improvement_recommendations: List[str] = field(default_factory=list)

@dataclass
class TreatmentDecision:
    """IPM treatment decision with supporting analysis"""
    decision_id: str
    location_id: str
    decision_date: datetime
    
    # Decision context
    pest_situation: Dict[str, Any] = field(default_factory=dict)  # Current pest status
    economic_analysis: Dict[str, Any] = field(default_factory=dict)  # Cost-benefit analysis
    environmental_factors: Dict[str, Any] = field(default_factory=dict)  # Weather, crop stage
    
    # Decision outcome
    treatment_recommended: bool = False
    recommended_tactics: List[str] = field(default_factory=list)
    treatment_urgency: str = "routine"      # "routine", "urgent", "emergency"
    
    # Decision rationale
    decision_factors: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, str] = field(default_factory=dict)  # factor: risk_level
    alternative_options: List[str] = field(default_factory=list)
    
    # Implementation planning
    optimal_timing: datetime = field(default_factory=datetime.now)
    application_conditions: Dict[str, Any] = field(default_factory=dict)
    expected_outcomes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResistanceMonitoring:
    """Pesticide resistance monitoring data"""
    monitoring_id: str
    location_id: str
    pest_id: str
    pesticide_mode_of_action: str
    
    # Resistance indicators
    control_efficacy_trend: List[float] = field(default_factory=list)  # Historical efficacy
    dose_response_shift: float = 0.0        # Change in dose needed for control
    cross_resistance_detected: List[str] = field(default_factory=list)  # Related modes affected
    
    # Population genetics indicators
    resistant_allele_frequency: float = 0.0  # Estimated frequency of resistance alleles
    selection_pressure_index: float = 0.0   # Intensity of selection for resistance
    
    # Management recommendations
    resistance_status: str = "susceptible"   # "susceptible", "developing", "confirmed"
    management_recommendations: List[str] = field(default_factory=list)
    alternative_modes_available: List[str] = field(default_factory=list)

class IntegratedPestManagement(System):
    """
    Comprehensive Integrated Pest Management System
    
    This system coordinates all aspects of IPM including:
    - Multi-tactic IPM programs with cultural, biological, and chemical control
    - Economic threshold analysis and treatment decision support
    - Resistance management and mode of action rotation
    - Environmental impact assessment and sustainability metrics
    - Performance tracking and adaptive management recommendations
    """
    
    def __init__(self):
        """Initialize the IPM System"""
        super().__init__()
        
        # Core system references
        self.event_system = None
        self.config_manager = None
        self.content_registry = None
        
        # IPM data structures
        self.ipm_tactics: Dict[str, IPMTacticData] = {}
        self.active_programs: Dict[str, IPMProgram] = {}
        self.treatment_decisions: Dict[str, TreatmentDecision] = {}
        self.resistance_monitoring: Dict[str, ResistanceMonitoring] = {}
        
        # Decision support systems
        self.economic_thresholds: Dict[str, Dict[str, float]] = {}  # crop: pest: threshold
        self.treatment_windows: Dict[str, Dict[str, Tuple]] = {}    # crop: pest: (start, end) days
        self.mode_of_action_groups: Dict[str, List[str]] = {}       # MOA group: pesticide list
        
        # System parameters
        self.system_parameters = {
            'economic_threshold_safety_margin': 0.8,    # Apply at 80% of threshold
            'benefit_cost_ratio_minimum': 2.0,          # Minimum B:C ratio for treatment
            'resistance_monitoring_threshold': 0.85,    # Efficacy drop triggering monitoring
            'environmental_impact_weight': 0.3,         # Weight of environmental factors
            'beneficial_conservation_priority': 0.7,    # Priority for beneficial conservation
            'sustainability_target_score': 75.0,       # Target sustainability score
            'mode_rotation_interval_applications': 3    # Max consecutive applications
        }
        
        # Performance tracking
        self.ipm_statistics: Dict[str, Any] = {
            'programs_active': 0,
            'treatments_applied': 0,
            'resistance_incidents': 0,
            'yield_protected': 0.0,
            'pesticide_reduction': 0.0,
            'beneficial_conservation_success': 0.0
        }
        
        self.is_initialized = False
    
    def initialize(self, event_system: EventSystem, config_manager: ConfigurationManager, 
                  content_registry: ContentRegistry) -> bool:
        """Initialize the IPM System with required dependencies"""
        try:
            self.event_system = event_system
            self.config_manager = config_manager
            self.content_registry = content_registry
            
            # Load IPM configuration
            self._load_configuration()
            
            # Initialize IPM tactics database
            self._initialize_ipm_tactics()
            
            # Initialize economic thresholds
            self._initialize_economic_thresholds()
            
            # Initialize mode of action groups
            self._initialize_mode_of_action_groups()
            
            # Register event handlers
            self._register_event_handlers()
            
            self.is_initialized = True
            
            # Emit initialization event
            self.event_system.emit_event("ipm_system_initialized", {
                "system": "integrated_pest_management",
                "status": "ready",
                "tactics_available": len(self.ipm_tactics),
                "economic_thresholds": len(self.economic_thresholds),
                "timestamp": datetime.now()
            })
            
            return True
            
        except Exception as e:
            print(f"Error initializing IPM System: {e}")
            return False
    
    def _load_configuration(self):
        """Load IPM configuration from config files"""
        ipm_config = self.config_manager.get("integrated_pest_management", {})
        
        # Update system parameters
        if "parameters" in ipm_config:
            self.system_parameters.update(ipm_config["parameters"])
    
    def _initialize_ipm_tactics(self):
        """Initialize comprehensive IPM tactics database"""
        
        # Cultural control tactics
        self.ipm_tactics["crop_rotation"] = IPMTacticData(
            tactic_id="crop_rotation",
            tactic_name="Crop Rotation",
            tactic_type=IPMTactic.CULTURAL,
            target_pests=["corn_rootworm", "soybean_cyst_nematode"],
            target_diseases=["soybean_sudden_death", "corn_gray_leaf_spot"],
            effectiveness_rating={
                "corn_rootworm": 0.85,
                "soybean_sudden_death": 0.70
            },
            implementation_cost=0.0,  # No direct cost, opportunity cost in planning
            effective_duration_days=365,  # Season-long effect
            environmental_impact_score=1.0,  # Very low impact
            pollinator_safety_rating="safe",
            beneficial_impact=0.1,  # Minimal impact on beneficials
            compatible_tactics=["resistant_varieties", "cover_crops"],
            resistance_risk=ResistanceRisk.LOW,
            mode_of_action="habitat_disruption"
        )
        
        self.ipm_tactics["resistant_varieties"] = IPMTacticData(
            tactic_id="resistant_varieties",
            tactic_name="Host Plant Resistance",
            tactic_type=IPMTactic.CULTURAL,
            target_pests=["european_corn_borer", "soybean_aphid"],
            target_diseases=["soybean_rust", "corn_northern_leaf_blight"],
            effectiveness_rating={
                "european_corn_borer": 0.90,
                "soybean_rust": 0.80
            },
            implementation_cost=15.0,  # Premium seed cost per acre
            effective_duration_days=365,
            environmental_impact_score=0.5,
            pollinator_safety_rating="safe",
            beneficial_impact=0.0,  # No impact on beneficials
            compatible_tactics=["crop_rotation", "biological_control"],
            resistance_risk=ResistanceRisk.MODERATE,  # Pests can evolve to overcome
            mode_of_action="antibiosis_antixenosis"
        )
        
        # Biological control tactics
        self.ipm_tactics["beneficial_habitat"] = IPMTacticData(
            tactic_id="beneficial_habitat",
            tactic_name="Beneficial Insect Habitat",
            tactic_type=IPMTactic.BIOLOGICAL,
            target_pests=["soybean_aphid", "armyworm"],
            effectiveness_rating={
                "soybean_aphid": 0.60,
                "armyworm": 0.40
            },
            implementation_cost=25.0,  # Habitat establishment cost per acre
            labor_hours_required=2.0,
            effective_duration_days=180,  # Growing season
            environmental_impact_score=0.0,  # Positive environmental impact
            pollinator_safety_rating="safe",
            beneficial_impact=-0.5,  # Positive impact on beneficials
            compatible_tactics=["biological_augmentation", "selective_pesticides"],
            resistance_risk=ResistanceRisk.LOW
        )
        
        self.ipm_tactics["biological_augmentation"] = IPMTacticData(
            tactic_id="biological_augmentation",
            tactic_name="Beneficial Insect Releases",
            tactic_type=IPMTactic.BIOLOGICAL,
            target_pests=["european_corn_borer", "soybean_aphid"],
            effectiveness_rating={
                "european_corn_borer": 0.70,
                "soybean_aphid": 0.65
            },
            implementation_cost=40.0,  # Cost of beneficial insects per acre
            labor_hours_required=1.0,
            effective_duration_days=60,
            environmental_impact_score=0.0,
            pollinator_safety_rating="safe",
            beneficial_impact=-0.3,  # Positive impact
            compatible_tactics=["beneficial_habitat", "selective_pesticides"],
            timing_requirements=["pest_threshold_reached", "optimal_weather"],
            resistance_risk=ResistanceRisk.LOW
        )
        
        # Chemical control tactics
        self.ipm_tactics["selective_insecticide"] = IPMTacticData(
            tactic_id="selective_insecticide",
            tactic_name="Selective Insecticides",
            tactic_type=IPMTactic.CHEMICAL,
            target_pests=["corn_rootworm", "european_corn_borer"],
            effectiveness_rating={
                "corn_rootworm": 0.90,
                "european_corn_borer": 0.85
            },
            implementation_cost=35.0,  # Cost per acre
            labor_hours_required=0.5,
            equipment_needed=["sprayer"],
            effective_duration_days=21,
            environmental_impact_score=4.0,  # Moderate impact
            pollinator_safety_rating="caution",
            beneficial_impact=0.3,  # Some impact on beneficials
            compatible_tactics=["beneficial_habitat"],
            incompatible_tactics=["biological_augmentation"],  # Timing conflict
            application_restrictions=["no_wind", "no_rain_forecast", "pollinator_protection"],
            resistance_risk=ResistanceRisk.MODERATE,
            mode_of_action="neonicotinoid",
            resistance_management_notes="Rotate with different modes of action"
        )
        
        self.ipm_tactics["bt_corn"] = IPMTacticData(
            tactic_id="bt_corn",
            tactic_name="Bt Corn Technology",
            tactic_type=IPMTactic.CULTURAL,  # Transgenic trait
            target_pests=["european_corn_borer", "corn_rootworm"],
            effectiveness_rating={
                "european_corn_borer": 0.95,
                "corn_rootworm": 0.90
            },
            implementation_cost=25.0,  # Technology fee per acre
            effective_duration_days=365,
            environmental_impact_score=2.0,
            pollinator_safety_rating="safe",
            beneficial_impact=0.1,
            compatible_tactics=["crop_rotation", "beneficial_habitat"],
            application_restrictions=["refuge_requirement"],
            resistance_risk=ResistanceRisk.HIGH,  # High selection pressure
            mode_of_action="bt_toxin",
            resistance_management_notes="20% refuge required for resistance management"
        )
        
        # Mechanical control tactics
        self.ipm_tactics["pheromone_traps"] = IPMTacticData(
            tactic_id="pheromone_traps",
            tactic_name="Pheromone Monitoring Traps",
            tactic_type=IPMTactic.MECHANICAL,
            target_pests=["european_corn_borer", "armyworm"],
            effectiveness_rating={
                "european_corn_borer": 0.20,  # Monitoring tool, not control
                "armyworm": 0.15
            },
            implementation_cost=10.0,  # Trap and lure costs
            labor_hours_required=0.5,
            effective_duration_days=30,
            environmental_impact_score=0.5,
            pollinator_safety_rating="safe",
            beneficial_impact=0.05,
            compatible_tactics=["all_tactics"],
            timing_requirements=["adult_flight_period"],
            resistance_risk=ResistanceRisk.LOW
        )
        
        print(f"Initialized {len(self.ipm_tactics)} IPM tactics")
    
    def _initialize_economic_thresholds(self):
        """Initialize economic thresholds for pest-crop combinations"""
        
        # Corn economic thresholds
        self.economic_thresholds["corn"] = {
            "corn_rootworm": 0.75,      # beetles per plant
            "european_corn_borer": 0.8,  # larvae per plant
            "armyworm": 1.5,            # larvae per plant
            "cutworm": 0.05             # Very low threshold for seedling damage
        }
        
        # Soybean economic thresholds
        self.economic_thresholds["soybeans"] = {
            "soybean_aphid": 200.0,     # aphids per plant
            "armyworm": 2.0,            # larvae per plant
            "cutworm": 0.1              # larvae per plant
        }
        
        # Treatment windows (crop stage days when treatment is effective)
        self.treatment_windows["corn"] = {
            "corn_rootworm": (30, 90),   # Vegetative to early reproductive
            "european_corn_borer": (45, 75),  # Pre-tassel to early silk
            "armyworm": (15, 60),        # Seedling to vegetative
            "cutworm": (1, 30)           # Seedling stage only
        }
        
        self.treatment_windows["soybeans"] = {
            "soybean_aphid": (30, 100),  # V3 to R5 stages
            "armyworm": (20, 80),        # V2 to R3 stages
            "cutworm": (1, 25)           # Seedling stage
        }
        
        print("Initialized economic thresholds and treatment windows")
    
    def _initialize_mode_of_action_groups(self):
        """Initialize pesticide mode of action groups for resistance management"""
        
        self.mode_of_action_groups = {
            "1A_carbamate": ["carbaryl", "aldicarb"],
            "1B_organophosphate": ["chlorpyrifos", "malathion", "dimethoate"],
            "3A_pyrethroid": ["bifenthrin", "lambda_cyhalothrin", "permethrin"],
            "4A_neonicotinoid": ["imidacloprid", "thiamethoxam", "clothianidin"],
            "11A_bt_toxin": ["cry1ab", "cry3bb1", "vip3a"],
            "28_diamide": ["chlorantraniliprole", "flubendiamide"]
        }
        
        print(f"Initialized {len(self.mode_of_action_groups)} mode of action groups")
    
    def _register_event_handlers(self):
        """Register event handlers for system integration"""
        self.event_system.subscribe("pest_monitoring_completed", self._handle_pest_monitoring)
        self.event_system.subscribe("economic_threshold_exceeded", self._handle_threshold_exceeded)
        self.event_system.subscribe("treatment_application_completed", self._handle_treatment_completed)
        self.event_system.subscribe("crop_growth_stage_changed", self._handle_crop_stage_change)
        self.event_system.subscribe("weather_forecast_updated", self._handle_weather_forecast)
    
    def create_ipm_program(self, location_id: str, crop_id: str, program_name: str,
                          target_pests: List[str]) -> IPMProgram:
        """Create comprehensive IPM program for location"""
        
        program_id = f"IPM_{location_id}_{crop_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        program = IPMProgram(
            program_id=program_id,
            location_id=location_id,
            crop_id=crop_id,
            program_name=program_name
        )
        
        # Select appropriate tactics based on target pests and crop
        recommended_tactics = self._select_ipm_tactics(crop_id, target_pests)
        
        # Prioritize tactics by IPM hierarchy (cultural > biological > chemical)
        cultural_tactics = [t for t in recommended_tactics if self.ipm_tactics[t].tactic_type == IPMTactic.CULTURAL]
        biological_tactics = [t for t in recommended_tactics if self.ipm_tactics[t].tactic_type == IPMTactic.BIOLOGICAL]
        chemical_tactics = [t for t in recommended_tactics if self.ipm_tactics[t].tactic_type == IPMTactic.CHEMICAL]
        mechanical_tactics = [t for t in recommended_tactics if self.ipm_tactics[t].tactic_type == IPMTactic.MECHANICAL]
        
        # Set up program structure
        program.active_tactics = cultural_tactics + mechanical_tactics  # Foundational tactics
        program.planned_tactics = biological_tactics  # Implemented when needed
        program.contingency_tactics = chemical_tactics  # Used when thresholds exceeded
        
        # Calculate program economics
        program.total_program_cost = sum(
            self.ipm_tactics[tactic].implementation_cost 
            for tactic in program.active_tactics + program.planned_tactics
        )
        program.cost_per_acre = program.total_program_cost
        
        # Estimate break-even threshold
        program.break_even_threshold = self._calculate_break_even_threshold(program, crop_id)
        
        # Store program
        self.active_programs[program_id] = program
        
        # Update statistics
        self.imp_statistics['programs_active'] = len(self.active_programs)
        
        # Emit program creation event
        self.event_system.emit_event("ipm_program_created", {
            "program_id": program_id,
            "location_id": location_id,
            "crop_id": crop_id,
            "active_tactics": len(program.active_tactics),
            "total_cost": program.total_program_cost
        })
        
        print(f"IPM program created: {program_name} for {crop_id} at {location_id}")
        return program
    
    def _select_ipm_tactics(self, crop_id: str, target_pests: List[str]) -> List[str]:
        """Select appropriate IPM tactics for crop and pest situation"""
        
        recommended_tactics = []
        
        # Evaluate each tactic for effectiveness against target pests
        for tactic_id, tactic_data in self.ipm_tactics.items():
            effectiveness_score = 0.0
            pest_matches = 0
            
            for pest_id in target_pests:
                if pest_id in tactic_data.effectiveness_rating:
                    effectiveness_score += tactic_data.effectiveness_rating[pest_id]
                    pest_matches += 1
            
            # Include tactic if it's effective against any target pest
            if pest_matches > 0:
                avg_effectiveness = effectiveness_score / pest_matches
                if avg_effectiveness >= 0.3:  # Minimum 30% effectiveness
                    recommended_tactics.append(tactic_id)
        
        return recommended_tactics
    
    def _calculate_break_even_threshold(self, program: IPMProgram, crop_id: str) -> float:
        """Calculate break-even threshold for IPM program"""
        
        # Simplified economic model
        expected_yield_per_acre = 180  # bushels for corn, would vary by crop
        expected_price_per_unit = 4.50  # $ per bushel
        
        gross_revenue = expected_yield_per_acre * expected_price_per_unit
        program_cost_ratio = program.cost_per_acre / gross_revenue
        
        # Break-even threshold is the yield loss % that equals program cost
        break_even_threshold = program_cost_ratio * 100
        
        return break_even_threshold
    
    def evaluate_treatment_decision(self, location_id: str, pest_situation: Dict[str, Any],
                                  environmental_conditions: Dict[str, Any]) -> TreatmentDecision:
        """Evaluate whether treatment is needed based on IPM principles"""
        
        decision_id = f"DEC_{location_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        decision = TreatmentDecision(
            decision_id=decision_id,
            location_id=location_id,
            decision_date=datetime.now(),
            pest_situation=pest_situation,
            environmental_factors=environmental_conditions
        )
        
        # Analyze pest situation
        crop_id = pest_situation.get('crop_id', 'corn')
        pest_densities = pest_situation.get('pest_densities', {})
        beneficial_densities = pest_situation.get('beneficial_densities', {})
        crop_stage_days = pest_situation.get('crop_stage_days', 50)
        
        # Economic threshold analysis
        thresholds_exceeded = []
        economic_injury_potential = 0.0
        
        for pest_id, density in pest_densities.items():
            if crop_id in self.economic_thresholds and pest_id in self.economic_thresholds[crop_id]:
                threshold = self.economic_thresholds[crop_id][pest_id]
                safety_threshold = threshold * self.system_parameters['economic_threshold_safety_margin']
                
                if density >= safety_threshold:
                    thresholds_exceeded.append(pest_id)
                    
                    # Calculate potential economic injury
                    injury_ratio = density / threshold
                    economic_injury_potential += injury_ratio
        
        decision.economic_analysis = {
            'thresholds_exceeded': thresholds_exceeded,
            'economic_injury_potential': economic_injury_potential,
            'treatment_window_status': self._check_treatment_windows(crop_id, crop_stage_days)
        }
        
        # Beneficial insect consideration
        beneficial_protection_factor = 0.0
        for beneficial_id, density in beneficial_densities.items():
            if density > 0:
                beneficial_protection_factor += min(density * 0.1, 0.5)  # Cap at 50% protection
        
        # Environmental conditions check
        weather_suitable = self._assess_weather_suitability(environmental_conditions)
        
        # Decision algorithm
        treatment_score = 0.0
        
        # Economic factors (40% weight)
        if thresholds_exceeded:
            treatment_score += 40 * (economic_injury_potential / len(thresholds_exceeded))
        
        # Biological factors (30% weight)
        treatment_score -= 30 * beneficial_protection_factor
        
        # Environmental factors (20% weight)
        if weather_suitable:
            treatment_score += 20
        else:
            treatment_score -= 10
        
        # Timing factors (10% weight)
        if decision.economic_analysis['treatment_window_status']:
            treatment_score += 10
        else:
            treatment_score -= 5
        
        # Make decision
        if treatment_score >= 50:  # 50% threshold for treatment recommendation
            decision.treatment_recommended = True
            decision.recommended_tactics = self._select_treatment_tactics(
                crop_id, thresholds_exceeded, beneficial_densities
            )
            
            if economic_injury_potential > 2.0:
                decision.treatment_urgency = "urgent"
            elif economic_injury_potential > 1.5:
                decision.treatment_urgency = "routine"
        
        # Generate decision rationale
        decision.decision_factors = self._generate_decision_rationale(
            thresholds_exceeded, beneficial_protection_factor, weather_suitable, treatment_score
        )
        
        # Risk assessment
        decision.risk_assessment = {
            'economic_risk': 'high' if economic_injury_potential > 1.5 else 'moderate',
            'environmental_risk': 'low' if beneficial_protection_factor > 0.3 else 'moderate',
            'resistance_risk': self._assess_resistance_risk(crop_id, thresholds_exceeded)
        }
        
        # Store decision
        self.treatment_decisions[decision_id] = decision
        
        # Emit decision event
        self.event_system.emit_event("ipm_treatment_decision", {
            "decision_id": decision_id,
            "location_id": location_id,
            "treatment_recommended": decision.treatment_recommended,
            "treatment_score": treatment_score,
            "pests_exceeding_threshold": len(thresholds_exceeded)
        })
        
        return decision
    
    def _check_treatment_windows(self, crop_id: str, crop_stage_days: int) -> bool:
        """Check if current crop stage is within treatment windows"""
        
        if crop_id not in self.treatment_windows:
            return True  # No restrictions
        
        for pest_id, (start_day, end_day) in self.treatment_windows[crop_id].items():
            if start_day <= crop_stage_days <= end_day:
                return True
        
        return False
    
    def _assess_weather_suitability(self, conditions: Dict[str, Any]) -> bool:
        """Assess if weather conditions are suitable for treatment application"""
        
        temperature = conditions.get('temperature_c', 20)
        wind_speed = conditions.get('wind_speed_kmh', 5)
        humidity = conditions.get('humidity_percent', 60)
        rain_forecast = conditions.get('rain_forecast_hours', 0)
        
        # Check weather suitability criteria
        suitable = True
        
        if temperature < 10 or temperature > 30:
            suitable = False  # Temperature too extreme
        
        if wind_speed > 15:
            suitable = False  # Too windy for application
        
        if rain_forecast < 2:
            suitable = False  # Rain too soon after application
        
        return suitable
    
    def _select_treatment_tactics(self, crop_id: str, target_pests: List[str], 
                                 beneficial_densities: Dict[str, float]) -> List[str]:
        """Select appropriate treatment tactics based on IPM principles"""
        
        selected_tactics = []
        
        # Prioritize selective tactics if beneficial insects are present
        beneficial_present = sum(beneficial_densities.values()) > 0
        
        # Find program for this crop to check current tactics
        active_program = None
        for program in self.active_programs.values():
            if program.crop_id == crop_id:
                active_program = program
                break
        
        # Select tactics based on IPM hierarchy and situation
        candidate_tactics = []
        
        for tactic_id, tactic_data in self.ipm_tactics.items():
            # Check if tactic is effective against target pests
            effectiveness = 0.0
            for pest_id in target_pests:
                effectiveness += tactic_data.effectiveness_rating.get(pest_id, 0.0)
            
            if effectiveness > 0.3:  # Minimum effectiveness threshold
                # Consider beneficial impact
                if beneficial_present and tactic_data.beneficial_impact > 0.3:
                    continue  # Skip tactics harmful to beneficials when they're present
                
                candidate_tactics.append((tactic_id, effectiveness, tactic_data.tactic_type))
        
        # Sort by IPM hierarchy and effectiveness
        hierarchy_priority = {
            IPMTactic.BIOLOGICAL: 1,
            IPMTactic.CULTURAL: 2,
            IPMTactic.MECHANICAL: 3,
            IPMTactic.CHEMICAL: 4
        }
        
        candidate_tactics.sort(key=lambda x: (hierarchy_priority[x[2]], -x[1]))
        
        # Select top tactics (limit to 2-3 for practical implementation)
        selected_tactics = [tactic[0] for tactic in candidate_tactics[:3]]
        
        return selected_tactics
    
    def _generate_decision_rationale(self, thresholds_exceeded: List[str], 
                                   beneficial_factor: float, weather_suitable: bool,
                                   treatment_score: float) -> List[str]:
        """Generate human-readable decision rationale"""
        
        rationale = []
        
        if thresholds_exceeded:
            rationale.append(f"Economic threshold exceeded for: {', '.join(thresholds_exceeded)}")
        
        if beneficial_factor > 0.3:
            rationale.append(f"Beneficial insects present (protection factor: {beneficial_factor:.2f})")
        
        if weather_suitable:
            rationale.append("Weather conditions suitable for treatment application")
        else:
            rationale.append("Weather conditions not optimal for treatment")
        
        rationale.append(f"Overall treatment score: {treatment_score:.1f}/100")
        
        return rationale
    
    def _assess_resistance_risk(self, crop_id: str, target_pests: List[str]) -> str:
        """Assess pesticide resistance risk for current situation"""
        
        # This would integrate with resistance monitoring data
        # For now, provide general risk assessment
        
        high_risk_pests = ["corn_rootworm", "armyworm"]  # Known resistance issues
        
        for pest_id in target_pests:
            if pest_id in high_risk_pests:
                return "high"
        
        return "moderate"
    
    def implement_resistance_management(self, location_id: str, pest_id: str, 
                                      treatment_history: List[str]) -> Dict[str, Any]:
        """Implement resistance management strategy"""
        
        # Analyze treatment history for mode of action patterns
        moa_usage = self._analyze_mode_of_action_usage(treatment_history)
        
        # Check for overuse of any single mode of action
        resistance_warnings = []
        alternative_modes = []
        
        for moa_group, usage_count in moa_usage.items():
            if usage_count >= self.system_parameters['mode_rotation_interval_applications']:
                resistance_warnings.append(f"Overuse of {moa_group} detected")
                
                # Find alternative modes of action
                for group, pesticides in self.mode_of_action_groups.items():
                    if group != moa_group:
                        alternative_modes.extend(pesticides)
        
        # Create resistance monitoring entry if needed
        monitoring_id = f"RES_{location_id}_{pest_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if resistance_warnings:
            monitoring = ResistanceMonitoring(
                monitoring_id=monitoring_id,
                location_id=location_id,
                pest_id=pest_id,
                pesticide_mode_of_action=max(moa_usage.keys(), key=moa_usage.get),  # Most used MOA
                resistance_status="developing",
                management_recommendations=[
                    "Rotate to different mode of action",
                    "Consider non-chemical alternatives",
                    "Monitor treatment efficacy closely"
                ],
                alternative_modes_available=alternative_modes[:3]  # Top 3 alternatives
            )
            
            self.resistance_monitoring[monitoring_id] = monitoring
            
            # Update statistics
            self.imp_statistics['resistance_incidents'] += 1
        
        return {
            "resistance_risk_detected": len(resistance_warnings) > 0,
            "warnings": resistance_warnings,
            "recommended_alternatives": alternative_modes[:3],
            "monitoring_initiated": len(resistance_warnings) > 0
        }
    
    def _analyze_mode_of_action_usage(self, treatment_history: List[str]) -> Dict[str, int]:
        """Analyze mode of action usage patterns in treatment history"""
        
        moa_usage = {}
        
        for treatment in treatment_history[-10:]:  # Last 10 treatments
            # Find mode of action group for this treatment
            for moa_group, pesticides in self.mode_of_action_groups.items():
                if treatment in pesticides:
                    moa_usage[moa_group] = moa_usage.get(moa_group, 0) + 1
                    break
        
        return moa_usage
    
    def evaluate_program_performance(self, program_id: str) -> Dict[str, Any]:
        """Evaluate IPM program performance and sustainability"""
        
        if program_id not in self.active_programs:
            return {"error": "Program not found"}
        
        program = self.active_programs[program_id]
        
        # Calculate performance metrics
        performance_metrics = {}
        
        # Economic performance
        total_yield_protected = sum(program.pest_control_efficacy.values())
        program_roi = (total_yield_protected - program.total_program_cost) / program.total_program_cost
        
        performance_metrics['economic'] = {
            'return_on_investment': program_roi,
            'cost_per_acre': program.cost_per_acre,
            'yield_protection': total_yield_protected
        }
        
        # Environmental performance
        total_pesticide_load = sum(
            self.ipm_tactics[tactic].environmental_impact_score
            for tactic in program.active_tactics
            if self.ipm_tactics[tactic].tactic_type == IPMTactic.CHEMICAL
        )
        
        beneficial_conservation = sum(
            -self.ipm_tactics[tactic].beneficial_impact  # Negative impact = positive conservation
            for tactic in program.active_tactics
            if self.ipm_tactics[tactic].beneficial_impact < 0
        )
        
        performance_metrics['environmental'] = {
            'pesticide_load_index': total_pesticide_load,
            'beneficial_conservation_score': beneficial_conservation,
            'pollinator_safety_rating': self._assess_pollinator_safety(program)
        }
        
        # Sustainability assessment
        sustainability_score = self._calculate_sustainability_score(performance_metrics)
        
        performance_metrics['sustainability'] = {
            'overall_score': sustainability_score,
            'rating': self._get_sustainability_rating(sustainability_score),
            'improvement_recommendations': self._generate_improvement_recommendations(program, sustainability_score)
        }
        
        # Update program with performance data
        program.program_effectiveness = (program_roi + beneficial_conservation) * 50  # Scale to 0-100
        program.sustainability_rating = performance_metrics['sustainability']['rating']
        program.improvement_recommendations = performance_metrics['sustainability']['improvement_recommendations']
        
        return performance_metrics
    
    def _assess_pollinator_safety(self, program: IPMProgram) -> str:
        """Assess overall pollinator safety of IPM program"""
        
        safety_ratings = []
        for tactic in program.active_tactics + program.planned_tactics + program.contingency_tactics:
            tactic_data = self.ipm_tactics[tactic]
            safety_ratings.append(tactic_data.pollinator_safety_rating)
        
        if "hazardous" in safety_ratings:
            return "hazardous"
        elif "caution" in safety_ratings:
            return "caution"
        else:
            return "safe"
    
    def _calculate_sustainability_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall sustainability score (0-100)"""
        
        economic_score = min(max(metrics['economic']['return_on_investment'] * 25, 0), 40)  # 0-40 points
        
        environmental_score = 0
        environmental_score += max(0, 30 - metrics['environmental']['pesticide_load_index'] * 3)  # 0-30 points
        environmental_score += metrics['environmental']['beneficial_conservation_score'] * 30  # 0-30 points
        environmental_score = min(environmental_score, 50)  # Cap at 50 points
        
        pollinator_bonus = 10 if metrics['environmental']['pollinator_safety_rating'] == "safe" else 0
        
        total_score = economic_score + environmental_score + pollinator_bonus
        return min(total_score, 100)
    
    def _get_sustainability_rating(self, score: float) -> str:
        """Convert sustainability score to rating"""
        
        if score >= 80:
            return "excellent"
        elif score >= 65:
            return "good"
        elif score >= 50:
            return "fair"
        else:
            return "poor"
    
    def _generate_improvement_recommendations(self, program: IPMProgram, score: float) -> List[str]:
        """Generate recommendations to improve program sustainability"""
        
        recommendations = []
        
        if score < 65:
            recommendations.append("Consider increasing use of biological control tactics")
        
        if score < 50:
            recommendations.append("Reduce reliance on chemical control methods")
            recommendations.append("Implement habitat management for beneficial insects")
        
        # Check for specific improvements
        chemical_tactics = [t for t in program.active_tactics 
                          if self.ipm_tactics[t].tactic_type == IPMTactic.CHEMICAL]
        
        if len(chemical_tactics) > 2:
            recommendations.append("Diversify control tactics beyond chemical methods")
        
        biological_tactics = [t for t in program.active_tactics + program.planned_tactics
                             if self.ipm_tactics[t].tactic_type == IPMTactic.BIOLOGICAL]
        
        if len(biological_tactics) < 1:
            recommendations.append("Add biological control components to program")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    # Event handlers for system integration
    def _handle_pest_monitoring(self, event_data: Dict[str, Any]):
        """Handle pest monitoring results for IPM decision making"""
        location_id = event_data.get("location_id")
        pests_detected = event_data.get("pests_detected", {})
        
        if pests_detected:
            # Trigger treatment decision evaluation
            pest_situation = {
                'crop_id': 'corn',  # Would get from field data
                'pest_densities': pests_detected,
                'beneficial_densities': {},  # Would get from monitoring
                'crop_stage_days': 50  # Would get from crop growth system
            }
            
            environmental_conditions = {
                'temperature_c': 22,
                'wind_speed_kmh': 8,
                'humidity_percent': 65,
                'rain_forecast_hours': 6
            }
            
            decision = self.evaluate_treatment_decision(location_id, pest_situation, environmental_conditions)
    
    def _handle_threshold_exceeded(self, event_data: Dict[str, Any]):
        """Handle economic threshold exceeded events"""
        location_id = event_data.get("location_id")
        pest_id = event_data.get("pest_id")
        
        # Generate urgent treatment recommendation
        self.event_system.emit_event("urgent_treatment_needed", {
            "location_id": location_id,
            "pest_id": pest_id,
            "urgency": "high",
            "recommended_action": "immediate_treatment"
        })
    
    def _handle_treatment_completed(self, event_data: Dict[str, Any]):
        """Handle treatment application completion"""
        location_id = event_data.get("location_id")
        treatment_type = event_data.get("treatment_type")
        efficacy = event_data.get("efficacy", 0.8)
        
        # Update program performance tracking
        for program in self.active_programs.values():
            if program.location_id == location_id:
                program.treatment_history.append({
                    "date": datetime.now(),
                    "treatment": treatment_type,
                    "efficacy": efficacy
                })
                
                # Update statistics
                self.imp_statistics['treatments_applied'] += 1
                break
    
    def _handle_crop_stage_change(self, event_data: Dict[str, Any]):
        """Handle crop growth stage changes affecting treatment timing"""
        location_id = event_data.get("location_id")
        crop_id = event_data.get("crop_id")
        new_stage = event_data.get("growth_stage")
        
        # Check if any programs need tactic adjustments based on crop stage
        for program in self.active_programs.values():
            if program.location_id == location_id and program.crop_id == crop_id:
                self._adjust_program_for_crop_stage(program, new_stage)
    
    def _adjust_program_for_crop_stage(self, program: IPMProgram, crop_stage: str):
        """Adjust IPM program tactics based on crop growth stage"""
        
        # Different stages may require different tactics
        # This would be more sophisticated in a full implementation
        
        if crop_stage == "reproductive":
            # Move biological tactics from planned to active
            biological_tactics = [t for t in program.planned_tactics 
                                if self.ipm_tactics[t].tactic_type == IPMTactic.BIOLOGICAL]
            
            for tactic in biological_tactics:
                if tactic not in program.active_tactics:
                    program.active_tactics.append(tactic)
                    program.planned_tactics.remove(tactic)
    
    def _handle_weather_forecast(self, event_data: Dict[str, Any]):
        """Handle weather forecast updates affecting treatment timing"""
        location_id = event_data.get("location_id")
        forecast = event_data.get("forecast", {})
        
        # Adjust treatment timing recommendations based on weather
        suitable_conditions = self._assess_weather_suitability(forecast)
        
        if not suitable_conditions:
            # Emit weather delay recommendation
            self.event_system.emit_event("treatment_weather_delay", {
                "location_id": location_id,
                "reason": "unsuitable_weather",
                "forecast": forecast
            })
    
    def get_ipm_system_status(self) -> Dict[str, Any]:
        """Get comprehensive IPM system status"""
        
        return {
            "system_status": "active" if self.is_initialized else "inactive",
            "ipm_tactics_available": len(self.ipm_tactics),
            "active_programs": len(self.active_programs),
            "treatment_decisions_made": len(self.treatment_decisions),
            "resistance_monitoring_cases": len(self.resistance_monitoring),
            "system_statistics": self.imp_statistics
        }

# Global convenience functions
def get_ipm_system() -> Optional[IntegratedPestManagement]:
    """Get the global IPM system instance"""
    # This would typically be managed by a system registry
    return None

def create_ipm_program_for_field(location_id: str, crop_id: str, target_pests: List[str]) -> Optional[IPMProgram]:
    """Convenience function to create IPM program for field"""
    system = get_ipm_system()
    if system:
        program_name = f"IPM Program - {crop_id.title()} {datetime.now().year}"
        return system.create_ipm_program(location_id, crop_id, program_name, target_pests)
    return None

def evaluate_treatment_need(location_id: str, pest_densities: Dict[str, float]) -> Optional[TreatmentDecision]:
    """Convenience function to evaluate treatment need"""
    system = get_ipm_system()
    if system:
        pest_situation = {
            'crop_id': 'corn',
            'pest_densities': pest_densities,
            'beneficial_densities': {},
            'crop_stage_days': 50
        }
        environmental_conditions = {
            'temperature_c': 22,
            'wind_speed_kmh': 8,
            'humidity_percent': 65,
            'rain_forecast_hours': 6
        }
        return system.evaluate_treatment_decision(location_id, pest_situation, environmental_conditions)
    return None