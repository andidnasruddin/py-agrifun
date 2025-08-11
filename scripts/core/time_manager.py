"""
Time Manager - Handles game time, day/night cycle, and speed controls
Manages the 20-minute real-time workday system with pause and speed controls.
"""

import time
from scripts.core.config import *


class TimeManager:
    """Manages game time and day/night cycles"""
    
    def __init__(self, event_system):
        """Initialize time manager"""
        self.event_system = event_system
        
        # Time tracking
        self.current_day = 1
        self.current_hour = WORK_START_HOUR  # Start at 5 AM
        self.current_minute = 0
        
        # Speed control
        self.time_speed = 1  # 0 = paused, 1 = normal, 2 = 2x, 4 = 4x
        self.is_paused = False
        
        # Real time tracking
        self.game_time_elapsed = 0.0  # Total game time in seconds
        self.real_time_per_game_day = MINUTES_PER_GAME_DAY * 60  # 20 minutes in seconds
        self.real_time_per_game_hour = self.real_time_per_game_day / 24
        self.real_time_per_game_minute = self.real_time_per_game_hour / 60
        
        # Day tracking
        self.total_days_elapsed = 0
        self.work_hours_today = 0.0
        
        # Register for speed change events
        self.event_system.subscribe('time_speed_change', self._handle_speed_change)
        
        print(f"Time Manager initialized - Day {self.current_day}, {self.current_hour:02d}:{self.current_minute:02d}")
        print(f"Real time per game day: {self.real_time_per_game_day} seconds")
    
    def update(self, dt: float):
        """Update game time based on real time"""
        if self.is_paused or self.time_speed == 0:
            return
        
        # Apply speed multiplier
        effective_dt = dt * self.time_speed
        self.game_time_elapsed += effective_dt
        
        # Calculate game time from elapsed time
        old_hour = self.current_hour
        old_minute = self.current_minute
        old_day = self.current_day
        
        # Convert elapsed time to game time
        total_game_minutes = self.game_time_elapsed / self.real_time_per_game_minute
        total_game_hours = total_game_minutes / 60
        total_game_days = total_game_hours / 24
        
        # Extract current time components
        self.current_day = int(total_game_days) + 1
        
        hours_today = total_game_hours % 24
        self.current_hour = int(hours_today)
        
        minutes_this_hour = (hours_today - self.current_hour) * 60
        self.current_minute = int(minutes_this_hour)
        
        # Emit time update event
        if (old_hour != self.current_hour or 
            old_minute != self.current_minute or 
            old_day != self.current_day):
            
            self._emit_time_update()
        
        # Check for day change
        if old_day != self.current_day:
            self._handle_day_change(old_day)
        
        # Check for hour change
        if old_hour != self.current_hour:
            self._handle_hour_change(old_hour)
    
    def _emit_time_update(self):
        """Emit time update event"""
        self.event_system.emit('time_updated', {
            'day': self.current_day,
            'hour': self.current_hour,
            'minute': self.current_minute,
            'time_string': self.get_time_string(),
            'is_work_hours': self.is_work_hours(),
            'speed': self.time_speed
        })
    
    def _handle_day_change(self, old_day: int):
        """Handle day transition"""
        self.total_days_elapsed = self.current_day - 1
        self.work_hours_today = 0.0
        
        # Emit day passed event
        self.event_system.emit('day_passed', {
            'old_day': old_day,
            'new_day': self.current_day,
            'total_days': self.total_days_elapsed,
            'days': 1  # Days that passed (usually 1)
        })
        
        print(f"Day changed from {old_day} to {self.current_day}")
    
    def _handle_hour_change(self, old_hour: int):
        """Handle hour transition"""
        # Track work hours
        if self.is_work_hours():
            self.work_hours_today += 1
        
        # Emit hour passed event
        self.event_system.emit('hour_passed', {
            'old_hour': old_hour,
            'new_hour': self.current_hour,
            'day': self.current_day,
            'is_work_hours': self.is_work_hours()
        })
        
        # Special events at specific hours
        if self.current_hour == WORK_START_HOUR:
            self.event_system.emit('work_day_started', {
                'day': self.current_day,
                'hour': self.current_hour
            })
        elif self.current_hour == WORK_END_HOUR:
            self.event_system.emit('work_day_ended', {
                'day': self.current_day,
                'hour': self.current_hour,
                'work_hours_today': self.work_hours_today
            })
    
    def is_work_hours(self) -> bool:
        """Check if current time is during work hours"""
        return WORK_START_HOUR <= self.current_hour < WORK_END_HOUR
    
    def get_time_string(self) -> str:
        """Get formatted time string"""
        am_pm = "AM" if self.current_hour < 12 else "PM"
        display_hour = self.current_hour if self.current_hour <= 12 else self.current_hour - 12
        if display_hour == 0:
            display_hour = 12
        
        return f"Day {self.current_day} - {display_hour}:{self.current_minute:02d} {am_pm}"
    
    def get_progress_through_day(self) -> float:
        """Get progress through current day (0.0 to 1.0)"""
        hours_passed = self.current_hour + (self.current_minute / 60.0)
        return hours_passed / 24.0
    
    def get_work_day_progress(self) -> float:
        """Get progress through work day (0.0 to 1.0)"""
        if not self.is_work_hours():
            if self.current_hour < WORK_START_HOUR:
                return 0.0
            else:
                return 1.0
        
        work_hours_passed = self.current_hour - WORK_START_HOUR + (self.current_minute / 60.0)
        total_work_hours = WORK_END_HOUR - WORK_START_HOUR
        return work_hours_passed / total_work_hours
    
    def pause(self):
        """Pause time progression"""
        self.is_paused = True
        self.event_system.emit('time_paused', {
            'day': self.current_day,
            'hour': self.current_hour,
            'minute': self.current_minute
        })
        print("Game paused")
    
    def resume(self):
        """Resume time progression"""
        self.is_paused = False
        self.event_system.emit('time_resumed', {
            'day': self.current_day,
            'hour': self.current_hour,
            'minute': self.current_minute,
            'speed': self.time_speed
        })
        print(f"Game resumed at {self.time_speed}x speed")
    
    def set_speed(self, speed: int):
        """Set time speed multiplier"""
        if speed == 0:
            self.pause()
        else:
            old_speed = self.time_speed
            self.time_speed = max(1, min(4, speed))  # Clamp to 1-4x
            
            if self.is_paused and speed > 0:
                self.resume()
            
            self.event_system.emit('time_speed_changed', {
                'old_speed': old_speed,
                'new_speed': self.time_speed,
                'day': self.current_day,
                'hour': self.current_hour
            })
            
            print(f"Time speed changed to {self.time_speed}x")
    
    def _handle_speed_change(self, event_data):
        """Handle speed change requests from UI"""
        speed = event_data.get('speed', 1)
        self.set_speed(speed)
    
    def advance_time(self, hours: float = 0, minutes: float = 0):
        """Manually advance time (for testing)"""
        additional_seconds = (hours * 60 + minutes) * self.real_time_per_game_minute
        self.game_time_elapsed += additional_seconds
        print(f"Advanced time by {hours}h {minutes}m")
    
    def get_current_time_info(self) -> dict:
        """Get comprehensive time information"""
        return {
            'day': self.current_day,
            'hour': self.current_hour,
            'minute': self.current_minute,
            'time_string': self.get_time_string(),
            'is_work_hours': self.is_work_hours(),
            'work_day_progress': self.get_work_day_progress(),
            'day_progress': self.get_progress_through_day(),
            'speed': self.time_speed,
            'is_paused': self.is_paused,
            'total_days_elapsed': self.total_days_elapsed,
            'work_hours_today': self.work_hours_today
        }
    
    def is_time_for_market_update(self) -> bool:
        """Check if it's time to update market prices (end of day)"""
        return self.current_hour == 23 and self.current_minute >= 59
    
    def should_save_game(self) -> bool:
        """Check if it's time for auto-save (every few hours)"""
        return (self.current_hour % 3 == 0 and 
                self.current_minute == 0 and 
                self.is_work_hours())