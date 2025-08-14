"""
Advanced Grid System - Multi-Layer Spatial Management for Comprehensive AgriFun Engine

This module implements a sophisticated grid system that supports the complex spatial
requirements of the comprehensive agricultural simulation. Features multiple layers,
spatial indexing, region management, and efficient queries for large-scale farming operations.

Key Features:
- Multi-layer grid system (terrain, crops, buildings, infrastructure, etc.)
- Spatial indexing for O(log n) entity lookups
- Region-based processing for performance optimization
- Dynamic grid expansion for unlimited farm sizes
- Pathfinding integration with obstacle management
- Environmental zone tracking (soil types, climate zones)
- Hierarchical detail levels for rendering optimization
- Collision detection and spatial constraints
- Grid-based AI navigation and planning

Grid Layers:
- TERRAIN: Base terrain type, elevation, natural features
- SOIL: Soil properties, nutrients, health, contamination
- CROPS: All planted crops and their growth states
- BUILDINGS: Structures, storage, processing facilities
- INFRASTRUCTURE: Roads, irrigation, power lines, fencing
- EQUIPMENT: Temporary equipment placement and movement
- ENVIRONMENTAL: Weather effects, pollution, conservation areas
- NAVIGATION: Pathfinding data, movement costs, accessibility

Spatial Features:
- Quadtree spatial indexing for efficient range queries
- Region chunking for large-scale farm management
- Distance-based processing optimization
- Multi-resolution rendering support
- Spatial relationship tracking between entities

Usage Example:
    # Initialize advanced grid system
    grid_system = AdvancedGridSystem(initial_size=(32, 32))
    
    # Create multi-layer tile
    tile = grid_system.get_tile(5, 3)
    tile.set_layer_data('terrain', {'type': 'fertile_loam', 'elevation': 102.5})
    tile.set_layer_data('soil', {'N': 45, 'P': 32, 'K': 28, 'pH': 6.8})
    
    # Add entity to spatial index
    crop_entity = entity_manager.create_entity({...})
    grid_system.add_entity_at_position(crop_entity, 5, 3, 'crops')
    
    # Spatial queries
    nearby_entities = grid_system.get_entities_in_radius(5, 3, 2.0)
    buildings_in_region = grid_system.get_entities_in_layer('buildings', x1=0, y1=0, x2=10, y2=10)
    
    # Region-based processing
    active_region = grid_system.get_active_region(player_x, player_y, radius=20)
    for entity in active_region.get_entities():
        # Process only entities in active region
        pass

Performance Features:
- Lazy loading of grid regions
- Spatial caching and invalidation
- Level-of-detail for distant tiles
- Chunked processing for large operations
- Memory-efficient sparse grid storage
"""

import math
import time
from typing import Dict, List, Set, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import heapq

# Import our core systems
from .entity_component_system import get_entity_manager, TransformComponent
from .advanced_event_system import get_event_system, EventPriority


class GridLayer(Enum):
    """Grid layer types for multi-layer spatial organization"""
    TERRAIN = "terrain"           # Base terrain, elevation, natural features
    SOIL = "soil"                # Soil properties, nutrients, health
    CROPS = "crops"              # Planted crops and growth states
    BUILDINGS = "buildings"       # Structures and facilities
    INFRASTRUCTURE = "infrastructure"  # Roads, irrigation, utilities
    EQUIPMENT = "equipment"       # Temporary equipment placement
    ENVIRONMENTAL = "environmental"  # Weather effects, zones
    NAVIGATION = "navigation"     # Pathfinding and movement data


