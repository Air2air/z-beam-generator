#!/usr/bin/env python3
"""
Data Completeness Analyzer

Measures completeness of generated content against JSON schemas to provide
comprehensive quality metrics and identify missing data fields.

This system leverages the existing schemas to provide:
1. Schema-based completeness scoring
2. Required vs optional field analysis  
3. Data quality metrics with confidence scores
4. Missing field identification and recommendations
5. Component-specific completeness reports
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum


class CompletenessLevel(Enum):
    """Completeness level classifications"""
    EXCELLENT = "excellent"      # 95-100%
    GOOD = "good"               # 85-94%
    FAIR = "fair"               # 70-84%
    POOR = "poor"               # 50-69%
    CRITICAL = "critical"       # <50%


@dataclass
class FieldAnalysis:
    """Analysis of individual field completeness"""
    field_name: str
    is_present: bool
    is_required: bool
    schema_type: str
    expected_type: Optional[str] = None
    actual_type: Optional[str] = None
    value_quality: Optional[float] = None  # 0.0-1.0 quality score
    validation_metadata: Optional[Dict] = None


@dataclass
class CompletenessReport:
    """Comprehensive completeness analysis report"""
    component_type: str
    material_name: str
    overall_score: float  # 0.0-100.0
    completeness_level: CompletenessLevel
    required_fields_score: float
    optional_fields_score: float
    total_fields_expected: int
    total_fields_present: int
    required_fields_present: int
    required_fields_total: int
    missing_required: List[str]
    missing_optional: List[str]
    field_analyses: List[FieldAnalysis]
    recommendations: List[str]
    quality_metrics: Dict[str, float]
    validation_errors: List[str]


class DataCompletenessAnalyzer:
    """Analyzes data completeness against JSON schemas"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.schemas_dir = self.project_root / "schemas"
        self.schemas = {}
        self.logger = logging.getLogger(__name__)
        
        # Load all available schemas
        self._load_schemas()
    
    def _load_schemas(self):
        """Load all JSON schemas for validation"""
        try:
            schema_files = {
                'frontmatter': 'frontmatter.json',
                'material': 'material.json',
                'metricsproperties': 'metricsproperties.json',
                'metricsmachinesettings': 'metricsmachinesettings.json',
                'jsonld': 'json-ld.json',
                'materials_yaml': 'Materials_yaml.json'
            }
            
            for schema_name, filename in schema_files.items():
                schema_path = self.schemas_dir / filename
                if schema_path.exists():
                    with open(schema_path, 'r') as f:
                        self.schemas[schema_name] = json.load(f)
                    self.logger.info(f"✅ Loaded schema: {schema_name}")
                else:
                    self.logger.warning(f"⚠️ Schema not found: {filename}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error loading schemas: {e}")
    
    def analyze_frontmatter_completeness(self, material_name: str) -> CompletenessReport:
        """Analyze frontmatter completeness against schema"""
        
        # Load frontmatter data
        frontmatter_path = self.project_root / "content" / "components" / "frontmatter" / f"{material_name.lower()}-laser-cleaning.md"
        
        if not frontmatter_path.exists():
            return CompletenessReport(
                component_type="frontmatter",
                material_name=material_name,
                overall_score=0.0,
                completeness_level=CompletenessLevel.CRITICAL,
                required_fields_score=0.0,
                optional_fields_score=0.0,
                total_fields_expected=0,
                total_fields_present=0,
                required_fields_present=0,
                required_fields_total=0,
                missing_required=[],
                missing_optional=[],
                field_analyses=[],
                recommendations=["Frontmatter file does not exist"],
                quality_metrics={},
                validation_errors=["File not found"]
            )
        
        # Parse frontmatter YAML
        try:
            with open(frontmatter_path, 'r') as f:
                content = f.read()
                
            # Extract YAML frontmatter
            if content.startswith('---'):
                yaml_content = content.split('---')[1]
                data = yaml.safe_load(yaml_content)
            else:
                data = {}
                
        except Exception as e:
            self.logger.error(f"❌ Error parsing frontmatter: {e}")
            data = {}
        
        return self._analyze_against_schema(data, 'frontmatter', material_name)
    
    def analyze_materials_yaml_completeness(self, material_name: str) -> CompletenessReport:
        """Analyze Materials.yaml entry completeness"""
        
        # Load Materials.yaml data
        materials_path = self.project_root / "data" / "Materials.yaml"
        
        try:
            with open(materials_path, 'r') as f:
                materials_data = yaml.safe_load(f)
            
            # Find material data
            material_data = None
            if 'materials' in materials_data:
                for category_data in materials_data['materials'].values():
                    if 'items' in category_data:
                        for item in category_data['items']:
                            if item.get('name', '').lower() == material_name.lower():
                                material_data = item
                                break
                    if material_data:
                        break
                        
            if not material_data:
                return CompletenessReport(
                    component_type="materials_yaml",
                    material_name=material_name,
                    overall_score=0.0,
                    completeness_level=CompletenessLevel.CRITICAL,
                    required_fields_score=0.0,
                    optional_fields_score=0.0,
                    total_fields_expected=0,
                    total_fields_present=0,
                    required_fields_present=0,
                    required_fields_total=0,
                    missing_required=[],
                    missing_optional=[],
                    field_analyses=[],
                    recommendations=["Material not found in Materials.yaml"],
                    quality_metrics={},
                    validation_errors=["Material data not found"]
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error loading Materials.yaml: {e}")
            material_data = {}
        
        return self._analyze_against_schema(material_data, 'materials_yaml', material_name)
    
    def _analyze_against_schema(self, data: Dict, schema_type: str, material_name: str) -> CompletenessReport:
        """Core analysis logic against JSON schema"""
        
        if schema_type not in self.schemas:
            return self._create_empty_report(schema_type, material_name, ["Schema not available"])
        
        schema = self.schemas[schema_type]
        field_analyses = []
        missing_required = []
        missing_optional = []
        validation_errors = []
        
        # Get required and optional fields from schema
        required_fields = set(schema.get('required', []))
        all_properties = schema.get('properties', {})
        optional_fields = set(all_properties.keys()) - required_fields
        
        # Analyze each field
        for field_name, field_schema in all_properties.items():
            is_required = field_name in required_fields
            is_present = field_name in data
            
            if not is_present:
                if is_required:
                    missing_required.append(field_name)
                else:
                    missing_optional.append(field_name)
            
            # Analyze field quality if present
            value_quality = None
            validation_metadata = None
            
            if is_present:
                value_quality = self._assess_field_quality(data[field_name], field_schema, field_name)
                
                # Check for validation metadata (research validation)
                if isinstance(data[field_name], dict):
                    validation_keys = ['confidence_score', 'sources_validated', 'research_sources', 'validation']
                    validation_metadata = {k: v for k, v in data[field_name].items() if k in validation_keys}
            
            field_analysis = FieldAnalysis(
                field_name=field_name,
                is_present=is_present,
                is_required=is_required,
                schema_type=field_schema.get('type', 'unknown'),
                expected_type=field_schema.get('type'),
                actual_type=type(data.get(field_name)).__name__ if is_present else None,
                value_quality=value_quality,
                validation_metadata=validation_metadata
            )
            
            field_analyses.append(field_analysis)
        
        # Calculate scores
        required_fields_present = len(required_fields) - len(missing_required)
        required_fields_total = len(required_fields)
        required_fields_score = (required_fields_present / required_fields_total * 100) if required_fields_total > 0 else 100.0
        
        optional_fields_present = len(optional_fields) - len(missing_optional)  
        optional_fields_total = len(optional_fields)
        optional_fields_score = (optional_fields_present / optional_fields_total * 100) if optional_fields_total > 0 else 100.0
        
        # Weight required fields more heavily (70% required, 30% optional)
        overall_score = (required_fields_score * 0.7) + (optional_fields_score * 0.3)
        
        # Determine completeness level
        if overall_score >= 95:
            completeness_level = CompletenessLevel.EXCELLENT
        elif overall_score >= 85:
            completeness_level = CompletenessLevel.GOOD
        elif overall_score >= 70:
            completeness_level = CompletenessLevel.FAIR
        elif overall_score >= 50:
            completeness_level = CompletenessLevel.POOR
        else:
            completeness_level = CompletenessLevel.CRITICAL
        
        # Generate recommendations
        recommendations = self._generate_recommendations(missing_required, missing_optional, field_analyses)
        
        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(field_analyses, data)
        
        return CompletenessReport(
            component_type=schema_type,
            material_name=material_name,
            overall_score=overall_score,
            completeness_level=completeness_level,
            required_fields_score=required_fields_score,
            optional_fields_score=optional_fields_score,
            total_fields_expected=len(all_properties),
            total_fields_present=len(all_properties) - len(missing_required) - len(missing_optional),
            required_fields_present=required_fields_present,
            required_fields_total=required_fields_total,
            missing_required=missing_required,
            missing_optional=missing_optional,
            field_analyses=field_analyses,
            recommendations=recommendations,
            quality_metrics=quality_metrics,
            validation_errors=validation_errors
        )
    
    def _assess_field_quality(self, value: Any, field_schema: Dict, field_name: str) -> float:
        """Assess quality of individual field value"""
        
        quality_score = 0.5  # Base score
        
        # Type matching
        expected_type = field_schema.get('type')
        if expected_type:
            actual_type = type(value).__name__
            type_mapping = {
                'string': 'str',
                'number': ['int', 'float'],
                'integer': 'int',
                'boolean': 'bool',
                'array': 'list',
                'object': 'dict'
            }
            
            expected_python_types = type_mapping.get(expected_type, expected_type)
            if isinstance(expected_python_types, list):
                type_matches = actual_type in expected_python_types
            else:
                type_matches = actual_type == expected_python_types
                
            if type_matches:
                quality_score += 0.2
        
        # Value completeness and richness
        if isinstance(value, str):
            if len(value.strip()) > 0:
                quality_score += 0.1
            if len(value.strip()) > 10:  # Substantial content
                quality_score += 0.1
        elif isinstance(value, (list, dict)):
            if len(value) > 0:
                quality_score += 0.2
        elif isinstance(value, (int, float)):
            if value > 0:  # Positive values generally indicate real data
                quality_score += 0.2
        
        # Research validation indicators
        if isinstance(value, dict):
            validation_indicators = ['confidence_score', 'sources_validated', 'research_sources', 'validation', 'min', 'max']
            validation_present = sum(1 for indicator in validation_indicators if indicator in value)
            if validation_present > 0:
                quality_score += min(0.3, validation_present * 0.1)  # Up to 0.3 bonus for validation
        
        return min(1.0, quality_score)  # Cap at 1.0
    
    def _generate_recommendations(self, missing_required: List[str], missing_optional: List[str], field_analyses: List[FieldAnalysis]) -> List[str]:
        """Generate actionable recommendations for improving completeness"""
        
        recommendations = []
        
        # Critical missing fields
        if missing_required:
            recommendations.append(f"🚨 CRITICAL: Add required fields: {', '.join(missing_required)}")
        
        # High-impact optional fields
        priority_optional = ['properties', 'machineSettings', 'applications', 'compatibility']
        missing_priority = [field for field in missing_optional if field in priority_optional]
        if missing_priority:
            recommendations.append(f"⚡ HIGH PRIORITY: Add key optional fields: {', '.join(missing_priority)}")
        
        # Quality improvements
        low_quality_fields = [f.field_name for f in field_analyses if f.value_quality and f.value_quality < 0.6]
        if low_quality_fields:
            recommendations.append(f"📈 ENHANCE: Improve data quality for: {', '.join(low_quality_fields)}")
        
        # Research validation suggestions
        unvalidated_fields = [f.field_name for f in field_analyses 
                            if f.is_present and not f.validation_metadata]
        if unvalidated_fields:
            recommendations.append(f"🔬 RESEARCH: Add validation metadata for: {', '.join(unvalidated_fields[:3])}...")
        
        return recommendations
    
    def _calculate_quality_metrics(self, field_analyses: List[FieldAnalysis], data: Dict) -> Dict[str, float]:
        """Calculate additional quality metrics"""
        
        metrics = {}
        
        # Average field quality
        quality_scores = [f.value_quality for f in field_analyses if f.value_quality is not None]
        if quality_scores:
            metrics['average_field_quality'] = sum(quality_scores) / len(quality_scores)
        
        # Research validation percentage
        validated_fields = [f for f in field_analyses if f.validation_metadata]
        total_present = [f for f in field_analyses if f.is_present]
        if total_present:
            metrics['research_validation_percentage'] = len(validated_fields) / len(total_present) * 100
        
        # Data richness (nested objects, arrays with content)
        rich_fields = 0
        for field in field_analyses:
            if field.is_present:
                value = data.get(field.field_name)
                if isinstance(value, dict) and len(value) > 2:
                    rich_fields += 1
                elif isinstance(value, list) and len(value) > 1:
                    rich_fields += 1
        
        if total_present:
            metrics['data_richness_percentage'] = rich_fields / len(total_present) * 100
        
        return metrics
    
    def _create_empty_report(self, schema_type: str, material_name: str, errors: List[str]) -> CompletenessReport:
        """Create empty report for error cases"""
        return CompletenessReport(
            component_type=schema_type,
            material_name=material_name,
            overall_score=0.0,
            completeness_level=CompletenessLevel.CRITICAL,
            required_fields_score=0.0,
            optional_fields_score=0.0,
            total_fields_expected=0,
            total_fields_present=0,
            required_fields_present=0,
            required_fields_total=0,
            missing_required=[],
            missing_optional=[],
            field_analyses=[],
            recommendations=[],
            quality_metrics={},
            validation_errors=errors
        )
    
    def analyze_complete_material(self, material_name: str) -> Dict[str, CompletenessReport]:
        """Analyze completeness across all components for a material"""
        
        reports = {}
        
        # Analyze frontmatter
        reports['frontmatter'] = self.analyze_frontmatter_completeness(material_name)
        
        # Analyze Materials.yaml
        reports['materials_yaml'] = self.analyze_materials_yaml_completeness(material_name)
        
        return reports
    
    def generate_completeness_summary(self, reports: Dict[str, CompletenessReport]) -> Dict[str, Any]:
        """Generate summary across all component reports"""
        
        if not reports:
            return {"error": "No reports provided"}
        
        # Calculate overall metrics
        total_score = sum(report.overall_score for report in reports.values())
        average_score = total_score / len(reports)
        
        # Find best and worst components
        sorted_reports = sorted(reports.items(), key=lambda x: x[1].overall_score, reverse=True)
        best_component = sorted_reports[0]
        worst_component = sorted_reports[-1]
        
        # Aggregate recommendations
        all_recommendations = []
        for component, report in reports.items():
            for rec in report.recommendations:
                all_recommendations.append(f"{component.upper()}: {rec}")
        
        return {
            "material_name": list(reports.values())[0].material_name,
            "overall_average_score": round(average_score, 1),
            "total_components_analyzed": len(reports),
            "best_component": {
                "name": best_component[0],
                "score": round(best_component[1].overall_score, 1),
                "level": best_component[1].completeness_level.value
            },
            "worst_component": {
                "name": worst_component[0], 
                "score": round(worst_component[1].overall_score, 1),
                "level": worst_component[1].completeness_level.value
            },
            "component_scores": {name: round(report.overall_score, 1) for name, report in reports.items()},
            "top_recommendations": all_recommendations[:5],
            "total_recommendations": len(all_recommendations)
        }


def main():
    """CLI interface for data completeness analysis"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze data completeness against schemas")
    parser.add_argument("material", help="Material name to analyze")
    parser.add_argument("--component", help="Specific component to analyze (frontmatter, materials_yaml)", default="all")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    
    analyzer = DataCompletenessAnalyzer()
    
    print(f"🔍 ANALYZING DATA COMPLETENESS: {args.material}")
    print("=" * 60)
    
    if args.component == "all":
        reports = analyzer.analyze_complete_material(args.material)
        summary = analyzer.generate_completeness_summary(reports)
        
        print(f"📊 OVERALL SUMMARY")
        print(f"   Material: {summary['material_name']}")
        print(f"   Average Score: {summary['overall_average_score']}%")
        print(f"   Components Analyzed: {summary['total_components_analyzed']}")
        print()
        
        print(f"🏆 COMPONENT SCORES")
        for component, score in summary['component_scores'].items():
            level = reports[component].completeness_level.value.upper()
            print(f"   {component}: {score}% ({level})")
        print()
        
        print(f"🎯 TOP RECOMMENDATIONS")
        for i, rec in enumerate(summary['top_recommendations'], 1):
            print(f"   {i}. {rec}")
        
        if args.verbose:
            print(f"\n📋 DETAILED REPORTS")
            for component, report in reports.items():
                print(f"\n--- {component.upper()} ---")
                print(f"Score: {report.overall_score:.1f}%")
                print(f"Required Fields: {report.required_fields_present}/{report.required_fields_total}")
                print(f"Missing Required: {report.missing_required}")
                print(f"Quality Metrics: {report.quality_metrics}")
    
    else:
        if args.component == "frontmatter":
            report = analyzer.analyze_frontmatter_completeness(args.material)
        elif args.component == "materials_yaml":
            report = analyzer.analyze_materials_yaml_completeness(args.material)
        else:
            print(f"❌ Unknown component: {args.component}")
            return
        
        print(f"📊 {args.component.upper()} ANALYSIS")
        print(f"   Score: {report.overall_score:.1f}% ({report.completeness_level.value.upper()})")
        print(f"   Required Fields: {report.required_fields_present}/{report.required_fields_total}")
        print(f"   Total Fields: {report.total_fields_present}/{report.total_fields_expected}")
        print()
        
        if report.missing_required:
            print(f"❌ Missing Required: {', '.join(report.missing_required)}")
        
        if report.recommendations:
            print(f"💡 Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"   {i}. {rec}")


if __name__ == "__main__":
    main()