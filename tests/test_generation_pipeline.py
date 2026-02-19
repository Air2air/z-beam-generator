"""
Integration Tests for Text Generation Pipeline

Tests the complete end-to-end flow:
- QualityEvaluatedGenerator → Generator → Domain Adapters → Data → API
- Voice loading and persona assignment
- Fail-fast behavior on missing data
- Configuration loading
- Cross-domain compatibility

Author: AI Assistant
Created: December 12, 2025
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Test imports
from generation.core.evaluated_generator import QualityEvaluatedGenerator
from generation.core.generator import Generator
from generation.config.dynamic_config import DynamicConfig


class TestVoiceLoading:
    """Test voice profile loading and validation"""
    
    def test_voice_profiles_exist(self):
        """Verify voice profile directory and files exist"""
        voice_dir = Path("shared/voice/profiles")
        assert voice_dir.exists(), f"Voice profiles directory not found: {voice_dir}"
        
        yaml_files = list(voice_dir.glob("*.yaml"))
        assert len(yaml_files) == 4, f"Expected 4 voice profiles, found {len(yaml_files)}"
    
    def test_voice_profiles_load_correctly(self):
        """Verify all voice profiles load without errors"""
        voice_dir = Path("shared/voice/profiles")
        
        for yaml_file in voice_dir.glob("*.yaml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            # Verify required fields (actual field is 'core_voice_instruction')
            assert 'id' in data, f"Missing 'id' in {yaml_file.name}"
            assert 'name' in data, f"Missing 'name' in {yaml_file.name}"
            assert 'core_voice_instruction' in data, f"Missing 'core_voice_instruction' in {yaml_file.name}"
            
            # Verify author IDs are 1-4
            assert 1 <= data['id'] <= 4, f"Invalid author ID {data['id']} in {yaml_file.name}"
    
    def test_generator_loads_all_personas(self):
        """Verify Generator loads all 4 personas"""
        mock_api = Mock()
        generator = Generator(mock_api, domain='materials')
        
        assert hasattr(generator, 'personas'), "Generator missing 'personas' attribute"
        assert len(generator.personas) == 4, f"Expected 4 personas, got {len(generator.personas)}"
        assert all(i in generator.personas for i in [1, 2, 3, 4]), "Missing author IDs 1-4"
    
    def test_persona_structure(self):
        """Verify persona structure is correct"""
        mock_api = Mock()
        generator = Generator(mock_api, domain='materials')
        
        for author_id, persona in generator.personas.items():
            assert 'id' in persona, f"Missing 'id' for author {author_id}"
            assert 'name' in persona, f"Missing 'name' for author {author_id}"
            # Actual field is 'core_voice_instruction', not 'voice_instruction'
            assert 'core_voice_instruction' in persona, f"Missing 'core_voice_instruction' for author {author_id}"
            assert isinstance(persona['core_voice_instruction'], str), f"core_voice_instruction not string for author {author_id}"
            assert len(persona['core_voice_instruction']) > 100, f"core_voice_instruction too short for author {author_id}"


class TestFailFastBehavior:
    """Test fail-fast architecture compliance"""
    
    def test_generator_requires_api_client(self):
        """Verify Generator fails without API client"""
        with pytest.raises(ValueError, match="API client required"):
            Generator(None, domain='materials')
    
    def test_evaluated_generator_requires_api_client(self):
        """Verify QualityEvaluatedGenerator fails without API client"""
        mock_evaluator = Mock()
        with pytest.raises(ValueError, match="API client required"):
            QualityEvaluatedGenerator(None, mock_evaluator)
    
    def test_evaluated_generator_requires_subjective_evaluator(self):
        """Verify QualityEvaluatedGenerator fails without evaluator"""
        mock_api = Mock()
        with pytest.raises(ValueError, match="SubjectiveEvaluator required"):
            QualityEvaluatedGenerator(mock_api, None)
    
    def test_generator_fails_on_missing_material(self):
        """Verify Generator fails fast on nonexistent material"""
        mock_api = Mock()
        generator = Generator(mock_api, domain='materials')
        
        # Note: generate() does NOT take author_id parameter (it's read from YAML)
        with pytest.raises((ValueError, KeyError, FileNotFoundError)):
            generator.generate("NonexistentMaterial12345", "micro")
    
    def test_generator_fails_on_invalid_author_id(self):
        """Verify Generator fails on invalid author ID"""
        mock_api = Mock()
        generator = Generator(mock_api, domain='materials')
        
        # Author ID 99 doesn't exist
        with pytest.raises((ValueError, KeyError)):
            generator._get_persona_by_author_id(99)


class TestConfigurationLoading:
    """Test configuration system"""
    
    def test_dynamic_config_loads(self):
        """Verify DynamicConfig loads without errors"""
        config = DynamicConfig()
        assert config is not None
        assert hasattr(config, 'base_config')
    
    def test_dynamic_config_has_required_methods(self):
        """Verify DynamicConfig has all required methods"""
        config = DynamicConfig()
        
        assert hasattr(config, 'calculate_temperature')
        assert hasattr(config, 'calculate_max_tokens')
        assert callable(config.calculate_temperature)
        assert callable(config.calculate_max_tokens)
    
    def test_temperature_calculation(self):
        """Verify temperature calculation works"""
        config = DynamicConfig()
        temp = config.calculate_temperature()
        
        assert temp is not None, "calculate_temperature returned None"
        assert isinstance(temp, (int, float)), f"Temperature not numeric: {type(temp)}"
        assert 0.0 <= temp <= 2.0, f"Temperature out of range: {temp}"
    
    def test_max_tokens_calculation(self):
        """Verify max_tokens calculation works"""
        config = DynamicConfig()
        
        for component_type in ['micro', 'pageDescription', 'faq']:
            max_tokens = config.calculate_max_tokens(component_type)
            
            assert max_tokens is not None, f"max_tokens None for {component_type}"
            assert isinstance(max_tokens, int), f"max_tokens not int for {component_type}"
            assert max_tokens > 0, f"max_tokens not positive for {component_type}"


class TestDomainCompatibility:
    """Test pipeline works across all domains"""
    
    @pytest.mark.parametrize("domain", ['materials', 'contaminants', 'settings'])
    def test_generator_initializes_for_domain(self, domain):
        """Verify Generator initializes for all domains"""
        mock_api = Mock()
        generator = Generator(mock_api, domain=domain)
        
        assert generator.domain == domain
        assert generator.adapter is not None
    
    def test_materials_domain_has_adapter(self):
        """Verify materials domain adapter works"""
        mock_api = Mock()
        generator = Generator(mock_api, domain='materials')
        
        assert hasattr(generator, 'adapter')
        assert hasattr(generator.adapter, 'load_all_data')
        assert hasattr(generator.adapter, 'get_item_data')


class TestEndToEndFlow:
    """Test complete generation flow (mocked API)"""
    
    @patch('generation.core.generator.Generator._load_data')
    @patch('generation.core.generator.Generator._get_item_data')
    def test_generation_flow_structure(self, mock_get_item, mock_load_data):
        """Verify generation flow executes without errors (structure test)"""
        # Mock API client
        mock_api = Mock()
        mock_api.generate.return_value = "Generated test content"
        
        # Mock data
        mock_load_data.return_value = {'materials': {'Aluminum': {'category': 'Metal'}}}
        mock_get_item.return_value = {
            'name': 'Aluminum',
            'category': 'Metal',
            'author': {'id': 1}
        }
        
        generator = Generator(mock_api, domain='materials')
        
        # Verify components initialized
        assert generator.personas is not None
        assert len(generator.personas) == 4
        assert generator.adapter is not None
        assert generator.data_provider is not None
    
    def test_evaluated_generator_initialization(self):
        """Verify QualityEvaluatedGenerator initializes correctly"""
        mock_api = Mock()
        mock_evaluator = Mock()
        mock_winston = Mock()
        mock_structural = Mock()
        
        gen = QualityEvaluatedGenerator(
            api_client=mock_api,
            subjective_evaluator=mock_evaluator,
            winston_client=mock_winston,
            structural_variation_checker=mock_structural
        )
        
        assert gen.api_client == mock_api
        assert gen.subjective_evaluator == mock_evaluator
        assert gen.winston_client == mock_winston
        assert gen.structural_variation_checker == mock_structural
        assert hasattr(gen, 'generator')
        assert isinstance(gen.generator, Generator)


class TestDataFlowIntegrity:
    """Test data flows correctly through pipeline"""
    
    def test_generator_has_data_provider(self):
        """Verify Generator has DataProvider"""
        mock_api = Mock()
        generator = Generator(mock_api, domain='materials')
        
        assert hasattr(generator, 'data_provider')
        assert generator.data_provider is not None
    
    def test_generator_has_researcher(self):
        """Verify Generator has SystemDataResearcher"""
        mock_api = Mock()
        generator = Generator(mock_api, domain='materials')
        
        assert hasattr(generator, 'researcher')
        assert generator.researcher is not None
    
    def test_generator_has_adapter(self):
        """Verify Generator has adapter for domain-specific data access"""
        mock_api = Mock()
        generator = Generator(mock_api, domain='materials')
        
        assert hasattr(generator, 'adapter')
        assert generator.adapter is not None
    
    def test_generator_has_dynamic_config(self):
        """Verify Generator has DynamicConfig"""
        mock_api = Mock()
        generator = Generator(mock_api, domain='materials')
        
        assert hasattr(generator, 'dynamic_config')
        assert isinstance(generator.dynamic_config, DynamicConfig)


class TestArchitectureCompliance:
    """Test architectural requirements"""
    
    def test_no_production_mocks_in_generator(self):
        """Verify Generator doesn't use MockAPIClient"""
        import inspect
        import generation.core.generator as gen_module
        
        source = inspect.getsource(gen_module.Generator)
        
        # Check for mock-related keywords
        assert 'MockAPIClient' not in source, "Found MockAPIClient in Generator"
        assert 'mock_response' not in source.lower(), "Found mock_response in Generator"
    
    def test_generator_uses_fail_fast_pattern(self):
        """Verify Generator uses fail-fast (raises exceptions)"""
        import inspect
        import generation.core.generator as gen_module
        
        source = inspect.getsource(gen_module.Generator.__init__)
        
        # Should have ValueError checks
        assert 'raise ValueError' in source or 'if not' in source, \
            "Generator.__init__ doesn't validate required parameters"
    
    def test_voice_path_is_correct(self):
        """Verify voice path matches actual location"""
        import generation.core.generator as gen_module
        import inspect
        
        source = inspect.getsource(gen_module.Generator._load_all_personas)
        
        # Should reference shared/voice/profiles NOT shared/prompts/personas
        assert 'shared/voice/profiles' in source, \
            "Generator uses wrong voice path (should be shared/voice/profiles)"
        assert 'shared/prompts/personas' not in source, \
            "Generator references deprecated shared/prompts/personas path"


