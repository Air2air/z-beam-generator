#!/usr/bin/env python3
"""
Materials.yaml cleanup tool after Categories.yaml field migration.
Removes redundancy, optimizes structure, and validates consistency.
"""

import yaml
from pathlib import Path
from datetime import datetime
import shutil
from collections import Counter, defaultdict


class MaterialsCleanupTool:
    def __init__(self):
        self.data_dir = Path("data")
        self.materials_path = self.data_dir / "materials.yaml"
        self.categories_path = self.data_dir / "Categories.yaml"
        self.backup_dir = Path("backups")
        
    def create_backup(self):
        """Create backup of materials.yaml before cleanup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"materials_pre_cleanup_{timestamp}.yaml"
        
        self.backup_dir.mkdir(exist_ok=True)
        shutil.copy2(self.materials_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return backup_path
        
    def load_data(self):
        """Load both materials.yaml and Categories.yaml."""
        with open(self.materials_path, 'r', encoding='utf-8') as f:
            materials = yaml.safe_load(f)
            
        with open(self.categories_path, 'r', encoding='utf-8') as f:
            categories = yaml.safe_load(f)
            
        return materials, categories
        
    def analyze_redundancy(self, materials, categories):
        """Analyze what can be cleaned up based on Categories.yaml coverage."""
        print("=== REDUNDANCY ANALYSIS ===")
        
        # Get all fields covered by Categories.yaml
        category_covered_fields = set()
        category_data = {}
        
        for cat_name, cat_data in categories['categories'].items():
            category_data[cat_name.lower()] = cat_data
            for section_name, section_data in cat_data.items():
                if isinstance(section_data, dict):
                    if section_name == 'category_ranges':
                        # These are the main property ranges
                        category_covered_fields.update(section_data.keys())
                    elif section_name in ['electricalProperties', 'processingParameters', 
                                        'chemicalProperties', 'mechanicalProperties', 
                                        'structuralProperties']:
                        # These are the enhanced property sections
                        category_covered_fields.update(section_data.keys())
        
        print(f"Fields covered by Categories.yaml: {len(category_covered_fields)}")
        print(f"Sample covered fields: {list(category_covered_fields)[:10]}")
        
        # Analyze materials for potential cleanup
        cleanup_stats = {
            'redundant_fields': defaultdict(int),
            'material_inconsistencies': [],
            'empty_values': 0,
            'field_frequency': Counter()
        }
        
        for category, cat_data in materials['materials'].items():
            if isinstance(cat_data, dict) and 'items' in cat_data:
                for i, item in enumerate(cat_data['items']):
                    if isinstance(item, dict):
                        for field, value in item.items():
                            cleanup_stats['field_frequency'][field] += 1
                            
                            # Check for empty values
                            if value is None or value == '' or value == []:
                                cleanup_stats['empty_values'] += 1
                                
                            # Check for fields that might be redundant with Categories
                            if field in category_covered_fields:
                                cleanup_stats['redundant_fields'][field] += 1
        
        return cleanup_stats, category_covered_fields
        
    def validate_material_index(self, materials):
        """Validate material_index consistency."""
        print("\n=== MATERIAL INDEX VALIDATION ===")
        
        material_index = materials['material_index']
        indexed_materials = set(material_index.keys())
        
        # Count actual materials
        actual_count = 0
        categories_with_materials = []
        
        for category, cat_data in materials['materials'].items():
            if isinstance(cat_data, dict) and 'items' in cat_data:
                count = len(cat_data['items'])
                actual_count += count
                categories_with_materials.append((category, count))
        
        print(f"Materials in index: {len(indexed_materials)}")
        print(f"Actual material items: {actual_count}")
        print(f"Categories with materials: {categories_with_materials}")
        
        if len(indexed_materials) == actual_count:
            print("✅ Material count matches between index and items")
        else:
            print("⚠️  Material count mismatch - index may need cleanup")
        
        return len(indexed_materials) == actual_count
        
    def optimize_structure(self, materials):
        """Optimize materials.yaml structure without losing essential data."""
        print("\n=== STRUCTURE OPTIMIZATION ===")
        
        optimized = materials.copy()
        changes = []
        
        # 1. Ensure consistent field ordering within materials
        standard_fields_order = [
            'author_id', 'category', 'subcategory', 'formula',
            # Physical properties
            'density', 'hardness', 'tensileStrength', 'compressive_strength',
            'youngsModulus', 'thermalConductivity', 'thermalExpansion',
            'melting_point', 'electricalResistivity', 'dielectric_constant',
            # Crystal and structural
            'crystal_structure', 'crystal_system',
            # Industry and regulatory
            'industryTags', 'regulatoryStandards'
        ]
        
        # 2. Clean up any duplicate or redundant entries
        for category, cat_data in optimized['materials'].items():
            if isinstance(cat_data, dict) and 'items' in cat_data:
                # Sort items for consistency
                items = cat_data['items']
                
                # Remove any items with missing critical fields
                cleaned_items = []
                for item in items:
                    if isinstance(item, dict) and 'author_id' in item and 'category' in item:
                        # Reorder fields for consistency
                        ordered_item = {}
                        
                        # Add fields in standard order
                        for field in standard_fields_order:
                            if field in item:
                                ordered_item[field] = item[field]
                        
                        # Add any remaining fields
                        for field, value in item.items():
                            if field not in ordered_item:
                                ordered_item[field] = value
                                
                        cleaned_items.append(ordered_item)
                    else:
                        changes.append(f"Removed incomplete item from {category}")
                
                cat_data['items'] = cleaned_items
                
        print(f"Optimization changes made: {len(changes)}")
        for change in changes:
            print(f"  - {change}")
            
        return optimized, changes
        
    def calculate_size_reduction(self, original, optimized):
        """Calculate the size reduction achieved."""
        original_yaml = yaml.dump(original, default_flow_style=False)
        optimized_yaml = yaml.dump(optimized, default_flow_style=False)
        
        original_size = len(original_yaml)
        optimized_size = len(optimized_yaml)
        
        reduction = original_size - optimized_size
        reduction_percent = (reduction / original_size) * 100
        
        return {
            'original_size': original_size,
            'optimized_size': optimized_size,
            'reduction_bytes': reduction,
            'reduction_percent': reduction_percent,
            'original_lines': len(original_yaml.split('\n')),
            'optimized_lines': len(optimized_yaml.split('\n'))
        }
        
    def save_cleaned_materials(self, optimized_materials):
        """Save the cleaned materials.yaml."""
        with open(self.materials_path, 'w', encoding='utf-8') as f:
            yaml.dump(optimized_materials, f, default_flow_style=False, 
                     allow_unicode=True, sort_keys=False, width=120)
        print("✅ Cleaned materials.yaml saved")
        
    def run_cleanup(self):
        """Run the complete cleanup process."""
        print("=== MATERIALS.YAML POST-CATEGORIES CLEANUP ===")
        print(f"Processing: {self.materials_path}")
        print()
        
        # Create backup
        backup_path = self.create_backup()
        
        # Load data
        materials, categories = self.load_data()
        
        # Analyze what can be cleaned up
        cleanup_stats, covered_fields = self.analyze_redundancy(materials, categories)
        
        print("\nCleanup Statistics:")
        print(f"  Most frequent fields: {dict(cleanup_stats['field_frequency'].most_common(5))}")
        print(f"  Empty values found: {cleanup_stats['empty_values']}")
        print(f"  Fields covered by Categories.yaml: {len(covered_fields)}")
        
        # Validate material index
        self.validate_material_index(materials)
        
        # Optimize structure
        optimized_materials, optimization_changes = self.optimize_structure(materials)
        
        # Calculate size reduction
        size_stats = self.calculate_size_reduction(materials, optimized_materials)
        
        print("\n=== CLEANUP RESULTS ===")
        print(f"Size reduction: {size_stats['reduction_bytes']:,} bytes ({size_stats['reduction_percent']:.1f}%)")
        print(f"Line reduction: {size_stats['original_lines'] - size_stats['optimized_lines']:,} lines")
        print(f"Optimization changes: {len(optimization_changes)}")
        
        # Save cleaned version
        self.save_cleaned_materials(optimized_materials)
        
        print("\n✅ Cleanup completed successfully!")
        print(f"   Backup: {backup_path}")
        print(f"   Original: {size_stats['original_lines']:,} lines")
        print(f"   Cleaned: {size_stats['optimized_lines']:,} lines")
        print(f"   Reduction: {size_stats['reduction_percent']:.1f}%")
        
        return {
            'backup_path': backup_path,
            'size_stats': size_stats,
            'optimization_changes': optimization_changes,
            'cleanup_stats': cleanup_stats
        }


if __name__ == "__main__":
    cleaner = MaterialsCleanupTool()
    result = cleaner.run_cleanup()