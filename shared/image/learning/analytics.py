#!/usr/bin/env python3
"""
Image Generation Analytics CLI

View analytics and insights from image generation learning database.

Usage:
    python3 domains/materials/image/learning/analytics.py --report
    python3 domains/materials/image/learning/analytics.py --category wood_hardwood
    python3 domains/materials/image/learning/analytics.py --physics-violations
    python3 domains/materials/image/learning/analytics.py --feedback-effectiveness
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.image.learning import create_logger


def main():
    parser = argparse.ArgumentParser(
        description="View image generation analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Show comprehensive analytics report'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        help='Show stats for specific material category'
    )
    
    parser.add_argument(
        '--physics-violations',
        action='store_true',
        help='Show most common physics violations'
    )
    
    parser.add_argument(
        '--feedback-effectiveness',
        action='store_true',
        help='Compare success rates before/after feedback'
    )
    
    parser.add_argument(
        '--truncation-impact',
        action='store_true',
        help='Analyze impact of prompt truncation'
    )
    
    parser.add_argument(
        '--recent',
        type=int,
        metavar='N',
        help='Show N most recent attempts'
    )
    
    parser.add_argument(
        '--feedback-patterns',
        action='store_true',
        help='Show which feedback categories are most effective'
    )
    
    parser.add_argument(
        '--search-feedback',
        type=str,
        metavar='TERM',
        help='Search feedback text for specific keywords'
    )
    
    parser.add_argument(
        '--best-feedback',
        type=str,
        nargs='?',
        const=True,
        metavar='CATEGORY',
        help='Show examples of successful feedback (optionally filtered by category)'
    )
    
    # Phase 2: Learned defaults commands
    parser.add_argument(
        '--learned-defaults',
        action='store_true',
        help='Show learned default parameters per category'
    )
    
    parser.add_argument(
        '--pattern-effectiveness',
        action='store_true',
        help='Show which contamination patterns work best'
    )
    
    parser.add_argument(
        '--context-stats',
        action='store_true',
        help='Show success rates by environmental context'
    )
    
    parser.add_argument(
        '--suggest',
        type=str,
        metavar='CATEGORY',
        help='Get suggested parameters for a category'
    )
    
    parser.add_argument(
        '--seed-defaults',
        action='store_true',
        help='Seed learned_defaults table from CATEGORY_DEFAULTS'
    )
    
    parser.add_argument(
        '--manual-feedback',
        action='store_true',
        help='Show manual feedback statistics and recent entries'
    )
    
    args = parser.parse_args()
    
    # Create logger
    logger = create_logger()
    
    # Show comprehensive report if requested or no specific flags
    if args.report or not any([args.category, args.physics_violations, 
                                args.feedback_effectiveness, args.truncation_impact,
                                args.recent, args.feedback_patterns, 
                                args.search_feedback, args.best_feedback,
                                args.learned_defaults, args.pattern_effectiveness,
                                args.context_stats, args.suggest, args.seed_defaults,
                                args.manual_feedback]):
        logger.print_analytics_report()
        return
    
    # Category stats
    if args.category:
        stats = logger.get_category_stats(args.category)
        print(f"\n📊 STATS FOR: {stats['category']}")
        print("=" * 70)
        print(f"   Total attempts: {stats['total_attempts']}")
        print(f"   Passed: {stats['passed']} ({stats['success_rate']:.1f}%)")
        print(f"   Failed: {stats['failed']}")
        print(f"   Average score: {stats['avg_realism_score']}/100")
        print(f"   Avg gen prompt: {stats['avg_gen_prompt_length']} chars")
        print(f"   Avg val prompt: {stats['avg_val_prompt_length']} chars")
        
        if stats['common_physics_issues']:
            print(f"\n   Common physics issues:")
            for issue in stats['common_physics_issues']:
                print(f"     • {issue['issue']}: {issue['count']} times")
    
    # Physics violations
    if args.physics_violations:
        violations = logger.get_common_physics_violations(10)
        print("\n🚨 MOST COMMON PHYSICS VIOLATIONS")
        print("=" * 70)
        for item in violations:
            print(f"   • {item['issue']}")
            print(f"     Count: {item['count']}, {item['percentage']:.1f}% of all failures")
    
    # Feedback effectiveness
    if args.feedback_effectiveness:
        feedback = logger.get_feedback_effectiveness()
        print("\n📈 FEEDBACK EFFECTIVENESS")
        print("=" * 70)
        print(f"\n   BEFORE FEEDBACK:")
        print(f"     • Attempts: {feedback['before_feedback']['total']}")
        print(f"     • Pass rate: {feedback['before_feedback']['success_rate']:.1f}%")
        print(f"     • Avg score: {feedback['before_feedback']['avg_score']}/100")
        
        print(f"\n   AFTER FEEDBACK:")
        print(f"     • Attempts: {feedback['after_feedback']['total']}")
        print(f"     • Pass rate: {feedback['after_feedback']['success_rate']:.1f}%")
        print(f"     • Avg score: {feedback['after_feedback']['avg_score']}/100")
        
        print(f"\n   IMPROVEMENT:")
        print(f"     • Pass rate: {feedback['improvement']['success_rate_delta']:+.1f}%")
        print(f"     • Avg score: {feedback['improvement']['avg_score_delta']:+.1f} points")
    
    # Truncation impact
    if args.truncation_impact:
        trunc = logger.get_prompt_truncation_impact()
        print("\n⚠️  PROMPT TRUNCATION IMPACT")
        print("=" * 70)
        print(f"\n   NON-TRUNCATED PROMPTS:")
        print(f"     • Attempts: {trunc['non_truncated']['total']}")
        print(f"     • Pass rate: {trunc['non_truncated']['success_rate']:.1f}%")
        print(f"     • Avg score: {trunc['non_truncated']['avg_score']}/100")
        
        print(f"\n   TRUNCATED PROMPTS:")
        print(f"     • Attempts: {trunc['truncated']['total']}")
        print(f"     • Pass rate: {trunc['truncated']['success_rate']:.1f}%")
        print(f"     • Avg score: {trunc['truncated']['avg_score']}/100")
    
    # Recent attempts
    if args.recent:
        attempts = logger.get_recent_attempts(args.recent)
        print(f"\n📝 RECENT {args.recent} ATTEMPTS")
        print("=" * 70)
        for attempt in attempts:
            status = "✅ PASS" if attempt['passed'] else "❌ FAIL"
            print(f"\n   {attempt['material']} ({attempt['category']})")
            print(f"     • Score: {attempt['realism_score']}/100 {status}")
            print(f"     • Time: {attempt['timestamp']}")
            if attempt['physics_issues']:
                print(f"     • Issues: {', '.join(attempt['physics_issues'][:2])}")
    
    # Feedback patterns
    if args.feedback_patterns:
        patterns = logger.get_feedback_patterns(10)
        print("\n💡 FEEDBACK EFFECTIVENESS BY CATEGORY")
        print("=" * 70)
        if patterns:
            for pattern in patterns:
                print(f"\n   {pattern['category'].upper()}")
                print(f"     • Used: {pattern['usage_count']} times")
                print(f"     • Success rate: {pattern['success_rate']:.1f}%")
                print(f"     • Avg score: {pattern['avg_score']}/100")
        else:
            print("\n   No feedback patterns found yet.")
            print("   Start logging feedback with category tags to track effectiveness.")
    
    # Search feedback
    if args.search_feedback:
        results = logger.search_feedback(args.search_feedback)
        print(f"\n🔍 SEARCH RESULTS FOR: '{args.search_feedback}'")
        print("=" * 70)
        if results:
            for result in results:
                status = "✅ PASS" if result['passed'] else "❌ FAIL"
                print(f"\n   {result['material']} - {result['realism_score']}/100 {status}")
                print(f"     • Category: {result['feedback_category']}")
                print(f"     • Feedback: \"{result['feedback_text'][:100]}...\"" if len(result['feedback_text']) > 100 else f"     • Feedback: \"{result['feedback_text']}\"")
                print(f"     • Time: {result['timestamp']}")
        else:
            print(f"\n   No feedback found containing '{args.search_feedback}'")
    
    # Best feedback examples
    if args.best_feedback:
        category = args.best_feedback if isinstance(args.best_feedback, str) else None
        examples = logger.get_best_feedback_examples(category=category, limit=5)
        
        if category:
            print(f"\n🌟 BEST FEEDBACK EXAMPLES: {category.upper()}")
        else:
            print("\n🌟 BEST FEEDBACK EXAMPLES (ALL CATEGORIES)")
        print("=" * 70)
        
        if examples:
            for ex in examples:
                print(f"\n   {ex['material']} - {ex['realism_score']}/100 ✅")
                print(f"     • Category: {ex['feedback_category']}")
                print(f"     • Feedback: \"{ex['feedback_text']}\"")
                print(f"     • Time: {ex['timestamp']}")
        else:
            print("\n   No successful feedback examples found yet.")
            print("   Keep generating with feedback to build this knowledge base!")
    
    # Learned defaults report
    if args.learned_defaults:
        logger.print_learned_defaults_report()
    
    # Pattern effectiveness
    if args.pattern_effectiveness:
        patterns = logger.get_pattern_effectiveness(15)
        print("\n🎯 PATTERN EFFECTIVENESS (by success rate)")
        print("=" * 70)
        if patterns:
            print(f"\n   {'Pattern':<30} {'Uses':<8} {'Success':<10} {'AvgScore':<10}")
            print("   " + "-" * 60)
            for p in patterns:
                print(f"   {p['pattern']:<30} {p['total']:<8} {p['success_rate']:.1f}%{'':5} {p['avg_score']:.1f}")
        else:
            print("\n   No pattern data yet. Run some generations first.")
    
    # Context stats
    if args.context_stats:
        stats = logger.get_context_effectiveness()
        print("\n🌍 CONTEXT EFFECTIVENESS")
        print("=" * 70)
        print(f"\n   {'Context':<15} {'Attempts':<10} {'Success':<10} {'AvgScore':<10} {'AvgAging':<10} {'AvgContam':<10}")
        print("   " + "-" * 65)
        for ctx, data in stats.items():
            if data['total'] > 0:
                aging = f"{data['avg_aging_weight']:.2f}" if data['avg_aging_weight'] else "N/A"
                contam = f"{data['avg_contamination_weight']:.2f}" if data['avg_contamination_weight'] else "N/A"
                print(f"   {ctx:<15} {data['total']:<10} {data['success_rate']:.1f}%{'':5} {data['avg_score']:<10.1f} {aging:<10} {contam:<10}")
        
        # Best category+context combos
        combos = logger.get_category_context_stats(5)
        if combos:
            print("\n   🏆 BEST CATEGORY+CONTEXT COMBINATIONS:")
            for c in combos:
                print(f"      • {c['category']} + {c['context']}: {c['success_rate']:.1f}% ({c['total']} attempts)")
    
    # Suggest parameters
    if args.suggest:
        category = args.suggest
        print(f"\n💡 SUGGESTED PARAMETERS FOR: {category}")
        print("=" * 70)
        
        # Get learned defaults
        defaults = logger.get_learned_defaults(category, 'outdoor')
        if defaults:
            sample_count = defaults.get('sample_count', 0)
            if sample_count > 0:
                print(f"\n   📊 From {sample_count} samples, avg score {defaults['avg_score']:.1f}:")
            else:
                print(f"\n   📋 Baseline defaults (not yet learned from generations):")
            print(f"      • guidance_scale: {defaults['guidance_scale']:.1f}")
            if defaults.get('aging_weight'):
                print(f"      • aging_weight: {defaults['aging_weight']:.2f}")
            if defaults.get('contamination_weight'):
                print(f"      • contamination_weight: {defaults['contamination_weight']:.2f}")
        else:
            print("\n   ⚠️  No defaults found for this category.")
        
        # Suggested threshold
        threshold = logger.get_suggested_threshold(category, 'outdoor')
        print(f"\n   🎯 Suggested pass_threshold: {threshold:.1f}")
        
        # Best patterns
        patterns = logger.get_best_patterns_for_category(category, 'outdoor', limit=5, min_uses=1)
        if patterns:
            print(f"\n   ✨ Best patterns for {category}:")
            for p in patterns:
                print(f"      • {p['pattern_id']}: {p['success_rate']:.0f}% success, {p['avg_score']:.1f} avg ({p['total_uses']} uses)")
        
        # Optimal guidance scale from successes
        optimal_scale = logger.get_optimal_guidance_scale(category)
        if optimal_scale:
            print(f"\n   ⚙️  Optimal guidance_scale (from successes): {optimal_scale}")
    
    # Seed defaults from CATEGORY_DEFAULTS
    if args.seed_defaults:
        print("\n🌱 SEEDING LEARNED DEFAULTS FROM CATEGORY_DEFAULTS")
        print("=" * 70)
        try:
            from domains.materials.image.material_config import CATEGORY_DEFAULTS

            # Use force_update=True to migrate existing rows with view_mode
            count = logger.seed_defaults_from_config(CATEGORY_DEFAULTS, force_update=True)
            print(f"\n   ✅ Seeded/updated {count} category defaults")
            print("   Run --learned-defaults to view them.")
        except ImportError as e:
            print(f"\n   ❌ Failed to import CATEGORY_DEFAULTS: {e}")
    
    # Manual feedback statistics
    if args.manual_feedback:
        print("\n👤 MANUAL FEEDBACK ANALYSIS")
        print("=" * 70)
        
        import sqlite3
        conn = sqlite3.connect(logger.db_path)
        cursor = conn.cursor()
        
        # Get stats by category
        cursor.execute("""
            SELECT feedback_category, COUNT(*) as count
            FROM generation_attempts
            WHERE feedback_source = 'user_manual'
            GROUP BY feedback_category
            ORDER BY count DESC
        """)
        cat_stats = cursor.fetchall()
        
        # Get recent entries
        cursor.execute("""
            SELECT timestamp, material, feedback_category, feedback_text
            FROM generation_attempts
            WHERE feedback_source = 'user_manual'
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        recent = cursor.fetchall()
        
        # Get total count
        cursor.execute("""
            SELECT COUNT(*) FROM generation_attempts WHERE feedback_source = 'user_manual'
        """)
        total = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\n   Total manual feedback entries: {total}")
        
        if cat_stats:
            print("\n   📊 BY CATEGORY:")
            for cat, count in cat_stats:
                pct = count / total * 100 if total > 0 else 0
                print(f"      • {cat or 'uncategorized':<15} {count:3} ({pct:.1f}%)")
        
        if recent:
            print("\n   📋 RECENT ENTRIES:")
            for ts, mat, cat, text in recent:
                ts_short = ts[:16] if ts else "?"
                text_short = text[:60] + "..." if len(text or '') > 60 else text
                print(f"      [{ts_short}] {mat} ({cat})")
                print(f"         → {text_short}")
        
        print("\n   💡 Add feedback: python3 domains/materials/image/tools/add_feedback.py -m <material> -f '<text>'")
        print("=" * 70)


if __name__ == "__main__":
    main()

