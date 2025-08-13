"""
Professional Dashboard System - Phase 3.1 UI Overhaul
Advanced metrics dashboard with interactive charts, KPIs, and real-time data visualization.

Features:
- Agricultural KPI tracking and visualization
- Interactive charts with trend analysis
- Customizable widget system
- Real-time data updates
- Professional styling and animations
"""

import pygame
import pygame_gui
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

# Import animation system for smooth transitions
from scripts.ui.enhanced_animation_system import AnimationManager, EasingType


class ChartType(Enum):
    """Types of charts available in the dashboard"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"


class MetricType(Enum):
    """Types of metrics tracked in the dashboard"""
    REVENUE = "revenue"
    PROFIT = "profit"
    CROP_YIELD = "crop_yield"
    EMPLOYEE_EFFICIENCY = "employee_efficiency"
    SOIL_HEALTH = "soil_health"
    MARKET_PRICE = "market_price"
    WEATHER_IMPACT = "weather_impact"
    BUILDING_UTILIZATION = "building_utilization"


@dataclass
class DataPoint:
    """Single data point for chart visualization"""
    timestamp: datetime  # When the data point was recorded
    value: float  # The numeric value
    label: str  # Human-readable label
    metadata: Dict[str, Any] = None  # Additional context data
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChartConfig:
    """Configuration for chart display and behavior"""
    chart_type: ChartType  # Type of chart to render
    title: str  # Chart title
    x_label: str  # X-axis label
    y_label: str  # Y-axis label
    color_scheme: List[Tuple[int, int, int]]  # Colors for chart elements
    show_grid: bool = True  # Whether to show grid lines
    show_legend: bool = True  # Whether to show legend
    animate_transitions: bool = True  # Whether to animate data changes
    max_data_points: int = 30  # Maximum number of data points to display
    auto_scale: bool = True  # Whether to automatically scale axes


@dataclass
class KPIMetric:
    """Key Performance Indicator metric"""
    name: str  # Metric name
    current_value: float  # Current metric value
    previous_value: float  # Previous period value for comparison
    unit: str  # Unit of measurement (e.g., "$", "%", "units")
    target_value: Optional[float] = None  # Target value for goal tracking
    trend_direction: str = "stable"  # "up", "down", "stable"
    color: Tuple[int, int, int] = (100, 150, 200)  # Display color
    
    @property
    def change_percentage(self) -> float:
        """Calculate percentage change from previous value"""
        if self.previous_value == 0:
            return 0.0
        return ((self.current_value - self.previous_value) / self.previous_value) * 100
    
    @property
    def is_improving(self) -> bool:
        """Determine if metric is improving (higher is better for most metrics)"""
        return self.current_value > self.previous_value


class InteractiveChart:
    """Interactive chart component with zoom, pan, and hover functionality"""
    
    def __init__(self, chart_config: ChartConfig, width: int, height: int):
        """Initialize interactive chart"""
        self.config = chart_config  # Chart configuration
        self.width = width  # Chart width in pixels
        self.height = height  # Chart height in pixels
        self.data_points: List[DataPoint] = []  # Chart data
        
        # Chart area calculations (leaving space for labels and legends)
        self.margin_left = 60  # Space for Y-axis labels
        self.margin_right = 20  # Right margin
        self.margin_top = 40  # Space for title
        self.margin_bottom = 60  # Space for X-axis labels
        
        # Actual chart drawing area
        self.chart_width = self.width - self.margin_left - self.margin_right
        self.chart_height = self.height - self.margin_top - self.margin_bottom
        
        # Data range tracking for scaling
        self.min_value = 0.0  # Minimum data value
        self.max_value = 100.0  # Maximum data value
        self.value_range = self.max_value - self.min_value  # Value range
        
        # Interactive state
        self.is_hovering = False  # Whether mouse is hovering over chart
        self.hover_point_index = -1  # Index of data point being hovered
        self.zoom_level = 1.0  # Current zoom level
        self.pan_offset_x = 0  # Horizontal pan offset
        
        # Animation state for smooth transitions
        self.animation_progress = 1.0  # 0.0 to 1.0, used for data transitions
        self.target_data_points: List[DataPoint] = []  # Target data for animation
    
    def add_data_point(self, data_point: DataPoint):
        """Add new data point to chart"""
        self.data_points.append(data_point)  # Add to data list
        
        # Limit number of data points to prevent performance issues
        if len(self.data_points) > self.config.max_data_points:
            self.data_points.pop(0)  # Remove oldest data point
        
        # Update data range for auto-scaling
        if self.config.auto_scale:
            self._update_data_range()
    
    def _update_data_range(self):
        """Update min/max values for chart scaling"""
        if not self.data_points:
            return
        
        # Find min and max values in current data
        values = [point.value for point in self.data_points]
        self.min_value = min(values)
        self.max_value = max(values)
        
        # Add padding to range for better visualization
        value_padding = (self.max_value - self.min_value) * 0.1
        self.min_value -= value_padding
        self.max_value += value_padding
        self.value_range = self.max_value - self.min_value
    
    def _get_chart_position(self, data_index: int, value: float) -> Tuple[int, int]:
        """Convert data point to chart pixel coordinates"""
        # Calculate X position based on data index
        if len(self.data_points) <= 1:
            x = self.margin_left + self.chart_width // 2
        else:
            x_ratio = data_index / (len(self.data_points) - 1)
            x = self.margin_left + int(x_ratio * self.chart_width)
        
        # Calculate Y position based on value (inverted because screen Y grows downward)
        if self.value_range == 0:
            y = self.margin_top + self.chart_height // 2
        else:
            y_ratio = (value - self.min_value) / self.value_range
            y = self.margin_top + self.chart_height - int(y_ratio * self.chart_height)
        
        return (x, y)
    
    def render_line_chart(self, surface: pygame.Surface):
        """Render line chart with data points and connections"""
        if len(self.data_points) < 2:
            return  # Need at least 2 points for a line
        
        # Get primary color from config
        line_color = self.config.color_scheme[0] if self.config.color_scheme else (100, 150, 200)
        point_color = (min(255, line_color[0] + 50), min(255, line_color[1] + 50), min(255, line_color[2] + 50))
        
        # Calculate all chart positions
        chart_points = []
        for i, data_point in enumerate(self.data_points):
            x, y = self._get_chart_position(i, data_point.value)
            chart_points.append((x, y))
        
        # Draw line connecting all points
        if len(chart_points) >= 2:
            pygame.draw.lines(surface, line_color, False, chart_points, 3)
        
        # Draw individual data points
        for i, (x, y) in enumerate(chart_points):
            # Highlight hovered point
            point_radius = 6 if self.hover_point_index == i else 4
            point_draw_color = (255, 255, 100) if self.hover_point_index == i else point_color
            
            pygame.draw.circle(surface, point_draw_color, (x, y), point_radius)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), point_radius, 2)
    
    def render_bar_chart(self, surface: pygame.Surface):
        """Render bar chart with vertical bars for each data point"""
        if not self.data_points:
            return
        
        # Get primary color from config
        bar_color = self.config.color_scheme[0] if self.config.color_scheme else (100, 150, 200)
        
        # Calculate bar width based on available space
        bar_width = max(10, self.chart_width // len(self.data_points) - 5)
        
        # Draw bars for each data point
        for i, data_point in enumerate(self.data_points):
            # Calculate bar position and height
            x_center = self.margin_left + int((i + 0.5) * self.chart_width / len(self.data_points))
            bar_left = x_center - bar_width // 2
            
            # Calculate bar height based on value
            if self.value_range == 0:
                bar_height = 10
            else:
                value_ratio = max(0, (data_point.value - self.min_value) / self.value_range)
                bar_height = int(value_ratio * self.chart_height)
            
            # Bar position from bottom of chart area
            bar_top = self.margin_top + self.chart_height - bar_height
            bar_rect = pygame.Rect(bar_left, bar_top, bar_width, bar_height)
            
            # Highlight hovered bar
            bar_draw_color = (255, 255, 100) if self.hover_point_index == i else bar_color
            
            # Draw bar with gradient effect
            pygame.draw.rect(surface, bar_draw_color, bar_rect)
            pygame.draw.rect(surface, (255, 255, 255), bar_rect, 2)
    
    def render_chart_axes(self, surface: pygame.Surface, font: pygame.font.Font):
        """Render chart axes, labels, and grid lines"""
        axis_color = (150, 150, 150)  # Gray color for axes
        grid_color = (200, 200, 200)  # Lighter gray for grid
        text_color = (80, 80, 80)  # Dark gray for text
        
        # Draw main axes
        # Y-axis (vertical line on left)
        pygame.draw.line(surface, axis_color, 
                        (self.margin_left, self.margin_top), 
                        (self.margin_left, self.margin_top + self.chart_height), 2)
        
        # X-axis (horizontal line on bottom)
        pygame.draw.line(surface, axis_color, 
                        (self.margin_left, self.margin_top + self.chart_height), 
                        (self.margin_left + self.chart_width, self.margin_top + self.chart_height), 2)
        
        # Draw grid lines if enabled
        if self.config.show_grid:
            # Horizontal grid lines (for Y values)
            for i in range(1, 5):  # 4 horizontal grid lines
                y = self.margin_top + int(i * self.chart_height / 5)
                pygame.draw.line(surface, grid_color, 
                               (self.margin_left, y), 
                               (self.margin_left + self.chart_width, y), 1)
            
            # Vertical grid lines (for X values)
            if len(self.data_points) > 1:
                for i in range(1, len(self.data_points)):
                    x = self.margin_left + int(i * self.chart_width / (len(self.data_points) - 1))
                    pygame.draw.line(surface, grid_color, 
                                   (x, self.margin_top), 
                                   (x, self.margin_top + self.chart_height), 1)
        
        # Draw Y-axis labels (values)
        for i in range(6):  # 6 Y-axis labels (0%, 20%, 40%, 60%, 80%, 100%)
            value = self.min_value + (i / 5) * self.value_range
            label_text = f"{value:.1f}"
            
            # Render label text
            text_surface = font.render(label_text, True, text_color)
            text_y = self.margin_top + self.chart_height - int(i * self.chart_height / 5) - text_surface.get_height() // 2
            surface.blit(text_surface, (10, text_y))
        
        # Draw chart title
        if self.config.title:
            title_surface = font.render(self.config.title, True, text_color)
            title_x = self.margin_left + (self.chart_width - title_surface.get_width()) // 2
            surface.blit(title_surface, (title_x, 10))
        
        # Draw axis labels
        if self.config.y_label:
            # Rotate Y-axis label (simulated by drawing vertically)
            y_label_surface = font.render(self.config.y_label, True, text_color)
            # Position on left side, centered vertically
            label_y = self.margin_top + (self.chart_height - y_label_surface.get_height()) // 2
            surface.blit(y_label_surface, (10, label_y))
        
        if self.config.x_label:
            x_label_surface = font.render(self.config.x_label, True, text_color)
            label_x = self.margin_left + (self.chart_width - x_label_surface.get_width()) // 2
            label_y = self.height - 20
            surface.blit(x_label_surface, (label_x, label_y))
    
    def handle_mouse_hover(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse hover for interactive features"""
        mouse_x, mouse_y = mouse_pos
        
        # Check if mouse is over chart area
        chart_rect = pygame.Rect(self.margin_left, self.margin_top, self.chart_width, self.chart_height)
        self.is_hovering = chart_rect.collidepoint(mouse_x, mouse_y)
        
        if not self.is_hovering:
            self.hover_point_index = -1
            return False
        
        # Find closest data point to mouse position
        if self.data_points:
            closest_distance = float('inf')
            closest_index = -1
            
            for i, data_point in enumerate(self.data_points):
                point_x, point_y = self._get_chart_position(i, data_point.value)
                distance = math.sqrt((mouse_x - point_x) ** 2 + (mouse_y - point_y) ** 2)
                
                if distance < closest_distance and distance < 20:  # 20px hover radius
                    closest_distance = distance
                    closest_index = i
            
            self.hover_point_index = closest_index
            return closest_index >= 0
        
        return False
    
    def render(self, surface: pygame.Surface, font: pygame.font.Font):
        """Render complete chart with all elements"""
        # Clear chart area with background
        chart_bg = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(surface, (250, 250, 250), chart_bg)
        pygame.draw.rect(surface, (200, 200, 200), chart_bg, 2)
        
        # Render axes and grid first (background elements)
        self.render_chart_axes(surface, font)
        
        # Render chart data based on type
        if self.config.chart_type == ChartType.LINE:
            self.render_line_chart(surface)
        elif self.config.chart_type == ChartType.BAR:
            self.render_bar_chart(surface)
        # Additional chart types can be implemented here
        
        # Render hover tooltip if hovering over data point
        if self.is_hovering and 0 <= self.hover_point_index < len(self.data_points):
            self._render_hover_tooltip(surface, font)
    
    def _render_hover_tooltip(self, surface: pygame.Surface, font: pygame.font.Font):
        """Render tooltip when hovering over data point"""
        data_point = self.data_points[self.hover_point_index]
        
        # Create tooltip text
        tooltip_lines = [
            data_point.label,
            f"Value: {data_point.value:.2f}",
            f"Time: {data_point.timestamp.strftime('%H:%M')}"
        ]
        
        # Calculate tooltip size
        line_height = font.get_height() + 2
        tooltip_width = max(font.size(line)[0] for line in tooltip_lines) + 20
        tooltip_height = len(tooltip_lines) * line_height + 10
        
        # Position tooltip near mouse, but keep it within chart bounds
        point_x, point_y = self._get_chart_position(self.hover_point_index, data_point.value)
        tooltip_x = min(point_x + 15, self.width - tooltip_width - 10)
        tooltip_y = max(10, point_y - tooltip_height - 15)
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(surface, (255, 255, 220), tooltip_rect)
        pygame.draw.rect(surface, (100, 100, 100), tooltip_rect, 2)
        
        # Draw tooltip text
        for i, line in enumerate(tooltip_lines):
            text_surface = font.render(line, True, (50, 50, 50))
            text_y = tooltip_y + 5 + i * line_height
            surface.blit(text_surface, (tooltip_x + 10, text_y))


