#!/usr/bin/env python3
"""
Database Migration Script: Normalize Scores to 0-1.0
 
Converts all score fields in z-beam.db from mixed formats (0-100 and 0-1.0)
to consistent 0-1.0 normalized scale.

Usage:
    python3 scripts/migrate_scores_to_normalized.py [--dry-run] [--db-path path/to/db]

Date: November 20, 2025
Fixes: Parameter normalization inconsistency (CRITICAL issue)
"""

import sqlite3
import argparse
from pathlib import Path
import sys


def analyze_current_state(db_path: str):
    """Analyze current database state before migration."""
    print("\n" + "="*70)
    print("📊 PRE-MIGRATION ANALYSIS")
    print("="*70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check detection_results scores
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            MIN(human_score) as min_human,
            MAX(human_score) as max_human,
            AVG(human_score) as avg_human,
            MIN(ai_score) as min_ai,
            MAX(ai_score) as max_ai,
            AVG(ai_score) as avg_ai,
            MIN(composite_quality_score) as min_composite,
            MAX(composite_quality_score) as max_composite,
            AVG(composite_quality_score) as avg_composite
        FROM detection_results
    """)
    
    stats = cursor.fetchone()
    total, min_h, max_h, avg_h, min_a, max_a, avg_a, min_c, max_c, avg_c = stats
    
    print(f"\n📋 detection_results table ({total} records):")
    print(f"   human_score:   {min_h:.4f} - {max_h:.4f} (avg: {avg_h:.4f})")
    print(f"   ai_score:      {min_a:.4f} - {max_a:.4f} (avg: {avg_a:.4f})")
    if max_c:
        print(f"   composite:     {min_c:.4f} - {max_c:.4f} (avg: {avg_c:.4f})")
    else:
        print(f"   composite:     No data")
    
    # Identify records needing migration
    cursor.execute("SELECT COUNT(*) FROM detection_results WHERE human_score > 1.0")
    needs_migration_human = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM detection_results WHERE composite_quality_score > 1.0")
    needs_migration_composite = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM detection_results WHERE readability_score > 1.0")
    needs_migration_read = cursor.fetchone()[0]
    
    print(f"\n🔍 Records needing migration:")
    print(f"   human_score > 1.0:     {needs_migration_human}")
    print(f"   composite_score > 1.0: {needs_migration_composite}")
    print(f"   readability > 1.0:     {needs_migration_read}")
    
    # Check sweet_spot_recommendations
    cursor.execute("SELECT COUNT(*) FROM sweet_spot_recommendations")
    sweet_spot_count = cursor.fetchone()[0]
    
    if sweet_spot_count > 0:
        cursor.execute("""
            SELECT 
                material, component_type, sample_count, avg_human_score
            FROM sweet_spot_recommendations
        """)
        print(f"\n📈 sweet_spot_recommendations ({sweet_spot_count} records):")
        for row in cursor.fetchall():
            material, component, samples, avg_score = row
            print(f"   {material or 'GLOBAL'} / {component or '*'}: {avg_score:.4f} ({samples} samples)")
    
    conn.close()
    
    return {
        'total_records': total,
        'needs_human_migration': needs_migration_human,
        'needs_composite_migration': needs_migration_composite,
        'needs_readability_migration': needs_migration_read
    }


def migrate_detection_results(cursor, dry_run: bool = False):
    """Migrate detection_results table scores to 0-1.0."""
    print("\n🔄 Migrating detection_results...")
    
    if dry_run:
        print("   [DRY RUN] No changes will be made")
    
    # Normalize human_score (divide by 100 if > 1.0)
    cursor.execute("""
        UPDATE detection_results
        SET human_score = human_score / 100.0
        WHERE human_score > 1.0
    """)
    human_updated = cursor.rowcount
    print(f"   ✅ human_score: {human_updated} records normalized")
    
    # Normalize composite_quality_score (divide by 100 if > 1.0)
    cursor.execute("""
        UPDATE detection_results
        SET composite_quality_score = composite_quality_score / 100.0
        WHERE composite_quality_score > 1.0
    """)
    composite_updated = cursor.rowcount
    print(f"   ✅ composite_quality_score: {composite_updated} records normalized")
    
    # Normalize readability_score (divide by 100 if > 1.0)
    cursor.execute("""
        UPDATE detection_results
        SET readability_score = readability_score / 100.0
        WHERE readability_score > 1.0
    """)
    readability_updated = cursor.rowcount
    print(f"   ✅ readability_score: {readability_updated} records normalized")
    
    return {
        'human_updated': human_updated,
        'composite_updated': composite_updated,
        'readability_updated': readability_updated
    }


def migrate_sweet_spot(cursor, dry_run: bool = False):
    """Migrate sweet_spot_recommendations table scores to 0-1.0."""
    print("\n🔄 Migrating sweet_spot_recommendations...")
    
    if dry_run:
        print("   [DRY RUN] No changes will be made")
    
    # Normalize avg_human_score and max_human_score (divide by 100 if > 1.0)
    cursor.execute("""
        UPDATE sweet_spot_recommendations
        SET 
            avg_human_score = avg_human_score / 100.0,
            max_human_score = max_human_score / 100.0
        WHERE avg_human_score > 1.0 OR max_human_score > 1.0
    """)
    updated = cursor.rowcount
    print(f"   ✅ avg/max_human_score: {updated} records normalized")
    
    return {'sweet_spot_updated': updated}


def verify_migration(db_path: str):
    """Verify all scores are now 0-1.0."""
    print("\n" + "="*70)
    print("✅ POST-MIGRATION VERIFICATION")
    print("="*70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check detection_results
    cursor.execute("""
        SELECT 
            MAX(human_score) as max_human,
            MAX(ai_score) as max_ai,
            MAX(composite_quality_score) as max_composite,
            MAX(readability_score) as max_readability
        FROM detection_results
    """)
    
    max_h, max_a, max_c, max_r = cursor.fetchone()
    
    print(f"\n📊 detection_results maximum values:")
    print(f"   human_score:   {max_h:.4f} {'✅' if max_h <= 1.0 else '❌ STILL > 1.0!'}")
    print(f"   ai_score:      {max_a:.4f} {'✅' if max_a <= 1.0 else '❌ STILL > 1.0!'}")
    if max_c:
        print(f"   composite:     {max_c:.4f} {'✅' if max_c <= 1.0 else '❌ STILL > 1.0!'}")
    else:
        print(f"   composite:     No data")
    if max_r:
        print(f"   readability:   {max_r:.4f} {'✅' if max_r <= 1.0 else '❌ STILL > 1.0!'}")
    else:
        print(f"   readability:   No data")
    
    # Check sweet_spot
    cursor.execute("""
        SELECT 
            MAX(avg_human_score) as max_avg,
            MAX(max_human_score) as max_max
        FROM sweet_spot_recommendations
    """)
    
    result = cursor.fetchone()
    if result and result[0]:
        max_avg, max_max = result
        print(f"\n📈 sweet_spot_recommendations maximum values:")
        print(f"   avg_human_score: {max_avg:.4f} {'✅' if max_avg <= 1.0 else '❌ STILL > 1.0!'}")
        print(f"   max_human_score: {max_max:.4f} {'✅' if max_max <= 1.0 else '❌ STILL > 1.0!'}")
    
    # Check for any remaining > 1.0
    cursor.execute("""
        SELECT COUNT(*) FROM detection_results 
        WHERE human_score > 1.0 OR ai_score > 1.0 
           OR composite_quality_score > 1.0 
           OR readability_score > 1.0
    """)
    remaining = cursor.fetchone()[0]
    
    conn.close()
    
    if remaining > 0:
        print(f"\n❌ WARNING: {remaining} records still have scores > 1.0!")
        return False
    else:
        print(f"\n✅ SUCCESS: All scores normalized to 0-1.0 range")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Migrate z-beam.db scores to 0-1.0 normalized format"
    )
    parser.add_argument(
        '--db-path',
        default='z-beam.db',
        help='Path to database file (default: z-beam.db)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create backup before migration'
    )
    
    args = parser.parse_args()
    
    # Check database exists
    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return 1
    
    print("="*70)
    print("🔄 SCORE NORMALIZATION MIGRATION")
    print("="*70)
    print(f"\nDatabase: {db_path.absolute()}")
    print(f"Mode: {'DRY RUN (no changes)' if args.dry_run else 'LIVE (will modify data)'}")
    
    # Create backup if requested
    if args.backup and not args.dry_run:
        import shutil
        from datetime import datetime
        backup_path = db_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        shutil.copy2(db_path, backup_path)
        print(f"\n💾 Backup created: {backup_path}")
    
    # Analyze current state
    stats = analyze_current_state(str(db_path))
    
    if stats['needs_human_migration'] == 0 and stats['needs_composite_migration'] == 0:
        print("\n✅ No migration needed - all scores already normalized")
        return 0
    
    # Confirm migration
    if not args.dry_run:
        print(f"\n⚠️  This will modify {stats['total_records']} records in the database.")
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled")
            return 0
    
    # Perform migration
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Migrate tables
        detection_stats = migrate_detection_results(cursor, dry_run=args.dry_run)
        sweet_spot_stats = migrate_sweet_spot(cursor, dry_run=args.dry_run)
        
        if not args.dry_run:
            conn.commit()
            print("\n✅ Migration committed to database")
        else:
            conn.rollback()
            print("\n[DRY RUN] No changes committed")
        
        conn.close()
        
        # Verify if not dry run
        if not args.dry_run:
            success = verify_migration(str(db_path))
            if not success:
                print("\n❌ Migration verification failed!")
                return 1
        
        print("\n" + "="*70)
        print("✅ MIGRATION COMPLETE")
        print("="*70)
        print(f"\nSummary:")
        print(f"   - detection_results human_score: {detection_stats['human_updated']} normalized")
        print(f"   - detection_results composite: {detection_stats['composite_updated']} normalized")
        print(f"   - detection_results readability: {detection_stats['readability_updated']} normalized")
        print(f"   - sweet_spot recommendations: {sweet_spot_stats['sweet_spot_updated']} normalized")
        
        if not args.dry_run:
            print(f"\n🎯 All scores now use consistent 0-1.0 normalized format")
            print(f"   - 0.0 = 0%")
            print(f"   - 0.5 = 50%")
            print(f"   - 1.0 = 100%")
        
        return 0
        
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
