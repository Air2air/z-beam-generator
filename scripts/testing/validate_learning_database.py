#!/usr/bin/env python3
"""
Database Validation & Cleanup Script

Validates learning database integrity and cleans contaminated data from
pattern-only detection era (before Nov 17, 2025).

Checks:
1. Suspicious 100% human scores (pattern-only false positives)
2. Parameter reuse effectiveness
3. Winston score distribution
4. Sweet spot confidence levels
5. Learning target vs acceptance gap
6. Prompt optimization effectiveness
7. Author persona differentiation
8. Failure pattern analysis
9. Subjective evaluation correlation
10. Cost-benefit tracking

Usage:
    python3 scripts/validate_learning_database.py [--fix] [--report-only]
    
    --fix: Apply cleanup operations (removes contaminated data)
    --report-only: Only show report, no fixes
"""

import sqlite3
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

DB_PATH = "data/winston_feedback.db"
WINSTON_ONLY_DATE = "2025-11-17"  # Date pattern-only was removed


def connect_db():
    """Connect to learning database"""
    if not Path(DB_PATH).exists():
        print(f"❌ Database not found: {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)


def has_exclusion_column(conn):
    """Check if exclusion_reason column exists"""
    cursor = conn.execute("PRAGMA table_info(detection_results)")
    columns = [row[1] for row in cursor.fetchall()]
    return 'exclusion_reason' in columns


def get_exclusion_filter(conn):
    """Get SQL filter for exclusion_reason if column exists"""
    return "AND exclusion_reason IS NULL" if has_exclusion_column(conn) else ""


def check_suspicious_perfect_scores(conn, fix=False):
    """Check #1: Suspicious 100% human scores (likely pattern-only)"""
    print("\n" + "="*80)
    print("CHECK 1: SUSPICIOUS PERFECT SCORES (Pattern-Only Contamination)")
    print("="*80)
    
    cursor = conn.execute("""
        SELECT 
            COUNT(*) as suspicious_count,
            MIN(timestamp) as earliest,
            MAX(timestamp) as latest
        FROM detection_results 
        WHERE success = 1 
          AND human_score = 100.0
          AND timestamp < ?
    """, [WINSTON_ONLY_DATE])
    
    row = cursor.fetchone()
    suspicious_count, earliest, latest = row
    
    print(f"📊 Found {suspicious_count} suspicious 100% human scores before Winston-only fix")
    if suspicious_count > 0:
        print(f"   Date range: {earliest} to {latest}")
        print(f"   ⚠️  These likely passed pattern-only but would fail Winston API")
        
        if fix:
            print(f"\n🔧 FIXING: Marking {suspicious_count} records as excluded from learning...")
            
            # Add exclusion_reason column if not exists
            try:
                conn.execute("ALTER TABLE detection_results ADD COLUMN exclusion_reason TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            # Mark as excluded
            conn.execute("""
                UPDATE detection_results 
                SET exclusion_reason = 'pattern_only_false_positive',
                    success = 0
                WHERE success = 1 
                  AND human_score = 100.0
                  AND timestamp < ?
            """, [WINSTON_ONLY_DATE])
            conn.commit()
            print(f"   ✅ Marked {suspicious_count} records as excluded")
    else:
        print("   ✅ No suspicious perfect scores found")


def check_parameter_reuse_effectiveness(conn):
    """Check #2: Do reused parameters actually lead to success?"""
    print("\n" + "="*80)
    print("CHECK 2: PARAMETER REUSE EFFECTIVENESS")
    print("="*80)
    
    exclusion_filter = get_exclusion_filter(conn)
    
    query = f"""
        WITH param_usage AS (
            SELECT 
                ROUND(p.temperature, 2) as temp_rounded,
                COUNT(*) as times_used,
                AVG(r.human_score) as avg_human,
                SUM(CASE WHEN r.success = 1 THEN 1 ELSE 0 END) as success_count
            FROM generation_parameters p
            JOIN detection_results r ON p.detection_result_id = r.id
            WHERE 1=1 {exclusion_filter}
            GROUP BY temp_rounded
            HAVING times_used >= 3
        )
        SELECT 
            temp_rounded,
            times_used,
            avg_human,
            success_count,
            ROUND((success_count * 100.0 / times_used), 1) as success_rate
        FROM param_usage
        ORDER BY times_used DESC
        LIMIT 10
    """
    
    cursor = conn.execute(query)
    
    rows = cursor.fetchall()
    if rows:
        print(f"📊 Top 10 reused temperature values:")
        print(f"{'Temp':<8} {'Uses':<6} {'Avg Human':<12} {'Successes':<12} {'Success Rate':<15}")
        print("-" * 63)
        for temp, uses, avg_human, successes, rate in rows:
            print(f"{temp:<8} {uses:<6} {avg_human:>10.1f}% {successes:>11} {rate:>13.1f}%")
    else:
        print("   ℹ️  Insufficient data (need 3+ uses per parameter)")


def check_winston_score_distribution(conn):
    """Check #3: Is score distribution realistic?"""
    print("\n" + "="*80)
    print("CHECK 3: WINSTON SCORE DISTRIBUTION")
    print("="*80)
    
    cursor = conn.execute("""
        SELECT 
            CASE 
                WHEN human_score = 0 THEN '0% (AI-detected)'
                WHEN human_score = 100 THEN '100% (perfect)'
                WHEN human_score BETWEEN 1 AND 20 THEN '1-20% (poor)'
                WHEN human_score BETWEEN 21 AND 50 THEN '21-50% (moderate)'
                WHEN human_score BETWEEN 51 AND 80 THEN '51-80% (good)'
                WHEN human_score BETWEEN 81 AND 99 THEN '81-99% (excellent)'
            END as score_range,
            COUNT(*) as count,
            ROUND(AVG(temperature), 3) as avg_temp
        FROM detection_results
        WHERE timestamp > datetime('now', '-7 days')
          AND exclusion_reason IS NULL
        GROUP BY score_range
        ORDER BY MIN(human_score)
    """)
    
    rows = cursor.fetchall()
    if rows:
        total = sum(row[1] for row in rows)
        print(f"📊 Score distribution (last 7 days, {total} total):")
        print(f"{'Score Range':<20} {'Count':<8} {'%':<8} {'Avg Temp':<12}")
        print("-" * 48)
        for score_range, count, avg_temp in rows:
            pct = (count * 100.0 / total) if total > 0 else 0
            temp_str = f"{avg_temp:.3f}" if avg_temp is not None else "N/A"
            print(f"{score_range:<20} {count:<8} {pct:>6.1f}% {temp_str:>11}")
        
        # Warning if too many at extremes
        extreme_count = sum(row[1] for row in rows if '0%' in row[0] or '100%' in row[0])
        if extreme_count > total * 0.6:
            print(f"\n   ⚠️  WARNING: {extreme_count/total*100:.1f}% of scores at extremes (0% or 100%)")
            print("   This may indicate detection issues")
    else:
        print("   ℹ️  No data in last 7 days")


def check_sweet_spot_confidence(conn):
    """Check #4: Are sweet spots based on sufficient data?"""
    print("\n" + "="*80)
    print("CHECK 4: SWEET SPOT CONFIDENCE LEVELS")
    print("="*80)
    
    cursor = conn.execute("""
        SELECT 
            confidence_level,
            COUNT(*) as recommendation_count,
            ROUND(AVG(sample_size), 1) as avg_sample_size,
            MIN(sample_size) as min_samples,
            ROUND(AVG(max_human_score), 1) as avg_max_score
        FROM sweet_spot_recommendations
        GROUP BY confidence_level
        ORDER BY 
            CASE confidence_level 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
            END
    """)
    
    rows = cursor.fetchall()
    if rows:
        print(f"📊 Sweet spot recommendations by confidence:")
        print(f"{'Confidence':<12} {'Count':<8} {'Avg Samples':<14} {'Min Samples':<14} {'Avg Max Score':<15}")
        print("-" * 63)
        for conf, count, avg_samples, min_samples, avg_score in rows:
            print(f"{conf:<12} {count:<8} {avg_samples:>12} {min_samples:>13} {avg_score:>13.1f}%")
        
        # Warning for low-confidence recommendations
        low_conf = [row for row in rows if row[0] == 'low']
        if low_conf and low_conf[0][1] > 0:
            print(f"\n   ⚠️  WARNING: {low_conf[0][1]} low-confidence recommendations")
            print(f"   These have <5 samples and shouldn't be trusted")
    else:
        print("   ℹ️  No sweet spot recommendations yet")


def check_learning_target_gap(conn):
    """Check #5: Gap between acceptance threshold and learning target"""
    print("\n" + "="*80)
    print("CHECK 5: LEARNING TARGET vs ACCEPTANCE THRESHOLD GAP")
    print("="*80)
    
    cursor = conn.execute("""
        SELECT 
            COUNT(*) as total_attempts,
            SUM(CASE WHEN ai_score <= 0.333 THEN 1 ELSE 0 END) as pass_acceptance,
            SUM(CASE WHEN human_score >= 10 THEN 1 ELSE 0 END) as meet_learning_target,
            SUM(CASE WHEN ai_score <= 0.333 AND human_score < 10 THEN 1 ELSE 0 END) as gap_cases
        FROM detection_results
        WHERE timestamp > datetime('now', '-1 day')
          AND exclusion_reason IS NULL
    """)
    
    row = cursor.fetchone()
    total, pass_accept, meet_target, gap = row
    
    if total > 0:
        print(f"📊 Last 24 hours ({total} attempts):")
        print(f"   Pass Acceptance (ai_score ≤ 33.3%): {pass_accept} ({pass_accept*100.0/total:.1f}%)")
        print(f"   Meet Learning Target (human ≥ 10%): {meet_target} ({meet_target*100.0/total:.1f}%)")
        print(f"   Gap Cases (pass but don't learn): {gap} ({gap*100.0/total:.1f}%)")
        
        if gap > total * 0.3:
            print(f"\n   ⚠️  WARNING: {gap*100.0/total:.1f}% pass acceptance but fail learning")
            print("   System is 'good enough' without actually improving")
    else:
        print("   ℹ️  No data in last 24 hours")


def check_prompt_optimization_effectiveness(conn):
    """Check #6: Does prompt optimization improve results?"""
    print("\n" + "="*80)
    print("CHECK 6: PROMPT OPTIMIZATION EFFECTIVENESS")
    print("="*80)
    
    cursor = conn.execute("""
        SELECT 
            attempt_number,
            COUNT(*) as attempts,
            ROUND(AVG(human_score), 1) as avg_human,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
            ROUND((SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 1) as success_rate
        FROM detection_results
        WHERE timestamp > datetime('now', '-7 days')
          AND exclusion_reason IS NULL
        GROUP BY attempt_number
        ORDER BY attempt_number
    """)
    
    rows = cursor.fetchall()
    if rows:
        print(f"📊 Success rate by attempt number (last 7 days):")
        print(f"{'Attempt':<10} {'Count':<8} {'Avg Human':<12} {'Successes':<12} {'Success Rate':<15}")
        print("-" * 57)
        for attempt, count, avg_human, successes, rate in rows:
            marker = " 🧠" if attempt == 1 else ""
            print(f"{attempt:<10} {count:<8} {avg_human:>10}% {successes:>11} {rate:>13}%{marker}")
        
        if len(rows) > 1:
            attempt1 = [r for r in rows if r[0] == 1]
            if attempt1 and attempt1[0][4] < rows[1][4]:
                print(f"\n   ⚠️  WARNING: Attempt 1 (with optimization) performs worse than attempt 2")
                print("   Prompt optimization may not be working")
    else:
        print("   ℹ️  No data in last 7 days")


def check_failure_patterns(conn):
    """Check #8: What causes failures?"""
    print("\n" + "="*80)
    print("CHECK 8: FAILURE PATTERN ANALYSIS")
    print("="*80)
    
    cursor = conn.execute("""
        SELECT 
            failure_type,
            COUNT(*) as failure_count,
            ROUND(AVG(temperature), 3) as avg_temp,
            ROUND(AVG(ai_score), 3) as avg_ai_score
        FROM detection_results
        WHERE success = 0
          AND failure_type IS NOT NULL
          AND timestamp > datetime('now', '-7 days')
          AND exclusion_reason IS NULL
        GROUP BY failure_type
        ORDER BY failure_count DESC
    """)
    
    rows = cursor.fetchall()
    if rows:
        total_failures = sum(row[1] for row in rows)
        print(f"📊 Failure types (last 7 days, {total_failures} total failures):")
        print(f"{'Failure Type':<15} {'Count':<8} {'%':<8} {'Avg Temp':<12} {'Avg AI Score':<15}")
        print("-" * 58)
        for failure_type, count, avg_temp, avg_ai in rows:
            pct = (count * 100.0 / total_failures) if total_failures > 0 else 0
            print(f"{failure_type:<15} {count:<8} {pct:>6.1f}% {avg_temp:>11} {avg_ai:>14}")
        
        # Recommendations based on dominant failure
        if rows[0][1] > total_failures * 0.5:
            dominant = rows[0][0]
            print(f"\n   💡 RECOMMENDATION: {dominant} failures dominate ({rows[0][1]/total_failures*100:.0f}%)")
            if dominant == 'uniform':
                print("   → Increase randomness: higher temperature, more imperfection")
            elif dominant == 'borderline':
                print("   → Fine-tune parameters: small temperature adjustments")
            elif dominant == 'partial':
                print("   → Moderate boost: increase variation and reader engagement")
    else:
        print("   ℹ️  No failures with type classification in last 7 days")


def check_cost_benefit(conn):
    """Check #10: Track success rate trend and costs"""
    print("\n" + "="*80)
    print("CHECK 10: COST-BENEFIT ANALYSIS")
    print("="*80)
    
    cursor = conn.execute("""
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as total_attempts,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
            ROUND((SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 1) as success_rate,
            SUM(COALESCE(credits_used, 0)) as total_credits
        FROM detection_results
        WHERE exclusion_reason IS NULL
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        LIMIT 7
    """)
    
    rows = cursor.fetchall()
    if rows:
        print(f"📊 Success rate trend (last 7 days):")
        print(f"{'Date':<12} {'Attempts':<10} {'Successes':<12} {'Success Rate':<15} {'Credits':<10}")
        print("-" * 59)
        for date, attempts, successes, rate, credits in rows:
            print(f"{date:<12} {attempts:<10} {successes:<12} {rate:>13}% {credits:>9}")
        
        # Calculate trend
        if len(rows) >= 3:
            recent_rate = sum(r[3] for r in rows[:3]) / 3
            older_rate = sum(r[3] for r in rows[-3:]) / 3
            trend = recent_rate - older_rate
            
            if trend > 5:
                print(f"\n   ✅ IMPROVING: Success rate up {trend:.1f}% (recent vs older)")
            elif trend < -5:
                print(f"\n   ⚠️  DECLINING: Success rate down {abs(trend):.1f}% (recent vs older)")
            else:
                print(f"\n   ➡️  STABLE: Success rate change {trend:+.1f}%")
    else:
        print("   ℹ️  No data available")


def generate_summary_report(conn):
    """Generate overall health summary"""
    print("\n" + "="*80)
    print("OVERALL DATABASE HEALTH SUMMARY")
    print("="*80)
    
    # Total records
    cursor = conn.execute("SELECT COUNT(*) FROM detection_results")
    total_records = cursor.fetchone()[0]
    
    # Excluded records
    cursor = conn.execute("SELECT COUNT(*) FROM detection_results WHERE exclusion_reason IS NOT NULL")
    excluded = cursor.fetchone()[0]
    
    # Recent success rate
    cursor = conn.execute("""
        SELECT 
            ROUND((SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 1)
        FROM detection_results
        WHERE timestamp > datetime('now', '-7 days')
          AND exclusion_reason IS NULL
    """)
    recent_success = cursor.fetchone()[0] or 0
    
    # Average human score
    cursor = conn.execute("""
        SELECT ROUND(AVG(human_score), 1)
        FROM detection_results
        WHERE success = 1
          AND timestamp > datetime('now', '-7 days')
          AND exclusion_reason IS NULL
    """)
    avg_human = cursor.fetchone()[0] or 0
    
    print(f"📊 Database Statistics:")
    print(f"   Total records: {total_records}")
    print(f"   Excluded (contaminated): {excluded} ({excluded*100.0/total_records:.1f}%)" if total_records > 0 else "   Excluded: 0")
    print(f"   Success rate (last 7 days): {recent_success}%")
    print(f"   Avg human score (successful): {avg_human}%")
    
    # Health rating
    if recent_success >= 30 and avg_human >= 50:
        health = "🟢 EXCELLENT"
    elif recent_success >= 20 and avg_human >= 40:
        health = "🟡 GOOD"
    elif recent_success >= 10:
        health = "🟠 FAIR"
    else:
        health = "🔴 NEEDS IMPROVEMENT"
    
    print(f"\n   Overall Health: {health}")


def main():
    parser = argparse.ArgumentParser(description="Validate and clean learning database")
    parser.add_argument('--fix', action='store_true', help='Apply cleanup operations')
    parser.add_argument('--report-only', action='store_true', help='Only show report, no fixes')
    args = parser.parse_args()
    
    print("="*80)
    print("LEARNING DATABASE VALIDATION & CLEANUP")
    print("="*80)
    print(f"Database: {DB_PATH}")
    print(f"Winston-only date: {WINSTON_ONLY_DATE}")
    print(f"Mode: {'FIX' if args.fix else 'REPORT ONLY'}")
    
    conn = connect_db()
    
    try:
        # Run all checks
        check_suspicious_perfect_scores(conn, fix=args.fix and not args.report_only)
        check_parameter_reuse_effectiveness(conn)
        check_winston_score_distribution(conn)
        check_sweet_spot_confidence(conn)
        check_learning_target_gap(conn)
        check_prompt_optimization_effectiveness(conn)
        check_failure_patterns(conn)
        check_cost_benefit(conn)
        
        # Summary
        generate_summary_report(conn)
        
        print("\n" + "="*80)
        if args.fix and not args.report_only:
            print("✅ Validation complete with fixes applied")
        else:
            print("✅ Validation complete (report only)")
            if not args.fix:
                print("\n💡 Run with --fix to apply cleanup operations")
        print("="*80)
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
