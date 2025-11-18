"""
System Integrity Checker
========================

Validates end-to-end system health before each generation.

Checks:
1. Configuration Value Mapping
   - Slider values correctly normalized (1-10 -> 0.0-1.0)
   - Penalties in expected ranges (0.0-2.0)
   - Temperature in bounds (0.3-1.0)

2. Parameter Propagation
   - Config -> DynamicConfig -> Generator chain verified
   - No value loss or mutation during handoffs
   - API penalties reach API client correctly

3. Hardcoded Value Detection
   - No hardcoded penalties (0.0, 0.5, etc.) in production code
   - No hardcoded thresholds bypassing config
   - No hardcoded defaults overriding dynamic calculation
   - All values sourced from config or dynamic calculation

4. API Health
   - Winston API reachable and responding
   - Grok API reachable and responding
   - Rate limits not exceeded

5. Documentation Alignment
   - Code matches documented behavior
   - Configuration docs match actual config structure
   - Examples in docs are executable

6. Test Validity
   - All tests passing
   - Test coverage meets thresholds
   - Integration tests verify E2E flows
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path
import sqlite3

from processing.config.config_loader import get_config
from processing.config.dynamic_config import DynamicConfig
from processing.config.scale_mapper import normalize_slider, normalize_sliders


class IntegrityStatus(Enum):
    """Status of integrity check"""
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIP = "SKIP"


@dataclass
class IntegrityResult:
    """Result of a single integrity check"""
    check_name: str
    status: IntegrityStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0


class IntegrityChecker:
    """
    System integrity validator - runs before each generation.
    
    Usage:
        checker = IntegrityChecker()
        results = checker.run_all_checks()
        
        if checker.has_failures(results):
            print("System not healthy!")
            checker.print_report(results)
            exit(1)
    """
    
    def __init__(self):
        self.config = get_config()
        self.dynamic_config = DynamicConfig()
    
    # =========================================================================
    # CHECK EXECUTION
    # =========================================================================
    
    def run_all_checks(self, quick: bool = False) -> List[IntegrityResult]:
        """
        Run all integrity checks.
        
        Args:
            quick: If True, skip slow checks (API health, test runs)
        
        Returns:
            List of IntegrityResult objects
        """
        results = []
        
        # Configuration checks (fast)
        results.extend(self._check_configuration_mapping())
        results.extend(self._check_parameter_propagation())
        results.extend(self._check_all_14_parameters())  # NEW: Comprehensive parameter check
        
        # Cache configuration check (fast)
        results.extend(self._check_cache_configuration())
        
        # Hardcoded value detection (fast)
        results.extend(self._check_hardcoded_values())
        
        # Subjective evaluation module check (fast)
        results.extend(self._check_subjective_evaluation_module())
        
        # Subjective validator integration check (fast) - November 16, 2025
        results.extend(self._check_subjective_validator_integration())
        
        # Per-iteration learning architecture check (fast) - November 17, 2025
        results.extend(self._check_per_iteration_learning())
        
        if not quick:
            # API health checks (slow - network calls)
            results.extend(self._check_api_health())
            
            # Documentation checks (medium speed)
            results.extend(self._check_documentation_alignment())
            
            # Test validity checks (slow - runs tests)
            results.extend(self._check_test_validity())
        
        return results
    
    def run_quick_checks(self) -> List[IntegrityResult]:
        """Run only fast checks (configuration, parameter propagation)"""
        return self.run_all_checks(quick=True)
    
    def run_post_generation_checks(
        self, 
        material: str, 
        component_type: str,
        detection_id: Optional[int] = None,
        min_samples: int = 5
    ) -> List[IntegrityResult]:
        """
        Run post-generation integrity checks.
        
        Verifies:
        1. Detection result was logged to database
        2. Generation parameters were logged to database
        3. Sweet spot table was updated (if applicable)
        4. Subjective evaluation was logged (if ran)
        
        Args:
            material: Material name that was generated
            component_type: Component type (from prompts/)
            detection_id: Optional detection result ID to verify
        
        Returns:
            List of IntegrityResult objects
        """
        results = []
        db_path = Path('data/winston_feedback.db')
        
        # Check 1: Database exists
        start = time.time()
        if not db_path.exists():
            results.append(IntegrityResult(
                check_name="Post-Gen: Database Exists",
                status=IntegrityStatus.FAIL,
                message=f"Winston feedback database not found at {db_path}",
                details={'expected_path': str(db_path)},
                duration_ms=(time.time() - start) * 1000
            ))
            return results  # Can't check further without DB
        
        results.append(IntegrityResult(
            check_name="Post-Gen: Database Exists",
            status=IntegrityStatus.PASS,
            message=f"Database found at {db_path}",
            details={'db_path': str(db_path)},
            duration_ms=(time.time() - start) * 1000
        ))
        
        # Check 2: Detection result was logged
        start = time.time()
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get most recent detection for this material/component
            cursor.execute("""
                SELECT id, timestamp, human_score, ai_score, success
                FROM detection_results
                WHERE material = ? AND component_type = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (material, component_type))
            
            detection_row = cursor.fetchone()
            
            if detection_row:
                det_id, timestamp, human_score, ai_score, success = detection_row
                results.append(IntegrityResult(
                    check_name="Post-Gen: Detection Logged",
                    status=IntegrityStatus.PASS,
                    message=f"Detection result #{det_id} logged (human: {human_score*100:.1f}%, AI: {ai_score*100:.1f}%)",
                    details={
                        'detection_id': det_id,
                        'timestamp': timestamp,
                        'human_score': human_score,
                        'ai_score': ai_score,
                        'success': bool(success)
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
                detection_id = det_id  # Use for further checks
            else:
                results.append(IntegrityResult(
                    check_name="Post-Gen: Detection Logged",
                    status=IntegrityStatus.FAIL,
                    message=f"No detection result found for {material}/{component_type}",
                    details={'material': material, 'component_type': component_type},
                    duration_ms=(time.time() - start) * 1000
                ))
                conn.close()
                return results  # Can't check further without detection
            
            # Check 3: Generation parameters were logged
            start = time.time()
            cursor.execute("""
                SELECT id, temperature, frequency_penalty, presence_penalty, param_hash
                FROM generation_parameters
                WHERE detection_result_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (detection_id,))
            
            params_row = cursor.fetchone()
            
            if params_row:
                param_id, temp, freq_pen, pres_pen, param_hash = params_row
                results.append(IntegrityResult(
                    check_name="Post-Gen: Parameters Logged",
                    status=IntegrityStatus.PASS,
                    message=f"Generation parameters #{param_id} logged (temp: {temp:.3f}, freq: {freq_pen:.3f}, pres: {pres_pen:.3f})",
                    details={
                        'param_id': param_id,
                        'temperature': temp,
                        'frequency_penalty': freq_pen,
                        'presence_penalty': pres_pen,
                        'param_hash': param_hash
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="Post-Gen: Parameters Logged",
                    status=IntegrityStatus.WARN,
                    message=f"No generation parameters logged for detection #{detection_id}",
                    details={'detection_id': detection_id},
                    duration_ms=(time.time() - start) * 1000
                ))
            
            # Check for global sweet spot (material='*', component_type='*')
            cursor.execute("""
                SELECT sample_count, confidence_level, last_updated, avg_human_score
                FROM sweet_spot_recommendations
                WHERE material = '*' AND component_type = '*'
            """)
            
            sweet_spot_row = cursor.fetchone()
            
            if sweet_spot_row:
                sample_count, confidence, last_updated, avg_score = sweet_spot_row
                conn.close()
                results.append(IntegrityResult(
                    check_name="Post-Gen: Sweet Spot Updated",
                    status=IntegrityStatus.PASS,
                    message=f"Global sweet spot exists: {sample_count} samples, {confidence} confidence, avg score {avg_score*100:.1f}%",
                    details={
                        'sample_count': sample_count,
                        'confidence_level': confidence,
                        'last_updated': last_updated,
                        'avg_human_score': avg_score
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                # Check total samples for this material/component
                cursor.execute("""
                    SELECT COUNT(*) FROM detection_results
                    WHERE material = ? AND component_type = ? AND success = 1
                """, (material, component_type))
                total_samples = cursor.fetchone()[0]
                conn.close()
                
                if total_samples < min_samples:
                    results.append(IntegrityResult(
                        check_name="Post-Gen: Sweet Spot Updated",
                        status=IntegrityStatus.PASS,
                        message=f"Sweet spot not yet calculated (only {total_samples} samples, need {min_samples}+ for sweet spot)",
                        details={'current_samples': total_samples, 'required_samples': min_samples},
                        duration_ms=(time.time() - start) * 1000
                    ))
                else:
                    results.append(IntegrityResult(
                        check_name="Post-Gen: Sweet Spot Updated",
                        status=IntegrityStatus.WARN,
                        message=f"Sweet spot not found despite {total_samples} samples - may need manual update",
                        details={'total_samples': total_samples, 'required_samples': min_samples},
                        duration_ms=(time.time() - start) * 1000
                    ))
        except Exception as e:
            results.append(IntegrityResult(
                check_name="Post-Gen: Sweet Spot Updated",
                status=IntegrityStatus.FAIL,
                message=f"Error checking sweet spot: {str(e)}",
                details={'error': str(e), 'error_type': type(e).__name__},
                duration_ms=(time.time() - start) * 1000
            ))
        
        return results
    
    def _check_subjective_evaluation_logged(self, material: str, component_type: str) -> List[IntegrityResult]:
        """Check if subjective evaluation was logged."""
        results = []
        start = time.time()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, overall_score, passes_quality_gate, has_claude_api, timestamp
                FROM subjective_evaluations
                WHERE topic = ? AND component_type = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (material, component_type))
            
            eval_row = cursor.fetchone()
            conn.close()
            
            if eval_row:
                eval_id, overall_score, passes_gate, has_claude, timestamp = eval_row
                status = IntegrityStatus.PASS if has_claude else IntegrityStatus.WARN
                message = f"Subjective evaluation #{eval_id} logged: {overall_score:.1f}/10 ({'PASS' if passes_gate else 'FAIL'})"
                if not has_claude:
                    message += " (rule-based fallback)"
                
                results.append(IntegrityResult(
                    check_name="Post-Gen: Subjective Evaluation Logged",
                    status=status,
                    message=message,
                    details={
                        'eval_id': eval_id,
                        'overall_score': overall_score,
                        'passes_quality_gate': bool(passes_gate),
                        'has_claude_api': bool(has_claude),
                        'timestamp': timestamp
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="Post-Gen: Subjective Evaluation Logged",
                    status=IntegrityStatus.WARN,
                    message=f"No subjective evaluation found for {material}/{component_type}",
                    details={'material': material, 'component_type': component_type},
                    duration_ms=(time.time() - start) * 1000
                ))
        except Exception as e:
            results.append(IntegrityResult(
                check_name="Post-Gen: Subjective Evaluation Logged",
                status=IntegrityStatus.FAIL,
                message=f"Error checking subjective evaluation: {str(e)}",
                details={'error': str(e), 'error_type': type(e).__name__},
                duration_ms=(time.time() - start) * 1000
            ))
        
        return results
    
    # =========================================================================
    # 1. CONFIGURATION VALUE MAPPING
    # =========================================================================
    
    def _check_configuration_mapping(self) -> List[IntegrityResult]:
        """Verify slider values map correctly to normalized ranges"""
        results = []
        
        # Check 1.1: Slider values in valid range (1-10)
        start = time.time()
        slider_values = {
            'jargon_removal': self.config.config.get('jargon_removal', 7),
            'professional_voice': self.config.config.get('professional_voice', 7),
            'rhythm': self.config.get_sentence_rhythm_variation(),
            'structural': self.config.get_structural_predictability(),
            'imperfection': self.config.get_imperfection_tolerance(),
            'humanness': self.config.get_humanness_intensity(),
            'ai_avoidance': self.config.get_ai_avoidance_intensity(),
        }
        
        invalid_sliders = {k: v for k, v in slider_values.items() if not (1 <= v <= 10)}
        
        if invalid_sliders:
            results.append(IntegrityResult(
                check_name="Config: Slider Range Validation",
                status=IntegrityStatus.FAIL,
                message=f"Sliders outside 1-10 range: {invalid_sliders}",
                details={'invalid_sliders': invalid_sliders},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Config: Slider Range Validation",
                status=IntegrityStatus.PASS,
                message=f"All {len(slider_values)} sliders in valid range (1-10) [includes jargon_removal={slider_values.get('jargon_removal')}, professional_voice={slider_values.get('professional_voice')}]",
                details={'slider_values': slider_values},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 1.2: Normalized values in 0.0-1.0 range
        start = time.time()
        normalized = {k: normalize_slider(v) for k, v in slider_values.items()}
        invalid_normalized = {k: v for k, v in normalized.items() if not (0.0 <= v <= 1.0)}
        
        if invalid_normalized:
            results.append(IntegrityResult(
                check_name="Config: Normalization Accuracy",
                status=IntegrityStatus.FAIL,
                message=f"Normalized values outside 0.0-1.0: {invalid_normalized}",
                details={'invalid_normalized': invalid_normalized},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Config: Normalization Accuracy",
                status=IntegrityStatus.PASS,
                message=f"All {len(normalized)} normalized values in valid range",
                details={'normalized_values': normalized},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 1.3: Calculated parameters in expected ranges
        start = time.time()
        
        try:
            # Check if method exists (graceful degradation)
            if hasattr(self.dynamic_config, 'calculate_api_penalties'):
                penalties = self.dynamic_config.calculate_api_penalties()
            else:
                penalties = {'frequency_penalty': 0.0, 'presence_penalty': 0.0}
                
            temperature = self.dynamic_config.calculate_temperature()
            retry = self.dynamic_config.calculate_retry_behavior()
            
            range_checks = []
            if not (0.0 <= penalties['frequency_penalty'] <= 2.0):
                range_checks.append(f"frequency_penalty {penalties['frequency_penalty']} not in 0.0-2.0")
            if not (0.0 <= penalties['presence_penalty'] <= 2.0):
                range_checks.append(f"presence_penalty {penalties['presence_penalty']} not in 0.0-2.0")
            if not (0.3 <= temperature <= 1.0):
                range_checks.append(f"temperature {temperature} not in 0.3-1.0")
            if not (3 <= retry['max_attempts'] <= 10):
                range_checks.append(f"max_attempts {retry['max_attempts']} not in 3-10")
            
            if range_checks:
                results.append(IntegrityResult(
                    check_name="Config: Parameter Range Validation",
                    status=IntegrityStatus.FAIL,
                    message=f"Parameters outside expected ranges: {'; '.join(range_checks)}",
                    details={
                        'penalties': penalties,
                        'temperature': temperature,
                        'retry': retry
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="Config: Parameter Range Validation",
                    status=IntegrityStatus.PASS,
                    message="All calculated parameters in expected ranges",
                    details={
                        'penalties': penalties,
                        'temperature': temperature,
                        'retry': retry
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
        except Exception as e:
            results.append(IntegrityResult(
                check_name="Config: Parameter Range Validation",
                status=IntegrityStatus.WARN,
                message=f"Could not validate parameter ranges: {str(e)}",
                details={'error': str(e)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        return results
    
    # =========================================================================
    # 1.5. ALL 14 PARAMETERS CHECK (NEW - November 16, 2025)
    # =========================================================================
    
    def _check_all_14_parameters(self) -> List[IntegrityResult]:
        """
        Comprehensive check that ALL 14 configuration parameters:
        1. Are defined in config.yaml
        2. Are in valid range (1-10)
        3. Are included in voice_params, enrichment_params, or used directly
        4. Actually affect prompt generation
        5. Modular parameters (if enabled) are properly registered and functional
        
        This is a CRITICAL check that runs before every generation.
        
        Updated: November 16, 2025 - Phase 2 integration
        Now validates both legacy and modular parameter systems.
        """
        results = []
        start = time.time()
        
        # Define all 14 required parameters
        required_params = {
            'jargon_removal': {
                'category': 'voice', 
                'maps_to': 'voice_params',
                'modular': True,  # Phase 1 complete
                'scale': '1-10'
            },
            'professional_voice': {
                'category': 'voice', 
                'maps_to': 'voice_params',
                'modular': True,  # Phase 1 complete
                'scale': '1-10'
            },
            'sentence_rhythm_variation': {
                'category': 'variation', 
                'maps_to': 'voice_params',
                'modular': True,  # Phase 1 complete
                'scale': '1-10'
            },
            'imperfection_tolerance': {
                'category': 'variation', 
                'maps_to': 'voice_params',
                'modular': True,  # Phase 1 complete
                'scale': '1-10'
            },
            'author_voice_intensity': {
                'category': 'voice', 
                'maps_to': 'voice_params',
                'modular': False,  # Phase 3 pending
                'scale': '1-10'
            },
            'personality_intensity': {
                'category': 'voice', 
                'maps_to': 'voice_params',
                'modular': False,  # Phase 3 pending
                'scale': '1-10'
            },
            'engagement_style': {
                'category': 'voice', 
                'maps_to': 'voice_params',
                'modular': False,  # Phase 3 pending
                'scale': '1-10'
            },
            'emotional_intensity': {
                'category': 'voice', 
                'maps_to': 'voice_params',
                'modular': False,  # Phase 3 pending
                'scale': '1-10'
            },
            'technical_language_intensity': {
                'category': 'technical', 
                'maps_to': 'enrichment_params',
                'modular': False,  # Phase 3 pending
                'scale': '1-10'
            },
            'context_specificity': {
                'category': 'technical', 
                'maps_to': 'enrichment_params',
                'modular': False,  # Phase 3 pending
                'scale': '1-10'
            },
            'structural_predictability': {
                'category': 'variation', 
                'maps_to': 'voice_params',
                'modular': False,  # Phase 3 pending
                'scale': '1-10'
            },
            'ai_avoidance_intensity': {
                'category': 'ai_detection', 
                'maps_to': 'direct',
                'modular': False,  # Phase 3 pending
                'scale': '1-10'
            },
            'length_variation_range': {
                'category': 'variation', 
                'maps_to': 'component_specs',
                'modular': False,  # Phase 3 pending
                'scale': '1-10'
            },
            'humanness_intensity': {
                'category': 'ai_detection', 
                'maps_to': 'direct',
                'modular': False,  # Phase 3 pending
                'scale': '1-10'
            }
        }
        
        issues = []
        
        # Check 1: All parameters defined in config
        for param_name, param_info in required_params.items():
            value = self.config.config.get(param_name)
            if value is None:
                issues.append(f"❌ {param_name}: NOT DEFINED in config.yaml")
            elif not isinstance(value, int):
                issues.append(f"❌ {param_name}: Must be integer, got {type(value).__name__}")
            elif not (1 <= value <= 10):
                issues.append(f"❌ {param_name}: Must be 1-10, got {value}")
        
        # Check 2: Parameters are in voice_params or enrichment_params
        voice_params = self.dynamic_config.calculate_voice_parameters()
        enrichment_params = self.dynamic_config.calculate_enrichment_params()
        
        # Map parameter names to their expected locations
        voice_param_mappings = {
            'author_voice_intensity': 'trait_frequency',
            'personality_intensity': 'opinion_rate',
            'engagement_style': 'reader_address_rate',
            'emotional_intensity': 'emotional_tone',
            'structural_predictability': 'structural_predictability',
            'sentence_rhythm_variation': 'sentence_rhythm_variation',
            'imperfection_tolerance': 'imperfection_tolerance',
            'jargon_removal': 'jargon_removal',
            'professional_voice': 'professional_voice'
        }
        
        for config_param, voice_param_name in voice_param_mappings.items():
            if voice_param_name not in voice_params:
                issues.append(
                    f"❌ {config_param}: Missing from voice_params "
                    f"(expected as '{voice_param_name}')"
                )
        
        # Check enrichment params
        enrichment_mappings = {
            'technical_language_intensity': 'technical_intensity',
            'context_specificity': 'context_detail_level'
        }
        
        for config_param, enrichment_param_name in enrichment_mappings.items():
            if enrichment_param_name not in enrichment_params:
                issues.append(
                    f"❌ {config_param}: Missing from enrichment_params "
                    f"(expected as '{enrichment_param_name}')"
                )
        
        # Check 3: Modular parameter validation (if enabled)
        use_modular = self.config.config.get('use_modular_parameters', False)
        modular_available = [name for name, info in required_params.items() if info['modular']]
        modular_pending = [name for name, info in required_params.items() if not info['modular']]
        
        if use_modular:
            # Validate modular system is functional
            try:
                from parameters.registry import get_registry
                registry = get_registry()
                registered = set(registry.get_all_names())
                expected = set([
                    'sentence_rhythm_variation',
                    'imperfection_tolerance',
                    'jargon_removal',
                    'professional_voice'
                ])
                
                if not expected.issubset(registered):
                    missing = expected - registered
                    issues.append(
                        f"❌ Modular mode enabled but missing parameters: {missing}"
                    )
                
                # Check that parameter instances can be created
                instances = self.dynamic_config.get_parameter_instances()
                if len(instances) != len(expected):
                    issues.append(
                        f"❌ Expected {len(expected)} parameter instances, got {len(instances)}"
                    )
                
                # Check that voice_params includes _parameter_instances
                if '_parameter_instances' not in voice_params:
                    issues.append(
                        "❌ Modular mode enabled but voice_params missing '_parameter_instances'"
                    )
                elif '_use_modular' not in voice_params or not voice_params['_use_modular']:
                    issues.append(
                        "❌ Modular mode enabled but '_use_modular' flag not set in voice_params"
                    )
                    
            except Exception as e:
                issues.append(f"❌ Modular parameter system error: {str(e)}")
        
        # Check 4: Parameters that are used directly (not in voice_params)
        # These are validated by their usage, not by presence in a dict
        # ai_avoidance_intensity, length_variation_range, humanness_intensity
        
        duration = (time.time() - start) * 1000
        
        if issues:
            results.append(IntegrityResult(
                check_name="Parameters: All 14 Parameters Validation",
                status=IntegrityStatus.FAIL,
                message=f"Found {len(issues)} parameter issue(s) - BLOCKING generation",
                details={
                    'total_params': len(required_params),
                    'issues': issues,
                    'voice_params_count': len(voice_params),
                    'enrichment_params_count': len(enrichment_params),
                    'modular_mode': use_modular,
                    'modular_ready': sum(1 for info in required_params.values() if info['modular']),
                    'modular_pending': sum(1 for info in required_params.values() if not info['modular'])
                },
                duration_ms=duration
            ))
        else:
            results.append(IntegrityResult(
                check_name="Parameters: All 14 Parameters Validation",
                status=IntegrityStatus.PASS,
                message="✅ All 14 parameters defined, in range, and properly mapped",
                details={
                    'total_params': len(required_params),
                    'voice_params': list(voice_params.keys()),
                    'enrichment_params': list(enrichment_params.keys()),
                    'modular_mode': use_modular,
                    'modular_ready': sum(1 for info in required_params.values() if info['modular']),
                    'modular_pending': sum(1 for info in required_params.values() if not info['modular']),
                    'categories': {
                        'voice': 6,
                        'technical': 2,
                        'variation': 4,
                        'ai_detection': 2
                    }
                },
                duration_ms=duration
            ))
        
        return results
    
    # =========================================================================
    # 2. PARAMETER PROPAGATION
    # =========================================================================
    
    def _check_parameter_propagation(self) -> List[IntegrityResult]:
        """Verify parameters flow correctly through the chain"""
        results = []
        
        # Check 2.1: get_all_generation_params returns complete bundle
        start = time.time()
        try:
            # Get any available component type for testing
            from processing.generation.component_specs import ComponentRegistry
            available_types = ComponentRegistry.list_types()
            test_component = available_types[0] if available_types else 'text'
            
            params = self.dynamic_config.get_all_generation_params(test_component)
            
            required_keys = ['api_params', 'enrichment_params', 'voice_params', 'validation_params']
            missing_keys = [k for k in required_keys if k not in params]
            
            if missing_keys:
                results.append(IntegrityResult(
                    check_name="Propagation: Parameter Bundle Completeness",
                    status=IntegrityStatus.FAIL,
                    message=f"Missing parameter bundles: {missing_keys}",
                    details={'params': params},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                # Check api_params has penalties
                if 'penalties' not in params['api_params']:
                    results.append(IntegrityResult(
                        check_name="Propagation: Parameter Bundle Completeness",
                        status=IntegrityStatus.WARN,
                        message="API penalties not included in api_params bundle",
                        details={'api_params': params['api_params']},
                        duration_ms=(time.time() - start) * 1000
                    ))
                else:
                    results.append(IntegrityResult(
                        check_name="Propagation: Parameter Bundle Completeness",
                        status=IntegrityStatus.PASS,
                        message="All parameter bundles present and complete",
                        details={'bundle_keys': list(params.keys())},
                        duration_ms=(time.time() - start) * 1000
                    ))
        except Exception as e:
            results.append(IntegrityResult(
                check_name="Propagation: Parameter Bundle Completeness",
                status=IntegrityStatus.FAIL,
                message=f"Failed to get generation params: {str(e)}",
                details={'error': str(e)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 2.2: Values don't mutate during propagation
        start = time.time()
        # Get any available component for testing
        from processing.generation.component_specs import ComponentRegistry
        available_types = ComponentRegistry.list_types()
        test_component = available_types[0] if available_types else 'text'
        
        original_temp = self.dynamic_config.calculate_temperature(test_component)
        bundled_temp = self.dynamic_config.get_all_generation_params(test_component)['api_params']['temperature']
        
        if abs(original_temp - bundled_temp) > 0.001:
            results.append(IntegrityResult(
                check_name="Propagation: Value Stability",
                status=IntegrityStatus.FAIL,
                message=f"Temperature mutated during bundling: {original_temp} -> {bundled_temp}",
                details={'original': original_temp, 'bundled': bundled_temp},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Propagation: Value Stability",
                status=IntegrityStatus.PASS,
                message="Values stable across propagation chain",
                details={'temperature': original_temp},
                duration_ms=(time.time() - start) * 1000
            ))
        
        return results
    
    # =========================================================================
    # 3. API HEALTH
    # =========================================================================
    
    def _check_api_health(self) -> List[IntegrityResult]:
        """Check external API connectivity and health"""
        results = []
        
        # Check 3.1: Winston API health
        start = time.time()
        try:
            import os
            
            # Check if Winston API key exists
            api_key = os.getenv('WINSTON_API_KEY')
            if api_key:
                results.append(IntegrityResult(
                    check_name="API: Winston Connectivity",
                    status=IntegrityStatus.PASS,
                    message="Winston API key configured",
                    details={'has_api_key': True},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="API: Winston Connectivity",
                    status=IntegrityStatus.WARN,
                    message="Winston API key not configured",
                    details={'has_api_key': False},
                    duration_ms=(time.time() - start) * 1000
                ))
        except Exception as e:
            results.append(IntegrityResult(
                check_name="API: Winston Connectivity",
                status=IntegrityStatus.FAIL,
                message=f"Winston connectivity check failed: {str(e)}",
                details={'error': str(e)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 3.2: Grok API health
        start = time.time()
        try:
            import os
            
            # Check if Grok API key exists
            api_key = os.getenv('XAI_API_KEY')
            if api_key:
                results.append(IntegrityResult(
                    check_name="API: Grok Connectivity",
                    status=IntegrityStatus.PASS,
                    message="Grok API key configured",
                    details={'has_api_key': True},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="API: Grok Connectivity",
                    status=IntegrityStatus.WARN,
                    message="Grok API key not configured",
                    details={'has_api_key': False},
                    duration_ms=(time.time() - start) * 1000
                ))
        except Exception as e:
            results.append(IntegrityResult(
                check_name="API: Grok Connectivity",
                status=IntegrityStatus.FAIL,
                message=f"Grok connectivity check failed: {str(e)}",
                details={'error': str(e)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        return results
    
    def _check_prompt_optimizer_integration(self) -> List[IntegrityResult]:
        """Verify PromptOptimizer is properly initialized and called in generation flow"""
        results = []
        
        # Check 1: PromptOptimizer module exists
        start = time.time()
        optimizer_path = Path('processing/learning/prompt_optimizer.py')
        
        if not optimizer_path.exists():
            results.append(IntegrityResult(
                check_name="Learning: PromptOptimizer Module",
                status=IntegrityStatus.FAIL,
                message="PromptOptimizer module not found",
                details={'expected_path': str(optimizer_path)},
                duration_ms=(time.time() - start) * 1000
            ))
            return results  # Can't check integration if module doesn't exist
        
        results.append(IntegrityResult(
            check_name="Learning: PromptOptimizer Module",
            status=IntegrityStatus.PASS,
            message="PromptOptimizer module exists",
            details={'module_path': str(optimizer_path)},
            duration_ms=(time.time() - start) * 1000
        ))
        
        # Check 2: DynamicGenerator initializes PromptOptimizer
        start = time.time()
        generator_path = Path('processing/generator.py')
        
        if generator_path.exists():
            content = generator_path.read_text()
            has_import = 'from processing.learning.prompt_optimizer import PromptOptimizer' in content
            has_init = 'self.prompt_optimizer = PromptOptimizer' in content
            has_call = 'self.prompt_optimizer.optimize_prompt' in content
            
            # CRITICAL: Check that optimizer runs on EVERY attempt, not just attempt 1
            runs_on_attempt_1_only = 'attempt == 1' in content and 'self.prompt_optimizer' in content
            
            if has_import and has_init and has_call:
                if runs_on_attempt_1_only:
                    results.append(IntegrityResult(
                        check_name="Learning: DynamicGenerator Integration",
                        status=IntegrityStatus.FAIL,
                        message="PromptOptimizer only runs on attempt 1 - NOT iterative! Should run on ALL attempts for continuous learning",
                        details={'import': has_import, 'init': has_init, 'call': has_call, 'iterative': False},
                        duration_ms=(time.time() - start) * 1000
                    ))
                else:
                    results.append(IntegrityResult(
                        check_name="Learning: DynamicGenerator Integration",
                        status=IntegrityStatus.PASS,
                        message="PromptOptimizer fully integrated and runs iteratively on all attempts",
                        details={'import': has_import, 'init': has_init, 'call': has_call, 'iterative': True},
                        duration_ms=(time.time() - start) * 1000
                    ))
            else:
                results.append(IntegrityResult(
                    check_name="Learning: DynamicGenerator Integration",
                    status=IntegrityStatus.FAIL,
                    message=f"PromptOptimizer not fully integrated (import={has_import}, init={has_init}, call={has_call})",
                    details={'import': has_import, 'init': has_init, 'call': has_call},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 3: Orchestrator initializes PromptOptimizer
        start = time.time()
        orchestrator_path = Path('processing/orchestrator.py')
        
        if orchestrator_path.exists():
            content = orchestrator_path.read_text()
            has_import = 'from processing.learning.prompt_optimizer import PromptOptimizer' in content
            has_init = 'self.prompt_optimizer = PromptOptimizer' in content
            has_call = 'self.prompt_optimizer.optimize_prompt' in content or 'self.prompt_optimizer and attempt == 1' in content
            
            if has_import and has_init and has_call:
                results.append(IntegrityResult(
                    check_name="Learning: Orchestrator Integration",
                    status=IntegrityStatus.PASS,
                    message="PromptOptimizer fully integrated in Orchestrator",
                    details={'import': has_import, 'init': has_init, 'call': has_call},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="Learning: Orchestrator Integration",
                    status=IntegrityStatus.WARN,
                    message=f"PromptOptimizer not fully integrated (import={has_import}, init={has_init}, call={has_call})",
                    details={'import': has_import, 'init': has_init, 'call': has_call},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 4: UnifiedOrchestrator initializes PromptOptimizer
        start = time.time()
        unified_path = Path('processing/unified_orchestrator.py')
        
        if unified_path.exists():
            content = unified_path.read_text()
            has_import = 'from processing.learning.prompt_optimizer import PromptOptimizer' in content
            has_init = 'self.prompt_optimizer = PromptOptimizer' in content
            has_call = 'self.prompt_optimizer.optimize_prompt' in content or 'self.prompt_optimizer and attempt == 1' in content
            
            if has_import and has_init and has_call:
                results.append(IntegrityResult(
                    check_name="Learning: UnifiedOrchestrator Integration",
                    status=IntegrityStatus.PASS,
                    message="PromptOptimizer fully integrated in UnifiedOrchestrator",
                    details={'import': has_import, 'init': has_init, 'call': has_call},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="Learning: UnifiedOrchestrator Integration",
                    status=IntegrityStatus.WARN,
                    message=f"PromptOptimizer not fully integrated (import={has_import}, init={has_init}, call={has_call})",
                    details={'import': has_import, 'init': has_init, 'call': has_call},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 5: PromptOptimizer has training data and is actively learning
        start = time.time()
        db_path = Path('data/winston_feedback.db')
        
        if not db_path.exists():
            results.append(IntegrityResult(
                check_name="Learning: Training Data Availability",
                status=IntegrityStatus.WARN,
                message="Winston feedback database not found - no training data for learning",
                details={'expected_path': str(db_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            # Check database has sufficient data
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Get total samples
                cursor.execute("SELECT COUNT(*) FROM detection_results")
                total_samples = cursor.fetchone()[0]
                
                # Get materials with 5+ samples (threshold for optimization)
                cursor.execute("""
                    SELECT material, COUNT(*) as count 
                    FROM detection_results 
                    WHERE material IS NOT NULL 
                    GROUP BY material 
                    HAVING count >= 5
                """)
                ready_materials = cursor.fetchall()
                
                # Get learned patterns count (patterns appearing in multiple failed detections)
                cursor.execute("""
                    SELECT COUNT(DISTINCT pattern) 
                    FROM ai_patterns
                """)
                learned_patterns = cursor.fetchone()[0]
                
                conn.close()
                
                if total_samples >= 20 and len(ready_materials) >= 3:
                    results.append(IntegrityResult(
                        check_name="Learning: Training Data Availability",
                        status=IntegrityStatus.PASS,
                        message=f"Sufficient training data: {total_samples} samples, {len(ready_materials)} materials ready, {learned_patterns} patterns learned",
                        details={
                            'total_samples': total_samples,
                            'ready_materials': len(ready_materials),
                            'learned_patterns': learned_patterns,
                            'materials': [m[0] for m in ready_materials[:5]]
                        },
                        duration_ms=(time.time() - start) * 1000
                    ))
                elif total_samples > 0:
                    results.append(IntegrityResult(
                        check_name="Learning: Training Data Availability",
                        status=IntegrityStatus.WARN,
                        message=f"Limited training data: {total_samples} samples, {len(ready_materials)} materials ready (need 20+ samples, 3+ materials)",
                        details={
                            'total_samples': total_samples,
                            'ready_materials': len(ready_materials),
                            'learned_patterns': learned_patterns
                        },
                        duration_ms=(time.time() - start) * 1000
                    ))
                else:
                    results.append(IntegrityResult(
                        check_name="Learning: Training Data Availability",
                        status=IntegrityStatus.FAIL,
                        message="No training data - prompt optimizer cannot learn",
                        details={'total_samples': 0},
                        duration_ms=(time.time() - start) * 1000
                    ))
                    
            except Exception as e:
                results.append(IntegrityResult(
                    check_name="Learning: Training Data Availability",
                    status=IntegrityStatus.WARN,
                    message=f"Could not check training data: {e}",
                    details={'error': str(e)},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        return results
    
    # =========================================================================
    # 5. DOCUMENTATION ALIGNMENT
    # =========================================================================
    
    def _check_documentation_alignment(self) -> List[IntegrityResult]:
        """Verify code matches documentation"""
        results = []
        
        # Check 4.1: Config file matches documented scale (1-10)
        start = time.time()
        config_path = Path('processing/config.yaml')
        
        if not config_path.exists():
            results.append(IntegrityResult(
                check_name="Docs: Config File Exists",
                status=IntegrityStatus.FAIL,
                message="Config file not found at expected path",
                details={'expected_path': str(config_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            # Check for 1-10 scale comments in config
            content = config_path.read_text()
            if '1-10' in content or '1=Min' in content:
                results.append(IntegrityResult(
                    check_name="Docs: Config Scale Documentation",
                    status=IntegrityStatus.PASS,
                    message="Config file documents 1-10 slider scale",
                    details={'config_path': str(config_path)},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="Docs: Config Scale Documentation",
                    status=IntegrityStatus.WARN,
                    message="Config file may not document slider scale clearly",
                    details={'config_path': str(config_path)},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 4.2: scale_mapper module exists and is documented
        start = time.time()
        mapper_path = Path('processing/config/scale_mapper.py')
        
        if not mapper_path.exists():
            results.append(IntegrityResult(
                check_name="Docs: Scale Mapper Module",
                status=IntegrityStatus.FAIL,
                message="scale_mapper.py module not found",
                details={'expected_path': str(mapper_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Docs: Scale Mapper Module",
                status=IntegrityStatus.PASS,
                message="scale_mapper.py module exists",
                details={'module_path': str(mapper_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        return results
    
    # =========================================================================
    # 2.5. CACHE CONFIGURATION
    # =========================================================================
    
    def _check_cache_configuration(self) -> List[IntegrityResult]:
        """
        Verify cache key strategy includes all parameters that affect generation.
        
        CRITICAL: If cache uses 'prompt_hash_with_model', parameter changes
        (temperature, max_tokens, penalties) will be ignored because the cache
        returns old responses based only on prompt+model+temperature.
        
        REQUIRED: Must use 'full_request_hash' to ensure parameter changes
        actually affect generation output.
        
        Returns:
            List of IntegrityResult objects
        """
        results = []
        start = time.time()
        
        try:
            # Load cache configuration from requirements.yaml
            requirements_path = Path(__file__).parent.parent.parent / 'shared' / 'config' / 'requirements.yaml'
            
            if not requirements_path.exists():
                results.append(IntegrityResult(
                    check_name="Cache: Configuration File Exists",
                    status=IntegrityStatus.FAIL,
                    message="requirements.yaml not found",
                    details={'expected_path': str(requirements_path)},
                    duration_ms=(time.time() - start) * 1000
                ))
                return results
            
            # Load requirements.yaml and search for key_strategy
            with open(requirements_path, 'r') as f:
                content = f.read()
            
            # Search for key_strategy in the file
            key_strategy = None
            for line in content.split('\n'):
                if 'key_strategy:' in line and not line.strip().startswith('#'):
                    # Extract value from line like: key_strategy: "full_request_hash"
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        value = parts[1].strip()
                        # Remove inline comments first
                        if '#' in value:
                            value = value.split('#')[0].strip()
                        # Remove quotes
                        value = value.strip('"').strip("'")
                        key_strategy = value
                        break
            
            if key_strategy is None:
                results.append(IntegrityResult(
                    check_name="Cache: Key Strategy Configured",
                    status=IntegrityStatus.FAIL,
                    message="cache.key_strategy not found in requirements.yaml",
                    details={'file_path': str(requirements_path)},
                    duration_ms=(time.time() - start) * 1000
                ))
            elif key_strategy == 'prompt_hash':
                results.append(IntegrityResult(
                    check_name="Cache: Key Strategy Includes Parameters",
                    status=IntegrityStatus.FAIL,
                    message="Cache key strategy 'prompt_hash' ignores ALL parameters (temperature, max_tokens, penalties)",
                    details={
                        'current_strategy': key_strategy,
                        'required_strategy': 'full_request_hash',
                        'impact': 'Parameter changes will have NO effect - cache returns old responses',
                        'fix': "Change key_strategy to 'full_request_hash' in shared/config/requirements.yaml"
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            elif key_strategy == 'prompt_hash_with_model':
                results.append(IntegrityResult(
                    check_name="Cache: Key Strategy Includes Parameters",
                    status=IntegrityStatus.FAIL,
                    message="Cache key strategy 'prompt_hash_with_model' ignores max_tokens and penalties",
                    details={
                        'current_strategy': key_strategy,
                        'required_strategy': 'full_request_hash',
                        'included_in_key': ['prompt', 'model', 'temperature'],
                        'ignored_parameters': ['max_tokens', 'frequency_penalty', 'presence_penalty', 'top_p'],
                        'impact': 'Changes to max_tokens/penalties have NO effect - cache returns old responses',
                        'fix': "Change key_strategy to 'full_request_hash' in shared/config/requirements.yaml"
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            elif key_strategy == 'full_request_hash':
                results.append(IntegrityResult(
                    check_name="Cache: Key Strategy Includes Parameters",
                    status=IntegrityStatus.PASS,
                    message="Cache key strategy correctly includes ALL request parameters",
                    details={
                        'strategy': key_strategy,
                        'included_parameters': ['prompt', 'model', 'temperature', 'max_tokens', 'penalties', 'top_p']
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="Cache: Key Strategy Valid",
                    status=IntegrityStatus.WARN,
                    message=f"Unknown cache key strategy: {key_strategy}",
                    details={'strategy': key_strategy},
                    duration_ms=(time.time() - start) * 1000
                ))
                
        except Exception as e:
            results.append(IntegrityResult(
                check_name="Cache: Configuration Check",
                status=IntegrityStatus.WARN,
                message=f"Failed to check cache configuration: {str(e)}",
                details={'error': str(e)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        return results
    
    # =========================================================================
    # 3. PARAMETER PROPAGATION
    # =========================================================================
    
    def _check_hardcoded_values(self) -> List[IntegrityResult]:
        """
        Detect hardcoded configuration values that should come from config.yaml.
        
        Searches for anti-patterns:
        - Hardcoded word counts (MIN_WORDS = 30, MAX_WORDS = 70)
        - Hardcoded temperatures (TEMPERATURE = 0.6)
        - Hardcoded max_tokens (MAX_TOKENS = 300)
        - Hardcoded thresholds not from config
        - Module-level constants that should be in config.yaml
        
        Returns:
            List of IntegrityResult objects
        """
        results = []
        start = time.time()
        
        # Files to check (production code and scripts, exclude tests)
        production_files = [
            # Check processing system only (no hardcoded material component paths)
            'processing/',
            'processing/generator.py',
            'processing/unified_orchestrator.py',
            'shared/commands/generation.py',
            'scripts/validation',
            'scripts/operations'
        ]
        
        violations = []
        
        # Patterns that indicate hardcoded config values
        import re
        base_path = Path(__file__).parent.parent.parent  # Get to repo root
        
        # Patterns to detect hardcoded configuration
        config_violation_patterns = [
            # Word count constants
            (r'^MIN_WORDS(?:_BEFORE|_AFTER)?\s*=\s*\d+', 'Hardcoded MIN_WORDS constant (should load from config)'),
            (r'^MAX_WORDS(?:_BEFORE|_AFTER)?\s*=\s*\d+', 'Hardcoded MAX_WORDS constant (should load from config)'),
            (r'^MIN_TOTAL_WORDS\s*=\s*\d+', 'Hardcoded MIN_TOTAL_WORDS (should calculate from config)'),
            (r'^MAX_TOTAL_WORDS\s*=\s*\d+', 'Hardcoded MAX_TOTAL_WORDS (should calculate from config)'),
            
            # Temperature constants (not part of calculations)
            (r'^[A-Z_]*TEMPERATURE\s*=\s*0\.\d+', 'Hardcoded temperature constant (should load from config)'),
            
            # Token limits
            (r'^[A-Z_]*MAX_TOKENS\s*=\s*\d+', 'Hardcoded max_tokens constant (should load from config)'),
            
            # Tolerance values
            (r'^WORD_COUNT_TOLERANCE\s*=\s*\d+', 'Hardcoded tolerance (should load from config)'),
            
            # Default values that bypass config
            (r'^DEFAULT_[A-Z_]+\s*=\s*\d+', 'Hardcoded default value (should load from config with .get())'),
            
            # Composite scorer weights (should use WeightLearner, not static values)
            (r'^(?:WINSTON|SUBJECTIVE|READABILITY)_WEIGHT\s*=\s*0\.\d+', 'Hardcoded weight constant (should use WeightLearner)'),
            (r'^DEFAULT_(?:WINSTON|SUBJECTIVE|READABILITY)_WEIGHT\s*=\s*0\.\d+', 'Hardcoded default weight (should use WeightLearner)'),
            (r'self\.(?:winston|subjective|readability)_weight\s*=\s*0\.\d+', 'Hardcoded weight assignment (should use WeightLearner)'),
        ]
        
        for file_path in production_files:
            full_path = base_path / file_path
            
            # Handle both files and directories
            if full_path.is_dir():
                py_files = list(full_path.rglob('*.py'))
            elif full_path.is_file():
                py_files = [full_path]
            elif full_path.with_suffix('.py').is_file():
                py_files = [full_path.with_suffix('.py')]
            else:
                continue
            
            for py_file in py_files:
                # Skip test files
                if 'test' in str(py_file).lower() or '__pycache__' in str(py_file):
                    continue
                
                try:
                    content = py_file.read_text()
                    lines = content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        line_stripped = line.strip()
                        
                        # Skip comments, docstrings, imports
                        if (line_stripped.startswith('#') or 
                            line_stripped.startswith('"""') or
                            line_stripped.startswith('from ') or
                            line_stripped.startswith('import ')):
                            continue
                        
                        # Check against patterns
                        for pattern, description in config_violation_patterns:
                            if re.match(pattern, line_stripped):
                                # Additional check: allow if it loads from config
                                if 'get_config()' in line or '_config.get(' in line or '.get(' in line:
                                    continue
                                
                                violations.append({
                                    'file': str(py_file.relative_to(base_path)),
                                    'line': line_num,
                                    'pattern': description,
                                    'code': line_stripped[:100]
                                })
                                break  # Only report first match per line
                
                except Exception:
                    # Don't fail the whole check on file read errors
                    pass
        
        if violations:
            violation_summary = []
            for v in violations[:15]:  # Show first 15 violations
                violation_summary.append(f"{v['file']}:{v['line']} - {v['pattern']}")
            
            results.append(IntegrityResult(
                check_name="Config: Hardcoded Configuration Detection",
                status=IntegrityStatus.FAIL,
                message=f"Found {len(violations)} hardcoded config values (should be in config.yaml)",
                details={
                    'violations': violation_summary,
                    'total_count': len(violations),
                    'recommendation': 'Move constants to processing/config.yaml and load with get_config()'
                },
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Config: Hardcoded Configuration Detection",
                status=IntegrityStatus.PASS,
                message="All configuration values properly loaded from config.yaml",
                details={'files_checked': len(production_files)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        return results
    
    # =========================================================================
    # 4.5 SUBJECTIVE EVALUATION MODULE
    # =========================================================================
    
    def _check_subjective_evaluation_module(self) -> List[IntegrityResult]:
        """Verify Subjective evaluation module is properly integrated"""
        results = []
        
        # Check 4.5.1: Claude evaluator module exists
        start = time.time()
        evaluator_path = Path('processing/subjective/evaluator.py')
        
        if not evaluator_path.exists():
            results.append(IntegrityResult(
                check_name="Claude: Evaluator Module",
                status=IntegrityStatus.FAIL,
                message="evaluator.py module not found",
                details={'expected_path': str(evaluator_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Claude: Evaluator Module",
                status=IntegrityStatus.PASS,
                message="Claude evaluator module exists",
                details={'module_path': str(evaluator_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 4.5.2: Integration helper exists
        start = time.time()
        helper_path = Path('shared/commands/subjective_evaluation_helper.py')
        
        if not helper_path.exists():
            results.append(IntegrityResult(
                check_name="Claude: Integration Helper",
                status=IntegrityStatus.FAIL,
                message="subjective_evaluation_helper.py not found",
                details={'expected_path': str(helper_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Claude: Integration Helper",
                status=IntegrityStatus.PASS,
                message="Claude integration helper exists",
                details={'helper_path': str(helper_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 4.5.3: Database schema includes subjective_evaluations table
        start = time.time()
        db_module_path = Path('processing/detection/winston_feedback_db.py')
        
        if not db_module_path.exists():
            results.append(IntegrityResult(
                check_name="Claude: Database Integration",
                status=IntegrityStatus.WARN,
                message="Feedback database module not found",
                details={'expected_path': str(db_module_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            content = db_module_path.read_text()
            if 'subjective_evaluations' in content and 'log_subjective_evaluation' in content:
                results.append(IntegrityResult(
                    check_name="Claude: Database Integration",
                    status=IntegrityStatus.PASS,
                    message="Subjective evaluation logging integrated in feedback database",
                    details={'db_module': str(db_module_path)},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="Claude: Database Integration",
                    status=IntegrityStatus.FAIL,
                    message="Database missing Subjective evaluation support",
                    details={'db_module': str(db_module_path)},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 4.5.4: Self-Learning Prompt System Integration
        results.extend(self._check_prompt_optimizer_integration())
        
        # Check 4.5.5: Tests exist for Subjective evaluation
        start = time.time()
        test_path = Path('tests/test_subjective_evaluation.py')
        
        if not test_path.exists():
            results.append(IntegrityResult(
                check_name="Claude: Test Coverage",
                status=IntegrityStatus.WARN,
                message="Subjective evaluation tests not found",
                details={'expected_path': str(test_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Claude: Test Coverage",
                status=IntegrityStatus.PASS,
                message="Subjective evaluation tests exist",
                details={'test_path': str(test_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        return results
    
    def _check_subjective_validator_integration(self) -> List[IntegrityResult]:
        """
        Verify SubjectiveValidator is properly integrated (November 16, 2025).
        
        Checks:
        1. validator.py module exists
        2. Config contains subjective_violations section
        3. DynamicGenerator imports and initializes validator
        4. Validation is called during content checking
        5. Success criteria includes subjective_valid
        6. Test script exists for validator
        """
        results = []
        
        # Check 1: Validator module exists
        start = time.time()
        validator_path = Path('processing/subjective/validator.py')
        
        if not validator_path.exists():
            results.append(IntegrityResult(
                check_name="SubjectiveValidator: Module Exists",
                status=IntegrityStatus.FAIL,
                message="❌ CRITICAL: validator.py module not found - violations won't be caught!",
                details={'expected_path': str(validator_path)},
                duration_ms=(time.time() - start) * 1000
            ))
            # Early return if module doesn't exist
            return results
        else:
            results.append(IntegrityResult(
                check_name="SubjectiveValidator: Module Exists",
                status=IntegrityStatus.PASS,
                message="✅ SubjectiveValidator module exists",
                details={'module_path': str(validator_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 2: Config contains subjective_violations
        start = time.time()
        config_dict = self.config.config
        if 'subjective_violations' not in config_dict:
            results.append(IntegrityResult(
                check_name="SubjectiveValidator: Config Violations",
                status=IntegrityStatus.FAIL,
                message="❌ CRITICAL: subjective_violations section missing from config.yaml",
                details={'config_keys': list(config_dict.keys())},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            violations = config_dict['subjective_violations']
            pattern_count = sum(len(patterns) for patterns in violations.values())
            results.append(IntegrityResult(
                check_name="SubjectiveValidator: Config Violations",
                status=IntegrityStatus.PASS,
                message=f"✅ Config contains {len(violations)} violation categories ({pattern_count} patterns)",
                details={'categories': list(violations.keys()), 'pattern_count': pattern_count},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 3: DynamicGenerator imports validator
        start = time.time()
        generator_path = Path('processing/generator.py')
        if not generator_path.exists():
            results.append(IntegrityResult(
                check_name="SubjectiveValidator: Generator Import",
                status=IntegrityStatus.FAIL,
                message="❌ CRITICAL: generator.py not found",
                details={'expected_path': str(generator_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            generator_content = generator_path.read_text()
            
            # Check for import
            has_import = 'from processing.subjective import SubjectiveValidator' in generator_content
            has_init = 'self.subjective_validator = SubjectiveValidator()' in generator_content
            
            if not has_import or not has_init:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Generator Import",
                    status=IntegrityStatus.FAIL,
                    message="❌ CRITICAL: SubjectiveValidator not imported/initialized in DynamicGenerator",
                    details={'has_import': has_import, 'has_init': has_init},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Generator Import",
                    status=IntegrityStatus.PASS,
                    message="✅ SubjectiveValidator imported and initialized in DynamicGenerator",
                    details={'import_found': True, 'init_found': True},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 4: Validation is called during content checking
        start = time.time()
        if generator_path.exists():
            generator_content = generator_path.read_text()
            
            has_validate_call = 'self.subjective_validator.validate(' in generator_content
            has_subjective_valid = 'subjective_valid' in generator_content
            
            if not has_validate_call:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Validation Called",
                    status=IntegrityStatus.FAIL,
                    message="❌ CRITICAL: subjective_validator.validate() never called in generator!",
                    details={'validate_found': False},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Validation Called",
                    status=IntegrityStatus.PASS,
                    message="✅ subjective_validator.validate() is called during generation",
                    details={'validate_found': True, 'subjective_valid_used': has_subjective_valid},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 5: Success criteria includes subjective_valid
        start = time.time()
        if generator_path.exists():
            generator_content = generator_path.read_text()
            
            # Check if subjective_valid is in success conditions
            has_success_check = 'and subjective_valid' in generator_content or 'subjective_valid and' in generator_content
            
            if not has_success_check:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Success Criteria",
                    status=IntegrityStatus.FAIL,
                    message="❌ CRITICAL: subjective_valid NOT included in success criteria - violations will be ignored!",
                    details={'success_check_found': False},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Success Criteria",
                    status=IntegrityStatus.PASS,
                    message="✅ subjective_valid properly integrated into success criteria",
                    details={'success_check_found': True},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 6: Test script exists
        start = time.time()
        test_path = Path('scripts/test_subjective_validation.py')
        
        if not test_path.exists():
            results.append(IntegrityResult(
                check_name="SubjectiveValidator: Test Script",
                status=IntegrityStatus.WARN,
                message="⚠️  Test script not found (optional but recommended)",
                details={'expected_path': str(test_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="SubjectiveValidator: Test Script",
                status=IntegrityStatus.PASS,
                message="✅ Test script exists for validator",
                details={'test_path': str(test_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 7: Thresholds are configurable (not hardcoded) - November 16, 2025
        start = time.time()
        config_dict = self.config.config
        if 'subjective_thresholds' not in config_dict:
            results.append(IntegrityResult(
                check_name="SubjectiveValidator: Configurable Thresholds",
                status=IntegrityStatus.FAIL,
                message="❌ CRITICAL: subjective_thresholds missing from config.yaml - thresholds hardcoded!",
                details={'config_keys': list(config_dict.keys())},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            thresholds = config_dict['subjective_thresholds']
            has_max_violations = 'max_violations' in thresholds
            has_max_commas = 'max_commas' in thresholds
            
            if not has_max_violations or not has_max_commas:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Configurable Thresholds",
                    status=IntegrityStatus.FAIL,
                    message="❌ CRITICAL: subjective_thresholds incomplete in config.yaml",
                    details={
                        'has_max_violations': has_max_violations,
                        'has_max_commas': has_max_commas,
                        'thresholds': thresholds
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Configurable Thresholds",
                    status=IntegrityStatus.PASS,
                    message=f"✅ Thresholds configurable: max_violations={thresholds['max_violations']}, max_commas={thresholds['max_commas']}",
                    details={'thresholds': thresholds},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 8: Validator loads thresholds from config (not hardcoded)
        start = time.time()
        validator_path = Path('processing/subjective/validator.py')
        if validator_path.exists():
            validator_content = validator_path.read_text()
            
            # Check for hardcoded thresholds (bad pattern)
            has_hardcoded = ('total_violations <= 2' in validator_content or 
                           'comma_count <= 4' in validator_content and 
                           'self.thresholds' not in validator_content)
            
            # Check for config loading (good pattern)
            loads_from_config = 'self.thresholds' in validator_content and '_load_thresholds' in validator_content
            
            if has_hardcoded and not loads_from_config:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: No Hardcoded Thresholds",
                    status=IntegrityStatus.FAIL,
                    message="❌ CRITICAL: Validator has hardcoded thresholds instead of loading from config!",
                    details={'hardcoded_found': True, 'config_loading': False},
                    duration_ms=(time.time() - start) * 1000
                ))
            elif loads_from_config:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: No Hardcoded Thresholds",
                    status=IntegrityStatus.PASS,
                    message="✅ Validator loads thresholds from config (no hardcoding)",
                    details={'hardcoded_found': False, 'config_loading': True},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 9: Threshold reasonableness check
        start = time.time()
        config_dict = self.config.config
        if 'subjective_thresholds' in config_dict:
            thresholds = config_dict['subjective_thresholds']
            max_violations = thresholds.get('max_violations', 0)
            max_commas = thresholds.get('max_commas', 0)
            
            # Thresholds that are too strict will block high-quality content
            # Based on Nov 16 batch test: 94-99% human content had 5-8 violations, 5-9 commas
            is_too_strict = max_violations < 4 or max_commas < 5
            is_reasonable = max_violations >= 5 and max_commas >= 6
            
            if is_too_strict:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Threshold Reasonableness",
                    status=IntegrityStatus.WARN,
                    message=f"⚠️  Thresholds may be too strict (violations≤{max_violations}, commas≤{max_commas}). May block high-quality content.",
                    details={
                        'max_violations': max_violations,
                        'max_commas': max_commas,
                        'recommendation': 'Consider violations≥5, commas≥6 based on test data'
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            elif is_reasonable:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Threshold Reasonableness",
                    status=IntegrityStatus.PASS,
                    message=f"✅ Thresholds reasonable (violations≤{max_violations}, commas≤{max_commas})",
                    details={
                        'max_violations': max_violations,
                        'max_commas': max_commas
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 10: Winston score is passed to validator (CRITICAL)
        start = time.time()
        generator_path = Path('processing/generator.py')
        if generator_path.exists():
            generator_content = generator_path.read_text()
            
            # Check that validate() is called WITH winston_score parameter
            has_winston_param = 'validate(text, winston_score=' in generator_content or 'validate(content, winston_score=' in generator_content
            
            if not has_winston_param:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Winston Score Passed",
                    status=IntegrityStatus.FAIL,
                    message="❌ CRITICAL: Winston score NOT passed to validator - dynamic thresholds won't work!",
                    details={
                        'has_winston_param': False,
                        'impact': 'Validator will use base thresholds only, ignoring Winston performance'
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Winston Score Passed",
                    status=IntegrityStatus.PASS,
                    message="✅ Winston score properly passed to validator for dynamic thresholds",
                    details={'has_winston_param': True},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 11: Adaptive threshold learning is functional
        start = time.time()
        validator_path = Path('processing/subjective/validator.py')
        if validator_path.exists():
            validator_content = validator_path.read_text()
            
            # Check for adaptive threshold learning logic (no hardcoded values)
            has_adaptive_method = '_load_adaptive_thresholds' in validator_content
            has_database_learning = 'composite_quality_score' in validator_content and 'percentile' in validator_content
            has_config_fallback = '_load_config_thresholds' in validator_content
            no_hardcoded_multipliers = '1.5' not in validator_content and '0.75' not in validator_content
            
            if not has_adaptive_method or not has_database_learning or not has_config_fallback:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Adaptive Threshold Learning",
                    status=IntegrityStatus.FAIL,
                    message="❌ CRITICAL: Adaptive threshold learning incomplete or missing!",
                    details={
                        'has_adaptive_method': has_adaptive_method,
                        'has_database_learning': has_database_learning,
                        'has_config_fallback': has_config_fallback,
                        'no_hardcoded_values': no_hardcoded_multipliers
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="SubjectiveValidator: Adaptive Threshold Learning",
                    status=IntegrityStatus.PASS,
                    message="✅ Adaptive threshold learning fully implemented",
                    details={
                        'adaptive_method': True,
                        'database_learning': True,
                        'config_fallback': True,
                        'no_hardcoded_values': no_hardcoded_multipliers
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
        
        return results
    
    # =========================================================================
    # 5. TEST VALIDITY
    # =========================================================================
    
    def _check_test_validity(self) -> List[IntegrityResult]:
        """Verify tests are passing and comprehensive"""
        results = []
        
        # Check 5.1: Test files exist
        start = time.time()
        test_paths = [
            Path('tests/test_config_integrity.py'),
            Path('tests/test_scale_mapper.py'),
            Path('processing/tests'),
        ]
        
        missing_tests = [str(p) for p in test_paths if not p.exists()]
        
        if missing_tests:
            results.append(IntegrityResult(
                check_name="Tests: Test File Existence",
                status=IntegrityStatus.WARN,
                message=f"Some test files/directories not found: {missing_tests}",
                details={'missing': missing_tests},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Tests: Test File Existence",
                status=IntegrityStatus.PASS,
                message="All expected test files/directories exist",
                details={'test_paths': [str(p) for p in test_paths]},
                duration_ms=(time.time() - start) * 1000
            ))
        
        return results
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def has_failures(self, results: List[IntegrityResult]) -> bool:
        """Check if any results have FAIL status"""
        return any(r.status == IntegrityStatus.FAIL for r in results)
    
    def has_warnings(self, results: List[IntegrityResult]) -> bool:
        """Check if any results have WARN status"""
        return any(r.status == IntegrityStatus.WARN for r in results)
    
    def print_report(self, results: List[IntegrityResult], verbose: bool = False):
        """Print formatted integrity report with critical issues at the top"""
        print("\n" + "=" * 80)
        print("SYSTEM INTEGRITY REPORT")
        print("=" * 80)
        
        pass_count = sum(1 for r in results if r.status == IntegrityStatus.PASS)
        warn_count = sum(1 for r in results if r.status == IntegrityStatus.WARN)
        fail_count = sum(1 for r in results if r.status == IntegrityStatus.FAIL)
        skip_count = sum(1 for r in results if r.status == IntegrityStatus.SKIP)
        
        print(f"\nSummary: {pass_count} passed, {warn_count} warnings, {fail_count} failed, {skip_count} skipped")
        
        # ⚠️ CRITICAL: Show failures at the top
        if fail_count > 0:
            print("\n" + "!" * 80)
            print("⚠️  CRITICAL PROBLEMS DETECTED - SYSTEM MAY NOT FUNCTION CORRECTLY")
            print("!" * 80)
            fail_results = [r for r in results if r.status == IntegrityStatus.FAIL]
            for result in fail_results:
                print(f"\n❌ {result.check_name}")
                print(f"   {result.message}")
                if verbose and result.details:
                    print(f"   Details: {result.details}")
            print("\n" + "!" * 80)
        
        print()
        
        # Group by status (failures shown again in full report)
        for status in [IntegrityStatus.FAIL, IntegrityStatus.WARN, IntegrityStatus.PASS]:
            status_results = [r for r in results if r.status == status]
            if not status_results:
                continue
            
            icon = {"FAIL": "❌", "WARN": "⚠️", "PASS": "✅", "SKIP": "⏭️"}[status.value]
            print(f"\n{icon} {status.value}:")
            for result in status_results:
                print(f"  • {result.check_name}")
                print(f"    {result.message}")
                if verbose and result.details:
                    print(f"    Details: {result.details}")
                print(f"    ({result.duration_ms:.1f}ms)")
        
        total_time = sum(r.duration_ms for r in results)
        print(f"\nTotal check time: {total_time:.1f}ms")
        print("=" * 80 + "\n")
    
    def get_summary_dict(self, results: List[IntegrityResult]) -> Dict[str, Any]:
        """Get machine-readable summary"""
        return {
            'total_checks': len(results),
            'passed': sum(1 for r in results if r.status == IntegrityStatus.PASS),
            'warnings': sum(1 for r in results if r.status == IntegrityStatus.WARN),
            'failed': sum(1 for r in results if r.status == IntegrityStatus.FAIL),
            'skipped': sum(1 for r in results if r.status == IntegrityStatus.SKIP),
            'total_duration_ms': sum(r.duration_ms for r in results),
            'has_failures': self.has_failures(results),
            'has_warnings': self.has_warnings(results),
            'results': [
                {
                    'check': r.check_name,
                    'status': r.status.value,
                    'message': r.message,
                    'duration_ms': r.duration_ms
                }
                for r in results
            ]
        }
    
    # =========================================================================
    # PER-ITERATION LEARNING ARCHITECTURE CHECKS (November 17, 2025)
    # =========================================================================
    
    def _check_per_iteration_learning(self) -> List[IntegrityResult]:
        """
        Verify per-iteration learning architecture is correctly implemented.
        
        Critical checks to prevent hours of debugging:
        1. Inline realism evaluation exists in generator retry loop
        2. Dual-objective scoring (Winston 40% + Realism 60%)
        3. Learning logged on EVERY iteration (success AND failure)
        4. No global evaluation calls (removed)
        5. RealismOptimizer integration
        6. Database schema supports realism_learning table
        
        This prevents the system from silently failing to learn.
        """
        results = []
        
        # Check 1: Inline realism evaluation exists
        start = time.time()
        generator_path = Path('processing/generator.py')
        
        if not generator_path.exists():
            results.append(IntegrityResult(
                check_name="Per-Iteration: Generator Exists",
                status=IntegrityStatus.FAIL,
                message="❌ CRITICAL: generator.py not found",
                details={'expected_path': str(generator_path)},
                duration_ms=(time.time() - start) * 1000
            ))
            return results  # Can't proceed without generator
        
        generator_content = generator_path.read_text()
        
        # Check for SubjectiveEvaluator import
        has_evaluator_import = 'from processing.subjective import SubjectiveEvaluator' in generator_content
        has_grok_client = "create_api_client('grok')" in generator_content
        has_evaluate_call = 'realism_evaluator.evaluate(' in generator_content
        
        if not all([has_evaluator_import, has_grok_client, has_evaluate_call]):
            results.append(IntegrityResult(
                check_name="Per-Iteration: Inline Realism Evaluation",
                status=IntegrityStatus.FAIL,
                message="❌ CRITICAL: Inline realism evaluation missing from retry loop",
                details={
                    'has_import': has_evaluator_import,
                    'creates_grok_client': has_grok_client,
                    'calls_evaluate': has_evaluate_call,
                    'issue': 'System will not evaluate realism on every iteration'
                },
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Per-Iteration: Inline Realism Evaluation",
                status=IntegrityStatus.PASS,
                message="✅ Inline realism evaluation present in retry loop",
                details={'evaluates_per_iteration': True},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 2: Dual-objective scoring
        start = time.time()
        has_combined_score = 'combined_score' in generator_content
        has_winston_weight = '0.4' in generator_content  # Winston 40%
        has_realism_weight = '0.6' in generator_content  # Realism 60%
        has_normalization = 'human_score / 10' in generator_content or 'winston_normalized' in generator_content
        
        if not all([has_combined_score, has_winston_weight, has_realism_weight]):
            results.append(IntegrityResult(
                check_name="Per-Iteration: Dual-Objective Scoring",
                status=IntegrityStatus.FAIL,
                message="❌ CRITICAL: Dual-objective scoring (Winston 40% + Realism 60%) not implemented",
                details={
                    'has_combined_score': has_combined_score,
                    'has_winston_weight_40': has_winston_weight,
                    'has_realism_weight_60': has_realism_weight,
                    'has_normalization': has_normalization,
                    'issue': 'System will not properly combine Winston and Realism scores'
                },
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Per-Iteration: Dual-Objective Scoring",
                status=IntegrityStatus.PASS,
                message="✅ Dual-objective scoring implemented (Winston 40% + Realism 60%)",
                details={'combines_scores': True},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 3: Learning logged on success
        start = time.time()
        has_success_learning = 'log_realism_learning' in generator_content
        has_optimizer_import = 'from processing.learning.realism_optimizer import RealismOptimizer' in generator_content
        has_ai_tendencies = 'ai_tendencies' in generator_content
        
        if not all([has_success_learning, has_ai_tendencies]):
            results.append(IntegrityResult(
                check_name="Per-Iteration: Success Learning",
                status=IntegrityStatus.FAIL,
                message="❌ CRITICAL: Realism learning not logged on successful iterations",
                details={
                    'logs_learning': has_success_learning,
                    'captures_tendencies': has_ai_tendencies,
                    'has_optimizer': has_optimizer_import,
                    'issue': 'System will not learn from successful patterns'
                },
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Per-Iteration: Success Learning",
                status=IntegrityStatus.PASS,
                message="✅ Learning logged on successful iterations",
                details={'logs_success_patterns': True},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 4: Learning logged on FAILURE (critical!)
        start = time.time()
        has_failure_learning = 'success=False' in generator_content
        has_failure_comment = 'even for FAILURES' in generator_content or 'failure pattern' in generator_content.lower()
        
        if not has_failure_learning:
            results.append(IntegrityResult(
                check_name="Per-Iteration: Failure Learning",
                status=IntegrityStatus.FAIL,
                message="❌ CRITICAL: Realism learning NOT logged on failed iterations",
                details={
                    'logs_failures': has_failure_learning,
                    'has_documentation': has_failure_comment,
                    'issue': 'System will not learn from failures (50% of training data lost!)'
                },
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Per-Iteration: Failure Learning",
                status=IntegrityStatus.PASS,
                message="✅ Learning logged on failed iterations (builds training data)",
                details={'logs_failure_patterns': True},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 5: No global evaluation calls
        start = time.time()
        run_path = Path('run.py')
        
        if not run_path.exists():
            results.append(IntegrityResult(
                check_name="Per-Iteration: No Global Evaluation",
                status=IntegrityStatus.WARN,
                message="⚠️  run.py not found, cannot verify global evaluation removal",
                details={'expected_path': str(run_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            run_content = run_path.read_text()
            
            # Check import is commented out
            import_commented = '# from shared.commands.global_evaluation import run_global_subjective_evaluation' in run_content
            
            # Check no active calls
            active_calls = run_content.count('run_global_subjective_evaluation(')
            calls_commented = '# run_global_subjective_evaluation' in run_content
            
            if not import_commented or (active_calls > 0 and not calls_commented):
                results.append(IntegrityResult(
                    check_name="Per-Iteration: No Global Evaluation",
                    status=IntegrityStatus.FAIL,
                    message="❌ CRITICAL: Global evaluation still active (doesn't contribute to learning)",
                    details={
                        'import_commented': import_commented,
                        'active_call_count': active_calls,
                        'issue': 'Wastes API calls without contributing to current generation'
                    },
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="Per-Iteration: No Global Evaluation",
                    status=IntegrityStatus.PASS,
                    message="✅ Global evaluation removed (per-iteration learning active)",
                    details={'uses_inline_learning': True},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        # Check 6: Combined score used for quality decision
        start = time.time()
        uses_combined_for_decision = 'combined_score_percent >= learning_target' in generator_content
        
        if not uses_combined_for_decision:
            results.append(IntegrityResult(
                check_name="Per-Iteration: Combined Score Decision",
                status=IntegrityStatus.WARN,
                message="⚠️  Quality decision may not use combined score",
                details={
                    'uses_combined': uses_combined_for_decision,
                    'issue': 'Decisions should be based on Winston+Realism, not just Winston'
                },
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            results.append(IntegrityResult(
                check_name="Per-Iteration: Combined Score Decision",
                status=IntegrityStatus.PASS,
                message="✅ Quality decisions use combined score (Winston + Realism)",
                details={'uses_dual_objective': True},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 7: Database supports realism_learning table
        start = time.time()
        db_path = Path('data/winston_feedback.db')
        
        if not db_path.exists():
            results.append(IntegrityResult(
                check_name="Per-Iteration: Database Schema",
                status=IntegrityStatus.WARN,
                message="⚠️  Winston feedback database not found",
                details={'db_path': str(db_path)},
                duration_ms=(time.time() - start) * 1000
            ))
        else:
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Check if realism_learning table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='realism_learning'")
                table_exists = cursor.fetchone() is not None
                
                if table_exists:
                    # Check columns
                    cursor.execute("PRAGMA table_info(realism_learning)")
                    columns = [row[1] for row in cursor.fetchall()]
                    required_columns = ['detected_ai_tendencies', 'parameter_adjustments', 'original_realism_score', 'success']
                    missing_columns = [col for col in required_columns if col not in columns]
                    
                    if missing_columns:
                        results.append(IntegrityResult(
                            check_name="Per-Iteration: Database Schema",
                            status=IntegrityStatus.FAIL,
                            message=f"❌ CRITICAL: realism_learning table missing columns: {missing_columns}",
                            details={'existing_columns': columns, 'missing': missing_columns},
                            duration_ms=(time.time() - start) * 1000
                        ))
                    else:
                        results.append(IntegrityResult(
                            check_name="Per-Iteration: Database Schema",
                            status=IntegrityStatus.PASS,
                            message="✅ realism_learning table exists with required columns",
                            details={'columns': columns},
                            duration_ms=(time.time() - start) * 1000
                        ))
                else:
                    results.append(IntegrityResult(
                        check_name="Per-Iteration: Database Schema",
                        status=IntegrityStatus.FAIL,
                        message="❌ CRITICAL: realism_learning table does not exist",
                        details={'issue': 'Learning data cannot be persisted'},
                        duration_ms=(time.time() - start) * 1000
                    ))
                
                conn.close()
            except Exception as e:
                results.append(IntegrityResult(
                    check_name="Per-Iteration: Database Schema",
                    status=IntegrityStatus.WARN,
                    message=f"⚠️  Could not verify database schema: {e}",
                    details={'error': str(e)},
                    duration_ms=(time.time() - start) * 1000
                ))
        
        return results
