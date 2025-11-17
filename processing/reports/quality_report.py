"""
Quality Analysis Report
=======================

Detailed quality scoring breakdown and interpretation.
"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime


@dataclass
class QualityReport:
    """
    Detailed quality analysis report.
    
    Provides comprehensive breakdown of quality scoring components
    and their interpretation for optimization insights.
    """
    
    material: str
    component_type: str
    timestamp: datetime
    
    # Winston Breakdown
    winston_score: float
    winston_weight: float = 0.6
    winston_contribution: float = 0.0
    
    # Subjective Breakdown
    subjective_score: float = 0.0
    subjective_weight: float = 0.3
    subjective_contribution: float = 0.0
    subjective_dimensions: Dict[str, float] = field(default_factory=dict)
    
    # Readability Breakdown
    readability_score: float = 0.0
    readability_weight: float = 0.1
    readability_contribution: float = 0.0
    
    # Composite Result
    composite_score: float = 0.0
    quality_tier: str = ""
    
    # Insights
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate contributions and interpret quality."""
        self.winston_contribution = self.winston_score * self.winston_weight
        self.subjective_contribution = self.subjective_score * self.subjective_weight
        self.readability_contribution = self.readability_score * self.readability_weight
        
        self.composite_score = (
            self.winston_contribution +
            self.subjective_contribution +
            self.readability_contribution
        )
        
        # Determine quality tier
        if self.composite_score >= 90:
            self.quality_tier = "🌟 EXCEPTIONAL"
        elif self.composite_score >= 80:
            self.quality_tier = "✨ EXCELLENT"
        elif self.composite_score >= 70:
            self.quality_tier = "✅ GOOD"
        elif self.composite_score >= 60:
            self.quality_tier = "⚠️ ACCEPTABLE"
        else:
            self.quality_tier = "❌ NEEDS IMPROVEMENT"
        
        self._analyze_quality()
    
    def _analyze_quality(self):
        """Identify strengths, weaknesses, and opportunities."""
        # Analyze strengths
        if self.winston_score >= 90:
            self.strengths.append("Excellent human-like writing quality (Winston 90+)")
        if self.subjective_score >= 8.0:
            self.strengths.append("High subjective quality rating (8.0+/10)")
        if self.readability_score >= 70:
            self.strengths.append("Strong readability and clarity")
        
        # Analyze weaknesses
        if self.winston_score < 70:
            self.weaknesses.append(f"Low Winston score ({self.winston_score:.1f}%) - content may be too robotic")
        if self.subjective_score < 6.0:
            self.weaknesses.append(f"Low subjective rating ({self.subjective_score:.1f}/10) - needs quality improvement")
        if self.readability_score < 50:
            self.weaknesses.append(f"Poor readability ({self.readability_score:.1f}/100) - text may be too complex")
        
        # Optimization opportunities
        if self.winston_contribution < 45:  # Less than 75% of max weighted contribution
            self.optimization_opportunities.append(
                "Winston score has the highest weight (60%) - improving human-like writing could significantly boost composite score"
            )
        
        if self.subjective_dimensions:
            weak_dimensions = [dim for dim, score in self.subjective_dimensions.items() if score < 6.0]
            if weak_dimensions:
                self.optimization_opportunities.append(
                    f"Weak subjective dimensions: {', '.join(weak_dimensions)} - focus improvements here"
                )
        
        # Balance analysis
        contributions = [
            ('Winston', self.winston_contribution, self.winston_weight * 100),
            ('Subjective', self.subjective_contribution, self.subjective_weight * 100),
            ('Readability', self.readability_contribution, self.readability_weight * 100),
        ]
        
        max_contrib = max(contributions, key=lambda x: x[1])
        min_contrib = min(contributions, key=lambda x: x[1])
        
        if max_contrib[1] - min_contrib[1] > 30:
            self.optimization_opportunities.append(
                f"Unbalanced scoring: {max_contrib[0]} performing much better than {min_contrib[0]} - "
                f"consider rebalancing parameters"
            )
    
    def to_markdown(self) -> str:
        """Generate detailed quality analysis report."""
        lines = [
            f"# Quality Analysis: {self.material} ({self.component_type})",
            "",
            f"**Analysis Date**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Quality Tier**: {self.quality_tier}",
            f"**Composite Score**: {self.composite_score:.2f}/100",
            "",
            "---",
            "",
            "## 📊 Score Breakdown",
            "",
            "| Component | Raw Score | Weight | Contribution | Percentage of Total |",
            "|-----------|-----------|--------|--------------|---------------------|",
            f"| **Winston AI** | {self.winston_score:.2f}% | {self.winston_weight*100:.0f}% | {self.winston_contribution:.2f} | {(self.winston_contribution/self.composite_score)*100:.1f}% |",
            f"| **Subjective** | {self.subjective_score:.2f}/10 | {self.subjective_weight*100:.0f}% | {self.subjective_contribution:.2f} | {(self.subjective_contribution/self.composite_score)*100:.1f}% |",
            f"| **Readability** | {self.readability_score:.2f}/100 | {self.readability_weight*100:.0f}% | {self.readability_contribution:.2f} | {(self.readability_contribution/self.composite_score)*100:.1f}% |",
            f"| **TOTAL** | — | 100% | **{self.composite_score:.2f}** | 100% |",
            "",
        ]
        
        # Subjective dimensions
        if self.subjective_dimensions:
            lines.extend([
                "### 📋 Subjective Quality Dimensions",
                "",
            ])
            for dim, score in sorted(self.subjective_dimensions.items(), key=lambda x: x[1], reverse=True):
                emoji = "✅" if score >= 7.0 else "⚠️" if score >= 5.0 else "❌"
                lines.append(f"- {emoji} **{dim}**: {score:.1f}/10")
            lines.append("")
        
        # Strengths
        if self.strengths:
            lines.extend([
                "## ✨ Strengths",
                "",
            ])
            for strength in self.strengths:
                lines.append(f"- {strength}")
            lines.append("")
        
        # Weaknesses
        if self.weaknesses:
            lines.extend([
                "## ⚠️ Areas for Improvement",
                "",
            ])
            for weakness in self.weaknesses:
                lines.append(f"- {weakness}")
            lines.append("")
        
        # Optimization opportunities
        if self.optimization_opportunities:
            lines.extend([
                "## 🎯 Optimization Opportunities",
                "",
            ])
            for opp in self.optimization_opportunities:
                lines.append(f"- {opp}")
            lines.append("")
        
        # Visual representation
        lines.extend([
            "## 📈 Visual Representation",
            "",
            "```",
            "Composite Score Composition:",
            f"Winston:     {'█' * int(self.winston_contribution/2)} {self.winston_contribution:.1f}",
            f"Subjective:  {'█' * int(self.subjective_contribution/2)} {self.subjective_contribution:.1f}",
            f"Readability: {'█' * int(self.readability_contribution/2)} {self.readability_contribution:.1f}",
            f"            {'─' * 50}",
            f"TOTAL:       {'█' * int(self.composite_score/2)} {self.composite_score:.1f}",
            "```",
            "",
        ])
        
        return "\n".join(lines)
