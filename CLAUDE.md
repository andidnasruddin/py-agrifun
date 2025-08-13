# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a 2D top-down grid-based farming simulation game built in **Python with Pygame**. The game is a solo development project focused on educational agricultural management with the theme "how fun and crazy agriculture really is." The player inherits farmland with $0 and must build an agricultural business from scratch.

## Development Status

**Current Phase:** Finalizing Game - Phase 1: UI Overhaul (Major Milestone)
**Target Platform:** Python with Pygame library
**Architecture:** Event-driven modular system with manager pattern
**Grid Size:** 16x16 tiles (fully optimized)

**Last Updated:** 2025-08-12
**Next Priority:** Complete professional UI transformation with enhanced information density and user experience

### ✅ **MAJOR SYSTEMS COMPLETED:**

**Core Foundation (100% Complete):**
- Event-driven architecture with comprehensive pub/sub communication
- Complete 16x16 grid system with tile management and drag selection
- Professional pygame-gui UI with resource panels and real-time displays
- Time management with 20-minute days, speed controls, and work hours
- Economy system with loans, subsidies, dynamic market pricing

**Advanced Employee System (100% Complete):**
- **Multi-employee support** (not limited to Sam - full hiring system implemented)
- A* pathfinding algorithm with visual debugging and path caching
- Complete needs system (hunger/thirst/rest) with visual status bars
- Trait system with stat modifications ("hard_worker" trait implemented)
- State machine AI (Idle→Moving→Working→Resting) with smooth transitions

**Inventory & Buildings (100% Complete):**
- Strategic crop storage system (100-unit capacity with quality tracking)
- Manual selling with FIFO inventory management
- Storage silo buildings (+50 capacity each, max 5 silos, progressive pricing)
- Complete building purchase system integrated with economy

**Advanced Features (95% Complete):**
- Real-time pathfinding visualization with green path lines
- Employee status displays with needs bars above workers
- Transaction history logging with financial categorization
- Market price history (30-day tracking) for strategic decisions
- 5-stage crop growth visualization (seed→sprout→young→mature→harvestable)

**🌾 Agricultural Science Systems (100% Complete):**
- Complete crop rotation and soil health implementation with educational principles
- Soil nutrient tracking (N-P-K levels) with realistic crop depletion effects
- Strategic rotation bonuses teaching proper agricultural practices (+15-20% yields)
- Interactive soil information panel with click-to-view functionality
- Crop history tracking and soil rest mechanics for long-term planning

**🌊 Irrigation & Water Management System (100% Complete):**
- **Strategic Irrigation Infrastructure** with $150/tile installation and drought mitigation
- **Economic Integration** with $5/day operational costs during drought events only
- **Player Controls** for irrigation toggle and cost management during weather events
- **Weather Integration** providing +30% growth boost during drought on irrigated tiles
- **Educational Value** teaching real agricultural irrigation principles and water conservation
- **Visual Feedback** with water-blue irrigation buildings and tile coverage indicators

### 🎮 **CURRENT GAME STATE - HIGHLY SOPHISTICATED:**
- **Fully playable multi-employee farming simulation**
- Complete economic simulation with realistic loan/subsidy mechanics  
- Strategic building system with meaningful cost/benefit decisions
- Professional-grade UI with comprehensive feedback systems
- Real-time gameplay with pause, 1x, 2x, 4x speed controls
- End-to-end workflows: Till→Plant→Harvest→Store→Sell with market timing

## Planned Code Architecture

Based on the design documentation, the codebase will follow this structure:

```
/scripts/
  /core/
    - main.py (main game loop)
    - grid_manager.py (tile management)
    - time_manager.py (day/night cycle)
  /employee/
    - employee.py (Employee class and AI)
    - employee_manager.py (hiring/management)
  /economy/
    - economy_manager.py (transactions/loans)
    - market_system.py (pricing/contracts)
  /crops/
    - crop_manager.py (growth/harvesting)
    - crop_data.py (crop definitions)
  /ui/
    - ui_manager.py (primary interface)
    - task_assignment.py (drag-drop system)
```