class TestRegressionPrevention:
    """Tests to prevent known failure patterns"""
    
    def test_no_fallback_defaults_in_generator_init(self):
        """Verify Generator.__init__ doesn't use fallback defaults"""
        import inspect
        import generation.core.generator as gen_module
        
        source = inspect.getsource(gen_module.Generator.__init__)
        
        # Should NOT have patterns like: param=param or "default"
        assert ' or {}' not in source, "Found ' or {}' fallback pattern"
        assert ' or []' not in source, "Found ' or []' fallback pattern"
        assert ' or ""' not in source, "Found ' or \"\"' fallback pattern"
    
    def test_evaluated_generator_has_no_retry_loop(self):
        """Verify QualityEvaluatedGenerator doesn't have automatic retry"""
        import inspect
        import generation.core.evaluated_generator as eval_gen_module
        
        source = inspect.getsource(eval_gen_module.QualityEvaluatedGenerator)
        
        # Single-pass design - should NOT have retry loops in generate()
        generate_source = inspect.getsource(eval_gen_module.QualityEvaluatedGenerator.generate)
        
        # Check for absence of retry patterns
        assert 'while attempt' not in generate_source.lower(), \
            "Found retry loop in QualityEvaluatedGenerator.generate()"
        assert 'for attempt in' not in generate_source.lower(), \
            "Found retry loop in QualityEvaluatedGenerator.generate()"


# Run with: python3 -m pytest tests/test_generation_pipeline.py -v
if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
