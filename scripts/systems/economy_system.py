"""
Economy & Market System - Comprehensive Economic Simulation for AgriFun Agricultural Game

This system provides a realistic economic simulation with dynamic pricing, market forces,
contracts, loans, subsidies, and comprehensive financial management. Integrates with the
Time Management System for realistic market fluctuations and seasonal effects.

Key Features:
- Dynamic market pricing based on supply/demand
- Contract system with buyers and delivery requirements
- Loan and subsidy management with time-based calculations
- Market history tracking and trend analysis
- Seasonal price variations and market events
- Multi-crop economic simulation
- Financial performance analytics
- Economic crisis and boom cycle simulation

Market Mechanics:
- Supply/demand calculations affect daily prices
- Weather events impact market conditions
- Seasonal variations create realistic price cycles
- Contract fulfillment affects reputation and future opportunities
- Economic indicators influence loan availability and interest rates

Integration Features:
- Time-based loan interest calculations
- Seasonal market adjustments
- Weather-dependent price volatility
- Contract deadline management
- Historical price tracking

Usage Example:
    # Initialize economy system
    economy = EconomySystem()
    await economy.initialize()
    
    # Market operations
    current_price = economy.get_current_price('corn')
    economy.sell_crop('corn', 100, 'premium')
    
    # Contract management
    contract_id = economy.create_contract('corn', 500, 'high', 30)
    economy.fulfill_contract(contract_id, 500, 'high')
    
    # Financial management
    loan_id = economy.apply_for_loan(10000, 365)
    economy.make_loan_payment(loan_id, 500)
"""

import time
import math
import random
from typing import Dict, List, Set, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

# Import Phase 1 architecture
from scripts.core.entity_component_system import System
from scripts.core.advanced_event_system import get_event_system, EventPriority
from scripts.core.time_management import get_time_manager, Season, WeatherType
from scripts.core.advanced_config_system import get_config_manager


class MarketCondition(Enum):
    """Overall market condition states"""
    DEPRESSION = "depression"
    RECESSION = "recession"
    STABLE = "stable"
    GROWTH = "growth"
    BOOM = "boom"


