"""
Multi-Crop Framework - Advanced Crop Management for AgriFun Agricultural Simulation

This system provides comprehensive crop variety management with genetic systems, breeding,
crop families, and unlimited expansion capabilities. Builds upon the Phase 2 Crop System
to provide scientific accuracy and educational value about plant genetics and agriculture.

Key Features:
- Unlimited crop types and varieties with data-driven definitions
- Genetic system with traits, breeding, and inheritance
- Crop family relationships and companion planting
- Advanced growth stages with variety-specific characteristics
- Seed genetics and quality tracking
- Breeding programs and variety development
- Market differentiation and specialty crops
- Disease and pest resistance breeding

Scientific Features:
- Mendelian genetics with dominant/recessive traits
- Hybrid vigor and inbreeding depression
- Crop rotation benefits and soil relationships
- Companion planting and allelopathy
- Genetic diversity and conservation
- Traditional vs. modern varieties
- Open-pollinated vs. hybrid varieties
- Heirloom and heritage variety preservation

Integration Features:
- Seamless integration with Phase 2 Crop System
- Market system integration for variety premiums
- Employee system integration for breeding expertise
- Time system integration for breeding cycles
- Save/load system integration for genetic data

Usage Example:
    # Initialize multi-crop framework
    multicrop = MultiCropFramework()
    await multicrop.initialize()
    
    # Create new variety
    variety_id = await multicrop.create_variety('tomato_cherry_red', parent_varieties=['tomato_cherry', 'tomato_red'])
    
    # Breed crops
    breeding_program = await multicrop.start_breeding_program('drought_resistant_corn', target_traits=['drought_tolerance'])
    
    # Plant specialty crops
    crop_id = await multicrop.plant_specialty_crop('heirloom_tomato_brandywine', (10, 12))
"""

import time
import random
import math
from typing import Dict, List, Set, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

# Import Phase 1 architecture
from scripts.core.entity_component_system import System, Entity, Component
from scripts.core.advanced_event_system import get_event_system, EventPriority
from scripts.core.time_management import get_time_manager, Season
from scripts.core.advanced_config_system import get_configuration_manager
from scripts.core.content_registry import get_content_registry

# Import Phase 2 systems
from scripts.systems.economy_system import get_economy_system
from scripts.systems.employee_system import get_employee_system
from scripts.systems.crop_system import get_crop_system, CropType, CropVariety, GrowthStage


class CropFamily(Enum):
    """Botanical families for crop classification"""
    SOLANACEAE = "solanaceae"        # Tomatoes, potatoes, peppers, eggplant
    BRASSICACEAE = "brassicaceae"    # Cabbage, broccoli, cauliflower, kale
    LEGUMINOSAE = "leguminosae"      # Beans, peas, lentils, soybeans
    CUCURBITACEAE = "cucurbitaceae"  # Cucumber, squash, melons, pumpkins
    GRAMINEAE = "gramineae"          # Corn, wheat, rice, oats, barley
    UMBELLIFERAE = "umbelliferae"    # Carrots, celery, parsley, dill
    COMPOSITAE = "compositae"        # Lettuce, sunflowers, artichokes
    CHENOPODIACEAE = "chenopodiaceae" # Beets, spinach, chard
    ALLIUM = "allium"                # Onions, garlic, leeks, chives


class GeneticTrait(Enum):
    """Genetic traits that affect crop characteristics"""
    YIELD_POTENTIAL = "yield_potential"
    DISEASE_RESISTANCE = "disease_resistance"
    PEST_RESISTANCE = "pest_resistance"
    DROUGHT_TOLERANCE = "drought_tolerance"
    COLD_TOLERANCE = "cold_tolerance"
    HEAT_TOLERANCE = "heat_tolerance"
    MATURITY_SPEED = "maturity_speed"
    FRUIT_SIZE = "fruit_size"
    FRUIT_COLOR = "fruit_color"
    FLAVOR_INTENSITY = "flavor_intensity"
    STORAGE_LIFE = "storage_life"
    NUTRIENT_CONTENT = "nutrient_content"
    PLANT_HEIGHT = "plant_height"
    ROOT_DEPTH = "root_depth"
    NITROGEN_FIXATION = "nitrogen_fixation"


class VarietyType(Enum):
    """Types of crop varieties"""
    HEIRLOOM = "heirloom"            # Traditional open-pollinated varieties
    HYBRID = "hybrid"                # F1 hybrids with hybrid vigor
    OPEN_POLLINATED = "open_pollinated"  # Modern open-pollinated varieties
    GENETICALLY_MODIFIED = "genetically_modified"  # GMO varieties
    LANDRACE = "landrace"            # Local adapted varieties
    BREEDING_LINE = "breeding_line"   # Experimental varieties in development


class BreedingObjective(Enum):
    """Objectives for breeding programs"""
    YIELD_IMPROVEMENT = "yield_improvement"
    DISEASE_RESISTANCE = "disease_resistance"
    CLIMATE_ADAPTATION = "climate_adaptation"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    SPECIALTY_MARKET = "specialty_market"
    CONSERVATION = "conservation"


@dataclass
class GeneticAllele:
    """Individual genetic allele with dominance and effect"""
    allele_id: str
    trait: GeneticTrait
    dominance: float = 0.5  # 0.0 = fully recessive, 1.0 = fully dominant
    effect_strength: float = 1.0  # Magnitude of effect
    beneficial: bool = True  # Whether this allele is beneficial
    
    def get_phenotype_contribution(self, is_homozygous: bool = False) -> float:
        """Calculate phenotype contribution of this allele"""
        base_effect = self.effect_strength
        
        # Homozygous advantage/disadvantage
        if is_homozygous:
            if self.beneficial:
                base_effect *= 1.2  # Homozygous advantage
            else:
                base_effect *= 0.8  # Homozygous disadvantage for negative traits
        
        return base_effect * (1.0 if self.beneficial else -1.0)


@dataclass
class GeneticProfile:
    """Complete genetic profile for a crop variety"""
    variety_id: str
    parent_varieties: List[str] = field(default_factory=list)
    generation: int = 1  # F1, F2, etc.
    
    # Genetic composition
    alleles: Dict[GeneticTrait, List[GeneticAllele]] = field(default_factory=dict)
    genetic_diversity: float = 1.0  # 0-1, affects stability and adaptation
    inbreeding_coefficient: float = 0.0  # 0-1, affects vigor
    
    # Breeding information
    breeding_date: Optional[int] = None  # Game time when bred
    breeder_employee_id: Optional[str] = None
    breeding_objective: Optional[BreedingObjective] = None
    
    # Performance tracking
    field_performance: Dict[str, float] = field(default_factory=dict)
    stability_rating: float = 1.0  # How consistent performance is
    adaptation_zones: List[str] = field(default_factory=list)
    
    def get_trait_value(self, trait: GeneticTrait) -> float:
        """Calculate expressed trait value from genetic composition"""
        if trait not in self.alleles or not self.alleles[trait]:
            return 0.5  # Neutral baseline
        
        allele_list = self.alleles[trait]
        
        if len(allele_list) == 1:
            # Homozygous
            return allele_list[0].get_phenotype_contribution(is_homozygous=True)
        elif len(allele_list) == 2:
            # Heterozygous - calculate dominance interaction
            allele1, allele2 = allele_list
            
            # Determine which allele is more dominant
            if allele1.dominance > allele2.dominance:
                dominant, recessive = allele1, allele2
            else:
                dominant, recessive = allele2, allele1
            
            # Calculate expression based on dominance
            dominance_ratio = dominant.dominance / (dominant.dominance + recessive.dominance)
            
            expression = (dominant.get_phenotype_contribution() * dominance_ratio + 
                         recessive.get_phenotype_contribution() * (1 - dominance_ratio))
            
            # Hybrid vigor for beneficial heterozygous combinations
            if allele1.beneficial and allele2.beneficial:
                expression *= 1.1  # 10% hybrid vigor
            
            return expression
        else:
            # Multiple alleles (complex trait)
            total_expression = sum(allele.get_phenotype_contribution() for allele in allele_list)
            return total_expression / len(allele_list)
    
    def get_overall_fitness(self) -> float:
        """Calculate overall genetic fitness of the variety"""
        fitness_traits = [
            GeneticTrait.YIELD_POTENTIAL,
            GeneticTrait.DISEASE_RESISTANCE,
            GeneticTrait.DROUGHT_TOLERANCE,
            GeneticTrait.STORAGE_LIFE
        ]
        
        fitness_scores = []
        for trait in fitness_traits:
            trait_value = self.get_trait_value(trait)
            fitness_scores.append(max(0.0, trait_value))
        
        base_fitness = sum(fitness_scores) / len(fitness_scores)
        
        # Inbreeding depression
        inbreeding_penalty = self.inbreeding_coefficient * 0.3
        
        # Genetic diversity bonus
        diversity_bonus = self.genetic_diversity * 0.1
        
        return max(0.1, base_fitness - inbreeding_penalty + diversity_bonus)


