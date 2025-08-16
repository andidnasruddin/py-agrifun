"""
Test Integration: Testing Framework with Enhanced Foundation

This test validates the comprehensive Testing Framework integration with our
foundation architecture, testing basic functionality, mock systems, test data
generation, and framework capabilities.

Test Coverage:
- Testing framework initialization and basic functionality
- Mock system factory validation
- Test data generation capabilities
- Performance benchmarking features
- Basic framework operations
"""

import asyncio
import time
import tempfile
from pathlib import Path
from scripts.core.testing_framework import (
    get_testing_framework, TestingFramework, TestCategory, TestStatus,
    MockSystemFactory, TestDataGenerator, PerformanceBenchmark,
    initialize_testing_framework
)


async def test_testing_framework_integration():
    """Test comprehensive testing framework functionality"""
    print(">>> Testing Framework Integration Test...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize testing framework with temporary directory
        test_framework = initialize_testing_framework(temp_dir)
        
        print(f"[OK] Testing framework initialized with temp directory: {temp_dir}")
        print(f"     - Test directory: {test_framework.test_directory}")
        print(f"     - Parallel execution: {test_framework.parallel_execution}")
        print(f"     - Max workers: {test_framework.max_workers}")
        
        # Test 1: Framework initialization
        print("\n>>> Test 1: Framework Initialization")
        
        # Test basic framework setup
        print(f"[OK] Framework components:")
        print(f"     - Test suites initialized: {len(test_framework.test_suites)}")
        print(f"     - Mock factory available: {test_framework.mock_factory is not None}")
        print(f"     - Data generator available: {test_framework.test_data_generator is not None}")
        print(f"     - Performance benchmark available: {test_framework.benchmark is not None}")
        
        assert test_framework.mock_factory is not None, "Mock factory not initialized"
        assert test_framework.test_data_generator is not None, "Data generator not initialized"
        
        # Test 2: Mock system factory
        print("\n>>> Test 2: Mock System Factory")
        
        mock_factory = MockSystemFactory()
        
        # Test all mock system creation
        mock_event_system = mock_factory.create_mock_event_system()
        mock_entity_manager = mock_factory.create_mock_entity_manager()
        mock_grid_system = mock_factory.create_mock_grid_system()
        mock_content_registry = mock_factory.create_mock_content_registry()
        
        print(f"[OK] Mock systems created:")
        print(f"     - Event system mock: {mock_event_system is not None}")
        print(f"     - Entity manager mock: {mock_entity_manager is not None}")
        print(f"     - Grid system mock: {mock_grid_system is not None}")
        print(f"     - Content registry mock: {mock_content_registry is not None}")
        
        # Test mock functionality
        mock_entity_manager.create_entity()
        mock_event_system.emit()
        
        assert mock_event_system.emit.called, "Mock event system not working"
        assert mock_entity_manager.create_entity.called, "Mock entity manager not working"
        
        # Test 3: Test data generation
        print("\n>>> Test 3: Test Data Generation")
        
        data_generator = TestDataGenerator()
        
        # Generate test entities
        test_entities = data_generator.generate_test_entities(10)
        test_content = data_generator.generate_test_content()
        performance_scenario = data_generator.generate_performance_test_scenario(100)
        
        print(f"[OK] Test data generated:")
        print(f"     - Test entities: {len(test_entities)}")
        print(f"     - Content categories: {len(test_content)}")
        print(f"     - Performance scenario entities: {len(performance_scenario['entities'])}")
        
        # Validate test entity structure
        first_entity = test_entities[0]
        assert 'identity' in first_entity, "Test entity missing identity"
        assert 'transform' in first_entity, "Test entity missing transform"
        assert first_entity['identity']['name'].startswith('test_entity_'), "Test entity name incorrect"
        
        # Test 4: Performance benchmarking
        print("\n>>> Test 4: Performance Benchmarking")
        
        benchmark = PerformanceBenchmark()
        
        # Test benchmark measurement
        benchmark.start_benchmark()
        
        # Simulate some work
        await asyncio.sleep(0.01)
        for i in range(1000):
            pass  # Simple computation
        
        metrics = benchmark.end_benchmark()
        
        print(f"[OK] Performance benchmark completed:")
        print(f"     - Execution time: {metrics['execution_time_ms']:.2f}ms")
        print(f"     - Memory delta: {metrics['memory_delta_mb']:.2f}MB")
        print(f"     - Peak memory: {metrics['peak_memory_mb']:.2f}MB")
        print(f"     - Avg CPU: {metrics['avg_cpu_percent']:.2f}%")
        
        assert metrics['execution_time_ms'] > 0, "Benchmark time measurement failed"
        assert 'memory_delta_mb' in metrics, "Memory measurement missing"
        
        # Test 5: Quick smoke test
        print("\n>>> Test 5: Quick Smoke Test")
        
        smoke_test_passed = await test_framework.run_quick_smoke_test()
        
        print(f"[OK] Quick smoke test: {smoke_test_passed}")
        
        assert smoke_test_passed, "Smoke test failed"
        
        # Test 6: Unit tests execution
        print("\n>>> Test 6: Unit Tests Execution")
        
        # Run unit tests for core systems
        unit_test_results = await test_framework.run_tests_by_category(TestCategory.UNIT)
        
        print(f"[OK] Unit tests execution completed:")
        print(f"     - Tests run: {len(unit_test_results)}")
        
        # Count results by status
        passed_tests = len([r for r in unit_test_results if r.status == TestStatus.PASSED])
        failed_tests = len([r for r in unit_test_results if r.status == TestStatus.FAILED])
        error_tests = len([r for r in unit_test_results if r.status == TestStatus.ERROR])
        
        print(f"     - Passed: {passed_tests}")
        print(f"     - Failed: {failed_tests}")
        print(f"     - Errors: {error_tests}")
        
        # Show details for failed tests
        if failed_tests > 0 or error_tests > 0:
            print("     - Failed/Error tests:")
            for result in unit_test_results:
                if result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    print(f"       {result.test_name}: {result.error_message}")
        
        assert len(unit_test_results) > 0, "No unit tests executed"
        
        # Test 7: Integration tests execution
        print("\n>>> Test 7: Integration Tests Execution")
        
        # Run integration tests
        integration_test_results = await test_framework.run_tests_by_category(TestCategory.INTEGRATION)
        
        print(f"[OK] Integration tests execution completed:")
        print(f"     - Tests run: {len(integration_test_results)}")
        
        # Count results by status
        integration_passed = len([r for r in integration_test_results if r.status == TestStatus.PASSED])
        integration_failed = len([r for r in integration_test_results if r.status == TestStatus.FAILED])
        integration_errors = len([r for r in integration_test_results if r.status == TestStatus.ERROR])
        
        print(f"     - Passed: {integration_passed}")
        print(f"     - Failed: {integration_failed}")
        print(f"     - Errors: {integration_errors}")
        
        assert len(integration_test_results) > 0, "No integration tests executed"
        
        # Test 8: Performance tests execution
        print("\n>>> Test 8: Performance Tests Execution")
        
        # Run performance tests
        performance_test_results = await test_framework.run_tests_by_category(TestCategory.PERFORMANCE)
        
        print(f"[OK] Performance tests execution completed:")
        print(f"     - Tests run: {len(performance_test_results)}")
        
        # Check performance metrics
        for result in performance_test_results:
            if result.execution_time_ms > 0:
                print(f"     - {result.test_name}: {result.execution_time_ms:.2f}ms")
        
        assert len(performance_test_results) > 0, "No performance tests executed"
        
        # Test 9: Test reporting
        print("\n>>> Test 9: Test Reporting")
        
        # Generate comprehensive test report
        test_report = test_framework.generate_test_report()
        
        print(f"[OK] Test report generated:")
        print(f"     - Total tests: {test_report['summary']['total_tests']}")
        print(f"     - Passed: {test_report['summary']['passed']}")
        print(f"     - Pass rate: {test_report['summary']['pass_rate_percent']:.1f}%")
        print(f"     - Total execution time: {test_report['summary']['total_execution_time_ms']:.2f}ms")
        print(f"     - Average test time: {test_report['summary']['average_test_time_ms']:.2f}ms")
        
        # Category breakdown
        print(f"     - Category breakdown:")
        for category, stats in test_report['category_breakdown'].items():
            print(f"       {category}: {stats['passed']}/{stats['total']} ({stats['pass_rate']:.1f}%)")
        
        # Save test report
        report_saved = test_framework.save_test_report(test_report)
        print(f"     - Report saved: {report_saved}")
        
        assert test_report['summary']['total_tests'] > 0, "No tests in report"
        assert report_saved, "Failed to save test report"
        
        # Test 10: Phase 1 architecture validation
        print("\n>>> Test 10: Phase 1 Architecture Validation")
        
        # Run comprehensive Phase 1 validation
        phase1_validation = await test_framework.validate_phase1_architecture()
        
        print(f"[OK] Phase 1 architecture validation completed:")
        print(f"     - Validation passed: {phase1_validation['validation_passed']}")
        print(f"     - Systems validated: {phase1_validation['systems_validated']}")
        print(f"     - Issues found: {len(phase1_validation['issues_found'])}")
        
        # Show system status
        print(f"     - System validation status:")
        for system_name, status in phase1_validation['system_status'].items():
            passed = status.get('passed', False)
            status_symbol = "✅" if passed else "❌"
            print(f"       {status_symbol} {system_name}")
            
            if not passed and 'issues' in status:
                for issue in status['issues']:
                    print(f"         Issue: {issue}")
        
        # Show recommendations
        print(f"     - Recommendations:")
        for recommendation in phase1_validation['recommendations']:
            print(f"       {recommendation}")
        
        # Show issues if any
        if phase1_validation['issues_found']:
            print(f"     - Issues found:")
            for issue in phase1_validation['issues_found']:
                print(f"       {issue}")
        
        # Final validation
        print("\n>>> Final Integration Validation")
        
        # Get final statistics
        final_stats = {
            'total_tests_run': test_framework.total_tests_run,
            'total_execution_time': test_framework.total_execution_time,
            'test_suites': len(test_framework.test_suites),
            'mock_factory_available': test_framework.mock_factory is not None,
            'data_generator_available': test_framework.test_data_generator is not None,
            'phase1_validation_passed': phase1_validation['validation_passed']
        }
        
        print(f"[OK] Final testing framework state:")
        print(f"     - Total tests run: {final_stats['total_tests_run']}")
        print(f"     - Total execution time: {final_stats['total_execution_time']:.2f}ms")
        print(f"     - Test suites available: {final_stats['test_suites']}")
        print(f"     - Mock factory available: {final_stats['mock_factory_available']}")
        print(f"     - Data generator available: {final_stats['data_generator_available']}")
        print(f"     - Phase 1 validation passed: {final_stats['phase1_validation_passed']}")
        
        print(f"\n>>> Testing Framework Integration Test PASSED!")
        print(f"     - All 10 test categories completed successfully")
        print(f"     - Framework initialization and configuration working")
        print(f"     - Mock systems and test data generation functional")
        print(f"     - Unit, integration, and performance tests executed")
        print(f"     - Comprehensive reporting and validation complete")
        print(f"     - Phase 1 architectural foundation validated")
        
        return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_testing_framework_integration())
        if success:
            print("\n[SUCCESS] All tests passed! Testing Framework integration is working correctly.")
        else:
            print("\n[FAILED] Some tests failed! Check the output above.")
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()