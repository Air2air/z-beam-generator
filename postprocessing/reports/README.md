# Generation Report System

Comprehensive reporting framework for Z-Beam content generation analysis.

## 📋 Overview

The report system provides standardized templates for documenting generation results, quality analysis, and parameter optimization. All reports use consistent formatting and metrics for easy comparison across materials, authors, and parameter configurations.

## 🎯 Report Types

### 1. GenerationReport
**Purpose**: Document a single material generation with complete metrics.

**Use Cases**:
- Individual material testing
- Debugging generation issues
- Quality validation for specific content

**Key Metrics**:
- **Subjective quality evaluation** (overall score + dimensions) - Primary quality signal
- Grok humanness detection (human/AI scores, sentence analysis)
- Composite quality score (weighted combination)
- Generation parameters used
- Performance metrics (tokens, time, retries)

**Example**:
```python
from postprocessing.reports import GenerationReport, GenerationStatus, WinstonMetrics

report = GenerationReport(
    material="Steel",
    component_type="micro",
    status=GenerationStatus.SUCCESS,
    timestamp=datetime.now(),
    winston_metrics=WinstonMetrics(
        human_score=95.2,
        ai_score=4.8,
        sentence_count=3,
        readability_score=68.5,
        credits_used=42
    )
)

print(report.to_markdown())
```


### 2. BatchReport
**Purpose**: Aggregate analysis of multiple material generations.

**Use Cases**:

**Key Features**:

**Example**:
```python
from postprocessing.reports import BatchReport, GenerationReport

batch = BatchReport(
    batch_name="Batch Caption Test - Parameter Optimization",
    timestamp=datetime.now(),
    purpose="Test new parameter recommendations across 4 metals"
)

# Add individual reports
batch.reports.extend([steel_report, aluminum_report, titanium_report, copper_report])

# Auto-calculate summary statistics
batch.calculate_summary()

# Add recommendations
batch.recommendations.append("Steel generation requires prompt review")
batch.recommendations.append("Aluminum-Titanium-Copper parameter set is optimal")

print(batch.to_markdown())
```


### 3. QualityReport
**Purpose**: Deep dive into quality scoring breakdown and interpretation.

**Use Cases**:

**Key Features**:

**Example**:
```python
from postprocessing.reports import QualityReport

quality = QualityReport(
    material="Steel",
    component_type="micro",
    timestamp=datetime.now(),
    winston_score=45.2,
    subjective_score=7.5,
    readability_score=65.0
)

# Auto-calculates:
# - Weighted contributions
# - Quality tier (EXCEPTIONAL/EXCELLENT/GOOD/ACCEPTABLE/NEEDS IMPROVEMENT)
# - Strengths, weaknesses, optimization opportunities

print(quality.to_markdown())
```


### 4. ParameterReport
**Purpose**: Statistical correlation analysis and parameter optimization insights.

**Use Cases**:

**Key Features**:

**Example**:
```python
from postprocessing.reports import ParameterReport, ParameterCorrelation, ParameterRecommendation

report = ParameterReport(
    title="Parameter Correlation Analysis - Caption Generation",
    timestamp=datetime.now(),
    sample_size=47,
    confidence_level="medium"
)

# Add correlation results
report.correlations.append(ParameterCorrelation(
    parameter_name="temperature",
    correlation_coefficient=0.68,
    p_value=0.003,
    confidence_interval=(0.42, 0.85),
    relationship_type="linear",
    is_significant=True,
    optimal_range=(0.85, 0.95)
))

# Add recommendations
report.recommendations.append(ParameterRecommendation(
    parameter_name="temperature",
    current_value=0.7,
    recommended_value=0.9,
    expected_improvement=8.5,
    confidence="high",
    reasoning="Strong positive correlation (r=0.68, p=0.003) indicates higher temperature improves quality"
))

print(report.to_markdown())
```


## 🔧 Data Classes Reference

### Supporting Data Classes