class KPIWidget:
    """Key Performance Indicator display widget"""
    
    def __init__(self, kpi_metric: KPIMetric, width: int, height: int):
        """Initialize KPI widget"""
        self.kpi = kpi_metric  # KPI metric data
        self.width = width  # Widget width
        self.height = height  # Widget height
        
        # Animation state for value changes
        self.animated_value = kpi_metric.current_value  # Current animated display value
        self.target_value = kpi_metric.current_value  # Target value for animation
        self.animation_speed = 2.0  # Animation speed multiplier
    
    def update_kpi(self, new_kpi: KPIMetric):
        """Update KPI with new data and trigger animation"""
        self.target_value = new_kpi.current_value  # Set animation target
        self.kpi = new_kpi  # Update KPI data
    
    def update_animation(self, dt: float):
        """Update value animation"""
        # Smoothly animate towards target value
        value_difference = self.target_value - self.animated_value
        if abs(value_difference) > 0.01:  # Only animate if difference is significant
            self.animated_value += value_difference * self.animation_speed * dt
        else:
            self.animated_value = self.target_value  # Snap to target when close
    
    def render(self, surface: pygame.Surface, font: pygame.font.Font, title_font: pygame.font.Font):
        """Render KPI widget with value, trend, and styling"""
        # Widget background
        widget_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(surface, (245, 245, 245), widget_rect)
        pygame.draw.rect(surface, self.kpi.color, widget_rect, 3)
        
        # Render KPI name/title
        title_surface = title_font.render(self.kpi.name, True, (60, 60, 60))
        title_x = (self.width - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, 10))
        
        # Render current value with unit
        value_text = f"{self.animated_value:.1f}{self.kpi.unit}"
        value_surface = font.render(value_text, True, (30, 30, 30))
        value_x = (self.width - value_surface.get_width()) // 2
        surface.blit(value_surface, (value_x, 40))
        
        # Render trend indicator
        change_pct = self.kpi.change_percentage
        if abs(change_pct) > 0.1:  # Only show trend if change is significant
            trend_text = f"{change_pct:+.1f}%"
            trend_color = (50, 150, 50) if self.kpi.is_improving else (150, 50, 50)
            trend_surface = font.render(trend_text, True, trend_color)
            trend_x = (self.width - trend_surface.get_width()) // 2
            surface.blit(trend_surface, (trend_x, 70))
            
            # Draw trend arrow
            arrow_y = 85
            arrow_center_x = self.width // 2
            if self.kpi.is_improving:
                # Up arrow
                pygame.draw.polygon(surface, trend_color, [
                    (arrow_center_x, arrow_y),
                    (arrow_center_x - 8, arrow_y + 10),
                    (arrow_center_x + 8, arrow_y + 10)
                ])
            else:
                # Down arrow
                pygame.draw.polygon(surface, trend_color, [
                    (arrow_center_x - 8, arrow_y),
                    (arrow_center_x + 8, arrow_y),
                    (arrow_center_x, arrow_y + 10)
                ])
        
        # Render target progress if target is set
        if self.kpi.target_value is not None:
            progress = min(1.0, self.animated_value / self.kpi.target_value) if self.kpi.target_value > 0 else 0
            
            # Progress bar
            bar_width = self.width - 20
            bar_height = 8
            bar_x = 10
            bar_y = self.height - 20
            
            # Progress bar background
            bar_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(surface, (200, 200, 200), bar_bg_rect)
            
            # Progress bar fill
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
                progress_color = (50, 150, 50) if progress >= 1.0 else (100, 150, 200)
                pygame.draw.rect(surface, progress_color, fill_rect)


