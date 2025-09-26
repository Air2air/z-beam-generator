#!/usr/bin/env python3
"""
Advanced Schema-Based Quality Metrics

Comprehensive quality measurement system that leverages JSON schemas to provide:
1. Multi-dimensional completeness scoring
2. Research validation depth analysis
3. Field priority weighting based on schema importance
4. Component interdependency validation
5. Quality trend tracking over time
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for generated content"""
    
    # Core Completeness Metrics
    overall_completeness_score: float
    required_fields_completeness: float
    optional_fields_completeness: float
    field_count_ratio: float  # actual/expected
    
    # Research Validation Metrics
    research_validation_score: float
    confidence_score_average: float
    sources_validation_coverage: float
    validation_metadata_richness: float
    
    # Data Quality Metrics
    data_richness_score: float
    type_accuracy_score: float
    value_depth_score: float  # nested objects, arrays
    semantic_completeness_score: float  # meaningful content
    
    # Schema Compliance Metrics
    schema_compliance_score: float
    required_field_violations: int
    type_violations: int
    format_violations: int
    
    # Component-Specific Metrics
    material_specificity_score: float  # Ti-6Al-4V vs generic Titanium
    laser_relevance_score: float
    processing_guidance_score: float
    safety_completeness_score: float
    
    # Metadata
    analysis_timestamp: str
    component_type: str
    material_name: str
    schema_version: Optional[str] = None


