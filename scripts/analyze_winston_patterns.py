#!/usr/bin/env python3
"""
Winston Pattern Analyzer

Analyzes detection_results table to understand parameter effectiveness,
failure patterns, sweet spot validation, and author performance.

UNIFIED LEARNING ARCHITECTURE - Phase 2 Analysis Tool
Per docs/architecture/UNIFIED_LEARNING_ARCHITECTURE.md

Usage:
    python3 scripts/analyze_winston_patterns.py --days 7
    python3 scripts/analyze_winston_patterns.py --since 2025-11-17
    python3 scripts/analyze_winston_patterns.py --material Aluminum

Created: November 17, 2025
"""

import sqlite3
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class WinstonPatternAnalyzer:
    """
    Analyzes Winston AI detection patterns for learning insights
    
    Analysis Focus:
    1. Parameter effectiveness (which temps/penalties work?)
    2. Failure patterns (why do some generations fail?)
    3. Sweet spot validation (are recommendations accurate?)
    4. Author performance (which authors pass Winston most?)
    """
    
    def __init__(self, db_path: str = "processing/detection/winston_feedback.db"):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to feedback database"""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ============================================================================
    # 1. PARAMETER EFFECTIVENESS ANALYSIS
    # ============================================================================
    
    def analyze_temperature_effectiveness(
        self,
        since_date: Optional[str] = None,
        days: Optional[int] = None
    ) -> Dict:
        """
        Analyze which temperature values produce best Winston scores
        
        Returns:
            dict: {
                'by_temperature': [(temp, avg_human_score, success_rate, count), ...],
                'optimal_range': (min_temp, max_temp),
                'insights': [str, ...]
            }
        """
        where_clause, params = self._build_time_filter(since_date, days)
        where_clause += " AND exclusion_reason IS NULL"  # Exclude contaminated data
        
        query = f"""
        SELECT 
            ROUND(temperature, 1) as temp,
            COUNT(*) as count,
            AVG(human_score) as avg_human,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
            CAST(SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as success_rate
        FROM detection_results
        WHERE {where_clause}
        GROUP BY temp
        HAVING count >= 3
        ORDER BY avg_human DESC
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        by_temp = [(r['temp'], r['avg_human'], r['success_rate'], r['count']) 
                   for r in results]
        
        # Find optimal range (temps with >80% avg success rate)
        high_success = [t for t, _, sr, c in by_temp if sr >= 0.8 and c >= 5]
        optimal_range = (min(high_success), max(high_success)) if high_success else (None, None)
        
        # Generate insights
        insights = []
        if by_temp:
            best = by_temp[0]
            insights.append(
                f"Best temperature: {best[0]} "
                f"(avg {best[1]:.1f}% human, {best[2]*100:.1f}% success, n={best[3]})"
            )
        
        if optimal_range[0] is not None:
            insights.append(
                f"Optimal range: {optimal_range[0]:.1f} - {optimal_range[1]:.1f} "
                f"(≥80% success rate with ≥5 samples)"
            )
        
        return {
            'by_temperature': by_temp,
            'optimal_range': optimal_range,
            'insights': insights
        }
    
    def analyze_penalty_effectiveness(
        self,
        since_date: Optional[str] = None,
        days: Optional[int] = None
    ) -> Dict:
        """
        Analyze frequency_penalty and presence_penalty effectiveness
        
        Returns:
            dict: Analysis of penalty parameters
        """
        where_clause, params = self._build_time_filter(since_date, days)
        where_clause += " AND exclusion_reason IS NULL"
        
        query = f"""
        SELECT 
            ROUND(frequency_penalty, 1) as freq_penalty,
            ROUND(presence_penalty, 1) as pres_penalty,
            COUNT(*) as count,
            AVG(human_score) as avg_human,
            CAST(SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as success_rate
        FROM detection_results
        WHERE {where_clause}
        GROUP BY freq_penalty, pres_penalty
        HAVING count >= 3
        ORDER BY avg_human DESC
        LIMIT 10
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        by_penalties = [
            (r['freq_penalty'], r['pres_penalty'], r['avg_human'], r['success_rate'], r['count'])
            for r in results
        ]
        
        insights = []
        if by_penalties:
            best = by_penalties[0]
            insights.append(
                f"Best penalty combo: freq={best[0]}, pres={best[1]} "
                f"(avg {best[2]:.1f}% human, {best[3]*100:.1f}% success, n={best[4]})"
            )
        
        return {
            'by_penalties': by_penalties,
            'insights': insights
        }
    
    # ============================================================================
    # 2. FAILURE PATTERN DETECTION
    # ============================================================================
    
    def analyze_failure_patterns(
        self,
        since_date: Optional[str] = None,
        days: Optional[int] = None
    ) -> Dict:
        """
        Identify common patterns in failed generations
        
        Returns:
            dict: {
                'total_failures': int,
                'failure_rate': float,
                'failure_score_distribution': [(range, count), ...],
                'common_parameters': [(temp, freq, pres, count), ...],
                'insights': [str, ...]
            }
        """
        where_clause, params = self._build_time_filter(since_date, days)
        where_clause += " AND exclusion_reason IS NULL"
        
        # Count total failures
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures
            FROM detection_results
            WHERE {where_clause}
        """, params)
        
        row = cursor.fetchone()
        total = row['total']
        failures = row['failures']
        failure_rate = failures / total if total > 0 else 0
        
        # Failure score distribution
        cursor.execute(f"""
            SELECT 
                CASE 
                    WHEN human_score < 20 THEN '0-20%'
                    WHEN human_score < 40 THEN '20-40%'
                    WHEN human_score < 60 THEN '40-60%'
                    WHEN human_score < 80 THEN '60-80%'
                    ELSE '80-100%'
                END as score_range,
                COUNT(*) as count
            FROM detection_results
            WHERE success = 0 AND {where_clause}
            GROUP BY score_range
            ORDER BY count DESC
        """, params)
        
        score_dist = [(r['score_range'], r['count']) for r in cursor.fetchall()]
        
        # Common failure parameters
        cursor.execute(f"""
            SELECT 
                ROUND(temperature, 1) as temp,
                ROUND(frequency_penalty, 1) as freq,
                ROUND(presence_penalty, 1) as pres,
                COUNT(*) as count,
                AVG(human_score) as avg_human
            FROM detection_results
            WHERE success = 0 AND {where_clause}
            GROUP BY temp, freq, pres
            HAVING count >= 2
            ORDER BY count DESC
            LIMIT 5
        """, params)
        
        failure_params = [
            (r['temp'], r['freq'], r['pres'], r['count'], r['avg_human'])
            for r in cursor.fetchall()
        ]
        
        # Generate insights
        insights = [
            f"Total failures: {failures}/{total} ({failure_rate*100:.1f}% failure rate)"
        ]
        
        if score_dist:
            worst_range = score_dist[0]
            insights.append(
                f"Most common failure range: {worst_range[0]} (n={worst_range[1]} failures)"
            )
        
        if failure_params:
            worst = failure_params[0]
            insights.append(
                f"Most frequent failure params: temp={worst[0]}, freq={worst[1]}, pres={worst[2]} "
                f"({worst[3]} failures, avg {worst[4]:.1f}% human)"
            )
        
        return {
            'total_failures': failures,
            'failure_rate': failure_rate,
            'failure_score_distribution': score_dist,
            'common_parameters': failure_params,
            'insights': insights
        }
    
    # ============================================================================
    # 3. SWEET SPOT VALIDATION
    # ============================================================================
    
    def validate_sweet_spots(self) -> Dict:
        """
        Validate current sweet spot recommendations against actual data
        
        Returns:
            dict: {
                'sweet_spots': [(material, component, temp, freq, pres, samples, avg_score), ...],
                'validation_results': [str, ...],
                'recommendations': [str, ...]
            }
        """
        cursor = self.conn.cursor()
        
        # Get current sweet spots
        cursor.execute("""
            SELECT 
                material,
                component_type,
                temperature,
                frequency_penalty,
                presence_penalty,
                sample_count,
                avg_human_score,
                last_updated
            FROM sweet_spot_recommendations
            WHERE sample_count >= 5
            ORDER BY material, component_type
        """)
        
        sweet_spots = cursor.fetchall()
        
        validation_results = []
        recommendations = []
        
        for spot in sweet_spots:
            material = spot['material']
            component = spot['component_type']
            sweet_temp = spot['temperature']
            sweet_freq = spot['frequency_penalty']
            sweet_pres = spot['presence_penalty']
            sample_count = spot['sample_count']
            avg_score = spot['avg_human_score']
            
            # Check if this sweet spot is still performing well
            cursor.execute("""
                SELECT 
                    COUNT(*) as recent_count,
                    AVG(human_score) as recent_avg,
                    CAST(SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as recent_success
                FROM detection_results
                WHERE material = ?
                AND component_type = ?
                AND ABS(temperature - ?) < 0.1
                AND ABS(frequency_penalty - ?) < 0.1
                AND ABS(presence_penalty - ?) < 0.1
                AND timestamp >= datetime('now', '-7 days')
                AND exclusion_reason IS NULL
            """, (material, component, sweet_temp, sweet_freq, sweet_pres))
            
            recent = cursor.fetchone()
            
            if recent['recent_count'] >= 3:
                score_diff = recent['recent_avg'] - avg_score
                
                if recent['recent_success'] >= 0.7:
                    status = "✅ VALIDATED"
                elif recent['recent_success'] >= 0.5:
                    status = "⚠️  MARGINAL"
                else:
                    status = "❌ UNDERPERFORMING"
                
                validation_results.append(
                    f"{status} {material}/{component}: "
                    f"avg {recent['recent_avg']:.1f}% ({"+"if score_diff>=0 else ""}{score_diff:.1f}), "
                    f"{recent['recent_success']*100:.0f}% success, n={recent['recent_count']}"
                )
                
                if status == "❌ UNDERPERFORMING":
                    recommendations.append(
                        f"Recalculate sweet spot for {material}/{component} "
                        f"(current: temp={sweet_temp}, success rate dropped to {recent['recent_success']*100:.0f}%)"
                    )
            else:
                validation_results.append(
                    f"⏳ {material}/{component}: Insufficient recent data (n={recent['recent_count']} in 7 days)"
                )
        
        return {
            'sweet_spots': [
                (s['material'], s['component_type'], s['temperature'],
                 s['frequency_penalty'], s['presence_penalty'],
                 s['sample_count'], s['avg_human_score'])
                for s in sweet_spots
            ],
            'validation_results': validation_results,
            'recommendations': recommendations
        }
    
    # ============================================================================
    # 4. AUTHOR PERFORMANCE COMPARISON
    # ============================================================================
    
    def analyze_author_performance(
        self,
        since_date: Optional[str] = None,
        days: Optional[int] = None
    ) -> Dict:
        """
        Compare Winston performance across different authors
        
        Note: Requires author tracking in database (may not be available)
        
        Returns:
            dict: Author performance comparison
        """
        # Check if author column exists
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(detection_results)")
        columns = [col['name'] for col in cursor.fetchall()]
        
        if 'author' not in columns:
            return {
                'available': False,
                'message': "Author tracking not available in current database schema"
            }
        
        where_clause, params = self._build_time_filter(since_date, days)
        where_clause += " AND exclusion_reason IS NULL"
        
        query = f"""
        SELECT 
            author,
            COUNT(*) as count,
            AVG(human_score) as avg_human,
            CAST(SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as success_rate,
            AVG(temperature) as avg_temp
        FROM detection_results
        WHERE author IS NOT NULL AND {where_clause}
        GROUP BY author
        HAVING count >= 5
        ORDER BY avg_human DESC
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        by_author = [
            (r['author'], r['avg_human'], r['success_rate'], r['count'], r['avg_temp'])
            for r in results
        ]
        
        insights = []
        if by_author:
            best = by_author[0]
            worst = by_author[-1]
            
            insights.append(
                f"Best author: {best[0]} "
                f"(avg {best[1]:.1f}% human, {best[2]*100:.1f}% success, n={best[3]})"
            )
            insights.append(
                f"Worst author: {worst[0]} "
                f"(avg {worst[1]:.1f}% human, {worst[2]*100:.1f}% success, n={worst[3]})"
            )
        
        return {
            'available': True,
            'by_author': by_author,
            'insights': insights
        }
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _build_time_filter(
        self,
        since_date: Optional[str],
        days: Optional[int]
    ) -> Tuple[str, List]:
        """Build WHERE clause for time filtering"""
        if since_date:
            return "timestamp >= ?", [since_date]
        elif days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            return "timestamp >= ?", [cutoff]
        else:
            return "1=1", []
    
    def get_summary_stats(
        self,
        since_date: Optional[str] = None,
        days: Optional[int] = None
    ) -> Dict:
        """Get overall summary statistics"""
        where_clause, params = self._build_time_filter(since_date, days)
        where_clause += " AND exclusion_reason IS NULL"
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_attempts,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                AVG(human_score) as avg_human,
                MIN(human_score) as min_human,
                MAX(human_score) as max_human,
                COUNT(DISTINCT material) as materials_tested,
                COUNT(DISTINCT component_type) as component_types
            FROM detection_results
            WHERE {where_clause}
        """, params)
        
        row = cursor.fetchone()
        
        return {
            'total_attempts': row['total_attempts'],
            'successes': row['successes'],
            'success_rate': row['successes'] / row['total_attempts'] if row['total_attempts'] > 0 else 0,
            'avg_human_score': row['avg_human'],
            'min_human_score': row['min_human'],
            'max_human_score': row['max_human'],
            'materials_tested': row['materials_tested'],
            'component_types': row['component_types']
        }


