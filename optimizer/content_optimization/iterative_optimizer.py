"""
Iterative Learning Optimizer for Z-Beam Content

Simple, single-command optimizer that:
1. Learns from previous optimization attempts
2. Gets smarter with each run
3. Builds on previous results
4. Uses historical data to improve strategies
5. Single command: just run it again to continue learning

Usage:
    python3 -c "
    import asyncio
    from optimizer.content_optimization.iterative_optimizer import optimize
    asyncio.run(optimize('text'))
    "
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import statistics

from optimizer.ai_detection.types import AIDetectionConfig
from optimizer.ai_detection.service import initialize_ai_detection_service
from components.text.generators.fail_fast_generator import create_fail_fast_generator
from data.materials import load_materials
from optimizer.content_optimization import content_analyzer

logger = logging.getLogger(__name__)


def get_config():
    """Get basic config from run.py"""
    try:
        from run import COMPONENT_CONFIG, API_PROVIDERS
        return {"components": COMPONENT_CONFIG, "api": API_PROVIDERS}
    except ImportError:
        return {"components": {}, "api": {}}


def is_test_mode():
    """Test mode detection using environment variables"""
    return any([
        os.getenv("TEST_MODE", "").lower() in ("true", "1", "yes"),
        os.getenv("PYTEST_CURRENT_TEST", "") != "",
        "pytest" in os.getenv("_", "").lower(),
    ])


class LearningDatabase:
    """Persistent learning database that tracks what works and what doesn't."""
    
    def __init__(self, db_path: str = "optimizer/learning/optimization_history.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load_database()
    
    def _load_database(self) -> Dict:
        """Load existing learning data or create new database."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"📚 Loaded learning database with {len(data.get('materials', {}))} materials")
                return data
            except Exception as e:
                logger.warning(f"Failed to load learning database: {e}")
        
        # Create new database structure
        return {
            "created_at": datetime.now().isoformat(),
            "total_runs": 0,
            "materials": {},  # material_name -> optimization history
            "successful_strategies": {},  # what enhancement flags work best
            "score_progressions": {},  # how scores improve over time
            "best_practices": {
                "effective_enhancement_flags": [],
                "optimal_iteration_counts": {},
                "score_improvement_patterns": {}
            }
        }
    
    def save_database(self):
        """Save learning database to disk."""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
        logger.info(f"💾 Learning database saved: {self.db_path}")
    
    def record_optimization_attempt(self, material: str, initial_score: float, 
                                  final_score: float, iterations: int, 
                                  enhancement_flags: Dict, successful: bool):
        """Record an optimization attempt for learning."""
        if material not in self.data["materials"]:
            self.data["materials"][material] = {
                "optimization_history": [],
                "best_score": 0.0,
                "total_attempts": 0,
                "successful_attempts": 0
            }
        
        attempt = {
            "timestamp": datetime.now().isoformat(),
            "initial_score": initial_score,
            "final_score": final_score,
            "improvement": final_score - initial_score,
            "iterations": iterations,
            "enhancement_flags": enhancement_flags,
            "successful": successful,
            "run_number": self.data["total_runs"] + 1
        }
        
        self.data["materials"][material]["optimization_history"].append(attempt)
        self.data["materials"][material]["total_attempts"] += 1
        
        if successful:
            self.data["materials"][material]["successful_attempts"] += 1
        
        if final_score > self.data["materials"][material]["best_score"]:
            self.data["materials"][material]["best_score"] = final_score
        
        self.data["total_runs"] += 1
        self._update_learning_insights()
    
    def _update_learning_insights(self):
        """Analyze historical data to extract learning insights."""
        # Analyze successful enhancement flags
        successful_flags = {}
        total_improvements = []
        
        for material_data in self.data["materials"].values():
            for attempt in material_data["optimization_history"]:
                if attempt["improvement"] > 1.0:  # Meaningful improvement
                    total_improvements.append(attempt["improvement"])
                    
                    for flag, enabled in attempt["enhancement_flags"].items():
                        if enabled:
                            if flag not in successful_flags:
                                successful_flags[flag] = {"count": 0, "total_improvement": 0.0}
                            successful_flags[flag]["count"] += 1
                            successful_flags[flag]["total_improvement"] += attempt["improvement"]
        
        # Calculate effectiveness scores for each flag
        effective_flags = []
        for flag, data in successful_flags.items():
            if data["count"] >= 2:  # At least 2 successful uses
                avg_improvement = data["total_improvement"] / data["count"]
                effective_flags.append((flag, avg_improvement, data["count"]))
        
        # Sort by average improvement
        effective_flags.sort(key=lambda x: x[1], reverse=True)
        self.data["best_practices"]["effective_enhancement_flags"] = [
            {"flag": flag, "avg_improvement": improvement, "usage_count": count}
            for flag, improvement, count in effective_flags[:10]  # Top 10
        ]
        
        # Update score improvement patterns
        if total_improvements:
            self.data["best_practices"]["score_improvement_patterns"] = {
                "average_improvement": statistics.mean(total_improvements),
                "median_improvement": statistics.median(total_improvements),
                "best_improvement": max(total_improvements),
                "total_successful_runs": len(total_improvements)
            }
    
    def get_smart_config_for_material(self, material: str, current_score: float) -> Dict:
        """Get intelligent configuration based on learning history."""
        base_config = {
            "target_score": 85.0,
            "max_iterations": 8,
            "improvement_threshold": 1.0,
            "enhancement_flags": {
                # Default enhancement flags for AI detection optimization
                "reduce_persona_intensity": True,
                "professional_tone": True,
                "reduce_casual_language": True,
                "technical_precision": True,
                "subtle_personality": True,
            }
        }
        
        # If we have no history, use conservative defaults
        if material not in self.data["materials"]:
            logger.info(f"🆕 No history for {material}, using default config")
            return base_config
        
        material_data = self.data["materials"][material]
        history = material_data["optimization_history"]
        
        if not history:
            return base_config
        
        # Analyze what worked for this specific material
        successful_attempts = [a for a in history if a["improvement"] > 1.0]
        
        if successful_attempts:
            # Use the most successful recent attempt as baseline
            recent_successful = sorted(successful_attempts, key=lambda x: x["timestamp"])[-1]
            base_config["enhancement_flags"] = recent_successful["enhancement_flags"].copy()
            
            # Adjust target based on best score achieved
            best_score = material_data["best_score"]
            if best_score > current_score:
                base_config["target_score"] = min(best_score + 5.0, 95.0)
            
            logger.info(f"📈 Using successful config for {material} (best: {best_score:.1f})")
        
        # Apply global learning insights
        effective_flags = self.data["best_practices"].get("effective_enhancement_flags", [])
        for flag_data in effective_flags[:5]:  # Top 5 most effective flags
            flag = flag_data["flag"]
            if flag not in base_config["enhancement_flags"]:
                base_config["enhancement_flags"][flag] = True
        
        # Adjust iteration count based on historical needs
        if successful_attempts:
            avg_iterations = statistics.mean([a["iterations"] for a in successful_attempts])
            base_config["max_iterations"] = max(int(avg_iterations * 1.2), 6)
        
        # Progressive difficulty: if score is already high, be more aggressive
        if current_score > 80.0:
            base_config["improvement_threshold"] = 0.5  # More sensitive to small improvements
            base_config["max_iterations"] *= 2  # More attempts for fine-tuning
        
        return base_config
    
    def get_learning_summary(self) -> str:
        """Get a summary of what the system has learned."""
        total_runs = self.data["total_runs"]
        materials_count = len(self.data["materials"])
        
        summary = [f"🧠 Learning Summary ({total_runs} total runs, {materials_count} materials)"]
        
        # Best practices learned
        effective_flags = self.data["best_practices"].get("effective_enhancement_flags", [])
        if effective_flags:
            summary.append("📊 Most Effective Enhancement Flags:")
            for flag_data in effective_flags[:3]:
                flag = flag_data["flag"]
                improvement = flag_data["avg_improvement"]
                count = flag_data["usage_count"]
                summary.append(f"  • {flag}: +{improvement:.1f} avg improvement ({count} uses)")
        
        # Improvement patterns
        patterns = self.data["best_practices"].get("score_improvement_patterns", {})
        if patterns:
            avg_imp = patterns.get("average_improvement", 0)
            best_imp = patterns.get("best_improvement", 0)
            summary.append(f"📈 Typical improvement: {avg_imp:.1f} points (best: {best_imp:.1f})")
        
        return "\n".join(summary)


async def optimize(component_name: str = "text") -> Dict[str, Any]:
    """
    Smart iterative optimizer that learns from each run.
    
    Just run this command repeatedly - it gets smarter each time!
    """
    # Initialize learning database
    learning_db = LearningDatabase()
    
    logger.info("🚀 Starting iterative learning optimization")
    logger.info(learning_db.get_learning_summary())
    
    results = {
        "materials_processed": 0,
        "materials_improved": 0,
        "total_improvement": 0.0,
        "best_improvements": {},
        "new_learning": False
    }
    
    try:
        # Initialize services
        config_data = get_config()
        test_mode = is_test_mode()
        
        ai_provider = "mock" if test_mode else "winston"
        
        # Basic AI config - will be customized per material based on learning
        base_ai_config = AIDetectionConfig(
            provider=ai_provider,
            enabled=True,
            target_score=85.0,
            max_iterations=8,
            improvement_threshold=1.0,
            timeout=30,
            retry_attempts=3,
        )
        
        ai_service = initialize_ai_detection_service(base_ai_config)
        
        # Load materials and find files
        generator = create_fail_fast_generator()
        materials_data = load_materials()
        
        component_dir = Path("content/components") / component_name
        if not component_dir.exists():
            logger.error(f"Component directory not found: {component_dir}")
            return results
        
        material_files = [f for f in component_dir.glob("*.md") if not f.name.endswith('.backup')]
        if not material_files:
            logger.warning(f"No material files found in {component_dir}")
            return results
        
        logger.info(f"📂 Processing {len(material_files)} materials with adaptive learning")
        for file_path in material_files:
            logger.info(f"  📄 {file_path.name}")
        
        # Process each material with personalized optimization
        for file_path in material_files:
            material_name = file_path.stem.replace(f'-laser-cleaning', '').replace('-', '_')
            
            try:
                logger.info(f"\n🔧 Optimizing: {material_name} (from {file_path.name})")
                
                # Check if we have material data first
                material_data = None
                # Look in the materials section for the material
                if 'materials' in materials_data:
                    for category_data in materials_data['materials'].values():
                        if 'items' in category_data:
                            for item in category_data['items']:
                                item_name = item.get('name', '').lower().replace(' ', '_').replace('-', '_')
                                if item_name == material_name:
                                    material_data = item
                                    break
                            if material_data:
                                break
                
                if not material_data:
                    logger.warning(f"  ⚠️ No material data found for {material_name}")
                    logger.warning(f"  Searched in materials structure with categories: {list(materials_data.get('materials', {}).keys())}")
                    continue
                
                # Read current content and get baseline score
                current_content = content_analyzer.extract_target_content_only(file_path.read_text())
                if not current_content:
                    continue
                
                initial_analysis = await asyncio.to_thread(
                    ai_service.detect_ai_content, current_content
                )
                initial_score = initial_analysis.score
                
                logger.info(f"  📊 Current score: {initial_score:.1f}")
                
                # Get smart configuration based on learning history
                smart_config = learning_db.get_smart_config_for_material(material_name, initial_score)
                
                logger.info(f"  🎯 Target: {smart_config['target_score']:.1f}, Max iterations: {smart_config['max_iterations']}")
                logger.info(f"  🔧 Enhancement flags: {list(smart_config['enhancement_flags'].keys())}")
                
                # Skip if already meets target
                if initial_score >= smart_config['target_score']:
                    logger.info(f"  ✅ Already meets target ({initial_score:.1f} >= {smart_config['target_score']:.1f}), skipping")
                    continue
                
                # Get material and author data
                author_id = material_data.get('author_id', 1)
                logger.info(f"  👤 Author ID: {author_id}")
                
                # Optimization loop
                best_score = initial_score
                best_content = current_content
                iteration_count = 0
                last_improvement = 0.0
                
                for iteration in range(1, smart_config['max_iterations'] + 1):
                    iteration_count = iteration
                    
                    try:
                        logger.info(f"    🔄 Iteration {iteration}")
                        
                        # Current analysis
                        current_analysis = await asyncio.to_thread(
                            ai_service.detect_ai_content, current_content
                        )
                        current_score = current_analysis.score
                        
                        # Check for improvement
                        improvement = current_score - best_score
                        if improvement > 0:
                            best_score = current_score
                            best_content = current_content
                            last_improvement = improvement
                            logger.info(f"      ✅ Improved: {current_score:.1f} (+{improvement:.1f})")
                        
                        # Check if target reached
                        if current_score >= smart_config['target_score']:
                            logger.info(f"      🎯 Target reached!")
                            break
                        
                        # Generate enhanced content using smart config
                        winston_result_dict = {
                            "overall_score": current_analysis.score,
                            "classification": current_analysis.classification,
                            "confidence": current_analysis.confidence,
                            "processing_time": current_analysis.processing_time,
                            "provider": current_analysis.provider,
                            "details": current_analysis.details or {},
                        }
                        
                        # Get API client for generation
                        from api.client_manager import get_api_client_for_component
                        api_client = get_api_client_for_component("text")
                        
                        # Create author info from author_id
                        author_info = {"id": author_id, "name": f"Author {author_id}"}
                        
                        # Log enhancement flags being applied
                        logger.info(f"      🎯 Applying enhancement flags: {list(smart_config['enhancement_flags'].keys())}")
                        
                        # Generate improved content using the text generator
                        generation_result = await asyncio.wait_for(
                            asyncio.to_thread(
                                generator.generate,
                                material_name,
                                material_data,
                                api_client,
                                author_info,
                                frontmatter_data=None,
                                enhancement_flags=smart_config['enhancement_flags']  # Pass learned enhancement flags
                            ),
                            timeout=60
                        )
                        
                        # Extract content from generation result
                        if generation_result and generation_result.success:
                            current_content = generation_result.content
                            logger.info(f"      📝 Generated new content ({len(current_content)} chars)")
                            
                            # Extract target content for next iteration analysis
                            current_content = content_analyzer.extract_target_content_only(current_content)
                        else:
                            logger.warning(f"      ⚠️ Generation failed: {generation_result.error_message}")
                            continue
                        
                    except Exception as e:
                        logger.error(f"      Error in iteration {iteration}: {e}")
                        continue
                
                # Record results and learning
                final_improvement = best_score - initial_score
                successful = final_improvement > smart_config['improvement_threshold']
                
                # Save learning data
                learning_db.record_optimization_attempt(
                    material_name, initial_score, best_score, iteration_count,
                    smart_config['enhancement_flags'], successful
                )
                
                if successful:
                    results["new_learning"] = True
                
                # Update file if improved
                if final_improvement > 0.1:  # Minimum meaningful improvement
                    results["materials_improved"] += 1
                    results["total_improvement"] += final_improvement
                    results["best_improvements"][material_name] = final_improvement
                    
                    logger.info(f"  ✅ Optimization successful: {initial_score:.1f} → {best_score:.1f} (+{final_improvement:.1f})")
                    
                    # Update content with new metadata
                    updated_content = content_analyzer.update_content_with_comprehensive_analysis(
                        file_path.read_text(), 
                        ai_result={
                            "score": best_score,
                            "classification": "optimized",
                            "provider": "winston"
                        },
                        quality_result=None,
                        material_name=material_name,
                        metadata={
                            "optimization_iterations": iteration_count,
                            "learning_applied": True,
                            "optimized_at": datetime.now().isoformat()
                        }
                    )
                    file_path.write_text(updated_content)
                    
                else:
                    logger.info(f"  ⚪ Minimal improvement: +{final_improvement:.1f}")
                
                results["materials_processed"] += 1
                
            except Exception as e:
                logger.error(f"Failed to optimize {material_name}: {e}")
                continue
        
        # Save learning database
        learning_db.save_database()
        
        # Print results
        logger.info(f"\n🏁 Optimization completed!")
        logger.info(f"📊 Processed: {results['materials_processed']} materials")
        logger.info(f"✅ Improved: {results['materials_improved']} materials")
        logger.info(f"📈 Total improvement: +{results['total_improvement']:.1f} points")
        
        if results["best_improvements"]:
            logger.info("🏆 Best improvements:")
            for material, improvement in sorted(results["best_improvements"].items(), 
                                              key=lambda x: x[1], reverse=True):
                logger.info(f"  • {material}: +{improvement:.1f}")
        
        if results["new_learning"]:
            logger.info("🧠 New learning patterns discovered - next run will be smarter!")
        
        return results
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        return results


# Simple command-line interface
if __name__ == "__main__":
    import sys
    component = sys.argv[1] if len(sys.argv) > 1 else "text"
    asyncio.run(optimize(component))
