"""
Soil Health System - Comprehensive Soil Science Simulation for AgriFun Agricultural Game

This system provides realistic soil health management with N-P-K tracking, pH levels,
organic matter simulation, and comprehensive soil chemistry. Integrates with crop
growth systems to provide educational agricultural soil science gameplay.

Key Features:
- Complete N-P-K-S nutrient cycle simulation
- pH level management and crop-specific requirements
- Organic matter decomposition and soil structure
- Micronutrient tracking (Ca, Mg, Fe, Zn, B, etc.)
- Soil compaction and structure management
- Water retention and drainage characteristics
- Soil biology and microbial activity simulation

Educational Value:
- Real-world soil chemistry principles
- Understanding of nutrient cycling and availability
- Soil management decisions and their consequences
- Sustainable agriculture and soil conservation practices
- Crop rotation benefits and soil health relationships

System Integration:
- Integrates with Advanced Growth System for nutrient supply
- Uses Multi-Crop Framework for variety-specific requirements
- Connects to Weather System for moisture and temperature effects
- Interfaces with Equipment System for soil management tools
- Links to Time Management for seasonal soil changes
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
from datetime import datetime, timedelta
import json
import math
import random

# Import Phase 1 systems
from scripts.core.advanced_event_system import EventSystem
from scripts.core.time_management import TimeManager
from scripts.core.advanced_config_system import ConfigurationManager
from scripts.core.content_registry import ContentRegistry
from scripts.core.entity_component_system import System, Component

# Phase 3 system imports
from scripts.systems.multicrop_framework import (
    MultiCropFramework, AdvancedCropVariety, GeneticProfile
)
from scripts.systems.advanced_growth_system import (
    AdvancedGrowthSystem, EnvironmentalFactor
)

# Configure logging for soil health system
logger = logging.getLogger(__name__)

class SoilTexture(Enum):
    """Soil texture classifications"""
    SAND = "sand"               # High drainage, low nutrient retention
    LOAMY_SAND = "loamy_sand"   # Moderate drainage, low-moderate retention
    SANDY_LOAM = "sandy_loam"   # Good drainage, moderate retention
    LOAM = "loam"              # Ideal balance of drainage and retention
    SILT_LOAM = "silt_loam"    # Good retention, moderate drainage
    CLAY_LOAM = "clay_loam"    # High retention, slower drainage
    CLAY = "clay"              # Very high retention, poor drainage

class SoilStructure(Enum):
    """Soil structure types affecting root penetration and water movement"""
    GRANULAR = "granular"       # Excellent structure, optimal root growth
    BLOCKY = "blocky"          # Good structure, good water movement
    PRISMATIC = "prismatic"     # Moderate structure, vertical water movement
    PLATY = "platy"            # Poor structure, restricted water movement
    MASSIVE = "massive"         # Very poor structure, compacted soil

class SoilHealth(Enum):
    """Overall soil health categories"""
    EXCELLENT = "excellent"     # 90-100% optimal conditions
    GOOD = "good"              # 75-89% optimal conditions
    FAIR = "fair"              # 60-74% optimal conditions
    POOR = "poor"              # 40-59% optimal conditions
    VERY_POOR = "very_poor"    # Below 40% optimal conditions

class NutrientAvailability(Enum):
    """Nutrient availability status"""
    DEFICIENT = "deficient"     # Below crop requirements
    LOW = "low"                # Minimal for crop needs
    ADEQUATE = "adequate"       # Sufficient for normal growth
    HIGH = "high"              # Abundant, optimal growth
    EXCESSIVE = "excessive"     # Too high, potential toxicity

@dataclass
class Nutrient:
    """Individual nutrient tracking"""
    symbol: str                # Chemical symbol (N, P, K, S, Ca, etc.)
    name: str                  # Full nutrient name
    current_ppm: float         # Current concentration in parts per million
    available_ppm: float       # Plant-available portion
    organic_bound_ppm: float   # Organically bound, slowly released
    mineral_bound_ppm: float   # Mineral-bound, very slowly released
    
    # Availability factors
    ph_availability_curve: Dict[float, float]  # pH vs availability factor
    temperature_factor: float  # Temperature effect on availability
    moisture_factor: float     # Moisture effect on availability
    microbial_factor: float    # Microbial activity effect
    
    # Movement characteristics
    mobility: float            # How easily nutrient moves in soil (0.0-1.0)
    leaching_rate: float       # Rate of loss through leaching
    fixation_rate: float       # Rate of conversion to unavailable forms
    
    def get_availability_factor(self, ph: float, temperature: float, 
                               moisture: float, microbial_activity: float) -> float:
        """Calculate overall nutrient availability factor"""
        # pH availability (most nutrients have optimal pH ranges)
        ph_factor = self.ph_availability_curve.get(round(ph, 1), 0.5)
        
        # Temperature factor (higher temps generally increase availability)
        temp_factor = min(1.0, max(0.1, temperature / 25.0))  # Optimal at 25°C
        
        # Moisture factor (needs adequate moisture for uptake)
        moisture_factor = min(1.0, max(0.1, moisture))
        
        # Microbial factor (biology helps release nutrients)
        bio_factor = min(1.0, max(0.2, microbial_activity))
        
        # Combined availability factor
        combined_factor = (ph_factor * temp_factor * moisture_factor * bio_factor) ** 0.25
        return max(0.05, min(1.0, combined_factor))
    
    def update_available_amount(self, ph: float, temperature: float, 
                               moisture: float, microbial_activity: float):
        """Update plant-available nutrient amount based on conditions"""
        availability_factor = self.get_availability_factor(ph, temperature, moisture, microbial_activity)
        
        # Calculate available nutrients from different pools
        organic_available = self.organic_bound_ppm * availability_factor * 0.1  # Slow release
        mineral_available = self.mineral_bound_ppm * availability_factor * 0.02  # Very slow release
        direct_available = self.current_ppm * availability_factor
        
        self.available_ppm = organic_available + mineral_available + direct_available

@dataclass
class SoilChemistry:
    """Complete soil chemistry profile"""
    # Major nutrients (macronutrients)
    nitrogen: Nutrient         # N - Primary growth nutrient
    phosphorus: Nutrient       # P - Root development and energy
    potassium: Nutrient        # K - Water regulation and disease resistance
    sulfur: Nutrient           # S - Protein synthesis
    
    # Secondary nutrients
    calcium: Nutrient          # Ca - Cell wall structure and pH buffering
    magnesium: Nutrient        # Mg - Chlorophyll center and enzyme activation
    
    # Micronutrients
    iron: Nutrient             # Fe - Chlorophyll synthesis
    manganese: Nutrient        # Mn - Enzyme activation and photosynthesis
    zinc: Nutrient             # Zn - Enzyme systems and growth regulation
    copper: Nutrient           # Cu - Enzyme systems and lignin formation
    boron: Nutrient            # B - Cell wall formation and reproduction
    molybdenum: Nutrient       # Mo - Nitrogen fixation and enzyme function
    
    # Soil reaction
    ph: float                  # Soil pH (3.0-10.0, optimal 6.0-7.0 for most crops)
    buffer_capacity: float     # Resistance to pH change (0.0-1.0)
    
    # Soil salinity
    electrical_conductivity: float  # EC in dS/m, measure of salt content
    sodium_percentage: float   # Exchangeable sodium percentage
    
    # Cation exchange capacity
    cec: float                 # CEC in meq/100g, nutrient holding capacity
    base_saturation: float     # Percentage of CEC filled with base cations

@dataclass
class SoilPhysical:
    """Physical soil properties"""
    texture: SoilTexture       # Soil texture classification
    structure: SoilStructure   # Soil structure type
    
    # Particle size distribution
    sand_percentage: float     # Sand content (2.0-0.05 mm)
    silt_percentage: float     # Silt content (0.05-0.002 mm)
    clay_percentage: float     # Clay content (<0.002 mm)
    
    # Physical characteristics
    bulk_density: float        # g/cm³, measure of compaction
    porosity: float           # Total pore space percentage
    macroporosity: float      # Large pores for drainage and aeration
    microporosity: float      # Small pores for water retention
    
    # Water characteristics
    field_capacity: float      # Water content at field capacity
    wilting_point: float      # Water content at permanent wilting point
    available_water_capacity: float  # Field capacity - wilting point
    saturated_hydraulic_conductivity: float  # Water movement rate
    
    # Temperature properties
    thermal_conductivity: float  # Heat transfer ability
    heat_capacity: float       # Heat storage ability
    
    # Compaction tracking
    compaction_level: float    # Current compaction (0.0-1.0)
    penetration_resistance: float  # Root penetration difficulty
    
    def calculate_water_retention(self, current_moisture: float) -> float:
        """Calculate how well soil retains water at current moisture level"""
        if current_moisture <= self.wilting_point:
            return 0.0  # No available water
        elif current_moisture >= self.field_capacity:
            return 1.0  # At maximum retention
        else:
            # Linear interpolation between wilting point and field capacity
            available_range = self.field_capacity - self.wilting_point
            current_available = current_moisture - self.wilting_point
            return current_available / available_range if available_range > 0 else 0.0

@dataclass
class SoilBiology:
    """Soil biological activity and health"""
    # Microbial biomass
    bacterial_biomass: float   # Bacterial population (mg C/kg soil)
    fungal_biomass: float     # Fungal population (mg C/kg soil)
    actinomycetes_biomass: float  # Actinomycetes population
    
    # Microbial activity
    respiration_rate: float    # CO2 evolution rate (μg C/g/h)
    enzyme_activity: float     # Overall enzyme activity index
    nitrogen_mineralization_rate: float  # N release from organic matter
    
    # Soil fauna
    earthworm_count: float     # Earthworms per m²
    arthropod_diversity: float # Arthropod diversity index
    nematode_count: float      # Beneficial nematodes per g soil
    
    # Biological health indicators
    mycorrhizal_colonization: float  # Root colonization percentage
    soil_food_web_stability: float   # Food web complexity index
    disease_suppression: float       # Natural disease suppression ability
    
    # Organic matter dynamics
    active_organic_matter: float     # Rapidly cycling organic matter
    stable_organic_matter: float     # Slowly cycling organic matter
    decomposition_rate: float        # Organic matter breakdown rate
    
    def calculate_biological_activity(self, temperature: float, moisture: float, 
                                    ph: float, organic_matter: float) -> float:
        """Calculate overall biological activity level"""
        # Temperature factor (optimal around 25-30°C)
        temp_factor = math.exp(-((temperature - 27.5) / 15.0) ** 2)
        
        # Moisture factor (optimal around 60-80% field capacity)
        optimal_moisture = 0.7
        moisture_factor = 1.0 - abs(moisture - optimal_moisture) / optimal_moisture
        moisture_factor = max(0.1, moisture_factor)
        
        # pH factor (optimal around 6.5-7.0)
        ph_factor = math.exp(-((ph - 6.75) / 2.0) ** 2)
        
        # Organic matter factor (more organic matter = more activity)
        om_factor = min(1.0, organic_matter / 0.05)  # Optimal at 5% OM
        
        # Combined biological activity
        activity = (temp_factor * moisture_factor * ph_factor * om_factor) ** 0.25
        return max(0.05, min(1.0, activity))

@dataclass
class SoilProfile:
    """Complete soil profile for a location"""
    location_id: str           # Grid location identifier
    
    # Soil composition
    chemistry: SoilChemistry   # Chemical properties
    physical: SoilPhysical     # Physical properties
    biology: SoilBiology       # Biological properties
    
    # Current conditions
    current_moisture: float    # Current soil moisture (0.0-1.0)
    current_temperature: float # Current soil temperature (°C)
    current_aeration: float    # Current soil aeration (0.0-1.0)
    
    # Management history
    last_tillage: Optional[datetime]  # Last tillage operation
    last_fertilizer: Optional[datetime]  # Last fertilizer application
    last_lime_application: Optional[datetime]  # Last lime application
    last_organic_addition: Optional[datetime]  # Last organic matter addition
    
    # Crop history
    crop_history: List[Dict[str, Any]]  # Past crops grown here
    cover_crop_periods: List[Dict[str, Any]]  # Cover crop periods
    fallow_periods: List[Dict[str, Any]]  # Fallow periods
    
    # Health tracking
    overall_health: SoilHealth # Current overall soil health
    health_trend: float        # Health trend (-1.0 to 1.0)
    degradation_risk: float    # Risk of soil degradation (0.0-1.0)
    
    # Erosion and conservation
    erosion_rate: float        # Current erosion rate (tons/acre/year)
    conservation_practices: List[str]  # Active conservation practices
    
    def calculate_overall_health(self) -> float:
        """Calculate overall soil health score (0.0-1.0)"""
        # Chemical health factors
        ph_score = 1.0 - abs(self.chemistry.ph - 6.75) / 3.75  # Optimal pH 6.75
        ph_score = max(0.0, min(1.0, ph_score))
        
        nutrient_score = 0.0
        nutrient_count = 0
        for nutrient_name in ['nitrogen', 'phosphorus', 'potassium']:
            nutrient = getattr(self.chemistry, nutrient_name)
            if nutrient.available_ppm > 0:
                # Score based on adequate availability
                score = min(1.0, nutrient.available_ppm / 50.0)  # Assuming 50 ppm is good
                nutrient_score += score
                nutrient_count += 1
        
        if nutrient_count > 0:
            nutrient_score /= nutrient_count
        
        # Physical health factors
        compaction_score = 1.0 - self.physical.compaction_level
        structure_scores = {
            SoilStructure.GRANULAR: 1.0,
            SoilStructure.BLOCKY: 0.8,
            SoilStructure.PRISMATIC: 0.6,
            SoilStructure.PLATY: 0.4,
            SoilStructure.MASSIVE: 0.2
        }
        structure_score = structure_scores.get(self.physical.structure, 0.5)
        
        # Biological health factors
        biological_activity = self.biology.calculate_biological_activity(
            self.current_temperature, self.current_moisture, 
            self.chemistry.ph, self.biology.active_organic_matter
        )
        
        organic_matter_score = min(1.0, (self.biology.active_organic_matter + 
                                        self.biology.stable_organic_matter) / 0.05)
        
        # Weighted overall health
        weights = {
            'chemical': 0.3,
            'physical': 0.3,
            'biological': 0.4
        }
        
        chemical_health = (ph_score + nutrient_score) / 2
        physical_health = (compaction_score + structure_score) / 2
        biological_health = (biological_activity + organic_matter_score) / 2
        
        overall_health = (chemical_health * weights['chemical'] +
                         physical_health * weights['physical'] +
                         biological_health * weights['biological'])
        
        return max(0.0, min(1.0, overall_health))

class SoilHealthSystem(System):
    """
    Soil Health System - Comprehensive soil science simulation
    
    This system manages realistic soil chemistry, physics, and biology
    with educational value and agricultural decision-making gameplay.
    """
    
    def __init__(self):
        """Initialize the Soil Health System"""
        super().__init__()
        self.system_name = "soil_health_system"
        
        # Core system references
        self.event_system: Optional[EventSystem] = None
        self.time_manager: Optional[TimeManager] = None
        self.config_manager: Optional[ConfigurationManager] = None
        self.content_registry: Optional[ContentRegistry] = None
        self.multicrop_framework: Optional[MultiCropFramework] = None
        self.growth_system: Optional[AdvancedGrowthSystem] = None
        
        # Soil profile management
        self.soil_profiles: Dict[str, SoilProfile] = {}
        self.nutrient_definitions: Dict[str, Dict[str, Any]] = {}
        self.crop_nutrient_requirements: Dict[str, Dict[str, float]] = {}
        
        # System parameters
        self.update_frequency = 6.0  # Update every 6 game hours
        self.last_update_time = 0.0
        self.simulation_precision = "detailed"  # Level of simulation detail
        
        # Environmental factors
        self.seasonal_modifiers: Dict[str, Dict[str, float]] = {}
        self.weather_effects: Dict[str, float] = {}
        
        # Educational content
        self.soil_education: Dict[str, str] = {}
        self.management_recommendations: Dict[str, List[str]] = {}
        
        logger.info("Soil Health System initialized")
    
    def initialize(self) -> bool:
        """Initialize the soil health system with required dependencies"""
        try:
            # Get system references
            from scripts.core.advanced_event_system import get_event_system
            from scripts.core.time_management import get_time_manager
            from scripts.core.advanced_config_system import get_config_manager
            from scripts.core.content_registry import get_content_registry
            
            self.event_system = get_event_system()
            self.time_manager = get_time_manager()
            self.config_manager = get_config_manager()
            self.content_registry = get_content_registry()
            
            # Load nutrient definitions
            self._load_nutrient_definitions()
            
            # Load crop requirements
            self._load_crop_nutrient_requirements()
            
            # Load educational content
            self._load_educational_content()
            
            # Subscribe to relevant events
            self._subscribe_to_events()
            
            # Load configuration
            self._load_configuration()
            
            logger.info("Soil Health System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Soil Health System: {e}")
            return False
    
    def _load_nutrient_definitions(self):
        """Load nutrient definitions from content registry"""
        try:
            # Load nutrient data from content registry
            nutrient_data = self.content_registry.get_content("soil_nutrients", {})
            
            for nutrient_id, data in nutrient_data.items():
                self.nutrient_definitions[nutrient_id] = data
            
            # Create default nutrient definitions if none loaded
            if not self.nutrient_definitions:
                self._create_default_nutrient_definitions()
            
            logger.info(f"Loaded {len(self.nutrient_definitions)} nutrient definitions")
            
        except Exception as e:
            logger.error(f"Failed to load nutrient definitions: {e}")
            self._create_default_nutrient_definitions()
    
    def _create_default_nutrient_definitions(self):
        """Create default nutrient definitions"""
        self.nutrient_definitions = {
            "nitrogen": {
                "symbol": "N",
                "name": "Nitrogen",
                "optimal_ppm": 50.0,
                "deficient_ppm": 15.0,
                "excessive_ppm": 150.0,
                "mobility": 0.9,
                "leaching_rate": 0.1,
                "ph_availability": {
                    5.0: 0.6, 5.5: 0.7, 6.0: 0.8, 6.5: 0.95, 
                    7.0: 1.0, 7.5: 0.95, 8.0: 0.8, 8.5: 0.6
                }
            },
            "phosphorus": {
                "symbol": "P",
                "name": "Phosphorus",
                "optimal_ppm": 30.0,
                "deficient_ppm": 10.0,
                "excessive_ppm": 100.0,
                "mobility": 0.2,
                "leaching_rate": 0.01,
                "ph_availability": {
                    5.0: 0.4, 5.5: 0.5, 6.0: 0.7, 6.5: 0.9, 
                    7.0: 1.0, 7.5: 0.8, 8.0: 0.5, 8.5: 0.3
                }
            },
            "potassium": {
                "symbol": "K",
                "name": "Potassium",
                "optimal_ppm": 200.0,
                "deficient_ppm": 80.0,
                "excessive_ppm": 500.0,
                "mobility": 0.6,
                "leaching_rate": 0.05,
                "ph_availability": {
                    5.0: 0.7, 5.5: 0.8, 6.0: 0.9, 6.5: 1.0, 
                    7.0: 1.0, 7.5: 0.9, 8.0: 0.8, 8.5: 0.7
                }
            }
        }
        logger.info("Created default nutrient definitions")
    
    def _load_crop_nutrient_requirements(self):
        """Load crop nutrient requirements"""
        try:
            # Load from content registry
            crop_data = self.content_registry.get_content("crop_nutrient_requirements", {})
            
            for crop_id, requirements in crop_data.items():
                self.crop_nutrient_requirements[crop_id] = requirements
            
            # Create defaults if none loaded
            if not self.crop_nutrient_requirements:
                self._create_default_crop_requirements()
            
            logger.info(f"Loaded nutrient requirements for {len(self.crop_nutrient_requirements)} crops")
            
        except Exception as e:
            logger.error(f"Failed to load crop requirements: {e}")
            self._create_default_crop_requirements()
    
    def _create_default_crop_requirements(self):
        """Create default crop nutrient requirements"""
        self.crop_nutrient_requirements = {
            "corn": {
                "nitrogen": 200.0,
                "phosphorus": 40.0,
                "potassium": 180.0,
                "sulfur": 20.0,
                "ph_range": (5.8, 7.0),
                "optimal_ph": 6.5
            },
            "soybeans": {
                "nitrogen": 100.0,  # Lower due to N fixation
                "phosphorus": 35.0,
                "potassium": 160.0,
                "sulfur": 15.0,
                "ph_range": (6.0, 7.0),
                "optimal_ph": 6.5
            },
            "wheat": {
                "nitrogen": 120.0,
                "phosphorus": 30.0,
                "potassium": 100.0,
                "sulfur": 15.0,
                "ph_range": (6.0, 7.5),
                "optimal_ph": 6.8
            }
        }
        logger.info("Created default crop nutrient requirements")
    
    def _load_educational_content(self):
        """Load educational content about soil health"""
        try:
            # Load soil education content
            education_data = self.content_registry.get_content("soil_education", {})
            self.soil_education.update(education_data)
            
            # Load management recommendations
            recommendations_data = self.content_registry.get_content("soil_management_tips", {})
            self.management_recommendations.update(recommendations_data)
            
            # Create defaults if none loaded
            if not self.soil_education:
                self._create_default_educational_content()
            
            logger.info("Loaded soil educational content successfully")
            
        except Exception as e:
            logger.warning(f"Could not load soil educational content: {e}")
            self._create_default_educational_content()
    
    def _create_default_educational_content(self):
        """Create default educational content"""
        self.soil_education = {
            "ph": "Soil pH affects nutrient availability. Most crops prefer slightly acidic to neutral soil (pH 6.0-7.0).",
            "nitrogen": "Nitrogen is essential for leaf growth and green color. Deficiency causes yellowing of older leaves.",
            "phosphorus": "Phosphorus promotes root development and flowering. Deficiency causes purple leaf coloration.",
            "potassium": "Potassium helps plants resist disease and drought. Deficiency causes brown leaf edges.",
            "organic_matter": "Organic matter improves soil structure, water retention, and nutrient availability."
        }
        
        self.management_recommendations = {
            "low_ph": ["Apply agricultural lime to raise pH", "Use wood ash in small amounts", "Avoid acidifying fertilizers"],
            "high_ph": ["Apply sulfur to lower pH", "Use acidifying fertilizers", "Add organic matter"],
            "low_nitrogen": ["Apply nitrogen fertilizer", "Plant nitrogen-fixing cover crops", "Add compost"],
            "compacted_soil": ["Perform deep tillage", "Add organic matter", "Avoid traffic on wet soil"]
        }
    
    def _subscribe_to_events(self):
        """Subscribe to relevant system events"""
        if self.event_system:
            # Time-based events
            self.event_system.subscribe("time_advanced", self._on_time_advanced)
            self.event_system.subscribe("day_changed", self._on_day_changed)
            self.event_system.subscribe("season_changed", self._on_season_changed)
            
            # Weather events
            self.event_system.subscribe("weather_updated", self._on_weather_updated)
            self.event_system.subscribe("precipitation_event", self._on_precipitation)
            
            # Agricultural events
            self.event_system.subscribe("fertilizer_applied", self._on_fertilizer_applied)
            self.event_system.subscribe("lime_applied", self._on_lime_applied)
            self.event_system.subscribe("organic_matter_added", self._on_organic_matter_added)
            self.event_system.subscribe("tillage_performed", self._on_tillage_performed)
            self.event_system.subscribe("crop_harvested", self._on_crop_harvested)
            self.event_system.subscribe("cover_crop_planted", self._on_cover_crop_planted)
    
    def _load_configuration(self):
        """Load system configuration parameters"""
        if self.config_manager:
            config = self.config_manager.get_config("soil_health_system", {})
            
            self.update_frequency = config.get("update_frequency", 6.0)
            self.simulation_precision = config.get("simulation_precision", "detailed")
    
    def create_soil_profile(self, location_id: str, base_texture: SoilTexture = SoilTexture.LOAM) -> SoilProfile:
        """Create a new soil profile for a location"""
        try:
            # Create default nutrients based on definitions
            nutrients = {}
            
            for nutrient_id, definition in self.nutrient_definitions.items():
                # Create pH availability curve
                ph_curve = definition.get("ph_availability", {
                    6.0: 0.8, 6.5: 0.9, 7.0: 1.0, 7.5: 0.9, 8.0: 0.8
                })
                
                nutrient = Nutrient(
                    symbol=definition["symbol"],
                    name=definition["name"],
                    current_ppm=definition.get("optimal_ppm", 50.0) * 0.7,  # Start at 70% of optimal
                    available_ppm=definition.get("optimal_ppm", 50.0) * 0.5,
                    organic_bound_ppm=definition.get("optimal_ppm", 50.0) * 0.3,
                    mineral_bound_ppm=definition.get("optimal_ppm", 50.0) * 0.2,
                    ph_availability_curve=ph_curve,
                    temperature_factor=1.0,
                    moisture_factor=1.0,
                    microbial_factor=1.0,
                    mobility=definition.get("mobility", 0.5),
                    leaching_rate=definition.get("leaching_rate", 0.05),
                    fixation_rate=definition.get("fixation_rate", 0.02)
                )
                nutrients[nutrient_id] = nutrient
            
            # Create soil chemistry
            chemistry = SoilChemistry(
                nitrogen=nutrients.get("nitrogen"),
                phosphorus=nutrients.get("phosphorus"),
                potassium=nutrients.get("potassium"),
                sulfur=nutrients.get("sulfur", self._create_default_nutrient("S", "Sulfur", 25.0)),
                calcium=nutrients.get("calcium", self._create_default_nutrient("Ca", "Calcium", 1500.0)),
                magnesium=nutrients.get("magnesium", self._create_default_nutrient("Mg", "Magnesium", 150.0)),
                iron=nutrients.get("iron", self._create_default_nutrient("Fe", "Iron", 10.0)),
                manganese=nutrients.get("manganese", self._create_default_nutrient("Mn", "Manganese", 5.0)),
                zinc=nutrients.get("zinc", self._create_default_nutrient("Zn", "Zinc", 2.0)),
                copper=nutrients.get("copper", self._create_default_nutrient("Cu", "Copper", 1.0)),
                boron=nutrients.get("boron", self._create_default_nutrient("B", "Boron", 0.5)),
                molybdenum=nutrients.get("molybdenum", self._create_default_nutrient("Mo", "Molybdenum", 0.1)),
                ph=6.5,  # Slightly acidic, good for most crops
                buffer_capacity=0.6,
                electrical_conductivity=0.8,
                sodium_percentage=3.0,
                cec=15.0,  # Good cation exchange capacity
                base_saturation=75.0
            )
            
            # Create physical properties based on texture
            physical = self._create_physical_properties(base_texture)
            
            # Create biological properties
            biology = SoilBiology(
                bacterial_biomass=300.0,
                fungal_biomass=200.0,
                actinomycetes_biomass=50.0,
                respiration_rate=2.5,
                enzyme_activity=0.6,
                nitrogen_mineralization_rate=0.03,
                earthworm_count=50.0,
                arthropod_diversity=0.7,
                nematode_count=100.0,
                mycorrhizal_colonization=30.0,
                soil_food_web_stability=0.6,
                disease_suppression=0.5,
                active_organic_matter=0.02,  # 2% active organic matter
                stable_organic_matter=0.03,  # 3% stable organic matter
                decomposition_rate=0.1
            )
            
            # Create soil profile
            profile = SoilProfile(
                location_id=location_id,
                chemistry=chemistry,
                physical=physical,
                biology=biology,
                current_moisture=0.6,  # 60% field capacity
                current_temperature=20.0,  # 20°C
                current_aeration=0.7,  # Good aeration
                last_tillage=None,
                last_fertilizer=None,
                last_lime_application=None,
                last_organic_addition=None,
                crop_history=[],
                cover_crop_periods=[],
                fallow_periods=[],
                overall_health=SoilHealth.GOOD,
                health_trend=0.0,
                degradation_risk=0.2,
                erosion_rate=1.0,  # tons/acre/year
                conservation_practices=[]
            )
            
            # Calculate initial health
            health_score = profile.calculate_overall_health()
            profile.overall_health = self._score_to_health_category(health_score)
            
            # Store profile
            self.soil_profiles[location_id] = profile
            
            # Publish soil profile created event
            if self.event_system:
                self.event_system.publish("soil_profile_created", {
                    "location_id": location_id,
                    "texture": base_texture.value,
                    "initial_health": profile.overall_health.value
                })
            
            logger.info(f"Created soil profile for location {location_id} with {base_texture.value} texture")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create soil profile for {location_id}: {e}")
            raise
    
    def _create_default_nutrient(self, symbol: str, name: str, optimal_ppm: float) -> Nutrient:
        """Create a default nutrient with standard properties"""
        return Nutrient(
            symbol=symbol,
            name=name,
            current_ppm=optimal_ppm * 0.7,
            available_ppm=optimal_ppm * 0.5,
            organic_bound_ppm=optimal_ppm * 0.3,
            mineral_bound_ppm=optimal_ppm * 0.2,
            ph_availability_curve={6.0: 0.8, 6.5: 0.9, 7.0: 1.0, 7.5: 0.9, 8.0: 0.8},
            temperature_factor=1.0,
            moisture_factor=1.0,
            microbial_factor=1.0,
            mobility=0.5,
            leaching_rate=0.05,
            fixation_rate=0.02
        )
    
    def _create_physical_properties(self, texture: SoilTexture) -> SoilPhysical:
        """Create physical properties based on soil texture"""
        # Define texture-specific properties
        texture_properties = {
            SoilTexture.SAND: {
                "sand": 85, "silt": 10, "clay": 5,
                "bulk_density": 1.6, "porosity": 40,
                "field_capacity": 0.15, "wilting_point": 0.05,
                "hydraulic_conductivity": 20.0
            },
            SoilTexture.LOAMY_SAND: {
                "sand": 75, "silt": 15, "clay": 10,
                "bulk_density": 1.5, "porosity": 43,
                "field_capacity": 0.20, "wilting_point": 0.08,
                "hydraulic_conductivity": 10.0
            },
            SoilTexture.SANDY_LOAM: {
                "sand": 65, "silt": 20, "clay": 15,
                "bulk_density": 1.4, "porosity": 47,
                "field_capacity": 0.25, "wilting_point": 0.12,
                "hydraulic_conductivity": 5.0
            },
            SoilTexture.LOAM: {
                "sand": 40, "silt": 40, "clay": 20,
                "bulk_density": 1.3, "porosity": 51,
                "field_capacity": 0.35, "wilting_point": 0.18,
                "hydraulic_conductivity": 2.5
            },
            SoilTexture.SILT_LOAM: {
                "sand": 20, "silt": 60, "clay": 20,
                "bulk_density": 1.2, "porosity": 55,
                "field_capacity": 0.40, "wilting_point": 0.22,
                "hydraulic_conductivity": 1.5
            },
            SoilTexture.CLAY_LOAM: {
                "sand": 30, "silt": 35, "clay": 35,
                "bulk_density": 1.1, "porosity": 58,
                "field_capacity": 0.45, "wilting_point": 0.28,
                "hydraulic_conductivity": 0.8
            },
            SoilTexture.CLAY: {
                "sand": 15, "silt": 25, "clay": 60,
                "bulk_density": 1.0, "porosity": 62,
                "field_capacity": 0.50, "wilting_point": 0.35,
                "hydraulic_conductivity": 0.3
            }
        }
        
        props = texture_properties.get(texture, texture_properties[SoilTexture.LOAM])
        
        return SoilPhysical(
            texture=texture,
            structure=SoilStructure.GRANULAR,  # Start with good structure
            sand_percentage=props["sand"],
            silt_percentage=props["silt"],
            clay_percentage=props["clay"],
            bulk_density=props["bulk_density"],
            porosity=props["porosity"],
            macroporosity=props["porosity"] * 0.4,  # 40% of total porosity
            microporosity=props["porosity"] * 0.6,  # 60% of total porosity
            field_capacity=props["field_capacity"],
            wilting_point=props["wilting_point"],
            available_water_capacity=props["field_capacity"] - props["wilting_point"],
            saturated_hydraulic_conductivity=props["hydraulic_conductivity"],
            thermal_conductivity=1.2,
            heat_capacity=2.0,
            compaction_level=0.2,  # Start with minimal compaction
            penetration_resistance=1.0
        )
    
    def _score_to_health_category(self, score: float) -> SoilHealth:
        """Convert numeric health score to health category"""
        if score >= 0.9:
            return SoilHealth.EXCELLENT
        elif score >= 0.75:
            return SoilHealth.GOOD
        elif score >= 0.6:
            return SoilHealth.FAIR
        elif score >= 0.4:
            return SoilHealth.POOR
        else:
            return SoilHealth.VERY_POOR
    
    def update(self, delta_time: float):
        """Update soil conditions for all profiles"""
        try:
            # Check if it's time for update
            current_time = self.time_manager.get_game_time_hours() if self.time_manager else 0.0
            if current_time - self.last_update_time < self.update_frequency:
                return
            
            self.last_update_time = current_time
            
            # Update each soil profile
            for location_id, profile in self.soil_profiles.items():
                self._update_soil_profile(profile, delta_time)
            
        except Exception as e:
            logger.error(f"Error updating soil health: {e}")
    
    def _update_soil_profile(self, profile: SoilProfile, delta_time: float):
        """Update a specific soil profile"""
        try:
            # Update nutrient availability based on current conditions
            self._update_nutrient_availability(profile)
            
            # Update biological activity
            self._update_biological_activity(profile)
            
            # Apply nutrient transformations
            self._apply_nutrient_transformations(profile, delta_time)
            
            # Update physical properties
            self._update_physical_properties(profile, delta_time)
            
            # Calculate new health score
            new_health_score = profile.calculate_overall_health()
            old_health = profile.overall_health
            profile.overall_health = self._score_to_health_category(new_health_score)
            
            # Update health trend
            if old_health != profile.overall_health:
                health_values = {
                    SoilHealth.VERY_POOR: 0.2,
                    SoilHealth.POOR: 0.4,
                    SoilHealth.FAIR: 0.6,
                    SoilHealth.GOOD: 0.8,
                    SoilHealth.EXCELLENT: 1.0
                }
                
                old_value = health_values[old_health]
                new_value = health_values[profile.overall_health]
                profile.health_trend = (new_value - old_value) * 0.1  # Smooth trend
            
            # Publish soil health update event
            if self.event_system:
                self.event_system.publish("soil_health_updated", {
                    "location_id": profile.location_id,
                    "health_score": new_health_score,
                    "health_category": profile.overall_health.value,
                    "health_trend": profile.health_trend
                })
            
        except Exception as e:
            logger.error(f"Error updating soil profile {profile.location_id}: {e}")
    
    def _update_nutrient_availability(self, profile: SoilProfile):
        """Update nutrient availability based on current conditions"""
        # Update availability for all nutrients
        nutrients = [
            profile.chemistry.nitrogen, profile.chemistry.phosphorus, profile.chemistry.potassium,
            profile.chemistry.sulfur, profile.chemistry.calcium, profile.chemistry.magnesium,
            profile.chemistry.iron, profile.chemistry.manganese, profile.chemistry.zinc,
            profile.chemistry.copper, profile.chemistry.boron, profile.chemistry.molybdenum
        ]
        
        # Calculate biological activity for microbial factor
        biological_activity = profile.biology.calculate_biological_activity(
            profile.current_temperature, profile.current_moisture,
            profile.chemistry.ph, profile.biology.active_organic_matter
        )
        
        for nutrient in nutrients:
            if nutrient:  # Check if nutrient exists
                nutrient.update_available_amount(
                    profile.chemistry.ph,
                    profile.current_temperature,
                    profile.current_moisture,
                    biological_activity
                )
    
    def _update_biological_activity(self, profile: SoilProfile):
        """Update soil biological activity"""
        biology = profile.biology
        
        # Calculate overall biological activity
        activity_level = biology.calculate_biological_activity(
            profile.current_temperature, profile.current_moisture,
            profile.chemistry.ph, biology.active_organic_matter
        )
        
        # Update microbial populations based on activity
        biology.bacterial_biomass *= (1.0 + (activity_level - 0.5) * 0.01)  # Small daily changes
        biology.fungal_biomass *= (1.0 + (activity_level - 0.5) * 0.008)
        
        # Update enzyme activity
        biology.enzyme_activity = activity_level
        
        # Update respiration rate
        biology.respiration_rate = activity_level * 3.0
        
        # Update nitrogen mineralization
        biology.nitrogen_mineralization_rate = activity_level * 0.05
        
        # Apply mineralization to nitrogen availability
        if profile.chemistry.nitrogen:
            mineralized_n = biology.active_organic_matter * biology.nitrogen_mineralization_rate
            profile.chemistry.nitrogen.current_ppm += mineralized_n * 1000  # Convert to ppm
            biology.active_organic_matter = max(0.0, biology.active_organic_matter - mineralized_n * 0.1)
    
    def _apply_nutrient_transformations(self, profile: SoilProfile, delta_time: float):
        """Apply nutrient transformations (leaching, fixation, etc.)"""
        # Calculate leaching based on drainage and nutrient mobility
        drainage_factor = profile.physical.saturated_hydraulic_conductivity / 10.0  # Normalize
        
        nutrients = [
            profile.chemistry.nitrogen, profile.chemistry.phosphorus, profile.chemistry.potassium
        ]
        
        for nutrient in nutrients:
            if nutrient:
                # Calculate leaching loss
                leaching_loss = (nutrient.current_ppm * nutrient.leaching_rate * 
                               drainage_factor * (delta_time / 24.0))  # Convert hours to days
                
                # Apply moisture factor (more leaching when wet)
                if profile.current_moisture > 0.8:
                    leaching_loss *= 2.0
                
                # Apply leaching loss
                nutrient.current_ppm = max(0.0, nutrient.current_ppm - leaching_loss)
                
                # Calculate fixation (conversion to unavailable forms)
                fixation_loss = nutrient.current_ppm * nutrient.fixation_rate * (delta_time / 24.0)
                nutrient.current_ppm = max(0.0, nutrient.current_ppm - fixation_loss)
                nutrient.mineral_bound_ppm += fixation_loss  # Move to mineral bound pool
    
    def _update_physical_properties(self, profile: SoilProfile, delta_time: float):
        """Update physical soil properties"""
        physical = profile.physical
        
        # Update compaction based on moisture and traffic (simplified)
        if profile.current_moisture > 0.8:  # Wet soil is more susceptible to compaction
            physical.compaction_level = min(1.0, physical.compaction_level + 0.001)
        
        # Improve structure over time with good management
        if profile.biology.earthworm_count > 30 and profile.biology.active_organic_matter > 0.02:
            if physical.structure != SoilStructure.GRANULAR:
                # Slowly improve structure
                pass  # Structure improvement logic would go here
        
        # Update bulk density based on compaction
        texture_base_density = {
            SoilTexture.SAND: 1.6,
            SoilTexture.LOAMY_SAND: 1.5,
            SoilTexture.SANDY_LOAM: 1.4,
            SoilTexture.LOAM: 1.3,
            SoilTexture.SILT_LOAM: 1.2,
            SoilTexture.CLAY_LOAM: 1.1,
            SoilTexture.CLAY: 1.0
        }
        
        base_density = texture_base_density.get(physical.texture, 1.3)
        physical.bulk_density = base_density * (1.0 + physical.compaction_level * 0.3)
        
        # Update porosity based on bulk density
        particle_density = 2.65  # g/cm³ for mineral soil
        physical.porosity = (1.0 - physical.bulk_density / particle_density) * 100
    
    # Event handlers
    def _on_time_advanced(self, event_data: Dict[str, Any]):
        """Handle time advancement"""
        delta_hours = event_data.get("delta_hours", 1.0)
        self.update(delta_hours)
    
    def _on_day_changed(self, event_data: Dict[str, Any]):
        """Handle day change events"""
        # Daily soil processing
        for profile in self.soil_profiles.values():
            # Update organic matter decomposition
            decomp_rate = profile.biology.decomposition_rate * profile.biology.calculate_biological_activity(
                profile.current_temperature, profile.current_moisture, 
                profile.chemistry.ph, profile.biology.active_organic_matter
            )
            
            # Decompose active organic matter
            daily_decomp = profile.biology.active_organic_matter * decomp_rate * 0.01
            profile.biology.active_organic_matter = max(0.0, profile.biology.active_organic_matter - daily_decomp)
            
            # Some active becomes stable
            profile.biology.stable_organic_matter += daily_decomp * 0.3
    
    def _on_season_changed(self, event_data: Dict[str, Any]):
        """Handle seasonal changes"""
        new_season = event_data.get("new_season")
        
        # Apply seasonal effects to all soil profiles
        for profile in self.soil_profiles.values():
            if new_season == "winter":
                # Reduce biological activity in winter
                profile.biology.bacterial_biomass *= 0.8
                profile.biology.fungal_biomass *= 0.9
            elif new_season == "spring":
                # Increase biological activity in spring
                profile.biology.bacterial_biomass *= 1.2
                profile.biology.fungal_biomass *= 1.1
    
    def _on_weather_updated(self, event_data: Dict[str, Any]):
        """Handle weather updates"""
        weather_data = event_data.get("weather_data", {})
        
        # Update soil temperature and moisture for all profiles
        for profile in self.soil_profiles.values():
            if "temperature" in weather_data:
                # Soil temperature lags air temperature
                air_temp = weather_data["temperature"]
                profile.current_temperature = profile.current_temperature * 0.9 + air_temp * 0.1
            
            if "precipitation" in weather_data:
                # Update soil moisture from precipitation
                precip = weather_data["precipitation"]
                moisture_increase = min(0.3, precip / 25.0)  # Max 30% increase from heavy rain
                profile.current_moisture = min(1.0, profile.current_moisture + moisture_increase)
    
    def _on_precipitation(self, event_data: Dict[str, Any]):
        """Handle precipitation events"""
        amount = event_data.get("amount", 0.0)
        locations = event_data.get("locations", [])
        
        # Apply precipitation to specific locations if specified
        if locations:
            for location_id in locations:
                if location_id in self.soil_profiles:
                    profile = self.soil_profiles[location_id]
                    moisture_increase = min(0.5, amount / 50.0)
                    profile.current_moisture = min(1.0, profile.current_moisture + moisture_increase)
        else:
            # Apply to all locations
            for profile in self.soil_profiles.values():
                moisture_increase = min(0.5, amount / 50.0)
                profile.current_moisture = min(1.0, profile.current_moisture + moisture_increase)
    
    def _on_fertilizer_applied(self, event_data: Dict[str, Any]):
        """Handle fertilizer application"""
        location_id = event_data.get("location_id")
        fertilizer_type = event_data.get("fertilizer_type", "balanced")
        amount = event_data.get("amount", 1.0)
        
        if location_id not in self.soil_profiles:
            return
        
        profile = self.soil_profiles[location_id]
        profile.last_fertilizer = self.time_manager.get_current_time() if self.time_manager else datetime.now()
        
        # Apply fertilizer based on type
        fertilizer_compositions = {
            "nitrogen": {"N": 100, "P": 0, "K": 0},
            "phosphorus": {"N": 0, "P": 100, "K": 0},
            "potassium": {"N": 0, "P": 0, "K": 100},
            "balanced": {"N": 33, "P": 33, "K": 33},
            "starter": {"N": 18, "P": 46, "K": 0},
            "complete": {"N": 20, "P": 20, "K": 20}
        }
        
        composition = fertilizer_compositions.get(fertilizer_type, fertilizer_compositions["balanced"])
        
        # Apply nutrients
        if profile.chemistry.nitrogen and "N" in composition:
            nutrient_addition = composition["N"] * amount
            profile.chemistry.nitrogen.current_ppm += nutrient_addition
        
        if profile.chemistry.phosphorus and "P" in composition:
            nutrient_addition = composition["P"] * amount
            profile.chemistry.phosphorus.current_ppm += nutrient_addition
        
        if profile.chemistry.potassium and "K" in composition:
            nutrient_addition = composition["K"] * amount
            profile.chemistry.potassium.current_ppm += nutrient_addition
        
        logger.info(f"Applied {fertilizer_type} fertilizer (amount: {amount}) to location {location_id}")
    
    def _on_lime_applied(self, event_data: Dict[str, Any]):
        """Handle lime application"""
        location_id = event_data.get("location_id")
        amount = event_data.get("amount", 1.0)
        
        if location_id not in self.soil_profiles:
            return
        
        profile = self.soil_profiles[location_id]
        profile.last_lime_application = self.time_manager.get_current_time() if self.time_manager else datetime.now()
        
        # Increase pH based on amount and buffer capacity
        ph_increase = amount * 0.5 * (1.0 - profile.chemistry.buffer_capacity)
        profile.chemistry.ph = min(8.5, profile.chemistry.ph + ph_increase)
        
        # Add calcium
        if profile.chemistry.calcium:
            profile.chemistry.calcium.current_ppm += amount * 500  # Lime adds calcium
        
        logger.info(f"Applied lime (amount: {amount}) to location {location_id}, pH increased to {profile.chemistry.ph:.2f}")
    
    def _on_organic_matter_added(self, event_data: Dict[str, Any]):
        """Handle organic matter addition"""
        location_id = event_data.get("location_id")
        organic_type = event_data.get("organic_type", "compost")
        amount = event_data.get("amount", 1.0)
        
        if location_id not in self.soil_profiles:
            return
        
        profile = self.soil_profiles[location_id]
        profile.last_organic_addition = self.time_manager.get_current_time() if self.time_manager else datetime.now()
        
        # Add organic matter
        if organic_type == "compost":
            profile.biology.active_organic_matter += amount * 0.01  # 1% per unit
            profile.biology.stable_organic_matter += amount * 0.005  # 0.5% per unit
        elif organic_type == "manure":
            profile.biology.active_organic_matter += amount * 0.015  # Higher active fraction
            # Manure also adds nutrients
            if profile.chemistry.nitrogen:
                profile.chemistry.nitrogen.organic_bound_ppm += amount * 20
        
        # Improve biological activity
        profile.biology.bacterial_biomass *= (1.0 + amount * 0.1)
        profile.biology.earthworm_count += amount * 10
        
        logger.info(f"Added {organic_type} (amount: {amount}) to location {location_id}")
    
    def _on_tillage_performed(self, event_data: Dict[str, Any]):
        """Handle tillage operations"""
        location_id = event_data.get("location_id")
        tillage_type = event_data.get("tillage_type", "conventional")
        
        if location_id not in self.soil_profiles:
            return
        
        profile = self.soil_profiles[location_id]
        profile.last_tillage = self.time_manager.get_current_time() if self.time_manager else datetime.now()
        
        if tillage_type == "deep_tillage":
            # Reduce compaction significantly
            profile.physical.compaction_level = max(0.0, profile.physical.compaction_level - 0.5)
            # But may damage soil structure
            if profile.physical.structure == SoilStructure.GRANULAR:
                profile.physical.structure = SoilStructure.BLOCKY
        elif tillage_type == "conventional":
            # Moderate compaction reduction
            profile.physical.compaction_level = max(0.0, profile.physical.compaction_level - 0.3)
        elif tillage_type == "minimum":
            # Small compaction reduction, preserves structure
            profile.physical.compaction_level = max(0.0, profile.physical.compaction_level - 0.1)
        
        # Tillage can temporarily increase organic matter decomposition
        profile.biology.decomposition_rate *= 1.2
        
        logger.info(f"Performed {tillage_type} tillage at location {location_id}")
    
    def _on_crop_harvested(self, event_data: Dict[str, Any]):
        """Handle crop harvest effects on soil"""
        location_id = event_data.get("location_id")
        crop_variety = event_data.get("variety_id", "unknown")
        
        if location_id not in self.soil_profiles:
            return
        
        profile = self.soil_profiles[location_id]
        
        # Add to crop history
        harvest_record = {
            "crop": crop_variety,
            "harvest_date": self.time_manager.get_current_time() if self.time_manager else datetime.now(),
            "location": location_id
        }
        profile.crop_history.append(harvest_record)
        
        # Crop removal affects nutrients
        if crop_variety in self.crop_nutrient_requirements:
            requirements = self.crop_nutrient_requirements[crop_variety]
            
            # Remove nutrients taken up by crop
            uptake_factor = 0.3  # Crop removes 30% of available nutrients
            
            if profile.chemistry.nitrogen:
                nitrogen_uptake = requirements.get("nitrogen", 0) * uptake_factor / 1000  # Convert to fraction
                profile.chemistry.nitrogen.current_ppm = max(0.0, 
                    profile.chemistry.nitrogen.current_ppm - nitrogen_uptake)
            
            if profile.chemistry.phosphorus:
                phosphorus_uptake = requirements.get("phosphorus", 0) * uptake_factor / 1000
                profile.chemistry.phosphorus.current_ppm = max(0.0, 
                    profile.chemistry.phosphorus.current_ppm - phosphorus_uptake)
            
            if profile.chemistry.potassium:
                potassium_uptake = requirements.get("potassium", 0) * uptake_factor / 1000
                profile.chemistry.potassium.current_ppm = max(0.0, 
                    profile.chemistry.potassium.current_ppm - potassium_uptake)
        
        # Add crop residue as organic matter
        residue_amount = 0.005  # 0.5% organic matter from residue
        profile.biology.active_organic_matter += residue_amount
        
        logger.info(f"Processed harvest effects for {crop_variety} at location {location_id}")
    
    def _on_cover_crop_planted(self, event_data: Dict[str, Any]):
        """Handle cover crop planting effects"""
        location_id = event_data.get("location_id")
        cover_crop_type = event_data.get("cover_crop_type", "grass")
        
        if location_id not in self.soil_profiles:
            return
        
        profile = self.soil_profiles[location_id]
        
        # Record cover crop period
        cover_crop_record = {
            "type": cover_crop_type,
            "start_date": self.time_manager.get_current_time() if self.time_manager else datetime.now(),
            "location": location_id
        }
        profile.cover_crop_periods.append(cover_crop_record)
        
        # Cover crops improve soil biology
        profile.biology.bacterial_biomass *= 1.1
        profile.biology.mycorrhizal_colonization += 5.0
        
        # Legume cover crops fix nitrogen
        if "legume" in cover_crop_type.lower() or "clover" in cover_crop_type.lower():
            if profile.chemistry.nitrogen:
                nitrogen_fixation = 20.0  # 20 ppm nitrogen fixed
                profile.chemistry.nitrogen.organic_bound_ppm += nitrogen_fixation
        
        logger.info(f"Planted {cover_crop_type} cover crop at location {location_id}")
    
    # Public interface methods
    def get_soil_profile(self, location_id: str) -> Optional[SoilProfile]:
        """Get soil profile for a location"""
        return self.soil_profiles.get(location_id)
    
    def get_soil_health_summary(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive soil health summary"""
        if location_id not in self.soil_profiles:
            return None
        
        profile = self.soil_profiles[location_id]
        
        return {
            "location_id": location_id,
            "overall_health": {
                "category": profile.overall_health.value,
                "score": profile.calculate_overall_health(),
                "trend": profile.health_trend
            },
            "chemistry": {
                "ph": profile.chemistry.ph,
                "ph_status": "optimal" if 6.0 <= profile.chemistry.ph <= 7.5 else "needs_adjustment",
                "nutrients": {
                    "nitrogen": {
                        "available_ppm": profile.chemistry.nitrogen.available_ppm if profile.chemistry.nitrogen else 0,
                        "status": self._get_nutrient_status(profile.chemistry.nitrogen, "nitrogen")
                    },
                    "phosphorus": {
                        "available_ppm": profile.chemistry.phosphorus.available_ppm if profile.chemistry.phosphorus else 0,
                        "status": self._get_nutrient_status(profile.chemistry.phosphorus, "phosphorus")
                    },
                    "potassium": {
                        "available_ppm": profile.chemistry.potassium.available_ppm if profile.chemistry.potassium else 0,
                        "status": self._get_nutrient_status(profile.chemistry.potassium, "potassium")
                    }
                },
                "cation_exchange_capacity": profile.chemistry.cec,
                "base_saturation": profile.chemistry.base_saturation
            },
            "physical": {
                "texture": profile.physical.texture.value,
                "structure": profile.physical.structure.value,
                "compaction_level": profile.physical.compaction_level,
                "water_capacity": profile.physical.available_water_capacity,
                "current_moisture": profile.current_moisture
            },
            "biology": {
                "organic_matter_total": profile.biology.active_organic_matter + profile.biology.stable_organic_matter,
                "biological_activity": profile.biology.calculate_biological_activity(
                    profile.current_temperature, profile.current_moisture,
                    profile.chemistry.ph, profile.biology.active_organic_matter
                ),
                "earthworm_count": profile.biology.earthworm_count,
                "mycorrhizal_colonization": profile.biology.mycorrhizal_colonization
            },
            "management": {
                "last_tillage": profile.last_tillage.isoformat() if profile.last_tillage else None,
                "last_fertilizer": profile.last_fertilizer.isoformat() if profile.last_fertilizer else None,
                "conservation_practices": profile.conservation_practices,
                "erosion_rate": profile.erosion_rate
            }
        }
    
    def _get_nutrient_status(self, nutrient: Optional[Nutrient], nutrient_type: str) -> str:
        """Get nutrient availability status"""
        if not nutrient or nutrient_type not in self.nutrient_definitions:
            return "unknown"
        
        definition = self.nutrient_definitions[nutrient_type]
        available = nutrient.available_ppm
        
        if available < definition.get("deficient_ppm", 0):
            return "deficient"
        elif available < definition.get("optimal_ppm", 50) * 0.5:
            return "low"
        elif available < definition.get("optimal_ppm", 50) * 1.5:
            return "adequate"
        elif available < definition.get("excessive_ppm", 200):
            return "high"
        else:
            return "excessive"
    
    def get_management_recommendations(self, location_id: str) -> List[str]:
        """Get management recommendations for a location"""
        if location_id not in self.soil_profiles:
            return []
        
        profile = self.soil_profiles[location_id]
        recommendations = []
        
        # pH recommendations
        if profile.chemistry.ph < 6.0:
            recommendations.extend(self.management_recommendations.get("low_ph", []))
        elif profile.chemistry.ph > 7.5:
            recommendations.extend(self.management_recommendations.get("high_ph", []))
        
        # Nutrient recommendations
        if profile.chemistry.nitrogen and profile.chemistry.nitrogen.available_ppm < 25:
            recommendations.extend(self.management_recommendations.get("low_nitrogen", []))
        
        # Physical recommendations
        if profile.physical.compaction_level > 0.6:
            recommendations.extend(self.management_recommendations.get("compacted_soil", []))
        
        # Organic matter recommendations
        total_om = profile.biology.active_organic_matter + profile.biology.stable_organic_matter
        if total_om < 0.03:  # Less than 3%
            recommendations.append("Add organic matter through compost or cover crops")
        
        return recommendations
    
    def test_soil_sample(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Simulate soil testing - returns detailed soil analysis"""
        if location_id not in self.soil_profiles:
            return None
        
        profile = self.soil_profiles[location_id]
        
        return {
            "location_id": location_id,
            "test_date": self.time_manager.get_current_time().isoformat() if self.time_manager else datetime.now().isoformat(),
            "laboratory_results": {
                "ph": round(profile.chemistry.ph, 1),
                "organic_matter_percent": round((profile.biology.active_organic_matter + 
                                               profile.biology.stable_organic_matter) * 100, 1),
                "nitrogen_ppm": round(profile.chemistry.nitrogen.available_ppm, 1) if profile.chemistry.nitrogen else 0,
                "phosphorus_ppm": round(profile.chemistry.phosphorus.available_ppm, 1) if profile.chemistry.phosphorus else 0,
                "potassium_ppm": round(profile.chemistry.potassium.available_ppm, 1) if profile.chemistry.potassium else 0,
                "cation_exchange_capacity": round(profile.chemistry.cec, 1),
                "base_saturation_percent": round(profile.chemistry.base_saturation, 1)
            },
            "interpretation": {
                "overall_fertility": profile.overall_health.value,
                "limiting_factors": self._identify_limiting_factors(profile),
                "recommendations": self.get_management_recommendations(location_id)
            },
            "cost": 50.0  # Cost of soil test
        }
    
    def _identify_limiting_factors(self, profile: SoilProfile) -> List[str]:
        """Identify factors limiting crop production"""
        limiting_factors = []
        
        # pH limitations
        if profile.chemistry.ph < 5.5:
            limiting_factors.append("Soil too acidic - lime needed")
        elif profile.chemistry.ph > 8.0:
            limiting_factors.append("Soil too alkaline - sulfur or organic matter needed")
        
        # Nutrient limitations
        if profile.chemistry.nitrogen and profile.chemistry.nitrogen.available_ppm < 20:
            limiting_factors.append("Nitrogen deficiency")
        
        if profile.chemistry.phosphorus and profile.chemistry.phosphorus.available_ppm < 15:
            limiting_factors.append("Phosphorus deficiency")
        
        if profile.chemistry.potassium and profile.chemistry.potassium.available_ppm < 100:
            limiting_factors.append("Potassium deficiency")
        
        # Physical limitations
        if profile.physical.compaction_level > 0.7:
            limiting_factors.append("Soil compaction limiting root growth")
        
        if profile.current_moisture < 0.3:
            limiting_factors.append("Insufficient soil moisture")
        
        # Biological limitations
        total_om = profile.biology.active_organic_matter + profile.biology.stable_organic_matter
        if total_om < 0.025:  # Less than 2.5%
            limiting_factors.append("Low organic matter")
        
        return limiting_factors
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status information"""
        return {
            "system_name": self.system_name,
            "soil_profiles": len(self.soil_profiles),
            "nutrient_definitions": len(self.nutrient_definitions),
            "crop_requirements": len(self.crop_nutrient_requirements),
            "update_frequency": self.update_frequency,
            "last_update": self.last_update_time,
            "simulation_precision": self.simulation_precision,
            "educational_content": {
                "soil_education_topics": len(self.soil_education),
                "management_recommendations": len(self.management_recommendations)
            },
            "health_distribution": {
                health.value: sum(1 for profile in self.soil_profiles.values() 
                                if profile.overall_health == health)
                for health in SoilHealth
            }
        }

# Global convenience functions for system access
_soil_health_system_instance = None

def get_soil_health_system() -> SoilHealthSystem:
    """Get the global Soil Health System instance"""
    global _soil_health_system_instance
    if _soil_health_system_instance is None:
        _soil_health_system_instance = SoilHealthSystem()
    return _soil_health_system_instance

def initialize_soil_health_system() -> bool:
    """Initialize the global Soil Health System"""
    system = get_soil_health_system()
    return system.initialize()

def create_soil_profile_for_location(location_id: str, texture: SoilTexture = SoilTexture.LOAM) -> SoilProfile:
    """Convenience function to create soil profile"""
    system = get_soil_health_system()
    return system.create_soil_profile(location_id, texture)

def get_soil_info(location_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get soil information"""
    system = get_soil_health_system()
    return system.get_soil_health_summary(location_id)

def test_soil(location_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to test soil"""
    system = get_soil_health_system()
    return system.test_soil_sample(location_id)

def get_soil_recommendations(location_id: str) -> List[str]:
    """Convenience function to get management recommendations"""
    system = get_soil_health_system()
    return system.get_management_recommendations(location_id)