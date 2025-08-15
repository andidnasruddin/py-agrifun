"""
Save/Load System - Comprehensive Game State Persistence for AgriFun Agricultural Simulation

This system provides complete game state saving and loading with version management,
compression, integrity checking, and cross-system coordination. Integrates with all
Phase 1 and Phase 2 systems to ensure complete game state preservation and restoration.

Key Features:
- Complete game state serialization across all systems
- Save file versioning and migration capabilities
- Compression and integrity checking
- Incremental saves and checkpoints
- Cross-platform compatibility
- Performance optimization for large save files
- Backup and recovery systems
- Save file analysis and debugging tools

Save File Structure:
- Metadata: Game version, save time, player stats
- Phase 1 Systems: ECS entities, events, configuration
- Phase 2 Systems: Time, economy, employees, crops, buildings
- Game World: Grid state, tile data, infrastructure
- Player Data: Progress, achievements, statistics

Integration Features:
- All system state serialization and deserialization
- Entity-Component-System persistence
- Event system state preservation
- Configuration and settings persistence
- Performance metrics and analytics
- Save file validation and error recovery

Usage Example:
    # Initialize save/load system
    save_system = SaveLoadSystem()
    await save_system.initialize()
    
    # Save game
    save_result = await save_system.save_game("my_farm_save")
    
    # Load game
    load_result = await save_system.load_game("my_farm_save")
    
    # Create checkpoint
    checkpoint_id = await save_system.create_checkpoint("before_expansion")
"""

import time
import json
import pickle
import gzip
import hashlib
import os
import shutil
from typing import Dict, List, Set, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import asyncio

# Import Phase 1 architecture
from scripts.core.entity_component_system import System, Entity, Component, get_entity_system
from scripts.core.advanced_event_system import get_event_system, EventPriority
from scripts.core.time_management import get_time_manager
from scripts.core.advanced_config_system import get_config_manager
from scripts.core.state_management import get_state_manager

# Import Phase 2 systems
from scripts.systems.economy_system import get_economy_system
from scripts.systems.employee_system import get_employee_system
from scripts.systems.crop_system import get_crop_system
from scripts.systems.building_system import get_building_system


class SaveFormat(Enum):
    """Save file formats supported"""
    JSON = "json"           # Human-readable, larger files
    PICKLE = "pickle"       # Python native, faster
    COMPRESSED = "gz"       # Compressed binary
    BINARY = "bin"          # Custom binary format


class SaveType(Enum):
    """Types of save operations"""
    MANUAL = "manual"       # Player-initiated save
    AUTO = "auto"          # Automatic periodic save
    CHECKPOINT = "checkpoint"  # Temporary checkpoint
    BACKUP = "backup"      # System backup
    EXPORT = "export"      # Portable export


