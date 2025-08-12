"""
Economy Manager - Handles financial transactions, loans, and subsidies
Manages the game's economic systems including cash flow, loans, and market interactions.
"""

import random
from typing import Dict, List, Optional
from scripts.core.config import *


class Transaction:
    """Individual financial transaction record"""
    
    def __init__(self, amount: float, description: str, transaction_type: str, day: int = 1):
        self.amount = amount  # Positive for income, negative for expenses
        self.description = description
        self.type = transaction_type  # 'income', 'expense', 'loan', 'subsidy'
        self.day = day
        
    def __str__(self):
        sign = "+" if self.amount >= 0 else ""
        return f"Day {self.day}: {self.description} ({sign}${self.amount:.2f})"


class Loan:
    """Loan tracking with interest and payments"""
    
    def __init__(self, principal: float, interest_rate: float, term_days: int, loan_type: str):
        self.principal = principal
        self.remaining_balance = principal
        self.interest_rate = interest_rate
        self.term_days = term_days
        self.loan_type = loan_type
        
        # Calculate daily payment
        if term_days > 0:
            # Simple interest calculation for game simplicity
            total_interest = principal * interest_rate * (term_days / 365.0)
            total_amount = principal + total_interest
            self.daily_payment = total_amount / term_days
        else:
            self.daily_payment = 0
        
        self.payments_made = 0
        self.days_overdue = 0
        self.is_paid_off = False
    
    def make_payment(self, amount: float) -> float:
        """Make a payment, returns actual amount paid"""
        if self.is_paid_off:
            return 0
        
        actual_payment = min(amount, self.remaining_balance)
        self.remaining_balance -= actual_payment
        self.payments_made += 1
        
        if self.remaining_balance <= 0.01:  # Close enough to zero
            self.remaining_balance = 0
            self.is_paid_off = True
        
        return actual_payment
    
    def get_status(self) -> Dict:
        """Get loan status information"""
        return {
            'type': self.loan_type,
            'principal': self.principal,
            'remaining': self.remaining_balance,
            'daily_payment': self.daily_payment,
            'payments_made': self.payments_made,
            'days_overdue': self.days_overdue,
            'is_paid_off': self.is_paid_off,
            'progress': 1.0 - (self.remaining_balance / self.principal) if self.principal > 0 else 1.0
        }


