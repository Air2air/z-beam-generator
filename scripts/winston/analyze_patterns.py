#!/usr/bin/env python3
"""
CLI Tool: Analyze Winston Feedback Patterns

This tool analyzes Winston detection results and corrections to identify
patterns, recurring issues, and effective solutions.

Usage:
    # Show overall statistics
    python3 scripts/winston/analyze_patterns.py --stats
    
    # Show most problematic AI patterns
    python3 scripts/winston/analyze_patterns.py --problematic --limit 20
    
    # Show successful corrections
    python3 scripts/winston/analyze_patterns.py --successful --limit 10
    
    # Show patterns for specific material
    python3 scripts/winston/analyze_patterns.py --material "Aluminum" --problematic
    
    # Show patterns for specific component type
    python3 scripts/winston/analyze_patterns.py --component "caption" --problematic
    
    # Full dashboard
    python3 scripts/winston/analyze_patterns.py --dashboard
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from processing.detection.winston_feedback_db import WinstonFeedbackDatabase
from processing.config.config_loader import get_config

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def show_stats(db: WinstonFeedbackDatabase) -> None:
    """Show overall database statistics."""
    stats = db.get_stats()
    
    print("\n" + "="*60)
    print("WINSTON FEEDBACK DATABASE - STATISTICS")
    print("="*60 + "\n")
    
    print(f"📊 Total Detections: {stats['total_detections']}")
    print(f"✅ Successful: {stats['successful_detections']} ({stats['success_rate']:.1f}%)")
    print(f"❌ Failed: {stats['failed_detections']} ({100-stats['success_rate']:.1f}%)")
    print(f"📝 Total Corrections: {stats['total_corrections']}")
    print(f"🔧 Approved Corrections: {stats['approved_corrections']}")
    print(f"🔍 Unique AI Patterns Detected: {stats['unique_ai_patterns']}")
    
    if stats['avg_human_score'] is not None:
        print(f"\n📈 Average Human Score: {stats['avg_human_score']:.1f}%")
        print(f"📉 Average AI Score: {100-stats['avg_human_score']:.1f}%")
    
    print("\n" + "-"*60 + "\n")


def show_problematic_patterns(
    db: WinstonFeedbackDatabase,
    limit: int = 20,
    material: Optional[str] = None,
    component_type: Optional[str] = None
) -> None:
    """Show most problematic AI patterns."""
    patterns = db.get_problematic_patterns(
        limit=limit,
        material=material,
        component_type=component_type
    )
    
    if not patterns:
        print("\n✅ No problematic patterns found!")
        return
    
    print("\n" + "="*60)
    print("MOST PROBLEMATIC AI PATTERNS")
    print("="*60 + "\n")
    
    if material:
        print(f"📌 Filtered by material: {material}\n")
    if component_type:
        print(f"📌 Filtered by component: {component_type}\n")
    
    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. Pattern: \"{pattern['pattern']}\"")
        print(f"   Occurrences: {pattern['frequency']} times")
        print(f"   Average AI score when present: {pattern['avg_ai_score']:.1f}%")
        print(f"   Category: {pattern['category']}")
        
        if pattern['context']:
            print(f"   Context: {pattern['context'][:80]}...")
        
        print()
    
    print("-"*60 + "\n")


def show_successful_corrections(
    db: WinstonFeedbackDatabase,
    limit: int = 10,
    material: Optional[str] = None,
    component_type: Optional[str] = None
) -> None:
    """Show successful corrections."""
    corrections = db.get_successful_corrections(
        limit=limit,
        material=material,
        component_type=component_type
    )
    
    if not corrections:
        print("\n📭 No approved corrections found yet.")
        return
    
    print("\n" + "="*60)
    print("SUCCESSFUL CORRECTIONS")
    print("="*60 + "\n")
    
    if material:
        print(f"📌 Filtered by material: {material}\n")
    if component_type:
        print(f"📌 Filtered by component: {component_type}\n")
    
    for i, correction in enumerate(corrections, 1):
        print(f"{i}. Material: {correction['material']} | Component: {correction['component_type']}")
        print(f"   Type: {correction['correction_type']}")
        print(f"   Improvement: {correction['original_ai_score']:.1f}% → {correction['corrected_ai_score']:.1f}% AI score")
        print(f"   ({correction['original_ai_score'] - correction['corrected_ai_score']:.1f}% reduction)")
        
        if correction['notes']:
            print(f"   Notes: {correction['notes']}")
        
        print(f"\n   Original:")
        print(f"   {correction['original_text'][:100]}...")
        print(f"\n   Corrected:")
        print(f"   {correction['corrected_text'][:100]}...")
        print()
    
    print("-"*60 + "\n")


def show_dashboard(
    db: WinstonFeedbackDatabase,
    material: Optional[str] = None,
    component_type: Optional[str] = None
) -> None:
    """Show full analysis dashboard."""
    show_stats(db)
    show_problematic_patterns(db, limit=10, material=material, component_type=component_type)
    show_successful_corrections(db, limit=5, material=material, component_type=component_type)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Winston feedback patterns and corrections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Display modes
    parser.add_argument(
        '--stats',
        action='store_true',
        help="Show overall statistics"
    )
    
    parser.add_argument(
        '--problematic',
        action='store_true',
        help="Show most problematic AI patterns"
    )
    
    parser.add_argument(
        '--successful',
        action='store_true',
        help="Show successful corrections"
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help="Show full analysis dashboard"
    )
    
    # Filters
    parser.add_argument(
        '--material',
        type=str,
        help="Filter by material name"
    )
    
    parser.add_argument(
        '--component',
        type=str,
        help="Filter by component type"
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help="Maximum results to show (default: 20)"
    )
    
    # Database
    parser.add_argument(
        '--db-path',
        type=str,
        help="Database path (default: from config.yaml)"
    )
    
    args = parser.parse_args()
    
    # Get database path
    db_path = args.db_path
    if not db_path:
        try:
            config = get_config()
            db_path = config.config.get('winston_feedback_db_path')
            if not db_path:
                logger.error("No database path in config.yaml. Use --db-path")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)
    
    # Initialize database
    try:
        db = WinstonFeedbackDatabase(db_path)
        logger.info(f"Connected to database: {db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    # Check if database has any data
    stats = db.get_stats()
    if stats['total_detections'] == 0:
        print("\n📭 Database is empty. Run some generations first!")
        sys.exit(0)
    
    # Run appropriate mode
    if args.dashboard:
        show_dashboard(db, material=args.material, component_type=args.component)
    elif args.stats:
        show_stats(db)
    elif args.problematic:
        show_problematic_patterns(
            db,
            limit=args.limit,
            material=args.material,
            component_type=args.component
        )
    elif args.successful:
        show_successful_corrections(
            db,
            limit=args.limit,
            material=args.material,
            component_type=args.component
        )
    else:
        # Default: show dashboard
        show_dashboard(db, material=args.material, component_type=args.component)


if __name__ == '__main__':
    main()
