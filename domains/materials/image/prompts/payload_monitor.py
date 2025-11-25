#!/usr/bin/env python3
"""
JSON Payload Conformity Monitor

Tracks JSON payloads throughout the pipeline, detects patterns in failures,
and dynamically adjusts prompt guidance to improve conformity.

Author: AI Assistant
Date: November 25, 2025
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict, deque
import re

logger = logging.getLogger(__name__)


class PayloadMonitor:
    """Monitor JSON payload conformity and adapt prompts dynamically"""
    
    def __init__(self, max_history: int = 100):
        """
        Initialize payload monitor with failure tracking.
        
        Args:
            max_history: Maximum number of failures to track
        """
        self.max_history = max_history
        
        # Track failure patterns
        self.failure_history = deque(maxlen=max_history)
        self.failure_patterns = defaultdict(int)
        
        # Track success metrics
        self.total_attempts = 0
        self.successful_parses = 0
        
        # Cache directory for persistent tracking
        self.cache_dir = "domains/cache/payload_monitoring"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load historical data
        self._load_history()
    
    def validate_schema(self, data: Dict, category: str) -> Tuple[bool, List[str]]:
        """
        Validate JSON payload against expected schema.
        
        Args:
            data: Parsed JSON data
            category: Material category
            
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []
        
        # Required top-level fields
        required_fields = ['contamination_patterns', 'base_appearance']
        for field in required_fields:
            if field not in data:
                violations.append(f"Missing required field: {field}")
        
        # Validate contamination_patterns structure
        if 'contamination_patterns' in data:
            patterns = data['contamination_patterns']
            if not isinstance(patterns, list):
                violations.append("contamination_patterns must be a list")
            else:
                for i, pattern in enumerate(patterns):
                    # Required pattern fields
                    pattern_required = [
                        'pattern_name',
                        'photo_reference_urls',
                        'photo_reference_description',
                        'visual_characteristics',
                        'distribution_physics'
                    ]
                    for field in pattern_required:
                        if field not in pattern:
                            violations.append(f"Pattern {i}: Missing field '{field}'")
                    
                    # Validate photo_reference_urls
                    if 'photo_reference_urls' in pattern:
                        urls = pattern['photo_reference_urls']
                        if not isinstance(urls, list):
                            violations.append(f"Pattern {i}: photo_reference_urls must be a list")
                        elif len(urls) < 2:
                            violations.append(f"Pattern {i}: Need at least 2 photo reference URLs")
                        elif len(urls) > 4:
                            violations.append(f"Pattern {i}: Maximum 4 photo reference URLs")
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    def record_parse_attempt(
        self,
        category: str,
        attempt_num: int,
        success: bool,
        error: Optional[Exception] = None,
        raw_json: Optional[str] = None,
        cleaning_strategy: Optional[int] = None
    ):
        """
        Record a JSON parse attempt with detailed context.
        
        Args:
            category: Material category
            attempt_num: Attempt number (1-3)
            success: Whether parsing succeeded
            error: Parse exception if failed
            raw_json: Raw JSON text (saved on failure)
            cleaning_strategy: Which cleaning strategy was used (0-2)
        """
        self.total_attempts += 1
        
        if success:
            self.successful_parses += 1
            return
        
        # Analyze failure
        failure_record = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'attempt': attempt_num,
            'strategy': cleaning_strategy,
            'error_type': type(error).__name__ if error else 'Unknown',
            'error_msg': str(error) if error else 'Unknown',
        }
        
        # Extract specific failure patterns
        if error and hasattr(error, 'msg'):
            failure_record['json_error'] = error.msg
            
            # Categorize common errors
            if 'Unterminated string' in error.msg:
                self.failure_patterns['unterminated_string'] += 1
                failure_record['pattern'] = 'unterminated_string'
            elif 'Expecting value' in error.msg:
                self.failure_patterns['missing_value'] += 1
                failure_record['pattern'] = 'missing_value'
            elif 'Expecting property name' in error.msg:
                self.failure_patterns['invalid_property_name'] += 1
                failure_record['pattern'] = 'invalid_property_name'
            elif 'Extra data' in error.msg:
                self.failure_patterns['extra_data'] += 1
                failure_record['pattern'] = 'extra_data'
            else:
                self.failure_patterns['other'] += 1
                failure_record['pattern'] = 'other'
        
        # Save raw JSON for analysis
        if raw_json and attempt_num == 3:  # Save on final failure
            failure_file = os.path.join(
                self.cache_dir,
                f"failed_{category}_{int(time.time())}.json"
            )
            try:
                with open(failure_file, 'w') as f:
                    f.write(raw_json)
                failure_record['saved_to'] = failure_file
            except Exception as e:
                logger.error(f"Failed to save failure JSON: {e}")
        
        self.failure_history.append(failure_record)
        self._save_history()
    
    def get_adaptive_prompt_guidance(self, category: str) -> str:
        """
        Generate adaptive prompt guidance based on recent failure patterns.
        
        Args:
            category: Material category
            
        Returns:
            Additional prompt text with specific JSON formatting guidance
        """
        if self.total_attempts == 0:
            return ""
        
        # Calculate failure rate
        failure_rate = 1.0 - (self.successful_parses / self.total_attempts)
        
        if failure_rate < 0.1:
            # Low failure rate - minimal guidance
            return ""
        
        guidance_parts = [
            "\n⚠️ CRITICAL JSON FORMATTING (Recent issues detected):\n"
        ]
        
        # Add specific guidance based on top failure patterns
        top_patterns = sorted(
            self.failure_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        for pattern, count in top_patterns:
            if count == 0:
                continue
                
            if pattern == 'unterminated_string':
                guidance_parts.append(
                    f"• UNTERMINATED STRING ERRORS ({count} recent): "
                    "Escape ALL quotes inside strings with \\\" "
                    "Example: \"description\": \"Shows \\\"aged\\\" surface\"\n"
                )
            elif pattern == 'missing_value':
                guidance_parts.append(
                    f"• MISSING VALUE ERRORS ({count} recent): "
                    "Ensure all keys have values. Use empty string \"\" or [] if needed.\n"
                )
            elif pattern == 'invalid_property_name':
                guidance_parts.append(
                    f"• INVALID PROPERTY ERRORS ({count} recent): "
                    "Property names must be in quotes: \"property_name\": value\n"
                )
            elif pattern == 'extra_data':
                guidance_parts.append(
                    f"• EXTRA DATA ERRORS ({count} recent): "
                    "Remove trailing commas. No comma after last item in array/object.\n"
                )
        
        # Add strategy recommendation
        if failure_rate > 0.5:
            guidance_parts.append(
                "\n🔧 SIMPLIFICATION REQUIRED:\n"
                "• Keep URLs simple (no embedded quotes in descriptions)\n"
                "• Use short, simple strings for all text fields\n"
                "• Avoid complex nested structures\n"
            )
        
        return "".join(guidance_parts)
    
    def get_monitoring_report(self) -> str:
        """
        Generate comprehensive monitoring report.
        
        Returns:
            Formatted report string
        """
        if self.total_attempts == 0:
            return "No payload monitoring data yet."
        
        success_rate = (self.successful_parses / self.total_attempts) * 100
        
        report = [
            "\n" + "="*80,
            "📊 JSON PAYLOAD CONFORMITY REPORT",
            "="*80,
            f"\n📈 Success Rate: {success_rate:.1f}% ({self.successful_parses}/{self.total_attempts})",
            f"\n🔍 Recent Failures: {len(self.failure_history)}",
        ]
        
        if self.failure_patterns:
            report.append("\n\n📉 Failure Patterns:")
            for pattern, count in sorted(
                self.failure_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                percentage = (count / (self.total_attempts - self.successful_parses)) * 100 if (self.total_attempts - self.successful_parses) > 0 else 0
                report.append(f"   • {pattern}: {count} ({percentage:.1f}%)")
        
        if self.failure_history:
            report.append("\n\n🕐 Recent Failures:")
            for failure in list(self.failure_history)[-5:]:  # Last 5
                report.append(
                    f"   • {failure['category']} (attempt {failure['attempt']}): "
                    f"{failure.get('pattern', 'unknown')} - {failure.get('json_error', 'N/A')}"
                )
        
        report.append("\n" + "="*80 + "\n")
        return "\n".join(report)
    
    def _load_history(self):
        """Load failure history from disk."""
        history_file = os.path.join(self.cache_dir, "failure_history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.total_attempts = data.get('total_attempts', 0)
                    self.successful_parses = data.get('successful_parses', 0)
                    self.failure_patterns = defaultdict(int, data.get('failure_patterns', {}))
                    
                    # Load recent history
                    history = data.get('recent_failures', [])
                    self.failure_history = deque(history[-self.max_history:], maxlen=self.max_history)
                    
                logger.info(f"📥 Loaded payload monitoring history: {self.total_attempts} attempts tracked")
            except Exception as e:
                logger.warning(f"Failed to load monitoring history: {e}")
    
    def _save_history(self):
        """Save failure history to disk."""
        history_file = os.path.join(self.cache_dir, "failure_history.json")
        try:
            data = {
                'total_attempts': self.total_attempts,
                'successful_parses': self.successful_parses,
                'failure_patterns': dict(self.failure_patterns),
                'recent_failures': list(self.failure_history),
                'last_updated': datetime.now().isoformat()
            }
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save monitoring history: {e}")


# Global monitor instance
_monitor_instance = None


def get_payload_monitor() -> PayloadMonitor:
    """Get or create global payload monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = PayloadMonitor()
    return _monitor_instance
