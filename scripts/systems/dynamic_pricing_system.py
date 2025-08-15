"""
Dynamic Pricing System - Realistic Agricultural Market Simulation for AgriFun

This system provides sophisticated agricultural commodity market modeling with supply/demand
dynamics, seasonal price variations, market volatility, and regional price differences.
Integrates with crop production, weather events, and global market conditions.

Key Features:
- Real-time supply/demand modeling based on production and consumption data
- Seasonal price patterns reflecting agricultural market cycles
- Market volatility simulation with random price movements and trend analysis
- Regional price differentials based on transportation costs and local demand
- Weather-driven price impacts (drought, flooding, excessive rain effects)
- Global market integration with import/export price influences
- Futures market simulation for price discovery and hedging opportunities
- Historical price tracking with technical analysis indicators

Market Factors Modeled:
- Supply: Local production, regional harvests, storage levels, import availability
- Demand: Local consumption, export demand, processing demand, feed demand
- External: Weather events, fuel costs, currency fluctuations, policy changes
- Technical: Moving averages, support/resistance levels, volatility indicators

Educational Value:
- Understanding of agricultural commodity market dynamics
- Impact of supply/demand fundamentals on pricing
- Seasonal marketing strategies and price timing
- Risk management through market analysis and hedging
- Global market interconnectedness and price relationships
"""

import time
import uuid
import random
import math
from typing import Dict, List, Set, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

# Import core systems
from ..core.advanced_event_system import get_event_system, EventPriority
from ..core.entity_component_system import get_entity_manager, Component, ComponentCategory
from ..core.advanced_config_system import get_config_manager
from ..core.time_management import get_time_manager

class MarketTrend(Enum):
    """Market trend directions"""
    STRONG_BEARISH = "strong_bearish"    # -3: Major downward trend
    BEARISH = "bearish"                  # -2: Downward trend
    WEAK_BEARISH = "weak_bearish"        # -1: Slight downward trend
    NEUTRAL = "neutral"                  # 0: No clear trend
    WEAK_BULLISH = "weak_bullish"        # +1: Slight upward trend
    BULLISH = "bullish"                  # +2: Upward trend
    STRONG_BULLISH = "strong_bullish"    # +3: Major upward trend

class PriceVolatility(Enum):
    """Market volatility levels"""
    VERY_LOW = "very_low"       # 0-2% daily variation
    LOW = "low"                 # 2-5% daily variation
    MODERATE = "moderate"       # 5-10% daily variation
    HIGH = "high"               # 10-15% daily variation
    VERY_HIGH = "very_high"     # 15%+ daily variation

class MarketRegion(Enum):
    """Regional market areas"""
    LOCAL = "local"             # Local county/area market
    REGIONAL = "regional"       # State or multi-state region
    NATIONAL = "national"       # National market (US)
    INTERNATIONAL = "international"  # Global market

class MarketEvent(Enum):
    """Market-moving events"""
    WEATHER_SHOCK = "weather_shock"         # Drought, flood, storm damage
    POLICY_CHANGE = "policy_change"         # Government policy/subsidy changes
    TRADE_NEWS = "trade_news"               # Export/import policy changes
    CURRENCY_MOVEMENT = "currency_movement" # USD strength changes
    FUEL_PRICE_SHOCK = "fuel_price_shock"   # Energy cost changes
    DEMAND_SHOCK = "demand_shock"           # Major demand increase/decrease
    SUPPLY_DISRUPTION = "supply_disruption" # Transportation, storage issues

@dataclass
class CommoditySpecification:
    """Detailed commodity trading specifications"""
    commodity_id: str
    name: str
    category: str                       # "grain", "oilseed", "livestock", "dairy"
    
    # Base price parameters
    base_price_per_unit: float          # Base price in dollars per unit
    price_unit: str                     # "bushel", "cwt", "ton", "gallon"
    unit_conversion: Dict[str, float]   # Conversion factors (bushels to tons, etc.)
    
    # Market characteristics
    typical_volatility: float           # Typical daily price volatility (as decimal)
    seasonal_pattern: Dict[str, float]  # Monthly price multipliers
    storage_cost_per_month: float       # Monthly storage cost per unit
    quality_premium_schedule: Dict[str, float]  # Quality grade premiums
    
    # Supply/demand elasticity
    supply_elasticity: float            # Price elasticity of supply
    demand_elasticity: float            # Price elasticity of demand
    
    # Market integration
    regional_price_differentials: Dict[MarketRegion, float]  # Regional price differences
    transportation_cost_per_mile: float # Cost to transport per mile
    
    # Contract specifications
    contract_months: List[str]          # Available contract months
    contract_size: int                  # Standard contract size
    minimum_price_increment: float     # Minimum price tick

