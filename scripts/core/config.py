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