class EconomyManager:
    """Manages the game economy"""
    
    def __init__(self, event_system):
        """Initialize economy manager"""
        self.event_system = event_system
        
        # Financial state
        self.cash = STARTING_CASH
        self.total_income = 0
        self.total_expenses = 0
        
        # Transaction history
        self.transactions: List[Transaction] = []
        
        # Loans
        self.loans: List[Loan] = []
        
        # Subsidies
        self.subsidy_days_remaining = SUBSIDY_DAYS
        self.daily_subsidy_amount = DAILY_SUBSIDY
        
        # Market prices (corn only for MVP)
        self.corn_price = (CORN_PRICE_MIN + CORN_PRICE_MAX) / 2  # Start at average
        self.price_history: List[float] = [self.corn_price]
        
        # Create starting loan
        self._create_starting_loan()
        
        # Register for events
        self.event_system.subscribe('day_passed', self._handle_day_passed)
        self.event_system.subscribe('payroll_due', self._handle_payroll)
        self.event_system.subscribe('inventory_sale_completed', self._handle_inventory_sale)
        self.event_system.subscribe('irrigation_daily_bill', self._handle_irrigation_bill)
        
        # Emit initial money update
        self.event_system.emit('money_changed', {'amount': self.cash})
        
        print(f"Economy Manager initialized - Starting cash: ${self.cash}")
        print(f"First-time farmer loan: ${FIRST_TIME_LOAN}")
        print(f"Daily subsidy: ${DAILY_SUBSIDY} for {SUBSIDY_DAYS} days")
    
    def _create_starting_loan(self):
        """Create the mandatory first-time farmer loan"""
        loan = Loan(
            principal=FIRST_TIME_LOAN,
            interest_rate=LOAN_INTEREST_RATE,
            term_days=365,  # 1 year term
            loan_type="First-Time Farmer Loan"
        )
        
        self.loans.append(loan)
        
        # Add loan money to cash
        self.add_money(FIRST_TIME_LOAN, "First-time farmer loan", "loan")
        
        print(f"Created starting loan: ${FIRST_TIME_LOAN} at {LOAN_INTEREST_RATE*100}% annual interest")
        print(f"Daily payment: ${loan.daily_payment:.2f}")
    
    def add_money(self, amount: float, description: str, transaction_type: str = "income") -> bool:
        """Add money to cash reserves"""
        if amount > 0:
            self.cash += amount
            self.total_income += amount
            transaction = Transaction(amount, description, transaction_type, self._get_current_day())
            self.transactions.append(transaction)
            
            # Emit money change event
            self.event_system.emit('money_changed', {'amount': self.cash})
            self.event_system.emit('transaction_added', {
                'amount': amount,
                'description': description,
                'type': transaction_type,
                'new_balance': self.cash
            })
            
            return True
        return False
    
    def spend_money(self, amount: float, description: str, transaction_type: str = "expense") -> bool:
        """Spend money if available"""
        if amount <= 0:
            return True
        
        if self.cash >= amount:
            self.cash -= amount
            self.total_expenses += amount
            transaction = Transaction(-amount, description, transaction_type, self._get_current_day())
            self.transactions.append(transaction)
            
            # Emit money change event
            self.event_system.emit('money_changed', {'amount': self.cash})
            self.event_system.emit('transaction_added', {
                'amount': -amount,
                'description': description,
                'type': transaction_type,
                'new_balance': self.cash
            })
            
            return True
        else:
            # Not enough money
            self.event_system.emit('insufficient_funds', {
                'required': amount,
                'available': self.cash,
                'description': description
            })
            return False
    
    def get_current_balance(self) -> float:
        """Get current cash balance"""
        return self.cash
    
    def get_net_worth(self) -> float:
        """Calculate net worth (cash - loan balances)"""
        total_debt = sum(loan.remaining_balance for loan in self.loans)
        return self.cash - total_debt
    
    def sell_corn(self, quantity: int) -> float:
        """Sell harvested corn at current market price"""
        if quantity <= 0:
            return 0
        
        total_value = quantity * self.corn_price
        self.add_money(total_value, f"Sold {quantity} corn @ ${self.corn_price:.2f}/unit", "income")
        
        # Emit crop sale event
        self.event_system.emit('crop_sold', {
            'crop_type': 'corn',
            'quantity': quantity,
            'price_per_unit': self.corn_price,
            'total_value': total_value
        })
        
        print(f"Sold {quantity} corn for ${total_value:.2f} (${self.corn_price:.2f}/unit)")
        return total_value
    
    def update_corn_price(self):
        """Update corn market price with some randomness"""
        # Simple price volatility model
        change_factor = random.uniform(0.85, 1.15)  # ±15% daily change
        
        # Trend toward average over time
        average_price = (CORN_PRICE_MIN + CORN_PRICE_MAX) / 2
        trend_factor = 0.1 * (average_price - self.corn_price) / average_price
        
        new_price = self.corn_price * change_factor * (1 + trend_factor)
        self.corn_price = max(CORN_PRICE_MIN, min(CORN_PRICE_MAX, new_price))
        
        # Store price history
        self.price_history.append(self.corn_price)
        if len(self.price_history) > 30:  # Keep last 30 days
            self.price_history.pop(0)
        
        # Emit price update event
        self.event_system.emit('market_price_updated', {
            'crop_type': 'corn',
            'old_price': self.price_history[-2] if len(self.price_history) > 1 else self.corn_price,
            'new_price': self.corn_price,
            'change_percent': ((self.corn_price / self.price_history[-2]) - 1) * 100 if len(self.price_history) > 1 else 0
        })
    
    def process_daily_expenses(self):
        """Process daily fixed expenses"""
        # Utilities
        self.spend_money(DAILY_UTILITIES, "Daily utilities", "expense")
        
        # Loan payments
        self._process_loan_payments()
        
        # Government subsidy
        if self.subsidy_days_remaining > 0:
            self.add_money(self.daily_subsidy_amount, "Government subsidy", "subsidy")
            self.subsidy_days_remaining -= 1
            
            if self.subsidy_days_remaining == 0:
                self.event_system.emit('subsidy_ended', {
                    'total_received': SUBSIDY_DAYS * DAILY_SUBSIDY
                })
    
    def _process_loan_payments(self):
        """Process daily loan payments"""
        for loan in self.loans:
            if loan.is_paid_off:
                continue
            
            payment_amount = loan.daily_payment
            
            if self.cash >= payment_amount:
                actual_payment = self.spend_money(payment_amount, f"{loan.loan_type} payment", "loan")
                if actual_payment:
                    loan.make_payment(payment_amount)
                    
                    if loan.is_paid_off:
                        self.event_system.emit('loan_paid_off', {
                            'loan_type': loan.loan_type,
                            'original_amount': loan.principal,
                            'total_payments': loan.payments_made
                        })
                        print(f"Loan paid off: {loan.loan_type}")
            else:
                # Missed payment
                loan.days_overdue += 1
                self.event_system.emit('loan_payment_missed', {
                    'loan_type': loan.loan_type,
                    'payment_due': payment_amount,
                    'available_cash': self.cash,
                    'days_overdue': loan.days_overdue
                })
                
                # Add penalty for missed payments
                if loan.days_overdue % 7 == 0:  # Weekly penalty
                    penalty = loan.principal * 0.01  # 1% penalty
                    loan.remaining_balance += penalty
                    print(f"Loan penalty applied: ${penalty:.2f} for {loan.loan_type}")
    
    def get_financial_summary(self) -> Dict:
        """Get comprehensive financial summary"""
        total_debt = sum(loan.remaining_balance for loan in self.loans)
        
        return {
            'cash': self.cash,
            'total_income': self.total_income,
            'total_expenses': self.total_expenses,
            'net_worth': self.get_net_worth(),
            'total_debt': total_debt,
            'daily_expenses': self._calculate_daily_expenses(),
            'subsidy_days_remaining': self.subsidy_days_remaining,
            'corn_price': self.corn_price,
            'loan_count': len([l for l in self.loans if not l.is_paid_off]),
            'loans': [loan.get_status() for loan in self.loans]
        }
    
    def _calculate_daily_expenses(self) -> float:
        """Calculate total daily expenses"""
        expenses = DAILY_UTILITIES
        expenses += sum(loan.daily_payment for loan in self.loans if not loan.is_paid_off)
        return expenses
    
    def get_recent_transactions(self, days: int = 7) -> List[Transaction]:
        """Get recent transactions"""
        current_day = self._get_current_day()
        cutoff_day = max(1, current_day - days)
        
        return [t for t in self.transactions if t.day >= cutoff_day]
    
    def _get_current_day(self) -> int:
        """Get current game day from time manager"""
        # This is a simplified version - would normally get from time manager
        return max(1, len(self.price_history))
    
    def update(self, dt: float):
        """Update economy systems"""
        # Economy updates are mostly event-driven
        pass
    
    def _handle_day_passed(self, event_data):
        """Handle day passing for daily expenses and market updates"""
        new_day = event_data.get('new_day', 1)
        
        # Process daily expenses
        self.process_daily_expenses()
        
        # Update market prices
        self.update_corn_price()
        
        print(f"Day {new_day} financial summary:")
        print(f"  Cash: ${self.cash:.2f}")
        print(f"  Corn price: ${self.corn_price:.2f}")
        print(f"  Daily expenses: ${self._calculate_daily_expenses():.2f}")
    
    def _handle_payroll(self, event_data):
        """Handle employee payroll"""
        total_wages = event_data.get('total_wages', 0)
        employee_count = event_data.get('employee_count', 0)
        
        if total_wages > 0:
            if self.spend_money(total_wages, f"Payroll for {employee_count} employees", "expense"):
                self.event_system.emit('payroll_paid', {
                    'amount': total_wages,
                    'employee_count': employee_count,
                    'remaining_cash': self.cash
                })
            else:
                self.event_system.emit('payroll_failed', {
                    'amount_due': total_wages,
                    'available_cash': self.cash,
                    'employee_count': employee_count
                })
    
    def _handle_inventory_sale(self, event_data):
        """Handle sales from inventory system"""
        crop_type = event_data.get('crop_type', 'corn')
        quantity = event_data.get('quantity', 0)
        revenue = event_data.get('revenue', 0)
        
        if revenue > 0:
            self.add_money(revenue, f"Sold {quantity} {crop_type} from storage", "income")
            print(f"Inventory sale completed: {quantity} {crop_type} for ${revenue:.2f}")
    
    def _handle_irrigation_bill(self, event_data):
        """Handle daily irrigation costs during drought"""
        cost = event_data.get('cost', 0)
        irrigated_tiles = event_data.get('irrigated_tiles', 0)
        cost_per_tile = event_data.get('cost_per_tile', 5)
        weather_event = event_data.get('weather_event', 'drought')
        
        if cost > 0:
            # Charge irrigation costs
            self.spend_money(cost, f"Irrigation water cost ({irrigated_tiles} tiles @ ${cost_per_tile}/day)", "irrigation")
            print(f"Irrigation bill: ${cost:.2f} for {irrigated_tiles} tiles during {weather_event}")
            
            # Emit irrigation cost notification for UI
            self.event_system.emit('irrigation_cost_incurred', {
                'cost': cost,
                'irrigated_tiles': irrigated_tiles,
                'weather_event': weather_event
            })