@dataclass
class MarketConditions:
    """Current market conditions and factors"""
    commodity_id: str
    timestamp: float
    
    # Price information
    current_price: float
    daily_change: float
    daily_change_percent: float
    
    # Supply factors
    local_production_estimate: float    # Expected local production
    regional_production_estimate: float # Expected regional production
    carry_over_stocks: float            # Beginning stocks
    expected_harvest: float             # Projected harvest
    
    # Demand factors
    local_consumption: float            # Local demand
    export_demand: float                # Export opportunities
    processing_demand: float            # Industrial/processing demand
    feed_demand: float                  # Livestock feed demand
    
    # Market technicals
    trend: MarketTrend                  # Current trend direction
    volatility: PriceVolatility        # Current volatility level
    volume_average_10day: float        # 10-day average volume
    open_interest: int                  # Futures open interest
    
    # Moving averages and indicators
    price_sma_20: float                 # 20-day simple moving average
    price_sma_50: float                 # 50-day simple moving average
    rsi_14: float                       # 14-day Relative Strength Index
    bollinger_upper: float              # Upper Bollinger Band
    bollinger_lower: float              # Lower Bollinger Band

@dataclass
class PriceHistory:
    """Historical price data point"""
    timestamp: float
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    market_events: List[MarketEvent] = field(default_factory=list)

