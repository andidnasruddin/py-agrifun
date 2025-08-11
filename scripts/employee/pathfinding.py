"""
A* Pathfinding Implementation for Employee Movement

This module provides A* pathfinding algorithm for employee navigation around obstacles.
Designed to be efficient for real-time game usage with caching and optimization.

Key Features:
- Classic A* algorithm with Manhattan distance heuristic
- Obstacle detection and avoidance
- Path smoothing and optimization
- Caching for repeated path requests
- Integration with existing employee movement system

Usage:
    pathfinder = Pathfinder(grid_manager)
    path = pathfinder.find_path(start_pos, end_pos)
    if path:
        employee.set_path(path)

Performance Considerations:
- Grid size: 16x16 is small enough for real-time pathfinding
- Obstacle detection: Checks for impassable tiles and future workstations
- Path caching: Avoids recalculating identical paths
- Early termination: Returns quickly if direct path is clear

Future Enhancements:
- Hierarchical pathfinding for larger grids
- Dynamic obstacle avoidance (other employees)
- Path sharing between employees with similar routes
"""

import heapq
import math
from typing import List, Tuple, Optional, Set
from scripts.core.config import GRID_WIDTH, GRID_HEIGHT


class PathNode:
    """A node in the pathfinding graph"""
    
    def __init__(self, x: int, y: int, g_cost: float = 0, h_cost: float = 0, parent=None):
        self.x = x
        self.y = y
        self.g_cost = g_cost  # Distance from start
        self.h_cost = h_cost  # Heuristic distance to goal
        self.f_cost = g_cost + h_cost  # Total cost
        self.parent = parent
    
    def __lt__(self, other):
        """For priority queue comparison"""
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        """For node comparison"""
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        """For use in sets and dictionaries"""
        return hash((self.x, self.y))
    
    def get_position(self) -> Tuple[int, int]:
        """Get node position as tuple"""
        return (self.x, self.y)


