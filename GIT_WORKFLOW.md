# Git Workflow for Context Continuity

**Purpose**: Establish git practices that support context preservation across Claude Code sessions and minimize bug introduction.

## 🔧 Repository Setup

### Initial Setup (One Time)
```bash
# Initialize git repo if not already done
git init

# Add all current files
git add .
git commit -m "MVP Phase 1 Complete - Core Foundation

- Event-driven architecture implemented
- Complete grid system with tile management  
- Employee AI with state machine and needs
- Time management with real-time progression
- Economy system with loans and market dynamics
- pygame-gui UI with resource panels
- Full till→plant→harvest→sell game loop functional

🤖 Generated with Claude Code (claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## 📝 Commit Message Standards

### Format Template
```
<Type>: <Brief summary>

<Detailed description>
- Key changes made
- Systems affected  
- Important implementation notes

<Context for future sessions>
- Current development phase
- Next priorities
- Known issues introduced or fixed

🤖 Generated with Claude Code (claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit Types
- **feat**: New feature implementation
- **fix**: Bug fix or issue resolution
- **refactor**: Code restructuring without behavior change
- **docs**: Documentation updates (including context files)
- **test**: Adding or updating tests
- **config**: Configuration changes or tuning
- **ui**: User interface changes
- **perf**: Performance improvements

### Example Commit Messages
```bash
# Feature commit
git commit -m "feat: Implement A* pathfinding for employee movement

- Replace direct movement with proper pathfinding algorithm
- Add obstacle detection and path optimization
- Employee now navigates around future workstations properly

Context: Resolves BUG-001, enables Phase 2 workstation placement
Next: Test pathfinding performance with multiple employees

🤖 Generated with Claude Code (claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Bug fix commit  
git commit -m "fix: Resolve employee stuck states in task transitions

- Add timeout handling for resting state
- Improve state machine transition logic
- Add debug logging for state changes

Context: Fixes BUG-004, improves employee reliability
Testing: Extended gameplay session shows no stuck states

🤖 Generated with Claude Code (claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Documentation commit
git commit -m "docs: Update context files with current development state

- Refresh DEVELOPMENT_STATE.md with completed features
- Add new architectural decisions to ARCHITECTURE_NOTES.md
- Update BUG_LOG.md with resolved issues

Context: End of session context preservation
Phase: MVP Phase 1 → Phase 2 transition planning

🤖 Generated with Claude Code (claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## 🌿 Branching Strategy

### Main Branches
- **main**: Stable, working code only
- **develop**: Integration branch for ongoing development
- **feature/***: Individual feature development
- **hotfix/***: Critical bug fixes

### Feature Development Workflow
```bash
# Start new feature
git checkout develop
git pull origin develop  # If working with remote
git checkout -b feature/employee-pathfinding

# Work on feature with frequent commits
git add scripts/employee/pathfinding.py
git commit -m "feat: Add A* pathfinding implementation"

git add scripts/employee/employee.py  
git commit -m "feat: Integrate pathfinding with employee AI"

# Merge back to develop when complete
git checkout develop
git merge feature/employee-pathfinding
git branch -d feature/employee-pathfinding
```

### Phase Transition Workflow
```bash
# Create phase branch for major milestones
git checkout main
git checkout -b phase-2-enhanced-systems

# Merge develop into phase branch
git merge develop

# When phase complete, merge to main
git checkout main
git merge phase-2-enhanced-systems
git tag -a v2.0 -m "Phase 2: Enhanced Systems Complete"
```

## 📊 Session Management

### Start of Session Checklist
1. **Review context**: Read DEVELOPMENT_STATE.md and BUG_LOG.md
2. **Check git status**: `git status` and `git log --oneline -5`
3. **Test current state**: `python main.py` to verify functionality
4. **Resume from checkpoint**: Use `claude --resume` if continuing work

### During Development
```bash
# Commit frequently with meaningful messages
git add <files>
git commit -m "<type>: <description>

Context: <current work and next steps>"

# Update context files as work progresses
# Commit context updates separately
git add DEVELOPMENT_STATE.md BUG_LOG.md
git commit -m "docs: Update development context

- Mark feature X as completed
- Add bug Y to tracking
- Update next session priorities"
```

### End of Session Protocol  
```bash
# Ensure all work is committed
git status  # Should be clean

# Update all context files
git add DEVELOPMENT_STATE.md ARCHITECTURE_NOTES.md BUG_LOG.md
git commit -m "docs: End-of-session context update

Phase: <current phase>
Completed: <what was accomplished>
Next: <priorities for next session>
Issues: <any new bugs discovered>

🤖 Generated with Claude Code (claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Tag major milestones
git tag -a session-$(date +%Y%m%d) -m "Development session $(date +%Y-%m-%d)"
```

## 🔍 Context Recovery Commands

### Quick Status Check
```bash
# See recent development history
git log --oneline -10

# Check what's changed since last session  
git diff HEAD~1

# See current branch and status
git status
git branch -v
```

### Detailed Context Recovery
```bash
# See commits since specific date
git log --since="2 days ago" --oneline

# Find specific bug fix commits
git log --grep="fix:" --oneline

# See file-specific history
git log -p scripts/core/game_manager.py

# Find when feature was implemented
git log --grep="pathfinding" --oneline
```

### Emergency Recovery
```bash
# If context is lost, check recent commit messages
git log -5 --format="%h %s %b"

# Find last working state
git log --grep="working" --oneline

# Revert to last stable state if needed
git checkout <commit-hash>
git checkout -b recovery-branch
```

## 🎯 Integration with Claude Code

### Memory File Updates
```bash
# After significant architectural changes
git add ARCHITECTURE_NOTES.md
git commit -m "docs: Document new event system patterns

- Add event-driven UI update pattern
- Document manager initialization order  
- Note performance considerations

Context: For future Claude Code sessions to understand system design"
```

### Checkpoint Creation
```bash
# Create checkpoints at logical stopping points
git tag -a checkpoint-ui-complete -m "UI system implementation complete

Features working:
- pygame-gui integration
- Resource panels and speed controls  
- Task assignment keyboard shortcuts
- Debug mode toggle

Next: Implement storage system for harvested crops
Known issues: See BUG_LOG.md entries BUG-002, BUG-005"
```

### Branch Naming for Claude Code
Use descriptive branch names that provide context:
```bash
git checkout -b feat/storage-system-for-crops
git checkout -b fix/employee-pathfinding-issues  
git checkout -b refactor/economy-manager-cleanup
git checkout -b phase-2/interview-system-prep
```

## ⚠️ Common Pitfalls to Avoid

### Don't Do This
- Commit WIP code without explaining current state
- Use generic messages like "fix bugs" or "update code"
- Forget to update context files before committing
- Work on main branch directly
- Let multiple features accumulate in single commit

### Do This Instead
- Commit working incremental changes with clear context
- Reference bug numbers and explain what was fixed
- Update DEVELOPMENT_STATE.md when completing features
- Use feature branches for experimental changes
- Separate feature commits from documentation commits

## 🚀 Integration with Development Tools

### VS Code Integration
```json
// .vscode/settings.json
{
    "git.inputValidationLength": 100,
    "git.inputValidationSubjectLength": 72,
    "git.defaultCloneDirectory": "./branches"
}
```

### Git Hooks (Optional)
```bash
# Pre-commit hook to ensure context files are updated
#!/bin/sh
if git diff --cached --name-only | grep -q "scripts/"; then
    if ! git diff --cached --name-only | grep -q "DEVELOPMENT_STATE.md"; then
        echo "Warning: Code changes without DEVELOPMENT_STATE.md update"
        echo "Consider updating context files before committing"
        exit 1
    fi
fi
```

This workflow ensures that each git commit provides sufficient context for future development sessions and helps prevent the bug introduction that occurs when context is lost between sessions.