class DynamicPricingSystem:
    """Comprehensive dynamic pricing and market simulation system"""
    
    def __init__(self):
        """Initialize the dynamic pricing system"""
        self.system_name = "dynamic_pricing_system"
        self.event_system = get_event_system()
        self.entity_manager = get_entity_manager()
        self.config_manager = get_config_manager()
        self.time_manager = get_time_manager()
        
        # Commodity specifications
        self.commodity_specs: Dict[str, CommoditySpecification] = {}
        self.market_conditions: Dict[str, MarketConditions] = {}
        
        # Price history and tracking
        self.price_history: Dict[str, List[PriceHistory]] = {}
        self.daily_prices: Dict[str, Dict[str, float]] = {}  # commodity -> {date -> price}
        
        # Market state variables
        self.market_volatility_factor: float = 1.0
        self.global_economic_sentiment: float = 0.0  # -1.0 to 1.0
        self.weather_impact_factor: float = 1.0
        self.fuel_price_index: float = 100.0  # Base 100
        
        # Random number generators for price movements
        self.price_rng = random.Random()
        self.event_rng = random.Random()
        
        # System state
        self.initialized = False
        self.update_frequency = 4.0  # 4 updates per second for real-time pricing
        self.last_price_update = 0.0
        
        print("Dynamic Pricing System initialized")
    
    def initialize(self) -> bool:
        """Initialize the dynamic pricing system"""
        try:
            # Subscribe to events
            self.event_system.subscribe('time_advanced', self._handle_time_advanced)
            self.event_system.subscribe('weather_event_occurred', self._handle_weather_event)
            self.event_system.subscribe('crop_harvested', self._handle_crop_harvested)
            self.event_system.subscribe('crop_planted', self._handle_crop_planted)
            self.event_system.subscribe('market_event_triggered', self._handle_market_event)
            
            # Load commodity specifications
            self._load_commodity_specifications()
            
            # Initialize market conditions
            self._initialize_market_conditions()
            
            # Generate initial price history
            self._generate_initial_price_history()
            
            # Set random seeds for reproducible but varied behavior
            self.price_rng.seed(int(time.time()) % 10000)
            self.event_rng.seed(int(time.time()) % 10000 + 1000)
            
            self.initialized = True
            
            # Emit initialization complete event
            self.event_system.emit('dynamic_pricing_initialized', {
                'commodities_tracked': len(self.commodity_specs),
                'initial_market_sentiment': self.global_economic_sentiment,
                'system_status': 'ready'
            }, priority=EventPriority.NORMAL)
            
            print("Dynamic Pricing System initialization complete")
            return True
            
        except Exception as e:
            print(f"Failed to initialize Dynamic Pricing System: {e}")
            return False
    
    def _load_commodity_specifications(self):
        """Load commodity trading specifications"""
        
        # Corn (Maize) specification
        corn_spec = CommoditySpecification(
            commodity_id="corn",
            name="Corn (Maize)",
            category="grain",
            base_price_per_unit=5.50,
            price_unit="bushel",
            unit_conversion={"bushel_to_ton": 0.0254, "ton_to_bushel": 39.37},
            typical_volatility=0.025,  # 2.5% daily volatility
            seasonal_pattern={
                "01": 1.05,  # January - winter demand
                "02": 1.03,  # February
                "03": 1.02,  # March - planting season
                "04": 1.00,  # April
                "05": 0.98,  # May - planting progress
                "06": 0.96,  # June - growing season
                "07": 0.94,  # July - pollination critical
                "08": 0.92,  # August - crop development
                "09": 0.90,  # September - pre-harvest
                "10": 0.88,  # October - harvest pressure
                "11": 0.92,  # November - harvest complete
                "12": 1.00   # December - marketing
            },
            storage_cost_per_month=0.04,  # $0.04 per bushel per month
            quality_premium_schedule={
                "US_Grade_1": 0.05,  # $0.05 premium
                "US_Grade_2": 0.00,  # Base price
                "US_Grade_3": -0.10, # $0.10 discount
                "US_Sample": -0.25   # $0.25 discount
            },
            supply_elasticity=0.3,   # Relatively inelastic supply
            demand_elasticity=-0.4,  # Inelastic demand
            regional_price_differentials={
                MarketRegion.LOCAL: 0.00,
                MarketRegion.REGIONAL: -0.15,  # $0.15 basis discount
                MarketRegion.NATIONAL: -0.25,  # $0.25 basis discount
                MarketRegion.INTERNATIONAL: 0.10  # $0.10 premium for export
            },
            transportation_cost_per_mile=0.04,  # $0.04 per bushel per 100 miles
            contract_months=["03", "05", "07", "09", "12"],  # Mar, May, Jul, Sep, Dec
            contract_size=5000,  # 5,000 bushels
            minimum_price_increment=0.0025  # 1/4 cent per bushel
        )
        
        # Soybeans specification
        soybeans_spec = CommoditySpecification(
            commodity_id="soybeans",
            name="Soybeans",
            category="oilseed",
            base_price_per_unit=12.80,
            price_unit="bushel",
            unit_conversion={"bushel_to_ton": 0.0272, "ton_to_bushel": 36.74},
            typical_volatility=0.030,  # 3.0% daily volatility
            seasonal_pattern={
                "01": 1.06,  # January - protein demand
                "02": 1.04,  # February
                "03": 1.02,  # March - meal demand
                "04": 1.00,  # April
                "05": 0.98,  # May - planting
                "06": 0.96,  # June - growing
                "07": 0.94,  # July - pod filling
                "08": 0.92,  # August - crop condition
                "09": 0.88,  # September - harvest pressure
                "10": 0.86,  # October - peak harvest
                "11": 0.90,  # November - harvest complete
                "12": 0.95   # December - export season
            },
            storage_cost_per_month=0.06,  # $0.06 per bushel per month
            quality_premium_schedule={
                "US_Grade_1": 0.08,
                "US_Grade_2": 0.00,
                "US_Grade_3": -0.15,
                "US_Sample": -0.30
            },
            supply_elasticity=0.25,
            demand_elasticity=-0.35,
            regional_price_differentials={
                MarketRegion.LOCAL: 0.00,
                MarketRegion.REGIONAL: -0.20,
                MarketRegion.NATIONAL: -0.35,
                MarketRegion.INTERNATIONAL: 0.15
            },
            transportation_cost_per_mile=0.05,
            contract_months=["01", "03", "05", "07", "08", "09", "11"],
            contract_size=5000,
            minimum_price_increment=0.0025
        )
        
        # Wheat specification
        wheat_spec = CommoditySpecification(
            commodity_id="wheat",
            name="Wheat",
            category="grain",
            base_price_per_unit=7.20,
            price_unit="bushel",
            unit_conversion={"bushel_to_ton": 0.0272, "ton_to_bushel": 36.74},
            typical_volatility=0.035,  # 3.5% daily volatility
            seasonal_pattern={
                "01": 1.04,  # January - winter wheat
                "02": 1.02,  # February
                "03": 1.00,  # March - spring planting
                "04": 0.98,  # April
                "05": 0.96,  # May - crop development
                "06": 0.94,  # June - harvest anxiety
                "07": 0.88,  # July - harvest pressure
                "08": 0.85,  # August - peak harvest
                "09": 0.90,  # September - new crop
                "10": 0.95,  # October - demand pickup
                "11": 1.00,  # November - export season
                "12": 1.02   # December - winter demand
            },
            storage_cost_per_month=0.05,
            quality_premium_schedule={
                "US_Hard_Red_Winter_1": 0.15,
                "US_Hard_Red_Winter_2": 0.00,
                "US_Soft_Red_Winter_2": -0.05,
                "US_Sample": -0.35
            },
            supply_elasticity=0.2,
            demand_elasticity=-0.3,
            regional_price_differentials={
                MarketRegion.LOCAL: 0.00,
                MarketRegion.REGIONAL: -0.18,
                MarketRegion.NATIONAL: -0.30,
                MarketRegion.INTERNATIONAL: 0.25
            },
            transportation_cost_per_mile=0.04,
            contract_months=["03", "05", "07", "09", "12"],
            contract_size=5000,
            minimum_price_increment=0.0025
        )
        
        # Store specifications
        self.commodity_specs["corn"] = corn_spec
        self.commodity_specs["soybeans"] = soybeans_spec
        self.commodity_specs["wheat"] = wheat_spec
        
        print(f"Loaded {len(self.commodity_specs)} commodity specifications")
    
    def _initialize_market_conditions(self):
        """Initialize current market conditions for all commodities"""
        current_time = time.time()
        
        for commodity_id, spec in self.commodity_specs.items():
            # Calculate initial seasonal price
            current_month = datetime.fromtimestamp(current_time).strftime("%m")
            seasonal_multiplier = spec.seasonal_pattern.get(current_month, 1.0)
            initial_price = spec.base_price_per_unit * seasonal_multiplier
            
            # Create initial market conditions
            conditions = MarketConditions(
                commodity_id=commodity_id,
                timestamp=current_time,
                current_price=initial_price,
                daily_change=0.0,
                daily_change_percent=0.0,
                local_production_estimate=1000000.0,  # Base production estimate
                regional_production_estimate=50000000.0,
                carry_over_stocks=200000.0,
                expected_harvest=1200000.0,
                local_consumption=900000.0,
                export_demand=300000.0,
                processing_demand=400000.0,
                feed_demand=500000.0,
                trend=MarketTrend.NEUTRAL,
                volatility=PriceVolatility.MODERATE,
                volume_average_10day=25000.0,
                open_interest=150000,
                price_sma_20=initial_price,
                price_sma_50=initial_price,
                rsi_14=50.0,  # Neutral RSI
                bollinger_upper=initial_price * 1.02,
                bollinger_lower=initial_price * 0.98
            )
            
            self.market_conditions[commodity_id] = conditions
            self.daily_prices[commodity_id] = {}
            self.price_history[commodity_id] = []
    
    def _generate_initial_price_history(self):
        """Generate initial price history for technical analysis"""
        current_time = time.time()
        
        for commodity_id, spec in self.commodity_specs.items():
            history = []
            base_price = spec.base_price_per_unit
            
            # Generate 100 days of historical data
            for day in range(100, 0, -1):
                timestamp = current_time - (day * 24 * 3600)  # Days ago
                date_obj = datetime.fromtimestamp(timestamp)
                month_key = date_obj.strftime("%m")
                
                # Apply seasonal pattern
                seasonal_mult = spec.seasonal_pattern.get(month_key, 1.0)
                seasonal_price = base_price * seasonal_mult
                
                # Add random variation
                daily_change = self.price_rng.gauss(0, spec.typical_volatility * seasonal_price)
                price = seasonal_price + daily_change
                
                # Ensure price stays positive and reasonable
                price = max(price, seasonal_price * 0.5)
                price = min(price, seasonal_price * 1.5)
                
                # Create price history entry
                price_entry = PriceHistory(
                    timestamp=timestamp,
                    open_price=price * 0.999,
                    high_price=price * 1.001,
                    low_price=price * 0.999,
                    close_price=price,
                    volume=self.price_rng.gauss(25000, 5000)
                )
                
                history.append(price_entry)
                self.daily_prices[commodity_id][date_obj.strftime("%Y-%m-%d")] = price
            
            self.price_history[commodity_id] = history
            
            # Update current market conditions with latest price
            if history:
                latest = history[-1]
                self.market_conditions[commodity_id].current_price = latest.close_price
                self.market_conditions[commodity_id].price_sma_20 = latest.close_price
                self.market_conditions[commodity_id].price_sma_50 = latest.close_price
    
    def update_market_prices(self, delta_time: float):
        """Update market prices based on supply/demand and market factors"""
        current_time = time.time()
        
        # Only update prices every few seconds to simulate market timing
        if current_time - self.last_price_update < (1.0 / self.update_frequency):
            return
        
        self.last_price_update = current_time
        
        for commodity_id, conditions in self.market_conditions.items():
            spec = self.commodity_specs[commodity_id]
            
            # Calculate price movement factors
            price_change = self._calculate_price_change(commodity_id, spec, conditions)
            
            # Apply price change
            new_price = conditions.current_price + price_change
            
            # Ensure price stays within reasonable bounds
            min_price = spec.base_price_per_unit * 0.3
            max_price = spec.base_price_per_unit * 3.0
            new_price = max(min_price, min(max_price, new_price))
            
            # Calculate daily change metrics
            daily_change = new_price - conditions.current_price
            daily_change_percent = (daily_change / conditions.current_price) * 100 if conditions.current_price > 0 else 0
            
            # Update market conditions
            conditions.current_price = new_price
            conditions.daily_change = daily_change
            conditions.daily_change_percent = daily_change_percent
            conditions.timestamp = current_time
            
            # Update technical indicators
            self._update_technical_indicators(commodity_id, new_price)
            
            # Add to price history
            self._add_price_history_entry(commodity_id, new_price)
            
            # Emit price update event
            self.event_system.emit('price_updated', {
                'commodity_id': commodity_id,
                'new_price': new_price,
                'price_change': daily_change,
                'price_change_percent': daily_change_percent,
                'market_trend': conditions.trend.value,
                'volatility': conditions.volatility.value
            }, priority=EventPriority.NORMAL)
    
    def _calculate_price_change(self, commodity_id: str, spec: CommoditySpecification, 
                               conditions: MarketConditions) -> float:
        """Calculate price change based on multiple market factors"""
        
        # Base random movement
        base_volatility = spec.typical_volatility * self.market_volatility_factor
        random_change = self.price_rng.gauss(0, base_volatility * conditions.current_price)
        
        # Supply/demand fundamental factor
        supply = conditions.carry_over_stocks + conditions.expected_harvest
        demand = (conditions.local_consumption + conditions.export_demand + 
                 conditions.processing_demand + conditions.feed_demand)
        
        supply_demand_ratio = supply / demand if demand > 0 else 1.0
        fundamental_pressure = -0.1 * (supply_demand_ratio - 1.0) * conditions.current_price
        
        # Seasonal factor
        current_month = datetime.fromtimestamp(conditions.timestamp).strftime("%m")
        seasonal_mult = spec.seasonal_pattern.get(current_month, 1.0)
        
        # Previous month for seasonal momentum
        prev_month = datetime.fromtimestamp(conditions.timestamp - 2592000).strftime("%m")  # 30 days ago
        prev_seasonal_mult = spec.seasonal_pattern.get(prev_month, 1.0)
        seasonal_momentum = (seasonal_mult - prev_seasonal_mult) * conditions.current_price * 0.1
        
        # Weather impact factor
        weather_change = (self.weather_impact_factor - 1.0) * conditions.current_price * 0.05
        
        # Global economic sentiment
        sentiment_change = self.global_economic_sentiment * conditions.current_price * 0.02
        
        # Fuel price impact (transportation costs)
        fuel_impact = ((self.fuel_price_index - 100) / 100) * conditions.current_price * 0.01
        
        # Technical momentum (trend following)
        momentum_factor = 0.0
        if conditions.trend == MarketTrend.STRONG_BULLISH:
            momentum_factor = 0.003
        elif conditions.trend == MarketTrend.BULLISH:
            momentum_factor = 0.002
        elif conditions.trend == MarketTrend.WEAK_BULLISH:
            momentum_factor = 0.001
        elif conditions.trend == MarketTrend.WEAK_BEARISH:
            momentum_factor = -0.001
        elif conditions.trend == MarketTrend.BEARISH:
            momentum_factor = -0.002
        elif conditions.trend == MarketTrend.STRONG_BEARISH:
            momentum_factor = -0.003
        
        momentum_change = momentum_factor * conditions.current_price
        
        # Combine all factors
        total_change = (random_change + fundamental_pressure + seasonal_momentum + 
                       weather_change + sentiment_change + fuel_impact + momentum_change)
        
        return total_change
    
    def _update_technical_indicators(self, commodity_id: str, new_price: float):
        """Update technical analysis indicators"""
        conditions = self.market_conditions[commodity_id]
        history = self.price_history[commodity_id]
        
        if len(history) < 50:
            return  # Not enough history for full calculations
        
        # Get recent prices
        recent_prices = [entry.close_price for entry in history[-50:]] + [new_price]
        
        # Update Simple Moving Averages
        conditions.price_sma_20 = sum(recent_prices[-20:]) / 20
        conditions.price_sma_50 = sum(recent_prices[-50:]) / 50
        
        # Update RSI (Relative Strength Index)
        if len(recent_prices) >= 15:
            price_changes = []
            for i in range(1, 15):
                change = recent_prices[-i] - recent_prices[-i-1]
                price_changes.append(change)
            
            gains = [change for change in price_changes if change > 0]
            losses = [-change for change in price_changes if change < 0]
            
            avg_gain = sum(gains) / len(gains) if gains else 0.001
            avg_loss = sum(losses) / len(losses) if losses else 0.001
            
            rs = avg_gain / avg_loss
            conditions.rsi_14 = 100 - (100 / (1 + rs))
        
        # Update Bollinger Bands
        if len(recent_prices) >= 20:
            sma_20 = conditions.price_sma_20
            variance = sum((price - sma_20) ** 2 for price in recent_prices[-20:]) / 20
            std_dev = math.sqrt(variance)
            
            conditions.bollinger_upper = sma_20 + (2 * std_dev)
            conditions.bollinger_lower = sma_20 - (2 * std_dev)
        
        # Update trend based on moving averages and price action
        if new_price > conditions.price_sma_20 > conditions.price_sma_50:
            if new_price > conditions.bollinger_upper:
                conditions.trend = MarketTrend.STRONG_BULLISH
            else:
                conditions.trend = MarketTrend.BULLISH
        elif new_price > conditions.price_sma_20:
            conditions.trend = MarketTrend.WEAK_BULLISH
        elif new_price < conditions.price_sma_20 < conditions.price_sma_50:
            if new_price < conditions.bollinger_lower:
                conditions.trend = MarketTrend.STRONG_BEARISH
            else:
                conditions.trend = MarketTrend.BEARISH
        elif new_price < conditions.price_sma_20:
            conditions.trend = MarketTrend.WEAK_BEARISH
        else:
            conditions.trend = MarketTrend.NEUTRAL
        
        # Update volatility based on recent price movements
        if len(history) >= 10:
            recent_changes = []
            for i in range(1, 11):
                if i < len(history):
                    change_pct = abs((history[-i].close_price - history[-i-1].close_price) / history[-i-1].close_price)
                    recent_changes.append(change_pct)
            
            if recent_changes:
                avg_volatility = sum(recent_changes) / len(recent_changes)
                if avg_volatility > 0.15:
                    conditions.volatility = PriceVolatility.VERY_HIGH
                elif avg_volatility > 0.10:
                    conditions.volatility = PriceVolatility.HIGH
                elif avg_volatility > 0.05:
                    conditions.volatility = PriceVolatility.MODERATE
                elif avg_volatility > 0.02:
                    conditions.volatility = PriceVolatility.LOW
                else:
                    conditions.volatility = PriceVolatility.VERY_LOW
    
    def _add_price_history_entry(self, commodity_id: str, close_price: float):
        """Add new price history entry"""
        current_time = time.time()
        
        # Create new price history entry
        price_entry = PriceHistory(
            timestamp=current_time,
            open_price=close_price * 0.9995,  # Slight variation from close
            high_price=close_price * 1.0005,
            low_price=close_price * 0.9995,
            close_price=close_price,
            volume=self.price_rng.gauss(25000, 5000)
        )
        
        self.price_history[commodity_id].append(price_entry)
        
        # Keep only recent history (last 200 entries)
        if len(self.price_history[commodity_id]) > 200:
            self.price_history[commodity_id] = self.price_history[commodity_id][-200:]
        
        # Update daily prices
        date_str = datetime.fromtimestamp(current_time).strftime("%Y-%m-%d")
        self.daily_prices[commodity_id][date_str] = close_price
    
    def get_current_price(self, commodity_id: str, region: MarketRegion = MarketRegion.LOCAL) -> Optional[float]:
        """Get current market price for a commodity"""
        if commodity_id not in self.market_conditions:
            return None
        
        base_price = self.market_conditions[commodity_id].current_price
        spec = self.commodity_specs[commodity_id]
        
        # Apply regional price differential
        regional_adjustment = spec.regional_price_differentials.get(region, 0.0)
        
        return base_price + regional_adjustment
    
    def get_price_with_quality_adjustment(self, commodity_id: str, quality_grade: str, 
                                         region: MarketRegion = MarketRegion.LOCAL) -> Optional[float]:
        """Get price adjusted for quality grade"""
        base_price = self.get_current_price(commodity_id, region)
        if base_price is None:
            return None
        
        spec = self.commodity_specs[commodity_id]
        quality_adjustment = spec.quality_premium_schedule.get(quality_grade, 0.0)
        
        return base_price + quality_adjustment
    
    def calculate_basis(self, commodity_id: str, local_region: MarketRegion, 
                       reference_region: MarketRegion = MarketRegion.NATIONAL) -> Optional[float]:
        """Calculate basis (local price - futures price)"""
        local_price = self.get_current_price(commodity_id, local_region)
        reference_price = self.get_current_price(commodity_id, reference_region)
        
        if local_price is None or reference_price is None:
            return None
        
        return local_price - reference_price
    
    def get_price_forecast(self, commodity_id: str, days_ahead: int) -> Optional[Dict[str, float]]:
        """Generate price forecast based on current conditions and seasonality"""
        if commodity_id not in self.market_conditions:
            return None
        
        current_conditions = self.market_conditions[commodity_id]
        spec = self.commodity_specs[commodity_id]
        
        current_time = time.time()
        future_time = current_time + (days_ahead * 24 * 3600)
        
        # Get seasonal pattern for future date
        future_month = datetime.fromtimestamp(future_time).strftime("%m")
        future_seasonal = spec.seasonal_pattern.get(future_month, 1.0)
        
        current_month = datetime.fromtimestamp(current_time).strftime("%m")
        current_seasonal = spec.seasonal_pattern.get(current_month, 1.0)
        
        # Calculate seasonal adjustment
        seasonal_change = future_seasonal / current_seasonal
        
        # Estimate price based on trend and seasonality
        trend_multiplier = 1.0
        if current_conditions.trend == MarketTrend.STRONG_BULLISH:
            trend_multiplier = 1.0 + (0.02 * days_ahead / 30)  # 2% per month
        elif current_conditions.trend == MarketTrend.BULLISH:
            trend_multiplier = 1.0 + (0.01 * days_ahead / 30)  # 1% per month
        elif current_conditions.trend == MarketTrend.BEARISH:
            trend_multiplier = 1.0 - (0.01 * days_ahead / 30)  # -1% per month
        elif current_conditions.trend == MarketTrend.STRONG_BEARISH:
            trend_multiplier = 1.0 - (0.02 * days_ahead / 30)  # -2% per month
        
        # Calculate forecast price
        base_forecast = current_conditions.current_price * seasonal_change * trend_multiplier
        
        # Add confidence intervals based on volatility
        volatility_factor = spec.typical_volatility * math.sqrt(days_ahead / 365)  # Annualized volatility
        
        return {
            'forecast_price': base_forecast,
            'low_estimate': base_forecast * (1 - 1.96 * volatility_factor),  # 95% confidence interval
            'high_estimate': base_forecast * (1 + 1.96 * volatility_factor),
            'confidence_level': max(0.5, 1.0 - (days_ahead / 365))  # Confidence decreases over time
        }
    
    def trigger_market_event(self, event_type: MarketEvent, commodity_ids: List[str], 
                           impact_magnitude: float):
        """Trigger a market event that affects prices"""
        for commodity_id in commodity_ids:
            if commodity_id not in self.market_conditions:
                continue
            
            conditions = self.market_conditions[commodity_id]
            
            # Apply event impact
            if event_type == MarketEvent.WEATHER_SHOCK:
                self.weather_impact_factor = 1.0 + impact_magnitude
                # Weather shocks typically increase volatility
                if hasattr(conditions, 'volatility'):
                    if impact_magnitude > 0.1:
                        conditions.volatility = PriceVolatility.VERY_HIGH
                    elif impact_magnitude > 0.05:
                        conditions.volatility = PriceVolatility.HIGH
            
            elif event_type == MarketEvent.DEMAND_SHOCK:
                # Adjust demand factors
                conditions.export_demand *= (1.0 + impact_magnitude)
                conditions.processing_demand *= (1.0 + impact_magnitude)
            
            elif event_type == MarketEvent.SUPPLY_DISRUPTION:
                # Reduce expected harvest
                conditions.expected_harvest *= (1.0 - abs(impact_magnitude))
            
            elif event_type == MarketEvent.FUEL_PRICE_SHOCK:
                self.fuel_price_index += impact_magnitude * 20  # Convert to index points
            
            # Add event to current price history
            if self.price_history[commodity_id]:
                self.price_history[commodity_id][-1].market_events.append(event_type)
        
        # Emit market event
        self.event_system.emit('market_event_occurred', {
            'event_type': event_type.value,
            'affected_commodities': commodity_ids,
            'impact_magnitude': impact_magnitude,
            'timestamp': time.time()
        }, priority=EventPriority.HIGH)
    
    def update(self, delta_time: float):
        """Update dynamic pricing system"""
        if not self.initialized:
            return
        
        # Update market prices
        self.update_market_prices(delta_time)
        
        # Occasionally trigger random market events
        if self.event_rng.random() < 0.001:  # 0.1% chance per update
            self._trigger_random_market_event()
    
    def _trigger_random_market_event(self):
        """Trigger a random market event for realism"""
        events = [
            MarketEvent.WEATHER_SHOCK,
            MarketEvent.TRADE_NEWS,
            MarketEvent.DEMAND_SHOCK,
            MarketEvent.FUEL_PRICE_SHOCK
        ]
        
        event = self.event_rng.choice(events)
        commodity_ids = list(self.commodity_specs.keys())
        impact = self.event_rng.gauss(0, 0.05)  # Random impact around 5%
        
        self.trigger_market_event(event, commodity_ids, impact)
    
    def _handle_time_advanced(self, event_data: Dict[str, Any]):
        """Handle time advancement events"""
        # Update global economic sentiment gradually
        self.global_economic_sentiment += self.price_rng.gauss(0, 0.01)
        self.global_economic_sentiment = max(-1.0, min(1.0, self.global_economic_sentiment))
    
    def _handle_weather_event(self, event_data: Dict[str, Any]):
        """Handle weather events that affect markets"""
        event_type = event_data.get('event_type', '')
        severity = event_data.get('severity', 0.0)
        
        if event_type in ['drought', 'flood', 'hail', 'frost']:
            impact = severity * 0.1  # Convert severity to price impact
            commodity_ids = ['corn', 'soybeans', 'wheat']  # Crops affected by weather
            self.trigger_market_event(MarketEvent.WEATHER_SHOCK, commodity_ids, impact)
    
    def _handle_crop_harvested(self, event_data: Dict[str, Any]):
        """Handle crop harvest events that increase supply"""
        crop_type = event_data.get('crop_type', '')
        quantity = event_data.get('quantity_harvested', 0.0)
        
        if crop_type in self.market_conditions:
            # Increase local supply
            conditions = self.market_conditions[crop_type]
            conditions.local_production_estimate += quantity
            
            # Small negative price pressure from increased supply
            supply_pressure = quantity / 1000000.0  # Scale down impact
            self.trigger_market_event(MarketEvent.SUPPLY_DISRUPTION, [crop_type], -supply_pressure)
    
    def _handle_crop_planted(self, event_data: Dict[str, Any]):
        """Handle crop planting events that affect future supply expectations"""
        crop_type = event_data.get('crop_type', '')
        acres_planted = event_data.get('acres_planted', 0.0)
        
        if crop_type in self.market_conditions:
            # Increase expected harvest based on planted acres
            conditions = self.market_conditions[crop_type]
            # Rough estimate: 150 bushels per acre for corn, 50 for soybeans, 60 for wheat
            bushels_per_acre = {'corn': 150, 'soybeans': 50, 'wheat': 60}.get(crop_type, 100)
            additional_harvest = acres_planted * bushels_per_acre
            conditions.expected_harvest += additional_harvest
    
    def _handle_market_event(self, event_data: Dict[str, Any]):
        """Handle external market events"""
        # Process external market events (from other systems or player actions)
        pass
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get comprehensive market summary"""
        summary = {
            'timestamp': time.time(),
            'global_sentiment': self.global_economic_sentiment,
            'market_volatility': self.market_volatility_factor,
            'weather_factor': self.weather_impact_factor,
            'fuel_index': self.fuel_price_index,
            'commodities': {}
        }
        
        for commodity_id, conditions in self.market_conditions.items():
            summary['commodities'][commodity_id] = {
                'current_price': conditions.current_price,
                'daily_change': conditions.daily_change,
                'daily_change_percent': conditions.daily_change_percent,
                'trend': conditions.trend.value,
                'volatility': conditions.volatility.value,
                'volume': conditions.volume_average_10day,
                'rsi': conditions.rsi_14,
                'sma_20': conditions.price_sma_20,
                'sma_50': conditions.price_sma_50
            }
        
        return summary
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get dynamic pricing system statistics"""
        total_price_points = sum(len(history) for history in self.price_history.values())
        
        return {
            'commodities_tracked': len(self.commodity_specs),
            'total_price_history_points': total_price_points,
            'global_economic_sentiment': self.global_economic_sentiment,
            'market_volatility_factor': self.market_volatility_factor,
            'weather_impact_factor': self.weather_impact_factor,
            'fuel_price_index': self.fuel_price_index,
            'update_frequency': self.update_frequency
        }

