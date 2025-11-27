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

from domains.materials.image.learning import create_logger


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
    
    args = parser.parse_args()
    
    # Create logger
    logger = create_logger()
    
    # Show comprehensive report if requested or no specific flags
    if args.report or not any([args.category, args.physics_violations, 
                                args.feedback_effectiveness, args.truncation_impact,
                                args.recent, args.feedback_patterns, 
                                args.search_feedback, args.best_feedback]):
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


if __name__ == "__main__":
    main()

