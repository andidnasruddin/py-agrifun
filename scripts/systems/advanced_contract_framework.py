"""
Advanced Contract Framework - Comprehensive Agricultural Contract Management for AgriFun

This system provides sophisticated contract management for agricultural operations including
forward contracts, basis contracts, minimum price contracts, production contracts, and
custom harvesting agreements. Integrates with dynamic pricing and risk management systems.

Key Features:
- Multiple contract types with realistic terms and conditions
- Forward pricing contracts with delivery windows and quality specifications
- Basis contracts with futures market integration
- Minimum price contracts with premium calculations
- Production contracts with input cost sharing and guaranteed margins
- Custom harvesting service agreements with performance guarantees
- Contract performance tracking and settlement processing
- Risk assessment and contract optimization recommendations

Contract Types:
- Forward Contracts: Fixed price delivery contracts with quality premiums/discounts
- Basis Contracts: Local price relative to futures with basis risk management
- Minimum Price Contracts: Price floors with upside participation
- Production Contracts: Comprehensive crop production agreements
- Marketing Pools: Collective marketing with seasonal delivery flexibility
- Custom Service Contracts: Equipment and labor service agreements

Educational Value:
- Understanding of agricultural marketing strategies and price risk management
- Contract terms negotiation and performance obligations
- Quality specifications and delivery requirements
- Financial planning with contracted vs. open market sales
- Risk-return trade-offs in different contract structures
"""

import time
import uuid
from typing import Dict, List, Set, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

# Import core systems
from ..core.advanced_event_system import get_event_system, EventPriority
from ..core.entity_component_system import get_entity_manager, Component, ComponentCategory
from ..core.advanced_config_system import get_config_manager
from ..core.time_management import get_time_manager
from .dynamic_pricing_system import get_dynamic_pricing_system, MarketRegion

class ContractType(Enum):
    """Types of agricultural contracts"""
    FORWARD_CONTRACT = "forward_contract"           # Fixed price for future delivery
    BASIS_CONTRACT = "basis_contract"               # Price relative to futures
    MINIMUM_PRICE = "minimum_price"                 # Price floor with upside
    PRODUCTION_CONTRACT = "production_contract"     # Comprehensive production agreement
    MARKETING_POOL = "marketing_pool"               # Collective marketing pool
    CUSTOM_SERVICE = "custom_service"               # Equipment/labor service contract
    CASH_SALE = "cash_sale"                        # Immediate cash transaction

class ContractStatus(Enum):
    """Contract status stages"""
    DRAFT = "draft"                     # Contract being negotiated
    PENDING = "pending"                 # Awaiting approval/signatures
    ACTIVE = "active"                   # Contract in force
    PARTIALLY_FULFILLED = "partial"     # Some deliveries made
    FULFILLED = "fulfilled"             # Contract completed
    BREACHED = "breached"               # Contract terms violated
    CANCELLED = "cancelled"             # Contract terminated early
    EXPIRED = "expired"                 # Contract term expired

class QualityGrade(Enum):
    """Commodity quality grades"""
    US_GRADE_1 = "us_grade_1"
    US_GRADE_2 = "us_grade_2"
    US_GRADE_3 = "us_grade_3"
    US_SAMPLE = "us_sample"
    REJECT = "reject"

class DeliveryPeriod(Enum):
    """Contract delivery periods"""
    IMMEDIATE = "immediate"             # Within 30 days
    HARVEST = "harvest"                # During harvest season
    POST_HARVEST = "post_harvest"      # 1-3 months after harvest
    WINTER = "winter"                  # December - February
    SPRING = "spring"                  # March - May
    SUMMER = "summer"                  # June - August
    CUSTOM = "custom"                  # Custom date range

@dataclass
class QualitySpecification:
    """Detailed quality requirements and premiums/discounts"""
    commodity_id: str
    
    # Basic quality parameters
    minimum_grade: QualityGrade
    maximum_moisture_percent: float
    maximum_foreign_material_percent: float
    maximum_damage_percent: float
    
    # Test weight requirements (for grains)
    minimum_test_weight_lbs: Optional[float] = None
    
    # Protein content (for wheat, soybeans)
    minimum_protein_percent: Optional[float] = None
    maximum_protein_percent: Optional[float] = None
    
    # Oil content (for soybeans)
    minimum_oil_percent: Optional[float] = None
    
    # Quality premiums and discounts
    grade_premiums: Dict[QualityGrade, float] = field(default_factory=dict)
    protein_premiums: Dict[str, float] = field(default_factory=dict)  # protein_range -> premium
    moisture_discounts: Dict[str, float] = field(default_factory=dict)  # moisture_range -> discount
    
    # Rejection criteria
    reject_if_exceeded: Dict[str, float] = field(default_factory=dict)

@dataclass
class DeliveryTerms:
    """Contract delivery terms and logistics"""
    delivery_location: str              # Elevator, farm, processing plant
    delivery_period: DeliveryPeriod
    delivery_window_start: Optional[float] = None  # Custom start date
    delivery_window_end: Optional[float] = None    # Custom end date
    
    # Logistics
    transportation_responsibility: str   # "seller", "buyer", "shared"
    loading_responsibility: str         # "seller", "buyer"
    weighing_location: str              # Where final weights are determined
    
    # Delivery flexibility
    delivery_schedule_flexibility: bool = True    # Can adjust delivery timing
    quantity_tolerance_percent: float = 5.0      # Allowable quantity variation
    
    # Performance requirements
    minimum_load_size_units: float = 1000.0     # Minimum delivery size
    maximum_delivery_rate_per_day: Optional[float] = None  # Rate limit
    notice_period_days: int = 7                  # Advance notice required