class AdvancedQualityAnalyzer:
    """Advanced schema-based quality analysis system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.schemas_dir = self.project_root / "schemas"
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict[str, Dict]:
        """Load and parse all JSON schemas"""
        schemas = {}
        
        schema_files = [
            'frontmatter.json',
            'material.json', 
            'metricsproperties.json',
            'metricsmachinesettings.json'
        ]
        
        for schema_file in schema_files:
            schema_path = self.schemas_dir / schema_file
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    schema_name = schema_file.replace('.json', '')
                    schemas[schema_name] = json.load(f)
        
        return schemas
    
    def analyze_frontmatter_quality(self, material_name: str) -> QualityMetrics:
        """Comprehensive frontmatter quality analysis"""
        
        # Load frontmatter data
        frontmatter_path = self.project_root / "content" / "components" / "frontmatter" / f"{material_name.lower()}-laser-cleaning.md"
        
        if not frontmatter_path.exists():
            return self._create_zero_metrics("frontmatter", material_name, "File not found")
        
        # Parse frontmatter
        try:
            with open(frontmatter_path, 'r') as f:
                content = f.read()
            
            if content.startswith('---'):
                yaml_content = content.split('---')[1]
                data = yaml.safe_load(yaml_content)
            else:
                return self._create_zero_metrics("frontmatter", material_name, "No YAML frontmatter found")
                
        except Exception as e:
            return self._create_zero_metrics("frontmatter", material_name, f"Parse error: {e}")
        
        return self._calculate_comprehensive_metrics(data, 'frontmatter', material_name)
    
    def _calculate_comprehensive_metrics(self, data: Dict, schema_type: str, material_name: str) -> QualityMetrics:
        """Calculate comprehensive quality metrics"""
        
        schema = self.schemas.get(schema_type, {})
        
        # 1. Core Completeness Metrics
        completeness_metrics = self._calculate_completeness_metrics(data, schema)
        
        # 2. Research Validation Metrics
        validation_metrics = self._calculate_validation_metrics(data)
        
        # 3. Data Quality Metrics
        quality_metrics = self._calculate_data_quality_metrics(data, schema)
        
        # 4. Schema Compliance Metrics
        compliance_metrics = self._calculate_compliance_metrics(data, schema)
        
        # 5. Component-Specific Metrics
        component_metrics = self._calculate_component_specific_metrics(data, material_name)
        
        return QualityMetrics(
            # Core completeness
            overall_completeness_score=completeness_metrics['overall'],
            required_fields_completeness=completeness_metrics['required'],
            optional_fields_completeness=completeness_metrics['optional'],
            field_count_ratio=completeness_metrics['count_ratio'],
            
            # Research validation
            research_validation_score=validation_metrics['overall'],
            confidence_score_average=validation_metrics['confidence_average'],
            sources_validation_coverage=validation_metrics['sources_coverage'],
            validation_metadata_richness=validation_metrics['metadata_richness'],
            
            # Data quality
            data_richness_score=quality_metrics['richness'],
            type_accuracy_score=quality_metrics['type_accuracy'],
            value_depth_score=quality_metrics['value_depth'],
            semantic_completeness_score=quality_metrics['semantic'],
            
            # Schema compliance
            schema_compliance_score=compliance_metrics['overall'],
            required_field_violations=compliance_metrics['required_violations'],
            type_violations=compliance_metrics['type_violations'],
            format_violations=compliance_metrics['format_violations'],
            
            # Component-specific
            material_specificity_score=component_metrics['material_specificity'],
            laser_relevance_score=component_metrics['laser_relevance'],
            processing_guidance_score=component_metrics['processing_guidance'],
            safety_completeness_score=component_metrics['safety_completeness'],
            
            # Metadata
            analysis_timestamp=datetime.now().isoformat(),
            component_type=schema_type,
            material_name=material_name,
            schema_version=schema.get('version', 'unknown')
        )
    
    def _calculate_completeness_metrics(self, data: Dict, schema: Dict) -> Dict[str, float]:
        """Calculate field completeness metrics"""
        
        if not schema:
            return {'overall': 0.0, 'required': 0.0, 'optional': 0.0, 'count_ratio': 0.0}
        
        properties = schema.get('properties', {})
        required_fields = set(schema.get('required', []))
        optional_fields = set(properties.keys()) - required_fields
        
        # Required field completeness
        required_present = sum(1 for field in required_fields if field in data)
        required_completeness = (required_present / len(required_fields) * 100) if required_fields else 100.0
        
        # Optional field completeness
        optional_present = sum(1 for field in optional_fields if field in data)
        optional_completeness = (optional_present / len(optional_fields) * 100) if optional_fields else 100.0
        
        # Overall completeness (weighted: 70% required, 30% optional)
        overall_completeness = (required_completeness * 0.7) + (optional_completeness * 0.3)
        
        # Field count ratio
        total_present = len([k for k in data.keys() if k in properties])
        total_expected = len(properties)
        count_ratio = (total_present / total_expected) if total_expected > 0 else 0.0
        
        return {
            'overall': overall_completeness,
            'required': required_completeness,
            'optional': optional_completeness,
            'count_ratio': count_ratio
        }
    
    def _calculate_validation_metrics(self, data: Dict) -> Dict[str, float]:
        """Calculate research validation metrics"""
        
        # Find fields with validation metadata
        validated_fields = []
        confidence_scores = []
        sources_counts = []
        
        def extract_validation_recursive(obj, path=""):
            if isinstance(obj, dict):
                # Check for validation indicators
                validation_keys = ['confidence_score', 'confidenceScore', 'sources_validated', 'sourcesValidated']
                has_validation = any(key in obj for key in validation_keys)
                
                if has_validation:
                    validated_fields.append(path)
                    
                    # Extract confidence score
                    for conf_key in ['confidence_score', 'confidenceScore']:
                        if conf_key in obj and isinstance(obj[conf_key], (int, float)):
                            confidence_scores.append(obj[conf_key])
                            break
                    
                    # Extract sources count
                    for sources_key in ['sources_validated', 'sourcesValidated']:
                        if sources_key in obj and isinstance(obj[sources_key], int):
                            sources_counts.append(obj[sources_key])
                            break
                
                # Recurse into nested objects
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    extract_validation_recursive(value, new_path)
        
        extract_validation_recursive(data)
        
        # Calculate metrics
        total_fields = self._count_total_fields(data)
        
        overall_validation = (len(validated_fields) / total_fields * 100) if total_fields > 0 else 0.0
        confidence_average = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        sources_coverage = (len(sources_counts) / total_fields * 100) if total_fields > 0 else 0.0
        
        # Metadata richness (how detailed the validation is)
        validation_detail_score = 0.0
        for field in validated_fields:
            field_obj = self._get_nested_value(data, field)
            if isinstance(field_obj, dict):
                detail_indicators = ['research_sources', 'processing_impact', 'description', 'priority']
                detail_score = sum(1 for indicator in detail_indicators if indicator in field_obj)
                validation_detail_score += detail_score / 4.0  # Normalize to 0-1
        
        metadata_richness = (validation_detail_score / len(validated_fields)) if validated_fields else 0.0
        
        return {
            'overall': overall_validation,
            'confidence_average': confidence_average,
            'sources_coverage': sources_coverage,
            'metadata_richness': metadata_richness * 100
        }
    
    def _calculate_data_quality_metrics(self, data: Dict, schema: Dict) -> Dict[str, float]:
        """Calculate data quality and richness metrics"""
        
        # Data richness - complex nested structures
        rich_fields = 0
        total_fields = 0
        
        def assess_richness_recursive(obj):
            nonlocal rich_fields, total_fields
            
            if isinstance(obj, dict):
                total_fields += 1
                if len(obj) > 3:  # Rich if more than 3 properties
                    rich_fields += 1
                for value in obj.values():
                    assess_richness_recursive(value)
            elif isinstance(obj, list):
                total_fields += 1
                if len(obj) > 2:  # Rich if more than 2 items
                    rich_fields += 1
                for item in obj:
                    assess_richness_recursive(item)
        
        assess_richness_recursive(data)
        richness_score = (rich_fields / total_fields * 100) if total_fields > 0 else 0.0
        
        # Type accuracy against schema
        type_matches = 0
        type_total = 0
        
        properties = schema.get('properties', {})
        for field_name, field_schema in properties.items():
            if field_name in data:
                expected_type = field_schema.get('type')
                actual_value = data[field_name]
                type_total += 1
                
                if self._check_type_match(actual_value, expected_type):
                    type_matches += 1
        
        type_accuracy = (type_matches / type_total * 100) if type_total > 0 else 100.0
        
        # Value depth - nested content analysis
        max_depth = self._calculate_max_depth(data)
        depth_score = min(100.0, max_depth * 20)  # Cap at 100, reward depth
        
        # Semantic completeness - meaningful content
        semantic_score = self._assess_semantic_completeness(data)
        
        return {
            'richness': richness_score,
            'type_accuracy': type_accuracy,
            'value_depth': depth_score,
            'semantic': semantic_score
        }
    
    def _calculate_compliance_metrics(self, data: Dict, schema: Dict) -> Dict[str, float]:
        """Calculate schema compliance metrics"""
        
        violations = {
            'required_violations': 0,
            'type_violations': 0,
            'format_violations': 0
        }
        
        if not schema:
            return {'overall': 0.0, **violations}
        
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                violations['required_violations'] += 1
        
        # Check type compliance
        for field_name, field_schema in properties.items():
            if field_name in data:
                expected_type = field_schema.get('type')
                if expected_type and not self._check_type_match(data[field_name], expected_type):
                    violations['type_violations'] += 1
        
        # Calculate overall compliance
        total_possible_violations = len(required_fields) + len(properties)
        total_violations = sum(violations.values())
        
        compliance_score = max(0.0, (total_possible_violations - total_violations) / total_possible_violations * 100) if total_possible_violations > 0 else 100.0
        
        return {
            'overall': compliance_score,
            **violations
        }
    
    def _calculate_component_specific_metrics(self, data: Dict, material_name: str) -> Dict[str, float]:
        """Calculate component-specific quality metrics"""
        
        # Material specificity (Ti-6Al-4V vs generic Titanium)
        specificity_indicators = [
            'Ti-6Al-4V' in str(data.get('name', '')),
            'Ti-6Al-4V' in str(data.get('formula', '')),
            'aerospace' in str(data.get('subcategory', '')),
            any('Ti-6Al-4V' in str(app) for app in data.get('applications', []))
        ]
        material_specificity = sum(specificity_indicators) / len(specificity_indicators) * 100
        
        # Laser relevance
        laser_indicators = [
            'machineSettings' in data,
            'wavelength' in str(data),
            'laser' in str(data).lower(),
            'fluence' in str(data).lower(),
            'ablation' in str(data).lower()
        ]
        laser_relevance = sum(laser_indicators) / len(laser_indicators) * 100
        
        # Processing guidance richness
        guidance_indicators = [
            'processing_notes' in str(data),
            'optimization_notes' in str(data),
            'processingImpact' in str(data),
            'thermalDamageThreshold' in str(data)
        ]
        processing_guidance = sum(guidance_indicators) / len(guidance_indicators) * 100
        
        # Safety completeness
        safety_indicators = [
            'safety' in str(data).lower(),
            'incompatibleConditions' in str(data),
            'thermalDamage' in str(data),
            'eye protection' in str(data).lower(),
            'ventilation' in str(data).lower()
        ]
        safety_completeness = sum(safety_indicators) / len(safety_indicators) * 100
        
        return {
            'material_specificity': material_specificity,
            'laser_relevance': laser_relevance,
            'processing_guidance': processing_guidance,
            'safety_completeness': safety_completeness
        }
    
    def _count_total_fields(self, obj) -> int:
        """Recursively count all fields in nested structure"""
        count = 0
        if isinstance(obj, dict):
            count += len(obj)
            for value in obj.values():
                count += self._count_total_fields(value)
        elif isinstance(obj, list):
            for item in obj:
                count += self._count_total_fields(item)
        return count
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    def _check_type_match(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected schema type"""
        type_mapping = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return True  # Unknown type, assume match
    
    def _calculate_max_depth(self, obj, current_depth=0) -> int:
        """Calculate maximum nesting depth"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_max_depth(value, current_depth + 1) for value in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_max_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
    
    def _assess_semantic_completeness(self, data: Dict) -> float:
        """Assess semantic completeness and meaningfulness of content"""
        
        semantic_indicators = []
        
        # Check for meaningful descriptions
        description_fields = ['description', 'processingImpact', 'optimization_notes', 'processing_notes']
        for field in description_fields:
            value = self._get_nested_value(data, field)
            if isinstance(value, str) and len(value.strip()) > 10:
                semantic_indicators.append(True)
            elif isinstance(value, list) and any(isinstance(item, str) and len(item.strip()) > 10 for item in value):
                semantic_indicators.append(True)
            else:
                semantic_indicators.append(False)
        
        # Check for comprehensive applications
        applications = data.get('applications', [])
        if isinstance(applications, list) and len(applications) >= 4:
            semantic_indicators.append(True)
        else:
            semantic_indicators.append(False)
        
        # Check for detailed machine settings
        machine_settings = data.get('machineSettings', {})
        if isinstance(machine_settings, dict) and len(machine_settings) >= 6:
            semantic_indicators.append(True)
        else:
            semantic_indicators.append(False)
        
        return sum(semantic_indicators) / len(semantic_indicators) * 100 if semantic_indicators else 0.0
    
    def _create_zero_metrics(self, component_type: str, material_name: str, error: str) -> QualityMetrics:
        """Create zero metrics for error cases"""
        return QualityMetrics(
            overall_completeness_score=0.0,
            required_fields_completeness=0.0,
            optional_fields_completeness=0.0,
            field_count_ratio=0.0,
            research_validation_score=0.0,
            confidence_score_average=0.0,
            sources_validation_coverage=0.0,
            validation_metadata_richness=0.0,
            data_richness_score=0.0,
            type_accuracy_score=0.0,
            value_depth_score=0.0,
            semantic_completeness_score=0.0,
            schema_compliance_score=0.0,
            required_field_violations=0,
            type_violations=0,
            format_violations=0,
            material_specificity_score=0.0,
            laser_relevance_score=0.0,
            processing_guidance_score=0.0,
            safety_completeness_score=0.0,
            analysis_timestamp=datetime.now().isoformat(),
            component_type=component_type,
            material_name=material_name
        )
    
    def generate_quality_report(self, metrics: QualityMetrics) -> str:
        """Generate human-readable quality report"""
        
        report = f"""
