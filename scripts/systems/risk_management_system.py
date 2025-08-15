"""
Risk Management System - Comprehensive Risk Assessment and Mitigation for AgriFun Agricultural Game

This system provides realistic risk management tools including crop insurance, market hedging,
weather risk assessment, and financial risk analysis. It helps players understand and mitigate
the various risks inherent in agricultural operations through education and strategic tools.

Key Features:
- Crop Insurance Programs (MPCI, Revenue Protection, Yield Protection)
- Market Hedging Tools (Futures, Options, Forward Contracts)
- Weather Risk Assessment and Crop-Hail Insurance
- Financial Risk Analysis and Credit Assessment
- Risk Portfolio Management and Optimization
- Educational Risk Management Strategies

Integration:
- Weather System: Real-time weather risk assessment
- Dynamic Pricing: Market volatility analysis for hedging decisions
- Contract Framework: Risk mitigation through contract structuring
- Economic System: Financial risk evaluation and credit management
- Crop Growth: Yield risk assessment based on growth conditions

Author: Agricultural Simulation Development Team
Version: 1.0.0 - Comprehensive Risk Management Implementation
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

class RiskType(Enum):
    """Types of agricultural risks"""
    YIELD_RISK = "yield_risk"
    PRICE_RISK = "price_risk"
    WEATHER_RISK = "weather_risk"
    CREDIT_RISK = "credit_risk"
    OPERATIONAL_RISK = "operational_risk"
    PRODUCTION_RISK = "production_risk"

class InsuranceType(Enum):
    """Types of crop insurance available"""
    MPCI = "multi_peril_crop_insurance"        # Multiple Peril Crop Insurance
    REVENUE_PROTECTION = "revenue_protection"   # Revenue Protection (RP)
    YIELD_PROTECTION = "yield_protection"       # Yield Protection (YP)
    CROP_HAIL = "crop_hail"                    # Crop-Hail Insurance
    WHOLE_FARM = "whole_farm_revenue"          # Whole-Farm Revenue Protection

class HedgingInstrument(Enum):
    """Financial instruments for market risk hedging"""
    FUTURES_CONTRACT = "futures_contract"
    PUT_OPTION = "put_option"
    CALL_OPTION = "call_option"
    COLLAR = "collar"                          # Put + Call combination
    FORWARD_CONTRACT = "forward_contract"

class RiskLevel(Enum):
    """Risk assessment levels"""
    VERY_LOW = "very_low"
    LOW = "low" 
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class RiskAssessment:
    """Comprehensive risk assessment for agricultural operations"""
    risk_type: RiskType
    risk_level: RiskLevel
    probability: float  # 0.0 to 1.0
    potential_loss: float  # Dollar amount
    confidence_interval: float  # Statistical confidence (0.0 to 1.0)
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    assessment_date: datetime = field(default_factory=datetime.now)

@dataclass 
class InsurancePolicy:
    """Crop insurance policy details"""
    policy_id: str
    insurance_type: InsuranceType
    crop_id: str
    coverage_level: float  # Percentage (50% to 85% typically)
    premium_rate: float    # Percentage of liability
    unit_structure: str    # "basic", "optional", "enterprise"
    liability_per_acre: float
    total_premium: float
    farmer_premium: float  # After subsidies
    acres_covered: float
    policy_start_date: datetime
    policy_end_date: datetime
    is_active: bool = True

@dataclass
class HedgePosition:
    """Market hedging position details"""
    position_id: str
    instrument: HedgingInstrument
    commodity_id: str
    contract_size: float   # Bushels/tons/units
    strike_price: Optional[float] = None  # For options
    futures_price: Optional[float] = None  # For futures/forwards
    premium_paid: Optional[float] = None  # For options
    expiration_date: datetime = field(default_factory=datetime.now)
    margin_requirement: float = 0.0
    current_value: float = 0.0
    unrealized_pnl: float = 0.0
    is_long: bool = True  # True for long, False for short

@dataclass
class WeatherRisk:
    """Weather-related risk assessment"""
    location_id: str
    risk_factors: Dict[str, float] = field(default_factory=dict)  # drought, flood, hail, etc.
    historical_loss_probability: Dict[str, float] = field(default_factory=dict)
    current_forecast_risk: Dict[str, float] = field(default_factory=dict)
    seasonal_risk_profile: Dict[str, Dict[str, float]] = field(default_factory=dict)

@dataclass
class FinancialRisk:
    """Financial and credit risk assessment"""
    debt_to_asset_ratio: float
    current_ratio: float
    working_capital: float
    cash_flow_volatility: float
    credit_score: int
    debt_service_coverage: float
    liquidity_ratio: float
    risk_rating: RiskLevel = RiskLevel.MODERATE

@dataclass
class RiskPortfolio:
    """Comprehensive risk portfolio for farm operation"""
    farm_id: str
    total_risk_exposure: float
    diversification_index: float  # 0.0 to 1.0, higher is better
    insurance_coverage_ratio: float
    hedging_effectiveness: float
    risk_assessments: Dict[RiskType, RiskAssessment] = field(default_factory=dict)
    active_policies: List[InsurancePolicy] = field(default_factory=list)
    hedge_positions: List[HedgePosition] = field(default_factory=list)
    optimization_recommendations: List[str] = field(default_factory=list)

class RiskManagementSystem(System):
    """
    Comprehensive Risk Management System for Agricultural Operations
    
    This system provides realistic risk assessment and mitigation tools including:
    - Crop insurance programs with accurate premium calculations
    - Market hedging strategies using futures and options
    - Weather risk modeling based on historical and forecast data
    - Financial risk analysis for farm operations
    - Portfolio optimization for risk/return balance
    """
    
    def __init__(self):
        """Initialize the Risk Management System"""
        super().__init__()
        
        # Core system references
        self.event_system = None
        self.config_manager = None
        self.content_registry = None
        
        # Risk management data
        self.risk_portfolios: Dict[str, RiskPortfolio] = {}
        self.insurance_policies: Dict[str, InsurancePolicy] = {}
        self.hedge_positions: Dict[str, HedgePosition] = {}
        self.weather_risks: Dict[str, WeatherRisk] = {}
        
        # Risk modeling parameters
        self.risk_parameters = {
            'yield_volatility': 0.15,      # 15% coefficient of variation
            'price_volatility': 0.25,      # 25% price volatility
            'weather_risk_weights': {
                'drought': 0.3,
                'flood': 0.2, 
                'hail': 0.15,
                'freeze': 0.2,
                'wind': 0.15
            },
            'insurance_subsidy_rates': {
                InsuranceType.MPCI: 0.62,           # 62% average subsidy
                InsuranceType.REVENUE_PROTECTION: 0.59,  # 59% average subsidy
                InsuranceType.YIELD_PROTECTION: 0.55,    # 55% average subsidy
                InsuranceType.CROP_HAIL: 0.0,           # No federal subsidy
                InsuranceType.WHOLE_FARM: 0.80           # 80% subsidy for whole farm
            }
        }
        
        # Market data for hedging
        self.market_data = {
            'volatility_surface': {},      # Options volatility by strike/expiration
            'interest_rates': 0.03,        # Risk-free rate for options pricing
            'margin_rates': {              # Margin requirements by commodity
                'corn': 0.05,
                'soybeans': 0.06,
                'wheat': 0.05
            }
        }
        
        # Statistical models
        self.yield_distributions = {}      # Historical yield distributions by crop/location
        self.price_correlations = {}       # Price correlations between commodities
        
        self.is_initialized = False
    
    def initialize(self, event_system: EventSystem, config_manager: ConfigurationManager, 
                  content_registry: ContentRegistry) -> bool:
        """Initialize the Risk Management System with required dependencies"""
        try:
            self.event_system = event_system
            self.config_manager = config_manager
            self.content_registry = content_registry
            
            # Load risk management configuration
            self._load_configuration()
            
            # Initialize risk models
            self._initialize_risk_models()
            
            # Register event handlers
            self._register_event_handlers()
            
            # Load historical data
            self._load_historical_data()
            
            self.is_initialized = True
            
            # Emit initialization event
            self.event_system.emit_event("risk_management_initialized", {
                "system": "risk_management",
                "status": "ready",
                "timestamp": datetime.now()
            })
            
            return True
            
        except Exception as e:
            print(f"Error initializing Risk Management System: {e}")
            return False
    
    def _load_configuration(self):
        """Load risk management configuration from config files"""
        # Load risk modeling parameters
        risk_config = self.config_manager.get("risk_management", {})
        self.risk_parameters.update(risk_config.get("parameters", {}))
        
        # Load insurance configuration
        insurance_config = risk_config.get("insurance", {})
        if insurance_config:
            self.risk_parameters["insurance_subsidy_rates"].update(
                insurance_config.get("subsidy_rates", {})
            )
        
        # Load hedging configuration
        hedging_config = risk_config.get("hedging", {})
        if hedging_config:
            self.market_data.update(hedging_config.get("market_data", {}))
    
    def _initialize_risk_models(self):
        """Initialize statistical risk models"""
        # Initialize yield distribution models
        self._initialize_yield_models()
        
        # Initialize price correlation models
        self._initialize_price_models()
        
        # Initialize weather risk models
        self._initialize_weather_models()
    
    def _initialize_yield_models(self):
        """Initialize yield risk distribution models"""
        # Sample yield distributions (normally would load from historical data)
        self.yield_distributions = {
            'corn': {
                'mean': 180.0,      # bushels per acre
                'std_dev': 27.0,    # standard deviation
                'min_yield': 50.0,
                'max_yield': 280.0
            },
            'soybeans': {
                'mean': 50.0,       # bushels per acre
                'std_dev': 7.5,
                'min_yield': 15.0,
                'max_yield': 75.0
            },
            'wheat': {
                'mean': 65.0,       # bushels per acre
                'std_dev': 12.0,
                'min_yield': 25.0,
                'max_yield': 95.0
            }
        }
    
    def _initialize_price_models(self):
        """Initialize price correlation and volatility models"""
        # Price correlations between commodities
        self.price_correlations = {
            ('corn', 'soybeans'): 0.65,
            ('corn', 'wheat'): 0.55,
            ('soybeans', 'wheat'): 0.48
        }
    
    def _initialize_weather_models(self):
        """Initialize weather risk models"""
        # Sample weather risk profiles by region
        self.weather_risks['midwest'] = WeatherRisk(
            location_id='midwest',
            risk_factors={
                'drought': 0.25,    # 25% probability in any given year
                'flood': 0.15,
                'hail': 0.20,
                'freeze': 0.10,
                'wind': 0.12
            },
            historical_loss_probability={
                'drought': 0.35,    # Probability of loss given event
                'flood': 0.60,
                'hail': 0.45,
                'freeze': 0.30,
                'wind': 0.25
            }
        )
    
    def _register_event_handlers(self):
        """Register event handlers for system integration"""
        self.event_system.subscribe("market_price_updated", self._handle_price_update)
        self.event_system.subscribe("weather_forecast_updated", self._handle_weather_update)
        self.event_system.subscribe("crop_yield_reported", self._handle_yield_report)
        self.event_system.subscribe("season_changed", self._handle_season_change)
        self.event_system.subscribe("financial_statement_updated", self._handle_financial_update)
    
    def _load_historical_data(self):
        """Load historical data for risk modeling"""
        # This would load from actual data files in a production system
        pass
    
    def create_risk_assessment(self, farm_id: str, risk_type: RiskType, 
                             assessment_params: Dict[str, Any]) -> RiskAssessment:
        """Create comprehensive risk assessment for specified risk type"""
        
        if risk_type == RiskType.YIELD_RISK:
            return self._assess_yield_risk(farm_id, assessment_params)
        elif risk_type == RiskType.PRICE_RISK:
            return self._assess_price_risk(farm_id, assessment_params)
        elif risk_type == RiskType.WEATHER_RISK:
            return self._assess_weather_risk(farm_id, assessment_params)
        elif risk_type == RiskType.CREDIT_RISK:
            return self._assess_credit_risk(farm_id, assessment_params)
        elif risk_type == RiskType.OPERATIONAL_RISK:
            return self._assess_operational_risk(farm_id, assessment_params)
        else:
            return self._assess_production_risk(farm_id, assessment_params)
    
    def _assess_yield_risk(self, farm_id: str, params: Dict[str, Any]) -> RiskAssessment:
        """Assess yield risk based on crop, location, and management practices"""
        crop_id = params.get('crop_id', 'corn')
        acres = params.get('acres', 100.0)
        management_score = params.get('management_score', 0.8)  # 0.0 to 1.0
        
        # Get yield distribution for crop
        yield_dist = self.yield_distributions.get(crop_id, self.yield_distributions['corn'])
        
        # Adjust for management practices
        adjusted_mean = yield_dist['mean'] * management_score
        adjusted_std = yield_dist['std_dev'] * (1.1 - management_score * 0.1)
        
        # Calculate risk metrics
        prob_low_yield = self._calculate_normal_cdf(
            yield_dist['mean'] * 0.8, adjusted_mean, adjusted_std
        )
        
        potential_loss = acres * (adjusted_mean - yield_dist['mean'] * 0.6) * params.get('price_per_unit', 4.5)
        
        # Determine risk level
        if prob_low_yield < 0.1:
            risk_level = RiskLevel.LOW
        elif prob_low_yield < 0.2:
            risk_level = RiskLevel.MODERATE
        elif prob_low_yield < 0.35:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH
        
        return RiskAssessment(
            risk_type=RiskType.YIELD_RISK,
            risk_level=risk_level,
            probability=prob_low_yield,
            potential_loss=max(0, potential_loss),
            confidence_interval=0.85,
            risk_factors=[
                f"Yield variability: {adjusted_std:.1f} bu/ac",
                f"Management score: {management_score:.2f}",
                f"Historical average: {yield_dist['mean']:.1f} bu/ac"
            ],
            mitigation_strategies=[
                "Purchase crop insurance",
                "Diversify crop portfolio",
                "Improve management practices",
                "Use certified seed varieties"
            ]
        )
    
    def _assess_price_risk(self, farm_id: str, params: Dict[str, Any]) -> RiskAssessment:
        """Assess price risk based on commodity and market conditions"""
        commodity_id = params.get('commodity_id', 'corn')
        production_volume = params.get('production_volume', 18000)  # bushels
        current_price = params.get('current_price', 4.5)
        volatility = params.get('price_volatility', self.risk_parameters['price_volatility'])
        
        # Calculate potential price decline scenarios
        price_decline_10pct = current_price * 0.10
        price_decline_20pct = current_price * 0.20
        
        loss_10pct = production_volume * price_decline_10pct
        loss_20pct = production_volume * price_decline_20pct
        
        # Probability of price decline (simplified model)
        prob_decline_10pct = 0.30  # 30% chance of 10%+ decline
        prob_decline_20pct = 0.15  # 15% chance of 20%+ decline
        
        # Expected loss
        expected_loss = (prob_decline_10pct * loss_10pct) + (prob_decline_20pct * loss_20pct)
        
        # Risk level based on volatility and exposure
        if volatility < 0.15:
            risk_level = RiskLevel.LOW
        elif volatility < 0.25:
            risk_level = RiskLevel.MODERATE
        elif volatility < 0.35:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH
        
        return RiskAssessment(
            risk_type=RiskType.PRICE_RISK,
            risk_level=risk_level,
            probability=prob_decline_10pct,
            potential_loss=expected_loss,
            confidence_interval=0.75,
            risk_factors=[
                f"Price volatility: {volatility:.1%}",
                f"Production volume: {production_volume:,.0f} bushels",
                f"Current price: ${current_price:.2f}/bu"
            ],
            mitigation_strategies=[
                "Use futures contracts for hedging",
                "Purchase put options for downside protection",
                "Establish forward contracts with buyers",
                "Diversify marketing across time periods"
            ]
        )
    
    def _assess_weather_risk(self, farm_id: str, params: Dict[str, Any]) -> RiskAssessment:
        """Assess weather-related risks"""
        location_id = params.get('location_id', 'midwest')
        crop_stage = params.get('crop_stage', 'reproductive')
        acres = params.get('acres', 100.0)
        
        weather_risk = self.weather_risks.get(location_id)
        if not weather_risk:
            # Use default midwest risk profile
            weather_risk = self.weather_risks['midwest']
        
        # Calculate aggregate weather risk
        total_risk_prob = 0.0
        risk_factors = []
        potential_losses = []
        
        for risk_factor, probability in weather_risk.risk_factors.items():
            loss_given_event = weather_risk.historical_loss_probability.get(risk_factor, 0.5)
            
            # Adjust probability based on crop stage
            adjusted_prob = self._adjust_weather_probability(risk_factor, crop_stage, probability)
            
            # Calculate potential loss
            loss_per_acre = params.get('value_per_acre', 800) * loss_given_event
            potential_loss = acres * loss_per_acre * adjusted_prob
            
            total_risk_prob += adjusted_prob
            potential_losses.append(potential_loss)
            risk_factors.append(f"{risk_factor.title()}: {adjusted_prob:.1%} probability")
        
        max_potential_loss = max(potential_losses) if potential_losses else 0
        
        # Determine risk level
        if total_risk_prob < 0.2:
            risk_level = RiskLevel.LOW
        elif total_risk_prob < 0.4:
            risk_level = RiskLevel.MODERATE  
        elif total_risk_prob < 0.6:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH
        
        return RiskAssessment(
            risk_type=RiskType.WEATHER_RISK,
            risk_level=risk_level,
            probability=min(total_risk_prob, 1.0),
            potential_loss=max_potential_loss,
            confidence_interval=0.70,
            risk_factors=risk_factors,
            mitigation_strategies=[
                "Purchase crop-hail insurance",
                "Install irrigation systems",
                "Use weather monitoring services",
                "Plant weather-resistant varieties"
            ]
        )
    
    def _assess_credit_risk(self, farm_id: str, params: Dict[str, Any]) -> RiskAssessment:
        """Assess financial and credit risk"""
        financial_metrics = params.get('financial_metrics', {})
        
        debt_to_asset = financial_metrics.get('debt_to_asset_ratio', 0.4)
        current_ratio = financial_metrics.get('current_ratio', 1.2)
        debt_service_coverage = financial_metrics.get('debt_service_coverage', 1.5)
        
        # Calculate risk score
        risk_score = 0.0
        
        # Debt-to-asset ratio scoring (higher is riskier)
        if debt_to_asset > 0.7:
            risk_score += 0.4
        elif debt_to_asset > 0.5:
            risk_score += 0.3
        elif debt_to_asset > 0.3:
            risk_score += 0.1
        
        # Current ratio scoring (lower is riskier)
        if current_ratio < 1.0:
            risk_score += 0.3
        elif current_ratio < 1.2:
            risk_score += 0.2
        elif current_ratio < 1.5:
            risk_score += 0.1
        
        # Debt service coverage scoring (lower is riskier)
        if debt_service_coverage < 1.2:
            risk_score += 0.3
        elif debt_service_coverage < 1.5:
            risk_score += 0.2
        elif debt_service_coverage < 2.0:
            risk_score += 0.1
        
        # Determine risk level
        if risk_score < 0.2:
            risk_level = RiskLevel.LOW
        elif risk_score < 0.4:
            risk_level = RiskLevel.MODERATE
        elif risk_score < 0.6:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH
        
        # Estimate potential financial distress cost
        total_assets = params.get('total_assets', 1000000)
        potential_loss = total_assets * risk_score * 0.1  # Simplified model
        
        return RiskAssessment(
            risk_type=RiskType.CREDIT_RISK,
            risk_level=risk_level,
            probability=risk_score,
            potential_loss=potential_loss,
            confidence_interval=0.80,
            risk_factors=[
                f"Debt-to-asset ratio: {debt_to_asset:.1%}",
                f"Current ratio: {current_ratio:.2f}",
                f"Debt service coverage: {debt_service_coverage:.2f}"
            ],
            mitigation_strategies=[
                "Improve cash flow management",
                "Reduce debt levels",
                "Build emergency reserves",
                "Diversify income sources"
            ]
        )
    
    def _assess_operational_risk(self, farm_id: str, params: Dict[str, Any]) -> RiskAssessment:
        """Assess operational risks (equipment, labor, management)"""
        equipment_age = params.get('equipment_age', 8)  # years
        labor_reliability = params.get('labor_reliability', 0.8)  # 0.0 to 1.0
        management_experience = params.get('management_experience', 15)  # years
        
        risk_score = 0.0
        risk_factors = []
        
        # Equipment risk
        if equipment_age > 15:
            risk_score += 0.3
            risk_factors.append(f"Old equipment (avg age: {equipment_age} years)")
        elif equipment_age > 10:
            risk_score += 0.2
            risk_factors.append(f"Aging equipment (avg age: {equipment_age} years)")
        
        # Labor risk
        if labor_reliability < 0.6:
            risk_score += 0.3
            risk_factors.append(f"Low labor reliability ({labor_reliability:.1%})")
        elif labor_reliability < 0.8:
            risk_score += 0.2
            risk_factors.append(f"Moderate labor reliability ({labor_reliability:.1%})")
        
        # Management experience
        if management_experience < 5:
            risk_score += 0.3
            risk_factors.append(f"Limited experience ({management_experience} years)")
        elif management_experience < 10:
            risk_score += 0.1
            risk_factors.append(f"Moderate experience ({management_experience} years)")
        
        # Determine risk level
        if risk_score < 0.2:
            risk_level = RiskLevel.LOW
        elif risk_score < 0.4:
            risk_level = RiskLevel.MODERATE
        elif risk_score < 0.6:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH
        
        # Estimate operational failure cost
        annual_revenue = params.get('annual_revenue', 500000)
        potential_loss = annual_revenue * risk_score * 0.2
        
        return RiskAssessment(
            risk_type=RiskType.OPERATIONAL_RISK,
            risk_level=risk_level,
            probability=risk_score * 0.5,  # Convert to probability
            potential_loss=potential_loss,
            confidence_interval=0.65,
            risk_factors=risk_factors,
            mitigation_strategies=[
                "Maintain equipment preventively",
                "Train reliable labor force",
                "Develop backup operational plans",
                "Invest in modern technology"
            ]
        )
    
    def _assess_production_risk(self, farm_id: str, params: Dict[str, Any]) -> RiskAssessment:
        """Assess overall production risk combining multiple factors"""
        yield_risk = self._assess_yield_risk(farm_id, params)
        weather_risk = self._assess_weather_risk(farm_id, params)
        operational_risk = self._assess_operational_risk(farm_id, params)
        
        # Combine risks (simplified model)
        combined_probability = 1 - (
            (1 - yield_risk.probability) * 
            (1 - weather_risk.probability) * 
            (1 - operational_risk.probability)
        )
        
        combined_loss = yield_risk.potential_loss + weather_risk.potential_loss + operational_risk.potential_loss
        
        # Determine overall risk level
        if combined_probability < 0.3:
            risk_level = RiskLevel.LOW
        elif combined_probability < 0.5:
            risk_level = RiskLevel.MODERATE
        elif combined_probability < 0.7:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH
        
        all_factors = yield_risk.risk_factors + weather_risk.risk_factors + operational_risk.risk_factors
        all_strategies = list(set(
            yield_risk.mitigation_strategies + 
            weather_risk.mitigation_strategies + 
            operational_risk.mitigation_strategies
        ))
        
        return RiskAssessment(
            risk_type=RiskType.PRODUCTION_RISK,
            risk_level=risk_level,
            probability=combined_probability,
            potential_loss=combined_loss,
            confidence_interval=0.75,
            risk_factors=all_factors[:8],  # Limit to top factors
            mitigation_strategies=all_strategies[:8]  # Limit to top strategies
        )
    
    def purchase_insurance(self, farm_id: str, insurance_type: InsuranceType, 
                         crop_id: str, coverage_params: Dict[str, Any]) -> Optional[InsurancePolicy]:
        """Purchase crop insurance policy"""
        
        # Validate parameters
        coverage_level = coverage_params.get('coverage_level', 0.75)  # 75%
        acres = coverage_params.get('acres', 100.0)
        expected_yield = coverage_params.get('expected_yield')
        expected_price = coverage_params.get('expected_price')
        
        if not expected_yield or not expected_price:
            print(f"Error: Must provide expected yield and price for insurance")
            return None
        
        # Calculate insurance parameters
        liability_per_acre = expected_yield * expected_price * coverage_level
        total_liability = liability_per_acre * acres
        
        # Get premium rate (would be from actuarial tables in real system)
        base_premium_rate = self._get_insurance_premium_rate(insurance_type, crop_id, coverage_level)
        
        # Calculate premiums
        total_premium = total_liability * base_premium_rate
        subsidy_rate = self.risk_parameters['insurance_subsidy_rates'].get(insurance_type, 0.0)
        farmer_premium = total_premium * (1 - subsidy_rate)
        
        # Create policy
        policy_id = f"INS_{farm_id}_{crop_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        policy = InsurancePolicy(
            policy_id=policy_id,
            insurance_type=insurance_type,
            crop_id=crop_id,
            coverage_level=coverage_level,
            premium_rate=base_premium_rate,
            unit_structure=coverage_params.get('unit_structure', 'basic'),
            liability_per_acre=liability_per_acre,
            total_premium=total_premium,
            farmer_premium=farmer_premium,
            acres_covered=acres,
            policy_start_date=datetime.now(),
            policy_end_date=datetime.now() + timedelta(days=365)
        )
        
        # Store policy
        self.insurance_policies[policy_id] = policy
        
        # Add to farm's risk portfolio
        if farm_id not in self.risk_portfolios:
            self.risk_portfolios[farm_id] = RiskPortfolio(farm_id=farm_id)
        
        self.risk_portfolios[farm_id].active_policies.append(policy)
        
        # Emit event
        self.event_system.emit_event("insurance_purchased", {
            "farm_id": farm_id,
            "policy_id": policy_id,
            "insurance_type": insurance_type.value,
            "crop_id": crop_id,
            "farmer_premium": farmer_premium,
            "coverage_level": coverage_level
        })
        
        print(f"Insurance purchased: {insurance_type.value} for {crop_id}")
        print(f"Coverage: {coverage_level:.0%} on {acres:.0f} acres")
        print(f"Farmer premium: ${farmer_premium:,.2f}")
        
        return policy
    
    def create_hedge_position(self, farm_id: str, instrument: HedgingInstrument,
                            commodity_id: str, hedge_params: Dict[str, Any]) -> Optional[HedgePosition]:
        """Create market hedging position"""
        
        contract_size = hedge_params.get('contract_size', 5000)  # bushels
        current_price = hedge_params.get('current_price', 4.5)
        
        position_id = f"HEDGE_{farm_id}_{commodity_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if instrument == HedgingInstrument.FUTURES_CONTRACT:
            # Futures contract
            margin_rate = self.market_data['margin_rates'].get(commodity_id, 0.05)
            margin_requirement = contract_size * current_price * margin_rate
            
            position = HedgePosition(
                position_id=position_id,
                instrument=instrument,
                commodity_id=commodity_id,
                contract_size=contract_size,
                futures_price=current_price,
                expiration_date=datetime.now() + timedelta(days=90),
                margin_requirement=margin_requirement,
                current_value=contract_size * current_price,
                is_long=hedge_params.get('is_long', False)  # Typically short hedge for producers
            )
            
        elif instrument in [HedgingInstrument.PUT_OPTION, HedgingInstrument.CALL_OPTION]:
            # Options contract
            strike_price = hedge_params.get('strike_price', current_price)
            expiration_days = hedge_params.get('expiration_days', 60)
            
            # Calculate option premium using simplified Black-Scholes
            volatility = hedge_params.get('volatility', 0.25)
            risk_free_rate = self.market_data['interest_rates']
            
            option_premium = self._calculate_option_premium(
                current_price, strike_price, expiration_days / 365.0,
                risk_free_rate, volatility, instrument == HedgingInstrument.CALL_OPTION
            )
            
            premium_paid = option_premium * contract_size
            
            position = HedgePosition(
                position_id=position_id,
                instrument=instrument,
                commodity_id=commodity_id,
                contract_size=contract_size,
                strike_price=strike_price,
                premium_paid=premium_paid,
                expiration_date=datetime.now() + timedelta(days=expiration_days),
                current_value=premium_paid,
                is_long=hedge_params.get('is_long', True)  # Buy options for protection
            )
            
        else:
            print(f"Error: Hedging instrument {instrument} not implemented")
            return None
        
        # Store position
        self.hedge_positions[position_id] = position
        
        # Add to farm's risk portfolio
        if farm_id not in self.risk_portfolios:
            self.risk_portfolios[farm_id] = RiskPortfolio(farm_id=farm_id)
        
        self.risk_portfolios[farm_id].hedge_positions.append(position)
        
        # Emit event
        self.event_system.emit_event("hedge_position_created", {
            "farm_id": farm_id,
            "position_id": position_id,
            "instrument": instrument.value,
            "commodity_id": commodity_id,
            "contract_size": contract_size,
            "cost": getattr(position, 'premium_paid', position.margin_requirement)
        })
        
        print(f"Hedge position created: {instrument.value} for {commodity_id}")
        print(f"Size: {contract_size:,.0f} bushels")
        
        return position
    
    def optimize_risk_portfolio(self, farm_id: str) -> Dict[str, Any]:
        """Analyze and optimize farm's risk management portfolio"""
        
        if farm_id not in self.risk_portfolios:
            return {"error": "Farm not found in risk portfolios"}
        
        portfolio = self.risk_portfolios[farm_id]
        
        # Analyze current risk exposure
        total_exposure = self._calculate_total_risk_exposure(portfolio)
        insurance_coverage = self._calculate_insurance_coverage(portfolio)
        hedging_effectiveness = self._calculate_hedging_effectiveness(portfolio)
        diversification_score = self._calculate_diversification_score(portfolio)
        
        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(
            portfolio, total_exposure, insurance_coverage, hedging_effectiveness
        )
        
        # Update portfolio
        portfolio.total_risk_exposure = total_exposure
        portfolio.insurance_coverage_ratio = insurance_coverage
        portfolio.hedging_effectiveness = hedging_effectiveness
        portfolio.diversification_index = diversification_score
        portfolio.optimization_recommendations = recommendations
        
        # Return analysis
        return {
            "farm_id": farm_id,
            "total_risk_exposure": total_exposure,
            "insurance_coverage_ratio": insurance_coverage,
            "hedging_effectiveness": hedging_effectiveness,
            "diversification_index": diversification_score,
            "recommendations": recommendations,
            "risk_score": self._calculate_overall_risk_score(portfolio)
        }
    
    def _calculate_total_risk_exposure(self, portfolio: RiskPortfolio) -> float:
        """Calculate total risk exposure for portfolio"""
        total_exposure = 0.0
        
        for risk_assessment in portfolio.risk_assessments.values():
            # Weight by probability and potential loss
            exposure = risk_assessment.probability * risk_assessment.potential_loss
            total_exposure += exposure
        
        return total_exposure
    
    def _calculate_insurance_coverage(self, portfolio: RiskPortfolio) -> float:
        """Calculate insurance coverage ratio"""
        if not portfolio.active_policies:
            return 0.0
        
        total_coverage = sum(policy.liability_per_acre * policy.acres_covered 
                           for policy in portfolio.active_policies if policy.is_active)
        
        # Estimate total production value (simplified)
        estimated_production_value = sum(
            assessment.potential_loss / assessment.probability
            for assessment in portfolio.risk_assessments.values()
            if assessment.risk_type in [RiskType.YIELD_RISK, RiskType.PRODUCTION_RISK] 
            and assessment.probability > 0
        )
        
        if estimated_production_value == 0:
            return 0.0
        
        return min(total_coverage / estimated_production_value, 1.0)
    
    def _calculate_hedging_effectiveness(self, portfolio: RiskPortfolio) -> float:
        """Calculate hedging effectiveness score"""
        if not portfolio.hedge_positions:
            return 0.0
        
        # Simplified hedging effectiveness calculation
        # In practice, this would use beta calculations and correlation analysis
        total_hedge_value = sum(abs(pos.current_value) for pos in portfolio.hedge_positions)
        
        price_risk_exposure = sum(
            assessment.potential_loss
            for assessment in portfolio.risk_assessments.values()
            if assessment.risk_type == RiskType.PRICE_RISK
        )
        
        if price_risk_exposure == 0:
            return 0.0
        
        return min(total_hedge_value / price_risk_exposure, 1.0)
    
    def _calculate_diversification_score(self, portfolio: RiskPortfolio) -> float:
        """Calculate portfolio diversification score"""
        # Simplified diversification calculation
        # Higher score for more diverse risk types and mitigation strategies
        
        risk_types_count = len(portfolio.risk_assessments)
        insurance_types_count = len(set(policy.insurance_type for policy in portfolio.active_policies))
        hedge_types_count = len(set(pos.instrument for pos in portfolio.hedge_positions))
        
        # Normalize to 0-1 scale
        diversification_score = min((risk_types_count + insurance_types_count + hedge_types_count) / 10.0, 1.0)
        
        return diversification_score
    
    def _generate_optimization_recommendations(self, portfolio: RiskPortfolio, 
                                            total_exposure: float, insurance_coverage: float,
                                            hedging_effectiveness: float) -> List[str]:
        """Generate risk management optimization recommendations"""
        recommendations = []
        
        # Insurance recommendations
        if insurance_coverage < 0.6:
            recommendations.append("Consider increasing crop insurance coverage to 70-80% level")
        
        # Hedging recommendations  
        if hedging_effectiveness < 0.3:
            recommendations.append("Implement price risk hedging using futures or options")
        
        # Diversification recommendations
        if portfolio.diversification_index < 0.4:
            recommendations.append("Diversify crop portfolio to reduce concentration risk")
        
        # High exposure recommendations
        if total_exposure > 100000:  # $100k threshold
            recommendations.append("Total risk exposure is high - consider additional risk mitigation")
        
        # Specific risk recommendations
        for risk_type, assessment in portfolio.risk_assessments.items():
            if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                recommendations.extend(assessment.mitigation_strategies[:2])  # Top 2 strategies
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_overall_risk_score(self, portfolio: RiskPortfolio) -> float:
        """Calculate overall risk score (0-100, lower is better)"""
        base_risk_score = min(portfolio.total_risk_exposure / 50000 * 100, 100)  # Scale exposure to 0-100
        
        # Adjust for risk mitigation
        insurance_adjustment = portfolio.insurance_coverage_ratio * -20  # Up to -20 points
        hedging_adjustment = portfolio.hedging_effectiveness * -15      # Up to -15 points  
        diversification_adjustment = portfolio.diversification_index * -10  # Up to -10 points
        
        final_score = max(base_risk_score + insurance_adjustment + hedging_adjustment + diversification_adjustment, 0)
        
        return min(final_score, 100)
    
    def _get_insurance_premium_rate(self, insurance_type: InsuranceType, 
                                   crop_id: str, coverage_level: float) -> float:
        """Get insurance premium rate (would use actuarial tables in production)"""
        # Simplified premium rate calculation
        base_rates = {
            InsuranceType.MPCI: 0.04,              # 4% of liability
            InsuranceType.REVENUE_PROTECTION: 0.045,  # 4.5% of liability  
            InsuranceType.YIELD_PROTECTION: 0.035,    # 3.5% of liability
            InsuranceType.CROP_HAIL: 0.02,           # 2% of liability
            InsuranceType.WHOLE_FARM: 0.06           # 6% of liability
        }
        
        base_rate = base_rates.get(insurance_type, 0.04)
        
        # Adjust for coverage level (higher coverage = higher rate)
        coverage_adjustment = (coverage_level - 0.5) * 0.5  # +/- 0.15 max
        
        # Adjust for crop (some crops riskier than others)
        crop_adjustments = {
            'corn': 0.0,
            'soybeans': 0.003,
            'wheat': 0.002,
            'cotton': 0.008
        }
        crop_adjustment = crop_adjustments.get(crop_id, 0.0)
        
        return base_rate + coverage_adjustment + crop_adjustment
    
    def _calculate_option_premium(self, spot_price: float, strike_price: float, 
                                time_to_expiry: float, risk_free_rate: float,
                                volatility: float, is_call: bool) -> float:
        """Calculate option premium using simplified Black-Scholes model"""
        
        # Simplified Black-Scholes calculation
        import math
        
        d1 = (math.log(spot_price / strike_price) + 
             (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
        d2 = d1 - volatility * math.sqrt(time_to_expiry)
        
        # Approximate normal CDF
        def norm_cdf(x):
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))
        
        if is_call:
            premium = (spot_price * norm_cdf(d1) - 
                      strike_price * math.exp(-risk_free_rate * time_to_expiry) * norm_cdf(d2))
        else:
            premium = (strike_price * math.exp(-risk_free_rate * time_to_expiry) * norm_cdf(-d2) -
                      spot_price * norm_cdf(-d1))
        
        return max(premium, 0.01)  # Minimum premium of 1 cent
    
    def _calculate_normal_cdf(self, x: float, mean: float, std_dev: float) -> float:
        """Calculate cumulative distribution function for normal distribution"""
        import math
        z = (x - mean) / std_dev
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))
    
    def _adjust_weather_probability(self, risk_factor: str, crop_stage: str, base_probability: float) -> float:
        """Adjust weather risk probability based on crop growth stage"""
        # Different weather risks are more critical at different growth stages
        stage_multipliers = {
            'drought': {
                'planting': 0.8,
                'vegetative': 1.2,
                'reproductive': 1.5,
                'maturity': 1.0
            },
            'hail': {
                'planting': 0.5,
                'vegetative': 1.0,
                'reproductive': 1.8,  # Most vulnerable
                'maturity': 1.2
            },
            'freeze': {
                'planting': 1.5,      # Early season freeze risk
                'vegetative': 1.0,
                'reproductive': 0.3,   # Later in season
                'maturity': 0.1
            }
        }
        
        multiplier = stage_multipliers.get(risk_factor, {}).get(crop_stage, 1.0)
        return min(base_probability * multiplier, 1.0)
    
    # Event handlers for system integration
    def _handle_price_update(self, event_data: Dict[str, Any]):
        """Handle market price updates for hedging positions"""
        commodity_id = event_data.get('commodity_id')
        new_price = event_data.get('price')
        
        if not commodity_id or not new_price:
            return
        
        # Update hedge positions
        for position in self.hedge_positions.values():
            if position.commodity_id == commodity_id:
                self._update_hedge_position_value(position, new_price)
    
    def _handle_weather_update(self, event_data: Dict[str, Any]):
        """Handle weather forecast updates for risk assessment"""
        location_id = event_data.get('location_id', 'midwest')
        weather_forecast = event_data.get('forecast', {})
        
        # Update weather risk assessment
        if location_id in self.weather_risks:
            self._update_weather_risk_assessment(location_id, weather_forecast)
    
    def _handle_yield_report(self, event_data: Dict[str, Any]):
        """Handle crop yield reports for insurance claims"""
        farm_id = event_data.get('farm_id')
        crop_id = event_data.get('crop_id')
        actual_yield = event_data.get('actual_yield')
        
        if farm_id and crop_id and actual_yield is not None:
            self._process_potential_insurance_claim(farm_id, crop_id, actual_yield)
    
    def _handle_season_change(self, event_data: Dict[str, Any]):
        """Handle seasonal changes affecting risk profiles"""
        new_season = event_data.get('season')
        
        # Update seasonal risk adjustments
        for portfolio in self.risk_portfolios.values():
            self._update_seasonal_risk_adjustments(portfolio, new_season)
    
    def _handle_financial_update(self, event_data: Dict[str, Any]):
        """Handle financial statement updates for credit risk assessment"""
        farm_id = event_data.get('farm_id')
        financial_data = event_data.get('financial_data', {})
        
        if farm_id and financial_data:
            # Update credit risk assessment
            credit_assessment = self._assess_credit_risk(farm_id, {'financial_metrics': financial_data})
            
            if farm_id in self.risk_portfolios:
                self.risk_portfolios[farm_id].risk_assessments[RiskType.CREDIT_RISK] = credit_assessment
    
    def _update_hedge_position_value(self, position: HedgePosition, current_price: float):
        """Update hedge position current value and P&L"""
        if position.instrument == HedgingInstrument.FUTURES_CONTRACT:
            # Futures P&L calculation
            price_change = current_price - position.futures_price
            if not position.is_long:
                price_change = -price_change  # Short position
            
            position.unrealized_pnl = price_change * position.contract_size
            position.current_value = current_price * position.contract_size
            
        elif position.instrument in [HedgingInstrument.PUT_OPTION, HedgingInstrument.CALL_OPTION]:
            # Options value update (simplified)
            intrinsic_value = 0.0
            if position.instrument == HedgingInstrument.CALL_OPTION:
                intrinsic_value = max(current_price - position.strike_price, 0)
            else:  # Put option
                intrinsic_value = max(position.strike_price - current_price, 0)
            
            position.current_value = intrinsic_value * position.contract_size
            position.unrealized_pnl = position.current_value - position.premium_paid
    
    def _update_weather_risk_assessment(self, location_id: str, weather_forecast: Dict[str, Any]):
        """Update weather risk based on forecast data"""
        if location_id not in self.weather_risks:
            return
        
        weather_risk = self.weather_risks[location_id]
        
        # Update current forecast risk based on weather forecast
        forecast_risks = {}
        
        # Example forecast analysis
        precipitation_forecast = weather_forecast.get('precipitation_mm', 0)
        temperature_forecast = weather_forecast.get('temperature_c', 20)
        
        if precipitation_forecast > 50:  # Heavy rain forecast
            forecast_risks['flood'] = 0.4
        elif precipitation_forecast < 5:  # Little rain forecast
            forecast_risks['drought'] = 0.3
        
        if temperature_forecast < 0:  # Freezing temperatures
            forecast_risks['freeze'] = 0.6
        
        weather_risk.current_forecast_risk = forecast_risks
    
    def _process_potential_insurance_claim(self, farm_id: str, crop_id: str, actual_yield: float):
        """Process potential insurance claims based on actual yield"""
        # Find active insurance policies for this farm and crop
        farm_policies = []
        if farm_id in self.risk_portfolios:
            farm_policies = [p for p in self.risk_portfolios[farm_id].active_policies 
                           if p.crop_id == crop_id and p.is_active]
        
        for policy in farm_policies:
            # Calculate expected yield based on policy
            expected_yield = policy.liability_per_acre / (policy.coverage_level * 4.5)  # Assuming $4.5 price
            trigger_yield = expected_yield * policy.coverage_level
            
            if actual_yield < trigger_yield:
                # Potential claim
                yield_shortfall = trigger_yield - actual_yield
                claim_amount = yield_shortfall * policy.acres_covered * 4.5
                
                self.event_system.emit_event("insurance_claim_triggered", {
                    "farm_id": farm_id,
                    "policy_id": policy.policy_id,
                    "crop_id": crop_id,
                    "actual_yield": actual_yield,
                    "trigger_yield": trigger_yield,
                    "claim_amount": claim_amount
                })
    
    def _update_seasonal_risk_adjustments(self, portfolio: RiskPortfolio, season: str):
        """Update risk assessments for seasonal changes"""
        # Seasonal risk adjustments would be implemented here
        # For example, higher weather risks during storm season
        pass
    
    def get_risk_management_status(self) -> Dict[str, Any]:
        """Get comprehensive risk management system status"""
        return {
            "system_status": "active" if self.is_initialized else "inactive",
            "total_portfolios": len(self.risk_portfolios),
            "active_insurance_policies": len([p for p in self.insurance_policies.values() if p.is_active]),
            "active_hedge_positions": len(self.hedge_positions),
            "total_insured_liability": sum(
                p.liability_per_acre * p.acres_covered 
                for p in self.insurance_policies.values() if p.is_active
            ),
            "total_hedge_exposure": sum(
                abs(p.current_value) for p in self.hedge_positions.values()
            )
        }

