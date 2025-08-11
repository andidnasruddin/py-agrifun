# Bug Log - Farming Simulation Game

**Purpose**: Track bugs, issues, and their resolution status for context continuity across development sessions.

**Last Updated**: 2025-08-11

## 🐛 Active Issues

### High Priority

*No high priority issues currently active*

#### BUG-001: Employee Direct Movement Pathfinding
**Status**: ✅ Resolved  
**Date Resolved**: 2025-01-28
**Severity**: Medium  
**Description**: Employee uses direct line movement instead of proper pathfinding  
**Solution**: Implemented A* pathfinding algorithm with visual debugging
**Technical Details**: 
- Created `pathfinding.py` with complete A* implementation
- Updated `employee.py` to use pathfinding for movement
- Added path visualization for debugging
- Includes path caching and optimization
- Fallback to direct movement if pathfinding fails
**Verification**: 
- Employee now follows optimal paths between waypoints
- Visual path debugging shows green lines and waypoint markers
- Performance tested on 16x16 grid with no issues

#### BUG-002: Automatic Crop Sales
**Status**: ✅ Resolved  
**Date Resolved**: 2025-08-11  
**Severity**: Was Low  
**Description**: Strategic inventory system implemented with manual selling  
**Solution**: Complete inventory management with FIFO selling, quality tracking  
**Technical Details**: 
- Full inventory system in `inventory_manager.py` with 100-unit base capacity
- Manual selling through UI with storage capacity management
- Quality-based pricing and harvest date tracking
- Building system integration for storage upgrades

#### BUG-003: Task Assignment Validation
**Status**: 🔴 Open  
**Severity**: Low  
**Description**: Limited validation when assigning inappropriate tasks  
**Reproduction**:
1. Try to plant on untilled soil
2. Try to harvest non-mature crops  
3. Tasks get assigned but can't be completed
**Impact**: Player confusion when tasks don't execute  
**Technical Details**:
- `_can_assign_task()` in `grid_manager.py` has basic validation
- Employee will move to tile but can't complete invalid tasks
**Solution**: Better pre-assignment validation and user feedback  
**Priority**: Polish phase  
**Workaround**: Players learn valid task sequences quickly

### Medium Priority

#### BUG-004: Employee Stuck States
**Status**: 🔴 Open  
**Severity**: Low  
**Description**: Employee can get stuck in certain edge cases  
**Reproduction**: 
1. Assign task while employee is resting
2. Employee might not transition back to work properly
**Impact**: Employee becomes unresponsive until needs change  
**Technical Details**: State machine transitions in `employee.py`  
**Solution**: Better state transition handling and timeouts  
**Priority**: Polish phase  
**Workaround**: Speed up time or wait for needs to change state

#### BUG-005: UI Tooltip Missing
**Status**: 🔴 Open  
**Severity**: Low  
**Description**: No tooltips implemented despite design specification  
**Impact**: Poor user experience for new players  
**Technical Details**: pygame-gui tooltip system not implemented  
**Solution**: Add comprehensive tooltip system  
**Priority**: UI polish phase  
**Workaround**: README provides controls documentation

#### BUG-006: Market Price Edge Cases
**Status**: 🔴 Open  
**Severity**: Low  
**Description**: Market price can theoretically hit exact min/max bounds  
**Reproduction**: Very rare, requires specific random sequences  
**Impact**: Price stuck at boundary for multiple days  
**Technical Details**: `update_corn_price()` in `economy_manager.py`  
**Solution**: Better price volatility algorithm with guaranteed variance  
**Priority**: Balance testing phase  
**Workaround**: Restart game if encountered

### Low Priority

#### BUG-007: Frame Rate Inconsistency
**Status**: 🔴 Open  
**Severity**: Low  
**Description**: Occasional frame drops during intensive UI updates  
**Reproduction**: Rapid tile selection with many UI events  
**Impact**: Minor visual stuttering  
**Solution**: Optimize event processing and UI updates  
**Priority**: Performance optimization phase  
**Workaround**: Avoid rapid clicking

#### BUG-008: Employee Needs Display Overlap
**Status**: 🔴 Open  
**Severity**: Trivial  
**Description**: Employee needs bars can overlap with tile highlights  
**Impact**: Minor visual issue  
**Solution**: Better needs bar positioning or transparency  
**Priority**: Visual polish  
**Workaround**: Cosmetic issue only

## ✅ Resolved Issues

### 🎉 MAJOR RESOLUTION - Phase 2 (August 2025)

#### BUG-009: Stuck UI Hiring Panel Elements (CRITICAL FIX)
**Status**: ✅ Resolved  
**Date Resolved**: 2025-08-11  
**Severity**: High (Game-breaking UI bug)  
**Description**: Permanent stuck UI elements including 'Strategic Hiring - Available Candidates' text, 'Sort by:' dropdown, and hiring table columns that wouldn't disappear on game startup  
**Impact**: Major - Caused stuck UI elements that blocked normal gameplay  
**Root Cause**: Multiple conflicting visibility management systems in pygame-gui:
  - Four competing systems: `.visible` flags, `.hide()/.show()` methods, internal tracking flags, and startup protection
  - pygame-gui element lifecycle problems with child elements remaining in rendering queue
  - Race conditions between competing visibility control systems
**Solution**: **Complete architectural refactoring of panel management**
  - **Phase 1**: Eliminated conflicting visibility systems and startup protection mechanisms
  - **Phase 2**: Implemented single-source-of-truth using dynamic create/destroy pattern instead of hide/show
  - **Phase 3**: Comprehensive cleanup of all child elements when panels close
