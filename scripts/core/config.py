"""
Game Configuration Constants
All game settings and constants are defined here for easy tweaking.
"""

# Display Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Grid Settings
GRID_WIDTH = 16
GRID_HEIGHT = 16
TILE_SIZE = 32  # pixels per tile

# Game World Settings
STARTING_CASH = 100000  # Increased for building feature testing
FIRST_TIME_LOAN = 10000
LOAN_INTEREST_RATE = 0.05  # 5% annual
DAILY_SUBSIDY = 100
SUBSIDY_DAYS = 30
DAILY_UTILITIES = 20

# Employee Settings
BASE_EMPLOYEE_WAGE = 80  # Reduced from 100 to improve multi-employee viability
EMPLOYEE_SPEED = 2.0  # tiles per second
MAX_HUNGER = 100
MAX_THIRST = 100
MAX_REST = 100
HUNGER_DECAY_RATE = 1.0  # points per hour
THIRST_DECAY_RATE = 2.0  # points per hour
REST_DECAY_RATE = 1.5   # points per hour when working

# Crop Settings - Multiple Crop Types

# Universal growth stages for all crops
GROWTH_STAGES = ['seed', 'sprout', 'young', 'mature', 'harvestable']

# Crop definitions with different strategic profiles
CROP_TYPES = {
    'corn': {
        'name': 'Corn',
        'growth_time': 0.125,  # 3 game days (balanced option)
        'base_yield': 15,      # units per tile (balanced yield)
        'price_min': 3,        # stable pricing
        'price_max': 6,
        'seed_cost': 5,        # cost per seed
        'description': 'Balanced crop - steady growth and reliable income'
    },
    'tomatoes': {
        'name': 'Tomatoes', 
        'growth_time': 0.083,  # 2 game days (fast growth)
        'base_yield': 8,       # lower yield per tile
        'price_min': 4,        # higher price range
        'price_max': 10,
        'seed_cost': 8,        # more expensive seeds
        'description': 'Fast crop - quick turnaround but lower yield and higher risk'
    },
    'wheat': {
        'name': 'Wheat',
        'growth_time': 0.208,  # 5 game days (slow growth)
        'base_yield': 25,      # high bulk yield
        'price_min': 2,        # lower but stable pricing
        'price_max': 4,
        'seed_cost': 3,        # cheaper seeds
        'description': 'Bulk crop - slow growth but high volume and stable prices'
    }
}

# Default crop type for backwards compatibility
DEFAULT_CROP_TYPE = 'corn'

# Soil Health and Crop Rotation System
SOIL_NUTRIENTS = {
    'nitrogen': {'name': 'Nitrogen', 'max': 100},
    'phosphorus': {'name': 'Phosphorus', 'max': 100},
    'potassium': {'name': 'Potassium', 'max': 100}
}

# Crop nutrient effects (depletion and restoration)
CROP_SOIL_EFFECTS = {
    'corn': {
        'depletes': {'nitrogen': 25, 'phosphorus': 15, 'potassium': 20},  # Heavy feeder
        'restores': {},
        'category': 'heavy_feeder',
        'description': 'Heavy feeder - depletes soil nutrients significantly'
    },
    'tomatoes': {
        'depletes': {'nitrogen': 15, 'phosphorus': 20, 'potassium': 15},  # Balanced consumption
        'restores': {},
        'category': 'balanced_feeder', 
        'description': 'Balanced feeder - moderate nutrient consumption'
    },
    'wheat': {
        'depletes': {'nitrogen': 10, 'phosphorus': 8, 'potassium': 12},   # Light feeder
        'restores': {},
        'category': 'light_feeder',
        'description': 'Light feeder - minimal nutrient depletion'
    }
}

# Crop rotation bonuses (educational agricultural principles)
ROTATION_BONUSES = {
    'after_heavy_feeder': {
        'applicable_to': ['wheat', 'tomatoes'],  # Light feeders benefit after heavy feeders
        'yield_bonus': 0.15,  # +15% yield
        'quality_bonus': 0.10,  # +10% quality
        'description': 'Crop rotation bonus: Following heavy feeder with light feeder'
    },
    'diverse_rotation': {
        'applicable_to': ['corn', 'tomatoes', 'wheat'],  # Any crop in diverse rotation
        'yield_bonus': 0.08,  # +8% yield  
        'quality_bonus': 0.05,  # +5% quality
        'description': 'Diverse rotation bonus: Growing different crop types builds soil health'
    },
    'soil_rest': {
        'applicable_to': ['corn', 'tomatoes', 'wheat'],  # Any crop after soil rest
        'yield_bonus': 0.20,  # +20% yield
        'quality_bonus': 0.15,  # +15% quality  
        'description': 'Soil rest bonus: Letting land recover between plantings'
    }
}

