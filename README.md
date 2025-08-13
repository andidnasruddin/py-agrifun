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

## Current Features (Phases 1-6+ with Professional UI Overhaul - Commercial Quality)

### 🎨 **Professional UI Framework (NEW!):**
- **Advanced Tooltip System**: Rich educational tooltips with agricultural knowledge and strategic advice
- **Comprehensive Notification System**: Priority-based alerts with 8 categories (Economy, Employee, Weather, Agriculture, Building, Achievement, System, Tutorial)
- **Enhanced Animation Framework**: 14 professional easing functions, property animation, particle effects for celebrations and feedback
- **Visual Feedback**: Button press animations, harvest celebrations, construction effects, success/error particles

### ✅ **Comprehensive Agricultural Systems:**
- **Multi-Crop System**: Corn, tomatoes, wheat with strategic planting seasons and yield variations
- **Soil Science**: N-P-K nutrient tracking, crop rotation bonuses, soil health management
- **Weather & Seasons**: Dynamic 4-season cycle with weather events (rain, drought, frost, storms)
- **Irrigation System**: Strategic drought mitigation with $150/tile installation and operational costs

### ✅ **Advanced Employee Management:**
- **Multi-Employee System**: Unlimited hiring with trait-based candidates and strategic hiring decisions
- **AI Pathfinding**: A* algorithm with visual debugging and intelligent navigation
- **Employee Needs**: Hunger/thirst/rest systems with visual status indicators
- **Advanced Buildings**: Water coolers, tool sheds, employee housing for workforce optimization

### ✅ **Strategic Economic Systems:**
- **Contract System**: Seasonal contracts with guaranteed pricing and bulk delivery requirements
- **Market Complexity**: Dynamic pricing with 30-day history and strategic selling opportunities
- **Farm Specialization**: Multiple specialization tracks for focused agricultural strategies
- **Building Infrastructure**: Storage silos, irrigation systems, and employee amenities

### ✅ **Complete Game Systems:**
- **Save/Load System**: Multiple save slots with auto-save and complete state persistence
- **Professional UI**: Commercial-grade interface with tooltips, notifications, and smooth animations
- **Event-Driven Architecture**: Modular pub/sub system enabling complex system interactions
- **Visual Effects**: Particle systems for achievements, construction, and user feedback

### Controls:
- **Mouse**: Click and drag to select tiles, click tilled plots for soil information
- **Keyboard Shortcuts**:
  - `T` - Assign Till task to selected tiles
  - `P` - Plant crop task (with crop selection UI)
  - `H` - Assign Harvest task to selected tiles
  - `C` - Clear tile selection
  - `F1` - Toggle debug information (pathfinding visualization)
- **UI Elements**: Speed controls (Pause, 1x, 2x, 4x), hiring system, building placement, irrigation controls

### Game Flow:
1. Start with $0 cash and a mandatory $10,000 farmer loan
2. Receive $100/day government subsidy for first 30 days
3. **Hire employees** through the strategic hiring system - each with unique traits and specializations
4. **Choose your crops** based on seasons, soil conditions, and contract opportunities
5. **Install irrigation systems** for drought protection and consistent yields
6. **Build infrastructure** (storage silos, water coolers, tool sheds, employee housing)
7. **Accept contracts** for guaranteed pricing or sell at optimal market timing
8. **Manage soil health** through crop rotation and scientific farming practices
9. **Adapt to weather** events and seasonal changes affecting your crops

## Advanced Game Systems

### Agricultural Science & Education:
- **Soil Chemistry**: N-P-K nutrient levels affect crop yields and require strategic management
- **Crop Rotation**: Educational agricultural principles with yield bonuses for proper rotation
- **Weather Integration**: Seasonal patterns affecting planting windows and growth rates
- **Irrigation Strategy**: Investment vs. operational cost decisions for drought mitigation

### Strategic Business Management:
- **Contract System**: Accept guaranteed-price contracts vs. market speculation
- **Farm Specialization**: Choose focus areas that optimize your operation for specific goals
- **Multi-Crop Planning**: Balance fast-growth tomatoes, stable wheat, and profitable corn
- **Infrastructure Investment**: Tool sheds boost efficiency, employee housing reduces commute times

### Sophisticated Employee Systems:
- **Trait-Based Hiring**: "Hard Worker", "Green Thumb", "Runner" traits affect performance
- **Needs Management**: Advanced AI with hunger/thirst/rest affecting productivity
- **Workplace Amenities**: Water coolers, tool sheds, and housing improve employee effectiveness
- **Multi-Employee Coordination**: Teams of workers with A* pathfinding and task distribution

### Economic Depth:
- **Market Dynamics**: 30-day price history, seasonal variations, and strategic timing
- **Financial Planning**: Loans, subsidies, daily expenses, and cash flow management
- **Building Economics**: Progressive pricing and capacity expansion decisions
- **Contract Risk/Reward**: Balance guaranteed income vs. potential market gains

## Development Status

✅ **Phase 1-4 Complete**: Core foundation, multi-employee systems, save/load, economic depth  
✅ **Phase 5 Complete**: Agricultural science systems (soil health, crop rotation, weather)  
✅ **Phase 6 Complete**: Irrigation & water management, contract system, farm specialization  
✅ **Advanced Features Complete**: Multi-crop system, advanced buildings, employee amenities  
✅ **UI Overhaul Phase 2 Complete**: Professional tooltip system, comprehensive notifications, enhanced animation framework with particle effects  
🎯 **Current Focus**: Tutorial system, additional employee traits, market complexity features

## Technical Architecture

Sophisticated modular design with event-driven architecture:
- **Core Systems**: Game manager, event system, time/grid managers, save/load persistence
- **Agricultural Systems**: Weather manager, soil chemistry, crop rotation, irrigation systems
- **Employee Systems**: Multi-employee coordination, trait systems, A* pathfinding, needs management  
- **Economic Systems**: Contract manager, market dynamics, specialization tracking, transaction logging
- **Building Systems**: Infrastructure placement, employee amenities, strategic capacity management
- **UI Systems**: Commercial-grade interface with tooltip system, notification framework, animation engine, and particle effects

## Development

See `CLAUDE.md` for detailed development guidance, `DEVELOPMENT_STATE.md` for current status, and `DOCUMENTATION.md` for comprehensive design specifications.