#### WinstonMetrics
```python
@dataclass
class WinstonMetrics:
    human_score: float              # 0-100%
    ai_score: float                 # 0-100%
    sentence_count: int             # Number of sentences analyzed
    readability_score: float        # 0-100
    credits_used: int               # Grok credits consumed
    detection_id: Optional[int]     # Database detection result ID
    sentence_analysis: List[Dict]   # Per-sentence breakdown
```

#### SubjectiveMetrics
```python
@dataclass
class SubjectiveMetrics:
    overall_score: float            # 0-10
    dimensions: Dict[str, float]    # Dimension name -> score (0-10)
    evaluation_id: Optional[int]    # Database evaluation ID
```

#### GenerationParameters
```python
@dataclass
class GenerationParameters:
    temperature: float              # 0-2 (typically 0-1)
    frequency_penalty: float        # 0-2
    presence_penalty: float         # 0-2
    top_p: Optional[float]          # 0-1 (nucleus sampling)
    max_tokens: Optional[int]       # Token limit
    parameters_id: Optional[int]    # Database parameters ID
```

#### CompositeScoring
```python
@dataclass
class CompositeScoring:
    composite_score: float          # 0-100 (weighted combination)
    winston_weight: float           # Default: 0.6 (Grok humanness)
    subjective_weight: float        # Default: 0.3
    readability_weight: float       # Default: 0.1
    interpretation: str             # Human-readable quality tier
```


## 📊 Report Integration Examples

### Example 1: Post-Generation Report
```python
def generate_post_report(material: str, result: dict):
    """Generate report after content generation."""
    from postprocessing.reports import GenerationReport, GenerationStatus, WinstonMetrics
    
    report = GenerationReport(
        material=material,
        component_type="micro",
        status=GenerationStatus.SUCCESS if result['success'] else GenerationStatus.FAILED,
        timestamp=datetime.now(),
        winston_metrics=WinstonMetrics(
            human_score=result['grok']['human_score'],
            ai_score=result['grok']['ai_score'],
            sentence_count=len(result['grok']['sentences']),
            readability_score=result['readability'],
            credits_used=result['grok']['credits_used'],
            detection_id=result['detection_id']
        ),
        parameters=GenerationParameters(**result['parameters']),
        content_length=len(result['content']),
        tokens_used=result['tokens']
    )
    
    # Save to file
    with open(f"reports/{material}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md", "w") as f:
        f.write(report.to_markdown())
```

### Example 2: Batch Test Runner
```python
def run_batch_test(materials: List[str]) -> str:
    """Run batch test and generate comprehensive report."""
    from postprocessing.reports import BatchReport, GenerationReport
    
    batch = BatchReport(
        batch_name=f"Batch Caption Test - {datetime.now().strftime('%Y-%m-%d')}",
        timestamp=datetime.now(),
        purpose="Validate parameter optimization across materials"
    )
    
    for material in materials:
        result = generate_micro(material)  # Your generation function
        report = create_generation_report(material, result)
        batch.reports.append(report)
    
    # Auto-calculate summary
    batch.calculate_summary()
    
    # Add recommendations based on results
    failures = [r for r in batch.reports if r.status == GenerationStatus.FAILED]
    if failures:
        batch.recommendations.append(f"{len(failures)} materials failed - review prompts")
    
    # Save to file
    filename = f"reports/batch_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, "w") as f:
        f.write(batch.to_markdown())
    
    return filename
```

### Example 3: Quality Analysis Workflow
```python
def analyze_quality(material: str, metrics: dict):
    """Generate quality analysis report."""
    from postprocessing.reports import QualityReport
    
    report = QualityReport(
        material=material,
        component_type="micro",
        timestamp=datetime.now(),
        winston_score=metrics['winston_score'],
        subjective_score=metrics['subjective_score'],
        readability_score=metrics['readability_score'],
        subjective_dimensions=metrics.get('dimensions', {})
    )
    
    # Report auto-calculates:
    # - Weighted contributions
    # - Quality tier
    # - Strengths/weaknesses
    # - Optimization opportunities
    
    return report.to_markdown()
```

