#!/usr/bin/env python3
"""
Material Recovery System

Main recovery coordination system that combines validation and recovery functionality.
Provides high-level interfaces for scanning materials and coordinating recovery efforts.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from .validator import ContentValidator, ComponentStatus, ComponentResult

@dataclass 
class MaterialValidationReport:
    subject: str
    total_components: int
    successful_components: int
    failed_components: List[str]
    overall_status: ComponentStatus
    components: Dict[str, ComponentResult]
    recommendations: List[str]

class MaterialRecoverySystem:
    """System for detecting and re-running failed material generation.
    
    The recovery system automatically respects the BATCH_CONFIG enabled settings.
    Only components with 'enabled: True' (or missing enabled key, defaulting to True)
    will be validated and considered for recovery.
    
    This means:
    - Components with 'enabled: False' are completely ignored
    - No validation reports will be generated for disabled components  
    - No recovery suggestions will include disabled components
    - Success rates are calculated based only on enabled components
    """
    
    def __init__(self, content_dir: str = "content/components"):
        self.content_dir = Path(content_dir)
        self.validator = ContentValidator()
        self.logger = logging.getLogger(__name__)
        
        # Load enabled components from BATCH_CONFIG
        self.components = self._get_enabled_components()
    
    def _get_enabled_components(self) -> List[str]:
        """Get list of enabled components from BATCH_CONFIG."""
        try:
            import run
            batch_config = run.BATCH_CONFIG
            components = batch_config.get("components", {})
            
            enabled_components = []
            for comp_name, comp_config in components.items():
                if comp_config.get("enabled", True):  # Default to True if not specified
                    enabled_components.append(comp_name)
            
            self.logger.info(f"Enabled components from BATCH_CONFIG: {enabled_components}")
            return enabled_components
            
        except Exception as e:
            self.logger.warning(f"Could not load BATCH_CONFIG, using default components: {e}")
            # Fallback to original hardcoded list
            return [
                'frontmatter', 'metatags', 'table', 'bullets', 
                'caption', 'propertiestable', 'tags', 'jsonld'
            ]
    
    def scan_materials(self, specific_subjects: List[str] = None) -> Dict[str, MaterialValidationReport]:
        """Scan materials and generate validation reports.
        
        Args:
            specific_subjects: Optional list of specific subjects to validate. 
                             If None, discovers all subjects automatically.
        """
        reports = {}
        
        # Use specific subjects if provided, otherwise discover all
        if specific_subjects:
            subjects = set(specific_subjects)
        else:
            subjects = self._discover_subjects()
        
        for subject in subjects:
            report = self._validate_material(subject)
            reports[subject] = report
            
        return reports
    
    def _discover_subjects(self) -> Set[str]:
        """Discover all subjects that have been generated."""
        subjects = set()
        
        for component_dir in self.content_dir.iterdir():
            if component_dir.is_dir() and component_dir.name in self.components:
                for file_path in component_dir.glob("*-laser-cleaning.md"):
                    subject = file_path.stem.replace('-laser-cleaning', '').replace('-', ' ').title()
                    subjects.add(subject)
        
        return subjects
    
    def _validate_material(self, subject: str) -> MaterialValidationReport:
        """Validate all components for a specific material."""
        subject_slug = subject.lower().replace(' ', '-')
        filename = f"{subject_slug}-laser-cleaning.md"
        
        component_results = {}
        failed_components = []
        successful_count = 0
        
        for component in self.components:
            file_path = self.content_dir / component / filename
            result = self.validator.validate_markdown_file(str(file_path), component)
            component_results[component] = result
            
            if result.status == ComponentStatus.SUCCESS:
                successful_count += 1
            else:
                failed_components.append(component)
        
        # Determine overall status
        success_rate = successful_count / len(self.components)
        if success_rate >= 0.8:
            overall_status = ComponentStatus.SUCCESS
        elif success_rate >= 0.5:
            overall_status = ComponentStatus.INVALID
        else:
            overall_status = ComponentStatus.FAILED
        
        # Generate recommendations
        recommendations = self._generate_recommendations(component_results, failed_components)
        
        return MaterialValidationReport(
            subject=subject,
            total_components=len(self.components),
            successful_components=successful_count,
            failed_components=failed_components,
            overall_status=overall_status,
            components=component_results,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, components: Dict[str, ComponentResult], 
                                failed_components: List[str]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if not failed_components:
            recommendations.append("✅ All components generated successfully")
            return recommendations
        
        # Categorize failures
        empty_failures = []
        api_failures = []
        content_failures = []
        
        for comp_name in failed_components:
            result = components[comp_name]
            if result.status == ComponentStatus.EMPTY:
                empty_failures.append(comp_name)
            elif result.status == ComponentStatus.MISSING:
                api_failures.append(comp_name)
            else:
                content_failures.append(comp_name)
        
        if empty_failures:
            recommendations.append(f"🔄 Re-run empty components: {', '.join(empty_failures)} (likely API timeouts)")
        
        if api_failures:
            recommendations.append(f"🚨 Missing components need generation: {', '.join(api_failures)}")
        
        if content_failures:
            recommendations.append(f"⚠️ Review content quality: {', '.join(content_failures)}")
        
        # Specific recommendations
        if len(failed_components) >= 3:
            recommendations.append("💡 Consider running components individually to avoid API timeouts")
        
        if 'frontmatter' in failed_components:
            recommendations.append("🔧 Frontmatter failure may indicate API connectivity issues")
            
        return recommendations
    
    def generate_recovery_commands(self, subject: str, failed_components: List[str]) -> List[str]:
        """Generate command-line commands to re-run failed components."""
        commands = []
        
        # Generate direct recovery command
        components_str = ' '.join(failed_components)
        cmd = f'python3 -m recovery.cli recover "{subject}" --components {components_str}'
        commands.append(cmd)
        
        # Also show individual component commands
        for component in failed_components:
            cmd = f'python3 -m recovery.cli recover "{subject}" --components {component}'
            commands.append(cmd)
        
        return commands
    
    def run_recovery(self, subject: str, failed_components: List[str], 
                    timeout: int = 60, retry_count: int = 3) -> Dict[str, bool]:
        """Run recovery for failed components using direct generator calls."""
        try:
            from .recovery_runner import DirectRecoveryRunner
            
            runner = DirectRecoveryRunner()
            results = runner.recover_components(
                subject=subject,
                failed_components=failed_components,
                timeout=timeout,
                retry_count=retry_count
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Recovery failed: {e}")
            return {comp: False for comp in failed_components}

def print_validation_report(report: MaterialValidationReport):
    """Print a formatted validation report."""
    print(f"\\n📊 Validation Report: {report.subject}")
    print("=" * 50)
    print(f"Overall Status: {report.overall_status.value.upper()}")
    print(f"Success Rate: {report.successful_components}/{report.total_components} "
          f"({report.successful_components/report.total_components*100:.1f}%)")
    
    if report.failed_components:
        print(f"\\n❌ Failed Components: {', '.join(report.failed_components)}")
    
    print("\\n📋 Component Details:")
    for comp_name, result in report.components.items():
        status_emoji = "✅" if result.status == ComponentStatus.SUCCESS else "❌"
        print(f"  {status_emoji} {comp_name}: {result.status.value} "
              f"({result.size_bytes} bytes, quality: {result.quality_score:.1f}%)")
        
        if result.issues:
            for issue in result.issues:
                print(f"    ⚠️  {issue}")
    
    print("\\n💡 Recommendations:")
    for rec in report.recommendations:
        print(f"  {rec}")
