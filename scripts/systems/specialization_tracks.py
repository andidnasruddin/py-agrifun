"""
Specialization Tracks - Advanced Career Progression for AgriFun Agricultural Simulation

This system provides specialized career development paths that allow players to focus on specific
agricultural disciplines. Each specialization track offers unique benefits, equipment access,
research bonuses, and economic opportunities while requiring dedicated resource allocation
and strategic decision-making.

Key Features:
- Multiple Specialization Tracks: Grain Farming, Organic Farming, Precision Agriculture, Livestock
- Progressive Skill Development: Tiered advancement with increasing benefits
- Exclusive Technologies: Specialization-specific equipment and techniques
- Economic Benefits: Specialized market access and premium pricing
- Research Synergies: Faster advancement in related research areas
- Certification Systems: Industry recognition and credentialing

Specialization Tracks Available:
- Grain Farming Specialist: Focus on commodity crop production
- Organic Farming Specialist: Sustainable and certified organic practices
- Precision Agriculture Specialist: Technology-driven farming optimization
- Livestock Integration Specialist: Mixed crop-livestock systems
- Sustainable Agriculture Specialist: Conservation and environmental stewardship
- Agricultural Technology Specialist: Equipment and innovation focus

Educational Value:
- Understanding of agricultural career specialization paths
- Economic benefits of focused expertise vs. diversification
- Professional certification and credentialing processes
- Technology adoption and innovation diffusion in agriculture
- Sustainable agriculture practices and market premiums
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
import yaml
import random


class SpecializationType(Enum):
    """Types of agricultural specializations"""
    GRAIN_FARMING = "grain_farming"                      # Commodity crop production
    ORGANIC_FARMING = "organic_farming"                  # Certified organic practices
    PRECISION_AGRICULTURE = "precision_agriculture"      # Technology-driven optimization
    LIVESTOCK_INTEGRATION = "livestock_integration"      # Mixed crop-livestock systems
    SUSTAINABLE_AGRICULTURE = "sustainable_agriculture"  # Conservation practices
    AGRICULTURAL_TECHNOLOGY = "agricultural_technology"  # Equipment and innovation
    CROP_CONSULTING = "crop_consulting"                 # Advisory services
    SEED_PRODUCTION = "seed_production"                 # Seed breeding and production
    AGRICULTURAL_RESEARCH = "agricultural_research"      # Research and development
    FARM_MANAGEMENT = "farm_management"                 # Business and operations


class SpecializationTier(Enum):
    """Tiers of specialization advancement"""
    NOVICE = "novice"                                   # 0-25 skill points
    INTERMEDIATE = "intermediate"                       # 26-75 skill points  
    ADVANCED = "advanced"                              # 76-150 skill points
    EXPERT = "expert"                                  # 151-300 skill points
    MASTER = "master"                                  # 301+ skill points


class CertificationStatus(Enum):
    """Professional certification status"""
    NOT_CERTIFIED = "not_certified"
    PENDING_CERTIFICATION = "pending_certification"
    CERTIFIED = "certified"
    ADVANCED_CERTIFIED = "advanced_certified"
    MASTER_CERTIFIED = "master_certified"
    CERTIFICATION_EXPIRED = "certification_expired"


class SkillCategory(Enum):
    """Categories of agricultural skills"""
    TECHNICAL_SKILLS = "technical_skills"               # Equipment operation, technology
    AGRONOMIC_KNOWLEDGE = "agronomic_knowledge"         # Crop science, soil management
    BUSINESS_MANAGEMENT = "business_management"         # Economics, marketing, planning
    ENVIRONMENTAL_STEWARDSHIP = "environmental_stewardship" # Sustainability, conservation
    INNOVATION_ADOPTION = "innovation_adoption"         # Technology adoption, R&D
    QUALITY_MANAGEMENT = "quality_management"           # Quality control, certification
    RISK_MANAGEMENT = "risk_management"                 # Insurance, hedging, planning
    COMMUNICATION = "communication"                     # Extension, education, marketing


@dataclass
class Skill:
    """Individual skill definition"""
    skill_id: str
    skill_name: str
    description: str
    category: SkillCategory
    max_level: int = 100
    
    # Learning parameters
    base_learning_rate: float = 1.0                    # Base skill gain per activity
    learning_curve_factor: float = 0.95                # Diminishing returns factor
    practice_activities: List[str] = field(default_factory=list)
    
    # Skill benefits
    efficiency_bonus_per_level: float = 0.01           # 1% efficiency per level
    quality_bonus_per_level: float = 0.005             # 0.5% quality per level
    cost_reduction_per_level: float = 0.002            # 0.2% cost reduction per level
    
    # Prerequisites
    prerequisite_skills: List[Tuple[str, int]] = field(default_factory=list)  # [(skill_id, level)]
    prerequisite_technologies: List[str] = field(default_factory=list)
    prerequisite_certifications: List[str] = field(default_factory=list)


@dataclass
class SpecializationBenefit:
    """Benefits granted by specialization advancement"""
    benefit_id: str
    benefit_name: str
    description: str
    tier_required: SpecializationTier
    
    # Benefit effects
    efficiency_multiplier: float = 1.0                 # Multiplicative efficiency bonus
    cost_reduction_percentage: float = 0.0             # Cost reduction bonus
    quality_bonus_percentage: float = 0.0              # Quality improvement bonus
    income_multiplier: float = 1.0                     # Income bonus multiplier
    
    # Unlocks
    equipment_unlocks: List[str] = field(default_factory=list)
    technique_unlocks: List[str] = field(default_factory=list)
    market_access_unlocks: List[str] = field(default_factory=list)
    research_unlocks: List[str] = field(default_factory=list)
    
    # Special abilities
    special_abilities: List[str] = field(default_factory=list)
    exclusive_contracts: List[str] = field(default_factory=list)
    certification_eligibility: List[str] = field(default_factory=list)


@dataclass
class Certification:
    """Professional certification definition"""
    cert_id: str
    cert_name: str
    description: str
    certifying_organization: str
    specialization_required: SpecializationType
    
    # Requirements
    minimum_tier: SpecializationTier
    required_skills: Dict[str, int]                     # {skill_id: minimum_level}
    required_experience_points: int
    required_education_hours: int
    practical_requirements: List[str]
    
    # Certification process
    application_cost: float
    examination_cost: float
    annual_maintenance_fee: float
    renewal_period_years: int
    continuing_education_hours_annual: int
    
    # Benefits
    certification_benefits: List[SpecializationBenefit]
    market_premium_percentage: float = 0.0             # Price premium for certified products
    exclusive_market_access: List[str] = field(default_factory=list)
    professional_recognition: str = ""


@dataclass
class SpecializationTrack:
    """Complete specialization track definition"""
    track_id: str
    track_name: str
    description: str
    specialization_type: SpecializationType
    
    # Core skills for this specialization
    core_skills: List[str]                              # Primary skills for this track
    supporting_skills: List[str]                        # Secondary skills
    skill_definitions: Dict[str, Skill] = field(default_factory=dict)
    
    # Progression benefits by tier
    tier_benefits: Dict[SpecializationTier, List[SpecializationBenefit]] = field(default_factory=dict)
    
    # Available certifications
    available_certifications: List[str] = field(default_factory=list)
    certification_definitions: Dict[str, Certification] = field(default_factory=dict)
    
    # Economic factors
    market_focus: List[str]                             # Market segments this specialization serves
    seasonal_demand_patterns: Dict[str, float] = field(default_factory=dict)  # Monthly demand multipliers
    competitive_advantages: List[str] = field(default_factory=list)
    
    # Technology integration
    preferred_technologies: List[str] = field(default_factory=list)
    technology_adoption_bonus: float = 1.2              # 20% faster tech adoption
    research_focus_areas: List[str] = field(default_factory=list)
    
    # Resource requirements
    initial_investment_cost: float = 0                  # Cost to begin specialization
    ongoing_maintenance_cost_annual: float = 0          # Annual specialization costs
    equipment_requirements: List[str] = field(default_factory=list)
    
    # Performance metrics
    success_metrics: Dict[str, str] = field(default_factory=dict)  # {metric: description}
    benchmark_targets: Dict[str, float] = field(default_factory=dict)  # Performance targets


@dataclass
class PlayerSpecialization:
    """Player's progress in a specific specialization"""
    track_id: str
    start_date: datetime
    current_tier: SpecializationTier = SpecializationTier.NOVICE
    
    # Skill progression
    skill_levels: Dict[str, int] = field(default_factory=dict)    # {skill_id: current_level}
    total_skill_points: int = 0
    skill_experience: Dict[str, float] = field(default_factory=dict)  # {skill_id: experience}
    
    # Certifications
    active_certifications: Set[str] = field(default_factory=set)
    certification_history: List[Dict[str, Any]] = field(default_factory=list)
    pending_certifications: Set[str] = field(default_factory=set)
    
    # Progress tracking
    activities_completed: List[Dict[str, Any]] = field(default_factory=list)
    milestones_achieved: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Economic impact
    specialization_income: float = 0                     # Income attributed to specialization
    premium_earnings: float = 0                          # Premium earnings from specialization
    cost_savings: float = 0                             # Cost savings from efficiency
    
    # Time investment
    hours_invested: float = 0                           # Total hours invested in specialization
    education_hours_completed: int = 0                  # Formal education hours
    practical_experience_hours: int = 0                 # Hands-on experience hours


