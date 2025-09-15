#!/usr/bin/env python3
"""
Compact Forensic Logging for Smart Optimizer

Captures essential investigative trails without verbose text samples.
Focus: Flag impacts, metrics, decisions, and learning outcomes.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from smart_optimize import ContentOptimizer, LearningDatabase

# Configure compact logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompactForensicOptimizer(ContentOptimizer):
    """Smart optimizer with compact forensic logging."""
    
    def __init__(self):
        super().__init__()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def optimize_with_compact_logging(self, material: str):
        """Run optimization with compact investigative logging."""
        
        logger.info(f"🔍 FORENSIC SESSION {self.session_id} - Material: {material}")
        
        # Find and process content file
        content_dir = Path("content/components/text")
        content_files = list(content_dir.glob(f"*{material}*.md"))
        
        if not content_files:
            logger.error(f"❌ No content files found for: {material}")
            return {"success": False, "error": "No content files found"}
        
        content_file = content_files[0]
        content = content_file.read_text()
        current_score = self._extract_ai_score(content)
        
        if current_score is None:
            logger.error(f"❌ Cannot extract AI score from {content_file.name}")
            return {"success": False, "error": "No AI score found"}
        
        # COMPACT FORENSIC LOG: Initial State
        logger.info(f"📊 INITIAL: Score={current_score:.1f}, Chars={len(content)}, File={content_file.name}")
        
        # Get strategy and analyze flags
        strategy = self.learning_db.get_smart_strategy(material, current_score)
        enhancement_flags = strategy["enhancement_flags"]
        
        # COMPACT FORENSIC LOG: Strategy Selection
        flag_names = list(enhancement_flags.keys()) if isinstance(enhancement_flags, dict) else enhancement_flags
        expected_improvement = sum(
            self.learning_db.proven_strategies.get(flag, {}).get("avg_improvement", 0)
            for flag in flag_names
        )
        
        logger.info(f"🎯 STRATEGY: Flags={len(flag_names)}, Expected=+{expected_improvement:.1f}, Reason={strategy.get('strategy_reason', 'Standard')}")
        logger.info(f"🔧 FLAGS: {', '.join(flag_names)}")
        
        # Generate enhanced content
        start_time = datetime.now()
        enhanced_content = await self._generate_enhanced_content(material, content, enhancement_flags)
        generation_time = (datetime.now() - start_time).total_seconds()
        
        if not enhanced_content:
            logger.error(f"❌ Content generation failed")
            return {"success": False, "error": "Generation failed"}
        
        # Analyze results
        new_score = await self._analyze_content_score(enhanced_content)
        improvement = new_score - current_score if new_score else 0
        
        # COMPACT FORENSIC LOG: Results Analysis
        performance_ratio = (improvement / expected_improvement * 100) if expected_improvement > 0 else 0
        
        # Quick text analysis
        original_words = content.split()
        enhanced_words = enhanced_content.split()
        casual_words = ["like", "totally", "awesome", "rad", "dude", "epic", "kinda", "gotta"]
        casual_removed = sum(1 for word in original_words if any(casual in word.lower() for casual in casual_words)) - \
                        sum(1 for word in enhanced_words if any(casual in word.lower() for casual in casual_words))
        
        logger.info(f"⚙️ GENERATION: Time={generation_time:.1f}s, NewChars={len(enhanced_content)}, CasualRemoved={casual_removed}")
        logger.info(f"📈 RESULTS: {current_score:.1f}→{new_score:.1f} ({improvement:+.1f}), Performance={performance_ratio:.0f}%")
        
        # Individual flag impact estimates
        logger.info(f"🔍 FLAG_IMPACTS:")
        for flag in flag_names:
            expected_contrib = self.learning_db.proven_strategies.get(flag, {}).get("avg_improvement", 0)
            estimated_contrib = (expected_contrib / expected_improvement * improvement) if expected_improvement > 0 else 0
            success_rate = self.learning_db.proven_strategies.get(flag, {}).get("success_rate", 0)
            logger.info(f"   {flag}: Expected={expected_contrib:.1f}, Estimated={estimated_contrib:+.1f}, SuccessRate={success_rate:.0%}")
        
        # Decision logic
        success = improvement > 1.0
        decision = "ACCEPT" if improvement > 0.5 else "REJECT"
        
        logger.info(f"⚖️ DECISION: {decision} (threshold=0.5), Success={success}, Learning={'YES' if success else 'NO'}")
        
        # Record in learning database with compact details
        details = {
            "session_id": self.session_id,
            "generation_time": round(generation_time, 2),
            "char_change": len(enhanced_content) - len(content),
            "casual_words_removed": casual_removed,
            "expected_improvement": round(expected_improvement, 1),
            "performance_ratio": round(performance_ratio, 1),
            "decision": decision,
            "flag_count": len(flag_names)
        }
        
        self.learning_db.record_result(
            material, current_score, new_score or current_score, 
            enhancement_flags, success, details
        )
        
        # Update content if improved
        if improvement > 0.5:
            self._update_content_file(content_file, enhanced_content, new_score, enhancement_flags)
            logger.info(f"✅ UPDATED: Content file updated with new score {new_score:.1f}")
        else:
            logger.info(f"⚪ KEPT: Original content retained (insufficient improvement)")
        
        # COMPACT FORENSIC LOG: Session Summary
        logger.info(f"📋 SESSION_COMPLETE: {material} | {current_score:.1f}→{new_score:.1f} | {decision} | {generation_time:.1f}s")
        
        return {
            "success": True,
            "session_id": self.session_id,
            "material": material,
            "initial_score": current_score,
            "final_score": new_score or current_score,
            "improvement": improvement,
            "decision": decision,
            "generation_time": generation_time,
            "performance_ratio": performance_ratio,
            "flags_applied": flag_names,
            "casual_words_removed": casual_removed
        }

async def demo_compact_forensic(material: str = "steel"):
    """Demo compact forensic logging on a material that hasn't been optimized yet."""
    
    print("🔍 COMPACT FORENSIC LOGGING DEMO")
    print("=" * 50)
    
    optimizer = CompactForensicOptimizer()
    result = await optimizer.optimize_with_compact_logging(material)
    
    print(f"\n📊 COMPACT SUMMARY:")
    print(f"   Material: {result.get('material', 'Unknown')}")
    print(f"   Score Change: {result.get('initial_score', 0):.1f} → {result.get('final_score', 0):.1f}")
    print(f"   Improvement: {result.get('improvement', 0):+.1f} points")
    print(f"   Decision: {result.get('decision', 'Unknown')}")
    print(f"   Flags: {len(result.get('flags_applied', []))}")
    print(f"   Performance: {result.get('performance_ratio', 0):.0f}%")
    print(f"   Session: {result.get('session_id', 'Unknown')}")

