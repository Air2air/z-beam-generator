"""
Generation Report Writer
========================
Saves generation reports to a single default markdown file in the root directory.

Features:
- Single file: GENERATION_REPORT.md (overwrites on each generation)
- Comprehensive formatting matching terminal output
- Always shows the most recent generation
- Individual and batch generation support
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List


class GenerationReportWriter:
    """Writes generation reports to a single default markdown file."""
    
    def __init__(self, report_file: Optional[Path] = None):
        """
        Initialize report writer.
        
        Args:
            report_file: Path to report file (default: GENERATION_REPORT.md in root)
        """
        self.report_file = report_file or Path("GENERATION_REPORT.md")
    
    def save_individual_report(
        self,
        material_name: str,
        component_type: str,
        content: str,
        metrics: Optional[Dict[str, Any]] = None,
        evaluation: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save individual generation report to default markdown file (overwrites).
        
        Args:
            material_name: Name of material
            component_type: Type of component (caption, faq, etc.)
            content: Generated content
            metrics: Optional quality metrics (Winston, Realism, etc.)
            evaluation: Optional subjective evaluation results
            
        Returns:
            Path to report file
        """
        # Build report content
        lines = [
            f"# Generation Report",
            "",
            f"**Last Updated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"**Material**: {material_name}",
            f"**Component**: {component_type}",
            "",
            "---",
            "",
            "## 📝 Generated Content",
            "",
            "```",
            content,
            "```",
            "",
            "## 📏 Statistics",
            "",
            f"- **Length**: {len(content)} characters",
            f"- **Word Count**: {len(content.split())} words",
            "",
        ]
        
        # Add quality metrics if available
        if metrics:
            lines.extend([
                "## 📈 Quality Metrics",
                "",
            ])
            
            if 'winston_score' in metrics:
                winston_score = metrics['winston_score']
                human_score = (1.0 - winston_score) * 100
                threshold = metrics.get('winston_threshold', 0.33)
                status = "✅ PASS" if winston_score < threshold else "❌ FAIL"
                lines.extend([
                    f"- **Winston AI Score**: {winston_score:.3f} (threshold: {threshold:.3f})",
                    f"- **Human Score**: {human_score:.1f}%",
                    f"- **Status**: {status}",
                ])
            
            if 'realism_score' in metrics:
                lines.append(f"- **Realism Score**: {metrics['realism_score']:.1f}/10")
            
            if 'attempts' in metrics:
                lines.append(f"- **Generation Attempts**: {metrics['attempts']}")
            
            lines.append("")
        
        # Add subjective evaluation if available
        if evaluation and evaluation.get('narrative_assessment'):
            lines.extend([
                "## 📊 Subjective Evaluation",
                "",
                evaluation['narrative_assessment'],
                "",
            ])
        
        # Add storage information
        lines.extend([
            "## 💾 Storage",
            "",
            "- **Location**: data/materials/Materials.yaml",
            f"- **Component**: {component_type}",
            f"- **Material**: {material_name}",
            "",
        ])
        
        # Write to file
        report_content = "\n".join(lines)
        self.report_file.write_text(report_content)
        
        return self.report_file
    
    def save_batch_report(
        self,
        component_type: str,
        materials: List[str],
        results: List[Dict[str, Any]],
        summary: Dict[str, Any]
    ) -> Path:
        """
        Save batch generation report to default markdown file (overwrites).
        
        Args:
            component_type: Type of component
            materials: List of material names
            results: List of generation results (one per material)
            summary: Batch summary statistics
            
        Returns:
            Path to report file
        """
        success_count = summary.get('success_count', 0)
        total_count = len(materials)
        
        # Build report content
        lines = [
            "# Batch Generation Report",
            "",
            f"**Last Updated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"**Component**: {component_type}",
            f"**Materials**: {total_count}",
            f"**Success Rate**: {success_count}/{total_count}",
            "",
            "---",
            "",
        ]
        
        # Add batch summary
        if summary:
            lines.extend([
                "## 📊 Batch Summary",
                "",
            ])
            
            if 'winston_score' in summary and summary['winston_score'] is not None:
                winston_score = summary['winston_score']
                human_score = (1.0 - winston_score) * 100
                lines.extend([
                    f"- **Batch Winston Score**: {winston_score:.3f}",
                    f"- **Batch Human Score**: {human_score:.1f}%",
                ])
            
            if 'concatenated_length' in summary:
                lines.append(f"- **Total Length**: {summary['concatenated_length']} characters")
            
            if 'cost_savings' in summary and summary['cost_savings'] is not None:
                lines.append(f"- **Cost Savings**: ${summary['cost_savings']:.2f}")
            
            lines.extend(["", "---", ""])
        
        # Add individual material results
        lines.extend([
            "## 📝 Individual Results",
            "",
        ])
        
        for result in results:
            material = result.get('material', 'Unknown')
            success = result.get('success', False)
            content = result.get('content', '')
            
            lines.extend([
                f"### {material}",
                "",
            ])
            
            if success:
                lines.extend([
                    "**Status**: ✅ SUCCESS",
                    "",
                    "**Generated Content**:",
                    "```",
                    content,
                    "```",
                    "",
                    f"- Length: {len(content)} characters",
                    f"- Words: {len(content.split())} words",
                ])
                
                if 'winston_score' in result and result['winston_score'] is not None:
                    lines.append(f"- Winston Score: {result['winston_score']:.3f}")
                
                if 'realism_score' in result and result['realism_score'] is not None:
                    lines.append(f"- Realism Score: {result['realism_score']:.1f}/10")
            else:
                error = result.get('error', 'Unknown error')
                lines.extend([
                    "**Status**: ❌ FAILED",
                    "",
                    f"**Error**: {error}",
                ])
            
            lines.extend(["", "---", ""])
        
        # Write to file
        report_content = "\n".join(lines)
        self.report_file.write_text(report_content)
        
        return self.report_file
