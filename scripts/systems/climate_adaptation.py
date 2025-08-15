"""
Climate Adaptation - Long-Term Climate Trends & Farm Adaptation for AgriFun Agricultural Simulation

This system models long-term climate change impacts on agriculture and provides adaptation
strategies for farmers to maintain productivity under changing conditions. It simulates
realistic climate trends, extreme weather events, and adaptive management practices.

Key Features:
- Climate Change Modeling: Temperature, precipitation, and weather pattern shifts
- Extreme Weather Events: Droughts, floods, heat waves, severe storms
- Crop Climate Suitability: Shifting growing zones and optimal varieties
- Adaptive Strategies: Technology, practices, and infrastructure adaptations
- Risk Assessment: Climate vulnerability analysis and mitigation planning
- Economic Impact: Climate costs and adaptation investment analysis
- Policy Integration: Carbon pricing, climate programs, and regulations

Climate Scenarios:
- RCP 2.6: Strong mitigation scenario (+1.5°C by 2100)
- RCP 4.5: Moderate mitigation scenario (+2.5°C by 2100)
- RCP 6.0: High emissions scenario (+3.5°C by 2100)
- RCP 8.5: Very high emissions scenario (+4.5°C by 2100)

Educational Value:
- Understanding climate change impacts on agriculture
- Adaptation planning and implementation strategies
- Economic analysis of climate risks and adaptation costs
- Sustainable farming practices for climate resilience
- Policy tools for climate adaptation support
- Regional climate variability and local adaptation needs
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
import yaml
import random
import math


class ClimateScenario(Enum):
    """IPCC climate change scenarios"""
    RCP26 = "rcp26"                                 # Strong mitigation (+1.5°C)
    RCP45 = "rcp45"                                 # Moderate mitigation (+2.5°C)
    RCP60 = "rcp60"                                 # High emissions (+3.5°C)
    RCP85 = "rcp85"                                 # Very high emissions (+4.5°C)


class ClimateVariable(Enum):
    """Climate variables tracked by the system"""
    TEMPERATURE = "temperature"                      # Average temperature
    PRECIPITATION = "precipitation"                  # Total precipitation
    HUMIDITY = "humidity"                           # Relative humidity
    WIND_SPEED = "wind_speed"                       # Average wind speed
    SOLAR_RADIATION = "solar_radiation"             # Solar irradiance
    GROWING_SEASON_LENGTH = "growing_season_length"  # Days suitable for growth
    FROST_DAYS = "frost_days"                       # Days below freezing
    HEAT_DAYS = "heat_days"                         # Days above 32°C


class ExtremeWeatherType(Enum):
    """Types of extreme weather events"""
    DROUGHT = "drought"                             # Extended dry period
    FLOOD = "flood"                                 # Excessive precipitation
    HEAT_WAVE = "heat_wave"                        # Extended high temperature
    COLD_SNAP = "cold_snap"                        # Extended low temperature
    SEVERE_STORM = "severe_storm"                   # High wind/hail storms
    WILDFIRE = "wildfire"                          # Fire risk conditions
    ICE_STORM = "ice_storm"                        # Freezing rain events


class AdaptationCategory(Enum):
    """Categories of climate adaptation strategies"""
    CROP_MANAGEMENT = "crop_management"             # Crop selection and practices
    WATER_MANAGEMENT = "water_management"           # Irrigation and conservation
    SOIL_MANAGEMENT = "soil_management"             # Soil health and conservation
    INFRASTRUCTURE = "infrastructure"               # Buildings and equipment
    TECHNOLOGY = "technology"                       # Climate-smart technologies
    DIVERSIFICATION = "diversification"             # Enterprise diversification
    RISK_MANAGEMENT = "risk_management"             # Insurance and hedging
    POLICY_PROGRAMS = "policy_programs"             # Government adaptation programs


class VulnerabilityLevel(Enum):
    """Climate vulnerability assessment levels"""
    LOW = "low"                                     # Minimal climate risk
    MODERATE = "moderate"                           # Some climate risk
    HIGH = "high"                                   # Significant climate risk
    SEVERE = "severe"                              # Critical climate risk


@dataclass
class ClimateProjection:
    """Climate projection data for a specific scenario"""
    scenario: ClimateScenario
    projection_year: int
    baseline_year: int = 2020
    
    # Temperature projections (°C change from baseline)
    temperature_change_annual: float = 0.0
    temperature_change_winter: float = 0.0
    temperature_change_summer: float = 0.0
    temperature_variability_change: float = 0.0
    
    # Precipitation projections (% change from baseline)
    precipitation_change_annual: float = 0.0
    precipitation_change_winter: float = 0.0
    precipitation_change_summer: float = 0.0
    precipitation_variability_change: float = 0.0
    
    # Extreme weather frequency changes
    drought_frequency_multiplier: float = 1.0
    flood_frequency_multiplier: float = 1.0
    heat_wave_frequency_multiplier: float = 1.0
    severe_storm_frequency_multiplier: float = 1.0
    
    # Growing conditions
    growing_season_length_change: int = 0           # Days change
    frost_free_period_change: int = 0               # Days change
    water_stress_index_change: float = 0.0          # Unitless stress index
    
    # Uncertainty ranges
    temperature_uncertainty_range: Tuple[float, float] = (0.0, 0.0)
    precipitation_uncertainty_range: Tuple[float, float] = (0.0, 0.0)


@dataclass
class ExtremeWeatherEvent:
    """Individual extreme weather event"""
    event_id: str
    event_type: ExtremeWeatherType
    start_date: datetime
    end_date: datetime
    intensity: float                                # 0-1 intensity scale
    
    # Spatial extent
    affected_regions: List[str] = field(default_factory=list)
    peak_location: Tuple[float, float] = (0.0, 0.0)  # GPS coordinates
    
    # Event characteristics
    magnitude: float = 0.0                          # Type-specific magnitude
    duration_hours: float = 0.0
    return_period_years: float = 10.0               # Statistical return period
    
    # Agricultural impacts
    crop_damage_potential: float = 0.0              # 0-1 damage potential
    infrastructure_damage_risk: float = 0.0         # 0-1 damage risk
    economic_impact_estimate: float = 0.0           # Economic loss estimate
    
    # Response and recovery
    warning_lead_time_hours: float = 24.0           # Advance warning time
    recovery_time_estimate_days: int = 7
    adaptation_measures_triggered: List[str] = field(default_factory=list)


@dataclass
class ClimateImpact:
    """Climate change impact on agricultural systems"""
    impact_id: str
    impact_name: str
    affected_system: str                            # Crop, livestock, infrastructure
    impact_category: str                            # Productivity, quality, cost
    
    # Impact quantification
    baseline_value: float
    projected_impact_2030: float
    projected_impact_2050: float
    projected_impact_2100: float
    
    # Impact mechanisms
    primary_climate_driver: ClimateVariable
    secondary_climate_drivers: List[ClimateVariable] = field(default_factory=list)
    impact_threshold: Optional[float] = None        # Threshold for impact occurrence
    
    # Geographic variation
    regional_variation: Dict[str, float] = field(default_factory=dict)  # {region: impact_multiplier}
    elevation_sensitivity: float = 0.0             # Impact per 100m elevation
    
    # Economic valuation
    economic_value_per_unit: float = 0.0           # $/unit impact
    adaptation_cost_reduction: float = 0.0         # Cost reduction with adaptation
    
    # Uncertainty and confidence
    confidence_level: str = "medium"               # low, medium, high
    uncertainty_range: Tuple[float, float] = (0.0, 0.0)  # Impact range


@dataclass
class AdaptationStrategy:
    """Climate adaptation strategy definition"""
    strategy_id: str
    strategy_name: str
    description: str
    adaptation_category: AdaptationCategory
    
    # Implementation characteristics
    implementation_timeframe: str                   # immediate, short_term, long_term
    implementation_cost: float                      # Implementation cost
    annual_maintenance_cost: float                  # Annual operating cost
    lifespan_years: int = 20                       # Strategy effectiveness period
    
    # Effectiveness
    climate_variables_addressed: List[ClimateVariable] = field(default_factory=list)
    risk_reduction_percentage: float = 0.0          # % risk reduction
    productivity_impact: float = 0.0                # % productivity change
    cost_savings_annual: float = 0.0               # Annual cost savings
    
    # Prerequisites and constraints
    prerequisite_technologies: List[str] = field(default_factory=list)
    minimum_farm_size: float = 0.0                 # Minimum viable farm size
    required_skills: List[str] = field(default_factory=list)
    financing_requirements: Dict[str, float] = field(default_factory=dict)
    
    # Co-benefits and trade-offs
    environmental_benefits: List[str] = field(default_factory=list)
    social_benefits: List[str] = field(default_factory=list)
    potential_trade_offs: List[str] = field(default_factory=list)
    
    # Monitoring and evaluation
    success_indicators: List[str] = field(default_factory=list)
    monitoring_requirements: List[str] = field(default_factory=list)


@dataclass
class VulnerabilityAssessment:
    """Climate vulnerability assessment for farm systems"""
    assessment_id: str
    farm_system_id: str
    assessment_date: datetime
    climate_scenario: ClimateScenario
    
    # Exposure assessment
    climate_exposure_score: float = 0.0            # 0-1 exposure level
    extreme_weather_exposure: Dict[str, float] = field(default_factory=dict)  # {event_type: exposure}
    
    # Sensitivity assessment
    system_sensitivity_score: float = 0.0          # 0-1 sensitivity level
    critical_thresholds: Dict[str, float] = field(default_factory=dict)  # {variable: threshold}
    
    # Adaptive capacity assessment
    adaptive_capacity_score: float = 0.0           # 0-1 adaptive capacity
    adaptation_barriers: List[str] = field(default_factory=list)
    adaptation_opportunities: List[str] = field(default_factory=list)
    
    # Overall vulnerability
    overall_vulnerability: VulnerabilityLevel
    vulnerability_score: float = 0.0               # 0-1 combined vulnerability
    priority_adaptation_needs: List[str] = field(default_factory=list)
    
    # Risk assessment
    climate_risks_identified: List[Dict[str, Any]] = field(default_factory=list)
    risk_tolerance_threshold: float = 0.5          # Acceptable risk level
    
    # Recommendations
    recommended_adaptations: List[str] = field(default_factory=list)
    adaptation_timeline: Dict[str, str] = field(default_factory=dict)  # {strategy: timeframe}


class ClimateAdaptation:
    """
    Comprehensive Climate Adaptation system for long-term climate resilience
    
    This system models climate change impacts, assesses vulnerability, and provides
    adaptive management strategies to maintain agricultural productivity under
    changing climate conditions.
    """
    
    def __init__(self, config_manager=None, event_system=None):
        """Initialize climate adaptation system"""
        self.config_manager = config_manager
        self.event_system = event_system
        self.logger = logging.getLogger(__name__)
        
        # Climate modeling
        self.climate_projections: Dict[str, ClimateProjection] = {}
        self.climate_baselines: Dict[str, Dict[str, float]] = {}
        self.current_climate_scenario: ClimateScenario = ClimateScenario.RCP45
        
        # Extreme weather tracking
        self.historical_extreme_events: List[ExtremeWeatherEvent] = []
        self.active_extreme_events: List[ExtremeWeatherEvent] = []
        self.extreme_weather_forecasts: List[Dict[str, Any]] = []
        
        # Impact assessment
        self.climate_impacts: Dict[str, ClimateImpact] = {}
        self.vulnerability_assessments: Dict[str, VulnerabilityAssessment] = {}
        self.impact_monitoring: Dict[str, List[Dict[str, Any]]] = {}
        
        # Adaptation strategies
        self.available_adaptations: Dict[str, AdaptationStrategy] = {}
        self.implemented_adaptations: Dict[str, List[str]] = {}  # {farm_id: [strategy_ids]}
        self.adaptation_effectiveness: Dict[str, Dict[str, float]] = {}
        
        # Economic analysis
        self.climate_costs: Dict[str, float] = {}               # {cost_category: annual_cost}
        self.adaptation_investments: Dict[str, float] = {}      # {strategy_id: investment}
        self.adaptation_benefits: Dict[str, float] = {}         # {strategy_id: annual_benefit}
        
        # Policy and programs
        self.climate_policies: Dict[str, Dict[str, Any]] = {}
        self.adaptation_programs: Dict[str, Dict[str, Any]] = {}
        self.carbon_pricing: Optional[float] = None            # $/tonne CO2
        
        # System parameters
        self.simulation_start_year: int = 2024
        self.current_simulation_year: int = 2024
        self.projection_horizon: int = 2100
        self.climate_update_frequency: str = "annual"          # annual, seasonal, monthly
        
        # Initialize system
        self._initialize_climate_adaptation()
        
    def _initialize_climate_adaptation(self):
        """Initialize climate adaptation system"""
        try:
            self._setup_climate_projections()
            self._load_adaptation_strategies()
            self._initialize_climate_baselines()
            self._setup_impact_monitoring()
            self._configure_policy_framework()
            
            if self.event_system:
                self._subscribe_to_events()
                
            self.logger.info("Climate Adaptation system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing climate adaptation: {e}")
            self._create_basic_climate_configuration()
    
    def _setup_climate_projections(self):
        """Setup climate change projections for different scenarios"""
        
        # Define projection data for different scenarios and time periods
        projection_definitions = [
            # RCP 2.6 - Strong mitigation scenario
            {
                "scenario": ClimateScenario.RCP26,
                "projection_year": 2030,
                "temperature_change_annual": 0.8,
                "temperature_change_winter": 1.0,
                "temperature_change_summer": 0.6,
                "precipitation_change_annual": 2.0,
                "precipitation_change_winter": 5.0,
                "precipitation_change_summer": -1.0,
                "drought_frequency_multiplier": 1.1,
                "heat_wave_frequency_multiplier": 1.3,
                "growing_season_length_change": 5
            },
            {
                "scenario": ClimateScenario.RCP26,
                "projection_year": 2050,
                "temperature_change_annual": 1.2,
                "temperature_change_winter": 1.5,
                "temperature_change_summer": 0.9,
                "precipitation_change_annual": 3.0,
                "precipitation_change_winter": 8.0,
                "precipitation_change_summer": -2.0,
                "drought_frequency_multiplier": 1.15,
                "heat_wave_frequency_multiplier": 1.5,
                "growing_season_length_change": 8
            },
            {
                "scenario": ClimateScenario.RCP26,
                "projection_year": 2100,
                "temperature_change_annual": 1.5,
                "temperature_change_winter": 1.8,
                "temperature_change_summer": 1.2,
                "precipitation_change_annual": 4.0,
                "precipitation_change_winter": 10.0,
                "precipitation_change_summer": -2.0,
                "drought_frequency_multiplier": 1.2,
                "heat_wave_frequency_multiplier": 1.8,
                "growing_season_length_change": 12
            },
            
            # RCP 4.5 - Moderate mitigation scenario  
            {
                "scenario": ClimateScenario.RCP45,
                "projection_year": 2030,
                "temperature_change_annual": 1.0,
                "temperature_change_winter": 1.2,
                "temperature_change_summer": 0.8,
                "precipitation_change_annual": 1.0,
                "precipitation_change_winter": 4.0,
                "precipitation_change_summer": -2.0,
                "drought_frequency_multiplier": 1.2,
                "heat_wave_frequency_multiplier": 1.5,
                "growing_season_length_change": 7
            },
            {
                "scenario": ClimateScenario.RCP45,
                "projection_year": 2050,
                "temperature_change_annual": 1.8,
                "temperature_change_winter": 2.1,
                "temperature_change_summer": 1.5,
                "precipitation_change_annual": 2.0,
                "precipitation_change_winter": 6.0,
                "precipitation_change_summer": -3.0,
                "drought_frequency_multiplier": 1.35,
                "heat_wave_frequency_multiplier": 2.2,
                "growing_season_length_change": 15
            },
            {
                "scenario": ClimateScenario.RCP45,
                "projection_year": 2100,
                "temperature_change_annual": 2.5,
                "temperature_change_winter": 2.8,
                "temperature_change_summer": 2.2,
                "precipitation_change_annual": 3.0,
                "precipitation_change_winter": 8.0,
                "precipitation_change_summer": -4.0,
                "drought_frequency_multiplier": 1.5,
                "heat_wave_frequency_multiplier": 3.0,
                "growing_season_length_change": 25
            },
            
            # RCP 8.5 - High emissions scenario
            {
                "scenario": ClimateScenario.RCP85,
                "projection_year": 2030,
                "temperature_change_annual": 1.2,
                "temperature_change_winter": 1.4,
                "temperature_change_summer": 1.0,
                "precipitation_change_annual": 0.0,
                "precipitation_change_winter": 3.0,
                "precipitation_change_summer": -4.0,
                "drought_frequency_multiplier": 1.3,
                "heat_wave_frequency_multiplier": 1.8,
                "growing_season_length_change": 10
            },
            {
                "scenario": ClimateScenario.RCP85,
                "projection_year": 2050,
                "temperature_change_annual": 2.4,
                "temperature_change_winter": 2.8,
                "temperature_change_summer": 2.0,
                "precipitation_change_annual": -1.0,
                "precipitation_change_winter": 4.0,
                "precipitation_change_summer": -8.0,
                "drought_frequency_multiplier": 1.8,
                "heat_wave_frequency_multiplier": 3.5,
                "growing_season_length_change": 20
            },
            {
                "scenario": ClimateScenario.RCP85,
                "projection_year": 2100,
                "temperature_change_annual": 4.5,
                "temperature_change_winter": 5.0,
                "temperature_change_summer": 4.0,
                "precipitation_change_annual": -2.0,
                "precipitation_change_winter": 5.0,
                "precipitation_change_summer": -15.0,
                "drought_frequency_multiplier": 2.5,
                "heat_wave_frequency_multiplier": 6.0,
                "growing_season_length_change": 40
            }
        ]
        
        # Create ClimateProjection objects
        for proj_dict in projection_definitions:
            projection = ClimateProjection(**proj_dict)
            
            # Add uncertainty ranges based on scenario and time horizon
            time_factor = (projection.projection_year - 2024) / 76  # Normalize to 2024-2100
            base_uncertainty = 0.1 + (time_factor * 0.2)  # Increasing uncertainty over time
            
            projection.temperature_uncertainty_range = (
                projection.temperature_change_annual * (1 - base_uncertainty),
                projection.temperature_change_annual * (1 + base_uncertainty)
            )
            
            projection.precipitation_uncertainty_range = (
                projection.precipitation_change_annual * (1 - base_uncertainty * 1.5),
                projection.precipitation_change_annual * (1 + base_uncertainty * 1.5)
            )
            
            # Store projection
            proj_key = f"{projection.scenario.value}_{projection.projection_year}"
            self.climate_projections[proj_key] = projection
        
        self.logger.info(f"Setup {len(self.climate_projections)} climate projections")
    
    def _load_adaptation_strategies(self):
        """Load climate adaptation strategies"""
        
        adaptation_definitions = [
            # Crop Management Adaptations
            {
                "strategy_id": "drought_tolerant_varieties",
                "strategy_name": "Drought-Tolerant Crop Varieties",
                "description": "Plant crop varieties bred or selected for drought tolerance",
                "adaptation_category": AdaptationCategory.CROP_MANAGEMENT,
                "implementation_timeframe": "short_term",
                "implementation_cost": 5000,
                "annual_maintenance_cost": 500,
                "climate_variables_addressed": [ClimateVariable.PRECIPITATION, ClimateVariable.TEMPERATURE],
                "risk_reduction_percentage": 25.0,
                "productivity_impact": -5.0,  # Slight yield penalty for resilience
                "cost_savings_annual": 2000,
                "environmental_benefits": ["reduced_irrigation_needs", "soil_water_conservation"],
                "success_indicators": ["yield_stability", "water_use_efficiency"]
            },
            {
                "strategy_id": "heat_tolerant_varieties",
                "strategy_name": "Heat-Tolerant Crop Varieties", 
                "description": "Plant crop varieties that maintain productivity under higher temperatures",
                "adaptation_category": AdaptationCategory.CROP_MANAGEMENT,
                "implementation_timeframe": "short_term",
                "implementation_cost": 4000,
                "annual_maintenance_cost": 400,
                "climate_variables_addressed": [ClimateVariable.TEMPERATURE, ClimateVariable.HEAT_DAYS],
                "risk_reduction_percentage": 30.0,
                "productivity_impact": 0.0,
                "cost_savings_annual": 3000,
                "environmental_benefits": ["maintained_productivity", "reduced_stress"],
                "success_indicators": ["heat_stress_tolerance", "yield_maintenance"]
            },
            {
                "strategy_id": "diversified_cropping",
                "strategy_name": "Diversified Cropping Systems",
                "description": "Increase crop diversity to spread climate risk across multiple species",
                "adaptation_category": AdaptationCategory.DIVERSIFICATION,
                "implementation_timeframe": "short_term",
                "implementation_cost": 8000,
                "annual_maintenance_cost": 1200,
                "climate_variables_addressed": [
                    ClimateVariable.TEMPERATURE, ClimateVariable.PRECIPITATION, 
                    ClimateVariable.GROWING_SEASON_LENGTH
                ],
                "risk_reduction_percentage": 40.0,
                "productivity_impact": 5.0,  # Potential yield increase from diversity
                "cost_savings_annual": 1500,
                "environmental_benefits": ["biodiversity_increase", "pest_reduction", "soil_health"],
                "success_indicators": ["risk_distribution", "income_stability"]
            },
            
            # Water Management Adaptations
            {
                "strategy_id": "efficient_irrigation",
                "strategy_name": "Water-Efficient Irrigation Systems",
                "description": "Install drip irrigation or other high-efficiency irrigation technology",
                "adaptation_category": AdaptationCategory.WATER_MANAGEMENT,
                "implementation_timeframe": "short_term",
                "implementation_cost": 25000,
                "annual_maintenance_cost": 2500,
                "climate_variables_addressed": [ClimateVariable.PRECIPITATION, ClimateVariable.TEMPERATURE],
                "risk_reduction_percentage": 35.0,
                "productivity_impact": 10.0,  # Better water control increases yields
                "cost_savings_annual": 4000,
                "environmental_benefits": ["water_conservation", "reduced_runoff"],
                "success_indicators": ["water_use_efficiency", "yield_per_water_unit"]
            },
            {
                "strategy_id": "water_storage",
                "strategy_name": "On-Farm Water Storage",
                "description": "Build ponds, tanks, or reservoirs for water storage during dry periods",
                "adaptation_category": AdaptationCategory.WATER_MANAGEMENT,
                "implementation_timeframe": "medium_term",
                "implementation_cost": 50000,
                "annual_maintenance_cost": 3000,
                "climate_variables_addressed": [ClimateVariable.PRECIPITATION],
                "risk_reduction_percentage": 50.0,
                "productivity_impact": 8.0,
                "cost_savings_annual": 6000,
                "environmental_benefits": ["drought_resilience", "water_security"],
                "success_indicators": ["water_availability", "drought_survival"]
            },
            {
                "strategy_id": "soil_moisture_conservation",
                "strategy_name": "Soil Moisture Conservation",
                "description": "Implement cover crops, mulching, and conservation tillage",
                "adaptation_category": AdaptationCategory.SOIL_MANAGEMENT,
                "implementation_timeframe": "short_term",
                "implementation_cost": 3000,
                "annual_maintenance_cost": 800,
                "climate_variables_addressed": [ClimateVariable.PRECIPITATION, ClimateVariable.TEMPERATURE],
                "risk_reduction_percentage": 20.0,
                "productivity_impact": 3.0,
                "cost_savings_annual": 1200,
                "environmental_benefits": ["soil_health", "erosion_reduction", "carbon_sequestration"],
                "success_indicators": ["soil_moisture_retention", "erosion_reduction"]
            },
            
            # Infrastructure Adaptations
            {
                "strategy_id": "climate_controlled_storage",
                "strategy_name": "Climate-Controlled Storage",
                "description": "Build temperature and humidity controlled storage facilities",
                "adaptation_category": AdaptationCategory.INFRASTRUCTURE,
                "implementation_timeframe": "medium_term",
                "implementation_cost": 100000,
                "annual_maintenance_cost": 8000,
                "climate_variables_addressed": [ClimateVariable.TEMPERATURE, ClimateVariable.HUMIDITY],
                "risk_reduction_percentage": 60.0,
                "productivity_impact": 0.0,  # Protects quality, not quantity
                "cost_savings_annual": 12000,
                "environmental_benefits": ["reduced_food_waste", "quality_preservation"],
                "success_indicators": ["storage_losses", "product_quality"]
            },
            {
                "strategy_id": "weather_protection",
                "strategy_name": "Weather Protection Infrastructure",
                "description": "Install greenhouses, hoop houses, or shade structures",
                "adaptation_category": AdaptationCategory.INFRASTRUCTURE,
                "implementation_timeframe": "medium_term",
                "implementation_cost": 75000,
                "annual_maintenance_cost": 5000,
                "climate_variables_addressed": [
                    ClimateVariable.TEMPERATURE, ClimateVariable.PRECIPITATION,
                    ClimateVariable.WIND_SPEED
                ],
                "risk_reduction_percentage": 70.0,
                "productivity_impact": 15.0,  # Protected environment increases yields
                "cost_savings_annual": 8000,
                "environmental_benefits": ["crop_protection", "extended_season"],
                "success_indicators": ["weather_damage_reduction", "yield_stability"]
            },
            
            # Technology Adaptations
            {
                "strategy_id": "precision_agriculture",
                "strategy_name": "Precision Agriculture Technology",
                "description": "Implement GPS-guided equipment and variable-rate application",
                "adaptation_category": AdaptationCategory.TECHNOLOGY,
                "implementation_timeframe": "medium_term",
                "implementation_cost": 150000,
                "annual_maintenance_cost": 15000,
                "climate_variables_addressed": [
                    ClimateVariable.PRECIPITATION, ClimateVariable.TEMPERATURE,
                    ClimateVariable.SOIL_MOISTURE
                ],
                "risk_reduction_percentage": 30.0,
                "productivity_impact": 12.0,
                "cost_savings_annual": 20000,
                "environmental_benefits": ["input_efficiency", "reduced_waste"],
                "success_indicators": ["input_use_efficiency", "spatial_yield_optimization"]
            },
            {
                "strategy_id": "climate_monitoring",
                "strategy_name": "Advanced Climate Monitoring",
                "description": "Install weather stations and soil sensors for real-time monitoring",
                "adaptation_category": AdaptationCategory.TECHNOLOGY,
                "implementation_timeframe": "short_term",
                "implementation_cost": 15000,
                "annual_maintenance_cost": 2000,
                "climate_variables_addressed": [
                    ClimateVariable.TEMPERATURE, ClimateVariable.PRECIPITATION,
                    ClimateVariable.HUMIDITY, ClimateVariable.WIND_SPEED
                ],
                "risk_reduction_percentage": 25.0,
                "productivity_impact": 5.0,
                "cost_savings_annual": 3000,
                "environmental_benefits": ["informed_decisions", "timely_responses"],
                "success_indicators": ["forecast_accuracy", "decision_timing"]
            },
            
            # Risk Management Adaptations
            {
                "strategy_id": "crop_insurance",
                "strategy_name": "Comprehensive Crop Insurance",
                "description": "Purchase crop insurance covering weather-related losses",
                "adaptation_category": AdaptationCategory.RISK_MANAGEMENT,
                "implementation_timeframe": "immediate",
                "implementation_cost": 0,
                "annual_maintenance_cost": 8000,  # Annual premium
                "climate_variables_addressed": [
                    ClimateVariable.PRECIPITATION, ClimateVariable.TEMPERATURE,
                    ClimateVariable.WIND_SPEED
                ],
                "risk_reduction_percentage": 80.0,  # Financial risk reduction
                "productivity_impact": 0.0,
                "cost_savings_annual": 0,  # Insurance doesn't save costs, reduces risk
                "environmental_benefits": [],
                "success_indicators": ["financial_stability", "risk_coverage"]
            }
        ]
        
        # Convert to AdaptationStrategy objects
        for strategy_dict in adaptation_definitions:
            strategy = AdaptationStrategy(**strategy_dict)
            self.available_adaptations[strategy.strategy_id] = strategy
            
        self.logger.info(f"Loaded {len(self.available_adaptations)} adaptation strategies")
    
    def _initialize_climate_baselines(self):
        """Initialize baseline climate data"""
        
        # Regional baseline climate data (example for Midwest US)
        self.climate_baselines = {
            "midwest_us": {
                "temperature_annual": 10.5,      # °C
                "temperature_winter": -2.0,      # °C
                "temperature_summer": 23.0,      # °C
                "precipitation_annual": 900,     # mm
                "precipitation_winter": 150,     # mm
                "precipitation_summer": 350,     # mm
                "growing_season_length": 180,    # days
                "frost_free_period": 160,        # days
                "heat_days_above_32c": 15,       # days
                "frost_days_below_0c": 120       # days
            }
        }
        
        self.logger.info("Climate baselines initialized")
    
    def _setup_impact_monitoring(self):
        """Setup climate impact monitoring"""
        
        # Define key climate impacts to monitor
        impact_definitions = [
            {
                "impact_id": "corn_yield_temperature",
                "impact_name": "Corn Yield - Temperature Impact",
                "affected_system": "corn_production",
                "impact_category": "productivity",
                "baseline_value": 10.0,  # tons/ha baseline yield
                "projected_impact_2030": -0.2,  # tons/ha change
                "projected_impact_2050": -0.5,
                "projected_impact_2100": -1.2,
                "primary_climate_driver": ClimateVariable.TEMPERATURE,
                "secondary_climate_drivers": [ClimateVariable.HEAT_DAYS],
                "economic_value_per_unit": 200,  # $/ton
                "confidence_level": "high"
            },
            {
                "impact_id": "corn_yield_precipitation",
                "impact_name": "Corn Yield - Precipitation Impact",
                "affected_system": "corn_production", 
                "impact_category": "productivity",
                "baseline_value": 10.0,
                "projected_impact_2030": -0.1,
                "projected_impact_2050": -0.3,
                "projected_impact_2100": -0.8,
                "primary_climate_driver": ClimateVariable.PRECIPITATION,
                "economic_value_per_unit": 200,
                "confidence_level": "medium"
            },
            {
                "impact_id": "irrigation_costs",
                "impact_name": "Irrigation Cost Increase",
                "affected_system": "water_management",
                "impact_category": "cost",
                "baseline_value": 500,  # $/ha baseline irrigation cost
                "projected_impact_2030": 50,   # $/ha increase
                "projected_impact_2050": 150,
                "projected_impact_2100": 400,
                "primary_climate_driver": ClimateVariable.PRECIPITATION,
                "secondary_climate_drivers": [ClimateVariable.TEMPERATURE],
                "economic_value_per_unit": 1.0,  # Direct cost
                "confidence_level": "high"
            }
        ]
        
        # Create ClimateImpact objects
        for impact_dict in impact_definitions:
            impact = ClimateImpact(**impact_dict)
            self.climate_impacts[impact.impact_id] = impact
        
        self.logger.info(f"Setup monitoring for {len(self.climate_impacts)} climate impacts")
    
    def _configure_policy_framework(self):
        """Configure climate policy and program framework"""
        
        # Sample climate policies
        self.climate_policies = {
            "carbon_tax": {
                "policy_type": "carbon_pricing",
                "price_per_tonne": 50.0,  # $/tonne CO2
                "implementation_year": 2025,
                "scope": ["fossil_fuels", "agriculture"],
                "exemptions": ["small_farms"]
            },
            "adaptation_subsidies": {
                "policy_type": "adaptation_support",
                "subsidy_rate": 0.3,  # 30% cost share
                "max_subsidy_per_farm": 100000,
                "eligible_practices": [
                    "efficient_irrigation", "water_storage", 
                    "climate_controlled_storage", "precision_agriculture"
                ]
            }
        }
        
        # Sample adaptation programs
        self.adaptation_programs = {
            "climate_smart_agriculture": {
                "program_name": "Climate-Smart Agriculture Initiative",
                "funding_available": 10000000,  # Total program funding
                "cost_share_percentage": 50,
                "eligible_strategies": [
                    "soil_moisture_conservation", "diversified_cropping",
                    "efficient_irrigation", "climate_monitoring"
                ],
                "application_deadline": "2024-12-31"
            }
        }
        
        # Set carbon pricing
        self.carbon_pricing = self.climate_policies["carbon_tax"]["price_per_tonne"]
        
        self.logger.info("Policy framework configured")
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        if self.event_system:
            self.event_system.subscribe('weather_extreme_event', self.handle_extreme_weather)
            self.event_system.subscribe('annual_climate_update', self.handle_annual_climate_update)
            self.event_system.subscribe('adaptation_implemented', self.handle_adaptation_implementation)
            self.event_system.subscribe('climate_assessment_requested', self.handle_assessment_request)
    
    # Core climate adaptation methods
    
    def assess_climate_vulnerability(self, farm_system_id: str, 
                                   climate_scenario: ClimateScenario = None) -> Dict[str, Any]:
        """Conduct comprehensive climate vulnerability assessment"""
        try:
            if climate_scenario is None:
                climate_scenario = self.current_climate_scenario
            
            assessment_id = f"vulnerability_{farm_system_id}_{int(datetime.now().timestamp())}"
            
            # Calculate exposure scores
            exposure_assessment = self._assess_climate_exposure(farm_system_id, climate_scenario)
            
            # Calculate sensitivity scores
            sensitivity_assessment = self._assess_climate_sensitivity(farm_system_id)
            
            # Calculate adaptive capacity
            adaptive_capacity = self._assess_adaptive_capacity(farm_system_id)
            
            # Calculate overall vulnerability
            vulnerability_score = self._calculate_overall_vulnerability(
                exposure_assessment["score"],
                sensitivity_assessment["score"], 
                adaptive_capacity["score"]
            )
            
            # Determine vulnerability level
            if vulnerability_score < 0.25:
                vulnerability_level = VulnerabilityLevel.LOW
            elif vulnerability_score < 0.5:
                vulnerability_level = VulnerabilityLevel.MODERATE
            elif vulnerability_score < 0.75:
                vulnerability_level = VulnerabilityLevel.HIGH
            else:
                vulnerability_level = VulnerabilityLevel.SEVERE
            
            # Generate recommendations
            recommendations = self._generate_adaptation_recommendations(
                vulnerability_score, exposure_assessment, sensitivity_assessment, adaptive_capacity
            )
            
            # Create assessment record
            assessment = VulnerabilityAssessment(
                assessment_id=assessment_id,
                farm_system_id=farm_system_id,
                assessment_date=datetime.now(),
                climate_scenario=climate_scenario,
                climate_exposure_score=exposure_assessment["score"],
                extreme_weather_exposure=exposure_assessment["extreme_weather"],
                system_sensitivity_score=sensitivity_assessment["score"],
                critical_thresholds=sensitivity_assessment["thresholds"],
                adaptive_capacity_score=adaptive_capacity["score"],
                adaptation_barriers=adaptive_capacity["barriers"],
                adaptation_opportunities=adaptive_capacity["opportunities"],
                overall_vulnerability=vulnerability_level,
                vulnerability_score=vulnerability_score,
                priority_adaptation_needs=recommendations["priority_needs"],
                climate_risks_identified=recommendations["risks"],
                recommended_adaptations=recommendations["strategies"],
                adaptation_timeline=recommendations["timeline"]
            )
            
            # Store assessment
            self.vulnerability_assessments[assessment_id] = assessment
            
            # Publish assessment event
            if self.event_system:
                self.event_system.publish('vulnerability_assessment_completed', {
                    'assessment': assessment,
                    'recommendations': recommendations
                })
            
            self.logger.info(f"Climate vulnerability assessment completed for {farm_system_id}")
            
            return {"success": True, "assessment": assessment, "recommendations": recommendations}
            
        except Exception as e:
            self.logger.error(f"Error assessing climate vulnerability: {e}")
            return {"success": False, "error": str(e)}
    
    def _assess_climate_exposure(self, farm_system_id: str, 
                                climate_scenario: ClimateScenario) -> Dict[str, Any]:
        """Assess climate exposure for a farm system"""
        
        # Get relevant climate projections
        projection_2030 = self.climate_projections.get(f"{climate_scenario.value}_2030")
        projection_2050 = self.climate_projections.get(f"{climate_scenario.value}_2050")
        
        exposure_factors = []
        
        if projection_2030 and projection_2050:
            # Temperature exposure
            temp_change = (projection_2030.temperature_change_annual + projection_2050.temperature_change_annual) / 2
            temp_exposure = min(1.0, abs(temp_change) / 3.0)  # Normalize to 3°C as high exposure
            exposure_factors.append(temp_exposure)
            
            # Precipitation exposure  
            precip_change = (projection_2030.precipitation_change_annual + projection_2050.precipitation_change_annual) / 2
            precip_exposure = min(1.0, abs(precip_change) / 20.0)  # Normalize to 20% as high exposure
            exposure_factors.append(precip_exposure)
            
            # Extreme weather exposure
            extreme_weather_exposure = {
                "drought": min(1.0, (projection_2050.drought_frequency_multiplier - 1.0) / 1.0),
                "heat_wave": min(1.0, (projection_2050.heat_wave_frequency_multiplier - 1.0) / 2.0),
                "flood": min(1.0, (projection_2050.flood_frequency_multiplier - 1.0) / 1.0),
                "severe_storm": min(1.0, (projection_2050.severe_storm_frequency_multiplier - 1.0) / 1.0)
            }
            
            avg_extreme_exposure = sum(extreme_weather_exposure.values()) / len(extreme_weather_exposure)
            exposure_factors.append(avg_extreme_exposure)
        else:
            # Default moderate exposure if projections not available
            temp_exposure = 0.5
            precip_exposure = 0.5
            avg_extreme_exposure = 0.5
            extreme_weather_exposure = {"drought": 0.5, "heat_wave": 0.5, "flood": 0.3, "severe_storm": 0.4}
            exposure_factors = [temp_exposure, precip_exposure, avg_extreme_exposure]
        
        # Calculate overall exposure score
        overall_exposure = sum(exposure_factors) / len(exposure_factors)
        
        return {
            "score": overall_exposure,
            "temperature_exposure": temp_exposure,
            "precipitation_exposure": precip_exposure,
            "extreme_weather": extreme_weather_exposure,
            "factors": exposure_factors
        }
    
    def _assess_climate_sensitivity(self, farm_system_id: str) -> Dict[str, Any]:
        """Assess climate sensitivity of farm system"""
        
        # Simplified sensitivity assessment - in real implementation would be more detailed
        sensitivity_factors = {
            "crop_diversity": 0.4,        # Lower diversity = higher sensitivity
            "irrigation_availability": 0.3,  # Less irrigation = higher sensitivity  
            "soil_quality": 0.2,          # Poor soil = higher sensitivity
            "infrastructure_quality": 0.6,  # Poor infrastructure = higher sensitivity
            "management_intensity": 0.3   # Extensive systems often more sensitive
        }
        
        # Calculate overall sensitivity
        overall_sensitivity = sum(sensitivity_factors.values()) / len(sensitivity_factors)
        
        # Define critical thresholds
        critical_thresholds = {
            "temperature": 35.0,      # °C critical temperature for crops
            "precipitation": 300.0,   # mm minimum annual precipitation
            "drought_days": 60,       # days without rain
            "heat_days": 30           # days above 32°C
        }
        
        return {
            "score": overall_sensitivity,
            "factors": sensitivity_factors,
            "thresholds": critical_thresholds
        }
    
    def _assess_adaptive_capacity(self, farm_system_id: str) -> Dict[str, Any]:
        """Assess adaptive capacity of farm system"""
        
        # Adaptive capacity factors
        capacity_factors = {
            "financial_resources": 0.6,      # Available capital for adaptation
            "technical_knowledge": 0.7,      # Understanding of adaptation options
            "institutional_support": 0.5,    # Access to programs and assistance
            "social_networks": 0.6,          # Connections for learning and support
            "flexibility": 0.8,              # Ability to change practices
            "innovation_adoption": 0.7       # Willingness to adopt new technologies
        }
        
        overall_capacity = sum(capacity_factors.values()) / len(capacity_factors)
        
        # Identify barriers and opportunities
        barriers = []
        opportunities = []
        
        if capacity_factors["financial_resources"] < 0.5:
            barriers.append("limited_financial_resources")
        else:
            opportunities.append("adequate_funding_for_adaptation")
            
        if capacity_factors["technical_knowledge"] < 0.6:
            barriers.append("limited_technical_knowledge")
        else:
            opportunities.append("good_technical_understanding")
            
        if capacity_factors["institutional_support"] < 0.6:
            barriers.append("limited_institutional_support")
        else:
            opportunities.append("strong_institutional_connections")
        
        return {
            "score": overall_capacity,
            "factors": capacity_factors,
            "barriers": barriers,
            "opportunities": opportunities
        }
    
    def _calculate_overall_vulnerability(self, exposure: float, sensitivity: float, 
                                       adaptive_capacity: float) -> float:
        """Calculate overall vulnerability score using IPCC framework"""
        
        # Vulnerability = f(Exposure, Sensitivity, Adaptive Capacity)
        # Higher exposure and sensitivity increase vulnerability
        # Higher adaptive capacity decreases vulnerability
        
        vulnerability = (exposure * 0.4 + sensitivity * 0.4) * (1.0 - adaptive_capacity * 0.6)
        
        return min(1.0, max(0.0, vulnerability))
    
    def _generate_adaptation_recommendations(self, vulnerability_score: float,
                                           exposure_assessment: Dict[str, Any],
                                           sensitivity_assessment: Dict[str, Any],
                                           adaptive_capacity: Dict[str, Any]) -> Dict[str, Any]:
        """Generate adaptation recommendations based on assessment"""
        
        recommendations = {
            "priority_needs": [],
            "strategies": [],
            "timeline": {},
            "risks": []
        }
        
        # High-level priority needs based on vulnerability
        if vulnerability_score > 0.7:
            recommendations["priority_needs"].extend([
                "immediate_risk_reduction", "diversification", "infrastructure_upgrade"
            ])
        elif vulnerability_score > 0.4:
            recommendations["priority_needs"].extend([
                "moderate_adaptation", "monitoring_enhancement", "capacity_building"
            ])
        else:
            recommendations["priority_needs"].extend([
                "preparedness_enhancement", "efficiency_improvement"
            ])
        
        # Specific strategy recommendations based on exposure patterns
        if exposure_assessment["temperature_exposure"] > 0.6:
            recommendations["strategies"].extend([
                "heat_tolerant_varieties", "climate_controlled_storage", "weather_protection"
            ])
            recommendations["timeline"]["heat_tolerant_varieties"] = "immediate"
        
        if exposure_assessment["precipitation_exposure"] > 0.6:
            recommendations["strategies"].extend([
                "efficient_irrigation", "water_storage", "drought_tolerant_varieties"
            ])
            recommendations["timeline"]["efficient_irrigation"] = "short_term"
        
        if exposure_assessment["extreme_weather"]["drought"] > 0.5:
            recommendations["strategies"].extend([
                "soil_moisture_conservation", "diversified_cropping"
            ])
            recommendations["timeline"]["soil_moisture_conservation"] = "immediate"
        
        # Address adaptive capacity gaps
        if adaptive_capacity["score"] < 0.5:
            if "limited_financial_resources" in adaptive_capacity["barriers"]:
                recommendations["strategies"].append("crop_insurance")
                recommendations["timeline"]["crop_insurance"] = "immediate"
        
        # Identify key risks
        if vulnerability_score > 0.6:
            recommendations["risks"].append({
                "risk_type": "productivity_loss",
                "probability": "high",
                "impact": "significant",
                "mitigation": "diversification_and_infrastructure"
            })
        
        if exposure_assessment["extreme_weather"]["drought"] > 0.7:
            recommendations["risks"].append({
                "risk_type": "drought_stress",
                "probability": "very_high", 
                "impact": "severe",
                "mitigation": "water_management_systems"
            })
        
        return recommendations
    
    def implement_adaptation_strategy(self, farm_system_id: str, 
                                    strategy_id: str) -> Dict[str, Any]:
        """Implement a climate adaptation strategy"""
        try:
            if strategy_id not in self.available_adaptations:
                return {"success": False, "error": "Adaptation strategy not found"}
            
            strategy = self.available_adaptations[strategy_id]
            
            # Check implementation feasibility
            feasibility_check = self._check_implementation_feasibility(farm_system_id, strategy)
            if not feasibility_check["feasible"]:
                return {"success": False, "error": "Implementation not feasible", 
                       "details": feasibility_check}
            
            # Record implementation
            if farm_system_id not in self.implemented_adaptations:
                self.implemented_adaptations[farm_system_id] = []
            
            self.implemented_adaptations[farm_system_id].append(strategy_id)
            
            # Track investment
            self.adaptation_investments[strategy_id] = (
                self.adaptation_investments.get(strategy_id, 0) + strategy.implementation_cost
            )
            
            # Estimate annual benefits
            annual_benefit = strategy.cost_savings_annual
            self.adaptation_benefits[strategy_id] = (
                self.adaptation_benefits.get(strategy_id, 0) + annual_benefit
            )
            
            # Create implementation record
            implementation_record = {
                "farm_system_id": farm_system_id,
                "strategy_id": strategy_id,
                "strategy_name": strategy.strategy_name,
                "implementation_date": datetime.now(),
                "implementation_cost": strategy.implementation_cost,
                "annual_maintenance_cost": strategy.annual_maintenance_cost,
                "expected_annual_savings": strategy.cost_savings_annual,
                "risk_reduction_percentage": strategy.risk_reduction_percentage,
                "productivity_impact": strategy.productivity_impact
            }
            
            # Publish implementation event
            if self.event_system:
                self.event_system.publish('adaptation_strategy_implemented', {
                    'implementation': implementation_record,
                    'strategy': strategy
                })
            
            self.logger.info(f"Adaptation strategy implemented: {strategy.strategy_name}")
            
            return {"success": True, "implementation": implementation_record}
            
        except Exception as e:
            self.logger.error(f"Error implementing adaptation strategy {strategy_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_implementation_feasibility(self, farm_system_id: str, 
                                        strategy: AdaptationStrategy) -> Dict[str, Any]:
        """Check feasibility of implementing adaptation strategy"""
        
        feasibility = {
            "feasible": True,
            "constraints": [],
            "requirements_met": []
        }
        
        # Check financial feasibility (simplified)
        available_capital = 200000  # Placeholder - would get from farm economic data
        if strategy.implementation_cost > available_capital:
            feasibility["feasible"] = False
            feasibility["constraints"].append(f"Insufficient capital: need ${strategy.implementation_cost}, have ${available_capital}")
        else:
            feasibility["requirements_met"].append("adequate_funding")
        
        # Check technical requirements
        if strategy.prerequisite_technologies:
            # Simplified check - assume some technologies available
            available_tech = ["basic_irrigation", "weather_monitoring", "soil_testing"]
            
            missing_tech = []
            for tech in strategy.prerequisite_technologies:
                if tech not in available_tech:
                    missing_tech.append(tech)
            
            if missing_tech:
                feasibility["feasible"] = False
                feasibility["constraints"].append(f"Missing technologies: {missing_tech}")
            else:
                feasibility["requirements_met"].append("technology_requirements")
        
        # Check minimum farm size
        if strategy.minimum_farm_size > 0:
            farm_size = 150  # Placeholder - would get from farm data
            if farm_size < strategy.minimum_farm_size:
                feasibility["feasible"] = False
                feasibility["constraints"].append(f"Farm too small: need {strategy.minimum_farm_size} ha, have {farm_size} ha")
            else:
                feasibility["requirements_met"].append("adequate_farm_size")
        
        return feasibility
    
    def simulate_extreme_weather_event(self, event_type: ExtremeWeatherType, 
                                     intensity: float = 0.5) -> Dict[str, Any]:
        """Simulate an extreme weather event"""
        try:
            event_id = f"extreme_{event_type.value}_{int(datetime.now().timestamp())}"
            
            # Generate event characteristics based on type and intensity
            event_characteristics = self._generate_event_characteristics(event_type, intensity)
            
            # Create extreme weather event
            event = ExtremeWeatherEvent(
                event_id=event_id,
                event_type=event_type,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(hours=event_characteristics["duration_hours"]),
                intensity=intensity,
                magnitude=event_characteristics["magnitude"],
                duration_hours=event_characteristics["duration_hours"],
                return_period_years=event_characteristics["return_period"],
                crop_damage_potential=event_characteristics["crop_damage"],
                infrastructure_damage_risk=event_characteristics["infrastructure_damage"],
                economic_impact_estimate=event_characteristics["economic_impact"],
                warning_lead_time_hours=event_characteristics["warning_time"],
                recovery_time_estimate_days=event_characteristics["recovery_time"]
            )
            
            # Add to active events
            self.active_extreme_events.append(event)
            
            # Calculate impacts on farm systems
            impact_assessment = self._assess_extreme_weather_impacts(event)
            
            # Trigger adaptation responses
            adaptation_responses = self._trigger_adaptation_responses(event)
            
            # Publish extreme weather event
            if self.event_system:
                self.event_system.publish('extreme_weather_event_occurred', {
                    'event': event,
                    'impacts': impact_assessment,
                    'responses': adaptation_responses
                })
            
            self.logger.warning(f"Extreme weather event simulated: {event_type.value}")
            
            return {
                "success": True,
                "event": event,
                "impacts": impact_assessment,
                "responses": adaptation_responses
            }
            
        except Exception as e:
            self.logger.error(f"Error simulating extreme weather event: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_event_characteristics(self, event_type: ExtremeWeatherType, 
                                      intensity: float) -> Dict[str, Any]:
        """Generate characteristics for extreme weather event"""
        
        base_characteristics = {
            ExtremeWeatherType.DROUGHT: {
                "duration_hours": 2160,  # 90 days
                "magnitude": intensity * 100,  # % rainfall deficit
                "return_period": 10 / intensity,  # More intense = rarer
                "crop_damage": intensity * 0.8,
                "infrastructure_damage": intensity * 0.2,
                "economic_impact": intensity * 50000,
                "warning_time": 720,  # 30 days
                "recovery_time": 30
            },
            ExtremeWeatherType.FLOOD: {
                "duration_hours": 72,    # 3 days
                "magnitude": intensity * 200,  # mm rainfall
                "return_period": 25 / intensity,
                "crop_damage": intensity * 0.9,
                "infrastructure_damage": intensity * 0.7,
                "economic_impact": intensity * 100000,
                "warning_time": 24,
                "recovery_time": 14
            },
            ExtremeWeatherType.HEAT_WAVE: {
                "duration_hours": 168,   # 7 days
                "magnitude": 35 + intensity * 10,  # °C peak temperature
                "return_period": 15 / intensity,
                "crop_damage": intensity * 0.6,
                "infrastructure_damage": intensity * 0.3,
                "economic_impact": intensity * 30000,
                "warning_time": 120,  # 5 days
                "recovery_time": 7
            },
            ExtremeWeatherType.SEVERE_STORM: {
                "duration_hours": 4,     # 4 hours
                "magnitude": intensity * 150,  # km/h wind speed
                "return_period": 20 / intensity,
                "crop_damage": intensity * 0.7,
                "infrastructure_damage": intensity * 0.8,
                "economic_impact": intensity * 75000,
                "warning_time": 6,
                "recovery_time": 5
            }
        }
        
        return base_characteristics.get(event_type, {
            "duration_hours": 24,
            "magnitude": intensity * 50,
            "return_period": 10,
            "crop_damage": intensity * 0.5,
            "infrastructure_damage": intensity * 0.4,
            "economic_impact": intensity * 25000,
            "warning_time": 12,
            "recovery_time": 7
        })
    
    def _assess_extreme_weather_impacts(self, event: ExtremeWeatherEvent) -> Dict[str, Any]:
        """Assess impacts of extreme weather event"""
        
        # Simplified impact assessment
        impacts = {
            "crop_impacts": {
                "yield_loss_percentage": event.crop_damage_potential * 100,
                "quality_degradation": event.intensity * 0.6,
                "replanting_needed": event.intensity > 0.7
            },
            "infrastructure_impacts": {
                "damage_level": event.infrastructure_damage_risk,
                "repair_cost_estimate": event.economic_impact_estimate * 0.3,
                "downtime_days": event.recovery_time_estimate_days
            },
            "economic_impacts": {
                "direct_losses": event.economic_impact_estimate,
                "indirect_losses": event.economic_impact_estimate * 0.5,
                "recovery_costs": event.economic_impact_estimate * 0.2
            },
            "adaptation_effectiveness": {}
        }
        
        # Assess how implemented adaptations reduce impacts
        for farm_id, strategies in self.implemented_adaptations.items():
            farm_protection = 0.0
            
            for strategy_id in strategies:
                strategy = self.available_adaptations[strategy_id]
                
                # Check if strategy addresses this type of extreme weather
                if event.event_type == ExtremeWeatherType.DROUGHT:
                    if ClimateVariable.PRECIPITATION in strategy.climate_variables_addressed:
                        farm_protection += strategy.risk_reduction_percentage / 100
                elif event.event_type == ExtremeWeatherType.HEAT_WAVE:
                    if ClimateVariable.TEMPERATURE in strategy.climate_variables_addressed:
                        farm_protection += strategy.risk_reduction_percentage / 100
                
            impacts["adaptation_effectiveness"][farm_id] = min(0.8, farm_protection)
        
        return impacts
    
    def _trigger_adaptation_responses(self, event: ExtremeWeatherEvent) -> List[str]:
        """Trigger appropriate adaptation responses to extreme weather"""
        
        responses = []
        
        if event.event_type == ExtremeWeatherType.DROUGHT:
            responses.extend([
                "activate_drought_management_plan",
                "implement_water_conservation_measures",
                "assess_crop_insurance_claims",
                "consider_emergency_irrigation"
            ])
            
        elif event.event_type == ExtremeWeatherType.FLOOD:
            responses.extend([
                "activate_flood_response_plan",
                "assess_drainage_systems",
                "evaluate_crop_damage",
                "implement_soil_recovery_measures"
            ])
            
        elif event.event_type == ExtremeWeatherType.HEAT_WAVE:
            responses.extend([
                "activate_heat_management_protocols",
                "increase_irrigation_frequency",
                "provide_livestock_cooling",
                "monitor_crop_stress_levels"
            ])
            
        elif event.event_type == ExtremeWeatherType.SEVERE_STORM:
            responses.extend([
                "assess_structural_damage",
                "secure_loose_equipment",
                "evaluate_crop_damage",
                "activate_emergency_repair_procedures"
            ])
        
        return responses
    
    # Reporting and analysis methods
    
    def get_climate_adaptation_report(self) -> Dict[str, Any]:
        """Generate comprehensive climate adaptation status report"""
        
        report = {
            "summary": {
                "current_climate_scenario": self.current_climate_scenario.value,
                "simulation_year": self.current_simulation_year,
                "total_adaptations_available": len(self.available_adaptations),
                "adaptations_implemented": sum(len(strategies) for strategies in self.implemented_adaptations.values()),
                "total_adaptation_investment": sum(self.adaptation_investments.values()),
                "annual_adaptation_benefits": sum(self.adaptation_benefits.values()),
                "extreme_events_this_year": len([e for e in self.historical_extreme_events 
                                               if e.start_date.year == self.current_simulation_year])
            },
            "vulnerability_status": {},
            "adaptation_portfolio": {},
            "economic_analysis": {},
            "climate_trends": {}
        }
        
        # Vulnerability status
        if self.vulnerability_assessments:
            recent_assessments = list(self.vulnerability_assessments.values())[-5:]  # Last 5 assessments
            
            vulnerability_levels = [a.overall_vulnerability.value for a in recent_assessments]
            avg_vulnerability_score = sum(a.vulnerability_score for a in recent_assessments) / len(recent_assessments)
            
            report["vulnerability_status"] = {
                "recent_assessments_count": len(recent_assessments),
                "average_vulnerability_score": avg_vulnerability_score,
                "vulnerability_levels": vulnerability_levels,
                "common_risks": self._identify_common_risks(recent_assessments)
            }
        
        # Adaptation portfolio analysis
        adaptation_by_category = {}
        for strategies in self.implemented_adaptations.values():
            for strategy_id in strategies:
                strategy = self.available_adaptations[strategy_id]
                category = strategy.adaptation_category.value
                
                if category not in adaptation_by_category:
                    adaptation_by_category[category] = []
                adaptation_by_category[category].append(strategy_id)
        
        report["adaptation_portfolio"] = {
            "by_category": adaptation_by_category,
            "most_common_strategies": self._get_most_common_strategies(),
            "portfolio_diversity": len(adaptation_by_category)
        }
        
        # Economic analysis
        total_investment = sum(self.adaptation_investments.values())
        total_benefits = sum(self.adaptation_benefits.values())
        
        report["economic_analysis"] = {
            "total_investment": total_investment,
            "annual_benefits": total_benefits,
            "benefit_cost_ratio": total_benefits / total_investment if total_investment > 0 else 0,
            "payback_period_years": total_investment / total_benefits if total_benefits > 0 else float('inf'),
            "climate_costs": self.climate_costs,
            "net_climate_benefit": total_benefits - sum(self.climate_costs.values())
        }
        
        return report
    
    def _identify_common_risks(self, assessments: List[VulnerabilityAssessment]) -> List[str]:
        """Identify common risks across vulnerability assessments"""
        risk_counts = {}
        
        for assessment in assessments:
            for risk in assessment.climate_risks_identified:
                risk_type = risk.get("risk_type", "unknown")
                risk_counts[risk_type] = risk_counts.get(risk_type, 0) + 1
        
        # Return risks that appear in more than half of assessments
        threshold = len(assessments) / 2
        common_risks = [risk for risk, count in risk_counts.items() if count >= threshold]
        
        return common_risks
    
    def _get_most_common_strategies(self) -> List[Tuple[str, int]]:
        """Get most commonly implemented adaptation strategies"""
        strategy_counts = {}
        
        for strategies in self.implemented_adaptations.values():
            for strategy_id in strategies:
                strategy_counts[strategy_id] = strategy_counts.get(strategy_id, 0) + 1
        
        # Sort by frequency and return top 5
        sorted_strategies = sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_strategies[:5]
    
    # Event handlers
    
    def handle_extreme_weather(self, event_data: Dict[str, Any]):
        """Handle extreme weather events"""
        try:
            event_type = ExtremeWeatherType(event_data.get("event_type", "drought"))
            intensity = event_data.get("intensity", 0.5)
            
            # Simulate the extreme weather event
            self.simulate_extreme_weather_event(event_type, intensity)
            
        except Exception as e:
            self.logger.error(f"Error handling extreme weather: {e}")
    
    def handle_annual_climate_update(self, event_data: Dict[str, Any]):
        """Handle annual climate updates"""
        try:
            self.current_simulation_year += 1
            
            # Move active extreme events to historical
            for event in self.active_extreme_events:
                if event.end_date < datetime.now():
                    self.historical_extreme_events.append(event)
            
            # Remove completed events from active list
            self.active_extreme_events = [
                event for event in self.active_extreme_events 
                if event.end_date >= datetime.now()
            ]
            
            # Update climate costs based on current year impacts
            self._update_annual_climate_costs()
            
            self.logger.info(f"Annual climate update completed for year {self.current_simulation_year}")
            
        except Exception as e:
            self.logger.error(f"Error handling annual climate update: {e}")
    
    def _update_annual_climate_costs(self):
        """Update annual climate-related costs"""
        
        # Calculate costs from extreme events this year
        current_year_events = [
            event for event in self.historical_extreme_events 
            if event.start_date.year == self.current_simulation_year
        ]
        
        annual_extreme_weather_costs = sum(
            event.economic_impact_estimate for event in current_year_events
        )
        
        # Update climate costs
        self.climate_costs["extreme_weather"] = annual_extreme_weather_costs
        self.climate_costs["adaptation_maintenance"] = sum(
            strategy.annual_maintenance_cost 
            for strategy in self.available_adaptations.values()
        )
        
        # Add carbon pricing costs if applicable
        if self.carbon_pricing:
            # Simplified carbon footprint calculation
            estimated_carbon_footprint = 500  # tonnes CO2/year placeholder
            self.climate_costs["carbon_pricing"] = estimated_carbon_footprint * self.carbon_pricing
    
    def _create_basic_climate_configuration(self):
        """Create basic climate configuration for fallback"""
        self.logger.warning("Creating basic climate configuration")
        
        # Create basic climate projection
        basic_projection = ClimateProjection(
            scenario=ClimateScenario.RCP45,
            projection_year=2050,
            temperature_change_annual=2.0,
            precipitation_change_annual=0.0
        )
        
        self.climate_projections["rcp45_2050"] = basic_projection
        
        # Create basic adaptation strategy
        basic_adaptation = AdaptationStrategy(
            strategy_id="basic_adaptation",
            strategy_name="Basic Climate Adaptation",
            description="Basic climate adaptation measures",
            adaptation_category=AdaptationCategory.CROP_MANAGEMENT,
            implementation_timeframe="short_term",
            implementation_cost=5000,
            annual_maintenance_cost=500,
            risk_reduction_percentage=20.0
        )
        
        self.available_adaptations["basic_adaptation"] = basic_adaptation


# Global convenience functions
climate_adaptation_instance = None

def get_climate_adaptation():
    """Get the global climate adaptation instance"""
    global climate_adaptation_instance
    if climate_adaptation_instance is None:
        climate_adaptation_instance = ClimateAdaptation()
    return climate_adaptation_instance

def assess_vulnerability(farm_system_id: str, climate_scenario: ClimateScenario = None):
    """Convenience function to assess climate vulnerability"""
    return get_climate_adaptation().assess_climate_vulnerability(farm_system_id, climate_scenario)

def implement_adaptation(farm_system_id: str, strategy_id: str):
    """Convenience function to implement adaptation strategy"""
    return get_climate_adaptation().implement_adaptation_strategy(farm_system_id, strategy_id)

def simulate_extreme_weather(event_type: ExtremeWeatherType, intensity: float = 0.5):
    """Convenience function to simulate extreme weather"""
    return get_climate_adaptation().simulate_extreme_weather_event(event_type, intensity)

def get_climate_report():
    """Convenience function to get climate adaptation report"""
    return get_climate_adaptation().get_climate_adaptation_report()