@dataclass
class CropCompanionship:
    """Defines beneficial/detrimental relationships between crops"""
    primary_crop: str
    companion_crop: str
    relationship_type: str  # "beneficial", "neutral", "detrimental"
    effect_strength: float = 1.0  # Magnitude of effect
    
    # Specific benefits/detriments
    yield_modifier: float = 1.0
    disease_resistance_modifier: float = 1.0
    pest_resistance_modifier: float = 1.0
    soil_improvement: float = 0.0
    
    # Distance requirements
    optimal_distance: float = 1.0  # Tiles
    max_effective_distance: float = 3.0
    
    # Mechanism of action
    mechanism: str = "unknown"  # "nitrogen_fixation", "pest_deterrent", "allelopathy", etc.
    
    def get_effect_at_distance(self, distance: float) -> float:
        """Calculate companionship effect based on distance"""
        if distance > self.max_effective_distance:
            return 1.0  # No effect
        
        # Optimal distance gives full effect
        if distance <= self.optimal_distance:
            return self.effect_strength
        
        # Linear falloff beyond optimal distance
        falloff = (self.max_effective_distance - distance) / (self.max_effective_distance - self.optimal_distance)
        return 1.0 + (self.effect_strength - 1.0) * falloff


@dataclass
class BreedingProgram:
    """Manages a breeding program for developing new varieties"""
    program_id: str
    program_name: str
    objective: BreedingObjective
    target_traits: List[GeneticTrait]
    
    # Parent varieties
    parent_varieties: List[str]
    current_generation: int = 1
    
    # Progress tracking
    started_time: int = 0  # Game time
    expected_completion_time: int = 0
    progress: float = 0.0  # 0-1
    
    # Resources
    assigned_employee_id: Optional[str] = None
    allocated_plots: List[Tuple[int, int]] = field(default_factory=list)
    annual_budget: float = 5000.0
    total_invested: float = 0.0
    
    # Results
    candidate_varieties: List[str] = field(default_factory=list)
    successful_varieties: List[str] = field(default_factory=list)
    
    # Performance metrics
    selection_pressure: float = 0.3  # Proportion of plants selected each generation
    heritability_estimates: Dict[GeneticTrait, float] = field(default_factory=dict)
    genetic_gain_per_cycle: Dict[GeneticTrait, float] = field(default_factory=dict)
    
    def get_expected_cycles(self) -> int:
        """Calculate expected breeding cycles needed"""
        base_cycles = {
            BreedingObjective.YIELD_IMPROVEMENT: 6,
            BreedingObjective.DISEASE_RESISTANCE: 4,
            BreedingObjective.CLIMATE_ADAPTATION: 5,
            BreedingObjective.QUALITY_ENHANCEMENT: 4,
            BreedingObjective.SPECIALTY_MARKET: 3,
            BreedingObjective.CONSERVATION: 2
        }.get(self.objective, 5)
        
        # Adjust based on number of target traits
        trait_complexity = len(self.target_traits)
        return base_cycles + max(0, trait_complexity - 2)
    
    def update_progress(self, hours_passed: float, employee_efficiency: float = 1.0):
        """Update breeding program progress"""
        if self.progress >= 1.0:
            return
        
        # Calculate progress rate based on resources and complexity
        base_progress_rate = 1.0 / (self.get_expected_cycles() * 365 * 24)  # Per hour
        
        # Employee skill affects progress
        skill_factor = employee_efficiency
        
        # Budget affects progress (diminishing returns)
        budget_factor = min(2.0, 1.0 + math.log10(max(1.0, self.annual_budget / 1000.0)))
        
        # Plot availability affects progress
        plot_factor = min(1.5, len(self.allocated_plots) / 10.0)
        
        actual_progress_rate = base_progress_rate * skill_factor * budget_factor * plot_factor
        self.progress = min(1.0, self.progress + actual_progress_rate * hours_passed)


@dataclass
class AdvancedCropVariety(CropVariety):
    """Extended crop variety with genetic and botanical information"""
    # Botanical classification
    family: CropFamily = CropFamily.SOLANACEAE
    genus: str = "Unknown"
    species: str = "unknown"
    cultivar: str = ""
    
    # Genetic information
    genetic_profile: Optional[GeneticProfile] = None
    variety_type: VarietyType = VarietyType.OPEN_POLLINATED
    chromosome_count: int = 24  # Diploid default
    
    # Origin and history
    origin_country: str = "Unknown"
    development_year: int = 2000
    developer: str = "Unknown"
    patent_status: str = "public_domain"
    
    # Market characteristics
    market_class: str = "standard"
    premium_multiplier: float = 1.0
    specialty_markets: List[str] = field(default_factory=list)
    certification_eligible: List[str] = field(default_factory=list)  # "organic", "non_gmo", etc.
    
    # Growing characteristics
    companion_crops: List[str] = field(default_factory=list)
    antagonistic_crops: List[str] = field(default_factory=list)
    rotation_benefits: Dict[str, float] = field(default_factory=dict)
    allelopathic_effects: Dict[str, float] = field(default_factory=dict)
    
    # Seed characteristics
    seed_size: float = 1.0  # Relative size
    seed_weight: float = 1.0  # Grams per 1000 seeds
    germination_rate: float = 0.85  # 0-1
    seed_longevity_years: int = 3
    pollination_type: str = "self_pollinated"  # "self", "cross", "both"
    
    # Advanced growing requirements
    photoperiod_sensitivity: str = "day_neutral"  # "short_day", "long_day", "day_neutral"
    vernalization_required: bool = False
    mycorrhizal_associations: List[str] = field(default_factory=list)
    
    def get_genetic_yield_potential(self) -> float:
        """Calculate yield potential based on genetics"""
        if not self.genetic_profile:
            return self.base_yield_per_plant
        
        yield_trait = self.genetic_profile.get_trait_value(GeneticTrait.YIELD_POTENTIAL)
        genetic_multiplier = 0.5 + yield_trait  # 0.5 to 1.5 range
        
        return self.base_yield_per_plant * genetic_multiplier
    
    def get_disease_resistance(self, disease_name: str) -> float:
        """Get genetic disease resistance for specific disease"""
        if not self.genetic_profile:
            return self.disease_resistance.get(disease_name, 0.5)
        
        genetic_resistance = self.genetic_profile.get_trait_value(GeneticTrait.DISEASE_RESISTANCE)
        base_resistance = self.disease_resistance.get(disease_name, 0.5)
        
        return min(1.0, base_resistance + genetic_resistance * 0.3)
    
    def calculate_companion_effect(self, companion_variety: str, distance: float) -> Dict[str, float]:
        """Calculate companion planting effects"""
        effects = {
            'yield_modifier': 1.0,
            'disease_resistance': 1.0,
            'pest_resistance': 1.0,
            'soil_health': 0.0
        }
        
        # Check if this is a known companion
        if companion_variety in self.companion_crops:
            # Beneficial companion
            distance_factor = max(0.0, 1.0 - distance / 5.0)  # Effect diminishes with distance
            
            effects['yield_modifier'] = 1.0 + (0.15 * distance_factor)  # Up to 15% yield boost
            effects['disease_resistance'] = 1.0 + (0.1 * distance_factor)
            effects['pest_resistance'] = 1.0 + (0.2 * distance_factor)
            
        elif companion_variety in self.antagonistic_crops:
            # Detrimental companion
            distance_factor = max(0.0, 1.0 - distance / 3.0)  # Negative effect at closer range
            
            effects['yield_modifier'] = 1.0 - (0.2 * distance_factor)  # Up to 20% yield reduction
            effects['disease_resistance'] = 1.0 - (0.1 * distance_factor)
        
        return effects