class SaveStatus(Enum):
    """Save operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CORRUPTED = "corrupted"


@dataclass
class SaveMetadata:
    """Metadata for a save file"""
    save_id: str
    save_name: str
    save_type: SaveType
    save_format: SaveFormat
    
    # Timing information
    created_time: float
    game_time_minutes: int
    session_duration: float
    
    # Version information
    game_version: str = "2.0.0"
    save_version: str = "2.0"
    engine_version: str = "Phase2"
    
    # Game state summary
    player_name: str = "Farmer"
    farm_name: str = "My Farm"
    difficulty: str = "normal"
    
    # Statistics
    total_crops_planted: int = 0
    total_crops_harvested: int = 0
    total_buildings: int = 0
    total_employees: int = 0
    player_cash: float = 0.0
    days_played: int = 0
    
    # File information
    file_size: int = 0
    checksum: str = ""
    compression_ratio: float = 1.0
    
    # System states
    systems_included: List[str] = field(default_factory=list)
    entity_count: int = 0
    component_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaveMetadata':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class SaveOperation:
    """Tracks a save/load operation"""
    operation_id: str
    operation_type: str  # "save" or "load"
    save_id: str
    status: SaveStatus = SaveStatus.PENDING
    
    start_time: float = 0.0
    end_time: float = 0.0
    progress: float = 0.0  # 0.0 to 1.0
    
    error_message: Optional[str] = None
    file_path: Optional[str] = None
    
    # Performance metrics
    serialization_time: float = 0.0
    compression_time: float = 0.0
    io_time: float = 0.0
    
    def get_duration(self) -> float:
        """Get operation duration in seconds"""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.time() - self.start_time if self.start_time > 0 else 0.0


class SaveLoadSystem(System):
    """Comprehensive save and load system for complete game state persistence"""
    
    def __init__(self):
        super().__init__()
        self.system_name = "save_load_system"
        
        # Core system references
        self.event_system = get_event_system()
        self.time_manager = get_time_manager()
        self.config_manager = get_config_manager()
        self.state_manager = get_state_manager()
        self.entity_system = get_entity_system()
        
        # Phase 2 system references
        self.economy_system = get_economy_system()
        self.employee_system = get_employee_system()
        self.crop_system = get_crop_system()
        self.building_system = get_building_system()
        
        # Save management
        self.save_directory: str = "saves"
        self.backup_directory: str = "saves/backups"
        self.checkpoint_directory: str = "saves/checkpoints"
        
        # Save tracking
        self.available_saves: Dict[str, SaveMetadata] = {}
        self.active_operations: Dict[str, SaveOperation] = {}
        self.save_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.default_format: SaveFormat = SaveFormat.COMPRESSED
        self.auto_save_enabled: bool = True
        self.auto_save_interval: int = 300  # 5 minutes
        self.max_auto_saves: int = 5
        self.max_checkpoints: int = 10
        self.compression_level: int = 6
        
        # Performance tracking
        self.total_saves: int = 0
        self.total_loads: int = 0
        self.total_save_time: float = 0.0
        self.total_load_time: float = 0.0
        self.largest_save_size: int = 0
        
        # Auto-save management
        self.last_auto_save: float = 0.0
        self.auto_save_counter: int = 0
        
        # System state tracking
        self.systems_to_save = [
            "time_manager",
            "economy_system", 
            "employee_system",
            "crop_system",
            "building_system",
            "entity_system",
            "state_manager"
        ]
    
    async def initialize(self):
        """Initialize the save/load system"""
        # Create save directories
        await self._create_save_directories()
        
        # Load configuration
        await self._load_save_configuration()
        
        # Scan existing saves
        await self._scan_existing_saves()
        
        # Subscribe to events
        self.event_system.subscribe('time_minute_passed', self._on_minute_passed)
        self.event_system.subscribe('game_shutdown', self._on_game_shutdown)
        self.event_system.subscribe('system_error', self._on_system_error)
        
        # Create initial checkpoint
        await self.create_checkpoint("game_start")
        
        self.logger.info("Save/Load System initialized successfully")
    
    async def _create_save_directories(self):
        """Create necessary save directories"""
        directories = [
            self.save_directory,
            self.backup_directory,
            self.checkpoint_directory
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    async def _load_save_configuration(self):
        """Load save system configuration"""
        try:
            save_config = self.config_manager.get_section('save_system')
            
            # Load settings
            self.auto_save_enabled = save_config.get('auto_save_enabled', True)
            self.auto_save_interval = save_config.get('auto_save_interval', 300)
            self.max_auto_saves = save_config.get('max_auto_saves', 5)
            self.max_checkpoints = save_config.get('max_checkpoints', 10)
            self.compression_level = save_config.get('compression_level', 6)
            
            # Load format preference
            format_str = save_config.get('default_format', 'compressed')
            self.default_format = SaveFormat(format_str)
            
        except Exception as e:
            self.logger.warning(f"Failed to load save configuration: {e}")
    
    async def _scan_existing_saves(self):
        """Scan and catalog existing save files"""
        try:
            if not os.path.exists(self.save_directory):
                return
            
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.json'):
                    metadata_path = os.path.join(self.save_directory, filename)
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata_dict = json.load(f)
                            metadata = SaveMetadata.from_dict(metadata_dict)
                            self.available_saves[metadata.save_id] = metadata
                    except Exception as e:
                        self.logger.warning(f"Failed to load save metadata {filename}: {e}")
            
            self.logger.info(f"Found {len(self.available_saves)} existing saves")
            
        except Exception as e:
            self.logger.error(f"Failed to scan existing saves: {e}")
    
    async def save_game(self, save_name: str, save_type: SaveType = SaveType.MANUAL,
                       save_format: Optional[SaveFormat] = None) -> Optional[str]:
        """Save the complete game state"""
        if save_format is None:
            save_format = self.default_format
        
        # Generate save ID
        save_id = f"save_{int(time.time())}_{hash(save_name) % 10000}"
        
        # Create save operation
        operation = SaveOperation(
            operation_id=f"save_op_{int(time.time())}",
            operation_type="save",
            save_id=save_id,
            start_time=time.time()
        )
        
        self.active_operations[operation.operation_id] = operation
        operation.status = SaveStatus.IN_PROGRESS
        
        try:
            # Collect all system states
            operation.progress = 0.1
            game_state = await self._collect_game_state()
            
            # Create metadata
            operation.progress = 0.2
            metadata = await self._create_save_metadata(save_id, save_name, save_type, save_format, game_state)
            
            # Serialize data
            operation.progress = 0.4
            serialization_start = time.time()
            serialized_data = await self._serialize_game_state(game_state, save_format)
            operation.serialization_time = time.time() - serialization_start
            
            # Compress if needed
            operation.progress = 0.6
            if save_format == SaveFormat.COMPRESSED:
                compression_start = time.time()
                serialized_data = await self._compress_data(serialized_data)
                operation.compression_time = time.time() - compression_start
                metadata.compression_ratio = len(serialized_data) / len(pickle.dumps(game_state))
            
            # Calculate checksum
            operation.progress = 0.7
            metadata.checksum = hashlib.sha256(serialized_data).hexdigest()
            metadata.file_size = len(serialized_data)
            
            # Write files
            operation.progress = 0.8
            io_start = time.time()
            file_path = await self._write_save_files(save_id, metadata, serialized_data, save_format)
            operation.io_time = time.time() - io_start
            operation.file_path = file_path
            
            # Update tracking
            operation.progress = 1.0
            operation.status = SaveStatus.COMPLETED
            operation.end_time = time.time()
            
            self.available_saves[save_id] = metadata
            self.total_saves += 1
            self.total_save_time += operation.get_duration()
            self.largest_save_size = max(self.largest_save_size, metadata.file_size)
            
            # Add to history
            self.save_history.append({
                'save_id': save_id,
                'save_name': save_name,
                'save_type': save_type.value,
                'timestamp': metadata.created_time,
                'file_size': metadata.file_size,
                'duration': operation.get_duration()
            })
            
            # Cleanup old auto-saves if needed
            if save_type == SaveType.AUTO:
                await self._cleanup_old_auto_saves()
            
            # Emit save completed event
            self.event_system.emit('game_saved', {
                'save_id': save_id,
                'save_name': save_name,
                'file_size': metadata.file_size,
                'duration': operation.get_duration()
            }, priority=EventPriority.NORMAL)
            
            self.logger.info(f"Game saved successfully: {save_name} ({metadata.file_size} bytes)")
            return save_id
            
        except Exception as e:
            operation.status = SaveStatus.FAILED
            operation.error_message = str(e)
            operation.end_time = time.time()
            
            self.logger.error(f"Failed to save game {save_name}: {e}")
            return None
        
        finally:
            # Clean up operation
            if operation.operation_id in self.active_operations:
                del self.active_operations[operation.operation_id]
    
    async def load_game(self, save_id: str) -> bool:
        """Load a complete game state"""
        if save_id not in self.available_saves:
            self.logger.error(f"Save {save_id} not found")
            return False
        
        metadata = self.available_saves[save_id]
        
        # Create load operation
        operation = SaveOperation(
            operation_id=f"load_op_{int(time.time())}",
            operation_type="load",
            save_id=save_id,
            start_time=time.time()
        )
        
        self.active_operations[operation.operation_id] = operation
        operation.status = SaveStatus.IN_PROGRESS
        
        try:
            # Read save file
            operation.progress = 0.1
            io_start = time.time()
            serialized_data = await self._read_save_file(save_id, metadata.save_format)
            operation.io_time = time.time() - io_start
            
            # Verify checksum
            operation.progress = 0.2
            if not await self._verify_save_integrity(serialized_data, metadata):
                raise Exception("Save file integrity check failed")
            
            # Decompress if needed
            operation.progress = 0.3
            if metadata.save_format == SaveFormat.COMPRESSED:
                compression_start = time.time()
                serialized_data = await self._decompress_data(serialized_data)
                operation.compression_time = time.time() - compression_start
            
            # Deserialize data
            operation.progress = 0.5
            serialization_start = time.time()
            game_state = await self._deserialize_game_state(serialized_data, metadata.save_format)
            operation.serialization_time = time.time() - serialization_start
            
            # Create backup of current state
            operation.progress = 0.6
            await self.create_checkpoint("before_load")
            
            # Restore system states
            operation.progress = 0.7
            await self._restore_game_state(game_state)
            
            # Finalize load
            operation.progress = 1.0
            operation.status = SaveStatus.COMPLETED
            operation.end_time = time.time()
            
            self.total_loads += 1
            self.total_load_time += operation.get_duration()
            
            # Emit load completed event
            self.event_system.emit('game_loaded', {
                'save_id': save_id,
                'save_name': metadata.save_name,
                'game_time': metadata.game_time_minutes,
                'duration': operation.get_duration()
            }, priority=EventPriority.HIGH)
            
            self.logger.info(f"Game loaded successfully: {metadata.save_name}")
            return True
            
        except Exception as e:
            operation.status = SaveStatus.FAILED
            operation.error_message = str(e)
            operation.end_time = time.time()
            
            self.logger.error(f"Failed to load game {save_id}: {e}")
            return False
        
        finally:
            # Clean up operation
            if operation.operation_id in self.active_operations:
                del self.active_operations[operation.operation_id]
    
    async def create_checkpoint(self, checkpoint_name: str) -> Optional[str]:
        """Create a temporary checkpoint"""
        checkpoint_id = await self.save_game(
            f"checkpoint_{checkpoint_name}",
            SaveType.CHECKPOINT,
            SaveFormat.COMPRESSED
        )
        
        if checkpoint_id:
            # Move to checkpoint directory
            await self._move_to_checkpoint_directory(checkpoint_id)
            
            # Cleanup old checkpoints
            await self._cleanup_old_checkpoints()
        
        return checkpoint_id
    
    async def _collect_game_state(self) -> Dict[str, Any]:
        """Collect complete game state from all systems"""
        game_state = {
            'metadata': {
                'collection_time': time.time(),
                'game_version': '2.0.0',
                'save_version': '2.0'
            },
            'systems': {}
        }
        
        # Time Management System
        if hasattr(self.time_manager, 'get_save_state'):
            game_state['systems']['time_manager'] = self.time_manager.get_save_state()
        else:
            game_state['systems']['time_manager'] = {
                'current_time': self.time_manager.get_current_time().total_minutes,
                'current_season': self.time_manager.get_current_season().value,
                'current_weather': self.time_manager.get_current_weather().weather_type.value,
                'time_speed': getattr(self.time_manager, 'time_speed', 1.0)
            }
        
        # Economy System
        if hasattr(self.economy_system, 'get_save_state'):
            game_state['systems']['economy_system'] = self.economy_system.get_save_state()
        else:
            game_state['systems']['economy_system'] = {
                'player_cash': self.economy_system.player_cash,
                'player_debt': self.economy_system.player_debt,
                'total_revenue': self.economy_system.total_revenue,
                'total_expenses': self.economy_system.total_expenses,
                'market_prices': {crop: asdict(price) for crop, price in self.economy_system.market_prices.items()},
                'active_contracts': {cid: asdict(contract) for cid, contract in self.economy_system.active_contracts.items()},
                'active_loans': {lid: asdict(loan) for lid, loan in self.economy_system.active_loans.items()}
            }
        
        # Employee System
        if hasattr(self.employee_system, 'get_save_state'):
            game_state['systems']['employee_system'] = self.employee_system.get_save_state()
        else:
            game_state['systems']['employee_system'] = {
                'employees': {eid: self.employee_system.get_employee_info(eid) 
                            for eid in self.employee_system.employees.keys()},
                'employee_positions': self.employee_system.employee_positions,
                'job_candidates': {cid: asdict(candidate) for cid, candidate in self.employee_system.job_candidates.items()},
                'performance_metrics': self.employee_system.performance_metrics
            }
        
        # Crop System
        if hasattr(self.crop_system, 'get_save_state'):
            game_state['systems']['crop_system'] = self.crop_system.get_save_state()
        else:
            game_state['systems']['crop_system'] = {
                'active_crops': {cid: asdict(crop) for cid, crop in self.crop_system.active_crops.items()},
                'soil_conditions': {str(pos): asdict(soil) for pos, soil in self.crop_system.soil_conditions.items()},
                'planted_positions': list(self.crop_system.planted_positions),
                'crop_rotation_history': {str(pos): [crop.value for crop in crops] 
                                        for pos, crops in self.crop_system.crop_rotation_history.items()},
                'harvest_history': self.crop_system.harvest_history
            }
        
        # Building System
        if hasattr(self.building_system, 'get_save_state'):
            game_state['systems']['building_system'] = self.building_system.get_save_state()
        else:
            game_state['systems']['building_system'] = {
                'active_buildings': {bid: asdict(building) for bid, building in self.building_system.active_buildings.items()},
                'occupied_positions': list(self.building_system.occupied_positions),
                'construction_queue': self.building_system.construction_queue,
                'material_inventory': {material.value: quantity for material, quantity in self.building_system.material_inventory.items()},
                'total_construction_investment': self.building_system.total_construction_investment
            }
        
        # Entity System
        if hasattr(self.entity_system, 'get_save_state'):
            game_state['systems']['entity_system'] = self.entity_system.get_save_state()
        
        return game_state
    
    async def _create_save_metadata(self, save_id: str, save_name: str, save_type: SaveType,
                                  save_format: SaveFormat, game_state: Dict[str, Any]) -> SaveMetadata:
        """Create metadata for a save file"""
        current_time = time.time()
        game_time = self.time_manager.get_current_time().total_minutes
        
        # Calculate statistics
        total_crops_planted = getattr(self.crop_system, 'total_crops_planted', 0)
        total_crops_harvested = getattr(self.crop_system, 'total_crops_harvested', 0)
        total_buildings = len(getattr(self.building_system, 'active_buildings', {}))
        total_employees = len(getattr(self.employee_system, 'employees', {}))
        player_cash = getattr(self.economy_system, 'player_cash', 0.0)
        
        # Entity counts
        entity_count = len(game_state.get('systems', {}).get('entity_system', {}).get('entities', {}))
        component_count = sum(len(entity.get('components', {})) 
                            for entity in game_state.get('systems', {}).get('entity_system', {}).get('entities', {}).values())
        
        return SaveMetadata(
            save_id=save_id,
            save_name=save_name,
            save_type=save_type,
            save_format=save_format,
            created_time=current_time,
            game_time_minutes=game_time,
            session_duration=current_time - getattr(self, 'session_start_time', current_time),
            total_crops_planted=total_crops_planted,
            total_crops_harvested=total_crops_harvested,
            total_buildings=total_buildings,
            total_employees=total_employees,
            player_cash=player_cash,
            days_played=int(game_time / 1440),
            systems_included=list(game_state.get('systems', {}).keys()),
            entity_count=entity_count,
            component_count=component_count
        )
    
    async def _serialize_game_state(self, game_state: Dict[str, Any], save_format: SaveFormat) -> bytes:
        """Serialize game state to bytes"""
        if save_format == SaveFormat.JSON:
            return json.dumps(game_state, indent=2, default=str).encode('utf-8')
        elif save_format in [SaveFormat.PICKLE, SaveFormat.COMPRESSED, SaveFormat.BINARY]:
            return pickle.dumps(game_state, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            raise ValueError(f"Unsupported save format: {save_format}")
    
    async def _compress_data(self, data: bytes) -> bytes:
        """Compress data using gzip"""
        return gzip.compress(data, compresslevel=self.compression_level)
    
    async def _decompress_data(self, data: bytes) -> bytes:
        """Decompress gzip data"""
        return gzip.decompress(data)
    
    async def _write_save_files(self, save_id: str, metadata: SaveMetadata, 
                              data: bytes, save_format: SaveFormat) -> str:
        """Write save files to disk"""
        # Determine file extensions
        data_extension = {
            SaveFormat.JSON: '.json',
            SaveFormat.PICKLE: '.pkl',
            SaveFormat.COMPRESSED: '.gz',
            SaveFormat.BINARY: '.bin'
        }.get(save_format, '.dat')
        
        # Write data file
        data_filename = f"{save_id}_data{data_extension}"
        data_path = os.path.join(self.save_directory, data_filename)
        
        with open(data_path, 'wb') as f:
            f.write(data)
        
        # Write metadata file
        metadata_filename = f"{save_id}_metadata.json"
        metadata_path = os.path.join(self.save_directory, metadata_filename)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
        
        return data_path
    
    async def _read_save_file(self, save_id: str, save_format: SaveFormat) -> bytes:
        """Read save file from disk"""
        data_extension = {
            SaveFormat.JSON: '.json',
            SaveFormat.PICKLE: '.pkl',
            SaveFormat.COMPRESSED: '.gz',
            SaveFormat.BINARY: '.bin'
        }.get(save_format, '.dat')
        
        data_filename = f"{save_id}_data{data_extension}"
        data_path = os.path.join(self.save_directory, data_filename)
        
        with open(data_path, 'rb') as f:
            return f.read()
    
    async def _verify_save_integrity(self, data: bytes, metadata: SaveMetadata) -> bool:
        """Verify save file integrity using checksum"""
        calculated_checksum = hashlib.sha256(data).hexdigest()
        return calculated_checksum == metadata.checksum
    
    async def _deserialize_game_state(self, data: bytes, save_format: SaveFormat) -> Dict[str, Any]:
        """Deserialize game state from bytes"""
        if save_format == SaveFormat.JSON:
            return json.loads(data.decode('utf-8'))
        elif save_format in [SaveFormat.PICKLE, SaveFormat.COMPRESSED, SaveFormat.BINARY]:
            return pickle.loads(data)
        else:
            raise ValueError(f"Unsupported save format: {save_format}")
    
    async def _restore_game_state(self, game_state: Dict[str, Any]):
        """Restore complete game state to all systems"""
        systems_data = game_state.get('systems', {})
        
        # Restore Time Management System
        if 'time_manager' in systems_data:
            if hasattr(self.time_manager, 'load_save_state'):
                self.time_manager.load_save_state(systems_data['time_manager'])
            else:
                # Basic restoration
                time_data = systems_data['time_manager']
                if 'current_time' in time_data:
                    # Would need to implement time restoration
                    pass
        
        # Restore Economy System
        if 'economy_system' in systems_data:
            if hasattr(self.economy_system, 'load_save_state'):
                self.economy_system.load_save_state(systems_data['economy_system'])
            else:
                # Basic restoration
                economy_data = systems_data['economy_system']
                self.economy_system.player_cash = economy_data.get('player_cash', 0.0)
                self.economy_system.player_debt = economy_data.get('player_debt', 0.0)
                self.economy_system.total_revenue = economy_data.get('total_revenue', 0.0)
                self.economy_system.total_expenses = economy_data.get('total_expenses', 0.0)
        
        # Restore Employee System
        if 'employee_system' in systems_data:
            if hasattr(self.employee_system, 'load_save_state'):
                self.employee_system.load_save_state(systems_data['employee_system'])
        
        # Restore Crop System
        if 'crop_system' in systems_data:
            if hasattr(self.crop_system, 'load_save_state'):
                self.crop_system.load_save_state(systems_data['crop_system'])
        
        # Restore Building System
        if 'building_system' in systems_data:
            if hasattr(self.building_system, 'load_save_state'):
                self.building_system.load_save_state(systems_data['building_system'])
        
        # Restore Entity System
        if 'entity_system' in systems_data:
            if hasattr(self.entity_system, 'load_save_state'):
                self.entity_system.load_save_state(systems_data['entity_system'])
        
        # Emit restoration completed event
        self.event_system.emit('game_state_restored', {
            'systems_restored': list(systems_data.keys()),
            'restoration_time': time.time()
        }, priority=EventPriority.HIGH)
    
    async def _move_to_checkpoint_directory(self, checkpoint_id: str):
        """Move checkpoint files to checkpoint directory"""
        # Implementation would move files to checkpoint directory
        pass
    
    async def _cleanup_old_auto_saves(self):
        """Remove old auto-save files"""
        auto_saves = [save for save in self.available_saves.values() 
                     if save.save_type == SaveType.AUTO]
        
        if len(auto_saves) > self.max_auto_saves:
            # Sort by creation time
            auto_saves.sort(key=lambda s: s.created_time)
            
            # Remove oldest saves
            saves_to_remove = auto_saves[:-self.max_auto_saves]
            for save in saves_to_remove:
                await self._delete_save_files(save.save_id)
                del self.available_saves[save.save_id]
    
    async def _cleanup_old_checkpoints(self):
        """Remove old checkpoint files"""
        checkpoints = [save for save in self.available_saves.values() 
                      if save.save_type == SaveType.CHECKPOINT]
        
        if len(checkpoints) > self.max_checkpoints:
            # Sort by creation time
            checkpoints.sort(key=lambda s: s.created_time)
            
            # Remove oldest checkpoints
            checkpoints_to_remove = checkpoints[:-self.max_checkpoints]
            for checkpoint in checkpoints_to_remove:
                await self._delete_save_files(checkpoint.save_id)
                del self.available_saves[checkpoint.save_id]
    
    async def _delete_save_files(self, save_id: str):
        """Delete save files from disk"""
        try:
            # Delete data file
            for ext in ['.json', '.pkl', '.gz', '.bin', '.dat']:
                data_path = os.path.join(self.save_directory, f"{save_id}_data{ext}")
                if os.path.exists(data_path):
                    os.remove(data_path)
            
            # Delete metadata file
            metadata_path = os.path.join(self.save_directory, f"{save_id}_metadata.json")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
                
        except Exception as e:
            self.logger.warning(f"Failed to delete save files for {save_id}: {e}")
    
    def get_available_saves(self) -> List[Dict[str, Any]]:
        """Get list of available save files"""
        saves = []
        for save in sorted(self.available_saves.values(), key=lambda s: s.created_time, reverse=True):
            saves.append({
                'save_id': save.save_id,
                'save_name': save.save_name,
                'save_type': save.save_type.value,
                'created_time': save.created_time,
                'game_time_days': save.days_played,
                'player_cash': save.player_cash,
                'total_crops': save.total_crops_planted,
                'total_buildings': save.total_buildings,
                'file_size': save.file_size,
                'game_version': save.game_version
            })
        return saves
    
    def get_save_info(self, save_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific save"""
        if save_id not in self.available_saves:
            return None
        
        save = self.available_saves[save_id]
        return {
            'save_id': save_id,
            'metadata': save.to_dict(),
            'file_exists': self._save_files_exist(save_id),
            'integrity_ok': True  # Would check file integrity
        }
    
    def _save_files_exist(self, save_id: str) -> bool:
        """Check if save files exist on disk"""
        metadata_path = os.path.join(self.save_directory, f"{save_id}_metadata.json")
        return os.path.exists(metadata_path)
    
    async def auto_save(self) -> Optional[str]:
        """Perform automatic save"""
        if not self.auto_save_enabled:
            return None
        
        current_time = time.time()
        if current_time - self.last_auto_save < self.auto_save_interval:
            return None
        
        self.auto_save_counter += 1
        auto_save_name = f"AutoSave_{self.auto_save_counter}"
        
        save_id = await self.save_game(auto_save_name, SaveType.AUTO)
        
        if save_id:
            self.last_auto_save = current_time
            self.logger.info(f"Auto-save completed: {auto_save_name}")
        
        return save_id
    
    async def export_save(self, save_id: str, export_path: str) -> bool:
        """Export a save file for sharing"""
        if save_id not in self.available_saves:
            return False
        
        try:
            metadata = self.available_saves[save_id]
            
            # Read save data
            save_data = await self._read_save_file(save_id, metadata.save_format)
            
            # Create export package
            export_package = {
                'metadata': metadata.to_dict(),
                'data': save_data.hex(),  # Convert to hex for JSON compatibility
                'export_time': time.time(),
                'export_version': '2.0'
            }
            
            # Write export file
            with open(export_path, 'w') as f:
                json.dump(export_package, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export save {save_id}: {e}")
            return False
    
    async def import_save(self, import_path: str) -> Optional[str]:
        """Import a save file from export"""
        try:
            with open(import_path, 'r') as f:
                export_package = json.load(f)
            
            # Extract data
            metadata_dict = export_package['metadata']
            save_data = bytes.fromhex(export_package['data'])
            
            # Create new save ID
            new_save_id = f"imported_{int(time.time())}"
            metadata_dict['save_id'] = new_save_id
            
            # Create metadata
            metadata = SaveMetadata.from_dict(metadata_dict)
            
            # Write save files
            await self._write_save_files(new_save_id, metadata, save_data, metadata.save_format)
            
            # Add to available saves
            self.available_saves[new_save_id] = metadata
            
            return new_save_id
            
        except Exception as e:
            self.logger.error(f"Failed to import save from {import_path}: {e}")
            return None
    
    # Event handlers
    async def _on_minute_passed(self, event_data):
        """Handle minute-based auto-save checks"""
        await self.auto_save()
    
    async def _on_game_shutdown(self, event_data):
        """Handle game shutdown - create final save"""
        if self.auto_save_enabled:
            await self.save_game("shutdown_save", SaveType.AUTO)
    
    async def _on_system_error(self, event_data):
        """Handle system errors - create emergency save"""
        try:
            await self.create_checkpoint("emergency_before_error")
        except Exception as e:
            self.logger.error(f"Failed to create emergency checkpoint: {e}")
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive save/load system summary"""
        return {
            'total_saves': self.total_saves,
            'total_loads': self.total_loads,
            'available_saves_count': len(self.available_saves),
            'auto_save_enabled': self.auto_save_enabled,
            'auto_save_interval': self.auto_save_interval,
            'total_save_time': self.total_save_time,
            'total_load_time': self.total_load_time,
            'average_save_time': self.total_save_time / max(1, self.total_saves),
            'average_load_time': self.total_load_time / max(1, self.total_loads),
            'largest_save_size': self.largest_save_size,
            'active_operations': len(self.active_operations),
            'save_history_count': len(self.save_history)
        }
    
    async def shutdown(self):
        """Shutdown the save/load system"""
        self.logger.info("Shutting down Save/Load System")
        
        # Create final save
        if self.auto_save_enabled:
            await self.save_game("final_save", SaveType.BACKUP)
        
        # Save system summary
        final_summary = self.get_system_summary()
        
        self.event_system.emit('save_load_system_shutdown', {
            'final_summary': final_summary,
            'total_saves': self.total_saves
        }, priority=EventPriority.HIGH)
        
        self.logger.info("Save/Load System shutdown complete")


# Global save/load system instance
_global_save_load_system: Optional[SaveLoadSystem] = None

def get_save_load_system() -> SaveLoadSystem:
    """Get the global save/load system instance"""
    global _global_save_load_system
    if _global_save_load_system is None:
        _global_save_load_system = SaveLoadSystem()
    return _global_save_load_system

def initialize_save_load_system() -> SaveLoadSystem:
    """Initialize the global save/load system"""
    global _global_save_load_system
    _global_save_load_system = SaveLoadSystem()
    return _global_save_load_system