def print_analysis_report(analyzer: WinstonPatternAnalyzer, args):
    """Print comprehensive analysis report"""
    
    print("=" * 80)
    print("WINSTON PATTERN ANALYSIS")
    print("=" * 80)
    print()
    
    # Time range
    if args.since:
        print(f"Time Range: Since {args.since}")
    elif args.days:
        print(f"Time Range: Last {args.days} days")
    else:
        print("Time Range: All time")
    print()
    
    # Summary stats
    print("-" * 80)
    print("SUMMARY STATISTICS")
    print("-" * 80)
    
    stats = analyzer.get_summary_stats(since_date=args.since, days=args.days)
    
    print(f"Total Attempts: {stats['total_attempts']}")
    print(f"Successes: {stats['successes']} ({stats['success_rate']*100:.1f}%)")
    print(f"Average Human Score: {stats['avg_human_score']:.1f}%")
    print(f"Score Range: {stats['min_human_score']:.1f}% - {stats['max_human_score']:.1f}%")
    print(f"Materials Tested: {stats['materials_tested']}")
    print(f"Component Types: {stats['component_types']}")
    print()
    
    # Temperature analysis
    print("-" * 80)
    print("TEMPERATURE EFFECTIVENESS")
    print("-" * 80)
    
    temp_analysis = analyzer.analyze_temperature_effectiveness(since_date=args.since, days=args.days)
    
    for insight in temp_analysis['insights']:
        print(f"• {insight}")
    print()
    
    print("Top 10 Temperatures:")
    print(f"{'Temp':<8} {'Avg Human':<12} {'Success Rate':<14} {'Count':<10}")
    print("-" * 50)
    for temp, avg_h, success, count in temp_analysis['by_temperature'][:10]:
        print(f"{temp:<8.1f} {avg_h:<12.1f} {success*100:<14.1f}% {count:<10}")
    print()
    
    # Penalty analysis
    print("-" * 80)
    print("PENALTY EFFECTIVENESS")
    print("-" * 80)
    
    penalty_analysis = analyzer.analyze_penalty_effectiveness(since_date=args.since, days=args.days)
    
    for insight in penalty_analysis['insights']:
        print(f"• {insight}")
    print()
    
    print("Top Penalty Combinations:")
    print(f"{'Freq Penalty':<14} {'Pres Penalty':<14} {'Avg Human':<12} {'Success Rate':<14} {'Count':<10}")
    print("-" * 70)
    for freq, pres, avg_h, success, count in penalty_analysis['by_penalties']:
        print(f"{freq:<14.1f} {pres:<14.1f} {avg_h:<12.1f} {success*100:<14.1f}% {count:<10}")
    print()
    
    # Failure analysis
    print("-" * 80)
    print("FAILURE PATTERNS")
    print("-" * 80)
    
    failure_analysis = analyzer.analyze_failure_patterns(since_date=args.since, days=args.days)
    
    for insight in failure_analysis['insights']:
        print(f"• {insight}")
    print()
    
    print("Failure Score Distribution:")
    for score_range, count in failure_analysis['failure_score_distribution']:
        print(f"  {score_range:<12} {count:>6} failures")
    print()
    
    if failure_analysis['common_parameters']:
        print("Common Failure Parameters:")
        print(f"{'Temp':<8} {'Freq':<8} {'Pres':<8} {'Count':<10} {'Avg Human':<12}")
        print("-" * 50)
        for temp, freq, pres, count, avg_h in failure_analysis['common_parameters']:
            print(f"{temp:<8.1f} {freq:<8.1f} {pres:<8.1f} {count:<10} {avg_h:<12.1f}")
        print()
    
    # Sweet spot validation
    print("-" * 80)
    print("SWEET SPOT VALIDATION")
    print("-" * 80)
    
    sweet_spot_validation = analyzer.validate_sweet_spots()
    
    for result in sweet_spot_validation['validation_results']:
        print(result)
    print()
    
    if sweet_spot_validation['recommendations']:
        print("Recommendations:")
        for rec in sweet_spot_validation['recommendations']:
            print(f"  • {rec}")
        print()
    
    # Author performance
    print("-" * 80)
    print("AUTHOR PERFORMANCE")
    print("-" * 80)
    
    author_analysis = analyzer.analyze_author_performance(since_date=args.since, days=args.days)
    
    if author_analysis['available']:
        for insight in author_analysis['insights']:
            print(f"• {insight}")
        print()
        
        if author_analysis['by_author']:
            print("All Authors:")
            print(f"{'Author':<20} {'Avg Human':<12} {'Success Rate':<14} {'Count':<10} {'Avg Temp':<10}")
            print("-" * 70)
            for author, avg_h, success, count, avg_temp in author_analysis['by_author']:
                print(f"{author:<20} {avg_h:<12.1f} {success*100:<14.1f}% {count:<10} {avg_temp:<10.2f}")
    else:
        print(author_analysis['message'])
    
    print()
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Winston AI detection patterns for learning insights"
    )
    parser.add_argument(
        '--days',
        type=int,
        help='Analyze last N days of data'
    )
    parser.add_argument(
        '--since',
        type=str,
        help='Analyze data since specific date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--material',
        type=str,
        help='Filter by specific material'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='processing/detection/winston_feedback.db',
        help='Path to feedback database'
    )
    
    args = parser.parse_args()
    
    try:
        with WinstonPatternAnalyzer(db_path=args.db) as analyzer:
            print_analysis_report(analyzer, args)
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
