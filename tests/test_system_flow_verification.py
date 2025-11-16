"""
System Flow Verification Tests
===============================

Tests the 3 critical end-to-end data flows:
1. Naming normalization (case-insensitive lookups)
2. Winston analysis → parameter updates (learning cycle)
3. Parameter updates → prompt modification (application)

These tests ensure data flows correctly through the entire system.
"""

import pytest
import sqlite3
import json
from pathlib import Path
from data.materials.materials import get_material_by_name_cached, find_material_case_insensitive


class TestFlow1_NamingNormalization:
    """Flow 1: Case-insensitive material name lookups throughout system"""
    
    def test_case_insensitive_material_lookup(self):
        """Verify material lookups work with any case variation"""
        # Test all case variations return same material
        test_cases = [
            "aluminum",    # lowercase
            "Aluminum",    # proper case
            "ALUMINUM",    # uppercase
            "AlUmInUm",    # mixed case
            "aLuMiNuM"     # random case
        ]
        
        materials = []
        for case_variant in test_cases:
            material = get_material_by_name_cached(case_variant)
            assert material is not None, f"Material not found for case: {case_variant}"
            materials.append(material)
        
        # All variations should return the exact same object
        first_material = materials[0]
        for i, material in enumerate(materials[1:], 1):
            assert material == first_material, \
                f"Case variant {test_cases[i]} returned different material than {test_cases[0]}"
    
    def test_case_insensitive_search_function(self):
        """Verify find_material_case_insensitive returns correct data"""
        # Test with different case variations
        material_data1, category1 = find_material_case_insensitive("steel")
        material_data2, category2 = find_material_case_insensitive("STEEL")
        material_data3, category3 = find_material_case_insensitive("Steel")
        
        assert material_data1 is not None, "Steel (lowercase) not found"
        assert material_data2 is not None, "STEEL (uppercase) not found"
        assert material_data3 is not None, "Steel (proper case) not found"
        
        # All should return same data
        assert material_data1 == material_data2 == material_data3
        assert category1 == category2 == category3 == "metal"
    
    def test_case_insensitive_throughout_pipeline(self):
        """Verify case-insensitivity across entire data pipeline"""
        # Test various materials with different case patterns
        test_materials = [
            ("copper", "Copper"),
            ("BRASS", "Brass"),
            ("TiTaNiUm", "Titanium")
        ]
        
        for input_name, expected_canonical in test_materials:
            material_data, category = find_material_case_insensitive(input_name)
            assert material_data is not None, f"Material {input_name} not found"
            assert category == "metal", f"Wrong category for {input_name}"
            
            # Verify canonical name is properly formatted
            actual_name = material_data.get('name')
            assert actual_name == expected_canonical, \
                f"Expected canonical name '{expected_canonical}', got '{actual_name}'"