🔍 COMPREHENSIVE QUALITY ANALYSIS: {metrics.material_name}
{'='*60}

📊 OVERALL QUALITY SCORES:
   Overall Completeness: {metrics.overall_completeness_score:.1f}%
   Research Validation: {metrics.research_validation_score:.1f}%
   Schema Compliance: {metrics.schema_compliance_score:.1f}%
   Data Richness: {metrics.data_richness_score:.1f}%

🎯 CORE COMPLETENESS:
   Required Fields: {metrics.required_fields_completeness:.1f}%
   Optional Fields: {metrics.optional_fields_completeness:.1f}%
   Field Count Ratio: {metrics.field_count_ratio:.2f}

🔬 RESEARCH VALIDATION:
   Validation Coverage: {metrics.research_validation_score:.1f}%
   Avg Confidence Score: {metrics.confidence_score_average:.2f}
   Sources Coverage: {metrics.sources_validation_coverage:.1f}%
   Metadata Richness: {metrics.validation_metadata_richness:.1f}%

⚡ DATA QUALITY:
   Type Accuracy: {metrics.type_accuracy_score:.1f}%
   Value Depth: {metrics.value_depth_score:.1f}%
   Semantic Completeness: {metrics.semantic_completeness_score:.1f}%

🎯 COMPONENT-SPECIFIC:
   Material Specificity: {metrics.material_specificity_score:.1f}%
   Laser Relevance: {metrics.laser_relevance_score:.1f}%
   Processing Guidance: {metrics.processing_guidance_score:.1f}%
   Safety Completeness: {metrics.safety_completeness_score:.1f}%

⚠️ COMPLIANCE ISSUES:
   Required Field Violations: {metrics.required_field_violations}
   Type Violations: {metrics.type_violations}
   Format Violations: {metrics.format_violations}

📅 Analysis: {metrics.analysis_timestamp}
"""
        
        return report


def main():
    """CLI interface for advanced quality analysis"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced schema-based quality analysis")
    parser.add_argument("material", help="Material name to analyze")
    parser.add_argument("--export", help="Export metrics to JSON file")
    
    args = parser.parse_args()
    
    analyzer = AdvancedQualityAnalyzer()
    metrics = analyzer.analyze_frontmatter_quality(args.material)
    
    # Display report
    report = analyzer.generate_quality_report(metrics)
    print(report)
    
    # Export if requested
    if args.export:
        with open(args.export, 'w') as f:
            json.dump(asdict(metrics), f, indent=2)
        print(f"📁 Metrics exported to: {args.export}")


if __name__ == "__main__":
    main()