"""
Economy & Market System - Comprehensive Economic Simulation for AgriFun Agricultural Game

This system provides realistic economic simulation with dynamic pricing, market forces,
contracts, loans, subsidies, and comprehensive financial management. Integrates with
the Time Management System for seasonal market fluctuations and realistic business cycles.

Key Features:
- Dynamic market pricing based on supply/demand
- Contract system with buyers and delivery requirements
- Loan management with time-based interest calculations
- Government subsidy programs
- Market history tracking and trend analysis
- Economic indicators and market condition simulation
- Seasonal price adjustments and market volatility
- Credit rating system affecting loan terms
- Transaction history and financial reporting
"""

import time
import math
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging

# Import foundation systems
from ..core.event_system import get_global_event_system, EventPriority
from ..core.entity_component_system import get_entity_manager
from ..core.configuration_system import get_configuration_manager
from ..core.state_management import get_state_manager
from ..systems.time_system import get_time_system, Season


class TransactionType(Enum):
    """Types of financial transactions"""
    CROP_SALE = "crop_sale"
    EQUIPMENT_PURCHASE = "equipment_purchase"
    LOAN_PAYMENT = "loan_payment"
    LOAN_DISBURSEMENT = "loan_disbursement"
    SUBSIDY_PAYMENT = "subsidy_payment"
    CONTRACT_PAYMENT = "contract_payment"
    OPERATING_EXPENSE = "operating_expense"


class MarketCondition(Enum):
    """Overall market condition states"""
    BULL_MARKET = "bull_market"      # Rising prices, good demand
    BEAR_MARKET = "bear_market"      # Falling prices, low demand
    STABLE_MARKET = "stable_market"  # Normal conditions
    VOLATILE_MARKET = "volatile_market"  # High price swings


@dataclass
class Transaction:
    """Financial transaction record"""
    transaction_id: str
    transaction_type: TransactionType
    amount: float               # Positive for income, negative for expenses
    description: str
    timestamp: int             # Game time in total minutes
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketPrice:
    """Market price information for a commodity"""
    commodity: str
    base_price: float          # Base price per unit
    current_price: float       # Current market price
    
    # Market factors
    supply_factor: float = 1.0    # Supply level (0.5 = low supply, 2.0 = oversupply)
    demand_factor: float = 1.0    # Demand level (0.5 = low demand, 2.0 = high demand)
    seasonal_factor: float = 1.0  # Seasonal price modifier
    quality_premium: float = 0.0  # Premium for high quality (per quality point)
    
    # Price history
    price_history: List[float] = field(default_factory=list)
    volatility: float = 0.1       # Price volatility factor
    
    def get_price_for_quality(self, quality: float) -> float:
        """Get price adjusted for quality (0.0 to 1.0)"""
        quality_bonus = quality * self.quality_premium
        return self.current_price * (1.0 + quality_bonus)


@dataclass
class Contract:
    """Market contract for crop sales"""
    contract_id: str
    buyer_name: str
    commodity: str
    quantity_required: int     # Units required
    price_per_unit: float     # Fixed price per unit
    quality_requirement: float  # Minimum quality (0.0 to 1.0)
    deadline_days: int        # Days to fulfill contract
    
    # Progress tracking
    quantity_delivered: int = 0
    
    def get_contract_value(self) -> float:
        """Get total contract value"""
        return self.quantity_required * self.price_per_unit
    
    def get_remaining_quantity(self) -> int:
        """Get remaining quantity to deliver"""
        return max(0, self.quantity_required - self.quantity_delivered)


@dataclass
class Loan:
    """Farm loan information"""
    loan_id: str
    principal: float           # Original loan amount
    remaining_balance: float   # Current balance
    interest_rate: float       # Annual interest rate
    term_months: int          # Loan term in months
    monthly_payment: float    # Required monthly payment
    
    def calculate_monthly_payment(self) -> float:
        """Calculate required monthly payment"""
        if self.interest_rate == 0:
            return self.principal / self.term_months
        
        monthly_rate = self.interest_rate / 12
        payment = self.principal * (monthly_rate * (1 + monthly_rate) ** self.term_months) / \
                 ((1 + monthly_rate) ** self.term_months - 1)
        return payment