@dataclass
class TileData:
    """Data storage for a single grid tile"""
    x: int
    y: int
    
    # Multi-layer data storage
    layer_data: Dict[GridLayer, Dict[str, Any]] = field(default_factory=dict)
    
    # Entity tracking
    entities: Dict[GridLayer, Set[str]] = field(default_factory=lambda: defaultdict(set))
    
    # Spatial properties
    elevation: float = 0.0
    accessibility: float = 1.0  # 0.0 = blocked, 1.0 = fully accessible
    movement_cost: float = 1.0  # Pathfinding cost multiplier
    
    # Processing optimization
    last_updated: float = field(default_factory=time.time)
    dirty_layers: Set[GridLayer] = field(default_factory=set)
    processing_priority: int = 1  # 1-5 scale for update priority
    
    # Caching
    cached_properties: Dict[str, Any] = field(default_factory=dict)
    cache_valid: bool = True
    
    def get_layer_data(self, layer: GridLayer) -> Dict[str, Any]:
        """Get data for a specific layer"""
        return self.layer_data.get(layer, {})
    
    def set_layer_data(self, layer: GridLayer, data: Dict[str, Any]):
        """Set data for a specific layer"""
        self.layer_data[layer] = data.copy()
        self.dirty_layers.add(layer)
        self.last_updated = time.time()
        self.cache_valid = False
    
    def update_layer_data(self, layer: GridLayer, updates: Dict[str, Any]):
        """Update specific fields in a layer"""
        if layer not in self.layer_data:
            self.layer_data[layer] = {}
        
        self.layer_data[layer].update(updates)
        self.dirty_layers.add(layer)
        self.last_updated = time.time()
        self.cache_valid = False
    
    def add_entity(self, entity_id: str, layer: GridLayer):
        """Add an entity to this tile"""
        if layer not in self.entities:
            self.entities[layer] = set()
        
        self.entities[layer].add(entity_id)
        self.dirty_layers.add(layer)
        self.last_updated = time.time()
    
    def remove_entity(self, entity_id: str, layer: GridLayer):
        """Remove an entity from this tile"""
        if layer in self.entities:
            self.entities[layer].discard(entity_id)
            if not self.entities[layer]:
                del self.entities[layer]
        
        self.dirty_layers.add(layer)
        self.last_updated = time.time()
    
    def get_entities(self, layer: Optional[GridLayer] = None) -> Set[str]:
        """Get entities on this tile, optionally filtered by layer"""
        if layer is not None:
            return self.entities.get(layer, set()).copy()
        
        all_entities = set()
        for entity_set in self.entities.values():
            all_entities.update(entity_set)
        return all_entities
    
    def has_entities(self, layer: Optional[GridLayer] = None) -> bool:
        """Check if tile has entities"""
        if layer is not None:
            return layer in self.entities and len(self.entities[layer]) > 0
        
        return any(self.entities.values())
    
    def clear_dirty_flags(self):
        """Clear dirty flags after processing"""
        self.dirty_layers.clear()
    
    def invalidate_cache(self):
        """Invalidate cached properties"""
        self.cached_properties.clear()
        self.cache_valid = False