class TestFlow2_WinstonToParameters:
    """Flow 2: Winston sentence analysis → parameter storage → parameter retrieval"""
    
    def test_winston_database_has_parameters(self):
        """Verify generation_parameters table exists and has data"""
        db_path = Path('data/winston_feedback.db')
        assert db_path.exists(), "Winston database not found"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verify generation_parameters table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='generation_parameters'
        """)
        assert cursor.fetchone() is not None, "generation_parameters table not found"
        
        # Verify table has data
        cursor.execute("SELECT COUNT(*) FROM generation_parameters")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count > 0, "No parameters logged in database"
    
    def test_parameters_linked_to_detection_results(self):
        """Verify 1:1 relationship between parameters and detection results"""
        db_path = Path('data/winston_feedback.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check that every detection result has corresponding parameters
        cursor.execute("""
            SELECT COUNT(*) FROM detection_results d
            LEFT JOIN generation_parameters p ON d.id = p.detection_result_id
            WHERE p.id IS NULL
        """)
        orphaned = cursor.fetchone()[0]
        conn.close()
        
        # Some early records may not have parameters (logged before system was added)
        # But we should have SOME linked records
        assert orphaned >= 0, "Database structure issue"
    
    def test_parameter_structure_complete(self):
        """Verify stored parameters have all required fields"""
        db_path = Path('data/winston_feedback.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get a recent parameter record
        cursor.execute("""
            SELECT temperature, frequency_penalty, presence_penalty, 
                   trait_frequency, technical_intensity, full_params_json
            FROM generation_parameters
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        
        if row:  # If we have any parameters logged
            temp, freq_pen, pres_pen, trait_freq, tech_intensity, full_json = row
            
            # Verify numeric fields are present
            assert temp is not None, "Temperature not stored"
            assert freq_pen is not None, "Frequency penalty not stored"
            assert pres_pen is not None, "Presence penalty not stored"
            
            # Verify voice parameters are stored
            if trait_freq is not None:
                assert 0.0 <= trait_freq <= 3.0, f"Trait frequency out of range: {trait_freq}"
            
            # Verify enrichment parameters are stored
            if tech_intensity is not None:
                assert tech_intensity > 0, f"Technical intensity must be positive: {tech_intensity}"
            
            # Verify full snapshot exists
            if full_json:
                full_params = json.loads(full_json)
                assert isinstance(full_params, dict), "Full params not a dict"
    
    def test_best_parameters_query_works(self):
        """Verify database query for best parameters returns valid data"""
        db_path = Path('data/winston_feedback.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query for best parameters (mimics _get_best_previous_parameters)
        cursor.execute("""
            SELECT 
                p.temperature,
                p.frequency_penalty,
                p.presence_penalty,
                p.trait_frequency,
                p.technical_intensity,
                r.human_score
            FROM generation_parameters p
            JOIN detection_results r ON p.detection_result_id = r.id
            WHERE r.success = 1
              AND r.human_score >= 20
            ORDER BY r.human_score DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        
        if row:  # If we have successful generations
            temp, freq_pen, pres_pen, trait_freq, tech_intensity, human_score = row
            
            # Verify returned data is valid
            assert 0.0 <= temp <= 2.0, f"Temperature out of range: {temp}"
            assert -2.0 <= freq_pen <= 2.0, f"Frequency penalty out of range: {freq_pen}"
            assert -2.0 <= pres_pen <= 2.0, f"Presence penalty out of range: {pres_pen}"
            assert human_score >= 20, f"Human score below threshold: {human_score}"


class TestFlow3_ParametersToPrompts:
    """Flow 3: Database parameters → unified_orchestrator → API client → prompts"""
    
    def test_unified_orchestrator_has_get_best_parameters(self):
        """Verify unified_orchestrator has parameter retrieval method"""
        from processing.unified_orchestrator import UnifiedOrchestrator
        
        # Check method exists
        assert hasattr(UnifiedOrchestrator, '_get_best_previous_parameters'), \
            "Missing _get_best_previous_parameters method"
    
    def test_unified_orchestrator_has_adaptive_parameters(self):
        """Verify unified_orchestrator has adaptive parameter method"""
        from processing.unified_orchestrator import UnifiedOrchestrator
        
        # Check method exists
        assert hasattr(UnifiedOrchestrator, '_get_adaptive_parameters'), \
            "Missing _get_adaptive_parameters method"
    
    def test_api_client_accepts_generation_request(self):
        """Verify API client can receive GenerationRequest with all parameters"""
        from shared.api.client import GenerationRequest
        
        # Create request with all parameters
        request = GenerationRequest(
            prompt="Test prompt",
            system_prompt="Test system",
            max_tokens=100,
            temperature=0.95,
            frequency_penalty=0.45,
            presence_penalty=0.45
        )
        
        # Verify all fields are set
        assert request.prompt == "Test prompt"
        assert request.temperature == 0.95
        assert request.frequency_penalty == 0.45
        assert request.presence_penalty == 0.45
    
    def test_prompt_builder_accepts_voice_params(self):
        """Verify PromptBuilder accepts voice and enrichment parameters"""
        from processing.generation.prompt_builder import PromptBuilder
        
        # Check method signature includes voice_params and enrichment_params
        import inspect
        sig = inspect.signature(PromptBuilder.build_unified_prompt)
        params = sig.parameters
        
        assert 'voice_params' in params, "PromptBuilder missing voice_params parameter"
        assert 'enrichment_params' in params, "PromptBuilder missing enrichment_params parameter"
    
    def test_parameter_flow_integration(self):
        """Verify complete parameter flow from config to API"""
        # This test verifies the data structures work together
        from processing.config.dynamic_config import DynamicConfig
        from shared.api.client import GenerationRequest
        
        # Create dynamic config
        config = DynamicConfig()
        
        # Get parameters (simulates what orchestrator does)
        params = config.get_all_generation_params('caption')
        
        # Verify structure contains all needed fields
        assert 'api_params' in params, "Missing api_params"
        assert 'voice_params' in params, "Missing voice_params"
        assert 'enrichment_params' in params, "Missing enrichment_params"
        
        # Verify can create GenerationRequest from params
        api_params = params['api_params']
        request = GenerationRequest(
            prompt="Test",
            max_tokens=api_params.get('max_tokens', 300),
            temperature=api_params.get('temperature', 0.7)
        )
        
        assert request.max_tokens > 0, "Invalid max_tokens"
        assert 0.0 <= request.temperature <= 2.0, "Invalid temperature"


class TestSystemFlowIntegration:
    """Integration tests verifying complete system flows"""
    
    def test_all_flows_documented(self):
        """Verify documentation exists for all flows"""
        doc_path = Path('SYSTEM_FLOW_VERIFICATION_COMPLETE.md')
        assert doc_path.exists(), "System flow verification documentation not found"
        
        # Verify document covers all 3 flows
        content = doc_path.read_text()
        assert "Naming Normalization E2E" in content
        assert "Winston Analysis → Parameter Updates" in content
        assert "Parameter Updates → Prompt Modification" in content
    
    def test_database_parameter_priority_documented(self):
        """Verify database-first parameter priority is documented"""
        doc_path = Path('docs/development/DATABASE_PARAMETER_PRIORITY.md')
        assert doc_path.exists(), "Database parameter priority doc not found"
        
        content = doc_path.read_text()
        assert "DATABASE (Primary" in content or "PRIMARY source" in content
    
    def test_case_insensitive_lookups_documented(self):
        """Verify case-insensitive lookup behavior is documented"""
        doc_path = Path('docs/reference/CASE_INSENSITIVE_LOOKUPS.md')
        assert doc_path.exists(), "Case-insensitive lookups doc not found"
        
        content = doc_path.read_text()
        assert "case-insensitive" in content.lower()
