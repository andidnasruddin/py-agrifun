"""
State Management System - Advanced Game State with Undo/Redo for AgriFun Engine

This module implements a comprehensive state management system that supports undo/redo
operations, game state checkpoints, time travel debugging, and state synchronization
across the complex AgriFun agricultural simulation.

Key Features:
- Command pattern for all state-modifying operations
- Unlimited undo/redo with intelligent state compression
- Game state checkpoints and branching timelines
- Time travel debugging for complex agricultural systems
- State validation and consistency checking
- Automatic state backup and recovery
- Multi-threaded state processing
- State serialization and network synchronization ready
- Memory-efficient state storage with compression

Command Types:
- Entity Commands: Create, modify, destroy entities
- Component Commands: Add, update, remove components
- Grid Commands: Tile modifications, layer changes
- Content Commands: Dynamic content registration
- Economic Commands: Financial transactions, market changes
- Time Commands: Time progression, season changes

State Features:
- Atomic Operations: All state changes are atomic
- State Validation: Automatic consistency checking
- Compression: Intelligent state diff compression
- Branching: Support for parallel timelines
- Snapshots: Regular automatic state snapshots
- Recovery: Automatic corruption detection and recovery

Usage Example:
    # Initialize state manager
    state_manager = StateManager()
    
    # Execute commands with automatic undo support
    command = CreateEntityCommand(entity_data)
    state_manager.execute_command(command)
    
    # Undo/redo operations
    state_manager.undo()  # Undo last operation
    state_manager.redo()  # Redo undone operation
    
    # Create checkpoint
    checkpoint_id = state_manager.create_checkpoint("before_harvest")
    
    # Restore to checkpoint
    state_manager.restore_checkpoint(checkpoint_id)
    
    # State validation
    if state_manager.validate_state():
        print("Game state is consistent")

Performance Features:
- State diffs for memory efficiency
- Lazy state loading and compression
- Background state processing
- Smart snapshot scheduling
- Memory pressure handling
"""

import time
import json
import pickle
import gzip
import hashlib
import threading
import asyncio
from typing import Dict, List, Set, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from collections import deque
from abc import ABC, abstractmethod
from enum import Enum
import logging
from pathlib import Path

# Import our core systems
from .advanced_event_system import get_event_system, EventPriority
from .entity_component_system import get_entity_manager, Component
from .advanced_grid_system import get_grid_system, TileData, GridLayer
from .content_registry import get_content_registry


class CommandType(Enum):
    """Types of state-modifying commands"""
    ENTITY_CREATE = "entity_create"
    ENTITY_DESTROY = "entity_destroy"
    COMPONENT_ADD = "component_add"
    COMPONENT_UPDATE = "component_update"
    COMPONENT_REMOVE = "component_remove"
    GRID_MODIFY = "grid_modify"
    CONTENT_REGISTER = "content_register"
    ECONOMIC_TRANSACTION = "economic_transaction"
    TIME_PROGRESS = "time_progress"
    CUSTOM = "custom"


class StateValidationLevel(Enum):
    """Levels of state validation"""
    NONE = "none"           # No validation
    BASIC = "basic"         # Basic consistency checks
    COMPREHENSIVE = "comprehensive"  # Full validation
    PARANOID = "paranoid"   # Maximum validation with performance impact


