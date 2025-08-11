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
STARTING_CASH = 0
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