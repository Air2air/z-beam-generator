"""
Parameter Analysis Report
=========================

Correlation analysis and parameter optimization insights.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime


@dataclass
class ParameterCorrelation:
    """Single parameter correlation result."""
    parameter_name: str
    correlation_coefficient: float
    p_value: float
    confidence_interval: Tuple[float, float]
    relationship_type: str  # 'linear', 'polynomial', 'logarithmic', 'none'
    is_significant: bool
    optimal_range: Optional[Tuple[float, float]] = None


@dataclass
class ParameterInteraction:
    """Two-parameter interaction/synergy result."""
    param1: str
    param2: str
    interaction_strength: float
    synergy_type: str  # 'synergistic', 'antagonistic', 'independent'
    description: str


@dataclass
class ParameterRecommendation:
    """Optimization recommendation for a parameter."""
    parameter_name: str
    current_value: float
    recommended_value: float
    expected_improvement: float
    confidence: str  # 'high', 'medium', 'low'
    reasoning: str


@dataclass
class ParameterReport:
    """
    Comprehensive parameter correlation and optimization report.
    
    Based on GranularParameterCorrelator analysis.
    """
    
    title: str
    timestamp: datetime
    sample_size: int
    confidence_level: str  # 'high', 'medium', 'low'
    
    # Individual parameter correlations
    correlations: List[ParameterCorrelation] = field(default_factory=list)
    
    # Parameter interactions
    interactions: List[ParameterInteraction] = field(default_factory=list)
    
    # Optimization recommendations
    recommendations: List[ParameterRecommendation] = field(default_factory=list)
    
    # Summary insights
    key_findings: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_key_finding(self, finding: str):
        """Add a key insight from analysis."""
        self.key_findings.append(finding)
    
    def add_warning(self, warning: str):
        """Add a warning about data quality or limitations."""
        self.warnings.append(warning)
    
    def to_markdown(self) -> str:
        """Generate comprehensive parameter analysis report."""
        lines = [
            f"# {self.title}",
            "",
            f"**Analysis Date**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Sample Size**: {self.sample_size} generations",
            f"**Confidence Level**: {self.confidence_level.upper()}",
            "",
            "---",
            "",
        ]
        
        # Warnings first
        if self.warnings:
            lines.extend([
                "## ⚠️ Data Quality Warnings",
                "",
            ])
            for warning in self.warnings:
                lines.append(f"- {warning}")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Key findings
        if self.key_findings:
            lines.extend([
                "## 🔍 Key Findings",
                "",
            ])
            for finding in self.key_findings:
                lines.append(f"- {finding}")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Parameter correlations
        if self.correlations:
            lines.extend([
                "## 📊 Parameter Correlation Analysis",
                "",
                "| Parameter | Correlation | P-Value | Relationship | Significance | Optimal Range |",
                "|-----------|-------------|---------|--------------|--------------|---------------|",
            ])
            
            for corr in sorted(self.correlations, key=lambda x: abs(x.correlation_coefficient), reverse=True):
                sig_emoji = "✅" if corr.is_significant else "❌"
                corr_str = f"{corr.correlation_coefficient:+.3f}"
                p_str = f"{corr.p_value:.4f}"
                opt_range = f"{corr.optimal_range[0]:.2f} - {corr.optimal_range[1]:.2f}" if corr.optimal_range else "N/A"
                
                lines.append(
                    f"| **{corr.parameter_name}** | {corr_str} | {p_str} | {corr.relationship_type} | {sig_emoji} | {opt_range} |"
                )
            
            lines.append("")
            
            # Detailed correlation breakdown
            lines.extend([
                "### 📈 Detailed Correlation Insights",
                "",
            ])
            
            significant = [c for c in self.correlations if c.is_significant]
            if significant:
                lines.append("**Statistically Significant Parameters** (p < 0.05):")
                lines.append("")
                for corr in significant:
                    direction = "positively" if corr.correlation_coefficient > 0 else "negatively"
                    strength = "strongly" if abs(corr.correlation_coefficient) > 0.7 else "moderately" if abs(corr.correlation_coefficient) > 0.4 else "weakly"
                    
                    lines.append(f"- **{corr.parameter_name}**: {strength} {direction} correlated (r={corr.correlation_coefficient:+.3f})")
                    lines.append(f"  - Confidence interval: [{corr.confidence_interval[0]:+.3f}, {corr.confidence_interval[1]:+.3f}]")
                    lines.append(f"  - Relationship type: {corr.relationship_type}")
                    if corr.optimal_range:
                        lines.append(f"  - Optimal range: {corr.optimal_range[0]:.3f} to {corr.optimal_range[1]:.3f}")
                    lines.append("")
            else:
                lines.append("*No statistically significant correlations detected at p < 0.05 level.*")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Parameter interactions
        if self.interactions:
            lines.extend([
                "## 🔗 Parameter Interaction Analysis",
                "",
                "Interactions between pairs of parameters that affect quality together.",
                "",
                "| Parameter 1 | Parameter 2 | Strength | Synergy Type | Description |",
                "|-------------|-------------|----------|--------------|-------------|",
            ])
            
            for interaction in sorted(self.interactions, key=lambda x: abs(x.interaction_strength), reverse=True):
                strength_str = f"{interaction.interaction_strength:+.3f}"
                
                lines.append(
                    f"| **{interaction.param1}** | **{interaction.param2}** | {strength_str} | "
                    f"{interaction.synergy_type} | {interaction.description} |"
                )
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Optimization recommendations
        if self.recommendations:
            lines.extend([
                "## 🎯 Optimization Recommendations",
                "",
                "Based on correlation analysis, these parameter adjustments are recommended:",
                "",
            ])
            
            for rec in sorted(self.recommendations, key=lambda x: x.expected_improvement, reverse=True):
                lines.extend([
                    f"### {rec.parameter_name}",
                    "",
                    f"- **Current Value**: {rec.current_value:.3f}",
                    f"- **Recommended Value**: {rec.recommended_value:.3f}",
                    f"- **Expected Improvement**: +{rec.expected_improvement:.1f} points",
                    f"- **Confidence**: {rec.confidence.upper()}",
                    f"- **Reasoning**: {rec.reasoning}",
                    "",
                ])
            
            lines.append("---")
            lines.append("")
        
        # Methodology
        lines.extend([
            "## 🔬 Methodology",
            "",
            "This analysis uses:",
            "- **Spearman Rank Correlation**: Non-parametric correlation for monotonic relationships",
            "- **Bootstrap Confidence Intervals**: 1000 resamples for robust uncertainty estimates",
            "- **Polynomial Regression**: Detection of non-linear relationships",
            "- **Interaction Analysis**: Two-way parameter effects on quality",
            "",
            "**Statistical Significance**: p-value < 0.05 (95% confidence)",
            "",
            "**Confidence Levels**:",
            "- **HIGH**: 100+ samples, stable correlations",
            "- **MEDIUM**: 30-99 samples, moderate reliability",
            "- **LOW**: <30 samples, exploratory only",
            "",
        ])
        
        return "\n".join(lines)
