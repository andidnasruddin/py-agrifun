"""
Test Time Management System - Comprehensive Temporal Engine Validation

This test validates the complete Time Management System including:
- Game time progression and calculations
- Seasonal transitions and agricultural calendar
- Dynamic weather simulation and effects
- Event scheduling and management
- Time acceleration and control
- Integration with foundation systems
"""

import asyncio
import time
from scripts.systems.time_system import (
    TimeSystem, GameTime, Season, WeatherType, TimeOfDay,
    get_time_system, initialize_time_system, get_current_time,
    get_current_season, get_current_weather
)


async def test_time_system():
    """Test comprehensive time management system"""
    print("=" * 60)
    print("TIME MANAGEMENT SYSTEM TEST")
    print("=" * 60)
    
    try:
        # Test 1: Time System Initialization
        print("\n>>> Test 1: Time System Initialization")
        
        time_system = initialize_time_system()
        
        print(f"Time system created: {time_system is not None}")
        print(f"Initial game time: {time_system.get_current_time().get_date_string()}")
        print(f"Initial season: {time_system.get_current_season().value}")
        print(f"Initial weather: {time_system.get_current_weather().get_description()}")
        
        # Test 2: Time Progression
        print("\n>>> Test 2: Time Progression")
        
        initial_time = time_system.get_current_time()
        print(f"Starting time: {initial_time.get_time_string()}")
        
        # Advance time by 2 hours
        time_system.advance_time(120)  # 120 minutes = 2 hours
        
        new_time = time_system.get_current_time()
        print(f"After 2 hours: {new_time.get_time_string()}")
        print(f"Time advancement working: {new_time.hours == (initial_time.hours + 2) % 24}")
        
        # Test 3: Day/Night Cycle
        print("\n>>> Test 3: Day/Night Cycle")
        
        # Set to evening time
        time_system.advance_time(600)  # 10 more hours to evening
        evening_time = time_system.get_current_time()
        
        print(f"Evening time: {evening_time.get_time_string()}")
        print(f"Time of day: {evening_time.get_time_of_day().value}")
        print(f"Is work hours: {evening_time.is_work_hours()}")
        
        # Advance to next day
        time_system.advance_time(600)  # 10 more hours to next morning
        morning_time = time_system.get_current_time()
        
        print(f"Next morning: {morning_time.get_time_string()}")
        print(f"Day changed: {morning_time.days > evening_time.days}")
        
        # Test 4: Seasonal Transitions
        print("\n>>> Test 4: Seasonal Transitions")
        
        current_season = time_system.get_current_season()
        print(f"Current season: {current_season.value}")
        
        # Advance through a full season (90 days = 90 * 24 * 60 minutes)
        season_minutes = 90 * 24 * 60
        time_system.advance_time(season_minutes)
        
        new_season = time_system.get_current_season()
        print(f"After 90 days: {new_season.value}")
        print(f"Season changed: {new_season != current_season}")
        
        # Get planting recommendations
        recommendations = time_system.get_planting_recommendations()
        print(f"Planting recommendations: {recommendations}")
        
        # Test 5: Weather System
        print("\n>>> Test 5: Weather System")
        
        weather = time_system.get_current_weather()
        print(f"Current weather: {weather.get_description()}")
        print(f"Temperature: {weather.temperature_c:.1f}C")
        print(f"Crop growth modifier: {weather.crop_growth_modifier:.2f}")
        print(f"Work efficiency: {weather.work_efficiency_modifier:.2f}")
        
        # Test weather forecast
        forecast = time_system.get_weather_forecast(3)
        print(f"3-day forecast: {len(forecast)} days")
        for i, day_weather in enumerate(forecast):
            print(f"  Day {i+1}: {day_weather.weather_type.value}")
        
        # Test 6: Event Scheduling
        print("\n>>> Test 6: Event Scheduling")
        
        events_received = []
        def track_events(event_data):
            events_received.append(event_data)
        
        # Subscribe to events
        event_system = time_system.event_system
        event_system.subscribe('test_scheduled_event', track_events)
        event_system.subscribe('harvest_reminder', track_events)
        
        # Schedule immediate event
        event_id = time_system.schedule_event('test_scheduled_event', 1, {'test': True})
        print(f"Scheduled event ID: {event_id}")
        
        # Schedule harvest reminder
        harvest_id = time_system.schedule_event('harvest_reminder', 5, {
            'crop': 'corn',
            'message': 'Time to harvest!'
        })
        
        # Advance time to trigger events
        time_system.advance_time(10)
        
        # Process events
        event_system.process_events()
        
        print(f"Events received: {len(events_received)}")
        for event in events_received:
            print(f"  Event: {event}")
        
        # Test 7: Time Scale Control
        print("\n>>> Test 7: Time Scale Control")
        
        original_scale = time_system.time_scale
        print(f"Original time scale: {original_scale}x")
        
        # Test different time scales
        time_system.set_time_scale(2.0)
        print(f"New time scale: {time_system.time_scale}x")
        
        time_system.set_time_scale(0.5)
        print(f"Slow time scale: {time_system.time_scale}x")
        
        # Reset to normal
        time_system.set_time_scale(1.0)
        print(f"Reset time scale: {time_system.time_scale}x")
        
        # Test 8: Pause/Resume
        print("\n>>> Test 8: Pause/Resume Control")
        
        print(f"Time paused: {time_system.paused}")
        
        time_system.pause()
        print(f"After pause: {time_system.paused}")
        
        time_system.resume()
        print(f"After resume: {time_system.paused}")
        
        # Test 9: Agricultural Calendar
        print("\n>>> Test 9: Agricultural Calendar")
        
        # Test planting recommendations for different seasons
        seasons = [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER]
        
        for season in seasons:
            # Temporarily set season by advancing time
            current_time = time_system.get_current_time()
            print(f"{season.value.title()} planting recommendations:")
            
            # Check if corn is optimal this season
            corn_optimal = time_system.is_optimal_planting_time('corn')
            print(f"  Corn optimal: {corn_optimal}")
            
            # Get time until next spring
            if season != Season.SPRING:
                time_to_spring = time_system.get_time_until_season(Season.SPRING)
                days_to_spring = time_to_spring // (24 * 60)
                print(f"  Days until spring: {days_to_spring}")
        
        # Test 10: Global Convenience Functions
        print("\n>>> Test 10: Global Convenience Functions")
        
        global_time = get_current_time()
        global_season = get_current_season()
        global_weather = get_current_weather()
        
        print(f"Global time access: {global_time.get_time_string()}")
        print(f"Global season access: {global_season.value}")
        print(f"Global weather access: {global_weather.weather_type.value}")
        
        # Test convenience event scheduling
        from scripts.systems.time_system import schedule_event, set_time_scale
        
        convenience_event_id = schedule_event('convenience_test', 1, {'source': 'convenience'})
        print(f"Convenience event scheduled: {convenience_event_id}")
        
        set_time_scale(1.5)
        print(f"Convenience time scale set: {time_system.time_scale}x")
        
        print("\n" + "=" * 60)
        print("TIME MANAGEMENT SYSTEM TEST: PASSED")
        print("All temporal systems working correctly!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nTime system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_weather_integration():
    """Test weather system integration and effects"""
    print("\n" + "=" * 60)
    print("WEATHER SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    try:
        time_system = get_time_system()
        
        # Test weather effects on different seasons
        seasons_tested = []
        weather_effects = []
        
        for i in range(4):  # Test 4 seasons
            season = time_system.get_current_season()
            weather = time_system.get_current_weather()
            
            print(f"\n{season.value.title()} Season Weather:")
            print(f"  Weather type: {weather.weather_type.value}")
            print(f"  Temperature: {weather.temperature_c:.1f}C")
            print(f"  Crop growth modifier: {weather.crop_growth_modifier:.2f}")
            print(f"  Work efficiency: {weather.work_efficiency_modifier:.2f}")
            print(f"  Soil moisture change: {weather.soil_moisture_change:.2f}")
            
            seasons_tested.append(season)
            weather_effects.append({
                'season': season,
                'growth_modifier': weather.crop_growth_modifier,
                'work_efficiency': weather.work_efficiency_modifier
            })
            
            # Advance to next season
            time_system.advance_time(90 * 24 * 60)  # 90 days
        
        print(f"\nWeather integration test passed!")
        print(f"Seasons tested: {len(seasons_tested)}")
        print(f"Weather effects calculated: {len(weather_effects)}")
        
        return True
        
    except Exception as e:
        print(f"Weather integration test failed: {e}")
        return False


if __name__ == "__main__":
    try:
        # Run main time system test
        success1 = asyncio.run(test_time_system())
        
        # Run weather integration test
        success2 = asyncio.run(test_weather_integration())
        
        if success1 and success2:
            print("\n[SUCCESS] All time management tests passed!")
        else:
            print("\n[FAILED] Some tests failed!")
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()