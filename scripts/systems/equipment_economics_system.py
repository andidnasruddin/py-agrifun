"""
Equipment Economics System - Comprehensive Financial Analysis for Agricultural Equipment

This system provides sophisticated economic modeling and decision-making tools for
agricultural equipment acquisition, operation, and management. Integrates with all
equipment systems to provide real-world financial analysis and recommendations.

Key Features:
- Purchase vs Lease analysis with detailed cash flow modeling
- Total Cost of Ownership (TCO) calculations over equipment lifetime
- Custom harvesting vs ownership economic comparisons
- Equipment financing options with loan modeling
- Depreciation schedules and tax implications
- Operational cost tracking and budgeting
- ROI and payback period calculations
- Market timing analysis for equipment purchases
- Fleet optimization and replacement timing

Financial Models:
- Net Present Value (NPV) analysis for long-term decisions
- Internal Rate of Return (IRR) calculations
- Cash flow projections with seasonal variations
- Risk assessment and sensitivity analysis
- Tax depreciation (MACRS, Section 179, Bonus depreciation)
- Insurance and warranty cost modeling

Educational Value:
- Understanding of agricultural equipment financing
- Capital budgeting and investment analysis
- Risk management in equipment decisions
- Tax planning strategies for equipment purchases
- Business planning and cash flow management
"""

import time
import uuid
from typing import Dict, List, Set, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import math

# Import core systems
from ..core.advanced_event_system import get_event_system, EventPriority
from ..core.entity_component_system import get_entity_manager, Component, ComponentCategory
from ..core.advanced_config_system import get_config_manager
from ..core.time_management import get_time_manager

class FinancingType(Enum):
    """Types of equipment financing"""
    CASH_PURCHASE = "cash_purchase"      # Full cash payment
    BANK_LOAN = "bank_loan"             # Traditional bank financing
    DEALER_FINANCING = "dealer_financing" # Manufacturer/dealer financing
    LEASE_TO_OWN = "lease_to_own"       # Lease with purchase option
    OPERATING_LEASE = "operating_lease"  # True operating lease
    CUSTOM_SERVICE = "custom_service"    # Hire custom operator

class DepreciationMethod(Enum):
    """Depreciation calculation methods"""
    STRAIGHT_LINE = "straight_line"      # Equal annual depreciation
    DECLINING_BALANCE = "declining_balance" # Accelerated depreciation
    MACRS = "macrs"                     # Modified Accelerated Cost Recovery System
    SECTION_179 = "section_179"         # Immediate expense deduction
    BONUS_DEPRECIATION = "bonus_depreciation" # First-year bonus depreciation

class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"           # Stable, predictable operations
    MEDIUM = "medium"     # Average farming risks
    HIGH = "high"         # High variability, weather dependent
    VERY_HIGH = "very_high" # Extremely volatile operations

@dataclass
class LoanTerms:
    """Loan financing terms and conditions"""
    principal_amount: float           # Loan amount
    annual_interest_rate: float       # Annual interest rate (as decimal)
    loan_term_years: int             # Loan duration in years
    payment_frequency: int           # Payments per year (12 = monthly)
    down_payment_percent: float      # Down payment as percentage
    origination_fee_percent: float   # Loan origination fee
    prepayment_penalty: bool         # Whether prepayment penalty applies
    variable_rate: bool              # Whether interest rate is variable
    
    def calculate_monthly_payment(self) -> float:
        """Calculate monthly loan payment using amortization formula"""
        if self.annual_interest_rate == 0:
            return self.principal_amount / (self.loan_term_years * self.payment_frequency)
        
        monthly_rate = self.annual_interest_rate / self.payment_frequency
        num_payments = self.loan_term_years * self.payment_frequency
        
        payment = self.principal_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                 ((1 + monthly_rate) ** num_payments - 1)
        
        return payment

@dataclass
class LeaseTerms:
    """Lease financing terms and conditions"""
    monthly_payment: float           # Monthly lease payment
    lease_term_months: int          # Lease duration in months
    security_deposit: float         # Upfront security deposit
    maintenance_included: bool      # Whether maintenance is included
    insurance_included: bool        # Whether insurance is included
    mileage_limit_annual: Optional[int] # Annual usage hour limit
    excess_usage_rate: float        # Cost per hour over limit
    purchase_option_percent: float  # Purchase option as % of original value
    early_termination_penalty: float # Early termination penalty
    
    def calculate_total_lease_cost(self) -> float:
        """Calculate total cost of lease term"""
        total_payments = self.monthly_payment * self.lease_term_months
        return total_payments + self.security_deposit

