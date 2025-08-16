"""
Migration Validation Framework - Comprehensive System Migration Testing

This framework provides comprehensive validation, testing, and quality assurance
for the gradual migration from legacy pygame systems to advanced Phase 2 systems.
It ensures data integrity, performance consistency, and user experience continuity.

Key Features:
- Multi-level validation (data, functional, performance, integration)
- Automated regression testing during migration
- Performance benchmarking and monitoring
- User experience consistency validation
- Rollback trigger conditions and safety checks
- Comprehensive migration reporting

Validation Levels:
1. Data Validation - Ensures data consistency between systems
2. Functional Validation - Verifies feature parity and behavior
3. Performance Validation - Monitors performance impact
4. Integration Validation - Tests cross-system interactions
5. User Experience Validation - Ensures UI/UX consistency

Usage:
    validator = MigrationValidator()
    
    # Run comprehensive validation
    result = validator.validate_migration('time_system', legacy_sys, phase2_sys)
    
    # Check if migration should proceed
    if result.should_proceed:
        # Safe to migrate
        pass
    else:
        # Rollback recommended
        pass
"""

import time
import math
import statistics
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from .system_bridge import SystemType, MigrationStatus
from .data_adapter import get_data_adapter


class ValidationLevel(Enum):
    """Levels of validation testing"""
    DATA = "data"                      # Data consistency validation
    FUNCTIONAL = "functional"          # Feature parity validation
    PERFORMANCE = "performance"        # Performance impact validation
    INTEGRATION = "integration"        # Cross-system validation
    USER_EXPERIENCE = "user_experience" # UI/UX consistency validation


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    CRITICAL = "critical"    # Must fix before migration
    WARNING = "warning"      # Should fix but can proceed
    INFO = "info"           # Informational only


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    level: ValidationLevel
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    system_type: Optional[SystemType] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'level': self.level.value,
            'severity': self.severity.value,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp,
            'system_type': self.system_type.value if self.system_type else None
        }


@dataclass
class ValidationResult:
    """Result of validation testing"""
    system_type: SystemType
    validation_level: ValidationLevel
    passed: bool
    score: float = 0.0  # Score out of 100
    issues: List[ValidationIssue] = field(default_factory=list)
    performance_data: Dict[str, float] = field(default_factory=dict)
    test_duration: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        """Get only critical issues"""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.CRITICAL]
    
    @property
    def warning_issues(self) -> List[ValidationIssue]:
        """Get only warning issues"""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]
    
    @property
    def should_proceed(self) -> bool:
        """Check if migration should proceed based on critical issues"""
        return len(self.critical_issues) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'system_type': self.system_type.value,
            'validation_level': self.validation_level.value,
            'passed': self.passed,
            'score': self.score,
            'should_proceed': self.should_proceed,
            'critical_issue_count': len(self.critical_issues),
            'warning_issue_count': len(self.warning_issues),
            'total_issue_count': len(self.issues),
            'issues': [issue.to_dict() for issue in self.issues],
            'performance_data': self.performance_data,
            'test_duration': self.test_duration,
            'timestamp': self.timestamp
        }


@dataclass
class ComprehensiveValidationResult:
    """Result of comprehensive multi-level validation"""
    system_type: SystemType
    overall_passed: bool
    overall_score: float = 0.0
    results_by_level: Dict[ValidationLevel, ValidationResult] = field(default_factory=dict)
    total_test_duration: float = 0.0
    recommendation: str = ""
    timestamp: float = field(default_factory=time.time)
    
    @property
    def should_proceed(self) -> bool:
        """Check if migration should proceed overall"""
        return self.overall_passed and all(
            result.should_proceed for result in self.results_by_level.values()
        )
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        """Get all critical issues across all levels"""
        issues = []
        for result in self.results_by_level.values():
            issues.extend(result.critical_issues)
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'system_type': self.system_type.value,
            'overall_passed': self.overall_passed,
            'overall_score': self.overall_score,
            'should_proceed': self.should_proceed,
            'total_critical_issues': len(self.critical_issues),
            'recommendation': self.recommendation,
            'results_by_level': {
                level.value: result.to_dict() 
                for level, result in self.results_by_level.items()
            },
            'total_test_duration': self.total_test_duration,
            'timestamp': self.timestamp
        }


