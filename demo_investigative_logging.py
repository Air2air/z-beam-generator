#!/usr/bin/env python3
"""
Enhanced Smart Optimizer with Comprehensive Investigative Logging

This version captures detailed logs for every parameter change and result
to provide complete investigative trails for optimization analysis.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from smart_optimize import ContentOptimizer, LearningDatabase

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InvestigativeOptimizer(ContentOptimizer):
    """Enhanced optimizer with detailed investigative logging."""
    
    def __init__(self):
        super().__init__()
        self.optimization_log = []
    
    async def optimize_with_detailed_logging(self, material: str):
        """Run optimization with comprehensive investigative trail logging."""
        
        logger.info("🔍 INVESTIGATIVE OPTIMIZATION SESSION STARTED")
        logger.info("=" * 60)
        
        # Find content file
        content_dir = Path("content/components/text")
        content_files = list(content_dir.glob(f"*{material}*.md"))
        
        if not content_files:
            logger.error(f"❌ No content files found for material: {material}")
            return {"success": False, "error": "No content files found"}
        
        content_file = content_files[0]
        logger.info(f"📁 Processing file: {content_file}")
        
        # STEP 1: INITIAL STATE ANALYSIS
        logger.info("📊 STEP 1: INITIAL STATE ANALYSIS")
        content = content_file.read_text()
        current_score = self._extract_ai_score(content)
        
        logger.info(f"📈 Initial AI Detection Score: {current_score}")
        logger.info(f"📝 Content Length: {len(content)} characters")
        logger.info(f"📄 Content Preview (first 150 chars):")
        logger.info(f"   '{content[:150]}...'")
        
        # STEP 2: STRATEGY SELECTION
        logger.info("🧠 STEP 2: STRATEGY SELECTION")
        strategy = self.learning_db.get_smart_strategy(material, current_score)
        enhancement_flags = strategy["enhancement_flags"]
        
        logger.info(f"🎯 Selected Strategy: {strategy.get('strategy_reason', 'Unknown')}")
        logger.info(f"🔧 Enhancement Flags Selected: {len(enhancement_flags)}")
        
        for i, flag in enumerate(enhancement_flags, 1):
            flag_data = self.learning_db.proven_strategies.get(flag, {})
            description = flag_data.get("description", "No description available")
            avg_improvement = flag_data.get("avg_improvement", 0)
            success_rate = flag_data.get("success_rate", 0)
            priority = flag_data.get("priority", "Unknown")
            
            logger.info(f"   {i}. {flag}")
            logger.info(f"      📝 Description: {description}")
            logger.info(f"      📈 Average Improvement: +{avg_improvement:.1f} points")
            logger.info(f"      ✅ Success Rate: {success_rate:.1%}")
            logger.info(f"      🎯 Priority: {priority}")
        
        # STEP 3: CONTENT GENERATION
        logger.info("⚙️ STEP 3: CONTENT GENERATION WITH ENHANCEMENTS")
        start_time = datetime.now()
        
        enhanced_content = await self._generate_enhanced_content(
            material, content, enhancement_flags
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"⏱️ Generation Time: {generation_time:.2f} seconds")
        logger.info(f"📝 Enhanced Content Length: {len(enhanced_content)} characters")
        logger.info(f"📄 Enhanced Content Preview (first 150 chars):")
        logger.info(f"   '{enhanced_content[:150]}...'")
        
        # STEP 4: CONTENT COMPARISON
        logger.info("🔍 STEP 4: BEFORE/AFTER CONTENT COMPARISON")
        
        # Character count changes
        char_change = len(enhanced_content) - len(content)
        logger.info(f"📊 Character Count Change: {char_change:+d} characters")
        
        # Word analysis (simplified)
        original_words = content.split()
        enhanced_words = enhanced_content.split()
        word_change = len(enhanced_words) - len(original_words)
        logger.info(f"📊 Word Count Change: {word_change:+d} words")
        
        # Look for specific changes
        casual_words = ["like", "totally", "awesome", "rad", "dude", "epic"]
        original_casual = sum(1 for word in original_words if any(casual in word.lower() for casual in casual_words))
        enhanced_casual = sum(1 for word in enhanced_words if any(casual in word.lower() for casual in casual_words))
        casual_reduction = original_casual - enhanced_casual
        
        logger.info(f"🗣️ Casual Language Analysis:")
        logger.info(f"   📊 Original casual words: {original_casual}")
        logger.info(f"   📊 Enhanced casual words: {enhanced_casual}")
        logger.info(f"   📈 Casual words removed: {casual_reduction}")
        
        # STEP 5: SCORE ANALYSIS
        logger.info("📈 STEP 5: AI DETECTION SCORE ANALYSIS")
        new_score = await self._analyze_content_score(enhanced_content)
        improvement = new_score - current_score if new_score else 0
        improvement_percentage = (improvement / current_score * 100) if current_score > 0 else 0
        
        logger.info(f"📊 Score Results:")
        logger.info(f"   📈 Initial Score: {current_score:.2f}")
        logger.info(f"   📈 Enhanced Score: {new_score:.2f}")
        logger.info(f"   📈 Net Improvement: {improvement:+.2f} points")
        logger.info(f"   📈 Percentage Change: {improvement_percentage:+.1f}%")
        
        # STEP 6: EFFECTIVENESS ANALYSIS
        logger.info("🎯 STEP 6: ENHANCEMENT FLAG EFFECTIVENESS ANALYSIS")
        
        expected_improvement = sum(
            self.learning_db.proven_strategies.get(flag, {}).get("avg_improvement", 0)
            for flag in enhancement_flags
        )
        
        logger.info(f"📊 Expected vs Actual Performance:")
        logger.info(f"   🎯 Expected Improvement: +{expected_improvement:.1f} points")
        logger.info(f"   📈 Actual Improvement: {improvement:+.1f} points")
        logger.info(f"   📊 Performance Ratio: {(improvement/expected_improvement*100) if expected_improvement > 0 else 0:.1f}%")
        
        # Analyze individual flag contributions (estimated)
        logger.info(f"🔍 Estimated Individual Flag Contributions:")
        for i, flag in enumerate(enhancement_flags, 1):
            expected_contrib = self.learning_db.proven_strategies.get(flag, {}).get("avg_improvement", 0)
            estimated_contrib = (expected_contrib / expected_improvement * improvement) if expected_improvement > 0 else 0
            logger.info(f"   {i}. {flag}: ~{estimated_contrib:+.1f} points")
        
        # STEP 7: DECISION AND LEARNING
        logger.info("🧠 STEP 7: DECISION LOGIC AND LEARNING UPDATE")
        
        success = improvement > 1.0
        decision = "ACCEPT" if improvement > 0.5 else "REJECT"
        
        logger.info(f"⚖️ Decision Logic:")
        logger.info(f"   📊 Improvement: {improvement:+.1f} points")
        logger.info(f"   📏 Threshold: 0.5 points for acceptance")
        logger.info(f"   ✅ Decision: {decision} enhancement")
        logger.info(f"   🧠 Learning Status: {'SUCCESS' if success else 'FAILURE'}")
        
        # Update learning database
        details = {
            "content_length": len(enhanced_content),
            "enhancement_count": len(enhancement_flags),
            "optimization_timestamp": datetime.now().isoformat(),
            "generation_time_seconds": generation_time,
            "character_change": char_change,
            "word_change": word_change,
            "casual_words_removed": casual_reduction,
            "expected_improvement": expected_improvement,
            "performance_ratio": (improvement/expected_improvement*100) if expected_improvement > 0 else 0,
            "decision": decision,
            "flags_applied": {flag: True for flag in enhancement_flags}
        }
        
        self.learning_db.record_result(
            material, current_score, new_score or current_score, 
            enhancement_flags, success, details
        )
        
        logger.info("💾 Learning database updated with detailed results")
        
        # STEP 8: FINAL SUMMARY
        logger.info("📋 STEP 8: OPTIMIZATION SESSION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"🎯 Material: {material}")
        logger.info(f"📊 Score: {current_score:.1f} → {new_score:.1f} ({improvement:+.1f})")
        logger.info(f"🔧 Flags Applied: {len(enhancement_flags)}")
        logger.info(f"⏱️ Generation Time: {generation_time:.2f}s")
        logger.info(f"✅ Decision: {decision}")
        logger.info(f"🧠 Learning: {'Updated with success' if success else 'Updated with failure'}")
        logger.info("=" * 60)
        
        return {
            "success": True,
            "initial_score": current_score,
            "final_score": new_score or current_score,
            "improvement": improvement,
            "enhancement_flags": enhancement_flags,
            "decision": decision,
            "generation_time": generation_time,
            "detailed_analysis": details
        }

async def demo_investigative_logging(material: str = "copper"):
    """Demo the comprehensive investigative logging system."""
    
    print("🔍 COMPREHENSIVE INVESTIGATIVE LOGGING DEMO")
    print("=" * 60)
    
    optimizer = InvestigativeOptimizer()
    result = await optimizer.optimize_with_detailed_logging(material)
    
    print("\n🎉 DEMO COMPLETE!")
    print(f"📊 Result Summary: {result}")

if __name__ == "__main__":
    import sys
    material = sys.argv[1] if len(sys.argv) > 1 else "copper"
    asyncio.run(demo_investigative_logging(material))
