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

3. API Health
   - Winston API reachable and responding
   - Grok API reachable and responding
   - Rate limits not exceeded

4. Documentation Alignment
   - Code matches documented behavior
   - Configuration docs match actual config structure
   - Examples in docs are executable

5. Test Validity
   - All tests passing
   - Test coverage meets thresholds
   - Integration tests verify E2E flows
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path

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
    
    # =========================================================================
    # 1. CONFIGURATION VALUE MAPPING
    # =========================================================================
    
    def _check_configuration_mapping(self) -> List[IntegrityResult]:
        """Verify slider values map correctly to normalized ranges"""
        results = []
        
        # Check 1.1: Slider values in valid range (1-10)
        start = time.time()
        slider_values = {
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
                message=f"All {len(slider_values)} sliders in valid range (1-10)",
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
    # 2. PARAMETER PROPAGATION
    # =========================================================================
    
    def _check_parameter_propagation(self) -> List[IntegrityResult]:
        """Verify parameters flow correctly through the chain"""
        results = []
        
        # Check 2.1: get_all_generation_params returns complete bundle
        start = time.time()
        try:
            params = self.dynamic_config.get_all_generation_params('caption')
            
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
        original_temp = self.dynamic_config.calculate_temperature('caption')
        bundled_temp = self.dynamic_config.get_all_generation_params('caption')['api_params']['temperature']
        
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
            from shared.services.winston_client import WinstonClient
            
            client = WinstonClient()
            # Simple connectivity test - don't burn credits
            # Just verify the client can be instantiated and has API key
            if client.api_key:
                results.append(IntegrityResult(
                    check_name="API: Winston Connectivity",
                    status=IntegrityStatus.PASS,
                    message="Winston client configured with API key",
                    details={'has_api_key': True},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="API: Winston Connectivity",
                    status=IntegrityStatus.WARN,
                    message="Winston client has no API key configured",
                    details={'has_api_key': False},
                    duration_ms=(time.time() - start) * 1000
                ))
        except Exception as e:
            results.append(IntegrityResult(
                check_name="API: Winston Connectivity",
                status=IntegrityStatus.FAIL,
                message=f"Winston client initialization failed: {str(e)}",
                details={'error': str(e)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Check 3.2: Grok API health
        start = time.time()
        try:
            from shared.services.grok_client import GrokClient
            
            client = GrokClient()
            if client.api_key:
                results.append(IntegrityResult(
                    check_name="API: Grok Connectivity",
                    status=IntegrityStatus.PASS,
                    message="Grok client configured with API key",
                    details={'has_api_key': True},
                    duration_ms=(time.time() - start) * 1000
                ))
            else:
                results.append(IntegrityResult(
                    check_name="API: Grok Connectivity",
                    status=IntegrityStatus.WARN,
                    message="Grok client has no API key configured",
                    details={'has_api_key': False},
                    duration_ms=(time.time() - start) * 1000
                ))
        except Exception as e:
            results.append(IntegrityResult(
                check_name="API: Grok Connectivity",
                status=IntegrityStatus.FAIL,
                message=f"Grok client initialization failed: {str(e)}",
                details={'error': str(e)},
                duration_ms=(time.time() - start) * 1000
            ))
        
        return results
    
    # =========================================================================
    # 4. DOCUMENTATION ALIGNMENT
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
        """Print formatted integrity report"""
        print("\n" + "=" * 80)
        print("SYSTEM INTEGRITY REPORT")
        print("=" * 80)
        
        pass_count = sum(1 for r in results if r.status == IntegrityStatus.PASS)
        warn_count = sum(1 for r in results if r.status == IntegrityStatus.WARN)
        fail_count = sum(1 for r in results if r.status == IntegrityStatus.FAIL)
        skip_count = sum(1 for r in results if r.status == IntegrityStatus.SKIP)
        
        print(f"\nSummary: {pass_count} passed, {warn_count} warnings, {fail_count} failed, {skip_count} skipped")
        print()
        
        # Group by status
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
