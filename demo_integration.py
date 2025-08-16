"""
Phase 2 Integration Demonstration

This script demonstrates the gradual migration capabilities from legacy pygame systems
to advanced Phase 2 systems. It shows how the integration framework provides seamless
transition while maintaining game functionality.

Features Demonstrated:
- Migration infrastructure initialization
- Time system migration (legacy → Phase 2)
- Economy system migration (legacy → Phase 2)
- System health monitoring
- Migration validation and rollback
- Performance comparison

Usage:
    python demo_integration.py

Controls During Demo:
- F5: Migrate Time System
- F6: Migrate Economy System  
- F7: Show Migration Status
- F8: Rollback Time System
- F9: Show Migration Health Report
- ESC: Exit Demo
"""

import pygame
import sys
import logging
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the scripts directory to path so we can import
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from scripts.integration.integrated_game_manager import IntegratedGameManager
from scripts.integration import SystemType


def setup_demo_environment():
    """Setup demonstration environment"""
    print("=" * 60)
    print("Phase 2 Integration Demonstration")
    print("=" * 60)
    print()
    print("This demo shows the gradual migration from legacy pygame systems")
    print("to advanced Phase 2 systems with zero downtime.")
    print()
    print("Controls:")
    print("  F5  - Migrate Time System (legacy → Phase 2)")
    print("  F6  - Migrate Economy System (legacy → Phase 2)")
    print("  F7  - Show Migration Status")
    print("  F8  - Rollback Time System (Phase 2 → legacy)")
    print("  F9  - Show Migration Health Report")
    print("  ESC - Exit Demo")
    print()
    print("=" * 60)
    print()


def main():
    """Main demonstration function"""
    try:
        # Setup demo environment
        setup_demo_environment()
        
        # Initialize Pygame
        pygame.init()
        
        # Create integrated game manager
        print("🔧 Initializing Integrated Game Manager...")
        game = IntegratedGameManager()
        
        # Initialize migration infrastructure
        print("🚀 Initializing Phase 2 Migration Infrastructure...")
        migration_success = game.initialize_migration()
        
        if migration_success:
            print("✅ Migration infrastructure initialized successfully!")
            print("   - System Bridge: Active")
            print("   - Data Adapter: Ready")
            print("   - Migration Validator: Operational")
            print("   - Rollback Manager: Standby")
            print()
        else:
            print("❌ Failed to initialize migration infrastructure!")
            return
        
        # Show initial status
        print("📊 Initial System Status:")
        status = game.get_migration_status()
        local_status = status.get('local_status', {})
        
        print(f"   - Migration Enabled: {local_status.get('migration_enabled', False)}")
        print(f"   - Legacy Systems Active: {local_status.get('legacy_systems_active', 0)}")
        print(f"   - Phase 2 Systems Active: {local_status.get('phase2_systems_active', 0)}")
        print()
        
        # Demonstration of automatic time system migration
        print("⏰ Demonstrating Time System Migration...")
        print("   Starting with legacy time system...")
        
        # The integrated game manager auto-migrates time system by default
        # Check if it was migrated
        if SystemType.TIME_SYSTEM in game.migrated_systems:
            print("✅ Time system automatically migrated to Phase 2!")
            print("   - Advanced seasonal progression enabled")
            print("   - Dynamic weather simulation active")
            print("   - Agricultural calendar integration operational")
        else:
            print("⚠️  Time system still using legacy implementation")
        
        print()
        print("🎮 Starting Interactive Demo...")
        print("   Use F5-F9 keys to interact with migration system")
        print("   Game will run normally while migration occurs")
        print()
        
        # Run the integrated game
        game.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        print("\n👋 Demo completed. Thank you!")


class DemoReporter:
    """Helper class for generating demo reports"""
    
    @staticmethod
    def print_migration_status(status):
        """Print formatted migration status"""
        print("\n📊 Migration Status Report")
        print("-" * 40)
        
        local_status = status.get('local_status', {})
        print(f"Migration Enabled: {local_status.get('migration_enabled', False)}")
        print(f"Migrated Systems: {local_status.get('migrated_systems', [])}")
        print(f"Legacy Systems: {local_status.get('legacy_systems_active', 0)}")
        print(f"Phase 2 Systems: {local_status.get('phase2_systems_active', 0)}")
        
        progress = status.get('migration_progress', {})
        if progress:
            print(f"Overall Progress: {progress.get('overall_progress_percent', 0):.1f}%")
            print(f"Current Phase: {progress.get('current_phase', 'unknown')}")
        
        print("-" * 40)
    
    @staticmethod
    def print_health_report(health):
        """Print formatted health report"""
        print("\n🏥 Migration Health Report")
        print("-" * 40)
        
        print(f"Overall Status: {health.get('status', 'unknown')}")
        print(f"Health Score: {health.get('score', 0):.1f}/100")
        
        print(f"Bridge Health: {health.get('bridge_health', 0):.1f}/100")
        print(f"Validation Health: {health.get('validation_health', 0):.1f}/100")
        print(f"Rollback Health: {health.get('rollback_health', 0):.1f}/100")
        print(f"Data Integrity: {health.get('data_integrity_health', 0):.1f}/100")
        
        critical_issues = health.get('critical_issues', [])
        if critical_issues:
            print("\n⚠️  Critical Issues:")
            for issue in critical_issues:
                print(f"   - {issue}")
        
        warnings = health.get('warnings', [])
        if warnings:
            print("\n⚡ Warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        recommendations = health.get('recommendations', [])
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   - {rec}")
        
        print("-" * 40)


if __name__ == "__main__":
    main()