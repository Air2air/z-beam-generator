"""
Validation-Winston Correlation Analyzer

Correlates prompt validation issues with subsequent Winston detection scores
to measure the impact of prompt quality on AI detection humanness.

Purpose:
- Identify which validation issues most impact Winston scores
- Measure effectiveness of auto-fix strategies
- Track improvement trends over time
- Provide data-driven prioritization for fixes

Created: December 12, 2025
"""

import sqlite3
import logging
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CorrelationInsight:
    """Insight about validation issue impact on Winston scores"""
    issue_type: str
    issue_message: str
    occurrences: int
    avg_winston_with_issue: float
    avg_winston_without_issue: float
    impact_score: float  # Positive = issue hurts scores, Negative = issue helps
    confidence: float  # 0-1, based on sample size


class ValidationWinstonCorrelator:
    """
    Analyzes correlation between validation issues and Winston detection scores.
    
    Queries both prompt_validation_feedback and detection_results tables to
    identify which prompt issues have the biggest impact on AI humanness.
    """
    
    def __init__(self, db_path: str = 'z-beam.db'):
        """
        Initialize correlator.
        
        Args:
            db_path: Path to SQLite database with validation and detection data
        """
        self.db_path = db_path
        logger.info(f"ValidationWinstonCorrelator initialized (DB: {db_path})")
    
    def analyze_correlation(
        self,
        lookback_days: int = 30,
        min_samples: int = 5
    ) -> List[CorrelationInsight]:
        """
        Analyze correlation between validation issues and Winston scores.
        
        Strategy:
        1. Get all validation feedback from last N days
        2. For each unique issue type, get materials with that issue
        3. Find Winston scores for those materials (same component type)
        4. Compare average scores with vs without each issue
        5. Calculate impact score (difference in averages)
        
        Args:
            lookback_days: Days to look back for data
            min_samples: Minimum samples required for confidence
        
        Returns:
            List of correlation insights sorted by impact (worst issues first)
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🔗 ANALYZING VALIDATION-WINSTON CORRELATION")
        logger.info(f"{'='*70}")
        logger.info(f"   Lookback: {lookback_days} days")
        logger.info(f"   Min samples: {min_samples}")
        
        insights = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get date threshold
            cutoff_date = (datetime.now() - timedelta(days=lookback_days)).isoformat()
            
            # Get unique issue types from validation feedback
            cursor.execute("""
                SELECT DISTINCT
                    json_extract(value, '$.severity') as severity,
                    json_extract(value, '$.message') as message
                FROM prompt_validation_feedback, json_each(issues)
                WHERE timestamp > ?
            """, (cutoff_date,))
            
            unique_issues = cursor.fetchall()
            logger.info(f"   Found {len(unique_issues)} unique issue types")
            
            # For each issue, analyze correlation
            for severity, message in unique_issues:
                if not message:
                    continue
                
                insight = self._analyze_single_issue(
                    cursor, 
                    severity, 
                    message, 
                    cutoff_date,
                    min_samples
                )
                
                if insight:
                    insights.append(insight)
            
            conn.close()
            
            # Sort by absolute impact (worst issues first)
            insights.sort(key=lambda x: abs(x.impact_score), reverse=True)
            
            logger.info(f"   ✅ Generated {len(insights)} correlation insights")
            logger.info(f"{'='*70}\n")
            
            return insights
            
        except Exception as e:
            logger.error(f"Correlation analysis failed: {e}")
            return []
    
    def _analyze_single_issue(
        self,
        cursor,
        severity: str,
        message: str,
        cutoff_date: str,
        min_samples: int
    ) -> Optional[CorrelationInsight]:
        """
        Analyze correlation for a single issue type.
        
        Returns:
            CorrelationInsight if enough samples, None otherwise
        """
        import json
        
        # Get materials/components WITH this issue
        cursor.execute("""
            SELECT DISTINCT 
                pv.material,
                pv.component_type
            FROM prompt_validation_feedback pv, json_each(pv.issues) issue
            WHERE pv.timestamp > ?
              AND json_extract(issue.value, '$.message') = ?
              AND pv.material IS NOT NULL
              AND pv.component_type IS NOT NULL
        """, (cutoff_date, message))
        
        with_issue = cursor.fetchall()
        
        if len(with_issue) < min_samples:
            return None
        
        # Get Winston scores for materials WITH this issue
        with_issue_scores = []
        for material, component_type in with_issue:
            cursor.execute("""
                SELECT human_score
                FROM detection_results
                WHERE material = ?
                  AND component_type = ?
                  AND timestamp > ?
                  AND human_score IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 1
            """, (material, component_type, cutoff_date))
            
            result = cursor.fetchone()
            if result and result[0] is not None:
                with_issue_scores.append(result[0])
        
        if len(with_issue_scores) < min_samples:
            return None
        
        avg_with = sum(with_issue_scores) / len(with_issue_scores)
        
        # Get Winston scores for materials WITHOUT this issue (same component types)
        component_types = list(set(comp for _, comp in with_issue))
        
        cursor.execute(f"""
            SELECT dr.human_score
            FROM detection_results dr
            WHERE dr.timestamp > ?
              AND dr.component_type IN ({','.join('?' * len(component_types))})
              AND dr.human_score IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM prompt_validation_feedback pv, json_each(pv.issues) issue
                  WHERE pv.material = dr.material
                    AND pv.component_type = dr.component_type
                    AND json_extract(issue.value, '$.message') = ?
                    AND pv.timestamp > ?
              )
        """, (cutoff_date, *component_types, message, cutoff_date))
        
        without_issue_scores = [row[0] for row in cursor.fetchall() if row[0] is not None]
        
        if len(without_issue_scores) < min_samples:
            return None
        
        avg_without = sum(without_issue_scores) / len(without_issue_scores)
        
        # Calculate impact: positive = issue hurts Winston scores
        impact = avg_without - avg_with
        
        # Calculate confidence based on sample sizes
        total_samples = len(with_issue_scores) + len(without_issue_scores)
        confidence = min(1.0, total_samples / (min_samples * 4))
        
        return CorrelationInsight(
            issue_type=severity,
            issue_message=message[:60],  # Truncate for display
            occurrences=len(with_issue),
            avg_winston_with_issue=avg_with,
            avg_winston_without_issue=avg_without,
            impact_score=impact,
            confidence=confidence
        )
    
    def get_top_impactful_issues(
        self,
        lookback_days: int = 30,
        top_n: int = 10
    ) -> List[CorrelationInsight]:
        """
        Get the top N most impactful validation issues.
        
        Returns issues sorted by impact score (issues that hurt Winston scores most).
        
        Args:
            lookback_days: Days to analyze
            top_n: Number of top issues to return
        
        Returns:
            Top N most impactful issues
        """
        insights = self.analyze_correlation(lookback_days=lookback_days)
        return insights[:top_n]
    
    def print_correlation_report(self, lookback_days: int = 30):
        """
        Print human-readable correlation report to terminal.
        
        Args:
            lookback_days: Days to analyze
        """
        insights = self.analyze_correlation(lookback_days=lookback_days)
        
        if not insights:
            print("\n⚠️  No correlation data available (need more samples)")
            return
        
        print(f"\n{'='*70}")
        print(f"📊 VALIDATION ISSUE IMPACT ON WINSTON SCORES")
        print(f"{'='*70}")
        print(f"Analyzed: {lookback_days} days of data\n")
        
        print(f"{'Issue':<50} {'Impact':>8} {'Conf':>6} {'Occurs':>7}")
        print(f"{'-'*50} {'-'*8} {'-'*6} {'-'*7}")
        
        for insight in insights[:15]:  # Top 15
            impact_str = f"{insight.impact_score:+.2%}"
            conf_str = f"{insight.confidence:.0%}"
            occurs_str = f"{insight.occurrences}"
            
            # Color code by impact
            if insight.impact_score > 0.05:
                marker = "🔴"  # Significantly hurts scores
            elif insight.impact_score > 0.02:
                marker = "🟠"  # Moderately hurts scores
            elif insight.impact_score > 0:
                marker = "🟡"  # Slightly hurts scores
            else:
                marker = "🟢"  # Helps scores (rare)
            
            issue_display = insight.issue_message[:48]
            print(f"{marker} {issue_display:<47} {impact_str:>8} {conf_str:>6} {occurs_str:>7}")
        
        print(f"\n{'='*70}")
        print("💡 Impact = (Avg Winston without issue) - (Avg Winston with issue)")
        print("   Positive impact = Issue hurts Winston scores")
        print("   Higher confidence = More samples analyzed")
        print(f"{'='*70}\n")
    
    def track_fix_effectiveness(
        self,
        issue_message: str,
        before_date: str,
        after_date: str
    ) -> Dict[str, Any]:
        """
        Track if fixing an issue improved Winston scores.
        
        Compares average Winston scores before and after a fix was implemented.
        
        Args:
            issue_message: The validation issue that was fixed
            before_date: Date before fix (ISO format)
            after_date: Date after fix (ISO format)
        
        Returns:
            Dict with before/after stats and improvement percentage
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get Winston scores before fix (with this issue)
            cursor.execute("""
                SELECT AVG(dr.human_score), COUNT(*)
                FROM detection_results dr
                JOIN prompt_validation_feedback pv 
                  ON dr.material = pv.material 
                  AND dr.component_type = pv.component_type
                WHERE pv.timestamp < ?
                  AND dr.timestamp < ?
                  AND EXISTS (
                      SELECT 1 
                      FROM json_each(pv.issues) issue
                      WHERE json_extract(issue.value, '$.message') = ?
                  )
            """, (before_date, before_date, issue_message))
            
            before_avg, before_count = cursor.fetchone()
            
            # Get Winston scores after fix (without this issue)
            cursor.execute("""
                SELECT AVG(dr.human_score), COUNT(*)
                FROM detection_results dr
                WHERE dr.timestamp > ?
                  AND NOT EXISTS (
                      SELECT 1
                      FROM prompt_validation_feedback pv, json_each(pv.issues) issue
                      WHERE pv.material = dr.material
                        AND pv.component_type = dr.component_type
                        AND json_extract(issue.value, '$.message') = ?
                        AND pv.timestamp > ?
                  )
            """, (after_date, issue_message, after_date))
            
            after_avg, after_count = cursor.fetchone()
            
            conn.close()
            
            if before_avg and after_avg:
                improvement = after_avg - before_avg
                improvement_pct = (improvement / before_avg) * 100 if before_avg > 0 else 0
                
                return {
                    'issue': issue_message,
                    'before_avg': before_avg,
                    'before_count': before_count,
                    'after_avg': after_avg,
                    'after_count': after_count,
                    'improvement': improvement,
                    'improvement_pct': improvement_pct
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Fix effectiveness tracking failed: {e}")
            return {}


if __name__ == "__main__":
    # Test the correlator
    correlator = ValidationWinstonCorrelator()
    correlator.print_correlation_report(lookback_days=30)
