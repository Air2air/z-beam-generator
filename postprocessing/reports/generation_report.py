"""
Generation Report Templates
============================

Standardized templates for single and batch generation reports.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class GenerationStatus(Enum):
    """Generation outcome status."""
    SUCCESS = "✅ PASS"
    FAILED = "❌ FAILED"
    PARTIAL = "⚠️ PARTIAL"
    SKIPPED = "⏭️ SKIPPED"


@dataclass
class WinstonMetrics:
    """Winston AI detection metrics."""
    human_score: float
    ai_score: float
    sentence_count: int
    readability_score: float
    credits_used: int
    detection_id: Optional[int] = None
    sentence_analysis: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SubjectiveMetrics:
    """Subjective quality evaluation metrics."""
    overall_score: float
    dimensions: Dict[str, float] = field(default_factory=dict)
    evaluation_id: Optional[int] = None


@dataclass
class GenerationParameters:
    """Parameters used for generation."""
    temperature: float
    frequency_penalty: float
    presence_penalty: float
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    parameters_id: Optional[int] = None


@dataclass
class CompositeScoring:
    """Composite quality scoring breakdown."""
    composite_score: float
    winston_weight: float = 0.6
    subjective_weight: float = 0.3
    readability_weight: float = 0.1
    interpretation: str = ""


@dataclass
class GenerationReport:
    """
    Comprehensive report for a single generation operation.
    
    Attributes:
        material: Material name
        component_type: Type of component (caption, subtitle, etc.)
        status: Generation outcome
        timestamp: When generation occurred
        author: Author persona used (if applicable)
        winston_metrics: AI detection results
        subjective_metrics: Quality evaluation results
        parameters: Generation parameters used
        composite_scoring: Unified quality score
        content_length: Generated content character count
        tokens_used: API tokens consumed
        response_time: Generation time in seconds
        error_message: Error details if failed
        notes: Additional observations
    """
    
    material: str
    component_type: str
    status: GenerationStatus
    timestamp: datetime
    
    # Optional metrics
    author: Optional[str] = None
    winston_metrics: Optional[WinstonMetrics] = None
    subjective_metrics: Optional[SubjectiveMetrics] = None
    parameters: Optional[GenerationParameters] = None
    composite_scoring: Optional[CompositeScoring] = None
    
    # Generation details
    content_length: int = 0
    tokens_used: int = 0
    response_time: float = 0.0
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # Additional context
    notes: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Generate markdown report for this generation."""
        lines = [
            f"## {self.material} - {self.component_type.upper()}",
            "",
            f"**Status**: {self.status.value}",
            f"**Timestamp**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        
        if self.author:
            lines.append(f"**Author**: {self.author}")
        
        lines.append("")
        
        # Winston Metrics
        if self.winston_metrics:
            lines.extend([
                "### 🔍 Winston AI Detection",
                f"- **Human Score**: {self.winston_metrics.human_score:.2f}%",
                f"- **AI Score**: {self.winston_metrics.ai_score:.2f}%",
                f"- **Readability**: {self.winston_metrics.readability_score:.2f}/100",
                f"- **Sentences Analyzed**: {self.winston_metrics.sentence_count}",
                f"- **Credits Used**: {self.winston_metrics.credits_used}",
            ])
            
            if self.winston_metrics.detection_id:
                lines.append(f"- **Detection ID**: #{self.winston_metrics.detection_id}")
            
            # Sentence-level analysis
            if self.winston_metrics.sentence_analysis:
                lines.append("")
                lines.append("**Sentence Analysis**:")
                for i, sent in enumerate(self.winston_metrics.sentence_analysis, 1):
                    score = sent.get('human_score', 0)
                    text = sent.get('text', '')[:60] + "..."
                    emoji = "✅" if score > 70 else "⚠️" if score > 40 else "🚨"
                    lines.append(f"  {emoji} #{i}: {score:.0f}% human - \"{text}\"")
            
            lines.append("")
        
        # Subjective Evaluation
        if self.subjective_metrics:
            lines.extend([
                "### 📊 Subjective Evaluation",
                f"- **Overall Score**: {self.subjective_metrics.overall_score:.1f}/10",
            ])
            
            if self.subjective_metrics.dimensions:
                lines.append("- **Quality Dimensions**:")
                for dim, score in self.subjective_metrics.dimensions.items():
                    lines.append(f"  - {dim}: {score:.1f}/10")
            
            if self.subjective_metrics.evaluation_id:
                lines.append(f"- **Evaluation ID**: #{self.subjective_metrics.evaluation_id}")
            
            lines.append("")
        
        # Composite Scoring
        if self.composite_scoring:
            lines.extend([
                "### 🎯 Composite Quality Score",
                f"- **Unified Score**: {self.composite_scoring.composite_score:.2f}/100",
                f"- **Interpretation**: {self.composite_scoring.interpretation}",
                f"- **Weight Distribution**: Winston {self.composite_scoring.winston_weight*100:.0f}% + "
                f"Subjective {self.composite_scoring.subjective_weight*100:.0f}% + "
                f"Readability {self.composite_scoring.readability_weight*100:.0f}%",
                "",
            ])
        
        # Generation Parameters
        if self.parameters:
            lines.extend([
                "### ⚙️ Generation Parameters",
                f"- **Temperature**: {self.parameters.temperature:.3f}",
                f"- **Frequency Penalty**: {self.parameters.frequency_penalty:.3f}",
                f"- **Presence Penalty**: {self.parameters.presence_penalty:.3f}",
            ])
            
            if self.parameters.top_p is not None:
                lines.append(f"- **Top P**: {self.parameters.top_p:.3f}")
            
            if self.parameters.max_tokens:
                lines.append(f"- **Max Tokens**: {self.parameters.max_tokens}")
            
            if self.parameters.parameters_id:
                lines.append(f"- **Parameters ID**: #{self.parameters.parameters_id}")
            
            lines.append("")
        
        # Performance Metrics
        lines.extend([
            "### 📈 Performance Metrics",
            f"- **Content Length**: {self.content_length} characters",
            f"- **Tokens Used**: {self.tokens_used}",
            f"- **Response Time**: {self.response_time:.2f}s",
        ])
        
        if self.retry_count > 0:
            lines.append(f"- **Retry Attempts**: {self.retry_count}")
        
        lines.append("")
        
        # Error Information
        if self.error_message:
            lines.extend([
                "### ❌ Error Details",
                f"```",
                self.error_message,
                f"```",
                "",
            ])
        
        # Additional Notes
        if self.notes:
            lines.extend([
                "### 📝 Notes",
            ])
            for note in self.notes:
                lines.append(f"- {note}")
            lines.append("")
        
        return "\n".join(lines)


@dataclass
class BatchReport:
    """
    Comprehensive report for batch generation operations.
    
    Attributes:
        batch_name: Descriptive name for this batch
        timestamp: When batch started
        purpose: Goal of this batch test
        reports: Individual generation reports
        summary_stats: Aggregated statistics
        recommendations: Next steps and insights
    """
    
    batch_name: str
    timestamp: datetime
    purpose: str
    reports: List[GenerationReport] = field(default_factory=list)
    summary_stats: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def calculate_summary(self):
        """Calculate aggregate statistics from individual reports."""
        total = len(self.reports)
        if total == 0:
            return
        
        successful = sum(1 for r in self.reports if r.status == GenerationStatus.SUCCESS)
        failed = sum(1 for r in self.reports if r.status == GenerationStatus.FAILED)
        
        # Average scores (only from successful generations)
        success_reports = [r for r in self.reports if r.status == GenerationStatus.SUCCESS]
        
        if success_reports:
            avg_human_score = sum(
                r.winston_metrics.human_score for r in success_reports 
                if r.winston_metrics
            ) / len(success_reports)
            
            avg_ai_score = sum(
                r.winston_metrics.ai_score for r in success_reports 
                if r.winston_metrics
            ) / len(success_reports)
            
            # Handle composite scoring (may not be present in all reports)
            composite_reports = [r for r in success_reports if r.composite_scoring]
            avg_composite = (
                sum(r.composite_scoring.composite_score for r in composite_reports) / len(composite_reports)
            ) if composite_reports else 0.0
            
            total_credits = sum(
                r.winston_metrics.credits_used for r in self.reports 
                if r.winston_metrics
            )
            
            total_tokens = sum(r.tokens_used for r in self.reports)
            
            self.summary_stats = {
                'total_materials': total,
                'successful': successful,
                'failed': failed,
                'success_rate': (successful / total) * 100,
                'avg_human_score': avg_human_score,
                'avg_ai_score': avg_ai_score,
                'avg_composite_score': avg_composite,
                'total_credits_used': total_credits,
                'total_tokens_used': total_tokens,
            }
    
    def to_markdown(self) -> str:
        """Generate comprehensive markdown report for batch."""
        self.calculate_summary()
        
        lines = [
            f"# {self.batch_name}",
            "",
            f"**Date**: {self.timestamp.strftime('%B %d, %Y %H:%M:%S')}",
            f"**Purpose**: {self.purpose}",
            "",
            "---",
            "",
            "## 📊 Executive Summary",
            "",
        ]
        
        stats = self.summary_stats
        if stats:
            lines.extend([
                "| Metric | Value |",
                "|--------|-------|",
                f"| **Total Materials** | {stats['total_materials']} |",
                f"| **Successful** | {stats['successful']} ✅ |",
                f"| **Failed** | {stats['failed']} ❌ |",
                f"| **Success Rate** | {stats['success_rate']:.1f}% |",
                f"| **Avg Human Score** | {stats['avg_human_score']:.2f}% |",
                f"| **Avg AI Score** | {stats['avg_ai_score']:.2f}% |",
                f"| **Avg Composite Score** | {stats['avg_composite_score']:.2f}/100 |",
                f"| **Total Credits Used** | {stats['total_credits_used']} |",
                f"| **Total Tokens Used** | {stats['total_tokens_used']:,} |",
                "",
            ])
        
        # Quick results table
        lines.extend([
            "## 📋 Quick Results",
            "",
            "| Material | Status | Human% | AI% | Composite | Notes |",
            "|----------|--------|--------|-----|-----------|-------|",
        ])
        
        for report in self.reports:
            human = f"{report.winston_metrics.human_score:.1f}%" if report.winston_metrics else "N/A"
            ai = f"{report.winston_metrics.ai_score:.1f}%" if report.winston_metrics else "N/A"
            comp = f"{report.composite_scoring.composite_score:.1f}" if report.composite_scoring else "N/A"
            note = report.notes[0] if report.notes else ""
            
            lines.append(
                f"| **{report.material}** | {report.status.value} | {human} | {ai} | {comp} | {note} |"
            )
        
        lines.extend(["", "---", ""])
        
        # Detailed individual reports
        lines.append("## 📖 Detailed Reports")
        lines.append("")
        
        for i, report in enumerate(self.reports, 1):
            lines.append(f"### {i}. {report.material}")
            lines.append("")
            lines.append(report.to_markdown())
            lines.append("---")
            lines.append("")
        
        # Recommendations
        if self.recommendations:
            lines.extend([
                "## 💡 Recommendations & Next Steps",
                "",
            ])
            for rec in self.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        return "\n".join(lines)