@dataclass
class CustomServiceTerms:
    """Custom service provider terms"""
    rate_per_acre: float            # Base rate per acre
    rate_per_hour: float            # Alternative hourly rate
    fuel_included: bool             # Whether fuel is included
    operator_included: bool         # Whether operator is included
    insurance_covered: bool         # Whether service provider carries insurance
    availability_guarantee: bool    # Whether availability is guaranteed
    quality_guarantee: bool         # Whether work quality is guaranteed
    seasonal_rate_adjustment: Dict[str, float] # Seasonal rate multipliers
    volume_discounts: Dict[str, float] # Volume-based discounts (acres -> discount%)

@dataclass
class EquipmentEconomicsComponent(Component):
    """ECS component for equipment economic data"""
    # Financial tracking
    purchase_price: float = 0.0
    current_market_value: float = 0.0
    accumulated_depreciation: float = 0.0
    
    # Operational costs
    fuel_costs_total: float = 0.0
    maintenance_costs_total: float = 0.0
    insurance_costs_total: float = 0.0
    operator_costs_total: float = 0.0
    
    # Revenue and savings
    revenue_generated: float = 0.0
    cost_savings_realized: float = 0.0
    
    # Usage tracking
    total_operating_hours: float = 0.0
    total_acres_worked: float = 0.0
    utilization_rate: float = 0.0  # Actual hours / Available hours
    
    # Financial metrics
    annual_depreciation: float = 0.0
    cost_per_hour: float = 0.0
    cost_per_acre: float = 0.0
    return_on_investment: float = 0.0
    payback_period_years: float = 0.0
    
    # Financing details
    financing_type: Optional[FinancingType] = None
    loan_balance: float = 0.0
    monthly_payment: float = 0.0
    
    category: ComponentCategory = ComponentCategory.ECONOMIC

@dataclass
class EquipmentAnalysis:
    """Comprehensive economic analysis of equipment"""
    equipment_id: str
    analysis_date: float
    
    # Cost breakdown
    purchase_costs: Dict[str, float]
    operating_costs: Dict[str, float]
    financing_costs: Dict[str, float]
    opportunity_costs: Dict[str, float]
    
    # Revenue and benefits
    revenue_sources: Dict[str, float]
    cost_savings: Dict[str, float]
    tax_benefits: Dict[str, float]
    
    # Financial metrics
    total_cost_of_ownership: float
    net_present_value: float
    internal_rate_of_return: float
    payback_period: float
    
    # Sensitivity analysis
    break_even_hours: float
    break_even_acres: float
    risk_assessment: RiskLevel