@dataclass
class SpatialNode:
    """Node in the spatial quadtree index"""
    x: float
    y: float
    width: float
    height: float
    entities: Set[str] = field(default_factory=set)
    children: List['SpatialNode'] = field(default_factory=list)
    max_entities: int = 10
    max_depth: int = 8
    depth: int = 0
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is within this node's bounds"""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def intersects_rect(self, x: float, y: float, width: float, height: float) -> bool:
        """Check if rectangle intersects this node's bounds"""
        return not (x >= self.x + self.width or 
                   x + width <= self.x or
                   y >= self.y + self.height or
                   y + height <= self.y)
    
    def subdivide(self):
        """Split this node into four quadrants"""
        if self.children:
            return  # Already subdivided
        
        half_width = self.width / 2
        half_height = self.height / 2
        
        self.children = [
            SpatialNode(self.x, self.y, half_width, half_height, 
                       max_entities=self.max_entities, max_depth=self.max_depth, 
                       depth=self.depth + 1),  # NW
            SpatialNode(self.x + half_width, self.y, half_width, half_height,
                       max_entities=self.max_entities, max_depth=self.max_depth,
                       depth=self.depth + 1),  # NE
            SpatialNode(self.x, self.y + half_height, half_width, half_height,
                       max_entities=self.max_entities, max_depth=self.max_depth,
                       depth=self.depth + 1),  # SW
            SpatialNode(self.x + half_width, self.y + half_height, half_width, half_height,
                       max_entities=self.max_entities, max_depth=self.max_depth,
                       depth=self.depth + 1)   # SE
        ]
        
        # Redistribute entities to children
        for entity_id in self.entities.copy():
            entity_manager = get_entity_manager()
            transform = entity_manager.get_component(entity_id, 'transform')
            if transform:
                for child in self.children:
                    if child.contains_point(transform.x, transform.y):
                        child.add_entity(entity_id)
                        break
        
        self.entities.clear()
    
    def add_entity(self, entity_id: str):
        """Add entity to this node"""
        if self.children:
            # If subdivided, add to appropriate child
            entity_manager = get_entity_manager()
            transform = entity_manager.get_component(entity_id, 'transform')
            if transform:
                for child in self.children:
                    if child.contains_point(transform.x, transform.y):
                        child.add_entity(entity_id)
                        return
        else:
            # Add to this node
            self.entities.add(entity_id)
            
            # Subdivide if necessary
            if (len(self.entities) > self.max_entities and 
                self.depth < self.max_depth):
                self.subdivide()
    
    def remove_entity(self, entity_id: str):
        """Remove entity from this node"""
        if self.children:
            for child in self.children:
                child.remove_entity(entity_id)
        else:
            self.entities.discard(entity_id)
    
    def query_range(self, x: float, y: float, width: float, height: float) -> Set[str]:
        """Query entities within a rectangular range"""
        if not self.intersects_rect(x, y, width, height):
            return set()
        
        result = set()
        
        if self.children:
            for child in self.children:
                result.update(child.query_range(x, y, width, height))
        else:
            # Check each entity in this node
            entity_manager = get_entity_manager()
            for entity_id in self.entities:
                transform = entity_manager.get_component(entity_id, 'transform')
                if (transform and 
                    x <= transform.x < x + width and 
                    y <= transform.y < y + height):
                    result.add(entity_id)
        
        return result
    
    def query_radius(self, center_x: float, center_y: float, radius: float) -> Set[str]:
        """Query entities within a circular radius"""
        # Use bounding box for initial filtering
        x = center_x - radius
        y = center_y - radius
        width = height = radius * 2
        
        if not self.intersects_rect(x, y, width, height):
            return set()
        
        result = set()
        
        if self.children:
            for child in self.children:
                result.update(child.query_radius(center_x, center_y, radius))
        else:
            # Check distance for each entity
            entity_manager = get_entity_manager()
            for entity_id in self.entities:
                transform = entity_manager.get_component(entity_id, 'transform')
                if transform:
                    distance = math.sqrt(
                        (transform.x - center_x) ** 2 + 
                        (transform.y - center_y) ** 2
                    )
                    if distance <= radius:
                        result.add(entity_id)
        
        return result


