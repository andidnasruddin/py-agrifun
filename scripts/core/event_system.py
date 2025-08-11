"""
Event System - Centralized event handling for decoupled system communication

This module implements a publish-subscribe pattern that enables loose coupling between
game systems. All inter-system communication should go through this event system to
maintain architectural integrity and support future features like save/load and replay.

Key Design Principles:
- Systems emit events without knowing who receives them
- Systems subscribe to events they care about
- Events are processed in batches to avoid frame-timing issues
- Event data is always passed as dictionaries for flexibility

Critical Events in the System:
- 'time_updated': Emitted every frame with current game time
- 'day_passed': Emitted when a new day begins (triggers economy, crop growth)  
- 'task_assigned': Emitted when tiles get work assignments
- 'money_changed': Emitted whenever cash balance changes (UI updates)
- 'game_quit': Emitted to shut down all systems gracefully

Usage Example:
    # Subscribe to events in system __init__
    event_system.subscribe('day_passed', self._handle_new_day)
    
    # Emit events when state changes
    event_system.emit('money_changed', {'amount': new_balance, 'change': delta})
    
    # Process events each frame (done by GameManager)
    event_system.process_events()

Performance Notes:
- Events are queued and processed in batches
- Recursive event processing is prevented
- Failed event handlers don't crash the system
"""

from typing import Dict, List, Callable, Any
from collections import defaultdict, deque


class EventSystem:
    """Central event hub for game systems communication"""
    
    def __init__(self):
        """Initialize the event system"""
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_queue: deque = deque()
        self._processing = False
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to an event type
        
        Args:
            event_type: Name of the event to listen for
            callback: Function to call when event is emitted
        """
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """
        Unsubscribe from an event type
        
        Args:
            event_type: Name of the event to stop listening for  
            callback: Function to remove from subscribers
        """
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
    
    def emit(self, event_type: str, event_data: Dict[str, Any]):
        """
        Emit an event to be processed
        
        Args:
            event_type: Name of the event
            event_data: Dictionary containing event information
        """
        self._event_queue.append((event_type, event_data))
    
    def process_events(self):
        """Process all queued events"""
        if self._processing:
            return  # Prevent recursive processing
            
        self._processing = True
        
        while self._event_queue:
            event_type, event_data = self._event_queue.popleft()
            
            # Call all subscribers for this event type
            for callback in self._subscribers[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    print(f"Error in event callback for {event_type}: {e}")
        
        self._processing = False
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get the number of subscribers for an event type"""
        return len(self._subscribers[event_type])
    
    def get_queue_size(self) -> int:
        """Get the number of queued events"""
        return len(self._event_queue)