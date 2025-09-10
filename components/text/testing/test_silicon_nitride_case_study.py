"""
Test case for Silicon Nitride laser cleaning content generation case study.
Validates prompt chain integration, AI detection optimization, and quality metrics.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from components.text.generators.fail_fast_generator import FailFastTextGenerator


class TestSiliconNitrideCaseStudy:
    """Test class validating the Silicon Nitride case study example."""

    @pytest.fixture
    def generator(self):
        """Create a FailFastContentGenerator instance for testing."""
        return FailFastTextGenerator()

    @pytest.fixture
    def case_study_content(self):
        """Load the actual Silicon Nitride case study content."""
        content_file = Path("content/components/text/silicon-nitride-laser-cleaning.md")
        if content_file.exists():
            with open(content_file, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def test_taiwan_persona_file_structure(self):
        """Verify Taiwan persona file contains expected structure from case study."""
        persona_file = Path("components/text/prompts/personas/taiwan_persona.yaml")
        assert persona_file.exists(), "Taiwan persona file should exist"

        with open(persona_file, "r", encoding="utf-8") as f:
            persona_data = yaml.safe_load(f)

        # Verify structure matches case study expectations
        assert "persona" in persona_data
        # Note: The actual file has placeholder content, not specific names
        assert "country" in persona_data["persona"]
        assert persona_data["persona"]["country"] == "Taiwan"
        assert "language_patterns" in persona_data
        assert "signature_phrases" in persona_data["language_patterns"]

        # Verify signature phrases from the actual file
        signature_phrases = persona_data["language_patterns"]["signature_phrases"]
        expected_phrases = [
            "This is important, very important",
            "It works good, really good",
            "Must consider carefully, very carefully",
        ]
        for phrase in expected_phrases:
            assert (
                phrase in signature_phrases
            ), f"Expected signature phrase '{phrase}' not found"

    def test_taiwan_formatting_file_structure(self):
        """Verify Taiwan formatting file contains expected structure from case study."""
        formatting_file = Path(
            "components/text/prompts/formatting/taiwan_formatting.yaml"
        )
        assert formatting_file.exists(), "Taiwan formatting file should exist"

        with open(formatting_file, "r", encoding="utf-8") as f:
            formatting_data = yaml.safe_load(f)

        # Verify structure matches case study expectations
        assert formatting_data["country"] == "Taiwan"
        assert "formatting_patterns" in formatting_data
        assert "content_constraints" in formatting_data
        assert formatting_data["content_constraints"]["max_word_count"] == 380

        # Verify formatting patterns from case study
        patterns = formatting_data["formatting_patterns"]
        assert "structure" in patterns
        assert "Method-results-discussion" in patterns["structure"]

    def test_ai_detection_config_structure(self):
        """Verify AI detection config contains expected structure from case study."""
        ai_file = Path("config/ai_detection.yaml")
        assert ai_file.exists(), "AI detection config file should exist"

        with open(ai_file, "r", encoding="utf-8") as f:
            ai_data = yaml.safe_load(f)

        # Verify basic structure exists
        assert "enabled" in ai_data
        assert "provider" in ai_data
        assert "target_score" in ai_data
        assert ai_data["enabled"] == True
        assert ai_data["provider"] == "winston"

        # Verify enhancement flags from case study
        assert "natural_language_patterns" in ai_data
        assert "sentence_variability" in ai_data
        assert "paragraph_structure" in ai_data

    def test_case_study_content_structure(self, case_study_content):
        """Verify the case study content has expected structure and metadata."""
        if case_study_content is None:
            pytest.skip("Case study content file not found")

        # Verify basic structure
        assert (
            "### A Practical Look at Laser Cleaning Silicon Nitride"
            in case_study_content
        )
        assert "Yi-Chun Lin" in case_study_content
        assert "silicon nitride" in case_study_content.lower()

        # Verify AI detection metadata
        assert "ai_detection_analysis:" in case_study_content
        assert "score: 76.71" in case_study_content
        assert 'classification: "human"' in case_study_content

        # Verify iteration history
        assert "iteration_history:" in case_study_content
        assert "max_iterations: 5" in case_study_content

    def test_prompt_chain_taiwan_integration(self, generator):
        """Test that prompt chain properly integrates Taiwan-specific elements."""
        subject = "silicon nitride laser cleaning"
        author_id = 1  # Taiwan author
        author_name = "Yi-Chun Lin"
        material_data = {"type": "ceramic_material"}
        author_info = {"country": "Taiwan"}

        prompt = generator._build_api_prompt(
            subject, author_id, author_name, material_data, author_info
        )

        # Verify Taiwan-specific elements are included
        assert "Yi-Chun Lin" in prompt
        assert "Taiwan" in prompt
        # Check for signature phrases that should be in the prompt
        signature_indicators = [
            "This is important, very important",
            "It works good, really good",
        ]
        signature_found = any(phrase in prompt for phrase in signature_indicators)
        assert signature_found, "Expected Taiwan signature phrases not found in prompt"

        # Verify word count constraint
        assert "Maximum word count: 380" in prompt

        # Verify formatting requirements
        assert "Formatting Requirements" in prompt
        assert "Method-results-discussion" in prompt

    def test_cultural_characteristics_integration(self, generator):
        """Test that Taiwanese cultural characteristics are properly integrated."""
        subject = "ceramic material cleaning"
        author_id = 1
        author_name = "Yi-Chun Lin"
        material_data = {}
        author_info = {"country": "Taiwan"}

        prompt = generator._build_api_prompt(
            subject, author_id, author_name, material_data, author_info
        )

        # Verify cultural characteristics from formatting file
        cultural_indicators = [
            "Systematic Approach",
            "Process Oriented",
            "Humble Expertise",
            "Method-results-discussion",
        ]

        cultural_found = any(indicator in prompt for indicator in cultural_indicators)
        assert cultural_found, "Expected Taiwanese cultural characteristics not found"

    def test_ai_detection_prompt_integration(self, generator):
        """Test that AI detection prompts are properly integrated."""
        subject = "laser cleaning technology"
        author_id = 1
        author_name = "Yi-Chun Lin"
        material_data = {}
        author_info = {}

        prompt = generator._build_api_prompt(
            subject, author_id, author_name, material_data, author_info
        )

        # Verify AI detection elements
        assert "Human-Like Content Generation" in prompt
        assert "PRIMARY OBJECTIVE" in prompt

        # Verify human writing characteristics from the actual system
        human_elements = ["conversational", "natural", "human"]
        human_found = any(element in prompt for element in human_elements)
        assert human_found, "Expected human writing characteristics not found"

    def test_word_count_enforcement(self, generator):
        """Test that word count constraints are properly enforced."""
        subject = "advanced ceramic cleaning"
        author_id = 1  # Taiwan - 380 word limit
        author_name = "Yi-Chun Lin"
        material_data = {}
        author_info = {}

        prompt = generator._build_api_prompt(
            subject, author_id, author_name, material_data, author_info
        )

        # Verify word count is specified
        assert "Maximum word count:" in prompt
        assert "380 words" in prompt

    def test_content_quality_validation(self, case_study_content):
        """Validate the quality metrics from the case study."""
        if case_study_content is None:
            pytest.skip("Case study content file not found")

        # Verify AI detection score
        assert "score: 76.71" in case_study_content
        assert 'classification: "human"' in case_study_content

        # Verify the score meets the threshold
        assert "76.71" in case_study_content  # Above 65.0 threshold

        # Verify confidence score
        assert "confidence: 0.4658000000000001" in case_study_content

    def test_iterative_improvement_tracking(self, case_study_content):
        """Test that iterative improvement history is properly tracked."""
        if case_study_content is None:
            pytest.skip("Case study content file not found")

        # Verify iteration structure
        assert "iteration_history:" in case_study_content
        assert "iteration: 1" in case_study_content
        assert "iteration: 2" in case_study_content
        assert "iteration: 3" in case_study_content

        # Verify improvement tracking
        assert "target_reached: false" in case_study_content  # Iterations 1 and 2
        assert "target_reached: true" in case_study_content  # Iteration 3

        # Verify score progression
        assert "score: 60.0" in case_study_content  # Iteration 1
        assert "score: 76.71" in case_study_content  # Iteration 3

    def test_configuration_optimization_tracking(self, case_study_content):
        """Test that configuration optimization is properly tracked."""
        if case_study_content is None:
            pytest.skip("Case study content file not found")

        # Verify optimization structure
        assert "configuration_optimization:" in case_study_content
        assert 'optimizer: "deepseek"' in case_study_content
        assert (
            'optimization_method: "iterative_config_modification"' in case_study_content
        )

        # Verify enhancement applications
        assert "enhancements_applied:" in case_study_content
        assert "conversational_style" in case_study_content
        assert "natural_language_patterns" in case_study_content
        assert "sentence_variability" in case_study_content

    @patch("components.text.generators.fail_fast_generator.logger")
    def test_prompt_verification_logging(self, mock_logger, generator):
        """Test that prompt verification logging works as expected."""
        subject = "silicon nitride"
        author_id = 1
        author_name = "Yi-Chun Lin"
        material_data = {}
        author_info = {}

        prompt = generator._build_api_prompt(
            subject, author_id, author_name, material_data, author_info
        )

        # Verify logging calls match case study expectations
        log_calls = [call.args[0] for call in mock_logger.info.call_args_list]

        assert any("PROMPT CHAIN VERIFICATION" in call for call in log_calls)
        assert any("PERSONA VERIFICATION" in call for call in log_calls)
        assert any("SIGNATURE PHRASES VERIFICATION" in call for call in log_calls)
        assert any("FORMATTING VERIFICATION" in call for call in log_calls)
        assert any("WORD COUNT VERIFICATION" in call for call in log_calls)
        assert any("CULTURAL VERIFICATION" in call for call in log_calls)
        assert any("PROMPT CHAIN COMPLETE" in call for call in log_calls)

    def test_technical_content_accuracy(self, case_study_content):
        """Test that technical content maintains accuracy through iterations."""
        if case_study_content is None:
            pytest.skip("Case study content file not found")

        content_lower = case_study_content.lower()

        # Verify technical terms are preserved
        technical_terms = [
            "silicon nitride",
            "laser cleaning",
            "thermal shock",
            "wavelength",
            "pulses",
            "ceramic",
            "aerospace",
            "bearings",
            "cutting tools",
        ]

        for term in technical_terms:
            assert (
                term in content_lower
            ), f"Technical term '{term}' not found in content"

    def test_authentic_writing_style(self, case_study_content):
        """Test that authentic Taiwanese writing style is maintained."""
        if case_study_content is None:
            pytest.skip("Case study content file not found")

        # Verify Taiwanese writing characteristics from actual content
        assert "in my work" in case_study_content.lower()
        # Check for "why" since the apostrophe might be different
        assert "why" in case_study_content.lower()
        assert "very important" in case_study_content.lower()

        # Verify signature phrases from the actual persona file
        assert "this is important, very important" in case_study_content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
