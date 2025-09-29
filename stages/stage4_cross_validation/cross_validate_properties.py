#!/usr/bin/env python3
"""
Stage 4: Cross-Validation
Implements comprehensive cross-validation against multiple sources and peer materials.
"""

import os
import yaml
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics
from datetime import datetime

class PropertyCrossValidator:
    """
    Cross-validates material properties against peer materials,
    category ranges, and statistical distributions to identify outliers.
    """
    
    def __init__(self):
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.categories_file = Path("data/Categories.yaml")
        self.config_file = Path("config/pipeline_config.yaml")
        
        # Load validation configuration
        self.validation_config = self._load_validation_config()
        
        # Material database
        self.materials_database = {}
        self.category_distributions = {}
        
        # Statistics tracking
        self.validation_stats = {
            'materials_validated': 0,
            'properties_cross_checked': 0,
            'outliers_detected': 0,
            'peer_comparisons': 0,
            'statistical_flags': 0,
            'errors': []
        }
    
    def _load_validation_config(self) -> Dict[str, Any]:
        """Load cross-validation configuration"""
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            return config.get('cross_validation', {
                'outlier_detection': {
                    'z_score_threshold': 2.5,
                    'iqr_multiplier': 1.5,
                    'min_samples': 5
                },
                'peer_comparison': {
                    'similarity_threshold': 0.8,
                    'property_weight': {
                        'density': 1.0,
                        'meltingPoint': 0.9,
                        'thermalConductivity': 0.8,
                        'hardness': 0.7
                    }
                },
                'validation_rules': {
                    'max_deviation_from_peers': 0.3,
                    'min_peer_group_size': 3,
                    'confidence_penalty_for_outliers': 0.2
                }
            })
            
        except Exception as e:
            print(f"⚠️  Could not load validation config: {e}")
            return self._get_default_validation_config()
    
    def _get_default_validation_config(self) -> Dict[str, Any]:
        """Default validation configuration"""
        
        return {
            'outlier_detection': {
                'z_score_threshold': 2.5,
                'iqr_multiplier': 1.5,
                'min_samples': 5
            },
            'peer_comparison': {
                'similarity_threshold': 0.8,
                'property_weight': {
                    'density': 1.0,
                    'meltingPoint': 0.9,
                    'thermalConductivity': 0.8,
                    'hardness': 0.7,
                    'youngsModulus': 0.8,
                    'tensileStrength': 0.7
                }
            },
            'validation_rules': {
                'max_deviation_from_peers': 0.3,
                'min_peer_group_size': 3,
                'confidence_penalty_for_outliers': 0.2,
                'category_variance_threshold': 0.5
            }
        }
    
    def cross_validate_properties(self, materials_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive cross-validation of material properties.
        
        Args:
            materials_filter: Optional list of specific materials to process
            
        Returns:
            Cross-validation results with outliers and recommendations
        """
        
        print("🔍 Starting cross-validation process...")
        
        # Build materials database
        self._build_materials_database(materials_filter)
        
        # Calculate category distributions
        self._calculate_category_distributions()
        
        # Perform validation
        validation_results = []
        outliers_detected = []
        
        for material_name, material_data in self.materials_database.items():
            try:
                # Cross-validate material
                material_validation = self._cross_validate_material(material_name, material_data)
                
                validation_results.append(material_validation)
                
                # Collect outliers
                if material_validation.get('outliers'):
                    outliers_detected.extend(material_validation['outliers'])
                
                self.validation_stats['materials_validated'] += 1
                
            except Exception as e:
                error_msg = f"Error validating {material_name}: {e}"
                self.validation_stats['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                
                validation_results.append({
                    'material': material_name,
                    'status': 'error',
                    'error': str(e)
                })
        
        print(f"✅ Cross-validation complete: {self.validation_stats['materials_validated']} materials validated")
        print(f"⚠️  {len(outliers_detected)} outliers detected")
        
        return {
            'results': validation_results,
            'outliers': outliers_detected,
            'statistics': self.validation_stats,
            'category_statistics': self._generate_category_statistics(),
            'summary': self._generate_validation_summary(validation_results, outliers_detected)
        }
    
    def _build_materials_database(self, materials_filter: Optional[List[str]] = None):
        """Build comprehensive materials database for cross-validation"""
        
        print("📊 Building materials database for cross-validation...")
        
        for yaml_file in self.frontmatter_dir.glob("*.yaml"):
            material_name = yaml_file.stem.replace("-laser-cleaning", "")
            
            # Apply materials filter if provided
            if materials_filter and material_name not in materials_filter:
                continue
            
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                # Extract relevant data
                material_record = {
                    'name': material_name,
                    'category': data.get('category', 'unknown').lower(),
                    'properties': data.get('materialProperties', {}),
                    'file_path': str(yaml_file)
                }
                
                # Process numeric properties
                numeric_properties = {}
                for prop_name, prop_data in material_record['properties'].items():
                    if isinstance(prop_data, dict) and 'value' in prop_data:
                        try:
                            numeric_value = float(prop_data['value'])
                            numeric_properties[prop_name] = {
                                'value': numeric_value,
                                'unit': prop_data.get('unit'),
                                'min': float(prop_data.get('min', numeric_value)) if prop_data.get('min') is not None else None,
                                'max': float(prop_data.get('max', numeric_value)) if prop_data.get('max') is not None else None,
                                'confidence': prop_data.get('confidence', 0.5)
                            }
                        except (ValueError, TypeError):
                            continue
                
                material_record['numeric_properties'] = numeric_properties
                self.materials_database[material_name] = material_record
                
            except Exception as e:
                print(f"⚠️  Error loading {material_name}: {e}")
        
        print(f"📊 Loaded {len(self.materials_database)} materials into database")
    
    def _calculate_category_distributions(self):
        """Calculate statistical distributions for each category and property"""
        
        print("📈 Calculating category statistical distributions...")
        
        # Group materials by category
        category_materials = defaultdict(list)
        for material_name, material_data in self.materials_database.items():
            category = material_data['category']
            category_materials[category].append(material_data)
        
        # Calculate distributions for each category
        for category, materials in category_materials.items():
            if len(materials) < 2:  # Need at least 2 materials for statistics
                continue
            
            category_stats = {}
            
            # Get all properties used in this category
            all_properties = set()
            for material in materials:
                all_properties.update(material['numeric_properties'].keys())
            
            # Calculate statistics for each property
            for prop_name in all_properties:
                values = []
                for material in materials:
                    if prop_name in material['numeric_properties']:
                        value = material['numeric_properties'][prop_name]['value']
                        if value is not None:
                            values.append(value)
                
                if len(values) >= 2:
                    category_stats[prop_name] = self._calculate_property_statistics(values)
            
            self.category_distributions[category] = {
                'material_count': len(materials),
                'property_statistics': category_stats
            }
        
        print(f"📈 Calculated distributions for {len(self.category_distributions)} categories")
    
    def _calculate_property_statistics(self, values: List[float]) -> Dict[str, Any]:
        """Calculate comprehensive statistics for a property"""
        
        if not values:
            return {}
        
        values = sorted(values)
        n = len(values)
        
        # Basic statistics
        stats = {
            'count': n,
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if n > 1 else 0,
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values)
        }
        
        # Quartiles and IQR
        if n >= 4:
            q1_idx = n // 4
            q3_idx = 3 * n // 4
            stats['q1'] = values[q1_idx]
            stats['q3'] = values[q3_idx]
            stats['iqr'] = stats['q3'] - stats['q1']
            
            # Outlier bounds
            iqr_multiplier = self.validation_config['outlier_detection']['iqr_multiplier']
            stats['outlier_lower'] = stats['q1'] - iqr_multiplier * stats['iqr']
            stats['outlier_upper'] = stats['q3'] + iqr_multiplier * stats['iqr']
        
        # Coefficient of variation
        if stats['mean'] != 0:
            stats['cv'] = stats['std_dev'] / abs(stats['mean'])
        else:
            stats['cv'] = float('inf')
        
        return stats
    
    def _cross_validate_material(self, material_name: str, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-validate a single material against peers and statistical norms"""
        
        category = material_data['category']
        properties = material_data['numeric_properties']
        
        validation_result = {
            'material': material_name,
            'category': category,
            'properties_validated': len(properties),
            'outliers': [],
            'peer_comparisons': [],
            'statistical_flags': [],
            'overall_confidence': 1.0,
            'status': 'success'
        }
        
        # Find peer materials
        peer_materials = self._find_peer_materials(material_name, material_data)
        
        # Validate each property
        for prop_name, prop_data in properties.items():
            try:
                # Statistical validation
                statistical_validation = self._validate_against_statistics(
                    material_name, category, prop_name, prop_data
                )
                
                # Peer validation
                peer_validation = self._validate_against_peers(
                    material_name, prop_name, prop_data, peer_materials
                )
                
                # Combine validations
                property_validation = self._combine_validations(
                    material_name, prop_name, statistical_validation, peer_validation
                )
                
                # Check for outliers
                if property_validation.get('is_outlier'):
                    validation_result['outliers'].append(property_validation)
                    self.validation_stats['outliers_detected'] += 1
                
                # Track peer comparisons
                if peer_validation.get('peer_count', 0) > 0:
                    validation_result['peer_comparisons'].append(peer_validation)
                    self.validation_stats['peer_comparisons'] += 1
                
                # Track statistical flags
                if statistical_validation.get('flags'):
                    validation_result['statistical_flags'].extend(statistical_validation['flags'])
                    self.validation_stats['statistical_flags'] += len(statistical_validation['flags'])
                
                # Update overall confidence
                confidence_impact = property_validation.get('confidence_impact', 0)
                validation_result['overall_confidence'] *= (1.0 + confidence_impact)
                
                self.validation_stats['properties_cross_checked'] += 1
                
            except Exception as e:
                error_msg = f"Error validating {prop_name} for {material_name}: {e}"
                self.validation_stats['errors'].append(error_msg)
        
        # Clamp overall confidence
        validation_result['overall_confidence'] = max(0.0, min(1.0, validation_result['overall_confidence']))
        
        return validation_result
    
    def _find_peer_materials(self, material_name: str, material_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find peer materials for comparison"""
        
        category = material_data['category']
        properties = material_data['numeric_properties']
        
        peer_materials = []
        
        # Find materials in the same category
        for other_name, other_data in self.materials_database.items():
            if other_name == material_name:
                continue
            
            if other_data['category'] == category:
                # Calculate similarity score
                similarity = self._calculate_material_similarity(material_data, other_data)
                
                if similarity >= self.validation_config['peer_comparison']['similarity_threshold']:
                    peer_materials.append({
                        'name': other_name,
                        'data': other_data,
                        'similarity': similarity
                    })
        
        # Sort by similarity
        peer_materials.sort(key=lambda x: x['similarity'], reverse=True)
        
        return peer_materials
    
    def _calculate_material_similarity(self, material1: Dict[str, Any], material2: Dict[str, Any]) -> float:
        """Calculate similarity score between two materials"""
        
        props1 = material1['numeric_properties']
        props2 = material2['numeric_properties']
        
        # Find common properties
        common_props = set(props1.keys()) & set(props2.keys())
        
        if not common_props:
            return 0.0
        
        # Calculate weighted similarity
        total_weight = 0
        weighted_similarity = 0
        
        property_weights = self.validation_config['peer_comparison']['property_weight']
        
        for prop_name in common_props:
            weight = property_weights.get(prop_name, 0.5)
            total_weight += weight
            
            val1 = props1[prop_name]['value']
            val2 = props2[prop_name]['value']
            
            if val1 == 0 and val2 == 0:
                prop_similarity = 1.0
            elif val1 == 0 or val2 == 0:
                prop_similarity = 0.0
            else:
                # Calculate relative difference
                relative_diff = abs(val1 - val2) / max(abs(val1), abs(val2))
                prop_similarity = max(0.0, 1.0 - relative_diff)
            
            weighted_similarity += weight * prop_similarity
        
        return weighted_similarity / total_weight if total_weight > 0 else 0.0
    
    def _validate_against_statistics(self, material_name: str, category: str, prop_name: str, prop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate property against category statistical distributions"""
        
        validation = {
            'material': material_name,
            'property': prop_name,
            'validation_type': 'statistical',
            'flags': [],
            'z_score': None,
            'percentile': None,
            'is_outlier': False
        }
        
        # Get category statistics
        if category not in self.category_distributions:
            validation['flags'].append('no_category_distribution')
            return validation
        
        category_stats = self.category_distributions[category]['property_statistics']
        if prop_name not in category_stats:
            validation['flags'].append('no_property_distribution')
            return validation
        
        prop_stats = category_stats[prop_name]
        value = prop_data['value']
        
        # Calculate z-score
        if prop_stats['std_dev'] > 0:
            z_score = (value - prop_stats['mean']) / prop_stats['std_dev']
            validation['z_score'] = round(z_score, 3)
            
            # Check z-score threshold
            z_threshold = self.validation_config['outlier_detection']['z_score_threshold']
            if abs(z_score) > z_threshold:
                validation['flags'].append(f'z_score_outlier_{abs(z_score):.1f}')
                validation['is_outlier'] = True
        
        # Calculate percentile
        if prop_stats['count'] >= 5:
            values_below = sum(1 for v in self._get_category_property_values(category, prop_name) if v < value)
            percentile = values_below / prop_stats['count'] * 100
            validation['percentile'] = round(percentile, 1)
            
            # Check extreme percentiles
            if percentile <= 5 or percentile >= 95:
                validation['flags'].append(f'extreme_percentile_{percentile:.0f}')
                validation['is_outlier'] = True
        
        # IQR-based outlier detection
        if 'outlier_lower' in prop_stats and 'outlier_upper' in prop_stats:
            if value < prop_stats['outlier_lower'] or value > prop_stats['outlier_upper']:
                validation['flags'].append('iqr_outlier')
                validation['is_outlier'] = True
        
        return validation
    
    def _validate_against_peers(self, material_name: str, prop_name: str, prop_data: Dict[str, Any], peer_materials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate property against peer materials"""
        
        validation = {
            'material': material_name,
            'property': prop_name,
            'validation_type': 'peer_comparison',
            'peer_count': 0,
            'peer_values': [],
            'deviation_from_peers': None,
            'flags': []
        }
        
        # Collect peer values for this property
        peer_values = []
        for peer in peer_materials:
            peer_props = peer['data']['numeric_properties']
            if prop_name in peer_props:
                peer_values.append(peer_props[prop_name]['value'])
        
        validation['peer_count'] = len(peer_values)
        validation['peer_values'] = peer_values
        
        if len(peer_values) < self.validation_config['validation_rules']['min_peer_group_size']:
            validation['flags'].append('insufficient_peer_data')
            return validation
        
        # Calculate deviation from peer average
        peer_mean = statistics.mean(peer_values)
        value = prop_data['value']
        
        if peer_mean != 0:
            deviation = abs(value - peer_mean) / abs(peer_mean)
            validation['deviation_from_peers'] = round(deviation, 3)
            
            max_deviation = self.validation_config['validation_rules']['max_deviation_from_peers']
            if deviation > max_deviation:
                validation['flags'].append(f'high_peer_deviation_{deviation:.2f}')
        
        return validation
    
    def _combine_validations(self, material_name: str, prop_name: str, statistical: Dict[str, Any], peer: Dict[str, Any]) -> Dict[str, Any]:
        """Combine statistical and peer validations"""
        
        combined = {
            'material': material_name,
            'property': prop_name,
            'is_outlier': False,
            'confidence_impact': 0.0,
            'flags': [],
            'severity': 'none'
        }
        
        # Combine flags
        combined['flags'].extend(statistical.get('flags', []))
        combined['flags'].extend(peer.get('flags', []))
        
        # Determine if outlier
        statistical_outlier = statistical.get('is_outlier', False)
        peer_deviation = peer.get('deviation_from_peers', 0)
        max_peer_deviation = self.validation_config['validation_rules']['max_deviation_from_peers']
        
        if statistical_outlier and peer_deviation > max_peer_deviation:
            combined['is_outlier'] = True
            combined['severity'] = 'high'
            combined['confidence_impact'] = -self.validation_config['validation_rules']['confidence_penalty_for_outliers']
        elif statistical_outlier or peer_deviation > max_peer_deviation:
            combined['is_outlier'] = True
            combined['severity'] = 'medium'
            combined['confidence_impact'] = -self.validation_config['validation_rules']['confidence_penalty_for_outliers'] * 0.5
        elif combined['flags']:
            combined['severity'] = 'low'
            combined['confidence_impact'] = -0.05
        
        # Add validation details
        combined['statistical_validation'] = statistical
        combined['peer_validation'] = peer
        
        return combined
    
    def _get_category_property_values(self, category: str, prop_name: str) -> List[float]:
        """Get all values for a property within a category"""
        
        values = []
        for material_name, material_data in self.materials_database.items():
            if material_data['category'] == category:
                if prop_name in material_data['numeric_properties']:
                    value = material_data['numeric_properties'][prop_name]['value']
                    if value is not None:
                        values.append(value)
        
        return values
    
    def _generate_category_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive category statistics"""
        
        category_stats = {}
        
        for category, distribution in self.category_distributions.items():
            property_stats = distribution['property_statistics']
            
            # Calculate category-level metrics
            property_count = len(property_stats)
            total_variance = sum(stats.get('cv', 0) for stats in property_stats.values())
            avg_variance = total_variance / property_count if property_count > 0 else 0
            
            category_stats[category] = {
                'material_count': distribution['material_count'],
                'property_count': property_count,
                'average_variance': round(avg_variance, 3),
                'high_variance_properties': [
                    prop for prop, stats in property_stats.items() 
                    if stats.get('cv', 0) > 0.5
                ],
                'properties': list(property_stats.keys())
            }
        
        return category_stats
    
    def _generate_validation_summary(self, results: List[Dict[str, Any]], outliers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive validation summary"""
        
        successful_validations = [r for r in results if r.get('status') == 'success']
        failed_validations = [r for r in results if r.get('status') == 'error']
        
        # Analyze outlier severity
        severity_counts = {'high': 0, 'medium': 0, 'low': 0, 'none': 0}
        for outlier in outliers:
            severity = outlier.get('severity', 'none')
            severity_counts[severity] += 1
        
        # Calculate validation rates
        total_properties = sum(r.get('properties_validated', 0) for r in successful_validations)
        outlier_rate = len(outliers) / total_properties if total_properties > 0 else 0
        
        # Most common flags
        all_flags = []
        for outlier in outliers:
            all_flags.extend(outlier.get('flags', []))
        
        flag_counts = {}
        for flag in all_flags:
            flag_counts[flag] = flag_counts.get(flag, 0) + 1
        
        top_flags = sorted(flag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'materials_validated': len(results),
            'successful_validations': len(successful_validations),
            'failed_validations': len(failed_validations),
            'total_properties_checked': total_properties,
            'outliers_detected': len(outliers),
            'outlier_rate': round(outlier_rate, 3),
            'severity_distribution': severity_counts,
            'most_common_flags': top_flags,
            'validation_efficiency': self.validation_stats['properties_cross_checked'] / max(1, self.validation_stats['materials_validated']),
            'categories_analyzed': len(self.category_distributions)
        }

def main():
    """Test the cross-validation functionality"""
    
    validator = PropertyCrossValidator()
    
    # Run cross-validation
    results = validator.cross_validate_properties()
    
    # Save results
    results_dir = Path("pipeline_results")
    results_dir.mkdir(exist_ok=True)
    
    with open(results_dir / "stage4_cross_validation_results.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("🔍 CROSS-VALIDATION STAGE COMPLETE")
    print("="*60)
    print(f"Materials validated: {results['summary']['materials_validated']}")
    print(f"Properties checked: {results['summary']['total_properties_checked']}")
    print(f"Outliers detected: {results['summary']['outliers_detected']}")
    print(f"Outlier rate: {results['summary']['outlier_rate']:.1%}")
    
    print("\nSeverity distribution:")
    for severity, count in results['summary']['severity_distribution'].items():
        if count > 0:
            print(f"  🚨 {severity}: {count}")
    
    print("\nMost common validation flags:")
    for flag, count in results['summary']['most_common_flags'][:5]:
        print(f"  ⚠️  {flag}: {count}")

if __name__ == "__main__":
    main()