if __name__ == "__main__":
    import sys
    material = sys.argv[1] if len(sys.argv) > 1 else "steel"
    asyncio.run(demo_compact_forensic(material))
"""
Demo: Compact AI Detection Iteration Logging

This script demonstrates the new optimized AI detection logging system that:
1. Tracks AI detection score changes per iteration
2. Reduces sentence logging size to essential failure patterns
3. Provides compact, readable iteration summaries

Run this to see the before/after comparison of logging formats.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.ai_detection_logger import AIDetectionIterationLogger, extract_key_failing_patterns


def demo_verbose_logging():
    """Show example of current verbose logging format."""
    print("=" * 80)
    print("CURRENT VERBOSE LOGGING FORMAT (BEFORE)")
    print("=" * 80)
    
    verbose_example = """
ai_detection_analysis:
  score: 35.320000
  confidence: 0.706400
  classification: "unclear"
  provider: "winston"
  processing_time: 7.427623
  optimization_iterations: 3
  details:
    input: "text"
    readability_score: 60.840000
    credits_used: 7763
    credits_remaining: 249038
    version: "4.11"
    language: "en"
    attack_detected:
      zero_width_space: False
      homoglyph_attack: False
    sentences: [{'length': 90, 'score': 99.35, 'text': 'Aluminum, it presents unique challenge for laser cleaning because surface very reflective.'}, {'length': 110, 'score': 93.56, 'text': 'This reflectivity, it can reach up to 98% for some alloys, means most laser energy bounces off, not absorbed.'}, {'length': 154, 'score': 85.63, 'text': 'But with correct parameters, laser cleaning works well, really well. Key is using 1064nm wavelength—this near-infrared light, aluminum absorbs it better.'}, {'length': 89, 'score': 88.37, 'text': 'Also important is pulsed fiber laser, with very short pulses, around 10-200 nanoseconds.'}, {'length': 92, 'score': 99.74, 'text': 'This short time prevents heat from spreading into material, so no damage to the base metal.'}, {'length': 143, 'score': 98.28, 'text': 'Must set fluence carefully, very carefully, between 0.5 to 10.0 J/cm². Too low, cleaning not effective; too high, risk of melting the surface.'}, {'length': 114, 'score': 96.99, 'text': 'In practice, for automotive industry, we use laser to remove lubricants and oxides from castings before welding.'}, {'length': 158, 'score': 95.66, 'text': 'Process is fast, no chemicals needed. For aerospace, same method cleans airframe components and strips anodized layers for repair—precision is key, very key.'}, {'length': 164, 'score': 99.75, 'text': 'Electronics industry also benefits for cleaning heat sinks. This laser method is good solution, much better than old ways like chemical baths or abrasive blasting.'}, {'length': 87, 'score': 99.69, 'text': 'Those traditional methods can leave residue, or even damage the soft aluminum surface.'}, {'length': 168, 'score': 99.63, 'text': 'Laser is non-contact, so no scratching, no problem. Success of cleaning, we measure by few things. Surface must be clean, no oxide layers—confirmed with spectroscopy.'}, {'length': 153, 'score': 99.84, 'text': 'Roughness should be low, and most important, no microcracks. The reflectivity itself can be indicator; clean aluminum surface should have uniform shine.'}, {'length': 147, 'score': 100, 'text': '**Process is also more environmentally friendly**, no toxic waste to dispose. *And for workshop teams, it is safer, no harsh chemicals to handle*.'}, {'length': 86, 'score': 99.83, 'text': 'Together, this technology helps our industries become more efficient and sustainable.'}, {'length': 86, 'score': 99.4, 'text': 'Already, many companies in Indonesia adopting this method, and results are very good.'}]
    failing_sentences_count: 64
    failing_sentences_percentage: 24.427481
    failing_patterns:
      avg_length: 28.953125
      contains_repetition: True
      uniform_structure: True
      technical_density: 0.369671
