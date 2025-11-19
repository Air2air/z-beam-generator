#!/usr/bin/env python3
"""
Sweet Spot Analyzer CLI

Command-line interface for analyzing optimal parameter ranges and tracking
maximum achievements from Winston feedback database.

Usage:
    python3 scripts/winston/sweet_spot.py                      # Full analysis
    python3 scripts/winston/sweet_spot.py --material Copper    # Material-specific
    python3 scripts/winston/sweet_spot.py --component caption  # Component-specific
    python3 scripts/winston/sweet_spot.py --maximums           # Show best achievements
    python3 scripts/winston/sweet_spot.py --correlations       # Parameter importance
"""

import sys
import argparse
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from learning.sweet_spot_analyzer import SweetSpotAnalyzer
from generation.config.config_loader import get_config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def show_sweet_spots(analyzer, args):
    """Display optimal parameter ranges."""
    sweet_spots = analyzer.find_sweet_spots(
        material=args.material,
        component_type=args.component,
        top_n_percent=args.top_percent
    )
    
    if not sweet_spots:
        print("\n⚠️  Insufficient data for sweet spot analysis")
        print(f"   Need at least {analyzer.min_samples} successful samples")
        return
    
    print("\n" + "="*80)
    print("🎯 SWEET SPOT ANALYSIS - Optimal Parameter Ranges")
    print("="*80)
    
    if args.material:
        print(f"\n📦 Material: {args.material}")
    if args.component:
        print(f"📝 Component: {args.component}")
    
    print(f"\n📊 Based on top {args.top_percent}% of successful generations\n")
    
    # Group by confidence level
    high_confidence = {k: v for k, v in sweet_spots.items() if v.confidence == 'high'}
    medium_confidence = {k: v for k, v in sweet_spots.items() if v.confidence == 'medium'}
    low_confidence = {k: v for k, v in sweet_spots.items() if v.confidence == 'low'}
    
    def print_sweet_spot_table(spots, title):
        if not spots:
            return
        
        print(f"\n{title}")
        print("-" * 80)
        print(f"{'Parameter':<30} {'Range':<25} {'Median':<10} {'Avg Score'}")
        print("-" * 80)
        
        for name, spot in sorted(spots.items()):
            range_str = f"{spot.optimal_min:.2f} - {spot.optimal_max:.2f}"
            print(
                f"{name:<30} {range_str:<25} {spot.optimal_median:<10.2f} "
                f"{spot.avg_human_score:.1f}% ({spot.sample_count} samples)"
            )
    
    print_sweet_spot_table(high_confidence, "🟢 HIGH CONFIDENCE (20+ samples, low variance)")
    print_sweet_spot_table(medium_confidence, "🟡 MEDIUM CONFIDENCE (10-20 samples)")
    print_sweet_spot_table(low_confidence, "🔴 LOW CONFIDENCE (<10 samples)")
    
    print("\n" + "="*80 + "\n")


def show_maximums(analyzer, args):
    """Display best ever achievements."""
    maximums = analyzer.get_maximum_achievements(
        material=args.material,
        component_type=args.component,
        limit=args.limit
    )
    
    if not maximums:
        print("\n⚠️  No successful generations found")
        return
    
    print("\n" + "="*80)
    print("🏆 MAXIMUM ACHIEVEMENTS - Best Ever Scores")
    print("="*80 + "\n")
    
    for i, max_achievement in enumerate(maximums, 1):
        print(f"\n#{i}. {max_achievement.material} {max_achievement.component_type}")
        print("-" * 80)
        print(f"   Winston Human Score: {max_achievement.max_human_score:.2f}%")
        
        if max_achievement.max_claude_score:
            print(f"   Claude Quality Score: {max_achievement.max_claude_score:.2f}/10")
        
        print(f"   Achieved: {max_achievement.achieved_at}")
        
        # Show key parameters
        params = max_achievement.parameters
        print(f"\n   Key Parameters:")
        print(f"   • Temperature: {params['api']['temperature']:.3f}")
        print(f"   • Frequency Penalty: {params['api']['frequency_penalty']:.3f}")
        print(f"   • Presence Penalty: {params['api']['presence_penalty']:.3f}")
        print(f"   • Trait Frequency: {params['voice']['trait_frequency']:.2f}")
        print(f"   • Technical Intensity: {params['enrichment']['technical_intensity']}")
        print(f"   • Imperfection Tolerance: {params['voice'].get('imperfection_tolerance', 'N/A')}")
        
        # Show preview of content
        preview = max_achievement.generated_text[:150]
        if len(max_achievement.generated_text) > 150:
            preview += "..."
        print(f"\n   Generated Text Preview:")
        print(f"   \"{preview}\"")
    
    print("\n" + "="*80 + "\n")