# Global dynamic pricing system instance
_global_pricing_system: Optional[DynamicPricingSystem] = None

def get_dynamic_pricing_system() -> DynamicPricingSystem:
    """Get the global dynamic pricing system instance"""
    global _global_pricing_system
    if _global_pricing_system is None:
        _global_pricing_system = DynamicPricingSystem()
        _global_pricing_system.initialize()
    return _global_pricing_system

def initialize_dynamic_pricing_system() -> DynamicPricingSystem:
    """Initialize the global dynamic pricing system"""
    global _global_pricing_system
    _global_pricing_system = DynamicPricingSystem()
    _global_pricing_system.initialize()
    return _global_pricing_system

# Convenience functions
def get_commodity_price(commodity_id: str, region: MarketRegion = MarketRegion.LOCAL) -> Optional[float]:
    """Convenience function to get current commodity price"""
    return get_dynamic_pricing_system().get_current_price(commodity_id, region)

def get_price_forecast(commodity_id: str, days_ahead: int) -> Optional[Dict[str, float]]:
    """Convenience function to get price forecast"""
    return get_dynamic_pricing_system().get_price_forecast(commodity_id, days_ahead)

def trigger_market_event(event_type: MarketEvent, commodity_ids: List[str], impact: float):
    """Convenience function to trigger market events"""
    return get_dynamic_pricing_system().trigger_market_event(event_type, commodity_ids, impact)