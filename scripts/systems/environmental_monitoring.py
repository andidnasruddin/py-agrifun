"""
Environmental Monitoring - Air and Water Quality Tracking for AgriFun Agricultural Simulation

This system provides comprehensive environmental monitoring capabilities for air and water
quality tracking, regulatory compliance, and environmental impact assessment on agricultural
operations. It simulates real-world monitoring requirements and environmental stewardship.

Key Features:
- Air Quality Monitoring: PM2.5, PM10, ozone, nitrogen oxides, ammonia emissions
- Water Quality Tracking: pH, dissolved oxygen, nutrients, pesticide residues, bacteria
- Soil Health Monitoring: Organic matter, pH, nutrient levels, heavy metals, biology
- Regulatory Compliance: EPA standards, state regulations, permit requirements
- Environmental Impact Assessment: Carbon footprint, biodiversity impact, ecosystem health
- Real-Time Monitoring: Sensor networks and automated data collection
- Trend Analysis: Historical data analysis and predictive modeling
- Alert Systems: Threshold exceedance notifications and emergency response

Educational Value:
- Understanding environmental monitoring requirements and methods
- Learning about agricultural impacts on air and water quality
- Regulatory compliance and environmental stewardship principles
- Data analysis and interpretation for environmental management
- Technology applications in environmental monitoring
- Sustainable agriculture practices for environmental protection
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from enum import Enum
import logging
from datetime import datetime, timedelta
import json
import yaml
import random
import math
import statistics


class MonitoringType(Enum):
    """Types of environmental monitoring"""
    AIR_QUALITY = "air_quality"                      # Atmospheric monitoring
    SURFACE_WATER = "surface_water"                  # Streams, lakes, ponds
    GROUNDWATER = "groundwater"                      # Wells, aquifers
    SOIL_HEALTH = "soil_health"                      # Soil chemistry and biology
    NOISE_MONITORING = "noise"                       # Agricultural noise levels
    BIODIVERSITY = "biodiversity"                    # Species monitoring
    GREENHOUSE_GAS = "greenhouse_gas"                # CO2, CH4, N2O emissions


class MonitoringFrequency(Enum):
    """Monitoring frequency options"""
    CONTINUOUS = "continuous"                        # Real-time monitoring
    HOURLY = "hourly"                               # Every hour
    DAILY = "daily"                                 # Once per day
    WEEKLY = "weekly"                               # Once per week
    MONTHLY = "monthly"                             # Once per month
    SEASONAL = "seasonal"                           # Once per season
    ANNUAL = "annual"                               # Once per year
    EVENT_DRIVEN = "event_driven"                   # Based on triggers


class MonitoringStatus(Enum):
    """Status of monitoring systems"""
    ACTIVE = "active"                               # Currently monitoring
    INACTIVE = "inactive"                           # Not currently active
    MAINTENANCE = "maintenance"                     # Under maintenance
    CALIBRATION = "calibration"                     # Being calibrated
    MALFUNCTION = "malfunction"                     # Equipment malfunction
    DECOMMISSIONED = "decommissioned"              # Permanently offline


class ComplianceStatus(Enum):
    """Regulatory compliance status"""
    COMPLIANT = "compliant"                         # Meeting all standards
    NON_COMPLIANT = "non_compliant"                 # Violating standards
    PENDING_REVIEW = "pending_review"               # Under regulatory review
    CORRECTIVE_ACTION = "corrective_action"         # Action required
    EXEMPTED = "exempted"                          # Exempt from regulations


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"                                     # Minor concern
    MEDIUM = "medium"                               # Moderate concern
    HIGH = "high"                                   # Significant concern
    CRITICAL = "critical"                           # Immediate action required


@dataclass
class MonitoringParameter:
    """Individual monitoring parameter definition"""
    parameter_id: str
    parameter_name: str
    description: str
    monitoring_type: MonitoringType
    
    # Measurement details
    units: str
    measurement_method: str
    detection_limit: float
    typical_range_min: float
    typical_range_max: float
    
    # Regulatory standards
    regulatory_limit: Optional[float] = None
    regulatory_standard: str = ""
    health_advisory_level: Optional[float] = None
    
    # Quality assurance
    precision_percentage: float = 5.0               # ±5% typical precision
    accuracy_percentage: float = 10.0               # ±10% typical accuracy
    calibration_frequency_days: int = 30
    
    # Sampling requirements
    minimum_sample_size: int = 1
    sample_collection_method: str = ""
    sample_preservation_requirements: List[str] = field(default_factory=list)
    
    # Alert thresholds
    alert_threshold_low: Optional[float] = None
    alert_threshold_medium: Optional[float] = None
    alert_threshold_high: Optional[float] = None
    alert_threshold_critical: Optional[float] = None


@dataclass
class MonitoringStation:
    """Environmental monitoring station"""
    station_id: str
    station_name: str
    monitoring_types: List[MonitoringType]
    location_coordinates: Tuple[float, float]       # (latitude, longitude)
    
    # Station specifications
    installation_date: datetime
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    station_status: MonitoringStatus = MonitoringStatus.ACTIVE
    
    # Monitoring capabilities
    parameters_monitored: List[str] = field(default_factory=list)
    monitoring_frequencies: Dict[str, MonitoringFrequency] = field(default_factory=dict)
    data_storage_capacity_days: int = 365
    
    # Equipment details
    equipment_list: List[str] = field(default_factory=list)
    power_source: str = "grid"                      # grid, solar, battery
    data_transmission_method: str = "cellular"       # cellular, wifi, satellite
    
    # Quality assurance
    last_calibration_date: Optional[datetime] = None
    calibration_due_date: Optional[datetime] = None
    quality_control_checks: List[str] = field(default_factory=list)
    
    # Environmental conditions
    weather_protection: bool = True
    temperature_control: bool = False
    security_level: str = "basic"                   # basic, enhanced, high


@dataclass
class MonitoringData:
    """Individual monitoring data point"""
    measurement_id: str
    station_id: str
    parameter_id: str
    
    # Measurement details
    timestamp: datetime
    measured_value: float
    units: str
    quality_flag: str = "good"                      # good, suspect, bad, missing
    
    # Quality assurance
    measurement_method: str = ""
    operator_id: str = ""
    sample_id: Optional[str] = None
    laboratory_id: Optional[str] = None
    
    # Data validation
    validation_status: str = "pending"              # pending, validated, rejected
    validation_date: Optional[datetime] = None
    validation_notes: str = ""
    
    # Metadata
    weather_conditions: Dict[str, Any] = field(default_factory=dict)
    sampling_conditions: Dict[str, Any] = field(default_factory=dict)
    equipment_used: List[str] = field(default_factory=list)


@dataclass
class ComplianceReport:
    """Regulatory compliance report"""
    report_id: str
    report_name: str
    farm_id: str
    reporting_period_start: datetime
    reporting_period_end: datetime
    
    # Regulatory information
    regulatory_agency: str                          # EPA, state agency, etc.
    permit_number: Optional[str] = None
    regulation_citations: List[str] = field(default_factory=list)
    
    # Compliance summary
    overall_compliance_status: ComplianceStatus = ComplianceStatus.COMPLIANT
    parameters_monitored: List[str] = field(default_factory=list)
    violations_detected: List[Dict[str, Any]] = field(default_factory=list)
    corrective_actions_taken: List[str] = field(default_factory=list)
    
    # Data summary
    total_measurements: int = 0
    measurements_above_limits: int = 0
    data_completeness_percentage: float = 100.0
    quality_assurance_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Report generation
    report_generation_date: datetime = field(default_factory=datetime.now)
    report_submitted_date: Optional[datetime] = None
    agency_response_received: bool = False
    agency_response_date: Optional[datetime] = None


@dataclass
class EnvironmentalAlert:
    """Environmental monitoring alert"""
    alert_id: str
    station_id: str
    parameter_id: str
    
    # Alert details
    alert_timestamp: datetime
    alert_severity: AlertSeverity
    alert_message: str
    measured_value: float
    threshold_exceeded: float
    
    # Response tracking
    alert_acknowledged: bool = False
    acknowledgment_timestamp: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    
    # Resolution tracking
    alert_resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    resolution_actions: List[str] = field(default_factory=list)
    resolution_notes: str = ""
    
    # Escalation
    escalated: bool = False
    escalation_level: int = 0
    escalation_contacts: List[str] = field(default_factory=list)


class EnvironmentalMonitoring:
    """
    Comprehensive Environmental Monitoring system for agricultural operations
    
    This system manages environmental monitoring programs, data collection,
    compliance tracking, and alert management for sustainable agriculture.
    """
    
    def __init__(self, config_manager=None, event_system=None):
        """Initialize environmental monitoring system"""
        self.config_manager = config_manager
        self.event_system = event_system
        self.logger = logging.getLogger(__name__)
        
        # Core monitoring data
        self.monitoring_parameters: Dict[str, MonitoringParameter] = {}
        self.monitoring_stations: Dict[str, MonitoringStation] = {}
        self.monitoring_data: List[MonitoringData] = []
        self.environmental_alerts: Dict[str, EnvironmentalAlert] = {}
        
        # Compliance and reporting
        self.compliance_reports: Dict[str, ComplianceReport] = {}
        self.regulatory_standards: Dict[str, Dict[str, Any]] = {}
        self.permit_requirements: Dict[str, Dict[str, Any]] = {}
        
        # Data management
        self.data_storage_settings: Dict[str, Any] = {}
        self.data_quality_metrics: Dict[str, Dict[str, float]] = {}
        self.calibration_schedules: Dict[str, List[Dict[str, Any]]] = {}
        
        # Analysis and trends
        self.trend_analysis_results: Dict[str, Dict[str, Any]] = {}
        self.statistical_summaries: Dict[str, Dict[str, Any]] = {}
        self.environmental_indicators: Dict[str, float] = {}
        
        # Alert management
        self.active_alerts: Set[str] = set()
        self.alert_notification_settings: Dict[str, Dict[str, Any]] = {}
        self.escalation_procedures: Dict[str, List[Dict[str, Any]]] = {}
        
        # Performance tracking
        self.system_uptime_metrics: Dict[str, float] = {}
        self.data_collection_rates: Dict[str, float] = {}
        self.maintenance_schedules: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize system
        self._initialize_environmental_monitoring()
    
    def _initialize_environmental_monitoring(self):
        """Initialize environmental monitoring with parameter and station data"""
        try:
            self._load_monitoring_parameters()
            self._setup_monitoring_stations()
            self._load_regulatory_standards()
            self._initialize_alert_systems()
            
            if self.event_system:
                self._subscribe_to_events()
            
            self.logger.info("Environmental Monitoring system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing environmental monitoring: {e}")
            self._create_basic_monitoring_configuration()
    
    def _load_monitoring_parameters(self):
        """Load environmental monitoring parameter definitions"""
        
        # Air Quality Parameters
        air_quality_parameters = [
            {
                "parameter_id": "pm25",
                "parameter_name": "PM2.5 (Fine Particulate Matter)",
                "description": "Particulate matter with diameter ≤ 2.5 micrometers",
                "monitoring_type": MonitoringType.AIR_QUALITY,
                "units": "μg/m³",
                "measurement_method": "Beta attenuation",
                "detection_limit": 1.0,
                "typical_range_min": 5.0,
                "typical_range_max": 35.0,
                "regulatory_limit": 35.0,                       # EPA annual standard
                "regulatory_standard": "EPA NAAQS",
                "health_advisory_level": 12.0,
                "alert_threshold_medium": 35.0,
                "alert_threshold_high": 55.0,
                "alert_threshold_critical": 150.0
            },
            {
                "parameter_id": "pm10",
                "parameter_name": "PM10 (Coarse Particulate Matter)",
                "description": "Particulate matter with diameter ≤ 10 micrometers",
                "monitoring_type": MonitoringType.AIR_QUALITY,
                "units": "μg/m³",
                "measurement_method": "Beta attenuation",
                "detection_limit": 2.0,
                "typical_range_min": 15.0,
                "typical_range_max": 50.0,
                "regulatory_limit": 150.0,                      # EPA 24-hour standard
                "regulatory_standard": "EPA NAAQS",
                "alert_threshold_medium": 150.0,
                "alert_threshold_high": 250.0,
                "alert_threshold_critical": 350.0
            },
            {
                "parameter_id": "ozone",
                "parameter_name": "Ground-Level Ozone",
                "description": "Tropospheric ozone concentration",
                "monitoring_type": MonitoringType.AIR_QUALITY,
                "units": "ppb",
                "measurement_method": "UV photometric",
                "detection_limit": 1.0,
                "typical_range_min": 20.0,
                "typical_range_max": 70.0,
                "regulatory_limit": 70.0,                       # EPA 8-hour standard
                "regulatory_standard": "EPA NAAQS",
                "alert_threshold_medium": 70.0,
                "alert_threshold_high": 85.0,
                "alert_threshold_critical": 125.0
            },
            {
                "parameter_id": "ammonia",
                "parameter_name": "Ammonia",
                "description": "Atmospheric ammonia from agricultural activities",
                "monitoring_type": MonitoringType.AIR_QUALITY,
                "units": "ppb",
                "measurement_method": "Ion chromatography",
                "detection_limit": 0.5,
                "typical_range_min": 1.0,
                "typical_range_max": 20.0,
                "health_advisory_level": 100.0,
                "alert_threshold_medium": 50.0,
                "alert_threshold_high": 100.0,
                "alert_threshold_critical": 200.0
            }
        ]
        
        # Water Quality Parameters
        water_quality_parameters = [
            {
                "parameter_id": "water_ph",
                "parameter_name": "pH",
                "description": "Water acidity/alkalinity measurement",
                "monitoring_type": MonitoringType.SURFACE_WATER,
                "units": "pH units",
                "measurement_method": "Electrochemical",
                "detection_limit": 0.1,
                "typical_range_min": 6.5,
                "typical_range_max": 8.5,
                "regulatory_limit": None,
                "regulatory_standard": "EPA Water Quality Standards",
                "alert_threshold_low": 6.0,
                "alert_threshold_medium": 5.5,
                "alert_threshold_high": 9.0,
                "alert_threshold_critical": 4.5
            },
            {
                "parameter_id": "dissolved_oxygen",
                "parameter_name": "Dissolved Oxygen",
                "description": "Oxygen concentration in water",
                "monitoring_type": MonitoringType.SURFACE_WATER,
                "units": "mg/L",
                "measurement_method": "Electrochemical probe",
                "detection_limit": 0.1,
                "typical_range_min": 5.0,
                "typical_range_max": 12.0,
                "regulatory_limit": 5.0,                        # Minimum for aquatic life
                "regulatory_standard": "EPA Water Quality Criteria",
                "alert_threshold_low": 6.0,
                "alert_threshold_medium": 4.0,
                "alert_threshold_high": 3.0,
                "alert_threshold_critical": 2.0
            },
            {
                "parameter_id": "nitrate_nitrogen",
                "parameter_name": "Nitrate as Nitrogen",
                "description": "Nitrate nitrogen concentration in water",
                "monitoring_type": MonitoringType.GROUNDWATER,
                "units": "mg/L",
                "measurement_method": "Ion chromatography",
                "detection_limit": 0.1,
                "typical_range_min": 0.1,
                "typical_range_max": 5.0,
                "regulatory_limit": 10.0,                       # EPA MCL
                "regulatory_standard": "EPA Safe Drinking Water Act",
                "health_advisory_level": 10.0,
                "alert_threshold_medium": 10.0,
                "alert_threshold_high": 15.0,
                "alert_threshold_critical": 25.0
            },
            {
                "parameter_id": "phosphorus_total",
                "parameter_name": "Total Phosphorus",
                "description": "Total phosphorus concentration in water",
                "monitoring_type": MonitoringType.SURFACE_WATER,
                "units": "mg/L",
                "measurement_method": "Colorimetric",
                "detection_limit": 0.01,
                "typical_range_min": 0.01,
                "typical_range_max": 0.5,
                "regulatory_limit": 0.1,                        # Typical eutrophication threshold
                "regulatory_standard": "State Water Quality Standards",
                "alert_threshold_medium": 0.1,
                "alert_threshold_high": 0.3,
                "alert_threshold_critical": 1.0
            },
            {
                "parameter_id": "turbidity",
                "parameter_name": "Turbidity",
                "description": "Water clarity/suspended particle measurement",
                "monitoring_type": MonitoringType.SURFACE_WATER,
                "units": "NTU",
                "measurement_method": "Nephelometric",
                "detection_limit": 0.1,
                "typical_range_min": 1.0,
                "typical_range_max": 10.0,
                "regulatory_limit": 4.0,                        # EPA Surface Water Treatment Rule
                "regulatory_standard": "EPA Surface Water Treatment Rule",
                "alert_threshold_medium": 10.0,
                "alert_threshold_high": 25.0,
                "alert_threshold_critical": 100.0
            }
        ]
        
        # Soil Health Parameters
        soil_health_parameters = [
            {
                "parameter_id": "soil_ph",
                "parameter_name": "Soil pH",
                "description": "Soil acidity/alkalinity measurement",
                "monitoring_type": MonitoringType.SOIL_HEALTH,
                "units": "pH units",
                "measurement_method": "Electrode in soil-water slurry",
                "detection_limit": 0.1,
                "typical_range_min": 6.0,
                "typical_range_max": 7.5,
                "alert_threshold_low": 5.5,
                "alert_threshold_medium": 5.0,
                "alert_threshold_high": 4.5,
                "alert_threshold_critical": 4.0
            },
            {
                "parameter_id": "soil_organic_matter",
                "parameter_name": "Soil Organic Matter",
                "description": "Percentage of organic matter in soil",
                "monitoring_type": MonitoringType.SOIL_HEALTH,
                "units": "%",
                "measurement_method": "Loss on ignition",
                "detection_limit": 0.1,
                "typical_range_min": 2.0,
                "typical_range_max": 6.0,
                "alert_threshold_low": 2.0,
                "alert_threshold_medium": 1.5,
                "alert_threshold_high": 1.0,
                "alert_threshold_critical": 0.5
            },
            {
                "parameter_id": "soil_heavy_metals",
                "parameter_name": "Heavy Metals (Lead)",
                "description": "Lead concentration in soil",
                "monitoring_type": MonitoringType.SOIL_HEALTH,
                "units": "mg/kg",
                "measurement_method": "ICP-MS",
                "detection_limit": 1.0,
                "typical_range_min": 5.0,
                "typical_range_max": 25.0,
                "regulatory_limit": 400.0,                      # EPA screening level
                "regulatory_standard": "EPA Regional Screening Levels",
                "alert_threshold_medium": 200.0,
                "alert_threshold_high": 400.0,
                "alert_threshold_critical": 800.0
            }
        ]
        
        # Greenhouse Gas Parameters
        greenhouse_gas_parameters = [
            {
                "parameter_id": "carbon_dioxide",
                "parameter_name": "Carbon Dioxide",
                "description": "CO2 emissions from agricultural activities",
                "monitoring_type": MonitoringType.GREENHOUSE_GAS,
                "units": "ppm",
                "measurement_method": "NDIR",
                "detection_limit": 1.0,
                "typical_range_min": 400.0,
                "typical_range_max": 500.0,
                "alert_threshold_medium": 1000.0,
                "alert_threshold_high": 5000.0,
                "alert_threshold_critical": 10000.0
            },
            {
                "parameter_id": "methane",
                "parameter_name": "Methane",
                "description": "CH4 emissions from livestock and anaerobic processes",
                "monitoring_type": MonitoringType.GREENHOUSE_GAS,
                "units": "ppm",
                "measurement_method": "Gas chromatography",
                "detection_limit": 0.1,
                "typical_range_min": 2.0,
                "typical_range_max": 10.0,
                "alert_threshold_medium": 50.0,
                "alert_threshold_high": 100.0,
                "alert_threshold_critical": 500.0
            },
            {
                "parameter_id": "nitrous_oxide",
                "parameter_name": "Nitrous Oxide",
                "description": "N2O emissions from fertilizer use and soil processes",
                "monitoring_type": MonitoringType.GREENHOUSE_GAS,
                "units": "ppb",
                "measurement_method": "Gas chromatography",
                "detection_limit": 1.0,
                "typical_range_min": 300.0,
                "typical_range_max": 350.0,
                "alert_threshold_medium": 500.0,
                "alert_threshold_high": 1000.0,
                "alert_threshold_critical": 2000.0
            }
        ]
        
        # Combine all parameters
        all_parameters = (air_quality_parameters + water_quality_parameters + 
                         soil_health_parameters + greenhouse_gas_parameters)
        
        # Convert to MonitoringParameter objects
        for param_dict in all_parameters:
            # Set defaults for missing fields
            param_dict.setdefault("sample_preservation_requirements", [])
            
            parameter = MonitoringParameter(**param_dict)
            self.monitoring_parameters[parameter.parameter_id] = parameter
        
        self.logger.info(f"Loaded {len(self.monitoring_parameters)} monitoring parameters")
    
    def _setup_monitoring_stations(self):
        """Setup environmental monitoring stations"""
        station_data = [
            {
                "station_id": "air_quality_main",
                "station_name": "Main Farm Air Quality Station",
                "monitoring_types": [MonitoringType.AIR_QUALITY, MonitoringType.GREENHOUSE_GAS],
                "location_coordinates": (40.7128, -74.0060),    # Example coordinates
                "installation_date": datetime(2020, 1, 1),
                "parameters_monitored": ["pm25", "pm10", "ozone", "ammonia", "carbon_dioxide", 
                                       "methane", "nitrous_oxide"],
                "monitoring_frequencies": {
                    "pm25": MonitoringFrequency.HOURLY,
                    "pm10": MonitoringFrequency.HOURLY,
                    "ozone": MonitoringFrequency.HOURLY,
                    "ammonia": MonitoringFrequency.DAILY,
                    "carbon_dioxide": MonitoringFrequency.CONTINUOUS,
                    "methane": MonitoringFrequency.DAILY,
                    "nitrous_oxide": MonitoringFrequency.WEEKLY
                },
                "equipment_list": [
                    "PM2.5/PM10 Monitor",
                    "Ozone Analyzer",
                    "Ammonia Analyzer",
                    "CO2 Monitor",
                    "Meteorological Sensors",
                    "Data Logger"
                ],
                "power_source": "solar",
                "data_transmission_method": "cellular"
            },
            {
                "station_id": "water_quality_stream",
                "station_name": "Stream Water Quality Monitoring",
                "monitoring_types": [MonitoringType.SURFACE_WATER],
                "location_coordinates": (40.7130, -74.0050),
                "installation_date": datetime(2019, 6, 1),
                "parameters_monitored": ["water_ph", "dissolved_oxygen", "nitrate_nitrogen", 
                                       "phosphorus_total", "turbidity"],
                "monitoring_frequencies": {
                    "water_ph": MonitoringFrequency.HOURLY,
                    "dissolved_oxygen": MonitoringFrequency.HOURLY,
                    "nitrate_nitrogen": MonitoringFrequency.WEEKLY,
                    "phosphorus_total": MonitoringFrequency.WEEKLY,
                    "turbidity": MonitoringFrequency.CONTINUOUS
                },
                "equipment_list": [
                    "Multi-parameter Water Quality Probe",
                    "Turbidity Meter",
                    "Automated Sampler",
                    "Flow Meter"
                ],
                "power_source": "solar",
                "weather_protection": True
            },
            {
                "station_id": "groundwater_well",
                "station_name": "Groundwater Monitoring Well",
                "monitoring_types": [MonitoringType.GROUNDWATER],
                "location_coordinates": (40.7125, -74.0055),
                "installation_date": datetime(2018, 3, 15),
                "parameters_monitored": ["water_ph", "nitrate_nitrogen", "phosphorus_total"],
                "monitoring_frequencies": {
                    "water_ph": MonitoringFrequency.MONTHLY,
                    "nitrate_nitrogen": MonitoringFrequency.MONTHLY,
                    "phosphorus_total": MonitoringFrequency.MONTHLY
                },
                "equipment_list": [
                    "Groundwater Sampling Pump",
                    "Water Level Sensor",
                    "Sample Preservation Equipment"
                ],
                "power_source": "battery"
            },
            {
                "station_id": "soil_health_grid",
                "station_name": "Soil Health Monitoring Grid",
                "monitoring_types": [MonitoringType.SOIL_HEALTH],
                "location_coordinates": (40.7120, -74.0065),
                "installation_date": datetime(2021, 4, 1),
                "parameters_monitored": ["soil_ph", "soil_organic_matter", "soil_heavy_metals"],
                "monitoring_frequencies": {
                    "soil_ph": MonitoringFrequency.SEASONAL,
                    "soil_organic_matter": MonitoringFrequency.ANNUAL,
                    "soil_heavy_metals": MonitoringFrequency.ANNUAL
                },
                "equipment_list": [
                    "Soil Sampling Equipment",
                    "pH Meter",
                    "Sample Processing Kit"
                ],
                "power_source": "portable"
            }
        ]
        
        # Convert to MonitoringStation objects
        for station_dict in station_data:
            station_dict.setdefault("equipment_list", [])
            station_dict.setdefault("quality_control_checks", [])
            
            station = MonitoringStation(**station_dict)
            
            # Set maintenance schedules
            if station.monitoring_types:
                station.next_maintenance_date = datetime.now() + timedelta(days=90)
            
            # Set calibration schedules
            station.calibration_due_date = datetime.now() + timedelta(days=30)
            
            self.monitoring_stations[station.station_id] = station
        
        self.logger.info(f"Setup {len(self.monitoring_stations)} monitoring stations")
    
    def _load_regulatory_standards(self):
        """Load regulatory standards and compliance requirements"""
        self.regulatory_standards = {
            "epa_naaqs": {
                "agency": "Environmental Protection Agency",
                "regulation": "National Ambient Air Quality Standards",
                "parameters": {
                    "pm25": {"annual": 12.0, "24_hour": 35.0, "units": "μg/m³"},
                    "pm10": {"24_hour": 150.0, "units": "μg/m³"},
                    "ozone": {"8_hour": 70.0, "units": "ppb"}
                }
            },
            "epa_water_quality": {
                "agency": "Environmental Protection Agency",
                "regulation": "Clean Water Act",
                "parameters": {
                    "nitrate_nitrogen": {"mcl": 10.0, "units": "mg/L"},
                    "dissolved_oxygen": {"minimum": 5.0, "units": "mg/L"},
                    "turbidity": {"maximum": 4.0, "units": "NTU"}
                }
            },
            "state_soil_standards": {
                "agency": "State Environmental Agency",
                "regulation": "State Soil Quality Standards",
                "parameters": {
                    "soil_heavy_metals": {"screening_level": 400.0, "units": "mg/kg"}
                }
            }
        }
        
        # Initialize permit requirements (would be loaded from database)
        self.permit_requirements = {
            "air_emissions_permit": {
                "permit_type": "Air Quality",
                "monitoring_required": ["pm25", "pm10", "ammonia"],
                "reporting_frequency": "quarterly",
                "compliance_threshold": 0.9
            },
            "npdes_permit": {
                "permit_type": "Water Discharge",
                "monitoring_required": ["water_ph", "dissolved_oxygen", "nitrate_nitrogen"],
                "reporting_frequency": "monthly",
                "compliance_threshold": 0.95
            }
        }
    
    def _initialize_alert_systems(self):
        """Initialize environmental alert and notification systems"""
        # Set up alert notification settings
        self.alert_notification_settings = {
            "low": {
                "notification_delay_minutes": 60,
                "notification_methods": ["email"],
                "escalation_required": False
            },
            "medium": {
                "notification_delay_minutes": 15,
                "notification_methods": ["email", "sms"],
                "escalation_required": False
            },
            "high": {
                "notification_delay_minutes": 5,
                "notification_methods": ["email", "sms", "phone"],
                "escalation_required": True
            },
            "critical": {
                "notification_delay_minutes": 0,
                "notification_methods": ["email", "sms", "phone", "emergency"],
                "escalation_required": True
            }
        }
        
        # Initialize environmental indicators
        self.environmental_indicators = {
            "air_quality_index": 50.0,                     # AQI scale 0-500
            "water_quality_index": 75.0,                   # WQI scale 0-100
            "soil_health_index": 80.0,                     # SHI scale 0-100
            "overall_environmental_health": 68.3           # Composite score
        }
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        if self.event_system:
            self.event_system.subscribe('monitoring_data_collected', self.handle_monitoring_data)
            self.event_system.subscribe('alert_threshold_exceeded', self.handle_alert_threshold)
            self.event_system.subscribe('equipment_maintenance_due', self.handle_maintenance_due)
            self.event_system.subscribe('calibration_due', self.handle_calibration_due)
    
    # Core monitoring methods
    
    def collect_monitoring_data(self, station_id: str, parameter_id: str, 
                               measured_value: float, operator_id: str = "system") -> Dict[str, Any]:
        """Collect and process monitoring data"""
        try:
            if station_id not in self.monitoring_stations:
                return {"success": False, "error": "Unknown monitoring station"}
            
            if parameter_id not in self.monitoring_parameters:
                return {"success": False, "error": "Unknown monitoring parameter"}
            
            station = self.monitoring_stations[station_id]
            parameter = self.monitoring_parameters[parameter_id]
            
            # Create measurement record
            measurement_id = f"meas_{station_id}_{parameter_id}_{int(datetime.now().timestamp())}"
            
            monitoring_data = MonitoringData(
                measurement_id=measurement_id,
                station_id=station_id,
                parameter_id=parameter_id,
                timestamp=datetime.now(),
                measured_value=measured_value,
                units=parameter.units,
                operator_id=operator_id
            )
            
            # Perform data quality checks
            quality_check_result = self._perform_quality_checks(monitoring_data, parameter)
            monitoring_data.quality_flag = quality_check_result["quality_flag"]
            
            # Check for alert conditions
            alert_check = self._check_alert_thresholds(monitoring_data, parameter)
            if alert_check["alert_required"]:
                self._create_environmental_alert(monitoring_data, parameter, alert_check)
            
            # Store monitoring data
            self.monitoring_data.append(monitoring_data)
            
            # Update data quality metrics
            self._update_data_quality_metrics(station_id, parameter_id, quality_check_result)
            
            # Update environmental indicators
            self._update_environmental_indicators()
            
            # Publish data collection event
            if self.event_system:
                self.event_system.publish('monitoring_data_collected', {
                    'measurement_id': measurement_id,
                    'station_id': station_id,
                    'parameter_id': parameter_id,
                    'measured_value': measured_value,
                    'quality_flag': monitoring_data.quality_flag,
                    'alert_triggered': alert_check["alert_required"]
                })
            
            self.logger.info(f"Monitoring data collected: {parameter_id} = {measured_value} {parameter.units}")
            
            return {
                "success": True,
                "measurement_id": measurement_id,
                "monitoring_data": monitoring_data,
                "quality_check": quality_check_result,
                "alert_check": alert_check
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting monitoring data: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_compliance_report(self, farm_id: str, reporting_period_days: int = 30,
                                  regulatory_agency: str = "EPA") -> Dict[str, Any]:
        """Generate regulatory compliance report"""
        try:
            report_id = f"report_{farm_id}_{regulatory_agency}_{int(datetime.now().timestamp())}"
            
            # Define reporting period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=reporting_period_days)
            
            # Get monitoring data for period
            period_data = [
                data for data in self.monitoring_data
                if start_date <= data.timestamp <= end_date
            ]
            
            # Create compliance report
            compliance_report = ComplianceReport(
                report_id=report_id,
                report_name=f"Environmental Compliance Report - {farm_id}",
                farm_id=farm_id,
                reporting_period_start=start_date,
                reporting_period_end=end_date,
                regulatory_agency=regulatory_agency
            )
            
            # Analyze compliance for each parameter
            parameters_monitored = list(set([data.parameter_id for data in period_data]))
            compliance_report.parameters_monitored = parameters_monitored
            
            violations_detected = []
            measurements_above_limits = 0
            total_measurements = len(period_data)
            
            for parameter_id in parameters_monitored:
                if parameter_id not in self.monitoring_parameters:
                    continue
                
                parameter = self.monitoring_parameters[parameter_id]
                param_data = [data for data in period_data if data.parameter_id == parameter_id]
                
                # Check for regulatory limit exceedances
                if parameter.regulatory_limit:
                    exceedances = [
                        data for data in param_data 
                        if data.measured_value > parameter.regulatory_limit
                    ]
                    
                    measurements_above_limits += len(exceedances)
                    
                    if exceedances:
                        violation = {
                            "parameter_id": parameter_id,
                            "parameter_name": parameter.parameter_name,
                            "regulatory_limit": parameter.regulatory_limit,
                            "exceedance_count": len(exceedances),
                            "max_exceedance_value": max(e.measured_value for e in exceedances),
                            "exceedance_dates": [e.timestamp.isoformat() for e in exceedances]
                        }
                        violations_detected.append(violation)
            
            compliance_report.violations_detected = violations_detected
            compliance_report.total_measurements = total_measurements
            compliance_report.measurements_above_limits = measurements_above_limits
            
            # Calculate data completeness
            if total_measurements > 0:
                good_quality_measurements = len([
                    data for data in period_data if data.quality_flag == "good"
                ])
                compliance_report.data_completeness_percentage = (
                    good_quality_measurements / total_measurements * 100
                )
            
            # Set overall compliance status
            if violations_detected:
                compliance_report.overall_compliance_status = ComplianceStatus.NON_COMPLIANT
            else:
                compliance_report.overall_compliance_status = ComplianceStatus.COMPLIANT
            
            # Store compliance report
            self.compliance_reports[report_id] = compliance_report
            
            # Publish report generation event
            if self.event_system:
                self.event_system.publish('compliance_report_generated', {
                    'report_id': report_id,
                    'farm_id': farm_id,
                    'compliance_status': compliance_report.overall_compliance_status.value,
                    'violations_count': len(violations_detected)
                })
            
            self.logger.info(f"Compliance report generated: {report_id}")
            
            return {
                "success": True,
                "report_id": report_id,
                "compliance_report": compliance_report,
                "summary": {
                    "compliance_status": compliance_report.overall_compliance_status.value,
                    "total_measurements": total_measurements,
                    "violations_detected": len(violations_detected),
                    "data_completeness": compliance_report.data_completeness_percentage
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_environmental_trends(self, parameter_id: str, analysis_period_days: int = 365) -> Dict[str, Any]:
        """Analyze environmental trends over time"""
        try:
            if parameter_id not in self.monitoring_parameters:
                return {"success": False, "error": "Unknown monitoring parameter"}
            
            # Get data for analysis period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            parameter_data = [
                data for data in self.monitoring_data
                if (data.parameter_id == parameter_id and 
                    start_date <= data.timestamp <= end_date and
                    data.quality_flag == "good")
            ]
            
            if not parameter_data:
                return {"success": False, "error": "No data available for analysis"}
            
            # Extract values and timestamps
            values = [data.measured_value for data in parameter_data]
            timestamps = [data.timestamp for data in parameter_data]
            
            # Calculate statistical summary
            statistical_summary = {
                "parameter_id": parameter_id,
                "parameter_name": self.monitoring_parameters[parameter_id].parameter_name,
                "analysis_period_start": start_date,
                "analysis_period_end": end_date,
                "data_points": len(values),
                "minimum_value": min(values),
                "maximum_value": max(values),
                "mean_value": statistics.mean(values),
                "median_value": statistics.median(values),
                "standard_deviation": statistics.stdev(values) if len(values) > 1 else 0.0
            }
            
            # Calculate trend analysis (simple linear regression)
            trend_analysis = self._calculate_trend(timestamps, values)
            statistical_summary.update(trend_analysis)
            
            # Calculate percentiles
            if len(values) >= 10:
                sorted_values = sorted(values)
                statistical_summary["percentile_10"] = sorted_values[int(0.1 * len(sorted_values))]
                statistical_summary["percentile_90"] = sorted_values[int(0.9 * len(sorted_values))]
                statistical_summary["percentile_95"] = sorted_values[int(0.95 * len(sorted_values))]
            
            # Check regulatory compliance
            parameter = self.monitoring_parameters[parameter_id]
            if parameter.regulatory_limit:
                exceedances = len([v for v in values if v > parameter.regulatory_limit])
                statistical_summary["regulatory_exceedances"] = exceedances
                statistical_summary["compliance_percentage"] = ((len(values) - exceedances) / 
                                                               len(values) * 100)
            
            # Store trend analysis results
            self.trend_analysis_results[parameter_id] = statistical_summary
            
            return {
                "success": True,
                "parameter_id": parameter_id,
                "trend_analysis": statistical_summary
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing environmental trends for {parameter_id}: {e}")
            return {"success": False, "error": str(e)}
    
    # Helper methods
    
    def _perform_quality_checks(self, monitoring_data: MonitoringData, 
                               parameter: MonitoringParameter) -> Dict[str, Any]:
        """Perform data quality checks on monitoring data"""
        quality_check = {
            "quality_flag": "good",
            "quality_score": 100.0,
            "quality_issues": []
        }
        
        # Range check
        if not (parameter.typical_range_min <= monitoring_data.measured_value <= parameter.typical_range_max):
            if monitoring_data.measured_value < parameter.typical_range_min * 0.1:
                quality_check["quality_flag"] = "suspect"
                quality_check["quality_score"] -= 30
                quality_check["quality_issues"].append("Value below typical minimum")
            elif monitoring_data.measured_value > parameter.typical_range_max * 5:
                quality_check["quality_flag"] = "suspect"
                quality_check["quality_score"] -= 30
                quality_check["quality_issues"].append("Value above typical maximum")
        
        # Detection limit check
        if monitoring_data.measured_value < parameter.detection_limit:
            quality_check["quality_flag"] = "suspect"
            quality_check["quality_score"] -= 20
            quality_check["quality_issues"].append("Below detection limit")
        
        # Temporal consistency check (if previous data exists)
        recent_data = [
            data for data in self.monitoring_data[-10:]  # Last 10 measurements
            if (data.parameter_id == parameter.parameter_id and 
                data.quality_flag == "good")
        ]
        
        if len(recent_data) >= 3:
            recent_values = [data.measured_value for data in recent_data]
            mean_recent = statistics.mean(recent_values)
            std_recent = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
            
            if std_recent > 0 and abs(monitoring_data.measured_value - mean_recent) > 3 * std_recent:
                quality_check["quality_flag"] = "suspect"
                quality_check["quality_score"] -= 25
                quality_check["quality_issues"].append("Statistical outlier")
        
        return quality_check
    
    def _check_alert_thresholds(self, monitoring_data: MonitoringData, 
                               parameter: MonitoringParameter) -> Dict[str, Any]:
        """Check if monitoring data exceeds alert thresholds"""
        alert_check = {
            "alert_required": False,
            "alert_severity": None,
            "threshold_exceeded": None,
            "threshold_value": None
        }
        
        value = monitoring_data.measured_value
        
        # Check critical threshold
        if parameter.alert_threshold_critical and value >= parameter.alert_threshold_critical:
            alert_check["alert_required"] = True
            alert_check["alert_severity"] = AlertSeverity.CRITICAL
            alert_check["threshold_exceeded"] = "critical"
            alert_check["threshold_value"] = parameter.alert_threshold_critical
        # Check high threshold
        elif parameter.alert_threshold_high and value >= parameter.alert_threshold_high:
            alert_check["alert_required"] = True
            alert_check["alert_severity"] = AlertSeverity.HIGH
            alert_check["threshold_exceeded"] = "high"
            alert_check["threshold_value"] = parameter.alert_threshold_high
        # Check medium threshold
        elif parameter.alert_threshold_medium and value >= parameter.alert_threshold_medium:
            alert_check["alert_required"] = True
            alert_check["alert_severity"] = AlertSeverity.MEDIUM
            alert_check["threshold_exceeded"] = "medium"
            alert_check["threshold_value"] = parameter.alert_threshold_medium
        # Check low threshold (reverse logic for parameters like dissolved oxygen)
        elif parameter.alert_threshold_low and value <= parameter.alert_threshold_low:
            alert_check["alert_required"] = True
            alert_check["alert_severity"] = AlertSeverity.LOW
            alert_check["threshold_exceeded"] = "low"
            alert_check["threshold_value"] = parameter.alert_threshold_low
        
        return alert_check
    
    def _create_environmental_alert(self, monitoring_data: MonitoringData, 
                                   parameter: MonitoringParameter,
                                   alert_check: Dict[str, Any]):
        """Create environmental alert"""
        alert_id = f"alert_{monitoring_data.station_id}_{monitoring_data.parameter_id}_{int(datetime.now().timestamp())}"
        
        alert_message = (f"{parameter.parameter_name} {alert_check['threshold_exceeded']} threshold exceeded: "
                        f"{monitoring_data.measured_value} {parameter.units} "
                        f"(threshold: {alert_check['threshold_value']} {parameter.units})")
        
        environmental_alert = EnvironmentalAlert(
            alert_id=alert_id,
            station_id=monitoring_data.station_id,
            parameter_id=monitoring_data.parameter_id,
            alert_timestamp=monitoring_data.timestamp,
            alert_severity=alert_check["alert_severity"],
            alert_message=alert_message,
            measured_value=monitoring_data.measured_value,
            threshold_exceeded=alert_check["threshold_value"]
        )
        
        # Store alert
        self.environmental_alerts[alert_id] = environmental_alert
        self.active_alerts.add(alert_id)
        
        # Publish alert event
        if self.event_system:
            self.event_system.publish('environmental_alert_created', {
                'alert_id': alert_id,
                'station_id': monitoring_data.station_id,
                'parameter_id': monitoring_data.parameter_id,
                'severity': alert_check["alert_severity"].value,
                'measured_value': monitoring_data.measured_value
            })
        
        self.logger.warning(f"Environmental alert created: {alert_id}")
    
    def _calculate_trend(self, timestamps: List[datetime], values: List[float]) -> Dict[str, Any]:
        """Calculate simple linear trend from time series data"""
        if len(timestamps) < 2:
            return {"trend_slope": 0.0, "trend_direction": "insufficient_data"}
        
        # Convert timestamps to numeric (days since first measurement)
        base_time = timestamps[0]
        x_values = [(t - base_time).total_seconds() / 86400 for t in timestamps]  # Days
        
        # Calculate linear regression slope
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Slope calculation: (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x^2)
        denominator = n * sum_x2 - sum_x * sum_x
        if abs(denominator) < 1e-10:  # Avoid division by zero
            slope = 0.0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Determine trend direction
        if abs(slope) < 0.001:  # Essentially flat
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"
        
        return {
            "trend_slope": slope,
            "trend_direction": trend_direction,
            "trend_slope_units_per_day": slope
        }
    
    def _update_data_quality_metrics(self, station_id: str, parameter_id: str, 
                                    quality_check: Dict[str, Any]):
        """Update data quality metrics"""
        if station_id not in self.data_quality_metrics:
            self.data_quality_metrics[station_id] = {}
        
        if parameter_id not in self.data_quality_metrics[station_id]:
            self.data_quality_metrics[station_id][parameter_id] = {
                "total_measurements": 0,
                "good_quality_count": 0,
                "suspect_quality_count": 0,
                "bad_quality_count": 0,
                "average_quality_score": 0.0
            }
        
        metrics = self.data_quality_metrics[station_id][parameter_id]
        metrics["total_measurements"] += 1
        
        if quality_check["quality_flag"] == "good":
            metrics["good_quality_count"] += 1
        elif quality_check["quality_flag"] == "suspect":
            metrics["suspect_quality_count"] += 1
        else:
            metrics["bad_quality_count"] += 1
        
        # Update rolling average of quality scores
        current_avg = metrics["average_quality_score"]
        total_measurements = metrics["total_measurements"]
        metrics["average_quality_score"] = (
            (current_avg * (total_measurements - 1) + quality_check["quality_score"]) / 
            total_measurements
        )
    
    def _update_environmental_indicators(self):
        """Update overall environmental health indicators"""
        # This is a simplified implementation - real systems would use more sophisticated algorithms
        
        # Air Quality Index calculation (simplified)
        recent_air_data = [
            data for data in self.monitoring_data[-100:]  # Last 100 measurements
            if (data.parameter_id in ["pm25", "pm10", "ozone"] and 
                data.quality_flag == "good")
        ]
        
        if recent_air_data:
            # Simple AQI calculation (would be more complex in real implementation)
            pm25_values = [d.measured_value for d in recent_air_data if d.parameter_id == "pm25"]
            if pm25_values:
                avg_pm25 = statistics.mean(pm25_values)
                # Convert PM2.5 to AQI (simplified)
                if avg_pm25 <= 12:
                    aqi = min(50, avg_pm25 * 4.17)
                elif avg_pm25 <= 35.4:
                    aqi = 50 + (avg_pm25 - 12) * 2.13
                else:
                    aqi = min(200, 100 + (avg_pm25 - 35.4) * 2.46)
                
                self.environmental_indicators["air_quality_index"] = aqi
        
        # Water Quality Index calculation (simplified)
        recent_water_data = [
            data for data in self.monitoring_data[-50:]
            if (data.parameter_id in ["water_ph", "dissolved_oxygen", "nitrate_nitrogen"] and 
                data.quality_flag == "good")
        ]
        
        if recent_water_data:
            # Simple WQI calculation
            ph_values = [d.measured_value for d in recent_water_data if d.parameter_id == "water_ph"]
            do_values = [d.measured_value for d in recent_water_data if d.parameter_id == "dissolved_oxygen"]
            
            wqi_score = 100  # Start with perfect score
            
            if ph_values:
                avg_ph = statistics.mean(ph_values)
                if not (6.5 <= avg_ph <= 8.5):
                    wqi_score -= abs(avg_ph - 7.5) * 10
            
            if do_values:
                avg_do = statistics.mean(do_values)
                if avg_do < 5.0:
                    wqi_score -= (5.0 - avg_do) * 10
            
            self.environmental_indicators["water_quality_index"] = max(0, wqi_score)
        
        # Calculate overall environmental health
        indicators = [
            self.environmental_indicators["air_quality_index"] / 100 * 25,  # 25% weight
            self.environmental_indicators["water_quality_index"] * 0.25,    # 25% weight
            self.environmental_indicators["soil_health_index"] * 0.50       # 50% weight
        ]
        
        self.environmental_indicators["overall_environmental_health"] = sum(indicators)
    
    def _create_basic_monitoring_configuration(self):
        """Create basic monitoring configuration for fallback"""
        self.logger.warning("Creating basic monitoring configuration")
        
        # Create minimal monitoring parameter
        basic_parameter = MonitoringParameter(
            parameter_id="basic_air_quality",
            parameter_name="Basic Air Quality",
            description="Basic air quality monitoring",
            monitoring_type=MonitoringType.AIR_QUALITY,
            units="AQI",
            measurement_method="Composite",
            detection_limit=1.0,
            typical_range_min=0.0,
            typical_range_max=150.0
        )
        
        self.monitoring_parameters["basic_air_quality"] = basic_parameter


# Global convenience functions
environmental_monitoring_instance = None

def get_environmental_monitoring():
    """Get the global environmental monitoring instance"""
    global environmental_monitoring_instance
    if environmental_monitoring_instance is None:
        environmental_monitoring_instance = EnvironmentalMonitoring()
    return environmental_monitoring_instance

def collect_environmental_data(station_id: str, parameter_id: str, value: float):
    """Convenience function to collect monitoring data"""
    return get_environmental_monitoring().collect_monitoring_data(station_id, parameter_id, value)

def generate_environmental_report(farm_id: str, period_days: int = 30):
    """Convenience function to generate compliance report"""
    return get_environmental_monitoring().generate_compliance_report(farm_id, period_days)

def analyze_parameter_trends(parameter_id: str, analysis_days: int = 365):
    """Convenience function to analyze environmental trends"""
    return get_environmental_monitoring().analyze_environmental_trends(parameter_id, analysis_days)

def get_environmental_indicators():
    """Convenience function to get environmental health indicators"""
    monitoring = get_environmental_monitoring()
    return monitoring.environmental_indicators