## Key Game Systems

### Grid System
- Each tile implemented as Python class or dictionary with terrain quality (1-10), crop data, growth stage, water level, and task assignments
- 16x16 tile MVP expanding to larger grids in future phases
- Rendered using Pygame's 2D drawing capabilities

### Employee AI
- Pathfinding-based movement (A* algorithm planned)
- State machine: Idle → Move → Work → Rest
- Needs system: Hunger, Thirst, Rest (0-100 scales)
- Procedural traits affecting efficiency and behavior

### Time Management
- Real-time with pause/speed controls (1x, 2x, 4x)
- 20-minute workday simulation
- Dynamic market price calculation at end of each day

### Economy
- Starting conditions: $0 cash, $10,000 mandatory loan, $100/day subsidy (30 days)
- Daily expenses: Employee wages, loan payments, utilities
- Dynamic crop pricing ($2-$8 per corn unit)

### Agricultural Systems 🌾 NEW!
- **Crop Rotation & Soil Health**: Educational agricultural science implementation
  - **Soil Nutrients**: Nitrogen, Phosphorus, Potassium tracking (0-100 levels)
  - **Crop Categories**: Heavy feeders (corn), balanced feeders (tomatoes), light feeders (wheat)
  - **Rotation Bonuses**: Strategic yield bonuses for proper crop sequencing
  - **Soil Rest**: Fallow periods provide recovery bonuses (+20% yield)
- **Soil Information Panel**: Click tilled plots to view comprehensive soil data
  - **Real-time Display**: Soil health, nutrient bars, crop history, rotation recommendations
  - **Strategic Planning**: Shows bonus calculations for each potential crop type
  - **UI Integration**: Left-side panel with solid background, event-driven show/hide

## Development Guidelines

### Core Design Principles
- **Modularity:** Each system independent and testable
- **Scalability:** Support future multi-employee/multi-farm expansion  
- **Realism Balance:** Educational value while maintaining fun gameplay
- **Player Agency:** All major decisions controlled by player

### Code Comment Requirements
**IMPORTANT: Line-by-Line Code Explanations Required**

When writing or modifying code, Claude MUST add detailed explanations for every line to help the developer understand what each line does. This is specifically requested by the developer for learning purposes.

**Example Format:**
```python
# Initialize the employee position to center of grid
self.x = 8.0  # Set X coordinate to grid center (8 out of 16)
self.y = 8.0  # Set Y coordinate to grid center (8 out of 16)

# Create task assignment list to store work orders
self.assigned_tasks = []  # Empty list to hold task dictionaries

# Set employee speed from config file
self.speed = EMPLOYEE_SPEED  # Get movement speed from config.py (tiles per second)
```

This applies to:
- ✅ New function implementations
- ✅ Code modifications and updates
- ✅ Bug fixes and improvements
- ✅ System integrations and refactoring

Exception: Simple variable assignments in config files or obvious operations may use shorter comments.

### Development Phases
1. **✅ MVP (Phase 1) - COMPLETED:** Core foundation - grid, multi-employee, crop management, economy
2. **✅ Phase 2 - COMPLETED:** Enhanced systems - hiring system, buildings, advanced AI pathfinding
3. **✅ Phase 3+ - COMPLETED:** Agricultural complexity - crop rotation, soil health, weather systems, irrigation
4. **🔄 Phase 4 (Current):** Additional features - employee traits, technology research, tutorial system

## Implementation Notes

This is a Python/Pygame project with specific technical considerations:
- Save system using Python's `pickle` or `json` modules for game state serialization
- UI implementation either custom-built or using Pygame GUI library
- Tooltip-heavy UI design inspired by RimWorld (challenging in Pygame)
- Drag-and-drop task assignment system
- Real-time simulation with pause capabilities
- Performance optimization needed for real-time grid simulation

## Development Commands

**Current Working Commands:**
- `python main.py` - Run the farming simulation game
- `pip install -r requirements.txt` - Install dependencies (pygame, pygame-gui)