class MultiCropFramework(System):
    """Advanced multi-crop framework with genetic systems and breeding"""
    
    def __init__(self):
        super().__init__()
        self.system_name = "multicrop_framework"
        
        # Core system references
        self.event_system = get_event_system()
        self.time_manager = get_time_manager()
        self.config_manager = get_configuration_manager()
        self.content_registry = get_content_registry()
        
        # Phase 2 system references
        self.economy_system = get_economy_system()
        self.employee_system = get_employee_system()
        self.crop_system = get_crop_system()
        
        # Crop variety management
        self.advanced_varieties: Dict[str, AdvancedCropVariety] = {}
        self.genetic_profiles: Dict[str, GeneticProfile] = {}
        self.crop_families: Dict[CropFamily, List[str]] = {}
        
        # Companion planting system
        self.companion_relationships: Dict[str, List[CropCompanionship]] = {}
        self.allelopathy_database: Dict[str, Dict[str, float]] = {}
        
        # Breeding system
        self.active_breeding_programs: Dict[str, BreedingProgram] = {}
        self.breeding_history: List[Dict[str, Any]] = []
        self.genetic_library: Dict[str, List[GeneticAllele]] = {}
        
        # Market differentiation
        self.specialty_markets: Dict[str, Dict[str, Any]] = {}
        self.variety_premiums: Dict[str, float] = {}
        self.certification_programs: Dict[str, Dict[str, Any]] = {}
        
        # Conservation and preservation
        self.heirloom_varieties: Set[str] = set()
        self.endangered_varieties: Set[str] = set()
        self.conservation_programs: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.varieties_created: int = 0
        self.breeding_programs_completed: int = 0
        self.genetic_diversity_index: float = 1.0
        self.conservation_success_rate: float = 0.0
        
        # Configuration
        self.enable_genetics: bool = True
        self.breeding_complexity: str = "realistic"  # "simple", "realistic", "advanced"
        self.market_differentiation: bool = True
        self.conservation_focus: bool = True
    
    async def initialize(self):
        """Initialize the multi-crop framework"""
        # Load configuration
        await self._load_multicrop_configuration()
        
        # Initialize genetic library
        await self._initialize_genetic_library()
        
        # Initialize advanced crop varieties
        await self._initialize_advanced_varieties()
        
        # Initialize companion planting database
        await self._initialize_companion_database()
        
        # Initialize specialty markets
        await self._initialize_specialty_markets()
        
        # Subscribe to events
        self.event_system.subscribe('crop_planted', self._on_crop_planted)
        self.event_system.subscribe('crop_harvested', self._on_crop_harvested)
        self.event_system.subscribe('time_season_changed', self._on_season_changed)
        self.event_system.subscribe('employee_hired', self._on_employee_hired)
        
        self.logger.info("Multi-Crop Framework initialized successfully")
    
    async def _load_multicrop_configuration(self):
        """Load multi-crop framework configuration"""
        try:
            multicrop_config = self.config_manager.get_section('multicrop_framework')
            
            self.enable_genetics = multicrop_config.get('enable_genetics', True)
            self.breeding_complexity = multicrop_config.get('breeding_complexity', 'realistic')
            self.market_differentiation = multicrop_config.get('market_differentiation', True)
            self.conservation_focus = multicrop_config.get('conservation_focus', True)
            
        except Exception as e:
            self.logger.warning(f"Failed to load multicrop configuration: {e}")
    
    async def _initialize_genetic_library(self):
        """Initialize the genetic allele library"""
        # Create genetic alleles for each trait
        for trait in GeneticTrait:
            self.genetic_library[trait.value] = []
            
            # Create multiple alleles per trait with different characteristics
            for i in range(5):  # 5 alleles per trait
                allele = GeneticAllele(
                    allele_id=f"{trait.value}_allele_{i+1}",
                    trait=trait,
                    dominance=random.uniform(0.1, 0.9),
                    effect_strength=random.uniform(0.5, 1.5),
                    beneficial=random.choice([True, True, True, False])  # 75% beneficial
                )
                self.genetic_library[trait.value].append(allele)
        
        self.logger.info(f"Initialized genetic library with {sum(len(alleles) for alleles in self.genetic_library.values())} alleles")
    
    async def _initialize_advanced_varieties(self):
        """Initialize advanced crop varieties with genetic profiles"""
        # Get base varieties from crop system
        base_varieties = self.crop_system.crop_varieties
        
        for variety_id, base_variety in base_varieties.items():
            # Create advanced variety
            advanced_variety = await self._create_advanced_variety_from_base(base_variety)
            self.advanced_varieties[variety_id] = advanced_variety
            
            # Create genetic profile
            genetic_profile = await self._create_base_genetic_profile(variety_id)
            self.genetic_profiles[variety_id] = genetic_profile
            advanced_variety.genetic_profile = genetic_profile
            
            # Organize by family
            family = advanced_variety.family
            if family not in self.crop_families:
                self.crop_families[family] = []
            self.crop_families[family].append(variety_id)
        
        # Create additional specialty varieties
        await self._create_specialty_varieties()
        
        self.logger.info(f"Initialized {len(self.advanced_varieties)} advanced crop varieties")
    
    async def _create_advanced_variety_from_base(self, base_variety: CropVariety) -> AdvancedCropVariety:
        """Convert base variety to advanced variety"""
        # Determine family based on crop type
        family_mapping = {
            CropType.TOMATOES: CropFamily.SOLANACEAE,
            CropType.POTATOES: CropFamily.SOLANACEAE,
            CropType.CORN: CropFamily.GRAMINEAE,
            CropType.WHEAT: CropFamily.GRAMINEAE,
            CropType.SOYBEANS: CropFamily.LEGUMINOSAE,
            CropType.BEANS: CropFamily.LEGUMINOSAE,
            CropType.LETTUCE: CropFamily.COMPOSITAE,
            CropType.CARROTS: CropFamily.UMBELLIFERAE,
            CropType.ONIONS: CropFamily.ALLIUM,
            CropType.PEPPERS: CropFamily.SOLANACEAE
        }
        
        family = family_mapping.get(base_variety.crop_type, CropFamily.SOLANACEAE)
        
        # Create advanced variety with additional properties
        advanced_variety = AdvancedCropVariety(
            variety_id=base_variety.variety_id,
            crop_type=base_variety.crop_type,
            variety_name=base_variety.variety_name,
            description=base_variety.description,
            days_to_maturity=base_variety.days_to_maturity,
            growth_stages_duration=base_variety.growth_stages_duration,
            min_temperature=base_variety.min_temperature,
            max_temperature=base_variety.max_temperature,
            optimal_temperature_range=base_variety.optimal_temperature_range,
            water_requirements=base_variety.water_requirements,
            light_requirements=base_variety.light_requirements,
            preferred_soil_types=base_variety.preferred_soil_types,
            optimal_ph_range=base_variety.optimal_ph_range,
            nutrient_requirements=base_variety.nutrient_requirements,
            base_yield_per_plant=base_variety.base_yield_per_plant,
            yield_quality_factors=base_variety.yield_quality_factors,
            market_value_multiplier=base_variety.market_value_multiplier,
            disease_resistance=base_variety.disease_resistance,
            pest_resistance=base_variety.pest_resistance,
            drought_tolerance=base_variety.drought_tolerance,
            cold_tolerance=base_variety.cold_tolerance,
            heat_tolerance=base_variety.heat_tolerance,
            storage_life_days=base_variety.storage_life_days,
            seed_cost_per_unit=base_variety.seed_cost_per_unit,
            planting_density=base_variety.planting_density,
            harvest_labor_hours=base_variety.harvest_labor_hours,
            
            # Advanced properties
            family=family,
            genus=self._get_genus_for_crop_type(base_variety.crop_type),
            species=self._get_species_for_crop_type(base_variety.crop_type),
            variety_type=VarietyType.OPEN_POLLINATED,
            development_year=random.randint(1980, 2020),
            premium_multiplier=random.uniform(0.9, 1.3),
            companion_crops=self._get_companion_crops(base_variety.crop_type),
            antagonistic_crops=self._get_antagonistic_crops(base_variety.crop_type)
        )
        
        return advanced_variety
    
    def _get_genus_for_crop_type(self, crop_type: CropType) -> str:
        """Get botanical genus for crop type"""
        genus_mapping = {
            CropType.TOMATOES: "Solanum",
            CropType.POTATOES: "Solanum",
            CropType.CORN: "Zea",
            CropType.WHEAT: "Triticum",
            CropType.SOYBEANS: "Glycine",
            CropType.BEANS: "Phaseolus",
            CropType.LETTUCE: "Lactuca",
            CropType.CARROTS: "Daucus",
            CropType.ONIONS: "Allium",
            CropType.PEPPERS: "Capsicum"
        }
        return genus_mapping.get(crop_type, "Unknown")
    
    def _get_species_for_crop_type(self, crop_type: CropType) -> str:
        """Get botanical species for crop type"""
        species_mapping = {
            CropType.TOMATOES: "lycopersicum",
            CropType.POTATOES: "tuberosum",
            CropType.CORN: "mays",
            CropType.WHEAT: "aestivum",
            CropType.SOYBEANS: "max",
            CropType.BEANS: "vulgaris",
            CropType.LETTUCE: "sativa",
            CropType.CARROTS: "carota",
            CropType.ONIONS: "cepa",
            CropType.PEPPERS: "annuum"
        }
        return species_mapping.get(crop_type, "unknown")
    
    def _get_companion_crops(self, crop_type: CropType) -> List[str]:
        """Get companion crops for a crop type"""
        companion_mapping = {
            CropType.TOMATOES: ["basil", "oregano", "carrots", "lettuce"],
            CropType.CORN: ["beans", "squash", "pumpkins"],  # Three Sisters
            CropType.BEANS: ["corn", "carrots", "lettuce"],
            CropType.LETTUCE: ["tomatoes", "carrots", "onions"],
            CropType.CARROTS: ["tomatoes", "lettuce", "onions"],
            CropType.ONIONS: ["tomatoes", "carrots", "lettuce", "peppers"]
        }
        return companion_mapping.get(crop_type, [])
    
    def _get_antagonistic_crops(self, crop_type: CropType) -> List[str]:
        """Get antagonistic crops for a crop type"""
        antagonistic_mapping = {
            CropType.TOMATOES: ["corn", "potatoes"],  # Same family diseases
            CropType.POTATOES: ["tomatoes", "peppers"],
            CropType.CORN: ["tomatoes"],
            CropType.BEANS: ["onions", "garlic"],  # Allelopathic effects
        }
        return antagonistic_mapping.get(crop_type, [])
    
    async def _create_base_genetic_profile(self, variety_id: str) -> GeneticProfile:
        """Create a base genetic profile for a variety"""
        profile = GeneticProfile(
            variety_id=variety_id,
            generation=1,
            genetic_diversity=random.uniform(0.7, 1.0),
            inbreeding_coefficient=random.uniform(0.0, 0.2)
        )
        
        # Assign random alleles for each trait
        for trait in GeneticTrait:
            available_alleles = self.genetic_library.get(trait.value, [])
            if available_alleles:
                # Diploid - two alleles per trait
                selected_alleles = random.sample(available_alleles, min(2, len(available_alleles)))
                profile.alleles[trait] = selected_alleles
        
        return profile
    
    async def _create_specialty_varieties(self):
        """Create additional specialty and heirloom varieties"""
        specialty_varieties = [
            # Heirloom tomatoes
            {
                'variety_id': 'tomato_brandywine_heirloom',
                'base_type': CropType.TOMATOES,
                'name': 'Brandywine Heirloom Tomato',
                'variety_type': VarietyType.HEIRLOOM,
                'premium_multiplier': 1.8,
                'specialty_markets': ['farmers_market', 'restaurant_supply', 'organic'],
                'development_year': 1885
            },
            {
                'variety_id': 'tomato_cherokee_purple',
                'base_type': CropType.TOMATOES,
                'name': 'Cherokee Purple Tomato',
                'variety_type': VarietyType.HEIRLOOM,
                'premium_multiplier': 2.0,
                'specialty_markets': ['farmers_market', 'gourmet'],
                'development_year': 1890
            },
            
            # Specialty corn
            {
                'variety_id': 'corn_glass_gem',
                'base_type': CropType.CORN,
                'name': 'Glass Gem Ornamental Corn',
                'variety_type': VarietyType.HEIRLOOM,
                'premium_multiplier': 3.0,
                'specialty_markets': ['ornamental', 'specialty_food'],
                'development_year': 1900
            },
            
            # Ancient grains
            {
                'variety_id': 'wheat_einkorn_ancient',
                'base_type': CropType.WHEAT,
                'name': 'Einkorn Ancient Wheat',
                'variety_type': VarietyType.LANDRACE,
                'premium_multiplier': 2.5,
                'specialty_markets': ['health_food', 'artisan_baking'],
                'development_year': -8000  # Ancient variety
            }
        ]
        
        for specialty_data in specialty_varieties:
            await self._create_specialty_variety(specialty_data)
    
    async def _create_specialty_variety(self, specialty_data: Dict[str, Any]):
        """Create a specialty crop variety"""
        base_variety_id = f"{specialty_data['base_type'].value}_standard"
        if base_variety_id in self.advanced_varieties:
            base_variety = self.advanced_varieties[base_variety_id]
            
            # Create specialty variety based on standard variety
            specialty_variety = AdvancedCropVariety(
                variety_id=specialty_data['variety_id'],
                crop_type=specialty_data['base_type'],
                variety_name=specialty_data['name'],
                description=f"Specialty {specialty_data['name']} variety",
                days_to_maturity=base_variety.days_to_maturity,
                growth_stages_duration=base_variety.growth_stages_duration,
                min_temperature=base_variety.min_temperature,
                max_temperature=base_variety.max_temperature,
                optimal_temperature_range=base_variety.optimal_temperature_range,
                water_requirements=base_variety.water_requirements,
                light_requirements=base_variety.light_requirements,
                preferred_soil_types=base_variety.preferred_soil_types,
                optimal_ph_range=base_variety.optimal_ph_range,
                nutrient_requirements=base_variety.nutrient_requirements,
                base_yield_per_plant=base_variety.base_yield_per_plant * 0.8,  # Often lower yield
                yield_quality_factors=base_variety.yield_quality_factors,
                market_value_multiplier=base_variety.market_value_multiplier,
                disease_resistance=base_variety.disease_resistance,
                pest_resistance=base_variety.pest_resistance,
                drought_tolerance=base_variety.drought_tolerance,
                cold_tolerance=base_variety.cold_tolerance,
                heat_tolerance=base_variety.heat_tolerance,
                storage_life_days=base_variety.storage_life_days,
                seed_cost_per_unit=base_variety.seed_cost_per_unit * 2.0,  # Higher seed cost
                planting_density=base_variety.planting_density,
                harvest_labor_hours=base_variety.harvest_labor_hours,
                
                # Specialty properties
                family=base_variety.family,
                genus=base_variety.genus,
                species=base_variety.species,
                variety_type=specialty_data['variety_type'],
                development_year=specialty_data['development_year'],
                premium_multiplier=specialty_data['premium_multiplier'],
                specialty_markets=specialty_data['specialty_markets'],
                companion_crops=base_variety.companion_crops,
                antagonistic_crops=base_variety.antagonistic_crops
            )
            
            # Create enhanced genetic profile for specialty varieties
            genetic_profile = await self._create_specialty_genetic_profile(
                specialty_data['variety_id'], 
                specialty_data['variety_type']
            )
            specialty_variety.genetic_profile = genetic_profile
            
            self.advanced_varieties[specialty_data['variety_id']] = specialty_variety
            self.genetic_profiles[specialty_data['variety_id']] = genetic_profile
            
            # Track heirloom varieties
            if specialty_data['variety_type'] == VarietyType.HEIRLOOM:
                self.heirloom_varieties.add(specialty_data['variety_id'])
    
    async def _create_specialty_genetic_profile(self, variety_id: str, variety_type: VarietyType) -> GeneticProfile:
        """Create genetic profile for specialty varieties"""
        profile = GeneticProfile(
            variety_id=variety_id,
            generation=1
        )
        
        if variety_type == VarietyType.HEIRLOOM:
            # Heirloom varieties have high genetic diversity but may have lower yields
            profile.genetic_diversity = random.uniform(0.9, 1.0)
            profile.inbreeding_coefficient = random.uniform(0.0, 0.1)
            
            # Enhanced flavor and quality traits
            for trait in [GeneticTrait.FLAVOR_INTENSITY, GeneticTrait.NUTRIENT_CONTENT, GeneticTrait.STORAGE_LIFE]:
                available_alleles = self.genetic_library.get(trait.value, [])
                if available_alleles:
                    # Select high-quality alleles
                    quality_alleles = [a for a in available_alleles if a.beneficial and a.effect_strength > 1.0]
                    if quality_alleles:
                        selected_alleles = random.sample(quality_alleles, min(2, len(quality_alleles)))
                        profile.alleles[trait] = selected_alleles
        
        elif variety_type == VarietyType.HYBRID:
            # Hybrid varieties have moderate diversity but potential hybrid vigor
            profile.genetic_diversity = random.uniform(0.6, 0.8)
            profile.inbreeding_coefficient = 0.0  # F1 hybrids
            
            # Enhanced yield traits
            for trait in [GeneticTrait.YIELD_POTENTIAL, GeneticTrait.DISEASE_RESISTANCE]:
                available_alleles = self.genetic_library.get(trait.value, [])
                if available_alleles:
                    selected_alleles = random.sample(available_alleles, min(2, len(available_alleles)))
                    profile.alleles[trait] = selected_alleles
        
        # Fill in remaining traits with random alleles
        for trait in GeneticTrait:
            if trait not in profile.alleles:
                available_alleles = self.genetic_library.get(trait.value, [])
                if available_alleles:
                    selected_alleles = random.sample(available_alleles, min(2, len(available_alleles)))
                    profile.alleles[trait] = selected_alleles
        
        return profile
    
    async def _initialize_companion_database(self):
        """Initialize companion planting database"""
        # Three Sisters (Native American companion planting)
        three_sisters = [
            CropCompanionship(
                primary_crop="corn",
                companion_crop="beans",
                relationship_type="beneficial",
                effect_strength=1.2,
                yield_modifier=1.15,
                soil_improvement=0.3,  # Nitrogen fixation
                mechanism="nitrogen_fixation"
            ),
            CropCompanionship(
                primary_crop="corn",
                companion_crop="squash",
                relationship_type="beneficial",
                effect_strength=1.1,
                pest_resistance_modifier=1.2,
                mechanism="pest_deterrent"
            ),
            CropCompanionship(
                primary_crop="beans",
                companion_crop="squash",
                relationship_type="beneficial",
                effect_strength=1.05,
                mechanism="ground_cover"
            )
        ]
        
        # Mediterranean companions
        mediterranean_companions = [
            CropCompanionship(
                primary_crop="tomatoes",
                companion_crop="basil",
                relationship_type="beneficial",
                effect_strength=1.3,
                yield_modifier=1.1,
                pest_resistance_modifier=1.4,
                mechanism="aromatic_pest_deterrent"
            ),
            CropCompanionship(
                primary_crop="tomatoes",
                companion_crop="oregano",
                relationship_type="beneficial",
                effect_strength=1.2,
                disease_resistance_modifier=1.2,
                mechanism="antimicrobial"
            )
        ]
        
        # Store companions
        all_companions = three_sisters + mediterranean_companions
        for companion in all_companions:
            if companion.primary_crop not in self.companion_relationships:
                self.companion_relationships[companion.primary_crop] = []
            self.companion_relationships[companion.primary_crop].append(companion)
    
    async def _initialize_specialty_markets(self):
        """Initialize specialty market definitions"""
        self.specialty_markets = {
            'farmers_market': {
                'name': 'Farmers Market',
                'premium_multiplier': 1.4,
                'volume_limits': {'small': 100, 'medium': 50, 'large': 20},
                'quality_requirements': 0.8,
                'preferred_varieties': ['heirloom', 'organic', 'locally_adapted']
            },
            'restaurant_supply': {
                'name': 'Restaurant Supply',
                'premium_multiplier': 1.6,
                'volume_limits': {'small': 50, 'medium': 30, 'large': 15},
                'quality_requirements': 0.9,
                'preferred_varieties': ['unique_flavor', 'presentation_quality']
            },
            'organic': {
                'name': 'Organic Market',
                'premium_multiplier': 1.5,
                'volume_limits': {'unlimited': True},
                'quality_requirements': 0.7,
                'certification_required': 'organic',
                'preferred_varieties': ['heirloom', 'non_gmo']
            },
            'gourmet': {
                'name': 'Gourmet Market',
                'premium_multiplier': 2.0,
                'volume_limits': {'small': 25, 'medium': 15, 'large': 8},
                'quality_requirements': 0.95,
                'preferred_varieties': ['rare', 'exceptional_flavor']
            }
        }
    
    async def start_breeding_program(self, program_name: str, objective: BreedingObjective,
                                   target_traits: List[GeneticTrait], parent_varieties: List[str],
                                   employee_id: Optional[str] = None) -> Optional[str]:
        """Start a new breeding program"""
        # Validate parent varieties exist
        for variety_id in parent_varieties:
            if variety_id not in self.advanced_varieties:
                self.logger.error(f"Parent variety {variety_id} not found")
                return None
        
        # Create breeding program
        program_id = f"breeding_{int(time.time())}_{random.randint(1000, 9999)}"
        
        program = BreedingProgram(
            program_id=program_id,
            program_name=program_name,
            objective=objective,
            target_traits=target_traits,
            parent_varieties=parent_varieties,
            started_time=self.time_manager.get_current_time().total_minutes,
            assigned_employee_id=employee_id
        )
        
        # Calculate expected completion time
        expected_cycles = program.get_expected_cycles()
        days_per_cycle = 365  # One year per breeding cycle
        program.expected_completion_time = (program.started_time + 
                                          (expected_cycles * days_per_cycle * 1440))
        
        self.active_breeding_programs[program_id] = program
        
        # Emit breeding program started event
        self.event_system.emit('breeding_program_started', {
            'program_id': program_id,
            'program_name': program_name,
            'objective': objective.value,
            'parent_varieties': parent_varieties,
            'expected_cycles': expected_cycles,
            'employee_id': employee_id
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Started breeding program: {program_name}")
        return program_id
    
    async def create_variety_through_breeding(self, parent1_id: str, parent2_id: str,
                                            variety_name: str, breeding_objective: Optional[BreedingObjective] = None) -> Optional[str]:
        """Create a new variety through controlled breeding"""
        if parent1_id not in self.genetic_profiles or parent2_id not in self.genetic_profiles:
            self.logger.error("One or both parent varieties not found")
            return None
        
        parent1 = self.genetic_profiles[parent1_id]
        parent2 = self.genetic_profiles[parent2_id]
        
        # Generate new variety ID
        new_variety_id = f"bred_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create offspring genetic profile through sexual reproduction
        offspring_profile = await self._perform_genetic_cross(parent1, parent2, new_variety_id, breeding_objective)
        
        # Create base variety from dominant parent
        base_parent = self.advanced_varieties[parent1_id]
        offspring_variety = await self._create_offspring_variety(base_parent, new_variety_id, variety_name, offspring_profile)
        
        # Store new variety and genetic profile
        self.advanced_varieties[new_variety_id] = offspring_variety
        self.genetic_profiles[new_variety_id] = offspring_profile
        
        # Update tracking
        self.varieties_created += 1
        
        # Emit variety created event
        self.event_system.emit('new_variety_created', {
            'variety_id': new_variety_id,
            'variety_name': variety_name,
            'parent1_id': parent1_id,
            'parent2_id': parent2_id,
            'breeding_method': 'controlled_cross',
            'generation': offspring_profile.generation
        }, priority=EventPriority.NORMAL)
        
        self.logger.info(f"Created new variety through breeding: {variety_name}")
        return new_variety_id
    
    async def _perform_genetic_cross(self, parent1: GeneticProfile, parent2: GeneticProfile,
                                   offspring_id: str, objective: Optional[BreedingObjective]) -> GeneticProfile:
        """Perform genetic cross between two parents"""
        offspring = GeneticProfile(
            variety_id=offspring_id,
            parent_varieties=[parent1.variety_id, parent2.variety_id],
            generation=max(parent1.generation, parent2.generation) + 1,
            breeding_objective=objective
        )
        
        # Calculate genetic diversity (average of parents with some recombination)
        offspring.genetic_diversity = (parent1.genetic_diversity + parent2.genetic_diversity) / 2
        offspring.genetic_diversity += random.uniform(-0.1, 0.1)  # Recombination variation
        offspring.genetic_diversity = max(0.1, min(1.0, offspring.genetic_diversity))
        
        # Calculate inbreeding coefficient
        if parent1.variety_id == parent2.variety_id:
            # Self-fertilization
            offspring.inbreeding_coefficient = 0.5 + (parent1.inbreeding_coefficient * 0.5)
        else:
            # Outcrossing
            offspring.inbreeding_coefficient = (parent1.inbreeding_coefficient + parent2.inbreeding_coefficient) / 4
        
        # Perform Mendelian inheritance for each trait
        for trait in GeneticTrait:
            parent1_alleles = parent1.alleles.get(trait, [])
            parent2_alleles = parent2.alleles.get(trait, [])
            
            if parent1_alleles and parent2_alleles:
                # Random segregation and independent assortment
                gamete1_allele = random.choice(parent1_alleles)
                gamete2_allele = random.choice(parent2_alleles)
                
                offspring.alleles[trait] = [gamete1_allele, gamete2_allele]
            elif parent1_alleles:
                offspring.alleles[trait] = random.sample(parent1_alleles, min(2, len(parent1_alleles)))
            elif parent2_alleles:
                offspring.alleles[trait] = random.sample(parent2_alleles, min(2, len(parent2_alleles)))
        
        # Apply selection pressure based on breeding objective
        if objective:
            await self._apply_selection_pressure(offspring, objective)
        
        return offspring
    
    async def _apply_selection_pressure(self, offspring: GeneticProfile, objective: BreedingObjective):
        """Apply selection pressure based on breeding objective"""
        selection_traits = {
            BreedingObjective.YIELD_IMPROVEMENT: [GeneticTrait.YIELD_POTENTIAL],
            BreedingObjective.DISEASE_RESISTANCE: [GeneticTrait.DISEASE_RESISTANCE],
            BreedingObjective.CLIMATE_ADAPTATION: [GeneticTrait.DROUGHT_TOLERANCE, GeneticTrait.HEAT_TOLERANCE, GeneticTrait.COLD_TOLERANCE],
            BreedingObjective.QUALITY_ENHANCEMENT: [GeneticTrait.FLAVOR_INTENSITY, GeneticTrait.NUTRIENT_CONTENT, GeneticTrait.STORAGE_LIFE],
            BreedingObjective.SPECIALTY_MARKET: [GeneticTrait.FLAVOR_INTENSITY, GeneticTrait.FRUIT_COLOR, GeneticTrait.FRUIT_SIZE],
            BreedingObjective.CONSERVATION: []  # No artificial selection
        }
        
        target_traits = selection_traits.get(objective, [])
        
        for trait in target_traits:
            if trait in offspring.alleles:
                # Increase probability of beneficial alleles
                trait_alleles = offspring.alleles[trait]
                beneficial_alleles = [a for a in trait_alleles if a.beneficial]
                
                if beneficial_alleles and len(trait_alleles) > 1:
                    # Replace one random allele with a beneficial one
                    if random.random() < 0.3:  # 30% chance of selection pressure
                        replace_index = random.randint(0, len(trait_alleles) - 1)
                        trait_alleles[replace_index] = random.choice(beneficial_alleles)
    
    async def _create_offspring_variety(self, base_parent: AdvancedCropVariety, variety_id: str,
                                      variety_name: str, genetic_profile: GeneticProfile) -> AdvancedCropVariety:
        """Create offspring variety from genetic profile"""
        # Start with parent characteristics
        offspring = AdvancedCropVariety(
            variety_id=variety_id,
            crop_type=base_parent.crop_type,
            variety_name=variety_name,
            description=f"Bred variety: {variety_name}",
            days_to_maturity=base_parent.days_to_maturity,
            growth_stages_duration=base_parent.growth_stages_duration.copy(),
            min_temperature=base_parent.min_temperature,
            max_temperature=base_parent.max_temperature,
            optimal_temperature_range=base_parent.optimal_temperature_range,
            water_requirements=base_parent.water_requirements,
            light_requirements=base_parent.light_requirements,
            preferred_soil_types=base_parent.preferred_soil_types.copy(),
            optimal_ph_range=base_parent.optimal_ph_range,
            nutrient_requirements=base_parent.nutrient_requirements.copy(),
            base_yield_per_plant=base_parent.base_yield_per_plant,
            yield_quality_factors=base_parent.yield_quality_factors.copy(),
            market_value_multiplier=base_parent.market_value_multiplier,
            disease_resistance=base_parent.disease_resistance.copy(),
            pest_resistance=base_parent.pest_resistance.copy(),
            drought_tolerance=base_parent.drought_tolerance,
            cold_tolerance=base_parent.cold_tolerance,
            heat_tolerance=base_parent.heat_tolerance,
            storage_life_days=base_parent.storage_life_days,
            seed_cost_per_unit=base_parent.seed_cost_per_unit,
            planting_density=base_parent.planting_density,
            harvest_labor_hours=base_parent.harvest_labor_hours,
            
            # Advanced properties
            family=base_parent.family,
            genus=base_parent.genus,
            species=base_parent.species,
            variety_type=VarietyType.BREEDING_LINE,
            development_year=int(self.time_manager.get_current_time().total_minutes / (365 * 1440)) + 2000,
            genetic_profile=genetic_profile,
            companion_crops=base_parent.companion_crops.copy(),
            antagonistic_crops=base_parent.antagonistic_crops.copy()
        )
        
        # Modify characteristics based on genetic profile
        await self._apply_genetic_effects_to_variety(offspring, genetic_profile)
        
        return offspring
    
    async def _apply_genetic_effects_to_variety(self, variety: AdvancedCropVariety, profile: GeneticProfile):
        """Apply genetic effects to variety characteristics"""
        # Yield modification
        yield_trait = profile.get_trait_value(GeneticTrait.YIELD_POTENTIAL)
        variety.base_yield_per_plant *= (0.7 + yield_trait * 0.6)  # 0.7 to 1.3 range
        
        # Disease resistance modification
        disease_trait = profile.get_trait_value(GeneticTrait.DISEASE_RESISTANCE)
        for disease in variety.disease_resistance:
            variety.disease_resistance[disease] = min(1.0, variety.disease_resistance[disease] + disease_trait * 0.3)
        
        # Tolerance modifications
        drought_trait = profile.get_trait_value(GeneticTrait.DROUGHT_TOLERANCE)
        variety.drought_tolerance = min(1.0, variety.drought_tolerance + drought_trait * 0.2)
        
        cold_trait = profile.get_trait_value(GeneticTrait.COLD_TOLERANCE)
        variety.cold_tolerance = min(1.0, variety.cold_tolerance + cold_trait * 0.2)
        
        heat_trait = profile.get_trait_value(GeneticTrait.HEAT_TOLERANCE)
        variety.heat_tolerance = min(1.0, variety.heat_tolerance + heat_trait * 0.2)
        
        # Maturity speed modification
        maturity_trait = profile.get_trait_value(GeneticTrait.MATURITY_SPEED)
        maturity_modifier = 0.9 + maturity_trait * 0.2  # 0.9 to 1.1 range
        variety.days_to_maturity = int(variety.days_to_maturity * maturity_modifier)
        
        # Storage life modification
        storage_trait = profile.get_trait_value(GeneticTrait.STORAGE_LIFE)
        variety.storage_life_days = int(variety.storage_life_days * (0.8 + storage_trait * 0.4))
        
        # Market value modification based on quality traits
        flavor_trait = profile.get_trait_value(GeneticTrait.FLAVOR_INTENSITY)
        nutrient_trait = profile.get_trait_value(GeneticTrait.NUTRIENT_CONTENT)
        quality_bonus = (flavor_trait + nutrient_trait) * 0.1
        variety.market_value_multiplier *= (1.0 + quality_bonus)
    
    def get_variety_info(self, variety_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a crop variety"""
        if variety_id not in self.advanced_varieties:
            return None
        
        variety = self.advanced_varieties[variety_id]
        genetic_profile = self.genetic_profiles.get(variety_id)
        
        info = {
            'variety_id': variety_id,
            'variety_name': variety.variety_name,
            'crop_type': variety.crop_type.value,
            'family': variety.family.value,
            'genus_species': f"{variety.genus} {variety.species}",
            'variety_type': variety.variety_type.value,
            'development_year': variety.development_year,
            
            # Growing characteristics
            'days_to_maturity': variety.days_to_maturity,
            'base_yield': variety.base_yield_per_plant,
            'genetic_yield': variety.get_genetic_yield_potential() if genetic_profile else variety.base_yield_per_plant,
            'drought_tolerance': variety.drought_tolerance,
            'cold_tolerance': variety.cold_tolerance,
            'heat_tolerance': variety.heat_tolerance,
            'storage_life_days': variety.storage_life_days,
            
            # Market information
            'seed_cost': variety.seed_cost_per_unit,
            'market_multiplier': variety.market_value_multiplier,
            'premium_multiplier': variety.premium_multiplier,
            'specialty_markets': variety.specialty_markets,
            
            # Companion planting
            'companion_crops': variety.companion_crops,
            'antagonistic_crops': variety.antagonistic_crops,
            
            # Genetic information
            'has_genetic_profile': genetic_profile is not None,
            'genetic_fitness': genetic_profile.get_overall_fitness() if genetic_profile else 0.0,
            'genetic_diversity': genetic_profile.genetic_diversity if genetic_profile else 0.0,
            'inbreeding_coefficient': genetic_profile.inbreeding_coefficient if genetic_profile else 0.0,
            'parent_varieties': genetic_profile.parent_varieties if genetic_profile else [],
            'generation': genetic_profile.generation if genetic_profile else 1
        }
        
        # Add trait values if genetic profile exists
        if genetic_profile:
            info['genetic_traits'] = {}
            for trait in GeneticTrait:
                info['genetic_traits'][trait.value] = genetic_profile.get_trait_value(trait)
        
        return info
    
    def get_available_varieties(self) -> List[Dict[str, Any]]:
        """Get all available crop varieties"""
        varieties = []
        for variety_id in self.advanced_varieties.keys():
            variety_info = self.get_variety_info(variety_id)
            if variety_info:
                varieties.append(variety_info)
        
        return sorted(varieties, key=lambda x: (x['crop_type'], x['variety_name']))
    
    def get_breeding_programs(self) -> List[Dict[str, Any]]:
        """Get information about all breeding programs"""
        programs = []
        for program in self.active_breeding_programs.values():
            programs.append({
                'program_id': program.program_id,
                'program_name': program.program_name,
                'objective': program.objective.value,
                'target_traits': [trait.value for trait in program.target_traits],
                'parent_varieties': program.parent_varieties,
                'current_generation': program.current_generation,
                'progress': program.progress,
                'expected_cycles': program.get_expected_cycles(),
                'assigned_employee': program.assigned_employee_id,
                'allocated_plots': len(program.allocated_plots),
                'annual_budget': program.annual_budget,
                'total_invested': program.total_invested
            })
        
        return programs
    
    async def update(self, delta_time: float):
        """Update multi-crop framework"""
        # Update breeding programs
        await self._update_breeding_programs(delta_time)
        
        # Update genetic diversity tracking
        await self._update_genetic_diversity_tracking()
    
    async def _update_breeding_programs(self, delta_time: float):
        """Update active breeding programs"""
        hours_passed = delta_time / 3600.0
        
        completed_programs = []
        
        for program_id, program in self.active_breeding_programs.items():
            if program.progress < 1.0:
                # Calculate employee efficiency
                employee_efficiency = 1.0
                if program.assigned_employee_id:
                    employee_info = self.employee_system.get_employee_info(program.assigned_employee_id)
                    if employee_info:
                        # Breeding requires crop management and quality control skills
                        crop_skill = employee_info['skills'].get('crop_management', {}).get('efficiency', 1.0)
                        quality_skill = employee_info['skills'].get('quality_control', {}).get('efficiency', 1.0)
                        employee_efficiency = (crop_skill + quality_skill) / 2
                
                # Update progress
                program.update_progress(hours_passed, employee_efficiency)
                
                # Check for completion
                if program.progress >= 1.0:
                    completed_programs.append(program_id)
        
        # Complete finished breeding programs
        for program_id in completed_programs:
            await self._complete_breeding_program(program_id)
    
    async def _complete_breeding_program(self, program_id: str):
        """Complete a breeding program and generate results"""
        program = self.active_breeding_programs[program_id]
        
        # Generate successful varieties based on program objective
        success_rate = random.uniform(0.3, 0.8)  # 30-80% success rate
        num_successes = max(1, int(len(program.parent_varieties) * success_rate))
        
        successful_varieties = []
        for i in range(num_successes):
            # Create new variety through breeding
            parent1 = random.choice(program.parent_varieties)
            parent2 = random.choice(program.parent_varieties)
            
            variety_name = f"{program.program_name}_Line_{i+1}"
            new_variety_id = await self.create_variety_through_breeding(
                parent1, parent2, variety_name, program.objective
            )
            
            if new_variety_id:
                successful_varieties.append(new_variety_id)
        
        program.successful_varieties = successful_varieties
        self.breeding_programs_completed += 1
        
        # Add to breeding history
        self.breeding_history.append({
            'program_id': program_id,
            'program_name': program.program_name,
            'completion_time': self.time_manager.get_current_time().total_minutes,
            'successful_varieties': successful_varieties,
            'total_invested': program.total_invested,
            'cycles_completed': program.current_generation
        })
        
        # Emit completion event
        self.event_system.emit('breeding_program_completed', {
            'program_id': program_id,
            'program_name': program.program_name,
            'successful_varieties': successful_varieties,
            'success_count': len(successful_varieties)
        }, priority=EventPriority.HIGH)
        
        self.logger.info(f"Completed breeding program: {program.program_name} with {len(successful_varieties)} successes")
    
    async def _update_genetic_diversity_tracking(self):
        """Update overall genetic diversity metrics"""
        if not self.genetic_profiles:
            return
        
        # Calculate average genetic diversity across all varieties
        total_diversity = sum(profile.genetic_diversity for profile in self.genetic_profiles.values())
        self.genetic_diversity_index = total_diversity / len(self.genetic_profiles)
        
        # Track conservation success
        heirloom_count = len(self.heirloom_varieties)
        total_varieties = len(self.advanced_varieties)
        self.conservation_success_rate = heirloom_count / max(1, total_varieties)
    
    # Event handlers
    async def _on_crop_planted(self, event_data):
        """Handle crop planting for companion analysis"""
        variety_id = event_data.get('variety_id', '')
        position = event_data.get('position', (0, 0))
        
        if variety_id in self.advanced_varieties:
            # Analyze nearby crops for companion effects
            await self._analyze_companion_effects(variety_id, position)
    
    async def _on_crop_harvested(self, event_data):
        """Handle crop harvest for performance tracking"""
        variety_id = event_data.get('variety_id', '')
        yield_kg = event_data.get('yield_kg', 0)
        quality_grade = event_data.get('quality_grade', 'standard')
        
        if variety_id in self.genetic_profiles:
            # Update field performance data
            profile = self.genetic_profiles[variety_id]
            if 'yield_performance' not in profile.field_performance:
                profile.field_performance['yield_performance'] = []
            profile.field_performance['yield_performance'].append(yield_kg)
            
            if 'quality_performance' not in profile.field_performance:
                profile.field_performance['quality_performance'] = []
            
            quality_score = {'poor': 0.2, 'fair': 0.4, 'standard': 0.6, 'high': 0.8, 'premium': 1.0}.get(quality_grade, 0.6)
            profile.field_performance['quality_performance'].append(quality_score)
    
    async def _analyze_companion_effects(self, variety_id: str, position: Tuple[int, int]):
        """Analyze companion planting effects for a planted crop"""
        if variety_id not in self.advanced_varieties:
            return
        
        variety = self.advanced_varieties[variety_id]
        companions = self.companion_relationships.get(variety.crop_type.value, [])
        
        # Check nearby planted crops
        nearby_crops = self.crop_system.get_crops_in_radius(position, 5.0)  # 5-tile radius
        
        for crop_info in nearby_crops:
            nearby_variety_id = crop_info.get('variety_id', '')
            distance = crop_info.get('distance', 10.0)
            
            # Check for companion relationships
            for companion in companions:
                if companion.companion_crop in nearby_variety_id:
                    effect = companion.get_effect_at_distance(distance)
                    
                    # Apply companion effects to crop
                    if effect != 1.0:
                        # Would apply effects to the crop instance
                        self.event_system.emit('companion_effect_detected', {
                            'primary_crop': variety_id,
                            'companion_crop': nearby_variety_id,
                            'effect_strength': effect,
                            'distance': distance,
                            'mechanism': companion.mechanism
                        }, priority=EventPriority.LOW)
    
    async def _on_season_changed(self, event_data):
        """Handle seasonal changes affecting breeding"""
        new_season = event_data.get('new_season')
        
        # Seasonal breeding activities
        if new_season == 'spring':
            # Spring is ideal for starting new breeding programs
            for program in self.active_breeding_programs.values():
                if program.assigned_employee_id:
                    # Boost breeding progress in spring
                    program.progress += 0.05  # 5% seasonal bonus
    
    async def _on_employee_hired(self, event_data):
        """Handle new employee for potential breeding assignments"""
        employee_id = event_data.get('employee_id', '')
        
        # Check if employee has relevant skills for breeding
        employee_info = self.employee_system.get_employee_info(employee_id)
        if employee_info:
            skills = employee_info.get('skills', {})
            if 'crop_management' in skills or 'quality_control' in skills:
                # Suggest assigning to breeding programs
                unassigned_programs = [p for p in self.active_breeding_programs.values() 
                                     if not p.assigned_employee_id]
                
                if unassigned_programs:
                    self.event_system.emit('breeding_assignment_suggested', {
                        'employee_id': employee_id,
                        'available_programs': [p.program_id for p in unassigned_programs]
                    }, priority=EventPriority.LOW)
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive multi-crop framework summary"""
        return {
            'total_varieties': len(self.advanced_varieties),
            'varieties_created': self.varieties_created,
            'active_breeding_programs': len(self.active_breeding_programs),
            'breeding_programs_completed': self.breeding_programs_completed,
            'genetic_diversity_index': self.genetic_diversity_index,
            'conservation_success_rate': self.conservation_success_rate,
            'heirloom_varieties_count': len(self.heirloom_varieties),
            'endangered_varieties_count': len(self.endangered_varieties),
            'varieties_by_family': {family.value: len(varieties) for family, varieties in self.crop_families.items()},
            'specialty_markets_count': len(self.specialty_markets),
            'companion_relationships_count': sum(len(companions) for companions in self.companion_relationships.values())
        }
    
    async def shutdown(self):
        """Shutdown the multi-crop framework"""
        self.logger.info("Shutting down Multi-Crop Framework")
        
        # Save final framework state
        final_summary = self.get_system_summary()
        
        self.event_system.emit('multicrop_framework_shutdown', {
            'final_summary': final_summary,
            'total_varieties': len(self.advanced_varieties)
        }, priority=EventPriority.HIGH)
        
        self.logger.info("Multi-Crop Framework shutdown complete")


# Global multi-crop framework instance
_global_multicrop_framework: Optional[MultiCropFramework] = None

def get_multicrop_framework() -> MultiCropFramework:
    """Get the global multi-crop framework instance"""
    global _global_multicrop_framework
    if _global_multicrop_framework is None:
        _global_multicrop_framework = MultiCropFramework()
    return _global_multicrop_framework

def initialize_multicrop_framework() -> MultiCropFramework:
    """Initialize the global multi-crop framework"""
    global _global_multicrop_framework
    _global_multicrop_framework = MultiCropFramework()
    return _global_multicrop_framework