class DashboardManager:
    """Main dashboard manager coordinating all dashboard components"""
    
    def __init__(self, event_system, screen_width: int, screen_height: int):
        """Initialize dashboard manager"""
        self.event_system = event_system  # Event system for communication
        self.screen_width = screen_width  # Display screen width
        self.screen_height = screen_height  # Display screen height
        
        # Dashboard state
        self.is_visible = False  # Whether dashboard is currently shown
        self.dashboard_surface = None  # Surface for rendering dashboard
        
        # Initialize fonts for text rendering
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)  # Main font
        self.title_font = pygame.font.Font(None, 32)  # Title font
        self.large_font = pygame.font.Font(None, 28)  # Large text font
        
        # Dashboard layout configuration
        self.dashboard_width = screen_width - 100  # Dashboard width (with margins)
        self.dashboard_height = screen_height - 100  # Dashboard height (with margins)
        self.dashboard_x = 50  # Dashboard X position
        self.dashboard_y = 50  # Dashboard Y position
        
        # Initialize dashboard components
        self.charts: Dict[str, InteractiveChart] = {}  # Chart instances by name
        self.kpi_widgets: Dict[str, KPIWidget] = {}  # KPI widget instances by name
        
        # Create default charts and KPIs
        self._create_default_dashboard_components()
        
        # Register for relevant events
        self.event_system.subscribe('money_changed', self._handle_money_update)
        self.event_system.subscribe('crop_harvested', self._handle_crop_harvest)
        self.event_system.subscribe('employee_performance_update', self._handle_employee_update)
        self.event_system.subscribe('market_price_update', self._handle_market_update)
        self.event_system.subscribe('weather_changed', self._handle_weather_update)
        
        # Data tracking for metrics
        self.daily_revenue_data: List[DataPoint] = []  # Revenue over time
        self.crop_yield_data: List[DataPoint] = []  # Crop yields over time
        self.employee_efficiency_data: List[DataPoint] = []  # Employee performance over time
        self.market_price_data: List[DataPoint] = []  # Market prices over time
    
    def _create_default_dashboard_components(self):
        """Create default charts and KPI widgets for the dashboard"""
        # Revenue chart configuration
        revenue_config = ChartConfig(
            chart_type=ChartType.LINE,
            title="Daily Revenue Trend",
            x_label="Time",
            y_label="Revenue ($)",
            color_scheme=[(50, 150, 50), (100, 200, 100)],  # Green theme
            show_grid=True,
            show_legend=True,
            max_data_points=14  # Show 2 weeks of data
        )
        
        # Create revenue chart
        chart_width = 400
        chart_height = 250
        self.charts["revenue"] = InteractiveChart(revenue_config, chart_width, chart_height)
        
        # Market price chart configuration
        market_config = ChartConfig(
            chart_type=ChartType.LINE,
            title="Market Price History",
            x_label="Time",
            y_label="Price ($)",
            color_scheme=[(150, 100, 50), (200, 150, 100)],  # Orange theme
            show_grid=True,
            max_data_points=30  # Show 30 days of price data
        )
        
        # Create market price chart
        self.charts["market_price"] = InteractiveChart(market_config, chart_width, chart_height)
        
        # Crop yield chart (bar chart)
        yield_config = ChartConfig(
            chart_type=ChartType.BAR,
            title="Crop Yield by Type",
            x_label="Crop Type",
            y_label="Yield (units)",
            color_scheme=[(100, 150, 200), (150, 200, 250)],  # Blue theme
            show_grid=True,
            max_data_points=10
        )
        
        # Create crop yield chart
        self.charts["crop_yield"] = InteractiveChart(yield_config, chart_width, chart_height)
        
        # Create KPI widgets
        self._create_kpi_widgets()
    
    def _create_kpi_widgets(self):
        """Create KPI widgets for key metrics"""
        # Total Revenue KPI
        revenue_kpi = KPIMetric(
            name="Total Revenue",
            current_value=0.0,
            previous_value=0.0,
            unit="$",
            target_value=10000.0,  # $10K revenue target
            color=(50, 150, 50)  # Green
        )
        self.kpi_widgets["revenue"] = KPIWidget(revenue_kpi, 180, 120)
        
        # Daily Profit KPI
        profit_kpi = KPIMetric(
            name="Daily Profit",
            current_value=0.0,
            previous_value=0.0,
            unit="$",
            target_value=500.0,  # $500 daily profit target
            color=(100, 150, 200)  # Blue
        )
        self.kpi_widgets["profit"] = KPIWidget(profit_kpi, 180, 120)
        
        # Employee Efficiency KPI
        efficiency_kpi = KPIMetric(
            name="Avg Efficiency",
            current_value=85.0,
            previous_value=82.0,
            unit="%",
            target_value=95.0,  # 95% efficiency target
            color=(150, 100, 200)  # Purple
        )
        self.kpi_widgets["efficiency"] = KPIWidget(efficiency_kpi, 180, 120)
        
        # Soil Health KPI
        soil_kpi = KPIMetric(
            name="Soil Health",
            current_value=75.0,
            previous_value=72.0,
            unit="%",
            target_value=90.0,  # 90% soil health target
            color=(150, 150, 50)  # Yellow-green
        )
        self.kpi_widgets["soil_health"] = KPIWidget(soil_kpi, 180, 120)
    
    def toggle_dashboard(self):
        """Toggle dashboard visibility"""
        self.is_visible = not self.is_visible
        
        # Create dashboard surface if showing for first time
        if self.is_visible and self.dashboard_surface is None:
            self.dashboard_surface = pygame.Surface((self.dashboard_width, self.dashboard_height))
        
        # Trigger event for UI state change
        self.event_system.publish('dashboard_toggled', {'visible': self.is_visible})
    
    def show_dashboard(self):
        """Show the dashboard"""
        self.is_visible = True
        if self.dashboard_surface is None:
            self.dashboard_surface = pygame.Surface((self.dashboard_width, self.dashboard_height))
    
    def hide_dashboard(self):
        """Hide the dashboard"""
        self.is_visible = False
    
    def handle_mouse_event(self, event):
        """Handle mouse events for dashboard interaction"""
        if not self.is_visible:
            return False
        
        # Convert screen coordinates to dashboard coordinates
        mouse_x = event.pos[0] - self.dashboard_x
        mouse_y = event.pos[1] - self.dashboard_y
        
        # Check if mouse is within dashboard area
        if 0 <= mouse_x <= self.dashboard_width and 0 <= mouse_y <= self.dashboard_height:
            # Handle chart interactions
            self._handle_chart_mouse_events((mouse_x, mouse_y), event)
            return True  # Event handled by dashboard
        
        return False  # Event not handled
    
    def _handle_chart_mouse_events(self, mouse_pos: Tuple[int, int], event):
        """Handle mouse events for chart interactions"""
        mouse_x, mouse_y = mouse_pos
        
        # Chart layout positions (2x2 grid)
        chart_positions = [
            (20, 150),    # Revenue chart (top-left)
            (440, 150),   # Market price chart (top-right)
            (20, 420),    # Crop yield chart (bottom-left)
            (440, 420),   # Employee efficiency chart (bottom-right)
        ]
        
        chart_names = ["revenue", "market_price", "crop_yield", "efficiency"]
        
        # Check each chart for mouse interaction
        for i, (chart_x, chart_y) in enumerate(chart_positions):
            if i < len(chart_names) and chart_names[i] in self.charts:
                chart = self.charts[chart_names[i]]
                
                # Check if mouse is over this chart
                chart_mouse_x = mouse_x - chart_x
                chart_mouse_y = mouse_y - chart_y
                
                if 0 <= chart_mouse_x <= chart.width and 0 <= chart_mouse_y <= chart.height:
                    # Handle hover events
                    if event.type == pygame.MOUSEMOTION:
                        chart.handle_mouse_hover((chart_mouse_x, chart_mouse_y))
    
    def update(self, dt: float):
        """Update dashboard animations and data"""
        if not self.is_visible:
            return
        
        # Update KPI widget animations
        for widget in self.kpi_widgets.values():
            widget.update_animation(dt)
        
        # Update chart animations (if implemented)
        for chart in self.charts.values():
            if hasattr(chart, 'update_animation'):
                chart.update_animation(dt)
    
    def render(self, screen: pygame.Surface):
        """Render the complete dashboard"""
        if not self.is_visible or self.dashboard_surface is None:
            return
        
        # Clear dashboard surface
        self.dashboard_surface.fill((240, 240, 240))  # Light gray background
        
        # Draw dashboard border
        dashboard_rect = pygame.Rect(0, 0, self.dashboard_width, self.dashboard_height)
        pygame.draw.rect(self.dashboard_surface, (200, 200, 200), dashboard_rect, 4)
        
        # Render dashboard title
        title_text = "Farm Analytics Dashboard"
        title_surface = self.large_font.render(title_text, True, (50, 50, 50))
        title_x = (self.dashboard_width - title_surface.get_width()) // 2
        self.dashboard_surface.blit(title_surface, (title_x, 20))
        
        # Render KPI widgets (top row)
        kpi_y = 60
        kpi_x_positions = [20, 220, 420, 620]  # Horizontal positions for 4 KPIs
        kpi_names = ["revenue", "profit", "efficiency", "soil_health"]
        
        for i, kpi_name in enumerate(kpi_names):
            if kpi_name in self.kpi_widgets and i < len(kpi_x_positions):
                widget = self.kpi_widgets[kpi_name]
                
                # Create temporary surface for widget
                widget_surface = pygame.Surface((widget.width, widget.height))
                widget.render(widget_surface, self.font, self.title_font)
                
                # Blit widget to dashboard
                self.dashboard_surface.blit(widget_surface, (kpi_x_positions[i], kpi_y))
        
        # Render charts (2x2 grid below KPIs)
        chart_positions = [
            (20, 200),    # Revenue chart (top-left)
            (440, 200),   # Market price chart (top-right)
            (20, 470),    # Crop yield chart (bottom-left)
            (440, 470),   # Employee efficiency chart (bottom-right)
        ]
        
        chart_names = ["revenue", "market_price", "crop_yield", "efficiency"]
        
        for i, (chart_x, chart_y) in enumerate(chart_positions):
            if i < len(chart_names) and chart_names[i] in self.charts:
                chart = self.charts[chart_names[i]]
                
                # Create temporary surface for chart
                chart_surface = pygame.Surface((chart.width, chart.height))
                chart.render(chart_surface, self.font)
                
                # Blit chart to dashboard
                self.dashboard_surface.blit(chart_surface, (chart_x, chart_y))
        
        # Render dashboard to main screen
        screen.blit(self.dashboard_surface, (self.dashboard_x, self.dashboard_y))
    
    # Event handlers for updating dashboard data
    def _handle_money_update(self, event_data):
        """Handle money changes for revenue tracking"""
        current_money = event_data.get('current_money', 0)
        change = event_data.get('change', 0)
        
        if change > 0:  # Only track positive changes as revenue
            # Add revenue data point
            revenue_point = DataPoint(
                timestamp=datetime.now(),
                value=change,
                label=f"Revenue: ${change:.2f}"
            )
            
            if "revenue" in self.charts:
                self.charts["revenue"].add_data_point(revenue_point)
            
            # Update revenue KPI
            if "revenue" in self.kpi_widgets:
                current_kpi = self.kpi_widgets["revenue"].kpi
                new_kpi = KPIMetric(
                    name=current_kpi.name,
                    current_value=current_kpi.current_value + change,
                    previous_value=current_kpi.current_value,
                    unit=current_kpi.unit,
                    target_value=current_kpi.target_value,
                    color=current_kpi.color
                )
                self.kpi_widgets["revenue"].update_kpi(new_kpi)
    
    def _handle_crop_harvest(self, event_data):
        """Handle crop harvest events for yield tracking"""
        crop_type = event_data.get('crop_type', 'Unknown')
        quantity = event_data.get('quantity', 0)
        
        # Add crop yield data point
        yield_point = DataPoint(
            timestamp=datetime.now(),
            value=quantity,
            label=f"{crop_type}: {quantity} units"
        )
        
        if "crop_yield" in self.charts:
            self.charts["crop_yield"].add_data_point(yield_point)
    
    def _handle_employee_update(self, event_data):
        """Handle employee performance updates"""
        efficiency = event_data.get('average_efficiency', 0)
        
        # Update efficiency KPI
        if "efficiency" in self.kpi_widgets:
            current_kpi = self.kpi_widgets["efficiency"].kpi
            new_kpi = KPIMetric(
                name=current_kpi.name,
                current_value=efficiency,
                previous_value=current_kpi.current_value,
                unit=current_kpi.unit,
                target_value=current_kpi.target_value,
                color=current_kpi.color
            )
            self.kpi_widgets["efficiency"].update_kpi(new_kpi)
    
    def _handle_market_update(self, event_data):
        """Handle market price updates"""
        price = event_data.get('current_price', 0)
        crop_type = event_data.get('crop_type', 'Corn')
        
        # Add market price data point
        price_point = DataPoint(
            timestamp=datetime.now(),
            value=price,
            label=f"{crop_type}: ${price:.2f}"
        )
        
        if "market_price" in self.charts:
            self.charts["market_price"].add_data_point(price_point)
    
    def _handle_weather_update(self, event_data):
        """Handle weather changes for impact tracking"""
        # This could be expanded to track weather impact on farming
        pass