# Soil health thresholds for visual/gameplay feedback
SOIL_HEALTH_LEVELS = {
    'excellent': {'min': 80, 'color': (100, 255, 100), 'bonus_multiplier': 1.1},
    'good': {'min': 60, 'color': (150, 255, 150), 'bonus_multiplier': 1.0},
    'fair': {'min': 40, 'color': (255, 255, 100), 'bonus_multiplier': 0.95},
    'poor': {'min': 20, 'color': (255, 150, 100), 'bonus_multiplier': 0.85},
    'depleted': {'min': 0, 'color': (255, 100, 100), 'bonus_multiplier': 0.7}
}

# Legacy constants for backwards compatibility
CORN_GROWTH_STAGES = GROWTH_STAGES
CORN_GROWTH_TIME = CROP_TYPES['corn']['growth_time']
CORN_BASE_YIELD = CROP_TYPES['corn']['base_yield']
CORN_PRICE_MIN = CROP_TYPES['corn']['price_min']
CORN_PRICE_MAX = CROP_TYPES['corn']['price_max']

# Time Settings
MINUTES_PER_GAME_DAY = 20  # real minutes
WORK_START_HOUR = 5  # 5 AM
WORK_END_HOUR = 18    # 6 PM

# Enhanced Task System Feature Flags
# These control the rollout of the new task assignment system
ENABLE_ENHANCED_TASK_SYSTEM = False  # Main feature flag - False = use legacy system
ENABLE_EMPLOYEE_SPECIALIZATIONS = True  # Employee roles and skills - Phase 2A ENABLED
ENABLE_WORK_ORDERS = False  # Advanced work order system
ENABLE_TASK_PRIORITIES = False  # Priority-based task assignment
ENABLE_EQUIPMENT_REQUIREMENTS = False  # Equipment and certification requirements
ENABLE_DYNAMIC_TASK_GENERATION = False  # Auto-generated work orders

# Enhanced Task System Configuration
ENHANCED_TASK_CONFIG = {
    'auto_assign_tasks': True,  # Automatically assign tasks to best-suited employees
    'respect_employee_preferences': True,  # Consider employee task preferences
    'allow_skill_development': True,  # Employees can learn new skills over time
    'require_certifications': False,  # Require certifications for advanced tasks
    'enable_equipment_system': False,  # Equipment requirements and maintenance
    'show_efficiency_indicators': True,  # Show employee efficiency for tasks
    'enable_task_tutorials': True,  # Show explanations for new task system
}

# Colors (RGB)
COLORS = {
    'background': (34, 34, 34),
    'grid_line': (60, 60, 60),
    'tile_soil': (101, 67, 33),
    'tile_tilled': (139, 90, 43),
    'tile_planted': (34, 89, 34),
    'tile_water': (64, 164, 223),
    'employee': (255, 200, 100),
    'ui_background': (50, 50, 50),
    'ui_text': (255, 255, 255),
    'ui_button': (70, 70, 70),
    'ui_button_hover': (100, 100, 100),
    'money_positive': (100, 255, 100),
    'money_negative': (255, 100, 100),
}

