#!/usr/bin/env python3
"""
Stage 5: Quality Assurance
Implements final quality checks and generates confidence scores for all validated properties.
"""

import os
import yaml
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import statistics
from datetime import datetime
import hashlib

class PropertyQualityAssurance:
    """
    Performs comprehensive quality assurance on validated material properties,
    generating final confidence scores and quality reports.
    """
    
    def __init__(self):
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.config_file = Path("config/pipeline_config.yaml")
        self.pipeline_results_dir = Path("pipeline_results")
        
        # Load QA configuration
        self.qa_config = self._load_qa_config()
        
        # Load previous stage results
        self.discovery_results = self._load_stage_results("stage1_discovery_results.json")
        self.standardization_results = self._load_stage_results("stage2_standardization_results.json")
        self.research_results = self._load_stage_results("stage3_research_results.json")
        self.validation_results = self._load_stage_results("stage4_cross_validation_results.json")
        
        # QA tracking
        self.qa_stats = {
            'materials_assessed': 0,
            'properties_scored': 0,
            'quality_grades_assigned': 0,
            'recommendations_generated': 0,
            'final_reports_created': 0,
            'errors': []
        }
    
    def _load_qa_config(self) -> Dict[str, Any]:
        """Load quality assurance configuration"""
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            return config.get('quality_assurance', {
                'scoring_weights': {
                    'completeness': 0.25,
                    'accuracy': 0.30,
                    'consistency': 0.20,
                    'research_validation': 0.15,
                    'peer_agreement': 0.10
                },
                'quality_thresholds': {
                    'excellent': 0.90,
                    'good': 0.75,
                    'acceptable': 0.60,
                    'poor': 0.40
                },
                'critical_properties': {
                    'density': {'weight': 1.0, 'min_confidence': 0.8},
                    'meltingPoint': {'weight': 0.9, 'min_confidence': 0.8},
                    'thermalConductivity': {'weight': 0.8, 'min_confidence': 0.7},
                    'hardness': {'weight': 0.7, 'min_confidence': 0.7}
                },
                'reporting': {
                    'generate_detailed_reports': True,
                    'include_recommendations': True,
                    'create_summary_dashboard': True
                }
            })
            
        except Exception as e:
            print(f"⚠️  Could not load QA config: {e}")
            return self._get_default_qa_config()
    
    def _get_default_qa_config(self) -> Dict[str, Any]:
        """Default QA configuration"""
        
        return {
            'scoring_weights': {
                'completeness': 0.25,
                'accuracy': 0.30,
                'consistency': 0.20,
                'research_validation': 0.15,
                'peer_agreement': 0.10
            },
            'quality_thresholds': {
                'excellent': 0.90,
                'good': 0.75,
                'acceptable': 0.60,
                'poor': 0.40
            },
            'critical_properties': {
                'density': {'weight': 1.0, 'min_confidence': 0.8},
                'meltingPoint': {'weight': 0.9, 'min_confidence': 0.8},
                'thermalConductivity': {'weight': 0.8, 'min_confidence': 0.7},
                'hardness': {'weight': 0.7, 'min_confidence': 0.7},
                'youngsModulus': {'weight': 0.8, 'min_confidence': 0.7},
                'tensileStrength': {'weight': 0.7, 'min_confidence': 0.7}
            },
            'reporting': {
                'generate_detailed_reports': True,
                'include_recommendations': True,
                'create_summary_dashboard': True
            }
        }
    
    def _load_stage_results(self, filename: str) -> Dict[str, Any]:
        """Load results from previous pipeline stages"""
        
        try:
            filepath = self.pipeline_results_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
            else:
                print(f"⚠️  Stage results not found: {filename}")
                return {}
        except Exception as e:
            print(f"⚠️  Error loading stage results {filename}: {e}")
            return {}
    
    def perform_quality_assurance(self, materials_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive quality assurance on all validated properties.
        
        Args:
            materials_filter: Optional list of specific materials to process
            
        Returns:
            QA results with quality scores and recommendations
        """
        
        print("🎯 Starting quality assurance process...")
        
        qa_results = []
        material_scores = {}
        recommendations = []
        
        # Load current material data
        materials_data = self._load_current_materials_data(materials_filter)
        
        for material_name, material_data in materials_data.items():
            try:
                # Perform QA assessment
                material_qa = self._assess_material_quality(material_name, material_data)
                
                qa_results.append(material_qa)
                material_scores[material_name] = material_qa['overall_score']
                
                # Generate recommendations
                material_recommendations = self._generate_material_recommendations(material_qa)
                recommendations.extend(material_recommendations)
                
                self.qa_stats['materials_assessed'] += 1
                
            except Exception as e:
                error_msg = f"Error assessing quality for {material_name}: {e}"
                self.qa_stats['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                
                qa_results.append({
                    'material': material_name,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Generate comprehensive QA report
        qa_report = self._generate_qa_report(qa_results, material_scores, recommendations)
        
        print(f"✅ Quality assurance complete: {self.qa_stats['materials_assessed']} materials assessed")
        print(f"🎯 {self.qa_stats['properties_scored']} properties scored")
        print(f"💡 {len(recommendations)} recommendations generated")
        
        return {
            'results': qa_results,
            'material_scores': material_scores,
            'recommendations': recommendations,
            'statistics': self.qa_stats,
            'report': qa_report,
            'summary': self._generate_qa_summary(qa_results, recommendations)
        }
    
    def _load_current_materials_data(self, materials_filter: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """Load current material data from frontmatter files"""
        
        materials_data = {}
        
        for yaml_file in self.frontmatter_dir.glob("*.yaml"):
            material_name = yaml_file.stem.replace("-laser-cleaning", "")
            
            # Apply materials filter if provided
            if materials_filter and material_name not in materials_filter:
                continue
            
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                materials_data[material_name] = data
                
            except Exception as e:
                print(f"⚠️  Error loading {material_name}: {e}")
        
        return materials_data
    
    def _assess_material_quality(self, material_name: str, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall quality for a single material"""
        
        properties = material_data.get('materialProperties', {})
        category = material_data.get('category', 'unknown')
        
        assessment = {
            'material': material_name,
            'category': category,
            'property_assessments': {},
            'overall_score': 0.0,
            'quality_grade': 'unknown',
            'critical_properties_status': {},
            'completeness_score': 0.0,
            'accuracy_score': 0.0,
            'consistency_score': 0.0,
            'research_validation_score': 0.0,
            'peer_agreement_score': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Assess each property
        property_scores = []
        for prop_name, prop_data in properties.items():
            try:
                prop_assessment = self._assess_property_quality(material_name, prop_name, prop_data)
                assessment['property_assessments'][prop_name] = prop_assessment
                property_scores.append(prop_assessment['quality_score'])
                
                self.qa_stats['properties_scored'] += 1
                
            except Exception as e:
                print(f"⚠️  Error assessing {prop_name} for {material_name}: {e}")
        
        # Calculate dimension scores
        assessment['completeness_score'] = self._calculate_completeness_score(material_name, properties)
        assessment['accuracy_score'] = self._calculate_accuracy_score(material_name, properties)
        assessment['consistency_score'] = self._calculate_consistency_score(material_name, properties)
        assessment['research_validation_score'] = self._calculate_research_validation_score(material_name)
        assessment['peer_agreement_score'] = self._calculate_peer_agreement_score(material_name)
        
        # Calculate overall score using weighted dimensions
        weights = self.qa_config['scoring_weights']
        assessment['overall_score'] = (
            weights['completeness'] * assessment['completeness_score'] +
            weights['accuracy'] * assessment['accuracy_score'] +
            weights['consistency'] * assessment['consistency_score'] +
            weights['research_validation'] * assessment['research_validation_score'] +
            weights['peer_agreement'] * assessment['peer_agreement_score']
        )
        
        # Assign quality grade
        assessment['quality_grade'] = self._assign_quality_grade(assessment['overall_score'])
        
        # Assess critical properties
        assessment['critical_properties_status'] = self._assess_critical_properties(properties)
        
        self.qa_stats['quality_grades_assigned'] += 1
        
        return assessment
    
    def _assess_property_quality(self, material_name: str, prop_name: str, prop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality for a single property"""
        
        assessment = {
            'property': prop_name,
            'quality_score': 0.0,
            'completeness': 0.0,
            'accuracy': 0.0,
            'consistency': 0.0,
            'validation_status': 'unknown',
            'confidence': prop_data.get('confidence', 0.5),
            'flags': []
        }
        
        # Completeness assessment
        required_fields = ['value', 'unit', 'min', 'max']
        present_fields = sum(1 for field in required_fields if field in prop_data and prop_data[field] is not None)
        assessment['completeness'] = present_fields / len(required_fields)
        
        # Accuracy assessment (based on research validation if available)
        research_validation = self._get_research_validation_for_property(material_name, prop_name)
        if research_validation:
            validation_status = research_validation.get('validation_status', 'unknown')
            if validation_status == 'validated':
                assessment['accuracy'] = 0.9
            elif validation_status == 'disputed':
                assessment['accuracy'] = 0.3
                assessment['flags'].append('disputed_by_research')
            else:
                assessment['accuracy'] = 0.6
        else:
            assessment['accuracy'] = 0.5  # Default if no research validation
        
        # Consistency assessment (based on cross-validation results)
        cross_validation = self._get_cross_validation_for_property(material_name, prop_name)
        if cross_validation:
            is_outlier = cross_validation.get('is_outlier', False)
            severity = cross_validation.get('severity', 'none')
            
            if is_outlier:
                if severity == 'high':
                    assessment['consistency'] = 0.2
                    assessment['flags'].append('high_severity_outlier')
                elif severity == 'medium':
                    assessment['consistency'] = 0.5
                    assessment['flags'].append('medium_severity_outlier')
                else:
                    assessment['consistency'] = 0.7
                    assessment['flags'].append('low_severity_outlier')
            else:
                assessment['consistency'] = 0.9
        else:
            assessment['consistency'] = 0.6  # Default if no cross-validation
        
        # Calculate overall property quality score
        weights = self.qa_config['scoring_weights']
        assessment['quality_score'] = (
            weights['completeness'] * assessment['completeness'] +
            weights['accuracy'] * assessment['accuracy'] +
            weights['consistency'] * assessment['consistency']
        )
        
        return assessment
    
    def _calculate_completeness_score(self, material_name: str, properties: Dict[str, Any]) -> float:
        """Calculate completeness score for a material"""
        
        if not properties:
            return 0.0
        
        # Essential properties for each category
        essential_properties = {
            'metals': ['density', 'meltingPoint', 'thermalConductivity', 'hardness'],
            'plastics': ['density', 'meltingPoint', 'glasstransition', 'hardness'],
            'ceramics': ['density', 'meltingPoint', 'thermalConductivity', 'hardness'],
            'composites': ['density', 'tensileStrength', 'youngsModulus']
        }
        
        # Get material category from discovery results
        category = 'metals'  # Default
        if self.discovery_results:
            for result in self.discovery_results.get('frontmatter_scan', {}).get('discovered_properties', []):
                if result.get('material') == material_name:
                    category = result.get('category', 'metals')
                    break
        
        essential_for_category = essential_properties.get(category, essential_properties['metals'])
        
        # Calculate completion rate
        present_essential = sum(1 for prop in essential_for_category if prop in properties)
        completeness = present_essential / len(essential_for_category)
        
        # Bonus for additional properties
        total_properties = len(properties)
        if total_properties > len(essential_for_category):
            bonus = min(0.2, (total_properties - len(essential_for_category)) * 0.05)
            completeness += bonus
        
        return min(1.0, completeness)
    
    def _calculate_accuracy_score(self, material_name: str, properties: Dict[str, Any]) -> float:
        """Calculate accuracy score based on research validation"""
        
        if not self.research_results or not properties:
            return 0.5
        
        # Get research validation results
        validated_count = 0
        disputed_count = 0
        total_researched = 0
        
        for enrichment in self.research_results.get('enrichments', []):
            if enrichment.get('material') == material_name:
                total_researched += 1
                validation_status = enrichment.get('research_findings', {}).get('validation_status', 'unknown')
                
                if validation_status == 'validated':
                    validated_count += 1
                elif validation_status == 'disputed':
                    disputed_count += 1
        
        if total_researched == 0:
            return 0.5
        
        # Calculate accuracy based on validation results
        validation_rate = validated_count / total_researched
        dispute_rate = disputed_count / total_researched
        
        accuracy = validation_rate - (dispute_rate * 0.5)
        return max(0.0, min(1.0, accuracy))
    
    def _calculate_consistency_score(self, material_name: str, properties: Dict[str, Any]) -> float:
        """Calculate consistency score based on cross-validation results"""
        
        if not self.validation_results or not properties:
            return 0.6
        
        # Find material in validation results
        material_validation = None
        for result in self.validation_results.get('results', []):
            if result.get('material') == material_name:
                material_validation = result
                break
        
        if not material_validation:
            return 0.6
        
        # Calculate consistency based on outliers
        outliers = material_validation.get('outliers', [])
        total_properties = material_validation.get('properties_validated', len(properties))
        
        if total_properties == 0:
            return 0.6
        
        # Calculate penalty based on outlier severity
        penalty = 0.0
        for outlier in outliers:
            severity = outlier.get('severity', 'none')
            if severity == 'high':
                penalty += 0.3
            elif severity == 'medium':
                penalty += 0.2
            elif severity == 'low':
                penalty += 0.1
        
        consistency = 1.0 - (penalty / total_properties)
        return max(0.0, consistency)
    
    def _calculate_research_validation_score(self, material_name: str) -> float:
        """Calculate research validation score"""
        
        if not self.research_results:
            return 0.3
        
        # Find material in research results
        material_research = None
        for result in self.research_results.get('results', []):
            if result.get('material') == material_name:
                material_research = result
                break
        
        if not material_research:
            return 0.3
        
        # Use research confidence as validation score
        research_confidence = material_research.get('research_confidence', 0.5)
        return research_confidence
    
    def _calculate_peer_agreement_score(self, material_name: str) -> float:
        """Calculate peer agreement score"""
        
        if not self.validation_results:
            return 0.5
        
        # Find material in validation results
        material_validation = None
        for result in self.validation_results.get('results', []):
            if result.get('material') == material_name:
                material_validation = result
                break
        
        if not material_validation:
            return 0.5
        
        # Calculate based on peer comparisons
        peer_comparisons = material_validation.get('peer_comparisons', [])
        if not peer_comparisons:
            return 0.4
        
        # Average peer agreement
        agreements = []
        for comparison in peer_comparisons:
            deviation = comparison.get('deviation_from_peers', 0)
            agreement = max(0.0, 1.0 - deviation)
            agreements.append(agreement)
        
        return statistics.mean(agreements) if agreements else 0.5
    
    def _get_research_validation_for_property(self, material_name: str, prop_name: str) -> Optional[Dict[str, Any]]:
        """Get research validation results for a specific property"""
        
        if not self.research_results:
            return None
        
        for enrichment in self.research_results.get('enrichments', []):
            if (enrichment.get('material') == material_name and 
                enrichment.get('property') == prop_name):
                return enrichment.get('research_findings', {})
        
        return None
    
    def _get_cross_validation_for_property(self, material_name: str, prop_name: str) -> Optional[Dict[str, Any]]:
        """Get cross-validation results for a specific property"""
        
        if not self.validation_results:
            return None
        
        # Find material validation results
        for result in self.validation_results.get('results', []):
            if result.get('material') == material_name:
                for outlier in result.get('outliers', []):
                    if outlier.get('property') == prop_name:
                        return outlier
        
        return None
    
    def _assign_quality_grade(self, score: float) -> str:
        """Assign quality grade based on score"""
        
        thresholds = self.qa_config['quality_thresholds']
        
        if score >= thresholds['excellent']:
            return 'excellent'
        elif score >= thresholds['good']:
            return 'good'
        elif score >= thresholds['acceptable']:
            return 'acceptable'
        elif score >= thresholds['poor']:
            return 'poor'
        else:
            return 'critical'
    
    def _assess_critical_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Assess status of critical properties"""
        
        critical_properties = self.qa_config['critical_properties']
        status = {}
        
        for prop_name, requirements in critical_properties.items():
            if prop_name in properties:
                prop_data = properties[prop_name]
                confidence = prop_data.get('confidence', 0.0)
                min_confidence = requirements['min_confidence']
                
                status[prop_name] = {
                    'present': True,
                    'confidence': confidence,
                    'meets_requirements': confidence >= min_confidence,
                    'required_confidence': min_confidence
                }
            else:
                status[prop_name] = {
                    'present': False,
                    'confidence': 0.0,
                    'meets_requirements': False,
                    'required_confidence': requirements['min_confidence']
                }
        
        return status
    
    def _generate_material_recommendations(self, material_qa: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for improving material data quality"""
        
        recommendations = []
        material_name = material_qa['material']
        
        # Low overall score recommendations
        if material_qa['overall_score'] < 0.6:
            recommendations.append({
                'material': material_name,
                'type': 'overall_quality',
                'priority': 'high',
                'description': f"Overall quality score is low ({material_qa['overall_score']:.2f}). Comprehensive review needed.",
                'suggested_actions': [
                    'Verify all property values with authoritative sources',
                    'Complete missing property data',
                    'Resolve any outlier flags'
                ]
            })
        
        # Completeness recommendations
        if material_qa['completeness_score'] < 0.7:
            recommendations.append({
                'material': material_name,
                'type': 'completeness',
                'priority': 'medium',
                'description': f"Material data is incomplete ({material_qa['completeness_score']:.2f} completeness).",
                'suggested_actions': [
                    'Add missing essential properties for this material category',
                    'Ensure all properties have value, unit, min, and max fields',
                    'Consider adding additional relevant properties'
                ]
            })
        
        # Accuracy recommendations
        if material_qa['accuracy_score'] < 0.6:
            recommendations.append({
                'material': material_name,
                'type': 'accuracy',
                'priority': 'high',
                'description': f"Property accuracy is questionable ({material_qa['accuracy_score']:.2f} accuracy).",
                'suggested_actions': [
                    'Research disputed property values with authoritative sources',
                    'Update values that have been flagged as inaccurate',
                    'Increase confidence scores for verified properties'
                ]
            })
        
        # Critical properties recommendations
        critical_status = material_qa['critical_properties_status']
        missing_critical = [prop for prop, status in critical_status.items() if not status['present']]
        low_confidence_critical = [prop for prop, status in critical_status.items() 
                                 if status['present'] and not status['meets_requirements']]
        
        if missing_critical:
            recommendations.append({
                'material': material_name,
                'type': 'critical_properties',
                'priority': 'high',
                'description': f"Missing critical properties: {', '.join(missing_critical)}",
                'suggested_actions': [
                    f'Research and add {prop}' for prop in missing_critical
                ]
            })
        
        if low_confidence_critical:
            recommendations.append({
                'material': material_name,
                'type': 'critical_properties',
                'priority': 'medium',
                'description': f"Low confidence critical properties: {', '.join(low_confidence_critical)}",
                'suggested_actions': [
                    f'Improve confidence for {prop}' for prop in low_confidence_critical
                ]
            })
        
        # Property-specific recommendations
        for prop_name, prop_assessment in material_qa['property_assessments'].items():
            if prop_assessment['quality_score'] < 0.5:
                recommendations.append({
                    'material': material_name,
                    'type': 'property_specific',
                    'priority': 'medium',
                    'property': prop_name,
                    'description': f"Property {prop_name} has low quality score ({prop_assessment['quality_score']:.2f})",
                    'suggested_actions': [
                        f'Review {prop_name} value and sources',
                        f'Address flags: {", ".join(prop_assessment["flags"])}' if prop_assessment['flags'] else 'Verify property data completeness'
                    ]
                })
        
        self.qa_stats['recommendations_generated'] += len(recommendations)
        
        return recommendations
    
    def _generate_qa_report(self, qa_results: List[Dict[str, Any]], material_scores: Dict[str, float], recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive QA report"""
        
        # Overall statistics
        successful_assessments = [r for r in qa_results if r.get('status') != 'error']
        scores = [r['overall_score'] for r in successful_assessments]
        
        # Grade distribution
        grade_distribution = {}
        for result in successful_assessments:
            grade = result['quality_grade']
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        # Category analysis
        category_scores = {}
        for result in successful_assessments:
            category = result['category']
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(result['overall_score'])
        
        category_averages = {
            cat: statistics.mean(scores) for cat, scores in category_scores.items()
        }
        
        # Top performers and issues
        sorted_materials = sorted(material_scores.items(), key=lambda x: x[1], reverse=True)
        top_performers = sorted_materials[:5]
        lowest_performers = sorted_materials[-5:]
        
        # Recommendation analysis
        recommendation_types = {}
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        
        for rec in recommendations:
            rec_type = rec.get('type', 'unknown')
            priority = rec.get('priority', 'medium')
            
            recommendation_types[rec_type] = recommendation_types.get(rec_type, 0) + 1
            priority_counts[priority] += 1
        
        report = {
            'assessment_summary': {
                'materials_assessed': len(successful_assessments),
                'average_score': statistics.mean(scores) if scores else 0,
                'median_score': statistics.median(scores) if scores else 0,
                'score_std_dev': statistics.stdev(scores) if len(scores) > 1 else 0,
                'grade_distribution': grade_distribution
            },
            'category_analysis': {
                'category_averages': category_averages,
                'best_category': max(category_averages.items(), key=lambda x: x[1]) if category_averages else None,
                'worst_category': min(category_averages.items(), key=lambda x: x[1]) if category_averages else None
            },
            'performance_highlights': {
                'top_performers': top_performers,
                'lowest_performers': lowest_performers,
                'excellent_materials': [name for name, result in zip(material_scores.keys(), successful_assessments) 
                                      if result['quality_grade'] == 'excellent'],
                'critical_materials': [name for name, result in zip(material_scores.keys(), successful_assessments) 
                                     if result['quality_grade'] == 'critical']
            },
            'recommendation_analysis': {
                'total_recommendations': len(recommendations),
                'recommendation_types': recommendation_types,
                'priority_distribution': priority_counts,
                'most_common_issues': sorted(recommendation_types.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            'pipeline_effectiveness': {
                'discovery_coverage': len(self.discovery_results) > 0,
                'standardization_applied': len(self.standardization_results) > 0,
                'research_conducted': len(self.research_results) > 0,
                'cross_validation_performed': len(self.validation_results) > 0,
                'overall_pipeline_health': 'healthy' if all([
                    len(self.discovery_results) > 0,
                    len(self.standardization_results) > 0,
                    len(self.research_results) > 0,
                    len(self.validation_results) > 0
                ]) else 'partial'
            }
        }
        
        self.qa_stats['final_reports_created'] += 1
        
        return report
    
    def _generate_qa_summary(self, qa_results: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate QA summary statistics"""
        
        successful_results = [r for r in qa_results if r.get('status') != 'error']
        failed_results = [r for r in qa_results if r.get('status') == 'error']
        
        if not successful_results:
            return {
                'materials_assessed': 0,
                'average_quality_score': 0,
                'quality_distribution': {},
                'total_recommendations': len(recommendations),
                'assessment_success_rate': 0
            }
        
        scores = [r['overall_score'] for r in successful_results]
        grades = [r['quality_grade'] for r in successful_results]
        
        grade_counts = {}
        for grade in grades:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        return {
            'materials_assessed': len(qa_results),
            'successful_assessments': len(successful_results),
            'failed_assessments': len(failed_results),
            'average_quality_score': round(statistics.mean(scores), 3),
            'median_quality_score': round(statistics.median(scores), 3),
            'quality_distribution': grade_counts,
            'total_recommendations': len(recommendations),
            'high_priority_recommendations': len([r for r in recommendations if r.get('priority') == 'high']),
            'assessment_success_rate': len(successful_results) / len(qa_results) if qa_results else 0,
            'properties_with_excellent_quality': sum(1 for r in successful_results if r['overall_score'] >= 0.9),
            'materials_needing_attention': len([r for r in successful_results if r['overall_score'] < 0.6])
        }

def main():
    """Test the quality assurance functionality"""
    
    qa_processor = PropertyQualityAssurance()
    
    # Run quality assurance
    results = qa_processor.perform_quality_assurance()
    
    # Save results
    results_dir = Path("pipeline_results")
    results_dir.mkdir(exist_ok=True)
    
    with open(results_dir / "stage5_quality_assurance_results.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("🎯 QUALITY ASSURANCE STAGE COMPLETE")
    print("="*60)
    print(f"Materials assessed: {results['summary']['materials_assessed']}")
    print(f"Average quality score: {results['summary']['average_quality_score']:.3f}")
    print(f"Total recommendations: {results['summary']['total_recommendations']}")
    print(f"High priority issues: {results['summary']['high_priority_recommendations']}")
    
    print("\nQuality distribution:")
    for grade, count in results['summary']['quality_distribution'].items():
        print(f"  🏆 {grade}: {count}")
    
    if results['summary']['materials_needing_attention'] > 0:
        print(f"\n⚠️  {results['summary']['materials_needing_attention']} materials need attention")

if __name__ == "__main__":
    main()