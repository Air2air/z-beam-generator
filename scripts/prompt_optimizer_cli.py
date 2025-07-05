#!/usr/bin/env python3
"""
Command-line tool for managing prompt optimization.
"""

import argparse
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from generator.core.application import Application


def main():
    """Main entry point for prompt optimization CLI."""
    parser = argparse.ArgumentParser(
        description="Prompt Optimization Tool for Z-Beam Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python prompt_optimizer_cli.py report              # Show performance report
  python prompt_optimizer_cli.py analyze ai          # Analyze AI prompt patterns
  python prompt_optimizer_cli.py generate ai         # Generate optimized AI prompt
  python prompt_optimizer_cli.py save human          # Save optimized human prompt
  python prompt_optimizer_cli.py test ai 3           # Test AI prompts for 3 iterations
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Report command
    subparsers.add_parser("report", help="Show comprehensive performance report")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze prompt patterns")
    analyze_parser.add_argument(
        "type", choices=["ai", "human", "all"], help="Type of prompts to analyze"
    )

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate optimized prompt"
    )
    generate_parser.add_argument(
        "type", choices=["ai", "human"], help="Type of prompt to generate"
    )
    generate_parser.add_argument(
        "--preview", action="store_true", help="Preview without saving"
    )

    # Save command
    save_parser = subparsers.add_parser(
        "save", help="Generate and save optimized prompt"
    )
    save_parser.add_argument(
        "type", choices=["ai", "human"], help="Type of prompt to save"
    )

    # Test command
    test_parser = subparsers.add_parser(
        "test", help="Test prompt selection with sample content"
    )
    test_parser.add_argument(
        "type", choices=["ai", "human", "both"], help="Type of detection to test"
    )
    test_parser.add_argument(
        "iterations",
        type=int,
        nargs="?",
        default=3,
        help="Number of iterations to test (default: 3)",
    )

    # Clear command
    subparsers.add_parser("clear", help="Clear performance data (use with caution)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        # Initialize application
        app = Application()
        app.initialize()
        from generator.core.interfaces.services import IDetectionService

        detection_service = app.container.get(IDetectionService)

        if args.command == "report":
            show_report(detection_service)

        elif args.command == "analyze":
            analyze_patterns(detection_service, args.type)

        elif args.command == "generate":
            generate_prompt(detection_service, args.type, args.preview)

        elif args.command == "save":
            save_prompt(detection_service, args.type)

        elif args.command == "test":
            test_prompts(detection_service, args.type, args.iterations)

        elif args.command == "clear":
            clear_data(detection_service)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def show_report(detection_service):
    """Show comprehensive performance report."""
    print("📊 Prompt Performance Report")
    print("=" * 50)
    report = detection_service.get_performance_report()
    print(report)


def analyze_patterns(detection_service, prompt_type):
    """Analyze prompt patterns."""
    print(f"🔍 Analyzing {prompt_type.upper()} Prompt Patterns")
    print("=" * 50)

    if prompt_type == "all":
        for ptype in ["ai", "human"]:
            print(f"\n📋 {ptype.upper()} Detection Analysis:")
            print("-" * 30)
            analysis = detection_service.get_optimization_analysis(ptype)
            print_analysis(analysis)
    else:
        analysis = detection_service.get_optimization_analysis(prompt_type)
        print_analysis(analysis)


def print_analysis(analysis):
    """Print analysis results."""
    if analysis["top_performers"]:
        print("🏆 Top Performers:")
        for i, perf in enumerate(analysis["top_performers"], 1):
            print(f"  {i}. {perf['prompt']}")
            print(f"     Success Rate: {perf['success_rate']:.1%}")
            print(f"     Average Score: {perf['avg_score']:.1f}")
            print(f"     Uses: {perf['uses']}")
    else:
        print("   No sufficient performance data yet")

    if analysis["worst_performers"]:
        print("\n📉 Needs Improvement:")
        for perf in analysis["worst_performers"]:
            print(f"  • {perf['prompt']} (Success: {perf['success_rate']:.1%})")

    if analysis["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in analysis["recommendations"]:
            print(f"  • {rec}")


def generate_prompt(detection_service, prompt_type, preview_only=False):
    """Generate optimized prompt."""
    print(f"🚀 Generating Optimized {prompt_type.upper()} Detection Prompt")
    print("=" * 60)

    try:
        content, filename = detection_service.generate_optimized_prompt(prompt_type)

        print(f"📄 Generated: {filename}")
        print("─" * 50)
        print(content)
        print("─" * 50)

        if not preview_only:
            save_path = f"generator/prompts/detection/{filename}"
            response = input(f"\nSave to {save_path}? (y/N): ").strip().lower()
            if response in ["y", "yes"]:
                with open(save_path, "w") as f:
                    f.write(content)
                print(f"✅ Saved to {save_path}")
            else:
                print("❌ Not saved")

    except Exception as e:
        print(f"❌ Failed to generate prompt: {e}")


def save_prompt(detection_service, prompt_type):
    """Generate and save optimized prompt."""
    print(f"💾 Saving Optimized {prompt_type.upper()} Detection Prompt")
    print("=" * 50)

    try:
        saved_path = detection_service.save_optimized_prompt(prompt_type)
        print(f"✅ Saved optimized prompt: {saved_path}")
        print("📋 Prompt has been added to available variations")
    except Exception as e:
        print(f"❌ Failed to save prompt: {e}")


def test_prompts(detection_service, prompt_type, iterations):
    """Test prompt selection with sample content."""
    print(f"🧪 Testing {prompt_type.upper()} Prompt Selection")
    print(f"Iterations: {iterations}")
    print("=" * 50)

    from generator.core.domain.models import GenerationContext

    # Sample content that typically scores high for AI
    test_content = """
    Laser cleaning technology represents a significant advancement in industrial cleaning processes. 
    This innovative approach utilizes precisely controlled laser beams to effectively remove various 
    contaminants from surfaces without causing damage to the underlying material. The process offers 
    numerous advantages including environmental sustainability, cost-effectiveness, and superior 
    precision compared to traditional chemical or abrasive cleaning methods. Industries across 
    multiple sectors are increasingly adopting this technology for applications ranging from 
    heritage restoration to routine industrial maintenance operations.
    """

    context = GenerationContext(
        material="test_material",
        content_type="article_section",
        variables={"section_name": "prompt_test"},
    )

    print(f"📝 Test Content: {len(test_content)} characters")
    print(f"Preview: {test_content[:100]}...")
    print()

    if prompt_type in ["ai", "both"]:
        print("🤖 AI Detection Test:")
        print("-" * 20)
        for i in range(1, iterations + 1):
            result = detection_service.detect_ai_likelihood(test_content, context, i)
            print(f"  Iteration {i}: {result.score}%")
        print()

    if prompt_type in ["human", "both"]:
        print("👤 Human Detection Test:")
        print("-" * 23)
        for i in range(1, iterations + 1):
            result = detection_service.detect_human_likelihood(test_content, context, i)
            print(f"  Iteration {i}: {result.score}%")

    print("\n✅ Test completed. Performance data updated.")


def clear_data(detection_service):
    """Clear performance data."""
    print("⚠️  Clear Performance Data")
    print("=" * 25)
    print("This will permanently delete all prompt performance tracking data.")

    response = input("Are you sure? Type 'DELETE' to confirm: ").strip()
    if response == "DELETE":
        try:
            # Get the optimizer and clear data
            optimizer = detection_service._optimizer
            optimizer.performance_data = {}
            optimizer._save_performance_data()
            print("✅ Performance data cleared")
        except Exception as e:
            print(f"❌ Failed to clear data: {e}")
    else:
        print("❌ Operation cancelled")


if __name__ == "__main__":
    main()
