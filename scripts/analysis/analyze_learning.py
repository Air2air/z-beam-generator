#!/usr/bin/env python3
"""
Unified Learning Analyzer

Analyzes correlations between Winston AI detection and Grok subjective evaluation
to identify parameters that optimize BOTH metrics and discover trade-offs.

UNIFIED LEARNING ARCHITECTURE - Phase 2 Critical Tool
Per docs/architecture/UNIFIED_LEARNING_ARCHITECTURE.md

This tool answers the key question: "Does Winston score predict Subjective score?"

Usage:
    python3 scripts/analysis/analyze_learning.py --days 7
    python3 scripts/analysis/analyze_learning.py --prove-correlation

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


class LearningAnalyzer:
    """
    Cross-module analyzer for Winston + Subjective learning insights
    
    KEY RESEARCH QUESTIONS:
    1. Does high Winston score (95% human) correlate with high Subjective score (8/10)?
    2. Can we predict Subjective quality from Winston parameters?
    3. Are there trade-offs? (high Winston but low Subjective, or vice versa)
    4. What parameters optimize BOTH metrics?
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
    
    def find_matching_evaluations(self, days: Optional[int] = 7) -> List[Tuple]:
        """
        Find Winston detections with corresponding Subjective evaluations
        
        Matches by: material, component_type, timestamp proximity (within 5 minutes)
        
        Returns:
            List of (winston_row, subjective_row) tuples
        """
        cutoff = None
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = self.conn.cursor()
        
        # Get all Winston detections
        winston_query = """
        SELECT 
            id, timestamp, material, component_type,
            human_score, ai_score, temperature,
            frequency_penalty, presence_penalty, success
        FROM detection_results
        WHERE exclusion_reason IS NULL
        """
        
        if cutoff:
            winston_query += " AND timestamp >= ?"
            cursor.execute(winston_query, [cutoff])
        else:
            cursor.execute(winston_query)
        
        winston_results = cursor.fetchall()
        
        matches = []
        
        for winston_row in winston_results:
            # Try to find matching subjective evaluation
            # Match criteria: same material + component + within 5 minutes
            winston_time = datetime.fromisoformat(winston_row['timestamp'])
            time_min = (winston_time - timedelta(minutes=5)).isoformat()
            time_max = (winston_time + timedelta(minutes=5)).isoformat()
            
            cursor.execute("""
                SELECT 
                    id, timestamp, topic as material, component_type,
                    overall_score, realism_score, voice_authenticity,
                    clarity_score, professionalism_score,
                    technical_accuracy_score, human_likeness_score,
                    engagement_score, jargon_free_score,
                    passes_quality_gate
                FROM subjective_evaluations
                WHERE topic = ?
                AND component_type = ?
                AND timestamp BETWEEN ? AND ?
                LIMIT 1
            """, (winston_row['material'], winston_row['component_type'], time_min, time_max))
            
            subjective_row = cursor.fetchone()
            
            if subjective_row:
                matches.append((dict(winston_row), dict(subjective_row)))
        
        return matches
    
    def analyze_correlation(self, matches: List[Tuple]) -> Dict:
        """
        Analyze correlation between Winston and Subjective scores
        
        Statistical analysis:
        - Pearson correlation (if possible)
        - Bucket analysis (high/med/low for each metric)
        - Agreement rate (both pass vs one fails)
        """
        if len(matches) < 5:
            return {
                'available': False,
                'message': f'Insufficient matched samples (found {len(matches)}, need ≥5)'
            }
        
        # Extract score pairs
        winston_scores = [w['human_score'] for w, s in matches]
        subjective_scores = [(s['overall_score'] * 10) for w, s in matches]  # Convert 0-10 to 0-100 scale
        
        # Bucket analysis
        buckets = {
            'high_winston_high_subjective': 0,  # ≥90% Winston, ≥80% Subjective
            'high_winston_low_subjective': 0,   # ≥90% Winston, <80% Subjective
            'low_winston_high_subjective': 0,   # <90% Winston, ≥80% Subjective
            'low_winston_low_subjective': 0     # <90% Winston, <80% Subjective
        }
        
        for winston_score, subjective_score in zip(winston_scores, subjective_scores):
            if winston_score >= 90:
                if subjective_score >= 80:
                    buckets['high_winston_high_subjective'] += 1
                else:
                    buckets['high_winston_low_subjective'] += 1
            else:
                if subjective_score >= 80:
                    buckets['low_winston_high_subjective'] += 1
                else:
                    buckets['low_winston_low_subjective'] += 1
        
        # Agreement analysis
        agreements = sum(1 for w, s in matches 
                        if w['success'] == s['passes_quality_gate'])
        agreement_rate = agreements / len(matches)
        
        # Simple correlation approximation (direction)
        avg_winston = sum(winston_scores) / len(winston_scores)
        avg_subjective = sum(subjective_scores) / len(subjective_scores)
        
        above_avg_both = sum(1 for ws, ss in zip(winston_scores, subjective_scores)
                            if ws >= avg_winston and ss >= avg_subjective)
        below_avg_both = sum(1 for ws, ss in zip(winston_scores, subjective_scores)
                            if ws < avg_winston and ss < avg_subjective)
        
        directional_agreement = (above_avg_both + below_avg_both) / len(matches)
        
        insights = []
        insights.append(f"Found {len(matches)} matched Winston + Subjective evaluations")
        insights.append(f"Agreement on pass/fail: {agreement_rate*100:.0f}% ({agreements}/{len(matches)})")
        insights.append(f"Directional correlation: {directional_agreement*100:.0f}% (both above/below average)")
        
        # Identify trade-offs
        if buckets['high_winston_low_subjective'] > 0:
            insights.append(
                f"⚠️  TRADE-OFF DETECTED: {buckets['high_winston_low_subjective']} cases with "
                f"high Winston (≥90%) but low Subjective (<80%)"
            )
        
        if buckets['low_winston_high_subjective'] > 0:
            insights.append(
                f"⚠️  TRADE-OFF DETECTED: {buckets['low_winston_high_subjective']} cases with "
                f"low Winston (<90%) but high Subjective (≥80%)"
            )
        
        if buckets['high_winston_high_subjective'] > len(matches) * 0.5:
            insights.append(
                f"✅ POSITIVE CORRELATION: {buckets['high_winston_high_subjective']}/{len(matches)} "
                f"({buckets['high_winston_high_subjective']/len(matches)*100:.0f}%) have both high scores"
            )
        
        return {
            'available': True,
            'sample_size': len(matches),
            'buckets': buckets,
            'agreement_rate': agreement_rate,
            'directional_correlation': directional_agreement,
            'avg_winston': avg_winston,
            'avg_subjective': avg_subjective,
            'insights': insights
        }
    
    def find_optimal_parameters(self, matches: List[Tuple]) -> Dict:
        """
        Find parameters that optimize BOTH Winston and Subjective scores
        
        Returns parameters with highest combined success rate
        """
        if len(matches) < 5:
            return {
                'available': False,
                'message': 'Insufficient data for parameter optimization'
            }
        
        # Group by parameter combinations
        param_groups = {}
        
        for winston, subjective in matches:
            key = (
                round(winston['temperature'], 1),
                round(winston['frequency_penalty'], 1),
                round(winston['presence_penalty'], 1)
            )
            
            if key not in param_groups:
                param_groups[key] = {
                    'count': 0,
                    'winston_passes': 0,
                    'subjective_passes': 0,
                    'both_pass': 0,
                    'avg_winston': 0,
                    'avg_subjective': 0
                }
            
            group = param_groups[key]
            group['count'] += 1
            group['winston_passes'] += 1 if winston['success'] else 0
            group['subjective_passes'] += 1 if subjective['passes_quality_gate'] else 0
            group['both_pass'] += 1 if (winston['success'] and subjective['passes_quality_gate']) else 0
            group['avg_winston'] += winston['human_score']
            group['avg_subjective'] += subjective['overall_score'] * 10  # Scale to 0-100
        
        # Calculate averages and rates
        for key in param_groups:
            group = param_groups[key]
            count = group['count']
            group['avg_winston'] /= count
            group['avg_subjective'] /= count
            group['winston_success_rate'] = group['winston_passes'] / count
            group['subjective_success_rate'] = group['subjective_passes'] / count
            group['both_success_rate'] = group['both_pass'] / count
        
        # Find best parameters (require ≥3 samples)
        viable_params = [(k, v) for k, v in param_groups.items() if v['count'] >= 3]
        
        if not viable_params:
            return {
                'available': False,
                'message': 'No parameter combinations with ≥3 samples'
            }
        
        # Sort by combined success rate
        viable_params.sort(key=lambda x: x[1]['both_success_rate'], reverse=True)
        
        best_params = viable_params[:5]  # Top 5
        
        insights = []
        if best_params:
            temp, freq, pres = best_params[0][0]
            stats = best_params[0][1]
            insights.append(
                f"Best parameters: temp={temp}, freq={freq}, pres={pres} "
                f"(both pass: {stats['both_success_rate']*100:.0f}%, n={stats['count']})"
            )
        
        return {
            'available': True,
            'best_parameters': best_params,
            'insights': insights
        }
    
    def identify_tradeoffs(self, matches: List[Tuple]) -> Dict:
        """
        Identify specific cases where Winston and Subjective disagree
        
        Returns examples of trade-off cases for manual review
        """
        if len(matches) < 5:
            return {
                'available': False,
                'message': 'Insufficient data for trade-off analysis'
            }
        
        high_winston_low_subjective = []
        low_winston_high_subjective = []
        
        for winston, subjective in matches:
            winston_score = winston['human_score']
            subjective_score = subjective['overall_score'] * 10
            
            if winston_score >= 90 and subjective_score < 70:
                high_winston_low_subjective.append({
                    'material': winston['material'],
                    'component': winston['component_type'],
                    'winston_score': winston_score,
                    'subjective_score': subjective_score,
                    'temperature': winston['temperature']
                })
            
            if winston_score < 80 and subjective_score >= 80:
                low_winston_high_subjective.append({
                    'material': winston['material'],
                    'component': winston['component_type'],
                    'winston_score': winston_score,
                    'subjective_score': subjective_score,
                    'temperature': winston['temperature']
                })
        
        insights = []
        if high_winston_low_subjective:
            insights.append(
                f"Found {len(high_winston_low_subjective)} cases: High Winston (≥90%) but Low Subjective (<70%)"
            )
        
        if low_winston_high_subjective:
            insights.append(
                f"Found {len(low_winston_high_subjective)} cases: Low Winston (<80%) but High Subjective (≥80%)"
            )
        
        return {
            'available': True,
            'high_winston_low_subjective': high_winston_low_subjective[:5],  # Top 5 examples
            'low_winston_high_subjective': low_winston_high_subjective[:5],
            'insights': insights
        }


