#!/usr/bin/env python3
"""
Winston Learning System - CLI Tool

Comprehensive tool for analyzing and learning from Winston AI feedback.
Uses machine learning to dynamically improve content generation.

Features:
- Pattern learning: Identify problematic phrases
- Temperature optimization: Find optimal settings
- Prompt enhancement: Auto-generate improved prompts
- Success prediction: Predict outcomes before generation
- Risk assessment: Evaluate material/component combinations

Usage:
    # Learn patterns for all materials
    python3 scripts/winston/learn.py --patterns
    
    # Get optimal temperature for specific material
    python3 scripts/winston/learn.py --temperature --material "Aluminum" --component caption
    
    # Optimize prompt with learned patterns
    python3 scripts/winston/learn.py --optimize-prompt prompts/caption.txt --material "Aluminum"
    
    # Predict success before generating
    python3 scripts/winston/learn.py --predict --material "Steel" --component subtitle --temp 0.7
    
    # Full learning dashboard
    python3 scripts/winston/learn.py --dashboard
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from learning.pattern_learner import PatternLearner
from learning.temperature_advisor import TemperatureAdvisor
from learning.prompt_optimizer import PromptOptimizer
from learning.success_predictor import SuccessPredictor
from generation.config.config_loader import get_config

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def learn_patterns(args, db_path):
    """Learn problematic patterns from Winston feedback."""
    learner = PatternLearner(db_path)
    
    result = learner.learn_patterns(
        material=args.material,
        component_type=args.component
    )
    
    print("\n" + "="*70)
    print("PATTERN LEARNING RESULTS")
    print("="*70 + "\n")
    
    print(f"📊 Total samples analyzed: {result['stats']['total_samples']}")
    print(f"   • Success: {result['stats']['success_samples']}")
    print(f"   • Failed: {result['stats']['failed_samples']}")
    print(f"   • Unique patterns found: {result['stats']['unique_patterns']}")
    
    if result['risky_patterns']:
        print(f"\n🚨 TOP {len(result['risky_patterns'])} RISKY PATTERNS:\n")
        for i, p in enumerate(result['risky_patterns'], 1):
            print(f"{i}. \"{p['pattern']}\"")
            print(f"   Fail rate: {p['fail_rate']:.0%} ({p['occurrences']} occurrences)")
            print(f"   Avg human score when present: {p['avg_score']:.1f}%")
            print(f"   Risk level: {p['risk_level']}\n")
    
    if result['safe_patterns']:
        print(f"✅ TOP {len(result['safe_patterns'])} SAFE PATTERNS:\n")
        for i, p in enumerate(result['safe_patterns'][:5], 1):
            print(f"{i}. \"{p['pattern']}\"")
            print(f"   Success rate: {p['success_rate']:.0%} ({p['occurrences']} occurrences)")
            print(f"   Avg human score: {p['avg_score']:.1f}%\n")
    
    if result['recommendations']:
        print("💡 RECOMMENDATIONS:\n")
        for rec in result['recommendations']:
            print(f"  {rec}")
    
    print("\n" + "-"*70 + "\n")


def optimize_temperature(args, db_path):
    """Find optimal temperature settings."""
    advisor = TemperatureAdvisor(db_path)
    
    result = advisor.get_optimal_temperature(
        material=args.material,
        component_type=args.component
    )
    
    print("\n" + "="*70)
    print("TEMPERATURE OPTIMIZATION")
    print("="*70 + "\n")
    
    if result.get('confidence') == 'none':
        print(f"⚠️  {result.get('reason', 'Insufficient data')}")
        print(f"   Samples needed: {result.get('sample_size', 0)}/{advisor.min_samples}")
        return
    
    print(f"🎯 RECOMMENDED TEMPERATURE: {result['recommended_temp']:.2f}")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Expected success rate: {result['success_rate']:.0%}")
    print(f"   Expected human score: {result['avg_human_score']:.1f}%")
    print(f"   Score stability: {result['score_stability']:.2f}")
    print(f"   Based on {result['sample_size']} samples\n")
    
    if 'analysis' in result:
        print("📊 Temperature Performance Analysis:\n")
        for i, temp_data in enumerate(result['analysis'], 1):
            print(f"{i}. Temperature {temp_data['temperature']:.2f}")
            print(f"   Success rate: {temp_data['success_rate']:.0%}")
            print(f"   Avg human score: {temp_data['avg_human_score']:.1f}%")
            print(f"   Samples: {temp_data['sample_size']}")
            print(f"   Composite score: {temp_data['composite_score']:.3f}\n")
    
    print("-"*70 + "\n")


def optimize_prompt(args, db_path):
    """Enhance prompt with learned patterns."""
    optimizer = PromptOptimizer(db_path)
    
    # Read base prompt
    prompt_path = Path(args.prompt_file)
    if not prompt_path.exists():
        logger.error(f"Prompt file not found: {args.prompt_file}")
        sys.exit(1)
    
    base_prompt = prompt_path.read_text()
    
    result = optimizer.optimize_prompt(
        base_prompt,
        material=args.material,
        component_type=args.component
    )
    
    print("\n" + "="*70)
    print("PROMPT OPTIMIZATION")
    print("="*70 + "\n")
    
    if result.get('confidence') == 'none':
        print(f"⚠️  {result.get('reason', 'Insufficient data')}")
        return
    
    print(f"✅ OPTIMIZATION COMPLETE")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Expected improvement: {result['expected_improvement']:.0%}")
    print(f"   Patterns analyzed: {result['patterns_analyzed']}\n")
    
    print("📝 Additions made:")
    for addition in result['additions']:
        print(f"   • {addition}")
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(result['optimized_prompt'])
        print(f"\n💾 Saved optimized prompt to: {args.output}")
    else:
        print("\n" + "="*70)
        print("OPTIMIZED PROMPT")
        print("="*70 + "\n")
        print(result['optimized_prompt'])
    
    print("\n" + "-"*70 + "\n")


def predict_success(args, db_path):
    """Predict success of generation before running."""
    predictor = SuccessPredictor(db_path)
    
    result = predictor.predict_success(
        material=args.material,
        component_type=args.component,
        temperature=args.temp,
        attempt_number=args.attempt
    )
    
    print("\n" + "="*70)
    print("SUCCESS PREDICTION")
    print("="*70 + "\n")
    
    print(f"🎯 PREDICTION FOR: {args.material} / {args.component}")
    print(f"   Temperature: {args.temp:.2f}")
    print(f"   Attempt: {args.attempt}\n")
    
    print(f"📊 SUCCESS PROBABILITY: {result['success_probability']:.0%}")
    print(f"   Expected human score: {result['expected_human_score']:.1f}%")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Sample size: {result['sample_size']}\n")
    
    print(f"💡 RECOMMENDATION: {result['recommendation']}")
    print(f"   Reasoning: {result['reasoning']}\n")
    
    if result['suggested_adjustments']:
        print("🔧 Suggested Adjustments:")
        for adj in result['suggested_adjustments']:
            print(f"   {adj}")
    
    print("\n" + "-"*70 + "\n")


def show_dashboard(db_path):
    """Show comprehensive learning dashboard."""
    learner = PatternLearner(db_path)
    advisor = TemperatureAdvisor(db_path)
    optimizer = PromptOptimizer(db_path)
    
    print("\n" + "="*70)
    print("WINSTON LEARNING SYSTEM - DASHBOARD")
    print("="*70 + "\n")
    
    # Overall statistics
    patterns = learner.learn_patterns()
    print(f"📊 OVERALL STATISTICS")
    print(f"   Total samples: {patterns['stats']['total_samples']}")
    if patterns['stats']['total_samples'] > 0:
        print(f"   Success rate: {patterns['stats']['success_samples'] / patterns['stats']['total_samples']:.0%}")
        print(f"   Risky patterns identified: {patterns['stats'].get('risky_patterns_found', 0)}")
        print(f"   Safe patterns identified: {patterns['stats'].get('safe_patterns_found', 0)}\n")
    else:
        print(f"   Status: No data yet - generate content to populate database\n")
    
    # Top issues
    if patterns['risky_patterns']:
        print("🚨 TOP 5 ISSUES TO ADDRESS:")
        for i, p in enumerate(patterns['risky_patterns'][:5], 1):
            print(f"   {i}. \"{p['pattern']}\" (fails {p['fail_rate']:.0%})")
    
    # Prompt effectiveness
    print("\n📝 PROMPT EFFECTIVENESS:")
    report = optimizer.get_prompt_effectiveness_report()
    if report['status'] == 'analyzed':
        print(f"   Overall success rate: {report['success_rate']:.0%}")
        print(f"   High-risk patterns: {report['high_risk_patterns']}")
        print(f"   Medium-risk patterns: {report['medium_risk_patterns']}")
        for rec in report['recommendations'][:3]:
            print(f"   {rec}")
    else:
        print(f"   {report['message']}")
    
    print("\n" + "-"*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Winston Learning System - Dynamic learning from AI feedback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Learning modes
    parser.add_argument(
        '--patterns',
        action='store_true',
        help="Learn problematic patterns"
    )
    
    parser.add_argument(
        '--temperature',
        action='store_true',
        help="Optimize temperature settings"
    )
    
    parser.add_argument(
        '--optimize-prompt',
        metavar='FILE',
        help="Optimize prompt file with learned patterns"
    )
    
    parser.add_argument(
        '--predict',
        action='store_true',
        help="Predict success before generating"
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help="Show comprehensive learning dashboard"
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
        choices=['caption', 'subtitle', 'faq'],
        help="Filter by component type"
    )
    
    parser.add_argument(
        '--temp',
        type=float,
        default=0.7,
        help="Temperature for prediction (default: 0.7)"
    )
    
    parser.add_argument(
        '--attempt',
        type=int,
        default=1,
        help="Attempt number for prediction (default: 1)"
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help="Output file for optimized prompt"
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
    
    # Run appropriate mode
    if args.dashboard:
        show_dashboard(db_path)
    elif args.patterns:
        learn_patterns(args, db_path)
    elif args.temperature:
        optimize_temperature(args, db_path)
    elif args.optimize_prompt:
        args.prompt_file = args.optimize_prompt
        optimize_prompt(args, db_path)
    elif args.predict:
        if not args.material or not args.component:
            logger.error("--predict requires --material and --component")
            sys.exit(1)
        predict_success(args, db_path)
    else:
        # Default: show dashboard
        show_dashboard(db_path)


if __name__ == '__main__':
    main()
