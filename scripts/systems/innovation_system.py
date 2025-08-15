"""
Innovation System - Breakthrough Discoveries & Agricultural Innovation for AgriFun Agricultural Simulation

This system manages breakthrough discoveries, innovation diffusion, technology commercialization,
and disruptive agricultural innovations. It simulates how new technologies emerge, spread through
the agricultural community, and transform farming practices over time.

Key Features:
- Breakthrough Discovery Engine: Random and triggered innovation events
- Innovation Diffusion Model: Adoption curves and market penetration
- Technology Commercialization: From lab to market transformation
- Disruptive Innovation Impact: Game-changing technologies and paradigm shifts
- Innovation Networks: Collaboration between researchers, companies, and farmers
- Patent System: Intellectual property protection and licensing
- Technology Transfer: University-industry-farmer knowledge flow

Innovation Categories:
- Biological Innovations: New crop varieties, biological controls, genetic technologies
- Mechanical Innovations: Equipment improvements, automation, robotics
- Digital Innovations: Software, sensors, data analytics, AI applications
- Chemical Innovations: New pesticides, fertilizers, soil amendments
- Process Innovations: New farming methods, supply chain improvements
- Social Innovations: New business models, collaborative approaches

Educational Value:
- Understanding innovation cycles in agriculture
- Technology adoption decision-making processes
- Economic impact of agricultural innovations
- Role of research institutions and private companies
- Importance of early adoption vs. risk management
- Network effects and collaborative innovation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
import yaml
import random
import math


class InnovationType(Enum):
    """Types of agricultural innovations"""
    BIOLOGICAL = "biological"                           # Crop varieties, biotech, genetics
    MECHANICAL = "mechanical"                          # Equipment, machinery, tools
    DIGITAL = "digital"                               # Software, sensors, data systems
    CHEMICAL = "chemical"                             # Pesticides, fertilizers, amendments
    PROCESS = "process"                               # Methods, practices, systems
    SOCIAL = "social"                                 # Business models, collaboration
    SUSTAINABILITY = "sustainability"                 # Environmental solutions
    PRECISION = "precision"                           # Precision agriculture tech


class InnovationStage(Enum):
    """Stages of innovation development"""
    RESEARCH = "research"                             # Basic research phase
    DEVELOPMENT = "development"                       # Applied R&D phase
    PROTOTYPE = "prototype"                          # Working prototype created
    TESTING = "testing"                              # Field testing and validation
    COMMERCIALIZATION = "commercialization"         # Market launch preparation
    MARKET_INTRODUCTION = "market_introduction"     # Early market adoption
    GROWTH = "growth"                               # Expanding market adoption
    MATURITY = "maturity"                           # Mature technology
    DECLINE = "decline"                             # Being replaced by newer tech


class AdoptionCategory(Enum):
    """Technology adoption categories (Rogers' Diffusion of Innovation)"""
    INNOVATORS = "innovators"                        # 2.5% - Risk takers, well connected
    EARLY_ADOPTERS = "early_adopters"               # 13.5% - Opinion leaders, educated
    EARLY_MAJORITY = "early_majority"               # 34% - Deliberate, practical
    LATE_MAJORITY = "late_majority"                 # 34% - Skeptical, cautious
    LAGGARDS = "laggards"                           # 16% - Traditional, resistant


class InnovationImpact(Enum):
    """Impact level of innovations"""
    INCREMENTAL = "incremental"                      # Small improvements
    SUBSTANTIAL = "substantial"                      # Significant improvements
    BREAKTHROUGH = "breakthrough"                    # Major advances
    DISRUPTIVE = "disruptive"                       # Game-changing paradigm shifts


class PatentStatus(Enum):
    """Patent protection status"""
    PATENT_PENDING = "patent_pending"               # Application submitted
    PATENTED = "patented"                          # Patent granted
    PATENT_EXPIRED = "patent_expired"              # Patent protection ended
    PUBLIC_DOMAIN = "public_domain"                # No patent protection
    TRADE_SECRET = "trade_secret"                  # Protected as trade secret


@dataclass
class Innovation:
    """Individual innovation definition"""
    innovation_id: str
    innovation_name: str
    description: str
    innovation_type: InnovationType
    impact_level: InnovationImpact
    
    # Development information
    research_institution: str                        # Where it was developed
    lead_researcher: str                            # Principal investigator
    development_start_date: datetime
    commercial_launch_date: Optional[datetime] = None
    
    # Current status
    current_stage: InnovationStage = InnovationStage.RESEARCH
    development_progress: float = 0.0               # 0-1 completion
    market_readiness: float = 0.0                   # 0-1 readiness for market
    
    # Technical specifications
    technical_requirements: List[str] = field(default_factory=list)
    prerequisite_technologies: List[str] = field(default_factory=list)
    complementary_technologies: List[str] = field(default_factory=list)
    
    # Economic factors
    development_cost_total: float = 0               # Total R&D investment
    development_cost_remaining: float = 0           # Remaining development costs
    commercialization_cost: float = 0              # Cost to bring to market
    expected_market_size: float = 0                 # Potential market value
    price_point: float = 0                         # Expected selling price
    cost_to_produce: float = 0                     # Manufacturing/service cost
    
    # Adoption characteristics
    adoption_benefits: Dict[str, float] = field(default_factory=dict)  # Benefits offered
    adoption_barriers: List[str] = field(default_factory=list)         # Implementation challenges
    target_adopters: List[AdoptionCategory] = field(default_factory=list)
    learning_curve_difficulty: float = 0.5         # 0-1 (easy to difficult)
    network_effects: bool = False                   # Benefits increase with adoption
    
    # Patent protection
    patent_status: PatentStatus = PatentStatus.PUBLIC_DOMAIN
    patent_expiry_date: Optional[datetime] = None
    patent_holder: str = ""
    licensing_fee_percentage: float = 0.0           # % of revenue as licensing fee
    
    # Market diffusion
    adopter_count: int = 0                          # Current number of adopters
    adoption_rate: float = 0.0                      # Current adoption rate
    market_penetration: float = 0.0                 # % of potential market captured
    adoption_curve_parameters: Dict[str, float] = field(default_factory=dict)
    
    # Performance tracking
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    user_satisfaction: float = 0.0                  # User satisfaction score
    competitive_advantage: float = 0.0              # Advantage over alternatives
    
    # Innovation networks
    research_partnerships: List[str] = field(default_factory=list)
    commercial_partners: List[str] = field(default_factory=list)
    funding_sources: List[str] = field(default_factory=list)
    competitor_responses: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class InnovationProject:
    """Active innovation development project"""
    project_id: str
    innovation_id: str
    project_name: str
    project_type: str                               # "basic_research", "applied_research", "development"
    
    # Project management
    project_manager: str
    research_team: List[str]
    start_date: datetime
    planned_completion: datetime
    actual_completion: Optional[datetime] = None
    
    # Progress tracking
    current_phase: str
    phase_completion: float = 0.0                   # 0-1 completion of current phase
    overall_progress: float = 0.0                   # 0-1 overall project progress
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    
    # Resource allocation
    budget_allocated: float
    budget_spent: float
    personnel_hours_planned: float
    personnel_hours_actual: float
    
    # Risk management
    technical_risks: List[Dict[str, Any]] = field(default_factory=list)
    commercial_risks: List[Dict[str, Any]] = field(default_factory=list)
    regulatory_risks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Collaboration
    external_partners: List[str] = field(default_factory=list)
    industry_sponsors: List[str] = field(default_factory=list)
    government_funding: float = 0.0
    private_funding: float = 0.0
    
    # Outcomes
    publications: List[str] = field(default_factory=list)
    patents_filed: List[str] = field(default_factory=list)
    prototype_iterations: int = 0
    field_test_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AdoptionDecision:
    """Individual adoption decision record"""
    decision_id: str
    innovation_id: str
    adopter_id: str
    decision_date: datetime
    
    # Decision factors
    adoption_decision: bool                         # True = adopted, False = rejected
    decision_rationale: List[str]
    key_benefits_expected: List[str]
    key_concerns: List[str]
    
    # Economic analysis
    expected_roi: float
    payback_period_years: float
    initial_investment: float
    ongoing_costs_annual: float
    expected_benefits_annual: float
    
    # Risk assessment
    technical_risk_rating: float                    # 0-1 (low to high)
    economic_risk_rating: float
    operational_risk_rating: float
    overall_risk_tolerance: float
    
    # Social factors
    peer_influence_score: float                     # Influence of other adopters
    opinion_leader_endorsement: bool
    demonstration_effect_witnessed: bool
    social_pressure_to_adopt: float
    
    # Implementation
    implementation_date: Optional[datetime] = None
    training_required_hours: float = 0
    support_needed: List[str] = field(default_factory=list)
    integration_challenges: List[str] = field(default_factory=list)


@dataclass
class MarketDynamics:
    """Market dynamics for innovation diffusion"""
    innovation_id: str
    market_segment: str
    
    # Market characteristics
    total_addressable_market: int                   # Total potential adopters
    serviceable_market: int                         # Realistic target market
    current_market_size: int                        # Current active adopters
    market_growth_rate: float                       # Annual growth rate
    
    # Competitive landscape
    competing_innovations: List[str] = field(default_factory=list)
    market_share_distribution: Dict[str, float] = field(default_factory=dict)
    competitive_intensity: float = 0.5              # 0-1 competition level
    
    # Adoption dynamics
    adoption_threshold: float = 0.1                 # Critical mass threshold
    network_effects_strength: float = 0.0           # Network effect multiplier
    switching_costs: float = 0.0                    # Cost to switch technologies
    
    # Economic factors
    average_selling_price: float = 0.0
    price_elasticity: float = -1.0                  # Demand response to price
    cost_reduction_learning_rate: float = 0.2       # Cost reduction with volume
    
    # Market maturity
    market_maturity_stage: str = "emerging"         # emerging, growth, mature, declining
    dominant_design_established: bool = False
    standardization_level: float = 0.0              # 0-1 industry standardization


class InnovationSystem:
    """
    Comprehensive Innovation System for agricultural breakthrough discoveries
    
    This system simulates the complete innovation lifecycle from research discovery
    through market adoption, including breakthrough events, technology diffusion,
    and economic impacts on agricultural transformation.
    """
    
    def __init__(self, config_manager=None, event_system=None):
        """Initialize innovation system"""
        self.config_manager = config_manager
        self.event_system = event_system
        self.logger = logging.getLogger(__name__)
        
        # Core innovation data
        self.innovations: Dict[str, Innovation] = {}
        self.innovation_projects: Dict[str, InnovationProject] = {}
        self.adoption_decisions: List[AdoptionDecision] = []
        self.market_dynamics: Dict[str, MarketDynamics] = {}
        
        # Discovery and development
        self.research_pipeline: List[Dict[str, Any]] = []
        self.breakthrough_opportunities: List[Dict[str, Any]] = []
        self.failed_innovations: List[Dict[str, Any]] = []
        
        # Market adoption tracking
        self.adoption_curves: Dict[str, Dict[str, float]] = {}  # {innovation_id: {time: adoption_rate}}
        self.adopter_networks: Dict[str, Set[str]] = {}         # {innovation_id: {adopter_ids}}
        self.opinion_leaders: List[str] = []                    # Influential adopters
        
        # Economic impact
        self.innovation_investments: Dict[str, float] = {}      # {innovation_id: total_investment}
        self.innovation_revenues: Dict[str, float] = {}         # {innovation_id: total_revenue}
        self.economic_impact_metrics: Dict[str, Dict[str, float]] = {}
        
        # Innovation networks
        self.research_institutions: Dict[str, Dict[str, Any]] = {}
        self.commercial_organizations: Dict[str, Dict[str, Any]] = {}
        self.funding_agencies: Dict[str, Dict[str, Any]] = {}
        self.collaboration_networks: List[Dict[str, Any]] = []
        
        # System parameters
        self.innovation_rate: float = 0.1               # Base innovation discovery rate
        self.breakthrough_probability: float = 0.05     # Probability of breakthrough
        self.diffusion_speed: float = 1.0              # Base adoption speed multiplier
        self.market_responsiveness: float = 0.8         # Market response to innovations
        
        # Time tracking
        self.current_time: datetime = datetime.now()
        self.simulation_speed: float = 1.0              # Time acceleration factor
        
        # Initialize system
        self._initialize_innovation_system()
        
    def _initialize_innovation_system(self):
        """Initialize innovation system with base data"""
        try:
            self._setup_research_institutions()
            self._setup_innovation_categories()
            self._load_historical_innovations()
            self._initialize_market_dynamics()
            self._setup_adoption_networks()
            
            if self.event_system:
                self._subscribe_to_events()
                
            self.logger.info("Innovation System initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing innovation system: {e}")
            self._create_basic_innovation_configuration()
    
    def _setup_research_institutions(self):
        """Setup research institutions and organizations"""
        institutions = {
            "agricultural_university": {
                "name": "State Agricultural University",
                "type": "university",
                "research_focus": ["biological", "sustainability", "precision"],
                "funding_capacity": 5000000,
                "research_strength": 0.8,
                "collaboration_openness": 0.9
            },
            "corporate_rd": {
                "name": "AgroTech Corporation R&D",
                "type": "corporate",
                "research_focus": ["mechanical", "digital", "chemical"],
                "funding_capacity": 15000000,
                "research_strength": 0.9,
                "collaboration_openness": 0.6
            },
            "government_lab": {
                "name": "National Agricultural Research Institute",
                "type": "government",
                "research_focus": ["biological", "sustainability", "process"],
                "funding_capacity": 8000000,
                "research_strength": 0.7,
                "collaboration_openness": 0.8
            },
            "startup_incubator": {
                "name": "AgriTech Startup Incubator",
                "type": "startup",
                "research_focus": ["digital", "precision", "social"],
                "funding_capacity": 2000000,
                "research_strength": 0.6,
                "collaboration_openness": 0.95
            }
        }
        
        self.research_institutions = institutions
        self.logger.info(f"Setup {len(institutions)} research institutions")
    
    def _setup_innovation_categories(self):
        """Setup innovation category parameters"""
        # Define parameters for each innovation type
        self.innovation_category_parameters = {
            InnovationType.BIOLOGICAL: {
                "development_time_years": 8,
                "success_probability": 0.3,
                "market_potential": 100000000,
                "typical_adoption_time": 5,
                "regulatory_complexity": 0.9
            },
            InnovationType.MECHANICAL: {
                "development_time_years": 4,
                "success_probability": 0.6,
                "market_potential": 50000000,
                "typical_adoption_time": 3,
                "regulatory_complexity": 0.3
            },
            InnovationType.DIGITAL: {
                "development_time_years": 2,
                "success_probability": 0.7,
                "market_potential": 75000000,
                "typical_adoption_time": 2,
                "regulatory_complexity": 0.2
            },
            InnovationType.CHEMICAL: {
                "development_time_years": 10,
                "success_probability": 0.2,
                "market_potential": 200000000,
                "typical_adoption_time": 4,
                "regulatory_complexity": 0.95
            },
            InnovationType.PROCESS: {
                "development_time_years": 3,
                "success_probability": 0.5,
                "market_potential": 30000000,
                "typical_adoption_time": 6,
                "regulatory_complexity": 0.1
            },
            InnovationType.SOCIAL: {
                "development_time_years": 5,
                "success_probability": 0.4,
                "market_potential": 40000000,
                "typical_adoption_time": 8,
                "regulatory_complexity": 0.4
            }
        }
        
        self.logger.info("Innovation category parameters configured")
    
    def _load_historical_innovations(self):
        """Load historical agricultural innovations as examples"""
        
        # Define some key historical innovations
        historical_innovations = [
            {
                "innovation_id": "hybrid_corn",
                "innovation_name": "Hybrid Corn Varieties",
                "description": "Development of high-yielding hybrid corn through controlled breeding",
                "innovation_type": InnovationType.BIOLOGICAL,
                "impact_level": InnovationImpact.BREAKTHROUGH,
                "research_institution": "agricultural_university",
                "lead_researcher": "Dr. Agricultural Pioneer",
                "development_start_date": datetime(1920, 1, 1),
                "commercial_launch_date": datetime(1930, 1, 1),
                "current_stage": InnovationStage.MATURITY,
                "development_progress": 1.0,
                "market_readiness": 1.0,
                "adoption_benefits": {
                    "yield_increase": 25.0,
                    "uniformity_improvement": 40.0,
                    "predictable_performance": 30.0
                },
                "adopter_count": 500000,
                "market_penetration": 0.95
            },
            {
                "innovation_id": "gps_guidance",
                "innovation_name": "GPS Tractor Guidance Systems",
                "description": "Satellite-based navigation for precise field operations",
                "innovation_type": InnovationType.DIGITAL,
                "impact_level": InnovationImpact.BREAKTHROUGH,
                "research_institution": "corporate_rd",
                "lead_researcher": "Engineering Team Alpha",
                "development_start_date": datetime(1995, 1, 1),
                "commercial_launch_date": datetime(2000, 1, 1),
                "current_stage": InnovationStage.MATURITY,
                "development_progress": 1.0,
                "market_readiness": 1.0,
                "adoption_benefits": {
                    "overlap_reduction": 80.0,
                    "fuel_savings": 15.0,
                    "operator_fatigue_reduction": 60.0
                },
                "adopter_count": 150000,
                "market_penetration": 0.6
            },
            {
                "innovation_id": "bt_corn",
                "innovation_name": "Bt-Modified Corn",
                "description": "Genetically modified corn with built-in pest resistance",
                "innovation_type": InnovationType.BIOLOGICAL,
                "impact_level": InnovationImpact.DISRUPTIVE,
                "research_institution": "corporate_rd",
                "lead_researcher": "Biotech Development Team",
                "development_start_date": datetime(1985, 1, 1),
                "commercial_launch_date": datetime(1996, 1, 1),
                "current_stage": InnovationStage.GROWTH,
                "development_progress": 1.0,
                "market_readiness": 1.0,
                "patent_status": PatentStatus.PATENTED,
                "patent_expiry_date": datetime(2016, 1, 1),
                "adoption_benefits": {
                    "pesticide_reduction": 50.0,
                    "yield_protection": 15.0,
                    "labor_savings": 25.0
                },
                "adoption_barriers": [
                    "regulatory_approval", 
                    "consumer_acceptance", 
                    "seed_cost_premium"
                ],
                "adopter_count": 200000,
                "market_penetration": 0.7
            }
        ]
        
        # Convert to Innovation objects and add to system
        for innov_data in historical_innovations:
            innovation = Innovation(**innov_data)
            self.innovations[innovation.innovation_id] = innovation
            
            # Initialize market dynamics
            self._create_market_dynamics_for_innovation(innovation)
        
        self.logger.info(f"Loaded {len(historical_innovations)} historical innovations")
    
    def _create_market_dynamics_for_innovation(self, innovation: Innovation):
        """Create market dynamics record for an innovation"""
        # Estimate market size based on innovation type and impact
        base_market_size = self.innovation_category_parameters[innovation.innovation_type]["market_potential"]
        impact_multiplier = {
            InnovationImpact.INCREMENTAL: 0.1,
            InnovationImpact.SUBSTANTIAL: 0.3,
            InnovationImpact.BREAKTHROUGH: 0.7,
            InnovationImpact.DISRUPTIVE: 1.0
        }
        
        total_market = int(base_market_size * impact_multiplier[innovation.impact_level] / 1000000)  # Convert to adopter count
        
        market_dynamics = MarketDynamics(
            innovation_id=innovation.innovation_id,
            market_segment=innovation.innovation_type.value,
            total_addressable_market=total_market,
            serviceable_market=int(total_market * 0.6),  # 60% of TAM
            current_market_size=innovation.adopter_count,
            market_growth_rate=0.15,  # 15% annual growth
            competitive_intensity=0.5,
            adoption_threshold=max(1, int(total_market * 0.05)),  # 5% critical mass
            average_selling_price=innovation.price_point if innovation.price_point > 0 else 10000
        )
        
        self.market_dynamics[innovation.innovation_id] = market_dynamics
    
    def _initialize_market_dynamics(self):
        """Initialize market dynamics for all innovations"""
        for innovation in self.innovations.values():
            if innovation.innovation_id not in self.market_dynamics:
                self._create_market_dynamics_for_innovation(innovation)
    
    def _setup_adoption_networks(self):
        """Setup innovation adoption networks"""
        # Initialize adoption networks for each innovation
        for innovation_id in self.innovations.keys():
            self.adopter_networks[innovation_id] = set()
            self.adoption_curves[innovation_id] = {}
        
        # Define opinion leaders (early adopters with influence)
        self.opinion_leaders = [
            "progressive_farmer_1", "tech_savvy_farmer_2", "large_farm_operator_3",
            "agricultural_extension_agent", "equipment_dealer", "crop_consultant"
        ]
        
        self.logger.info("Adoption networks initialized")
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        if self.event_system:
            self.event_system.subscribe('research_completed', self.handle_research_completion)
            self.event_system.subscribe('technology_demonstrated', self.handle_technology_demonstration)
            self.event_system.subscribe('market_conditions_changed', self.handle_market_change)
            self.event_system.subscribe('regulatory_approval_granted', self.handle_regulatory_approval)
            self.event_system.subscribe('patent_filed', self.handle_patent_filing)
    
    # Core innovation discovery and development methods
    
    def generate_innovation_opportunity(self) -> Dict[str, Any]:
        """Generate a new innovation opportunity"""
        try:
            # Select innovation type based on current research focus
            innovation_types = list(InnovationType)
            weights = self._calculate_innovation_type_weights()
            innovation_type = random.choices(innovation_types, weights=weights)[0]
            
            # Determine impact level
            impact_weights = [0.5, 0.3, 0.15, 0.05]  # Incremental most common
            impact_level = random.choices(list(InnovationImpact), weights=impact_weights)[0]
            
            # Generate innovation details
            innovation_id = f"innovation_{int(self.current_time.timestamp())}_{random.randint(1000, 9999)}"
            
            # Get category parameters
            category_params = self.innovation_category_parameters[innovation_type]
            
            # Create innovation opportunity
            opportunity = {
                "innovation_id": innovation_id,
                "innovation_name": self._generate_innovation_name(innovation_type, impact_level),
                "description": self._generate_innovation_description(innovation_type, impact_level),
                "innovation_type": innovation_type,
                "impact_level": impact_level,
                "discovery_date": self.current_time,
                "estimated_development_time": category_params["development_time_years"],
                "success_probability": category_params["success_probability"],
                "estimated_market_potential": category_params["market_potential"],
                "research_institution": self._select_lead_institution(innovation_type),
                "initial_funding_required": self._estimate_development_cost(innovation_type, impact_level),
                "breakthrough_potential": impact_level in [InnovationImpact.BREAKTHROUGH, InnovationImpact.DISRUPTIVE]
            }
            
            self.breakthrough_opportunities.append(opportunity)
            
            # Publish discovery event
            if self.event_system:
                self.event_system.publish('innovation_opportunity_discovered', {
                    'opportunity': opportunity,
                    'breakthrough_potential': opportunity["breakthrough_potential"]
                })
            
            self.logger.info(f"Innovation opportunity discovered: {opportunity['innovation_name']}")
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error generating innovation opportunity: {e}")
            return {}
    
    def start_innovation_project(self, opportunity: Dict[str, Any], 
                                funding_amount: float) -> Dict[str, Any]:
        """Start development of an innovation opportunity"""
        try:
            if funding_amount < opportunity.get("initial_funding_required", 0):
                return {"success": False, "error": "Insufficient funding"}
            
            # Create innovation record
            innovation = Innovation(
                innovation_id=opportunity["innovation_id"],
                innovation_name=opportunity["innovation_name"],
                description=opportunity["description"],
                innovation_type=opportunity["innovation_type"],
                impact_level=opportunity["impact_level"],
                research_institution=opportunity["research_institution"],
                lead_researcher=f"Lead Researcher {random.randint(1, 100)}",
                development_start_date=self.current_time,
                current_stage=InnovationStage.RESEARCH,
                development_cost_total=opportunity["initial_funding_required"],
                development_cost_remaining=opportunity["initial_funding_required"],
                expected_market_size=opportunity["estimated_market_potential"]
            )
            
            # Create innovation project
            project_id = f"proj_{innovation.innovation_id}"
            project = InnovationProject(
                project_id=project_id,
                innovation_id=innovation.innovation_id,
                project_name=f"Development: {innovation.innovation_name}",
                project_type="applied_research",
                project_manager=innovation.lead_researcher,
                research_team=[f"Researcher {i}" for i in range(3, 8)],  # 3-7 team members
                start_date=self.current_time,
                planned_completion=self.current_time + timedelta(
                    days=int(opportunity["estimated_development_time"] * 365)
                ),
                budget_allocated=funding_amount,
                budget_spent=0
            )
            
            # Add to system
            self.innovations[innovation.innovation_id] = innovation
            self.innovation_projects[project_id] = project
            self.innovation_investments[innovation.innovation_id] = funding_amount
            
            # Create market dynamics
            self._create_market_dynamics_for_innovation(innovation)
            
            # Remove from opportunities
            self.breakthrough_opportunities = [
                opp for opp in self.breakthrough_opportunities 
                if opp["innovation_id"] != innovation.innovation_id
            ]
            
            # Publish project start event
            if self.event_system:
                self.event_system.publish('innovation_project_started', {
                    'innovation': innovation,
                    'project': project,
                    'funding': funding_amount
                })
            
            self.logger.info(f"Innovation project started: {innovation.innovation_name}")
            
            return {"success": True, "innovation": innovation, "project": project}
            
        except Exception as e:
            self.logger.error(f"Error starting innovation project: {e}")
            return {"success": False, "error": str(e)}
    
    def advance_innovation_development(self, innovation_id: str, 
                                     time_advance_months: int = 1) -> Dict[str, Any]:
        """Advance development of an innovation over time"""
        try:
            if innovation_id not in self.innovations:
                return {"success": False, "error": "Innovation not found"}
            
            innovation = self.innovations[innovation_id]
            
            # Find associated project
            project = None
            for proj in self.innovation_projects.values():
                if proj.innovation_id == innovation_id and proj.actual_completion is None:
                    project = proj
                    break
            
            if not project:
                return {"success": False, "error": "No active project found"}
            
            # Calculate development progress
            category_params = self.innovation_category_parameters[innovation.innovation_type]
            base_progress_rate = 1.0 / (category_params["development_time_years"] * 12)  # Monthly progress
            
            # Apply various factors
            institution_efficiency = self.research_institutions[innovation.research_institution]["research_strength"]
            funding_adequacy = min(1.0, project.budget_allocated / innovation.development_cost_total)
            
            # Random variation and breakthrough chances
            random_factor = random.uniform(0.5, 1.5)
            breakthrough_bonus = 1.0
            
            if random.random() < self.breakthrough_probability:
                breakthrough_bonus = 2.0
                project.milestones.append({
                    "milestone": "research_breakthrough",
                    "date": self.current_time,
                    "description": "Unexpected research breakthrough accelerated development",
                    "impact": "2x progress for this period"
                })
            
            # Calculate final progress increment
            progress_increment = (base_progress_rate * time_advance_months * 
                                institution_efficiency * funding_adequacy * 
                                random_factor * breakthrough_bonus)
            
            # Update progress
            old_progress = innovation.development_progress
            innovation.development_progress = min(1.0, innovation.development_progress + progress_increment)
            project.overall_progress = innovation.development_progress
            
            # Update stage based on progress
            old_stage = innovation.current_stage
            new_stage = self._determine_development_stage(innovation.development_progress)
            
            if new_stage != old_stage:
                innovation.current_stage = new_stage
                project.milestones.append({
                    "milestone": f"stage_transition",
                    "date": self.current_time,
                    "description": f"Transitioned from {old_stage.value} to {new_stage.value}",
                    "stage_from": old_stage.value,
                    "stage_to": new_stage.value
                })
            
            # Update costs
            monthly_cost = innovation.development_cost_total / (category_params["development_time_years"] * 12)
            cost_this_period = monthly_cost * time_advance_months
            project.budget_spent += cost_this_period
            innovation.development_cost_remaining = max(0, innovation.development_cost_remaining - cost_this_period)
            
            # Check for completion
            completion_result = None
            if innovation.development_progress >= 1.0:
                completion_result = self._complete_innovation_development(innovation_id)
            
            # Check for failure
            failure_result = None
            if random.random() > category_params["success_probability"]:
                failure_chance = (1.0 - category_params["success_probability"]) * 0.1 * time_advance_months
                if random.random() < failure_chance:
                    failure_result = self._fail_innovation_project(innovation_id)
            
            result = {
                "success": True,
                "progress_increment": progress_increment,
                "new_progress": innovation.development_progress,
                "stage_change": new_stage != old_stage,
                "new_stage": new_stage.value if new_stage != old_stage else None,
                "cost_incurred": cost_this_period,
                "breakthrough_occurred": breakthrough_bonus > 1.0
            }
            
            if completion_result:
                result["completed"] = completion_result
            
            if failure_result:
                result["failed"] = failure_result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error advancing innovation development {innovation_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _determine_development_stage(self, progress: float) -> InnovationStage:
        """Determine development stage based on progress"""
        if progress < 0.1:
            return InnovationStage.RESEARCH
        elif progress < 0.3:
            return InnovationStage.DEVELOPMENT
        elif progress < 0.5:
            return InnovationStage.PROTOTYPE
        elif progress < 0.7:
            return InnovationStage.TESTING
        elif progress < 0.9:
            return InnovationStage.COMMERCIALIZATION
        else:
            return InnovationStage.MARKET_INTRODUCTION
    
    def _complete_innovation_development(self, innovation_id: str) -> Dict[str, Any]:
        """Complete innovation development and prepare for market launch"""
        innovation = self.innovations[innovation_id]
        
        # Update innovation status
        innovation.current_stage = InnovationStage.MARKET_INTRODUCTION
        innovation.commercial_launch_date = self.current_time
        innovation.market_readiness = 1.0
        
        # Set pricing
        category_params = self.innovation_category_parameters[innovation.innovation_type]
        base_price = category_params["market_potential"] / 10000  # Estimate based on market size
        impact_multiplier = {
            InnovationImpact.INCREMENTAL: 0.8,
            InnovationImpact.SUBSTANTIAL: 1.0,
            InnovationImpact.BREAKTHROUGH: 1.5,
            InnovationImpact.DISRUPTIVE: 2.0
        }
        innovation.price_point = base_price * impact_multiplier[innovation.impact_level]
        innovation.cost_to_produce = innovation.price_point * 0.6  # 60% of selling price
        
        # Initialize adoption tracking
        self.adopter_networks[innovation_id] = set()
        self.adoption_curves[innovation_id] = {0: 0.0}
        
        # Find and complete project
        for project in self.innovation_projects.values():
            if project.innovation_id == innovation_id and project.actual_completion is None:
                project.actual_completion = self.current_time
                break
        
        completion_record = {
            "innovation_id": innovation_id,
            "innovation_name": innovation.innovation_name,
            "completion_date": self.current_time,
            "development_duration_days": (self.current_time - innovation.development_start_date).days,
            "total_development_cost": innovation.development_cost_total,
            "market_ready": True
        }
        
        # Publish completion event
        if self.event_system:
            self.event_system.publish('innovation_development_completed', {
                'innovation': innovation,
                'completion_record': completion_record
            })
        
        self.logger.info(f"Innovation development completed: {innovation.innovation_name}")
        
        return completion_record
    
    def _fail_innovation_project(self, innovation_id: str) -> Dict[str, Any]:
        """Handle innovation project failure"""
        innovation = self.innovations[innovation_id]
        
        # Record failure
        failure_record = {
            "innovation_id": innovation_id,
            "innovation_name": innovation.innovation_name,
            "failure_date": self.current_time,
            "development_progress": innovation.development_progress,
            "resources_invested": innovation.development_cost_total - innovation.development_cost_remaining,
            "failure_reasons": ["technical_challenges", "insufficient_funding", "market_changes"]
        }
        
        self.failed_innovations.append(failure_record)
        
        # Remove from active innovations
        del self.innovations[innovation_id]
        
        # Mark projects as failed
        for project in self.innovation_projects.values():
            if project.innovation_id == innovation_id and project.actual_completion is None:
                project.actual_completion = self.current_time
                project.milestones.append({
                    "milestone": "project_failure",
                    "date": self.current_time,
                    "description": "Project terminated due to technical/commercial challenges"
                })
        
        # Publish failure event
        if self.event_system:
            self.event_system.publish('innovation_project_failed', {
                'failure_record': failure_record
            })
        
        self.logger.info(f"Innovation project failed: {innovation.innovation_name}")
        
        return failure_record
    
    # Market adoption and diffusion methods
    
    def simulate_adoption_decision(self, innovation_id: str, potential_adopter_id: str) -> Dict[str, Any]:
        """Simulate an individual adoption decision"""
        try:
            if innovation_id not in self.innovations:
                return {"success": False, "error": "Innovation not found"}
            
            innovation = self.innovations[innovation_id]
            
            # Skip if innovation not market ready
            if innovation.current_stage not in [InnovationStage.MARKET_INTRODUCTION, 
                                               InnovationStage.GROWTH, InnovationStage.MATURITY]:
                return {"success": False, "error": "Innovation not available for adoption"}
            
            # Skip if already adopted
            if potential_adopter_id in self.adopter_networks[innovation_id]:
                return {"success": False, "error": "Already adopted"}
            
            # Calculate adoption decision factors
            decision_factors = self._calculate_adoption_factors(innovation, potential_adopter_id)
            
            # Make adoption decision using logistic function
            adoption_probability = self._calculate_adoption_probability(decision_factors)
            adoption_decision = random.random() < adoption_probability
            
            # Create adoption decision record
            decision_record = AdoptionDecision(
                decision_id=f"decision_{innovation_id}_{potential_adopter_id}_{int(self.current_time.timestamp())}",
                innovation_id=innovation_id,
                adopter_id=potential_adopter_id,
                decision_date=self.current_time,
                adoption_decision=adoption_decision,
                decision_rationale=decision_factors["key_reasons"],
                key_benefits_expected=list(innovation.adoption_benefits.keys()),
                key_concerns=innovation.adoption_barriers,
                expected_roi=decision_factors["expected_roi"],
                payback_period_years=decision_factors["payback_period"],
                initial_investment=innovation.price_point,
                peer_influence_score=decision_factors["peer_influence"],
                technical_risk_rating=decision_factors["technical_risk"],
                economic_risk_rating=decision_factors["economic_risk"]
            )
            
            self.adoption_decisions.append(decision_record)
            
            # Update adoption tracking if adopted
            if adoption_decision:
                self.adopter_networks[innovation_id].add(potential_adopter_id)
                innovation.adopter_count += 1
                
                # Update market penetration
                market_dynamics = self.market_dynamics[innovation_id]
                innovation.market_penetration = (innovation.adopter_count / 
                                               market_dynamics.serviceable_market)
                
                # Record revenue
                if innovation_id not in self.innovation_revenues:
                    self.innovation_revenues[innovation_id] = 0
                self.innovation_revenues[innovation_id] += innovation.price_point
            
            # Publish adoption event
            if self.event_system:
                self.event_system.publish('adoption_decision_made', {
                    'decision_record': decision_record,
                    'adopted': adoption_decision
                })
            
            return {"success": True, "adopted": adoption_decision, "decision": decision_record}
            
        except Exception as e:
            self.logger.error(f"Error simulating adoption decision: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_adoption_factors(self, innovation: Innovation, adopter_id: str) -> Dict[str, Any]:
        """Calculate factors influencing adoption decision"""
        
        # Economic factors
        expected_benefits = sum(innovation.adoption_benefits.values()) * 100  # Convert to dollars
        expected_roi = expected_benefits / innovation.price_point if innovation.price_point > 0 else 1.0
        payback_period = innovation.price_point / expected_benefits if expected_benefits > 0 else 10
        
        # Risk factors
        technical_risk = innovation.learning_curve_difficulty
        economic_risk = 1.0 - min(1.0, expected_roi / 2.0)  # Higher risk if low ROI
        
        # Social factors
        current_adopters = len(self.adopter_networks[innovation.innovation_id])
        market_dynamics = self.market_dynamics[innovation.innovation_id]
        
        # Peer influence increases with adoption but plateaus
        peer_influence = min(0.8, current_adopters / market_dynamics.adoption_threshold)
        
        # Opinion leader influence
        opinion_leader_influence = 0.0
        for leader in self.opinion_leaders:
            if leader in self.adopter_networks[innovation.innovation_id]:
                opinion_leader_influence = 0.3
                break
        
        # Innovation characteristics
        relative_advantage = sum(innovation.adoption_benefits.values()) / 100  # Normalize
        compatibility = 1.0 - len(innovation.adoption_barriers) * 0.1  # More barriers = less compatible
        complexity = innovation.learning_curve_difficulty
        observability = 0.8 if innovation.innovation_type == InnovationType.MECHANICAL else 0.6
        
        # Key decision reasons
        key_reasons = []
        if expected_roi > 2.0:
            key_reasons.append("high_roi_potential")
        if payback_period < 3:
            key_reasons.append("short_payback_period")
        if peer_influence > 0.3:
            key_reasons.append("peer_adoption")
        if opinion_leader_influence > 0:
            key_reasons.append("opinion_leader_endorsement")
        if relative_advantage > 0.2:
            key_reasons.append("significant_benefits")
        
        return {
            "expected_roi": expected_roi,
            "payback_period": payback_period,
            "technical_risk": technical_risk,
            "economic_risk": economic_risk,
            "peer_influence": peer_influence,
            "opinion_leader_influence": opinion_leader_influence,
            "relative_advantage": relative_advantage,
            "compatibility": compatibility,
            "complexity": complexity,
            "observability": observability,
            "key_reasons": key_reasons
        }
    
    def _calculate_adoption_probability(self, factors: Dict[str, Any]) -> float:
        """Calculate probability of adoption using multi-factor model"""
        
        # Economic utility
        economic_utility = min(1.0, factors["expected_roi"] / 3.0) - factors["economic_risk"]
        
        # Social influence
        social_influence = (factors["peer_influence"] + factors["opinion_leader_influence"])
        
        # Innovation characteristics (Rogers' attributes)
        innovation_attractiveness = (
            factors["relative_advantage"] +
            factors["compatibility"] +
            (1.0 - factors["complexity"]) +
            factors["observability"]
        ) / 4.0
        
        # Risk tolerance
        risk_factor = 1.0 - (factors["technical_risk"] + factors["economic_risk"]) / 2.0
        
        # Combine factors
        utility_score = (
            economic_utility * 0.4 +
            social_influence * 0.25 +
            innovation_attractiveness * 0.25 +
            risk_factor * 0.1
        )
        
        # Convert to probability using logistic function
        probability = 1.0 / (1.0 + math.exp(-5 * (utility_score - 0.5)))
        
        return max(0.0, min(1.0, probability))
    
    def simulate_market_diffusion(self, innovation_id: str, time_period_months: int = 1) -> Dict[str, Any]:
        """Simulate market diffusion over time period"""
        try:
            if innovation_id not in self.innovations:
                return {"success": False, "error": "Innovation not found"}
            
            innovation = self.innovations[innovation_id]
            market_dynamics = self.market_dynamics[innovation_id]
            
            # Skip if not market ready
            if innovation.current_stage not in [InnovationStage.MARKET_INTRODUCTION, 
                                               InnovationStage.GROWTH, InnovationStage.MATURITY]:
                return {"success": False, "error": "Innovation not in market"}
            
            diffusion_results = {
                "period_start_adopters": innovation.adopter_count,
                "new_adopters": 0,
                "period_end_adopters": innovation.adopter_count,
                "adoption_rate": 0.0,
                "market_penetration": innovation.market_penetration,
                "stage_transitions": []
            }
            
            # Calculate potential adopters for this period
            remaining_market = market_dynamics.serviceable_market - innovation.adopter_count
            if remaining_market <= 0:
                return {"success": True, "diffusion_results": diffusion_results}
            
            # Bass diffusion model parameters
            coefficient_innovation = 0.03  # Innovativeness coefficient
            coefficient_imitation = 0.38   # Imitation coefficient
            
            # Current adoption rate
            m = market_dynamics.serviceable_market
            current_adopters = innovation.adopter_count
            
            # Bass model adoption rate
            adoption_rate = (coefficient_innovation + 
                           (coefficient_imitation * current_adopters / m)) * remaining_market
            
            # Apply time period and various adjustments
            period_multiplier = time_period_months / 12.0
            innovation_factors = self._get_innovation_diffusion_factors(innovation)
            market_factors = self._get_market_diffusion_factors(market_dynamics)
            
            adjusted_adoption_rate = (adoption_rate * period_multiplier * 
                                     innovation_factors * market_factors)
            
            # Simulate individual adoption decisions
            potential_adopters = max(1, int(adjusted_adoption_rate))
            new_adopters = 0
            
            for i in range(potential_adopters):
                adopter_id = f"adopter_{innovation_id}_{current_adopters + new_adopters + 1}"
                adoption_result = self.simulate_adoption_decision(innovation_id, adopter_id)
                
                if adoption_result.get("success") and adoption_result.get("adopted"):
                    new_adopters += 1
            
            # Update results
            diffusion_results["new_adopters"] = new_adopters
            diffusion_results["period_end_adopters"] = innovation.adopter_count
            diffusion_results["adoption_rate"] = new_adopters / remaining_market if remaining_market > 0 else 0
            diffusion_results["market_penetration"] = innovation.market_penetration
            
            # Check for stage transitions
            old_stage = innovation.current_stage
            new_stage = self._determine_market_stage(innovation, market_dynamics)
            
            if new_stage != old_stage:
                innovation.current_stage = new_stage
                diffusion_results["stage_transitions"].append({
                    "from_stage": old_stage.value,
                    "to_stage": new_stage.value,
                    "transition_date": self.current_time
                })
            
            # Update adoption curve
            current_time_key = int((self.current_time - innovation.commercial_launch_date).days / 30)
            self.adoption_curves[innovation_id][current_time_key] = innovation.market_penetration
            
            # Publish diffusion event
            if self.event_system:
                self.event_system.publish('market_diffusion_update', {
                    'innovation_id': innovation_id,
                    'diffusion_results': diffusion_results
                })
            
            return {"success": True, "diffusion_results": diffusion_results}
            
        except Exception as e:
            self.logger.error(f"Error simulating market diffusion: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_innovation_diffusion_factors(self, innovation: Innovation) -> float:
        """Get factors that affect innovation diffusion speed"""
        factors = 1.0
        
        # Impact level affects adoption speed
        impact_multipliers = {
            InnovationImpact.INCREMENTAL: 0.8,
            InnovationImpact.SUBSTANTIAL: 1.0,
            InnovationImpact.BREAKTHROUGH: 1.3,
            InnovationImpact.DISRUPTIVE: 0.7  # Slower initially due to resistance
        }
        factors *= impact_multipliers.get(innovation.impact_level, 1.0)
        
        # Learning curve difficulty affects adoption
        factors *= (1.1 - innovation.learning_curve_difficulty)
        
        # Network effects accelerate adoption
        if innovation.network_effects:
            network_multiplier = 1.0 + (innovation.market_penetration * 0.5)
            factors *= network_multiplier
        
        return factors
    
    def _get_market_diffusion_factors(self, market_dynamics: MarketDynamics) -> float:
        """Get market factors that affect diffusion speed"""
        factors = 1.0
        
        # Market growth affects adoption
        factors *= (1.0 + market_dynamics.market_growth_rate)
        
        # Competitive intensity can slow adoption
        factors *= (1.1 - market_dynamics.competitive_intensity * 0.1)
        
        # Market maturity affects adoption patterns
        maturity_multipliers = {
            "emerging": 1.2,
            "growth": 1.0,
            "mature": 0.8,
            "declining": 0.6
        }
        factors *= maturity_multipliers.get(market_dynamics.market_maturity_stage, 1.0)
        
        return factors
    
    def _determine_market_stage(self, innovation: Innovation, 
                               market_dynamics: MarketDynamics) -> InnovationStage:
        """Determine current market stage based on adoption"""
        penetration = innovation.market_penetration
        
        if penetration < 0.05:  # Less than 5%
            return InnovationStage.MARKET_INTRODUCTION
        elif penetration < 0.5:  # Less than 50%
            return InnovationStage.GROWTH
        elif penetration < 0.9:  # Less than 90%
            return InnovationStage.MATURITY
        else:
            return InnovationStage.DECLINE
    
    # Helper and utility methods
    
    def _calculate_innovation_type_weights(self) -> List[float]:
        """Calculate weights for innovation type selection based on current focus"""
        # For now, equal weights - could be made more sophisticated
        return [1.0] * len(InnovationType)
    
    def _generate_innovation_name(self, innovation_type: InnovationType, 
                                 impact_level: InnovationImpact) -> str:
        """Generate a name for an innovation"""
        
        type_prefixes = {
            InnovationType.BIOLOGICAL: ["Bio", "Genetic", "Organic", "Natural"],
            InnovationType.MECHANICAL: ["Smart", "Automated", "Precision", "Advanced"],
            InnovationType.DIGITAL: ["AI", "Smart", "Connected", "Digital"],
            InnovationType.CHEMICAL: ["Enhanced", "Advanced", "Targeted", "Optimized"],
            InnovationType.PROCESS: ["Integrated", "Streamlined", "Optimized", "Efficient"],
            InnovationType.SOCIAL: ["Collaborative", "Community", "Shared", "Network"]
        }
        
        type_bases = {
            InnovationType.BIOLOGICAL: ["Crop System", "Breeding Platform", "Biocontrol", "Genetic Tool"],
            InnovationType.MECHANICAL: ["Equipment", "Harvester", "Planter", "Automation System"],
            InnovationType.DIGITAL: ["Platform", "Analytics", "Monitoring System", "App"],
            InnovationType.CHEMICAL: ["Fertilizer", "Pesticide", "Amendment", "Treatment"],
            InnovationType.PROCESS: ["Method", "System", "Process", "Approach"],
            InnovationType.SOCIAL: ["Platform", "Network", "Cooperative", "Service"]
        }
        
        impact_modifiers = {
            InnovationImpact.INCREMENTAL: ["Plus", "Enhanced", "Improved"],
            InnovationImpact.SUBSTANTIAL: ["Pro", "Advanced", "Superior"],
            InnovationImpact.BREAKTHROUGH: ["Revolution", "Breakthrough", "Next-Gen"],
            InnovationImpact.DISRUPTIVE: ["Disruptor", "Game-Changer", "Paradigm"]
        }
        
        prefix = random.choice(type_prefixes[innovation_type])
        base = random.choice(type_bases[innovation_type])
        modifier = random.choice(impact_modifiers[impact_level])
        
        return f"{prefix} {base} {modifier}"
    
    def _generate_innovation_description(self, innovation_type: InnovationType, 
                                       impact_level: InnovationImpact) -> str:
        """Generate a description for an innovation"""
        
        type_descriptions = {
            InnovationType.BIOLOGICAL: "biotechnology solution for enhanced crop performance",
            InnovationType.MECHANICAL: "mechanical innovation for improved farming efficiency",
            InnovationType.DIGITAL: "digital technology for data-driven agriculture",
            InnovationType.CHEMICAL: "chemical innovation for optimized crop protection",
            InnovationType.PROCESS: "process innovation for streamlined operations",
            InnovationType.SOCIAL: "social innovation for collaborative agriculture"
        }
        
        impact_descriptions = {
            InnovationImpact.INCREMENTAL: "providing modest improvements to current practices",
            InnovationImpact.SUBSTANTIAL: "offering significant advantages over existing solutions",
            InnovationImpact.BREAKTHROUGH: "delivering breakthrough capabilities and performance",
            InnovationImpact.DISRUPTIVE: "fundamentally transforming agricultural practices"
        }
        
        type_desc = type_descriptions[innovation_type]
        impact_desc = impact_descriptions[impact_level]
        
        return f"Innovative {type_desc} {impact_desc}."
    
    def _select_lead_institution(self, innovation_type: InnovationType) -> str:
        """Select lead research institution based on innovation type"""
        
        # Filter institutions by research focus
        suitable_institutions = []
        for inst_id, institution in self.research_institutions.items():
            if innovation_type.value in institution["research_focus"]:
                suitable_institutions.append((inst_id, institution["research_strength"]))
        
        if not suitable_institutions:
            suitable_institutions = list(self.research_institutions.items())
        
        # Weight by research strength
        weights = [inst[1] if isinstance(inst[1], (int, float)) else inst[1]["research_strength"] 
                  for inst in suitable_institutions]
        
        institution_ids = [inst[0] if isinstance(inst[0], str) else inst[0] 
                          for inst in suitable_institutions]
        
        return random.choices(institution_ids, weights=weights)[0]
    
    def _estimate_development_cost(self, innovation_type: InnovationType, 
                                  impact_level: InnovationImpact) -> float:
        """Estimate development cost for innovation"""
        
        base_costs = {
            InnovationType.BIOLOGICAL: 2000000,
            InnovationType.MECHANICAL: 1000000,
            InnovationType.DIGITAL: 500000,
            InnovationType.CHEMICAL: 5000000,
            InnovationType.PROCESS: 300000,
            InnovationType.SOCIAL: 200000
        }
        
        impact_multipliers = {
            InnovationImpact.INCREMENTAL: 0.5,
            InnovationImpact.SUBSTANTIAL: 1.0,
            InnovationImpact.BREAKTHROUGH: 2.0,
            InnovationImpact.DISRUPTIVE: 4.0
        }
        
        base_cost = base_costs.get(innovation_type, 1000000)
        multiplier = impact_multipliers.get(impact_level, 1.0)
        
        return base_cost * multiplier * random.uniform(0.7, 1.5)  # Add variation
    
    # Query and reporting methods
    
    def get_innovation_portfolio_report(self) -> Dict[str, Any]:
        """Get comprehensive innovation portfolio report"""
        
        report = {
            "summary": {
                "total_innovations": len(self.innovations),
                "active_projects": len([p for p in self.innovation_projects.values() 
                                      if p.actual_completion is None]),
                "market_ready_innovations": len([i for i in self.innovations.values() 
                                               if i.current_stage in [InnovationStage.MARKET_INTRODUCTION,
                                                                    InnovationStage.GROWTH, 
                                                                    InnovationStage.MATURITY]]),
                "total_investment": sum(self.innovation_investments.values()),
                "total_revenue": sum(self.innovation_revenues.values()),
                "failed_projects": len(self.failed_innovations)
            },
            "by_type": {},
            "by_stage": {},
            "by_impact": {},
            "top_performers": [],
            "adoption_leaders": [],
            "market_trends": {}
        }
        
        # Analysis by innovation type
        for innovation_type in InnovationType:
            type_innovations = [i for i in self.innovations.values() if i.innovation_type == innovation_type]
            report["by_type"][innovation_type.value] = {
                "count": len(type_innovations),
                "total_adopters": sum(i.adopter_count for i in type_innovations),
                "average_penetration": sum(i.market_penetration for i in type_innovations) / len(type_innovations) if type_innovations else 0
            }
        
        # Analysis by development stage
        for stage in InnovationStage:
            stage_innovations = [i for i in self.innovations.values() if i.current_stage == stage]
            report["by_stage"][stage.value] = {
                "count": len(stage_innovations),
                "total_investment": sum(self.innovation_investments.get(i.innovation_id, 0) for i in stage_innovations)
            }
        
        # Analysis by impact level
        for impact in InnovationImpact:
            impact_innovations = [i for i in self.innovations.values() if i.impact_level == impact]
            report["by_impact"][impact.value] = {
                "count": len(impact_innovations),
                "average_adopters": sum(i.adopter_count for i in impact_innovations) / len(impact_innovations) if impact_innovations else 0
            }
        
        # Top performers by adoption
        sorted_innovations = sorted(self.innovations.values(), key=lambda x: x.adopter_count, reverse=True)
        report["top_performers"] = [
            {
                "innovation_name": i.innovation_name,
                "adopter_count": i.adopter_count,
                "market_penetration": i.market_penetration,
                "revenue": self.innovation_revenues.get(i.innovation_id, 0)
            }
            for i in sorted_innovations[:5]
        ]
        
        return report
    
    def get_innovation_details(self, innovation_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific innovation"""
        
        if innovation_id not in self.innovations:
            return {"error": "Innovation not found"}
        
        innovation = self.innovations[innovation_id]
        market_dynamics = self.market_dynamics.get(innovation_id)
        
        details = {
            "innovation": {
                "id": innovation.innovation_id,
                "name": innovation.innovation_name,
                "description": innovation.description,
                "type": innovation.innovation_type.value,
                "impact_level": innovation.impact_level.value,
                "current_stage": innovation.current_stage.value
            },
            "development": {
                "lead_institution": innovation.research_institution,
                "lead_researcher": innovation.lead_researcher,
                "start_date": innovation.development_start_date,
                "launch_date": innovation.commercial_launch_date,
                "development_progress": innovation.development_progress,
                "total_cost": innovation.development_cost_total
            },
            "market_performance": {
                "adopter_count": innovation.adopter_count,
                "market_penetration": innovation.market_penetration,
                "price_point": innovation.price_point,
                "total_revenue": self.innovation_revenues.get(innovation_id, 0),
                "adoption_rate": innovation.adoption_rate
            },
            "benefits": innovation.adoption_benefits,
            "barriers": innovation.adoption_barriers,
            "patent_info": {
                "status": innovation.patent_status.value,
                "holder": innovation.patent_holder,
                "expiry_date": innovation.patent_expiry_date
            }
        }
        
        if market_dynamics:
            details["market_dynamics"] = {
                "total_addressable_market": market_dynamics.total_addressable_market,
                "serviceable_market": market_dynamics.serviceable_market,
                "market_growth_rate": market_dynamics.market_growth_rate,
                "competitive_intensity": market_dynamics.competitive_intensity
            }
        
        return details
    
    def get_adoption_curve(self, innovation_id: str) -> Dict[str, Any]:
        """Get adoption curve data for visualization"""
        
        if innovation_id not in self.adoption_curves:
            return {"error": "Innovation not found"}
        
        curve_data = self.adoption_curves[innovation_id]
        innovation = self.innovations[innovation_id]
        
        return {
            "innovation_name": innovation.innovation_name,
            "curve_data": curve_data,
            "current_penetration": innovation.market_penetration,
            "total_adopters": innovation.adopter_count,
            "launch_date": innovation.commercial_launch_date
        }
    
    # Event handlers
    
    def handle_research_completion(self, event_data: Dict[str, Any]):
        """Handle research completion that might trigger innovation"""
        try:
            # Research completion might lead to innovation opportunities
            if random.random() < 0.3:  # 30% chance
                self.generate_innovation_opportunity()
        
        except Exception as e:
            self.logger.error(f"Error handling research completion: {e}")
    
    def handle_technology_demonstration(self, event_data: Dict[str, Any]):
        """Handle technology demonstration events"""
        try:
            # Demonstrations can increase adoption rates
            innovation_id = event_data.get("innovation_id")
            if innovation_id in self.innovations:
                # Boost adoption for next period
                pass
        
        except Exception as e:
            self.logger.error(f"Error handling technology demonstration: {e}")
    
    def _create_basic_innovation_configuration(self):
        """Create basic innovation configuration for fallback"""
        self.logger.warning("Creating basic innovation configuration")
        
        # Create basic innovation
        basic_innovation = Innovation(
            innovation_id="basic_improvement",
            innovation_name="Basic Farm Improvement",
            description="Basic farming improvement",
            innovation_type=InnovationType.PROCESS,
            impact_level=InnovationImpact.INCREMENTAL,
            research_institution="agricultural_university",
            lead_researcher="Basic Researcher",
            development_start_date=self.current_time,
            current_stage=InnovationStage.MATURITY
        )
        
        self.innovations["basic_improvement"] = basic_innovation


# Global convenience functions
innovation_system_instance = None

def get_innovation_system():
    """Get the global innovation system instance"""
    global innovation_system_instance
    if innovation_system_instance is None:
        innovation_system_instance = InnovationSystem()
    return innovation_system_instance

def generate_innovation():
    """Convenience function to generate innovation opportunity"""
    return get_innovation_system().generate_innovation_opportunity()

def start_innovation_project(opportunity: Dict[str, Any], funding: float):
    """Convenience function to start innovation project"""
    return get_innovation_system().start_innovation_project(opportunity, funding)

def simulate_adoption(innovation_id: str, adopter_id: str):
    """Convenience function to simulate adoption decision"""
    return get_innovation_system().simulate_adoption_decision(innovation_id, adopter_id)

def get_innovation_portfolio():
    """Convenience function to get innovation portfolio"""
    return get_innovation_system().get_innovation_portfolio_report()