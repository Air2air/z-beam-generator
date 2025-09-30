#!/usr/bin/env python3
"""
Frontmatter Optimization Plan
Based on analysis results, implement organization and redundancy removal strategies.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.insert(0, '/Users/todddunning/Desktop/Z-Beam/z-beam-generator')

class FrontmatterOptimizer:
    """Implements frontmatter optimization strategies."""
    
    def __init__(self):
        self.optimization_strategies = {
            "redundancy_removal": self._remove_redundancy,
            "property_templating": self._implement_property_templates,
            "component_consolidation": self._consolidate_components,
            "metadata_separation": self._separate_metadata,
            "size_optimization": self._optimize_size
        }
    
    def optimize_frontmatter_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all optimization strategies to frontmatter data."""
        
        print("🔧 APPLYING FRONTMATTER OPTIMIZATIONS")
        print("=" * 50)
        
        optimized_data = data.copy()
        optimization_results = {}
        
        for strategy_name, strategy_func in self.optimization_strategies.items():
            print(f"\\n🎯 Applying: {strategy_name}")
            try:
                optimized_data, result = strategy_func(optimized_data)
                optimization_results[strategy_name] = result
                print(f"   ✅ {result['message']}")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                optimization_results[strategy_name] = {"status": "failed", "error": str(e)}
        
        return optimized_data, optimization_results
    
    def _remove_redundancy(self, data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Remove redundant data patterns."""
        optimized = data.copy()
        changes = []
        
        # Remove name/subcategory redundancy
        if optimized.get('name') == optimized.get('subcategory'):
            optimized.pop('subcategory', None)
            changes.append("Removed redundant subcategory (identical to name)")
        
        # Consolidate duplicate material properties
        if 'materialProperties' in optimized:
            props = optimized['materialProperties']
            
            # Remove properties with null/empty values
            empty_props = [k for k, v in props.items() if not v or (isinstance(v, dict) and not v.get('value'))]
            for prop in empty_props:
                props.pop(prop, None)
                changes.append(f"Removed empty property: {prop}")
        
        # Remove duplicate generation metadata
        if 'componentOutputs' in optimized:
            for comp_name, comp_data in optimized['componentOutputs'].items():
                if 'generation' in comp_data:
                    gen_meta = comp_data['generation']
                    # Keep only essential generation info
                    essential_keys = ['method', 'timestamp', 'bypass']
                    filtered_gen = {k: v for k, v in gen_meta.items() if k in essential_keys}
                    comp_data['generation'] = filtered_gen
                    changes.append(f"Simplified {comp_name} generation metadata")
        
        return optimized, {
            "status": "success",
            "message": f"Removed {len(changes)} redundancy issues",
            "changes": changes
        }
    
    def _implement_property_templates(self, data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Implement property templates for common material categories."""
        optimized = data.copy()
        
        category = optimized.get('category', '').lower()
        
        # Define essential properties by category
        essential_properties = {
            'metal': ['density', 'meltingPoint', 'thermalConductivity', 'hardness', 'ablationThreshold'],
            'glass': ['density', 'refractiveIndex', 'hardness', 'thermalExpansion', 'absorptionCoefficient'],
            'polymer': ['density', 'glassTempo', 'thermalStability', 'laserAbsorption'],
            'ceramic': ['density', 'hardness', 'thermalConductivity', 'thermalExpansion'],
            'wood': ['density', 'moistureContent', 'laserAbsorption', 'thermalDecomposition']
        }
        
        if category in essential_properties and 'materialProperties' in optimized:
            essential_props = essential_properties[category]
            current_props = optimized['materialProperties']
            
            # Create template-based structure
            template_props = {}
            non_essential_props = {}
            
            for prop_name, prop_data in current_props.items():
                if prop_name in essential_props:
                    template_props[prop_name] = prop_data
                else:
                    non_essential_props[prop_name] = prop_data
            
            # Restructure with template priority
            optimized['materialProperties'] = {
                **template_props,  # Essential properties first
                **non_essential_props  # Additional properties after
            }
            
            return optimized, {
                "status": "success",
                "message": f"Applied {category} template - {len(template_props)} essential properties prioritized",
                "template_applied": category,
                "essential_count": len(template_props)
            }
        
        return optimized, {
            "status": "success", 
            "message": "No template applied - category not recognized or no properties found",
            "template_applied": None
        }
    
    def _consolidate_components(self, data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Consolidate component outputs for better organization."""
        optimized = data.copy()
        
        if 'componentOutputs' not in optimized:
            return optimized, {"status": "success", "message": "No components to consolidate"}
        
        components = optimized['componentOutputs']
        consolidation_changes = []
        
        # Group related components
        consolidated = {
            "content": {},  # Tags, Caption
            "metadata": {},  # JSON-LD, Metatags  
            "generation": {}  # Generation metadata
        }
        
        # Categorize components
        for comp_name, comp_data in components.items():
            comp_copy = comp_data.copy()
            
            # Extract and consolidate generation metadata
            if 'generation' in comp_copy:
                consolidated["generation"][comp_name] = comp_copy.pop('generation')
            
            # Categorize by type
            if comp_name in ['tags', 'caption']:
                consolidated["content"][comp_name] = comp_copy
            elif comp_name in ['jsonld', 'metatags']:
                consolidated["metadata"][comp_name] = comp_copy
            else:
                # Unknown component type
                consolidated["content"][comp_name] = comp_copy
            
            consolidation_changes.append(f"Categorized {comp_name}")
        
        # Apply consolidation
        optimized['componentOutputs'] = consolidated
        
        return optimized, {
            "status": "success",
            "message": f"Consolidated {len(components)} components into 3 categories",
            "changes": consolidation_changes,
            "categories": list(consolidated.keys())
        }
    
    def _separate_metadata(self, data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Separate orchestration metadata from main content."""
        optimized = data.copy()
        
        # Move orchestration to separate metadata section
        metadata_section = {}
        
        if 'orchestration' in optimized:
            metadata_section['orchestration'] = optimized.pop('orchestration')
        
        # Consolidate all generation metadata
        if 'componentOutputs' in optimized and 'generation' in optimized['componentOutputs']:
            metadata_section['componentGeneration'] = optimized['componentOutputs'].pop('generation', {})
        
        # Add metadata section if we have any metadata
        if metadata_section:
            optimized['_metadata'] = metadata_section
        
        return optimized, {
            "status": "success",
            "message": f"Separated {len(metadata_section)} metadata sections",
            "metadata_sections": list(metadata_section.keys())
        }
    
    def _optimize_size(self, data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Optimize for size by removing verbose elements."""
        optimized = data.copy()
        size_reductions = []
        
        # Simplify property descriptions (keep only essential info)
        if 'materialProperties' in optimized:
            for prop_name, prop_data in optimized['materialProperties'].items():
                if isinstance(prop_data, dict):
                    # Keep only essential fields
                    essential_fields = ['value', 'unit', 'confidence']
                    simplified = {k: v for k, v in prop_data.items() if k in essential_fields}
                    optimized['materialProperties'][prop_name] = simplified
                    size_reductions.append(f"Simplified {prop_name} property")
        
        # Compress verbose application and process lists
        for field in ['applications', 'processes']:
            if field in optimized and isinstance(optimized[field], list):
                if len(optimized[field]) > 5:
                    optimized[field] = optimized[field][:5]  # Keep top 5
                    size_reductions.append(f"Truncated {field} to top 5 items")
        
        # Simplify outcome metrics (remove empty fields)
        if 'outcomeMetrics' in optimized and isinstance(optimized['outcomeMetrics'], list):
            simplified_metrics = []
            for metric in optimized['outcomeMetrics']:
                if isinstance(metric, dict) and metric.get('metric') and metric.get('description'):
                    # Keep only non-empty metrics with essential fields
                    essential_metric = {
                        'metric': metric.get('metric'),
                        'description': metric.get('description'),
                        'typicalRanges': metric.get('typicalRanges', '')
                    }
                    simplified_metrics.append(essential_metric)
            optimized['outcomeMetrics'] = simplified_metrics
            size_reductions.append("Simplified outcome metrics")
        
        return optimized, {
            "status": "success",
            "message": f"Applied {len(size_reductions)} size optimizations",
            "optimizations": size_reductions
        }

def demonstrate_optimization():
    """Demonstrate optimization on our orchestrated files."""
    
    print("🚀 FRONTMATTER OPTIMIZATION DEMONSTRATION")
    print("=" * 60)
    
    optimizer = FrontmatterOptimizer()
    
    # Test on our direct orchestrated file
    input_file = "aluminum-direct-orchestrated.yaml"
    output_file = "aluminum-optimized.yaml"
    
    if Path(input_file).exists():
        print(f"📁 Loading: {input_file}")
        
        with open(input_file, 'r') as f:
            original_data = yaml.safe_load(f)
        
        original_size = len(str(original_data))
        print(f"📏 Original size: {original_size:,} characters")
        
        # Apply optimizations
        optimized_data, results = optimizer.optimize_frontmatter_structure(original_data)
        
        optimized_size = len(str(optimized_data))
        size_reduction = original_size - optimized_size
        size_reduction_pct = (size_reduction / original_size) * 100
        
        print(f"\\n📊 OPTIMIZATION RESULTS:")
        print(f"   📏 Optimized size: {optimized_size:,} characters")
        print(f"   📉 Size reduction: {size_reduction:,} characters ({size_reduction_pct:.1f}%)")
        
        # Save optimized version
        with open(output_file, 'w') as f:
            yaml.dump(optimized_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
        
        print(f"   💾 Saved optimized version: {output_file}")
        
        # Show detailed results
        print(f"\\n📋 OPTIMIZATION BREAKDOWN:")
        for strategy, result in results.items():
            if result.get('status') == 'success':
                print(f"   ✅ {strategy}: {result['message']}")
            else:
                print(f"   ❌ {strategy}: {result.get('error', 'Unknown error')}")
        
        return True
    else:
        print(f"❌ File not found: {input_file}")
        return False

def generate_optimization_guidelines():
    """Generate optimization guidelines for future frontmatter generation."""
    
    guidelines = {
        "organization_principles": [
            "Prioritize essential properties by material category",
            "Group related components (content vs metadata)",
            "Separate generation metadata from content",
            "Use consistent property templates by material type"
        ],
        "redundancy_removal": [
            "Eliminate identical name/subcategory fields",
            "Remove empty or null property values",
            "Consolidate duplicate generation metadata",
            "Avoid repetitive descriptions across materials"
        ],
        "size_optimization": [
            "Keep only essential property fields (value, unit, confidence)",
            "Limit application/process lists to top 5 items",
            "Simplify outcome metrics structure",
            "Use abbreviated generation metadata"
        ],
        "template_structure": {
            "metal": ["density", "meltingPoint", "thermalConductivity", "hardness", "ablationThreshold"],
            "glass": ["density", "refractiveIndex", "hardness", "thermalExpansion", "absorptionCoefficient"],
            "polymer": ["density", "glassTempo", "thermalStability", "laserAbsorption"],
            "ceramic": ["density", "hardness", "thermalConductivity", "thermalExpansion"]
        }
    }
    
    print("\\n📋 OPTIMIZATION GUIDELINES")
    print("=" * 40)
    
    for category, items in guidelines.items():
        if category == "template_structure":
            print(f"\\n🏗️ {category.upper().replace('_', ' ')}:")
            for material_type, properties in items.items():
                print(f"   {material_type}: {', '.join(properties)}")
        else:
            print(f"\\n🎯 {category.upper().replace('_', ' ')}:")
            for item in items:
                print(f"   • {item}")
    
    # Save guidelines to file
    with open("frontmatter_optimization_guidelines.yaml", "w") as f:
        yaml.dump(guidelines, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\\n💾 Guidelines saved to: frontmatter_optimization_guidelines.yaml")

if __name__ == "__main__":
    # Run optimization demonstration
    success = demonstrate_optimization()
    
    if success:
        # Generate optimization guidelines
        generate_optimization_guidelines()
        
        print(f"\\n" + "=" * 60)
        print("🎉 OPTIMIZATION COMPLETE!")
        print("✅ Frontmatter structure optimized")
        print("✅ Redundancy removed")
        print("✅ Organization improved")
        print("✅ Guidelines generated for future use")
    else:
        print("❌ Optimization failed - check file availability")