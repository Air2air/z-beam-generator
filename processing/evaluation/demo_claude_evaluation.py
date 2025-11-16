#!/usr/bin/env python3
"""
Claude Evaluation Demo

Demonstrates the Claude subjective evaluation module in action.
Shows both basic usage and integration with generation workflows.
"""

from processing.evaluation.subjective_evaluator import evaluate_content
from shared.commands.claude_evaluation_helper import evaluate_after_generation


def demo_basic_evaluation():
    """Demo basic evaluation functionality"""
    
    print("=" * 70)
    print("DEMO: Basic Claude Evaluation")
    print("=" * 70)
    print()
    
    # Sample caption
    caption = """
    Aluminum oxide coatings accumulate rapidly on aluminum surfaces exposed to 
    industrial environments, forming a persistent layer that affects thermal 
    conductivity. Laser cleaning removes these layers through selective ablation, 
    targeting the oxide while preserving the base metal integrity.
    """
    
    # Evaluate
    result = evaluate_content(
        content=caption.strip(),
        material_name="Aluminum",
        component_type="caption",
        verbose=True
    )
    
    print(f"\n✅ Evaluation complete!")
    print(f"   Overall Score: {result.overall_score:.1f}/10")
    print(f"   Quality Gate: {'PASS' if result.passes_quality_gate else 'FAIL'}")
    print(f"   Time: {result.evaluation_time_ms:.1f}ms")


def demo_poor_content():
    """Demo evaluation of poor quality content"""
    
    print("\n\n" + "=" * 70)
    print("DEMO: Poor Content Detection")
    print("=" * 70)
    print()
    
    # Poor quality caption with casual language
    poor_caption = """
    Yeah so aluminum is like totally awesome for laser cleaning and stuff. 
    Gonna use lasers to clean it and it's gonna be super cool. The oxide 
    coating is kinda annoying but lasers make it go away real quick.
    """
    
    print("Evaluating poor quality content with casual language...\n")
    
    result = evaluate_content(
        content=poor_caption.strip(),
        material_name="Aluminum",
        component_type="caption",
        verbose=True
    )
    
    print(f"\n⚠️  Poor content detected!")
    print(f"   Overall Score: {result.overall_score:.1f}/10")
    print(f"   Professionalism issues identified")


def demo_integration_helper():
    """Demo integration helper for post-generation evaluation"""
    
    print("\n\n" + "=" * 70)
    print("DEMO: Integration Helper (Post-Generation)")
    print("=" * 70)
    print()
    
    # Simulated generation output
    generated_content = """
    Steel surface contamination requires specialized cleaning approaches that 
    preserve material integrity while removing oxidation layers. Laser ablation 
    technology delivers precise energy to target contaminants without affecting 
    the underlying substrate structure.
    """
    
    print("Simulating post-generation evaluation...\n")
    
    # Use convenience function
    result = evaluate_after_generation(
        content=generated_content.strip(),
        material_name="Steel",
        component_type="caption",
        verbose=True,
        skip_evaluation=False
    )
    
    print(f"\n✅ Post-generation evaluation complete!")
    print(f"   Ready for deployment: {result.passes_quality_gate}")


def demo_skip_evaluation():
    """Demo skipping evaluation (--skip-claude-eval flag)"""
    
    print("\n\n" + "=" * 70)
    print("DEMO: Skip Evaluation (Disabled Mode)")
    print("=" * 70)
    print()
    
    content = "Sample caption for copper laser cleaning."
    
    print("Running with skip_evaluation=True...\n")
    
    result = evaluate_after_generation(
        content=content,
        material_name="Copper",
        verbose=True,
        skip_evaluation=True
    )
    
    print(f"\n⏭️  Evaluation skipped as requested")
    print(f"   Result: {result}")


def main():
    """Run all demos"""
    
    print("\n" + "🤖" * 35)
    print("CLAUDE SUBJECTIVE EVALUATION MODULE - DEMO")
    print("🤖" * 35)
    print()
    print("This demo shows the Claude evaluation module in action.")
    print("Since Claude API is not configured, it uses fallback evaluation.")
    print()
    
    # Run demos
    demo_basic_evaluation()
    demo_poor_content()
    demo_integration_helper()
    demo_skip_evaluation()
    
    print("\n\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Configure Claude API key in .env (optional)")
    print("2. Add to generation workflow with --enable-claude-eval flag")
    print("3. Integrate in run.py for automatic post-generation evaluation")
    print()


if __name__ == "__main__":
    main()
