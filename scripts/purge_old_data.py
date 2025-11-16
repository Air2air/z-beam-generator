#!/usr/bin/env python3
"""
Purge Old Contaminated Data
============================

Removes data from before the dynamic penalties fix (Nov 15, 2025).
This data contains 95% bad examples with hardcoded 0.0 penalties.
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

def purge_old_data(db_path: str, before_date: str, dry_run: bool = False):
    """
    Purge detection results before a specific date.
    
    Args:
        db_path: Path to winston_feedback.db
        before_date: ISO date string (e.g., '2025-11-15')
        dry_run: If True, show what would be deleted without actually deleting
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Purging data before {before_date}...")
    print()
    
    # Count what will be deleted
    cursor.execute('SELECT COUNT(*) FROM detection_results WHERE timestamp < ?', (before_date,))
    detection_count = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM sentence_analysis 
        WHERE detection_result_id IN (
            SELECT id FROM detection_results WHERE timestamp < ?
        )
    ''', (before_date,))
    sentence_count = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM ai_patterns 
        WHERE detection_result_id IN (
            SELECT id FROM detection_results WHERE timestamp < ?
        )
    ''', (before_date,))
    pattern_count = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM generation_parameters 
        WHERE detection_result_id IN (
            SELECT id FROM detection_results WHERE timestamp < ?
        )
    ''', (before_date,))
    param_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM subjective_evaluations WHERE timestamp < ?', (before_date,))
    claude_count = cursor.fetchone()[0]
    
    print(f"📊 Records to be deleted:")
    print(f"  - Detection Results: {detection_count}")
    print(f"  - Sentence Analyses: {sentence_count}")
    print(f"  - AI Patterns: {pattern_count}")
    print(f"  - Generation Parameters: {param_count}")
    print(f"  - Subjective Evaluations: {claude_count}")
    print()
    
    if detection_count == 0:
        print("✅ No records to delete")
        conn.close()
        return
    
    if dry_run:
        print("🔍 DRY RUN - No data will be deleted")
        print("   Run without --dry-run to actually delete")
        conn.close()
        return
    
    # Confirm deletion
    response = input(f"⚠️  Delete {detection_count} detection results and related data? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Cancelled")
        conn.close()
        return
    
    # Delete in correct order (foreign keys)
    print("\n🗑️  Deleting data...")
    
    cursor.execute('''
        DELETE FROM sentence_analysis 
        WHERE detection_result_id IN (
            SELECT id FROM detection_results WHERE timestamp < ?
        )
    ''', (before_date,))
    print(f"  ✓ Deleted {cursor.rowcount} sentence analyses")
    
    cursor.execute('''
        DELETE FROM ai_patterns 
        WHERE detection_result_id IN (
            SELECT id FROM detection_results WHERE timestamp < ?
        )
    ''', (before_date,))
    print(f"  ✓ Deleted {cursor.rowcount} AI patterns")
    
    cursor.execute('''
        DELETE FROM generation_parameters 
        WHERE detection_result_id IN (
            SELECT id FROM detection_results WHERE timestamp < ?
        )
    ''', (before_date,))
    print(f"  ✓ Deleted {cursor.rowcount} generation parameters")
    
    cursor.execute('''
        DELETE FROM subjective_evaluations 
        WHERE timestamp < ?
    ''', (before_date,))
    print(f"  ✓ Deleted {cursor.rowcount} Subjective evaluations")
    
    cursor.execute('DELETE FROM detection_results WHERE timestamp < ?', (before_date,))
    print(f"  ✓ Deleted {cursor.rowcount} detection results")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Data purged successfully")
    print(f"   Database: {db_path}")
    print(f"   Before: {before_date}")
    print()
    print("💡 Next steps:")
    print("   1. Generate fresh samples with dynamic penalties")
    print("   2. Run: python3 scripts/e2e_system_evaluation.py")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Purge old contaminated data')
    parser.add_argument('--before', default='2025-11-15',
                       help='Delete data before this date (ISO format: YYYY-MM-DD)')
    parser.add_argument('--db', default='data/winston_feedback.db',
                       help='Path to database file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    # Validate database exists
    if not Path(args.db).exists():
        print(f"❌ Error: Database not found: {args.db}")
        sys.exit(1)
    
    # Validate date format
    try:
        datetime.fromisoformat(args.before)
    except ValueError:
        print(f"❌ Error: Invalid date format: {args.before}")
        print("   Use ISO format: YYYY-MM-DD")
        sys.exit(1)
    
    purge_old_data(args.db, args.before, args.dry_run)