class MarketSimulator:
    """Market dynamics simulation engine"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger('MarketSimulator')
        
        # Market state
        self.market_condition = MarketCondition.STABLE_MARKET
        self.global_price_modifier = 1.0
        
        # Commodity prices
        self.market_prices: Dict[str, MarketPrice] = {}
        
        # Initialize default commodities
        self._initialize_market_prices()
    
    def _initialize_market_prices(self):
        """Initialize default commodity prices"""
        default_commodities = {
            'corn': {'base_price': 5.0, 'volatility': 0.15, 'quality_premium': 0.2},
            'wheat': {'base_price': 6.0, 'volatility': 0.12, 'quality_premium': 0.25},
            'tomatoes': {'base_price': 8.0, 'volatility': 0.25, 'quality_premium': 0.3},
            'lettuce': {'base_price': 12.0, 'volatility': 0.3, 'quality_premium': 0.35}
        }
        
        for commodity, data in default_commodities.items():
            market_price = MarketPrice(
                commodity=commodity,
                base_price=data['base_price'],
                current_price=data['base_price'],
                volatility=data['volatility'],
                quality_premium=data['quality_premium']
            )
            self.market_prices[commodity] = market_price
    
    def update_market_prices(self, season: Season, weather_modifier: float = 1.0):
        """Update market prices based on season and conditions"""
        for commodity, price_info in self.market_prices.items():
            # Apply seasonal factors
            seasonal_factor = self._get_seasonal_factor(commodity, season)
            
            # Apply weather effects
            weather_factor = weather_modifier
            
            # Apply market volatility
            volatility_change = random.uniform(-price_info.volatility, price_info.volatility)
            
            # Calculate new price
            base_price = price_info.base_price
            new_price = base_price * seasonal_factor * weather_factor * self.global_price_modifier
            new_price *= (1.0 + volatility_change)
            
            # Ensure price doesn't go below 20% or above 300% of base price
            new_price = max(base_price * 0.2, min(base_price * 3.0, new_price))
            
            # Update price and history
            price_info.current_price = new_price
            price_info.seasonal_factor = seasonal_factor
            price_info.price_history.append(new_price)
            
            # Keep only last 30 days of history
            if len(price_info.price_history) > 30:
                price_info.price_history.pop(0)
    
    def _get_seasonal_factor(self, commodity: str, season: Season) -> float:
        """Get seasonal price modifier for commodity"""
        # Different crops have different seasonal patterns
        seasonal_factors = {
            'corn': {
                Season.SPRING: 1.1,  # Planting season - higher demand for seed
                Season.SUMMER: 0.9,   # Growing season
                Season.FALL: 1.3,     # Harvest time - high supply, but also high demand
                Season.WINTER: 1.0    # Storage/processing
            },
            'wheat': {
                Season.SPRING: 1.0,
                Season.SUMMER: 0.8,
                Season.FALL: 1.4,
                Season.WINTER: 1.1
            },
            'tomatoes': {
                Season.SPRING: 1.2,   # Fresh demand
                Season.SUMMER: 0.8,   # Peak season
                Season.FALL: 1.0,
                Season.WINTER: 1.6    # Greenhouse premium
            },
            'lettuce': {
                Season.SPRING: 0.9,
                Season.SUMMER: 1.3,   # Hot weather premium
                Season.FALL: 0.8,
                Season.WINTER: 1.4
            }
        }
        
        return seasonal_factors.get(commodity, {}).get(season, 1.0)


class EconomySystem:
    """Main economy and market management system"""
    
    def __init__(self):
        # Core systems
        self.event_system = get_global_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_configuration_manager()
        self.state_manager = get_state_manager()
        self.time_system = get_time_system()
        
        # Financial state
        self.current_cash = 1000.0
        self.total_assets = 0.0
        self.total_liabilities = 0.0
        self.credit_rating = 650  # Starting credit score
        
        # Transaction history
        self.transactions: List[Transaction] = []
        self.transaction_counter = 0
        
        # Market system
        self.market_simulator = MarketSimulator(self.config_manager)
        
        # Contracts
        self.available_contracts: Dict[str, Contract] = {}
        self.active_contracts: Dict[str, Contract] = {}
        self.contract_counter = 0
        
        # Loans
        self.active_loans: Dict[str, Loan] = {}
        self.loan_counter = 0
        
        # Subsidies
        self.subsidy_balance = 3000.0  # Starting subsidy
        self.subsidy_days_remaining = 30
        
        self.logger = logging.getLogger('EconomySystem')
        
        # Subscribe to time events
        self._subscribe_to_events()
        
        # Initialize with starting loan
        self._initialize_economy()
    
    def _subscribe_to_events(self):
        """Subscribe to relevant system events"""
        self.event_system.subscribe('day_changed', self._on_day_changed)
        self.event_system.subscribe('season_changed', self._on_season_changed)
    
    def _initialize_economy(self):
        """Initialize economy with starting conditions"""
        # Create mandatory starting loan
        starting_loan = 10000.0
        loan = Loan(
            loan_id="startup_loan_001",
            principal=starting_loan,
            remaining_balance=starting_loan,
            interest_rate=0.06,  # 6% annual
            term_months=60,  # 5 year term
            monthly_payment=0
        )
        loan.monthly_payment = loan.calculate_monthly_payment()
        self.active_loans[loan.loan_id] = loan
        
        # Add starting cash from loan
        self.current_cash += starting_loan
        self.add_transaction(
            TransactionType.LOAN_DISBURSEMENT,
            starting_loan,
            "Starting farm loan disbursement"
        )
        
        # Generate initial contracts
        self._generate_contracts()
        
        self.logger.info(f"Economy initialized: ${self.current_cash:.2f} cash, ${starting_loan:.2f} loan")
    
    def get_current_price(self, commodity: str) -> float:
        """Get current market price for commodity"""
        if commodity in self.market_simulator.market_prices:
            return self.market_simulator.market_prices[commodity].current_price
        return 0.0
    
    def get_price_for_quality(self, commodity: str, quality: float) -> float:
        """Get price adjusted for quality"""
        if commodity in self.market_simulator.market_prices:
            return self.market_simulator.market_prices[commodity].get_price_for_quality(quality)
        return 0.0
    
    def get_market_info(self, commodity: str) -> Optional[MarketPrice]:
        """Get complete market information for commodity"""
        return self.market_simulator.market_prices.get(commodity)
    
    def sell_crops(self, commodity: str, quantity: int, quality: float = 1.0) -> Dict[str, Any]:
        """Sell crops at current market price"""
        if quantity <= 0:
            return {'success': False, 'message': 'Invalid quantity'}
        
        if commodity not in self.market_simulator.market_prices:
            return {'success': False, 'message': f'Unknown commodity: {commodity}'}
        
        # Calculate sale price
        unit_price = self.get_price_for_quality(commodity, quality)
        total_value = quantity * unit_price
        
        # Add transaction
        transaction_id = self.add_transaction(
            TransactionType.CROP_SALE,
            total_value,
            f"Sold {quantity} units of {commodity}",
            metadata={
                'commodity': commodity,
                'quantity': quantity,
                'unit_price': unit_price,
                'quality': quality
            }
        )
        
        self.logger.info(f"Sold {quantity} {commodity} for ${total_value:.2f}")
        
        # Emit sale event
        self.event_system.publish('crop_sold', {
            'commodity': commodity,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_value': total_value,
            'quality': quality,
            'transaction_id': transaction_id
        }, EventPriority.NORMAL, 'economy_system')
        
        return {
            'success': True,
            'total_value': total_value,
            'unit_price': unit_price,
            'transaction_id': transaction_id
        }
    
    def apply_for_loan(self, amount: float, term_months: int, purpose: str = "Farm operations") -> Dict[str, Any]:
        """Apply for a new loan"""
        if amount <= 0 or term_months <= 0:
            return {'success': False, 'message': 'Invalid loan parameters'}
        
        # Simple credit check based on current debt
        current_debt = sum(loan.remaining_balance for loan in self.active_loans.values())
        debt_ratio = current_debt / max(self.current_cash + current_debt, 1000)
        
        if debt_ratio > 0.8:  # Debt-to-asset ratio too high
            return {'success': False, 'message': 'Loan application denied - too much existing debt'}
        
        # Create loan
        self.loan_counter += 1
        loan_id = f"loan_{self.loan_counter:03d}"
        
        loan = Loan(
            loan_id=loan_id,
            principal=amount,
            remaining_balance=amount,
            interest_rate=0.06,  # 6% base rate
            term_months=term_months,
            monthly_payment=0
        )
        loan.monthly_payment = loan.calculate_monthly_payment()
        
        self.active_loans[loan_id] = loan
        
        # Add loan disbursement transaction
        transaction_id = self.add_transaction(
            TransactionType.LOAN_DISBURSEMENT,
            amount,
            f"Loan disbursement: {purpose}",
            metadata={'loan_id': loan_id, 'purpose': purpose}
        )
        
        self.logger.info(f"Loan approved: ${amount:.2f} for {term_months} months")
        
        return {
            'success': True,
            'loan_id': loan_id,
            'amount': amount,
            'monthly_payment': loan.monthly_payment,
            'transaction_id': transaction_id
        }
    
    def make_loan_payment(self, loan_id: str, amount: float) -> Dict[str, Any]:
        """Make payment on a loan"""
        if loan_id not in self.active_loans:
            return {'success': False, 'message': 'Loan not found'}
        
        loan = self.active_loans[loan_id]
        
        if amount > self.current_cash:
            return {'success': False, 'message': 'Insufficient funds'}
        
        # Simple payment processing
        payment_to_principal = min(amount, loan.remaining_balance)
        loan.remaining_balance -= payment_to_principal
        
        # Deduct from cash
        self.current_cash -= amount
        
        # Add transaction
        transaction_id = self.add_transaction(
            TransactionType.LOAN_PAYMENT,
            -amount,
            f"Loan payment for {loan_id}",
            metadata={'loan_id': loan_id, 'principal_paid': payment_to_principal}
        )
        
        # Remove loan if paid off
        loan_paid_off = loan.remaining_balance <= 0
        if loan_paid_off:
            del self.active_loans[loan_id]
            self.logger.info(f"Loan {loan_id} paid off!")
        
        return {
            'success': True,
            'principal_paid': payment_to_principal,
            'remaining_balance': loan.remaining_balance,
            'loan_paid_off': loan_paid_off,
            'transaction_id': transaction_id
        }
    
    def accept_contract(self, contract_id: str) -> Dict[str, Any]:
        """Accept an available contract"""
        if contract_id not in self.available_contracts:
            return {'success': False, 'message': 'Contract not found'}
        
        contract = self.available_contracts[contract_id]
        
        # Move to active contracts
        self.active_contracts[contract_id] = contract
        del self.available_contracts[contract_id]
        
        self.logger.info(f"Contract accepted: {contract.commodity} x{contract.quantity_required}")
        
        return {'success': True, 'contract': contract}
    
    def fulfill_contract(self, contract_id: str, quantity: int, quality: float) -> Dict[str, Any]:
        """Fulfill part or all of a contract"""
        if contract_id not in self.active_contracts:
            return {'success': False, 'message': 'Contract not found'}
        
        contract = self.active_contracts[contract_id]
        
        if quality < contract.quality_requirement:
            return {'success': False, 'message': 'Quality does not meet contract requirements'}
        
        # Calculate delivery amount
        remaining = contract.get_remaining_quantity()
        delivery_quantity = min(quantity, remaining)
        
        if delivery_quantity <= 0:
            return {'success': False, 'message': 'Contract already fulfilled'}
        
        # Update contract progress
        contract.quantity_delivered += delivery_quantity
        
        # Calculate payment
        payment = delivery_quantity * contract.price_per_unit
        
        # Add transaction
        transaction_id = self.add_transaction(
            TransactionType.CONTRACT_PAYMENT,
            payment,
            f"Contract fulfillment: {contract.commodity} x{delivery_quantity}",
            metadata={
                'contract_id': contract_id,
                'quantity_delivered': delivery_quantity,
                'quality': quality,
                'unit_price': contract.price_per_unit
            }
        )
        
        # Check if contract complete
        contract_completed = contract.get_remaining_quantity() == 0
        if contract_completed:
            del self.active_contracts[contract_id]
            self.logger.info(f"Contract {contract_id} completed!")
        
        return {
            'success': True,
            'payment': payment,
            'remaining_quantity': contract.get_remaining_quantity(),
            'contract_completed': contract_completed,
            'transaction_id': transaction_id
        }
    
    def add_transaction(self, transaction_type: TransactionType, amount: float, 
                       description: str, category: str = "general", 
                       metadata: Dict[str, Any] = None) -> str:
        """Add a financial transaction"""
        self.transaction_counter += 1
        transaction_id = f"txn_{self.transaction_counter:06d}"
        
        current_time = self.time_system.get_current_time().total_minutes
        
        transaction = Transaction(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            timestamp=current_time,
            category=category,
            metadata=metadata or {}
        )
        
        self.transactions.append(transaction)
        
        # Update cash balance
        self.current_cash += amount
        
        return transaction_id
    
    def get_financial_summary(self) -> Dict[str, Any]:
        """Get comprehensive financial summary"""
        # Calculate loan totals
        total_loan_balance = sum(loan.remaining_balance for loan in self.active_loans.values())
        total_monthly_payments = sum(loan.monthly_payment for loan in self.active_loans.values())
        
        # Calculate asset value
        asset_value = self.current_cash
        
        # Calculate net worth
        net_worth = asset_value - total_loan_balance
        
        return {
            'current_cash': self.current_cash,
            'total_assets': asset_value,
            'total_liabilities': total_loan_balance,
            'net_worth': net_worth,
            'credit_rating': self.credit_rating,
            'monthly_loan_payments': total_monthly_payments,
            'subsidy_balance': self.subsidy_balance,
            'subsidy_days_remaining': self.subsidy_days_remaining,
            'active_loans': len(self.active_loans),
            'active_contracts': len(self.active_contracts),
            'total_transactions': len(self.transactions),
            'market_prices': {k: v.current_price for k, v in self.market_simulator.market_prices.items()}
        }
    
    def _generate_contracts(self):
        """Generate available contracts"""
        # Generate 2-3 random contracts
        num_contracts = random.randint(2, 3)
        
        buyers = ['AgriCorp', 'FarmFresh Inc', 'Green Valley Co-op']
        commodities = list(self.market_simulator.market_prices.keys())
        
        for i in range(num_contracts):
            self.contract_counter += 1
            contract_id = f"contract_{self.contract_counter:03d}"
            
            commodity = random.choice(commodities)
            base_price = self.market_simulator.market_prices[commodity].current_price
            
            # Contract price is usually 10-20% above market price
            contract_price = base_price * random.uniform(1.1, 1.2)
            
            contract = Contract(
                contract_id=contract_id,
                buyer_name=random.choice(buyers),
                commodity=commodity,
                quantity_required=random.randint(50, 150),
                price_per_unit=contract_price,
                quality_requirement=random.uniform(0.7, 0.9),
                deadline_days=random.randint(14, 45)
            )
            
            self.available_contracts[contract_id] = contract
    
    def _on_day_changed(self, event_data: Dict[str, Any]):
        """Handle daily economy updates"""
        # Process subsidies
        if self.subsidy_days_remaining > 0:
            daily_subsidy = 100.0
            self.add_transaction(
                TransactionType.SUBSIDY_PAYMENT,
                daily_subsidy,
                "Daily government subsidy",
                category="subsidy"
            )
            self.subsidy_days_remaining -= 1
            self.subsidy_balance += daily_subsidy
        
        # Update market prices
        current_season = self.time_system.get_current_season()
        weather = self.time_system.get_current_weather()
        weather_modifier = weather.crop_growth_modifier if weather else 1.0
        
        self.market_simulator.update_market_prices(current_season, weather_modifier)
        
        # Generate new contracts occasionally
        if random.random() < 0.2:  # 20% chance daily
            self._generate_contracts()
    
    def _on_season_changed(self, event_data: Dict[str, Any]):
        """Handle seasonal economy changes"""
        self.logger.info(f"Season changed to {event_data['new_season']}")
        
        # Major market update for new season
        new_season = Season(event_data['new_season'])
        self.market_simulator.update_market_prices(new_season)
        
        # Generate seasonal contracts
        self._generate_contracts()


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

# Convenience functions
def get_current_price(commodity: str) -> float:
    """Get current market price for commodity"""
    return get_economy_system().get_current_price(commodity)

def sell_crops(commodity: str, quantity: int, quality: float = 1.0) -> Dict[str, Any]:
    """Sell crops at current market price"""
    return get_economy_system().sell_crops(commodity, quantity, quality)

def get_financial_summary() -> Dict[str, Any]:
    """Get current financial summary"""
    return get_economy_system().get_financial_summary()

def apply_for_loan(amount: float, term_months: int, purpose: str = "Farm operations") -> Dict[str, Any]:
    """Apply for a new loan"""
    return get_economy_system().apply_for_loan(amount, term_months, purpose)
