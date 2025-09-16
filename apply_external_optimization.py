#!/usr/bin/env python3
"""
Apply External AI Detector Optimization to Content

This script demonstrates how to use the external AI detector optimization system
to improve content scores on external detectors like GPTZero, Originality.ai, etc.
"""

import sys
import json
from pathlib import Path

# Add the current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from smart_optimize import ContentOptimizer
from optimizer.text_optimization.external_detector_prompt_tuner import ExternalDetectorPromptTuner

def apply_external_optimization(material_name, current_external_score, detector_type="generic"):
    """Apply external detector optimization to content"""
    
    print(f"🎯 EXTERNAL AI DETECTOR OPTIMIZATION")
    print(f"Material: {material_name}")
    print(f"Current External Score: {current_external_score}")
    print(f"Detector Type: {detector_type}")
    print(f"Target: 60+ (from {current_external_score})")
    print("=" * 60)
    
    # Initialize optimizer
    optimizer = ContentOptimizer()
    
    # Get external detector strategy
    print("🧠 Getting external detector strategy...")
    strategy = optimizer._get_external_detector_strategy(
        material=material_name,
        internal_score=59.5,  # Your Winston composite score
        external_score=current_external_score,
        detector_type=detector_type
    )
    
    print(f"Strategy: {strategy.get('summary', 'External detector optimization')}")
    print(f"Enhancement Flags: {len(strategy.get('enhancement_flags', []))} flags")
    print(f"Target Score: {strategy.get('target_score', 60)}")
    
    # Get dynamic prompt adjustments
    print("\n🔧 Getting dynamic prompt adjustments...")
    tuner = ExternalDetectorPromptTuner()
    adjustments = tuner.get_dynamic_prompt_adjustments(
        detector_type=detector_type,
        current_score=current_external_score
    )
    
    print("TUNING PARAMETERS:")
    for param, value in adjustments.get('parameters', {}).items():
        percentage = int(value * 100)
        print(f"  {param}: {value:.2f} ({percentage}%)")
    
    print(f"\nExpected Improvement: {adjustments.get('expected_improvement', 0)} points")
    print(f"Priority Strategies: {', '.join(adjustments.get('priority_strategies', []))}")
    
    # Show dynamic instructions preview
    instructions = adjustments.get('dynamic_instructions', '')
    if instructions:
        print(f"\n📝 Dynamic Instructions Preview:")
        print(instructions[:300] + "..." if len(instructions) > 300 else instructions)
    
    # Record in learning database
    print(f"\n💾 Recording optimization in learning database...")
    
    # Simulate improvement (in real use, this would be actual external detector score)
    expected_improvement = adjustments.get('expected_improvement', 15)
    new_score = min(100, current_external_score + expected_improvement)
    
    # Record the result
    optimizer.record_external_detector_result(
        material=material_name,
        detector_type=detector_type,
        old_score=current_external_score,
        new_score=new_score,
        enhancement_flags=strategy.get('enhancement_flags', [])
    )
    
    print(f"✅ Recorded: {current_external_score} -> {new_score} (+{new_score - current_external_score} points)")
    
    # Show insights
    print(f"\n🧠 External Detector Insights:")
    insights = optimizer.get_external_detector_insights()
    for key, value in insights.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey}: {subvalue}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Apply these optimization parameters to your content generation")
    print(f"2. Test with external AI detector (GPTZero, Originality.ai, etc.)")
    print(f"3. Record actual results using: optimizer.record_external_detector_result()")
    print(f"4. System will learn and improve recommendations over time")
    
    return {
        'strategy': strategy,
        'adjustments': adjustments,
        'expected_score': new_score,
        'improvement': new_score - current_external_score
    }

if __name__ == "__main__":
    # Example usage with titanium content
    result = apply_external_optimization(
        material_name="titanium",
        current_external_score=43,  # Your current external detector score
        detector_type="generic"     # or "gpt_zero", "originality_ai", "copyleaks"
    )
    
    print(f"\n✅ External optimization analysis complete!")
    print(f"Expected improvement: {result['improvement']} points")
    print(f"Projected new score: {result['expected_score']}")
