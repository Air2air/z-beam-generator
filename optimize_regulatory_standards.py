#!/usr/bin/env python3
"""
Regulatory Standards Optimization Script

Removes universal regulatory standards from Materials.yaml after they've been moved to Categories.yaml.
This eliminates 484+ redundant entries while preserving material-specific standards.

Universal standards being removed (99-100% coverage):
- FDA 21 CFR 1040.10 - Laser Product Performance Standards
- ANSI Z136.1 - Safe Use of Lasers  
- IEC 60825 - Safety of Laser Products
- OSHA 29 CFR 1926.95 - Personal Protective Equipment
"""

import yaml
from pathlib import Path
from collections import Counter
import time


class RegulatoryStandardsOptimizer:
    """Remove universal regulatory standards from Materials.yaml"""
    
    def __init__(self):
        self.materials_file = Path("data/Materials.yaml")
        self.backup_file = Path("data") / f"Materials_backup_before_regulatory_optimization_{int(time.time())}.yaml"
        
        # Universal standards to remove (moved to Categories.yaml)
        self.universal_standards = [
            "FDA 21 CFR 1040.10 - Laser Product Performance Standards",
            "ANSI Z136.1 - Safe Use of Lasers",
            "IEC 60825 - Safety of Laser Products", 
            "OSHA 29 CFR 1926.95 - Personal Protective Equipment"
        ]
    
    def create_backup(self):
        """Create backup before optimization"""
        print(f"📦 Creating backup: {self.backup_file}")
        import shutil
        shutil.copy2(self.materials_file, self.backup_file)
        print("✅ Backup created successfully")
    
    def load_materials_data(self):
        """Load current Materials.yaml data"""
        print("📖 Loading Materials.yaml data")
        with open(self.materials_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        print(f"✅ Loaded data with {len(data.get('materials', {}))} categories")
        return data
    
    def analyze_current_standards(self, data):
        """Analyze current regulatory standards distribution"""
        print("🔍 Analyzing current regulatory standards distribution")
        
        materials = data.get('materials', {})
        all_standards = Counter()
        total_materials = 0
        materials_with_standards = 0
        
        for category, category_data in materials.items():
            items = category_data.get('items', [])
            for item in items:
                total_materials += 1
                
                # Get standards from material_metadata or direct field
                if 'material_metadata' in item:
                    standards = item['material_metadata'].get('regulatoryStandards', [])
                else:
                    standards = item.get('regulatoryStandards', [])
                
                if standards:
                    materials_with_standards += 1
                    for standard in standards:
                        all_standards[standard] += 1
        
        # Analyze universal standards coverage
        universal_coverage = {}
        for standard in self.universal_standards:
            count = all_standards.get(standard, 0)
            coverage = (count / total_materials) * 100 if total_materials > 0 else 0
            universal_coverage[standard] = {
                'count': count,
                'coverage': coverage
            }
        
        analysis = {
            'total_materials': total_materials,
            'materials_with_standards': materials_with_standards,
            'total_unique_standards': len(all_standards),
            'universal_coverage': universal_coverage,
            'all_standards': all_standards
        }
        
        print(f"📊 Analysis Results:")
        print(f"  • Total materials: {total_materials}")
        print(f"  • Materials with standards: {materials_with_standards}")
        print(f"  • Total unique standards: {len(all_standards)}")
        
        print(f"\n🌟 Universal Standards Coverage:")
        for standard, info in universal_coverage.items():
            print(f"  • {standard}: {info['count']}/{total_materials} ({info['coverage']:.1f}%)")
        
        return analysis
    
    def optimize_regulatory_standards(self, data):
        """Remove universal standards from all materials"""
        print("🚀 Removing universal regulatory standards from materials")
        
        materials = data.get('materials', {})
        optimization_stats = {
            'materials_processed': 0,
            'standards_removed': 0,
            'materials_with_remaining_standards': 0,
            'materials_with_no_remaining_standards': 0
        }
        
        for category, category_data in materials.items():
            items = category_data.get('items', [])
            
            for item in items:
                optimization_stats['materials_processed'] += 1
                material_name = item.get('name', 'Unknown')
                
                # Get current standards
                if 'material_metadata' in item:
                    current_standards = item['material_metadata'].get('regulatoryStandards', [])
                    standards_location = 'material_metadata'
                else:
                    current_standards = item.get('regulatoryStandards', [])
                    standards_location = 'direct'
                
                # Filter out universal standards
                remaining_standards = [
                    std for std in current_standards 
                    if std not in self.universal_standards
                ]
                
                # Count removed standards
                removed_count = len(current_standards) - len(remaining_standards)
                optimization_stats['standards_removed'] += removed_count
                
                # Update standards in the appropriate location
                if standards_location == 'material_metadata':
                    if remaining_standards:
                        item['material_metadata']['regulatoryStandards'] = remaining_standards
                        optimization_stats['materials_with_remaining_standards'] += 1
                    else:
                        # Remove the regulatoryStandards field if empty
                        if 'regulatoryStandards' in item['material_metadata']:
                            del item['material_metadata']['regulatoryStandards']
                        optimization_stats['materials_with_no_remaining_standards'] += 1
                else:
                    if remaining_standards:
                        item['regulatoryStandards'] = remaining_standards
                        optimization_stats['materials_with_remaining_standards'] += 1
                    else:
                        # Remove the regulatoryStandards field if empty
                        if 'regulatoryStandards' in item:
                            del item['regulatoryStandards']
                        optimization_stats['materials_with_no_remaining_standards'] += 1
        
        print(f"✅ Optimization completed:")
        print(f"  • Materials processed: {optimization_stats['materials_processed']}")
        print(f"  • Universal standards removed: {optimization_stats['standards_removed']}")
        print(f"  • Materials with remaining specific standards: {optimization_stats['materials_with_remaining_standards']}")
        print(f"  • Materials with no remaining standards: {optimization_stats['materials_with_no_remaining_standards']}")
        
        return optimization_stats
    
    def save_optimized_data(self, data):
        """Save the optimized Materials.yaml"""
        print("💾 Saving optimized Materials.yaml")
        
        with open(self.materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, 
                     allow_unicode=True, sort_keys=False, width=1000, indent=2)
        
        print("✅ Optimized Materials.yaml saved successfully")
    
    def validate_optimization(self, data):
        """Validate the optimization results"""
        print("🔍 Validating optimization results")
        
        materials = data.get('materials', {})
        validation_results = {
            'universal_standards_found': 0,
            'materials_checked': 0,
            'specific_standards_preserved': 0,
            'sample_remaining_standards': []
        }
        
        for category, category_data in materials.items():
            items = category_data.get('items', [])
            
            for item in items:
                validation_results['materials_checked'] += 1
                material_name = item.get('name', 'Unknown')
                
                # Get remaining standards
                if 'material_metadata' in item:
                    standards = item['material_metadata'].get('regulatoryStandards', [])
                else:
                    standards = item.get('regulatoryStandards', [])
                
                # Check for universal standards (should be 0)
                for standard in standards:
                    if standard in self.universal_standards:
                        validation_results['universal_standards_found'] += 1
                    else:
                        validation_results['specific_standards_preserved'] += 1
                
                # Sample remaining standards for report
                if standards and len(validation_results['sample_remaining_standards']) < 10:
                    validation_results['sample_remaining_standards'].extend([
                        f"{material_name}: {std}" for std in standards[:2]
                    ])
        
        print(f"📋 Validation Results:")
        print(f"  • Materials checked: {validation_results['materials_checked']}")
        print(f"  • Universal standards found (should be 0): {validation_results['universal_standards_found']}")
        print(f"  • Material-specific standards preserved: {validation_results['specific_standards_preserved']}")
        
        if validation_results['sample_remaining_standards']:
            print(f"\n📄 Sample of remaining material-specific standards:")
            for sample in validation_results['sample_remaining_standards'][:5]:
                print(f"  • {sample}")
        
        is_valid = validation_results['universal_standards_found'] == 0
        print(f"\n{'✅ VALIDATION PASSED' if is_valid else '❌ VALIDATION FAILED'}")
        
        return validation_results, is_valid
    
    def generate_optimization_report(self, analysis, optimization_stats, validation_results):
        """Generate comprehensive optimization report"""
        report_file = Path("REGULATORY_STANDARDS_OPTIMIZATION_REPORT.md")
        
        redundancy_eliminated = optimization_stats['standards_removed']
        
        report_content = f"""# Regulatory Standards Optimization Report

## 🚀 Optimization Summary

**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Optimization Type**: Universal Regulatory Standards Migration
**Source**: Materials.yaml → Categories.yaml

## 📊 Performance Impact

### Redundancy Elimination
- **Universal Standards Removed**: {redundancy_eliminated} entries
- **Materials Processed**: {optimization_stats['materials_processed']}
- **Categories.yaml Enhanced**: Added 4 universal standards
- **File Size Reduction**: ~{redundancy_eliminated * 50} bytes estimated

### Universal Standards Migrated to Categories.yaml
1. **FDA 21 CFR 1040.10** - Laser Product Performance Standards
2. **ANSI Z136.1** - Safe Use of Lasers
3. **IEC 60825** - Safety of Laser Products  
4. **OSHA 29 CFR 1926.95** - Personal Protective Equipment

### Coverage Analysis (Before Migration)
"""
        
        for standard, info in analysis['universal_coverage'].items():
            report_content += f"- **{standard}**: {info['count']}/{analysis['total_materials']} materials ({info['coverage']:.1f}%)\n"
        
        report_content += f"""
## 🏗️ Structural Changes

### Materials.yaml Optimization
- **Materials with Remaining Specific Standards**: {optimization_stats['materials_with_remaining_standards']}
- **Materials with No Remaining Standards**: {optimization_stats['materials_with_no_remaining_standards']}
- **Material-Specific Standards Preserved**: {validation_results['specific_standards_preserved']}

### Categories.yaml Enhancement
- Added `universal_regulatory_standards` section
- Version updated to 2.4.0
- Single source of truth for universal laser safety standards

## ✅ Validation Results

- **Materials Validated**: {validation_results['materials_checked']}
- **Universal Standards Remaining**: {validation_results['universal_standards_found']} (target: 0)
- **Validation Status**: {'✅ PASSED' if validation_results['universal_standards_found'] == 0 else '❌ FAILED'}

## 📈 Benefits Achieved

### Performance Improvements
- **Lookup Efficiency**: Universal standards now inherited from Categories.yaml
- **Maintenance**: Update universal standards in 1 location instead of 121+
- **Data Consistency**: Single source of truth prevents drift
- **File Size**: Reduced redundancy by {redundancy_eliminated} entries

### Frontmatter Generation Impact
- **Universal standards**: Auto-inherited from Categories.yaml
- **Specific standards**: Material-specific standards preserved
- **Combined approach**: Optimal balance of efficiency and specificity

## 🔄 Integration Requirements

### Frontmatter Generator Updates Needed
The frontmatter generator should be updated to:
1. **Load universal standards** from Categories.yaml
2. **Merge with material-specific standards** from Materials.yaml
3. **Combine both sources** in the final regulatory standards list

### Example Integration Logic
```python
# Load universal standards from Categories.yaml
universal_standards = categories_data.get('universal_regulatory_standards', [])

# Load material-specific standards from Materials.yaml  
specific_standards = material_data.get('regulatoryStandards', [])

# Combine for complete regulatory compliance
all_standards = universal_standards + specific_standards
```

## 🔧 Rollback Instructions

If issues arise, restore from backup:
```bash
cp {self.backup_file} data/Materials.yaml
```

## 📋 Next Steps

1. **Update frontmatter generator** to inherit universal standards from Categories.yaml
2. **Test frontmatter generation** with hybrid regulatory standards approach  
3. **Validate regulatory completeness** in generated content
4. **Monitor performance improvements** from reduced redundancy

This optimization achieves optimal balance: universal standards managed centrally in Categories.yaml while preserving material-specific regulatory requirements in Materials.yaml.
"""
        
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        print(f"📋 Optimization report saved: {report_file}")
    
    def run_complete_optimization(self):
        """Execute complete regulatory standards optimization"""
        print("🚀 Starting Regulatory Standards Optimization")
        print("=" * 60)
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Load and analyze current data
            data = self.load_materials_data()
            analysis = self.analyze_current_standards(data)
            
            # Step 3: Optimize regulatory standards
            optimization_stats = self.optimize_regulatory_standards(data)
            
            # Step 4: Save optimized data
            self.save_optimized_data(data)
            
            # Step 5: Validate optimization
            validation_results, is_valid = self.validate_optimization(data)
            
            # Step 6: Generate report
            self.generate_optimization_report(analysis, optimization_stats, validation_results)
            
            # Success summary
            print("\n" + "=" * 60)
            print("✅ REGULATORY STANDARDS OPTIMIZATION COMPLETED")
            print("=" * 60)
            
            print(f"\n📊 Optimization Results:")
            print(f"  • Universal standards removed: {optimization_stats['standards_removed']} entries")
            print(f"  • Materials optimized: {optimization_stats['materials_processed']}")
            print(f"  • Specific standards preserved: {validation_results['specific_standards_preserved']}")
            print(f"  • Validation status: {'✅ PASSED' if is_valid else '❌ FAILED'}")
            
            print(f"\n📁 Files Updated:")
            print(f"  • Categories.yaml: Added universal_regulatory_standards")
            print(f"  • Materials.yaml: Removed universal standards redundancy")
            
            print(f"\n🔄 Backup Available: {self.backup_file}")
            print(f"📋 Full Report: REGULATORY_STANDARDS_OPTIMIZATION_REPORT.md")
            
            if not is_valid:
                print(f"\n⚠️ WARNING: Validation failed - check results before proceeding")
            
            return is_valid
            
        except Exception as e:
            print(f"\n❌ Optimization failed: {e}")
            print(f"🔄 Restore from backup: cp {self.backup_file} {self.materials_file}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    optimizer = RegulatoryStandardsOptimizer()
    success = optimizer.run_complete_optimization()
    
    if success:
        print("\n🎉 Regulatory standards optimization completed successfully!")
        print("💡 Next: Update frontmatter generator to inherit universal standards from Categories.yaml")
    else:
        print("\n⚠️ Optimization failed - check error messages and restore from backup if needed")