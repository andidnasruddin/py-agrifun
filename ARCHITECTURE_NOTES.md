# Architecture Notes - Farming Simulation Game

**Purpose**: Document key architectural decisions and patterns for context continuity across development sessions.

## 🏗️ Core Architectural Patterns

### 1. Event-Driven Architecture

**Decision**: Use centralized event system for all inter-system communication  
**Rationale**: Enables loose coupling, easy testing, and future expansion  
**Implementation**: `scripts/core/event_system.py`

```python
# Pattern Example
self.event_system.emit('day_passed', {'new_day': day, 'old_day': old_day})
self.event_system.subscribe('day_passed', self._handle_day_passed)
```

**Key Benefits**:
- Systems can communicate without direct dependencies
- Easy to add new systems without modifying existing ones
- Event history provides debugging insight
- Supports future save/load system (events can be serialized)

**Critical Events**:
- `time_updated` - UI updates, employee needs decay
- `day_passed` - Economy processing, crop growth, payroll
- `task_assigned` - Employee receives work, tiles get task markers
- `money_changed` - UI updates, transaction logging

### 2. Component-Based Game Objects

**Decision**: Use composition over inheritance for game entities  
**Implementation**: Tile class with distinct responsibilities, Employee with modular systems

```python
class Tile:
    # Separate concerns: terrain, crops, tasks, visual state
    def __init__(self):
        self.terrain_type = 'soil'      # Terrain management
        self.current_crop = None        # Crop system
        self.task_assignment = None     # Task system
        self.highlight = False          # Visual system
```

**Benefits**:
- Easy to add new tile features without breaking existing code
- Clear separation of concerns
- Supports data-driven configuration
- Enables future save system with clean serialization

### 3. State Machine Pattern for Employee AI

**Decision**: Explicit state machine for employee behavior  
**Rationale**: Predictable AI behavior, easy debugging, extensible

```python
class EmployeeState(Enum):
    IDLE = "idle"
    MOVING = "moving" 
    WORKING = "working"
    RESTING = "resting"
    SEEKING_AMENITY = "seeking_amenity"
```

**State Transitions**:
- IDLE → MOVING (task assigned)
- MOVING → WORKING (arrived at target)
- WORKING → IDLE (task completed)
- ANY → RESTING (critical needs)
- ANY → SEEKING_AMENITY (amenity required)

**Benefits**:
- Clear, debuggable AI behavior
- Easy to add new states for Phase 2 features
- Visual state indicators for player feedback
- Supports complex behaviors without code complexity

### 4. Manager Pattern for System Organization

**Decision**: Each major system has a dedicated manager class  
**Systems**: GridManager, EmployeeManager, EconomyManager, TimeManager, UIManager

**Manager Responsibilities**:
- **GridManager**: Tile state, selection, task assignment
- **EmployeeManager**: Employee collection, hiring, task coordination
- **EconomyManager**: Financial transactions, loans, market prices
- **TimeManager**: Game time progression, speed controls
- **UIManager**: Interface elements, user input handling

**Benefits**:
- Clear ownership of functionality
- Easy to test individual systems
- Supports parallel development of different features
- Clean initialization and update order

## 🎯 Key Design Decisions

### Time System Design

**Decision**: Real-time with speed multipliers rather than turn-based  
**Parameters**: 20-minute real workday = 13 hours game time (5AM-6PM)

```python
# Time calculation approach
effective_dt = real_dt * speed_multiplier
game_minutes = elapsed_time / real_time_per_game_minute
```

**Rationale**:
- More engaging than turn-based for farming simulation
- Speed controls provide player agency over pacing
- Supports future pause-and-plan mechanics
- Realistic time pressure for decision making

**Trade-offs**:
- More complex than turn-based implementation
- Requires careful balance of time scales
- Performance considerations for real-time updates

### Economic System Design

**Decision**: Simplified interest model with daily payments  
**Implementation**: Fixed daily payment rather than compound interest

```python
# Loan payment calculation
total_interest = principal * rate * (days / 365.0)
daily_payment = (principal + total_interest) / term_days
```

**Rationale**:
- Easy for players to understand and plan around
- Predictable cash flow requirements
- Avoids complex financial calculations
- Supports clear failure conditions

**Alternative Considered**: Real compound interest rejected due to complexity