class Pathfinder:
    """A* pathfinding implementation for employee movement"""
    
    def __init__(self, grid_manager):
        """Initialize pathfinder with grid reference"""
        self.grid_manager = grid_manager
        self.path_cache = {}  # Cache for recently calculated paths
        self.max_cache_size = 50
        
        # Movement directions (4-directional movement)
        self.directions = [
            (0, -1),  # North
            (1, 0),   # East  
            (0, 1),   # South
            (-1, 0)   # West
        ]
        
        # Optional: 8-directional movement
        # self.directions = [
        #     (0, -1), (1, -1), (1, 0), (1, 1),
        #     (0, 1), (-1, 1), (-1, 0), (-1, -1)
        # ]
        
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Find optimal path from start to goal using A* algorithm
        
        Args:
            start: Starting position (x, y)
            goal: Target position (x, y)
            
        Returns:
            List of positions representing the path, or None if no path exists
        """
        # Check cache first
        cache_key = (start, goal)
        if cache_key in self.path_cache:
            return self.path_cache[cache_key].copy()
        
        # Quick validation
        if not self._is_valid_position(goal[0], goal[1]) or self._is_obstacle(goal[0], goal[1]):
            return None
        
        if start == goal:
            return [start]
        
        # Check if direct path is clear (optimization for open areas)
        direct_path = self._get_direct_path(start, goal)
        if direct_path:
            self._cache_path(cache_key, direct_path)
            return direct_path
        
        # A* algorithm implementation
        path = self._astar_search(start, goal)
        
        if path:
            # Smooth the path to reduce unnecessary waypoints
            smoothed_path = self._smooth_path(path)
            self._cache_path(cache_key, smoothed_path)
            return smoothed_path
        
        return None
    
    def _astar_search(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Core A* algorithm implementation"""
        start_node = PathNode(start[0], start[1], 0, self._heuristic(start, goal))
        goal_node = PathNode(goal[0], goal[1])
        
        open_list = [start_node]  # Priority queue of nodes to explore
        closed_set = set()  # Positions we've already explored
        
        # Track best g_cost for each position
        g_costs = {start: 0}
        
        while open_list:
            # Get node with lowest f_cost
            current_node = heapq.heappop(open_list)
            current_pos = current_node.get_position()
            
            # Check if we reached the goal
            if current_pos == goal:
                return self._reconstruct_path(current_node)
            
            closed_set.add(current_pos)
            
            # Explore neighbors
            for neighbor_pos in self._get_neighbors(current_pos):
                if neighbor_pos in closed_set:
                    continue
                
                if self._is_obstacle(neighbor_pos[0], neighbor_pos[1]):
                    continue
                
                # Calculate costs
                movement_cost = self._get_movement_cost(current_pos, neighbor_pos)
                tentative_g_cost = current_node.g_cost + movement_cost
                
                # Check if this path to neighbor is better
                if neighbor_pos not in g_costs or tentative_g_cost < g_costs[neighbor_pos]:
                    g_costs[neighbor_pos] = tentative_g_cost
                    
                    neighbor_node = PathNode(
                        neighbor_pos[0], neighbor_pos[1],
                        tentative_g_cost,
                        self._heuristic(neighbor_pos, goal),
                        current_node
                    )
                    
                    heapq.heappush(open_list, neighbor_node)
        
        # No path found
        return None
    
    def _get_direct_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Check if a direct straight-line path is possible"""
        dx = goal[0] - start[0]
        dy = goal[1] - start[1]
        
        # Only check for perfectly straight paths (horizontal, vertical, or diagonal)
        if dx != 0 and dy != 0 and abs(dx) != abs(dy):
            return None
        
        # Generate path points
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            return [start]
        
        path = [start]
        for i in range(1, steps + 1):
            x = start[0] + (dx * i // steps)
            y = start[1] + (dy * i // steps)
            
            if self._is_obstacle(x, y):
                return None
            
            path.append((x, y))
        
        return path
    
    def _get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring positions"""
        neighbors = []
        x, y = pos
        
        for dx, dy in self.directions:
            new_x, new_y = x + dx, y + dy
            
            if self._is_valid_position(new_x, new_y):
                neighbors.append((new_x, new_y))
        
        return neighbors
    
    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is within grid bounds"""
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT
    
    def _is_obstacle(self, x: int, y: int) -> bool:
        """
        Check if position is blocked by an obstacle
        
        Future workstations will be considered obstacles here
        """
        if not self._is_valid_position(x, y):
            return True
        
        # For now, no obstacles in the basic grid
        # Future implementation will check:
        # - Workstation positions
        # - Impassable terrain
        # - Other employees (dynamic obstacles)
        
        # Example future obstacle checking:
        # tile = self.grid_manager.get_tile(x, y)
        # if tile.has_workstation():
        #     return True
        # if tile.terrain_type == 'water':
        #     return True
        
        return False
    
    def _heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Manhattan distance heuristic (good for 4-directional movement)"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _get_movement_cost(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> float:
        """Get cost of moving between adjacent positions"""
        # Basic cost is 1.0 for adjacent tiles
        # Could be modified based on terrain difficulty in future
        dx = abs(to_pos[0] - from_pos[0])
        dy = abs(to_pos[1] - from_pos[1])
        
        if dx + dy == 1:  # Orthogonal movement
            return 1.0
        elif dx == 1 and dy == 1:  # Diagonal movement
            return math.sqrt(2)  # ~1.414
        else:
            return float('inf')  # Invalid movement
    
    def _reconstruct_path(self, goal_node: PathNode) -> List[Tuple[int, int]]:
        """Reconstruct path from goal node back to start"""
        path = []
        current = goal_node
        
        while current:
            path.append(current.get_position())
            current = current.parent
        
        path.reverse()
        return path
    
    def _smooth_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Remove unnecessary waypoints from path using line-of-sight
        
        This optimization removes intermediate points when a direct line is possible
        """
        if len(path) <= 2:
            return path
        
        smoothed = [path[0]]  # Always include start point
        current_index = 0
        
        while current_index < len(path) - 1:
            # Find the farthest point we can reach directly
            farthest_index = current_index + 1
            
            for i in range(current_index + 2, len(path)):
                if self._has_line_of_sight(path[current_index], path[i]):
                    farthest_index = i
                else:
                    break
            
            smoothed.append(path[farthest_index])
            current_index = farthest_index
        
        return smoothed
    
    def _has_line_of_sight(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Check if there's a clear line of sight between two points"""
        # Simple line-of-sight check using Bresenham's line algorithm concept
        dx = abs(end[0] - start[0])
        dy = abs(end[1] - start[1])
        
        if dx == 0 and dy == 0:
            return True
        
        step_x = 1 if end[0] > start[0] else -1
        step_y = 1 if end[1] > start[1] else -1
        
        # Check all points along the line
        steps = max(dx, dy)
        for i in range(1, steps):
            check_x = start[0] + (step_x * dx * i) // steps
            check_y = start[1] + (step_y * dy * i) // steps
            
            if self._is_obstacle(check_x, check_y):
                return False
        
        return True
    
    def _cache_path(self, cache_key: Tuple, path: List[Tuple[int, int]]):
        """Cache a calculated path"""
        if len(self.path_cache) >= self.max_cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.path_cache))
            del self.path_cache[oldest_key]
        
        self.path_cache[cache_key] = path.copy()
    
    def clear_cache(self):
        """Clear the path cache (useful when obstacles change)"""
        self.path_cache.clear()
    
    def add_temporary_obstacle(self, x: int, y: int):
        """
        Add temporary obstacle (e.g., another employee)
        This will clear the cache to force recalculation
        """
        # Future implementation for dynamic obstacles
        self.clear_cache()
    
    def remove_temporary_obstacle(self, x: int, y: int):
        """Remove temporary obstacle"""
        # Future implementation for dynamic obstacles
        self.clear_cache()