class EquipmentEconomicsSystem:
    """Comprehensive equipment economics and financial analysis system"""
    
    def __init__(self):
        """Initialize the equipment economics system"""
        self.system_name = "equipment_economics_system"
        self.event_system = get_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_config_manager()
        self.time_manager = get_time_manager()
        
        # Economic parameters
        self.discount_rate = 0.06  # 6% discount rate for NPV calculations
        self.inflation_rate = 0.03  # 3% annual inflation
        self.tax_rate = 0.25      # 25% tax rate
        self.fuel_price_trend = 0.04  # 4% annual fuel price increase
        
        # Equipment tracking
        self.equipment_analyses: Dict[str, EquipmentAnalysis] = {}
        self.financing_options: Dict[str, Dict] = {}
        self.market_conditions: Dict[str, float] = {}
        
        # Custom service rates by region/crop
        self.custom_service_rates: Dict[str, CustomServiceTerms] = {}
        
        # System state
        self.initialized = False
        
        print("Equipment Economics System initialized")
    
    def initialize(self) -> bool:
        """Initialize the equipment economics system"""
        try:
            # Subscribe to events
            self.event_system.subscribe('equipment_purchased', self._handle_equipment_purchased)
            self.event_system.subscribe('equipment_operated', self._handle_equipment_operated)
            self.event_system.subscribe('maintenance_performed', self._handle_maintenance_performed)
            self.event_system.subscribe('fuel_price_updated', self._handle_fuel_price_change)
            self.event_system.subscribe('market_conditions_updated', self._handle_market_change)
            
            # Load economic parameters from config
            self._load_economic_parameters()
            
            # Initialize custom service rates
            self._load_custom_service_rates()
            
            # Initialize financing options
            self._initialize_financing_options()
            
            self.initialized = True
            
            # Emit initialization complete event
            self.event_system.emit('equipment_economics_initialized', {
                'discount_rate': self.discount_rate,
                'system_status': 'ready'
            }, priority=EventPriority.NORMAL)
            
            print("Equipment Economics System initialization complete")
            return True
            
        except Exception as e:
            print(f"Failed to initialize Equipment Economics System: {e}")
            return False
    
    def _load_economic_parameters(self):
        """Load economic parameters from configuration"""
        # These would typically come from config files or market data
        self.market_conditions = {
            'equipment_inflation_rate': 0.035,
            'used_equipment_depreciation': 0.15,
            'fuel_price_volatility': 0.12,
            'interest_rate_environment': 0.055,
            'agricultural_commodity_outlook': 1.05  # Positive outlook
        }
    
    def _load_custom_service_rates(self):
        """Load custom service rates for different operations"""
        self.custom_service_rates = {
            'tillage': CustomServiceTerms(
                rate_per_acre=22.00,
                rate_per_hour=185.00,
                fuel_included=True,
                operator_included=True,
                insurance_covered=True,
                availability_guarantee=False,
                quality_guarantee=True,
                seasonal_rate_adjustment={'spring': 1.1, 'fall': 1.0},
                volume_discounts={100: 0.05, 500: 0.10, 1000: 0.15}
            ),
            'planting': CustomServiceTerms(
                rate_per_acre=28.00,
                rate_per_hour=225.00,
                fuel_included=True,
                operator_included=True,
                insurance_covered=True,
                availability_guarantee=False,
                quality_guarantee=True,
                seasonal_rate_adjustment={'spring': 1.15, 'fall': 0.90},
                volume_discounts={100: 0.05, 500: 0.10, 1000: 0.15}
            ),
            'harvesting_corn': CustomServiceTerms(
                rate_per_acre=42.00,
                rate_per_hour=350.00,
                fuel_included=True,
                operator_included=True,
                insurance_covered=True,
                availability_guarantee=True,
                quality_guarantee=True,
                seasonal_rate_adjustment={'fall': 1.0},
                volume_discounts={200: 0.05, 800: 0.10, 2000: 0.15}
            ),
            'harvesting_soybeans': CustomServiceTerms(
                rate_per_acre=38.00,
                rate_per_hour=320.00,
                fuel_included=True,
                operator_included=True,
                insurance_covered=True,
                availability_guarantee=True,
                quality_guarantee=True,
                seasonal_rate_adjustment={'fall': 1.0},
                volume_discounts={200: 0.05, 800: 0.10, 2000: 0.15}
            ),
            'spraying': CustomServiceTerms(
                rate_per_acre=12.50,
                rate_per_hour=95.00,
                fuel_included=False,  # Chemicals separate
                operator_included=True,
                insurance_covered=True,
                availability_guarantee=False,
                quality_guarantee=True,
                seasonal_rate_adjustment={'spring': 1.05, 'summer': 1.1, 'fall': 0.95},
                volume_discounts={500: 0.05, 1500: 0.10, 3000: 0.15}
            )
        }
    
    def _initialize_financing_options(self):
        """Initialize common financing options"""
        self.financing_options = {
            'bank_loan_5yr': {
                'type': FinancingType.BANK_LOAN,
                'interest_rate': 0.065,
                'term_years': 5,
                'down_payment_percent': 0.20,
                'origination_fee': 0.015
            },
            'bank_loan_7yr': {
                'type': FinancingType.BANK_LOAN,
                'interest_rate': 0.070,
                'term_years': 7,
                'down_payment_percent': 0.15,
                'origination_fee': 0.015
            },
            'dealer_financing': {
                'type': FinancingType.DEALER_FINANCING,
                'interest_rate': 0.059,  # Often promotional rates
                'term_years': 5,
                'down_payment_percent': 0.10,
                'origination_fee': 0.005
            },
            'operating_lease': {
                'type': FinancingType.OPERATING_LEASE,
                'monthly_rate_percent': 0.018,  # 1.8% of value per month
                'term_years': 4,
                'purchase_option_percent': 0.35
            }
        }
    
    def create_equipment_economics_component(self, entity_id: str, purchase_price: float, 
                                           financing_type: FinancingType = FinancingType.CASH_PURCHASE) -> bool:
        """Add economic tracking component to equipment entity"""
        economics_component = EquipmentEconomicsComponent(
            purchase_price=purchase_price,
            current_market_value=purchase_price,
            financing_type=financing_type
        )
        
        self.entity_manager.add_component(entity_id, 'equipment_economics', economics_component)
        
        return True
    
    def analyze_purchase_vs_lease(self, equipment_specs: Dict[str, Any], 
                                 usage_params: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive purchase vs lease analysis"""
        purchase_price = equipment_specs.get('price', 0)
        annual_hours = usage_params.get('annual_hours', 200)
        analysis_years = usage_params.get('analysis_years', 7)
        
        # Purchase analysis
        purchase_analysis = self._analyze_purchase_option(equipment_specs, usage_params)
        
        # Lease analysis
        lease_analysis = self._analyze_lease_option(equipment_specs, usage_params)
        
        # Custom service analysis
        custom_analysis = self._analyze_custom_service_option(equipment_specs, usage_params)
        
        # Comparison and recommendation
        comparison = self._compare_financing_options(purchase_analysis, lease_analysis, custom_analysis)
        
        return {
            'purchase_analysis': purchase_analysis,
            'lease_analysis': lease_analysis,
            'custom_service_analysis': custom_analysis,
            'comparison': comparison,
            'recommendation': self._generate_recommendation(comparison, usage_params)
        }
    
    def _analyze_purchase_option(self, equipment_specs: Dict[str, Any], 
                                usage_params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze equipment purchase option"""
        purchase_price = equipment_specs.get('price', 0)
        annual_hours = usage_params.get('annual_hours', 200)
        analysis_years = usage_params.get('analysis_years', 7)
        financing_option = usage_params.get('financing_option', 'cash_purchase')
        
        # Initial costs
        if financing_option == 'cash_purchase':
            initial_cash_outlay = purchase_price
            loan_payments = []
        else:
            # Financed purchase
            financing = self.financing_options.get('bank_loan_5yr', {})
            down_payment = purchase_price * financing.get('down_payment_percent', 0.20)
            loan_amount = purchase_price - down_payment
            interest_rate = financing.get('interest_rate', 0.065)
            term_years = financing.get('term_years', 5)
            
            loan_terms = LoanTerms(
                principal_amount=loan_amount,
                annual_interest_rate=interest_rate,
                loan_term_years=term_years,
                payment_frequency=12,
                down_payment_percent=financing.get('down_payment_percent', 0.20),
                origination_fee_percent=financing.get('origination_fee', 0.015),
                prepayment_penalty=False,
                variable_rate=False
            )
            
            initial_cash_outlay = down_payment + (loan_amount * loan_terms.origination_fee_percent)
            monthly_payment = loan_terms.calculate_monthly_payment()
            loan_payments = [monthly_payment * 12] * min(term_years, analysis_years)
        
        # Annual operating costs
        fuel_cost_per_hour = equipment_specs.get('fuel_cost_per_hour', 25.00)
        maintenance_cost_per_hour = equipment_specs.get('maintenance_cost_per_hour', 15.00)
        insurance_rate = equipment_specs.get('insurance_rate', 0.015)
        
        annual_costs = []
        salvage_values = []
        
        for year in range(analysis_years):
            # Operating costs (increasing with inflation)
            fuel_cost = fuel_cost_per_hour * annual_hours * (1 + self.fuel_price_trend) ** year
            maintenance_cost = maintenance_cost_per_hour * annual_hours * (1 + self.inflation_rate) ** year
            insurance_cost = purchase_price * insurance_rate * (1 + self.inflation_rate) ** year
            
            # Depreciation (tax benefit)
            depreciation = self._calculate_depreciation(purchase_price, year, DepreciationMethod.MACRS)
            tax_savings = depreciation * self.tax_rate
            
            annual_cost = fuel_cost + maintenance_cost + insurance_cost - tax_savings
            if year < len(loan_payments):
                annual_cost += loan_payments[year]
            
            annual_costs.append(annual_cost)
            
            # Calculate salvage value
            depreciation_rate = equipment_specs.get('depreciation_rate', 0.12)
            salvage_value = purchase_price * (1 - depreciation_rate) ** (year + 1)
            salvage_values.append(salvage_value)
        
        # Calculate NPV
        cash_flows = [-initial_cash_outlay] + [-cost for cost in annual_costs]
        cash_flows[-1] += salvage_values[-1]  # Add salvage value to final year
        
        npv = self._calculate_npv(cash_flows, self.discount_rate)
        
        # Calculate cost per hour and per acre
        total_costs = initial_cash_outlay + sum(annual_costs) - salvage_values[-1]
        total_hours = annual_hours * analysis_years
        cost_per_hour = total_costs / total_hours if total_hours > 0 else 0
        
        annual_acres = usage_params.get('annual_acres', annual_hours * 8)  # Estimate acres
        total_acres = annual_acres * analysis_years
        cost_per_acre = total_costs / total_acres if total_acres > 0 else 0
        
        return {
            'initial_cash_outlay': initial_cash_outlay,
            'annual_costs': annual_costs,
            'total_costs': total_costs,
            'salvage_value': salvage_values[-1],
            'net_present_value': npv,
            'cost_per_hour': cost_per_hour,
            'cost_per_acre': cost_per_acre,
            'financing_type': financing_option,
            'cash_flows': cash_flows
        }
    
    def _analyze_lease_option(self, equipment_specs: Dict[str, Any], 
                             usage_params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze equipment lease option"""
        purchase_price = equipment_specs.get('price', 0)
        annual_hours = usage_params.get('annual_hours', 200)
        analysis_years = usage_params.get('analysis_years', 7)
        
        lease_terms = LeaseTerms(
            monthly_payment=purchase_price * 0.018,  # 1.8% of value per month
            lease_term_months=48,  # 4 years
            security_deposit=purchase_price * 0.05,
            maintenance_included=False,
            insurance_included=False,
            mileage_limit_annual=300,  # 300 hours per year
            excess_usage_rate=150.00,  # $150 per hour over limit
            purchase_option_percent=0.35,
            early_termination_penalty=0.15
        )
        
        # Initial costs
        initial_cash_outlay = lease_terms.security_deposit
        
        # Annual costs
        annual_costs = []
        lease_years = min(lease_terms.lease_term_months // 12, analysis_years)
        
        for year in range(analysis_years):
            if year < lease_years:
                # Lease payments
                annual_lease_payment = lease_terms.monthly_payment * 12
                
                # Excess usage charges
                excess_hours = max(0, annual_hours - lease_terms.mileage_limit_annual)
                excess_charges = excess_hours * lease_terms.excess_usage_rate
                
                # Operating costs not included in lease
                fuel_cost = equipment_specs.get('fuel_cost_per_hour', 25.00) * annual_hours * (1 + self.fuel_price_trend) ** year
                if not lease_terms.maintenance_included:
                    maintenance_cost = equipment_specs.get('maintenance_cost_per_hour', 15.00) * annual_hours * (1 + self.inflation_rate) ** year
                else:
                    maintenance_cost = 0
                
                if not lease_terms.insurance_included:
                    insurance_cost = purchase_price * 0.015 * (1 + self.inflation_rate) ** year
                else:
                    insurance_cost = 0
                
                annual_cost = annual_lease_payment + excess_charges + fuel_cost + maintenance_cost + insurance_cost
                
                # Tax benefit (lease payments are deductible)
                tax_savings = annual_lease_payment * self.tax_rate
                annual_cost -= tax_savings
                
            else:
                # Post-lease period - purchase or replace
                if year == lease_years:
                    # Purchase option
                    purchase_option_cost = purchase_price * lease_terms.purchase_option_percent
                    annual_cost = purchase_option_cost
                else:
                    # Own the equipment - only operating costs
                    fuel_cost = equipment_specs.get('fuel_cost_per_hour', 25.00) * annual_hours * (1 + self.fuel_price_trend) ** year
                    maintenance_cost = equipment_specs.get('maintenance_cost_per_hour', 15.00) * annual_hours * (1 + self.inflation_rate) ** year
                    insurance_cost = purchase_price * lease_terms.purchase_option_percent * 0.015 * (1 + self.inflation_rate) ** year
                    
                    # Depreciation tax benefit on owned equipment
                    current_value = purchase_price * lease_terms.purchase_option_percent
                    depreciation = self._calculate_depreciation(current_value, year - lease_years, DepreciationMethod.MACRS)
                    tax_savings = depreciation * self.tax_rate
                    
                    annual_cost = fuel_cost + maintenance_cost + insurance_cost - tax_savings
            
            annual_costs.append(annual_cost)
        
        # Calculate NPV
        cash_flows = [-initial_cash_outlay] + [-cost for cost in annual_costs]
        
        # Add salvage value if equipment is owned at end
        if analysis_years > lease_years:
            current_value = purchase_price * lease_terms.purchase_option_percent
            depreciation_rate = equipment_specs.get('depreciation_rate', 0.12)
            years_owned = analysis_years - lease_years
            salvage_value = current_value * (1 - depreciation_rate) ** years_owned
            cash_flows[-1] += salvage_value
        else:
            salvage_value = 0
        
        npv = self._calculate_npv(cash_flows, self.discount_rate)
        
        # Calculate cost metrics
        total_costs = initial_cash_outlay + sum(annual_costs) - salvage_value
        total_hours = annual_hours * analysis_years
        cost_per_hour = total_costs / total_hours if total_hours > 0 else 0
        
        annual_acres = usage_params.get('annual_acres', annual_hours * 8)
        total_acres = annual_acres * analysis_years
        cost_per_acre = total_costs / total_acres if total_acres > 0 else 0
        
        return {
            'initial_cash_outlay': initial_cash_outlay,
            'annual_costs': annual_costs,
            'total_costs': total_costs,
            'salvage_value': salvage_value,
            'net_present_value': npv,
            'cost_per_hour': cost_per_hour,
            'cost_per_acre': cost_per_acre,
            'lease_terms': lease_terms.__dict__,
            'cash_flows': cash_flows
        }
    
    def _analyze_custom_service_option(self, equipment_specs: Dict[str, Any], 
                                      usage_params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze custom service option"""
        equipment_type = equipment_specs.get('equipment_type', 'tillage')
        annual_hours = usage_params.get('annual_hours', 200)
        annual_acres = usage_params.get('annual_acres', annual_hours * 8)
        analysis_years = usage_params.get('analysis_years', 7)
        
        # Get custom service rates
        service_terms = self.custom_service_rates.get(equipment_type, self.custom_service_rates['tillage'])
        
        # Calculate annual costs
        annual_costs = []
        
        for year in range(analysis_years):
            # Base rate per acre
            base_cost = annual_acres * service_terms.rate_per_acre
            
            # Apply seasonal adjustments (simplified - assume spring work)
            seasonal_multiplier = service_terms.seasonal_rate_adjustment.get('spring', 1.0)
            base_cost *= seasonal_multiplier
            
            # Apply volume discounts
            discount_rate = 0.0
            for volume_threshold, discount in service_terms.volume_discounts.items():
                if annual_acres >= volume_threshold:
                    discount_rate = discount
            
            discounted_cost = base_cost * (1 - discount_rate)
            
            # Apply inflation
            inflated_cost = discounted_cost * (1 + self.inflation_rate) ** year
            
            # Additional costs if not included
            additional_costs = 0.0
            if not service_terms.fuel_included:
                fuel_cost = equipment_specs.get('fuel_cost_per_hour', 25.00) * annual_hours * (1 + self.fuel_price_trend) ** year
                additional_costs += fuel_cost
            
            total_annual_cost = inflated_cost + additional_costs
            
            # Tax deduction for operating expense
            tax_savings = total_annual_cost * self.tax_rate
            net_annual_cost = total_annual_cost - tax_savings
            
            annual_costs.append(net_annual_cost)
        
        # Calculate NPV (no initial investment)
        cash_flows = [0] + [-cost for cost in annual_costs]
        npv = self._calculate_npv(cash_flows, self.discount_rate)
        
        # Calculate cost metrics
        total_costs = sum(annual_costs)
        total_hours = annual_hours * analysis_years
        cost_per_hour = total_costs / total_hours if total_hours > 0 else 0
        
        total_acres = annual_acres * analysis_years
        cost_per_acre = total_costs / total_acres if total_acres > 0 else 0
        
        # Risk assessment
        risk_factors = {
            'availability_risk': not service_terms.availability_guarantee,
            'quality_risk': not service_terms.quality_guarantee,
            'price_volatility': True,  # Custom rates can change
            'dependency_risk': True   # Dependent on service provider
        }
        
        return {
            'initial_cash_outlay': 0.0,
            'annual_costs': annual_costs,
            'total_costs': total_costs,
            'salvage_value': 0.0,
            'net_present_value': npv,
            'cost_per_hour': cost_per_hour,
            'cost_per_acre': cost_per_acre,
            'service_terms': service_terms.__dict__,
            'risk_factors': risk_factors,
            'cash_flows': cash_flows
        }
    
    def _compare_financing_options(self, purchase: Dict[str, Any], lease: Dict[str, Any], 
                                  custom: Dict[str, Any]) -> Dict[str, Any]:
        """Compare all financing options"""
        options = {
            'purchase': purchase,
            'lease': lease,
            'custom_service': custom
        }
        
        # Find lowest cost option
        lowest_npv = min(opt['net_present_value'] for opt in options.values())
        lowest_cost_option = next(name for name, opt in options.items() 
                                if opt['net_present_value'] == lowest_npv)
        
        # Calculate savings compared to highest cost option
        highest_npv = max(opt['net_present_value'] for opt in options.values())
        max_savings = highest_npv - lowest_npv
        
        # Cost per hour comparison
        cost_per_hour_ranking = sorted(options.items(), key=lambda x: x[1]['cost_per_hour'])
        
        # Cost per acre comparison
        cost_per_acre_ranking = sorted(options.items(), key=lambda x: x[1]['cost_per_acre'])
        
        return {
            'lowest_cost_option': lowest_cost_option,
            'lowest_npv': lowest_npv,
            'max_potential_savings': max_savings,
            'cost_per_hour_ranking': [(name, opt['cost_per_hour']) for name, opt in cost_per_hour_ranking],
            'cost_per_acre_ranking': [(name, opt['cost_per_acre']) for name, opt in cost_per_acre_ranking],
            'npv_comparison': {name: opt['net_present_value'] for name, opt in options.items()}
        }
    
    def _generate_recommendation(self, comparison: Dict[str, Any], 
                                usage_params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendation based on analysis"""
        annual_hours = usage_params.get('annual_hours', 200)
        annual_acres = usage_params.get('annual_acres', annual_hours * 8)
        cash_available = usage_params.get('cash_available', 100000)
        risk_tolerance = usage_params.get('risk_tolerance', RiskLevel.MEDIUM)
        
        recommendation = {
            'primary_recommendation': comparison['lowest_cost_option'],
            'reasoning': [],
            'considerations': [],
            'break_even_analysis': {}
        }
        
        # Usage-based recommendations
        if annual_hours < 100:
            recommendation['reasoning'].append("Low annual usage favors custom service")
            if comparison['lowest_cost_option'] != 'custom_service':
                recommendation['considerations'].append("Consider custom service despite higher cost due to low usage")
        elif annual_hours > 400:
            recommendation['reasoning'].append("High annual usage favors ownership")
            if comparison['lowest_cost_option'] == 'custom_service':
                recommendation['considerations'].append("High usage may justify ownership despite higher NPV")
        
        # Cash flow considerations
        purchase_initial = comparison.get('purchase', {}).get('initial_cash_outlay', 0)
        if cash_available < purchase_initial:
            recommendation['considerations'].append("Cash constraints may require financing or leasing")
        
        # Risk considerations
        if risk_tolerance == RiskLevel.LOW:
            if comparison['lowest_cost_option'] == 'custom_service':
                recommendation['reasoning'].append("Custom service reduces equipment ownership risk")
            else:
                recommendation['considerations'].append("Consider custom service to reduce ownership risk")
        elif risk_tolerance == RiskLevel.HIGH:
            if comparison['lowest_cost_option'] == 'purchase':
                recommendation['reasoning'].append("Purchase provides maximum control and potential returns")
        
        return recommendation
    
    def _calculate_depreciation(self, purchase_price: float, year: int, 
                               method: DepreciationMethod) -> float:
        """Calculate annual depreciation"""
        if method == DepreciationMethod.STRAIGHT_LINE:
            useful_life = 7  # 7 years for agricultural equipment
            return purchase_price / useful_life
        
        elif method == DepreciationMethod.MACRS:
            # MACRS 7-year property depreciation rates
            macrs_rates = [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893]
            if year < len(macrs_rates):
                return purchase_price * macrs_rates[year]
            return 0.0
        
        elif method == DepreciationMethod.DECLINING_BALANCE:
            rate = 2.0 / 7  # Double declining balance for 7-year life
            remaining_value = purchase_price
            for i in range(year):
                remaining_value *= (1 - rate)
            return remaining_value * rate
        
        else:
            return purchase_price / 7  # Default to straight line
    
    def _calculate_npv(self, cash_flows: List[float], discount_rate: float) -> float:
        """Calculate Net Present Value of cash flows"""
        npv = 0.0
        for i, cash_flow in enumerate(cash_flows):
            npv += cash_flow / (1 + discount_rate) ** i
        return npv
    
    def calculate_break_even_analysis(self, equipment_specs: Dict[str, Any], 
                                    financing_option: str = 'purchase') -> Dict[str, Any]:
        """Calculate break-even hours and acres for equipment"""
        purchase_price = equipment_specs.get('price', 0)
        annual_fixed_costs = purchase_price * 0.18  # Depreciation, insurance, interest
        variable_cost_per_hour = equipment_specs.get('fuel_cost_per_hour', 25.00) + \
                                equipment_specs.get('maintenance_cost_per_hour', 15.00)
        
        # Custom service alternative
        equipment_type = equipment_specs.get('equipment_type', 'tillage')
        custom_rate_per_acre = self.custom_service_rates.get(equipment_type, 
                                                           self.custom_service_rates['tillage']).rate_per_acre
        
        # Assume 8 acres per hour average
        acres_per_hour = 8.0
        custom_cost_per_hour = custom_rate_per_acre * acres_per_hour
        
        # Break-even calculation
        if custom_cost_per_hour > variable_cost_per_hour:
            break_even_hours = annual_fixed_costs / (custom_cost_per_hour - variable_cost_per_hour)
            break_even_acres = break_even_hours * acres_per_hour
        else:
            break_even_hours = float('inf')  # Never breaks even
            break_even_acres = float('inf')
        
        return {
            'break_even_hours': break_even_hours,
            'break_even_acres': break_even_acres,
            'annual_fixed_costs': annual_fixed_costs,
            'variable_cost_per_hour': variable_cost_per_hour,
            'custom_cost_per_hour': custom_cost_per_hour,
            'recommendation': 'purchase' if break_even_hours < 300 else 'custom_service'
        }
    
    def generate_cash_flow_projection(self, equipment_specs: Dict[str, Any], 
                                     financing_option: str, years: int = 10) -> Dict[str, Any]:
        """Generate detailed cash flow projections"""
        usage_params = {
            'annual_hours': 250,
            'annual_acres': 2000,
            'analysis_years': years
        }
        
        if financing_option == 'purchase':
            analysis = self._analyze_purchase_option(equipment_specs, usage_params)
        elif financing_option == 'lease':
            analysis = self._analyze_lease_option(equipment_specs, usage_params)
        else:  # custom_service
            analysis = self._analyze_custom_service_option(equipment_specs, usage_params)
        
        # Create detailed cash flow table
        cash_flow_table = []
        cumulative_cash_flow = 0
        
        for year, cash_flow in enumerate(analysis['cash_flows']):
            cumulative_cash_flow += cash_flow
            cash_flow_table.append({
                'year': year,
                'cash_flow': cash_flow,
                'cumulative_cash_flow': cumulative_cash_flow,
                'present_value': cash_flow / (1 + self.discount_rate) ** year
            })
        
        return {
            'cash_flow_table': cash_flow_table,
            'total_npv': analysis['net_present_value'],
            'payback_period': self._calculate_payback_period(analysis['cash_flows']),
            'irr': self._calculate_irr(analysis['cash_flows'])
        }
    
    def _calculate_payback_period(self, cash_flows: List[float]) -> float:
        """Calculate payback period in years"""
        cumulative = 0
        for year, cash_flow in enumerate(cash_flows[1:], 1):  # Skip initial investment
            cumulative += cash_flow
            if cumulative >= 0:  # Recovered initial investment
                return year
        return float('inf')  # Never pays back
    
    def _calculate_irr(self, cash_flows: List[float], precision: float = 0.0001) -> float:
        """Calculate Internal Rate of Return using Newton-Raphson method"""
        # Initial guess
        rate = 0.1
        
        for _ in range(100):  # Maximum iterations
            npv = sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
            npv_derivative = sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows) if i > 0)
            
            if abs(npv) < precision:
                return rate
            
            if npv_derivative == 0:
                break
            
            rate = rate - npv / npv_derivative
        
        return rate if rate > -1 else float('nan')  # Return NaN if no valid IRR
    
    def update(self, delta_time: float):
        """Update equipment economics system"""
        if not self.initialized:
            return
        
        # Update market conditions periodically
        # Update economic analyses for tracked equipment
        # Process financing payments and schedule updates
        pass
    
    def _handle_equipment_purchased(self, event_data: Dict[str, Any]):
        """Handle equipment purchase events"""
        entity_id = event_data.get('entity_id')
        purchase_price = event_data.get('price', 0)
        financing_type = event_data.get('financing_type', FinancingType.CASH_PURCHASE)
        
        if entity_id:
            self.create_equipment_economics_component(entity_id, purchase_price, financing_type)
    
    def _handle_equipment_operated(self, event_data: Dict[str, Any]):
        """Handle equipment operation events"""
        # Update operational cost tracking
        pass
    
    def _handle_maintenance_performed(self, event_data: Dict[str, Any]):
        """Handle maintenance events"""
        # Update maintenance cost tracking
        pass
    
    def _handle_fuel_price_change(self, event_data: Dict[str, Any]):
        """Handle fuel price changes"""
        if 'diesel_price' in event_data:
            self.fuel_price_trend = event_data.get('price_change_rate', self.fuel_price_trend)
    
    def _handle_market_change(self, event_data: Dict[str, Any]):
        """Handle market condition changes"""
        self.market_conditions.update(event_data)
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get equipment economics system statistics"""
        return {
            'discount_rate': self.discount_rate,
            'inflation_rate': self.inflation_rate,
            'tax_rate': self.tax_rate,
            'fuel_price_trend': self.fuel_price_trend,
            'market_conditions': self.market_conditions,
            'custom_service_operations': len(self.custom_service_rates),
            'financing_options': len(self.financing_options),
            'active_analyses': len(self.equipment_analyses)
        }

# Global equipment economics system instance
_global_economics_system: Optional[EquipmentEconomicsSystem] = None

def get_equipment_economics_system() -> EquipmentEconomicsSystem:
    """Get the global equipment economics system instance"""
    global _global_economics_system
    if _global_economics_system is None:
        _global_economics_system = EquipmentEconomicsSystem()
        _global_economics_system.initialize()
    return _global_economics_system

def initialize_equipment_economics_system() -> EquipmentEconomicsSystem:
    """Initialize the global equipment economics system"""
    global _global_economics_system
    _global_economics_system = EquipmentEconomicsSystem()
    _global_economics_system.initialize()
    return _global_economics_system

# Convenience functions
def analyze_equipment_financing(equipment_specs: Dict[str, Any], usage_params: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for equipment financing analysis"""
    return get_equipment_economics_system().analyze_purchase_vs_lease(equipment_specs, usage_params)

def calculate_equipment_break_even(equipment_specs: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for break-even analysis"""
    return get_equipment_economics_system().calculate_break_even_analysis(equipment_specs)

def generate_equipment_cash_flow(equipment_specs: Dict[str, Any], financing_option: str) -> Dict[str, Any]:
    """Convenience function for cash flow projections"""
    return get_equipment_economics_system().generate_cash_flow_projection(equipment_specs, financing_option)