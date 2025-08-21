#!/usr/bin/env python3
"""
Comprehensive Schema-Component Matching Analysis

FEATURES:
1. Parse all frontmatter examples
2. Compare against material schema requirements  
3. Analyze field usage patterns
4. Provide optimization recommendations
5. Generate detailed matching reports
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

from dynamic_schema_generator import DynamicSchemaValidator

# Setup logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise
logger = logging.getLogger(__name__)


@dataclass 
class FieldAnalysis:
    """Analysis of a specific field across examples."""
    field_name: str
    present_in: int
    total_examples: int
    usage_percentage: float
    example_values: List[str]
    field_types: Set[str]
    is_required: bool


@dataclass
class SchemaMatchResult:
    """Complete schema matching analysis."""
    total_examples: int
    valid_examples: int
    schema_compliance: float
    field_analyses: Dict[str, FieldAnalysis]
    optimization_recommendations: List[str]


class SchemaComponentMatcher:
    """Comprehensive schema-component matching analyzer."""
    
    def __init__(self):
        self.validator = DynamicSchemaValidator()
        self.content_dir = Path("content/components/frontmatter")
    
    def parse_all_frontmatter_examples(self) -> List[Tuple[str, Dict]]:
        """Parse all frontmatter examples."""
        examples = []
        
        if not self.content_dir.exists():
            logger.error(f"Content directory not found: {self.content_dir}")
            return examples
        
        for md_file in self.content_dir.glob("*.md"):
            try:
                with open(md_file) as f:
                    content = f.read()
                
                frontmatter = self._parse_frontmatter(content)
                if frontmatter:
                    examples.append((md_file.name, frontmatter))
                else:
                    logger.warning(f"Could not parse frontmatter from {md_file.name}")
                    
            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
        
        logger.info(f"Successfully parsed {len(examples)} frontmatter examples")
        return examples
    
    def _parse_frontmatter(self, content: str) -> Optional[Dict]:
        """Parse YAML frontmatter from markdown content."""
        try:
            if not content.strip().startswith('---'):
                return None
            
            lines = content.split('\n')
            yaml_lines = []
            in_frontmatter = False
            
            for line in lines:
                if line.strip() == '---':
                    if in_frontmatter:
                        break
                    else:
                        in_frontmatter = True
                        continue
                
                if in_frontmatter:
                    yaml_lines.append(line)
            
            if yaml_lines:
                yaml_content = '\n'.join(yaml_lines)
                return yaml.safe_load(yaml_content)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse frontmatter: {e}")
            return None
    
    def analyze_schema_matching(self) -> SchemaMatchResult:
        """Comprehensive schema matching analysis."""
        examples = self.parse_all_frontmatter_examples()
        
        if not examples:
            return SchemaMatchResult(0, 0, 0.0, {}, ["No examples found"])
        
        # Get schema requirements
        schema = self.validator.get_schema_for_component('frontmatter')
        required_fields = set(self.validator.get_required_fields_from_schema(schema, 'frontmatter'))
        
        # Analyze each field
        all_fields = set()
        for _, frontmatter in examples:
            all_fields.update(frontmatter.keys())
        
        field_analyses = {}
        valid_examples = 0
        
        for field_name in all_fields:
            analysis = self._analyze_field(field_name, examples, field_name in required_fields)
            field_analyses[field_name] = analysis
        
        # Count valid examples (those with all required fields)
        for _, frontmatter in examples:
            if required_fields.issubset(set(frontmatter.keys())):
                valid_examples += 1
        
        compliance = (valid_examples / len(examples)) * 100 if examples else 0
        
        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(
            field_analyses, required_fields, examples
        )
        
        return SchemaMatchResult(
            total_examples=len(examples),
            valid_examples=valid_examples,
            schema_compliance=compliance,
            field_analyses=field_analyses,
            optimization_recommendations=recommendations
        )
    
    def _analyze_field(self, field_name: str, examples: List[Tuple[str, Dict]], 
                      is_required: bool) -> FieldAnalysis:
        """Analyze usage of a specific field."""
        present_count = 0
        example_values = []
        field_types = set()
        
        for filename, frontmatter in examples:
            if field_name in frontmatter:
                present_count += 1
                value = frontmatter[field_name]
                
                # Collect type information
                field_types.add(type(value).__name__)
                
                # Collect example values (truncated)
                if isinstance(value, str):
                    example_values.append(value[:50] + "..." if len(value) > 50 else value)
                elif isinstance(value, (list, dict)):
                    example_values.append(f"{type(value).__name__}[{len(value)}]")
                else:
                    example_values.append(str(value))
        
        usage_percentage = (present_count / len(examples)) * 100 if examples else 0
        
        return FieldAnalysis(
            field_name=field_name,
            present_in=present_count,
            total_examples=len(examples),
            usage_percentage=usage_percentage,
            example_values=example_values[:5],  # Keep top 5 examples
            field_types=field_types,
            is_required=is_required
        )
    
    def _generate_optimization_recommendations(self, field_analyses: Dict[str, FieldAnalysis],
                                             required_fields: Set[str], 
                                             examples: List[Tuple[str, Dict]]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Check required field compliance
        required_compliance = []
        for field_name in required_fields:
            if field_name in field_analyses:
                analysis = field_analyses[field_name]
                required_compliance.append((field_name, analysis.usage_percentage))
        
        avg_required_compliance = sum(pct for _, pct in required_compliance) / len(required_compliance)
        
        if avg_required_compliance < 100:
            recommendations.append(
                f"Required field compliance is {avg_required_compliance:.1f}%. "
                f"Some examples missing required fields."
            )
        
        # Check for consistently used non-required fields
        non_required_high_usage = []
        for field_name, analysis in field_analyses.items():
            if not analysis.is_required and analysis.usage_percentage >= 80:
                non_required_high_usage.append((field_name, analysis.usage_percentage))
        
        if non_required_high_usage:
            recommendations.append(
                f"Consider making these fields required: "
                f"{', '.join(f'{name} ({pct:.1f}%)' for name, pct in non_required_high_usage)}"
            )
        
        # Check for rarely used required fields
        low_usage_required = []
        for field_name, analysis in field_analyses.items():
            if analysis.is_required and analysis.usage_percentage < 90:
                low_usage_required.append((field_name, analysis.usage_percentage))
        
        if low_usage_required:
            recommendations.append(
                f"Required fields with low usage: "
                f"{', '.join(f'{name} ({pct:.1f}%)' for name, pct in low_usage_required)}"
            )
        
        # Check for inconsistent field types
        inconsistent_types = []
        for field_name, analysis in field_analyses.items():
            if len(analysis.field_types) > 1:
                inconsistent_types.append((field_name, analysis.field_types))
        
        if inconsistent_types:
            recommendations.append(
                f"Fields with inconsistent types: "
                f"{', '.join(f'{name} {types}' for name, types in inconsistent_types)}"
            )
        
        # Overall assessment
        total_fields = len(field_analyses)
        required_count = len(required_fields)
        
        recommendations.append(
            f"Schema defines {required_count} required fields out of {total_fields} total fields used. "
            f"Schema coverage: {(required_count/total_fields)*100:.1f}%"
        )
        
        return recommendations
    
    def generate_detailed_report(self) -> str:
        """Generate comprehensive matching report."""
        result = self.analyze_schema_matching()
        
        report = ["# Schema-Component Matching Analysis", ""]
        
        # Executive Summary
        report.extend([
            "## Executive Summary",
            "",
            f"- **Total Examples Analyzed**: {result.total_examples}",
            f"- **Schema Compliant Examples**: {result.valid_examples}/{result.total_examples} ({result.schema_compliance:.1f}%)",
            f"- **Fields Analyzed**: {len(result.field_analyses)}",
            ""
        ])
        
        # Field Analysis
        report.extend(["## Field Usage Analysis", ""])
        
        # Sort fields by usage percentage
        sorted_fields = sorted(
            result.field_analyses.items(),
            key=lambda x: (x[1].is_required, x[1].usage_percentage),
            reverse=True
        )
        
        # Required fields section
        report.extend(["### Required Fields", ""])
        required_fields = [(name, analysis) for name, analysis in sorted_fields if analysis.is_required]
        
        if required_fields:
            report.append("| Field | Usage | Type(s) | Example Values |")
            report.append("|-------|-------|---------|----------------|")
            
            for field_name, analysis in required_fields:
                types_str = ", ".join(analysis.field_types)
                examples_str = "; ".join(analysis.example_values[:2])
                report.append(
                    f"| {field_name} | {analysis.usage_percentage:.1f}% "
                    f"({analysis.present_in}/{analysis.total_examples}) | {types_str} | {examples_str} |"
                )
        else:
            report.append("*No required fields found in schema.*")
        
        report.append("")
        
        # Optional fields section
        report.extend(["### Optional Fields", ""])
        optional_fields = [(name, analysis) for name, analysis in sorted_fields if not analysis.is_required]
        
        if optional_fields:
            report.append("| Field | Usage | Type(s) | Example Values |")
            report.append("|-------|-------|---------|----------------|")
            
            for field_name, analysis in optional_fields:
                types_str = ", ".join(analysis.field_types)
                examples_str = "; ".join(analysis.example_values[:2])
                report.append(
                    f"| {field_name} | {analysis.usage_percentage:.1f}% "
                    f"({analysis.present_in}/{analysis.total_examples}) | {types_str} | {examples_str} |"
                )
        
        report.append("")
        
        # Optimization recommendations
        report.extend(["## Optimization Recommendations", ""])
        
        for i, recommendation in enumerate(result.optimization_recommendations, 1):
            report.append(f"{i}. {recommendation}")
        
        report.append("")
        
        # Technical Assessment
        report.extend([
            "## Technical Assessment for Laser Cleaning Website", "",
            "### Schema Completeness",
        ])
        
        # Calculate metrics
        high_usage_optional = sum(1 for _, analysis in result.field_analyses.items() 
                                if not analysis.is_required and analysis.usage_percentage >= 80)
        
        schema_completeness = (len([f for f in result.field_analyses.values() if f.is_required]) / 
                             len(result.field_analyses)) * 100
        
        report.extend([
            f"- **Required field coverage**: {len([f for f in result.field_analyses.values() if f.is_required])}/{len(result.field_analyses)} fields ({schema_completeness:.1f}%)",
            f"- **High-usage optional fields**: {high_usage_optional} fields used in 80%+ examples",
            f"- **Schema compliance rate**: {result.schema_compliance:.1f}%",
            "",
            "### Recommendations for Production",
            ""
        ])
        
        if result.schema_compliance >= 95:
            report.append("✅ **READY FOR PRODUCTION** - High schema compliance")
        elif result.schema_compliance >= 80:
            report.append("⚠️ **NEEDS MINOR OPTIMIZATION** - Good compliance with room for improvement")
        else:
            report.append("❌ **NEEDS MAJOR OPTIMIZATION** - Low schema compliance")
        
        return "\n".join(report)


def main():
    """Run comprehensive schema-component matching analysis."""
    print("Starting comprehensive schema-component matching analysis...")
    
    matcher = SchemaComponentMatcher()
    report = matcher.generate_detailed_report()
    
    # Save detailed report
    report_file = Path("schema_component_matching_report.md")
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Detailed report saved to {report_file}")
    
    # Print summary to console
    print("\n" + "="*80)
    print("SCHEMA-COMPONENT MATCHING SUMMARY")
    print("="*80)
    print(report)


if __name__ == "__main__":
    main()
