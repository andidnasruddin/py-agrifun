"""
Supply Chain Integration System - Comprehensive Supply Chain Management for AgriFun Agricultural Game

This system provides realistic supply chain management including input purchasing (seeds, fertilizers, 
chemicals), equipment procurement, logistics coordination, and supply chain optimization. It helps 
players understand agricultural supply chains and make strategic procurement decisions.

Key Features:
- Input Purchasing (Seeds, Fertilizers, Pesticides, Fuel)
- Equipment Procurement and Leasing
- Supplier Relationship Management
- Logistics and Transportation Coordination
- Inventory Management and Just-in-Time Delivery
- Supply Chain Risk Assessment and Mitigation
- Cost Optimization and Bulk Purchasing

Integration:
- Economic System: Cost analysis and financial planning
- Risk Management: Supply chain risk assessment
- Equipment System: Equipment procurement and maintenance
- Crop Growth System: Input requirements and timing
- Contract System: Supply contracts and delivery agreements

Author: Agricultural Simulation Development Team
Version: 1.0.0 - Comprehensive Supply Chain Implementation
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

class InputCategory(Enum):
    """Categories of agricultural inputs"""
    SEEDS = "seeds"
    FERTILIZERS = "fertilizers"
    PESTICIDES = "pesticides"
    FUEL = "fuel"
    EQUIPMENT = "equipment"
    SERVICES = "services"

class SupplierType(Enum):
    """Types of agricultural suppliers"""
    SEED_COMPANY = "seed_company"
    FERTILIZER_DEALER = "fertilizer_dealer"
    CHEMICAL_SUPPLIER = "chemical_supplier"
    FUEL_DISTRIBUTOR = "fuel_distributor"
    EQUIPMENT_DEALER = "equipment_dealer"
    SERVICE_PROVIDER = "service_provider"
    COOPERATIVE = "cooperative"

class DeliveryMethod(Enum):
    """Methods of product delivery"""
    PICKUP = "pickup"
    FARM_DELIVERY = "farm_delivery"
    BULK_DELIVERY = "bulk_delivery"
    PIPELINE = "pipeline"
    RAIL = "rail"
    TRUCK = "truck"

class PaymentTerm(Enum):
    """Payment terms for purchases"""
    CASH_ON_DELIVERY = "cod"
    NET_30 = "net_30"
    NET_60 = "net_60"
    SEASONAL_PAY = "seasonal_pay"    # Pay after harvest
    CREDIT_LINE = "credit_line"

class InventoryStatus(Enum):
    """Inventory item status"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    ON_ORDER = "on_order"
    BACKORDERED = "backorder"

@dataclass
class InputProduct:
    """Agricultural input product definition"""
    product_id: str
    product_name: str
    category: InputCategory
    brand: str
    package_size: float  # Units (lbs, gallons, etc.)
    package_unit: str
    cost_per_package: float
    cost_per_unit: float
    active_ingredients: Dict[str, float] = field(default_factory=dict)
    application_rate: Optional[float] = None  # Per acre
    application_unit: str = "lbs/acre"
    shelf_life_days: Optional[int] = None
    storage_requirements: List[str] = field(default_factory=list)
    regulatory_restrictions: List[str] = field(default_factory=list)

@dataclass
class Supplier:
    """Agricultural supplier information"""
    supplier_id: str
    company_name: str
    supplier_type: SupplierType
    contact_info: Dict[str, str] = field(default_factory=dict)
    location: Dict[str, float] = field(default_factory=dict)  # lat, lon, distance
    products_offered: List[str] = field(default_factory=list)
    payment_terms: List[PaymentTerm] = field(default_factory=list)
    delivery_methods: List[DeliveryMethod] = field(default_factory=list)
    minimum_order: float = 0.0
    volume_discounts: Dict[float, float] = field(default_factory=dict)  # volume: discount%
    reliability_score: float = 0.85  # 0.0 to 1.0
    credit_terms: Dict[str, Any] = field(default_factory=dict)
    seasonal_availability: Dict[str, bool] = field(default_factory=dict)

@dataclass
class PurchaseOrder:
    """Purchase order for agricultural inputs"""
    order_id: str
    supplier_id: str
    order_date: datetime
    requested_delivery_date: datetime
    farm_id: str
    order_items: List[Dict[str, Any]] = field(default_factory=list)
    subtotal: float = 0.0
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    delivery_fee: float = 0.0
    total_amount: float = 0.0
    payment_term: PaymentTerm = PaymentTerm.NET_30
    delivery_method: DeliveryMethod = DeliveryMethod.FARM_DELIVERY
    delivery_address: str = ""
    special_instructions: str = ""
    order_status: str = "pending"
    tracking_number: Optional[str] = None

@dataclass
class InventoryItem:
    """Inventory item tracking"""
    item_id: str
    product_id: str
    quantity_on_hand: float
    unit_cost: float
    total_value: float
    expiration_date: Optional[datetime] = None
    storage_location: str = "main_storage"
    lot_number: Optional[str] = None
    supplier_id: str = ""
    received_date: datetime = field(default_factory=datetime.now)
    status: InventoryStatus = InventoryStatus.IN_STOCK
    reserved_quantity: float = 0.0  # Reserved for planned activities

@dataclass
class DeliverySchedule:
    """Delivery scheduling and tracking"""
    delivery_id: str
    order_id: str
    supplier_id: str
    farm_id: str
    scheduled_date: datetime
    delivery_window_start: datetime
    delivery_window_end: datetime
    delivery_method: DeliveryMethod
    delivery_status: str = "scheduled"
    driver_contact: Optional[str] = None
    vehicle_info: Optional[str] = None
    estimated_arrival: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    delivery_notes: str = ""

@dataclass
class SupplyChainMetrics:
    """Supply chain performance metrics"""
    farm_id: str
    total_procurement_spend: float = 0.0
    average_cost_per_acre: float = 0.0
    supplier_performance_scores: Dict[str, float] = field(default_factory=dict)
    inventory_turnover_ratio: float = 0.0
    stockout_incidents: int = 0
    on_time_delivery_rate: float = 0.0
    cost_savings_from_optimization: float = 0.0
    days_inventory_outstanding: float = 0.0
    procurement_cycle_time: float = 0.0

@dataclass
class SupplyChainPlan:
    """Strategic supply chain planning"""
    farm_id: str
    planning_year: int
    crop_plan: Dict[str, float] = field(default_factory=dict)  # crop: acres
    input_requirements: Dict[str, Dict[str, float]] = field(default_factory=dict)  # crop: {input: quantity}
    preferred_suppliers: Dict[str, List[str]] = field(default_factory=dict)  # category: [supplier_ids]
    bulk_purchase_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    delivery_schedule_preferences: Dict[str, str] = field(default_factory=dict)
    budget_allocations: Dict[str, float] = field(default_factory=dict)
    risk_mitigation_strategies: List[str] = field(default_factory=list)