### Employee Needs System

**Decision**: Three-need system (Hunger/Thirst/Rest) with different decay rates  
**Balance**: Thirst decays fastest, encourages water cooler placement

```python
HUNGER_DECAY_RATE = 1.0   # points per hour
THIRST_DECAY_RATE = 2.0   # points per hour  
REST_DECAY_RATE = 1.5     # points per hour when working
```

**Rationale**:
- Simple enough for players to manage
- Different decay rates create prioritization decisions
- Supports workstation placement strategy
- Visual feedback through progress bars

### Grid Coordinate System

**Decision**: (0,0) at top-left, y increases downward  
**Pixel Conversion**: `pixel_x = grid_x * TILE_SIZE, pixel_y = grid_y * TILE_SIZE + UI_OFFSET`

**Rationale**:
- Matches pygame screen coordinates
- Consistent with 2D array indexing
- Easy mouse-to-grid coordinate conversion
- UI offset separates game area from interface

## 🔧 Implementation Patterns

### Event System Usage Pattern

```python
# Standard event emission
self.event_system.emit('event_name', {
    'param1': value1,
    'param2': value2,
    'timestamp': current_time
})

# Standard event subscription
self.event_system.subscribe('event_name', self._handler_method)

def _handler_method(self, event_data):
    param1 = event_data.get('param1')
    # Process event
```

### Manager Update Order

**Critical**: Systems must update in dependency order to avoid frame-delay issues

```python
def _update(self, dt):
    self.time_manager.update(dt)      # First: time drives everything
    self.grid_manager.update(dt)      # Second: world state
    self.employee_manager.update(dt)  # Third: entities that act on world
    self.economy_manager.update(dt)   # Fourth: consequences of actions
    self.ui_manager.update(dt)        # Last: display current state
    self.event_system.process_events() # Process all events generated
```

### Configuration Pattern

**Decision**: All magic numbers in central config file  
**Access Pattern**: `from scripts.core.config import *`

**Benefits**:
- Easy gameplay balance tuning
- Prevents scattered magic numbers
- Supports data-driven development
- Future configuration UI support

## 🚀 Extensibility Decisions

### Future Employee System

**Prepared Architecture**: Employee traits as list, work_efficiency as modifier
- Supports multiple traits per employee
- Trait effects applied in `_apply_trait_effects()`
- Easy to add new traits without code changes

### Future Crop System

**Prepared Architecture**: Generic growth stage system
- `CORN_GROWTH_STAGES` list easily replaceable
- Tile stores crop type as string
- Growth calculation uses configurable parameters

### Future Save System

**Prepared Architecture**: Event-driven, serializable state
- All game state accessible through managers
- Events can be logged for replay
- Clean separation between game logic and persistence

### Future UI Expansion

**Prepared Architecture**: pygame-gui integration with custom overlay
- Professional UI components for complex interfaces
- Custom rendering for game-specific elements
- Event-driven UI updates

## ⚠️ Architectural Risks & Mitigation

### Risk: Event System Performance
**Concern**: Too many events per frame  
**Mitigation**: Event batching, selective subscription, performance monitoring

### Risk: Manager Coupling
**Concern**: Managers becoming interdependent  
**Mitigation**: All communication through events, clear interface definitions

### Risk: State Synchronization
**Concern**: Game state becoming inconsistent across systems  
**Mitigation**: Single source of truth for each state, event ordering

### Risk: Save/Load Complexity
**Concern**: Complex state serialization  
**Mitigation**: JSON-serializable data structures, version migration support

## 📋 Architecture Evolution Guidelines

### Adding New Systems
1. Create manager class with event subscription
2. Register with GameManager in proper update order
3. Document events emitted/consumed
4. Add configuration parameters to config.py
5. Update ARCHITECTURE_NOTES.md

### Modifying Existing Systems
1. Consider event system impact
2. Update manager interfaces through events only
3. Maintain backward compatibility where possible
4. Update configuration parameters
5. Test manager update order

### Performance Considerations
1. Minimize per-frame calculations
2. Use event system for infrequent updates
3. Cache expensive calculations
4. Profile before optimizing

This architecture successfully balances simplicity for MVP development with extensibility for future phases. The event-driven approach has proven effective for system decoupling while maintaining clear data flow.