def print_analysis_report(analyzer: UnifiedLearningAnalyzer, args):
    """Print comprehensive unified learning analysis report"""
    
    print("=" * 80)
    print("UNIFIED LEARNING ANALYSIS")
    print("Winston AI Detection + Grok Subjective Evaluation")
    print("=" * 80)
    print()
    
    if args.days:
        print(f"Time Range: Last {args.days} days")
    else:
        print("Time Range: All time")
    print()
    
    # Find matching evaluations
    print("Finding matched Winston + Subjective evaluations...")
    matches = analyzer.find_matching_evaluations(days=args.days)
    print(f"✅ Found {len(matches)} matched pairs")
    print()
    
    if len(matches) < 5:
        print("❌ Insufficient data for analysis (need ≥5 matched pairs)")
        print("   Run more generations with both Winston detection and Subjective evaluation enabled.")
        return
    
    # Correlation analysis
    print("-" * 80)
    print("CORRELATION ANALYSIS")
    print("-" * 80)
    
    correlation = analyzer.analyze_correlation(matches)
    
    if correlation['available']:
        for insight in correlation['insights']:
            print(f"• {insight}")
        print()
        
        print("Score Distribution:")
        buckets = correlation['buckets']
        total = sum(buckets.values())
        for bucket_name, count in buckets.items():
            pct = count / total * 100
            label = bucket_name.replace('_', ' ').title()
            print(f"  {label}: {count} ({pct:.0f}%)")
        print()
    else:
        print(correlation['message'])
        print()
    
    # Optimal parameters
    print("-" * 80)
    print("OPTIMAL PARAMETERS (Both Winston + Subjective)")
    print("-" * 80)
    
    optimal = analyzer.find_optimal_parameters(matches)
    
    if optimal['available']:
        for insight in optimal['insights']:
            print(f"• {insight}")
        print()
        
        print("Top 5 Parameter Combinations:")
        print(f"{'Temp':<8} {'Freq':<8} {'Pres':<8} {'Both Pass':<12} {'Winston':<10} {'Subjective':<12} {'Samples':<8}")
        print("-" * 75)
        
        for params, stats in optimal['best_parameters']:
            temp, freq, pres = params
            print(
                f"{temp:<8.1f} {freq:<8.1f} {pres:<8.1f} "
                f"{stats['both_success_rate']*100:<12.0f}% "
                f"{stats['winston_success_rate']*100:<10.0f}% "
                f"{stats['subjective_success_rate']*100:<12.0f}% "
                f"{stats['count']:<8}"
            )
        print()
    else:
        print(optimal['message'])
        print()
    
    # Trade-offs
    print("-" * 80)
    print("TRADE-OFF ANALYSIS")
    print("-" * 80)
    
    tradeoffs = analyzer.identify_tradeoffs(matches)
    
    if tradeoffs['available']:
        for insight in tradeoffs['insights']:
            print(f"• {insight}")
        print()
        
        if tradeoffs['high_winston_low_subjective']:
            print("Examples: High Winston, Low Subjective (first 5):")
            for case in tradeoffs['high_winston_low_subjective']:
                print(
                    f"  • {case['material']}/{case['component']}: "
                    f"Winston {case['winston_score']:.0f}%, Subjective {case['subjective_score']:.0f}% "
                    f"(temp={case['temperature']:.1f})"
                )
            print()
        
        if tradeoffs['low_winston_high_subjective']:
            print("Examples: Low Winston, High Subjective (first 5):")
            for case in tradeoffs['low_winston_high_subjective']:
                print(
                    f"  • {case['material']}/{case['component']}: "
                    f"Winston {case['winston_score']:.0f}%, Subjective {case['subjective_score']:.0f}% "
                    f"(temp={case['temperature']:.1f})"
                )
            print()
    else:
        print(tradeoffs['message'])
        print()
    
    # Conclusion
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    
    if correlation['available']:
        if correlation['agreement_rate'] >= 0.7:
            print("✅ STRONG ALIGNMENT: Winston and Subjective agree ≥70% of the time")
            print("   → Unified learning library is RECOMMENDED")
            print("   → Parameters that optimize Winston likely optimize Subjective too")
        elif correlation['agreement_rate'] >= 0.5:
            print("⚠️  MODERATE ALIGNMENT: Winston and Subjective agree 50-70% of the time")
            print("   → Unified learning library is OPTIONAL")
            print("   → Consider trade-offs when optimizing parameters")
        else:
            print("❌ WEAK ALIGNMENT: Winston and Subjective agree <50% of the time")
            print("   → Unified learning library is NOT RECOMMENDED")
            print("   → Keep modules separate, optimize independently")
    
    print()
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze unified learning across Winston + Subjective modules"
    )
    parser.add_argument('--days', type=int, default=7, help='Analyze last N days (default: 7)')
    parser.add_argument('--prove-correlation', action='store_true', help='Run correlation proof analysis')
    parser.add_argument('--db', type=str, default='data/winston_feedback.db')
    
    args = parser.parse_args()
    
    try:
        with UnifiedLearningAnalyzer(db_path=args.db) as analyzer:
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
