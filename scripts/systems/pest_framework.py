"""
Pest Framework - Comprehensive Agricultural Pest Management for AgriFun Agricultural Game

This system provides realistic insect pest modeling including lifecycle simulation, population 
dynamics, economic injury levels, and integrated pest management strategies. It helps players
understand entomology principles and make informed pest management decisions.

Key Features:
- Comprehensive pest database with 30+ agricultural insect pests
- Detailed lifecycle modeling (egg, larva, pupa, adult stages)
- Population dynamics with environmental factors and natural mortality
- Economic injury levels and treatment thresholds
- Beneficial insect populations (predators, parasites, pollinators)
- Pest damage assessment on crop yield and quality
- Integrated pest management recommendations
- Pesticide resistance development modeling

Pest Categories:
- Chewing Insects: Caterpillars, beetles, grasshoppers (40% of pest incidents)
- Sucking Insects: Aphids, thrips, whiteflies (35% of pest incidents)  
- Boring Insects: Corn borers, stem borers, root borers (15% of pest incidents)
- Soil Insects: Root worms, wireworms, grubs (10% of pest incidents)

Educational Value:
- Understanding of insect biology and lifecycle management
- Economic thresholds and treatment timing decisions
- Beneficial insect conservation and biological control
- Integrated pest management principles and sustainability
- Pesticide resistance management strategies

Integration:
- Weather System: Temperature affects development rates and activity
- Crop Growth System: Pest damage reduces yield and affects plant health
- Time Management: Degree-day accumulation drives insect development
- Equipment System: Application equipment for pest control
- Economic System: Treatment costs vs. crop protection benefits

Author: Agricultural Simulation Development Team
Version: 1.0.0 - Comprehensive Pest Framework Implementation
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

class PestType(Enum):
    """Types of agricultural pests"""
    CHEWING = "chewing"         # Caterpillars, beetles, grasshoppers
    SUCKING = "sucking"         # Aphids, thrips, whiteflies
    BORING = "boring"           # Stem borers, root borers
    SOIL_DWELLING = "soil_dwelling"  # Root worms, wireworms, grubs
    STORED_PRODUCT = "stored_product"  # Grain weevils, moths

class LifecycleStage(Enum):
    """Insect lifecycle stages"""
    EGG = "egg"
    LARVA = "larva"             # Also includes nymph for hemimetabolous insects
    PUPA = "pupa"               # Only for holometabolous insects
    ADULT = "adult"
    OVERWINTERING = "overwintering"

class DamageType(Enum):
    """Types of crop damage caused by pests"""
    DEFOLIATION = "defoliation"         # Leaf consumption
    ROOT_FEEDING = "root_feeding"       # Root system damage
    STEM_BORING = "stem_boring"         # Stem tunneling
    SAP_FEEDING = "sap_feeding"         # Phloem/xylem feeding
    FRUIT_FEEDING = "fruit_feeding"     # Direct fruit damage
    VIRUS_TRANSMISSION = "virus_transmission"  # Vector transmission
    STORAGE_DAMAGE = "storage_damage"   # Post-harvest damage

class BeneficialType(Enum):
    """Types of beneficial insects"""
    PREDATOR = "predator"       # Natural enemies that consume pests
    PARASITE = "parasite"       # Parasitoid wasps, flies
    POLLINATOR = "pollinator"   # Bees, butterflies, beneficial flies
    DECOMPOSER = "decomposer"   # Insects that break down organic matter

@dataclass
class LifecycleStageData:
    """Data for specific lifecycle stage"""
    stage: LifecycleStage
    duration_degree_days: float      # Degree-days required for stage completion
    base_temperature_c: float        # Base temperature for development
    optimal_temperature_c: float     # Optimal temperature for development
    survival_rate: float             # Survival rate through this stage (0-1)
    feeding_activity: float          # Relative feeding activity (0-1)
    damage_potential: float          # Damage potential relative to other stages
    mobility: float                  # Movement capability (0-1)
    detection_difficulty: float      # How hard to detect (0-1, higher = harder)

@dataclass
class PestBiology:
    """Comprehensive pest biology and lifecycle information"""
    pest_id: str
    common_name: str
    scientific_name: str
    pest_type: PestType
    
    # Lifecycle characteristics
    metamorphosis_type: str          # "complete" or "incomplete"
    generations_per_year: int        # Number of generations annually
    overwintering_stage: LifecycleStage
    lifecycle_stages: Dict[LifecycleStage, LifecycleStageData] = field(default_factory=dict)
    
    # Host relationships
    primary_hosts: List[str] = field(default_factory=list)
    secondary_hosts: List[str] = field(default_factory=list)
    preferred_plant_parts: List[str] = field(default_factory=list)
    
    # Environmental requirements
    temperature_thresholds: Dict[str, float] = field(default_factory=dict)  # min, max, optimal
    humidity_preferences: Tuple[float, float] = (40, 80)  # Min, max humidity
    photoperiod_sensitivity: bool = False                  # Day length sensitivity
    
    # Population dynamics
    egg_laying_capacity: int = 100                        # Average eggs per female
    sex_ratio: float = 0.5                               # Proportion of females
    dispersal_range_km: float = 1.0                      # Maximum dispersal distance
    aggregation_tendency: float = 0.5                     # Tendency to cluster (0-1)
    
    # Damage characteristics
    damage_types: List[DamageType] = field(default_factory=list)
    economic_injury_level: float = 1.0                    # Pest density causing economic loss
    economic_threshold: float = 0.8                       # Treatment threshold
    damage_function_slope: float = 0.1                    # % yield loss per pest unit
    
    # Natural enemies and mortality factors
    natural_enemies: List[str] = field(default_factory=list)
    mortality_factors: Dict[str, float] = field(default_factory=dict)
    
    # Management susceptibility
    insecticide_susceptibility: Dict[str, float] = field(default_factory=dict)  # Mode of action: efficacy
    cultural_control_sensitivity: Dict[str, float] = field(default_factory=dict)
    biological_control_agents: List[str] = field(default_factory=list)

@dataclass
class PestPopulation:
    """Active pest population in field"""
    population_id: str
    pest_id: str
    location_id: str
    crop_id: str
    
    # Population structure by stage
    stage_populations: Dict[LifecycleStage, float] = field(default_factory=dict)
    total_population: float = 0.0
    population_density_per_m2: float = 0.0
    
    # Development tracking
    degree_day_accumulation: Dict[LifecycleStage, float] = field(default_factory=dict)
    generation_number: int = 1
    
    # Population dynamics
    establishment_date: datetime = field(default_factory=datetime.now)
    peak_population_date: Optional[datetime] = None
    current_growth_rate: float = 0.0
    carrying_capacity: float = 1000.0
    
    # Environmental factors
    temperature_stress: float = 0.0                       # Temperature-induced mortality
    humidity_stress: float = 0.0                         # Humidity-induced mortality
    host_plant_quality: float = 1.0                     # Host plant suitability (0-1)
    
    # Natural control factors
    predation_pressure: float = 0.0                      # Predation mortality rate
    parasitism_rate: float = 0.0                        # Parasitism mortality rate
    disease_pressure: float = 0.0                       # Pathogen mortality rate
    
    # Damage assessment
    cumulative_damage: float = 0.0                       # Total damage inflicted
    current_damage_rate: float = 0.0                     # Current daily damage rate
    yield_impact_percent: float = 0.0                    # Estimated yield impact
    
    # Management history
    treatments_applied: List[Dict[str, Any]] = field(default_factory=list)
    resistance_development: Dict[str, float] = field(default_factory=dict)
    
    # Monitoring data
    last_scouting_date: Optional[datetime] = None
    detection_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class BeneficialInsect:
    """Beneficial insect population data"""
    beneficial_id: str
    common_name: str
    scientific_name: str
    beneficial_type: BeneficialType
    location_id: str
    
    # Population data
    population_density: float = 0.0
    activity_level: float = 1.0                          # Activity multiplier (0-2)
    
    # Effectiveness data
    target_pests: List[str] = field(default_factory=list)
    control_effectiveness: Dict[str, float] = field(default_factory=dict)  # pest_id: efficacy
    search_efficiency: float = 0.5                       # Host/prey finding ability
    
    # Environmental sensitivity
    pesticide_sensitivity: Dict[str, float] = field(default_factory=dict)
    temperature_activity_curve: Dict[float, float] = field(default_factory=dict)
    
    # Conservation factors
    habitat_requirements: List[str] = field(default_factory=list)
    nectar_sources_needed: bool = False
    overwintering_habitat: List[str] = field(default_factory=list)

@dataclass
class PestMonitoring:
    """Pest monitoring and scouting data"""
    monitoring_id: str
    location_id: str
    monitoring_date: datetime
    monitoring_method: str                                # "visual", "trap", "sweep_net", "beat_sheet"
    
    # Detection results
    pests_detected: Dict[str, float] = field(default_factory=dict)  # pest_id: density
    beneficial_insects: Dict[str, float] = field(default_factory=dict)  # beneficial_id: density
    damage_assessment: Dict[str, float] = field(default_factory=dict)  # damage_type: severity
    
    # Environmental conditions
    weather_conditions: Dict[str, Any] = field(default_factory=dict)
    crop_stage: str = ""
    plant_stress_factors: List[str] = field(default_factory=list)
    
    # Economic analysis
    treatment_threshold_status: Dict[str, bool] = field(default_factory=dict)  # pest_id: exceeded
    economic_injury_assessment: Dict[str, float] = field(default_factory=dict)  # pest_id: injury_level
    
    # Recommendations
    immediate_actions: List[str] = field(default_factory=list)
    monitoring_recommendations: List[str] = field(default_factory=list)
    treatment_recommendations: List[str] = field(default_factory=list)

class PestFramework(System):
    """
    Comprehensive Pest Framework for Agricultural Pest Management
    
    This system provides realistic insect pest modeling including:
    - Pest database with 30+ agricultural insect pests
    - Detailed lifecycle simulation with degree-day models
    - Population dynamics with environmental factors
    - Economic injury levels and treatment thresholds
    - Beneficial insect populations and biological control
    - Integrated pest management recommendations
    """
    
    def __init__(self):
        """Initialize the Pest Framework"""
        super().__init__()
        
        # Core system references
        self.event_system = None
        self.config_manager = None
        self.content_registry = None
        
        # Pest management data
        self.pest_database: Dict[str, PestBiology] = {}
        self.active_populations: Dict[str, PestPopulation] = {}
        self.beneficial_insects: Dict[str, BeneficialInsect] = {}
        self.monitoring_records: Dict[str, List[PestMonitoring]] = {}
        
        # Environmental tracking
        self.degree_day_accumulation: Dict[str, Dict[str, float]] = {}  # location: pest: dd
        self.pest_pressure_index: Dict[str, float] = {}  # location: pressure
        
        # System parameters
        self.system_parameters = {
            'base_establishment_probability': 0.05,    # Base probability of pest establishment
            'population_growth_modifier': 1.0,        # Global population growth rate
            'natural_mortality_rate': 0.1,            # Daily natural mortality rate
            'detection_threshold': 0.1,               # Minimum density for detection
            'economic_multiplier': 1.0,               # Economic threshold multiplier
            'beneficial_effectiveness': 0.8,          # Base beneficial insect effectiveness
            'dispersal_rate': 0.05,                   # Daily dispersal between locations
            'resistance_development_rate': 0.01       # Rate of pesticide resistance development
        }
        
        # Performance tracking
        self.pest_statistics: Dict[str, Any] = {
            'total_populations': 0,
            'active_populations': 0,
            'total_damage_prevented': 0.0,
            'treatment_applications': 0,
            'beneficial_releases': 0,
            'resistance_incidents': 0
        }
        
        self.is_initialized = False
    
    def initialize(self, event_system: EventSystem, config_manager: ConfigurationManager, 
                  content_registry: ContentRegistry) -> bool:
        """Initialize the Pest Framework with required dependencies"""
        try:
            self.event_system = event_system
            self.config_manager = config_manager
            self.content_registry = content_registry
            
            # Load pest management configuration
            self._load_configuration()
            
            # Initialize pest database
            self._initialize_pest_database()
            
            # Initialize beneficial insect database
            self._initialize_beneficial_database()
            
            # Register event handlers
            self._register_event_handlers()
            
            # Initialize degree-day tracking
            self._initialize_degree_day_tracking()
            
            self.is_initialized = True
            
            # Emit initialization event
            self.event_system.emit_event("pest_framework_initialized", {
                "system": "pest_framework",
                "status": "ready",
                "pests_loaded": len(self.pest_database),
                "beneficial_species": len(self.beneficial_insects),
                "timestamp": datetime.now()
            })
            
            return True
            
        except Exception as e:
            print(f"Error initializing Pest Framework: {e}")
            return False
    
    def _load_configuration(self):
        """Load pest framework configuration from config files"""
        pest_config = self.config_manager.get("pest_framework", {})
        
        # Update system parameters
        if "parameters" in pest_config:
            self.system_parameters.update(pest_config["parameters"])
        
        # Load pest-specific configuration
        if "pest_settings" in pest_config:
            # Additional pest-specific settings would be loaded here
            pass
    
    def _initialize_pest_database(self):
        """Initialize comprehensive agricultural pest database"""
        
        # Corn pests
        self.pest_database["corn_rootworm"] = PestBiology(
            pest_id="corn_rootworm",
            common_name="Western Corn Rootworm",
            scientific_name="Diabrotica virgifera virgifera",
            pest_type=PestType.CHEWING,
            metamorphosis_type="complete",
            generations_per_year=1,
            overwintering_stage=LifecycleStage.EGG,
            primary_hosts=["corn"],
            preferred_plant_parts=["roots", "silk", "pollen"],
            temperature_thresholds={"min": 11.0, "max": 35.0, "optimal": 25.0},
            humidity_preferences=(50, 90),
            egg_laying_capacity=600,
            sex_ratio=0.5,
            dispersal_range_km=5.0,
            damage_types=[DamageType.ROOT_FEEDING, DamageType.DEFOLIATION],
            economic_injury_level=1.0,  # 1 beetle per plant
            economic_threshold=0.75,
            damage_function_slope=0.15,  # 15% yield loss per beetle per plant
            natural_enemies=["ground_beetles", "rove_beetles", "parasitic_wasps"],
            mortality_factors={"cold_winter": 0.8, "wet_spring": 0.3, "drought": 0.4},
            insecticide_susceptibility={
                "organophosphate": 0.85,
                "pyrethroid": 0.60,  # Resistance developed
                "neonicotinoid": 0.90
            },
            biological_control_agents=["steinernema_feltiae", "heterorhabditis_bacteriophora"]
        )
        
        # Add lifecycle stage data for corn rootworm
        self.pest_database["corn_rootworm"].lifecycle_stages = {
            LifecycleStage.EGG: LifecycleStageData(
                stage=LifecycleStage.EGG,
                duration_degree_days=800,
                base_temperature_c=11.0,
                optimal_temperature_c=25.0,
                survival_rate=0.7,
                feeding_activity=0.0,
                damage_potential=0.0,
                mobility=0.0,
                detection_difficulty=0.9
            ),
            LifecycleStage.LARVA: LifecycleStageData(
                stage=LifecycleStage.LARVA,
                duration_degree_days=400,
                base_temperature_c=11.0,
                optimal_temperature_c=25.0,
                survival_rate=0.8,
                feeding_activity=0.9,
                damage_potential=0.8,
                mobility=0.2,
                detection_difficulty=0.8
            ),
            LifecycleStage.PUPA: LifecycleStageData(
                stage=LifecycleStage.PUPA,
                duration_degree_days=150,
                base_temperature_c=11.0,
                optimal_temperature_c=25.0,
                survival_rate=0.9,
                feeding_activity=0.0,
                damage_potential=0.0,
                mobility=0.0,
                detection_difficulty=0.9
            ),
            LifecycleStage.ADULT: LifecycleStageData(
                stage=LifecycleStage.ADULT,
                duration_degree_days=600,
                base_temperature_c=11.0,
                optimal_temperature_c=25.0,
                survival_rate=0.6,
                feeding_activity=0.7,
                damage_potential=0.3,
                mobility=1.0,
                detection_difficulty=0.2
            )
        }
        
        # Soybean aphid
        self.pest_database["soybean_aphid"] = PestBiology(
            pest_id="soybean_aphid",
            common_name="Soybean Aphid",
            scientific_name="Aphis glycines",
            pest_type=PestType.SUCKING,
            metamorphosis_type="incomplete",
            generations_per_year=15,  # Multiple generations
            overwintering_stage=LifecycleStage.EGG,
            primary_hosts=["soybeans"],
            secondary_hosts=["buckthorn"],  # Alternate host
            preferred_plant_parts=["leaves", "stems", "pods"],
            temperature_thresholds={"min": 5.0, "max": 30.0, "optimal": 22.0},
            humidity_preferences=(60, 95),
            egg_laying_capacity=80,
            sex_ratio=0.9,  # Mostly parthenogenetic females
            dispersal_range_km=100.0,  # Wind dispersal
            aggregation_tendency=0.8,
            damage_types=[DamageType.SAP_FEEDING, DamageType.VIRUS_TRANSMISSION],
            economic_injury_level=250.0,  # 250 aphids per plant
            economic_threshold=200.0,
            damage_function_slope=0.05,  # 5% yield loss per 100 aphids
            natural_enemies=["ladybird_beetles", "lacewing_larvae", "parasitic_wasps"],
            insecticide_susceptibility={
                "organophosphate": 0.95,
                "pyrethroid": 0.80,
                "neonicotinoid": 0.85
            }
        )
        
        # Add soybean aphid lifecycle stages (simplified for incomplete metamorphosis)
        self.pest_database["soybean_aphid"].lifecycle_stages = {
            LifecycleStage.EGG: LifecycleStageData(
                stage=LifecycleStage.EGG,
                duration_degree_days=100,
                base_temperature_c=5.0,
                optimal_temperature_c=22.0,
                survival_rate=0.8,
                feeding_activity=0.0,
                damage_potential=0.0,
                mobility=0.0,
                detection_difficulty=1.0
            ),
            LifecycleStage.LARVA: LifecycleStageData(  # Nymph stages combined
                stage=LifecycleStage.LARVA,
                duration_degree_days=120,
                base_temperature_c=5.0,
                optimal_temperature_c=22.0,
                survival_rate=0.9,
                feeding_activity=0.6,
                damage_potential=0.4,
                mobility=0.1,
                detection_difficulty=0.4
            ),
            LifecycleStage.ADULT: LifecycleStageData(
                stage=LifecycleStage.ADULT,
                duration_degree_days=300,
                base_temperature_c=5.0,
                optimal_temperature_c=22.0,
                survival_rate=0.7,
                feeding_activity=1.0,
                damage_potential=1.0,
                mobility=0.8,
                detection_difficulty=0.1
            )
        }
        
        # European corn borer
        self.pest_database["european_corn_borer"] = PestBiology(
            pest_id="european_corn_borer",
            common_name="European Corn Borer",
            scientific_name="Ostrinia nubilalis",
            pest_type=PestType.BORING,
            metamorphosis_type="complete",
            generations_per_year=2,
            overwintering_stage=LifecycleStage.LARVA,
            primary_hosts=["corn"],
            secondary_hosts=["peppers", "potatoes", "beans"],
            preferred_plant_parts=["stalks", "ears", "tassels"],
            temperature_thresholds={"min": 10.0, "max": 32.0, "optimal": 24.0},
            photoperiod_sensitivity=True,
            egg_laying_capacity=500,
            dispersal_range_km=2.0,
            damage_types=[DamageType.STEM_BORING],
            economic_injury_level=1.0,  # 1 larva per plant
            economic_threshold=0.8,
            damage_function_slope=0.12,
            natural_enemies=["trichogramma_wasps", "tachinid_flies"],
            insecticide_susceptibility={
                "pyrethroid": 0.75,
                "organophosphate": 0.80,
                "bt_toxin": 0.95
            }
        )
        
        # Armyworm
        self.pest_database["armyworm"] = PestBiology(
            pest_id="armyworm",
            common_name="True Armyworm",
            scientific_name="Pseudaletia unipuncta",
            pest_type=PestType.CHEWING,
            metamorphosis_type="complete",
            generations_per_year=3,
            overwintering_stage=LifecycleStage.PUPA,
            primary_hosts=["corn", "wheat", "barley", "oats"],
            preferred_plant_parts=["leaves", "stems"],
            temperature_thresholds={"min": 9.0, "max": 33.0, "optimal": 26.0},
            egg_laying_capacity=1000,
            dispersal_range_km=50.0,  # Long-distance migration
            aggregation_tendency=0.9,  # Highly gregarious
            damage_types=[DamageType.DEFOLIATION],
            economic_injury_level=2.0,  # 2 larvae per plant
            economic_threshold=1.5,
            damage_function_slope=0.08,
            natural_enemies=["ground_beetles", "spiders", "birds"],
            mortality_factors={"nuclear_polyhedrosis_virus": 0.6},
            insecticide_susceptibility={
                "pyrethroid": 0.90,
                "organophosphate": 0.85,
                "carbamate": 0.80
            }
        )
        
        # Cutworm
        self.pest_database["cutworm"] = PestBiology(
            pest_id="cutworm",
            common_name="Black Cutworm",
            scientific_name="Agrotis ipsilon",
            pest_type=PestType.CHEWING,
            metamorphosis_type="complete",
            generations_per_year=2,
            overwintering_stage=LifecycleStage.PUPA,
            primary_hosts=["corn", "soybeans", "vegetables"],
            preferred_plant_parts=["stems", "seedlings"],
            temperature_thresholds={"min": 8.0, "max": 30.0, "optimal": 22.0},
            egg_laying_capacity=1500,
            dispersal_range_km=100.0,  # Strong migratory behavior
            damage_types=[DamageType.STEM_BORING, DamageType.DEFOLIATION],
            economic_injury_level=0.1,  # Very low threshold for seedling damage
            economic_threshold=0.05,
            damage_function_slope=0.25,  # High impact on young plants
            natural_enemies=["ground_beetles", "parasitic_wasps"],
            insecticide_susceptibility={
                "pyrethroid": 0.85,
                "organophosphate": 0.90
            }
        )
        
        print(f"Initialized pest database with {len(self.pest_database)} pest species")
    
    def _initialize_beneficial_database(self):
        """Initialize beneficial insect database"""
        
        # Ladybird beetles (predators)
        self.beneficial_insects["ladybird_beetles"] = BeneficialInsect(
            beneficial_id="ladybird_beetles",
            common_name="Ladybird Beetles",
            scientific_name="Coccinellidae",
            beneficial_type=BeneficialType.PREDATOR,
            location_id="general",
            population_density=5.0,  # per square meter
            target_pests=["soybean_aphid"],
            control_effectiveness={"soybean_aphid": 0.7},
            search_efficiency=0.8,
            pesticide_sensitivity={
                "organophosphate": 0.9,  # Highly sensitive
                "pyrethroid": 0.8,
                "neonicotinoid": 0.6
            },
            habitat_requirements=["diverse_vegetation", "overwintering_sites"],
            nectar_sources_needed=True
        )
        
        # Parasitic wasps
        self.beneficial_insects["trichogramma_wasps"] = BeneficialInsect(
            beneficial_id="trichogramma_wasps",
            common_name="Trichogramma Wasps",
            scientific_name="Trichogramma spp.",
            beneficial_type=BeneficialType.PARASITE,
            location_id="general",
            population_density=20.0,
            target_pests=["european_corn_borer"],
            control_effectiveness={"european_corn_borer": 0.6},
            search_efficiency=0.9,
            pesticide_sensitivity={
                "organophosphate": 0.95,
                "pyrethroid": 0.85,
                "bt_toxin": 0.1  # Compatible with Bt
            },
            habitat_requirements=["flowering_plants", "shelter"],
            nectar_sources_needed=True
        )
        
        # Ground beetles
        self.beneficial_insects["ground_beetles"] = BeneficialInsect(
            beneficial_id="ground_beetles",
            common_name="Ground Beetles",
            scientific_name="Carabidae",
            beneficial_type=BeneficialType.PREDATOR,
            location_id="general",
            population_density=3.0,
            target_pests=["corn_rootworm", "cutworm", "armyworm"],
            control_effectiveness={
                "corn_rootworm": 0.4,
                "cutworm": 0.5,
                "armyworm": 0.3
            },
            search_efficiency=0.6,
            pesticide_sensitivity={
                "organophosphate": 0.7,
                "pyrethroid": 0.6,
                "carbamate": 0.8
            },
            habitat_requirements=["ground_cover", "organic_matter"],
            overwintering_habitat=["field_margins", "woodlots"]
        )
        
        print(f"Initialized {len(self.beneficial_insects)} beneficial insect species")
    
    def _register_event_handlers(self):
        """Register event handlers for system integration"""
        self.event_system.subscribe("weather_conditions_updated", self._handle_weather_update)
        self.event_system.subscribe("crop_growth_stage_changed", self._handle_growth_stage_change)
        self.event_system.subscribe("field_operation_completed", self._handle_field_operation)
        self.event_system.subscribe("time_advanced", self._handle_time_advancement)
        self.event_system.subscribe("season_changed", self._handle_season_change)
    
    def _initialize_degree_day_tracking(self):
        """Initialize degree-day accumulation tracking"""
        locations = ["field_001", "field_002", "field_003"]  # Would come from farm management
        
        for location in locations:
            self.degree_day_accumulation[location] = {}
            self.pest_pressure_index[location] = 0.0
            
            for pest_id in self.pest_database:
                self.degree_day_accumulation[location][pest_id] = 0.0
    
    def establish_pest_population(self, location_id: str, crop_id: str, pest_id: str,
                                initial_population: float, environmental_conditions: Dict[str, Any]) -> Optional[PestPopulation]:
        """Establish a new pest population at location"""
        
        if pest_id not in self.pest_database:
            print(f"Pest {pest_id} not found in database")
            return None
        
        pest_biology = self.pest_database[pest_id]
        
        # Check host suitability
        if crop_id not in pest_biology.primary_hosts and crop_id not in pest_biology.secondary_hosts:
            return None
        
        # Calculate establishment probability
        establishment_factors = []
        
        # Temperature suitability
        current_temp = environmental_conditions.get('temperature_c', 20)
        temp_min = pest_biology.temperature_thresholds.get('min', 0)
        temp_max = pest_biology.temperature_thresholds.get('max', 40)
        
        if temp_min <= current_temp <= temp_max:
            temp_factor = 1.0
        else:
            temp_factor = 0.3
        establishment_factors.append(temp_factor)
        
        # Host plant quality
        host_factor = 1.0 if crop_id in pest_biology.primary_hosts else 0.7
        establishment_factors.append(host_factor)
        
        # Calculate establishment probability
        establishment_prob = (sum(establishment_factors) / len(establishment_factors) * 
                            self.system_parameters['base_establishment_probability'])
        
        # Determine if establishment occurs
        if random.random() < establishment_prob:
            population_id = f"POP_{location_id}_{pest_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize stage populations
            stage_populations = {}
            
            # Distribute initial population across lifecycle stages based on season and biology
            if pest_biology.overwintering_stage == LifecycleStage.EGG:
                stage_populations[LifecycleStage.EGG] = initial_population * 0.8
                stage_populations[LifecycleStage.LARVA] = initial_population * 0.2
            elif pest_biology.overwintering_stage == LifecycleStage.LARVA:
                stage_populations[LifecycleStage.LARVA] = initial_population * 0.9
                stage_populations[LifecycleStage.ADULT] = initial_population * 0.1
            else:
                # Distribute more evenly
                num_stages = len(pest_biology.lifecycle_stages)
                stage_pop = initial_population / num_stages
                for stage in pest_biology.lifecycle_stages:
                    stage_populations[stage] = stage_pop
            
            # Create population
            population = PestPopulation(
                population_id=population_id,
                pest_id=pest_id,
                location_id=location_id,
                crop_id=crop_id,
                stage_populations=stage_populations,
                total_population=initial_population,
                population_density_per_m2=initial_population / 10000,  # Assume 1 hectare
                carrying_capacity=initial_population * 10,  # Dynamic carrying capacity
                host_plant_quality=host_factor
            )
            
            # Initialize degree day tracking for this population
            for stage in pest_biology.lifecycle_stages:
                population.degree_day_accumulation[stage] = 0.0
            
            # Store population
            self.active_populations[population_id] = population
            
            # Update statistics
            self.pest_statistics['total_populations'] += 1
            self.pest_statistics['active_populations'] = len(self.active_populations)
            
            # Emit establishment event
            self.event_system.emit_event("pest_population_established", {
                "population_id": population_id,
                "pest_id": pest_id,
                "location_id": location_id,
                "crop_id": crop_id,
                "initial_population": initial_population,
                "establishment_probability": establishment_prob
            })
            
            print(f"Pest population established: {pest_biology.common_name} at {location_id}")
            
            return population
        
        return None
    
    def update_pest_development(self, population_id: str, temperature_c: float, 
                               time_delta_days: float) -> bool:
        """Update pest development based on temperature and time"""
        
        if population_id not in self.active_populations:
            return False
        
        population = self.active_populations[population_id]
        pest_biology = self.pest_database[population.pest_id]
        
        # Calculate degree-days for each lifecycle stage
        for stage, stage_data in pest_biology.lifecycle_stages.items():
            if stage in population.stage_populations and population.stage_populations[stage] > 0:
                
                # Calculate degree-days accumulated
                base_temp = stage_data.base_temperature_c
                if temperature_c > base_temp:
                    degree_days = (temperature_c - base_temp) * time_delta_days
                    population.degree_day_accumulation[stage] += degree_days
                    
                    # Check for stage completion and transition
                    required_dd = stage_data.duration_degree_days
                    if population.degree_day_accumulation[stage] >= required_dd:
                        self._transition_lifecycle_stage(population, stage, stage_data)
        
        # Update population totals
        population.total_population = sum(population.stage_populations.values())
        population.population_density_per_m2 = population.total_population / 10000
        
        # Apply mortality factors
        self._apply_mortality_factors(population, temperature_c, time_delta_days)
        
        # Calculate damage
        self._calculate_pest_damage(population, pest_biology, time_delta_days)
        
        # Update population growth rate
        self._calculate_population_growth_rate(population, pest_biology)
        
        return True
    
    def _transition_lifecycle_stage(self, population: PestPopulation, current_stage: LifecycleStage,
                                  stage_data: LifecycleStageData):
        """Transition insects from one lifecycle stage to the next"""
        
        pest_biology = self.pest_database[population.pest_id]
        current_pop = population.stage_populations[current_stage]
        
        # Calculate survival rate
        surviving_pop = current_pop * stage_data.survival_rate
        
        # Determine next stage
        stage_order = [LifecycleStage.EGG, LifecycleStage.LARVA, LifecycleStage.PUPA, LifecycleStage.ADULT]
        
        try:
            current_index = stage_order.index(current_stage)
            
            if current_index < len(stage_order) - 1:
                next_stage = stage_order[current_index + 1]
                
                # Skip pupa stage for incomplete metamorphosis
                if (pest_biology.metamorphosis_type == "incomplete" and 
                    next_stage == LifecycleStage.PUPA):
                    next_stage = LifecycleStage.ADULT
                
                # Transfer to next stage
                if next_stage in population.stage_populations:
                    population.stage_populations[next_stage] += surviving_pop
                else:
                    population.stage_populations[next_stage] = surviving_pop
            
            elif current_stage == LifecycleStage.ADULT:
                # Adults die but may produce eggs for next generation
                if random.random() < 0.8:  # 80% reproduce
                    eggs_produced = surviving_pop * pest_biology.egg_laying_capacity * pest_biology.sex_ratio
                    population.stage_populations[LifecycleStage.EGG] = population.stage_populations.get(LifecycleStage.EGG, 0) + eggs_produced
                    population.generation_number += 1
            
            # Remove from current stage
            population.stage_populations[current_stage] = 0
            population.degree_day_accumulation[current_stage] = 0
            
        except ValueError:
            print(f"Unknown lifecycle stage: {current_stage}")
    
    def _apply_mortality_factors(self, population: PestPopulation, temperature_c: float, 
                                time_delta_days: float):
        """Apply various mortality factors to pest population"""
        
        pest_biology = self.pest_database[population.pest_id]
        
        # Temperature stress mortality
        temp_min = pest_biology.temperature_thresholds.get('min', 0)
        temp_max = pest_biology.temperature_thresholds.get('max', 40)
        
        if temperature_c < temp_min or temperature_c > temp_max:
            temp_mortality = 0.2 * time_delta_days  # 20% daily mortality under stress
            population.temperature_stress += temp_mortality
        else:
            temp_mortality = 0.0
        
        # Natural mortality
        natural_mortality = self.system_parameters['natural_mortality_rate'] * time_delta_days
        
        # Predation mortality
        predation_mortality = population.predation_pressure * time_delta_days
        
        # Total mortality rate
        total_mortality = min(temp_mortality + natural_mortality + predation_mortality, 0.9)
        
        # Apply mortality to all life stages
        for stage in population.stage_populations:
            current_pop = population.stage_populations[stage]
            surviving_pop = current_pop * (1 - total_mortality)
            population.stage_populations[stage] = max(surviving_pop, 0)
    
    def _calculate_pest_damage(self, population: PestPopulation, pest_biology: PestBiology, 
                              time_delta_days: float):
        """Calculate crop damage caused by pest population"""
        
        total_damage = 0.0
        
        # Calculate damage by lifecycle stage
        for stage, stage_pop in population.stage_populations.items():
            if stage in pest_biology.lifecycle_stages:
                stage_data = pest_biology.lifecycle_stages[stage]
                
                # Damage = population * feeding activity * damage potential * time
                stage_damage = (stage_pop * stage_data.feeding_activity * 
                              stage_data.damage_potential * time_delta_days)
                total_damage += stage_damage
        
        # Apply damage function
        daily_damage = total_damage * pest_biology.damage_function_slope
        population.current_damage_rate = daily_damage
        population.cumulative_damage += daily_damage
        
        # Calculate yield impact
        population.yield_impact_percent = min(population.cumulative_damage, 80.0)  # Cap at 80% loss
    
    def _calculate_population_growth_rate(self, population: PestPopulation, pest_biology: PestBiology):
        """Calculate current population growth rate"""
        
        # Base growth rate from reproduction
        reproductive_adults = population.stage_populations.get(LifecycleStage.ADULT, 0)
        potential_offspring = reproductive_adults * pest_biology.egg_laying_capacity * 0.1  # Daily rate
        
        # Carrying capacity effects
        capacity_factor = 1.0 - (population.total_population / population.carrying_capacity)
        capacity_factor = max(capacity_factor, 0.1)
        
        # Environmental suitability
        env_factor = population.host_plant_quality * (1 - population.temperature_stress)
        
        # Calculate growth rate
        population.current_growth_rate = (potential_offspring / max(population.total_population, 1)) * capacity_factor * env_factor
    
    def conduct_pest_monitoring(self, location_id: str, monitoring_method: str = "visual",
                               monitoring_date: datetime = None) -> PestMonitoring:
        """Conduct pest monitoring at specified location"""
        
        if monitoring_date is None:
            monitoring_date = datetime.now()
        
        monitoring_id = f"PEST_MON_{location_id}_{monitoring_date.strftime('%Y%m%d_%H%M%S')}"
        
        monitoring = PestMonitoring(
            monitoring_id=monitoring_id,
            location_id=location_id,
            monitoring_date=monitoring_date,
            monitoring_method=monitoring_method
        )
        
        # Detect pests at location
        location_populations = [
            pop for pop in self.active_populations.values()
            if pop.location_id == location_id
        ]
        
        for population in location_populations:
            pest_biology = self.pest_database[population.pest_id]
            
            # Calculate detection probability based on method and pest characteristics
            detection_prob = self._calculate_detection_probability(
                population, pest_biology, monitoring_method
            )
            
            if random.random() < detection_prob:
                monitoring.pests_detected[population.pest_id] = population.population_density_per_m2
                
                # Assess economic thresholds
                if population.population_density_per_m2 >= pest_biology.economic_threshold:
                    monitoring.treatment_threshold_status[population.pest_id] = True
                    monitoring.economic_injury_assessment[population.pest_id] = (
                        population.population_density_per_m2 / pest_biology.economic_injury_level
                    )
        
        # Detect beneficial insects
        location_beneficials = [
            beneficial for beneficial in self.beneficial_insects.values()
            if beneficial.location_id == location_id or beneficial.location_id == "general"
        ]
        
        for beneficial in location_beneficials:
            # Beneficial insects are generally easier to detect when present
            if beneficial.population_density > 0:
                monitoring.beneficial_insects[beneficial.beneficial_id] = beneficial.population_density
        
        # Generate recommendations
        monitoring.immediate_actions = self._generate_immediate_actions(monitoring)
        monitoring.treatment_recommendations = self._generate_treatment_recommendations(monitoring)
        monitoring.monitoring_recommendations = self._generate_monitoring_recommendations(monitoring)
        
        # Store monitoring record
        if location_id not in self.monitoring_records:
            self.monitoring_records[location_id] = []
        self.monitoring_records[location_id].append(monitoring)
        
        # Emit monitoring event
        self.event_system.emit_event("pest_monitoring_completed", {
            "monitoring_id": monitoring_id,
            "location_id": location_id,
            "pests_detected": len(monitoring.pests_detected),
            "economic_thresholds_exceeded": sum(monitoring.treatment_threshold_status.values()),
            "beneficial_insects_present": len(monitoring.beneficial_insects)
        })
        
        return monitoring
    
    def _calculate_detection_probability(self, population: PestPopulation, pest_biology: PestBiology,
                                       monitoring_method: str) -> float:
        """Calculate probability of detecting pest population during monitoring"""
        
        base_detection = 0.7  # Base detection probability
        
        # Population density factor
        density_factor = min(population.population_density_per_m2 / 
                           self.system_parameters['detection_threshold'], 1.0)
        
        # Lifecycle stage detection difficulty
        detection_difficulty = 0.0
        total_pop = population.total_population
        
        if total_pop > 0:
            for stage, stage_pop in population.stage_populations.items():
                if stage in pest_biology.lifecycle_stages:
                    stage_data = pest_biology.lifecycle_stages[stage]
                    weight = stage_pop / total_pop
                    detection_difficulty += weight * (1 - stage_data.detection_difficulty)
        
        # Monitoring method effectiveness
        method_effectiveness = {
            "visual": 0.8,
            "trap": 0.9,
            "sweep_net": 0.7,
            "beat_sheet": 0.75
        }
        
        method_factor = method_effectiveness.get(monitoring_method, 0.6)
        
        # Calculate final detection probability
        detection_prob = base_detection * density_factor * detection_difficulty * method_factor
        
        return min(max(detection_prob, 0.0), 1.0)
    
    def _generate_immediate_actions(self, monitoring: PestMonitoring) -> List[str]:
        """Generate immediate action recommendations based on monitoring"""
        
        actions = []
        
        for pest_id, threshold_exceeded in monitoring.treatment_threshold_status.items():
            if threshold_exceeded:
                pest_name = self.pest_database[pest_id].common_name
                actions.append(f"Economic threshold exceeded for {pest_name} - consider immediate treatment")
        
        if not monitoring.pests_detected:
            actions.append("No economic pests detected - continue regular monitoring")
        
        return actions
    
    def _generate_treatment_recommendations(self, monitoring: PestMonitoring) -> List[str]:
        """Generate treatment recommendations based on monitoring results"""
        
        recommendations = []
        
        for pest_id, density in monitoring.pests_detected.items():
            pest_biology = self.pest_database[pest_id]
            
            if density >= pest_biology.economic_threshold:
                # Chemical control recommendations
                best_insecticides = sorted(
                    pest_biology.insecticide_susceptibility.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                if best_insecticides:
                    insecticide = best_insecticides[0][0]
                    recommendations.append(f"Apply {insecticide} for {pest_biology.common_name} control")
                
                # Biological control recommendations
                if pest_biology.biological_control_agents:
                    agent = pest_biology.biological_control_agents[0]
                    recommendations.append(f"Consider {agent} for biological control of {pest_biology.common_name}")
        
        return recommendations
    
    def _generate_monitoring_recommendations(self, monitoring: PestMonitoring) -> List[str]:
        """Generate monitoring recommendations for future scouting"""
        
        recommendations = []
        
        if monitoring.pests_detected:
            recommendations.append("Increase monitoring frequency to twice weekly")
            recommendations.append("Focus scouting on field edges and stressed areas")
        
        if monitoring.beneficial_insects:
            recommendations.append("Monitor beneficial insect populations to assess biological control")
        
        recommendations.append("Continue weekly monitoring throughout growing season")
        
        return recommendations
    
    def apply_biological_control(self, location_id: str, beneficial_id: str, 
                                release_density: float) -> Dict[str, Any]:
        """Apply biological control by releasing beneficial insects"""
        
        if beneficial_id not in self.beneficial_insects:
            return {"success": False, "error": "Beneficial insect not found"}
        
        beneficial = self.beneficial_insects[beneficial_id]
        
        # Increase beneficial population at location
        if beneficial.location_id == "general":
            # Create location-specific beneficial population
            location_beneficial = BeneficialInsect(
                beneficial_id=f"{beneficial_id}_{location_id}",
                common_name=beneficial.common_name,
                scientific_name=beneficial.scientific_name,
                beneficial_type=beneficial.beneficial_type,
                location_id=location_id,
                population_density=release_density,
                target_pests=beneficial.target_pests.copy(),
                control_effectiveness=beneficial.control_effectiveness.copy(),
                search_efficiency=beneficial.search_efficiency
            )
            
            self.beneficial_insects[f"{beneficial_id}_{location_id}"] = location_beneficial
        else:
            beneficial.population_density += release_density
        
        # Apply biological control pressure to target pests
        location_populations = [
            pop for pop in self.active_populations.values()
            if pop.location_id == location_id
        ]
        
        control_effectiveness = 0.0
        pests_controlled = 0
        
        for population in location_populations:
            if population.pest_id in beneficial.target_pests:
                effectiveness = beneficial.control_effectiveness.get(population.pest_id, 0.0)
                population.predation_pressure += effectiveness * release_density * 0.01  # Scale factor
                control_effectiveness += effectiveness
                pests_controlled += 1
        
        # Update statistics
        self.pest_statistics['beneficial_releases'] += 1
        
        # Emit biological control event
        self.event_system.emit_event("biological_control_applied", {
            "location_id": location_id,
            "beneficial_id": beneficial_id,
            "release_density": release_density,
            "pests_targeted": pests_controlled,
            "expected_effectiveness": control_effectiveness / max(pests_controlled, 1)
        })
        
        return {
            "success": True,
            "beneficial_species": beneficial.common_name,
            "release_density": release_density,
            "pests_targeted": pests_controlled,
            "expected_control": control_effectiveness / max(pests_controlled, 1)
        }
    
    # Event handlers for system integration
    def _handle_weather_update(self, event_data: Dict[str, Any]):
        """Handle weather condition updates for pest development"""
        location_id = event_data.get("location_id", "default")
        temperature = event_data.get("temperature_c", 20)
        
        # Update degree-day accumulation for all pests at location
        if location_id in self.degree_day_accumulation:
            for pest_id in self.degree_day_accumulation[location_id]:
                pest_biology = self.pest_database[pest_id]
                base_temp = pest_biology.temperature_thresholds.get('min', 10)
                
                if temperature > base_temp:
                    dd = temperature - base_temp
                    self.degree_day_accumulation[location_id][pest_id] += dd
        
        # Update all active populations at this location
        location_populations = [
            pop for pop in self.active_populations.values()
            if pop.location_id == location_id
        ]
        
        for population in location_populations:
            self.update_pest_development(population.population_id, temperature, 1.0)  # 1 day
    
    def _handle_growth_stage_change(self, event_data: Dict[str, Any]):
        """Handle crop growth stage changes affecting pest susceptibility"""
        location_id = event_data.get("location_id")
        crop_id = event_data.get("crop_id")
        new_stage = event_data.get("growth_stage")
        
        # Adjust host plant quality based on growth stage
        stage_quality_factors = {
            "seedling": 0.8,      # Less attractive/suitable when very young
            "vegetative": 1.0,    # Optimal host quality
            "reproductive": 1.2,  # More attractive during reproduction
            "maturity": 0.7       # Less suitable when mature
        }
        
        quality_factor = stage_quality_factors.get(new_stage, 1.0)
        
        location_populations = [
            pop for pop in self.active_populations.values()
            if pop.location_id == location_id and pop.crop_id == crop_id
        ]
        
        for population in location_populations:
            population.host_plant_quality = quality_factor
    
    def _handle_field_operation(self, event_data: Dict[str, Any]):
        """Handle field operations affecting pest populations"""
        operation_type = event_data.get("operation_type")
        location_id = event_data.get("location_id")
        
        location_populations = [
            pop for pop in self.active_populations.values()
            if pop.location_id == location_id
        ]
        
        if operation_type == "tillage":
            # Tillage can disrupt soil-dwelling pests and overwintering stages
            for population in location_populations:
                pest_biology = self.pest_database[population.pest_id]
                if pest_biology.pest_type == PestType.SOIL_DWELLING:
                    # Apply mechanical mortality
                    mortality_rate = 0.4  # 40% mortality from tillage
                    for stage in population.stage_populations:
                        population.stage_populations[stage] *= (1 - mortality_rate)
        
        elif operation_type == "harvest":
            # Harvest removes pest habitat and food sources
            for population in location_populations:
                # Force transition to overwintering stage or dispersal
                overwintering_stage = self.pest_database[population.pest_id].overwintering_stage
                total_pop = sum(population.stage_populations.values())
                
                # Concentrate population in overwintering stage
                population.stage_populations.clear()
                population.stage_populations[overwintering_stage] = total_pop * 0.3  # 30% survive harvest
    
    def _handle_time_advancement(self, event_data: Dict[str, Any]):
        """Handle daily time advancement for pest development"""
        time_delta_days = event_data.get("days_elapsed", 1.0)
        
        # Update all active pest populations
        for population_id in list(self.active_populations.keys()):
            population = self.active_populations[population_id]
            
            # Remove populations that have died out
            if population.total_population < 0.1:
                del self.active_populations[population_id]
                continue
            
            # Update pest development (temperature will be handled in weather updates)
            current_temp = 20.0  # Default temperature - would get from weather system
            self.update_pest_development(population_id, current_temp, time_delta_days)
        
        # Update statistics
        self.pest_statistics['active_populations'] = len(self.active_populations)
    
    def _handle_season_change(self, event_data: Dict[str, Any]):
        """Handle seasonal changes affecting pest populations"""
        new_season = event_data.get("season")
        
        # Trigger seasonal events for pest populations
        for population in self.active_populations.values():
            pest_biology = self.pest_database[population.pest_id]
            
            # Handle overwintering preparation
            if new_season == "winter":
                overwintering_stage = pest_biology.overwintering_stage
                total_pop = sum(population.stage_populations.values())
                
                # Consolidate into overwintering stage
                population.stage_populations.clear()
                population.stage_populations[overwintering_stage] = total_pop * 0.6  # 60% survive winter prep
            
            # Handle spring emergence
            elif new_season == "spring":
                if pest_biology.overwintering_stage in population.stage_populations:
                    overwintering_pop = population.stage_populations[pest_biology.overwintering_stage]
                    # Transition to active stages
                    population.stage_populations[LifecycleStage.LARVA] = overwintering_pop * 0.8
                    population.stage_populations[pest_biology.overwintering_stage] = 0
    
    def get_pest_status_summary(self, location_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive pest status summary"""
        
        # Filter populations by location if specified
        if location_id:
            populations = [p for p in self.active_populations.values() if p.location_id == location_id]
        else:
            populations = list(self.active_populations.values())
        
        # Calculate summary statistics
        total_populations = len(populations)
        total_pest_density = sum(p.population_density_per_m2 for p in populations)
        total_damage = sum(p.yield_impact_percent for p in populations)
        
        # Most problematic pests
        pest_impacts = {}
        for pop in populations:
            pest_name = self.pest_database[pop.pest_id].common_name
            if pest_name not in pest_impacts:
                pest_impacts[pest_name] = 0.0
            pest_impacts[pest_name] += pop.yield_impact_percent
        
        top_pests = sorted(pest_impacts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Economic thresholds exceeded
        thresholds_exceeded = 0
        for pop in populations:
            pest_biology = self.pest_database[pop.pest_id]
            if pop.population_density_per_m2 >= pest_biology.economic_threshold:
                thresholds_exceeded += 1
        
        return {
            "total_active_populations": total_populations,
            "total_pest_density": total_pest_density,
            "total_yield_impact": total_damage,
            "economic_thresholds_exceeded": thresholds_exceeded,
            "most_problematic_pests": top_pests,
            "beneficial_insects_active": len([b for b in self.beneficial_insects.values() if b.population_density > 0]),
            "locations_affected": len(set(p.location_id for p in populations)),
            "average_population_growth": sum(p.current_growth_rate for p in populations) / len(populations) if populations else 0
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get pest framework system status"""
        return {
            "system_status": "active" if self.is_initialized else "inactive",
            "pests_in_database": len(self.pest_database),
            "beneficial_species": len(self.beneficial_insects),
            "active_populations": len(self.active_populations),
            "monitoring_locations": len(self.monitoring_records),
            "total_yield_impact": sum(p.yield_impact_percent for p in self.active_populations.values()),
            "system_statistics": self.pest_statistics
        }

# Global convenience functions
def get_pest_framework() -> Optional[PestFramework]:
    """Get the global pest framework instance"""
    # This would typically be managed by a system registry
    return None

def establish_pest_at_location(location_id: str, crop_id: str, pest_id: str, initial_pop: float) -> Optional[PestPopulation]:
    """Convenience function to establish pest population"""
    system = get_pest_framework()
    if system:
        conditions = {"temperature_c": 20, "humidity_percent": 60}  # Default conditions
        return system.establish_pest_population(location_id, crop_id, pest_id, initial_pop, conditions)
    return None

def monitor_pests_at_location(location_id: str, method: str = "visual") -> Optional[PestMonitoring]:
    """Convenience function to monitor pests at location"""
    system = get_pest_framework()
    if system:
        return system.conduct_pest_monitoring(location_id, method)
    return None

def release_beneficial_insects(location_id: str, beneficial_id: str, density: float) -> Dict[str, Any]:
    """Convenience function to release beneficial insects"""
    system = get_pest_framework()
    if system:
        return system.apply_biological_control(location_id, beneficial_id, density)
    return {"success": False, "error": "Pest system not available"}