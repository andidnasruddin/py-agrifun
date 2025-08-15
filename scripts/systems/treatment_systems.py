"""
Treatment Systems - Pesticide Application & Resistance Management for AgriFun Agricultural Simulation

This system provides comprehensive treatment application management including spray equipment,
pesticide formulations, application timing optimization, resistance management, and regulatory
compliance. Integrates with Disease Framework, Pest Framework, and IPM systems to provide
realistic agricultural chemical management.

Key Features:
- Spray Equipment System: Boom sprayers, airblast sprayers, granule applicators
- Pesticide Formulation Management: Active ingredients, adjuvants, tank mixing
- Application Timing Optimization: Weather windows, crop growth stages, pest thresholds
- Resistance Management: Mode of action rotation, resistance monitoring
- Regulatory Compliance: PHI tracking, MRL compliance, application records
- Economic Analysis: Treatment cost analysis and ROI calculations
- Environmental Impact: Drift modeling, beneficial impact assessment

Educational Value:
- Proper pesticide selection and application techniques
- Understanding of resistance management principles
- Regulatory compliance and record-keeping requirements
- Environmental stewardship and IPM integration
- Equipment calibration and maintenance procedures
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
import yaml


class EquipmentType(Enum):
    """Types of pesticide application equipment"""
    BOOM_SPRAYER = "boom_sprayer"           # Field crop spraying
    AIRBLAST_SPRAYER = "airblast_sprayer"   # Orchard/vineyard spraying
    BACKPACK_SPRAYER = "backpack_sprayer"   # Small area/spot treatment
    GRANULE_APPLICATOR = "granule_applicator" # Granular pesticide application
    SEED_TREATER = "seed_treater"           # Seed treatment equipment
    SOIL_INJECTOR = "soil_injector"         # Soil fumigation equipment
    ULV_SPRAYER = "ulv_sprayer"            # Ultra-low volume application
    ELECTROSTATIC_SPRAYER = "electrostatic_sprayer" # Charged droplet application


class ApplicationMethod(Enum):
    """Methods of pesticide application"""
    FOLIAR_SPRAY = "foliar_spray"           # Leaf surface application
    SOIL_APPLICATION = "soil_application"    # Soil-applied pesticide
    SEED_TREATMENT = "seed_treatment"        # Pre-plant seed treatment
    GRANULAR_BROADCAST = "granular_broadcast" # Granular surface application
    BANDED_APPLICATION = "banded_application" # Row or band application
    SPOT_TREATMENT = "spot_treatment"        # Targeted small area treatment
    SYSTEMIC_DRENCH = "systemic_drench"     # Root zone application
    FUMIGATION = "fumigation"               # Gas-phase application


class ModeOfAction(Enum):
    """IRAC/FRAC mode of action classifications"""
    # Insecticides (IRAC)
    ACETYLCHOLINE_ESTERASE = "irac_1"       # Organophosphates, carbamates
    GABA_GATED_CHLORIDE = "irac_2"          # Cyclodiene, phenylpyrazole
    SODIUM_CHANNEL_MODULATORS = "irac_3"     # Pyrethroids, DDT
    NICOTINIC_ACETYLCHOLINE = "irac_4"      # Neonicotinoids
    GLUTAMATE_GATED_CHLORIDE = "irac_6"     # Avermectins, milbemycins
    JUVENILE_HORMONE_MIMICS = "irac_7"       # IGRs
    CHITIN_BIOSYNTHESIS = "irac_15"         # Benzoylureas
    
    # Fungicides (FRAC)
    QOI_STROBILURINS = "frac_11"            # Strobilurin fungicides
    DMI_TRIAZOLES = "frac_3"                # Triazole fungicides
    SDHI_SUCCINATE = "frac_7"               # Succinate dehydrogenase inhibitors
    MULTI_SITE_CONTACT = "frac_m"           # Multi-site contact fungicides
    
    # Herbicides (HRAC)
    ALS_INHIBITORS = "hrac_2"               # Sulfonylureas, imidazolinones
    PHOTOSYSTEM_II = "hrac_5"               # Atrazine, simazine
    EPSP_SYNTHASE = "hrac_9"                # Glyphosate
    AUXIN_MIMICS = "hrac_4"                 # 2,4-D, dicamba


class ResistanceRisk(Enum):
    """Risk levels for resistance development"""
    LOW = "low"                             # Multi-site modes of action
    MEDIUM = "medium"                       # Some documented resistance
    HIGH = "high"                           # Single-site, high selection pressure
    CRITICAL = "critical"                   # Widespread resistance documented


class WeatherSuitability(Enum):
    """Weather conditions for application"""
    EXCELLENT = "excellent"                 # Ideal conditions
    GOOD = "good"                          # Acceptable conditions
    MARGINAL = "marginal"                  # Borderline conditions
    POOR = "poor"                          # Not recommended
    PROHIBITED = "prohibited"              # Unsafe/illegal conditions


@dataclass
class ActiveIngredient:
    """Individual pesticide active ingredient"""
    ai_id: str
    common_name: str
    chemical_name: str
    cas_number: str
    mode_of_action: ModeOfAction
    resistance_risk: ResistanceRisk
    
    # Regulatory information
    epa_registration: str
    maximum_residue_limit: float  # mg/kg
    pre_harvest_interval: int     # days
    restricted_entry_interval: int # hours
    
    # Application parameters
    application_rate_range: Tuple[float, float]  # kg/ha or L/ha
    water_carrier_rate: Tuple[float, float]      # L/ha
    compatible_adjuvants: List[str]
    
    # Environmental fate
    soil_half_life_days: float
    water_solubility: float      # mg/L
    vapor_pressure: float        # Pa
    bioaccumulation_factor: float
    
    # Toxicity information
    oral_ld50_rat: float         # mg/kg
    dermal_ld50_rat: float      # mg/kg
    bee_toxicity: str           # "low", "medium", "high"
    fish_toxicity: str          # "low", "medium", "high"
    

@dataclass
class PesticideFormulation:
    """Complete pesticide product formulation"""
    formulation_id: str
    product_name: str
    manufacturer: str
    active_ingredients: List[Tuple[str, float]]  # [(ai_id, concentration%), ...]
    formulation_type: str    # EC, WP, WG, SC, etc.
    
    # Physical properties
    density: float           # kg/L
    ph_range: Tuple[float, float]
    viscosity: float        # cP
    particle_size: Optional[float] # microns (for WP, WG)
    
    # Application properties
    recommended_rate: float  # L/ha or kg/ha
    water_rate: float       # L/ha
    adjuvant_required: bool
    tank_mix_compatible: List[str] # Compatible formulation IDs
    
    # Storage and handling
    shelf_life_months: int
    storage_temperature_range: Tuple[float, float] # °C
    special_handling: List[str]


@dataclass
class SprayEquipment:
    """Pesticide application equipment specifications"""
    equipment_id: str
    equipment_name: str
    equipment_type: EquipmentType
    manufacturer: str
    
    # Performance specifications
    tank_capacity: float     # L
    working_width: float     # m
    operating_pressure_range: Tuple[float, float] # bar
    flow_rate_range: Tuple[float, float]  # L/min
    droplet_size_range: Tuple[int, int]   # microns (VMD)
    
    # Power requirements
    power_requirement_hp: float
    hydraulic_flow_required: float # L/min
    pto_speed_rpm: int
    
    # Calibration data
    nozzle_type: str
    nozzle_count: int
    orifice_size: str
    boom_height_range: Tuple[float, float] # m
    
    # Economic data
    purchase_price: float
    annual_maintenance_cost: float
    calibration_interval_hours: int
    replacement_interval_years: int
    
    # Performance factors
    coverage_quality: float  # 0.0-1.0
    drift_potential: float   # 0.0-1.0 (higher = more drift)
    application_efficiency: float # 0.0-1.0
    

@dataclass
class ApplicationRecord:
    """Individual pesticide application record"""
    record_id: str
    application_date: datetime
    location_id: str
    field_area_treated: float # ha
    
    # Product information
    formulation_used: str
    rate_applied: float      # L/ha or kg/ha
    water_volume: float      # L/ha
    adjuvants_used: List[Tuple[str, float]] # [(adjuvant, rate), ...]
    
    # Equipment and conditions
    equipment_used: str
    operator_name: str
    weather_conditions: Dict[str, Any]
    application_start_time: datetime
    application_end_time: datetime
    
    # Regulatory compliance
    pre_harvest_interval_respected: bool
    restricted_entry_posted: bool
    buffer_zones_observed: bool
    drift_mitigation_measures: List[str]
    
    # Target information
    target_pests: List[str]
    growth_stage_at_application: str
    pest_pressure_level: str
    
    # Economic data
    material_cost: float
    application_cost: float
    total_treatment_cost: float


@dataclass
class ResistanceMonitoringData:
    """Resistance monitoring and management data"""
    monitoring_id: str
    location_id: str
    pest_species: str
    monitoring_date: datetime
    
    # Resistance testing results
    baseline_mortality: float    # 0.0-1.0
    current_mortality: float     # 0.0-1.0
    resistance_ratio: float      # Current LC50 / Susceptible LC50
    resistance_classification: str # "S", "R", "HR" (Susceptible, Resistant, Highly Resistant)
    
    # Mode of action usage history
    moa_usage_history: Dict[str, List[datetime]]  # {moa_id: [application_dates]}
    consecutive_applications_same_moa: int
    season_applications_same_moa: int
    
    # Resistance risk assessment
    resistance_risk_score: float # 0.0-1.0
    recommended_actions: List[str]
    alternative_modes_available: List[str]
    

class TreatmentSystems:
    """
    Comprehensive Treatment Systems for pesticide application management
    
    This system coordinates all aspects of pesticide treatment including equipment
    selection, product formulation, application timing, resistance management,
    and regulatory compliance.
    """
    
    def __init__(self, config_manager=None, event_system=None):
        """Initialize treatment systems"""
        self.config_manager = config_manager
        self.event_system = event_system
        self.logger = logging.getLogger(__name__)
        
        # System state
        self.active_ingredients: Dict[str, ActiveIngredient] = {}
        self.formulations: Dict[str, PesticideFormulation] = {}
        self.spray_equipment: Dict[str, SprayEquipment] = {}
        self.application_records: List[ApplicationRecord] = []
        self.resistance_monitoring: Dict[str, ResistanceMonitoringData] = {}
        
        # Equipment fleet management
        self.owned_equipment: Set[str] = set()
        self.equipment_status: Dict[str, str] = {}  # "available", "in_use", "maintenance"
        self.maintenance_schedules: Dict[str, datetime] = {}
        
        # Application planning
        self.scheduled_applications: List[Dict[str, Any]] = []
        self.weather_windows: List[Dict[str, Any]] = []
        
        # Resistance management
        self.moa_rotation_rules: Dict[str, Dict[str, Any]] = {}
        self.resistance_alerts: List[Dict[str, Any]] = []
        
        # Regulatory tracking
        self.phi_tracking: Dict[str, List[Tuple[datetime, int]]] = {}  # {location_id: [(app_date, phi_days)]}
        self.rei_violations: List[Dict[str, Any]] = []
        
        # Performance metrics
        self.application_efficiency_history: List[Dict[str, Any]] = []
        self.cost_analysis_data: List[Dict[str, Any]] = []
        
        # Initialize system
        self._initialize_treatment_systems()
        
    def _initialize_treatment_systems(self):
        """Initialize treatment systems with default data"""
        try:
            self._load_active_ingredients()
            self._load_formulations()
            self._load_spray_equipment()
            self._setup_resistance_management()
            self._setup_weather_monitoring()
            
            if self.event_system:
                self._subscribe_to_events()
                
            self.logger.info("Treatment Systems initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing treatment systems: {e}")
            # Initialize with minimal default configuration
            self._create_default_configuration()
    
    def _load_active_ingredients(self):
        """Load active ingredient database"""
        # Create comprehensive active ingredient database
        ai_data = [
            # Insecticides
            {
                "ai_id": "chlorpyrifos",
                "common_name": "Chlorpyrifos",
                "chemical_name": "O,O-diethyl O-3,5,6-trichloro-2-pyridinyl phosphorothioate",
                "cas_number": "2921-88-2",
                "mode_of_action": ModeOfAction.ACETYLCHOLINE_ESTERASE,
                "resistance_risk": ResistanceRisk.MEDIUM,
                "epa_registration": "62719-527",
                "maximum_residue_limit": 0.05,
                "pre_harvest_interval": 14,
                "restricted_entry_interval": 24,
                "application_rate_range": (0.56, 1.12),
                "water_carrier_rate": (140, 280),
                "compatible_adjuvants": ["crop_oil", "methylated_seed_oil"],
                "soil_half_life_days": 60,
                "water_solubility": 0.73,
                "vapor_pressure": 0.00187,
                "bioaccumulation_factor": 5100,
                "oral_ld50_rat": 96,
                "dermal_ld50_rat": 2000,
                "bee_toxicity": "high",
                "fish_toxicity": "high"
            },
            {
                "ai_id": "bifenthrin",
                "common_name": "Bifenthrin",
                "chemical_name": "(2-methyl-3-phenylphenyl)methyl (1S,3S)-3-[(Z)-2-chloro-3,3,3-trifluoro-1-propenyl]-2,2-dimethylcyclopropanecarboxylate",
                "cas_number": "82657-04-3",
                "mode_of_action": ModeOfAction.SODIUM_CHANNEL_MODULATORS,
                "resistance_risk": ResistanceRisk.HIGH,
                "epa_registration": "279-3206",
                "maximum_residue_limit": 0.01,
                "pre_harvest_interval": 7,
                "restricted_entry_interval": 12,
                "application_rate_range": (0.05, 0.1),
                "water_carrier_rate": (140, 280),
                "compatible_adjuvants": ["nonionic_surfactant", "crop_oil"],
                "soil_half_life_days": 82,
                "water_solubility": 0.1,
                "vapor_pressure": 0.000016,
                "bioaccumulation_factor": 236000,
                "oral_ld50_rat": 54,
                "dermal_ld50_rat": 2000,
                "bee_toxicity": "high",
                "fish_toxicity": "high"
            },
            {
                "ai_id": "imidacloprid",
                "common_name": "Imidacloprid",
                "chemical_name": "1-[(6-chloro-3-pyridinyl)methyl]-N-nitro-2-imidazolidinamine",
                "cas_number": "138261-41-3",
                "mode_of_action": ModeOfAction.NICOTINIC_ACETYLCHOLINE,
                "resistance_risk": ResistanceRisk.HIGH,
                "epa_registration": "264-827",
                "maximum_residue_limit": 0.5,
                "pre_harvest_interval": 21,
                "restricted_entry_interval": 12,
                "application_rate_range": (0.044, 0.175),
                "water_carrier_rate": (140, 280),
                "compatible_adjuvants": ["nonionic_surfactant", "penetrant"],
                "soil_half_life_days": 191,
                "water_solubility": 610,
                "vapor_pressure": 0.0000004,
                "bioaccumulation_factor": 12,
                "oral_ld50_rat": 425,
                "dermal_ld50_rat": 5000,
                "bee_toxicity": "high",
                "fish_toxicity": "medium"
            },
            
            # Fungicides
            {
                "ai_id": "tebuconazole",
                "common_name": "Tebuconazole",
                "chemical_name": "1-(4-chlorophenyl)-4,4-dimethyl-3-(1H-1,2,4-triazol-1-ylmethyl)pentan-3-ol",
                "cas_number": "107534-96-3",
                "mode_of_action": ModeOfAction.DMI_TRIAZOLES,
                "resistance_risk": ResistanceRisk.HIGH,
                "epa_registration": "264-1025",
                "maximum_residue_limit": 0.2,
                "pre_harvest_interval": 30,
                "restricted_entry_interval": 12,
                "application_rate_range": (0.25, 0.5),
                "water_carrier_rate": (140, 280),
                "compatible_adjuvants": ["nonionic_surfactant", "penetrant"],
                "soil_half_life_days": 63,
                "water_solubility": 36,
                "vapor_pressure": 0.00000013,
                "bioaccumulation_factor": 363,
                "oral_ld50_rat": 1700,
                "dermal_ld50_rat": 2000,
                "bee_toxicity": "low",
                "fish_toxicity": "medium"
            },
            {
                "ai_id": "azoxystrobin",
                "common_name": "Azoxystrobin",
                "chemical_name": "methyl (E)-2-[2-[6-(2-cyanophenoxy)pyrimidin-4-yloxy]phenyl]-3-methoxyacrylate",
                "cas_number": "131860-33-8",
                "mode_of_action": ModeOfAction.QOI_STROBILURINS,
                "resistance_risk": ResistanceRisk.HIGH,
                "epa_registration": "100-1098",
                "maximum_residue_limit": 2.0,
                "pre_harvest_interval": 0,
                "restricted_entry_interval": 4,
                "application_rate_range": (0.15, 0.25),
                "water_carrier_rate": (140, 280),
                "compatible_adjuvants": ["nonionic_surfactant", "penetrant"],
                "soil_half_life_days": 71,
                "water_solubility": 6.7,
                "vapor_pressure": 0.00000011,
                "bioaccumulation_factor": 49,
                "oral_ld50_rat": 5000,
                "dermal_ld50_rat": 2000,
                "bee_toxicity": "medium",
                "fish_toxicity": "high"
            },
            
            # Herbicides
            {
                "ai_id": "glyphosate",
                "common_name": "Glyphosate",
                "chemical_name": "N-(phosphonomethyl)glycine",
                "cas_number": "1071-83-6",
                "mode_of_action": ModeOfAction.EPSP_SYNTHASE,
                "resistance_risk": ResistanceRisk.HIGH,
                "epa_registration": "524-308",
                "maximum_residue_limit": 0.2,
                "pre_harvest_interval": 7,
                "restricted_entry_interval": 4,
                "application_rate_range": (0.84, 3.36),
                "water_carrier_rate": (140, 280),
                "compatible_adjuvants": ["ams", "surfactant"],
                "soil_half_life_days": 32,
                "water_solubility": 12000,
                "vapor_pressure": 0.000000013,
                "bioaccumulation_factor": 2,
                "oral_ld50_rat": 5600,
                "dermal_ld50_rat": 5000,
                "bee_toxicity": "low",
                "fish_toxicity": "medium"
            },
            {
                "ai_id": "atrazine",
                "common_name": "Atrazine",
                "chemical_name": "6-chloro-N-ethyl-N'-(1-methylethyl)-1,3,5-triazine-2,4-diamine",
                "cas_number": "1912-24-9",
                "mode_of_action": ModeOfAction.PHOTOSYSTEM_II,
                "resistance_risk": ResistanceRisk.HIGH,
                "epa_registration": "100-497",
                "maximum_residue_limit": 0.02,
                "pre_harvest_interval": 21,
                "restricted_entry_interval": 12,
                "application_rate_range": (1.12, 2.24),
                "water_carrier_rate": (140, 280),
                "compatible_adjuvants": ["crop_oil", "nonionic_surfactant"],
                "soil_half_life_days": 60,
                "water_solubility": 35,
                "vapor_pressure": 0.000039,
                "bioaccumulation_factor": 3.2,
                "oral_ld50_rat": 1869,
                "dermal_ld50_rat": 7500,
                "bee_toxicity": "low",
                "fish_toxicity": "medium"
            }
        ]
        
        # Convert to ActiveIngredient objects
        for ai_dict in ai_data:
            ai = ActiveIngredient(**ai_dict)
            self.active_ingredients[ai.ai_id] = ai
            
        self.logger.info(f"Loaded {len(self.active_ingredients)} active ingredients")
    
    def _load_formulations(self):
        """Load pesticide formulation database"""
        # Create comprehensive formulation database
        formulation_data = [
            {
                "formulation_id": "lorsban_advanced",
                "product_name": "Lorsban Advanced",
                "manufacturer": "Corteva",
                "active_ingredients": [("chlorpyrifos", 42.4)],
                "formulation_type": "EC",
                "density": 1.18,
                "ph_range": (5.0, 7.0),
                "viscosity": 15.2,
                "particle_size": None,
                "recommended_rate": 2.6,
                "water_rate": 140,
                "adjuvant_required": False,
                "tank_mix_compatible": ["bifenthrin_fc", "tebuconazole_sc"],
                "shelf_life_months": 24,
                "storage_temperature_range": (0, 35),
                "special_handling": ["personal_protective_equipment", "restricted_entry_interval"]
            },
            {
                "formulation_id": "brigade_2ec",
                "product_name": "Brigade 2EC",
                "manufacturer": "FMC",
                "active_ingredients": [("bifenthrin", 22.6)],
                "formulation_type": "EC",
                "density": 0.86,
                "ph_range": (5.5, 7.5),
                "viscosity": 5.1,
                "particle_size": None,
                "recommended_rate": 0.46,
                "water_rate": 140,
                "adjuvant_required": True,
                "tank_mix_compatible": ["tebuconazole_sc", "azoxystrobin_sc"],
                "shelf_life_months": 36,
                "storage_temperature_range": (-10, 40),
                "special_handling": ["restricted_use_pesticide", "aquatic_buffer"]
            },
            {
                "formulation_id": "admire_pro",
                "product_name": "Admire Pro",
                "manufacturer": "Bayer",
                "active_ingredients": [("imidacloprid", 42.8)],
                "formulation_type": "SC",
                "density": 1.26,
                "ph_range": (4.0, 8.0),
                "viscosity": 150,
                "particle_size": None,
                "recommended_rate": 0.41,
                "water_rate": 140,
                "adjuvant_required": False,
                "tank_mix_compatible": ["tebuconazole_sc", "chlorpyrifos_ec"],
                "shelf_life_months": 24,
                "storage_temperature_range": (0, 35),
                "special_handling": ["pollinator_protection", "soil_application_preferred"]
            },
            {
                "formulation_id": "folicur_3_6f",
                "product_name": "Folicur 3.6F",
                "manufacturer": "Bayer",
                "active_ingredients": [("tebuconazole", 38.7)],
                "formulation_type": "SC",
                "density": 1.11,
                "ph_range": (4.5, 8.5),
                "viscosity": 85,
                "particle_size": None,
                "recommended_rate": 0.73,
                "water_rate": 140,
                "adjuvant_required": False,
                "tank_mix_compatible": ["azoxystrobin_sc", "chlorpyrifos_ec", "bifenthrin_ec"],
                "shelf_life_months": 36,
                "storage_temperature_range": (-5, 35),
                "special_handling": ["avoid_drift_to_water", "resistance_management"]
            },
            {
                "formulation_id": "quadris",
                "product_name": "Quadris",
                "manufacturer": "Syngenta",
                "active_ingredients": [("azoxystrobin", 22.9)],
                "formulation_type": "SC",
                "density": 1.11,
                "ph_range": (4.0, 9.0),
                "viscosity": 45,
                "particle_size": None,
                "recommended_rate": 1.09,
                "water_rate": 140,
                "adjuvant_required": True,
                "tank_mix_compatible": ["tebuconazole_sc", "bifenthrin_ec"],
                "shelf_life_months": 24,
                "storage_temperature_range": (0, 35),
                "special_handling": ["resistance_management", "maximum_applications_limit"]
            },
            {
                "formulation_id": "roundup_powermax",
                "product_name": "Roundup PowerMAX",
                "manufacturer": "Bayer",
                "active_ingredients": [("glyphosate", 48.7)],
                "formulation_type": "SL",
                "density": 1.21,
                "ph_range": (4.5, 5.5),
                "viscosity": 12,
                "particle_size": None,
                "recommended_rate": 3.51,
                "water_rate": 140,
                "adjuvant_required": False,
                "tank_mix_compatible": ["atrazine_wg", "bifenthrin_ec"],
                "shelf_life_months": 60,
                "storage_temperature_range": (-10, 40),
                "special_handling": ["resistance_management", "drift_reduction_agent"]
            },
            {
                "formulation_id": "aatrex_4l",
                "product_name": "AAtrex 4L",
                "manufacturer": "Syngenta",
                "active_ingredients": [("atrazine", 42.2)],
                "formulation_type": "SC",
                "density": 1.15,
                "ph_range": (6.0, 8.0),
                "viscosity": 25,
                "particle_size": None,
                "recommended_rate": 5.26,
                "water_rate": 140,
                "adjuvant_required": False,
                "tank_mix_compatible": ["glyphosate_sl", "chlorpyrifos_ec"],
                "shelf_life_months": 36,
                "storage_temperature_range": (-5, 35),
                "special_handling": ["groundwater_advisory", "resistance_management"]
            }
        ]
        
        # Convert to PesticideFormulation objects
        for form_dict in formulation_data:
            formulation = PesticideFormulation(**form_dict)
            self.formulations[formulation.formulation_id] = formulation
            
        self.logger.info(f"Loaded {len(self.formulations)} pesticide formulations")
    
    def _load_spray_equipment(self):
        """Load spray equipment database"""
        equipment_data = [
            {
                "equipment_id": "apache_as1220",
                "equipment_name": "Apache AS1220 Field Sprayer",
                "equipment_type": EquipmentType.BOOM_SPRAYER,
                "manufacturer": "Equipment Technologies",
                "tank_capacity": 4542,
                "working_width": 36.6,
                "operating_pressure_range": (1.4, 5.5),
                "flow_rate_range": (189, 757),
                "droplet_size_range": (150, 450),
                "power_requirement_hp": 120,
                "hydraulic_flow_required": 83,
                "pto_speed_rpm": 540,
                "nozzle_type": "TeeJet AIXR",
                "nozzle_count": 122,
                "orifice_size": "11004",
                "boom_height_range": (0.5, 1.2),
                "purchase_price": 285000,
                "annual_maintenance_cost": 8550,
                "calibration_interval_hours": 100,
                "replacement_interval_years": 15,
                "coverage_quality": 0.92,
                "drift_potential": 0.25,
                "application_efficiency": 0.94
            },
            {
                "equipment_id": "hardi_commander",
                "equipment_name": "Hardi Commander 4400",
                "equipment_type": EquipmentType.BOOM_SPRAYER,
                "manufacturer": "Hardi",
                "tank_capacity": 4400,
                "working_width": 28.0,
                "operating_pressure_range": (1.0, 8.0),
                "flow_rate_range": (140, 560),
                "droplet_size_range": (100, 500),
                "power_requirement_hp": 100,
                "hydraulic_flow_required": 75,
                "pto_speed_rpm": 540,
                "nozzle_type": "Hardi ISO",
                "nozzle_count": 112,
                "orifice_size": "03",
                "boom_height_range": (0.4, 1.5),
                "purchase_price": 195000,
                "annual_maintenance_cost": 5850,
                "calibration_interval_hours": 120,
                "replacement_interval_years": 12,
                "coverage_quality": 0.89,
                "drift_potential": 0.30,
                "application_efficiency": 0.91
            },
            {
                "equipment_id": "blast_master_200",
                "equipment_name": "Blast Master 200 Airblast",
                "equipment_type": EquipmentType.AIRBLAST_SPRAYER,
                "manufacturer": "Durand-Wayland",
                "tank_capacity": 757,
                "working_width": 6.1,
                "operating_pressure_range": (5.5, 20.7),
                "flow_rate_range": (38, 152),
                "droplet_size_range": (50, 200),
                "power_requirement_hp": 25,
                "hydraulic_flow_required": 19,
                "pto_speed_rpm": 540,
                "nozzle_type": "Disc/Core",
                "nozzle_count": 18,
                "orifice_size": "D3/46",
                "boom_height_range": (2.0, 4.0),
                "purchase_price": 45000,
                "annual_maintenance_cost": 2250,
                "calibration_interval_hours": 50,
                "replacement_interval_years": 10,
                "coverage_quality": 0.85,
                "drift_potential": 0.45,
                "application_efficiency": 0.87
            },
            {
                "equipment_id": "gandy_10t",
                "equipment_name": "Gandy 10T Granule Applicator",
                "equipment_type": EquipmentType.GRANULE_APPLICATOR,
                "manufacturer": "Gandy",
                "tank_capacity": 3785,  # 3785L = 1000 gallons dry capacity equivalent
                "working_width": 18.3,
                "operating_pressure_range": (0, 0),  # Gravity fed
                "flow_rate_range": (0, 0),  # Granular application
                "droplet_size_range": (0, 0),  # Granules, not droplets
                "power_requirement_hp": 15,
                "hydraulic_flow_required": 0,
                "pto_speed_rpm": 540,
                "nozzle_type": "Metering Gate",
                "nozzle_count": 6,
                "orifice_size": "Variable",
                "boom_height_range": (0.3, 0.6),
                "purchase_price": 25000,
                "annual_maintenance_cost": 1250,
                "calibration_interval_hours": 40,
                "replacement_interval_years": 20,
                "coverage_quality": 0.88,
                "drift_potential": 0.05,
                "application_efficiency": 0.96
            }
        ]
        
        # Convert to SprayEquipment objects
        for equip_dict in equipment_data:
            equipment = SprayEquipment(**equip_dict)
            self.spray_equipment[equipment.equipment_id] = equipment
            
        self.logger.info(f"Loaded {len(self.spray_equipment)} spray equipment models")
    
    def _setup_resistance_management(self):
        """Setup resistance management protocols"""
        # Create mode of action rotation rules
        self.moa_rotation_rules = {
            "corn_rootworm": {
                "max_consecutive_same_moa": 2,
                "max_seasonal_same_moa": 3,
                "required_rotation_interval": 1,  # years
                "high_risk_moas": ["irac_4", "irac_3"],
                "rotation_partners": {
                    "irac_4": ["irac_1", "irac_6"],  # Neonicotinoids rotate with OPs, avermectins
                    "irac_3": ["irac_1", "irac_15"], # Pyrethroids rotate with OPs, IGRs
                    "irac_1": ["irac_4", "irac_6"]   # OPs rotate with neonics, avermectins
                }
            },
            "corn_borer": {
                "max_consecutive_same_moa": 1,
                "max_seasonal_same_moa": 2,
                "required_rotation_interval": 0,  # Rotate within season
                "high_risk_moas": ["irac_3", "irac_28"],
                "rotation_partners": {
                    "irac_3": ["irac_5", "irac_6"],   # Pyrethroids rotate with spinosad, avermectins
                    "irac_28": ["irac_1", "irac_3"],  # Diamides rotate with OPs, pyrethroids
                    "irac_5": ["irac_28", "irac_15"]  # Spinosyns rotate with diamides, IGRs
                }
            },
            "gray_leaf_spot": {
                "max_consecutive_same_moa": 1,
                "max_seasonal_same_moa": 1,
                "required_rotation_interval": 0,
                "high_risk_moas": ["frac_11", "frac_3", "frac_7"],
                "rotation_partners": {
                    "frac_11": ["frac_m", "frac_3"],  # Strobilurins rotate with multi-site, DMIs
                    "frac_3": ["frac_m", "frac_7"],   # DMIs rotate with multi-site, SDHIs
                    "frac_7": ["frac_m", "frac_11"]   # SDHIs rotate with multi-site, strobilurins
                }
            }
        }
        
        self.logger.info("Resistance management protocols initialized")
    
    def _setup_weather_monitoring(self):
        """Setup weather monitoring for application timing"""
        # Initialize weather criteria for application decisions
        self.weather_criteria = {
            "wind_speed_max_kmh": 16,      # Maximum wind speed for application
            "temperature_max_c": 32,        # Maximum temperature
            "temperature_min_c": 4,         # Minimum temperature
            "relative_humidity_min": 40,    # Minimum RH for optimal efficacy
            "rainfall_forecast_hours": 6,   # Hours of rainfall forecast to avoid
            "inversion_risk_conditions": { # Temperature inversion risk
                "wind_speed_max": 5,
                "temperature_differential": 2
            }
        }
        
        self.logger.info("Weather monitoring criteria established")
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        if self.event_system:
            self.event_system.subscribe('weather_updated', self.handle_weather_update)
            self.event_system.subscribe('crop_growth_stage_changed', self.handle_crop_stage_change)
            self.event_system.subscribe('pest_threshold_exceeded', self.handle_pest_threshold)
            self.event_system.subscribe('disease_detected', self.handle_disease_detection)
            self.event_system.subscribe('equipment_maintenance_due', self.handle_maintenance_due)
    
    # Core treatment planning methods
    
    def plan_treatment_program(self, location_id: str, target_pests: List[str], 
                             crop_type: str, growth_stage: str) -> Dict[str, Any]:
        """
        Plan comprehensive treatment program for a location
        
        Args:
            location_id: Field or area identifier
            target_pests: List of target pest/disease IDs
            crop_type: Crop being treated
            growth_stage: Current crop growth stage
            
        Returns:
            Comprehensive treatment plan
        """
        try:
            treatment_plan = {
                "plan_id": f"plan_{location_id}_{int(datetime.now().timestamp())}",
                "location_id": location_id,
                "crop_type": crop_type,
                "growth_stage": growth_stage,
                "target_pests": target_pests,
                "plan_created": datetime.now(),
                "treatments": [],
                "resistance_strategy": {},
                "economic_analysis": {},
                "environmental_considerations": {}
            }
            
            # Analyze each target pest/disease
            for pest_id in target_pests:
                pest_treatments = self._analyze_pest_treatment_options(
                    pest_id, crop_type, growth_stage, location_id
                )
                treatment_plan["treatments"].extend(pest_treatments)
            
            # Optimize treatment combinations
            optimized_treatments = self._optimize_treatment_combinations(
                treatment_plan["treatments"]
            )
            treatment_plan["treatments"] = optimized_treatments
            
            # Develop resistance management strategy
            treatment_plan["resistance_strategy"] = self._develop_resistance_strategy(
                target_pests, treatment_plan["treatments"]
            )
            
            # Perform economic analysis
            treatment_plan["economic_analysis"] = self._analyze_treatment_economics(
                treatment_plan["treatments"]
            )
            
            # Assess environmental impact
            treatment_plan["environmental_considerations"] = self._assess_environmental_impact(
                treatment_plan["treatments"], location_id
            )
            
            self.logger.info(f"Treatment plan created for location {location_id}")
            return treatment_plan
            
        except Exception as e:
            self.logger.error(f"Error creating treatment plan: {e}")
            return {"error": str(e)}
    
    def _analyze_pest_treatment_options(self, pest_id: str, crop_type: str, 
                                      growth_stage: str, location_id: str) -> List[Dict[str, Any]]:
        """Analyze treatment options for specific pest"""
        treatment_options = []
        
        # Find suitable active ingredients for this pest
        suitable_ais = self._find_suitable_active_ingredients(pest_id, crop_type)
        
        for ai_id in suitable_ais:
            ai = self.active_ingredients[ai_id]
            
            # Find formulations containing this AI
            suitable_formulations = [
                form for form_id, form in self.formulations.items()
                if any(ai_pair[0] == ai_id for ai_pair in form.active_ingredients)
            ]
            
            for formulation in suitable_formulations:
                # Check PHI compatibility
                if self._check_phi_compatibility(formulation, growth_stage, crop_type):
                    treatment_option = {
                        "pest_target": pest_id,
                        "formulation_id": formulation.formulation_id,
                        "active_ingredient": ai_id,
                        "mode_of_action": ai.mode_of_action.value,
                        "resistance_risk": ai.resistance_risk.value,
                        "application_rate": formulation.recommended_rate,
                        "water_rate": formulation.water_rate,
                        "phi_days": ai.pre_harvest_interval,
                        "rei_hours": ai.restricted_entry_interval,
                        "efficacy_rating": self._calculate_efficacy_rating(ai_id, pest_id),
                        "cost_per_hectare": self._calculate_treatment_cost(formulation),
                        "environmental_impact_score": self._calculate_environmental_impact(ai_id)
                    }
                    treatment_options.append(treatment_option)
        
        return treatment_options
    
    def _find_suitable_active_ingredients(self, pest_id: str, crop_type: str) -> List[str]:
        """Find active ingredients suitable for pest and crop"""
        # This would normally query a comprehensive pest/AI efficacy database
        # For demo, return realistic examples based on pest type
        efficacy_database = {
            "corn_rootworm": ["chlorpyrifos", "bifenthrin", "imidacloprid"],
            "corn_borer": ["chlorpyrifos", "bifenthrin"],
            "armyworm": ["chlorpyrifos", "bifenthrin", "imidacloprid"],
            "gray_leaf_spot": ["tebuconazole", "azoxystrobin"],
            "northern_corn_leaf_blight": ["tebuconazole", "azoxystrobin"],
            "common_rust": ["tebuconazole", "azoxystrobin"],
            "giant_foxtail": ["glyphosate", "atrazine"],
            "common_lambsquarters": ["glyphosate", "atrazine"],
            "velvetleaf": ["glyphosate", "atrazine"]
        }
        
        return efficacy_database.get(pest_id, [])
    
    def _check_phi_compatibility(self, formulation: PesticideFormulation, 
                               growth_stage: str, crop_type: str) -> bool:
        """Check if formulation PHI is compatible with harvest timing"""
        # Estimate days to harvest based on growth stage
        days_to_harvest_estimates = {
            "emergence": 120,
            "vegetative": 90,
            "tasseling": 60,
            "grain_filling": 30,
            "physiological_maturity": 0
        }
        
        estimated_days = days_to_harvest_estimates.get(growth_stage, 60)
        
        # Get maximum PHI for all AIs in formulation
        max_phi = 0
        for ai_id, concentration in formulation.active_ingredients:
            if ai_id in self.active_ingredients:
                ai_phi = self.active_ingredients[ai_id].pre_harvest_interval
                max_phi = max(max_phi, ai_phi)
        
        return estimated_days >= max_phi
    
    def _optimize_treatment_combinations(self, treatments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize treatment combinations for tank mixing and timing"""
        optimized = []
        
        # Group treatments by compatibility and timing
        treatment_groups = {}
        
        for treatment in treatments:
            formulation_id = treatment["formulation_id"]
            formulation = self.formulations[formulation_id]
            
            # Create compatibility key based on tank mix compatibility
            compat_key = tuple(sorted(formulation.tank_mix_compatible))
            
            if compat_key not in treatment_groups:
                treatment_groups[compat_key] = []
            treatment_groups[compat_key].append(treatment)
        
        # For each group, create optimized combinations
        for group_treatments in treatment_groups.values():
            if len(group_treatments) > 1:
                # Create tank mix combination
                combo_treatment = self._create_tank_mix_combination(group_treatments)
                optimized.append(combo_treatment)
            else:
                optimized.extend(group_treatments)
        
        return optimized
    
    def _create_tank_mix_combination(self, treatments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create tank mix combination from compatible treatments"""
        combo = {
            "treatment_type": "tank_mix",
            "component_treatments": treatments,
            "formulations": [t["formulation_id"] for t in treatments],
            "target_pests": [t["pest_target"] for t in treatments],
            "modes_of_action": [t["mode_of_action"] for t in treatments],
            "total_cost": sum(t["cost_per_hectare"] for t in treatments),
            "application_rate_total": sum(t["application_rate"] for t in treatments),
            "water_rate": max(t["water_rate"] for t in treatments),
            "phi_days": max(t["phi_days"] for t in treatments),
            "rei_hours": max(t["rei_hours"] for t in treatments),
            "resistance_benefit": len(set(t["mode_of_action"] for t in treatments)) > 1
        }
        
        return combo
    
    def _develop_resistance_strategy(self, target_pests: List[str], 
                                   treatments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Develop resistance management strategy"""
        strategy = {
            "rotation_required": False,
            "high_risk_moas": [],
            "rotation_recommendations": [],
            "monitoring_required": [],
            "resistance_alerts": []
        }
        
        # Analyze mode of action usage
        moa_usage = {}
        for treatment in treatments:
            if "mode_of_action" in treatment:
                moa = treatment["mode_of_action"]
                if moa not in moa_usage:
                    moa_usage[moa] = 0
                moa_usage[moa] += 1
        
        # Check against rotation rules
        for pest_id in target_pests:
            if pest_id in self.moa_rotation_rules:
                rules = self.moa_rotation_rules[pest_id]
                
                for moa, usage_count in moa_usage.items():
                    if moa in rules["high_risk_moas"]:
                        strategy["high_risk_moas"].append(moa)
                        
                        if usage_count > rules["max_consecutive_same_moa"]:
                            strategy["rotation_required"] = True
                            
                            # Get rotation partners
                            partners = rules["rotation_partners"].get(moa, [])
                            strategy["rotation_recommendations"].append({
                                "current_moa": moa,
                                "recommended_alternatives": partners,
                                "pest_target": pest_id
                            })
        
        return strategy
    
    def _analyze_treatment_economics(self, treatments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze treatment program economics"""
        total_cost = sum(t.get("cost_per_hectare", 0) for t in treatments)
        
        economic_analysis = {
            "total_cost_per_hectare": total_cost,
            "cost_breakdown": [],
            "cost_benefit_ratio": None,
            "payback_analysis": {},
            "risk_adjusted_return": None
        }
        
        # Break down costs by treatment type
        for treatment in treatments:
            cost_item = {
                "treatment": treatment.get("formulation_id", "Unknown"),
                "target": treatment.get("pest_target", "Unknown"),
                "cost": treatment.get("cost_per_hectare", 0),
                "percentage_of_total": (treatment.get("cost_per_hectare", 0) / total_cost * 100) if total_cost > 0 else 0
            }
            economic_analysis["cost_breakdown"].append(cost_item)
        
        # Estimate yield protection value (would be more sophisticated in reality)
        estimated_yield_protection = self._estimate_yield_protection_value(treatments)
        
        if estimated_yield_protection > 0:
            economic_analysis["cost_benefit_ratio"] = estimated_yield_protection / total_cost
            economic_analysis["net_benefit"] = estimated_yield_protection - total_cost
            
        return economic_analysis
    
    def _estimate_yield_protection_value(self, treatments: List[Dict[str, Any]]) -> float:
        """Estimate economic value of yield protection"""
        # Simplified yield protection calculation
        # In reality, this would use historical efficacy data and economic models
        
        base_yield_value_per_ha = 2000  # Example: $2000/ha crop value
        protection_factors = {
            "corn_rootworm": 0.15,    # 15% yield protection
            "corn_borer": 0.08,       # 8% yield protection
            "gray_leaf_spot": 0.12,   # 12% yield protection
            "northern_corn_leaf_blight": 0.10,
            "giant_foxtail": 0.20,    # 20% yield protection
            "common_lambsquarters": 0.08
        }
        
        total_protection = 0
        protected_pests = set()
        
        for treatment in treatments:
            pest_target = treatment.get("pest_target", "")
            if pest_target in protection_factors and pest_target not in protected_pests:
                efficacy = treatment.get("efficacy_rating", 0.8)  # Default 80% efficacy
                protection_value = base_yield_value_per_ha * protection_factors[pest_target] * efficacy
                total_protection += protection_value
                protected_pests.add(pest_target)
        
        return total_protection
    
    def _assess_environmental_impact(self, treatments: List[Dict[str, Any]], 
                                   location_id: str) -> Dict[str, Any]:
        """Assess environmental impact of treatment program"""
        impact_assessment = {
            "overall_risk_score": 0.0,  # 0-1 scale
            "bee_risk_level": "low",
            "aquatic_risk_level": "low",
            "soil_persistence_concern": False,
            "groundwater_risk": "low",
            "beneficial_impact_rating": "low",
            "drift_risk_assessment": {},
            "mitigation_recommendations": []
        }
        
        # Analyze each treatment for environmental impact
        total_risk_score = 0
        high_bee_toxicity_count = 0
        high_aquatic_toxicity_count = 0
        
        for treatment in treatments:
            if "active_ingredient" in treatment:
                ai_id = treatment["active_ingredient"]
                if ai_id in self.active_ingredients:
                    ai = self.active_ingredients[ai_id]
                    
                    # Assess bee toxicity
                    if ai.bee_toxicity == "high":
                        high_bee_toxicity_count += 1
                    
                    # Assess aquatic toxicity
                    if ai.fish_toxicity == "high":
                        high_aquatic_toxicity_count += 1
                    
                    # Assess soil persistence
                    if ai.soil_half_life_days > 100:
                        impact_assessment["soil_persistence_concern"] = True
                    
                    # Calculate individual risk score
                    ai_risk = self._calculate_environmental_risk_score(ai)
                    total_risk_score += ai_risk
        
        # Calculate overall risk scores
        if treatments:
            impact_assessment["overall_risk_score"] = total_risk_score / len(treatments)
        
        # Determine risk levels
        if high_bee_toxicity_count > 0:
            impact_assessment["bee_risk_level"] = "high" if high_bee_toxicity_count > 1 else "medium"
            impact_assessment["mitigation_recommendations"].append(
                "Apply during evening hours when bees are less active"
            )
            impact_assessment["mitigation_recommendations"].append(
                "Avoid application during crop flowering"
            )
        
        if high_aquatic_toxicity_count > 0:
            impact_assessment["aquatic_risk_level"] = "high" if high_aquatic_toxicity_count > 1 else "medium"
            impact_assessment["mitigation_recommendations"].append(
                "Maintain buffer zones around water bodies"
            )
            impact_assessment["mitigation_recommendations"].append(
                "Use drift reduction agents and techniques"
            )
        
        return impact_assessment
    
    def _calculate_environmental_risk_score(self, ai: ActiveIngredient) -> float:
        """Calculate environmental risk score for active ingredient"""
        risk_score = 0.0
        
        # Toxicity factors
        if ai.bee_toxicity == "high":
            risk_score += 0.3
        elif ai.bee_toxicity == "medium":
            risk_score += 0.15
        
        if ai.fish_toxicity == "high":
            risk_score += 0.2
        elif ai.fish_toxicity == "medium":
            risk_score += 0.1
        
        # Persistence factors
        if ai.soil_half_life_days > 100:
            risk_score += 0.2
        elif ai.soil_half_life_days > 50:
            risk_score += 0.1
        
        # Mobility factors
        if ai.water_solubility > 100:  # mg/L
            risk_score += 0.15
        
        # Bioaccumulation
        if ai.bioaccumulation_factor > 1000:
            risk_score += 0.15
        elif ai.bioaccumulation_factor > 100:
            risk_score += 0.1
        
        return min(risk_score, 1.0)  # Cap at 1.0
    
    # Application execution methods
    
    def execute_application(self, treatment_plan: Dict[str, Any], 
                           equipment_id: str, weather_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pesticide application"""
        try:
            # Validate application conditions
            validation_result = self._validate_application_conditions(
                treatment_plan, equipment_id, weather_conditions
            )
            
            if not validation_result["approved"]:
                return {
                    "success": False,
                    "error": "Application conditions not suitable",
                    "validation_result": validation_result
                }
            
            # Create application record
            application_record = self._create_application_record(
                treatment_plan, equipment_id, weather_conditions
            )
            
            # Update equipment status
            if equipment_id in self.equipment_status:
                self.equipment_status[equipment_id] = "in_use"
            
            # Execute application simulation
            application_result = self._simulate_application_execution(
                application_record, weather_conditions
            )
            
            # Record completed application
            self.application_records.append(application_record)
            
            # Update PHI tracking
            self._update_phi_tracking(application_record)
            
            # Update resistance monitoring
            self._update_resistance_monitoring(application_record)
            
            # Publish events
            if self.event_system:
                self.event_system.publish('pesticide_application_completed', {
                    'record': application_record,
                    'result': application_result
                })
            
            self.logger.info(f"Application executed successfully: {application_record.record_id}")
            
            return {
                "success": True,
                "record": application_record,
                "result": application_result
            }
            
        except Exception as e:
            self.logger.error(f"Error executing application: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_application_conditions(self, treatment_plan: Dict[str, Any], 
                                       equipment_id: str, weather_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Validate conditions for pesticide application"""
        validation = {
            "approved": True,
            "warnings": [],
            "violations": [],
            "weather_suitability": WeatherSuitability.GOOD,
            "equipment_ready": True
        }
        
        # Check weather conditions
        weather_check = self._check_weather_suitability(weather_conditions)
        validation["weather_suitability"] = weather_check["suitability"]
        
        if weather_check["suitability"] in [WeatherSuitability.POOR, WeatherSuitability.PROHIBITED]:
            validation["approved"] = False
            validation["violations"].extend(weather_check["violations"])
        elif weather_check["suitability"] == WeatherSuitability.MARGINAL:
            validation["warnings"].extend(weather_check["warnings"])
        
        # Check equipment status
        if equipment_id not in self.spray_equipment:
            validation["approved"] = False
            validation["violations"].append(f"Equipment {equipment_id} not found")
        elif self.equipment_status.get(equipment_id) != "available":
            validation["approved"] = False
            validation["violations"].append(f"Equipment {equipment_id} not available")
        
        # Check calibration status
        if equipment_id in self.maintenance_schedules:
            last_calibration = self.maintenance_schedules[equipment_id]
            if (datetime.now() - last_calibration).days > 30:  # 30 days since calibration
                validation["warnings"].append("Equipment calibration overdue")
        
        # Check PHI compliance
        location_id = treatment_plan.get("location_id")
        if location_id:
            phi_check = self._check_phi_compliance(location_id, treatment_plan)
            if not phi_check["compliant"]:
                validation["approved"] = False
                validation["violations"].extend(phi_check["violations"])
        
        return validation
    
    def _check_weather_suitability(self, weather_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Check weather conditions for spray application suitability"""
        result = {
            "suitability": WeatherSuitability.EXCELLENT,
            "warnings": [],
            "violations": []
        }
        
        wind_speed = weather_conditions.get("wind_speed_kmh", 0)
        temperature = weather_conditions.get("temperature_c", 20)
        humidity = weather_conditions.get("relative_humidity", 60)
        rain_forecast = weather_conditions.get("rainfall_forecast_mm", 0)
        
        # Wind speed check
        if wind_speed > self.weather_criteria["wind_speed_max_kmh"]:
            result["suitability"] = WeatherSuitability.PROHIBITED
            result["violations"].append(f"Wind speed too high: {wind_speed} km/h")
        elif wind_speed > 12:
            result["suitability"] = WeatherSuitability.MARGINAL
            result["warnings"].append(f"Wind speed marginal: {wind_speed} km/h")
        
        # Temperature check
        if (temperature > self.weather_criteria["temperature_max_c"] or 
            temperature < self.weather_criteria["temperature_min_c"]):
            result["suitability"] = WeatherSuitability.POOR
            result["violations"].append(f"Temperature outside acceptable range: {temperature}°C")
        
        # Humidity check
        if humidity < self.weather_criteria["relative_humidity_min"]:
            result["suitability"] = WeatherSuitability.MARGINAL
            result["warnings"].append(f"Low humidity may reduce efficacy: {humidity}%")
        
        # Rainfall forecast
        if rain_forecast > 0:
            result["suitability"] = WeatherSuitability.POOR
            result["violations"].append(f"Rainfall forecast: {rain_forecast} mm")
        
        # Temperature inversion check
        if (wind_speed < 5 and 
            weather_conditions.get("temperature_differential", 0) > 2):
            result["suitability"] = WeatherSuitability.MARGINAL
            result["warnings"].append("Temperature inversion conditions possible")
        
        return result
    
    def _check_phi_compliance(self, location_id: str, treatment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Check pre-harvest interval compliance"""
        result = {
            "compliant": True,
            "violations": [],
            "days_to_harvest": None
        }
        
        # Get PHI tracking for location
        if location_id in self.phi_tracking:
            phi_records = self.phi_tracking[location_id]
            
            for treatment in treatment_plan.get("treatments", []):
                phi_days = treatment.get("phi_days", 0)
                
                # Check against any previous applications
                for app_date, previous_phi in phi_records:
                    days_since_application = (datetime.now() - app_date).days
                    
                    if days_since_application < previous_phi:
                        result["compliant"] = False
                        result["violations"].append(
                            f"PHI violation: {previous_phi - days_since_application} days remaining"
                        )
        
        return result
    
    def _create_application_record(self, treatment_plan: Dict[str, Any], 
                                 equipment_id: str, weather_conditions: Dict[str, Any]) -> ApplicationRecord:
        """Create detailed application record"""
        record = ApplicationRecord(
            record_id=f"app_{int(datetime.now().timestamp())}",
            application_date=datetime.now(),
            location_id=treatment_plan["location_id"],
            field_area_treated=treatment_plan.get("area_hectares", 1.0),
            formulation_used=treatment_plan["treatments"][0]["formulation_id"] if treatment_plan["treatments"] else "",
            rate_applied=treatment_plan["treatments"][0]["application_rate"] if treatment_plan["treatments"] else 0,
            water_volume=treatment_plan["treatments"][0]["water_rate"] if treatment_plan["treatments"] else 0,
            adjuvants_used=[],  # Would be populated based on treatment plan
            equipment_used=equipment_id,
            operator_name="System User",  # Would be actual operator
            weather_conditions=weather_conditions,
            application_start_time=datetime.now(),
            application_end_time=datetime.now() + timedelta(hours=2),  # Estimated duration
            pre_harvest_interval_respected=True,  # Validated earlier
            restricted_entry_posted=True,
            buffer_zones_observed=True,
            drift_mitigation_measures=["boom_height_optimized", "appropriate_nozzles"],
            target_pests=treatment_plan.get("target_pests", []),
            growth_stage_at_application=treatment_plan.get("growth_stage", ""),
            pest_pressure_level="medium",  # Would be assessed
            material_cost=0,  # Would be calculated
            application_cost=0,  # Would be calculated
            total_treatment_cost=0  # Would be calculated
        )
        
        return record
    
    def _simulate_application_execution(self, record: ApplicationRecord, 
                                      weather_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate the actual application execution"""
        # Calculate application efficiency based on equipment and weather
        equipment = self.spray_equipment[record.equipment_used]
        base_efficiency = equipment.application_efficiency
        
        # Weather adjustments
        weather_factor = 1.0
        wind_speed = weather_conditions.get("wind_speed_kmh", 8)
        if wind_speed > 10:
            weather_factor *= 0.95  # Slight reduction for higher wind
        
        temperature = weather_conditions.get("temperature_c", 20)
        if temperature > 25:
            weather_factor *= 0.98  # Slight reduction for higher temperature
        
        final_efficiency = base_efficiency * weather_factor
        
        # Calculate coverage quality
        coverage_quality = equipment.coverage_quality * weather_factor
        
        # Calculate drift potential
        drift_potential = equipment.drift_potential * (wind_speed / 10)
        
        return {
            "application_efficiency": final_efficiency,
            "coverage_quality": coverage_quality,
            "drift_potential": drift_potential,
            "weather_factor": weather_factor,
            "estimated_efficacy": final_efficiency * coverage_quality,
            "completion_time": record.application_end_time
        }
    
    def _update_phi_tracking(self, record: ApplicationRecord):
        """Update pre-harvest interval tracking"""
        location_id = record.location_id
        
        if location_id not in self.phi_tracking:
            self.phi_tracking[location_id] = []
        
        # Add PHI record for each formulation used
        formulation = self.formulations.get(record.formulation_used)
        if formulation:
            max_phi = 0
            for ai_id, concentration in formulation.active_ingredients:
                if ai_id in self.active_ingredients:
                    ai_phi = self.active_ingredients[ai_id].pre_harvest_interval
                    max_phi = max(max_phi, ai_phi)
            
            self.phi_tracking[location_id].append(
                (record.application_date, max_phi)
            )
    
    def _update_resistance_monitoring(self, record: ApplicationRecord):
        """Update resistance monitoring data"""
        for pest_target in record.target_pests:
            monitoring_key = f"{record.location_id}_{pest_target}"
            
            if monitoring_key not in self.resistance_monitoring:
                self.resistance_monitoring[monitoring_key] = ResistanceMonitoringData(
                    monitoring_id=monitoring_key,
                    location_id=record.location_id,
                    pest_species=pest_target,
                    monitoring_date=datetime.now(),
                    baseline_mortality=0.95,  # Default baseline
                    current_mortality=0.95,   # Would be measured
                    resistance_ratio=1.0,     # Baseline ratio
                    resistance_classification="S",
                    moa_usage_history={},
                    consecutive_applications_same_moa=0,
                    season_applications_same_moa=0,
                    resistance_risk_score=0.1,
                    recommended_actions=[],
                    alternative_modes_available=[]
                )
            
            # Update mode of action usage history
            formulation = self.formulations.get(record.formulation_used)
            if formulation:
                for ai_id, concentration in formulation.active_ingredients:
                    if ai_id in self.active_ingredients:
                        ai = self.active_ingredients[ai_id]
                        moa = ai.mode_of_action.value
                        
                        monitoring_data = self.resistance_monitoring[monitoring_key]
                        if moa not in monitoring_data.moa_usage_history:
                            monitoring_data.moa_usage_history[moa] = []
                        
                        monitoring_data.moa_usage_history[moa].append(record.application_date)
    
    # Equipment management methods
    
    def calibrate_equipment(self, equipment_id: str) -> Dict[str, Any]:
        """Calibrate spray equipment"""
        try:
            if equipment_id not in self.spray_equipment:
                return {"success": False, "error": "Equipment not found"}
            
            equipment = self.spray_equipment[equipment_id]
            
            # Simulate calibration process
            calibration_result = {
                "equipment_id": equipment_id,
                "calibration_date": datetime.now(),
                "flow_rate_check": True,
                "pressure_check": True,
                "nozzle_pattern_check": True,
                "boom_height_check": True,
                "accuracy_percentage": 98.5,  # Simulated accuracy
                "recommendations": []
            }
            
            # Update maintenance schedule
            self.maintenance_schedules[equipment_id] = datetime.now()
            
            # Update equipment status
            self.equipment_status[equipment_id] = "available"
            
            self.logger.info(f"Equipment {equipment_id} calibrated successfully")
            
            return {"success": True, "calibration_result": calibration_result}
            
        except Exception as e:
            self.logger.error(f"Error calibrating equipment {equipment_id}: {e}")
            return {"success": False, "error": str(e)}
    
    # Event handlers
    
    def handle_weather_update(self, event_data: Dict[str, Any]):
        """Handle weather update events"""
        try:
            # Update weather windows for application timing
            self._update_weather_windows(event_data)
            
            # Check if any scheduled applications need adjustment
            self._adjust_scheduled_applications_for_weather(event_data)
            
        except Exception as e:
            self.logger.error(f"Error handling weather update: {e}")
    
    def handle_pest_threshold(self, event_data: Dict[str, Any]):
        """Handle pest threshold exceeded events"""
        try:
            location_id = event_data.get("location_id")
            pest_id = event_data.get("pest_id")
            threshold_level = event_data.get("threshold_level")
            
            # Create treatment recommendation
            treatment_plan = self.plan_treatment_program(
                location_id, [pest_id], 
                event_data.get("crop_type", "corn"),
                event_data.get("growth_stage", "vegetative")
            )
            
            # Add to scheduled applications if treatment is warranted
            if treatment_plan.get("treatments"):
                self.scheduled_applications.append({
                    "priority": "high" if threshold_level > 2.0 else "medium",
                    "treatment_plan": treatment_plan,
                    "trigger_event": "pest_threshold",
                    "created_date": datetime.now()
                })
            
        except Exception as e:
            self.logger.error(f"Error handling pest threshold: {e}")
    
    def handle_disease_detection(self, event_data: Dict[str, Any]):
        """Handle disease detection events"""
        try:
            location_id = event_data.get("location_id")
            disease_id = event_data.get("disease_id")
            severity = event_data.get("severity", "low")
            
            # Create treatment recommendation
            treatment_plan = self.plan_treatment_program(
                location_id, [disease_id],
                event_data.get("crop_type", "corn"),
                event_data.get("growth_stage", "vegetative")
            )
            
            # High severity diseases get immediate priority
            priority = "critical" if severity == "high" else "high"
            
            self.scheduled_applications.append({
                "priority": priority,
                "treatment_plan": treatment_plan,
                "trigger_event": "disease_detection",
                "created_date": datetime.now()
            })
            
        except Exception as e:
            self.logger.error(f"Error handling disease detection: {e}")
    
    # Utility methods
    
    def get_treatment_history(self, location_id: str) -> List[ApplicationRecord]:
        """Get treatment history for a location"""
        return [record for record in self.application_records 
                if record.location_id == location_id]
    
    def get_resistance_status(self, location_id: str) -> Dict[str, Any]:
        """Get resistance status for a location"""
        location_resistance = {
            monitoring_id: data for monitoring_id, data in self.resistance_monitoring.items()
            if data.location_id == location_id
        }
        
        return location_resistance
    
    def calculate_treatment_cost(self, formulation_id: str, rate: float, area_ha: float) -> float:
        """Calculate treatment cost"""
        return self._calculate_treatment_cost_detailed(formulation_id, rate, area_ha)
    
    def _calculate_treatment_cost(self, formulation: PesticideFormulation) -> float:
        """Calculate cost per hectare for formulation"""
        # Simplified cost calculation - would use actual pricing data
        base_cost_per_liter = {
            "EC": 25,   # $25/L for emulsifiable concentrate
            "SC": 30,   # $30/L for suspension concentrate
            "WP": 20,   # $20/kg for wettable powder
            "SL": 22    # $22/L for soluble liquid
        }
        
        unit_cost = base_cost_per_liter.get(formulation.formulation_type, 25)
        return formulation.recommended_rate * unit_cost
    
    def _calculate_treatment_cost_detailed(self, formulation_id: str, rate: float, area_ha: float) -> float:
        """Calculate detailed treatment cost"""
        if formulation_id not in self.formulations:
            return 0
        
        formulation = self.formulations[formulation_id]
        cost_per_ha = self._calculate_treatment_cost(formulation)
        
        return cost_per_ha * area_ha
    
    def _calculate_efficacy_rating(self, ai_id: str, pest_id: str) -> float:
        """Calculate efficacy rating for AI against pest"""
        # Simplified efficacy database - in reality would be comprehensive
        efficacy_database = {
            ("chlorpyrifos", "corn_rootworm"): 0.85,
            ("chlorpyrifos", "corn_borer"): 0.80,
            ("bifenthrin", "corn_rootworm"): 0.90,
            ("bifenthrin", "corn_borer"): 0.88,
            ("imidacloprid", "corn_rootworm"): 0.88,
            ("tebuconazole", "gray_leaf_spot"): 0.82,
            ("azoxystrobin", "gray_leaf_spot"): 0.85,
            ("glyphosate", "giant_foxtail"): 0.95,
            ("atrazine", "giant_foxtail"): 0.75
        }
        
        return efficacy_database.get((ai_id, pest_id), 0.70)  # Default 70% efficacy
    
    def _update_weather_windows(self, weather_data: Dict[str, Any]):
        """Update suitable weather windows for applications"""
        # Analyze next 7 days of weather for application windows
        # This would integrate with weather forecasting system
        pass
    
    def _adjust_scheduled_applications_for_weather(self, weather_data: Dict[str, Any]):
        """Adjust scheduled applications based on weather"""
        # Check if weather conditions affect scheduled applications
        # Reschedule if necessary
        pass
    
    def _create_default_configuration(self):
        """Create minimal default configuration for fallback"""
        self.logger.warning("Creating minimal default treatment configuration")
        
        # Create basic active ingredient
        default_ai = ActiveIngredient(
            ai_id="default",
            common_name="Default Active Ingredient",
            chemical_name="Default Chemical",
            cas_number="0000-00-0",
            mode_of_action=ModeOfAction.MULTI_SITE_CONTACT,
            resistance_risk=ResistanceRisk.LOW,
            epa_registration="000-000",
            maximum_residue_limit=1.0,
            pre_harvest_interval=14,
            restricted_entry_interval=12,
            application_rate_range=(1.0, 2.0),
            water_carrier_rate=(140, 280),
            compatible_adjuvants=[],
            soil_half_life_days=30,
            water_solubility=100,
            vapor_pressure=0.001,
            bioaccumulation_factor=10,
            oral_ld50_rat=2000,
            dermal_ld50_rat=5000,
            bee_toxicity="low",
            fish_toxicity="low"
        )
        
        self.active_ingredients["default"] = default_ai


# Global convenience functions for easy access
treatment_systems_instance = None

def get_treatment_systems():
    """Get the global treatment systems instance"""
    global treatment_systems_instance
    if treatment_systems_instance is None:
        treatment_systems_instance = TreatmentSystems()
    return treatment_systems_instance

def plan_treatment(location_id: str, target_pests: List[str], crop_type: str, growth_stage: str):
    """Convenience function to plan treatment program"""
    return get_treatment_systems().plan_treatment_program(location_id, target_pests, crop_type, growth_stage)

def execute_treatment(treatment_plan: Dict[str, Any], equipment_id: str, weather_conditions: Dict[str, Any]):
    """Convenience function to execute treatment application"""
    return get_treatment_systems().execute_application(treatment_plan, equipment_id, weather_conditions)

def get_treatment_cost(formulation_id: str, rate: float, area_ha: float):
    """Convenience function to calculate treatment cost"""
    return get_treatment_systems().calculate_treatment_cost(formulation_id, rate, area_ha)

def check_resistance_status(location_id: str):
    """Convenience function to check resistance status"""
    return get_treatment_systems().get_resistance_status(location_id)