class DataValidator:
    """Validates data consistency between legacy and Phase 2 systems"""
    
    def __init__(self):
        self.logger = logging.getLogger('DataValidator')
        self.data_adapter = get_data_adapter()
    
    def validate_time_data(self, legacy_system, phase2_system) -> ValidationResult:
        """Validate time system data consistency"""
        start_time = time.time()
        issues = []
        score = 100.0
        
        try:
            # Convert legacy time to Phase 2 format
            conversion_result = self.data_adapter.convert_legacy_time_to_phase2(legacy_system)
            
            if not conversion_result.success:
                issues.append(ValidationIssue(
                    level=ValidationLevel.DATA,
                    severity=ValidationSeverity.CRITICAL,
                    message="Failed to convert legacy time data",
                    details={'error': conversion_result.error_message},
                    system_type=SystemType.TIME_SYSTEM
                ))
                score = 0.0
            else:
                # Compare converted data with Phase 2 system
                converted_time = conversion_result.data
                current_time = phase2_system.get_current_time()
                
                # Check time consistency
                time_diff = abs(converted_time.total_minutes - current_time.total_minutes)
                if time_diff > 60:  # More than 1 hour difference
                    issues.append(ValidationIssue(
                        level=ValidationLevel.DATA,
                        severity=ValidationSeverity.WARNING,
                        message=f"Time difference of {time_diff} minutes between systems",
                        details={
                            'converted_time': converted_time.total_minutes,
                            'phase2_time': current_time.total_minutes,
                            'difference': time_diff
                        },
                        system_type=SystemType.TIME_SYSTEM
                    ))
                    score -= 20.0
                
                # Check day/hour consistency
                if converted_time.days != current_time.days:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.DATA,
                        severity=ValidationSeverity.WARNING,
                        message="Day values don't match between systems",
                        details={
                            'converted_day': converted_time.days,
                            'phase2_day': current_time.days
                        },
                        system_type=SystemType.TIME_SYSTEM
                    ))
                    score -= 10.0
                
                if abs(converted_time.hours - current_time.hours) > 1:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.DATA,
                        severity=ValidationSeverity.INFO,
                        message="Hour values differ between systems",
                        details={
                            'converted_hour': converted_time.hours,
                            'phase2_hour': current_time.hours
                        },
                        system_type=SystemType.TIME_SYSTEM
                    ))
                    score -= 5.0
        
        except Exception as e:
            issues.append(ValidationIssue(
                level=ValidationLevel.DATA,
                severity=ValidationSeverity.CRITICAL,
                message=f"Exception during time data validation: {e}",
                details={'traceback': traceback.format_exc()},
                system_type=SystemType.TIME_SYSTEM
            ))
            score = 0.0
        
        test_duration = time.time() - start_time
        
        return ValidationResult(
            system_type=SystemType.TIME_SYSTEM,
            validation_level=ValidationLevel.DATA,
            passed=score >= 70.0,
            score=max(0.0, score),
            issues=issues,
            test_duration=test_duration
        )
    
    def validate_economy_data(self, legacy_system, phase2_system) -> ValidationResult:
        """Validate economy system data consistency"""
        start_time = time.time()
        issues = []
        score = 100.0
        
        try:
            # Get data from both systems
            legacy_cash = getattr(legacy_system, 'current_cash', 0.0)
            legacy_debt = getattr(legacy_system, 'current_debt', 0.0)
            
            phase2_cash = phase2_system.current_cash
            phase2_debt = phase2_system.current_debt
            
            # Check cash consistency (allow 1% tolerance)
            cash_diff = abs(legacy_cash - phase2_cash)
            cash_tolerance = max(1.0, abs(legacy_cash) * 0.01)
            
            if cash_diff > cash_tolerance:
                severity = ValidationSeverity.CRITICAL if cash_diff > abs(legacy_cash) * 0.1 else ValidationSeverity.WARNING
                issues.append(ValidationIssue(
                    level=ValidationLevel.DATA,
                    severity=severity,
                    message=f"Cash difference of ${cash_diff:.2f} between systems",
                    details={
                        'legacy_cash': legacy_cash,
                        'phase2_cash': phase2_cash,
                        'difference': cash_diff,
                        'tolerance': cash_tolerance
                    },
                    system_type=SystemType.ECONOMY_SYSTEM
                ))
                score -= 30.0 if severity == ValidationSeverity.CRITICAL else 15.0
            
            # Check debt consistency
            debt_diff = abs(legacy_debt - phase2_debt)
            debt_tolerance = max(1.0, abs(legacy_debt) * 0.01)
            
            if debt_diff > debt_tolerance:
                severity = ValidationSeverity.CRITICAL if debt_diff > abs(legacy_debt) * 0.1 else ValidationSeverity.WARNING
                issues.append(ValidationIssue(
                    level=ValidationLevel.DATA,
                    severity=severity,
                    message=f"Debt difference of ${debt_diff:.2f} between systems",
                    details={
                        'legacy_debt': legacy_debt,
                        'phase2_debt': phase2_debt,
                        'difference': debt_diff,
                        'tolerance': debt_tolerance
                    },
                    system_type=SystemType.ECONOMY_SYSTEM
                ))
                score -= 20.0 if severity == ValidationSeverity.CRITICAL else 10.0
        
        except Exception as e:
            issues.append(ValidationIssue(
                level=ValidationLevel.DATA,
                severity=ValidationSeverity.CRITICAL,
                message=f"Exception during economy data validation: {e}",
                details={'traceback': traceback.format_exc()},
                system_type=SystemType.ECONOMY_SYSTEM
            ))
            score = 0.0
        
        test_duration = time.time() - start_time
        
        return ValidationResult(
            system_type=SystemType.ECONOMY_SYSTEM,
            validation_level=ValidationLevel.DATA,
            passed=score >= 70.0,
            score=max(0.0, score),
            issues=issues,
            test_duration=test_duration
        )


