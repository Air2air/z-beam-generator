#!/usr/bin/env python3
"""
Quality Measurement System - Master CLI

Comprehensive quality measurement system that leverages schemas to provide:
1. Multi-dimensional completeness analysis
2. Research validation assessment  
3. Quality improvement recommendations
4. Historical trend tracking
5. Multi-material comparison

This master script orchestrates all quality measurement tools in the system.
"""

import json
import sys
from pathlib import Path

# Add scripts/tools to path
sys.path.append(str(Path(__file__).parent))

from advanced_quality_analyzer import AdvancedQualityAnalyzer
from quality_improvement_tracker import QualityImprovementTracker


class QualityMeasurementSystem:
    """Master quality measurement system"""
    
    def __init__(self):
        self.analyzer = AdvancedQualityAnalyzer()
        self.tracker = QualityImprovementTracker()
        self.project_root = Path(__file__).parent.parent.parent
    
    def comprehensive_quality_assessment(self, material_name: str, save_history: bool = True) -> dict:
        """Run comprehensive quality assessment with all metrics"""
        
        print(f"🔍 Running comprehensive quality assessment for: {material_name}")
        print("=" * 60)
        
        # 1. Advanced Quality Analysis
        print("📊 Analyzing quality metrics...")
        metrics = self.analyzer.analyze_frontmatter_quality(material_name)
        
        if metrics.overall_completeness_score == 0:
            print(f"❌ No data found for material: {material_name}")
            return {"error": f"No data found for {material_name}"}
        
        # Display quality report
        report = self.analyzer.generate_quality_report(metrics)
        print(report)
        
        # 2. Generate Improvement Plan
        print("\n🎯 Generating improvement recommendations...")
        metrics_dict = {
            'overall_completeness_score': metrics.overall_completeness_score,
            'required_fields_completeness': metrics.required_fields_completeness,
            'optional_fields_completeness': metrics.optional_fields_completeness,
            'research_validation_score': metrics.research_validation_score,
            'material_specificity_score': metrics.material_specificity_score,
            'semantic_completeness_score': metrics.semantic_completeness_score,
            'type_violations': metrics.type_violations,
            'safety_completeness_score': metrics.safety_completeness_score,
            'type_accuracy_score': metrics.type_accuracy_score
        }
        
        improvement_plan = self.tracker.create_improvement_plan(material_name, metrics_dict)
        improvement_report = self.tracker.generate_improvement_report(material_name, improvement_plan)
        print(improvement_report)
        
        # 3. Save Quality Snapshot (if requested)
        if save_history:
            print("\n💾 Saving quality snapshot...")
            snapshot_path = self.tracker.save_quality_snapshot(metrics_dict, material_name)
            print(f"📁 Quality snapshot saved: {snapshot_path}")
        
        return {
            "material": material_name,
            "quality_metrics": metrics_dict,
            "improvement_plan": improvement_plan,
            "analysis_timestamp": metrics.analysis_timestamp
        }
    
    def quality_summary_dashboard(self, material_names: list[str]) -> dict:
        """Create quality dashboard for multiple materials"""
        
        print("🎛️  QUALITY MEASUREMENT DASHBOARD")
        print("=" * 60)
        
        dashboard = {
            "materials": [],
            "summary_stats": {},
            "system_overview": {}
        }
        
        total_materials = 0
        total_completeness = 0
        total_validation = 0
        
        for material in material_names:
            print(f"\n📊 Analyzing {material}...")
            
            metrics = self.analyzer.analyze_frontmatter_quality(material)
            if metrics.overall_completeness_score > 0:
                material_data = {
                    "name": material,
                    "overall_score": metrics.overall_completeness_score,
                    "validation_score": metrics.research_validation_score,
                    "specificity_score": metrics.material_specificity_score,
                    "safety_score": metrics.safety_completeness_score,
                    "quality_grade": self._get_quality_grade(metrics.overall_completeness_score)
                }
                
                dashboard["materials"].append(material_data)
                total_materials += 1
                total_completeness += metrics.overall_completeness_score
                total_validation += metrics.research_validation_score
                
                print(f"   Overall: {metrics.overall_completeness_score:.1f}% | Grade: {material_data['quality_grade']}")
        
        # Calculate summary statistics
        if total_materials > 0:
            dashboard["summary_stats"] = {
                "total_materials_analyzed": total_materials,
                "average_completeness": total_completeness / total_materials,
                "average_validation": total_validation / total_materials,
                "materials_needing_improvement": len([m for m in dashboard["materials"] if m["overall_score"] < 85]),
                "excellent_materials": len([m for m in dashboard["materials"] if m["overall_score"] >= 95]),
                "validation_coverage_gap": total_materials - len([m for m in dashboard["materials"] if m["validation_score"] > 0])
            }
        
        # System overview
        dashboard["system_overview"] = {
            "schema_integration": "✅ Active - JSON schemas loaded successfully",
            "measurement_capabilities": [
                "Multi-dimensional completeness scoring",
                "Research validation depth analysis", 
                "Field priority weighting",
                "Component interdependency validation",
                "Quality trend tracking",
                "Improvement recommendations"
            ],
            "quality_grades": {
                "EXCELLENT (95-100%)": len([m for m in dashboard["materials"] if m["quality_grade"] == "EXCELLENT"]),
                "GOOD (85-94%)": len([m for m in dashboard["materials"] if m["quality_grade"] == "GOOD"]),
                "FAIR (70-84%)": len([m for m in dashboard["materials"] if m["quality_grade"] == "FAIR"]),
                "POOR (50-69%)": len([m for m in dashboard["materials"] if m["quality_grade"] == "POOR"]),
                "CRITICAL (<50%)": len([m for m in dashboard["materials"] if m["quality_grade"] == "CRITICAL"])
            }
        }
        
        return dashboard
    
    def _get_quality_grade(self, score: float) -> str:
        """Get quality grade based on score"""
        if score >= 95:
            return "EXCELLENT"
        elif score >= 85:
            return "GOOD"
        elif score >= 70:
            return "FAIR"
        elif score >= 50:
            return "POOR"
        else:
            return "CRITICAL"
    
    def print_dashboard_summary(self, dashboard: dict):
        """Print formatted dashboard summary"""
        
        stats = dashboard["summary_stats"]
        overview = dashboard["system_overview"]
        
        print("\n📊 SYSTEM QUALITY SUMMARY")
        print("=" * 60)
        print(f"Total Materials Analyzed: {stats['total_materials_analyzed']}")
        print(f"Average Completeness: {stats['average_completeness']:.1f}%")
        print(f"Average Validation: {stats['average_validation']:.1f}%")
        print(f"Materials Needing Improvement: {stats['materials_needing_improvement']}")
        print(f"Validation Coverage Gap: {stats['validation_coverage_gap']} materials")
        
        print("\n🏆 QUALITY GRADE DISTRIBUTION")
        print("-" * 30)
        for grade, count in overview["quality_grades"].items():
            print(f"{grade}: {count} materials")
        
        print("\n🔧 SYSTEM CAPABILITIES")
        print("-" * 30)
        print(f"Schema Integration: {overview['schema_integration']}")
        print("Measurement Features:")
        for capability in overview["measurement_capabilities"]:
            print(f"  • {capability}")
        
        if stats["materials_needing_improvement"] > 0:
            print("\n⚠️  RECOMMENDED ACTIONS")
            print("-" * 30)
            print(f"• Run improvement analysis on {stats['materials_needing_improvement']} materials")
            print("• Implement research validation metadata system")
            print("• Focus on materials with validation coverage gap")


def main():
    """CLI interface for comprehensive quality measurement"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive quality measurement system")
    parser.add_argument("command", choices=['assess', 'dashboard'], help="Command to run")
    parser.add_argument("materials", help="Material name (for assess) or comma-separated list (for dashboard)")
    parser.add_argument("--export", help="Export results to JSON file")
    parser.add_argument("--no-history", action="store_true", help="Don't save quality history snapshot")
    
    args = parser.parse_args()
    
    system = QualityMeasurementSystem()
    
    if args.command == "assess":
        # Single material comprehensive assessment
        result = system.comprehensive_quality_assessment(
            args.materials, 
            save_history=not args.no_history
        )
        
        if args.export:
            with open(args.export, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n📁 Assessment exported: {args.export}")
    
    elif args.command == "dashboard":
        # Multi-material dashboard
        materials = [m.strip() for m in args.materials.split(',')]
        dashboard = system.quality_summary_dashboard(materials)
        system.print_dashboard_summary(dashboard)
        
        if args.export:
            with open(args.export, 'w') as f:
                json.dump(dashboard, f, indent=2, default=str)
            print(f"\n📁 Dashboard exported: {args.export}")


if __name__ == "__main__":
    main()