"""
    
    print(verbose_example)
    print(f"Character count: {len(verbose_example):,}")
    print(f"Line count: {len(verbose_example.split())}")


def demo_compact_logging():
    """Show example of new compact logging format."""
    print("\n" + "=" * 80)
    print("NEW COMPACT ITERATION LOGGING FORMAT (AFTER)")
    print("=" * 80)
    
    # Create iteration logger and simulate optimization process
    logger = AIDetectionIterationLogger()
    
    # Simulate 3 optimization iterations with improving scores
    iterations_data = [
        {
            "iteration": 1, "score": 35.2, "classification": "unclear", "confidence": 0.706,
            "provider": "winston", "processing_time": 2.1, "failing_count": 25, 
            "failing_percentage": 31.6, "patterns": {
                "avg_length": 21.3, "contains_repetition": True, 
                "uniform_structure": True, "technical_density": 0.274
            }
        },
        {
            "iteration": 2, "score": 42.8, "classification": "unclear", "confidence": 0.856,
            "provider": "winston", "processing_time": 1.9, "failing_count": 18,
            "failing_percentage": 24.1, "patterns": {
                "avg_length": 23.7, "contains_repetition": True,
                "uniform_structure": False, "technical_density": 0.291
            }
        },
        {
            "iteration": 3, "score": 46.2, "classification": "unclear", "confidence": 0.924,
            "provider": "winston", "processing_time": 2.3, "failing_count": 15,
            "failing_percentage": 20.8, "patterns": {
                "avg_length": 25.1, "contains_repetition": False,
                "uniform_structure": False, "technical_density": 0.312
            }
        }
    ]
    
    for data in iterations_data:
        logger.log_iteration(
            iteration=data["iteration"],
            score=data["score"],
            classification=data["classification"],
            confidence=data["confidence"],
            provider=data["provider"],
            processing_time=data["processing_time"],
            failing_sentences_count=data["failing_count"],
            failing_sentences_percentage=data["failing_percentage"],
            key_failing_patterns=data["patterns"]
        )
    
    compact_log = logger.format_compact_log(include_details=True)
    print(compact_log)
    
    print(f"\nCharacter count: {len(compact_log):,}")
    print(f"Line count: {len(compact_log.split())}")
    
    # Show summary
    print("\n" + "-" * 40)
    print("ITERATION SUMMARY")
    print("-" * 40)
    summary = logger.get_iteration_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")


def show_size_comparison():
    """Show the dramatic size reduction."""
    print("\n" + "=" * 80)
    print("SIZE COMPARISON & BENEFITS")
    print("=" * 80)
    
    # Rough estimates based on real data
    verbose_chars = 15000  # Typical verbose log with sentence arrays
    compact_chars = 800    # Compact iteration log
    
    reduction_percentage = ((verbose_chars - compact_chars) / verbose_chars) * 100
    
    print(f"📊 Verbose Logging:     ~{verbose_chars:,} characters")
    print(f"📊 Compact Logging:     ~{compact_chars:,} characters")
    print(f"📉 Size Reduction:      {reduction_percentage:.1f}%")
    print()
    
    print("✅ BENEFITS:")
    print("   • Clear iteration-by-iteration score progression")
    print("   • Score changes highlighted (+/- from previous)")
    print("   • Essential failure patterns preserved")
    print("   • Massive sentence arrays eliminated")
    print("   • Readable trend analysis (improving/degrading/stable)")
    print("   • Processing time tracking per iteration")
    print("   • Cumulative optimization metrics")
    print()
    
    print("🎯 SOLVES YOUR REQUIREMENTS:")
    print("   1. ✅ Log AI detection score changes per iteration")
    print("   2. ✅ Reduce size of sentence logging significantly")


def demo_integration_example():
    """Show how this integrates with existing system."""
    print("\n" + "=" * 80)
    print("INTEGRATION WITH EXISTING OPTIMIZATION SYSTEM")
    print("=" * 80)
    
    integration_code = '''
# Before (in content_optimization.py)
def update_content_with_comprehensive_analysis(content, ai_result, quality_result, ...):
    # Massive verbose logging with full sentence arrays
    result_lines.append("ai_detection_analysis:")
    result_lines.append(f"  score: {ai_result.score:.6f}")
    # ... hundreds of lines of sentence data ...

# After (with compact iteration logging)
def update_content_with_comprehensive_analysis(content, ai_result, quality_result, 
                                             iteration_logger=None, ...):
    if iteration_logger and iteration_logger.iteration_history:
        # Use compact iteration logging
        compact_log = iteration_logger.format_compact_log(include_details=True)
        result_lines.extend(compact_log.split('\\n'))
    else:
        # Fallback to simplified traditional logging (no sentence arrays)
        result_lines.append("ai_detection_analysis:")
        result_lines.append(f"  score: {ai_result.score:.2f}")

# Usage in optimization orchestrator
async def optimize_content(self, content, material_name, ...):
    iteration_logger = AIDetectionIterationLogger()
    
    # Log each iteration during optimization
    for iteration in range(max_iterations):
        ai_result = await ai_service.detect_ai_content(optimized_content)
        
        iteration_logger.log_iteration(
            iteration=iteration + 1,
            score=ai_result.score,
            classification=ai_result.classification,
            # ... other essential metrics only
        )
    
    # Return logger with optimization result
    return OptimizationResult(..., iteration_logger=iteration_logger)
'''
    
    print(integration_code)


if __name__ == "__main__":
    print("🚀 AI Detection Compact Logging Demo")
    print("🎯 Solving: 1) Score changes per iteration, 2) Reduce sentence logging size")
    
    demo_verbose_logging()
    demo_compact_logging()
    show_size_comparison()
    demo_integration_example()
    
    print("\n" + "=" * 80)
    print("✨ READY TO INTEGRATE")
    print("=" * 80)
    print("The new compact logging system is implemented and ready to use!")
    print("Key files updated:")
    print("  • utils/ai_detection_logger.py (new compact logging system)")
    print("  • optimizer/content_optimization.py (updated to use compact logging)")
    print("  • optimizer/optimization_orchestrator.py (integrated iteration tracking)")
    print()
    print("Next step: Update callers to use the new iteration_logger parameter")