def show_correlations(analyzer, args):
    """Display parameter correlations with human scores."""
    correlations = analyzer.analyze_parameter_correlation(
        material=args.material,
        component_type=args.component
    )
    
    if not correlations:
        print("\n⚠️  Insufficient data for correlation analysis")
        return
    
    print("\n" + "="*80)
    print("📊 PARAMETER CORRELATIONS - What Affects Human Score Most")
    print("="*80)
    
    if args.material:
        print(f"\n📦 Material: {args.material}")
    if args.component:
        print(f"📝 Component: {args.component}")
    
    print("\n" + "-"*80)
    print(f"{'Parameter':<35} {'Correlation':<15} {'Impact'}")
    print("-"*80)
    
    for param_name, correlation in correlations:
        # Interpret correlation
        abs_corr = abs(correlation)
        if abs_corr > 0.7:
            strength = "VERY STRONG"
            emoji = "🔥"
        elif abs_corr > 0.5:
            strength = "STRONG"
            emoji = "⚡"
        elif abs_corr > 0.3:
            strength = "MODERATE"
            emoji = "📈" if correlation > 0 else "📉"
        else:
            strength = "WEAK"
            emoji = "〰️"
        
        direction = "Increase helps" if correlation > 0 else "Decrease helps"
        
        print(
            f"{param_name:<35} {correlation:>6.3f} ({abs_corr:.0%})    "
            f"{emoji} {strength} - {direction}"
        )
    
    print("-"*80)
    print("\nLegend:")
    print("  • Positive correlation (+): Increasing parameter improves human score")
    print("  • Negative correlation (−): Decreasing parameter improves human score")
    print("  • |0.7+|: Very strong relationship")
    print("  • |0.5-0.7|: Strong relationship")
    print("  • |0.3-0.5|: Moderate relationship")
    print("  • |<0.3|: Weak relationship")
    
    print("\n" + "="*80 + "\n")


def show_full_analysis(analyzer, args):
    """Display comprehensive sweet spot analysis."""
    analysis = analyzer.get_sweet_spot_table(
        material=args.material,
        component_type=args.component
    )
    
    print("\n" + "="*80)
    print("🔬 COMPREHENSIVE SWEET SPOT ANALYSIS")
    print("="*80)
    
    metadata = analysis['metadata']
    print(f"\n📋 Analysis Scope:")
    print(f"   • Material: {metadata['material']}")
    print(f"   • Component: {metadata['component_type']}")
    print(f"   • Samples: {metadata['sample_count']}")
    
    # Show recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in analysis['recommendations']:
        print(f"   {rec}")
    
    # Show top correlations
    if analysis['parameter_correlations']:
        print(f"\n📊 TOP PARAMETER CORRELATIONS:")
        for corr in analysis['parameter_correlations'][:5]:
            print(
                f"   • {corr['parameter']:<30} "
                f"{'▲' if corr['correlation'] > 0 else '▼'} "
                f"{corr['correlation']:>6.3f}"
            )
    
    # Show best achievement
    if analysis['maximum_achievements']:
        best = analysis['maximum_achievements'][0]
        print(f"\n🏆 BEST ACHIEVEMENT:")
        print(f"   • Material: {best['material']}")
        print(f"   • Component: {best['component_type']}")
        print(f"   • Human Score: {best['max_human_score']:.2f}%")
        if best['max_claude_score']:
            print(f"   • Claude Score: {best['max_claude_score']:.2f}/10")
    
    # Show sweet spot summary
    sweet_spots = analysis['sweet_spots']
    if sweet_spots:
        high_conf = sum(1 for ss in sweet_spots.values() if ss['confidence'] == 'high')
        med_conf = sum(1 for ss in sweet_spots.values() if ss['confidence'] == 'medium')
        low_conf = sum(1 for ss in sweet_spots.values() if ss['confidence'] == 'low')
        
        print(f"\n🎯 SWEET SPOT SUMMARY:")
        print(f"   • Total parameters analyzed: {len(sweet_spots)}")
        print(f"   • High confidence: {high_conf}")
        print(f"   • Medium confidence: {med_conf}")
        print(f"   • Low confidence: {low_conf}")
    
    print("\n" + "="*80 + "\n")
    
    # Option to save to file
    if args.save:
        output_file = Path(args.save)
        output_file.write_text(json.dumps(analysis, indent=2))
        print(f"✅ Full analysis saved to: {output_file}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze optimal parameter ranges from Winston feedback"
    )
    
    # Filters
    parser.add_argument(
        '--material',
        type=str,
        help='Filter by specific material'
    )
    parser.add_argument(
        '--component',
        type=str,
        help='Filter by component type (caption, subtitle, etc.)'
    )
    
    # Analysis modes
    parser.add_argument(
        '--sweet-spots',
        action='store_true',
        help='Show optimal parameter ranges'
    )
    parser.add_argument(
        '--maximums',
        action='store_true',
        help='Show best ever achievements'
    )
    parser.add_argument(
        '--correlations',
        action='store_true',
        help='Show parameter correlations with human score'
    )
    
    # Options
    parser.add_argument(
        '--top-percent',
        type=int,
        default=25,
        help='Consider top N%% of successful generations (default: 25)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Number of maximum achievements to show (default: 10)'
    )
    parser.add_argument(
        '--min-samples',
        type=int,
        default=10,
        help='Minimum samples needed for analysis (default: 10)'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=50.0,
        help='Minimum human score to consider successful (default: 50.0)'
    )
    parser.add_argument(
        '--save',
        type=str,
        help='Save full analysis to JSON file'
    )
    
    args = parser.parse_args()
    
    # Get database path from config
    config = get_config()
    db_path = getattr(config, 'winston_feedback_db_path', 'data/winston_feedback.db')
    
    # Initialize analyzer
    analyzer = SweetSpotAnalyzer(
        db_path=db_path,
        min_samples=args.min_samples,
        success_threshold=args.threshold
    )
    
    # Determine what to show
    show_something = (
        args.sweet_spots or 
        args.maximums or 
        args.correlations
    )
    
    if not show_something:
        # Default: show full analysis
        show_full_analysis(analyzer, args)
    else:
        # Show specific requested analyses
        if args.sweet_spots:
            show_sweet_spots(analyzer, args)
        
        if args.maximums:
            show_maximums(analyzer, args)
        
        if args.correlations:
            show_correlations(analyzer, args)


if __name__ == '__main__':
    main()