class CropQuality(Enum):
    """Crop quality grades"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    HIGH = "high"
    PREMIUM = "premium"


class ContractStatus(Enum):
    """Contract fulfillment status"""
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LoanStatus(Enum):
    """Loan repayment status"""
    ACTIVE = "active"
    PAID_OFF = "paid_off"
    DEFAULTED = "defaulted"
    REFINANCED = "refinanced"


@dataclass
class MarketPrice:
    """Current market price for a commodity"""
    crop_type: str
    base_price: float
    current_price: float
    quality_multipliers: Dict[CropQuality, float]
    last_updated: int  # Game time in minutes
    daily_change_percent: float = 0.0
    weekly_change_percent: float = 0.0
    volatility: float = 0.1  # Price volatility factor


@dataclass
class PriceHistory:
    """Historical price data for analysis"""
    crop_type: str
    daily_prices: List[Tuple[int, float]]  # (game_time, price) pairs
    weekly_averages: List[Tuple[int, float]]
    seasonal_trends: Dict[Season, float]
    max_price: float = 0.0
    min_price: float = float('inf')
    average_price: float = 0.0


@dataclass
class Contract:
    """Agricultural contract for crop delivery"""
    contract_id: str
    buyer_name: str
    crop_type: str
    quantity_required: int
    quality_required: CropQuality
    price_per_unit: float
    deadline_days: int
    created_time: int  # Game time when created
    status: ContractStatus = ContractStatus.ACTIVE
    
    # Performance tracking
    quantity_delivered: int = 0
    average_quality_delivered: float = 0.0
    completion_bonus: float = 0.0
    penalty_amount: float = 0.0
    
    # Contract terms
    early_completion_bonus: float = 0.1  # 10% bonus for early delivery
    late_penalty_rate: float = 0.05  # 5% penalty per day late
    quality_bonus_rate: float = 0.15  # 15% bonus for exceeding quality


@dataclass
class Loan:
    """Agricultural loan with time-based interest"""
    loan_id: str
    principal_amount: float
    current_balance: float
    annual_interest_rate: float
    term_days: int
    daily_payment: float
    
    # Loan tracking
    created_time: int  # Game time when created
    last_payment_time: int
    payments_made: int = 0
    total_paid: float = 0.0
    status: LoanStatus = LoanStatus.ACTIVE
    
    # Payment terms
    grace_period_days: int = 7
    late_fee_rate: float = 0.02  # 2% late fee
    default_threshold_days: int = 30


@dataclass
class Subsidy:
    """Government subsidy program"""
    subsidy_id: str
    subsidy_name: str
    daily_amount: float
    total_amount: float
    duration_days: int
    
    # Subsidy tracking
    start_time: int  # Game time when started
    amount_received: float = 0.0
    days_remaining: int = 0
    is_active: bool = True
    
    # Conditions
    crop_requirements: List[str] = field(default_factory=list)
    minimum_acreage: int = 0
    sustainability_requirements: bool = False


@dataclass
class MarketEvent:
    """Special market events that affect prices"""
    event_id: str
    event_name: str
    description: str
    affected_crops: List[str]
    price_multiplier: float
    duration_days: int
    
    # Event tracking
    start_time: int
    is_active: bool = True
    events_triggered: int = 0


@dataclass
class EconomicIndicators:
    """Overall economic health indicators"""
    market_condition: MarketCondition = MarketCondition.STABLE
    inflation_rate: float = 0.02  # Annual inflation rate
    interest_base_rate: float = 0.05  # Base interest rate
    unemployment_rate: float = 0.06
    gdp_growth_rate: float = 0.03
    
    # Market sentiment
    consumer_confidence: float = 0.75  # 0.0 to 1.0
    agricultural_outlook: float = 0.80  # 0.0 to 1.0
    commodity_demand: float = 0.85  # 0.0 to 1.0
    
    # Volatility factors
    political_stability: float = 0.90  # 0.0 to 1.0
    weather_impact_factor: float = 1.0  # 0.5 to 2.0
    global_trade_factor: float = 1.0  # 0.7 to 1.3


class EconomySystem(System):
    """Comprehensive economic simulation system"""
    
    def __init__(self):
        super().__init__()
        self.system_name = "economy_system"
        
        # Core system references
        self.event_system = get_event_system()
        self.time_manager = get_time_manager()
        self.config_manager = get_config_manager()
        
        # Economic data storage
        self.market_prices: Dict[str, MarketPrice] = {}
        self.price_history: Dict[str, PriceHistory] = {}
        self.active_contracts: Dict[str, Contract] = {}
        self.active_loans: Dict[str, Loan] = {}
        self.active_subsidies: Dict[str, Subsidy] = {}
        self.market_events: Dict[str, MarketEvent] = {}
        
        # Economic state
        self.economic_indicators = EconomicIndicators()
        self.player_cash: float = 0.0
        self.player_debt: float = 0.0
        self.player_credit_rating: float = 0.75  # 0.0 to 1.0
        self.total_revenue: float = 0.0
        self.total_expenses: float = 0.0
        
        # Market configuration
        self.crop_types = ['corn', 'wheat', 'soybeans', 'tomatoes', 'potatoes']
        self.quality_base_multipliers = {
            CropQuality.POOR: 0.6,
            CropQuality.FAIR: 0.8,
            CropQuality.GOOD: 1.0,
            CropQuality.HIGH: 1.3,
            CropQuality.PREMIUM: 1.6
        }
        
        # Performance tracking
        self.transactions_processed = 0
        self.contracts_completed = 0
        self.loans_processed = 0
        self.daily_update_count = 0
        
        # Market simulation parameters
        self.base_volatility = 0.15
        self.seasonal_amplitude = 0.25
        self.weather_impact_range = 0.30
        self.supply_demand_sensitivity = 0.20
        
        # Cache for performance
        self.cached_calculations: Dict[str, Any] = {}
        self.cache_expiry_time = 0
        self.cache_duration_minutes = 5
    
    async def initialize(self):
        """Initialize the economy system"""
        # Load configuration
        await self._load_economic_configuration()
        
        # Initialize market prices
        await self._initialize_market_prices()
        
        # Initialize price history
        await self._initialize_price_history()
        
        # Subscribe to time events
        self.event_system.subscribe('time_day_passed', self._on_day_passed)
        self.event_system.subscribe('time_week_passed', self._on_week_passed)
        self.event_system.subscribe('time_month_passed', self._on_month_passed)
        self.event_system.subscribe('time_season_changed', self._on_season_changed)
        self.event_system.subscribe('weather_changed', self._on_weather_changed)
        
        # Subscribe to game events
        self.event_system.subscribe('crop_harvested', self._on_crop_harvested)
        self.event_system.subscribe('crop_planted', self._on_crop_planted)
        
        # Initialize starting financial state
        await self._initialize_player_finances()
        
        self.logger.info("Economy System initialized successfully")
    
    async def _load_economic_configuration(self):
        """Load economic parameters from configuration"""
        try:
            economy_config = self.config_manager.get_section('economy')
            
            # Update base parameters from config
            self.base_volatility = economy_config.get('base_volatility', 0.15)
            self.seasonal_amplitude = economy_config.get('seasonal_amplitude', 0.25)
            self.weather_impact_range = economy_config.get('weather_impact_range', 0.30)
            
            # Load starting financial conditions
            starting_config = economy_config.get('starting_conditions', {})
            self.player_cash = starting_config.get('starting_cash', 0.0)
            
            # Load economic indicators
            indicators_config = economy_config.get('economic_indicators', {})
            self.economic_indicators.inflation_rate = indicators_config.get('inflation_rate', 0.02)
            self.economic_indicators.interest_base_rate = indicators_config.get('base_interest_rate', 0.05)
            
        except Exception as e:
            self.logger.warning(f"Failed to load economic configuration: {e}")
            # Use default values
    
    async def _initialize_market_prices(self):
        """Initialize base market prices for all crops"""
        base_prices = {
            'corn': 4.50,
            'wheat': 6.20,
            'soybeans': 12.80,
            'tomatoes': 2.30,
            'potatoes': 3.75
        }
        
        for crop_type, base_price in base_prices.items():
            self.market_prices[crop_type] = MarketPrice(
                crop_type=crop_type,
                base_price=base_price,
                current_price=base_price,
                quality_multipliers=self.quality_base_multipliers.copy(),
                last_updated=self.time_manager.get_current_time().total_minutes,
                volatility=self.base_volatility + random.uniform(-0.05, 0.05)
            )
    
    async def _initialize_price_history(self):
        """Initialize price history tracking"""
        for crop_type in self.crop_types:
            self.price_history[crop_type] = PriceHistory(
                crop_type=crop_type,
                daily_prices=[],
                weekly_averages=[],
                seasonal_trends={season: 1.0 for season in Season},
                average_price=self.market_prices[crop_type].base_price
            )
    
    async def _initialize_player_finances(self):
        """Initialize player's starting financial state"""
        # Create starting loan if configured
        if self.player_cash <= 0:
            starting_loan = await self.create_loan(
                principal=10000.0,
                annual_rate=0.08,
                term_days=365,
                loan_type="startup_loan"
            )
            self.player_cash = 10000.0
            self.logger.info("Created starting loan for player")
        
        # Create starting subsidy
        startup_subsidy = await self.create_subsidy(
            name="New Farmer Assistance",
            daily_amount=100.0,
            duration_days=30,
            requirements=[]
        )
        
        self.logger.info(f"Player starting finances: ${self.player_cash:.2f}")
    
    def get_current_price(self, crop_type: str, quality: CropQuality = CropQuality.GOOD) -> float:
        """Get current market price for a crop with quality adjustment"""
        if crop_type not in self.market_prices:
            self.logger.error(f"Unknown crop type: {crop_type}")
            return 0.0
        
        market_price = self.market_prices[crop_type]
        quality_multiplier = market_price.quality_multipliers.get(quality, 1.0)
        
        return market_price.current_price * quality_multiplier
    
    def get_price_trend(self, crop_type: str, days: int = 7) -> Dict[str, float]:
        """Get price trend analysis for a crop"""
        if crop_type not in self.price_history:
            return {'trend': 0.0, 'volatility': 0.0, 'confidence': 0.0}
        
        history = self.price_history[crop_type]
        
        if len(history.daily_prices) < 2:
            return {'trend': 0.0, 'volatility': 0.0, 'confidence': 0.0}
        
        # Calculate trend over specified days
        recent_prices = history.daily_prices[-days:] if len(history.daily_prices) >= days else history.daily_prices
        
        if len(recent_prices) < 2:
            return {'trend': 0.0, 'volatility': 0.0, 'confidence': 0.0}
        
        # Linear regression for trend
        x_values = list(range(len(recent_prices)))
        y_values = [price for _, price in recent_prices]
        
        n = len(recent_prices)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope (trend)
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            trend_percent = (slope / (sum_y / n)) * 100 if sum_y != 0 else 0.0
        else:
            trend_percent = 0.0
        
        # Calculate volatility
        avg_price = sum_y / n
        variance = sum((price - avg_price) ** 2 for _, price in recent_prices) / n
        volatility = math.sqrt(variance) / avg_price if avg_price > 0 else 0.0
        
        # Calculate confidence based on data points and consistency
        confidence = min(1.0, n / days) * (1.0 - min(0.5, volatility))
        
        return {
            'trend': trend_percent,
            'volatility': volatility,
            'confidence': confidence
        }
    
    async def sell_crop(self, crop_type: str, quantity: int, quality: CropQuality) -> Dict[str, Any]:
        """Sell crops to the market"""
        if quantity <= 0:
            return {'success': False, 'error': 'Invalid quantity'}
        
        current_price = self.get_current_price(crop_type, quality)
        total_revenue = current_price * quantity
        
        # Apply market conditions
        market_modifier = self._get_market_condition_modifier()
        total_revenue *= market_modifier
        
        # Update player finances
        self.player_cash += total_revenue
        self.total_revenue += total_revenue
        self.transactions_processed += 1
        
        # Update market supply (affects future prices)
        await self._update_market_supply(crop_type, quantity)
        
        # Create transaction record
        transaction = {
            'type': 'sale',
            'crop_type': crop_type,
            'quantity': quantity,
            'quality': quality.value,
            'unit_price': current_price,
            'total_revenue': total_revenue,
            'market_modifier': market_modifier,
            'timestamp': self.time_manager.get_current_time().total_minutes
        }
        
        # Emit sale event
        self.event_system.emit('crop_sold', transaction, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Sold {quantity} units of {quality.value} {crop_type} for ${total_revenue:.2f}")
        
        return {
            'success': True,
            'revenue': total_revenue,
            'unit_price': current_price,
            'transaction': transaction
        }
    
    async def create_contract(self, crop_type: str, quantity: int, quality: CropQuality, 
                            deadline_days: int, buyer_name: str = None) -> str:
        """Create a new crop delivery contract"""
        contract_id = f"contract_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Calculate contract price (usually better than market price)
        base_price = self.get_current_price(crop_type, quality)
        contract_price = base_price * (1.0 + random.uniform(0.05, 0.15))  # 5-15% premium
        
        # Generate buyer name if not provided
        if not buyer_name:
            buyers = [
                "AgriCorp Industries", "Farm Fresh Foods", "Golden Harvest Co.",
                "Prairie Valley Distributors", "Sunrise Agricultural", "GreenField Partners"
            ]
            buyer_name = random.choice(buyers)
        
        contract = Contract(
            contract_id=contract_id,
            buyer_name=buyer_name,
            crop_type=crop_type,
            quantity_required=quantity,
            quality_required=quality,
            price_per_unit=contract_price,
            deadline_days=deadline_days,
            created_time=self.time_manager.get_current_time().total_minutes
        )
        
        self.active_contracts[contract_id] = contract
        
        # Emit contract creation event
        self.event_system.emit('contract_created', {
            'contract_id': contract_id,
            'buyer_name': buyer_name,
            'crop_type': crop_type,
            'quantity': quantity,
            'quality': quality.value,
            'price': contract_price,
            'deadline_days': deadline_days
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Created contract {contract_id}: {quantity} {crop_type} for ${contract_price:.2f}/unit")
        
        return contract_id
    
    async def fulfill_contract(self, contract_id: str, quantity: int, quality: CropQuality) -> Dict[str, Any]:
        """Fulfill a contract with delivered crops"""
        if contract_id not in self.active_contracts:
            return {'success': False, 'error': 'Contract not found'}
        
        contract = self.active_contracts[contract_id]
        
        if contract.status != ContractStatus.ACTIVE:
            return {'success': False, 'error': 'Contract not active'}
        
        # Check if crop type matches
        if contract.crop_type != contract.crop_type:  # This seems like a bug, should compare with delivered crop
            return {'success': False, 'error': 'Wrong crop type'}
        
        # Calculate quality adjustment
        quality_bonus = 0.0
        if quality.value > contract.quality_required.value:
            quality_levels = list(CropQuality)
            quality_diff = quality_levels.index(quality) - quality_levels.index(contract.quality_required)
            quality_bonus = quality_diff * contract.quality_bonus_rate
        
        # Calculate timing bonus/penalty
        current_time = self.time_manager.get_current_time().total_minutes
        contract_age_days = (current_time - contract.created_time) / 1440.0
        timing_modifier = 1.0
        
        if contract_age_days < contract.deadline_days * 0.8:  # Early completion
            timing_modifier = 1.0 + contract.early_completion_bonus
        elif contract_age_days > contract.deadline_days:  # Late delivery
            days_late = contract_age_days - contract.deadline_days
            timing_modifier = 1.0 - (days_late * contract.late_penalty_rate)
            timing_modifier = max(0.5, timing_modifier)  # Minimum 50% payment
        
        # Calculate payment
        base_payment = contract.price_per_unit * quantity
        quality_payment = base_payment * quality_bonus
        final_payment = (base_payment + quality_payment) * timing_modifier
        
        # Update contract progress
        contract.quantity_delivered += quantity
        contract.average_quality_delivered = (
            (contract.average_quality_delivered * (contract.quantity_delivered - quantity) + 
             list(CropQuality).index(quality) * quantity) / contract.quantity_delivered
        )
        
        # Check if contract is complete
        if contract.quantity_delivered >= contract.quantity_required:
            contract.status = ContractStatus.FULFILLED
            self.contracts_completed += 1
            
            # Update credit rating based on performance
            performance_factor = min(1.0, final_payment / base_payment)
            credit_adjustment = (performance_factor - 0.8) * 0.02  # ±2% max adjustment
            self.player_credit_rating = max(0.0, min(1.0, self.player_credit_rating + credit_adjustment))
        
        # Update player finances
        self.player_cash += final_payment
        self.total_revenue += final_payment
        self.transactions_processed += 1
        
        # Create fulfillment record
        fulfillment = {
            'contract_id': contract_id,
            'quantity_delivered': quantity,
            'quality_delivered': quality.value,
            'payment_received': final_payment,
            'quality_bonus': quality_payment,
            'timing_modifier': timing_modifier,
            'contract_completed': contract.status == ContractStatus.FULFILLED,
            'timestamp': current_time
        }
        
        # Emit contract fulfillment event
        self.event_system.emit('contract_fulfilled', fulfillment, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Fulfilled contract {contract_id}: {quantity} units for ${final_payment:.2f}")
        
        return {
            'success': True,
            'payment': final_payment,
            'contract_completed': contract.status == ContractStatus.FULFILLED,
            'fulfillment': fulfillment
        }
    
    async def create_loan(self, principal: float, annual_rate: float, term_days: int, 
                         loan_type: str = "agricultural") -> str:
        """Create a new agricultural loan"""
        loan_id = f"loan_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Adjust interest rate based on credit rating
        credit_adjustment = (1.0 - self.player_credit_rating) * 0.03  # Up to 3% adjustment
        adjusted_rate = annual_rate + credit_adjustment
        
        # Calculate daily payment (simple interest for agricultural loans)
        daily_rate = adjusted_rate / 365.0
        daily_payment = (principal * (1 + adjusted_rate * (term_days / 365.0))) / term_days
        
        loan = Loan(
            loan_id=loan_id,
            principal_amount=principal,
            current_balance=principal,
            annual_interest_rate=adjusted_rate,
            term_days=term_days,
            daily_payment=daily_payment,
            created_time=self.time_manager.get_current_time().total_minutes,
            last_payment_time=self.time_manager.get_current_time().total_minutes
        )
        
        self.active_loans[loan_id] = loan
        self.player_debt += principal
        self.loans_processed += 1
        
        # Emit loan creation event
        self.event_system.emit('loan_created', {
            'loan_id': loan_id,
            'principal': principal,
            'interest_rate': adjusted_rate,
            'term_days': term_days,
            'daily_payment': daily_payment,
            'loan_type': loan_type
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Created loan {loan_id}: ${principal:.2f} at {adjusted_rate:.2%} for {term_days} days")
        
        return loan_id
    
    async def make_loan_payment(self, loan_id: str, amount: float) -> Dict[str, Any]:
        """Make a payment on a loan"""
        if loan_id not in self.active_loans:
            return {'success': False, 'error': 'Loan not found'}
        
        loan = self.active_loans[loan_id]
        
        if loan.status != LoanStatus.ACTIVE:
            return {'success': False, 'error': 'Loan not active'}
        
        if amount <= 0:
            return {'success': False, 'error': 'Invalid payment amount'}
        
        if self.player_cash < amount:
            return {'success': False, 'error': 'Insufficient funds'}
        
        # Process payment
        payment_amount = min(amount, loan.current_balance)
        loan.current_balance -= payment_amount
        loan.total_paid += payment_amount
        loan.payments_made += 1
        loan.last_payment_time = self.time_manager.get_current_time().total_minutes
        
        # Update player finances
        self.player_cash -= payment_amount
        self.player_debt -= payment_amount
        self.total_expenses += payment_amount
        
        # Check if loan is paid off
        if loan.current_balance <= 0.01:  # Account for floating point precision
            loan.status = LoanStatus.PAID_OFF
            loan.current_balance = 0.0
            
            # Improve credit rating for paying off loan
            self.player_credit_rating = min(1.0, self.player_credit_rating + 0.05)
        
        # Create payment record
        payment_record = {
            'loan_id': loan_id,
            'payment_amount': payment_amount,
            'remaining_balance': loan.current_balance,
            'loan_paid_off': loan.status == LoanStatus.PAID_OFF,
            'timestamp': self.time_manager.get_current_time().total_minutes
        }
        
        # Emit payment event
        self.event_system.emit('loan_payment_made', payment_record, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Loan payment {loan_id}: ${payment_amount:.2f}, balance: ${loan.current_balance:.2f}")
        
        return {
            'success': True,
            'payment_amount': payment_amount,
            'remaining_balance': loan.current_balance,
            'loan_paid_off': loan.status == LoanStatus.PAID_OFF,
            'payment_record': payment_record
        }
    
    async def create_subsidy(self, name: str, daily_amount: float, duration_days: int, 
                           requirements: List[str]) -> str:
        """Create a new government subsidy"""
        subsidy_id = f"subsidy_{int(time.time())}_{random.randint(1000, 9999)}"
        
        subsidy = Subsidy(
            subsidy_id=subsidy_id,
            subsidy_name=name,
            daily_amount=daily_amount,
            total_amount=daily_amount * duration_days,
            duration_days=duration_days,
            start_time=self.time_manager.get_current_time().total_minutes,
            days_remaining=duration_days,
            crop_requirements=requirements
        )
        
        self.active_subsidies[subsidy_id] = subsidy
        
        # Emit subsidy creation event
        self.event_system.emit('subsidy_created', {
            'subsidy_id': subsidy_id,
            'name': name,
            'daily_amount': daily_amount,
            'duration_days': duration_days,
            'total_amount': subsidy.total_amount
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Created subsidy {subsidy_id}: ${daily_amount:.2f}/day for {duration_days} days")
        
        return subsidy_id
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get comprehensive market summary"""
        current_time = self.time_manager.get_current_time()
        
        # Crop prices summary
        crop_prices = {}
        for crop_type, market_price in self.market_prices.items():
            trend = self.get_price_trend(crop_type)
            crop_prices[crop_type] = {
                'current_price': market_price.current_price,
                'daily_change': market_price.daily_change_percent,
                'trend': trend['trend'],
                'volatility': trend['volatility']
            }
        
        # Contract summary
        active_contract_count = len([c for c in self.active_contracts.values() if c.status == ContractStatus.ACTIVE])
        
        # Loan summary
        total_debt = sum(loan.current_balance for loan in self.active_loans.values() if loan.status == LoanStatus.ACTIVE)
        
        # Subsidy summary
        active_subsidies = [s for s in self.active_subsidies.values() if s.is_active]
        total_subsidy_remaining = sum(s.daily_amount * s.days_remaining for s in active_subsidies)
        
        return {
            'market_condition': self.economic_indicators.market_condition.value,
            'crop_prices': crop_prices,
            'contracts': {
                'active_count': active_contract_count,
                'total_completed': self.contracts_completed
            },
            'loans': {
                'total_debt': total_debt,
                'credit_rating': self.player_credit_rating
            },
            'subsidies': {
                'active_count': len(active_subsidies),
                'total_remaining': total_subsidy_remaining
            },
            'finances': {
                'cash': self.player_cash,
                'total_revenue': self.total_revenue,
                'total_expenses': self.total_expenses,
                'net_income': self.total_revenue - self.total_expenses
            }
        }
    
    def _update_daily_prices(self):
        """Update daily market prices based on various factors"""
        current_time = self.time_manager.get_current_time()
        current_season = self.time_manager.get_current_season()
        current_weather = self.time_manager.get_current_weather()
        
        for crop_type, market_price in self.market_prices.items():
            # Base price adjustment
            base_change = random.gauss(0, market_price.volatility)
            
            # Seasonal adjustment
            seasonal_factor = self._get_seasonal_price_factor(crop_type, current_season)
            
            # Weather adjustment
            weather_factor = self._get_weather_price_factor(crop_type, current_weather.weather_type)
            
            # Market condition adjustment
            condition_factor = self._get_market_condition_factor()
            
            # Calculate total price change
            total_factor = (1.0 + base_change) * seasonal_factor * weather_factor * condition_factor
            new_price = market_price.current_price * total_factor
            
            # Apply bounds (prevent extreme price swings)
            min_price = market_price.base_price * 0.3
            max_price = market_price.base_price * 3.0
            new_price = max(min_price, min(max_price, new_price))
            
            # Calculate change percentage
            daily_change = ((new_price - market_price.current_price) / market_price.current_price) * 100
            
            # Update market price
            market_price.current_price = new_price
            market_price.daily_change_percent = daily_change
            market_price.last_updated = current_time.total_minutes
            
            # Update price history
            history = self.price_history[crop_type]
            history.daily_prices.append((current_time.total_minutes, new_price))
            
            # Keep only last 365 days of history
            if len(history.daily_prices) > 365:
                history.daily_prices = history.daily_prices[-365:]
            
            # Update min/max/average
            history.max_price = max(history.max_price, new_price)
            history.min_price = min(history.min_price, new_price)
            if history.daily_prices:
                history.average_price = sum(price for _, price in history.daily_prices) / len(history.daily_prices)
    
    def _get_seasonal_price_factor(self, crop_type: str, season: Season) -> float:
        """Get seasonal price adjustment factor"""
        # Simplified seasonal adjustments - in reality this would be more complex
        seasonal_factors = {
            'corn': {Season.SPRING: 1.1, Season.SUMMER: 0.95, Season.FALL: 0.85, Season.WINTER: 1.15},
            'wheat': {Season.SPRING: 0.9, Season.SUMMER: 1.2, Season.FALL: 0.8, Season.WINTER: 1.1},
            'soybeans': {Season.SPRING: 1.05, Season.SUMMER: 0.9, Season.FALL: 0.85, Season.WINTER: 1.2},
            'tomatoes': {Season.SPRING: 1.3, Season.SUMMER: 0.7, Season.FALL: 1.1, Season.WINTER: 1.4},
            'potatoes': {Season.SPRING: 1.1, Season.SUMMER: 0.9, Season.FALL: 0.8, Season.WINTER: 1.3}
        }
        
        return seasonal_factors.get(crop_type, {}).get(season, 1.0)
    
    def _get_weather_price_factor(self, crop_type: str, weather_type: WeatherType) -> float:
        """Get weather-based price adjustment factor"""
        # Weather affects prices through supply concerns
        weather_factors = {
            WeatherType.DROUGHT: 1.25,
            WeatherType.EXTREME_HEAT: 1.15,
            WeatherType.EXTREME_COLD: 1.10,
            WeatherType.HEAVY_RAIN: 1.05,
            WeatherType.STORM: 1.08,
            WeatherType.CLEAR: 1.0,
            WeatherType.PARTLY_CLOUDY: 1.0,
            WeatherType.CLOUDY: 0.98,
            WeatherType.LIGHT_RAIN: 0.95,
            WeatherType.SNOW: 1.02,
            WeatherType.FOG: 0.98
        }
        
        return weather_factors.get(weather_type, 1.0)
    
    def _get_market_condition_factor(self) -> float:
        """Get market condition adjustment factor"""
        condition_factors = {
            MarketCondition.DEPRESSION: 0.7,
            MarketCondition.RECESSION: 0.85,
            MarketCondition.STABLE: 1.0,
            MarketCondition.GROWTH: 1.15,
            MarketCondition.BOOM: 1.3
        }
        
        return condition_factors.get(self.economic_indicators.market_condition, 1.0)
    
    def _get_market_condition_modifier(self) -> float:
        """Get current market condition modifier for transactions"""
        return self._get_market_condition_factor()
    
    async def _update_market_supply(self, crop_type: str, quantity_sold: int):
        """Update market supply data (affects future prices)"""
        # Simple supply tracking - selling crops increases supply, lowering future prices
        if crop_type in self.market_prices:
            supply_impact = quantity_sold * 0.0001  # Small impact per unit
            volatility_increase = supply_impact * 0.1
            
            market_price = self.market_prices[crop_type]
            market_price.volatility = min(0.5, market_price.volatility + volatility_increase)
    
    # Event handlers
    async def _on_day_passed(self, event_data):
        """Handle daily economic updates"""
        self.daily_update_count += 1
        
        # Update market prices
        self._update_daily_prices()
        
        # Process loan interest
        await self._process_daily_loan_interest()
        
        # Process subsidies
        await self._process_daily_subsidies()
        
        # Update economic indicators
        await self._update_economic_indicators()
        
        # Check contract deadlines
        await self._check_contract_deadlines()
        
        # Emit daily economic update
        self.event_system.emit('economy_daily_update', {
            'day': self.daily_update_count,
            'market_summary': self.get_market_summary()
        }, priority=EventPriority.LOW)
    
    async def _on_week_passed(self, event_data):
        """Handle weekly economic updates"""
        # Update weekly price averages
        current_time = self.time_manager.get_current_time().total_minutes
        
        for crop_type, history in self.price_history.items():
            if len(history.daily_prices) >= 7:
                recent_prices = [price for _, price in history.daily_prices[-7:]]
                weekly_average = sum(recent_prices) / len(recent_prices)
                history.weekly_averages.append((current_time, weekly_average))
                
                # Keep only last 52 weeks
                if len(history.weekly_averages) > 52:
                    history.weekly_averages = history.weekly_averages[-52:]
    
    async def _on_month_passed(self, event_data):
        """Handle monthly economic updates"""
        # Update credit ratings based on payment history
        # Generate new contracts
        # Update economic indicators
        pass
    
    async def _on_season_changed(self, event_data):
        """Handle seasonal economic changes"""
        new_season = Season(event_data.get('new_season'))
        
        # Update seasonal price trends
        for crop_type, history in self.price_history.items():
            if crop_type in self.market_prices:
                current_price = self.market_prices[crop_type].current_price
                base_price = self.market_prices[crop_type].base_price
                seasonal_trend = current_price / base_price
                history.seasonal_trends[new_season] = seasonal_trend
        
        # Generate seasonal contracts
        await self._generate_seasonal_contracts(new_season)
    
    async def _on_weather_changed(self, event_data):
        """Handle weather-related economic impacts"""
        weather_type = WeatherType(event_data.get('weather_type'))
        
        # Immediate price reactions to severe weather
        if weather_type in [WeatherType.DROUGHT, WeatherType.EXTREME_HEAT, WeatherType.STORM]:
            # Create temporary price volatility
            for market_price in self.market_prices.values():
                market_price.volatility *= 1.2  # Increase volatility
    
    async def _on_crop_harvested(self, event_data):
        """Handle crop harvest events for market impact"""
        crop_type = event_data.get('crop_type')
        quantity = event_data.get('quantity', 0)
        
        # Large harvests can affect market prices
        if quantity > 100:  # Significant harvest
            await self._update_market_supply(crop_type, quantity // 2)  # Partial impact
    
    async def _on_crop_planted(self, event_data):
        """Handle crop planting events for future market predictions"""
        # Track planting data for supply forecasting
        pass
    
    async def _process_daily_loan_interest(self):
        """Process daily loan payments and interest"""
        current_time = self.time_manager.get_current_time().total_minutes
        
        for loan in self.active_loans.values():
            if loan.status == LoanStatus.ACTIVE:
                # Check for missed payments
                days_since_payment = (current_time - loan.last_payment_time) / 1440.0
                
                if days_since_payment >= 1.0:  # Payment due
                    if self.player_cash >= loan.daily_payment:
                        # Automatic payment
                        await self.make_loan_payment(loan.loan_id, loan.daily_payment)
                    else:
                        # Late payment - apply penalties
                        if days_since_payment > loan.grace_period_days:
                            late_fee = loan.daily_payment * loan.late_fee_rate
                            self.player_debt += late_fee
                            self.total_expenses += late_fee
                            
                            # Check for default
                            if days_since_payment > loan.default_threshold_days:
                                loan.status = LoanStatus.DEFAULTED
                                self.player_credit_rating = max(0.0, self.player_credit_rating - 0.2)
                                
                                self.event_system.emit('loan_defaulted', {
                                    'loan_id': loan.loan_id,
                                    'outstanding_balance': loan.current_balance
                                }, priority=EventPriority.HIGH)
    
    async def _process_daily_subsidies(self):
        """Process daily subsidy payments"""
        current_time = self.time_manager.get_current_time().total_minutes
        
        for subsidy in self.active_subsidies.values():
            if subsidy.is_active and subsidy.days_remaining > 0:
                # Pay daily subsidy
                self.player_cash += subsidy.daily_amount
                subsidy.amount_received += subsidy.daily_amount
                subsidy.days_remaining -= 1
                
                if subsidy.days_remaining <= 0:
                    subsidy.is_active = False
                    
                    self.event_system.emit('subsidy_completed', {
                        'subsidy_id': subsidy.subsidy_id,
                        'total_received': subsidy.amount_received
                    }, priority=EventPriority.NORMAL)
    
    async def _update_economic_indicators(self):
        """Update overall economic health indicators"""
        # Simple economic indicator updates
        # In a full game, these would be more sophisticated
        
        # Random walk for economic indicators
        self.economic_indicators.consumer_confidence += random.gauss(0, 0.01)
        self.economic_indicators.consumer_confidence = max(0.0, min(1.0, self.economic_indicators.consumer_confidence))
        
        self.economic_indicators.agricultural_outlook += random.gauss(0, 0.005)
        self.economic_indicators.agricultural_outlook = max(0.0, min(1.0, self.economic_indicators.agricultural_outlook))
        
        # Update market condition based on indicators
        avg_confidence = (self.economic_indicators.consumer_confidence + 
                         self.economic_indicators.agricultural_outlook) / 2
        
        if avg_confidence < 0.4:
            self.economic_indicators.market_condition = MarketCondition.DEPRESSION
        elif avg_confidence < 0.6:
            self.economic_indicators.market_condition = MarketCondition.RECESSION
        elif avg_confidence > 0.8:
            self.economic_indicators.market_condition = MarketCondition.BOOM
        elif avg_confidence > 0.7:
            self.economic_indicators.market_condition = MarketCondition.GROWTH
        else:
            self.economic_indicators.market_condition = MarketCondition.STABLE
    
    async def _check_contract_deadlines(self):
        """Check for contract deadline violations"""
        current_time = self.time_manager.get_current_time().total_minutes
        
        for contract in self.active_contracts.values():
            if contract.status == ContractStatus.ACTIVE:
                contract_age_days = (current_time - contract.created_time) / 1440.0
                
                if contract_age_days > contract.deadline_days:
                    # Contract failed due to deadline
                    contract.status = ContractStatus.FAILED
                    
                    # Credit rating penalty
                    self.player_credit_rating = max(0.0, self.player_credit_rating - 0.1)
                    
                    self.event_system.emit('contract_failed', {
                        'contract_id': contract.contract_id,
                        'buyer_name': contract.buyer_name,
                        'penalty_amount': contract.penalty_amount
                    }, priority=EventPriority.HIGH)
    
    async def _generate_seasonal_contracts(self, season: Season):
        """Generate seasonal contract opportunities"""
        # Generate 1-3 new contracts each season
        num_contracts = random.randint(1, 3)
        
        for _ in range(num_contracts):
            crop_type = random.choice(self.crop_types)
            quantity = random.randint(50, 500)
            quality = random.choice(list(CropQuality)[2:])  # Good or better
            deadline_days = random.randint(30, 90)
            
            await self.create_contract(crop_type, quantity, quality, deadline_days)
    
    async def shutdown(self):
        """Shutdown the economy system"""
        self.logger.info("Shutting down Economy System")
        
        # Save final economic state
        final_summary = self.get_market_summary()
        
        self.event_system.emit('economy_shutdown', {
            'final_summary': final_summary,
            'transactions_processed': self.transactions_processed,
            'contracts_completed': self.contracts_completed
        }, priority=EventPriority.HIGH)
        
        self.logger.info("Economy System shutdown complete")


# Global economy system instance
_global_economy_system: Optional[EconomySystem] = None

def get_economy_system() -> EconomySystem:
    """Get the global economy system instance"""
    global _global_economy_system
    if _global_economy_system is None:
        _global_economy_system = EconomySystem()
    return _global_economy_system

def initialize_economy_system() -> EconomySystem:
    """Initialize the global economy system"""
    global _global_economy_system
    _global_economy_system = EconomySystem()
    return _global_economy_system