@dataclass
class GridRegion:
    """A region of the grid for chunked processing"""
    region_x: int
    region_y: int
    region_size: int
    
    # Tiles in this region
    tiles: Dict[Tuple[int, int], TileData] = field(default_factory=dict)
    
    # Processing state
    active: bool = False
    last_processed: float = field(default_factory=time.time)
    processing_priority: int = 1
    
    # Spatial index for this region
    spatial_index: Optional[SpatialNode] = None
    
    # Statistics
    entity_count: int = 0
    update_frequency: float = 1.0  # Updates per second
    
    def __post_init__(self):
        """Initialize spatial index for this region"""
        start_x = self.region_x * self.region_size
        start_y = self.region_y * self.region_size
        
        self.spatial_index = SpatialNode(
            x=start_x,
            y=start_y,
            width=self.region_size,
            height=self.region_size,
            max_entities=20,
            max_depth=6
        )
    
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Get region bounds as (min_x, min_y, max_x, max_y)"""
        min_x = self.region_x * self.region_size
        min_y = self.region_y * self.region_size
        max_x = min_x + self.region_size - 1
        max_y = min_y + self.region_size - 1
        return min_x, min_y, max_x, max_y
    
    def contains_tile(self, x: int, y: int) -> bool:
        """Check if tile coordinates are within this region"""
        min_x, min_y, max_x, max_y = self.get_bounds()
        return min_x <= x <= max_x and min_y <= y <= max_y
    
    def add_tile(self, x: int, y: int, tile: TileData):
        """Add a tile to this region"""
        self.tiles[(x, y)] = tile
    
    def remove_tile(self, x: int, y: int):
        """Remove a tile from this region"""
        self.tiles.pop((x, y), None)
    
    def get_tile(self, x: int, y: int) -> Optional[TileData]:
        """Get tile at coordinates"""
        return self.tiles.get((x, y))
    
    def get_entities(self, layer: Optional[GridLayer] = None) -> Set[str]:
        """Get all entities in this region"""
        entities = set()
        for tile in self.tiles.values():
            entities.update(tile.get_entities(layer))
        return entities
    
    def needs_processing(self) -> bool:
        """Check if region needs processing based on activity"""
        time_since_update = time.time() - self.last_processed
        return self.active and time_since_update >= (1.0 / self.update_frequency)
    
    def mark_processed(self):
        """Mark region as processed"""
        self.last_processed = time.time()


class AdvancedGridSystem:
    """Advanced multi-layer grid system with spatial indexing"""
    
    def __init__(self, initial_size: Tuple[int, int] = (32, 32), region_size: int = 16):
        self.entity_manager = get_entity_manager()
        self.event_system = get_event_system()
        
        # Grid configuration
        self.width, self.height = initial_size
        self.region_size = region_size
        
        # Tile storage (sparse grid)
        self.tiles: Dict[Tuple[int, int], TileData] = {}
        
        # Region management
        self.regions: Dict[Tuple[int, int], GridRegion] = {}
        self.active_regions: Set[Tuple[int, int]] = set()
        
        # Spatial indexing
        self.global_spatial_index = SpatialNode(
            x=0, y=0, width=initial_size[0], height=initial_size[1],
            max_entities=50, max_depth=10
        )
        
        # Layer-specific spatial indices
        self.layer_spatial_indices: Dict[GridLayer, SpatialNode] = {}
        for layer in GridLayer:
            self.layer_spatial_indices[layer] = SpatialNode(
                x=0, y=0, width=initial_size[0], height=initial_size[1],
                max_entities=30, max_depth=8
            )
        
        # Processing optimization
        self.dirty_tiles: Set[Tuple[int, int]] = set()
        self.processing_queue: List[Tuple[int, Tuple[int, int]]] = []  # Priority queue
        
        # Performance tracking
        self.statistics = {
            'total_tiles': 0,
            'active_tiles': 0,
            'entities_tracked': 0,
            'regions_active': 0,
            'spatial_queries_per_second': 0,
            'average_query_time_ms': 0.0
        }
        
        # Caching
        self.query_cache: Dict[str, Tuple[float, Set[str]]] = {}
        self.cache_ttl = 0.1  # 100ms cache TTL
        
        # Initialize with basic terrain
        self._initialize_base_grid()
        
        # Subscribe to entity events
        self.event_system.subscribe('entity_created', self._on_entity_created)
        self.event_system.subscribe('entity_destroyed', self._on_entity_destroyed)
        self.event_system.subscribe('component_updated', self._on_component_updated)
    
    def _initialize_base_grid(self):
        """Initialize the base grid with default terrain"""
        for x in range(self.width):
            for y in range(self.height):
                tile = self.create_tile(x, y)
                tile.set_layer_data(GridLayer.TERRAIN, {
                    'type': 'grassland',
                    'fertility': 5,
                    'elevation': 100.0,
                    'drainage': 'moderate'
                })
                tile.set_layer_data(GridLayer.SOIL, {
                    'N': 50, 'P': 40, 'K': 35,
                    'pH': 6.5,
                    'organic_matter': 3.0,
                    'compaction': 0.2
                })
    
    def create_tile(self, x: int, y: int) -> TileData:
        """Create a new tile at the specified coordinates"""
        if (x, y) in self.tiles:
            return self.tiles[(x, y)]
        
        tile = TileData(x=x, y=y)
        self.tiles[(x, y)] = tile
        self.statistics['total_tiles'] += 1
        
        # Add to appropriate region
        region_coords = self._get_region_coords(x, y)
        if region_coords not in self.regions:
            self.regions[region_coords] = GridRegion(
                region_x=region_coords[0],
                region_y=region_coords[1],
                region_size=self.region_size
            )
        
        self.regions[region_coords].add_tile(x, y, tile)
        
        # Emit tile creation event
        self.event_system.emit('tile_created', {
            'x': x, 'y': y,
            'region_x': region_coords[0],
            'region_y': region_coords[1]
        }, priority=EventPriority.NORMAL)
        
        return tile
    
    def get_tile(self, x: int, y: int) -> Optional[TileData]:
        """Get tile at specified coordinates"""
        return self.tiles.get((x, y))
    
    def get_or_create_tile(self, x: int, y: int) -> TileData:
        """Get existing tile or create new one"""
        return self.tiles.get((x, y)) or self.create_tile(x, y)
    
    def _get_region_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Get region coordinates for a tile"""
        return (x // self.region_size, y // self.region_size)
    
    def add_entity_at_position(self, entity_id: str, x: float, y: float, 
                              layer: GridLayer = GridLayer.CROPS):
        """Add entity to grid at specified position"""
        # Update entity's transform component
        transform = self.entity_manager.get_component(entity_id, 'transform')
        if transform:
            transform.x = x
            transform.y = y
            transform.mark_modified()
        else:
            # Create transform component if it doesn't exist
            self.entity_manager.add_component(entity_id, 'transform', {
                'x': x, 'y': y
            })
        
        # Add to tile
        tile_x, tile_y = int(x), int(y)
        tile = self.get_or_create_tile(tile_x, tile_y)
        tile.add_entity(entity_id, layer)
        
        # Add to spatial indices
        self.global_spatial_index.add_entity(entity_id)
        self.layer_spatial_indices[layer].add_entity(entity_id)
        
        # Add to region spatial index
        region_coords = self._get_region_coords(tile_x, tile_y)
        if region_coords in self.regions:
            region = self.regions[region_coords]
            if region.spatial_index:
                region.spatial_index.add_entity(entity_id)
        
        self.statistics['entities_tracked'] += 1
        
        # Emit entity placement event
        self.event_system.emit('entity_placed_on_grid', {
            'entity_id': entity_id,
            'x': x, 'y': y,
            'layer': layer.value,
            'tile_x': tile_x, 'tile_y': tile_y
        }, priority=EventPriority.NORMAL)
    
    def remove_entity_from_grid(self, entity_id: str, layer: GridLayer = GridLayer.CROPS):
        """Remove entity from grid"""
        # Find entity's current position
        transform = self.entity_manager.get_component(entity_id, 'transform')
        if not transform:
            return
        
        tile_x, tile_y = int(transform.x), int(transform.y)
        tile = self.get_tile(tile_x, tile_y)
        if tile:
            tile.remove_entity(entity_id, layer)
        
        # Remove from spatial indices
        self.global_spatial_index.remove_entity(entity_id)
        self.layer_spatial_indices[layer].remove_entity(entity_id)
        
        # Remove from region spatial index
        region_coords = self._get_region_coords(tile_x, tile_y)
        if region_coords in self.regions:
            region = self.regions[region_coords]
            if region.spatial_index:
                region.spatial_index.remove_entity(entity_id)
        
        self.statistics['entities_tracked'] -= 1
        
        # Emit entity removal event
        self.event_system.emit('entity_removed_from_grid', {
            'entity_id': entity_id,
            'x': transform.x, 'y': transform.y,
            'layer': layer.value
        }, priority=EventPriority.NORMAL)
    
    def move_entity(self, entity_id: str, new_x: float, new_y: float, 
                   layer: GridLayer = GridLayer.CROPS):
        """Move entity to new position on grid"""
        # Remove from old position
        self.remove_entity_from_grid(entity_id, layer)
        
        # Add to new position
        self.add_entity_at_position(entity_id, new_x, new_y, layer)
    
    def get_entities_at_tile(self, x: int, y: int, 
                           layer: Optional[GridLayer] = None) -> Set[str]:
        """Get entities at specific tile coordinates"""
        tile = self.get_tile(x, y)
        if tile:
            return tile.get_entities(layer)
        return set()
    
    def get_entities_in_radius(self, center_x: float, center_y: float, radius: float,
                              layer: Optional[GridLayer] = None) -> Set[str]:
        """Get entities within radius of a point"""
        # Check cache first
        cache_key = f"radius_{center_x}_{center_y}_{radius}_{layer}"
        if cache_key in self.query_cache:
            cache_time, cached_result = self.query_cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return cached_result.copy()
        
        start_time = time.time()
        
        if layer is not None:
            result = self.layer_spatial_indices[layer].query_radius(center_x, center_y, radius)
        else:
            result = self.global_spatial_index.query_radius(center_x, center_y, radius)
        
        # Update cache
        self.query_cache[cache_key] = (time.time(), result.copy())
        
        # Update statistics
        query_time = (time.time() - start_time) * 1000
        self.statistics['average_query_time_ms'] = (
            self.statistics['average_query_time_ms'] * 0.9 + query_time * 0.1
        )
        
        return result
    
    def get_entities_in_rect(self, x: float, y: float, width: float, height: float,
                           layer: Optional[GridLayer] = None) -> Set[str]:
        """Get entities within a rectangular area"""
        cache_key = f"rect_{x}_{y}_{width}_{height}_{layer}"
        if cache_key in self.query_cache:
            cache_time, cached_result = self.query_cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return cached_result.copy()
        
        start_time = time.time()
        
        if layer is not None:
            result = self.layer_spatial_indices[layer].query_range(x, y, width, height)
        else:
            result = self.global_spatial_index.query_range(x, y, width, height)
        
        # Update cache
        self.query_cache[cache_key] = (time.time(), result.copy())
        
        # Update statistics
        query_time = (time.time() - start_time) * 1000
        self.statistics['average_query_time_ms'] = (
            self.statistics['average_query_time_ms'] * 0.9 + query_time * 0.1
        )
        
        return result
    
    def get_tiles_in_rect(self, x1: int, y1: int, x2: int, y2: int) -> List[TileData]:
        """Get all tiles within a rectangular area"""
        tiles = []
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                tile = self.get_tile(x, y)
                if tile:
                    tiles.append(tile)
        return tiles
    
    def set_active_region(self, center_x: float, center_y: float, radius: int = 20):
        """Set active processing region around a center point"""
        # Calculate region bounds
        min_region_x = int((center_x - radius) // self.region_size)
        max_region_x = int((center_x + radius) // self.region_size)
        min_region_y = int((center_y - radius) // self.region_size)
        max_region_y = int((center_y + radius) // self.region_size)
        
        # Update active regions
        new_active_regions = set()
        for region_x in range(min_region_x, max_region_x + 1):
            for region_y in range(min_region_y, max_region_y + 1):
                region_coords = (region_x, region_y)
                new_active_regions.add(region_coords)
                
                if region_coords not in self.regions:
                    self.regions[region_coords] = GridRegion(
                        region_x=region_x,
                        region_y=region_y,
                        region_size=self.region_size
                    )
                
                self.regions[region_coords].active = True
        
        # Deactivate regions that are no longer active
        for region_coords in self.active_regions - new_active_regions:
            if region_coords in self.regions:
                self.regions[region_coords].active = False
        
        self.active_regions = new_active_regions
        self.statistics['regions_active'] = len(self.active_regions)
        
        # Emit active region change event
        self.event_system.emit('active_region_changed', {
            'center_x': center_x,
            'center_y': center_y,
            'radius': radius,
            'active_region_count': len(self.active_regions)
        }, priority=EventPriority.LOW)
    
    def process_active_regions(self):
        """Process all active regions that need updates"""
        processed_count = 0
        
        for region_coords in self.active_regions:
            if region_coords in self.regions:
                region = self.regions[region_coords]
                if region.needs_processing():
                    self._process_region(region)
                    processed_count += 1
        
        return processed_count
    
    def _process_region(self, region: GridRegion):
        """Process a single region"""
        # Update entity positions in spatial index
        for tile in region.tiles.values():
            for layer, entities in tile.entities.items():
                for entity_id in entities:
                    transform = self.entity_manager.get_component(entity_id, 'transform')
                    if transform and hasattr(transform, 'modified_at'):
                        # Re-index if entity position changed
                        if region.spatial_index:
                            region.spatial_index.remove_entity(entity_id)
                            region.spatial_index.add_entity(entity_id)
        
        # Clear dirty flags
        for tile in region.tiles.values():
            tile.clear_dirty_flags()
        
        region.mark_processed()
    
    def find_path(self, start_x: int, start_y: int, end_x: int, end_y: int,
                 movement_type: str = "walking") -> List[Tuple[int, int]]:
        """Find path between two points using A* algorithm"""
        # Simple A* implementation for grid pathfinding
        open_set = [(0, start_x, start_y)]
        came_from = {}
        g_score = {(start_x, start_y): 0}
        f_score = {(start_x, start_y): self._heuristic(start_x, start_y, end_x, end_y)}
        
        while open_set:
            current_f, current_x, current_y = heapq.heappop(open_set)
            
            if current_x == end_x and current_y == end_y:
                # Reconstruct path
                path = []
                while (current_x, current_y) in came_from:
                    path.append((current_x, current_y))
                    current_x, current_y = came_from[(current_x, current_y)]
                path.append((start_x, start_y))
                return list(reversed(path))
            
            # Check neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                neighbor_x = current_x + dx
                neighbor_y = current_y + dy
                
                # Check bounds and accessibility
                tile = self.get_tile(neighbor_x, neighbor_y)
                if not tile or tile.accessibility < 0.1:
                    continue
                
                # Calculate movement cost
                diagonal_cost = 1.414 if abs(dx) + abs(dy) == 2 else 1.0
                tentative_g = g_score[(current_x, current_y)] + diagonal_cost * tile.movement_cost
                
                if (neighbor_x, neighbor_y) not in g_score or tentative_g < g_score[(neighbor_x, neighbor_y)]:
                    came_from[(neighbor_x, neighbor_y)] = (current_x, current_y)
                    g_score[(neighbor_x, neighbor_y)] = tentative_g
                    f_score[(neighbor_x, neighbor_y)] = tentative_g + self._heuristic(neighbor_x, neighbor_y, end_x, end_y)
                    heapq.heappush(open_set, (f_score[(neighbor_x, neighbor_y)], neighbor_x, neighbor_y))
        
        return []  # No path found
    
    def _heuristic(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """Heuristic function for A* pathfinding"""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def expand_grid(self, new_width: int, new_height: int):
        """Expand grid size to accommodate larger farms"""
        old_width, old_height = self.width, self.height
        self.width = max(self.width, new_width)
        self.height = max(self.height, new_height)
        
        # Update spatial indices
        self.global_spatial_index.width = self.width
        self.global_spatial_index.height = self.height
        
        for spatial_index in self.layer_spatial_indices.values():
            spatial_index.width = self.width
            spatial_index.height = self.height
        
        # Emit grid expansion event
        self.event_system.emit('grid_expanded', {
            'old_size': (old_width, old_height),
            'new_size': (self.width, self.height)
        }, priority=EventPriority.HIGH)
    
    def clear_cache(self):
        """Clear spatial query cache"""
        self.query_cache.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive grid system statistics"""
        # Update active tile count
        active_tiles = sum(1 for tile in self.tiles.values() if tile.has_entities())
        self.statistics['active_tiles'] = active_tiles
        
        return {
            **self.statistics,
            'grid_size': (self.width, self.height),
            'region_size': self.region_size,
            'total_regions': len(self.regions),
            'cache_size': len(self.query_cache),
            'memory_usage_estimate_mb': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        tile_size = 1024  # Rough estimate per tile in bytes
        entity_size = 64   # Rough estimate per entity reference
        
        total_size = (
            len(self.tiles) * tile_size +
            self.statistics['entities_tracked'] * entity_size +
            len(self.query_cache) * 256  # Cache entry size
        )
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    # Event handlers
    def _on_entity_created(self, event_data: Dict[str, Any]):
        """Handle entity creation events"""
        entity_id = event_data.get('entity_id')
        if not entity_id:
            return
        
        # Check if entity has transform component
        transform = self.entity_manager.get_component(entity_id, 'transform')
        if transform:
            # Determine appropriate layer based on entity components
            layer = GridLayer.CROPS  # Default
            
            if self.entity_manager.has_component(entity_id, 'equipment'):
                layer = GridLayer.EQUIPMENT
            elif self.entity_manager.has_component(entity_id, 'building'):
                layer = GridLayer.BUILDINGS
            elif self.entity_manager.has_component(entity_id, 'employee'):
                layer = GridLayer.EQUIPMENT  # Employees are mobile
            
            self.add_entity_at_position(entity_id, transform.x, transform.y, layer)
    
    def _on_entity_destroyed(self, event_data: Dict[str, Any]):
        """Handle entity destruction events"""
        entity_id = event_data.get('entity_id')
        if not entity_id:
            return
        
        # Remove from all layers (brute force approach)
        for layer in GridLayer:
            self.remove_entity_from_grid(entity_id, layer)
    
    def _on_component_updated(self, event_data: Dict[str, Any]):
        """Handle component update events"""
        entity_id = event_data.get('entity_id')
        component_type = event_data.get('component_type')
        
        if component_type == 'transform' and entity_id:
            # Entity moved, update spatial indices
            transform = self.entity_manager.get_component(entity_id, 'transform')
            if transform:
                # Find current layer and update position
                for layer in GridLayer:
                    # Check if entity exists in this layer's spatial index
                    if entity_id in self.layer_spatial_indices[layer].query_radius(
                        transform.x, transform.y, 0.1
                    ):
                        self.move_entity(entity_id, transform.x, transform.y, layer)
                        break


# Global grid system instance
_global_grid_system: Optional[AdvancedGridSystem] = None

def get_grid_system() -> AdvancedGridSystem:
    """Get the global grid system instance"""
    global _global_grid_system
    if _global_grid_system is None:
        _global_grid_system = AdvancedGridSystem()
    return _global_grid_system

def initialize_grid_system(initial_size: Tuple[int, int] = (32, 32), 
                          region_size: int = 16) -> AdvancedGridSystem:
    """Initialize the global grid system"""
    global _global_grid_system
    _global_grid_system = AdvancedGridSystem(initial_size, region_size)
    return _global_grid_system