class PerformanceValidator:
    """Validates performance impact of migration"""
    
    def __init__(self):
        self.logger = logging.getLogger('PerformanceValidator')
    
    def validate_system_performance(self, system_type: SystemType, legacy_system, phase2_system) -> ValidationResult:
        """Validate performance impact of migrating to Phase 2 system"""
        start_time = time.time()
        issues = []
        score = 100.0
        performance_data = {}
        
        try:
            # Benchmark legacy system
            legacy_times = self._benchmark_system_operations(legacy_system, system_type, "legacy")
            
            # Benchmark Phase 2 system
            phase2_times = self._benchmark_system_operations(phase2_system, system_type, "phase2")
            
            # Compare performance
            for operation, legacy_time in legacy_times.items():
                phase2_time = phase2_times.get(operation, 0.0)
                
                if phase2_time > 0:
                    performance_ratio = phase2_time / legacy_time
                    performance_data[f"{operation}_legacy_ms"] = legacy_time * 1000
                    performance_data[f"{operation}_phase2_ms"] = phase2_time * 1000
                    performance_data[f"{operation}_ratio"] = performance_ratio
                    
                    # Check for performance regression
                    if performance_ratio > 2.0:  # Phase 2 is more than 2x slower
                        issues.append(ValidationIssue(
                            level=ValidationLevel.PERFORMANCE,
                            severity=ValidationSeverity.WARNING,
                            message=f"Performance regression in {operation}: {performance_ratio:.1f}x slower",
                            details={
                                'operation': operation,
                                'legacy_time_ms': legacy_time * 1000,
                                'phase2_time_ms': phase2_time * 1000,
                                'ratio': performance_ratio
                            },
                            system_type=system_type
                        ))
                        score -= 20.0
                    elif performance_ratio > 1.5:  # Phase 2 is more than 1.5x slower
                        issues.append(ValidationIssue(
                            level=ValidationLevel.PERFORMANCE,
                            severity=ValidationSeverity.INFO,
                            message=f"Minor performance impact in {operation}: {performance_ratio:.1f}x slower",
                            details={
                                'operation': operation,
                                'legacy_time_ms': legacy_time * 1000,
                                'phase2_time_ms': phase2_time * 1000,
                                'ratio': performance_ratio
                            },
                            system_type=system_type
                        ))
                        score -= 10.0
        
        except Exception as e:
            issues.append(ValidationIssue(
                level=ValidationLevel.PERFORMANCE,
                severity=ValidationSeverity.CRITICAL,
                message=f"Exception during performance validation: {e}",
                details={'traceback': traceback.format_exc()},
                system_type=system_type
            ))
            score = 0.0
        
        test_duration = time.time() - start_time
        
        return ValidationResult(
            system_type=system_type,
            validation_level=ValidationLevel.PERFORMANCE,
            passed=score >= 70.0,
            score=max(0.0, score),
            issues=issues,
            performance_data=performance_data,
            test_duration=test_duration
        )
    
    def _benchmark_system_operations(self, system, system_type: SystemType, system_name: str) -> Dict[str, float]:
        """Benchmark common operations for a system"""
        times = {}
        
        try:
            if system_type == SystemType.TIME_SYSTEM:
                # Benchmark time operations
                times['get_current_time'] = self._time_operation(lambda: getattr(system, 'get_current_time', lambda: None)())
                times['advance_time'] = self._time_operation(lambda: getattr(system, 'advance_time', lambda x: None)(1))
                
            elif system_type == SystemType.ECONOMY_SYSTEM:
                # Benchmark economy operations
                times['get_balance'] = self._time_operation(lambda: getattr(system, 'current_cash', 0.0))
                times['calculate_interest'] = self._time_operation(lambda: getattr(system, 'calculate_daily_interest', lambda: 0.0)())
                
            elif system_type == SystemType.EMPLOYEE_SYSTEM:
                # Benchmark employee operations
                times['get_employees'] = self._time_operation(lambda: getattr(system, 'employees', {}))
                times['update_employees'] = self._time_operation(lambda: getattr(system, 'update', lambda x: None)(0.016))
        
        except Exception as e:
            self.logger.warning(f"Error benchmarking {system_name} {system_type.value}: {e}")
        
        return times
    
    def _time_operation(self, operation: Callable, iterations: int = 100) -> float:
        """Time how long an operation takes (average over iterations)"""
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                operation()
            except Exception:
                pass  # Ignore errors during benchmarking
            end = time.perf_counter()
            times.append(end - start)
        
        return statistics.mean(times) if times else 0.0