**Game Controls:**
- Mouse: Click and drag to select tiles
- T: Assign Till task, P: Plant task, H: Harvest task, C: Clear selection
- F1: Toggle debug information
- UI Buttons: Pause, 1x, 2x, 4x speed controls
- Building Placement: Click building buttons to enter placement mode, click tiles to place
- Irrigation Controls: "Irrigation ($150)" to install, "Toggle Irrigation" to manage costs

**Future Commands (Planned):**
- `python -m pytest` - Run unit tests (Phase 2)
- `python tools/balance_tester.py` - Balance testing utility
- `python tools/save_converter.py` - Save file migration (Phase 3)

## Context Continuity Files

**Essential files for maintaining development context across sessions:**

### Primary Context Files:
- **DEVELOPMENT_STATE.md** - Current project status, completed features, known issues
- **ARCHITECTURE_NOTES.md** - Key design decisions and implementation patterns  
- **BUG_LOG.md** - Issue tracking and resolution status
- **DOCUMENTATION.md** - Original game design specification

### Code Context:
- **scripts/core/config.py** - All game parameters and balance settings
- **scripts/core/game_manager.py** - Main coordination and system integration
- **scripts/core/event_system.py** - Event-driven communication patterns

## Session Continuity Protocol

**Before starting development:**
1. Review DEVELOPMENT_STATE.md for current status
2. Check BUG_LOG.md for known issues
3. Run `python main.py` to verify current functionality
4. Use `--resume` flag to continue from specific conversation

**During development:**
1. Update DEVELOPMENT_STATE.md when completing major features
2. Log any bugs discovered in BUG_LOG.md
3. Update ARCHITECTURE_NOTES.md for significant design decisions
4. Use TodoWrite tool to track current session progress

**End of session:**
1. Update all context files with current state
2. Commit code with descriptive messages
3. Note next priorities in DEVELOPMENT_STATE.md

## Current Technical Status

**Architecture Health:** ✅ Strong event-driven foundation ready for expansion  
**Performance:** ✅ 60 FPS target achieved on reference hardware  
**Code Quality:** ⚠️ Needs comprehensive docstrings and unit tests  
**Extensibility:** ✅ Well-prepared for Phase 2 features  

**Resolved Technical Items:**
- ✅ A* pathfinding fully implemented with visualization
- ✅ Multi-employee system completed and functional
- ✅ Inventory system with strategic storage management
- ✅ Building system with storage upgrades

**Remaining Technical Opportunities:**
- ✅ Additional crop types (tomatoes, wheat) for variety
- ✅ Extended balance testing across economic scenarios  
- ✅ Additional employee traits and specializations
- ✅ Save/load system implementation (architecture ready)
- Automated testing infrastructure for regression prevention
- ✅ Trying save and load system
- ✅ Grid-Based Building ver. 1
- ✅ Updated buildings ver. 1
- ✅ Click-based placement buildings
- ✅ Multicrop, contracts
- ✅ Soil Nutrient System
- ✅ Added soil information panel system
- ✅ added soil information
- ✅ tried to fix HUD, but not fixed yet
- ✅ Fixed right HUD for a bit
- ✅ added weather
- ✅ going to begin the irrigation infrastructure system
- ✅ Phases 1, 2, 3+, and 4 are done!
- ✅ Updated the Roadmap with tons of completed tasks
- ✅ added a new final plan for UI overhaul
- ✅ COMPLETED - UI Overhaul Phase 1: Professional Agricultural Management Interface
- ✅ Enhanced Top HUD - comprehensive farm information bar with 6-section layout
- ✅ Dynamic Right Panel - context-sensitive information switching system
- ✅ Advanced Grid Renderer - zoom/pan with soil health overlays and progressive detail
- ✅ Smart Action System - intelligent context-aware action buttons with cost analysis
- ✅ Animation System - professional transitions, notifications, and visual polish
- ✅ System Integration - seamless event-driven communication between all components
- ✅ Performance Optimization - 60 FPS with viewport culling and efficient rendering
- ✅ Comprehensive Testing - complete validation of integrated UI systems
- 🎉 MAJOR MILESTONE: Professional interface that rivals commercial agricultural software!