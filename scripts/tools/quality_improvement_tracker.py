#!/usr/bin/env python3
"""
Quality Improvement Tracker

Tracks quality metrics over time and provides improvement recommendations:
1. Historical trend analysis
2. Quality improvement suggestions
3. Automated quality enhancement pipeline
4. Multi-material comparison dashboard
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class QualityImprovement:
    """Quality improvement recommendation"""
    
    category: str  # validation, completeness, specificity, etc
    priority: str  # HIGH, MEDIUM, LOW
    description: str
    current_score: float
    target_score: float
    improvement_steps: list[str]
    estimated_effort: str  # LOW, MEDIUM, HIGH
    expected_impact: float  # 0-100% score improvement


class QualityImprovementTracker:
    """Track and improve quality metrics over time"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.quality_history_dir = self.project_root / "logs" / "quality_history"
        self.quality_history_dir.mkdir(parents=True, exist_ok=True)
    
    def save_quality_snapshot(self, metrics: Dict[str, Any], material_name: str) -> str:
        """Save quality metrics snapshot with timestamp"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{material_name}_quality_{timestamp}.json"
        filepath = self.quality_history_dir / filename
        
        # Add metadata
        snapshot = {
            "material": material_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        return str(filepath)
    
    def load_quality_history(self, material_name: str) -> list[Dict]:
        """Load all quality snapshots for a material"""
        
        history = []
        pattern = f"{material_name}_quality_*.json"
        
        for filepath in self.quality_history_dir.glob(pattern):
            with open(filepath, 'r') as f:
                snapshot = json.load(f)
                history.append(snapshot)
        
        # Sort by timestamp
        history.sort(key=lambda x: x.get('timestamp', ''))
        return history
    
    def analyze_quality_trends(self, material_name: str) -> Dict[str, Any]:
        """Analyze quality trends over time"""
        
        history = self.load_quality_history(material_name)
        
        if len(history) < 2:
            return {"error": "Need at least 2 snapshots to analyze trends"}
        
        # Extract key metrics over time
        timestamps = []
        overall_scores = []
        validation_scores = []
        completeness_scores = []
        specificity_scores = []
        
        for snapshot in history:
            metrics = snapshot['metrics']
            timestamps.append(snapshot['timestamp'])
            overall_scores.append(metrics.get('overall_completeness_score', 0))
            validation_scores.append(metrics.get('research_validation_score', 0))
            completeness_scores.append(metrics.get('required_fields_completeness', 0))
            specificity_scores.append(metrics.get('material_specificity_score', 0))
        
        # Calculate trends
        def calculate_trend(values):
            if len(values) >= 2:
                return values[-1] - values[0]  # Latest - earliest
            return 0
        
        trends = {
            "overall_trend": calculate_trend(overall_scores),
            "validation_trend": calculate_trend(validation_scores),
            "completeness_trend": calculate_trend(completeness_scores),
            "specificity_trend": calculate_trend(specificity_scores),
            "total_snapshots": len(history),
            "time_span": (
                datetime.fromisoformat(timestamps[-1]) - 
                datetime.fromisoformat(timestamps[0])
            ).days if len(timestamps) >= 2 else 0
        }
        
        return {
            "material": material_name,
            "trends": trends,
            "latest_scores": {
                "overall": overall_scores[-1],
                "validation": validation_scores[-1],
                "completeness": completeness_scores[-1],
                "specificity": specificity_scores[-1]
            },
            "historical_data": {
                "timestamps": timestamps,
                "overall_scores": overall_scores,
                "validation_scores": validation_scores
            }
        }
    
    def generate_improvement_recommendations(self, metrics: Dict[str, Any]) -> list[QualityImprovement]:
        """Generate prioritized improvement recommendations"""
        
        recommendations = []
        
        # 1. Research Validation (Critical if 0%)
        if metrics.get('research_validation_score', 0) == 0:
            recommendations.append(QualityImprovement(
                category="research_validation",
                priority="HIGH",
                description="No research validation metadata found",
                current_score=0.0,
                target_score=80.0,
                improvement_steps=[
                    "Add confidence_score fields to critical properties",
                    "Include sources_validated counts",
                    "Add research_sources arrays with citations", 
                    "Implement validation metadata in generation pipeline",
                    "Create validation scoring system"
                ],
                estimated_effort="HIGH",
                expected_impact=30.0
            ))
        
        # 2. Material Specificity (if below 90%)
        specificity_score = metrics.get('material_specificity_score', 0)
        if specificity_score < 90:
            recommendations.append(QualityImprovement(
                category="material_specificity",
                priority="MEDIUM",
                description=f"Material specificity at {specificity_score:.1f}% - needs more Ti-6Al-4V specific content",
                current_score=specificity_score,
                target_score=95.0,
                improvement_steps=[
                    "Update material name to include Ti-6Al-4V designation",
                    "Add aerospace-specific applications",
                    "Include Ti-6Al-4V specific processing parameters",
                    "Add alloy composition details",
                    "Include Ti-6Al-4V market applications"
                ],
                estimated_effort="MEDIUM",
                expected_impact=15.0
            ))
        
        # 3. Optional Fields Completeness (if below 60%)
        optional_completeness = metrics.get('optional_fields_completeness', 0)
        if optional_completeness < 60:
            recommendations.append(QualityImprovement(
                category="field_completeness",
                priority="MEDIUM",
                description=f"Optional fields at {optional_completeness:.1f}% - missing valuable content",
                current_score=optional_completeness,
                target_score=75.0,
                improvement_steps=[
                    "Add environmental_impact field",
                    "Include recyclability information",
                    "Add cost_considerations",
                    "Include market_applications array",
                    "Add regulatory_compliance data"
                ],
                estimated_effort="MEDIUM",
                expected_impact=12.0
            ))
        
        # 4. Semantic Completeness (if below 70%)
        semantic_score = metrics.get('semantic_completeness_score', 0)
        if semantic_score < 70:
            recommendations.append(QualityImprovement(
                category="semantic_content",
                priority="MEDIUM",
                description=f"Semantic completeness at {semantic_score:.1f}% - needs richer content",
                current_score=semantic_score,
                target_score=85.0,
                improvement_steps=[
                    "Expand processing_notes with detailed guidance",
                    "Add comprehensive optimization_notes",
                    "Include 6+ specific applications",
                    "Enhance machine settings with 8+ parameters",
                    "Add detailed processingImpact descriptions"
                ],
                estimated_effort="MEDIUM",
                expected_impact=20.0
            ))
        
        # 5. Type Violations (if any)
        type_violations = metrics.get('type_violations', 0)
        if type_violations > 0:
            recommendations.append(QualityImprovement(
                category="schema_compliance",
                priority="HIGH",
                description=f"{type_violations} type violations found",
                current_score=metrics.get('type_accuracy_score', 0),
                target_score=100.0,
                improvement_steps=[
                    "Review schema type definitions",
                    "Fix numeric fields to proper number types",
                    "Ensure boolean fields use true/false",
                    "Validate array structures",
                    "Test schema compliance in generation pipeline"
                ],
                estimated_effort="LOW",
                expected_impact=5.0
            ))
        
        # 6. Safety Completeness (if below 100%)
        safety_score = metrics.get('safety_completeness_score', 0)
        if safety_score < 100:
            recommendations.append(QualityImprovement(
                category="safety_content",
                priority="HIGH",
                description=f"Safety completeness at {safety_score:.1f}% - critical for laser applications",
                current_score=safety_score,
                target_score=100.0,
                improvement_steps=[
                    "Add incompatibleConditions array",
                    "Include thermalDamageThreshold data",
                    "Add eye protection requirements",
                    "Include ventilation requirements",
                    "Add material-specific safety warnings"
                ],
                estimated_effort="MEDIUM",
                expected_impact=10.0
            ))
        
        # Sort by priority and expected impact
        priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(key=lambda x: (priority_order[x.priority], -x.expected_impact))
        
        return recommendations
    
    def create_improvement_plan(self, material_name: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive improvement plan"""
        
        recommendations = self.generate_improvement_recommendations(metrics)
        
        # Calculate total expected improvement
        total_impact = sum(rec.expected_impact for rec in recommendations)
        current_overall = metrics.get('overall_completeness_score', 0)
        projected_score = min(100.0, current_overall + total_impact)
        
        # Group by priority
        high_priority = [rec for rec in recommendations if rec.priority == "HIGH"]
        medium_priority = [rec for rec in recommendations if rec.priority == "MEDIUM"]
        low_priority = [rec for rec in recommendations if rec.priority == "LOW"]
        
        # Create implementation phases
        phases = []
        if high_priority:
            phases.append({
                "phase": 1,
                "name": "Critical Fixes",
                "items": len(high_priority),
                "expected_impact": sum(rec.expected_impact for rec in high_priority),
                "recommendations": [asdict(rec) for rec in high_priority]
            })
        
        if medium_priority:
            phases.append({
                "phase": 2,
                "name": "Quality Enhancement",
                "items": len(medium_priority),
                "expected_impact": sum(rec.expected_impact for rec in medium_priority),
                "recommendations": [asdict(rec) for rec in medium_priority]
            })
        
        if low_priority:
            phases.append({
                "phase": 3,
                "name": "Polish & Optimization",
                "items": len(low_priority),
                "expected_impact": sum(rec.expected_impact for rec in low_priority),
                "recommendations": [asdict(rec) for rec in low_priority]
            })
        
        return {
            "material": material_name,
            "current_score": current_overall,
            "projected_score": projected_score,
            "total_improvements": len(recommendations),
            "total_expected_impact": total_impact,
            "implementation_phases": phases,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_improvement_report(self, material_name: str, improvement_plan: Dict[str, Any]) -> str:
        """Generate human-readable improvement report"""
        
        report = f"""
🎯 QUALITY IMPROVEMENT PLAN: {material_name.upper()}
{'='*60}

📊 CURRENT STATE:
   Current Overall Score: {improvement_plan['current_score']:.1f}%
   Projected Score: {improvement_plan['projected_score']:.1f}%
   Expected Improvement: +{improvement_plan['total_expected_impact']:.1f}%
   Total Recommendations: {improvement_plan['total_improvements']}

🚀 IMPLEMENTATION PHASES:
"""
        
        for phase in improvement_plan['implementation_phases']:
            report += f"""
   Phase {phase['phase']}: {phase['name']}
   └── {phase['items']} items (+{phase['expected_impact']:.1f}% impact)
"""
        
        report += "\n📋 DETAILED RECOMMENDATIONS:\n"
        
        for phase in improvement_plan['implementation_phases']:
            report += f"\n🔥 PHASE {phase['phase']}: {phase['name'].upper()}\n"
            report += f"{'─'*50}\n"
            
            for i, rec in enumerate(phase['recommendations'], 1):
                report += f"""
{i}. {rec['description']}
   Priority: {rec['priority']} | Impact: +{rec['expected_impact']:.1f}%
   Effort: {rec['estimated_effort']} | Target: {rec['target_score']:.1f}%
   
   Steps:
"""
                for step in rec['improvement_steps']:
                    report += f"   • {step}\n"
        
        report += f"\n📅 Generated: {improvement_plan['timestamp']}\n"
        
        return report
    
    def compare_materials_quality(self, material_names: list[str]) -> Dict[str, Any]:
        """Compare quality metrics across multiple materials"""
        
        comparison = {
            "materials": [],
            "comparison_metrics": {},
            "rankings": {}
        }
        
        # Load latest metrics for each material
        for material in material_names:
            history = self.load_quality_history(material)
            if history:
                latest = history[-1]['metrics']
                comparison["materials"].append({
                    "name": material,
                    "metrics": latest
                })
        
        if not comparison["materials"]:
            return {"error": "No quality data found for any materials"}
        
        # Create comparison metrics
        metric_keys = [
            'overall_completeness_score',
            'research_validation_score', 
            'material_specificity_score',
            'laser_relevance_score',
            'safety_completeness_score'
        ]
        
        for metric in metric_keys:
            values = []
            for material_data in comparison["materials"]:
                values.append({
                    "material": material_data["name"],
                    "value": material_data["metrics"].get(metric, 0)
                })
            
            # Sort by value (descending)
            values.sort(key=lambda x: x["value"], reverse=True)
            comparison["comparison_metrics"][metric] = values
        
        # Create overall rankings
        overall_scores = []
        for material_data in comparison["materials"]:
            overall_scores.append({
                "material": material_data["name"],
                "score": material_data["metrics"].get('overall_completeness_score', 0)
            })
        
        overall_scores.sort(key=lambda x: x["score"], reverse=True)
        comparison["rankings"]["overall"] = overall_scores
        
        return comparison


def main():
    """CLI interface for quality improvement tracking"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Quality improvement tracking and recommendations")
    parser.add_argument("command", choices=['recommend', 'plan', 'trends', 'compare'])
    parser.add_argument("material", help="Material name")
    parser.add_argument("--metrics-file", help="JSON file with quality metrics")
    parser.add_argument("--export", help="Export results to file")
    
    args = parser.parse_args()
    
    tracker = QualityImprovementTracker()
    
    if args.command == "recommend":
        # Load metrics
        if not args.metrics_file:
            print("❌ --metrics-file required for recommendations")
            return
        
        with open(args.metrics_file, 'r') as f:
            metrics = json.load(f)
        
        # Generate improvement plan
        plan = tracker.create_improvement_plan(args.material, metrics)
        report = tracker.generate_improvement_report(args.material, plan)
        print(report)
        
        # Save snapshot
        snapshot_path = tracker.save_quality_snapshot(metrics, args.material)
        print(f"📁 Quality snapshot saved: {snapshot_path}")
        
        if args.export:
            with open(args.export, 'w') as f:
                json.dump(plan, f, indent=2)
            print(f"📁 Improvement plan exported: {args.export}")
    
    elif args.command == "trends":
        trends = tracker.analyze_quality_trends(args.material)
        print(json.dumps(trends, indent=2))
    
    elif args.command == "compare":
        materials = args.material.split(',')
        comparison = tracker.compare_materials_quality(materials)
        print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()