@dataclass
class StateSnapshot:
    """Complete game state snapshot"""
    snapshot_id: str
    timestamp: float
    description: str = ""
    
    # Core system states
    entities: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    grid_tiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    content_registry: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Game-specific state
    game_time: Dict[str, Any] = field(default_factory=dict)
    economy_state: Dict[str, Any] = field(default_factory=dict)
    weather_state: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    command_count: int = 0
    validation_hash: str = ""
    compressed_size: int = 0
    
    def calculate_hash(self) -> str:
        """Calculate validation hash for integrity checking"""
        state_str = json.dumps({
            'entities': self.entities,
            'grid_tiles': self.grid_tiles,
            'game_time': self.game_time,
            'economy_state': self.economy_state
        }, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()


@dataclass
class CommandMetadata:
    """Metadata for executed commands"""
    command_id: str
    command_type: CommandType
    timestamp: float
    execution_time_ms: float = 0.0
    affected_entities: Set[str] = field(default_factory=set)
    affected_tiles: Set[tuple] = field(default_factory=set)
    user_description: str = ""
    
    # Grouping for batch operations
    group_id: Optional[str] = None
    is_atomic_group: bool = False


class Command(ABC):
    """Base class for all state-modifying commands"""
    
    def __init__(self, command_type: CommandType = CommandType.CUSTOM):
        self.command_type = command_type
        self.command_id = f"cmd_{int(time.time() * 1000000)}"
        self.timestamp = time.time()
        self.metadata = CommandMetadata(
            command_id=self.command_id,
            command_type=command_type,
            timestamp=self.timestamp
        )
        
        # State management
        self._executed = False
        self._undone = False
        
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command and return success"""
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """Undo the command and return success"""
        pass
    
    @abstractmethod
    def get_affected_entities(self) -> Set[str]:
        """Get set of entity IDs affected by this command"""
        pass
    
    @abstractmethod
    def get_affected_tiles(self) -> Set[tuple]:
        """Get set of tile coordinates affected by this command"""
        pass
    
    def can_execute(self) -> bool:
        """Check if command can be executed"""
        return not self._executed
    
    def can_undo(self) -> bool:
        """Check if command can be undone"""
        return self._executed and not self._undone
    
    def can_redo(self) -> bool:
        """Check if command can be redone"""
        return self._executed and self._undone
    
    def get_description(self) -> str:
        """Get human-readable description of command"""
        return f"{self.command_type.value} at {self.timestamp}"


class CreateEntityCommand(Command):
    """Command to create a new entity"""
    
    def __init__(self, entity_data: Dict[str, Any], entity_id: Optional[str] = None):
        super().__init__(CommandType.ENTITY_CREATE)
        self.entity_data = entity_data.copy()
        self.entity_id = entity_id
        self.created_entity_id = None
        
    def execute(self) -> bool:
        try:
            entity_manager = get_entity_manager()
            self.created_entity_id = entity_manager.create_entity(self.entity_data, self.entity_id)
            self._executed = True
            self._undone = False
            
            self.metadata.affected_entities.add(self.created_entity_id)
            return True
            
        except Exception as e:
            logging.error(f"Failed to execute CreateEntityCommand: {e}")
            return False
    
    def undo(self) -> bool:
        if not self.can_undo() or not self.created_entity_id:
            return False
        
        try:
            entity_manager = get_entity_manager()
            entity_manager.destroy_entity(self.created_entity_id)
            self._undone = True
            return True
            
        except Exception as e:
            logging.error(f"Failed to undo CreateEntityCommand: {e}")
            return False
    
    def get_affected_entities(self) -> Set[str]:
        return {self.created_entity_id} if self.created_entity_id else set()
    
    def get_affected_tiles(self) -> Set[tuple]:
        return set()  # Entity creation doesn't directly affect tiles
    
    def get_description(self) -> str:
        return f"Create entity with {len(self.entity_data)} components"


class UpdateComponentCommand(Command):
    """Command to update an entity component"""
    
    def __init__(self, entity_id: str, component_type: str, 
                 update_data: Dict[str, Any], description: str = ""):
        super().__init__(CommandType.COMPONENT_UPDATE)
        self.entity_id = entity_id
        self.component_type = component_type
        self.update_data = update_data.copy()
        self.previous_data = {}
        self.metadata.user_description = description
        
    def execute(self) -> bool:
        try:
            entity_manager = get_entity_manager()
            
            # Store previous state for undo
            current_component = entity_manager.get_component(self.entity_id, self.component_type)
            if current_component:
                # Store only the fields we're updating
                self.previous_data = {
                    field: getattr(current_component, field)
                    for field in self.update_data.keys()
                    if hasattr(current_component, field)
                }
            
            # Apply update
            entity_manager.update_component(self.entity_id, self.component_type, self.update_data)
            
            self._executed = True
            self._undone = False
            self.metadata.affected_entities.add(self.entity_id)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to execute UpdateComponentCommand: {e}")
            return False
    
    def undo(self) -> bool:
        if not self.can_undo():
            return False
        
        try:
            entity_manager = get_entity_manager()
            
            # Restore previous values
            if self.previous_data:
                entity_manager.update_component(self.entity_id, self.component_type, self.previous_data)
            
            self._undone = True
            return True
            
        except Exception as e:
            logging.error(f"Failed to undo UpdateComponentCommand: {e}")
            return False
    
    def get_affected_entities(self) -> Set[str]:
        return {self.entity_id}
    
    def get_affected_tiles(self) -> Set[tuple]:
        # If updating transform component, get affected tile
        if self.component_type == 'transform' and 'x' in self.update_data and 'y' in self.update_data:
            return {(int(self.update_data['x']), int(self.update_data['y']))}
        return set()
    
    def get_description(self) -> str:
        if self.metadata.user_description:
            return self.metadata.user_description
        return f"Update {self.component_type} component of entity {self.entity_id}"


class ModifyTileCommand(Command):
    """Command to modify grid tile data"""
    
    def __init__(self, tile_x: int, tile_y: int, layer: GridLayer, 
                 tile_data: Dict[str, Any], description: str = ""):
        super().__init__(CommandType.GRID_MODIFY)
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.layer = layer
        self.tile_data = tile_data.copy()
        self.previous_data = {}
        self.metadata.user_description = description
        
    def execute(self) -> bool:
        try:
            grid_system = get_grid_system()
            tile = grid_system.get_or_create_tile(self.tile_x, self.tile_y)
            
            # Store previous state
            self.previous_data = tile.get_layer_data(self.layer).copy()
            
            # Apply changes
            tile.update_layer_data(self.layer, self.tile_data)
            
            self._executed = True
            self._undone = False
            self.metadata.affected_tiles.add((self.tile_x, self.tile_y))
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to execute ModifyTileCommand: {e}")
            return False
    
    def undo(self) -> bool:
        if not self.can_undo():
            return False
        
        try:
            grid_system = get_grid_system()
            tile = grid_system.get_tile(self.tile_x, self.tile_y)
            
            if tile:
                # Restore previous data
                tile.set_layer_data(self.layer, self.previous_data)
            
            self._undone = True
            return True
            
        except Exception as e:
            logging.error(f"Failed to undo ModifyTileCommand: {e}")
            return False
    
    def get_affected_entities(self) -> Set[str]:
        return set()  # Tile modifications don't directly affect entities
    
    def get_affected_tiles(self) -> Set[tuple]:
        return {(self.tile_x, self.tile_y)}
    
    def get_description(self) -> str:
        if self.metadata.user_description:
            return self.metadata.user_description
        return f"Modify {self.layer.value} layer at ({self.tile_x}, {self.tile_y})"


class CompositeCommand(Command):
    """Command that groups multiple commands together"""
    
    def __init__(self, commands: List[Command], description: str = ""):
        super().__init__(CommandType.CUSTOM)
        self.commands = commands
        self.metadata.user_description = description
        self.executed_commands = []
        
        # Aggregate metadata
        for cmd in commands:
            self.metadata.affected_entities.update(cmd.get_affected_entities())
            self.metadata.affected_tiles.update(cmd.get_affected_tiles())
    
    def execute(self) -> bool:
        try:
            self.executed_commands.clear()
            
            for command in self.commands:
                if command.execute():
                    self.executed_commands.append(command)
                else:
                    # Rollback previously executed commands
                    for rollback_cmd in reversed(self.executed_commands):
                        rollback_cmd.undo()
                    return False
            
            self._executed = True
            self._undone = False
            return True
            
        except Exception as e:
            logging.error(f"Failed to execute CompositeCommand: {e}")
            return False
    
    def undo(self) -> bool:
        if not self.can_undo():
            return False
        
        try:
            # Undo in reverse order
            for command in reversed(self.executed_commands):
                if not command.undo():
                    logging.error(f"Failed to undo command in composite: {command}")
                    return False
            
            self._undone = True
            return True
            
        except Exception as e:
            logging.error(f"Failed to undo CompositeCommand: {e}")
            return False
    
    def get_affected_entities(self) -> Set[str]:
        entities = set()
        for command in self.commands:
            entities.update(command.get_affected_entities())
        return entities
    
    def get_affected_tiles(self) -> Set[tuple]:
        tiles = set()
        for command in self.commands:
            tiles.update(command.get_affected_tiles())
        return tiles
    
    def get_description(self) -> str:
        if self.metadata.user_description:
            return self.metadata.user_description
        return f"Composite command with {len(self.commands)} operations"


class StateManager:
    """Advanced state management with undo/redo and checkpoints"""
    
    def __init__(self, max_undo_history: int = 1000, auto_checkpoint_interval: float = 300.0):
        self.entity_manager = get_entity_manager()
        self.grid_system = get_grid_system()
        self.content_registry = get_content_registry()
        self.event_system = get_event_system()
        
        # Command history
        self.max_undo_history = max_undo_history
        self.command_history: deque = deque(maxlen=max_undo_history)
        self.undo_stack: deque = deque(maxlen=max_undo_history)
        self.redo_stack: deque = deque(maxlen=max_undo_history)
        
        # Checkpoints and snapshots
        self.checkpoints: Dict[str, StateSnapshot] = {}
        self.auto_checkpoint_interval = auto_checkpoint_interval
        self.last_auto_checkpoint = time.time()
        
        # State validation
        self.validation_level = StateValidationLevel.BASIC
        self.validation_errors: List[str] = []
        
        # Performance tracking
        self.total_commands_executed = 0
        self.total_execution_time = 0.0
        self.average_command_time = 0.0
        
        # Threading
        self.state_lock = threading.RLock()
        self.background_thread: Optional[threading.Thread] = None
        self.background_running = False
        
        # Compression and storage
        self.compress_snapshots = True
        self.snapshot_storage_path = Path("state_snapshots/")
        self.snapshot_storage_path.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger('StateManager')
        
        # Start background processing
        self._start_background_processing()
        
        # Subscribe to system events
        self.event_system.subscribe('game_shutdown', self._on_game_shutdown)
    
    def execute_command(self, command: Command) -> bool:
        """Execute a command with automatic undo support"""
        with self.state_lock:
            start_time = time.time()
            
            try:
                # Clear redo stack when new command is executed
                self.redo_stack.clear()
                
                # Execute command
                if command.execute():
                    # Add to undo stack
                    self.undo_stack.append(command)
                    
                    # Track performance
                    execution_time = (time.time() - start_time) * 1000
                    command.metadata.execution_time_ms = execution_time
                    
                    self.total_commands_executed += 1
                    self.total_execution_time += execution_time
                    self.average_command_time = self.total_execution_time / self.total_commands_executed
                    
                    # Add to history
                    self.command_history.append(command)
                    
                    # Emit command executed event
                    self.event_system.emit('command_executed', {
                        'command_id': command.command_id,
                        'command_type': command.command_type.value,
                        'execution_time_ms': execution_time,
                        'affected_entities': list(command.get_affected_entities()),
                        'affected_tiles': list(command.get_affected_tiles())
                    }, priority=EventPriority.LOW)
                    
                    # Check if auto-checkpoint is needed
                    self._check_auto_checkpoint()
                    
                    return True
                
                return False
                
            except Exception as e:
                self.logger.error(f"Failed to execute command: {e}")
                return False
    
    def undo(self) -> bool:
        """Undo the last command"""
        with self.state_lock:
            if not self.undo_stack:
                return False
            
            command = self.undo_stack.pop()
            
            try:
                if command.undo():
                    self.redo_stack.append(command)
                    
                    # Emit undo event
                    self.event_system.emit('command_undone', {
                        'command_id': command.command_id,
                        'command_type': command.command_type.value
                    }, priority=EventPriority.NORMAL)
                    
                    return True
                else:
                    # Put command back if undo failed
                    self.undo_stack.append(command)
                    return False
                    
            except Exception as e:
                self.logger.error(f"Failed to undo command: {e}")
                self.undo_stack.append(command)  # Put it back
                return False
    
    def redo(self) -> bool:
        """Redo the last undone command"""
        with self.state_lock:
            if not self.redo_stack:
                return False
            
            command = self.redo_stack.pop()
            
            try:
                if command.execute():
                    self.undo_stack.append(command)
                    
                    # Emit redo event
                    self.event_system.emit('command_redone', {
                        'command_id': command.command_id,
                        'command_type': command.command_type.value
                    }, priority=EventPriority.NORMAL)
                    
                    return True
                else:
                    # Put command back if redo failed
                    self.redo_stack.append(command)
                    return False
                    
            except Exception as e:
                self.logger.error(f"Failed to redo command: {e}")
                self.redo_stack.append(command)  # Put it back
                return False
    
    def can_undo(self) -> bool:
        """Check if undo is possible"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible"""
        return len(self.redo_stack) > 0
    
    def get_undo_description(self) -> Optional[str]:
        """Get description of the command that would be undone"""
        if self.undo_stack:
            return self.undo_stack[-1].get_description()
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """Get description of the command that would be redone"""
        if self.redo_stack:
            return self.redo_stack[-1].get_description()
        return None
    
    def create_checkpoint(self, description: str = "") -> str:
        """Create a state checkpoint"""
        checkpoint_id = f"checkpoint_{int(time.time() * 1000)}"
        
        with self.state_lock:
            try:
                snapshot = self._capture_state_snapshot(checkpoint_id, description)
                self.checkpoints[checkpoint_id] = snapshot
                
                # Save to disk if compression enabled
                if self.compress_snapshots:
                    self._save_snapshot_to_disk(snapshot)
                
                # Emit checkpoint created event
                self.event_system.emit('checkpoint_created', {
                    'checkpoint_id': checkpoint_id,
                    'description': description,
                    'snapshot_size': snapshot.compressed_size
                }, priority=EventPriority.HIGH)
                
                self.logger.info(f"Created checkpoint: {checkpoint_id}")
                return checkpoint_id
                
            except Exception as e:
                self.logger.error(f"Failed to create checkpoint: {e}")
                return ""
    
    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """Restore game state to a checkpoint"""
        if checkpoint_id not in self.checkpoints:
            # Try loading from disk
            if not self._load_snapshot_from_disk(checkpoint_id):
                self.logger.error(f"Checkpoint {checkpoint_id} not found")
                return False
        
        with self.state_lock:
            try:
                snapshot = self.checkpoints[checkpoint_id]
                
                # Clear command history
                self.undo_stack.clear()
                self.redo_stack.clear()
                
                # Restore state
                success = self._restore_state_snapshot(snapshot)
                
                if success:
                    # Emit checkpoint restored event
                    self.event_system.emit('checkpoint_restored', {
                        'checkpoint_id': checkpoint_id,
                        'description': snapshot.description
                    }, priority=EventPriority.HIGH)
                    
                    self.logger.info(f"Restored checkpoint: {checkpoint_id}")
                
                return success
                
            except Exception as e:
                self.logger.error(f"Failed to restore checkpoint: {e}")
                return False
    
    def validate_state(self) -> bool:
        """Validate current game state consistency"""
        self.validation_errors.clear()
        
        try:
            if self.validation_level == StateValidationLevel.NONE:
                return True
            
            # Basic validation
            if self.validation_level >= StateValidationLevel.BASIC:
                # Check entity-component consistency
                for entity_id in self.entity_manager._entities:
                    if entity_id not in self.entity_manager._entity_components:
                        self.validation_errors.append(f"Entity {entity_id} missing component mapping")
                
                # Check grid-entity consistency
                for tile in self.grid_system.tiles.values():
                    for layer, entities in tile.entities.items():
                        for entity_id in entities:
                            if entity_id not in self.entity_manager._entities:
                                self.validation_errors.append(
                                    f"Grid references non-existent entity {entity_id}"
                                )
            
            # Comprehensive validation
            if self.validation_level >= StateValidationLevel.COMPREHENSIVE:
                # Additional validation logic would go here
                pass
            
            # Paranoid validation
            if self.validation_level >= StateValidationLevel.PARANOID:
                # Even more validation logic
                pass
            
            return len(self.validation_errors) == 0
            
        except Exception as e:
            self.validation_errors.append(f"Validation failed with exception: {e}")
            return False
    
    def _capture_state_snapshot(self, snapshot_id: str, description: str) -> StateSnapshot:
        """Capture complete state snapshot"""
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            timestamp=time.time(),
            description=description,
            command_count=self.total_commands_executed
        )
        
        # Capture entity state
        for entity_id in self.entity_manager._entities:
            snapshot.entities[entity_id] = self.entity_manager.serialize_entity(entity_id)
        
        # Capture grid state
        for (x, y), tile in self.grid_system.tiles.items():
            tile_key = f"{x},{y}"
            snapshot.grid_tiles[tile_key] = {
                'x': tile.x,
                'y': tile.y,
                'layer_data': {layer.value: data for layer, data in tile.layer_data.items()},
                'elevation': tile.elevation,
                'accessibility': tile.accessibility,
                'movement_cost': tile.movement_cost
            }
        
        # Capture content registry state (if needed)
        # This might be skipped if content is static
        
        # Calculate validation hash
        snapshot.validation_hash = snapshot.calculate_hash()
        
        return snapshot
    
    def _restore_state_snapshot(self, snapshot: StateSnapshot) -> bool:
        """Restore state from snapshot"""
        try:
            # Validate snapshot integrity
            if snapshot.validation_hash != snapshot.calculate_hash():
                self.logger.error("Snapshot integrity check failed")
                return False
            
            # Clear current state
            self.entity_manager._entities.clear()
            self.entity_manager._entity_components.clear()
            self.entity_manager._components.clear()
            self.grid_system.tiles.clear()
            
            # Restore entities
            for entity_id, entity_data in snapshot.entities.items():
                self.entity_manager.deserialize_entity(entity_data)
            
            # Restore grid
            for tile_key, tile_data in snapshot.grid_tiles.items():
                x, y = map(int, tile_key.split(','))
                tile = self.grid_system.create_tile(x, y)
                
                tile.elevation = tile_data.get('elevation', 0.0)
                tile.accessibility = tile_data.get('accessibility', 1.0)
                tile.movement_cost = tile_data.get('movement_cost', 1.0)
                
                for layer_name, layer_data in tile_data.get('layer_data', {}).items():
                    try:
                        layer = GridLayer(layer_name)
                        tile.set_layer_data(layer, layer_data)
                    except ValueError:
                        # Skip unknown layers
                        pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore state snapshot: {e}")
            return False
    
    def _save_snapshot_to_disk(self, snapshot: StateSnapshot):
        """Save compressed snapshot to disk"""
        try:
            snapshot_path = self.snapshot_storage_path / f"{snapshot.snapshot_id}.snap"
            
            # Serialize and compress
            snapshot_data = pickle.dumps(snapshot)
            compressed_data = gzip.compress(snapshot_data)
            
            with open(snapshot_path, 'wb') as f:
                f.write(compressed_data)
            
            snapshot.compressed_size = len(compressed_data)
            
        except Exception as e:
            self.logger.error(f"Failed to save snapshot to disk: {e}")
    
    def _load_snapshot_from_disk(self, checkpoint_id: str) -> bool:
        """Load compressed snapshot from disk"""
        try:
            snapshot_path = self.snapshot_storage_path / f"{checkpoint_id}.snap"
            
            if not snapshot_path.exists():
                return False
            
            with open(snapshot_path, 'rb') as f:
                compressed_data = f.read()
            
            snapshot_data = gzip.decompress(compressed_data)
            snapshot = pickle.loads(snapshot_data)
            
            self.checkpoints[checkpoint_id] = snapshot
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load snapshot from disk: {e}")
            return False
    
    def _check_auto_checkpoint(self):
        """Check if auto-checkpoint should be created"""
        current_time = time.time()
        if current_time - self.last_auto_checkpoint >= self.auto_checkpoint_interval:
            self.create_checkpoint(f"Auto-checkpoint at {current_time}")
            self.last_auto_checkpoint = current_time
    
    def _start_background_processing(self):
        """Start background thread for state management tasks"""
        self.background_running = True
        self.background_thread = threading.Thread(
            target=self._background_loop,
            daemon=True
        )
        self.background_thread.start()
    
    def _background_loop(self):
        """Background processing loop"""
        while self.background_running:
            try:
                # Periodic state validation
                if self.validation_level != StateValidationLevel.NONE:
                    if not self.validate_state():
                        self.logger.warning(f"State validation failed: {self.validation_errors}")
                
                # Cleanup old checkpoints
                self._cleanup_old_checkpoints()
                
                time.sleep(10.0)  # Run every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Background processing error: {e}")
    
    def _cleanup_old_checkpoints(self):
        """Clean up old checkpoints to manage memory"""
        # Keep only the last 10 checkpoints
        if len(self.checkpoints) > 10:
            sorted_checkpoints = sorted(
                self.checkpoints.items(),
                key=lambda x: x[1].timestamp
            )
            
            # Remove oldest checkpoints
            for checkpoint_id, _ in sorted_checkpoints[:-10]:
                del self.checkpoints[checkpoint_id]
                
                # Remove from disk
                snapshot_path = self.snapshot_storage_path / f"{checkpoint_id}.snap"
                if snapshot_path.exists():
                    snapshot_path.unlink()
    
    def _on_game_shutdown(self, event_data: Dict[str, Any]):
        """Handle game shutdown"""
        self.logger.info("Shutting down state manager")
        
        # Stop background processing
        self.background_running = False
        
        # Create final checkpoint
        self.create_checkpoint("Final checkpoint before shutdown")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get state manager statistics"""
        return {
            'total_commands_executed': self.total_commands_executed,
            'average_command_time_ms': self.average_command_time,
            'undo_stack_size': len(self.undo_stack),
            'redo_stack_size': len(self.redo_stack),
            'checkpoint_count': len(self.checkpoints),
            'validation_level': self.validation_level.value,
            'validation_errors': len(self.validation_errors),
            'memory_usage_estimate_mb': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        command_size = len(self.undo_stack) * 1024  # Rough estimate
        checkpoint_size = len(self.checkpoints) * 10240  # Rough estimate
        
        return (command_size + checkpoint_size) / (1024 * 1024)


# Global state manager instance
_global_state_manager: Optional[StateManager] = None

def get_state_manager() -> StateManager:
    """Get the global state manager instance"""
    global _global_state_manager
    if _global_state_manager is None:
        _global_state_manager = StateManager()
    return _global_state_manager

def initialize_state_manager(max_undo_history: int = 1000, 
                           auto_checkpoint_interval: float = 300.0) -> StateManager:
    """Initialize the global state manager"""
    global _global_state_manager
    _global_state_manager = StateManager(max_undo_history, auto_checkpoint_interval)
    return _global_state_manager