class SupplyChainSystem(System):
    """
    Comprehensive Supply Chain Integration System for Agricultural Operations
    
    This system provides realistic supply chain management including:
    - Input procurement from multiple suppliers with competitive pricing
    - Inventory management with expiration tracking and storage optimization
    - Delivery scheduling and logistics coordination
    - Supplier relationship management and performance tracking
    - Cost optimization through bulk purchasing and timing strategies
    - Supply chain risk assessment and mitigation planning
    """
    
    def __init__(self):
        """Initialize the Supply Chain System"""
        super().__init__()
        
        # Core system references
        self.event_system = None
        self.config_manager = None
        self.content_registry = None
        
        # Supply chain data
        self.input_products: Dict[str, InputProduct] = {}
        self.suppliers: Dict[str, Supplier] = {}
        self.purchase_orders: Dict[str, PurchaseOrder] = {}
        self.inventory_items: Dict[str, InventoryItem] = {}
        self.delivery_schedules: Dict[str, DeliverySchedule] = {}
        self.supply_chain_plans: Dict[str, SupplyChainPlan] = {}
        
        # Performance tracking
        self.metrics: Dict[str, SupplyChainMetrics] = {}
        
        # Market data
        self.market_prices: Dict[str, Dict[str, float]] = {}  # product_id: {supplier_id: price}
        self.seasonal_price_patterns: Dict[str, Dict[str, float]] = {}
        
        # System parameters
        self.system_parameters = {
            'delivery_lead_times': {
                DeliveryMethod.PICKUP: 0,
                DeliveryMethod.FARM_DELIVERY: 2,
                DeliveryMethod.BULK_DELIVERY: 5,
                DeliveryMethod.RAIL: 10,
                DeliveryMethod.PIPELINE: 1
            },
            'inventory_thresholds': {
                'reorder_point_days': 30,
                'safety_stock_days': 14,
                'max_inventory_days': 120
            },
            'cost_parameters': {
                'delivery_cost_per_mile': 2.5,
                'bulk_delivery_minimum': 1000.0,
                'rush_delivery_surcharge': 0.15
            }
        }
        
        self.is_initialized = False
    
    def initialize(self, event_system: EventSystem, config_manager: ConfigurationManager, 
                  content_registry: ContentRegistry) -> bool:
        """Initialize the Supply Chain System with required dependencies"""
        try:
            self.event_system = event_system
            self.config_manager = config_manager
            self.content_registry = content_registry
            
            # Load supply chain configuration
            self._load_configuration()
            
            # Initialize product catalog and supplier database
            self._initialize_product_catalog()
            self._initialize_supplier_database()
            
            # Register event handlers
            self._register_event_handlers()
            
            # Load market price data
            self._load_market_data()
            
            self.is_initialized = True
            
            # Emit initialization event
            self.event_system.emit_event("supply_chain_initialized", {
                "system": "supply_chain",
                "status": "ready",
                "products_loaded": len(self.input_products),
                "suppliers_loaded": len(self.suppliers),
                "timestamp": datetime.now()
            })
            
            return True
            
        except Exception as e:
            print(f"Error initializing Supply Chain System: {e}")
            return False
    
    def _load_configuration(self):
        """Load supply chain configuration from config files"""
        supply_config = self.config_manager.get("supply_chain", {})
        
        # Update system parameters
        if "parameters" in supply_config:
            self.system_parameters.update(supply_config["parameters"])
        
        # Load delivery configuration
        if "delivery" in supply_config:
            self.system_parameters["delivery_lead_times"].update(
                supply_config["delivery"].get("lead_times", {})
            )
    
    def _initialize_product_catalog(self):
        """Initialize agricultural input product catalog"""
        # Seeds
        self.input_products["seed_corn_pioneer"] = InputProduct(
            product_id="seed_corn_pioneer",
            product_name="Pioneer 1234A Corn Seed",
            category=InputCategory.SEEDS,
            brand="Pioneer",
            package_size=80000,  # seeds per bag
            package_unit="seeds",
            cost_per_package=350.0,
            cost_per_unit=0.004375,  # per seed
            application_rate=32000,  # seeds per acre
            application_unit="seeds/acre",
            shelf_life_days=730,  # 2 years
            storage_requirements=["cool", "dry", "pest_free"]
        )
        
        self.input_products["seed_soybean_dekalb"] = InputProduct(
            product_id="seed_soybean_dekalb",
            product_name="DeKalb DK4567 Soybean Seed",
            category=InputCategory.SEEDS,
            brand="DeKalb",
            package_size=50,  # pounds per bag
            package_unit="lbs",
            cost_per_package=55.0,
            cost_per_unit=1.10,  # per pound
            application_rate=1.2,  # lbs per acre
            application_unit="lbs/acre",
            shelf_life_days=365,
            storage_requirements=["cool", "dry"]
        )
        
        # Fertilizers
        self.input_products["fertilizer_urea"] = InputProduct(
            product_id="fertilizer_urea",
            product_name="Urea 46-0-0",
            category=InputCategory.FERTILIZERS,
            brand="Generic",
            package_size=2000,  # pounds per ton
            package_unit="lbs",
            cost_per_package=600.0,
            cost_per_unit=0.30,
            active_ingredients={"nitrogen": 0.46},
            application_rate=150,  # lbs per acre
            application_unit="lbs/acre",
            storage_requirements=["dry", "covered"]
        )
        
        self.input_products["fertilizer_dap"] = InputProduct(
            product_id="fertilizer_dap",
            product_name="DAP 18-46-0",
            category=InputCategory.FERTILIZERS,
            brand="Generic",
            package_size=2000,
            package_unit="lbs",
            cost_per_package=800.0,
            cost_per_unit=0.40,
            active_ingredients={"nitrogen": 0.18, "phosphorus": 0.46},
            application_rate=100,
            application_unit="lbs/acre",
            storage_requirements=["dry", "covered"]
        )
        
        # Pesticides
        self.input_products["herbicide_roundup"] = InputProduct(
            product_id="herbicide_roundup",
            product_name="Roundup PowerMAX",
            category=InputCategory.PESTICIDES,
            brand="Bayer",
            package_size=2.5,  # gallons
            package_unit="gallons",
            cost_per_package=75.0,
            cost_per_unit=30.0,
            active_ingredients={"glyphosate": 0.54},
            application_rate=1.5,  # pints per acre
            application_unit="pints/acre",
            shelf_life_days=1460,  # 4 years
            storage_requirements=["cool", "dry", "secure"],
            regulatory_restrictions=["applicator_license", "drift_management"]
        )
        
        # Fuel
        self.input_products["diesel_fuel"] = InputProduct(
            product_id="diesel_fuel",
            product_name="Ultra Low Sulfur Diesel",
            category=InputCategory.FUEL,
            brand="Generic",
            package_size=1000,  # gallons per delivery
            package_unit="gallons",
            cost_per_package=3200.0,  # $3.20 per gallon
            cost_per_unit=3.20,
            shelf_life_days=365,
            storage_requirements=["underground_tank", "spill_containment"]
        )
        
        print(f"Initialized {len(self.input_products)} agricultural input products")
    
    def _initialize_supplier_database(self):
        """Initialize supplier database with regional agricultural suppliers"""
        
        # Seed suppliers
        self.suppliers["pioneer_seeds"] = Supplier(
            supplier_id="pioneer_seeds",
            company_name="Pioneer Seed Company",
            supplier_type=SupplierType.SEED_COMPANY,
            contact_info={
                "phone": "800-PIONEER",
                "email": "sales@pioneer.com",
                "website": "pioneer.com"
            },
            location={"lat": 41.5, "lon": -93.6, "distance": 45.0},
            products_offered=["seed_corn_pioneer"],
            payment_terms=[PaymentTerm.NET_30, PaymentTerm.SEASONAL_PAY],
            delivery_methods=[DeliveryMethod.FARM_DELIVERY, DeliveryMethod.PICKUP],
            minimum_order=5000.0,  # 5 bags minimum
            volume_discounts={
                10000: 0.03,   # 3% discount for 10+ bags
                25000: 0.05,   # 5% discount for 25+ bags
                50000: 0.08    # 8% discount for 50+ bags
            },
            reliability_score=0.92,
            seasonal_availability={
                "spring": True, "summer": False, "fall": True, "winter": True
            }
        )
        
        self.suppliers["dekalb_seeds"] = Supplier(
            supplier_id="dekalb_seeds",
            company_name="DeKalb Seed Company",
            supplier_type=SupplierType.SEED_COMPANY,
            contact_info={
                "phone": "800-DEKALB1",
                "email": "orders@dekalb.com"
            },
            location={"lat": 41.8, "lon": -88.8, "distance": 120.0},
            products_offered=["seed_soybean_dekalb"],
            payment_terms=[PaymentTerm.NET_30, PaymentTerm.SEASONAL_PAY, PaymentTerm.CREDIT_LINE],
            delivery_methods=[DeliveryMethod.FARM_DELIVERY, DeliveryMethod.PICKUP],
            minimum_order=2000.0,  # $2000 minimum order
            volume_discounts={
                5000: 0.02,    # 2% discount for $5k+
                10000: 0.04,   # 4% discount for $10k+
                25000: 0.07    # 7% discount for $25k+
            },
            reliability_score=0.89
        )
        
        # Fertilizer suppliers
        self.suppliers["midwest_fertilizer"] = Supplier(
            supplier_id="midwest_fertilizer",
            company_name="Midwest Fertilizer Co-op",
            supplier_type=SupplierType.COOPERATIVE,
            contact_info={
                "phone": "555-FERT-001",
                "email": "orders@midwestfert.coop"
            },
            location={"lat": 41.2, "lon": -96.0, "distance": 25.0},
            products_offered=["fertilizer_urea", "fertilizer_dap"],
            payment_terms=[PaymentTerm.CASH_ON_DELIVERY, PaymentTerm.NET_60, PaymentTerm.SEASONAL_PAY],
            delivery_methods=[DeliveryMethod.BULK_DELIVERY, DeliveryMethod.FARM_DELIVERY],
            minimum_order=2000.0,  # 1 ton minimum
            volume_discounts={
                10000: 0.03,   # 3% for 5+ tons
                20000: 0.05,   # 5% for 10+ tons
                40000: 0.08    # 8% for 20+ tons
            },
            reliability_score=0.95,
            credit_terms={"credit_limit": 50000, "interest_rate": 0.06}
        )
        
        # Chemical suppliers
        self.suppliers["ag_chemicals_inc"] = Supplier(
            supplier_id="ag_chemicals_inc",
            company_name="Agricultural Chemicals Inc.",
            supplier_type=SupplierType.CHEMICAL_SUPPLIER,
            contact_info={
                "phone": "555-CHEM-001",
                "email": "orders@agchem.com"
            },
            location={"lat": 40.8, "lon": -96.7, "distance": 35.0},
            products_offered=["herbicide_roundup"],
            payment_terms=[PaymentTerm.NET_30, PaymentTerm.CASH_ON_DELIVERY],
            delivery_methods=[DeliveryMethod.FARM_DELIVERY, DeliveryMethod.PICKUP],
            minimum_order=500.0,
            volume_discounts={
                2000: 0.02,    # 2% for $2k+
                5000: 0.04,    # 4% for $5k+
                10000: 0.06    # 6% for $10k+
            },
            reliability_score=0.88
        )
        
        # Fuel suppliers
        self.suppliers["rural_energy"] = Supplier(
            supplier_id="rural_energy",
            company_name="Rural Energy Solutions",
            supplier_type=SupplierType.FUEL_DISTRIBUTOR,
            contact_info={
                "phone": "555-FUEL-001",
                "email": "dispatch@ruralenergy.com"
            },
            location={"lat": 41.1, "lon": -95.9, "distance": 15.0},
            products_offered=["diesel_fuel"],
            payment_terms=[PaymentTerm.NET_30, PaymentTerm.CASH_ON_DELIVERY],
            delivery_methods=[DeliveryMethod.BULK_DELIVERY, DeliveryMethod.FARM_DELIVERY],
            minimum_order=500.0,  # 500 gallons minimum
            volume_discounts={
                1000: 0.02,    # 2 cents off per gallon for 1000+ gallons
                5000: 0.05,    # 5 cents off per gallon for 5000+ gallons
                10000: 0.08    # 8 cents off per gallon for 10000+ gallons
            },
            reliability_score=0.94,
            seasonal_availability={
                "spring": True, "summer": True, "fall": True, "winter": True
            }
        )
        
        print(f"Initialized {len(self.suppliers)} agricultural suppliers")
    
    def _register_event_handlers(self):
        """Register event handlers for system integration"""
        self.event_system.subscribe("crop_planning_updated", self._handle_crop_planning_update)
        self.event_system.subscribe("season_changed", self._handle_season_change)
        self.event_system.subscribe("market_price_updated", self._handle_price_update)
        self.event_system.subscribe("inventory_threshold_reached", self._handle_inventory_threshold)
        self.event_system.subscribe("field_operation_scheduled", self._handle_operation_scheduled)
    
    def _load_market_data(self):
        """Load and initialize market price data"""
        # Initialize market prices for each product from each supplier
        for product_id in self.input_products:
            self.market_prices[product_id] = {}
            
        # Set initial prices based on supplier costs and competitive positioning
        self.market_prices["seed_corn_pioneer"]["pioneer_seeds"] = 350.0
        self.market_prices["seed_soybean_dekalb"]["dekalb_seeds"] = 55.0
        
        self.market_prices["fertilizer_urea"]["midwest_fertilizer"] = 600.0
        self.market_prices["fertilizer_dap"]["midwest_fertilizer"] = 800.0
        
        self.market_prices["herbicide_roundup"]["ag_chemicals_inc"] = 75.0
        self.market_prices["diesel_fuel"]["rural_energy"] = 3200.0
        
        # Initialize seasonal price patterns (simplified)
        self.seasonal_price_patterns = {
            "fertilizer_urea": {
                "spring": 1.1,   # 10% higher in spring
                "summer": 0.95,  # 5% lower in summer
                "fall": 1.0,     # Base price in fall
                "winter": 0.9    # 10% lower in winter
            },
            "diesel_fuel": {
                "spring": 1.05,  # 5% higher in spring
                "summer": 1.1,   # 10% higher in summer (driving season)
                "fall": 0.98,    # 2% lower in fall
                "winter": 0.95   # 5% lower in winter
            }
        }
    
    def create_supply_chain_plan(self, farm_id: str, planning_year: int, 
                                crop_plan: Dict[str, float]) -> SupplyChainPlan:
        """Create comprehensive supply chain plan for farm operation"""
        
        plan = SupplyChainPlan(
            farm_id=farm_id,
            planning_year=planning_year,
            crop_plan=crop_plan.copy()
        )
        
        # Calculate input requirements for each crop
        plan.input_requirements = self._calculate_input_requirements(crop_plan)
        
        # Identify preferred suppliers for each input category
        plan.preferred_suppliers = self._identify_preferred_suppliers(plan.input_requirements)
        
        # Identify bulk purchase opportunities
        plan.bulk_purchase_opportunities = self._identify_bulk_opportunities(plan.input_requirements)
        
        # Set delivery schedule preferences
        plan.delivery_schedule_preferences = self._determine_delivery_preferences(crop_plan)
        
        # Calculate budget allocations
        plan.budget_allocations = self._calculate_budget_allocations(plan.input_requirements)
        
        # Develop risk mitigation strategies
        plan.risk_mitigation_strategies = self._develop_risk_strategies(plan)
        
        # Store the plan
        self.supply_chain_plans[farm_id] = plan
        
        # Emit planning event
        self.event_system.emit_event("supply_chain_plan_created", {
            "farm_id": farm_id,
            "planning_year": planning_year,
            "total_budget": sum(plan.budget_allocations.values()),
            "crops": list(crop_plan.keys()),
            "suppliers": sum(len(suppliers) for suppliers in plan.preferred_suppliers.values())
        })
        
        return plan
    
    def _calculate_input_requirements(self, crop_plan: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Calculate input requirements based on crop acreage plan"""
        requirements = {}
        
        # Corn input requirements
        if "corn" in crop_plan:
            corn_acres = crop_plan["corn"]
            requirements["corn"] = {
                "seed_corn_pioneer": corn_acres * 32000,  # seeds per acre
                "fertilizer_urea": corn_acres * 150,      # lbs per acre
                "fertilizer_dap": corn_acres * 100,       # lbs per acre
                "herbicide_roundup": corn_acres * 1.5,    # pints per acre
                "diesel_fuel": corn_acres * 6.0           # gallons per acre
            }
        
        # Soybean input requirements
        if "soybeans" in crop_plan:
            soybean_acres = crop_plan["soybeans"]
            requirements["soybeans"] = {
                "seed_soybean_dekalb": soybean_acres * 1.2,  # lbs per acre
                "fertilizer_dap": soybean_acres * 75,        # lbs per acre (starter only)
                "herbicide_roundup": soybean_acres * 1.0,    # pints per acre
                "diesel_fuel": soybean_acres * 4.5           # gallons per acre
            }
        
        # Wheat input requirements
        if "wheat" in crop_plan:
            wheat_acres = crop_plan["wheat"]
            requirements["wheat"] = {
                "fertilizer_urea": wheat_acres * 80,      # lbs per acre
                "fertilizer_dap": wheat_acres * 60,       # lbs per acre
                "diesel_fuel": wheat_acres * 5.0          # gallons per acre
            }
        
        return requirements
    
    def _identify_preferred_suppliers(self, input_requirements: Dict[str, Dict[str, float]]) -> Dict[str, List[str]]:
        """Identify preferred suppliers for each input category"""
        preferred_suppliers = {}
        
        # Group requirements by input category
        category_requirements = {}
        for crop, inputs in input_requirements.items():
            for input_id, quantity in inputs.items():
                if input_id in self.input_products:
                    product = self.input_products[input_id]
                    category = product.category.value
                    
                    if category not in category_requirements:
                        category_requirements[category] = 0.0
                    category_requirements[category] += quantity
        
        # Find suppliers for each category
        for category, total_quantity in category_requirements.items():
            category_suppliers = []
            
            for supplier_id, supplier in self.suppliers.items():
                # Check if supplier offers products in this category
                has_category_products = any(
                    product_id for product_id in supplier.products_offered
                    if product_id in self.input_products and 
                    self.input_products[product_id].category.value == category
                )
                
                if has_category_products:
                    # Score supplier based on reliability, pricing, and logistics
                    score = self._score_supplier(supplier, total_quantity)
                    category_suppliers.append((supplier_id, score))
            
            # Sort by score and take top suppliers
            category_suppliers.sort(key=lambda x: x[1], reverse=True)
            preferred_suppliers[category] = [supplier_id for supplier_id, _ in category_suppliers[:3]]
        
        return preferred_suppliers
    
    def _score_supplier(self, supplier: Supplier, estimated_volume: float) -> float:
        """Score supplier based on multiple criteria"""
        score = 0.0
        
        # Reliability score (0-30 points)
        score += supplier.reliability_score * 30
        
        # Volume discount potential (0-20 points)
        best_discount = 0.0
        for volume_threshold, discount in supplier.volume_discounts.items():
            if estimated_volume >= volume_threshold:
                best_discount = max(best_discount, discount)
        score += best_discount * 200  # Convert % to points
        
        # Distance/logistics (0-20 points)
        distance = supplier.location.get("distance", 100)
        distance_score = max(0, 20 - (distance / 10))  # Closer is better
        score += distance_score
        
        # Payment terms flexibility (0-15 points)
        terms_score = len(supplier.payment_terms) * 3
        if PaymentTerm.SEASONAL_PAY in supplier.payment_terms:
            terms_score += 6  # Bonus for seasonal pay
        score += min(terms_score, 15)
        
        # Delivery options (0-15 points)
        delivery_score = len(supplier.delivery_methods) * 5
        score += min(delivery_score, 15)
        
        return score
    
    def _identify_bulk_opportunities(self, input_requirements: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """Identify opportunities for bulk purchasing discounts"""
        opportunities = []
        
        # Aggregate requirements across crops
        total_requirements = {}
        for crop, inputs in input_requirements.items():
            for input_id, quantity in inputs.items():
                if input_id not in total_requirements:
                    total_requirements[input_id] = 0.0
                total_requirements[input_id] += quantity
        
        # Check each product for bulk opportunities
        for input_id, total_quantity in total_requirements.items():
            if input_id not in self.input_products:
                continue
            
            product = self.input_products[input_id]
            
            # Find suppliers offering this product
            for supplier_id, supplier in self.suppliers.items():
                if input_id not in supplier.products_offered:
                    continue
                
                # Calculate potential savings from volume discounts
                for volume_threshold, discount_rate in supplier.volume_discounts.items():
                    if total_quantity >= volume_threshold:
                        base_cost = total_quantity * product.cost_per_unit
                        discounted_cost = base_cost * (1 - discount_rate)
                        savings = base_cost - discounted_cost
                        
                        opportunities.append({
                            "input_id": input_id,
                            "supplier_id": supplier_id,
                            "quantity": total_quantity,
                            "volume_threshold": volume_threshold,
                            "discount_rate": discount_rate,
                            "cost_savings": savings,
                            "recommendation": f"Purchase {total_quantity:.0f} {product.package_unit} of {product.product_name} from {supplier.company_name} for {discount_rate:.1%} discount"
                        })
        
        # Sort opportunities by potential savings
        opportunities.sort(key=lambda x: x["cost_savings"], reverse=True)
        
        return opportunities[:10]  # Return top 10 opportunities
    
    def _determine_delivery_preferences(self, crop_plan: Dict[str, float]) -> Dict[str, str]:
        """Determine optimal delivery timing for different inputs"""
        preferences = {}
        
        # Seed delivery preferences
        preferences["seeds"] = "early_spring"    # Deliver seeds 2-4 weeks before planting
        
        # Fertilizer delivery preferences
        preferences["fertilizers"] = "pre_season"  # Deliver fertilizers in late winter/early spring
        
        # Chemical delivery preferences
        preferences["pesticides"] = "just_in_time"  # Deliver chemicals 1-2 weeks before application
        
        # Fuel delivery preferences
        preferences["fuel"] = "monthly"  # Regular monthly fuel deliveries
        
        return preferences
    
    def _calculate_budget_allocations(self, input_requirements: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate budget allocations for different input categories"""
        budget = {}
        
        # Calculate total costs by category
        category_costs = {}
        
        for crop, inputs in input_requirements.items():
            for input_id, quantity in inputs.items():
                if input_id not in self.input_products:
                    continue
                    
                product = self.input_products[input_id]
                category = product.category.value
                cost = quantity * product.cost_per_unit
                
                if category not in category_costs:
                    category_costs[category] = 0.0
                category_costs[category] += cost
        
        # Add contingency and operational margins
        for category, base_cost in category_costs.items():
            # Add 10% contingency for price volatility and 5% for operational buffer
            budget[category] = base_cost * 1.15
        
        return budget
    
    def _develop_risk_strategies(self, plan: SupplyChainPlan) -> List[str]:
        """Develop supply chain risk mitigation strategies"""
        strategies = []
        
        # Multiple supplier strategy
        if len(plan.preferred_suppliers) > 1:
            strategies.append("Maintain relationships with multiple suppliers per input category")
        
        # Inventory management strategies
        strategies.append("Maintain 30-day safety stock for critical inputs")
        
        # Price risk strategies
        strategies.append("Consider forward contracting for major input purchases")
        
        # Delivery risk strategies
        strategies.append("Schedule deliveries with 2-week lead time buffer")
        
        # Quality assurance strategies
        strategies.append("Implement incoming quality inspection procedures")
        
        # Seasonal strategies
        strategies.append("Purchase off-season when prices are typically lower")
        
        return strategies
    
    def create_purchase_order(self, farm_id: str, supplier_id: str, 
                            order_items: List[Dict[str, Any]], 
                            delivery_params: Dict[str, Any]) -> Optional[PurchaseOrder]:
        """Create purchase order for agricultural inputs"""
        
        if supplier_id not in self.suppliers:
            print(f"Error: Supplier {supplier_id} not found")
            return None
        
        supplier = self.suppliers[supplier_id]
        
        # Generate order ID
        order_id = f"PO_{farm_id}_{supplier_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate order totals
        subtotal = 0.0
        processed_items = []
        
        for item in order_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)
            
            if product_id not in self.input_products:
                print(f"Warning: Product {product_id} not found")
                continue
            
            if product_id not in supplier.products_offered:
                print(f"Warning: Supplier {supplier_id} does not offer {product_id}")
                continue
            
            product = self.input_products[product_id]
            unit_price = self.market_prices.get(product_id, {}).get(supplier_id, product.cost_per_unit)
            line_total = quantity * unit_price
            
            processed_items.append({
                "product_id": product_id,
                "product_name": product.product_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": line_total
            })
            
            subtotal += line_total
        
        if not processed_items:
            print("Error: No valid items in purchase order")
            return None
        
        # Check minimum order requirement
        if subtotal < supplier.minimum_order:
            print(f"Error: Order total ${subtotal:.2f} is below minimum order of ${supplier.minimum_order:.2f}")
            return None
        
        # Calculate discounts
        discount_amount = 0.0
        for volume_threshold, discount_rate in supplier.volume_discounts.items():
            if subtotal >= volume_threshold:
                discount_amount = subtotal * discount_rate
                break
        
        # Calculate delivery fee
        delivery_method = delivery_params.get("delivery_method", DeliveryMethod.FARM_DELIVERY)
        delivery_fee = self._calculate_delivery_fee(supplier, delivery_method, subtotal)
        
        # Calculate tax (simplified - would vary by location and product type)
        tax_rate = 0.08  # 8% sales tax
        tax_amount = (subtotal - discount_amount) * tax_rate
        
        # Calculate total
        total_amount = subtotal - discount_amount + delivery_fee + tax_amount
        
        # Create purchase order
        order = PurchaseOrder(
            order_id=order_id,
            supplier_id=supplier_id,
            order_date=datetime.now(),
            requested_delivery_date=delivery_params.get("requested_date", 
                                                       datetime.now() + timedelta(days=7)),
            farm_id=farm_id,
            order_items=processed_items,
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            payment_term=delivery_params.get("payment_term", PaymentTerm.NET_30),
            delivery_method=delivery_method,
            delivery_address=delivery_params.get("delivery_address", "Main Farm Location"),
            special_instructions=delivery_params.get("special_instructions", "")
        )
        
        # Store purchase order
        self.purchase_orders[order_id] = order
        
        # Schedule delivery
        self._schedule_delivery(order)
        
        # Emit purchase order event
        self.event_system.emit_event("purchase_order_created", {
            "order_id": order_id,
            "farm_id": farm_id,
            "supplier_id": supplier_id,
            "total_amount": total_amount,
            "item_count": len(processed_items),
            "delivery_date": order.requested_delivery_date.isoformat()
        })
        
        print(f"Purchase order {order_id} created")
        print(f"Supplier: {supplier.company_name}")
        print(f"Total: ${total_amount:,.2f}")
        print(f"Items: {len(processed_items)}")
        
        return order
    
    def _calculate_delivery_fee(self, supplier: Supplier, delivery_method: DeliveryMethod, order_value: float) -> float:
        """Calculate delivery fee based on method and distance"""
        
        if delivery_method == DeliveryMethod.PICKUP:
            return 0.0
        
        distance = supplier.location.get("distance", 50.0)
        base_fee = distance * self.system_parameters["cost_parameters"]["delivery_cost_per_mile"]
        
        if delivery_method == DeliveryMethod.BULK_DELIVERY:
            # Bulk delivery has higher base cost but better per-unit economics
            if order_value >= self.system_parameters["cost_parameters"]["bulk_delivery_minimum"]:
                base_fee *= 1.5  # 50% premium for bulk equipment
            else:
                base_fee *= 2.0  # 100% premium if below bulk minimum
        
        elif delivery_method == DeliveryMethod.FARM_DELIVERY:
            # Standard farm delivery
            base_fee *= 1.0
        
        # Volume discount on delivery fees
        if order_value > 10000:
            base_fee *= 0.5  # 50% delivery discount for large orders
        elif order_value > 5000:
            base_fee *= 0.75  # 25% delivery discount for medium orders
        
        return max(base_fee, 25.0)  # Minimum delivery fee
    
    def _schedule_delivery(self, order: PurchaseOrder):
        """Schedule delivery for purchase order"""
        
        supplier = self.suppliers[order.supplier_id]
        lead_time = self.system_parameters["delivery_lead_times"].get(
            order.delivery_method, 
            3  # Default 3 days
        )
        
        # Calculate delivery window
        scheduled_date = order.requested_delivery_date
        if scheduled_date < datetime.now() + timedelta(days=lead_time):
            scheduled_date = datetime.now() + timedelta(days=lead_time)
        
        window_start = scheduled_date.replace(hour=8, minute=0)
        window_end = scheduled_date.replace(hour=17, minute=0)
        
        delivery_id = f"DEL_{order.order_id}_{datetime.now().strftime('%H%M%S')}"
        
        delivery = DeliverySchedule(
            delivery_id=delivery_id,
            order_id=order.order_id,
            supplier_id=order.supplier_id,
            farm_id=order.farm_id,
            scheduled_date=scheduled_date,
            delivery_window_start=window_start,
            delivery_window_end=window_end,
            delivery_method=order.delivery_method
        )
        
        self.delivery_schedules[delivery_id] = delivery
        
        # Emit delivery scheduled event
        self.event_system.emit_event("delivery_scheduled", {
            "delivery_id": delivery_id,
            "order_id": order.order_id,
            "scheduled_date": scheduled_date.isoformat(),
            "delivery_window": f"{window_start.strftime('%H:%M')} - {window_end.strftime('%H:%M')}"
        })
    
    def receive_delivery(self, delivery_id: str, received_items: List[Dict[str, Any]]) -> bool:
        """Process delivery receipt and update inventory"""
        
        if delivery_id not in self.delivery_schedules:
            print(f"Error: Delivery {delivery_id} not found")
            return False
        
        delivery = self.delivery_schedules[delivery_id]
        order = self.purchase_orders.get(delivery.order_id)
        
        if not order:
            print(f"Error: Order {delivery.order_id} not found")
            return False
        
        # Process each received item
        for received_item in received_items:
            product_id = received_item.get("product_id")
            quantity_received = received_item.get("quantity_received", 0)
            quality_grade = received_item.get("quality_grade", "A")
            lot_number = received_item.get("lot_number")
            
            if product_id not in self.input_products:
                continue
            
            product = self.input_products[product_id]
            
            # Find corresponding order item
            order_item = None
            for item in order.order_items:
                if item["product_id"] == product_id:
                    order_item = item
                    break
            
            if not order_item:
                continue
            
            # Create inventory item
            item_id = f"INV_{order.farm_id}_{product_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            inventory_item = InventoryItem(
                item_id=item_id,
                product_id=product_id,
                quantity_on_hand=quantity_received,
                unit_cost=order_item["unit_price"],
                total_value=quantity_received * order_item["unit_price"],
                supplier_id=order.supplier_id,
                lot_number=lot_number,
                storage_location="main_storage"
            )
            
            # Set expiration date if applicable
            if product.shelf_life_days:
                inventory_item.expiration_date = datetime.now() + timedelta(days=product.shelf_life_days)
            
            self.inventory_items[item_id] = inventory_item
        
        # Update delivery status
        delivery.delivery_status = "completed"
        delivery.actual_delivery_time = datetime.now()
        
        # Update order status
        order.order_status = "delivered"
        
        # Update metrics
        if order.farm_id not in self.metrics:
            self.metrics[order.farm_id] = SupplyChainMetrics(farm_id=order.farm_id)
        
        metrics = self.metrics[order.farm_id]
        metrics.total_procurement_spend += order.total_amount
        
        # Calculate on-time delivery
        if delivery.actual_delivery_time <= delivery.delivery_window_end:
            # Update on-time delivery rate (simplified calculation)
            pass
        
        # Emit delivery completed event
        self.event_system.emit_event("delivery_completed", {
            "delivery_id": delivery_id,
            "order_id": order.order_id,
            "farm_id": order.farm_id,
            "items_received": len(received_items),
            "total_value": sum(item.total_value for item in self.inventory_items.values() 
                             if item.supplier_id == order.supplier_id)
        })
        
        print(f"Delivery {delivery_id} completed successfully")
        return True
    
    def get_inventory_status(self, farm_id: str, category: Optional[InputCategory] = None) -> Dict[str, Any]:
        """Get current inventory status for farm"""
        
        farm_inventory = {}
        total_value = 0.0
        items_by_category = {}
        
        for item in self.inventory_items.values():
            # Filter by farm (would need farm association in real system)
            product = self.input_products.get(item.product_id)
            if not product:
                continue
            
            # Filter by category if specified
            if category and product.category != category:
                continue
            
            category_name = product.category.value
            if category_name not in items_by_category:
                items_by_category[category_name] = []
            
            # Calculate days remaining if product has expiration
            days_remaining = None
            if item.expiration_date:
                days_remaining = (item.expiration_date - datetime.now()).days
            
            item_info = {
                "product_id": item.product_id,
                "product_name": product.product_name,
                "quantity_on_hand": item.quantity_on_hand,
                "unit": product.package_unit,
                "unit_cost": item.unit_cost,
                "total_value": item.total_value,
                "storage_location": item.storage_location,
                "supplier": self.suppliers.get(item.supplier_id, {}).get("company_name", "Unknown"),
                "received_date": item.received_date.isoformat(),
                "days_remaining": days_remaining,
                "status": item.status.value
            }
            
            items_by_category[category_name].append(item_info)
            total_value += item.total_value
        
        return {
            "farm_id": farm_id,
            "total_inventory_value": total_value,
            "categories": items_by_category,
            "summary": {
                "total_items": sum(len(items) for items in items_by_category.values()),
                "categories_stocked": len(items_by_category),
                "low_stock_alerts": self._get_low_stock_alerts(farm_id)
            }
        }
    
    def _get_low_stock_alerts(self, farm_id: str) -> List[Dict[str, Any]]:
        """Get low stock alerts for critical inputs"""
        alerts = []
        
        # This would integrate with crop planning to determine critical needs
        # For now, using simplified thresholds
        
        for item in self.inventory_items.values():
            product = self.input_products.get(item.product_id)
            if not product:
                continue
            
            # Check for low stock based on typical usage rates
            if item.quantity_on_hand < self._get_minimum_stock_level(product):
                days_until_empty = self._calculate_days_until_empty(item, product)
                
                alerts.append({
                    "product_id": item.product_id,
                    "product_name": product.product_name,
                    "current_quantity": item.quantity_on_hand,
                    "minimum_level": self._get_minimum_stock_level(product),
                    "days_until_empty": days_until_empty,
                    "recommended_order_quantity": self._get_recommended_order_quantity(product),
                    "urgency": "high" if days_until_empty < 7 else "medium"
                })
        
        return alerts
    
    def _get_minimum_stock_level(self, product: InputProduct) -> float:
        """Calculate minimum stock level for product"""
        # Simplified calculation - would be more sophisticated in real system
        if product.category == InputCategory.FUEL:
            return 500.0  # 500 gallons minimum
        elif product.category == InputCategory.FERTILIZERS:
            return 2000.0  # 1 ton minimum
        elif product.category == InputCategory.SEEDS:
            return 50000.0 if product.package_unit == "seeds" else 100.0  # Seeds or lbs
        else:
            return 10.0  # Default minimum
    
    def _calculate_days_until_empty(self, item: InventoryItem, product: InputProduct) -> int:
        """Calculate days until inventory runs out based on usage patterns"""
        # Simplified calculation - would use historical usage data
        daily_usage = self._estimate_daily_usage(product)
        if daily_usage > 0:
            return int(item.quantity_on_hand / daily_usage)
        return 999  # Unknown usage pattern
    
    def _estimate_daily_usage(self, product: InputProduct) -> float:
        """Estimate daily usage rate for product during peak season"""
        # Simplified estimates - would use historical data and seasonal patterns
        usage_rates = {
            InputCategory.FUEL: 50.0,        # 50 gallons per day during peak season
            InputCategory.FERTILIZERS: 100.0, # 100 lbs per day during application season
            InputCategory.PESTICIDES: 5.0,    # 5 gallons per day during spray season
            InputCategory.SEEDS: 1000.0       # 1000 seeds per day during planting
        }
        
        return usage_rates.get(product.category, 1.0)
    
    def _get_recommended_order_quantity(self, product: InputProduct) -> float:
        """Get recommended reorder quantity"""
        # Calculate based on economic order quantity principles
        minimum_stock = self._get_minimum_stock_level(product)
        return minimum_stock * 3  # Order 3x minimum to reduce frequent ordering
    
    def optimize_procurement(self, farm_id: str) -> Dict[str, Any]:
        """Optimize procurement strategy for farm"""
        
        if farm_id not in self.supply_chain_plans:
            return {"error": "No supply chain plan found for farm"}
        
        plan = self.supply_chain_plans[farm_id]
        optimization_results = {}
        
        # Analyze current procurement patterns
        current_metrics = self.metrics.get(farm_id, SupplyChainMetrics(farm_id=farm_id))
        
        # Calculate procurement optimization opportunities
        cost_savings_opportunities = []
        
        # 1. Volume consolidation opportunities
        consolidation_savings = self._analyze_consolidation_opportunities(plan)
        cost_savings_opportunities.extend(consolidation_savings)
        
        # 2. Seasonal timing optimization
        timing_savings = self._analyze_timing_opportunities(plan)
        cost_savings_opportunities.extend(timing_savings)
        
        # 3. Supplier relationship optimization
        supplier_savings = self._analyze_supplier_relationships(farm_id)
        cost_savings_opportunities.extend(supplier_savings)
        
        # 4. Inventory optimization
        inventory_savings = self._analyze_inventory_optimization(farm_id)
        cost_savings_opportunities.extend(inventory_savings)
        
        # Sort opportunities by potential savings
        cost_savings_opportunities.sort(key=lambda x: x.get("potential_savings", 0), reverse=True)
        
        # Calculate total optimization potential
        total_potential_savings = sum(opp.get("potential_savings", 0) for opp in cost_savings_opportunities)
        
        optimization_results = {
            "farm_id": farm_id,
            "current_annual_spend": current_metrics.total_procurement_spend,
            "total_optimization_potential": total_potential_savings,
            "savings_percentage": (total_potential_savings / max(current_metrics.total_procurement_spend, 1)) * 100,
            "opportunities": cost_savings_opportunities[:10],  # Top 10 opportunities
            "recommendations": self._generate_procurement_recommendations(cost_savings_opportunities)
        }
        
        return optimization_results
    
    def _analyze_consolidation_opportunities(self, plan: SupplyChainPlan) -> List[Dict[str, Any]]:
        """Analyze opportunities for volume consolidation"""
        opportunities = []
        
        # Look for products where multiple suppliers could be consolidated
        product_suppliers = {}
        for category, supplier_ids in plan.preferred_suppliers.items():
            for supplier_id in supplier_ids:
                supplier = self.suppliers[supplier_id]
                for product_id in supplier.products_offered:
                    if product_id not in product_suppliers:
                        product_suppliers[product_id] = []
                    product_suppliers[product_id].append(supplier_id)
        
        # Find consolidation opportunities
        for product_id, supplier_list in product_suppliers.items():
            if len(supplier_list) > 1:
                product = self.input_products[product_id]
                
                # Calculate potential volume consolidation savings
                # This is simplified - would involve complex supplier negotiations
                potential_volume_increase = 1.5  # 50% volume increase from consolidation
                best_discount_rate = 0.0
                
                for supplier_id in supplier_list:
                    supplier = self.suppliers[supplier_id]
                    for volume, discount in supplier.volume_discounts.items():
                        if discount > best_discount_rate:
                            best_discount_rate = discount
                
                estimated_annual_spend = 10000  # Simplified estimate
                potential_savings = estimated_annual_spend * best_discount_rate * 0.5  # Conservative estimate
                
                opportunities.append({
                    "opportunity_type": "volume_consolidation",
                    "product_id": product_id,
                    "product_name": product.product_name,
                    "current_suppliers": len(supplier_list),
                    "recommended_suppliers": 1,
                    "potential_savings": potential_savings,
                    "description": f"Consolidate {product.product_name} purchases with single supplier for volume discounts"
                })
        
        return opportunities
    
    def _analyze_timing_opportunities(self, plan: SupplyChainPlan) -> List[Dict[str, Any]]:
        """Analyze seasonal timing optimization opportunities"""
        opportunities = []
        
        # Analyze seasonal price patterns for cost optimization
        for product_id, seasonal_patterns in self.seasonal_price_patterns.items():
            if product_id in self.input_products:
                product = self.input_products[product_id]
                
                # Find lowest price season
                lowest_price_season = min(seasonal_patterns, key=seasonal_patterns.get)
                price_multiplier = seasonal_patterns[lowest_price_season]
                
                # Calculate savings from optimal timing
                if price_multiplier < 1.0:
                    estimated_annual_spend = 15000  # Simplified estimate
                    potential_savings = estimated_annual_spend * (1.0 - price_multiplier) * 0.8
                    
                    opportunities.append({
                        "opportunity_type": "seasonal_timing",
                        "product_id": product_id,
                        "product_name": product.product_name,
                        "optimal_purchase_season": lowest_price_season,
                        "price_advantage": f"{(1.0 - price_multiplier) * 100:.0f}%",
                        "potential_savings": potential_savings,
                        "description": f"Purchase {product.product_name} in {lowest_price_season} for {(1.0 - price_multiplier) * 100:.0f}% savings"
                    })
        
        return opportunities
    
    def _analyze_supplier_relationships(self, farm_id: str) -> List[Dict[str, Any]]:
        """Analyze supplier relationship optimization opportunities"""
        opportunities = []
        
        # Analyze supplier performance and consolidation opportunities
        for supplier_id, supplier in self.suppliers.items():
            if supplier.reliability_score < 0.9:
                # Low reliability supplier - recommend replacement
                estimated_impact = 5000  # Cost of supply disruptions
                
                opportunities.append({
                    "opportunity_type": "supplier_replacement",
                    "supplier_id": supplier_id,
                    "supplier_name": supplier.company_name,
                    "current_reliability": f"{supplier.reliability_score:.1%}",
                    "recommended_action": "Replace with higher reliability supplier",
                    "potential_savings": estimated_impact * 0.5,  # Risk reduction value
                    "description": f"Replace {supplier.company_name} (reliability: {supplier.reliability_score:.1%}) with more reliable supplier"
                })
            
            # Check for credit term optimization
            if PaymentTerm.NET_60 in supplier.payment_terms and PaymentTerm.NET_30 in supplier.payment_terms:
                cash_flow_benefit = 2000  # Simplified benefit calculation
                
                opportunities.append({
                    "opportunity_type": "payment_terms",
                    "supplier_id": supplier_id,
                    "supplier_name": supplier.company_name,
                    "recommended_action": "Negotiate extended payment terms",
                    "cash_flow_benefit": cash_flow_benefit,
                    "potential_savings": cash_flow_benefit * 0.03,  # 3% interest rate benefit
                    "description": f"Negotiate NET 60 terms with {supplier.company_name} for improved cash flow"
                })
        
        return opportunities
    
    def _analyze_inventory_optimization(self, farm_id: str) -> List[Dict[str, Any]]:
        """Analyze inventory management optimization opportunities"""
        opportunities = []
        
        # Analyze current inventory levels and turnover
        for item in self.inventory_items.values():
            product = self.input_products.get(item.product_id)
            if not product:
                continue
            
            # Check for overstock situations
            minimum_stock = self._get_minimum_stock_level(product)
            if item.quantity_on_hand > minimum_stock * 4:  # More than 4x minimum
                carrying_cost = item.total_value * 0.15  # 15% annual carrying cost
                excess_value = (item.quantity_on_hand - minimum_stock * 2) * item.unit_cost
                
                opportunities.append({
                    "opportunity_type": "inventory_reduction",
                    "product_id": item.product_id,
                    "product_name": product.product_name,
                    "current_stock": item.quantity_on_hand,
                    "optimal_stock": minimum_stock * 2,
                    "excess_value": excess_value,
                    "potential_savings": excess_value * 0.15,  # Carrying cost savings
                    "description": f"Reduce {product.product_name} inventory by ${excess_value:,.0f} to optimize carrying costs"
                })
        
        return opportunities
    
    def _generate_procurement_recommendations(self, opportunities: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable procurement recommendations"""
        recommendations = []
        
        # Group opportunities by type
        opportunity_types = {}
        for opp in opportunities[:5]:  # Top 5 opportunities
            opp_type = opp.get("opportunity_type", "other")
            if opp_type not in opportunity_types:
                opportunity_types[opp_type] = []
            opportunity_types[opp_type].append(opp)
        
        # Generate recommendations by type
        if "volume_consolidation" in opportunity_types:
            recommendations.append("Consolidate purchases with preferred suppliers to achieve volume discounts")
        
        if "seasonal_timing" in opportunity_types:
            recommendations.append("Time purchases to take advantage of seasonal price patterns")
        
        if "supplier_replacement" in opportunity_types:
            recommendations.append("Replace low-performing suppliers with more reliable alternatives")
        
        if "inventory_reduction" in opportunity_types:
            recommendations.append("Optimize inventory levels to reduce carrying costs")
        
        if "payment_terms" in opportunity_types:
            recommendations.append("Negotiate improved payment terms to optimize cash flow")
        
        # Add general recommendations
        recommendations.extend([
            "Implement automated reorder points to prevent stockouts",
            "Develop strategic supplier partnerships for long-term cost stability",
            "Use forward contracting to manage price volatility risk",
            "Implement quality metrics to ensure consistent input performance"
        ])
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    # Event handlers for system integration
    def _handle_crop_planning_update(self, event_data: Dict[str, Any]):
        """Handle crop planning updates to adjust supply chain requirements"""
        farm_id = event_data.get("farm_id")
        crop_plan = event_data.get("crop_plan", {})
        
        if farm_id and crop_plan:
            # Update supply chain plan with new crop requirements
            current_year = datetime.now().year
            self.create_supply_chain_plan(farm_id, current_year, crop_plan)
    
    def _handle_season_change(self, event_data: Dict[str, Any]):
        """Handle seasonal changes affecting procurement and pricing"""
        new_season = event_data.get("season")
        
        # Update seasonal pricing
        for product_id, patterns in self.seasonal_price_patterns.items():
            if new_season in patterns:
                price_multiplier = patterns[new_season]
                
                # Update market prices for this season
                for supplier_id in self.market_prices.get(product_id, {}):
                    base_price = self.input_products[product_id].cost_per_unit
                    self.market_prices[product_id][supplier_id] = base_price * price_multiplier
    
    def _handle_price_update(self, event_data: Dict[str, Any]):
        """Handle market price updates from external sources"""
        product_id = event_data.get("product_id")
        supplier_id = event_data.get("supplier_id")
        new_price = event_data.get("price")
        
        if product_id and supplier_id and new_price:
            if product_id not in self.market_prices:
                self.market_prices[product_id] = {}
            self.market_prices[product_id][supplier_id] = new_price
    
    def _handle_inventory_threshold(self, event_data: Dict[str, Any]):
        """Handle inventory threshold alerts"""
        farm_id = event_data.get("farm_id")
        product_id = event_data.get("product_id")
        current_level = event_data.get("current_level", 0)
        
        # Generate automatic reorder recommendation
        if product_id in self.input_products:
            product = self.input_products[product_id]
            recommended_quantity = self._get_recommended_order_quantity(product)
            
            # Find preferred supplier
            preferred_supplier = None
            for supplier_id, supplier in self.suppliers.items():
                if product_id in supplier.products_offered:
                    preferred_supplier = supplier_id
                    break
            
            if preferred_supplier:
                self.event_system.emit_event("reorder_recommendation", {
                    "farm_id": farm_id,
                    "product_id": product_id,
                    "current_level": current_level,
                    "recommended_quantity": recommended_quantity,
                    "preferred_supplier": preferred_supplier
                })
    
    def _handle_operation_scheduled(self, event_data: Dict[str, Any]):
        """Handle field operation scheduling to ensure input availability"""
        farm_id = event_data.get("farm_id")
        operation_type = event_data.get("operation_type")
        scheduled_date = event_data.get("scheduled_date")
        acres = event_data.get("acres", 0)
        
        # Check if required inputs are available
        required_inputs = self._get_operation_input_requirements(operation_type, acres)
        
        for input_id, quantity_needed in required_inputs.items():
            available_quantity = self._get_available_inventory(farm_id, input_id)
            
            if available_quantity < quantity_needed:
                shortage = quantity_needed - available_quantity
                self.event_system.emit_event("input_shortage_alert", {
                    "farm_id": farm_id,
                    "operation_type": operation_type,
                    "scheduled_date": scheduled_date,
                    "input_id": input_id,
                    "quantity_needed": quantity_needed,
                    "quantity_available": available_quantity,
                    "shortage": shortage
                })
    
    def _get_operation_input_requirements(self, operation_type: str, acres: float) -> Dict[str, float]:
        """Get input requirements for specific field operation"""
        # Simplified operation requirements
        requirements = {}
        
        if operation_type == "planting":
            requirements["seed_corn_pioneer"] = acres * 32000  # seeds per acre
            requirements["fertilizer_dap"] = acres * 100      # lbs per acre
            requirements["diesel_fuel"] = acres * 1.5         # gallons per acre
            
        elif operation_type == "fertilizer_application":
            requirements["fertilizer_urea"] = acres * 150     # lbs per acre
            requirements["diesel_fuel"] = acres * 0.8         # gallons per acre
            
        elif operation_type == "spraying":
            requirements["herbicide_roundup"] = acres * 1.5   # pints per acre
            requirements["diesel_fuel"] = acres * 0.5         # gallons per acre
        
        return requirements
    
    def _get_available_inventory(self, farm_id: str, product_id: str) -> float:
        """Get available inventory quantity for specific product"""
        total_available = 0.0
        
        for item in self.inventory_items.values():
            if item.product_id == product_id and item.status == InventoryStatus.IN_STOCK:
                available = item.quantity_on_hand - item.reserved_quantity
                total_available += max(0, available)
        
        return total_available
    
    def get_supply_chain_status(self) -> Dict[str, Any]:
        """Get comprehensive supply chain system status"""
        return {
            "system_status": "active" if self.is_initialized else "inactive",
            "total_suppliers": len(self.suppliers),
            "total_products": len(self.input_products),
            "active_purchase_orders": len([po for po in self.purchase_orders.values() if po.order_status != "delivered"]),
            "pending_deliveries": len([d for d in self.delivery_schedules.values() if d.delivery_status == "scheduled"]),
            "total_inventory_items": len(self.inventory_items),
            "total_inventory_value": sum(item.total_value for item in self.inventory_items.values()),
            "farms_with_plans": len(self.supply_chain_plans)
        }

# Global convenience functions
def get_supply_chain_system() -> Optional[SupplyChainSystem]:
    """Get the global supply chain system instance"""
    # This would typically be managed by a system registry
    return None

def create_purchase_order_for_farm(farm_id: str, supplier_id: str, items: List[Dict[str, Any]]) -> Optional[PurchaseOrder]:
    """Convenience function to create purchase order"""
    system = get_supply_chain_system()
    if system:
        delivery_params = {
            "delivery_method": DeliveryMethod.FARM_DELIVERY,
            "requested_date": datetime.now() + timedelta(days=7)
        }
        return system.create_purchase_order(farm_id, supplier_id, items, delivery_params)
    return None

def get_farm_inventory(farm_id: str, category: Optional[InputCategory] = None) -> Dict[str, Any]:
    """Convenience function to get farm inventory status"""
    system = get_supply_chain_system()
    if system:
        return system.get_inventory_status(farm_id, category)
    return {}

def optimize_farm_procurement(farm_id: str) -> Dict[str, Any]:
    """Convenience function to optimize procurement for farm"""
    system = get_supply_chain_system()
    if system:
        return system.optimize_procurement(farm_id)
    return {}