class SpecializationTracks:
    """
    Comprehensive Specialization Tracks system for agricultural career development
    
    This system manages multiple specialized career paths, skill development, professional
    certifications, and the economic benefits of focused expertise in specific agricultural
    disciplines.
    """
    
    def __init__(self, config_manager=None, event_system=None):
        """Initialize specialization tracks system"""
        self.config_manager = config_manager
        self.event_system = event_system
        self.logger = logging.getLogger(__name__)
        
        # Core specialization data
        self.specialization_tracks: Dict[str, SpecializationTrack] = {}
        self.skill_definitions: Dict[str, Skill] = {}
        self.certification_definitions: Dict[str, Certification] = {}
        
        # Player progression
        self.player_specializations: Dict[str, PlayerSpecialization] = {}
        self.active_specialization: Optional[str] = None
        self.specialization_history: List[Dict[str, Any]] = []
        
        # Skill development tracking
        self.skill_activities: Dict[str, List[Dict[str, Any]]] = {}  # {activity_id: [skill_gains]}
        self.learning_efficiency: Dict[str, float] = {}              # {skill_id: efficiency_multiplier}
        self.skill_decay_rates: Dict[str, float] = {}               # {skill_id: decay_rate}
        
        # Certification management
        self.certification_applications: List[Dict[str, Any]] = []
        self.certification_schedules: Dict[str, datetime] = {}       # {cert_id: next_renewal_date}
        self.continuing_education_records: List[Dict[str, Any]] = []
        
        # Market integration
        self.specialization_market_access: Dict[str, List[str]] = {} # {track_id: [market_segments]}
        self.premium_pricing_agreements: List[Dict[str, Any]] = []
        self.competitive_advantages: Dict[str, List[str]] = {}       # {track_id: [advantages]}
        
        # Performance tracking
        self.specialization_performance: Dict[str, Dict[str, float]] = {}  # {track_id: {metric: value}}
        self.benchmark_comparisons: Dict[str, Dict[str, float]] = {}       # Performance vs benchmarks
        self.achievement_records: List[Dict[str, Any]] = []
        
        # Initialize system
        self._initialize_specialization_system()
        
    def _initialize_specialization_system(self):
        """Initialize specialization system with track definitions"""
        try:
            self._load_specialization_tracks()
            self._setup_skill_activities()
            self._initialize_certification_system()
            self._setup_market_integration()
            
            if self.event_system:
                self._subscribe_to_events()
                
            self.logger.info("Specialization Tracks system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing specialization tracks: {e}")
            self._create_basic_specialization_configuration()
    
    def _load_specialization_tracks(self):
        """Load comprehensive specialization track definitions"""
        
        # Grain Farming Specialist Track
        grain_farming_track = self._create_grain_farming_track()
        self.specialization_tracks[grain_farming_track.track_id] = grain_farming_track
        
        # Organic Farming Specialist Track
        organic_farming_track = self._create_organic_farming_track()
        self.specialization_tracks[organic_farming_track.track_id] = organic_farming_track
        
        # Precision Agriculture Specialist Track
        precision_ag_track = self._create_precision_agriculture_track()
        self.specialization_tracks[precision_ag_track.track_id] = precision_ag_track
        
        # Sustainable Agriculture Specialist Track
        sustainable_ag_track = self._create_sustainable_agriculture_track()
        self.specialization_tracks[sustainable_ag_track.track_id] = sustainable_ag_track
        
        # Agricultural Technology Specialist Track
        ag_tech_track = self._create_agricultural_technology_track()
        self.specialization_tracks[ag_tech_track.track_id] = ag_tech_track
        
        self.logger.info(f"Loaded {len(self.specialization_tracks)} specialization tracks")
    
    def _create_grain_farming_track(self) -> SpecializationTrack:
        """Create grain farming specialization track"""
        
        # Define core skills for grain farming
        grain_skills = {
            "grain_crop_management": Skill(
                skill_id="grain_crop_management",
                skill_name="Grain Crop Management",
                description="Expertise in managing corn, soybeans, wheat, and other grain crops",
                category=SkillCategory.AGRONOMIC_KNOWLEDGE,
                max_level=100,
                base_learning_rate=2.0,
                practice_activities=["planting_operations", "harvest_operations", "crop_scouting"],
                efficiency_bonus_per_level=0.015,  # 1.5% per level
                quality_bonus_per_level=0.008
            ),
            "commodity_marketing": Skill(
                skill_id="commodity_marketing",
                skill_name="Commodity Marketing",
                description="Marketing grain commodities for optimal profitability",
                category=SkillCategory.BUSINESS_MANAGEMENT,
                max_level=100,
                base_learning_rate=1.5,
                practice_activities=["market_analysis", "futures_trading", "contract_negotiation"],
                efficiency_bonus_per_level=0.01,
                cost_reduction_per_level=0.005
            ),
            "grain_storage": Skill(
                skill_id="grain_storage",
                skill_name="Grain Storage Management",
                description="Proper storage and handling of harvested grains",
                category=SkillCategory.TECHNICAL_SKILLS,
                max_level=100,
                base_learning_rate=1.8,
                practice_activities=["storage_management", "quality_monitoring", "pest_control"],
                quality_bonus_per_level=0.012
            ),
            "large_equipment_operation": Skill(
                skill_id="large_equipment_operation",
                skill_name="Large Equipment Operation",
                description="Operating large-scale farming equipment efficiently",
                category=SkillCategory.TECHNICAL_SKILLS,
                max_level=100,
                base_learning_rate=1.2,
                practice_activities=["tractor_operation", "combine_operation", "implement_setup"],
                efficiency_bonus_per_level=0.02
            )
        }
        
        # Define tier benefits
        tier_benefits = {
            SpecializationTier.NOVICE: [
                SpecializationBenefit(
                    benefit_id="grain_novice_1",
                    benefit_name="Basic Grain Knowledge",
                    description="5% improvement in grain crop yields",
                    tier_required=SpecializationTier.NOVICE,
                    efficiency_multiplier=1.05,
                    technique_unlocks=["basic_grain_rotation"]
                )
            ],
            SpecializationTier.INTERMEDIATE: [
                SpecializationBenefit(
                    benefit_id="grain_intermediate_1",
                    benefit_name="Grain Marketing Access",
                    description="Access to commodity futures markets and contracts",
                    tier_required=SpecializationTier.INTERMEDIATE,
                    income_multiplier=1.1,
                    market_access_unlocks=["commodity_futures", "grain_contracts"],
                    equipment_unlocks=["grain_elevator_access"]
                )
            ],
            SpecializationTier.ADVANCED: [
                SpecializationBenefit(
                    benefit_id="grain_advanced_1",
                    benefit_name="Large-Scale Efficiency",
                    description="15% reduction in per-unit production costs for grain crops",
                    tier_required=SpecializationTier.ADVANCED,
                    cost_reduction_percentage=15.0,
                    equipment_unlocks=["large_scale_planters", "large_combines"],
                    special_abilities=["bulk_purchasing_discounts"]
                )
            ],
            SpecializationTier.EXPERT: [
                SpecializationBenefit(
                    benefit_id="grain_expert_1",
                    benefit_name="Grain Quality Premium",
                    description="20% premium for high-quality grain production",
                    tier_required=SpecializationTier.EXPERT,
                    quality_bonus_percentage=25.0,
                    income_multiplier=1.2,
                    exclusive_contracts=["premium_grain_buyers"]
                )
            ],
            SpecializationTier.MASTER: [
                SpecializationBenefit(
                    benefit_id="grain_master_1",
                    benefit_name="Grain Farming Mastery",
                    description="Industry leadership in grain production excellence",
                    tier_required=SpecializationTier.MASTER,
                    efficiency_multiplier=1.3,
                    income_multiplier=1.25,
                    special_abilities=["consulting_opportunities", "industry_leadership"],
                    certification_eligibility=["certified_crop_advisor"]
                )
            ]
        }
        
        # Create certifications
        grain_certifications = {
            "certified_crop_advisor": Certification(
                cert_id="certified_crop_advisor",
                cert_name="Certified Crop Advisor (CCA)",
                description="Professional certification for crop advisory services",
                certifying_organization="American Society of Agronomy",
                specialization_required=SpecializationType.GRAIN_FARMING,
                minimum_tier=SpecializationTier.EXPERT,
                required_skills={
                    "grain_crop_management": 75,
                    "commodity_marketing": 50
                },
                required_experience_points=1000,
                required_education_hours=40,
                practical_requirements=["field_demonstration", "crop_advisory_project"],
                application_cost=500,
                examination_cost=300,
                annual_maintenance_fee=150,
                renewal_period_years=2,
                continuing_education_hours_annual=20,
                market_premium_percentage=15.0,
                exclusive_market_access=["premium_advisory_services"],
                professional_recognition="Industry-recognized crop advisor"
            )
        }
        
        return SpecializationTrack(
            track_id="grain_farming_specialist",
            track_name="Grain Farming Specialist",
            description="Specialization in large-scale grain crop production and marketing",
            specialization_type=SpecializationType.GRAIN_FARMING,
            core_skills=["grain_crop_management", "commodity_marketing"],
            supporting_skills=["grain_storage", "large_equipment_operation"],
            skill_definitions=grain_skills,
            tier_benefits=tier_benefits,
            available_certifications=["certified_crop_advisor"],
            certification_definitions=grain_certifications,
            market_focus=["commodity_grains", "export_markets", "livestock_feed"],
            competitive_advantages=["scale_efficiency", "market_access", "technology_adoption"],
            preferred_technologies=["large_tractors", "combines", "grain_storage"],
            technology_adoption_bonus=1.3,
            research_focus_areas=["crop_genetics", "precision_agriculture", "storage_technology"],
            initial_investment_cost=50000,
            ongoing_maintenance_cost_annual=5000,
            equipment_requirements=["large_tractor", "combine_harvester", "grain_storage"],
            success_metrics={
                "yield_per_hectare": "Grain yield efficiency",
                "cost_per_bushel": "Production cost efficiency",
                "market_price_received": "Marketing effectiveness"
            },
            benchmark_targets={
                "yield_per_hectare": 10.0,  # tons/ha
                "cost_per_bushel": 3.50,    # $/bushel
                "market_price_received": 1.05  # Premium ratio
            }
        )
    
    def _create_organic_farming_track(self) -> SpecializationTrack:
        """Create organic farming specialization track"""
        
        # Define core skills for organic farming
        organic_skills = {
            "organic_crop_management": Skill(
                skill_id="organic_crop_management",
                skill_name="Organic Crop Management",
                description="Managing crops without synthetic pesticides and fertilizers",
                category=SkillCategory.AGRONOMIC_KNOWLEDGE,
                max_level=100,
                base_learning_rate=1.5,
                practice_activities=["organic_pest_control", "cover_crop_management", "organic_fertilization"],
                efficiency_bonus_per_level=0.01,
                quality_bonus_per_level=0.015,  # Quality more important in organic
                prerequisite_technologies=["organic_certification"]
            ),
            "soil_health_management": Skill(
                skill_id="soil_health_management",
                skill_name="Soil Health Management",
                description="Building and maintaining healthy soil ecosystems",
                category=SkillCategory.ENVIRONMENTAL_STEWARDSHIP,
                max_level=100,
                base_learning_rate=1.3,
                practice_activities=["composting", "cover_cropping", "soil_testing"],
                efficiency_bonus_per_level=0.012,
                quality_bonus_per_level=0.01
            ),
            "organic_marketing": Skill(
                skill_id="organic_marketing",
                skill_name="Organic Marketing",
                description="Marketing organic products for premium prices",
                category=SkillCategory.BUSINESS_MANAGEMENT,
                max_level=100,
                base_learning_rate=1.2,
                practice_activities=["organic_market_development", "consumer_education", "brand_building"],
                income_multiplier=1.02  # 2% per level income boost
            ),
            "certification_management": Skill(
                skill_id="certification_management",
                skill_name="Organic Certification Management",
                description="Managing organic certification requirements and compliance",
                category=SkillCategory.QUALITY_MANAGEMENT,
                max_level=100,
                base_learning_rate=1.0,
                practice_activities=["record_keeping", "compliance_monitoring", "inspection_preparation"],
                cost_reduction_per_level=0.008  # Reduces certification costs
            )
        }
        
        # Define tier benefits for organic farming
        tier_benefits = {
            SpecializationTier.NOVICE: [
                SpecializationBenefit(
                    benefit_id="organic_novice_1",
                    benefit_name="Organic Transition Support",
                    description="Reduced penalties during organic transition period",
                    tier_required=SpecializationTier.NOVICE,
                    cost_reduction_percentage=10.0,
                    technique_unlocks=["transition_planning"]
                )
            ],
            SpecializationTier.INTERMEDIATE: [
                SpecializationBenefit(
                    benefit_id="organic_intermediate_1",
                    benefit_name="Organic Certification Access",
                    description="Eligible for organic certification and premium markets",
                    tier_required=SpecializationTier.INTERMEDIATE,
                    market_access_unlocks=["organic_markets", "farmers_markets"],
                    certification_eligibility=["usda_organic"]
                )
            ],
            SpecializationTier.ADVANCED: [
                SpecializationBenefit(
                    benefit_id="organic_advanced_1",
                    benefit_name="Premium Organic Marketing",
                    description="30% premium pricing for organic products",
                    tier_required=SpecializationTier.ADVANCED,
                    income_multiplier=1.3,
                    market_access_unlocks=["specialty_organic_markets", "restaurant_direct"],
                    special_abilities=["direct_marketing", "agritourism"]
                )
            ],
            SpecializationTier.EXPERT: [
                SpecializationBenefit(
                    benefit_id="organic_expert_1",
                    benefit_name="Organic System Mastery",
                    description="Advanced organic farming techniques and biodiversity",
                    tier_required=SpecializationTier.EXPERT,
                    efficiency_multiplier=1.2,
                    quality_bonus_percentage=30.0,
                    special_abilities=["biodiversity_bonuses", "ecosystem_services"]
                )
            ],
            SpecializationTier.MASTER: [
                SpecializationBenefit(
                    benefit_id="organic_master_1",
                    benefit_name="Organic Leadership",
                    description="Industry leadership in organic farming practices",
                    tier_required=SpecializationTier.MASTER,
                    income_multiplier=1.4,
                    special_abilities=["organic_consulting", "certification_inspector"],
                    certification_eligibility=["organic_inspector"]
                )
            ]
        }
        
        # Organic certifications
        organic_certifications = {
            "usda_organic": Certification(
                cert_id="usda_organic",
                cert_name="USDA Organic Certification",
                description="Official USDA organic certification for crop production",
                certifying_organization="USDA National Organic Program",
                specialization_required=SpecializationType.ORGANIC_FARMING,
                minimum_tier=SpecializationTier.INTERMEDIATE,
                required_skills={
                    "organic_crop_management": 50,
                    "certification_management": 40
                },
                required_experience_points=500,
                required_education_hours=20,
                practical_requirements=["three_year_transition", "organic_system_plan"],
                application_cost=2000,
                examination_cost=0,
                annual_maintenance_fee=1000,
                renewal_period_years=1,
                continuing_education_hours_annual=10,
                market_premium_percentage=25.0,
                exclusive_market_access=["organic_wholesale", "organic_retail"],
                professional_recognition="USDA Certified Organic"
            )
        }
        
        return SpecializationTrack(
            track_id="organic_farming_specialist",
            track_name="Organic Farming Specialist",
            description="Specialization in certified organic crop production and marketing",
            specialization_type=SpecializationType.ORGANIC_FARMING,
            core_skills=["organic_crop_management", "soil_health_management"],
            supporting_skills=["organic_marketing", "certification_management"],
            skill_definitions=organic_skills,
            tier_benefits=tier_benefits,
            available_certifications=["usda_organic"],
            certification_definitions=organic_certifications,
            market_focus=["organic_consumers", "specialty_markets", "direct_sales"],
            competitive_advantages=["premium_pricing", "environmental_benefits", "consumer_demand"],
            preferred_technologies=["organic_inputs", "biological_controls", "soil_amendments"],
            technology_adoption_bonus=1.1,
            research_focus_areas=["soil_biology", "organic_pest_control", "sustainable_practices"],
            initial_investment_cost=25000,
            ongoing_maintenance_cost_annual=8000,  # Higher due to certification costs
            equipment_requirements=["composting_equipment", "cover_crop_seeder"],
            success_metrics={
                "organic_premium_percentage": "Premium over conventional prices",
                "soil_health_score": "Soil biological activity and health",
                "certification_compliance": "Certification audit scores"
            },
            benchmark_targets={
                "organic_premium_percentage": 25.0,
                "soil_health_score": 80.0,
                "certification_compliance": 95.0
            }
        )
    
    def _create_precision_agriculture_track(self) -> SpecializationTrack:
        """Create precision agriculture specialization track"""
        
        # Define core skills for precision agriculture
        precision_skills = {
            "gps_technology": Skill(
                skill_id="gps_technology",
                skill_name="GPS Technology Operation",
                description="Operating GPS guidance and variable-rate application systems",
                category=SkillCategory.TECHNICAL_SKILLS,
                max_level=100,
                base_learning_rate=1.0,
                practice_activities=["gps_calibration", "guidance_operation", "boundary_mapping"],
                efficiency_bonus_per_level=0.02,
                prerequisite_technologies=["gps_guidance"]
            ),
            "data_analytics": Skill(
                skill_id="data_analytics",
                skill_name="Agricultural Data Analytics",
                description="Analyzing field data for optimization decisions",
                category=SkillCategory.INNOVATION_ADOPTION,
                max_level=100,
                base_learning_rate=0.8,
                practice_activities=["yield_analysis", "soil_mapping", "prescription_development"],
                efficiency_bonus_per_level=0.018,
                quality_bonus_per_level=0.01
            ),
            "sensor_technology": Skill(
                skill_id="sensor_technology",
                skill_name="Sensor Technology Integration",
                description="Integrating and managing agricultural sensor networks",
                category=SkillCategory.TECHNICAL_SKILLS,
                max_level=100,
                base_learning_rate=1.1,
                practice_activities=["sensor_installation", "data_collection", "system_maintenance"],
                efficiency_bonus_per_level=0.015,
                prerequisite_technologies=["sensor_networks"]
            ),
            "precision_application": Skill(
                skill_id="precision_application",
                skill_name="Precision Application Management",
                description="Variable-rate application of inputs for optimal efficiency",
                category=SkillCategory.AGRONOMIC_KNOWLEDGE,
                max_level=100,
                base_learning_rate=1.3,
                practice_activities=["prescription_mapping", "variable_rate_seeding", "variable_rate_fertilizing"],
                efficiency_bonus_per_level=0.022,
                cost_reduction_per_level=0.01
            )
        }
        
        # Precision agriculture tier benefits
        tier_benefits = {
            SpecializationTier.NOVICE: [
                SpecializationBenefit(
                    benefit_id="precision_novice_1",
                    benefit_name="Basic Precision Tools",
                    description="10% improvement in input application accuracy",
                    tier_required=SpecializationTier.NOVICE,
                    efficiency_multiplier=1.1,
                    equipment_unlocks=["basic_gps_receiver"]
                )
            ],
            SpecializationTier.INTERMEDIATE: [
                SpecializationBenefit(
                    benefit_id="precision_intermediate_1",
                    benefit_name="Variable Rate Technology",
                    description="Access to variable-rate application equipment",
                    tier_required=SpecializationTier.INTERMEDIATE,
                    cost_reduction_percentage=12.0,
                    equipment_unlocks=["variable_rate_spreader", "yield_monitor"],
                    technique_unlocks=["prescription_mapping"]
                )
            ],
            SpecializationTier.ADVANCED: [
                SpecializationBenefit(
                    benefit_id="precision_advanced_1",
                    benefit_name="Advanced Analytics",
                    description="20% improvement in decision-making through data analytics",
                    tier_required=SpecializationTier.ADVANCED,
                    efficiency_multiplier=1.2,
                    equipment_unlocks=["drone_systems", "advanced_sensors"],
                    special_abilities=["predictive_analytics", "automated_recommendations"]
                )
            ],
            SpecializationTier.EXPERT: [
                SpecializationBenefit(
                    benefit_id="precision_expert_1",
                    benefit_name="Precision Agriculture Mastery",
                    description="25% reduction in input costs through precision management",
                    tier_required=SpecializationTier.EXPERT,
                    cost_reduction_percentage=25.0,
                    efficiency_multiplier=1.25,
                    equipment_unlocks=["autonomous_equipment"],
                    special_abilities=["system_integration", "custom_algorithms"]
                )
            ],
            SpecializationTier.MASTER: [
                SpecializationBenefit(
                    benefit_id="precision_master_1",
                    benefit_name="Precision Technology Leadership",
                    description="Industry leadership in precision agriculture innovation",
                    tier_required=SpecializationTier.MASTER,
                    efficiency_multiplier=1.3,
                    special_abilities=["technology_consulting", "system_design"],
                    certification_eligibility=["precision_agriculture_specialist"]
                )
            ]
        }
        
        return SpecializationTrack(
            track_id="precision_agriculture_specialist",
            track_name="Precision Agriculture Specialist",
            description="Specialization in technology-driven farming optimization",
            specialization_type=SpecializationType.PRECISION_AGRICULTURE,
            core_skills=["gps_technology", "data_analytics"],
            supporting_skills=["sensor_technology", "precision_application"],
            skill_definitions=precision_skills,
            tier_benefits=tier_benefits,
            market_focus=["technology_adoption", "efficiency_optimization", "data_services"],
            competitive_advantages=["input_efficiency", "yield_optimization", "technology_leadership"],
            preferred_technologies=["gps_systems", "drones", "sensors", "data_analytics"],
            technology_adoption_bonus=1.5,
            research_focus_areas=["precision_technology", "data_science", "automation"],
            initial_investment_cost=75000,
            ongoing_maintenance_cost_annual=12000,
            equipment_requirements=["gps_tractor", "yield_monitor", "computer_system"],
            success_metrics={
                "input_efficiency": "Reduction in input waste",
                "yield_variability": "Reduction in field variability",
                "technology_roi": "Return on technology investment"
            },
            benchmark_targets={
                "input_efficiency": 20.0,  # % reduction in waste
                "yield_variability": 15.0,  # % reduction in CV
                "technology_roi": 3.0      # Years payback
            }
        )
    
    def _create_sustainable_agriculture_track(self) -> SpecializationTrack:
        """Create sustainable agriculture specialization track"""
        
        # Define core skills for sustainable agriculture
        sustainable_skills = {
            "conservation_practices": Skill(
                skill_id="conservation_practices",
                skill_name="Conservation Practices",
                description="Implementing soil and water conservation methods",
                category=SkillCategory.ENVIRONMENTAL_STEWARDSHIP,
                max_level=100,
                base_learning_rate=1.4,
                practice_activities=["no_till_farming", "cover_cropping", "buffer_strips"],
                efficiency_bonus_per_level=0.01,
                quality_bonus_per_level=0.012
            ),
            "biodiversity_management": Skill(
                skill_id="biodiversity_management",
                skill_name="Biodiversity Management",
                description="Promoting and managing on-farm biodiversity",
                category=SkillCategory.ENVIRONMENTAL_STEWARDSHIP,
                max_level=100,
                base_learning_rate=1.1,
                practice_activities=["habitat_creation", "pollinator_support", "beneficial_insects"],
                quality_bonus_per_level=0.015
            ),
            "carbon_management": Skill(
                skill_id="carbon_management",
                skill_name="Carbon Sequestration Management",
                description="Managing farming practices for carbon sequestration",
                category=SkillCategory.ENVIRONMENTAL_STEWARDSHIP,
                max_level=100,
                base_learning_rate=1.0,
                practice_activities=["carbon_farming", "soil_carbon_monitoring", "offset_programs"],
                income_multiplier=1.015  # Carbon credit income
            ),
            "sustainable_economics": Skill(
                skill_id="sustainable_economics",
                skill_name="Sustainable Agriculture Economics",
                description="Economic analysis of sustainable farming practices",
                category=SkillCategory.BUSINESS_MANAGEMENT,
                max_level=100,
                base_learning_rate=1.2,
                practice_activities=["cost_benefit_analysis", "grant_applications", "sustainability_reporting"],
                cost_reduction_per_level=0.008
            )
        }
        
        return SpecializationTrack(
            track_id="sustainable_agriculture_specialist",
            track_name="Sustainable Agriculture Specialist",
            description="Specialization in environmentally sustainable farming practices",
            specialization_type=SpecializationType.SUSTAINABLE_AGRICULTURE,
            core_skills=["conservation_practices", "biodiversity_management"],
            supporting_skills=["carbon_management", "sustainable_economics"],
            skill_definitions=sustainable_skills,
            market_focus=["sustainability_markets", "carbon_credits", "conservation_programs"],
            competitive_advantages=["environmental_benefits", "regulatory_compliance", "grant_access"],
            preferred_technologies=["conservation_equipment", "monitoring_systems"],
            technology_adoption_bonus=1.15,
            research_focus_areas=["conservation_agriculture", "ecosystem_services", "climate_adaptation"],
            initial_investment_cost=30000,
            ongoing_maintenance_cost_annual=3000,
            equipment_requirements=["no_till_drill", "cover_crop_seeder"],
            success_metrics={
                "soil_erosion_reduction": "Reduction in soil loss",
                "carbon_sequestration": "Annual carbon sequestered",
                "biodiversity_index": "On-farm biodiversity score"
            },
            benchmark_targets={
                "soil_erosion_reduction": 60.0,  # % reduction
                "carbon_sequestration": 2.0,     # tons CO2/ha/year
                "biodiversity_index": 75.0       # Biodiversity score
            }
        )
    
    def _create_agricultural_technology_track(self) -> SpecializationTrack:
        """Create agricultural technology specialization track"""
        
        # Define core skills for agricultural technology
        ag_tech_skills = {
            "equipment_technology": Skill(
                skill_id="equipment_technology",
                skill_name="Equipment Technology Management",
                description="Managing advanced agricultural equipment and systems",
                category=SkillCategory.TECHNICAL_SKILLS,
                max_level=100,
                base_learning_rate=1.2,
                practice_activities=["equipment_optimization", "technology_integration", "system_troubleshooting"],
                efficiency_bonus_per_level=0.025,
                cost_reduction_per_level=0.01
            ),
            "innovation_adoption": Skill(
                skill_id="innovation_adoption",
                skill_name="Agricultural Innovation Adoption",
                description="Identifying and adopting new agricultural technologies",
                category=SkillCategory.INNOVATION_ADOPTION,
                max_level=100,
                base_learning_rate=1.0,
                practice_activities=["technology_evaluation", "pilot_testing", "system_integration"],
                efficiency_bonus_per_level=0.02
            ),
            "automation_systems": Skill(
                skill_id="automation_systems",
                skill_name="Farm Automation Systems",
                description="Implementing and managing automated farming systems",
                category=SkillCategory.TECHNICAL_SKILLS,
                max_level=100,
                base_learning_rate=0.9,
                practice_activities=["automation_setup", "system_programming", "performance_monitoring"],
                efficiency_bonus_per_level=0.03,
                prerequisite_technologies=["autonomous_vehicles"]
            ),
            "technology_consulting": Skill(
                skill_id="technology_consulting",
                skill_name="Agricultural Technology Consulting",
                description="Providing technology advisory services to other farmers",
                category=SkillCategory.COMMUNICATION,
                max_level=100,
                base_learning_rate=0.8,
                practice_activities=["client_consultation", "system_design", "training_delivery"],
                income_multiplier=1.03
            )
        }
        
        return SpecializationTrack(
            track_id="agricultural_technology_specialist",
            track_name="Agricultural Technology Specialist",
            description="Specialization in agricultural equipment and technology innovation",
            specialization_type=SpecializationType.AGRICULTURAL_TECHNOLOGY,
            core_skills=["equipment_technology", "innovation_adoption"],
            supporting_skills=["automation_systems", "technology_consulting"],
            skill_definitions=ag_tech_skills,
            market_focus=["technology_services", "equipment_consulting", "innovation_adoption"],
            competitive_advantages=["early_adoption", "technical_expertise", "efficiency_optimization"],
            preferred_technologies=["autonomous_equipment", "robotics", "ai_systems"],
            technology_adoption_bonus=2.0,  # Double adoption rate
            research_focus_areas=["agricultural_robotics", "automation", "ai_applications"],
            initial_investment_cost=100000,
            ongoing_maintenance_cost_annual=15000,
            equipment_requirements=["advanced_tractors", "automation_systems", "computing_equipment"],
            success_metrics={
                "technology_adoption_rate": "Rate of new technology adoption",
                "equipment_efficiency": "Equipment utilization efficiency",
                "consulting_revenue": "Income from technology consulting"
            },
            benchmark_targets={
                "technology_adoption_rate": 80.0,   # % of available tech adopted
                "equipment_efficiency": 90.0,      # % utilization
                "consulting_revenue": 25000.0      # Annual consulting income
            }
        )
    
    def _setup_skill_activities(self):
        """Setup skill development activities"""
        # Define activities that develop specific skills
        skill_activities = {
            "planting_operations": {
                "name": "Planting Operations",
                "description": "Conducting crop planting activities",
                "skill_gains": {
                    "grain_crop_management": 2.0,
                    "large_equipment_operation": 1.5,
                    "precision_application": 1.0
                },
                "time_required_hours": 8,
                "seasonal_availability": ["spring"]
            },
            "harvest_operations": {
                "name": "Harvest Operations", 
                "description": "Conducting crop harvest activities",
                "skill_gains": {
                    "grain_crop_management": 2.5,
                    "large_equipment_operation": 2.0,
                    "grain_storage": 1.5
                },
                "time_required_hours": 10,
                "seasonal_availability": ["fall"]
            },
            "market_analysis": {
                "name": "Market Analysis",
                "description": "Analyzing commodity markets for trading decisions",
                "skill_gains": {
                    "commodity_marketing": 3.0,
                    "organic_marketing": 2.0,
                    "sustainable_economics": 1.0
                },
                "time_required_hours": 4,
                "seasonal_availability": ["winter", "spring", "summer", "fall"]
            },
            "technology_evaluation": {
                "name": "Technology Evaluation",
                "description": "Evaluating new agricultural technologies",
                "skill_gains": {
                    "innovation_adoption": 3.0,
                    "equipment_technology": 2.0,
                    "data_analytics": 1.5
                },
                "time_required_hours": 6,
                "seasonal_availability": ["winter", "spring"]
            }
        }
        
        self.skill_activities = skill_activities
        self.logger.info(f"Setup {len(skill_activities)} skill development activities")
    
    def _initialize_certification_system(self):
        """Initialize certification management system"""
        # Setup certification schedules and requirements
        for track in self.specialization_tracks.values():
            for cert_id, certification in track.certification_definitions.items():
                self.certification_definitions[cert_id] = certification
        
        self.logger.info("Certification system initialized")
    
    def _setup_market_integration(self):
        """Setup market access and premium pricing for specializations"""
        for track_id, track in self.specialization_tracks.items():
            self.specialization_market_access[track_id] = track.market_focus
            self.competitive_advantages[track_id] = track.competitive_advantages
        
        self.logger.info("Market integration setup completed")
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        if self.event_system:
            self.event_system.subscribe('activity_completed', self.handle_activity_completion)
            self.event_system.subscribe('certification_earned', self.handle_certification_earned)
            self.event_system.subscribe('skill_milestone_reached', self.handle_skill_milestone)
            self.event_system.subscribe('technology_adopted', self.handle_technology_adoption)
    
    # Core specialization management methods
    
    def start_specialization(self, track_id: str) -> Dict[str, Any]:
        """Start a new specialization track"""
        try:
            if track_id not in self.specialization_tracks:
                return {"success": False, "error": "Specialization track not found"}
            
            if track_id in self.player_specializations:
                return {"success": False, "error": "Already specialized in this track"}
            
            track = self.specialization_tracks[track_id]
            
            # Check investment requirements
            if track.initial_investment_cost > 0:
                # This would check player funds in a real implementation
                pass
            
            # Create player specialization record
            player_spec = PlayerSpecialization(
                track_id=track_id,
                start_date=datetime.now()
            )
            
            # Initialize skill levels
            for skill_id in track.core_skills + track.supporting_skills:
                player_spec.skill_levels[skill_id] = 0
                player_spec.skill_experience[skill_id] = 0.0
            
            self.player_specializations[track_id] = player_spec
            
            # Set as active specialization if none active
            if self.active_specialization is None:
                self.active_specialization = track_id
            
            # Record specialization start
            self.specialization_history.append({
                "action": "started",
                "track_id": track_id,
                "date": datetime.now(),
                "investment": track.initial_investment_cost
            })
            
            # Publish event
            if self.event_system:
                self.event_system.publish('specialization_started', {
                    'track_id': track_id,
                    'track_name': track.track_name
                })
            
            self.logger.info(f"Started specialization: {track.track_name}")
            
            return {"success": True, "specialization": player_spec}
            
        except Exception as e:
            self.logger.error(f"Error starting specialization {track_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def gain_skill_experience(self, skill_id: str, activity_id: str, 
                            time_invested: float = 1.0) -> Dict[str, Any]:
        """Gain experience in a skill through activity"""
        try:
            if skill_id not in self.skill_definitions:
                return {"success": False, "error": "Skill not found"}
            
            skill = self.skill_definitions[skill_id]
            
            # Find player specialization that includes this skill
            player_spec = None
            for spec in self.player_specializations.values():
                track = self.specialization_tracks[spec.track_id]
                if skill_id in (track.core_skills + track.supporting_skills):
                    player_spec = spec
                    break
            
            if not player_spec:
                return {"success": False, "error": "Skill not available in current specializations"}
            
            # Calculate experience gain
            current_level = player_spec.skill_levels.get(skill_id, 0)
            base_gain = skill.base_learning_rate * time_invested
            
            # Apply learning curve (diminishing returns)
            level_factor = skill.learning_curve_factor ** current_level
            
            # Apply learning efficiency bonuses
            efficiency_multiplier = self.learning_efficiency.get(skill_id, 1.0)
            
            final_gain = base_gain * level_factor * efficiency_multiplier
            
            # Update experience and check for level up
            current_experience = player_spec.skill_experience.get(skill_id, 0.0)
            new_experience = current_experience + final_gain
            
            # Calculate new level (every 100 experience = 1 level)
            new_level = min(int(new_experience / 100), skill.max_level)
            old_level = current_level
            
            # Update player specialization
            player_spec.skill_experience[skill_id] = new_experience
            player_spec.skill_levels[skill_id] = new_level
            player_spec.hours_invested += time_invested
            player_spec.practical_experience_hours += int(time_invested)
            
            # Update total skill points
            player_spec.total_skill_points = sum(player_spec.skill_levels.values())
            
            # Check for tier advancement
            tier_update = self._check_tier_advancement(player_spec)
            
            # Record activity
            player_spec.activities_completed.append({
                "activity_id": activity_id,
                "skill_id": skill_id,
                "date": datetime.now(),
                "time_invested": time_invested,
                "experience_gained": final_gain,
                "level_gained": new_level - old_level
            })
            
            result = {
                "success": True,
                "experience_gained": final_gain,
                "new_experience": new_experience,
                "old_level": old_level,
                "new_level": new_level,
                "level_up": new_level > old_level
            }
            
            # Add tier advancement info if applicable
            if tier_update:
                result["tier_advancement"] = tier_update
            
            # Publish events
            if self.event_system:
                self.event_system.publish('skill_experience_gained', {
                    'skill_id': skill_id,
                    'experience_gained': final_gain,
                    'new_level': new_level
                })
                
                if new_level > old_level:
                    self.event_system.publish('skill_level_up', {
                        'skill_id': skill_id,
                        'new_level': new_level,
                        'track_id': player_spec.track_id
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error gaining skill experience {skill_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_tier_advancement(self, player_spec: PlayerSpecialization) -> Optional[Dict[str, Any]]:
        """Check if player has advanced to a new specialization tier"""
        current_tier = player_spec.current_tier
        total_points = player_spec.total_skill_points
        
        # Determine new tier based on total skill points
        new_tier = current_tier
        if total_points >= 301:
            new_tier = SpecializationTier.MASTER
        elif total_points >= 151:
            new_tier = SpecializationTier.EXPERT
        elif total_points >= 76:
            new_tier = SpecializationTier.ADVANCED
        elif total_points >= 26:
            new_tier = SpecializationTier.INTERMEDIATE
        else:
            new_tier = SpecializationTier.NOVICE
        
        if new_tier != current_tier:
            # Tier advancement occurred
            player_spec.current_tier = new_tier
            
            # Apply tier benefits
            track = self.specialization_tracks[player_spec.track_id]
            tier_benefits = track.tier_benefits.get(new_tier, [])
            
            advancement_record = {
                "old_tier": current_tier.value,
                "new_tier": new_tier.value,
                "advancement_date": datetime.now(),
                "total_skill_points": total_points,
                "benefits_unlocked": [benefit.benefit_name for benefit in tier_benefits]
            }
            
            player_spec.milestones_achieved.append(advancement_record)
            
            # Publish tier advancement event
            if self.event_system:
                self.event_system.publish('specialization_tier_advanced', {
                    'track_id': player_spec.track_id,
                    'new_tier': new_tier.value,
                    'benefits': tier_benefits
                })
            
            self.logger.info(f"Tier advancement: {current_tier.value} -> {new_tier.value}")
            
            return advancement_record
        
        return None
    
    def apply_for_certification(self, certification_id: str) -> Dict[str, Any]:
        """Apply for professional certification"""
        try:
            if certification_id not in self.certification_definitions:
                return {"success": False, "error": "Certification not found"}
            
            certification = self.certification_definitions[certification_id]
            
            # Find relevant player specialization
            player_spec = None
            for spec in self.player_specializations.values():
                track = self.specialization_tracks[spec.track_id]
                if track.specialization_type == certification.specialization_required:
                    player_spec = spec
                    break
            
            if not player_spec:
                return {"success": False, "error": "Required specialization not found"}
            
            # Check requirements
            requirements_check = self._check_certification_requirements(certification, player_spec)
            if not requirements_check["eligible"]:
                return {"success": False, "error": "Requirements not met", 
                       "requirements": requirements_check["unmet_requirements"]}
            
            # Process application
            application_record = {
                "application_id": f"cert_app_{int(datetime.now().timestamp())}",
                "certification_id": certification_id,
                "applicant_specialization": player_spec.track_id,
                "application_date": datetime.now(),
                "application_cost": certification.application_cost,
                "status": "pending_review",
                "review_completion_date": datetime.now() + timedelta(days=30)
            }
            
            self.certification_applications.append(application_record)
            player_spec.pending_certifications.add(certification_id)
            
            # Deduct application cost (would integrate with economy system)
            # self.deduct_funds(certification.application_cost)
            
            self.logger.info(f"Certification application submitted: {certification.cert_name}")
            
            return {"success": True, "application": application_record}
            
        except Exception as e:
            self.logger.error(f"Error applying for certification {certification_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_certification_requirements(self, certification: Certification, 
                                        player_spec: PlayerSpecialization) -> Dict[str, Any]:
        """Check if player meets certification requirements"""
        requirements_check = {
            "eligible": True,
            "met_requirements": [],
            "unmet_requirements": []
        }
        
        # Check tier requirement
        if player_spec.current_tier.value < certification.minimum_tier.value:
            requirements_check["eligible"] = False
            requirements_check["unmet_requirements"].append({
                "requirement": "tier",
                "required": certification.minimum_tier.value,
                "current": player_spec.current_tier.value
            })
        else:
            requirements_check["met_requirements"].append("tier")
        
        # Check skill requirements
        for skill_id, required_level in certification.required_skills.items():
            current_level = player_spec.skill_levels.get(skill_id, 0)
            if current_level < required_level:
                requirements_check["eligible"] = False
                requirements_check["unmet_requirements"].append({
                    "requirement": f"skill_{skill_id}",
                    "required": required_level,
                    "current": current_level
                })
            else:
                requirements_check["met_requirements"].append(f"skill_{skill_id}")
        
        # Check experience points
        total_experience = sum(player_spec.skill_experience.values())
        if total_experience < certification.required_experience_points:
            requirements_check["eligible"] = False
            requirements_check["unmet_requirements"].append({
                "requirement": "experience_points",
                "required": certification.required_experience_points,
                "current": total_experience
            })
        else:
            requirements_check["met_requirements"].append("experience_points")
        
        # Check education hours
        if player_spec.education_hours_completed < certification.required_education_hours:
            requirements_check["eligible"] = False
            requirements_check["unmet_requirements"].append({
                "requirement": "education_hours",
                "required": certification.required_education_hours,
                "current": player_spec.education_hours_completed
            })
        else:
            requirements_check["met_requirements"].append("education_hours")
        
        return requirements_check
    
    # Query and reporting methods
    
    def get_specialization_progress_report(self, track_id: str) -> Dict[str, Any]:
        """Get detailed progress report for a specialization"""
        if track_id not in self.player_specializations:
            return {"error": "Specialization not active"}
        
        player_spec = self.player_specializations[track_id]
        track = self.specialization_tracks[track_id]
        
        report = {
            "specialization_info": {
                "track_name": track.track_name,
                "current_tier": player_spec.current_tier.value,
                "total_skill_points": player_spec.total_skill_points,
                "start_date": player_spec.start_date,
                "hours_invested": player_spec.hours_invested
            },
            "skill_progress": {},
            "tier_progress": {},
            "certification_status": {},
            "economic_impact": {},
            "next_milestones": []
        }
        
        # Skill progress details
        for skill_id in track.core_skills + track.supporting_skills:
            skill = track.skill_definitions.get(skill_id)
            if skill:
                current_level = player_spec.skill_levels.get(skill_id, 0)
                current_exp = player_spec.skill_experience.get(skill_id, 0.0)
                
                report["skill_progress"][skill_id] = {
                    "skill_name": skill.skill_name,
                    "current_level": current_level,
                    "max_level": skill.max_level,
                    "current_experience": current_exp,
                    "progress_to_next_level": (current_exp % 100) / 100.0,
                    "efficiency_bonus": current_level * skill.efficiency_bonus_per_level,
                    "quality_bonus": current_level * skill.quality_bonus_per_level
                }
        
        # Tier progress
        tier_points_required = {
            SpecializationTier.NOVICE: 0,
            SpecializationTier.INTERMEDIATE: 26,
            SpecializationTier.ADVANCED: 76,
            SpecializationTier.EXPERT: 151,
            SpecializationTier.MASTER: 301
        }
        
        current_tier_points = tier_points_required[player_spec.current_tier]
        next_tier_points = 301  # Default to master
        
        for tier, points in tier_points_required.items():
            if points > player_spec.total_skill_points:
                next_tier_points = points
                break
        
        report["tier_progress"] = {
            "current_tier": player_spec.current_tier.value,
            "current_points": player_spec.total_skill_points,
            "points_to_next_tier": max(0, next_tier_points - player_spec.total_skill_points),
            "progress_percentage": min(100, (player_spec.total_skill_points / next_tier_points) * 100)
        }
        
        # Certification status
        for cert_id in track.available_certifications:
            cert = track.certification_definitions.get(cert_id)
            if cert:
                requirements_check = self._check_certification_requirements(cert, player_spec)
                
                report["certification_status"][cert_id] = {
                    "certification_name": cert.cert_name,
                    "eligible": requirements_check["eligible"],
                    "active": cert_id in player_spec.active_certifications,
                    "pending": cert_id in player_spec.pending_certifications,
                    "requirements_met": len(requirements_check["met_requirements"]),
                    "total_requirements": len(requirements_check["met_requirements"]) + 
                                        len(requirements_check["unmet_requirements"])
                }
        
        # Economic impact
        report["economic_impact"] = {
            "specialization_income": player_spec.specialization_income,
            "premium_earnings": player_spec.premium_earnings,
            "cost_savings": player_spec.cost_savings,
            "total_benefit": (player_spec.specialization_income + 
                            player_spec.premium_earnings + 
                            player_spec.cost_savings),
            "roi_on_investment": 0  # Would calculate based on investment costs
        }
        
        return report
    
    def get_available_specializations(self) -> List[Dict[str, Any]]:
        """Get list of available specialization tracks"""
        available = []
        
        for track_id, track in self.specialization_tracks.items():
            track_info = {
                "track_id": track_id,
                "track_name": track.track_name,
                "description": track.description,
                "specialization_type": track.specialization_type.value,
                "initial_investment": track.initial_investment_cost,
                "annual_maintenance": track.ongoing_maintenance_cost_annual,
                "market_focus": track.market_focus,
                "competitive_advantages": track.competitive_advantages,
                "active": track_id in self.player_specializations,
                "skill_count": len(track.core_skills) + len(track.supporting_skills),
                "certification_count": len(track.available_certifications)
            }
            available.append(track_info)
        
        return available
    
    def get_skill_development_opportunities(self, skill_id: str) -> List[Dict[str, Any]]:
        """Get available activities for developing a specific skill"""
        opportunities = []
        
        for activity_id, activity in self.skill_activities.items():
            if skill_id in activity.get("skill_gains", {}):
                opportunity = {
                    "activity_id": activity_id,
                    "activity_name": activity["name"],
                    "description": activity["description"],
                    "skill_gain": activity["skill_gains"][skill_id],
                    "time_required": activity["time_required_hours"],
                    "seasonal_availability": activity.get("seasonal_availability", [])
                }
                opportunities.append(opportunity)
        
        return opportunities
    
    # Event handlers
    
    def handle_activity_completion(self, event_data: Dict[str, Any]):
        """Handle activity completion events"""
        try:
            activity_id = event_data.get("activity_id")
            time_invested = event_data.get("time_invested", 1.0)
            
            if activity_id in self.skill_activities:
                activity = self.skill_activities[activity_id]
                
                # Apply skill gains for all affected skills
                for skill_id, gain_amount in activity.get("skill_gains", {}).items():
                    self.gain_skill_experience(skill_id, activity_id, time_invested)
        
        except Exception as e:
            self.logger.error(f"Error handling activity completion: {e}")
    
    def handle_certification_earned(self, event_data: Dict[str, Any]):
        """Handle certification earned events"""
        try:
            cert_id = event_data.get("certification_id")
            track_id = event_data.get("track_id")
            
            if track_id in self.player_specializations:
                player_spec = self.player_specializations[track_id]
                player_spec.active_certifications.add(cert_id)
                player_spec.pending_certifications.discard(cert_id)
                
                # Record certification achievement
                cert_record = {
                    "certification_id": cert_id,
                    "date_earned": datetime.now(),
                    "track_id": track_id
                }
                player_spec.certification_history.append(cert_record)
                
                self.logger.info(f"Certification earned: {cert_id}")
        
        except Exception as e:
            self.logger.error(f"Error handling certification earned: {e}")
    
    def _create_basic_specialization_configuration(self):
        """Create minimal specialization configuration for fallback"""
        self.logger.warning("Creating basic specialization configuration")
        
        # Create basic track
        basic_skill = Skill(
            skill_id="basic_farming",
            skill_name="Basic Farming",
            description="Fundamental farming skills",
            category=SkillCategory.AGRONOMIC_KNOWLEDGE
        )
        
        basic_track = SpecializationTrack(
            track_id="general_farming",
            track_name="General Farming",
            description="General agricultural skills",
            specialization_type=SpecializationType.GRAIN_FARMING,
            core_skills=["basic_farming"],
            supporting_skills=[],
            skill_definitions={"basic_farming": basic_skill},
            market_focus=["general_agriculture"]
        )
        
        self.specialization_tracks["general_farming"] = basic_track
        self.skill_definitions["basic_farming"] = basic_skill


# Global convenience functions
specialization_tracks_instance = None

def get_specialization_tracks():
    """Get the global specialization tracks instance"""
    global specialization_tracks_instance
    if specialization_tracks_instance is None:
        specialization_tracks_instance = SpecializationTracks()
    return specialization_tracks_instance

def start_specialization(track_id: str):
    """Convenience function to start specialization"""
    return get_specialization_tracks().start_specialization(track_id)

def gain_skill_experience(skill_id: str, activity_id: str, time_invested: float = 1.0):
    """Convenience function to gain skill experience"""
    return get_specialization_tracks().gain_skill_experience(skill_id, activity_id, time_invested)

def get_specialization_progress(track_id: str):
    """Convenience function to get specialization progress"""
    return get_specialization_tracks().get_specialization_progress_report(track_id)

def get_available_specializations():
    """Convenience function to get available specializations"""
    return get_specialization_tracks().get_available_specializations()