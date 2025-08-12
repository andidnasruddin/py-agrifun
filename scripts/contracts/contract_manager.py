"""
Contract Manager - Handles farming contracts and agricultural business agreements

This system manages contracts between the player and buyers, providing guaranteed
pricing in exchange for committed crop deliveries. Contracts add strategic depth
by requiring players to plan production in advance while managing risk vs reward.

Key Features:
- Multiple contract types with different terms and requirements
- Reputation system affecting available contracts and pricing
- Risk vs reward balance between contracts and spot market
- Strategic resource planning and allocation decisions

Design Goals:
- Realistic agricultural business simulation
- Strategic depth through commitment and planning
- Educational value about commodity markets and contracts
- Integration with existing crop, economy, and employee systems

Usage:
    contract_manager = ContractManager(event_system, economy_manager, time_manager)
    contract_manager.generate_monthly_contracts()
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import random
from scripts.core.config import *


class ContractType(Enum):
    """Types of farming contracts"""
    VOLUME = "volume"        # Large quantity, standard price
    PREMIUM = "premium"      # Quality bonus, higher price per unit
    SEASONAL = "seasonal"    # Seasonal crop, specific delivery window
    BULK = "bulk"           # Very large quantity, lower per-unit price but high total


class ContractStatus(Enum):
    """Contract status states"""
    AVAILABLE = "available"     # Available for acceptance
    ACCEPTED = "accepted"       # Player has accepted, in progress
    FULFILLED = "fulfilled"     # Successfully completed
    FAILED = "failed"          # Failed to meet terms
    EXPIRED = "expired"        # Expired without acceptance


@dataclass
class Contract:
    """Individual farming contract"""
    id: str
    contract_type: ContractType
    buyer_name: str
    crop_type: str
    quantity_required: int
    price_per_unit: float
    deadline_days: int          # Days from acceptance to fulfill
    quality_requirement: float  # Minimum quality (0.0-1.0)
    status: ContractStatus
    created_day: int
    accepted_day: Optional[int] = None
    bonus_payment: float = 0.0  # Extra payment for premium contracts
    penalty_rate: float = 0.1   # Penalty if failed (% of contract value)
    reputation_bonus: int = 10   # Reputation gained if fulfilled
    reputation_penalty: int = 25 # Reputation lost if failed


class ContractManager:
    """Manages farming contracts and business relationships"""
    
    def __init__(self, event_system, economy_manager, time_manager, inventory_manager=None):
        """Initialize contract manager"""
        self.event_system = event_system
        self.economy_manager = economy_manager
        self.time_manager = time_manager
        self.inventory_manager = inventory_manager
        
        # Contract storage
        self.available_contracts: List[Contract] = []
        self.active_contracts: List[Contract] = []
        self.completed_contracts: List[Contract] = []
        
        # Player reputation (affects contract availability and terms)
        self.reputation = 50  # Start neutral (0-100 scale)
        self.contracts_fulfilled = 0
        self.contracts_failed = 0
        
        # Buyer companies for variety
        self.buyer_companies = [
            "AgriCorp Foods", "Valley Fresh Co.", "Farm Direct Ltd.",
            "Premium Produce Inc.", "Golden Harvest Co.", "Regional Foods LLC",
            "Countryside Markets", "Fresh Fields Corp.", "Harvest Moon Foods",
            "Green Valley Trading"
        ]
        
        # Contract generation settings
        self.next_contract_id = 1
        self.contracts_per_month = 6  # Generate 6 contracts monthly
        self.last_generation_day = -30  # Start with immediate contract generation
        
        # Register for events
        self.event_system.subscribe('day_passed', self._handle_day_passed)
        self.event_system.subscribe('accept_contract_requested', self._handle_contract_acceptance)
        self.event_system.subscribe('crop_harvested', self._handle_crop_harvested)
        self.event_system.subscribe('show_contracts_requested', self._handle_show_contracts)
        self.event_system.subscribe('get_contract_data_for_ui', self._handle_contract_data_request)
        self.event_system.subscribe('inventory_updated', self._handle_inventory_updated)
        
        # Generate initial contracts
        self._generate_contracts()
        
        print("Contract Manager initialized - Ready for agricultural business!")
        print(f"Starting reputation: {self.reputation}/100")
    
    def _generate_contracts(self):
        """Generate new contracts based on current game state"""
        current_day = self.time_manager.current_day if self.time_manager else 1
        
        # Clear expired contracts
        self._remove_expired_contracts()
        
        # Generate contracts if it's been long enough
        if current_day >= self.last_generation_day + 30:  # Monthly generation
            contracts_to_generate = self.contracts_per_month
            
            for _ in range(contracts_to_generate):
                contract = self._create_random_contract(current_day)
                self.available_contracts.append(contract)
            
            self.last_generation_day = current_day
            
            # Emit event for UI update
            self.event_system.emit('contracts_updated', {
                'available_count': len(self.available_contracts),
                'active_count': len(self.active_contracts)
            })
            
            print(f"Generated {contracts_to_generate} new contracts for day {current_day}")
    
    def _create_random_contract(self, current_day: int) -> Contract:
        """Create a randomized contract based on game state and reputation"""
        contract_id = f"CONTRACT_{self.next_contract_id:04d}"
        self.next_contract_id += 1
        
        # Select contract type based on reputation
        contract_types = [ContractType.VOLUME, ContractType.BULK]
        if self.reputation >= 60:
            contract_types.extend([ContractType.PREMIUM, ContractType.SEASONAL])
        
        contract_type = random.choice(contract_types)
        buyer_name = random.choice(self.buyer_companies)
        crop_type = random.choice(list(CROP_TYPES.keys()))
        
        # Base parameters from crop data
        crop_data = CROP_TYPES[crop_type]
        base_price = (crop_data['price_min'] + crop_data['price_max']) / 2
        
        # Adjust parameters based on contract type
        if contract_type == ContractType.VOLUME:
            quantity = random.randint(50, 150)
            price_multiplier = 0.95  # Slightly below market average
            deadline_days = random.randint(45, 90)
            quality_requirement = 0.5
            bonus_payment = 0
            
        elif contract_type == ContractType.PREMIUM:
            quantity = random.randint(20, 80)
            price_multiplier = 1.15  # Premium pricing
            deadline_days = random.randint(60, 120)
            quality_requirement = 0.8  # High quality requirement
            bonus_payment = quantity * base_price * 0.1  # 10% bonus
            
        elif contract_type == ContractType.SEASONAL:
            quantity = random.randint(30, 100)
            price_multiplier = 1.05  # Slight premium
            deadline_days = random.randint(30, 60)  # Tighter deadline
            quality_requirement = 0.6
            bonus_payment = 0
            
        elif contract_type == ContractType.BULK:
            quantity = random.randint(200, 400)
            price_multiplier = 0.85  # Lower per-unit price
            deadline_days = random.randint(90, 180)  # Longer deadline
            quality_requirement = 0.4  # Lower quality requirement
            bonus_payment = 0
        
        # Reputation affects pricing and terms
        reputation_bonus = (self.reputation - 50) / 100  # -0.5 to +0.5
        price_multiplier += reputation_bonus * 0.1  # Up to 10% better pricing
        
        final_price = base_price * price_multiplier
        
        return Contract(
            id=contract_id,
            contract_type=contract_type,
            buyer_name=buyer_name,
            crop_type=crop_type,
            quantity_required=quantity,
            price_per_unit=final_price,
            deadline_days=deadline_days,
            quality_requirement=quality_requirement,
            status=ContractStatus.AVAILABLE,
            created_day=current_day,
            bonus_payment=bonus_payment
        )
    
    def _remove_expired_contracts(self):
        """Remove contracts that have expired"""
        current_day = self.time_manager.current_day if self.time_manager else 1
        contract_lifetime = 60  # Contracts available for 60 days
        
        expired_contracts = []
        for contract in self.available_contracts[:]:  # Copy list for safe removal
            if current_day >= contract.created_day + contract_lifetime:
                contract.status = ContractStatus.EXPIRED
                expired_contracts.append(contract)
                self.available_contracts.remove(contract)
                self.completed_contracts.append(contract)
        
        if expired_contracts:
            print(f"Expired {len(expired_contracts)} contracts")
    
    def accept_contract(self, contract_id: str) -> bool:
        """Accept a contract and move it to active contracts"""
        current_day = self.time_manager.current_day if self.time_manager else 1
        
        # Find contract in available list
        contract = None
        for c in self.available_contracts:
            if c.id == contract_id:
                contract = c
                break
        
        if not contract:
            print(f"Contract {contract_id} not found or not available")
            return False
        
        # Move contract to active list
        self.available_contracts.remove(contract)
        contract.status = ContractStatus.ACCEPTED
        contract.accepted_day = current_day
        self.active_contracts.append(contract)
        
        # Emit acceptance event
        self.event_system.emit('contract_accepted', {
            'contract_id': contract.id,
            'buyer_name': contract.buyer_name,
            'crop_type': contract.crop_type,
            'quantity': contract.quantity_required,
            'total_value': contract.quantity_required * contract.price_per_unit + contract.bonus_payment,
            'deadline_days': contract.deadline_days
        })
        
        print(f"Accepted contract {contract.id}: {contract.quantity_required} {CROP_TYPES[contract.crop_type]['name']} for {contract.buyer_name}")
        return True
    
    def get_available_contracts(self) -> List[Contract]:
        """Get list of available contracts for UI display"""
        return self.available_contracts.copy()
    
    def get_active_contracts(self) -> List[Contract]:
        """Get list of active contracts"""
        return self.active_contracts.copy()
    
    def get_contract_summary(self) -> Dict:
        """Get contract summary for UI display"""
        return {
            'reputation': self.reputation,
            'available_contracts': len(self.available_contracts),
            'active_contracts': len(self.active_contracts),
            'contracts_fulfilled': self.contracts_fulfilled,
            'contracts_failed': self.contracts_failed,
            'success_rate': (self.contracts_fulfilled / (self.contracts_fulfilled + self.contracts_failed * 100)) if (self.contracts_fulfilled + self.contracts_failed) > 0 else 0
        }
    
    def _handle_day_passed(self, event_data):
        """Handle day passing for contract management"""
        current_day = event_data.get('day', 1)
        
        # Generate new contracts if needed
        self._generate_contracts()
        
        # Check contract deadlines
        self._check_contract_deadlines(current_day)
    
    def _check_contract_deadlines(self, current_day: int):
        """Check if any active contracts have passed their deadline"""
        failed_contracts = []
        
        for contract in self.active_contracts[:]:  # Copy for safe removal
            if contract.accepted_day and current_day >= contract.accepted_day + contract.deadline_days:
                # Contract has failed due to deadline
                contract.status = ContractStatus.FAILED
                failed_contracts.append(contract)
                
                # Apply reputation penalty
                self.reputation = max(0, self.reputation - contract.reputation_penalty)
                self.contracts_failed += 1
                
                # Apply financial penalty
                penalty_amount = (contract.quantity_required * contract.price_per_unit) * contract.penalty_rate
                self.economy_manager.spend_money(penalty_amount, f"Contract penalty: {contract.buyer_name}", "penalty")
                
                # Move to completed contracts
                self.active_contracts.remove(contract)
                self.completed_contracts.append(contract)
                
                print(f"CONTRACT FAILED: {contract.id} - Reputation: {self.reputation}, Penalty: ${penalty_amount}")
        
        if failed_contracts:
            self.event_system.emit('contracts_failed', {
                'failed_contracts': len(failed_contracts),
                'reputation': self.reputation
            })
    
    def _handle_contract_acceptance(self, event_data):
        """Handle contract acceptance from UI"""
        contract_id = event_data.get('contract_id')
        if contract_id:
            self.accept_contract(contract_id)
    
    def _handle_crop_harvested(self, event_data):
        """Handle crop harvest for contract fulfillment"""
        crop_type = event_data.get('crop_type')
        quantity = event_data.get('quantity', 0)
        quality = event_data.get('quality', 0.5)
        
        print(f"Contract Manager: Noted harvest - {quantity} {crop_type} (quality: {quality:.2f})")
        
        # Check for contract fulfillment opportunities
        self._check_contract_fulfillment()
    
    def _handle_show_contracts(self, event_data):
        """Handle request to show contract board"""
        self._display_contract_board()
    
    def _display_contract_board(self):
        """Display available and active contracts in console"""
        print("\n" + "="*80)
        print("CONTRACT BOARD - AGRICULTURAL BUSINESS OPPORTUNITIES")
        print("="*80)
        print(f"Reputation: {self.reputation}/100 | Completed: {self.contracts_fulfilled} | Failed: {self.contracts_failed}")
        
        if not self.available_contracts and not self.active_contracts:
            print("No contracts available. Contracts are generated monthly.")
            print("="*80)
            return
        
        # Show available contracts
        if self.available_contracts:
            print(f"\n📋 AVAILABLE CONTRACTS ({len(self.available_contracts)}):")
            print("-" * 80)
            for i, contract in enumerate(self.available_contracts, 1):
                crop_name = CROP_TYPES[contract.crop_type]['name']
                total_value = contract.quantity_required * contract.price_per_unit + contract.bonus_payment
                quality_req = f"{contract.quality_requirement*100:.0f}%"
                
                print(f"{i}. {contract.buyer_name} - {contract.contract_type.value.upper()}")
                print(f"   Crop: {contract.quantity_required} units of {crop_name}")
                print(f"   Price: ${contract.price_per_unit:.2f}/unit (Total: ${total_value:.2f})")
                print(f"   Quality: {quality_req}+ required | Deadline: {contract.deadline_days} days")
                if contract.bonus_payment > 0:
                    print(f"   BONUS: ${contract.bonus_payment:.2f} for quality delivery")
                print(f"   Contract ID: {contract.id}")
                print()
        
        # Show active contracts
        if self.active_contracts:
            current_day = self.time_manager.current_day if self.time_manager else 1
            print(f"📝 ACTIVE CONTRACTS ({len(self.active_contracts)}):")
            print("-" * 80)
            for i, contract in enumerate(self.active_contracts, 1):
                crop_name = CROP_TYPES[contract.crop_type]['name']
                days_left = (contract.accepted_day + contract.deadline_days) - current_day
                total_value = contract.quantity_required * contract.price_per_unit + contract.bonus_payment
                
                print(f"{i}. {contract.buyer_name} - {contract.contract_type.value.upper()}")
                print(f"   Need: {contract.quantity_required} units of {crop_name}")
                print(f"   Value: ${total_value:.2f} | Days Left: {days_left}")
                print(f"   Status: {'⚠️  URGENT' if days_left <= 10 else '✓ On Track'}")
                print()
        
        print("="*80)
        print("Use 'Accept Contract' functionality to commit to deliveries.")
        print("Remember: Contract failures damage reputation and incur penalties!")
        print("="*80 + "\n")
    
    def _check_contract_fulfillment(self):
        """Check if any active contracts can be fulfilled with current inventory"""
        if not self.inventory_manager or not self.active_contracts:
            return
        
        current_day = self.time_manager.current_day if self.time_manager else 1
        fulfilled_contracts = []
        
        for contract in self.active_contracts[:]:  # Copy list for safe modification
            crop_type = contract.crop_type
            required_quantity = contract.quantity_required
            required_quality = contract.quality_requirement
            
            # Check if we have enough crops in inventory
            if self._has_sufficient_inventory(crop_type, required_quantity, required_quality):
                # Fulfill the contract
                if self._fulfill_contract(contract):
                    fulfilled_contracts.append(contract)
        
        # Process fulfilled contracts
        for contract in fulfilled_contracts:
            self._complete_contract(contract, current_day)
    
    def _has_sufficient_inventory(self, crop_type: str, required_quantity: int, required_quality: float) -> bool:
        """Check if inventory has sufficient crops of required quality"""
        if not self.inventory_manager:
            return False
        
        # Get available crops of the required type
        available_crops = self.inventory_manager.crops.get(crop_type, [])
        
        # Count crops that meet quality requirements
        suitable_crops = [crop for crop in available_crops if crop.quality >= required_quality]
        total_suitable_quantity = sum(crop.quantity for crop in suitable_crops)
        
        return total_suitable_quantity >= required_quantity
    
    def _fulfill_contract(self, contract) -> bool:
        """Fulfill a contract by consuming crops from inventory"""
        if not self.inventory_manager:
            return False
        
        crop_type = contract.crop_type
        required_quantity = contract.quantity_required
        required_quality = contract.quality_requirement
        
        # Get suitable crops sorted by quality (use highest quality first for premium contracts)
        available_crops = self.inventory_manager.crops.get(crop_type, [])
        suitable_crops = [crop for crop in available_crops if crop.quality >= required_quality]
        suitable_crops.sort(key=lambda x: x.quality, reverse=True)  # Best quality first
        
        # Consume crops to fulfill contract
        remaining_needed = required_quantity
        crops_to_remove = []
        
        for crop in suitable_crops:
            if remaining_needed <= 0:
                break
            
            if crop.quantity <= remaining_needed:
                # Use entire crop entry
                remaining_needed -= crop.quantity
                crops_to_remove.append(crop)
            else:
                # Partial consumption
                crop.quantity -= remaining_needed
                remaining_needed = 0
        
        # Remove consumed crops from inventory
        for crop in crops_to_remove:
            available_crops.remove(crop)
        
        # Update inventory display
        self.event_system.emit('inventory_updated', {
            'crop_type': crop_type,
            'total_quantity': sum(crop.quantity for crop in available_crops),
            'action': 'contract_fulfillment'
        })
        
        print(f"Fulfilled contract {contract.id}: Used {required_quantity} {crop_type} from inventory")
        return remaining_needed == 0
    
    def _complete_contract(self, contract, current_day: int):
        """Complete a fulfilled contract and process payment"""
        # Calculate payment
        base_payment = contract.quantity_required * contract.price_per_unit
        bonus_payment = contract.bonus_payment
        total_payment = base_payment + bonus_payment
        
        # Pay the player
        self.economy_manager.add_money(
            total_payment, 
            f"Contract completed: {contract.buyer_name}", 
            "contract_payment"
        )
        
        # Update reputation
        self.reputation = min(100, self.reputation + contract.reputation_bonus)
        self.contracts_fulfilled += 1
        
        # Move contract to completed
        contract.status = ContractStatus.FULFILLED
        self.active_contracts.remove(contract)
        self.completed_contracts.append(contract)
        
        # Emit completion event
        self.event_system.emit('contract_completed', {
            'contract_id': contract.id,
            'buyer_name': contract.buyer_name,
            'crop_type': contract.crop_type,
            'quantity': contract.quantity_required,
            'payment': total_payment,
            'reputation_gained': contract.reputation_bonus,
            'new_reputation': self.reputation
        })
        
        print(f"CONTRACT COMPLETED: {contract.id} - Payment: ${total_payment:.2f}, Reputation: {self.reputation}")
    
    def _handle_inventory_updated(self, event_data):
        """Handle inventory updates - check for contract fulfillment opportunities"""
        # Check fulfillment whenever inventory changes
        self._check_contract_fulfillment()
    
    def _handle_contract_data_request(self, event_data):
        """Handle request for contract data from UI"""
        # Send contract data to UI
        self.event_system.emit('contract_data_for_ui', {
            'available_contracts': self.available_contracts,
            'active_contracts': self.active_contracts,
            'reputation': self.reputation
        })
        print(f"Sent contract data to UI: {len(self.available_contracts)} available, {len(self.active_contracts)} active")
    
    def update(self, dt: float):
        """Update contract systems"""
        # Periodically check for contract fulfillment opportunities
        # Check every 1 second for responsive contract completion
        if not hasattr(self, '_fulfillment_check_timer'):
            self._fulfillment_check_timer = 0.0
        
        self._fulfillment_check_timer += dt
        if self._fulfillment_check_timer >= 1.0:  # Check every 1 second
            self._check_contract_fulfillment()
            self._fulfillment_check_timer = 0.0