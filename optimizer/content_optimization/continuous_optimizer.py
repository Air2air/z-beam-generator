"""
Continuous Optimization Engine for Z-Beam Content

This module provides enhanced optimization capabilities that allow for:
1. Resumable optimization sessions
2. Configurable improvement thresholds
3. Force re-optimization regardless of current scores
4. Persistent optimization state tracking
5. Configurable stopping conditions

Key improvements over sophisticated_optimizer:
- No early stopping for "good enough" scores
- Configurable improvement thresholds (default 1.0 instead of 5.0)
- Option to force re-optimization of all files
- Better iteration tracking and resumability
- More aggressive optimization by default
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from optimizer.ai_detection.types import AIDetectionConfig
from optimizer.ai_detection.service import initialize_ai_detection_service
from optimizer.text_optimization.ai_detection_prompt_optimizer import AIDetectionPromptOptimizer
from optimizer.text_optimization.dynamic_prompt_generator import DynamicPromptGenerator
from optimizer.text_optimization.validation.content_scorer import ContentQualityScorer
from components.text.generators.dynamic_generator import DynamicGenerator
from data.materials import load_materials
from config.runtime_config import get_config, is_test_mode
from optimizer.content_optimization.content_analyzer import ContentAnalyzer

logger = logging.getLogger(__name__)


class ContinuousOptimizationConfig:
    """Configuration for continuous optimization sessions."""
    
    def __init__(
        self,
        target_score: float = 85.0,
        max_iterations: int = 10,
        improvement_threshold: float = 1.0,  # Much lower threshold
        consecutive_failure_limit: int = 5,  # Higher failure tolerance
        force_reoptimize: bool = False,  # Force re-optimization regardless of current scores
        min_score_for_skip: float = 95.0,  # Only skip if score is truly excellent
        timeout_seconds: int = 600,
        save_progress: bool = True,
        aggressive_mode: bool = True,  # More aggressive optimization
    ):
        self.target_score = target_score
        self.max_iterations = max_iterations
        self.improvement_threshold = improvement_threshold
        self.consecutive_failure_limit = consecutive_failure_limit
        self.force_reoptimize = force_reoptimize
        self.min_score_for_skip = min_score_for_skip
        self.timeout_seconds = timeout_seconds
        self.save_progress = save_progress
        self.aggressive_mode = aggressive_mode


class OptimizationSession:
    """Tracks optimization session state for resumability."""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = datetime.now()
        self.materials_processed: Dict[str, Dict] = {}
        self.total_iterations = 0
        self.best_scores: Dict[str, float] = {}
        self.session_config: Optional[ContinuousOptimizationConfig] = None
        
    def update_material_progress(self, material: str, iteration: int, score: float, 
                               improvement: float, content: str):
        """Update progress tracking for a material."""
        if material not in self.materials_processed:
            self.materials_processed[material] = {
                "iterations": 0,
                "best_score": 0.0,
                "total_improvement": 0.0,
                "last_updated": None,
                "status": "processing"
            }
        
        self.materials_processed[material].update({
            "iterations": iteration,
            "best_score": score,
            "total_improvement": self.materials_processed[material]["total_improvement"] + improvement,
            "last_updated": datetime.now().isoformat(),
            "content_length": len(content)
        })
        
        self.best_scores[material] = score
        self.total_iterations += 1
    
    def save_session(self, save_path: Path = None):
        """Save session state for resumability."""
        if save_path is None:
            save_path = Path("optimizer/sessions") / f"session_{self.session_id}.json"
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        session_data = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "materials_processed": self.materials_processed,
            "total_iterations": self.total_iterations,
            "best_scores": self.best_scores,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(save_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        logger.info(f"💾 Session saved: {save_path}")
    
    @classmethod
    def load_session(cls, session_id: str) -> Optional['OptimizationSession']:
        """Load a previous optimization session."""
        session_path = Path("optimizer/sessions") / f"session_{session_id}.json"
        
        if not session_path.exists():
            logger.warning(f"Session file not found: {session_path}")
            return None
        
        try:
            with open(session_path, 'r') as f:
                data = json.load(f)
            
            session = cls(session_id=data["session_id"])
            session.start_time = datetime.fromisoformat(data["start_time"])
            session.materials_processed = data["materials_processed"]
            session.total_iterations = data["total_iterations"]
            session.best_scores = data["best_scores"]
            
            logger.info(f"📂 Session loaded: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None


async def run_continuous_optimization(
    component_name: str,
    config: ContinuousOptimizationConfig = None,
    session_id: str = None
) -> OptimizationSession:
    """
    Run continuous optimization with resumability and configurable parameters.
    
    Args:
        component_name: Component to optimize (e.g., 'text')
        config: Optimization configuration
        session_id: Resume from existing session ID
    
    Returns:
        OptimizationSession with complete optimization results
    """
    if config is None:
        config = ContinuousOptimizationConfig()
    
    # Load or create session
    if session_id:
        session = OptimizationSession.load_session(session_id)
        if session is None:
            logger.warning(f"Could not load session {session_id}, creating new session")
            session = OptimizationSession()
    else:
        session = OptimizationSession()
    
    session.session_config = config
    
    logger.info(f"🚀 Starting continuous optimization session: {session.session_id}")
    logger.info(f"📊 Config: target={config.target_score}, threshold={config.improvement_threshold}, force={config.force_reoptimize}")
    
    try:
        # Initialize services
        config_data = get_config()
        test_mode = is_test_mode()
        
        ai_provider = "mock" if test_mode else "winston"
        
        ai_config = AIDetectionConfig(
            provider=ai_provider,
            enabled=True,
            target_score=config.target_score,
            max_iterations=config.max_iterations,
            improvement_threshold=config.improvement_threshold,
            timeout=30,
            retry_attempts=3,
        )
        
        ai_service = initialize_ai_detection_service(ai_config)
        prompt_optimizer = AIDetectionPromptOptimizer()
        dynamic_generator = DynamicPromptGenerator()
        quality_scorer = ContentQualityScorer(human_threshold=75.0)
        content_analyzer = ContentAnalyzer()
        
        # Load materials and find files
        generator = DynamicGenerator()
        materials_data = load_materials()
        
        component_dir = Path("content/components") / component_name
        if not component_dir.exists():
            logger.error(f"Component directory not found: {component_dir}")
            return session
        
        material_files = [f for f in component_dir.glob("*.md") if not f.name.endswith('.backup')]
        if not material_files:
            logger.warning(f"No material files found in {component_dir}")
            return session
        
        logger.info(f"📂 Found {len(material_files)} material files to optimize")
        
        # Process each material file
        for file_path in material_files:
            material_name = file_path.stem.replace(f'-laser-cleaning', '').replace('-', '_')
            
            logger.info(f"\n🔧 Processing material: {material_name}")
            
            # Read current content
            try:
                current_content = content_analyzer.extract_content(file_path)
                if not current_content:
                    logger.warning(f"No content found in {file_path}")
                    continue
                    
            except Exception as e:
                logger.error(f"Failed to read {file_path}: {e}")
                continue
            
            # Get current score
            try:
                current_analysis = await asyncio.to_thread(
                    ai_service.detect_ai_content, current_content
                )
                current_score = current_analysis.score
                logger.info(f"  📊 Current AI Detection Score: {current_score:.1f}")
                
            except Exception as e:
                logger.error(f"Failed to analyze current content: {e}")
                current_score = 0.0
            
            # Decide whether to optimize this material
            should_optimize = (
                config.force_reoptimize or 
                current_score < config.min_score_for_skip or
                material_name in session.materials_processed
            )
            
            if not should_optimize:
                logger.info(f"  ⏭️  Skipping {material_name} - score {current_score:.1f} >= {config.min_score_for_skip}")
                continue
            
            # Get material data
            material_data = materials_data.get(material_name, {})
            if not material_data:
                logger.warning(f"No material data found for {material_name}")
                continue
            
            # Get author info
            author_id = material_data.get('author_id', 1)
            author_info = generator.get_author_info(author_id)
            
            # Start optimization iterations
            best_score = current_score
            best_content = current_content
            consecutive_failures = 0
            
            logger.info(f"  🎯 Starting optimization iterations (target: {config.target_score})")
            
            for iteration in range(1, config.max_iterations + 1):
                try:
                    logger.info(f"    🔄 Iteration {iteration}/{config.max_iterations}")
                    
                    # Quality analysis
                    quality_result = quality_scorer.score_content(
                        current_content, material_data, author_info
                    )
                    
                    # AI detection analysis
                    try:
                        ai_result = await asyncio.wait_for(
                            asyncio.to_thread(ai_service.detect_ai_content, current_content),
                            timeout=30,
                        )
                        current_score = ai_result.score
                        logger.info(f"      📊 Score: {current_score:.1f} (Best: {best_score:.1f})")
                        
                    except asyncio.TimeoutError:
                        logger.error(f"      AI detection timeout in iteration {iteration}")
                        consecutive_failures += 1
                        continue
                    except Exception as e:
                        logger.error(f"      AI detection failed: {e}")
                        consecutive_failures += 1
                        continue
                    
                    # Check for improvement
                    improvement = current_score - best_score
                    if current_score > best_score:
                        best_score = current_score
                        best_content = current_content
                        logger.info(f"      ✅ New best score: {best_score:.1f} (+{improvement:.1f})")
                        consecutive_failures = 0
                        
                        # Update session progress
                        session.update_material_progress(
                            material_name, iteration, best_score, improvement, best_content
                        )
                    
                    # Check if target reached
                    if current_score >= config.target_score:
                        logger.info(f"      🎯 Target reached! Score: {current_score:.1f}")
                        break
                    
                    # Generate optimization suggestions
                    winston_result_dict = {
                        "overall_score": ai_result.score,
                        "classification": ai_result.classification,
                        "confidence": ai_result.confidence,
                        "processing_time": ai_result.processing_time,
                        "provider": ai_result.provider,
                        "details": ai_result.details or {},
                    }
                    
                    improvement_context = {
                        "material_name": material_name,
                        "current_score": current_score,
                        "target_score": config.target_score,
                        "iteration": iteration,
                        "quality_metrics": {
                            "overall": quality_result.overall_score,
                            "believability": quality_result.believability_score,
                            "authenticity": quality_result.authenticity_score,
                        }
                    }
                    
                    # Generate enhanced content
                    try:
                        enhanced_prompt = dynamic_generator.generate_optimized_prompt(
                            material_name=material_name,
                            author_id=author_id,
                            winston_result=winston_result_dict,
                            improvement_context=improvement_context,
                            current_content=current_content
                        )
                        
                        # Generate new content
                        new_content = await asyncio.wait_for(
                            asyncio.to_thread(
                                generator.generate_content,
                                material_name,
                                component_name,
                                enhanced_prompt
                            ),
                            timeout=60
                        )
                        
                        current_content = new_content
                        logger.info(f"      🔄 Content regenerated ({len(new_content)} chars)")
                        
                    except asyncio.TimeoutError:
                        logger.error(f"      Content generation timeout")
                        consecutive_failures += 1
                    except Exception as e:
                        logger.error(f"      Content generation failed: {e}")
                        consecutive_failures += 1
                    
                    # Check stopping conditions
                    if improvement < config.improvement_threshold and iteration > 1:
                        consecutive_failures += 1
                        logger.warning(f"      Minimal improvement: {improvement:.1f}")
                    
                    if consecutive_failures >= config.consecutive_failure_limit:
                        logger.warning(f"      🛑 Stopping after {consecutive_failures} consecutive issues")
                        break
                        
                except Exception as e:
                    logger.error(f"      Error in iteration {iteration}: {e}")
                    consecutive_failures += 1
            
            # Save best content if improved
            if best_score > current_analysis.score:
                total_improvement = best_score - current_analysis.score
                logger.info(f"  ✅ Material optimized: {current_analysis.score:.1f} → {best_score:.1f} (+{total_improvement:.1f})")
                
                # Update the file with best content
                try:
                    content_analyzer.update_content_with_metadata(
                        file_path, best_content, {
                            "ai_detection_analysis": {
                                "score": best_score,
                                "optimization_iterations": session.materials_processed.get(material_name, {}).get("iterations", 0),
                                "session_id": session.session_id,
                                "optimized_at": datetime.now().isoformat()
                            }
                        }
                    )
                    logger.info(f"  💾 Updated {file_path}")
                    
                except Exception as e:
                    logger.error(f"  ❌ Failed to save {file_path}: {e}")
            else:
                logger.info(f"  ⚪ No improvement for {material_name}")
        
        # Save session progress
        if config.save_progress:
            session.save_session()
            
    except Exception as e:
        logger.error(f"Optimization session failed: {e}")
        raise
    
    logger.info(f"🏁 Optimization session completed: {session.session_id}")
    logger.info(f"📈 Materials processed: {len(session.materials_processed)}")
    logger.info(f"🔄 Total iterations: {session.total_iterations}")
    
    return session


# Convenience functions for different optimization modes

async def force_reoptimize_all(component_name: str = "text") -> OptimizationSession:
    """Force re-optimization of all files regardless of current scores."""
    config = ContinuousOptimizationConfig(
        force_reoptimize=True,
        improvement_threshold=0.5,
        target_score=90.0,
        max_iterations=15,
        aggressive_mode=True
    )
    return await run_continuous_optimization(component_name, config)


async def gentle_optimization(component_name: str = "text") -> OptimizationSession:
    """Gentle optimization that only processes files below 80 score."""
    config = ContinuousOptimizationConfig(
        force_reoptimize=False,
        min_score_for_skip=80.0,
        improvement_threshold=2.0,
        target_score=85.0,
        max_iterations=8
    )
    return await run_continuous_optimization(component_name, config)


async def aggressive_optimization(component_name: str = "text") -> OptimizationSession:
    """Aggressive optimization for maximum improvement."""
    config = ContinuousOptimizationConfig(
        force_reoptimize=True,
        improvement_threshold=0.1,
        target_score=95.0,
        max_iterations=20,
        consecutive_failure_limit=8,
        aggressive_mode=True
    )
    return await run_continuous_optimization(component_name, config)


async def resume_optimization(session_id: str, component_name: str = "text") -> OptimizationSession:
    """Resume a previous optimization session."""
    config = ContinuousOptimizationConfig()
    return await run_continuous_optimization(component_name, config, session_id)
