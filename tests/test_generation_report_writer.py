#!/usr/bin/env python3
"""
Test Generation Report Writer
==============================
Tests the GenerationReportWriter to ensure reports are saved correctly.
"""

import pytest
from pathlib import Path
from postprocessing.reports.generation_report_writer import GenerationReportWriter


def test_report_writer_creates_default_file(tmp_path):
    """Test that report writer creates file in specified location."""
    report_file = tmp_path / "TEST_REPORT.md"
    writer = GenerationReportWriter(report_file=report_file)
    
    result = writer.save_individual_report(
        material_name="Aluminum",
        component_type="subtitle",
        content="Test content for aluminum subtitle"
    )
    
    assert result == report_file
    assert report_file.exists()


def test_report_contains_required_sections(tmp_path):
    """Test that report includes all required sections."""
    report_file = tmp_path / "TEST_REPORT.md"
    writer = GenerationReportWriter(report_file=report_file)
    
    writer.save_individual_report(
        material_name="Steel",
        component_type="caption",
        content="BEFORE: Dirty\nAFTER: Clean"
    )
    
    content = report_file.read_text()
    
    # Check required sections
    assert "# Generation Report" in content
    assert "**Material**: Steel" in content
    assert "**Component**: caption" in content
    assert "## 📝 Generated Content" in content
    assert "## 📏 Statistics" in content
    assert "## 💾 Storage" in content
    assert "BEFORE: Dirty" in content
    assert "AFTER: Clean" in content


def test_report_statistics_accurate(tmp_path):
    """Test that statistics are calculated correctly."""
    report_file = tmp_path / "TEST_REPORT.md"
    writer = GenerationReportWriter(report_file=report_file)
    
    test_content = "This is a test with exactly ten words in it."
    writer.save_individual_report(
        material_name="Copper",
        component_type="subtitle",
        content=test_content
    )
    
    content = report_file.read_text()
    
    assert f"**Length**: {len(test_content)} characters" in content
    assert "**Word Count**: 10 words" in content


def test_report_overwrites_on_second_generation(tmp_path):
    """Test that report file is overwritten, not appended."""
    report_file = tmp_path / "TEST_REPORT.md"
    writer = GenerationReportWriter(report_file=report_file)
    
    # First generation
    writer.save_individual_report(
        material_name="Aluminum",
        component_type="subtitle",
        content="First generation content"
    )
    
    first_content = report_file.read_text()
    assert "Aluminum" in first_content
    assert "First generation" in first_content
    
    # Second generation (should overwrite)
    writer.save_individual_report(
        material_name="Titanium",
        component_type="caption",
        content="Second generation content"
    )
    
    second_content = report_file.read_text()
    assert "Titanium" in second_content
    assert "Second generation" in second_content
    assert "Aluminum" not in second_content  # First material should be gone
    assert "First generation" not in second_content  # First content should be gone


def test_batch_report_format(tmp_path):
    """Test batch report contains summary and individual results."""
    report_file = tmp_path / "TEST_REPORT.md"
    writer = GenerationReportWriter(report_file=report_file)
    
    results = [
        {
            'material': 'Aluminum',
            'success': True,
            'content': 'Aluminum content',
            'winston_score': 0.25
        },
        {
            'material': 'Steel',
            'success': True,
            'content': 'Steel content',
            'winston_score': 0.30
        }
    ]
    
    summary = {
        'success_count': 2,
        'winston_score': 0.275,
        'concatenated_length': 500,
        'cost_savings': 0.10
    }
    
    writer.save_batch_report(
        component_type='subtitle',
        materials=['Aluminum', 'Steel'],
        results=results,
        summary=summary
    )
    
    content = report_file.read_text()
    
    assert "# Batch Generation Report" in content
    assert "**Success Rate**: 2/2" in content
    assert "## 📊 Batch Summary" in content
    assert "## 📝 Individual Results" in content
    assert "### Aluminum" in content
    assert "### Steel" in content


def test_report_with_evaluation(tmp_path):
    """Test report includes evaluation when provided."""
    report_file = tmp_path / "TEST_REPORT.md"
    writer = GenerationReportWriter(report_file=report_file)
    
    evaluation = {
        'narrative_assessment': 'This content is excellent quality with good technical accuracy.'
    }
    
    writer.save_individual_report(
        material_name="Brass",
        component_type="faq",
        content="Q: What is brass?\nA: An alloy of copper and zinc.",
        evaluation=evaluation
    )
    
    content = report_file.read_text()
    
    assert "## 📊 Subjective Evaluation" in content
    assert "excellent quality" in content


def test_default_report_location():
    """Test that default location is GENERATION_REPORT.md in root."""
    writer = GenerationReportWriter()
    assert writer.report_file == Path("GENERATION_REPORT.md")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
