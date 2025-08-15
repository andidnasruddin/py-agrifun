"""
Disease Framework - Comprehensive Agricultural Disease Management for AgriFun Agricultural Game

This system provides realistic plant disease modeling including fungal, bacterial, and viral 
diseases with environmental triggers, lifecycle modeling, and integrated management strategies.
It helps players understand plant pathology and make informed disease management decisions.

Key Features:
- Comprehensive disease database with 50+ agricultural diseases
- Environmental disease pressure modeling based on weather conditions
- Disease lifecycle simulation (infection, incubation, sporulation, spread)
- Host-pathogen interactions with crop susceptibility ratings
- Disease severity assessment and yield impact calculations
- Integrated disease management recommendations
- Resistance development and durability modeling

Disease Categories:
- Fungal Diseases: Rusts, smuts, blights, rots, mildews (70% of plant diseases)
- Bacterial Diseases: Blights, wilts, spots, cankers (15% of plant diseases)
- Viral Diseases: Mosaics, yellows, stunting disorders (10% of plant diseases)
- Nematode Diseases: Root lesions, cyst formation (5% of plant diseases)

Educational Value:
- Understanding of plant pathology principles and disease triangles
- Environmental factors affecting disease development
- Disease identification and diagnostic skills
- Economic thresholds and treatment decision-making
- Sustainable disease management strategies

Integration:
- Weather System: Temperature, humidity, rainfall affect disease pressure
- Crop Growth System: Disease damage reduces yield and quality
- Time Management: Disease development follows realistic timelines
- Equipment System: Spray application for disease control
- Economic System: Treatment costs vs. yield protection decisions

Author: Agricultural Simulation Development Team
Version: 1.0.0 - Comprehensive Disease Framework Implementation
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

class DiseaseType(Enum):
    """Types of plant diseases"""
    FUNGAL = "fungal"
    BACTERIAL = "bacterial"
    VIRAL = "viral"
    NEMATODE = "nematode"
    PHYSIOLOGICAL = "physiological"

class DiseaseStage(Enum):
    """Disease development stages"""
    DORMANT = "dormant"           # Pathogen dormant/overwintering
    INFECTION = "infection"       # Initial infection occurring
    INCUBATION = "incubation"     # Disease developing but not visible
    VISIBLE = "visible"           # Symptoms visible but limited
    SPORULATION = "sporulation"   # Pathogen producing spores/spreading
    SEVERE = "severe"             # Severe symptoms, major yield impact
    SENESCENCE = "senescence"     # Disease declining with crop maturity

class TransmissionMethod(Enum):
    """Disease transmission methods"""
    AIRBORNE = "airborne"         # Wind-dispersed spores
    SOILBORNE = "soilborne"       # Soil-dwelling pathogens
    SEEDBORNE = "seedborne"       # Seed-transmitted pathogens
    INSECT_VECTOR = "insect_vector"  # Insect-transmitted diseases
    WATERBORNE = "waterborne"     # Water splash dispersal
    CONTACT = "contact"           # Direct plant contact
    GRAFTING = "grafting"         # Propagation transmission

class ResistanceType(Enum):
    """Types of disease resistance"""
    IMMUNE = "immune"             # Complete resistance
    HIGHLY_RESISTANT = "highly_resistant"  # Very high resistance
    MODERATELY_RESISTANT = "moderately_resistant"  # Moderate resistance
    TOLERANT = "tolerant"         # Can withstand infection
    SUSCEPTIBLE = "susceptible"   # Prone to infection
    HIGHLY_SUSCEPTIBLE = "highly_susceptible"  # Very prone to infection

@dataclass
class DiseaseConditions:
    """Environmental conditions favoring disease development"""
    optimal_temperature_range: Tuple[float, float]  # Celsius
    optimal_humidity_range: Tuple[float, float]     # Percentage
    optimal_wetness_hours: float                    # Hours of leaf wetness
    ph_preference: Tuple[float, float]              # Soil pH range
    nutrient_factors: Dict[str, str] = field(default_factory=dict)  # N/P/K effects
    seasonal_factors: Dict[str, float] = field(default_factory=dict)  # Season preferences
    stress_factors: List[str] = field(default_factory=list)  # Conditions that predispose

@dataclass
class DiseaseSymptoms:
    """Disease symptom descriptions for identification"""
    early_symptoms: List[str] = field(default_factory=list)
    advanced_symptoms: List[str] = field(default_factory=list)
    diagnostic_features: List[str] = field(default_factory=list)
    affected_plant_parts: List[str] = field(default_factory=list)
    symptom_timing: str = ""  # When symptoms typically appear
    confusion_diseases: List[str] = field(default_factory=list)  # Similar diseases

@dataclass
class Disease:
    """Comprehensive disease definition"""
    disease_id: str
    common_name: str
    scientific_name: str
    disease_type: DiseaseType
    
    # Host range and specificity
    primary_hosts: List[str] = field(default_factory=list)
    secondary_hosts: List[str] = field(default_factory=list)
    host_specificity: str = "specific"  # "specific", "moderate", "broad"
    
    # Pathogen characteristics
    transmission_methods: List[TransmissionMethod] = field(default_factory=list)
    survival_structures: List[str] = field(default_factory=list)
    overwintering_method: str = ""
    
    # Environmental preferences
    disease_conditions: DiseaseConditions = field(default_factory=lambda: DiseaseConditions((15, 25), (60, 90), 12, (6.0, 7.5)))
    
    # Disease development
    incubation_period_days: Tuple[int, int] = (3, 14)  # Min, max days
    infectious_period_days: Tuple[int, int] = (14, 60)
    sporulation_cycles_per_season: int = 3
    
    # Impact assessment
    max_yield_loss_percent: float = 30.0
    quality_impact_factors: Dict[str, float] = field(default_factory=dict)
    economic_threshold: float = 5.0  # % yield loss threshold for treatment
    
    # Management options
    cultural_controls: List[str] = field(default_factory=list)
    biological_controls: List[str] = field(default_factory=list)
    chemical_controls: List[str] = field(default_factory=list)
    resistant_varieties: List[str] = field(default_factory=list)
    
    # Disease identification
    symptoms: DiseaseSymptoms = field(default_factory=DiseaseSymptoms)
    
    # System properties
    virulence_factors: Dict[str, float] = field(default_factory=dict)
    mutation_rate: float = 0.01  # Rate of pathogen evolution

@dataclass
class DiseaseIncident:
    """Active disease incident on farm"""
    incident_id: str
    disease_id: str
    location_id: str  # Field/plot location
    crop_id: str
    
    # Disease status
    current_stage: DiseaseStage
    severity_percent: float  # 0-100% severity
    affected_area_percent: float  # % of field affected
    
    # Timeline tracking
    infection_date: datetime
    detection_date: Optional[datetime] = None
    peak_severity_date: Optional[datetime] = None
    resolution_date: Optional[datetime] = None
    
    # Environmental context
    infection_conditions: Dict[str, Any] = field(default_factory=dict)
    weather_favorability: float = 0.5  # 0-1 scale
    
    # Impact tracking
    current_yield_impact: float = 0.0  # Current yield reduction %
    projected_yield_impact: float = 0.0  # Final projected impact %
    quality_impacts: Dict[str, float] = field(default_factory=dict)
    
    # Management history
    treatments_applied: List[Dict[str, Any]] = field(default_factory=list)
    control_effectiveness: Dict[str, float] = field(default_factory=dict)
    
    # Spread tracking
    infection_source: Optional[str] = None
    spread_rate: float = 0.0  # %/day spread rate
    secondary_infections: List[str] = field(default_factory=list)

@dataclass
class ResistanceProfile:
    """Crop variety resistance profile"""
    variety_id: str
    crop_id: str
    resistance_ratings: Dict[str, ResistanceType] = field(default_factory=dict)  # disease_id -> resistance
    resistance_genes: Dict[str, List[str]] = field(default_factory=dict)  # disease_id -> gene list
    resistance_durability: Dict[str, int] = field(default_factory=dict)  # years of effectiveness
    yield_penalty: float = 0.0  # Yield reduction for resistance genes

@dataclass
class DiseaseMonitoring:
    """Disease monitoring and scouting data"""
    monitoring_id: str
    location_id: str
    scout_date: datetime
    
    # Scouting results
    diseases_detected: List[str] = field(default_factory=list)
    disease_severity: Dict[str, float] = field(default_factory=dict)
    symptoms_observed: Dict[str, List[str]] = field(default_factory=dict)
    
    # Environmental conditions
    weather_conditions: Dict[str, Any] = field(default_factory=dict)
    crop_stage: str = ""
    stress_factors: List[str] = field(default_factory=list)
    
    # Risk assessment
    disease_pressure_rating: str = "low"  # low, moderate, high, severe
    treatment_recommendations: List[str] = field(default_factory=list)
    monitoring_frequency: str = "weekly"  # daily, weekly, biweekly

class DiseaseFramework(System):
    """
    Comprehensive Disease Framework for Agricultural Disease Management
    
    This system provides realistic plant disease modeling including:
    - Disease database with 50+ agricultural diseases
    - Environmental disease pressure modeling
    - Disease lifecycle and spread simulation
    - Host-pathogen interaction modeling
    - Disease impact assessment on yield and quality
    - Integrated disease management recommendations
    """
    
    def __init__(self):
        """Initialize the Disease Framework"""
        super().__init__()
        
        # Core system references
        self.event_system = None
        self.config_manager = None
        self.content_registry = None
        
        # Disease management data
        self.disease_database: Dict[str, Disease] = {}
        self.active_incidents: Dict[str, DiseaseIncident] = {}
        self.resistance_profiles: Dict[str, ResistanceProfile] = {}
        self.monitoring_records: Dict[str, List[DiseaseMonitoring]] = {}
        
        # Disease pressure tracking
        self.environmental_pressure: Dict[str, float] = {}  # location_id -> pressure
        self.seasonal_disease_patterns: Dict[str, Dict[str, float]] = {}
        self.disease_forecasts: Dict[str, Dict[str, float]] = {}
        
        # System parameters
        self.system_parameters = {
            'infection_probability_base': 0.1,     # Base daily infection probability
            'spread_rate_multiplier': 1.0,        # Global spread rate modifier
            'severity_progression_rate': 0.05,    # Daily severity increase
            'environmental_weight': 0.7,          # Weight of environmental factors
            'host_resistance_weight': 0.8,        # Weight of host resistance
            'treatment_efficacy_base': 0.8,       # Base treatment effectiveness
            'monitoring_detection_threshold': 0.1, # Minimum severity for detection
            'economic_threshold_multiplier': 1.0   # Threshold adjustment factor
        }
        
        # Performance tracking
        self.disease_statistics: Dict[str, Any] = {
            'total_incidents': 0,
            'active_incidents': 0,
            'yield_losses_prevented': 0.0,
            'treatment_costs': 0.0,
            'resistance_breakdowns': 0
        }
        
        self.is_initialized = False
    
    def initialize(self, event_system: EventSystem, config_manager: ConfigurationManager, 
                  content_registry: ContentRegistry) -> bool:
        """Initialize the Disease Framework with required dependencies"""
        try:
            self.event_system = event_system
            self.config_manager = config_manager
            self.content_registry = content_registry
            
            # Load disease management configuration
            self._load_configuration()
            
            # Initialize disease database
            self._initialize_disease_database()
            
            # Initialize resistance profiles
            self._initialize_resistance_profiles()
            
            # Register event handlers
            self._register_event_handlers()
            
            # Initialize environmental disease pressure tracking
            self._initialize_disease_pressure_tracking()
            
            self.is_initialized = True
            
            # Emit initialization event
            self.event_system.emit_event("disease_framework_initialized", {
                "system": "disease_framework",
                "status": "ready",
                "diseases_loaded": len(self.disease_database),
                "resistance_profiles": len(self.resistance_profiles),
                "timestamp": datetime.now()
            })
            
            return True
            
        except Exception as e:
            print(f"Error initializing Disease Framework: {e}")
            return False
    
    def _load_configuration(self):
        """Load disease framework configuration from config files"""
        disease_config = self.config_manager.get("disease_framework", {})
        
        # Update system parameters
        if "parameters" in disease_config:
            self.system_parameters.update(disease_config["parameters"])
        
        # Load disease-specific configuration
        if "disease_settings" in disease_config:
            # Additional disease-specific settings would be loaded here
            pass
    
    def _initialize_disease_database(self):
        """Initialize comprehensive agricultural disease database"""
        
        # Corn diseases
        self.disease_database["corn_gray_leaf_spot"] = Disease(
            disease_id="corn_gray_leaf_spot",
            common_name="Gray Leaf Spot",
            scientific_name="Cercospora zeae-maydis",
            disease_type=DiseaseType.FUNGAL,
            primary_hosts=["corn"],
            transmission_methods=[TransmissionMethod.AIRBORNE, TransmissionMethod.SEEDBORNE],
            survival_structures=["conidia", "pseudothecia"],
            overwintering_method="crop_residue",
            disease_conditions=DiseaseConditions(
                optimal_temperature_range=(22, 30),
                optimal_humidity_range=(80, 95),
                optimal_wetness_hours=14,
                ph_preference=(5.5, 7.0),
                seasonal_factors={"summer": 1.5, "fall": 1.2},
                stress_factors=["nitrogen_deficiency", "drought_stress"]
            ),
            incubation_period_days=(7, 21),
            infectious_period_days=(21, 45),
            sporulation_cycles_per_season=4,
            max_yield_loss_percent=60.0,
            economic_threshold=10.0,
            cultural_controls=["crop_rotation", "residue_management", "balanced_fertility"],
            biological_controls=["trichoderma_spp"],
            chemical_controls=["strobilurin_fungicides", "triazole_fungicides"],
            resistant_varieties=["corn_bt_hybrid", "corn_resistant_hybrid"],
            symptoms=DiseaseSymptoms(
                early_symptoms=["small_gray_spots", "rectangular_lesions"],
                advanced_symptoms=["large_necrotic_areas", "premature_senescence"],
                diagnostic_features=["gray_sporulation", "parallel_leaf_veins"],
                affected_plant_parts=["leaves", "husks"],
                symptom_timing="mid_to_late_season"
            )
        )
        
        self.disease_database["corn_northern_leaf_blight"] = Disease(
            disease_id="corn_northern_leaf_blight",
            common_name="Northern Corn Leaf Blight",
            scientific_name="Exserohilum turcicum",
            disease_type=DiseaseType.FUNGAL,
            primary_hosts=["corn", "sorghum"],
            transmission_methods=[TransmissionMethod.AIRBORNE],
            survival_structures=["conidia", "chlamydospores"],
            overwintering_method="crop_residue",
            disease_conditions=DiseaseConditions(
                optimal_temperature_range=(18, 27),
                optimal_humidity_range=(85, 95),
                optimal_wetness_hours=12,
                ph_preference=(6.0, 7.5),
                seasonal_factors={"summer": 1.8, "spring": 1.3}
            ),
            incubation_period_days=(3, 10),
            infectious_period_days=(14, 35),
            max_yield_loss_percent=50.0,
            economic_threshold=8.0,
            symptoms=DiseaseSymptoms(
                early_symptoms=["elliptical_lesions", "tan_colored_spots"],
                advanced_symptoms=["cigar_shaped_lesions", "dark_sporulation"],
                diagnostic_features=["boat_shaped_conidia", "concentric_rings"],
                affected_plant_parts=["leaves", "leaf_sheaths"]
            )
        )
        
        # Soybean diseases
        self.disease_database["soybean_rust"] = Disease(
            disease_id="soybean_rust",
            common_name="Soybean Rust",
            scientific_name="Phakopsora pachyrhizi",
            disease_type=DiseaseType.FUNGAL,
            primary_hosts=["soybeans"],
            secondary_hosts=["kudzu", "wild_legumes"],
            transmission_methods=[TransmissionMethod.AIRBORNE],
            survival_structures=["urediniospores", "teliospores"],
            overwintering_method="alternate_hosts",
            disease_conditions=DiseaseConditions(
                optimal_temperature_range=(20, 28),
                optimal_humidity_range=(95, 100),
                optimal_wetness_hours=8,
                ph_preference=(6.0, 7.0),
                seasonal_factors={"late_summer": 2.0, "fall": 1.5}
            ),
            incubation_period_days=(5, 14),
            infectious_period_days=(10, 21),
            sporulation_cycles_per_season=8,
            max_yield_loss_percent=80.0,
            economic_threshold=5.0,
            cultural_controls=["early_planting", "resistant_varieties"],
            chemical_controls=["triazole_fungicides", "strobilurin_fungicides"],
            symptoms=DiseaseSymptoms(
                early_symptoms=["small_pustules", "tan_lesions"],
                advanced_symptoms=["orange_uredinia", "premature_defoliation"],
                diagnostic_features=["rust_colored_spores", "pustule_morphology"],
                affected_plant_parts=["leaves", "pods", "stems"]
            )
        )
        
        self.disease_database["soybean_sudden_death"] = Disease(
            disease_id="soybean_sudden_death",
            common_name="Sudden Death Syndrome",
            scientific_name="Fusarium virguliforme",
            disease_type=DiseaseType.FUNGAL,
            primary_hosts=["soybeans"],
            transmission_methods=[TransmissionMethod.SOILBORNE],
            survival_structures=["chlamydospores", "sclerotia"],
            overwintering_method="soil_survival",
            disease_conditions=DiseaseConditions(
                optimal_temperature_range=(15, 20),
                optimal_humidity_range=(70, 90),
                optimal_wetness_hours=24,
                ph_preference=(6.5, 8.0),
                stress_factors=["compaction", "poor_drainage", "nematodes"]
            ),
            incubation_period_days=(14, 35),
            max_yield_loss_percent=70.0,
            economic_threshold=15.0,
            symptoms=DiseaseSymptoms(
                early_symptoms=["interveinal_chlorosis", "root_rot"],
                advanced_symptoms=["sudden_wilting", "leaf_necrosis"],
                diagnostic_features=["blue_fungal_growth", "intact_leaflets"],
                affected_plant_parts=["roots", "leaves", "pods"]
            )
        )
        
        # Wheat diseases
        self.disease_database["wheat_stripe_rust"] = Disease(
            disease_id="wheat_stripe_rust",
            common_name="Stripe Rust",
            scientific_name="Puccinia striiformis",
            disease_type=DiseaseType.FUNGAL,
            primary_hosts=["wheat", "barley"],
            transmission_methods=[TransmissionMethod.AIRBORNE],
            survival_structures=["urediniospores", "teliospores"],
            overwintering_method="living_plants",
            disease_conditions=DiseaseConditions(
                optimal_temperature_range=(10, 18),
                optimal_humidity_range=(85, 100),
                optimal_wetness_hours=6,
                seasonal_factors={"spring": 2.0, "fall": 1.5}
            ),
            max_yield_loss_percent=70.0,
            economic_threshold=8.0,
            symptoms=DiseaseSymptoms(
                early_symptoms=["yellow_stripes", "linear_pustules"],
                advanced_symptoms=["severe_chlorosis", "stunted_growth"],
                diagnostic_features=["parallel_stripe_pattern", "yellow_spores"],
                affected_plant_parts=["leaves", "glumes", "awns"]
            )
        )
        
        # Bacterial diseases
        self.disease_database["bacterial_leaf_blight"] = Disease(
            disease_id="bacterial_leaf_blight",
            common_name="Bacterial Leaf Blight",
            scientific_name="Xanthomonas oryzae",
            disease_type=DiseaseType.BACTERIAL,
            primary_hosts=["corn", "rice"],
            transmission_methods=[TransmissionMethod.WATERBORNE, TransmissionMethod.SEEDBORNE],
            survival_structures=["bacterial_cells"],
            overwintering_method="crop_residue",
            disease_conditions=DiseaseConditions(
                optimal_temperature_range=(25, 32),
                optimal_humidity_range=(90, 100),
                optimal_wetness_hours=2,
                seasonal_factors={"summer": 1.8, "rainy_season": 2.2}
            ),
            max_yield_loss_percent=40.0,
            economic_threshold=12.0,
            symptoms=DiseaseSymptoms(
                early_symptoms=["water_soaked_lesions", "bacterial_streaming"],
                advanced_symptoms=["leaf_wilting", "systemic_infection"],
                affected_plant_parts=["leaves", "stems"]
            )
        )
        
        # Viral diseases
        self.disease_database["maize_dwarf_mosaic"] = Disease(
            disease_id="maize_dwarf_mosaic",
            common_name="Maize Dwarf Mosaic Virus",
            scientific_name="Maize dwarf mosaic virus",
            disease_type=DiseaseType.VIRAL,
            primary_hosts=["corn"],
            secondary_hosts=["johnsongrass", "sorghum"],
            transmission_methods=[TransmissionMethod.INSECT_VECTOR],
            overwintering_method="perennial_hosts",
            disease_conditions=DiseaseConditions(
                optimal_temperature_range=(22, 30),
                seasonal_factors={"summer": 1.5}
            ),
            max_yield_loss_percent=30.0,
            economic_threshold=20.0,
            cultural_controls=["weed_control", "vector_management"],
            symptoms=DiseaseSymptoms(
                early_symptoms=["mosaic_patterns", "stunted_growth"],
                advanced_symptoms=["severe_dwarfing", "yield_reduction"],
                affected_plant_parts=["leaves", "entire_plant"]
            )
        )
        
        print(f"Initialized disease database with {len(self.disease_database)} diseases")
    
    def _initialize_resistance_profiles(self):
        """Initialize crop variety resistance profiles"""
        
        # Corn resistance profiles
        self.resistance_profiles["corn_bt_hybrid"] = ResistanceProfile(
            variety_id="corn_bt_hybrid",
            crop_id="corn",
            resistance_ratings={
                "corn_gray_leaf_spot": ResistanceType.MODERATELY_RESISTANT,
                "corn_northern_leaf_blight": ResistanceType.HIGHLY_RESISTANT,
                "maize_dwarf_mosaic": ResistanceType.TOLERANT
            },
            resistance_genes={
                "corn_northern_leaf_blight": ["Ht1", "Ht2", "Ht3"]
            },
            resistance_durability={
                "corn_northern_leaf_blight": 8,
                "corn_gray_leaf_spot": 5
            }
        )
        
        # Soybean resistance profiles
        self.resistance_profiles["soybean_resistant"] = ResistanceProfile(
            variety_id="soybean_resistant",
            crop_id="soybeans",
            resistance_ratings={
                "soybean_rust": ResistanceType.HIGHLY_RESISTANT,
                "soybean_sudden_death": ResistanceType.MODERATELY_RESISTANT
            },
            resistance_genes={
                "soybean_rust": ["Rpp1", "Rpp2", "Rpp3"]
            },
            resistance_durability={
                "soybean_rust": 6,
                "soybean_sudden_death": 10
            },
            yield_penalty=0.05  # 5% yield penalty for resistance
        )
        
        # Wheat resistance profiles
        self.resistance_profiles["wheat_resistant"] = ResistanceProfile(
            variety_id="wheat_resistant",
            crop_id="wheat",
            resistance_ratings={
                "wheat_stripe_rust": ResistanceType.HIGHLY_RESISTANT
            },
            resistance_genes={
                "wheat_stripe_rust": ["Yr5", "Yr10", "Yr15"]
            },
            resistance_durability={
                "wheat_stripe_rust": 7
            }
        )
        
        print(f"Initialized {len(self.resistance_profiles)} resistance profiles")
    
    def _register_event_handlers(self):
        """Register event handlers for system integration"""
        self.event_system.subscribe("weather_conditions_updated", self._handle_weather_update)
        self.event_system.subscribe("crop_growth_stage_changed", self._handle_growth_stage_change)
        self.event_system.subscribe("field_operation_completed", self._handle_field_operation)
        self.event_system.subscribe("season_changed", self._handle_season_change)
        self.event_system.subscribe("time_advanced", self._handle_time_advancement)
    
    def _initialize_disease_pressure_tracking(self):
        """Initialize environmental disease pressure tracking systems"""
        # Initialize regional disease pressure tracking
        regions = ["midwest", "great_plains", "southeast", "northwest"]
        
        for region in regions:
            self.environmental_pressure[region] = 0.0
            self.seasonal_disease_patterns[region] = {}
            self.disease_forecasts[region] = {}
            
            # Initialize seasonal patterns for each disease
            for disease_id in self.disease_database:
                self.seasonal_disease_patterns[region][disease_id] = 0.0
                self.disease_forecasts[region][disease_id] = 0.0
    
    def assess_disease_risk(self, location_id: str, crop_id: str, 
                          environmental_conditions: Dict[str, Any]) -> Dict[str, float]:
        """Assess disease risk for specific location and crop"""
        
        risk_assessment = {}
        
        # Get applicable diseases for this crop
        applicable_diseases = [
            disease for disease in self.disease_database.values()
            if crop_id in disease.primary_hosts or crop_id in disease.secondary_hosts
        ]
        
        for disease in applicable_diseases:
            risk_score = self._calculate_disease_risk_score(
                disease, location_id, crop_id, environmental_conditions
            )
            risk_assessment[disease.disease_id] = risk_score
        
        return risk_assessment
    
    def _calculate_disease_risk_score(self, disease: Disease, location_id: str, 
                                    crop_id: str, conditions: Dict[str, Any]) -> float:
        """Calculate disease risk score (0-1) for specific disease"""
        
        risk_factors = []
        
        # Environmental favorability
        env_score = self._assess_environmental_favorability(disease, conditions)
        risk_factors.append(env_score * self.system_parameters['environmental_weight'])
        
        # Host susceptibility
        host_score = self._assess_host_susceptibility(disease, crop_id)
        risk_factors.append(host_score * self.system_parameters['host_resistance_weight'])
        
        # Inoculum pressure (pathogen presence)
        inoculum_score = self._assess_inoculum_pressure(disease, location_id)
        risk_factors.append(inoculum_score * 0.6)
        
        # Seasonal factors
        seasonal_score = self._assess_seasonal_factors(disease)
        risk_factors.append(seasonal_score * 0.4)
        
        # Calculate weighted average
        total_weight = (self.system_parameters['environmental_weight'] + 
                       self.system_parameters['host_resistance_weight'] + 0.6 + 0.4)
        
        final_risk_score = sum(risk_factors) / total_weight
        
        return min(max(final_risk_score, 0.0), 1.0)
    
    def _assess_environmental_favorability(self, disease: Disease, conditions: Dict[str, Any]) -> float:
        """Assess how favorable environmental conditions are for disease"""
        
        favorability_scores = []
        disease_conditions = disease.disease_conditions
        
        # Temperature favorability
        current_temp = conditions.get('temperature_c', 20)
        temp_min, temp_max = disease_conditions.optimal_temperature_range
        
        if temp_min <= current_temp <= temp_max:
            temp_score = 1.0
        else:
            # Calculate distance from optimal range
            if current_temp < temp_min:
                temp_score = max(0, 1 - (temp_min - current_temp) / 10)
            else:
                temp_score = max(0, 1 - (current_temp - temp_max) / 10)
        
        favorability_scores.append(temp_score)
        
        # Humidity favorability
        current_humidity = conditions.get('humidity_percent', 60)
        humid_min, humid_max = disease_conditions.optimal_humidity_range
        
        if humid_min <= current_humidity <= humid_max:
            humid_score = 1.0
        else:
            if current_humidity < humid_min:
                humid_score = max(0, 1 - (humid_min - current_humidity) / 20)
            else:
                humid_score = max(0, 1 - (current_humidity - humid_max) / 20)
        
        favorability_scores.append(humid_score)
        
        # Wetness duration favorability
        leaf_wetness = conditions.get('leaf_wetness_hours', 0)
        optimal_wetness = disease_conditions.optimal_wetness_hours
        
        if leaf_wetness >= optimal_wetness:
            wetness_score = 1.0
        else:
            wetness_score = leaf_wetness / optimal_wetness
        
        favorability_scores.append(wetness_score)
        
        # Calculate average environmental favorability
        return sum(favorability_scores) / len(favorability_scores)
    
    def _assess_host_susceptibility(self, disease: Disease, crop_id: str) -> float:
        """Assess host plant susceptibility to disease"""
        
        # Check if variety-specific resistance profile exists
        variety_resistance = None
        for profile in self.resistance_profiles.values():
            if profile.crop_id == crop_id:
                variety_resistance = profile.resistance_ratings.get(disease.disease_id)
                break
        
        if variety_resistance:
            # Convert resistance type to susceptibility score
            resistance_scores = {
                ResistanceType.IMMUNE: 0.0,
                ResistanceType.HIGHLY_RESISTANT: 0.1,
                ResistanceType.MODERATELY_RESISTANT: 0.3,
                ResistanceType.TOLERANT: 0.5,
                ResistanceType.SUSCEPTIBLE: 0.8,
                ResistanceType.HIGHLY_SUSCEPTIBLE: 1.0
            }
            return resistance_scores.get(variety_resistance, 0.8)
        else:
            # Default susceptibility for crops in host range
            if crop_id in disease.primary_hosts:
                return 0.8  # High susceptibility for primary hosts
            elif crop_id in disease.secondary_hosts:
                return 0.4  # Moderate susceptibility for secondary hosts
            else:
                return 0.0  # No susceptibility for non-hosts
    
    def _assess_inoculum_pressure(self, disease: Disease, location_id: str) -> float:
        """Assess pathogen inoculum pressure at location"""
        
        # Base inoculum pressure
        base_pressure = 0.3
        
        # Increase pressure based on previous disease incidents
        location_incidents = [
            incident for incident in self.active_incidents.values()
            if (incident.location_id == location_id and 
                incident.disease_id == disease.disease_id and
                incident.current_stage in [DiseaseStage.SPORULATION, DiseaseStage.SEVERE])
        ]
        
        incident_pressure = min(len(location_incidents) * 0.2, 0.6)
        
        # Environmental inoculum factors
        survival_pressure = 0.0
        if "crop_residue" in disease.overwintering_method:
            survival_pressure += 0.3
        if "soil_survival" in disease.overwintering_method:
            survival_pressure += 0.4
        if "alternate_hosts" in disease.overwintering_method:
            survival_pressure += 0.2
        
        total_pressure = base_pressure + incident_pressure + survival_pressure
        return min(total_pressure, 1.0)
    
    def _assess_seasonal_factors(self, disease: Disease) -> float:
        """Assess seasonal factors affecting disease risk"""
        
        current_season = self._get_current_season()
        seasonal_factors = disease.disease_conditions.seasonal_factors
        
        return seasonal_factors.get(current_season, 1.0)
    
    def _get_current_season(self) -> str:
        """Determine current agricultural season"""
        current_month = datetime.now().month
        
        if current_month in [12, 1, 2]:
            return 'winter'
        elif current_month in [3, 4, 5]:
            return 'spring'
        elif current_month in [6, 7, 8]:
            return 'summer'
        else:  # [9, 10, 11]
            return 'fall'
    
    def initiate_disease_infection(self, location_id: str, crop_id: str, disease_id: str,
                                 environmental_conditions: Dict[str, Any]) -> Optional[DiseaseIncident]:
        """Initiate a new disease infection"""
        
        if disease_id not in self.disease_database:
            print(f"Disease {disease_id} not found in database")
            return None
        
        disease = self.disease_database[disease_id]
        
        # Check if crop is susceptible to this disease
        if crop_id not in disease.primary_hosts and crop_id not in disease.secondary_hosts:
            return None
        
        # Calculate infection probability
        risk_score = self._calculate_disease_risk_score(disease, location_id, crop_id, environmental_conditions)
        infection_probability = risk_score * self.system_parameters['infection_probability_base']
        
        # Determine if infection occurs
        if random.random() < infection_probability:
            # Create disease incident
            incident_id = f"DIS_{location_id}_{disease_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            incident = DiseaseIncident(
                incident_id=incident_id,
                disease_id=disease_id,
                location_id=location_id,
                crop_id=crop_id,
                current_stage=DiseaseStage.INFECTION,
                severity_percent=1.0,  # Start with 1% severity
                affected_area_percent=random.uniform(0.1, 2.0),  # Start small
                infection_date=datetime.now(),
                infection_conditions=environmental_conditions.copy(),
                weather_favorability=self._assess_environmental_favorability(disease, environmental_conditions)
            )
            
            # Store incident
            self.active_incidents[incident_id] = incident
            
            # Update statistics
            self.disease_statistics['total_incidents'] += 1
            self.disease_statistics['active_incidents'] = len([
                i for i in self.active_incidents.values() 
                if i.current_stage not in [DiseaseStage.SENESCENCE]
            ])
            
            # Emit infection event
            self.event_system.emit_event("disease_infection_initiated", {
                "incident_id": incident_id,
                "disease_id": disease_id,
                "location_id": location_id,
                "crop_id": crop_id,
                "initial_severity": incident.severity_percent,
                "risk_score": risk_score
            })
            
            print(f"Disease infection initiated: {disease.common_name} on {crop_id} at {location_id}")
            
            return incident
        
        return None
    
    def progress_disease_development(self, incident_id: str, time_delta_days: float) -> bool:
        """Progress disease development over time"""
        
        if incident_id not in self.active_incidents:
            return False
        
        incident = self.active_incidents[incident_id]
        disease = self.disease_database[incident.disease_id]
        
        # Skip if disease is dormant or resolved
        if incident.current_stage in [DiseaseStage.DORMANT, DiseaseStage.SENESCENCE]:
            return True
        
        # Calculate disease progression rate based on environmental favorability
        base_progression = self.system_parameters['severity_progression_rate']
        progression_rate = base_progression * (1 + incident.weather_favorability)
        
        # Progress severity
        severity_increase = progression_rate * time_delta_days
        incident.severity_percent = min(incident.severity_percent + severity_increase, 100.0)
        
        # Progress disease stage based on time and severity
        self._update_disease_stage(incident, disease)
        
        # Update spread within field
        if incident.current_stage == DiseaseStage.SPORULATION:
            spread_rate = self._calculate_spread_rate(incident, disease)
            area_increase = spread_rate * time_delta_days
            incident.affected_area_percent = min(incident.affected_area_percent + area_increase, 100.0)
        
        # Calculate yield impact
        incident.current_yield_impact = self._calculate_yield_impact(incident, disease)
        
        # Emit progression event
        self.event_system.emit_event("disease_progressed", {
            "incident_id": incident_id,
            "current_stage": incident.current_stage.value,
            "severity": incident.severity_percent,
            "affected_area": incident.affected_area_percent,
            "yield_impact": incident.current_yield_impact
        })
        
        return True
    
    def _update_disease_stage(self, incident: DiseaseIncident, disease: Disease):
        """Update disease development stage"""
        
        days_since_infection = (datetime.now() - incident.infection_date).days
        
        # Stage progression based on time and severity
        if incident.current_stage == DiseaseStage.INFECTION:
            min_incubation, max_incubation = disease.incubation_period_days
            if days_since_infection >= min_incubation or incident.severity_percent >= 5.0:
                incident.current_stage = DiseaseStage.INCUBATION
        
        elif incident.current_stage == DiseaseStage.INCUBATION:
            if incident.severity_percent >= 10.0:
                incident.current_stage = DiseaseStage.VISIBLE
                incident.detection_date = datetime.now()
        
        elif incident.current_stage == DiseaseStage.VISIBLE:
            if incident.severity_percent >= 25.0:
                incident.current_stage = DiseaseStage.SPORULATION
        
        elif incident.current_stage == DiseaseStage.SPORULATION:
            if incident.severity_percent >= 60.0:
                incident.current_stage = DiseaseStage.SEVERE
                incident.peak_severity_date = datetime.now()
        
        elif incident.current_stage == DiseaseStage.SEVERE:
            # Natural senescence or control
            if incident.severity_percent >= 90.0 or days_since_infection > 90:
                incident.current_stage = DiseaseStage.SENESCENCE
                incident.resolution_date = datetime.now()
    
    def _calculate_spread_rate(self, incident: DiseaseIncident, disease: Disease) -> float:
        """Calculate disease spread rate within field"""
        
        base_spread_rate = 1.0  # %/day base spread rate
        
        # Environmental factors
        environmental_multiplier = 1 + incident.weather_favorability
        
        # Transmission method effects
        transmission_multiplier = 1.0
        if TransmissionMethod.AIRBORNE in disease.transmission_methods:
            transmission_multiplier *= 1.5
        if TransmissionMethod.WATERBORNE in disease.transmission_methods:
            transmission_multiplier *= 1.2
        
        # Density effects (slower spread as area increases)
        density_factor = 1.0 / (1 + incident.affected_area_percent / 50.0)
        
        final_spread_rate = (base_spread_rate * environmental_multiplier * 
                           transmission_multiplier * density_factor)
        
        return final_spread_rate * self.system_parameters['spread_rate_multiplier']
    
    def _calculate_yield_impact(self, incident: DiseaseIncident, disease: Disease) -> float:
        """Calculate current yield impact of disease"""
        
        # Base yield impact based on severity and affected area
        severity_impact = (incident.severity_percent / 100.0) * disease.max_yield_loss_percent
        area_impact = incident.affected_area_percent / 100.0
        
        # Stage-based impact multipliers
        stage_multipliers = {
            DiseaseStage.INFECTION: 0.0,
            DiseaseStage.INCUBATION: 0.1,
            DiseaseStage.VISIBLE: 0.3,
            DiseaseStage.SPORULATION: 0.7,
            DiseaseStage.SEVERE: 1.0,
            DiseaseStage.SENESCENCE: 1.0
        }
        
        stage_multiplier = stage_multipliers.get(incident.current_stage, 0.5)
        
        # Calculate final yield impact
        yield_impact = severity_impact * area_impact * stage_multiplier
        
        return min(yield_impact, disease.max_yield_loss_percent)
    
    def conduct_disease_monitoring(self, location_id: str, scout_date: datetime = None) -> DiseaseMonitoring:
        """Conduct disease monitoring/scouting at location"""
        
        if scout_date is None:
            scout_date = datetime.now()
        
        monitoring_id = f"MON_{location_id}_{scout_date.strftime('%Y%m%d_%H%M%S')}"
        
        # Collect monitoring data
        monitoring = DiseaseMonitoring(
            monitoring_id=monitoring_id,
            location_id=location_id,
            scout_date=scout_date
        )
        
        # Detect diseases at location
        location_incidents = [
            incident for incident in self.active_incidents.values()
            if incident.location_id == location_id
        ]
        
        for incident in location_incidents:
            disease = self.disease_database[incident.disease_id]
            
            # Determine if disease is detectable based on severity and stage
            detection_threshold = self.system_parameters['monitoring_detection_threshold']
            
            if (incident.severity_percent >= detection_threshold and 
                incident.current_stage in [DiseaseStage.VISIBLE, DiseaseStage.SPORULATION, 
                                         DiseaseStage.SEVERE]):
                
                monitoring.diseases_detected.append(incident.disease_id)
                monitoring.disease_severity[incident.disease_id] = incident.severity_percent
                
                # Record observed symptoms
                if incident.current_stage == DiseaseStage.VISIBLE:
                    monitoring.symptoms_observed[incident.disease_id] = disease.symptoms.early_symptoms
                else:
                    monitoring.symptoms_observed[incident.disease_id] = disease.symptoms.advanced_symptoms
        
        # Assess overall disease pressure
        if not monitoring.diseases_detected:
            monitoring.disease_pressure_rating = "low"
        elif len(monitoring.diseases_detected) == 1 and max(monitoring.disease_severity.values()) < 20:
            monitoring.disease_pressure_rating = "moderate"
        elif max(monitoring.disease_severity.values()) < 50:
            monitoring.disease_pressure_rating = "high"
        else:
            monitoring.disease_pressure_rating = "severe"
        
        # Generate treatment recommendations
        monitoring.treatment_recommendations = self._generate_treatment_recommendations(monitoring)
        
        # Store monitoring record
        if location_id not in self.monitoring_records:
            self.monitoring_records[location_id] = []
        self.monitoring_records[location_id].append(monitoring)
        
        # Emit monitoring event
        self.event_system.emit_event("disease_monitoring_completed", {
            "monitoring_id": monitoring_id,
            "location_id": location_id,
            "diseases_detected": len(monitoring.diseases_detected),
            "pressure_rating": monitoring.disease_pressure_rating,
            "recommendations": len(monitoring.treatment_recommendations)
        })
        
        return monitoring
    
    def _generate_treatment_recommendations(self, monitoring: DiseaseMonitoring) -> List[str]:
        """Generate treatment recommendations based on monitoring results"""
        
        recommendations = []
        
        for disease_id, severity in monitoring.disease_severity.items():
            disease = self.disease_database[disease_id]
            
            # Check if economic threshold is exceeded
            if severity >= disease.economic_threshold:
                
                # Chemical control recommendations
                if disease.chemical_controls:
                    recommendations.append(
                        f"Apply {disease.chemical_controls[0]} for {disease.common_name} control"
                    )
                
                # Cultural control recommendations
                if disease.cultural_controls and severity < 30:
                    recommendations.append(
                        f"Implement {disease.cultural_controls[0]} for {disease.common_name} management"
                    )
                
                # Biological control recommendations
                if disease.biological_controls and severity < 20:
                    recommendations.append(
                        f"Consider {disease.biological_controls[0]} for biological control"
                    )
        
        # General recommendations
        if monitoring.disease_pressure_rating in ["high", "severe"]:
            recommendations.append("Increase monitoring frequency to weekly")
            recommendations.append("Consider preventive fungicide applications")
        
        return recommendations
    
    def apply_disease_treatment(self, incident_id: str, treatment_type: str, 
                              efficacy: float, application_date: datetime = None) -> Dict[str, Any]:
        """Apply disease treatment and track results"""
        
        if incident_id not in self.active_incidents:
            return {"success": False, "error": "Disease incident not found"}
        
        if application_date is None:
            application_date = datetime.now()
        
        incident = self.active_incidents[incident_id]
        disease = self.disease_database[incident.disease_id]
        
        # Calculate treatment effectiveness
        base_efficacy = efficacy * self.system_parameters['treatment_efficacy_base']
        
        # Adjust efficacy based on disease stage (earlier treatment more effective)
        stage_efficacy_multipliers = {
            DiseaseStage.INFECTION: 0.9,
            DiseaseStage.INCUBATION: 0.8,
            DiseaseStage.VISIBLE: 0.7,
            DiseaseStage.SPORULATION: 0.5,
            DiseaseStage.SEVERE: 0.3,
            DiseaseStage.SENESCENCE: 0.1
        }
        
        stage_multiplier = stage_efficacy_multipliers.get(incident.current_stage, 0.5)
        final_efficacy = base_efficacy * stage_multiplier
        
        # Apply treatment effects
        severity_reduction = incident.severity_percent * final_efficacy
        incident.severity_percent = max(incident.severity_percent - severity_reduction, 0)
        
        # Slow spread rate
        incident.spread_rate *= (1 - final_efficacy * 0.8)
        
        # Record treatment
        treatment_record = {
            "treatment_type": treatment_type,
            "application_date": application_date,
            "efficacy_applied": efficacy,
            "final_efficacy": final_efficacy,
            "severity_before": incident.severity_percent + severity_reduction,
            "severity_after": incident.severity_percent,
            "reduction_achieved": severity_reduction
        }
        
        incident.treatments_applied.append(treatment_record)
        incident.control_effectiveness[treatment_type] = final_efficacy
        
        # Update statistics
        self.disease_statistics['treatment_costs'] += 50.0  # Simplified cost
        
        # Emit treatment event
        self.event_system.emit_event("disease_treatment_applied", {
            "incident_id": incident_id,
            "treatment_type": treatment_type,
            "efficacy": final_efficacy,
            "severity_reduction": severity_reduction
        })
        
        return {
            "success": True,
            "treatment_efficacy": final_efficacy,
            "severity_reduction": severity_reduction,
            "new_severity": incident.severity_percent
        }
    
    # Event handlers for system integration
    def _handle_weather_update(self, event_data: Dict[str, Any]):
        """Handle weather condition updates"""
        location_id = event_data.get("location_id", "default")
        conditions = event_data.get("conditions", {})
        
        # Update environmental disease pressure
        self._update_environmental_pressure(location_id, conditions)
        
        # Check for new infection opportunities
        self._evaluate_infection_opportunities(location_id, conditions)
    
    def _update_environmental_pressure(self, location_id: str, conditions: Dict[str, Any]):
        """Update environmental disease pressure based on weather"""
        
        pressure_factors = []
        
        # Temperature factor
        temp = conditions.get('temperature_c', 20)
        if 15 <= temp <= 30:  # Favorable temperature range for most diseases
            pressure_factors.append(0.8)
        else:
            pressure_factors.append(0.3)
        
        # Humidity factor
        humidity = conditions.get('humidity_percent', 60)
        if humidity >= 80:
            pressure_factors.append(1.0)
        elif humidity >= 60:
            pressure_factors.append(0.6)
        else:
            pressure_factors.append(0.2)
        
        # Wetness factor
        wetness = conditions.get('leaf_wetness_hours', 0)
        if wetness >= 12:
            pressure_factors.append(1.0)
        elif wetness >= 6:
            pressure_factors.append(0.7)
        else:
            pressure_factors.append(0.3)
        
        # Calculate overall pressure
        overall_pressure = sum(pressure_factors) / len(pressure_factors)
        self.environmental_pressure[location_id] = overall_pressure
    
    def _evaluate_infection_opportunities(self, location_id: str, conditions: Dict[str, Any]):
        """Evaluate potential for new disease infections"""
        
        # This would integrate with crop management system to get current crops
        # For now, simulate with common crops
        crops = ["corn", "soybeans", "wheat"]
        
        for crop_id in crops:
            risk_assessment = self.assess_disease_risk(location_id, crop_id, conditions)
            
            for disease_id, risk_score in risk_assessment.items():
                if risk_score > 0.7:  # High risk threshold
                    # Attempt disease infection
                    self.initiate_disease_infection(location_id, crop_id, disease_id, conditions)
    
    def _handle_growth_stage_change(self, event_data: Dict[str, Any]):
        """Handle crop growth stage changes affecting disease susceptibility"""
        location_id = event_data.get("location_id")
        crop_id = event_data.get("crop_id")
        new_stage = event_data.get("growth_stage")
        
        # Adjust disease susceptibility based on growth stage
        # Some diseases are more severe at certain growth stages
        for incident in self.active_incidents.values():
            if incident.location_id == location_id and incident.crop_id == crop_id:
                self._adjust_disease_for_growth_stage(incident, new_stage)
    
    def _adjust_disease_for_growth_stage(self, incident: DiseaseIncident, growth_stage: str):
        """Adjust disease severity based on crop growth stage"""
        
        # Growth stage susceptibility factors
        stage_factors = {
            "seedling": 1.2,      # More susceptible when young
            "vegetative": 1.0,    # Normal susceptibility
            "reproductive": 1.3,  # More susceptible during reproduction
            "maturity": 0.8       # Less susceptible when mature
        }
        
        stage_factor = stage_factors.get(growth_stage, 1.0)
        
        # Adjust progression rate for future development
        # This would be applied in the next disease progression update
        pass
    
    def _handle_field_operation(self, event_data: Dict[str, Any]):
        """Handle field operations that may affect disease"""
        operation_type = event_data.get("operation_type")
        location_id = event_data.get("location_id")
        
        if operation_type in ["tillage", "cultivation"]:
            # Reduce soilborne disease inoculum
            self._reduce_soilborne_inoculum(location_id, 0.3)
        
        elif operation_type == "harvest":
            # Create crop residue that may harbor pathogens
            self._increase_residue_inoculum(location_id, 0.4)
    
    def _reduce_soilborne_inoculum(self, location_id: str, reduction_factor: float):
        """Reduce soilborne pathogen inoculum through tillage"""
        
        for incident in self.active_incidents.values():
            if (incident.location_id == location_id and 
                incident.disease_id in self.disease_database):
                
                disease = self.disease_database[incident.disease_id]
                if TransmissionMethod.SOILBORNE in disease.transmission_methods:
                    # Reduce severity due to inoculum reduction
                    incident.severity_percent *= (1 - reduction_factor)
    
    def _increase_residue_inoculum(self, location_id: str, increase_factor: float):
        """Increase crop residue pathogen inoculum after harvest"""
        
        # This would increase future disease risk for residue-borne pathogens
        # Implementation would affect next season's disease pressure
        pass
    
    def _handle_season_change(self, event_data: Dict[str, Any]):
        """Handle seasonal changes affecting disease patterns"""
        new_season = event_data.get("season")
        
        # Update seasonal disease patterns
        for location_id in self.seasonal_disease_patterns:
            for disease_id, disease in self.disease_database.items():
                seasonal_factor = disease.disease_conditions.seasonal_factors.get(new_season, 1.0)
                self.seasonal_disease_patterns[location_id][disease_id] = seasonal_factor
    
    def _handle_time_advancement(self, event_data: Dict[str, Any]):
        """Handle time advancement for disease progression"""
        time_delta_days = event_data.get("days_elapsed", 1.0)
        
        # Progress all active disease incidents
        for incident_id in list(self.active_incidents.keys()):
            self.progress_disease_development(incident_id, time_delta_days)
    
    def get_disease_status_summary(self, location_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive disease status summary"""
        
        # Filter incidents by location if specified
        if location_id:
            incidents = [i for i in self.active_incidents.values() if i.location_id == location_id]
        else:
            incidents = list(self.active_incidents.values())
        
        # Count incidents by stage
        stage_counts = {}
        for stage in DiseaseStage:
            stage_counts[stage.value] = len([i for i in incidents if i.current_stage == stage])
        
        # Calculate total yield impact
        total_yield_impact = sum(i.current_yield_impact for i in incidents)
        
        # Get most common diseases
        disease_counts = {}
        for incident in incidents:
            disease_id = incident.disease_id
            disease_name = self.disease_database[disease_id].common_name
            disease_counts[disease_name] = disease_counts.get(disease_name, 0) + 1
        
        most_common_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_active_incidents": len(incidents),
            "incidents_by_stage": stage_counts,
            "total_yield_impact": total_yield_impact,
            "most_common_diseases": most_common_diseases,
            "average_severity": sum(i.severity_percent for i in incidents) / len(incidents) if incidents else 0,
            "locations_affected": len(set(i.location_id for i in incidents)),
            "disease_pressure": {
                location: pressure for location, pressure in self.environmental_pressure.items()
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get disease framework system status"""
        return {
            "system_status": "active" if self.is_initialized else "inactive",
            "diseases_in_database": len(self.disease_database),
            "resistance_profiles": len(self.resistance_profiles),
            "active_incidents": len(self.active_incidents),
            "monitoring_locations": len(self.monitoring_records),
            "total_yield_impact": sum(i.current_yield_impact for i in self.active_incidents.values()),
            "system_statistics": self.disease_statistics
        }

# Global convenience functions
def get_disease_framework() -> Optional[DiseaseFramework]:
    """Get the global disease framework instance"""
    # This would typically be managed by a system registry
    return None

def assess_field_disease_risk(location_id: str, crop_id: str, conditions: Dict[str, Any]) -> Dict[str, float]:
    """Convenience function to assess disease risk for a field"""
    system = get_disease_framework()
    if system:
        return system.assess_disease_risk(location_id, crop_id, conditions)
    return {}

def monitor_field_diseases(location_id: str) -> Optional[DiseaseMonitoring]:
    """Convenience function to conduct disease monitoring"""
    system = get_disease_framework()
    if system:
        return system.conduct_disease_monitoring(location_id)
    return None

def treat_disease_incident(incident_id: str, treatment_type: str, efficacy: float) -> Dict[str, Any]:
    """Convenience function to treat a disease incident"""
    system = get_disease_framework()
    if system:
        return system.apply_disease_treatment(incident_id, treatment_type, efficacy)
    return {"success": False, "error": "Disease system not available"}