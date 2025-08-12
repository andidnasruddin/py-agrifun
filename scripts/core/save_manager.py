"""
Save Manager - Handles game state serialization and persistence

This system manages saving and loading the complete game state including:
- Time progression and day/hour information
- Employee data (stats, traits, position, tasks)
- Grid state (tiles, crops, growth stages)  
- Economy state (cash, loans, transactions)
- Building state (owned buildings, capacity)
- Inventory state (crops, quantities, quality)

Features:
- JSON-based serialization for readability
- Multiple save slots (save_1.json, save_2.json, etc.)
- Auto-save functionality with configurable intervals
- Version compatibility for future game updates
- Comprehensive error handling and validation

Usage:
    save_manager = SaveManager(event_system, game_managers)
    save_manager.save_game("My Farm", slot=1)
    save_manager.load_game(slot=1)
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from scripts.core.config import *


class SaveManager:
    """Manages game state serialization and persistence"""
    
    def __init__(self, event_system, game_manager):
        """Initialize save manager with access to all game systems"""
        self.event_system = event_system
        self.game_manager = game_manager
        
        # Save directory and file management
        self.save_directory = "saves"
        self.auto_save_file = "autosave.json"
        self.save_version = "1.0"  # Version for compatibility tracking
        
        # Auto-save configuration
        self.auto_save_enabled = True
        self.auto_save_interval = 300.0  # 5 minutes in real time
        self.auto_save_timer = 0.0
        
        # Ensure save directory exists
        self._ensure_save_directory()
        
        # Register for events that trigger auto-save
        self.event_system.subscribe('day_passed', self._handle_day_passed)
        self.event_system.subscribe('manual_save_requested', self._handle_manual_save_request)
        self.event_system.subscribe('load_game_requested', self._handle_load_game_request)
        
        print(f"Save Manager initialized - Save directory: {self.save_directory}")
    
    def _ensure_save_directory(self):
        """Create saves directory if it doesn't exist"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
            print(f"Created save directory: {self.save_directory}")
    
    def save_game(self, save_name: str = "Quicksave", slot: int = 0, is_auto_save: bool = False) -> bool:
        """Save complete game state to specified slot"""
        try:
            # Generate filename based on slot or auto-save
            if is_auto_save:
                filename = self.auto_save_file
            else:
                filename = f"save_{slot}.json" if slot > 0 else "quicksave.json"
            
            filepath = os.path.join(self.save_directory, filename)
            
            # Collect game state from all managers
            game_state = self._collect_game_state(save_name)
            
            # Write to file with pretty formatting
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=2, ensure_ascii=False)
            
            save_type = "Auto-saved" if is_auto_save else "Saved"
            print(f"{save_type} game: '{save_name}' to {filename}")
            
            # Emit save completion event
            self.event_system.emit('game_saved', {
                'save_name': save_name,
                'filename': filename,
                'is_auto_save': is_auto_save,
                'slot': slot
            })
            
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            self.event_system.emit('save_failed', {
                'error': str(e),
                'save_name': save_name,
                'slot': slot
            })
            return False
    
    def load_game(self, slot: int = 0, filename: str = None) -> bool:
        """Load game state from specified slot or filename"""
        try:
            # Determine filename
            if filename:
                filepath = os.path.join(self.save_directory, filename)
            elif slot > 0:
                filepath = os.path.join(self.save_directory, f"save_{slot}.json")
            else:
                filepath = os.path.join(self.save_directory, "quicksave.json")
            
            # Check if save file exists
            if not os.path.exists(filepath):
                print(f"Save file not found: {filepath}")
                self.event_system.emit('load_failed', {
                    'error': 'Save file not found',
                    'filename': os.path.basename(filepath)
                })
                return False
            
            # Load and parse save file
            with open(filepath, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
            
            # Validate save file version
            save_version = game_state.get('save_version', '0.0')
            if not self._is_compatible_version(save_version):
                print(f"Incompatible save version: {save_version} (current: {self.save_version})")
                self.event_system.emit('load_failed', {
                    'error': f'Incompatible save version: {save_version}',
                    'filename': os.path.basename(filepath)
                })
                return False
            
            # Apply game state to all managers
            success = self._apply_game_state(game_state)
            
            if success:
                print(f"Loaded game: {game_state.get('save_name', 'Unknown')} from {os.path.basename(filepath)}")
                self.event_system.emit('game_loaded', {
                    'save_name': game_state.get('save_name', 'Unknown'),
                    'filename': os.path.basename(filepath),
                    'save_date': game_state.get('save_date', 'Unknown')
                })
            
            return success
            
        except Exception as e:
            print(f"Error loading game: {e}")
            self.event_system.emit('load_failed', {
                'error': str(e),
                'filename': filename or f"save_{slot}.json"
            })
            return False
    
    def _collect_game_state(self, save_name: str) -> Dict[str, Any]:
        """Collect complete game state from all managers"""
        game_state = {
            # Meta information
            'save_version': self.save_version,
            'save_name': save_name,
            'save_date': datetime.now().isoformat(),
            
            # Core game state from each manager
            'time_state': self._get_time_manager_state(),
            'economy_state': self._get_economy_manager_state(),
            'inventory_state': self._get_inventory_manager_state(),
            'grid_state': self._get_grid_manager_state(),
            'employee_state': self._get_employee_manager_state(),
            'building_state': self._get_building_manager_state(),
            'ui_state': self._get_ui_manager_state()
        }
        
        return game_state
    
    def _get_time_manager_state(self) -> Dict[str, Any]:
        """Get time manager state for saving"""
        time_manager = self.game_manager.time_manager
        return {
            'current_day': time_manager.current_day,
            'current_hour': time_manager.current_hour,
            'current_minute': time_manager.current_minute,
            'time_speed': time_manager.time_speed,  # Use correct attribute name
            'is_paused': time_manager.is_paused,
            'game_time_elapsed': getattr(time_manager, 'game_time_elapsed', 0.0)  # Use correct attribute name
        }
    
    def _get_economy_manager_state(self) -> Dict[str, Any]:
        """Get economy manager state for saving"""
        economy_manager = self.game_manager.economy_manager
        
        # Serialize loans data
        loans_data = []
        for loan in economy_manager.loans:
            loan_data = {
                'principal': loan.principal,
                'remaining_balance': loan.remaining_balance,
                'interest_rate': loan.interest_rate,
                'term_days': loan.term_days,
                'loan_type': loan.loan_type,
                'daily_payment': loan.daily_payment,
                'payments_made': loan.payments_made,
                'days_overdue': loan.days_overdue,
                'is_paid_off': loan.is_paid_off
            }
            loans_data.append(loan_data)
        
        # Serialize transactions
        transactions_data = []
        for transaction in economy_manager.transactions:
            trans_data = {
                'amount': transaction.amount,
                'description': transaction.description,
                'type': transaction.type,
                'day': transaction.day
            }
            transactions_data.append(trans_data)
        
        return {
            'cash': economy_manager.cash,
            'total_income': economy_manager.total_income,
            'total_expenses': economy_manager.total_expenses,
            'loans': loans_data,
            'subsidy_days_remaining': economy_manager.subsidy_days_remaining,
            'daily_subsidy_amount': economy_manager.daily_subsidy_amount,
            'corn_price': economy_manager.corn_price,
            'price_history': economy_manager.price_history,
            'transactions': transactions_data
        }
    
    def _get_inventory_manager_state(self) -> Dict[str, Any]:
        """Get inventory manager state for saving"""
        inventory_manager = self.game_manager.inventory_manager
        
        # Serialize crop entries
        crops_data = {}
        for crop_type, crop_entries in inventory_manager.crops.items():
            entries_data = []
            for entry in crop_entries:
                entry_data = {
                    'crop_type': entry.crop_type,
                    'quantity': entry.quantity,
                    'quality': entry.quality,
                    'harvest_day': entry.harvest_day
                }
                entries_data.append(entry_data)
            crops_data[crop_type] = entries_data
        
        return {
            'storage_capacity': inventory_manager.storage_capacity,
            'current_storage': inventory_manager.current_storage,
            'crops': crops_data
        }
    
    def _get_grid_manager_state(self) -> Dict[str, Any]:
        """Get grid manager state for saving"""
        grid_manager = self.game_manager.grid_manager
        
        # Serialize all tiles
        tiles_data = []
        for row in grid_manager.grid:
            row_data = []
            for tile in row:
                tile_data = {
                    'x': tile.x,
                    'y': tile.y,
                    'terrain_type': tile.terrain_type,
                    'soil_quality': tile.soil_quality,
                    'water_level': tile.water_level,
                    'current_crop': tile.current_crop,
                    'growth_stage': tile.growth_stage,
                    'days_growing': tile.days_growing,
                    'task_assignment': tile.task_assignment,
                    'task_assigned_to': tile.task_assigned_to,
                    'building_type': tile.building_type,
                    'is_occupied': tile.is_occupied
                }
                row_data.append(tile_data)
            tiles_data.append(row_data)
        
        return {
            'grid_width': GRID_WIDTH,
            'grid_height': GRID_HEIGHT,
            'tiles': tiles_data
        }
    
    def _get_employee_manager_state(self) -> Dict[str, Any]:
        """Get employee manager state for saving"""
        employee_manager = self.game_manager.employee_manager
        
        # Serialize all employees
        employees_data = []
        for employee_id, employee in employee_manager.employees.items():
            employee_data = {
                'id': employee.id,
                'name': employee.name,
                'x': employee.x,
                'y': employee.y,
                'target_x': employee.target_x,
                'target_y': employee.target_y,
                'state': employee.state.value,
                'state_timer': employee.state_timer,
                'skill_level': employee.skill_level,
                'walking_speed': employee.walking_speed,
                'max_stamina': employee.max_stamina,
                'hunger': employee.hunger,
                'thirst': employee.thirst,
                'rest': employee.rest,
                'traits': employee.traits.copy(),
                'work_efficiency': employee.work_efficiency,
                'daily_wage': employee.daily_wage,
                'assigned_tasks': self._serialize_employee_tasks(employee.assigned_tasks),
                'current_task': self._serialize_employee_task(employee.current_task)
            }
            employees_data.append(employee_data)
        
        return {
            'employees': employees_data,
            'next_employee_id': getattr(employee_manager, '_next_employee_id', 2)
        }
    
    def _serialize_employee_tasks(self, tasks: list) -> list:
        """Serialize employee tasks, converting Tile objects to coordinates"""
        serialized_tasks = []
        for task in tasks:
            serialized_task = task.copy()
            # Convert tile objects to coordinates
            if 'tiles' in serialized_task:
                tile_coords = []
                for tile in serialized_task['tiles']:
                    tile_coords.append({'x': tile.x, 'y': tile.y})
                serialized_task['tiles'] = tile_coords
            # Handle completed_tiles if present
            if 'completed_tiles' in serialized_task:
                completed_coords = []
                for tile in serialized_task['completed_tiles']:
                    completed_coords.append({'x': tile.x, 'y': tile.y})
                serialized_task['completed_tiles'] = completed_coords
            serialized_tasks.append(serialized_task)
        return serialized_tasks
    
    def _serialize_employee_task(self, task: dict) -> dict:
        """Serialize a single employee task, converting Tile objects to coordinates"""
        if not task:
            return None
        
        serialized_task = task.copy()
        # Convert tile objects to coordinates
        if 'tiles' in serialized_task:
            tile_coords = []
            for tile in serialized_task['tiles']:
                tile_coords.append({'x': tile.x, 'y': tile.y})
            serialized_task['tiles'] = tile_coords
        # Handle completed_tiles if present
        if 'completed_tiles' in serialized_task:
            completed_coords = []
            for tile in serialized_task['completed_tiles']:
                completed_coords.append({'x': tile.x, 'y': tile.y})
            serialized_task['completed_tiles'] = completed_coords
        return serialized_task
    
    def _get_building_manager_state(self) -> Dict[str, Any]:
        """Get building manager state for saving"""
        building_manager = self.game_manager.building_manager
        
        # Serialize owned buildings
        buildings_data = []
        for building in building_manager.owned_buildings:
            building_data = {
                'building_type_id': building.building_type.id,
                'x': building.x,
                'y': building.y,
                'level': building.level,
                'purchase_day': building.purchase_day
            }
            buildings_data.append(building_data)
        
        return {
            'owned_buildings': buildings_data
        }
    
    def _get_ui_manager_state(self) -> Dict[str, Any]:
        """Get UI manager state for saving"""
        ui_manager = self.game_manager.ui_manager
        return {
            'current_crop_type': getattr(ui_manager, 'current_crop_type', DEFAULT_CROP_TYPE),
            'show_debug': ui_manager.show_debug
        }
    
    def _is_compatible_version(self, save_version: str) -> bool:
        """Check if save file version is compatible with current game"""
        # For now, only exact version match
        # Future versions could implement backward compatibility
        return save_version == self.save_version
    
    def _apply_game_state(self, game_state: Dict[str, Any]) -> bool:
        """Apply loaded game state to all managers"""
        try:
            # Apply state to each manager in dependency order
            self._apply_time_manager_state(game_state.get('time_state', {}))
            self._apply_economy_manager_state(game_state.get('economy_state', {}))
            self._apply_inventory_manager_state(game_state.get('inventory_state', {}))
            self._apply_grid_manager_state(game_state.get('grid_state', {}))
            self._apply_employee_manager_state(game_state.get('employee_state', {}))
            self._apply_building_manager_state(game_state.get('building_state', {}))
            self._apply_ui_manager_state(game_state.get('ui_state', {}))
            
            return True
            
        except Exception as e:
            print(f"Error applying game state: {e}")
            return False
    
    def _apply_time_manager_state(self, time_state: Dict[str, Any]):
        """Apply time manager state from save file"""
        time_manager = self.game_manager.time_manager
        time_manager.current_day = time_state.get('current_day', 1)
        time_manager.current_hour = time_state.get('current_hour', 5)
        time_manager.current_minute = time_state.get('current_minute', 0)
        # Handle both old and new attribute names for compatibility
        time_manager.time_speed = time_state.get('time_speed', time_state.get('speed_multiplier', 1))
        time_manager.is_paused = time_state.get('is_paused', False)
        if hasattr(time_manager, 'game_time_elapsed'):
            time_manager.game_time_elapsed = time_state.get('game_time_elapsed', time_state.get('total_elapsed_time', 0.0))
    
    def _apply_economy_manager_state(self, economy_state: Dict[str, Any]):
        """Apply economy manager state from save file"""
        economy_manager = self.game_manager.economy_manager
        
        # Restore basic financial state
        economy_manager.cash = economy_state.get('cash', 0)
        economy_manager.total_income = economy_state.get('total_income', 0)
        economy_manager.total_expenses = economy_state.get('total_expenses', 0)
        
        # Restore subsidy info
        economy_manager.subsidy_days_remaining = economy_state.get('subsidy_days_remaining', 0)
        economy_manager.daily_subsidy_amount = economy_state.get('daily_subsidy_amount', 100)
        
        # Restore market data
        economy_manager.corn_price = economy_state.get('corn_price', 5.0)
        economy_manager.price_history = economy_state.get('price_history', [5.0])
        
        # Restore loans
        from scripts.economy.economy_manager import Loan
        economy_manager.loans.clear()
        loans_data = economy_state.get('loans', [])
        for loan_data in loans_data:
            loan = Loan(
                principal=loan_data['principal'],
                interest_rate=loan_data['interest_rate'],
                term_days=loan_data['term_days'],
                loan_type=loan_data['loan_type']
            )
            # Restore loan state
            loan.remaining_balance = loan_data['remaining_balance']
            loan.daily_payment = loan_data['daily_payment']
            loan.payments_made = loan_data['payments_made']
            loan.days_overdue = loan_data['days_overdue']
            loan.is_paid_off = loan_data['is_paid_off']
            economy_manager.loans.append(loan)
        
        # Restore transactions
        from scripts.economy.economy_manager import Transaction
        economy_manager.transactions.clear()
        transactions_data = economy_state.get('transactions', [])
        for trans_data in transactions_data:
            transaction = Transaction(
                amount=trans_data['amount'],
                description=trans_data['description'],
                transaction_type=trans_data['type'],
                day=trans_data['day']
            )
            economy_manager.transactions.append(transaction)
        
        # Emit money update event
        economy_manager.event_system.emit('money_changed', {'amount': economy_manager.cash})
    
    def _apply_inventory_manager_state(self, inventory_state: Dict[str, Any]):
        """Apply inventory manager state from save file"""
        inventory_manager = self.game_manager.inventory_manager
        
        # Restore basic inventory state
        inventory_manager.storage_capacity = inventory_state.get('storage_capacity', 100)
        inventory_manager.current_storage = inventory_state.get('current_storage', 0)
        
        # Restore crop entries
        from scripts.core.inventory_manager import CropEntry
        inventory_manager.crops.clear()
        crops_data = inventory_state.get('crops', {})
        
        for crop_type, entries_data in crops_data.items():
            crop_entries = []
            for entry_data in entries_data:
                entry = CropEntry(
                    crop_type=entry_data['crop_type'],
                    quantity=entry_data['quantity'],
                    quality=entry_data['quality'],
                    harvest_day=entry_data['harvest_day']
                )
                crop_entries.append(entry)
            inventory_manager.crops[crop_type] = crop_entries
    
    def _apply_grid_manager_state(self, grid_state: Dict[str, Any]):
        """Apply grid manager state from save file"""
        grid_manager = self.game_manager.grid_manager
        tiles_data = grid_state.get('tiles', [])
        
        # Restore tile states
        for y, row_data in enumerate(tiles_data):
            for x, tile_data in enumerate(row_data):
                if y < len(grid_manager.grid) and x < len(grid_manager.grid[y]):
                    tile = grid_manager.grid[y][x]
                    tile.terrain_type = tile_data.get('terrain_type', 'soil')
                    tile.soil_quality = tile_data.get('soil_quality', 5)
                    tile.water_level = tile_data.get('water_level', 100)
                    tile.current_crop = tile_data.get('current_crop', None)
                    tile.growth_stage = tile_data.get('growth_stage', 0)
                    tile.days_growing = tile_data.get('days_growing', 0)
                    tile.task_assignment = tile_data.get('task_assignment', None)
                    tile.task_assigned_to = tile_data.get('task_assigned_to', None)
                    tile.building_type = tile_data.get('building_type', None)
                    tile.is_occupied = tile_data.get('is_occupied', False)
                    # Note: building object will be restored by building manager
    
    def _apply_employee_manager_state(self, employee_state: Dict[str, Any]):
        """Apply employee manager state from save file"""
        employee_manager = self.game_manager.employee_manager
        
        # Clear existing employees
        employee_manager.employees.clear()
        
        # Recreate employees from save data
        from scripts.employee.employee import Employee, EmployeeState
        employees_data = employee_state.get('employees', [])
        
        for emp_data in employees_data:
            employee = Employee(emp_data['id'], emp_data['name'], emp_data['x'], emp_data['y'])
            
            # Restore employee state
            employee.target_x = emp_data.get('target_x', employee.x)
            employee.target_y = emp_data.get('target_y', employee.y)
            employee.state = EmployeeState(emp_data.get('state', 'idle'))
            employee.state_timer = emp_data.get('state_timer', 0.0)
            employee.skill_level = emp_data.get('skill_level', 1.0)
            employee.walking_speed = emp_data.get('walking_speed', employee.speed)
            employee.max_stamina = emp_data.get('max_stamina', 100)
            employee.hunger = emp_data.get('hunger', MAX_HUNGER)
            employee.thirst = emp_data.get('thirst', MAX_THIRST)
            employee.rest = emp_data.get('rest', MAX_REST)
            employee.traits = emp_data.get('traits', [])
            employee.work_efficiency = emp_data.get('work_efficiency', 1.0)
            employee.daily_wage = emp_data.get('daily_wage', BASE_EMPLOYEE_WAGE)
            employee.assigned_tasks = self._deserialize_employee_tasks(emp_data.get('assigned_tasks', []))
            employee.current_task = self._deserialize_employee_task(emp_data.get('current_task', None))
            
            # Re-apply traits
            for trait in employee.traits:
                employee._apply_trait_effects(trait)
            
            # Add to dictionary using ID as key
            employee_manager.employees[employee.id] = employee
        
        # Restore next ID counter
        if hasattr(employee_manager, '_next_employee_id'):
            employee_manager._next_employee_id = employee_state.get('next_employee_id', len(employees_data) + 1)
    
    def _deserialize_employee_tasks(self, tasks_data: list) -> list:
        """Deserialize employee tasks, converting coordinates back to Tile objects"""
        deserialized_tasks = []
        grid_manager = self.game_manager.grid_manager
        
        for task_data in tasks_data:
            task = task_data.copy()
            # Convert tile coordinates back to Tile objects
            if 'tiles' in task:
                tiles = []
                for coord in task['tiles']:
                    tile = grid_manager.get_tile(coord['x'], coord['y'])
                    if tile:
                        tiles.append(tile)
                task['tiles'] = tiles
            # Handle completed_tiles if present
            if 'completed_tiles' in task:
                completed_tiles = []
                for coord in task['completed_tiles']:
                    tile = grid_manager.get_tile(coord['x'], coord['y'])
                    if tile:
                        completed_tiles.append(tile)
                task['completed_tiles'] = completed_tiles
            deserialized_tasks.append(task)
        return deserialized_tasks
    
    def _deserialize_employee_task(self, task_data: dict) -> dict:
        """Deserialize a single employee task, converting coordinates back to Tile objects"""
        if not task_data:
            return None
        
        task = task_data.copy()
        grid_manager = self.game_manager.grid_manager
        
        # Convert tile coordinates back to Tile objects
        if 'tiles' in task:
            tiles = []
            for coord in task['tiles']:
                tile = grid_manager.get_tile(coord['x'], coord['y'])
                if tile:
                    tiles.append(tile)
            task['tiles'] = tiles
        # Handle completed_tiles if present
        if 'completed_tiles' in task:
            completed_tiles = []
            for coord in task['completed_tiles']:
                tile = grid_manager.get_tile(coord['x'], coord['y'])
                if tile:
                    completed_tiles.append(tile)
            task['completed_tiles'] = completed_tiles
        return task
    
    def _apply_building_manager_state(self, building_state: Dict[str, Any]):
        """Apply building manager state from save file"""
        building_manager = self.game_manager.building_manager
        
        # Clear existing buildings from both manager and grid
        for building in building_manager.owned_buildings:
            if hasattr(building, 'x') and hasattr(building, 'y'):
                building_manager.grid_manager.remove_building_at(building.x, building.y)
        building_manager.owned_buildings.clear()
        
        # Recreate buildings from save data
        from scripts.buildings.building_manager import Building
        buildings_data = building_state.get('owned_buildings', [])
        
        for building_data in buildings_data:
            building_type_id = building_data['building_type_id']
            if building_type_id in building_manager.building_types:
                building_type = building_manager.building_types[building_type_id]
                building = Building(
                    building_type=building_type,
                    x=building_data.get('x', 0),
                    y=building_data.get('y', 0),
                    level=building_data.get('level', 1),
                    purchase_day=building_data.get('purchase_day', 1)
                )
                building_manager.owned_buildings.append(building)
                
                # Place building on grid if grid manager is available
                if building_manager.grid_manager and building_data.get('x') is not None:
                    x, y = building.x, building.y
                    building_manager.grid_manager.place_building_at(x, y, building_type_id, building)
                
                # Re-apply building benefits
                building_manager._apply_building_benefits(building)
    
    def _apply_ui_manager_state(self, ui_state: Dict[str, Any]):
        """Apply UI manager state from save file"""
        ui_manager = self.game_manager.ui_manager
        if hasattr(ui_manager, 'current_crop_type'):
            ui_manager.current_crop_type = ui_state.get('current_crop_type', DEFAULT_CROP_TYPE)
        ui_manager.show_debug = ui_state.get('show_debug', False)
    
    def get_save_list(self) -> List[Dict[str, Any]]:
        """Get list of available save files with metadata"""
        saves = []
        
        # Check for save files in directory
        if os.path.exists(self.save_directory):
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.json'):
                    try:
                        filepath = os.path.join(self.save_directory, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        save_info = {
                            'filename': filename,
                            'save_name': data.get('save_name', 'Unknown'),
                            'save_date': data.get('save_date', 'Unknown'),
                            'save_version': data.get('save_version', '0.0'),
                            'day': data.get('time_state', {}).get('current_day', 1),
                            'cash': data.get('economy_state', {}).get('current_balance', 0),
                            'employees': len(data.get('employee_state', {}).get('employees', []))
                        }
                        saves.append(save_info)
                        
                    except Exception as e:
                        print(f"Error reading save file {filename}: {e}")
        
        # Sort by date (newest first)
        saves.sort(key=lambda x: x['save_date'], reverse=True)
        return saves
    
    def update(self, dt: float):
        """Update save manager (handle auto-save timer)"""
        if self.auto_save_enabled:
            self.auto_save_timer += dt
            if self.auto_save_timer >= self.auto_save_interval:
                self.save_game("Auto Save", is_auto_save=True)
                self.auto_save_timer = 0.0
    
    def _handle_day_passed(self, event_data):
        """Handle day passed event for conditional auto-save"""
        current_day = event_data.get('new_day', 1)
        
        # Auto-save every 5 days or on important milestones
        if current_day % 5 == 0 or current_day in [1, 10, 30]:
            self.save_game(f"Day {current_day} Auto Save", is_auto_save=True)
    
    def _handle_manual_save_request(self, event_data):
        """Handle manual save requests from UI"""
        save_name = event_data.get('save_name', 'Manual Save')
        slot = event_data.get('slot', 0)
        self.save_game(save_name, slot)
    
    def _handle_load_game_request(self, event_data):
        """Handle load game requests from UI"""
        slot = event_data.get('slot', 0)
        filename = event_data.get('filename', None)
        self.load_game(slot, filename)