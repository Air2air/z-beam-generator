#!/usr/bin/env python3
"""
Analyze E/TS Ratio Errors

Investigates the 60 materials with E/TS ratio > 500 to determine if these are:
1. Magnitude errors (GPa vs MPa confusion)
2. Legitimate brittle material ratios (ceramics, stone, glass)
3. Data entry errors requiring manual correction
"""

import yaml
import json
from pathlib import Path
from collections import defaultdict

class RatioErrorAnalyzer:
    """Analyze E/TS ratio anomalies"""
    
    def __init__(self, data_dir: Path = Path(".")):
        self.data_dir = data_dir
        self.frontmatter_dir = data_dir / "content" / "components" / "frontmatter"
        
    def load_validation_report(self) -> dict:
        """Load validation report"""
        report_path = self.data_dir / "validation_report.json"
        with open(report_path) as f:
            return json.load(f)
    
    def load_material(self, material: str) -> dict:
        """Load material frontmatter"""
        file_path = self.frontmatter_dir / f"{material}-laser-cleaning.yaml"
        with open(file_path) as f:
            return yaml.safe_load(f)
    
    def analyze_ratio_error(self, error: dict) -> dict:
        """Analyze a specific ratio error"""
        material = error['material']
        category = error['category']
        E_GPa = error['E_GPa']
        TS_MPa = error['TS_MPa']
        ratio = error['ratio']
        
        # Load full material data
        data = self.load_material(material)
        
        analysis = {
            'material': material,
            'category': category,
            'E_GPa': E_GPa,
            'TS_MPa': TS_MPa,
            'ratio': ratio,
            'likely_cause': None,
            'recommended_fix': None,
            'notes': []
        }
        
        # Brittle materials (ceramics, stone, glass) naturally have high ratios
        if category in ['ceramic', 'stone', 'glass']:
            if ratio < 2000:
                analysis['likely_cause'] = 'legitimate_brittle_material'
                analysis['recommended_fix'] = 'review_but_likely_correct'
                analysis['notes'].append(f"{category} materials naturally have high E/TS ratios (500-2000+)")
            else:
                analysis['likely_cause'] = 'extreme_ratio_needs_verification'
                analysis['recommended_fix'] = 'verify_tensile_strength_value'
                analysis['notes'].append(f"Ratio {ratio:.0f} is extreme even for {category}")
        
        # Check if TS might be in wrong units (GPa instead of MPa)
        if TS_MPa < 1.0:
            analysis['likely_cause'] = 'tensile_strength_unit_error'
            analysis['recommended_fix'] = f'multiply_TS_by_1000 (change {TS_MPa} to {TS_MPa * 1000})'
            analysis['notes'].append(f"TS = {TS_MPa} MPa is suspiciously low, might be {TS_MPa} GPa")
        
        # Check if E might be in wrong units (MPa instead of GPa)
        elif E_GPa > 500 and category not in ['ceramic']:
            analysis['likely_cause'] = 'youngs_modulus_unit_error'
            analysis['recommended_fix'] = f'divide_E_by_1000 (change {E_GPa} to {E_GPa / 1000})'
            analysis['notes'].append(f"E = {E_GPa} GPa is suspiciously high for {category}")
        
        # Metals should have ratio 100-300
        elif category == 'metal' and ratio > 500:
            analysis['likely_cause'] = 'data_inconsistency'
            analysis['recommended_fix'] = 'verify_both_values'
            analysis['notes'].append(f"Metals typically have E/TS ratio 100-300, got {ratio:.0f}")
        
        # Woods and plastics should have lower ratios
        elif category in ['wood', 'plastic'] and ratio > 500:
            analysis['likely_cause'] = 'data_error'
            analysis['recommended_fix'] = 'verify_both_values'
            analysis['notes'].append(f"{category} rarely has E/TS ratio > 500")
        
        # Composites vary widely
        elif category == 'composite':
            analysis['likely_cause'] = 'composite_variability'
            analysis['recommended_fix'] = 'verify_specific_composite_type'
            analysis['notes'].append("Composites vary widely; verify against specific material type")
        
        else:
            analysis['likely_cause'] = 'unknown'
            analysis['recommended_fix'] = 'manual_verification_required'
        
        return analysis
    
    def analyze_all_ratio_errors(self):
        """Analyze all E/TS ratio errors"""
        print("=" * 80)
        print("E/TS RATIO ERROR ANALYZER")
        print("=" * 80)
        print()
        
        # Load validation report
        report = self.load_validation_report()
        ratio_errors = [e for e in report['ERROR'] if e['type'] == 'ratio_too_high']
        
        print(f"Analyzing {len(ratio_errors)} E/TS ratio errors (ratio > 500)\n")
        
        # Analyze each error
        analyses = []
        for error in ratio_errors:
            analysis = self.analyze_ratio_error(error)
            analyses.append(analysis)
        
        # Group by likely cause
        by_cause = defaultdict(list)
        for analysis in analyses:
            by_cause[analysis['likely_cause']].append(analysis)
        
        # Print summary
        print("ANALYSIS SUMMARY")
        print("-" * 80)
        for cause, items in sorted(by_cause.items(), key=lambda x: -len(x[1])):
            print(f"\n{cause}: {len(items)} cases")
            for item in items[:5]:  # Show first 5
                print(f"  {item['material']} ({item['category']}): "
                      f"E={item['E_GPa']:.1f} GPa, TS={item['TS_MPa']:.1f} MPa, ratio={item['ratio']:.0f}")
                print(f"    → {item['recommended_fix']}")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")
        
        # Save detailed analysis
        report_path = self.data_dir / "ratio_analysis_report.json"
        with open(report_path, 'w') as f:
            json.dump(analyses, f, indent=2)
        
        print(f"\n✅ Detailed analysis saved to: {report_path}")
        
        # Recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        
        brittle_count = len(by_cause.get('legitimate_brittle_material', []))
        unit_errors = len(by_cause.get('tensile_strength_unit_error', [])) + len(by_cause.get('youngs_modulus_unit_error', []))
        needs_verification = len(ratio_errors) - brittle_count - unit_errors
        
        print(f"""
1. LEGITIMATE ({brittle_count} cases): Ceramics, stone, glass naturally have high ratios
   → Review but likely correct
   
2. UNIT ERRORS ({unit_errors} cases): Likely GPa/MPa confusion
   → Create automated fix script
   
3. NEEDS MANUAL VERIFICATION ({needs_verification} cases): Inconsistent data
   → Review source data and correct manually
        """)

def main():
    analyzer = RatioErrorAnalyzer()
    analyzer.analyze_all_ratio_errors()

if __name__ == '__main__':
    main()
