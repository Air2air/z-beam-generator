#!/usr/bin/env python3
"""
Generation Reporter - Comprehensive Terminal Reporting for Content Generation

Provides detailed terminal output for each generation attempt including:
- Full generated text
- AI detection scores
- Retry attempts and reasons
- Quality metrics
- Author personality settings

Usage:
    # As a wrapper for run.py
    python3 scripts/generation_reporter.py --material "Aluminum" --components "subtitle,caption"
    
    # As an importable reporter
    from scripts.generation_reporter import GenerationReporter
    reporter = GenerationReporter()
    reporter.report_generation(result, attempt_num=1)
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generation.config.author_config_loader import get_author_config, get_author_config_loader
from generation.config.dynamic_config import DynamicConfig

logger = logging.getLogger(__name__)


class GenerationReporter:
    """
    Comprehensive terminal reporter for content generation.
    
    Shows full text output, AI detection scores, retry attempts, and metrics.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize reporter.
        
        Args:
            verbose: Show detailed metrics and settings
        """
        self.verbose = verbose
        self.generation_history: List[Dict] = []
    
    def report_generation_start(
        self,
        material_name: str,
        component_type: str,
        author_id: int,
        author_name: str
    ):
        """Report the start of a generation attempt."""
        print("\n" + "=" * 100)
        print(f"🎯 GENERATION START")
        print("=" * 100)
        print(f"Material:     {material_name}")
        print(f"Component:    {component_type}")
        print(f"Author:       {author_name} (ID: {author_id})")
        print(f"Timestamp:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if self.verbose:
            self._report_author_settings(author_id, component_type)
    
    def _report_author_settings(self, author_id: int, component_type: str):
        """Report author-specific configuration settings."""
        try:
            config = get_author_config(author_id)
            dynamic = DynamicConfig(base_config=config)
            
            loader = get_author_config_loader()
            profile = loader.get_author_profile(author_id)
            
            print("📊 AUTHOR CONFIGURATION:")
            print(f"   Personality: {profile.get('personality', 'Unknown')}")
            print(f"   Technical Language: {config.get_technical_language_intensity()}")
            print(f"   Imperfection Tolerance: {config.get_imperfection_tolerance()}")
            print(f"   AI Avoidance: {config.get_ai_avoidance_intensity()}")
            print()
            print("🔧 CALCULATED PARAMETERS:")
            print(f"   Temperature: {dynamic.calculate_temperature(component_type):.2f}")
            print(f"   Max Tokens: {dynamic.calculate_max_tokens(component_type)}")
            print(f"   AI Threshold: {dynamic.calculate_detection_threshold():.1f}")
            print(f"   Min Readability: {dynamic.calculate_readability_thresholds()['min']:.1f}")
            print()
        except Exception as e:
            logger.warning(f"Could not load author settings: {e}")
    
    def report_generation_attempt(
        self,
        attempt_num: int,
        max_attempts: int,
        generated_text: str,
        ai_score: Optional[float] = None,
        ai_threshold: Optional[float] = None,
        quality_metrics: Optional[Dict] = None,
        reason_for_retry: Optional[str] = None
    ):
        """
        Report a generation attempt.
        
        Args:
            attempt_num: Current attempt number (1-indexed)
            max_attempts: Maximum attempts allowed
            generated_text: The generated content
            ai_score: AI detection score (0-100, lower is more human)
            ai_threshold: Threshold for AI detection
            quality_metrics: Additional quality metrics
            reason_for_retry: Why this attempt failed (if applicable)
        """
        print("-" * 100)
        print(f"📝 ATTEMPT {attempt_num}/{max_attempts}")
        print("-" * 100)
        print()
        
        # Show generated text
        print("📄 GENERATED TEXT:")
        print("┌" + "─" * 98 + "┐")
        for line in generated_text.strip().split('\n'):
            print(f"│ {line:<96} │")
        print("└" + "─" * 98 + "┘")
        print()
        
        # Show AI detection
        if ai_score is not None:
            self._report_ai_detection(ai_score, ai_threshold)
        
        # Show quality metrics
        if quality_metrics:
            self._report_quality_metrics(quality_metrics)
        
        # Show retry reason
        if reason_for_retry:
            print(f"⚠️  RETRY REASON: {reason_for_retry}")
            print()
        
        # Store in history
        self.generation_history.append({
            'attempt': attempt_num,
            'text': generated_text,
            'ai_score': ai_score,
            'quality_metrics': quality_metrics,
            'retry_reason': reason_for_retry,
            'timestamp': datetime.now().isoformat()
        })
    
    def _report_ai_detection(self, ai_score: float, threshold: Optional[float] = None):
        """Report AI detection score with visual indicator."""
        print("🔍 AI DETECTION:")
        
        # Visual bar for AI score
        bar_width = 50
        filled = int((ai_score / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        # Color coding based on score
        if ai_score < 30:
            status = "✅ EXCELLENT (Very human-like)"
        elif ai_score < 50:
            status = "✓ GOOD (Acceptable)"
        elif ai_score < 70:
            status = "⚠️  MARGINAL (Borderline)"
        else:
            status = "❌ HIGH (Too AI-like)"
        
        print(f"   Score: {ai_score:.1f}% {bar} {status}")
        
        if threshold is not None:
            print(f"   Threshold: {threshold:.1f}% (must be below)")
            if ai_score <= threshold:
                print("   ✅ PASSED threshold")
            else:
                print(f"   ❌ FAILED threshold (exceeded by {ai_score - threshold:.1f}%)")
        
        print()
    
    def _report_quality_metrics(self, metrics: Dict):
        """Report quality metrics."""
        print("📊 QUALITY METRICS:")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
        print()
    
    def report_generation_success(
        self,
        final_text: str,
        total_attempts: int,
        ai_score: float
    ):
        """Report successful generation."""
        print("=" * 100)
        print("✅ GENERATION SUCCESS")
        print("=" * 100)
        print(f"Final attempt: {total_attempts}")
        print(f"Final AI score: {ai_score:.1f}%")
        print()
        print("📄 FINAL TEXT:")
        print("┌" + "─" * 98 + "┐")
        for line in final_text.strip().split('\n'):
            print(f"│ {line:<96} │")
        print("└" + "─" * 98 + "┘")
        print()
    
    def report_generation_failure(
        self,
        reason: str,
        total_attempts: int,
        best_attempt: Optional[Dict] = None
    ):
        """Report generation failure."""
        print("=" * 100)
        print("❌ GENERATION FAILURE")
        print("=" * 100)
        print(f"Reason: {reason}")
        print(f"Total attempts: {total_attempts}")
        print()
        
        if best_attempt:
            print("📄 BEST ATTEMPT:")
            print(f"   AI Score: {best_attempt.get('ai_score', 'N/A'):.1f}%")
            print()
            print("┌" + "─" * 98 + "┐")
            for line in best_attempt.get('text', '').strip().split('\n'):
                print(f"│ {line:<96} │")
            print("└" + "─" * 98 + "┘")
        print()
    
    def report_summary(self):
        """Report summary of all generation attempts."""
        if not self.generation_history:
            return
        
        print("=" * 100)
        print("📈 GENERATION SUMMARY")
        print("=" * 100)
        print(f"Total attempts: {len(self.generation_history)}")
        print()
        
        # Show attempt progression
        print("ATTEMPT PROGRESSION:")
        print(f"{'#':<5} {'AI Score':<12} {'Status':<20} {'Reason':<40}")
        print("-" * 100)
        
        for entry in self.generation_history:
            attempt = entry['attempt']
            ai_score = entry.get('ai_score', 'N/A')
            ai_score_str = f"{ai_score:.1f}%" if isinstance(ai_score, (int, float)) else str(ai_score)
            
            if entry.get('retry_reason'):
                status = "❌ Failed"
                reason = entry['retry_reason'][:37] + "..." if len(entry['retry_reason']) > 40 else entry['retry_reason']
            else:
                status = "✅ Success"
                reason = "-"
            
            print(f"{attempt:<5} {ai_score_str:<12} {status:<20} {reason:<40}")
        
        print()
    
    def export_report(self, output_path: str):
        """Export generation history to JSON file."""
        with open(output_path, 'w') as f:
            json.dump({
                'generation_history': self.generation_history,
                'summary': {
                    'total_attempts': len(self.generation_history),
                    'timestamp': datetime.now().isoformat()
                }
            }, f, indent=2)
        
        print(f"📁 Report exported to: {output_path}")


def main():
    """CLI wrapper for generation with reporting."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate content with detailed reporting')
    parser.add_argument('--material', required=True, help='Material name')
    parser.add_argument('--components', default='subtitle', help='Comma-separated components')
    parser.add_argument('--export', help='Export report to JSON file')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    # This would integrate with your actual generation pipeline
    # For now, it's a demonstration of the reporting capabilities
    
    reporter = GenerationReporter(verbose=not args.quiet)
    
    # Example usage (replace with actual generation calls)
    reporter.report_generation_start(
        material_name=args.material,
        component_type=args.components.split(',')[0],
        author_id=1,
        author_name="Yi-Chun Lin"
    )
    
    # Simulate attempts
    reporter.report_generation_attempt(
        attempt_num=1,
        max_attempts=5,
        generated_text="Example generated text for demonstration purposes",
        ai_score=45.3,
        ai_threshold=40.0,
        quality_metrics={'readability': 58.5, 'word_count': 15},
        reason_for_retry="AI score exceeded threshold"
    )
    
    reporter.report_generation_attempt(
        attempt_num=2,
        max_attempts=5,
        generated_text="Improved text with better human-like characteristics",
        ai_score=38.2,
        ai_threshold=40.0,
        quality_metrics={'readability': 60.2, 'word_count': 14}
    )
    
    reporter.report_generation_success(
        final_text="Improved text with better human-like characteristics",
        total_attempts=2,
        ai_score=38.2
    )
    
    reporter.report_summary()
    
    if args.export:
        reporter.export_report(args.export)


if __name__ == '__main__':
    main()