@dataclass
class ContractTerms:
    """Comprehensive contract terms and conditions"""
    # Pricing terms
    price_per_unit: Optional[float] = None       # Fixed price contracts
    basis_level: Optional[float] = None          # Basis contracts (local - futures)
    minimum_price: Optional[float] = None        # Minimum price contracts
    maximum_price: Optional[float] = None        # Price cap contracts
    premium_participation: float = 1.0           # Upside participation (0.0-1.0)
    
    # Price adjustments
    seasonal_price_adjustments: Dict[str, float] = field(default_factory=dict)
    volume_discounts: Dict[str, float] = field(default_factory=dict)
    loyalty_bonuses: Dict[str, float] = field(default_factory=dict)
    
    # Payment terms
    payment_schedule: str = "upon_delivery"      # "upon_delivery", "30_days", "60_days"
    advance_payment_percent: float = 0.0         # Upfront payment percentage
    retainage_percent: float = 0.0               # Amount held until contract completion
    
    # Performance guarantees
    performance_bond_required: bool = False
    performance_bond_amount: float = 0.0
    liquidated_damages_per_day: float = 0.0      # Daily penalty for late delivery
    
    # Risk allocation
    act_of_god_clause: bool = True               # Weather/natural disaster protection
    price_redetermination_triggers: List[str] = field(default_factory=list)
    force_majeure_provisions: List[str] = field(default_factory=list)

@dataclass
class Contract:
    """Comprehensive agricultural contract"""
    contract_id: str
    contract_type: ContractType
    status: ContractStatus
    
    # Parties
    buyer_entity_id: str                # Contract buyer
    seller_entity_id: str               # Contract seller (usually player)
    
    # Commodity details
    commodity_id: str
    contracted_quantity: float          # Total contracted amount
    delivered_quantity: float = 0.0     # Amount delivered so far
    
    # Contract specifications
    quality_spec: QualitySpecification
    delivery_terms: DeliveryTerms
    contract_terms: ContractTerms
    
    # Contract timeline
    contract_date: float                # When contract was signed
    effective_date: float               # When contract becomes active
    expiration_date: float              # When contract expires
    
    # Financial tracking
    total_contract_value: float = 0.0   # Total contract value
    delivered_value: float = 0.0        # Value of deliveries made
    remaining_value: float = 0.0        # Value of remaining deliveries
    
    # Performance tracking
    delivery_schedule: List[Dict[str, Any]] = field(default_factory=list)
    quality_test_results: List[Dict[str, Any]] = field(default_factory=list)
    payment_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Risk metrics
    price_risk_exposure: float = 0.0    # Unrealized gain/loss vs current market
    delivery_risk_score: float = 0.0    # Risk of non-delivery (0-100)
    counterparty_risk_score: float = 0.0 # Credit risk of counterparty

@dataclass
class ContractOffer:
    """Contract offer from potential buyers"""
    offer_id: str
    buyer_name: str
    buyer_entity_id: str
    
    # Offer details
    commodity_id: str
    quantity_offered: float
    contract_type: ContractType
    
    # Pricing
    offered_price: Optional[float] = None
    offered_basis: Optional[float] = None
    offered_minimum_price: Optional[float] = None
    price_participation: float = 1.0
    
    # Terms
    delivery_period: DeliveryPeriod
    quality_requirements: QualitySpecification = None
    payment_terms: str = "upon_delivery"
    
    # Offer validity
    offer_expires: float = 0.0
    quantity_flexibility: float = 0.1    # ±10% quantity flexibility
    
    # Market context
    current_market_price: float = 0.0
    basis_vs_market: float = 0.0
    premium_vs_market: float = 0.0