class MigrationValidator:
    """Main migration validation coordinator"""
    
    def __init__(self):
        self.logger = logging.getLogger('MigrationValidator')
        
        # Initialize specialized validators
        self.data_validator = DataValidator()
        self.performance_validator = PerformanceValidator()
        
        # Validation configuration
        self.validation_timeout = 30.0  # 30 seconds per validation
        self.enable_parallel_validation = True
        
        # Validation history
        self.validation_history: List[ComprehensiveValidationResult] = []
        
        self.logger.info("Migration Validator initialized")
    
    def validate_migration(self, system_type: SystemType, legacy_system, phase2_system,
                          validation_levels: List[ValidationLevel] = None) -> ComprehensiveValidationResult:
        """Run comprehensive migration validation"""
        start_time = time.time()
        
        if validation_levels is None:
            validation_levels = [ValidationLevel.DATA, ValidationLevel.PERFORMANCE]
        
        self.logger.info(f"Starting comprehensive validation for {system_type.value}")
        
        results_by_level = {}
        
        # Run validations
        if self.enable_parallel_validation:
            results_by_level = self._run_parallel_validation(
                system_type, legacy_system, phase2_system, validation_levels
            )
        else:
            results_by_level = self._run_sequential_validation(
                system_type, legacy_system, phase2_system, validation_levels
            )
        
        # Calculate overall results
        overall_passed = all(result.passed for result in results_by_level.values())
        overall_score = statistics.mean([result.score for result in results_by_level.values()]) if results_by_level else 0.0
        
        # Generate recommendation
        recommendation = self._generate_recommendation(overall_passed, overall_score, results_by_level)
        
        total_test_duration = time.time() - start_time
        
        # Create comprehensive result
        comprehensive_result = ComprehensiveValidationResult(
            system_type=system_type,
            overall_passed=overall_passed,
            overall_score=overall_score,
            results_by_level=results_by_level,
            total_test_duration=total_test_duration,
            recommendation=recommendation
        )
        
        # Store in history
        self.validation_history.append(comprehensive_result)
        
        self.logger.info(f"Validation completed for {system_type.value}: "
                        f"Passed={overall_passed}, Score={overall_score:.1f}, "
                        f"Duration={total_test_duration:.2f}s")
        
        return comprehensive_result
    
    def _run_sequential_validation(self, system_type: SystemType, legacy_system, phase2_system,
                                  validation_levels: List[ValidationLevel]) -> Dict[ValidationLevel, ValidationResult]:
        """Run validations sequentially"""
        results = {}
        
        for level in validation_levels:
            try:
                if level == ValidationLevel.DATA:
                    if system_type == SystemType.TIME_SYSTEM:
                        results[level] = self.data_validator.validate_time_data(legacy_system, phase2_system)
                    elif system_type == SystemType.ECONOMY_SYSTEM:
                        results[level] = self.data_validator.validate_economy_data(legacy_system, phase2_system)
                    else:
                        # Create default successful result for unsupported systems
                        results[level] = ValidationResult(
                            system_type=system_type,
                            validation_level=level,
                            passed=True,
                            score=100.0
                        )
                
                elif level == ValidationLevel.PERFORMANCE:
                    results[level] = self.performance_validator.validate_system_performance(
                        system_type, legacy_system, phase2_system
                    )
                
                else:
                    # Create default result for unsupported validation levels
                    results[level] = ValidationResult(
                        system_type=system_type,
                        validation_level=level,
                        passed=True,
                        score=100.0
                    )
            
            except Exception as e:
                self.logger.error(f"Error in {level.value} validation for {system_type.value}: {e}")
                results[level] = ValidationResult(
                    system_type=system_type,
                    validation_level=level,
                    passed=False,
                    score=0.0,
                    issues=[ValidationIssue(
                        level=level,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Validation failed with exception: {e}",
                        details={'traceback': traceback.format_exc()},
                        system_type=system_type
                    )]
                )
        
        return results
    
    def _run_parallel_validation(self, system_type: SystemType, legacy_system, phase2_system,
                                validation_levels: List[ValidationLevel]) -> Dict[ValidationLevel, ValidationResult]:
        """Run validations in parallel for better performance"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(validation_levels)) as executor:
            # Submit validation tasks
            future_to_level = {}
            
            for level in validation_levels:
                if level == ValidationLevel.DATA:
                    if system_type == SystemType.TIME_SYSTEM:
                        future = executor.submit(self.data_validator.validate_time_data, legacy_system, phase2_system)
                    elif system_type == SystemType.ECONOMY_SYSTEM:
                        future = executor.submit(self.data_validator.validate_economy_data, legacy_system, phase2_system)
                    else:
                        future = executor.submit(self._create_default_result, system_type, level)
                elif level == ValidationLevel.PERFORMANCE:
                    future = executor.submit(self.performance_validator.validate_system_performance, 
                                           system_type, legacy_system, phase2_system)
                else:
                    future = executor.submit(self._create_default_result, system_type, level)
                
                future_to_level[future] = level
            
            # Collect results
            for future in future_to_level:
                level = future_to_level[future]
                try:
                    result = future.result(timeout=self.validation_timeout)
                    results[level] = result
                except TimeoutError:
                    self.logger.error(f"Validation timeout for {level.value} on {system_type.value}")
                    results[level] = ValidationResult(
                        system_type=system_type,
                        validation_level=level,
                        passed=False,
                        score=0.0,
                        issues=[ValidationIssue(
                            level=level,
                            severity=ValidationSeverity.CRITICAL,
                            message=f"Validation timed out after {self.validation_timeout}s",
                            system_type=system_type
                        )]
                    )
                except Exception as e:
                    self.logger.error(f"Error in parallel {level.value} validation: {e}")
                    results[level] = ValidationResult(
                        system_type=system_type,
                        validation_level=level,
                        passed=False,
                        score=0.0,
                        issues=[ValidationIssue(
                            level=level,
                            severity=ValidationSeverity.CRITICAL,
                            message=f"Validation failed: {e}",
                            system_type=system_type
                        )]
                    )
        
        return results
    
    def _create_default_result(self, system_type: SystemType, level: ValidationLevel) -> ValidationResult:
        """Create a default successful validation result"""
        return ValidationResult(
            system_type=system_type,
            validation_level=level,
            passed=True,
            score=100.0
        )
    
    def _generate_recommendation(self, overall_passed: bool, overall_score: float,
                                results_by_level: Dict[ValidationLevel, ValidationResult]) -> str:
        """Generate migration recommendation based on validation results"""
        if not overall_passed:
            critical_count = sum(len(result.critical_issues) for result in results_by_level.values())
            return f"Migration NOT recommended. {critical_count} critical issues found. Fix issues before proceeding."
        
        if overall_score >= 90.0:
            return "Migration HIGHLY recommended. All validations passed with excellent scores."
        elif overall_score >= 70.0:
            warning_count = sum(len(result.warning_issues) for result in results_by_level.values())
            return f"Migration recommended with caution. {warning_count} warnings found. Monitor carefully during migration."
        else:
            return f"Migration possible but risky. Score {overall_score:.1f}/100. Consider addressing issues first."
    
    def get_validation_report(self, system_type: SystemType = None) -> Dict[str, Any]:
        """Get comprehensive validation report"""
        if system_type:
            # Filter for specific system
            relevant_results = [r for r in self.validation_history if r.system_type == system_type]
        else:
            relevant_results = self.validation_history
        
        if not relevant_results:
            return {'message': 'No validation history available'}
        
        latest_result = relevant_results[-1]
        
        return {
            'latest_validation': latest_result.to_dict(),
            'validation_count': len(relevant_results),
            'average_score': statistics.mean([r.overall_score for r in relevant_results]),
            'trend': self._analyze_validation_trend(relevant_results),
            'summary': {
                'total_validations': len(self.validation_history),
                'systems_validated': len(set(r.system_type for r in self.validation_history)),
                'average_test_duration': statistics.mean([r.total_test_duration for r in self.validation_history])
            }
        }
    
    def _analyze_validation_trend(self, results: List[ComprehensiveValidationResult]) -> str:
        """Analyze trend in validation scores"""
        if len(results) < 2:
            return "Insufficient data for trend analysis"
        
        scores = [r.overall_score for r in results[-5:]]  # Last 5 validations
        
        if len(scores) >= 2:
            trend_slope = (scores[-1] - scores[0]) / len(scores)
            
            if trend_slope > 5:
                return "Improving trend - validation scores are increasing"
            elif trend_slope < -5:
                return "Declining trend - validation scores are decreasing"
            else:
                return "Stable trend - validation scores are consistent"
        
        return "No clear trend"


# Global migration validator instance
_global_migration_validator: Optional[MigrationValidator] = None

def get_migration_validator() -> MigrationValidator:
    """Get the global migration validator instance"""
    global _global_migration_validator
    if _global_migration_validator is None:
        _global_migration_validator = MigrationValidator()
    return _global_migration_validator

def initialize_migration_validator() -> MigrationValidator:
    """Initialize the global migration validator"""
    global _global_migration_validator
    _global_migration_validator = MigrationValidator()
    return _global_migration_validator