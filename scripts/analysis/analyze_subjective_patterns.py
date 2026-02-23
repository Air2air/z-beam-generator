#!/usr/bin/env python3
"""
Subjective Pattern Analyzer

Analyzes subjective_evaluations table to understand dimension correlations,
weakness patterns, recommendation impact, and author voice quality.

UNIFIED LEARNING ARCHITECTURE - Phase 2 Analysis Tool
Per docs/architecture/UNIFIED_LEARNING_ARCHITECTURE.md

Usage:
    python3 scripts/analyze_subjective_patterns.py --days 7
    python3 scripts/analyze_subjective_patterns.py --material Aluminum

Created: November 17, 2025
"""

import sqlite3
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SubjectivePatternAnalyzer:
    """
    Analyzes Grok subjective evaluation patterns for learning insights
    
    Analysis Focus:
    1. Dimension correlations (which dimensions correlate?)
    2. Weakness patterns (common quality issues?)
    3. Recommendation impact (do recommendations help?)
    4. Author voice quality (which authors score best?)
    """
    
    def __init__(self, db_path: str = "data/winston_feedback.db"):
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
    
    def get_summary_stats(self, days: Optional[int] = None) -> Dict:
        """Get overall subjective evaluation statistics"""
        where_clause = "1=1"
        params = []
        
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            where_clause = "timestamp >= ?"
            params = [cutoff]
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_evaluations,
                AVG(overall_score) as avg_overall,
                AVG(clarity_score) as avg_clarity,
                AVG(professionalism_score) as avg_professionalism,
                AVG(technical_accuracy_score) as avg_technical,
                AVG(human_likeness_score) as avg_human_likeness,
                AVG(engagement_score) as avg_engagement,
                AVG(jargon_free_score) as avg_jargon_free,
                SUM(CASE WHEN passes_quality_gate = 1 THEN 1 ELSE 0 END) as passed,
                AVG(realism_score) as avg_realism,
                AVG(voice_authenticity) as avg_voice,
                AVG(tonal_consistency) as avg_tonal
            FROM subjective_evaluations
            WHERE {where_clause}
        """, params)
        
        return dict(cursor.fetchone())
    
    def analyze_dimension_correlations(self, days: Optional[int] = None) -> Dict:
        """Analyze correlations between evaluation dimensions"""
        # Get all evaluations
        where_clause = "1=1"
        params = []
        
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            where_clause = "timestamp >= ?"
            params = [cutoff]
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT 
                overall_score,
                clarity_score,
                professionalism_score,
                technical_accuracy_score,
                human_likeness_score,
                engagement_score,
                jargon_free_score
            FROM subjective_evaluations
            WHERE {where_clause}
            AND clarity_score IS NOT NULL
        """, params)
        
        evaluations = cursor.fetchall()
        
        if len(evaluations) < 5:
            return {'available': False, 'message': 'Insufficient data for correlation analysis (need ≥5 samples)'}
        
        # Simple correlation: find which dimension best predicts overall score
        dimensions = ['clarity', 'professionalism', 'technical_accuracy', 'human_likeness', 'engagement', 'jargon_free']
        correlations = []
        
        for dim in dimensions:
            dim_col = f"{dim}_score"
            cursor.execute(f"""
                SELECT 
                    AVG(overall_score) as avg_overall,
                    AVG({dim_col}) as avg_dim,
                    COUNT(*) as count
                FROM subjective_evaluations
                WHERE {where_clause}
                AND {dim_col} IS NOT NULL
                GROUP BY CAST({dim_col} AS INTEGER)
                HAVING count >= 2
            """, params)
            
            results = cursor.fetchall()
            if results:
                correlations.append((dim, len(results)))
        
        insights = []
        if correlations:
            correlations.sort(key=lambda x: x[1], reverse=True)
            insights.append(f"Most varied dimension: {correlations[0][0]} (range across {correlations[0][1]} score levels)")
        
        return {
            'available': True,
            'correlations': correlations,
            'insights': insights
        }
    
    def analyze_weakness_patterns(self, days: Optional[int] = None) -> Dict:
        """Identify most common weaknesses"""
        where_clause = "1=1"
        params = []
        
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            where_clause = "timestamp >= ?"
            params = [cutoff]
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT weaknesses
            FROM subjective_evaluations
            WHERE {where_clause}
            AND weaknesses IS NOT NULL
            AND weaknesses != '[]'
        """, params)
        
        all_weaknesses = []
        for row in cursor.fetchall():
            try:
                weaknesses = json.loads(row['weaknesses'])
                all_weaknesses.extend(weaknesses)
            except:
                pass
        
        # Count frequency
        weakness_counts = {}
        for weakness in all_weaknesses:
            key = weakness.lower()[:50]  # First 50 chars as key
            weakness_counts[key] = weakness_counts.get(key, 0) + 1
        
        top_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        insights = []
        if top_weaknesses:
            insights.append(f"Most common weakness: '{top_weaknesses[0][0]}' ({top_weaknesses[0][1]} occurrences)")
        
        return {
            'top_weaknesses': top_weaknesses,
            'total_unique': len(weakness_counts),
            'insights': insights
        }
    
    def analyze_realism_metrics(self, days: Optional[int] = None) -> Dict:
        """Analyze realism, voice authenticity, and AI tendencies"""
        where_clause = "1=1"
        params = []
        
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            where_clause = "timestamp >= ?"
            params = [cutoff]
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                AVG(realism_score) as avg_realism,
                AVG(voice_authenticity) as avg_voice,
                AVG(tonal_consistency) as avg_tonal,
                SUM(CASE WHEN realism_score >= 8 THEN 1 ELSE 0 END) as high_realism_count
            FROM subjective_evaluations
            WHERE {where_clause}
            AND realism_score IS NOT NULL
        """, params)
        
        stats = dict(cursor.fetchone())
        
        # AI tendencies analysis
        cursor.execute(f"""
            SELECT ai_tendencies
            FROM subjective_evaluations
            WHERE {where_clause}
            AND ai_tendencies IS NOT NULL
            AND ai_tendencies != '[]'
        """, params)
        
        all_tendencies = []
        for row in cursor.fetchall():
            try:
                tendencies = json.loads(row['ai_tendencies'])
                all_tendencies.extend(tendencies)
            except:
                pass
        
        tendency_counts = {}
        for tendency in all_tendencies:
            tendency_counts[tendency] = tendency_counts.get(tendency, 0) + 1
        
        top_tendencies = sorted(tendency_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        insights = []
        if stats['total'] > 0:
            insights.append(f"Average realism: {stats['avg_realism']:.1f}/10")
            insights.append(f"High realism rate: {stats['high_realism_count']}/{stats['total']} ({stats['high_realism_count']/stats['total']*100:.0f}%)")
        
        if top_tendencies:
            insights.append(f"Most detected AI tendency: {top_tendencies[0][0]} ({top_tendencies[0][1]} times)")
        
        return {
            'stats': stats,
            'top_ai_tendencies': top_tendencies,
            'insights': insights
        }


def print_analysis_report(analyzer: SubjectivePatternAnalyzer, args):
    """Print comprehensive analysis report"""
    
    print("=" * 80)
    print("SUBJECTIVE EVALUATION PATTERN ANALYSIS")
    print("=" * 80)
    print()
    
    if args.days:
        print(f"Time Range: Last {args.days} days")
    else:
        print("Time Range: All time")
    print()
    
    # Summary stats
    print("-" * 80)
    print("SUMMARY STATISTICS")
    print("-" * 80)
    
    stats = analyzer.get_summary_stats(days=args.days)
    
    print(f"Total Evaluations: {stats['total_evaluations']}")
    print(f"Average Overall Score: {stats['avg_overall']:.1f}/10")
    print(f"Quality Gate Pass Rate: {stats['passed']}/{stats['total_evaluations']} ({stats['passed']/stats['total_evaluations']*100:.1f}%)")
    print()
    
    print("Dimension Averages:")
    print(f"  Clarity: {stats['avg_clarity']:.1f}/10")
    print(f"  Professionalism: {stats['avg_professionalism']:.1f}/10")
    print(f"  Technical Accuracy: {stats['avg_technical']:.1f}/10")
    print(f"  Human Likeness: {stats['avg_human_likeness']:.1f}/10")
    print(f"  Engagement: {stats['avg_engagement']:.1f}/10")
    print(f"  Jargon-free: {stats['avg_jargon_free']:.1f}/10")
    print()
    
    if stats['avg_realism'] is not None:
        print("Realism Metrics:")
        print(f"  Realism Score: {stats['avg_realism']:.1f}/10")
        print(f"  Voice Authenticity: {stats['avg_voice']:.1f}/10")
        print(f"  Tonal Consistency: {stats['avg_tonal']:.1f}/10")
        print()
    
    # Dimension correlations
    print("-" * 80)
    print("DIMENSION CORRELATIONS")
    print("-" * 80)
    
    corr = analyzer.analyze_dimension_correlations(days=args.days)
    
    if corr['available']:
        for insight in corr['insights']:
            print(f"• {insight}")
    else:
        print(corr['message'])
    print()
    
    # Weakness patterns
    print("-" * 80)
    print("COMMON WEAKNESSES")
    print("-" * 80)
    
    weaknesses = analyzer.analyze_weakness_patterns(days=args.days)
    
    for insight in weaknesses['insights']:
        print(f"• {insight}")
    print()
    
    print(f"Top 10 Weaknesses (Total unique: {weaknesses['total_unique']}):")
    for i, (weakness, count) in enumerate(weaknesses['top_weaknesses'], 1):
        print(f"{i:2}. [{count:3}x] {weakness}")
    print()
    
    # Realism analysis
    print("-" * 80)
    print("REALISM & AI TENDENCY ANALYSIS")
    print("-" * 80)
    
    realism = analyzer.analyze_realism_metrics(days=args.days)
    
    for insight in realism['insights']:
        print(f"• {insight}")
    print()
    
    if realism['top_ai_tendencies']:
        print("Most Detected AI Tendencies:")
        for tendency, count in realism['top_ai_tendencies']:
            print(f"  • {tendency}: {count} times")
    else:
        print("No AI tendencies detected")
    print()
    
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Grok subjective evaluation patterns"
    )
    parser.add_argument('--days', type=int, help='Analyze last N days')
    parser.add_argument('--material', type=str, help='Filter by material')
    parser.add_argument('--db', type=str, default='data/winston_feedback.db')
    
    args = parser.parse_args()
    
    try:
        with SubjectivePatternAnalyzer(db_path=args.db) as analyzer:
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
