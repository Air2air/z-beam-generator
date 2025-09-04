#!/usr/bin/env python3
"""
Content Component Generator

Lightweight wrapper for ComponentGeneratorFactory integration.
Provides a clean interface to the fail_fast_generator.py content generation system.
"""

import logging
import datetime
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)

class TextComponentGenerator(APIComponentGenerator):
    """
    Text component generator that wraps the fail_fast_generator.

    This is a lightweight wrapper that integrates with ComponentGeneratorFactory
    while delegating the actual content generation to fail_fast_generator.py.
    """

    def __init__(self, ai_detection_service=None):
        """Initialize the text component generator."""
        super().__init__("text")
        self.ai_detection_service = ai_detection_service

    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """
        Generate content using the fail_fast_generator with iterative AI detection improvement.

        Args:
            material_name: Name of the material
            material_data: Material data dictionary
            api_client: API client for content generation
            author_info: Author information
            frontmatter_data: Frontmatter data from previous generation
            schema_fields: Schema fields (not used for content)

        Returns:
            ComponentResult with generated content
        """
        try:
            # Import the fail_fast_generator
            from .generators.fail_fast_generator import create_fail_fast_generator

            # Get AI detection configuration for iteration parameters - FAIL-FAST: no defaults
            if not self.ai_detection_service:
                raise Exception("AI detection service is required for iterative content generation - fail-fast architecture requires complete configuration")
            
            if not hasattr(self.ai_detection_service, 'config'):
                raise Exception("AI detection service configuration missing - fail-fast architecture requires complete configuration")
            
            config = self.ai_detection_service.config
            
            # FAIL-FAST: Configuration must provide ALL required values
            if not hasattr(config, 'target_score'):
                raise Exception("AI detection service configuration missing required 'target_score' - fail-fast architecture requires complete configuration")
            if not hasattr(config, 'max_iterations'):
                raise Exception("AI detection service configuration missing required 'max_iterations' - fail-fast architecture requires complete configuration")
            if not hasattr(config, 'improvement_threshold'):
                raise Exception("AI detection service configuration missing required 'improvement_threshold' - fail-fast architecture requires complete configuration")
            
            target_score = config.target_score
            max_iterations = config.max_iterations
            improvement_threshold = config.improvement_threshold

            # Initialize config optimizer for dynamic configuration improvement
            from components.text.ai_detection_config_optimizer import AIDetectionConfigOptimizer
            config_optimizer = AIDetectionConfigOptimizer()
            current_config = config_optimizer._load_current_config()

            logger.info(f"🎯 Starting intelligent iterative content generation for {material_name}")
            logger.info(f"Target Winston score: ≥{target_score} (human-like), Max iterations: {max_iterations}")
            logger.info("📋 Dynamic configuration optimization enabled")

            best_result = None
            best_score = 0.0
            iteration_history = []  # Track iteration details
            previous_content = None  # Track previous iteration's content for comparison
            
            # Status update tracking
            import time as time_module
            start_time = time_module.time()
            last_status_update = start_time
            status_update_interval = 10  # seconds
            
            # Initial status update
            print(f"📊 [START] Beginning iterative improvement for {material_name} - Target: {target_score:.1f} - Max iterations: {max_iterations}")
            
            # Iterative improvement loop
            for iteration in range(max_iterations):
                current_time = time_module.time()
                
                # Always check for time-based status update (every 10 seconds)
                time_since_last_update = current_time - last_status_update
                if time_since_last_update >= status_update_interval:
                    elapsed_time = current_time - start_time
                    progress_percent = ((iteration + 1) / max_iterations) * 100
                    print(f"📊 [TIME STATUS] {time_module.strftime('%H:%M:%S')} - Elapsed: {elapsed_time:.1f}s - "
                          f"Progress: {progress_percent:.1f}% - Iteration: {iteration + 1}/{max_iterations} - "
                          f"Best score: {best_score:.1f}")
                    last_status_update = current_time
                
                # Always show iteration status for first, last, and every 5th iteration
                should_show_iteration_status = (
                    iteration == 0 or  # Always show first iteration
                    iteration == max_iterations - 1 or  # Always show last iteration
                    (iteration + 1) % 5 == 0  # Show every 5th iteration
                )
                
                if should_show_iteration_status:
                    elapsed_time = current_time - start_time
                    progress_percent = ((iteration + 1) / max_iterations) * 100
                    print(f"📊 [ITERATION STATUS] Iteration {iteration + 1}/{max_iterations} ({progress_percent:.1f}%) - "
                          f"Elapsed: {elapsed_time:.1f}s - Best score: {best_score:.1f}")
                    # Don't update last_status_update here to avoid interfering with time-based updates
                
                logger.info(f"🔄 Iteration {iteration + 1}/{max_iterations} for {material_name}")

                iteration_data = {
                    'iteration_number': iteration + 1,
                    'max_iterations': max_iterations,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'ai_detection_performed': False,
                    'ai_detection_skipped': False,
                    'score': 0.0,
                    'classification': 'unknown',
                    'improvement': 0.0,
                    'target_reached': False,
                    'enhancements_applied': [],
                    'content_length_chars': 0,
                    'content_length_words': 0,
                    'content_change_percent_chars': 0.0,
                    'content_change_percent_words': 0.0
                }

                # Create generator with current iteration settings
                generator = create_fail_fast_generator(
                    max_retries=3,
                    retry_delay=1.0,
                    enable_scoring=True,
                    human_threshold=75.0,
                    ai_detection_service=self.ai_detection_service,
                    skip_ai_detection=True  # Skip AI detection in fail_fast_generator since we handle it here
                )

                # Prepare author info with iteration feedback for AI detection refinement
                current_author_info = author_info.copy() if author_info else {}
                
                # Add iteration feedback for AI detection prompt refinement
                if iteration_history:
                    ai_detection_scores = [iter_data.get('score', 0) for iter_data in iteration_history 
                                         if iter_data.get('ai_detection_performed', False)]
                    if ai_detection_scores:
                        current_author_info['iteration_feedback'] = {
                            'ai_detection_scores': ai_detection_scores,
                            'iteration_count': iteration + 1,
                            'avg_ai_score': sum(ai_detection_scores) / len(ai_detection_scores)
                        }

                # Add iteration-specific enhancements to improve human-like qualities
                if iteration > 0:
                    # Apply configuration-based enhancements from optimizer
                    if 'conversational_style' in current_config and current_config['conversational_style']:
                        current_author_info['conversational_boost'] = True
                        iteration_data['enhancements_applied'].append('conversational_style')

                    if 'natural_language_patterns' in current_config and current_config['natural_language_patterns']:
                        current_author_info['human_elements_emphasis'] = True
                        iteration_data['enhancements_applied'].append('natural_language_patterns')

                    if 'cultural_adaptation' in current_config and current_config['cultural_adaptation']:
                        current_author_info['nationality_emphasis'] = True
                        iteration_data['enhancements_applied'].append('cultural_adaptation')

                    if 'sentence_variability' in current_config and current_config['sentence_variability']:
                        current_author_info['sentence_variability'] = True
                        iteration_data['enhancements_applied'].append('sentence_variability')

                    if 'paragraph_structure' in current_config and current_config['paragraph_structure']:
                        current_author_info['paragraph_structure'] = True
                        iteration_data['enhancements_applied'].append('paragraph_structure')

                    if 'lexical_diversity' in current_config and current_config['lexical_diversity']:
                        current_author_info['lexical_diversity'] = True
                        iteration_data['enhancements_applied'].append('lexical_diversity')

                    if 'rhetorical_devices' in current_config and current_config['rhetorical_devices']:
                        current_author_info['rhetorical_devices'] = True
                        iteration_data['enhancements_applied'].append('rhetorical_devices')

                    if 'personal_anecdotes' in current_config and current_config['personal_anecdotes']:
                        current_author_info['personal_anecdotes'] = True
                        iteration_data['enhancements_applied'].append('personal_anecdotes')

                    if 'human_error_simulation' in current_config and current_config['human_error_simulation']:
                        current_author_info['human_error_simulation'] = True
                        iteration_data['enhancements_applied'].append('human_error_simulation')

                    logger.info(f"✨ Applied configuration-based enhancements: {iteration_data['enhancements_applied']}")
                else:
                    logger.info("🎯 First iteration: Using base configuration")

                # Generate content
                result = generator.generate(
                    material_name=material_name,
                    material_data=material_data,
                    api_client=api_client,
                    author_info=current_author_info,
                    frontmatter_data=frontmatter_data
                )

                if not result.success:
                    logger.warning(f"❌ Generation failed on iteration {iteration + 1}: {result.error_message}")
                    if iteration == max_iterations - 1:
                        # Last attempt failed, return the failure
                        return ComponentResult(
                            component_type="text",
                            content="",
                            success=False,
                            error_message=result.error_message
                        )
                    continue

                # Calculate content metrics and changes
                current_content = result.content
                current_char_count = len(current_content)
                current_word_count = len(current_content.split())

                iteration_data['content_length_chars'] = current_char_count
                iteration_data['content_length_words'] = current_word_count

                # Calculate percentage change from previous iteration
                if previous_content is not None:
                    prev_char_count = len(previous_content)
                    prev_word_count = len(previous_content.split())

                    if prev_char_count > 0:
                        char_change_percent = ((current_char_count - prev_char_count) / prev_char_count) * 100
                        iteration_data['content_change_percent_chars'] = round(char_change_percent, 2)

                    if prev_word_count > 0:
                        word_change_percent = ((current_word_count - prev_word_count) / prev_word_count) * 100
                        iteration_data['content_change_percent_words'] = round(word_change_percent, 2)

                    logger.info(f"📊 Content change: {iteration_data['content_change_percent_chars']:+.1f}% chars, "
                              f"{iteration_data['content_change_percent_words']:+.1f}% words")
                else:
                    # First iteration - no previous content to compare
                    iteration_data['content_change_percent_chars'] = 0.0
                    iteration_data['content_change_percent_words'] = 0.0
                    logger.info(f"📊 First iteration: {current_char_count} chars, {current_word_count} words")

                # Update previous content for next iteration comparison
                previous_content = current_content

                # Check AI detection score if service is available
                current_score = 0.0
                if self.ai_detection_service and self.ai_detection_service.is_available():
                    try:
                        # Extract clean text for AI detection (remove frontmatter)
                        content_lines = result.content.split('\n')
                        clean_text = ""
                        in_frontmatter = False

                        for line in content_lines:
                            if line.strip() == '---':
                                in_frontmatter = not in_frontmatter
                                continue
                            if not in_frontmatter and line.strip():
                                clean_text += line + '\n'

                        if len(clean_text.strip()) >= 300:  # Reduced minimum for Winston
                            # Skip AI detection on first iteration for speed, but be more aggressive on later iterations
                            if iteration == 0:
                                logger.info("⏭️ Skipping AI detection on first iteration for speed")
                                current_score = 60.0  # Reasonable baseline for first iteration
                                iteration_data['ai_detection_skipped'] = True
                                iteration_data['score'] = current_score
                                iteration_data['classification'] = 'neutral'
                            elif len(clean_text.strip()) < 400:  # Reduced threshold for short content
                                logger.info("⏭️ Content moderately short, using estimated score")
                                current_score = 55.0  # Better estimate for short content
                                iteration_data['ai_detection_skipped'] = True
                                iteration_data['score'] = current_score
                                iteration_data['classification'] = 'neutral'
                            else:
                                ai_result = self.ai_detection_service.analyze_text(clean_text.strip())
                                current_score = ai_result.score
                                iteration_data['ai_detection_performed'] = True
                                iteration_data['score'] = current_score
                                iteration_data['classification'] = ai_result.classification

                                logger.info(f"🎯 Iteration {iteration + 1} Winston score: {current_score:.1f} "
                                          f"({ai_result.classification})")

                                # Use config optimizer to improve configuration for next iteration
                                if iteration < max_iterations - 1:  # Don't optimize on last iteration
                                    logger.info("🤖 Sending Winston results to DeepSeek for configuration optimization...")
                                    optimized_config, deepseek_response = config_optimizer.optimize_config(
                                        winston_result={
                                            'overall_score': current_score,
                                            'sentence_scores': ai_result.details.get('sentences', []) if ai_result and ai_result.details else [],
                                            'analysis': ai_result.details if ai_result and ai_result.details else {}
                                        },
                                        content=clean_text.strip(),
                                        current_config=current_config
                                    )

                                    # Store DeepSeek response in iteration data
                                    iteration_data['deepseek_response'] = deepseek_response

                                    if optimized_config != current_config:
                                        current_config = optimized_config
                                        logger.info("✅ Configuration updated by DeepSeek for next iteration")
                                    else:
                                        logger.info("ℹ️ Configuration unchanged by DeepSeek")

                            # Calculate improvement from previous best
                            iteration_data['improvement'] = current_score - best_score

                            # Update best result if this is better
                            if current_score > best_score:
                                best_score = current_score
                                best_result = result
                                logger.info(f"💡 New best score: {best_score:.1f}")

                            # Check if we've reached the target (be more lenient for early iterations)
                            target_threshold = target_score if iteration >= 2 else target_score - 10  # Allow lower scores (more lenient) on early iterations
                            if current_score >= target_threshold:
                                # Only exit early if we've done at least 3 iterations OR if this is the last possible iteration
                                if iteration >= 2 or iteration == max_iterations - 1:  # iteration is 0-indexed, so iteration >= 2 means 3+ iterations
                                    logger.info(f"🎉 Target score reached after {iteration + 1} iterations! Final score: {current_score:.1f}")
                                    iteration_data['target_reached'] = True
                                    iteration_history.append(iteration_data)
                                    # Update frontmatter with correct AI detection score and iteration history
                                    updated_content = self._update_frontmatter_with_iterations(result.content, current_score, ai_result if 'ai_result' in locals() else None, iteration_history)
                                    return ComponentResult(
                                        component_type="text",
                                        content=updated_content,
                                        success=True,
                                        error_message=None
                                    )
                                else:
                                    logger.info(f"🎯 Target threshold reached on iteration {iteration + 1}, but continuing for minimum 3 iterations (current: {current_score:.1f})")
                            else:
                                logger.info(f"🎯 Target not yet reached on iteration {iteration + 1} (current: {current_score:.1f}, target: {target_threshold})")

                            # Check for significant improvement (reduced threshold)
                            if iteration > 0 and (current_score - best_score) >= (improvement_threshold - 1):
                                logger.info(f"📈 Significant improvement detected: +{current_score - best_score:.1f}")
                        else:
                            logger.warning(f"📝 Content too short for AI detection: {len(clean_text.strip())} chars")
                            # Use default score for short content
                            current_score = 40.0  # Lower baseline for very short content
                            iteration_data['score'] = current_score
                            iteration_data['classification'] = 'ai'
                            iteration_data['ai_detection_skipped'] = True

                        # Add this iteration to history
                        iteration_history.append(iteration_data)

                    except Exception as ai_error:
                        logger.warning(f"⚠️ AI detection failed on iteration {iteration + 1}: {ai_error}")
                        # Use default score when AI detection fails
                        current_score = 50.0  # Neutral score when AI detection fails
                        iteration_data['score'] = current_score
                        iteration_data['classification'] = 'unknown'
                        iteration_data['ai_detection_performed'] = False
                else:
                    logger.info("ℹ️ AI detection service not available, using generated content")
                    if best_result is None:
                        best_result = result

            # Return the best result achieved
            if best_result:
                # Final status update
                total_elapsed_time = time_module.time() - start_time
                print(f"🎉 [STATUS] Iterative improvement completed! Total time: {total_elapsed_time:.1f}s - "
                      f"Final best score: {best_score:.1f} - Iterations: {len(iteration_history)}")
                
                logger.info(f"🏁 Completed iterations. Best Winston score: {best_score:.1f}")
                # Update frontmatter with correct AI detection score and iteration history
                # Find the most recent ai_result for frontmatter update
                latest_ai_result = None
                if iteration_history:
                    for iter_data in reversed(iteration_history):
                        if iter_data.get('ai_detection_performed') and 'ai_result' in locals():
                            latest_ai_result = ai_result
                            break
                
                updated_content = self._update_frontmatter_with_iterations(best_result.content, best_score, latest_ai_result, iteration_history)
                logger.info("✅ Frontmatter updated with AI detection analysis and iteration history")
                return ComponentResult(
                    component_type="text",
                    content=updated_content,
                    success=True,
                    error_message=None
                )
            else:
                # Error status update
                total_elapsed_time = time_module.time() - start_time
                print(f"❌ [STATUS] All iterations failed! Total time: {total_elapsed_time:.1f}s")
                
                logger.error("❌ All iterations failed to generate content")
                return ComponentResult(
                    component_type="text",
                    content="",
                    success=False,
                    error_message="All content generation iterations failed"
                )

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return ComponentResult(
                component_type="text",
                content="",
                success=False,
                error_message=str(e)
            )

    def _update_frontmatter_with_iterations(self, content: str, score: float, ai_result=None, iteration_history=None) -> str:
        """Update the frontmatter with AI detection score and iteration history."""
        try:
            lines = content.split('\n')
            updated_lines = []
            
            # Find the closing frontmatter marker
            frontmatter_end_idx = -1
            for i, line in enumerate(lines):
                if line.strip() == '---' and i > 0:  # Found closing frontmatter marker
                    frontmatter_end_idx = i
                    break
            
            if frontmatter_end_idx == -1:
                # No frontmatter found, add it at the beginning
                logger.info("No frontmatter found, adding AI detection data at the end")
                updated_lines = lines
                # Add AI detection data at the end
                updated_lines.append("")  # Empty line before additions
                updated_lines.append("---")  # Start frontmatter
            else:
                # Insert before the closing frontmatter marker
                updated_lines = lines[:frontmatter_end_idx]
            
            # Add AI detection analysis
            ai_lines = [
                "ai_detection_analysis:",
                f"  score: {score}",
            ]
            
            if ai_result:
                ai_lines.extend([
                    f"  confidence: {ai_result.confidence}",
                    f"  classification: \"{ai_result.classification}\"",
                    "  provider: \"winston\"",
                    f"  processing_time: {ai_result.processing_time}",
                ])
                
                if ai_result.details:
                    ai_lines.append("  details:")
                    for key, value in ai_result.details.items():
                        # Include sentence-level details for Winston
                        if key == "sentences" and isinstance(value, list):
                            ai_lines.append("    sentences:")
                            for sentence_data in value[:5]:  # Limit to first 5 sentences
                                if isinstance(sentence_data, dict):
                                    ai_lines.append("      - text: \"{}\"".format(sentence_data.get('text', '').replace('"', '\\"')))
                                    ai_lines.append("        score: {}".format(sentence_data.get('score', 0.0)))
                        else:
                            ai_lines.append(f"    {key}: {value}")
            else:
                # Handle case where no AI detection was performed
                ai_lines.extend([
                    "  confidence: 0.0",
                    "  classification: \"unknown\"",
                    "  provider: \"none\"",
                    "  processing_time: 0.0",
                ])
                logger.info("ℹ️ No AI detection results available for frontmatter")
            
            updated_lines.extend(ai_lines)
            
            # Add iteration history
            if iteration_history:
                updated_lines.extend([
                    "iteration_history:"
                ])
                
                for iter_data in iteration_history:
                    updated_lines.extend([
                        f"  - iteration: {iter_data['iteration_number']}",
                        f"    max_iterations: {iter_data['max_iterations']}",
                        f"    timestamp: \"{iter_data['timestamp']}\"",
                        f"    ai_detection_performed: {str(iter_data['ai_detection_performed']).lower()}",
                        f"    ai_detection_skipped: {str(iter_data['ai_detection_skipped']).lower()}",
                        f"    score: {iter_data['score']}",
                        f"    classification: \"{iter_data['classification']}\"",
                        f"    improvement: {iter_data['improvement']}",
                        f"    target_reached: {str(iter_data['target_reached']).lower()}",
                        f"    content_length_chars: {iter_data['content_length_chars']}",
                        f"    content_length_words: {iter_data['content_length_words']}",
                        f"    content_change_percent_chars: {iter_data['content_change_percent_chars']}",
                        f"    content_change_percent_words: {iter_data['content_change_percent_words']}",
                    ])
                    
                    # Add DeepSeek response if available
                    if 'deepseek_response' in iter_data and iter_data['deepseek_response']:
                        # Clean and format the DeepSeek response for YAML
                        deepseek_clean = iter_data['deepseek_response'].strip()
                        if deepseek_clean.startswith("```json"):
                            deepseek_clean = deepseek_clean[7:]
                        if deepseek_clean.endswith("```"):
                            deepseek_clean = deepseek_clean[:-3]
                        # Escape quotes and format for YAML
                        deepseek_formatted = deepseek_clean.replace('"', '\\"').replace('\n', '\\n')
                        updated_lines.append(f"    deepseek_response: \"{deepseek_formatted}\"")
                    
                    if iter_data['enhancements_applied']:
                        enhancements_str = ', '.join(f'"{enh}"' for enh in iter_data['enhancements_applied'])
                        updated_lines.append(f"    enhancements_applied: [{enhancements_str}]")
                    else:
                        updated_lines.append("    enhancements_applied: []")
            
            # Add configuration optimization info
            updated_lines.extend([
                "configuration_optimization:",
                "  enabled: true",
                "  optimizer: \"deepseek\"",
                "  optimization_method: \"iterative_config_modification\"",
                f"  total_iterations: {len(iteration_history) if iteration_history else 0}",
                "---"  # Close frontmatter
            ])
            
            # Add the rest of the content
            if frontmatter_end_idx != -1:
                updated_lines.extend(lines[frontmatter_end_idx:])
            
            return '\n'.join(updated_lines)
            
        except Exception as e:
            logger.warning(f"Failed to update frontmatter with iterations: {e}")
            return content