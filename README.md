# Farming Simulation Game

A 2D top-down grid-based farming simulation built in Python with Pygame, focused on educational agricultural management.

## Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Game:**
   ```bash
   python main.py
   ```

## Current Features (MVP Phase 1)

### Core Systems Implemented:
- **16x16 Grid System**: Interactive tile-based farming grid
- **Employee AI**: Single employee "Sam" with needs system (hunger, thirst, rest)
- **Time Management**: 20-minute real-time workday with pause/speed controls (1x, 2x, 4x)
- **Economy System**: Starting loan of $10,000, daily expenses, government subsidy
- **Task Assignment**: Drag-and-drop or keyboard shortcuts for assigning work

### Controls:
- **Mouse**: Click and drag to select tiles
- **Keyboard Shortcuts**:
  - `T` - Assign Till task to selected tiles
  - `P` - Assign Plant task to selected tiles  
  - `H` - Assign Harvest task to selected tiles
  - `C` - Clear tile selection
  - `F1` - Toggle debug information
- **UI Buttons**: Speed controls (Pause, 1x, 2x, 4x)

### Game Flow:
1. Start with $0 cash and a mandatory $10,000 farmer loan
2. Receive $100/day government subsidy for first 30 days
3. Assign your employee Sam to till soil, plant corn, and harvest crops
4. Sell corn at fluctuating market prices ($2-$8 per unit)
5. Manage daily expenses (utilities, loan payments, employee wages)
6. Monitor employee needs and work efficiency

## Game Systems

### Employee AI:
- **Sam** starts at grid center with "Hard Worker" trait (+10% efficiency, -5% stamina drain)
- Automatically pathfinds to assigned tiles and performs work
- Needs system: Hunger/Thirst/Rest bars decrease over time
- State indicators: Gray (idle), Blue (moving), Green (working), Yellow (resting)

### Economy:
- **Starting Loan**: $10,000 at 5% annual interest, 1-year term (~$27.40/day payment)
- **Daily Expenses**: $20 utilities + loan payments + employee wages ($100/day)
- **Revenue**: Corn sales at market price
- **Subsidies**: $100/day for first 30 days

### Crop System (Corn Only):
- **Growth Stages**: Seed → Sprout → Young → Mature → Harvestable
- **Growth Time**: 3 game days (accelerated for testing)
- **Yield**: Based on soil quality and care (5-15 units per tile)

## Technical Architecture

Built with modular, event-driven architecture:

- **Core Systems**: Game manager, event system, time manager, grid manager
- **Employee System**: AI with pathfinding, needs, and task execution
- **Economy System**: Financial tracking, loans, market dynamics
- **UI System**: pygame-gui based interface with tooltips and panels

## Development Status

✅ **Completed**: Core foundation with all MVP systems functional
🚧 **In Progress**: Balance testing and bug fixes
📋 **Next Phase**: Interview system, workstations, multiple crops

## Known Issues

- Employee pathfinding uses simple direct movement (A* pathfinding planned)
- No save/load system yet (planned for Phase 3)
- Limited to corn crop only (multiple crops in Phase 4)
- UI could use more polish and better tooltips

## Development

See `CLAUDE.md` for detailed development guidance and `DOCUMENTATION.md` for comprehensive game design specifications.