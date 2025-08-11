# py-agrifun
## A Comprehensive 2D Farming Simulation Game

A sophisticated top-down grid-based farming simulation built in Python with Pygame, featuring multi-employee management, economic simulation, and educational agricultural mechanics.

## Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Game:**
   ```bash
   python main.py
   ```

## Current Features (Phase 2 - Advanced Implementation)

### ✅ **Fully Completed Systems:**
- **Multi-Employee System**: Full hiring system with interview process (not limited to Sam)
- **Advanced AI**: A* pathfinding with visual debugging and employee needs management  
- **Economic Simulation**: Loans, subsidies, dynamic market pricing with transaction history
- **Building System**: Storage silos with capacity upgrades and strategic placement
- **Professional UI**: pygame-gui interface with real-time displays and comprehensive feedback

### Controls:
- **Mouse**: Click and drag to select tiles, interact with UI elements
- **Keyboard Shortcuts**:
  - `T` - Assign Till task to selected tiles
  - `P` - Assign Plant task to selected tiles  
  - `H` - Assign Harvest task to selected tiles
  - `C` - Clear tile selection
  - `F1` - Toggle debug information (pathfinding visualization)
- **UI Elements**: Speed controls (Pause, 1x, 2x, 4x), hiring button, building purchases

### Game Flow:
1. Start with $0 cash and a mandatory $10,000 farmer loan
2. Receive $100/day government subsidy for first 30 days
3. **Hire employees** through the interview system - each with unique traits
4. Assign tasks and watch employees pathfind autonomously to work sites
5. **Build storage silos** to increase crop capacity strategically  
6. Sell corn at market timing of your choice with FIFO inventory management
7. Monitor real-time employee needs, financial status, and market trends

## Advanced Game Systems

### Multi-Employee Management:
- **Hiring System**: Interview candidates with different traits and stats
- **Employee Needs**: Visual hunger/thirst/rest bars above each worker
- **Trait System**: "Hard Worker" trait affects efficiency and stamina drain
- **AI States**: Idle → Moving → Working → Resting with smooth visual transitions

### Economic Complexity:
- **Strategic Storage**: Base 100-unit capacity + silos (+50 each, max 5, progressive pricing)  
- **Market Timing**: 30-day price history tracking for strategic selling decisions
- **Financial Categories**: Detailed transaction logging with expense categorization
- **Dynamic Pricing**: Market fluctuations affecting daily crop values

### Technical Excellence:
- **A* Pathfinding**: Optimized pathfinding with visual green path lines
- **Event-Driven Architecture**: Pub/sub system for modular communication
- **Real-Time Performance**: Maintains 60 FPS with multiple employees and systems
- **Professional UI**: Comprehensive status panels and real-time feedback

## Development Status

✅ **Phase 1 Complete**: Core foundation  
✅ **Phase 2 Complete**: Advanced multi-employee systems, buildings, economic depth  
🚧 **Current Focus**: Balance testing, additional crop types, UI polish  
📋 **Phase 3 Planned**: Save/load system, tutorial, extended content

## Technical Architecture

Sophisticated modular design:
- **Core Systems**: Game manager, event system, time/grid managers, inventory system
- **Employee Systems**: Multi-employee manager, interview system, A* pathfinding  
- **Economic Systems**: Transaction tracking, market dynamics, loan management
- **Building Systems**: Strategic placement and capacity management
- **UI Systems**: Professional pygame-gui implementation with real-time updates

## Development

See `CLAUDE.md` for detailed development guidance, `DEVELOPMENT_STATE.md` for current status, and `DOCUMENTATION.md` for comprehensive design specifications.