# Farm Specialization System
FARM_SPECIALIZATIONS = {
    'none': {
        'name': 'Unspecialized Farm',
        'description': 'Basic farming operations without specialization bonuses',
        'cost': 0,  # Starting specialization
        'bonuses': {}
    },
    'grain': {
        'name': 'Grain Farm',
        'description': 'Specialized in bulk grain production and storage efficiency',
        'cost': 2500,  # Cost to specialize
        'requirements': {
            'wheat_harvested': 100,  # Must have harvested 100+ wheat
            'storage_capacity': 200   # Must have expanded storage
        },
        'bonuses': {
            'wheat_yield_multiplier': 1.25,  # +25% wheat yield
            'bulk_storage_efficiency': 1.15,  # +15% storage efficiency
            'grain_growth_speed': 1.20,       # +20% faster grain growth
            'grain_price_bonus': 1.10         # +10% grain sale prices
        },
        'description_long': 'Focus on large-scale grain production with enhanced wheat yields and storage systems.'
    },
    'market_garden': {
        'name': 'Market Garden',
        'description': 'Specialized in high-value premium crops and quality production',
        'cost': 3000,  # Higher cost for premium specialization
        'requirements': {
            'tomatoes_harvested': 75,   # Must have grown premium crops
            'average_crop_quality': 1.2  # Must maintain quality standards
        },
        'bonuses': {
            'tomato_yield_multiplier': 1.30,   # +30% tomato yield
            'premium_crop_quality': 1.20,      # +20% crop quality
            'harvest_speed_bonus': 1.15,       # +15% faster harvest
            'premium_price_bonus': 1.25,       # +25% premium crop prices
            'soil_nutrient_efficiency': 1.25   # +25% better nutrient use
        },
        'description_long': 'Maximize profits through high-quality premium crops and efficient market timing.'
    },
    'diversified': {
        'name': 'Diversified Farm',
        'description': 'Specialized in sustainable crop rotation and soil health management',
        'cost': 2000,  # Educational/sustainable focus
        'requirements': {
            'rotation_cycles_completed': 3,  # Must complete rotation cycles
            'soil_health_average': 80        # Must maintain good soil health
        },
        'bonuses': {
            'rotation_bonus_multiplier': 1.35,  # +35% rotation bonus multiplier
            'soil_rest_recovery_speed': 1.20,   # +20% faster soil recovery
            'overall_crop_quality': 1.15,       # +15% overall quality bonus
            'advanced_rotation_unlocked': True, # Access to advanced rotations
            'sustainability_bonus': 1.10        # +10% long-term yield sustainability
        },
        'description_long': 'Master sustainable agriculture through advanced rotation and soil management techniques.'
    }
}

# Specialization unlock conditions and progression
SPECIALIZATION_PROGRESSION = {
    'tracking_stats': [
        'wheat_harvested', 'tomatoes_harvested', 'corn_harvested',
        'rotation_cycles_completed', 'total_crops_sold',
        'storage_capacity_purchased', 'soil_health_average'
    ],
    'notification_thresholds': {
        'grain_available': {'wheat_harvested': 80, 'storage_capacity': 150},
        'market_garden_available': {'tomatoes_harvested': 60, 'average_crop_quality': 1.1},
        'diversified_available': {'rotation_cycles_completed': 2, 'soil_health_average': 70}
    }
}

# Weather & Seasons System Configuration
SEASON_LENGTH_DAYS = 30  # Days per season (30 days = ~10 hour seasons at 20min/day)
WEATHER_EVENT_PROBABILITY = 0.15  # 15% chance per day for weather events

# Weather Effects Configuration
WEATHER_GROWTH_EFFECTS = {
    'rain': {'growth_rate': 1.2, 'yield_modifier': 1.1},      # +20% growth, +10% yield
    'drought': {'growth_rate': 0.7, 'yield_modifier': 0.8},   # -30% growth, -20% yield  
    'frost': {'growth_rate': 0.3, 'yield_modifier': 0.6},     # -70% growth, -40% yield
    'heat_wave': {'growth_rate': 0.8, 'yield_modifier': 0.9}, # -20% growth, -10% yield
    'storm': {'growth_rate': 0.9, 'yield_modifier': 0.85}     # -10% growth, -15% yield
}

# Seasonal Crop Planting Windows (educational realism)
SEASONAL_CROP_WINDOWS = {
    'corn': ['spring', 'summer'],           # Warm-season crop
    'tomatoes': ['spring', 'summer'],       # Heat-loving crop
    'wheat': ['fall', 'winter', 'spring']   # Cool-season crop
}

# Off-season planting penalties for educational gameplay
OFF_SEASON_PLANTING_PENALTY = 0.7  # 30% reduction in growth/yield

# Irrigation System Configuration
IRRIGATION_WATER_COST_PER_TILE = 5   # Daily cost per irrigated tile during drought
IRRIGATION_DROUGHT_MITIGATION = 0.3  # How much irrigation helps during drought
IRRIGATION_SYSTEM_COST = 150         # Cost to install irrigation per tile

# Weather UI Colors
WEATHER_COLORS = {
    'spring': (100, 200, 100),    # Light green for spring
    'summer': (255, 200, 50),     # Golden yellow for summer  
    'fall': (200, 150, 50),       # Orange-brown for fall
    'winter': (150, 200, 255),    # Light blue for winter
    'clear': (255, 255, 255),     # White for clear weather
    'rain': (100, 150, 255),      # Blue for rain
    'drought': (255, 150, 100),   # Orange-red for drought
    'frost': (200, 200, 255),     # Light purple for frost
    'heat_wave': (255, 100, 100), # Red for heat wave
    'storm': (150, 150, 150)      # Gray for storms
}