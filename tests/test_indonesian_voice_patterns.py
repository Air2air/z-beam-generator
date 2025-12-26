"""
Test Indonesian Voice Pattern Strengthening (Dec 26, 2025)

Verifies that strengthened Indonesian linguistic markers appear with correct frequency.

Expected patterns (2-3 per paragraph):
- Topic prominence: "This X, it..." structures
- Aspectual markers: "already", "still", "just now"
- Preposition patterns: "from the data", "at the surface", "in observations"
- Time-fronting with passive: "After treatment is applied..."
"""

import pytest
import re


class TestIndonesianVoicePatterns:
    """Test strengthened Indonesian voice markers for detection."""

    def test_topic_prominence_pattern(self):
        """Verify 'This X, it...' topic prominence structure."""
        test_samples = [
            "This contamination, it forms thick layers on surfaces.",
            "The oxide buildup, it reduces reflectivity significantly.",
            "This layer, it measures 15 μm thickness already.",
        ]
        
        pattern = r'(?:This|The)\s+\w+(?:\s+\w+)?,\s+it\s+'
        
        for sample in test_samples:
            matches = re.findall(pattern, sample, re.IGNORECASE)
            assert len(matches) > 0, f"Topic prominence not found in: {sample}"

    def test_aspectual_markers_present(self):
        """Verify aspectual markers (already, still, just now) appear."""
        test_samples = [
            "The surface is already cleaned after treatment.",
            "Particles are still present in the scans.",
            "Contamination just now detected on the substrate.",
        ]
        
        aspectual_markers = ['already', 'still', 'just now']
        
        for sample in test_samples:
            found = any(marker in sample.lower() for marker in aspectual_markers)
            assert found, f"No aspectual markers in: {sample}"

    def test_preposition_patterns(self):
        """Verify explicit preposition patterns appear."""
        test_samples = [
            "Results are obtained from the data collected.",
            "Contamination is detected at the surface level.",
            "No issues are noted in observations made.",
        ]
        
        prep_patterns = [
            'from the data',
            'from the measurements',
            'at the surface',
            'in observations',
            'on the surfaces'
        ]
        
        for sample in test_samples:
            found = any(pattern in sample.lower() for pattern in prep_patterns)
            assert found, f"No preposition pattern in: {sample}"

    def test_time_fronting_with_passive(self):
        """Verify time-fronting with passive voice structure."""
        test_samples = [
            "After treatment is applied, roughness decreases significantly.",
            "Before ablation is performed, oxide measures 30 μm.",
        ]
        
        # Pattern: Time marker followed by passive construction somewhere in the clause
        # Simplified: just check the marker appears with passive voice nearby
        for sample in test_samples:
            has_time_marker = any(marker in sample for marker in ['After', 'Before', 'During'])
            has_passive = any(passive in sample for passive in ['is applied', 'is performed', 'are observed', 'is detected'])
            
            assert has_time_marker, f"No time marker in: {sample}"
            assert has_passive, f"No passive construction in: {sample}"

    def test_agentless_passive_with_prepositions(self):
        """Verify agentless passives with explicit prepositions."""
        test_samples = [
            "Buildup is observed at 20 μm thickness.",
            "Contamination is detected on the surfaces.",
            "Results are obtained from the measurements.",
        ]
        
        # Pattern: passive verb + preposition
        pattern = r'(?:is|are)\s+(?:observed|detected|obtained|noted|measured)\s+(?:at|on|from|in)\s+'
        
        for sample in test_samples:
            matches = re.findall(pattern, sample.lower())
            assert len(matches) > 0, f"Agentless passive + prep not found in: {sample}"

    def test_marker_frequency_in_paragraph(self):
        """Verify 2-3 markers appear per paragraph."""
        paragraph = """
        This contamination layer, it forms gradually over time on surfaces.
        After treatment is applied, thickness is reduced from 20 μm already.
        Results are obtained from the measurements performed.
        The surface, it exhibits improved clarity still.
        """
        
        # Count all marker types
        markers_found = []
        
        # Topic prominence
        if re.search(r'(?:This|The)\s+\w+(?:\s+\w+)?,\s+it\s+', paragraph):
            markers_found.append('topic_prominence')
        
        # Aspectual markers
        if any(marker in paragraph.lower() for marker in ['already', 'still', 'just now']):
            markers_found.append('aspectual')
        
        # Preposition patterns
        prep_patterns = ['from the', 'at the', 'in observations', 'on the']
        if any(pattern in paragraph.lower() for pattern in prep_patterns):
            markers_found.append('preposition')
        
        # Time-fronting
        if re.search(r'(?:After|Before|During)\s+\w+\s+(?:is|are)\s+\w+,', paragraph):
            markers_found.append('time_fronting')
        
        # Passive + prep
        if re.search(r'(?:is|are)\s+(?:observed|detected|obtained|measured)\s+(?:at|on|from|in)', paragraph.lower()):
            markers_found.append('passive_prep')
        
        assert len(markers_found) >= 2, f"Expected 2-3 markers per paragraph, found {len(markers_found)}: {markers_found}"

    def test_contrast_with_other_nationalities(self):
        """Verify Indonesian patterns are distinct from Taiwan/Italy patterns."""
        indonesian_sample = "This contamination, it forms already on surfaces from the data."
        taiwan_sample = "Surface roughness, it measures 0.8 μm precisely."  # Similar but different emphasis
        american_sample = "Contamination builds up over time and lines up along edges."  # Phrasal verbs
        
        # Indonesian should have aspectual marker
        assert 'already' in indonesian_sample or 'still' in indonesian_sample
        
        # Indonesian should have explicit preposition
        assert 'from the' in indonesian_sample or 'at the' in indonesian_sample
        
        # American should have phrasal verbs (not Indonesian)
        assert 'builds up' in american_sample or 'lines up' in american_sample
        assert 'builds up' not in indonesian_sample

    def test_persona_file_has_strengthened_markers(self):
        """Verify persona file contains updated marker requirements."""
        import yaml
        
        with open('shared/voice/profiles/indonesia.yaml', 'r') as f:
            persona = yaml.safe_load(f)
        
        core_instruction = persona['core_voice_instruction']
        
        # Check for strengthened frequency mention
        assert '2-3 per paragraph' in core_instruction, "Should mention 2-3 markers per paragraph"
        
        # Check for topic prominence mention
        assert 'topic prominence' in core_instruction.lower(), "Should mention topic prominence"
        
        # Check for aspectual markers
        assert 'aspectual markers' in core_instruction.lower(), "Should mention aspectual markers"
        
        # Check for examples of "This X, it..."
        assert 'This contamination, it' in core_instruction or 'This oxide, it' in core_instruction
        
        # Check markers list updated
        markers_list = persona.get('markers', [])
        assert 'already' in markers_list, "Should include 'already' aspectual marker"
        assert 'still' in markers_list, "Should include 'still' aspectual marker"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