# Global convenience functions
def get_risk_management_system() -> Optional[RiskManagementSystem]:
    """Get the global risk management system instance"""
    # This would typically be managed by a system registry
    return None

def assess_farm_risk(farm_id: str, risk_type: RiskType, parameters: Dict[str, Any]) -> Optional[RiskAssessment]:
    """Convenience function to assess specific farm risk"""
    system = get_risk_management_system()
    if system:
        return system.create_risk_assessment(farm_id, risk_type, parameters)
    return None

def purchase_crop_insurance(farm_id: str, crop_id: str, coverage_params: Dict[str, Any]) -> Optional[InsurancePolicy]:
    """Convenience function to purchase crop insurance"""
    system = get_risk_management_system()
    if system:
        insurance_type = coverage_params.get('insurance_type', InsuranceType.MPCI)
        return system.purchase_insurance(farm_id, insurance_type, crop_id, coverage_params)
    return None

def create_hedge(farm_id: str, commodity_id: str, hedge_params: Dict[str, Any]) -> Optional[HedgePosition]:
    """Convenience function to create market hedge"""
    system = get_risk_management_system()
    if system:
        instrument = hedge_params.get('instrument', HedgingInstrument.FUTURES_CONTRACT)
        return system.create_hedge_position(farm_id, instrument, commodity_id, hedge_params)
    return None