"""
Balance Testing Utility for Farming Simulation Game

This tool runs automated gameplay simulations to test economic balance and identify
issues with game parameters. It simulates multiple game scenarios to ensure the
game provides challenging but achievable gameplay.

Usage:
    python tools/balance_tester.py
    python tools/balance_tester.py --scenario=aggressive --days=60
    python tools/balance_tester.py --help

Features:
- Multiple gameplay scenarios (conservative, balanced, aggressive)
- Extended simulation periods (7, 30, 60+ days)
- Economic analysis and recommendations
- Parameter sensitivity testing
- Bankruptcy and success condition analysis
"""

import sys
import os
import argparse
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add the parent directory to sys.path to import game modules
# This allows us to import from scripts/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import game configuration and systems
from scripts.core.config import *
from scripts.core.event_system import EventSystem
from scripts.core.time_manager import TimeManager
from scripts.economy.economy_manager import EconomyManager
from scripts.core.inventory_manager import InventoryManager
from scripts.employee.employee_manager import EmployeeManager
from scripts.buildings.building_manager import BuildingManager


class GameplayScenario:
    """Defines a specific gameplay scenario for testing"""
    
    def __init__(self, name: str, description: str, strategy: Dict[str, Any]):
        # Store scenario identification information
        self.name = name  # Short name for the scenario (e.g., "conservative")
        self.description = description  # Human-readable description of the strategy
        self.strategy = strategy  # Dictionary containing all strategy parameters
        
        # Initialize tracking variables for this scenario
        self.results = {}  # Will store simulation results after running
        self.daily_snapshots = []  # Will store daily economic data