**Technical Details**: 
  - Replaced `_hide_applicant_panel()` with `_destroy_applicant_panel()` that completely destroys all child elements
  - Implemented `_applicant_panel_exists` flag for clean state tracking
  - Dynamic panel creation via `_create_applicant_panel()` only when needed
  - Proper pygame-gui element lifecycle with `.kill()` methods
  - Removed all startup protection and competing visibility mechanisms
**Testing**: 
  - ✅ No stuck elements detected on startup
  - ✅ Panel creation/destruction working perfectly
  - ✅ All hiring workflow functionality preserved
  - ✅ Performance unchanged with dynamic creation
**Why Previous Attempts Failed**: 
  - Previous fixes (including Claude Opus 4.1, specialized UI agents) attempted to patch existing complex system
  - This solution addressed the fundamental architecture problem rather than symptoms
  - Root cause was pygame-gui rendering queue management, not just visibility flags
**Fix Location**: Complete refactoring of `scripts/ui/ui_manager.py` panel management system

### Resolved in MVP Phase 1

#### BUG-R001: Event System Queue Overflow
**Status**: ✅ Resolved  
**Date Resolved**: 2025-01-28  
**Description**: Events could accumulate without processing  
**Solution**: Added event processing at end of each game loop frame  
**Fix Location**: `game_manager.py:run()` - added event processing call

#### BUG-R002: Time Speed Control Not Working
**Status**: ✅ Resolved  
**Date Resolved**: 2025-01-28  
**Description**: UI speed buttons didn't affect game time  
**Solution**: Proper event connection between UI and time manager  
**Fix Location**: `ui_manager.py:handle_event()` and `time_manager.py:_handle_speed_change()`

#### BUG-R003: Employee Tasks Not Clearing
**Status**: ✅ Resolved  
**Date Resolved**: 2025-01-28  
**Description**: Completed tasks remained assigned to tiles  
**Solution**: Clear task assignment when work completes  
**Fix Location**: `employee.py:_complete_current_tile()`

## 🧪 Testing Status

### Manual Testing Completed
- ✅ Basic game loop functionality
- ✅ Employee state transitions
- ✅ Economic transactions
- ✅ Time progression and controls
- ✅ UI interaction and feedback

### Testing Needed
- 🔲 Extended gameplay sessions (multiple hours)
- 🔲 Economic failure conditions (bankruptcy scenarios)  
- 🔲 Employee edge cases (critical needs while working)
- 🔲 Performance under extended play
- 🔲 Save/load system (when implemented)

## 🔍 Known Limitations (By Design)

### MVP Phase 1 Limitations
These are intentional limitations for the MVP that will be addressed in future phases:

#### LIMIT-001: Single Employee Only
**Status**: ✅ Resolved  
**Date Resolved**: 2025-08-11  
**Description**: Multi-employee system fully implemented - not limited to "Sam"  
**Technical Details**: Employee manager supports unlimited employees with full coordination

#### LIMIT-002: Corn Crop Only
**Status**: By Design  
**Description**: Only corn farming implemented  
**Future**: Multiple crops in Phase 4

#### LIMIT-003: No Save System
**Status**: By Design  
**Description**: No game persistence between sessions  
**Future**: Save/load system in Phase 3

#### LIMIT-004: No Workstations
**Status**: ✅ Partially Resolved  
**Date Resolved**: 2025-08-11  
**Description**: Storage silos fully implemented and functional  
**Technical Details**: Building system with progressive pricing ($500-$1687) and capacity upgrades  
**Remaining**: Water cooler and employee housing planned for Phase 3

#### LIMIT-005: Simple Market System
**Status**: By Design  
**Description**: Only basic price volatility  
**Future**: Complex market dynamics in Phase 5

## 📊 Bug Statistics

### Current Status
- **Active Issues**: 6 (0 High, 4 Medium, 2 Low priority)
- **Resolved Issues**: 7 (including 1 CRITICAL UI bug that defeated multiple AI attempts)
- **Known Limitations**: 3 (by design, 2 resolved)

### Resolution Rate  
- **Phase 1**: 4 core issues resolved during initial development
- **Phase 2**: 2 major limitations resolved (multi-employee, storage system)
- **Current**: All High priority issues resolved, focus on polish and balance
- **Target for Phase 3**: Resolve remaining Medium priority issues

### Major Feature Completions
- ✅ Multi-employee system (was LIMIT-001)
- ✅ Strategic storage system (was BUG-002)  
- ✅ Building system with storage silos (was LIMIT-004 partial)
- ✅ A* pathfinding implementation (was BUG-001)
- ✅ **CRITICAL UI BUG RESOLUTION** - Stuck hiring panel elements (BUG-009) - **DEFEATED MULTIPLE AI ATTEMPTS**

## 🚨 Emergency Issues Protocol

### Critical Issues (Game Unplayable)
1. Stop current development
2. Create emergency branch for fixes
3. Document issue with full reproduction steps
4. Fix immediately before continuing other work
5. Update BUG_LOG.md with resolution

### Non-Critical Issues
1. Add to this log with appropriate priority
2. Consider workarounds for immediate relief
3. Schedule fix based on priority and development phase
4. Test fix thoroughly before marking resolved

## 💡 Issue Prevention Guidelines

### Code Review Checklist
- [ ] Event subscriptions properly cleaned up
- [ ] State machine transitions handle all edge cases
- [ ] UI updates don't block game logic
- [ ] Error handling for user input edge cases
- [ ] Performance impact considered for real-time systems

### Testing Guidelines
- Always test with extreme values (very low money, critical employee needs)
- Test rapid user input and edge case timing
- Verify state consistency after major operations
- Test with different game speeds and pause/resume cycles

This bug log will be maintained throughout development to ensure issues don't get lost between sessions and to track the overall health of the codebase.