class AdvancedContractFramework:
    """Comprehensive contract management system"""
    
    def __init__(self):
        """Initialize the advanced contract framework"""
        self.system_name = "advanced_contract_framework"
        self.event_system = get_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_config_manager()
        self.time_manager = get_time_manager()
        self.pricing_system = get_dynamic_pricing_system()
        
        # Contract management
        self.active_contracts: Dict[str, Contract] = {}
        self.contract_offers: Dict[str, ContractOffer] = {}
        self.contract_templates: Dict[ContractType, Dict] = {}
        
        # Buyer/seller network
        self.registered_buyers: Dict[str, Dict] = {}
        self.market_participants: Dict[str, Dict] = {}
        
        # Contract performance tracking
        self.delivery_schedule: Dict[str, List] = {}
        self.payment_schedule: Dict[str, List] = {}
        
        # System state
        self.initialized = False
        
        print("Advanced Contract Framework initialized")
    
    def initialize(self) -> bool:
        """Initialize the advanced contract framework"""
        try:
            # Subscribe to events
            self.event_system.subscribe('time_advanced', self._handle_time_advanced)
            self.event_system.subscribe('crop_harvested', self._handle_crop_harvested)
            self.event_system.subscribe('price_updated', self._handle_price_updated)
            self.event_system.subscribe('delivery_completed', self._handle_delivery_completed)
            
            # Initialize contract templates
            self._initialize_contract_templates()
            
            # Load market participants (buyers)
            self._load_market_participants()
            
            # Generate initial contract offers
            self._generate_initial_offers()
            
            self.initialized = True
            
            # Emit initialization complete event
            self.event_system.emit('contract_framework_initialized', {
                'active_contracts': len(self.active_contracts),
                'available_offers': len(self.contract_offers),
                'registered_buyers': len(self.registered_buyers),
                'system_status': 'ready'
            }, priority=EventPriority.NORMAL)
            
            print("Advanced Contract Framework initialization complete")
            return True
            
        except Exception as e:
            print(f"Failed to initialize Advanced Contract Framework: {e}")
            return False
    
    def _initialize_contract_templates(self):
        """Initialize standard contract templates"""
        
        # Forward Contract Template
        self.contract_templates[ContractType.FORWARD_CONTRACT] = {
            'name': 'Forward Delivery Contract',
            'description': 'Fixed price contract for future delivery',
            'typical_price_premium': 0.05,  # $0.05 premium for price certainty
            'typical_delivery_window': 60,   # 60 days delivery window
            'quality_flexibility': 'standard',
            'default_payment_terms': 'upon_delivery'
        }
        
        # Basis Contract Template
        self.contract_templates[ContractType.BASIS_CONTRACT] = {
            'name': 'Basis Contract',
            'description': 'Price based on futures plus/minus basis',
            'typical_basis_range': (-0.30, 0.10),  # Typical basis range
            'basis_risk_sharing': True,
            'futures_month': 'nearby',
            'default_payment_terms': 'upon_delivery'
        }
        
        # Minimum Price Contract Template
        self.contract_templates[ContractType.MINIMUM_PRICE] = {
            'name': 'Minimum Price Contract',
            'description': 'Price floor with upside participation',
            'typical_floor_discount': 0.20,  # $0.20 below current price
            'participation_rate': 0.80,      # 80% of upside
            'premium_cost': 0.15,            # $0.15 premium cost
            'default_payment_terms': 'upon_delivery'
        }
        
        # Production Contract Template
        self.contract_templates[ContractType.PRODUCTION_CONTRACT] = {
            'name': 'Production Contract',
            'description': 'Comprehensive crop production agreement',
            'input_cost_sharing': 0.50,      # 50% input cost sharing
            'guaranteed_margin': 0.10,       # 10% guaranteed profit margin
            'yield_insurance': True,
            'default_payment_terms': '30_days'
        }
    
    def _load_market_participants(self):
        """Load market participants (grain elevators, processors, etc.)"""
        
        # Local grain elevators
        local_elevators = [
            {
                'buyer_id': 'prairie_grain_coop',
                'name': 'Prairie Grain Cooperative',
                'type': 'grain_elevator',
                'location': 'local',
                'credit_rating': 'A',
                'storage_capacity': 2000000,  # 2M bushels
                'specialties': ['corn', 'soybeans', 'wheat'],
                'typical_basis': {'corn': -0.15, 'soybeans': -0.20, 'wheat': -0.18},
                'contract_preferences': [ContractType.FORWARD_CONTRACT, ContractType.BASIS_CONTRACT],
                'seasonal_needs': {
                    'harvest': {'quantity_multiplier': 2.0, 'price_pressure': -0.05},
                    'spring': {'quantity_multiplier': 0.5, 'price_pressure': 0.03}
                }
            },
            {
                'buyer_id': 'heartland_grain',
                'name': 'Heartland Grain & Feed',
                'type': 'grain_elevator',
                'location': 'regional',
                'credit_rating': 'A-',
                'storage_capacity': 1500000,
                'specialties': ['corn', 'wheat'],
                'typical_basis': {'corn': -0.12, 'wheat': -0.15},
                'contract_preferences': [ContractType.FORWARD_CONTRACT, ContractType.CASH_SALE],
                'seasonal_needs': {
                    'harvest': {'quantity_multiplier': 1.8, 'price_pressure': -0.03},
                    'winter': {'quantity_multiplier': 0.7, 'price_pressure': 0.02}
                }
            }
        ]
        
        # Processing companies
        processors = [
            {
                'buyer_id': 'midwest_ethanol',
                'name': 'Midwest Ethanol Solutions',
                'type': 'ethanol_plant',
                'location': 'regional',
                'credit_rating': 'BBB+',
                'processing_capacity': 50000000,  # 50M gallons/year
                'specialties': ['corn'],
                'typical_basis': {'corn': 0.05},  # Premium for processing
                'contract_preferences': [ContractType.PRODUCTION_CONTRACT, ContractType.FORWARD_CONTRACT],
                'seasonal_needs': {
                    'year_round': {'quantity_multiplier': 1.0, 'price_pressure': 0.00}
                },
                'quality_premiums': {
                    'US_Grade_1': 0.03,
                    'low_moisture': 0.02
                }
            },
            {
                'buyer_id': 'soy_processing_inc',
                'name': 'Soy Processing Inc.',
                'type': 'soybean_crusher',
                'location': 'regional',
                'credit_rating': 'A',
                'processing_capacity': 30000000,  # 30M bushels/year
                'specialties': ['soybeans'],
                'typical_basis': {'soybeans': 0.10},
                'contract_preferences': [ContractType.BASIS_CONTRACT, ContractType.MINIMUM_PRICE],
                'seasonal_needs': {
                    'year_round': {'quantity_multiplier': 1.0, 'price_pressure': 0.00}
                },
                'quality_premiums': {
                    'high_protein': 0.15,
                    'high_oil': 0.10
                }
            }
        ]
        
        # Export facilities
        exporters = [
            {
                'buyer_id': 'global_grain_export',
                'name': 'Global Grain Export Terminal',
                'type': 'export_terminal',
                'location': 'international',
                'credit_rating': 'A+',
                'export_capacity': 100000000,  # 100M bushels/year
                'specialties': ['corn', 'soybeans', 'wheat'],
                'typical_basis': {'corn': 0.20, 'soybeans': 0.25, 'wheat': 0.30},
                'contract_preferences': [ContractType.FORWARD_CONTRACT, ContractType.BASIS_CONTRACT],
                'seasonal_needs': {
                    'harvest': {'quantity_multiplier': 1.5, 'price_pressure': 0.05},
                    'spring': {'quantity_multiplier': 0.8, 'price_pressure': -0.02}
                },
                'quality_requirements': 'export_grade'
            }
        ]
        
        # Combine all participants
        all_participants = local_elevators + processors + exporters
        
        for participant in all_participants:
            self.registered_buyers[participant['buyer_id']] = participant
            self.market_participants[participant['buyer_id']] = participant
        
        print(f"Loaded {len(all_participants)} market participants")
    
    def _generate_initial_offers(self):
        """Generate initial contract offers from market participants"""
        current_time = time.time()
        
        for buyer_id, buyer_info in self.registered_buyers.items():
            # Generate 2-4 offers per buyer
            num_offers = 2 + int(time.time()) % 3  # 2-4 offers
            
            for i in range(num_offers):
                offer = self._create_contract_offer(buyer_id, buyer_info)
                if offer:
                    self.contract_offers[offer.offer_id] = offer
        
        print(f"Generated {len(self.contract_offers)} initial contract offers")
    
    def _create_contract_offer(self, buyer_id: str, buyer_info: Dict[str, Any]) -> Optional[ContractOffer]:
        """Create a contract offer from a market participant"""
        import random
        
        # Select commodity from buyer's specialties
        commodities = buyer_info.get('specialties', ['corn'])
        commodity_id = random.choice(commodities)
        
        # Get current market price
        current_price = self.pricing_system.get_current_price(commodity_id, MarketRegion.LOCAL)
        if not current_price:
            return None
        
        # Select contract type based on preferences
        preferred_types = buyer_info.get('contract_preferences', [ContractType.CASH_SALE])
        contract_type = random.choice(preferred_types)
        
        # Calculate offer terms based on contract type and buyer characteristics
        offer_price = None
        offer_basis = None
        offer_minimum = None
        
        typical_basis = buyer_info.get('typical_basis', {}).get(commodity_id, 0.0)
        
        if contract_type == ContractType.FORWARD_CONTRACT:
            # Forward contract: fixed price with small premium/discount
            price_adjustment = random.gauss(0.05, 0.10)  # Small premium on average
            offer_price = current_price + typical_basis + price_adjustment
        
        elif contract_type == ContractType.BASIS_CONTRACT:
            # Basis contract: basis relative to futures
            basis_variation = random.gauss(0.0, 0.05)  # Variation around typical basis
            offer_basis = typical_basis + basis_variation
        
        elif contract_type == ContractType.MINIMUM_PRICE:
            # Minimum price: floor with upside participation
            floor_discount = random.uniform(0.15, 0.30)
            offer_minimum = current_price - floor_discount
        
        # Quantity offered (based on buyer capacity and seasonal needs)
        base_quantity = random.randint(5000, 50000)  # 5K to 50K bushels
        
        # Adjust for seasonal needs
        current_season = self._get_current_season()
        seasonal_factor = buyer_info.get('seasonal_needs', {}).get(current_season, {}).get('quantity_multiplier', 1.0)
        quantity_offered = base_quantity * seasonal_factor
        
        # Create quality specification
        quality_spec = self._create_quality_specification(commodity_id, buyer_info)
        
        # Delivery period
        delivery_periods = [DeliveryPeriod.HARVEST, DeliveryPeriod.POST_HARVEST, DeliveryPeriod.WINTER]
        delivery_period = random.choice(delivery_periods)
        
        # Create offer
        offer = ContractOffer(
            offer_id=str(uuid.uuid4()),
            buyer_name=buyer_info['name'],
            buyer_entity_id=buyer_id,
            commodity_id=commodity_id,
            quantity_offered=quantity_offered,
            contract_type=contract_type,
            offered_price=offer_price,
            offered_basis=offer_basis,
            offered_minimum_price=offer_minimum,
            delivery_period=delivery_period,
            quality_requirements=quality_spec,
            offer_expires=time.time() + (30 * 24 * 3600),  # 30 days
            current_market_price=current_price,
            basis_vs_market=typical_basis,
            premium_vs_market=offer_price - current_price if offer_price else 0.0
        )
        
        return offer
    
    def _create_quality_specification(self, commodity_id: str, buyer_info: Dict[str, Any]) -> QualitySpecification:
        """Create quality specification based on buyer requirements"""
        
        # Base quality specs by commodity
        base_specs = {
            'corn': {
                'minimum_grade': QualityGrade.US_GRADE_2,
                'maximum_moisture_percent': 15.5,
                'maximum_foreign_material_percent': 2.0,
                'maximum_damage_percent': 3.0,
                'minimum_test_weight_lbs': 56.0
            },
            'soybeans': {
                'minimum_grade': QualityGrade.US_GRADE_2,
                'maximum_moisture_percent': 13.0,
                'maximum_foreign_material_percent': 2.0,
                'maximum_damage_percent': 2.0,
                'minimum_protein_percent': 34.0,
                'minimum_oil_percent': 18.5
            },
            'wheat': {
                'minimum_grade': QualityGrade.US_GRADE_2,
                'maximum_moisture_percent': 14.0,
                'maximum_foreign_material_percent': 2.0,
                'maximum_damage_percent': 2.0,
                'minimum_test_weight_lbs': 60.0,
                'minimum_protein_percent': 11.5
            }
        }
        
        spec_data = base_specs.get(commodity_id, base_specs['corn'])
        
        # Adjust for buyer type
        if buyer_info.get('type') == 'export_terminal':
            # Export facilities have stricter requirements
            if 'maximum_moisture_percent' in spec_data:
                spec_data['maximum_moisture_percent'] -= 0.5
            if 'minimum_grade' in spec_data:
                spec_data['minimum_grade'] = QualityGrade.US_GRADE_1
        
        quality_spec = QualitySpecification(
            commodity_id=commodity_id,
            **spec_data
        )
        
        # Add quality premiums from buyer info
        quality_premiums = buyer_info.get('quality_premiums', {})
        for premium_type, premium_value in quality_premiums.items():
            if premium_type == 'US_Grade_1':
                quality_spec.grade_premiums[QualityGrade.US_GRADE_1] = premium_value
            elif premium_type == 'high_protein':
                quality_spec.protein_premiums['high'] = premium_value
        
        return quality_spec
    
    def _get_current_season(self) -> str:
        """Determine current agricultural season"""
        current_month = datetime.now().month
        
        if current_month in [12, 1, 2]:
            return 'winter'
        elif current_month in [3, 4, 5]:
            return 'spring'
        elif current_month in [6, 7, 8]:
            return 'summer'
        else:  # [9, 10, 11]
            return 'harvest'
    
    def accept_contract_offer(self, offer_id: str, player_entity_id: str) -> Optional[Contract]:
        """Accept a contract offer and create active contract"""
        if offer_id not in self.contract_offers:
            print(f"Contract offer {offer_id} not found")
            return None
        
        offer = self.contract_offers[offer_id]
        
        # Check if offer is still valid
        if time.time() > offer.offer_expires:
            print("Contract offer has expired")
            return None
        
        # Create contract from offer
        contract = self._create_contract_from_offer(offer, player_entity_id)
        
        if contract:
            # Add to active contracts
            self.active_contracts[contract.contract_id] = contract
            
            # Remove accepted offer
            del self.contract_offers[offer_id]
            
            # Emit contract acceptance event
            self.event_system.emit('contract_accepted', {
                'contract_id': contract.contract_id,
                'buyer_name': offer.buyer_name,
                'commodity_id': contract.commodity_id,
                'quantity': contract.contracted_quantity,
                'contract_type': contract.contract_type.value,
                'estimated_value': contract.total_contract_value
            }, priority=EventPriority.NORMAL)
            
            print(f"Contract accepted: {contract.contract_id}")
        
        return contract
    
    def _create_contract_from_offer(self, offer: ContractOffer, seller_entity_id: str) -> Contract:
        """Create a contract from an accepted offer"""
        current_time = time.time()
        
        # Create contract terms
        contract_terms = ContractTerms(
            price_per_unit=offer.offered_price,
            basis_level=offer.offered_basis,
            minimum_price=offer.offered_minimum_price,
            premium_participation=offer.price_participation
        )
        
        # Create delivery terms
        delivery_terms = DeliveryTerms(
            delivery_location=f"{offer.buyer_name} Facility",
            delivery_period=offer.delivery_period
        )
        
        # Set delivery window based on delivery period
        if offer.delivery_period == DeliveryPeriod.HARVEST:
            delivery_terms.delivery_window_start = current_time + (60 * 24 * 3600)  # 60 days
            delivery_terms.delivery_window_end = current_time + (120 * 24 * 3600)   # 120 days
        elif offer.delivery_period == DeliveryPeriod.POST_HARVEST:
            delivery_terms.delivery_window_start = current_time + (120 * 24 * 3600) # 120 days
            delivery_terms.delivery_window_end = current_time + (180 * 24 * 3600)   # 180 days
        elif offer.delivery_period == DeliveryPeriod.WINTER:
            delivery_terms.delivery_window_start = current_time + (150 * 24 * 3600) # 150 days
            delivery_terms.delivery_window_end = current_time + (240 * 24 * 3600)   # 240 days
        
        # Calculate contract value estimate
        estimated_price = offer.offered_price or offer.current_market_price
        total_value = offer.quantity_offered * estimated_price
        
        # Create contract
        contract = Contract(
            contract_id=str(uuid.uuid4()),
            contract_type=offer.contract_type,
            status=ContractStatus.ACTIVE,
            buyer_entity_id=offer.buyer_entity_id,
            seller_entity_id=seller_entity_id,
            commodity_id=offer.commodity_id,
            contracted_quantity=offer.quantity_offered,
            quality_spec=offer.quality_requirements,
            delivery_terms=delivery_terms,
            contract_terms=contract_terms,
            contract_date=current_time,
            effective_date=current_time,
            expiration_date=delivery_terms.delivery_window_end or (current_time + 365 * 24 * 3600),
            total_contract_value=total_value,
            remaining_value=total_value
        )
        
        return contract
    
    def deliver_against_contract(self, contract_id: str, delivery_quantity: float, 
                                quality_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process a delivery against a contract"""
        if contract_id not in self.active_contracts:
            return {'success': False, 'error': 'Contract not found'}
        
        contract = self.active_contracts[contract_id]
        
        if contract.status != ContractStatus.ACTIVE:
            return {'success': False, 'error': f'Contract status is {contract.status.value}'}
        
        # Check delivery window
        current_time = time.time()
        if (contract.delivery_terms.delivery_window_start and 
            current_time < contract.delivery_terms.delivery_window_start):
            return {'success': False, 'error': 'Delivery window not yet open'}
        
        if (contract.delivery_terms.delivery_window_end and 
            current_time > contract.delivery_terms.delivery_window_end):
            return {'success': False, 'error': 'Delivery window has closed'}
        
        # Check quantity limits
        remaining_quantity = contract.contracted_quantity - contract.delivered_quantity
        if delivery_quantity > remaining_quantity:
            delivery_quantity = remaining_quantity  # Limit to remaining quantity
        
        # Evaluate quality and calculate price adjustments
        price_per_unit, quality_adjustments = self._calculate_delivery_price(contract, quality_results)
        
        # Calculate delivery value
        delivery_value = delivery_quantity * price_per_unit
        
        # Update contract
        contract.delivered_quantity += delivery_quantity
        contract.delivered_value += delivery_value
        contract.remaining_value = contract.total_contract_value - contract.delivered_value
        
        # Update contract status
        if contract.delivered_quantity >= contract.contracted_quantity:
            contract.status = ContractStatus.FULFILLED
        else:
            contract.status = ContractStatus.PARTIALLY_FULFILLED
        
        # Record delivery
        delivery_record = {
            'timestamp': current_time,
            'quantity': delivery_quantity,
            'price_per_unit': price_per_unit,
            'total_value': delivery_value,
            'quality_results': quality_results,
            'quality_adjustments': quality_adjustments
        }
        
        contract.delivery_schedule.append(delivery_record)
        contract.quality_test_results.append(quality_results)
        
        # Emit delivery event
        self.event_system.emit('contract_delivery_completed', {
            'contract_id': contract_id,
            'delivery_quantity': delivery_quantity,
            'delivery_value': delivery_value,
            'contract_completion_percent': (contract.delivered_quantity / contract.contracted_quantity) * 100,
            'quality_grade': quality_results.get('grade', 'unknown')
        }, priority=EventPriority.NORMAL)
        
        return {
            'success': True,
            'delivery_quantity': delivery_quantity,
            'price_per_unit': price_per_unit,
            'delivery_value': delivery_value,
            'quality_adjustments': quality_adjustments,
            'contract_status': contract.status.value,
            'remaining_quantity': contract.contracted_quantity - contract.delivered_quantity
        }
    
    def _calculate_delivery_price(self, contract: Contract, quality_results: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Calculate delivery price including quality adjustments"""
        base_price = 0.0
        quality_adjustments = {}
        
        # Determine base price based on contract type
        if contract.contract_type == ContractType.FORWARD_CONTRACT:
            base_price = contract.contract_terms.price_per_unit
        
        elif contract.contract_type == ContractType.BASIS_CONTRACT:
            # Get current futures price (simplified - use current market price)
            current_market_price = self.pricing_system.get_current_price(contract.commodity_id, MarketRegion.NATIONAL)
            base_price = current_market_price + contract.contract_terms.basis_level
        
        elif contract.contract_type == ContractType.MINIMUM_PRICE:
            current_market_price = self.pricing_system.get_current_price(contract.commodity_id, MarketRegion.LOCAL)
            minimum_price = contract.contract_terms.minimum_price
            market_participation = current_market_price * contract.contract_terms.premium_participation
            base_price = max(minimum_price, market_participation)
        
        else:
            # Default to current market price
            base_price = self.pricing_system.get_current_price(contract.commodity_id, MarketRegion.LOCAL) or 5.0
        
        # Apply quality adjustments
        quality_spec = contract.quality_spec
        
        # Grade premium/discount
        delivered_grade = quality_results.get('grade', QualityGrade.US_GRADE_2)
        if isinstance(delivered_grade, str):
            # Convert string to enum
            try:
                delivered_grade = QualityGrade(delivered_grade)
            except ValueError:
                delivered_grade = QualityGrade.US_GRADE_2
        
        grade_adjustment = quality_spec.grade_premiums.get(delivered_grade, 0.0)
        quality_adjustments['grade_adjustment'] = grade_adjustment
        
        # Moisture adjustment
        delivered_moisture = quality_results.get('moisture_percent', 14.0)
        if delivered_moisture > quality_spec.maximum_moisture_percent:
            excess_moisture = delivered_moisture - quality_spec.maximum_moisture_percent
            moisture_discount = excess_moisture * 0.05  # $0.05 per point over
            quality_adjustments['moisture_discount'] = -moisture_discount
        
        # Damage adjustment
        delivered_damage = quality_results.get('damage_percent', 1.0)
        if delivered_damage > quality_spec.maximum_damage_percent:
            excess_damage = delivered_damage - quality_spec.maximum_damage_percent
            damage_discount = excess_damage * 0.02  # $0.02 per point over
            quality_adjustments['damage_discount'] = -damage_discount
        
        # Calculate final price
        total_adjustment = sum(quality_adjustments.values())
        final_price = base_price + total_adjustment
        
        return final_price, quality_adjustments
    
    def get_available_offers(self, commodity_filter: Optional[str] = None) -> List[ContractOffer]:
        """Get available contract offers, optionally filtered by commodity"""
        current_time = time.time()
        available_offers = []
        
        for offer in self.contract_offers.values():
            # Check if offer is still valid
            if offer.offer_expires > current_time:
                # Apply commodity filter if specified
                if commodity_filter is None or offer.commodity_id == commodity_filter:
                    available_offers.append(offer)
        
        # Sort by best terms (highest price/lowest basis)
        def sort_key(offer):
            if offer.offered_price:
                return -offer.offered_price  # Higher price first
            elif offer.offered_basis:
                return -offer.offered_basis   # Higher basis first
            return 0
        
        available_offers.sort(key=sort_key)
        
        return available_offers
    
    def get_contract_performance_summary(self, entity_id: str) -> Dict[str, Any]:
        """Get contract performance summary for an entity"""
        entity_contracts = [contract for contract in self.active_contracts.values() 
                           if contract.seller_entity_id == entity_id]
        
        total_contracts = len(entity_contracts)
        fulfilled_contracts = len([c for c in entity_contracts if c.status == ContractStatus.FULFILLED])
        active_contracts = len([c for c in entity_contracts if c.status == ContractStatus.ACTIVE])
        
        total_value = sum(c.total_contract_value for c in entity_contracts)
        delivered_value = sum(c.delivered_value for c in entity_contracts)
        
        # Calculate average delivery performance
        delivery_performance = []
        for contract in entity_contracts:
            if contract.contracted_quantity > 0:
                completion_rate = contract.delivered_quantity / contract.contracted_quantity
                delivery_performance.append(completion_rate)
        
        avg_delivery_rate = sum(delivery_performance) / len(delivery_performance) if delivery_performance else 0.0
        
        return {
            'total_contracts': total_contracts,
            'active_contracts': active_contracts,
            'fulfilled_contracts': fulfilled_contracts,
            'fulfillment_rate': fulfilled_contracts / total_contracts if total_contracts > 0 else 0.0,
            'total_contract_value': total_value,
            'delivered_value': delivered_value,
            'delivery_completion_rate': avg_delivery_rate,
            'contracts_by_commodity': self._get_contracts_by_commodity(entity_contracts),
            'contracts_by_type': self._get_contracts_by_type(entity_contracts)
        }
    
    def _get_contracts_by_commodity(self, contracts: List[Contract]) -> Dict[str, int]:
        """Group contracts by commodity"""
        commodity_counts = {}
        for contract in contracts:
            commodity = contract.commodity_id
            commodity_counts[commodity] = commodity_counts.get(commodity, 0) + 1
        return commodity_counts
    
    def _get_contracts_by_type(self, contracts: List[Contract]) -> Dict[str, int]:
        """Group contracts by type"""
        type_counts = {}
        for contract in contracts:
            contract_type = contract.contract_type.value
            type_counts[contract_type] = type_counts.get(contract_type, 0) + 1
        return type_counts
    
    def update(self, delta_time: float):
        """Update contract framework"""
        if not self.initialized:
            return
        
        current_time = time.time()
        
        # Update contract price risk exposure
        self._update_price_risk_exposure()
        
        # Remove expired offers
        self._remove_expired_offers()
        
        # Generate new offers periodically
        if int(current_time) % 3600 == 0:  # Every hour
            self._generate_periodic_offers()
        
        # Check for contract deadlines and delivery windows
        self._check_contract_deadlines()
    
    def _update_price_risk_exposure(self):
        """Update price risk exposure for all contracts"""
        for contract in self.active_contracts.values():
            if contract.status not in [ContractStatus.ACTIVE, ContractStatus.PARTIALLY_FULFILLED]:
                continue
            
            current_market_price = self.pricing_system.get_current_price(contract.commodity_id, MarketRegion.LOCAL)
            if not current_market_price:
                continue
            
            remaining_quantity = contract.contracted_quantity - contract.delivered_quantity
            
            if contract.contract_type == ContractType.FORWARD_CONTRACT:
                # Risk is difference between contract price and current market
                price_difference = current_market_price - contract.contract_terms.price_per_unit
                contract.price_risk_exposure = price_difference * remaining_quantity
            
            elif contract.contract_type == ContractType.MINIMUM_PRICE:
                # Risk is limited by minimum price floor
                minimum_price = contract.contract_terms.minimum_price
                if current_market_price > minimum_price:
                    # Opportunity cost of not selling at full market price
                    participation_rate = contract.contract_terms.premium_participation
                    foregone_income = (current_market_price - minimum_price) * (1 - participation_rate)
                    contract.price_risk_exposure = -foregone_income * remaining_quantity
                else:
                    # Benefiting from price floor
                    contract.price_risk_exposure = (minimum_price - current_market_price) * remaining_quantity
    
    def _remove_expired_offers(self):
        """Remove expired contract offers"""
        current_time = time.time()
        expired_offers = [offer_id for offer_id, offer in self.contract_offers.items() 
                         if offer.offer_expires <= current_time]
        
        for offer_id in expired_offers:
            del self.contract_offers[offer_id]
    
    def _generate_periodic_offers(self):
        """Generate new contract offers periodically"""
        # Limit total number of active offers
        if len(self.contract_offers) >= 20:
            return
        
        # Select random buyers to generate new offers
        import random
        active_buyers = random.sample(list(self.registered_buyers.items()), 
                                     min(3, len(self.registered_buyers)))
        
        for buyer_id, buyer_info in active_buyers:
            new_offer = self._create_contract_offer(buyer_id, buyer_info)
            if new_offer:
                self.contract_offers[new_offer.offer_id] = new_offer
    
    def _check_contract_deadlines(self):
        """Check for approaching contract deadlines"""
        current_time = time.time()
        warning_threshold = 7 * 24 * 3600  # 7 days
        
        for contract in self.active_contracts.values():
            if contract.status != ContractStatus.ACTIVE:
                continue
            
            # Check delivery window deadlines
            if (contract.delivery_terms.delivery_window_end and 
                contract.delivery_terms.delivery_window_end - current_time < warning_threshold):
                
                # Emit deadline warning
                self.event_system.emit('contract_deadline_warning', {
                    'contract_id': contract.contract_id,
                    'days_remaining': (contract.delivery_terms.delivery_window_end - current_time) / (24 * 3600),
                    'remaining_quantity': contract.contracted_quantity - contract.delivered_quantity
                }, priority=EventPriority.HIGH)
    
    def _handle_time_advanced(self, event_data: Dict[str, Any]):
        """Handle time advancement events"""
        # Update seasonal factors, refresh offers, etc.
        pass
    
    def _handle_crop_harvested(self, event_data: Dict[str, Any]):
        """Handle crop harvest events"""
        crop_type = event_data.get('crop_type', '')
        quantity = event_data.get('quantity_harvested', 0.0)
        quality = event_data.get('quality_results', {})
        
        # Check if this harvest can fulfill any active contracts
        for contract in self.active_contracts.values():
            if (contract.commodity_id == crop_type and 
                contract.status == ContractStatus.ACTIVE and
                contract.delivered_quantity < contract.contracted_quantity):
                
                # Emit potential delivery opportunity
                self.event_system.emit('contract_delivery_opportunity', {
                    'contract_id': contract.contract_id,
                    'available_quantity': quantity,
                    'crop_type': crop_type,
                    'quality_results': quality
                }, priority=EventPriority.NORMAL)
    
    def _handle_price_updated(self, event_data: Dict[str, Any]):
        """Handle price update events"""
        # Update contract risk exposures when prices change
        self._update_price_risk_exposure()
    
    def _handle_delivery_completed(self, event_data: Dict[str, Any]):
        """Handle delivery completion events"""
        # Process contract delivery settlements
        pass
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get contract framework system statistics"""
        active_count = len([c for c in self.active_contracts.values() if c.status == ContractStatus.ACTIVE])
        fulfilled_count = len([c for c in self.active_contracts.values() if c.status == ContractStatus.FULFILLED])
        
        total_value = sum(c.total_contract_value for c in self.active_contracts.values())
        delivered_value = sum(c.delivered_value for c in self.active_contracts.values())
        
        return {
            'total_contracts': len(self.active_contracts),
            'active_contracts': active_count,
            'fulfilled_contracts': fulfilled_count,
            'available_offers': len(self.contract_offers),
            'registered_buyers': len(self.registered_buyers),
            'total_contract_value': total_value,
            'delivered_value': delivered_value,
            'delivery_completion_rate': delivered_value / total_value if total_value > 0 else 0.0
        }

# Global advanced contract framework instance
_global_contract_framework: Optional[AdvancedContractFramework] = None

def get_advanced_contract_framework() -> AdvancedContractFramework:
    """Get the global advanced contract framework instance"""
    global _global_contract_framework
    if _global_contract_framework is None:
        _global_contract_framework = AdvancedContractFramework()
        _global_contract_framework.initialize()
    return _global_contract_framework

def initialize_advanced_contract_framework() -> AdvancedContractFramework:
    """Initialize the global advanced contract framework"""
    global _global_contract_framework
    _global_contract_framework = AdvancedContractFramework()
    _global_contract_framework.initialize()
    return _global_contract_framework

# Convenience functions
def get_available_contract_offers(commodity_filter: Optional[str] = None) -> List[ContractOffer]:
    """Convenience function to get available contract offers"""
    return get_advanced_contract_framework().get_available_offers(commodity_filter)

def accept_contract_offer(offer_id: str, seller_entity_id: str) -> Optional[Contract]:
    """Convenience function to accept a contract offer"""
    return get_advanced_contract_framework().accept_contract_offer(offer_id, seller_entity_id)

def deliver_to_contract(contract_id: str, quantity: float, quality_results: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to deliver against a contract"""
    return get_advanced_contract_framework().deliver_against_contract(contract_id, quantity, quality_results)