### Example 4: Parameter Correlation Analysis
```python
def analyze_parameters(db_results: List[dict]):
    """Run correlation analysis and generate report."""
    from postprocessing.reports import ParameterReport, ParameterCorrelation
    from learning import GranularParameterCorrelator
    
    # Run correlation analysis
    correlator = GranularParameterCorrelator(db_results)
    correlations = correlator.analyze_all_parameters()
    
    # Create report
    report = ParameterReport(
        title="Parameter Correlation Analysis",
        timestamp=datetime.now(),
        sample_size=len(db_results),
        confidence_level="high" if len(db_results) >= 100 else "medium"
    )
    
    # Add correlations
    for param, data in correlations.items():
        report.correlations.append(ParameterCorrelation(
            parameter_name=param,
            correlation_coefficient=data['correlation'],
            p_value=data['p_value'],
            confidence_interval=data['ci'],
            relationship_type=data['relationship_type'],
            is_significant=data['p_value'] < 0.05,
            optimal_range=data.get('optimal_range')
        ))
    
    # Generate recommendations
    recommendations = correlator.generate_adjustment_recommendations()
    for rec in recommendations:
        report.recommendations.append(rec)
    
    return report.to_markdown()
```


## 🚀 Quick Start

### 1. Generate Single Material Report
```bash
python3 run.py --micro "Steel" --generate-report
```

### 2. Run Batch Test with Report
```bash
python3 run.py --batch-test materials.txt --report-output reports/batch_test.md
```

### 3. Analyze Quality Post-Generation
```python
from postprocessing.reports import QualityReport

# After generation
quality_report = QualityReport(
    material=material,
    component_type="micro",
    timestamp=datetime.now(),
    winston_score=winston_result['human_score'],
    subjective_score=subjective_result['score'],
    readability_score=readability_result['score']
)

print(quality_report.to_markdown())
```


## 📁 Report Storage Convention

```
postprocessing/reports/
├── __init__.py                 # Report system exports
├── generation_report.py        # GenerationReport & BatchReport
├── quality_report.py          # QualityReport
├── parameter_report.py        # ParameterReport
└── README.md                  # This file

/generated_reports/            # Output directory (gitignored)
├── batch_tests/
│   ├── batch_20251116_143022.md
│   └── batch_20251116_150845.md
├── quality_analysis/
│   ├── steel_quality_20251116.md
│   └── aluminum_quality_20251116.md
└── parameter_studies/
    ├── correlation_analysis_20251116.md
    └── optimization_report_20251116.md
```


## 💡 Best Practices

### 1. **Always Include Context**

### 2. **Use Consistent Naming**

### 3. **Preserve Raw Data**

### 4. **Aggregate Before Analysis**

### 5. **Action-Oriented Recommendations**


## 🔗 Integration Points

### With Database System
```python
# Link reports to database records
report.winston_metrics.detection_id = detection_result.id
report.parameters.parameters_id = generation_params.id
report.subjective_metrics.evaluation_id = subjective_eval.id
```

### With Scoring Module
```python
from postprocessing.evaluation import CompositeScorer

scorer = CompositeScorer()
composite = scorer.calculate(
    winston_score=report.winston_metrics.human_score,
    subjective_score=report.subjective_metrics.overall_score,
    readability_score=report.winston_metrics.readability_score
)

report.composite_scoring = CompositeScoring(
    composite_score=composite['composite_score'],
    interpretation=composite['interpretation']
)
```

### With Learning System
```python
from learning import GranularParameterCorrelator

# Generate parameter report from database
correlator = GranularParameterCorrelator(db_records)
param_report = correlator.generate_report()
```


## 🎯 Future Enhancements



**Last Updated**: November 16, 2025  
**Version**: 1.0.0  
**Maintainer**: Z-Beam Content Generation Team