class BalanceTester:
    """Main balance testing system that runs economic simulations"""
    
    def __init__(self):
        """Initialize the balance tester with default scenarios"""
        
        # Create event system for simulation (required by all game systems)
        self.event_system = EventSystem()
        
        # Define different gameplay scenarios to test
        # Each scenario represents a different player strategy
        self.scenarios = [
            GameplayScenario(
                name="conservative",
                description="Cautious player - minimal risk, slow expansion",
                strategy={
                    'initial_field_size': 4,  # Start with 4 tilled tiles
                    'expansion_rate': 0.5,    # Add 0.5 tiles per day on average
                    'max_field_size': 32,     # Never exceed 32 planted tiles
                    'employee_hiring_threshold': 500,  # Hire when cash > $500
                    'max_employees': 2,       # Conservative hiring (max 2 employees)
                    'building_purchase_threshold': 1000,  # Buy buildings when cash > $1000
                    'sell_timing': 'immediate',  # Sell crops as soon as harvested
                    'storage_usage': 0.3      # Only use 30% of storage capacity
                }
            ),
            GameplayScenario(
                name="balanced",
                description="Typical player - moderate risk and growth",
                strategy={
                    'initial_field_size': 8,  # Start with 8 tilled tiles
                    'expansion_rate': 1.0,    # Add 1 tile per day on average
                    'max_field_size': 64,     # Expand to 64 planted tiles
                    'employee_hiring_threshold': 300,  # Hire when cash > $300
                    'max_employees': 3,       # Moderate hiring (max 3 employees)
                    'building_purchase_threshold': 600,  # Buy buildings when cash > $600
                    'sell_timing': 'strategic',  # Wait for good prices when possible
                    'storage_usage': 0.7      # Use 70% of storage capacity
                }
            ),
            GameplayScenario(
                name="aggressive",
                description="Risk-taking player - rapid expansion and high risk",
                strategy={
                    'initial_field_size': 16,  # Start with 16 tilled tiles (ambitious)
                    'expansion_rate': 2.0,     # Add 2 tiles per day on average
                    'max_field_size': 100,     # Expand to nearly full grid
                    'employee_hiring_threshold': 200,  # Hire when cash > $200 (risky)
                    'max_employees': 5,        # Aggressive hiring (max 5 employees)
                    'building_purchase_threshold': 400,  # Buy buildings when cash > $400
                    'sell_timing': 'market_timing',  # Hold crops for best prices
                    'storage_usage': 0.9       # Use 90% of storage capacity
                }
            )
        ]
        
        # Store results from all scenario runs
        self.all_results = []  # List of all completed scenario results
        
        print("Balance Tester initialized with 3 gameplay scenarios")
        print("Scenarios: Conservative, Balanced, Aggressive")
    
    def run_simulation(self, scenario: GameplayScenario, simulation_days: int = 30) -> Dict[str, Any]:
        """
        Run a complete gameplay simulation for the specified scenario
        
        Args:
            scenario: The gameplay scenario to simulate
            simulation_days: Number of game days to simulate
            
        Returns:
            Dictionary containing complete simulation results and analysis
        """
        print(f"\n=== Running {scenario.name} scenario for {simulation_days} days ===")
        print(f"Strategy: {scenario.description}")
        
        # Initialize all game systems for this simulation run
        # Create fresh event system for isolated simulation
        sim_event_system = EventSystem()
        
        # Create time manager to drive the simulation
        time_manager = TimeManager(sim_event_system)
        
        # Create economy manager to track financial state
        economy_manager = EconomyManager(sim_event_system)
        
        # Create inventory manager for crop storage
        inventory_manager = InventoryManager(sim_event_system)
        
        # Create building manager for storage upgrades
        building_manager = BuildingManager(sim_event_system, economy_manager, inventory_manager)
        
        # Create employee manager with starting employee disabled (we'll control hiring)
        employee_manager = EmployeeManager(
            sim_event_system, 
            None,  # No grid manager needed for simulation
            inventory_manager, 
            time_manager,
            create_starting_employee=True  # Start with Sam for consistency
        )
        
        # Initialize scenario tracking
        scenario.daily_snapshots = []  # Clear any previous data
        current_day = 1  # Track what day we're simulating
        
        # Simulate each day of the scenario
        for day in range(1, simulation_days + 1):
            # Process one day of game time
            daily_result = self._simulate_single_day(
                day, scenario, time_manager, economy_manager, 
                inventory_manager, building_manager, employee_manager
            )
            
            # Store daily snapshot for analysis
            scenario.daily_snapshots.append(daily_result)
            
            # Check for bankruptcy or other failure conditions
            if daily_result['cash'] < -1000:  # Significant debt threshold
                print(f"  Day {day}: BANKRUPTCY DETECTED - Ending simulation early")
                break
            
            # Print progress updates every 7 days
            if day % 7 == 0:
                cash = daily_result['cash']
                employees = daily_result['employee_count']
                storage = daily_result['storage_used']
                print(f"  Day {day}: Cash=${cash:.2f}, Employees={employees}, Storage={storage}")
        
        # Generate comprehensive analysis of the simulation results
        analysis = self._analyze_simulation_results(scenario, simulation_days)
        
        # Store final results in the scenario object
        scenario.results = analysis
        
        print(f"=== {scenario.name} simulation complete ===")
        print(f"Final Status: {analysis['final_status']}")
        print(f"Final Cash: ${analysis['final_cash']:.2f}")
        print(f"Net Worth: ${analysis['final_net_worth']:.2f}")
        
        return analysis
    
    def _simulate_single_day(self, day: int, scenario: GameplayScenario, 
                           time_manager, economy_manager, inventory_manager,
                           building_manager, employee_manager) -> Dict[str, Any]:
        """
        Simulate a single day of gameplay according to the scenario strategy
        
        Args:
            day: Current day number (1-based)
            scenario: The scenario being simulated
            *_manager: All the game system managers
            
        Returns:
            Dictionary with daily statistics and state information
        """
        
        # Advance time to trigger daily events (loan payments, subsidies, etc.)
        # Simulate advancing time by 24 hours (1 full game day)
        time_manager.advance_time(hours=24)
        
        # Process daily economic events (utilities, loan payments, subsidies)
        economy_manager.process_daily_expenses()
        
        # Get current game state for decision making
        current_cash = economy_manager.get_current_balance()
        current_storage = inventory_manager.get_total_storage_used()
        storage_capacity = inventory_manager.get_storage_capacity()
        employee_count = len(employee_manager.employees)
        
        # Simulate player decisions based on scenario strategy
        strategy = scenario.strategy  # Get the strategy parameters for this scenario
        
        # Decision 1: Employee Hiring
        # Check if we should hire more employees based on cash and strategy
        if (current_cash > strategy['employee_hiring_threshold'] and 
            employee_count < strategy['max_employees']):
            
            # Simulate hiring a new employee
            new_employee_name = f"Worker_{employee_count + 1}"  # Generate simple name
            employee_id = employee_manager.hire_employee(new_employee_name, ['hard_worker'])
            print(f"    Day {day}: Hired {new_employee_name} (Cash: ${current_cash:.2f})")
        
        # Decision 2: Building Purchases (Storage Silos)
        # Check if we should buy storage buildings based on cash and need
        if (current_cash > strategy['building_purchase_threshold'] and
            current_storage > storage_capacity * 0.8):  # Storage is 80%+ full
            
            # Check if we can actually purchase a storage silo
            if building_manager.can_purchase_building('storage_silo'):
                # Simulate purchasing a storage silo
                building_manager._handle_purchase_request({
                    'building_id': 'storage_silo',
                    'player_confirmed': True
                })
                print(f"    Day {day}: Purchased Storage Silo (Cash: ${current_cash:.2f})")
        
        # Decision 3: Crop Selling Strategy
        # Simulate selling crops based on the scenario's selling strategy
        corn_inventory = inventory_manager.get_crop_count('corn')
        current_corn_price = economy_manager.corn_price
        
        if corn_inventory > 0:  # Only sell if we have crops
            
            if strategy['sell_timing'] == 'immediate':
                # Conservative: Sell everything immediately
                sell_quantity = corn_inventory
                
            elif strategy['sell_timing'] == 'strategic':
                # Balanced: Sell when storage is getting full or price is good
                storage_percentage = current_storage / storage_capacity
                if storage_percentage > strategy['storage_usage'] or current_corn_price >= 6.0:
                    sell_quantity = corn_inventory // 2  # Sell half the inventory
                else:
                    sell_quantity = 0  # Hold crops
                    
            elif strategy['sell_timing'] == 'market_timing':
                # Aggressive: Only sell when price is very good or storage is critical
                if current_corn_price >= 7.0 or current_storage >= storage_capacity * 0.95:
                    sell_quantity = corn_inventory
                else:
                    sell_quantity = 0  # Hold for better prices
            
            # Execute the selling decision
            if sell_quantity > 0:
                revenue = inventory_manager.sell_crop('corn', sell_quantity, current_corn_price)
                if revenue > 0:
                    print(f"    Day {day}: Sold {sell_quantity} corn for ${revenue:.2f} at ${current_corn_price:.2f}/unit")
        
        # Simulate crop production based on field size and employee efficiency
        # This is a simplified simulation of the actual farming process
        field_size = min(strategy['max_field_size'], 
                        strategy['initial_field_size'] + int(day * strategy['expansion_rate']))
        
        # Calculate daily crop yield (simplified - assume some tiles harvest each day)
        # In reality, crops take time to grow, but for simulation we average it out
        daily_harvest_tiles = field_size * 0.2  # Assume 20% of field harvests daily on average
        employee_efficiency = 1.0 + (employee_count - 1) * 0.15  # Improved from 0.1 to 0.15 - better employee ROI
        
        # Simulate harvesting crops with quality variation
        if daily_harvest_tiles > 0:
            total_yield = int(daily_harvest_tiles * CORN_BASE_YIELD * employee_efficiency)
            if total_yield > 0:
                # Add harvested crops to inventory with average quality
                success = inventory_manager.add_crop('corn', total_yield, 0.8, day)
                if success:
                    print(f"    Day {day}: Harvested {total_yield} corn from {daily_harvest_tiles:.1f} tiles")
        
        # Update all game systems to process the day's events
        economy_manager.update(1.0)  # Update with 1 day delta
        inventory_manager.update(1.0)
        building_manager.update(1.0)
        employee_manager.update(1.0)
        
        # Process all events that were generated during this day
        economy_manager.event_system.process_events()
        
        # Collect daily statistics for analysis
        daily_stats = {
            'day': day,
            'cash': economy_manager.get_current_balance(),
            'net_worth': economy_manager.get_net_worth(),
            'corn_inventory': inventory_manager.get_crop_count('corn'),
            'storage_used': inventory_manager.get_total_storage_used(),
            'storage_capacity': inventory_manager.get_storage_capacity(),
            'employee_count': len(employee_manager.employees),
            'corn_price': economy_manager.corn_price,
            'field_size': field_size,
            'loan_balance': sum(loan.remaining_balance for loan in economy_manager.loans),
            'daily_expenses': economy_manager._calculate_daily_expenses(),
            'subsidy_days_remaining': economy_manager.subsidy_days_remaining
        }
        
        return daily_stats
    
    def _analyze_simulation_results(self, scenario: GameplayScenario, days_simulated: int) -> Dict[str, Any]:
        """
        Analyze the results of a completed simulation and generate insights
        
        Args:
            scenario: The completed scenario with daily_snapshots filled
            days_simulated: Number of days that were simulated
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        
        # Get the final day's data for summary statistics
        if not scenario.daily_snapshots:
            return {'error': 'No simulation data to analyze'}
        
        final_day = scenario.daily_snapshots[-1]  # Get last day's data
        first_day = scenario.daily_snapshots[0]   # Get first day's data
        
        # Calculate key performance metrics
        final_cash = final_day['cash']
        final_net_worth = final_day['net_worth']
        cash_change = final_cash - first_day['cash']
        
        # Determine simulation outcome
        if final_cash < -500:
            final_status = "BANKRUPTCY"
        elif final_net_worth > 5000:
            final_status = "HIGHLY_SUCCESSFUL"
        elif final_net_worth > 2000:
            final_status = "SUCCESSFUL"
        elif final_net_worth > 0:
            final_status = "VIABLE"
        else:
            final_status = "STRUGGLING"
        
        # Calculate growth and efficiency metrics
        max_cash = max(day['cash'] for day in scenario.daily_snapshots)
        min_cash = min(day['cash'] for day in scenario.daily_snapshots)
        cash_volatility = max_cash - min_cash
        
        # Calculate average daily profit over the simulation period
        # Skip first few days to avoid initial loan distortion
        if len(scenario.daily_snapshots) > 7:
            profit_days = scenario.daily_snapshots[7:]  # Use days 7+ for profit calculation
            daily_profits = []
            for i in range(1, len(profit_days)):
                daily_profit = profit_days[i]['net_worth'] - profit_days[i-1]['net_worth']
                daily_profits.append(daily_profit)
            
            average_daily_profit = sum(daily_profits) / len(daily_profits) if daily_profits else 0
        else:
            average_daily_profit = 0
        
        # Analyze employee and expansion efficiency
        max_employees = max(day['employee_count'] for day in scenario.daily_snapshots)
        max_field_size = max(day['field_size'] for day in scenario.daily_snapshots)
        
        # Calculate storage utilization statistics
        storage_usage_rates = [day['storage_used'] / day['storage_capacity'] * 100 
                              for day in scenario.daily_snapshots if day['storage_capacity'] > 0]
        avg_storage_usage = sum(storage_usage_rates) / len(storage_usage_rates) if storage_usage_rates else 0
        max_storage_usage = max(storage_usage_rates) if storage_usage_rates else 0
        
        # Identify critical events and days
        bankruptcy_days = [day['day'] for day in scenario.daily_snapshots if day['cash'] < 0]
        high_risk_days = [day['day'] for day in scenario.daily_snapshots if day['cash'] < 100]
        
        # Analyze loan repayment progress
        initial_loan = first_day['loan_balance']
        final_loan = final_day['loan_balance']
        loan_progress = (initial_loan - final_loan) / initial_loan * 100 if initial_loan > 0 else 100
        
        # Generate recommendations based on the analysis
        recommendations = []
        
        if final_status == "BANKRUPTCY":
            recommendations.append("CRITICAL: Reduce initial expansion rate or increase subsidy period")
        elif average_daily_profit < 50:
            recommendations.append("Consider increasing crop prices or reducing daily expenses")
        
        if cash_volatility > 2000:
            recommendations.append("High cash volatility detected - consider smoothing income/expenses")
        
        if max_storage_usage < 50:
            recommendations.append("Storage capacity may be too high - players not utilizing fully")
        elif max_storage_usage > 95:
            recommendations.append("Storage capacity may be too low - players hitting limits")
        
        if len(bankruptcy_days) > days_simulated * 0.1:  # More than 10% of days in bankruptcy
            recommendations.append("Frequent bankruptcy periods - economic balance too harsh")
        
        # Compile comprehensive analysis results
        analysis = {
            'scenario_name': scenario.name,
            'days_simulated': days_simulated,
            'final_status': final_status,
            'final_cash': final_cash,
            'final_net_worth': final_net_worth,
            'cash_change': cash_change,
            'average_daily_profit': average_daily_profit,
            'max_cash': max_cash,
            'min_cash': min_cash,
            'cash_volatility': cash_volatility,
            'max_employees': max_employees,
            'max_field_size': max_field_size,
            'avg_storage_usage': avg_storage_usage,
            'max_storage_usage': max_storage_usage,
            'bankruptcy_days': len(bankruptcy_days),
            'high_risk_days': len(high_risk_days),
            'loan_repayment_progress': loan_progress,
            'recommendations': recommendations,
            'daily_data': scenario.daily_snapshots  # Include all daily data for detailed analysis
        }
        
        return analysis
    
    def run_all_scenarios(self, simulation_days: int = 30) -> List[Dict[str, Any]]:
        """
        Run balance testing for all defined scenarios
        
        Args:
            simulation_days: Number of days to simulate for each scenario
            
        Returns:
            List of analysis results for all scenarios
        """
        print(f"\n{'='*60}")
        print(f"BALANCE TESTING: Running {len(self.scenarios)} scenarios for {simulation_days} days each")
        print(f"{'='*60}")
        
        # Clear any previous results
        self.all_results = []
        
        # Run each scenario sequentially
        for scenario in self.scenarios:
            try:
                # Run the simulation for this scenario
                result = self.run_simulation(scenario, simulation_days)
                self.all_results.append(result)
                
            except Exception as e:
                # Handle any errors during simulation
                print(f"ERROR in {scenario.name} scenario: {e}")
                error_result = {
                    'scenario_name': scenario.name,
                    'error': str(e),
                    'final_status': 'ERROR'
                }
                self.all_results.append(error_result)
        
        # Generate comparative analysis across all scenarios
        comparative_analysis = self._generate_comparative_analysis()
        
        return self.all_results
    
    def _generate_comparative_analysis(self) -> Dict[str, Any]:
        """
        Compare results across all scenarios to identify balance issues
        
        Returns:
            Dictionary containing comparative analysis and recommendations
        """
        print(f"\n{'='*60}")
        print("COMPARATIVE ANALYSIS")
        print(f"{'='*60}")
        
        # Extract key metrics from all successful scenarios
        successful_scenarios = [r for r in self.all_results if r.get('final_status') not in ['ERROR', 'BANKRUPTCY']]
        
        if not successful_scenarios:
            print("WARNING: No scenarios were successful - major balance issues detected!")
            return {'status': 'CRITICAL_FAILURE', 'successful_scenarios': 0}
        
        # Compare final outcomes across scenarios
        print("\nSCENARIO COMPARISON:")
        print(f"{'Scenario':<15} {'Status':<15} {'Final Cash':<12} {'Net Worth':<12} {'Daily Profit':<12}")
        print("-" * 75)
        
        for result in self.all_results:
            if 'error' not in result:
                scenario_name = result['scenario_name']
                status = result['final_status']
                final_cash = result['final_cash']
                net_worth = result['final_net_worth']
                daily_profit = result['average_daily_profit']
                
                print(f"{scenario_name:<15} {status:<15} ${final_cash:<11.2f} ${net_worth:<11.2f} ${daily_profit:<11.2f}")
        
        # Identify balance concerns
        balance_issues = []
        
        # Check if conservative strategy is viable
        conservative_result = next((r for r in self.all_results if r['scenario_name'] == 'conservative'), None)
        if conservative_result and conservative_result['final_status'] in ['BANKRUPTCY', 'STRUGGLING']:
            balance_issues.append("Conservative strategy not viable - game may be too difficult")
        
        # Check if aggressive strategy is too rewarding
        aggressive_result = next((r for r in self.all_results if r['scenario_name'] == 'aggressive'), None)
        if aggressive_result and aggressive_result['final_status'] == 'HIGHLY_SUCCESSFUL':
            if aggressive_result['average_daily_profit'] > 200:  # Very high profit
                balance_issues.append("Aggressive strategy may be too profitable - lacks challenge")
        
        # Check for strategy diversity (all strategies shouldn't have identical outcomes)
        net_worths = [r['final_net_worth'] for r in successful_scenarios]
        if len(set(int(nw/500) for nw in net_worths)) == 1:  # All within same 500-unit range
            balance_issues.append("All strategies yield similar results - need more strategic differentiation")
        
        print(f"\nBALANCE ASSESSMENT:")
        print(f"Successful Scenarios: {len(successful_scenarios)}/{len(self.all_results)}")
        
        if balance_issues:
            print("ISSUES DETECTED:")
            for issue in balance_issues:
                print(f"  - {issue}")
        else:
            print("[SUCCESS] No major balance issues detected")
        
        return {
            'successful_scenarios': len(successful_scenarios),
            'total_scenarios': len(self.all_results),
            'balance_issues': balance_issues,
            'comparative_data': self.all_results
        }
    
    def save_results(self, filename: str = None):
        """
        Save all simulation results to a JSON file for later analysis
        
        Args:
            filename: Optional filename, defaults to timestamped filename
        """
        if filename is None:
            # Generate timestamped filename if none provided
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"balance_test_results_{timestamp}.json"
        
        # Ensure tools directory exists for saving results
        os.makedirs('tools', exist_ok=True)
        filepath = os.path.join('tools', filename)
        
        # Prepare data for JSON serialization
        save_data = {
            'test_timestamp': datetime.now().isoformat(),
            'scenarios': len(self.scenarios),
            'results': self.all_results
        }
        
        try:
            # Write results to JSON file with proper formatting
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"\n[SUCCESS] Results saved to: {filepath}")
            print(f"   File size: {os.path.getsize(filepath)} bytes")
            
        except Exception as e:
            print(f"[ERROR] Error saving results: {e}")


def main():
    """Main entry point for the balance testing utility"""
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Balance Testing Utility for Farming Simulation Game')
    
    # Add command line options for customizing the test run
    parser.add_argument('--days', type=int, default=30,
                       help='Number of days to simulate (default: 30)')
    parser.add_argument('--scenario', type=str, choices=['conservative', 'balanced', 'aggressive', 'all'],
                       default='all', help='Which scenario to run (default: all)')
    parser.add_argument('--save', action='store_true',
                       help='Save results to JSON file')
    parser.add_argument('--output', type=str,
                       help='Output filename for results (implies --save)')
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Print header information
    print("FARMING SIMULATION BALANCE TESTER")
    print("==================================")
    print(f"Simulation Days: {args.days}")
    print(f"Target Scenario: {args.scenario}")
    
    try:
        # Create the balance tester instance
        tester = BalanceTester()
        
        if args.scenario == 'all':
            # Run all scenarios
            results = tester.run_all_scenarios(args.days)
        else:
            # Run specific scenario
            target_scenario = next((s for s in tester.scenarios if s.name == args.scenario), None)
            if target_scenario:
                result = tester.run_simulation(target_scenario, args.days)
                results = [result]
            else:
                print(f"ERROR: Scenario '{args.scenario}' not found")
                return 1
        
        # Save results if requested
        if args.save or args.output:
            tester.save_results(args.output)
        
        print("\n[SUCCESS] Balance testing completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Balance testing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    # Run the main function and exit with appropriate code
    exit_code = main()
    sys.exit(exit_code)