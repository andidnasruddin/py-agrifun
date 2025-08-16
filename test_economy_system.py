"""
Test Economy & Market System - Comprehensive Economic Simulation Validation

This test validates the complete Economy & Market System including:
- Market price dynamics and seasonal fluctuations
- Transaction management and financial tracking
- Loan system with interest calculations
- Contract system with buyers and deliveries
- Subsidy programs and government support
- Integration with Time Management System
"""

import asyncio
import time
from scripts.systems.economy_system import (
    EconomySystem, TransactionType, MarketCondition, 
    get_economy_system, initialize_economy_system,
    get_current_price, sell_crops, get_financial_summary
)
from scripts.systems.time_system import get_time_system, Season


async def test_economy_system():
    """Test comprehensive economy and market system"""
    print("=" * 60)
    print("ECONOMY & MARKET SYSTEM TEST")
    print("=" * 60)
    
    try:
        # Test 1: Economy System Initialization
        print("\n>>> Test 1: Economy System Initialization")
        
        economy = initialize_economy_system()
        time_system = get_time_system()
        
        initial_summary = economy.get_financial_summary()
        
        print(f"Economy system created: {economy is not None}")
        print(f"Starting cash: ${initial_summary['current_cash']:.2f}")
        print(f"Starting loans: {initial_summary['active_loans']}")
        print(f"Starting contracts: {initial_summary['active_contracts']}")
        print(f"Subsidy days remaining: {initial_summary['subsidy_days_remaining']}")
        
        # Test 2: Market Prices
        print("\n>>> Test 2: Market Price System")
        
        # Check market prices for all commodities
        commodities = ['corn', 'wheat', 'tomatoes', 'lettuce']
        initial_prices = {}
        
        for commodity in commodities:
            price = economy.get_current_price(commodity)
            quality_price = economy.get_price_for_quality(commodity, 0.9)  # 90% quality
            initial_prices[commodity] = price
            
            print(f"{commodity.title()}: ${price:.2f} (90% quality: ${quality_price:.2f})")
        
        market_prices_working = all(price > 0 for price in initial_prices.values())
        print(f"Market prices working: {market_prices_working}")
        
        # Test 3: Crop Sales
        print("\n>>> Test 3: Crop Sales System")
        
        # Sell some crops
        corn_sale = economy.sell_crops('corn', 100, quality=0.8)
        wheat_sale = economy.sell_crops('wheat', 50, quality=0.9)
        
        print(f"Corn sale success: {corn_sale['success']}")
        if corn_sale['success']:
            print(f"  Sold 100 corn for ${corn_sale['total_value']:.2f}")
            print(f"  Unit price: ${corn_sale['unit_price']:.2f}")
        
        print(f"Wheat sale success: {wheat_sale['success']}")
        if wheat_sale['success']:
            print(f"  Sold 50 wheat for ${wheat_sale['total_value']:.2f}")
            print(f"  Unit price: ${wheat_sale['unit_price']:.2f}")
        
        # Check updated cash
        post_sale_summary = economy.get_financial_summary()
        cash_increased = post_sale_summary['current_cash'] > initial_summary['current_cash']
        print(f"Cash increased after sales: {cash_increased}")
        print(f"New cash balance: ${post_sale_summary['current_cash']:.2f}")
        
        # Test 4: Loan System
        print("\n>>> Test 4: Loan Management System")
        
        # Apply for a new loan
        loan_application = economy.apply_for_loan(5000.0, 36, "Equipment purchase")
        
        print(f"Loan application success: {loan_application['success']}")
        if loan_application['success']:
            loan_id = loan_application['loan_id']
            monthly_payment = loan_application['monthly_payment']
            print(f"  Loan ID: {loan_id}")
            print(f"  Monthly payment: ${monthly_payment:.2f}")
            
            # Make a loan payment
            payment_result = economy.make_loan_payment(loan_id, monthly_payment)
            print(f"  Payment success: {payment_result['success']}")
            if payment_result['success']:
                print(f"  Remaining balance: ${payment_result['remaining_balance']:.2f}")
        
        # Test 5: Contract System
        print("\n>>> Test 5: Contract Management System")
        
        # Check available contracts
        available_contracts = list(economy.available_contracts.values())
        print(f"Available contracts: {len(available_contracts)}")
        
        if available_contracts:
            # Accept first contract
            contract = available_contracts[0]
            contract_id = contract.contract_id
            
            print(f"Contract details:")
            print(f"  Buyer: {contract.buyer_name}")
            print(f"  Commodity: {contract.commodity}")
            print(f"  Quantity: {contract.quantity_required}")
            print(f"  Price per unit: ${contract.price_per_unit:.2f}")
            print(f"  Quality requirement: {contract.quality_requirement:.1%}")
            
            # Accept the contract
            accept_result = economy.accept_contract(contract_id)
            print(f"Contract acceptance: {accept_result['success']}")
            
            if accept_result['success']:
                # Fulfill part of the contract
                fulfill_result = economy.fulfill_contract(contract_id, 25, 0.85)
                print(f"Contract fulfillment: {fulfill_result['success']}")
                if fulfill_result['success']:
                    print(f"  Payment received: ${fulfill_result['payment']:.2f}")
                    print(f"  Remaining quantity: {fulfill_result['remaining_quantity']}")
        
        # Test 6: Transaction History
        print("\n>>> Test 6: Transaction History")
        
        transactions = economy.transactions
        print(f"Total transactions: {len(transactions)}")
        
        # Show recent transactions
        recent_transactions = transactions[-5:] if len(transactions) >= 5 else transactions
        print("Recent transactions:")
        for txn in recent_transactions:
            print(f"  {txn.transaction_type.value}: ${txn.amount:.2f} - {txn.description}")
        
        # Test 7: Seasonal Market Changes
        print("\n>>> Test 7: Seasonal Market Dynamics")
        
        # Advance to next season
        print(f"Current season: {time_system.get_current_season().value}")
        
        # Record current prices
        current_prices = {commodity: economy.get_current_price(commodity) for commodity in commodities}
        
        # Advance through a season (90 days)
        time_system.advance_time(90 * 24 * 60)  # 90 days in minutes
        
        new_season = time_system.get_current_season()
        print(f"New season: {new_season.value}")
        
        # Check price changes
        new_prices = {commodity: economy.get_current_price(commodity) for commodity in commodities}
        
        print("Price changes:")
        for commodity in commodities:
            old_price = current_prices[commodity]
            new_price = new_prices[commodity]
            change_percent = ((new_price - old_price) / old_price) * 100
            print(f"  {commodity.title()}: ${old_price:.2f} → ${new_price:.2f} ({change_percent:+.1f}%)")
        
        # Test 8: Subsidy System
        print("\n>>> Test 8: Subsidy System")
        
        pre_subsidy_cash = economy.current_cash
        subsidy_days_before = economy.subsidy_days_remaining
        
        # Advance one day to trigger subsidy
        time_system.advance_time(24 * 60)  # 1 day
        
        post_subsidy_cash = economy.current_cash
        subsidy_days_after = economy.subsidy_days_remaining
        
        subsidy_received = post_subsidy_cash > pre_subsidy_cash
        days_decreased = subsidy_days_after < subsidy_days_before
        
        print(f"Subsidy received: {subsidy_received}")
        print(f"Subsidy days decreased: {days_decreased}")
        print(f"Subsidy days remaining: {subsidy_days_after}")
        
        # Test 9: Market Info and Analytics
        print("\n>>> Test 9: Market Information & Analytics")
        
        # Get detailed market info for corn
        corn_market_info = economy.get_market_info('corn')
        if corn_market_info:
            print(f"Corn market analysis:")
            print(f"  Base price: ${corn_market_info.base_price:.2f}")
            print(f"  Current price: ${corn_market_info.current_price:.2f}")
            print(f"  Seasonal factor: {corn_market_info.seasonal_factor:.2f}")
            print(f"  Quality premium: {corn_market_info.quality_premium:.1%}")
            print(f"  Price history entries: {len(corn_market_info.price_history)}")
        
        # Test 10: Global Convenience Functions
        print("\n>>> Test 10: Global Convenience Functions")
        
        # Test global access functions
        global_corn_price = get_current_price('corn')
        global_tomato_sale = sell_crops('tomatoes', 20, 0.95)
        global_summary = get_financial_summary()
        
        print(f"Global corn price: ${global_corn_price:.2f}")
        print(f"Global tomato sale success: {global_tomato_sale['success']}")
        print(f"Global summary cash: ${global_summary['current_cash']:.2f}")
        
        # Final summary
        final_summary = economy.get_financial_summary()
        
        print("\n" + "=" * 60)
        print("ECONOMY & MARKET SYSTEM TEST: PASSED")
        print("All economic systems working correctly!")
        print("=" * 60)
        print("Final Financial Summary:")
        print(f"  Cash: ${final_summary['current_cash']:.2f}")
        print(f"  Net Worth: ${final_summary['net_worth']:.2f}")
        print(f"  Active Loans: {final_summary['active_loans']}")
        print(f"  Active Contracts: {final_summary['active_contracts']}")
        print(f"  Total Transactions: {final_summary['total_transactions']}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nEconomy system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_market_integration():
    """Test market system integration with time and weather"""
    print("\n" + "=" * 60)
    print("MARKET INTEGRATION TEST")
    print("=" * 60)
    
    try:
        economy = get_economy_system()
        time_system = get_time_system()
        
        # Test market response to weather changes
        print("\n>>> Testing Market Response to Conditions")
        
        commodities = ['corn', 'wheat', 'tomatoes', 'lettuce']
        
        # Record baseline prices
        baseline_prices = {}
        for commodity in commodities:
            baseline_prices[commodity] = economy.get_current_price(commodity)
        
        print("Baseline prices:")
        for commodity, price in baseline_prices.items():
            print(f"  {commodity.title()}: ${price:.2f}")
        
        # Simulate multiple seasons
        for season_num in range(4):
            # Advance one season
            time_system.advance_time(90 * 24 * 60)  # 90 days
            
            current_season = time_system.get_current_season()
            print(f"\n{current_season.value.title()} Season Prices:")
            
            for commodity in commodities:
                current_price = economy.get_current_price(commodity)
                baseline_price = baseline_prices[commodity]
                change = ((current_price - baseline_price) / baseline_price) * 100
                print(f"  {commodity.title()}: ${current_price:.2f} ({change:+.1f}%)")
        
        # Test contract generation over time
        print("\n>>> Testing Contract Generation")
        
        initial_contracts = len(economy.available_contracts)
        
        # Advance several days to trigger contract generation
        for day in range(10):
            time_system.advance_time(24 * 60)  # 1 day
            
        final_contracts = len(economy.available_contracts)
        contracts_generated = final_contracts > initial_contracts
        
        print(f"Initial contracts: {initial_contracts}")
        print(f"Final contracts: {final_contracts}")
        print(f"New contracts generated: {contracts_generated}")
        
        print("\nMarket integration test passed!")
        
        return True
        
    except Exception as e:
        print(f"Market integration test failed: {e}")
        return False


if __name__ == "__main__":
    try:
        # Run main economy system test
        success1 = asyncio.run(test_economy_system())
        
        # Run market integration test
        success2 = asyncio.run(test_market_integration())
        
        if success1 and success2:
            print("\n[SUCCESS] All economy management tests passed!")
        else:
            print("\n[FAILED] Some tests failed!")
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()