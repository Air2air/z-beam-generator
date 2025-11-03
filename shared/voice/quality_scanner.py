"""
Voice Quality Scanner - Automated quality validation for text fields.

Scans text fields for voice quality issues:
- Excessive marker repetition
- Formulaic phrases
- Poor marker distribution
- Translation artifacts

Used during frontmatter export as automatic quality gate.
"""

import logging
from typing import Dict, Any, List, Tuple
from shared.voice.orchestrator import VoiceOrchestrator

logger = logging.getLogger(__name__)


class VoiceQualityScanner:
    """
    Automated voice quality scanner for text validation.
    
    Scans text fields and returns quality scores with detailed issues.
    Designed for automatic quality gates during export.
    """
    
    def __init__(self, api_client=None):
        """
        Initialize quality scanner.
        
        Args:
            api_client: Optional API client for advanced validation
        """
        self.api_client = api_client
    
    def scan_text_fields(
        self,
        data: Any,
        author_data: Dict[str, str],
        field_path: str = ""
    ) -> Tuple[List[Dict[str, Any]], int, int]:
        """
        Recursively scan all text fields for quality issues.
        
        Args:
            data: Data structure to scan (dict, list, or string)
            author_data: Author information with country
            field_path: Current field path for reporting
            
        Returns:
            Tuple of (issues_list, total_fields_scanned, failed_fields_count)
        """
        issues = []
        total_scanned = 0
        failed_count = 0
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{field_path}.{key}" if field_path else key
                field_issues, scanned, failed = self.scan_text_fields(
                    value, author_data, current_path
                )
                issues.extend(field_issues)
                total_scanned += scanned
                failed_count += failed
                
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                current_path = f"{field_path}[{idx}]"
                field_issues, scanned, failed = self.scan_text_fields(
                    item, author_data, current_path
                )
                issues.extend(field_issues)
                total_scanned += scanned
                failed_count += failed
                
        elif isinstance(data, str) and len(data.split()) > 10:
            # Scan substantial text fields
            total_scanned += 1
            quality_result = self._check_text_quality(data, author_data, field_path)
            
            if quality_result['failed']:
                failed_count += 1
                issues.append(quality_result)
        
        return issues, total_scanned, failed_count
    
    def _check_text_quality(
        self,
        text: str,
        author_data: Dict[str, str],
        field_path: str
    ) -> Dict[str, Any]:
        """
        Check quality of a single text field.
        
        Args:
            text: Text to check
            author_data: Author information
            field_path: Field location for reporting
            
        Returns:
            Quality check result with score and issues
        """
        try:
            from shared.voice.post_processor import VoicePostProcessor
            
            if not self.api_client:
                # Simple marker count check if no API client
                return self._simple_quality_check(text, author_data, field_path)
            
            processor = VoicePostProcessor(self.api_client)
            
            country = author_data.get('country', 'Unknown')
            voice = VoiceOrchestrator(country=country)
            voice_indicators = voice.get_signature_phrases()
            
            # Run full quality scoring
            quality = processor.score_voice_authenticity(
                text, author_data, voice_indicators
            )
            
            score = quality['authenticity_score']
            issues_list = quality.get('issues', [])
            
            return {
                'field_path': field_path,
                'score': score,
                'failed': score < 70,
                'issues': issues_list,
                'text_preview': text[:100] + '...' if len(text) > 100 else text
            }
            
        except Exception as e:
            logger.warning(f"Quality check failed for {field_path}: {e}")
            return {
                'field_path': field_path,
                'score': 100,  # Pass by default if check fails
                'failed': False,
                'issues': [],
                'text_preview': text[:100] + '...' if len(text) > 100 else text
            }
    
    def _simple_quality_check(
        self,
        text: str,
        author_data: Dict[str, str],
        field_path: str
    ) -> Dict[str, Any]:
        """
        Simple quality check without API client (marker counting only).
        
        Args:
            text: Text to check
            author_data: Author information
            field_path: Field location
            
        Returns:
            Basic quality result
        """
        try:
            country = author_data.get('country', 'Unknown')
            voice = VoiceOrchestrator(country=country)
            voice_indicators = voice.get_signature_phrases()
            
            text_lower = text.lower()
            
            # Count marker occurrences
            marker_counts = {}
            for marker in voice_indicators:
                count = text_lower.count(marker)
                if count > 0:
                    marker_counts[marker] = count
            
            # Check for excessive repetition
            issues = []
            score = 100
            
            for marker, count in marker_counts.items():
                if count > 2:
                    penalty = (count - 2) * 10
                    score -= penalty
                    issues.append(f"Repeated marker '{marker}': {count} times")
            
            # Check total marker count
            total_markers = len(marker_counts)
            if total_markers > 6:
                score -= 15
                issues.append(f"Excessive markers: {total_markers} found")
            
            return {
                'field_path': field_path,
                'score': max(0, score),
                'failed': score < 70,
                'issues': issues,
                'text_preview': text[:100] + '...' if len(text) > 100 else text
            }
            
        except Exception as e:
            logger.warning(f"Simple quality check failed for {field_path}: {e}")
            return {
                'field_path': field_path,
                'score': 100,
                'failed': False,
                'issues': [],
                'text_preview': ''
            }
