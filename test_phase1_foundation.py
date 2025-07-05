"""
Test suite for Phase 1 architecture foundation.
Validates domain models, DI container, and configuration system.
"""

import asyncio
from typing import Protocol

# Domain imports
from domain import (
    ContentGenerationRequest,
    SectionSpec,
    WordBudget,
    SectionType,
    GenerationSettings,
    Provider,
    DetectionMode,
    DetectionResult,
    DetectionStatus,
    ContentQuality
)

# Infrastructure imports
from infrastructure.di import (
    ModernServiceContainer,
    ServiceNotRegisteredException
)

from infrastructure.configuration import ConfigProvider, Environment

# Domain services
from domain.services import WordBudgetDomainService, ContentQualityDomainService

# Application commands
from application.commands import GenerateContentCommand, AnalyzeContentCommand


class TestDomainModels:
    """Test domain models and value objects."""
    
    def test_section_spec_creation(self):
        """Test SectionSpec creation and validation."""
        spec = SectionSpec(
            name="introduction",
            section_type=SectionType.INTRODUCTION,
            word_budget=200,
            max_iterations=3,
            priority=1
        )
        
        assert spec.name == "introduction"
        assert spec.section_type == SectionType.INTRODUCTION
        assert spec.word_budget == 200
        assert spec.is_high_priority()
    
    def test_section_spec_validation(self):
        """Test SectionSpec validation rules."""
        with pytest.raises(ValueError, match="Word budget must be positive"):
            SectionSpec(
                name="test",
                section_type=SectionType.INTRODUCTION,
                word_budget=0,
                max_iterations=3
            )
    
    def test_word_budget_creation(self):
        """Test WordBudget creation and methods."""
        allocations = {
            "introduction": 200,
            "comparison": 300,
            "conclusion": 100
        }
        
        budget = WordBudget(total_words=600, section_allocations=allocations)
        
        assert budget.total_words == 600
        assert budget.get_section_budget("introduction") == 200
        assert budget.get_section_budget_with_buffer("introduction") == 220  # 10% buffer
        assert budget.is_within_budget("introduction", 210)
    
    def test_word_budget_balanced_allocation(self):
        """Test balanced word budget allocation."""
        sections = ["intro", "body", "conclusion"]
        budget = WordBudget.create_balanced_allocation(600, sections)
        
        assert budget.total_words == 600
        assert budget.get_section_budget("intro") == 200
        assert budget.get_section_budget("body") == 200
        assert budget.get_section_budget("conclusion") == 200
    
    def test_generation_settings_creation(self):
        """Test GenerationSettings creation."""
        settings = GenerationSettings.create_default(Provider.GEMINI)
        
        assert settings.api_settings.provider == Provider.GEMINI
        assert settings.detection_mode == DetectionMode.COMPREHENSIVE
        assert settings.should_run_ai_detection()
        assert settings.should_run_human_detection()
    
    def test_content_generation_request(self):
        """Test ContentGenerationRequest entity."""
        sections = [
            SectionSpec("intro", SectionType.INTRODUCTION, 200, 3),
            SectionSpec("body", SectionType.COMPARISON, 400, 3)
        ]
        
        budget = WordBudget.create_balanced_allocation(600, ["intro", "body"])
        settings = GenerationSettings.create_default()
        
        request = ContentGenerationRequest(
            material="Bronze",
            sections=sections,
            word_budget=budget,
            settings=settings
        )
        
        assert request.material == "Bronze"
        assert len(request.sections) == 2
        assert request.get_section_by_name("intro") is not None
        assert request.get_total_expected_iterations() == 6
    
    def test_detection_result_creation(self):
        """Test DetectionResult value object."""
        result = DetectionResult.create_passed(
            ai_score=20.0,
            human_score=80.0,
            ai_confidence=0.9,
            human_confidence=0.85,
            iteration=1
        )
        
        assert result.status == DetectionStatus.PASSED
        assert result.quality == ContentQuality.EXCELLENT
        assert result.passes_thresholds(25.0, 75.0)
        assert result.get_quality_score() == 80.0  # (80 + 80) / 2


class ITestService(Protocol):
    """Test service interface."""
    def get_value(self) -> str:
        ...


class TestServiceImpl:
    """Test service implementation."""
    def __init__(self, value: str = "test"):
        self.value = value
    
    def get_value(self) -> str:
        return self.value


class TestDependencyInjection:
    """Test the modern DI container."""
    
    @pytest.fixture
    def container(self):
        """Create a fresh container for each test."""
        return ModernServiceContainer()
    
    def test_register_and_resolve_singleton(self, container):
        """Test singleton service registration and resolution."""
        container.register_singleton(ITestService, TestServiceImpl)
        
        # Should return the same instance
        service1 = asyncio.run(container.resolve(ITestService))
        service2 = asyncio.run(container.resolve(ITestService))
        
        assert service1 is service2
        assert service1.get_value() == "test"
    
    def test_register_and_resolve_transient(self, container):
        """Test transient service registration and resolution."""
        container.register_transient(ITestService, TestServiceImpl)
        
        # Should return different instances
        service1 = asyncio.run(container.resolve(ITestService))
        service2 = asyncio.run(container.resolve(ITestService))
        
        assert service1 is not service2
        assert service1.get_value() == "test"
        assert service2.get_value() == "test"
    
    def test_register_factory(self, container):
        """Test factory registration."""
        def create_service():
            return TestServiceImpl("factory_value")
        
        container.register_singleton(ITestService, factory=create_service)
        
        service = asyncio.run(container.resolve(ITestService))
        assert service.get_value() == "factory_value"
    
    def test_register_instance(self, container):
        """Test instance registration."""
        instance = TestServiceImpl("instance_value")
        container.register_instance(ITestService, instance)
        
        service = asyncio.run(container.resolve(ITestService))
        assert service is instance
        assert service.get_value() == "instance_value"
    
    def test_service_not_registered_exception(self, container):
        """Test exception when service not registered."""
        with pytest.raises(ServiceNotRegisteredException):
            asyncio.run(container.resolve(ITestService))
    
    def test_service_info(self, container):
        """Test service information retrieval."""
        container.register_singleton(ITestService, TestServiceImpl)
        
        info = container.get_service_info(ITestService)
        assert info['interface'] == 'ITestService'
        assert info['implementation'] == 'TestServiceImpl'
        assert info['lifetime'] == 'singleton'
        assert info['access_count'] == 0
        
        # Access the service
        asyncio.run(container.resolve(ITestService))
        
        info = container.get_service_info(ITestService)
        assert info['access_count'] == 1
    
    async def test_service_scope(self, container):
        """Test scoped services."""
        container.register_scoped(ITestService, TestServiceImpl)
        
        async with container.create_scope() as scope1:
            service1a = await scope1.resolve(ITestService)
            service1b = await scope1.resolve(ITestService)
            assert service1a is service1b  # Same instance within scope
        
        async with container.create_scope() as scope2:
            service2 = await scope2.resolve(ITestService)
            assert service1a is not service2  # Different instance in different scope


class TestConfiguration:
    """Test configuration system."""
    
    def test_config_provider_default(self):
        """Test default configuration provider."""
        provider = ConfigProvider("development")
        config = provider.get_config()
        
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is True
        assert config.generation_settings.api_settings.provider == Provider.GEMINI
    
    def test_generation_config(self):
        """Test generation configuration."""
        provider = ConfigProvider("production")
        gen_config = provider.get_generation_config()
        
        assert gen_config.temperature_settings.content_generation == 0.6
        assert gen_config.threshold_settings.ai_threshold == 25.0
        assert gen_config.api_settings.timeout_seconds == 30


class TestDomainServices:
    """Test domain services."""
    
    def test_word_budget_domain_service(self):
        """Test word budget calculation."""
        service = WordBudgetDomainService()
        
        sections = [
            SectionSpec("intro", SectionType.INTRODUCTION, 100, 3, priority=1),
            SectionSpec("comparison", SectionType.COMPARISON, 200, 3, priority=2),
            SectionSpec("conclusion", SectionType.CONCLUSION, 50, 3, priority=3)
        ]
        
        budget = service.calculate_optimal_allocation(1000, sections)
        
        assert budget.total_words == 1000
        assert budget.get_section_budget("intro") > 0
        assert budget.get_section_budget("comparison") > 0
        assert budget.get_section_budget("conclusion") > 0
        
        # Total allocations should equal total words
        total_allocated = sum(budget.section_allocations.values())
        assert total_allocated == 1000
    
    def test_content_quality_domain_service(self):
        """Test content quality assessment."""
        service = ContentQualityDomainService()
        
        content = "This is a test content with multiple sentences. It has good structure and flow."
        assessment = service.assess_content_quality(
            content=content,
            ai_score=20.0,
            human_score=80.0,
            word_target=15
        )
        
        assert 'quality_score' in assessment
        assert 'grade' in assessment
        assert 'suggestions' in assessment
        assert assessment['quality_score'] > 0


class TestApplicationCommands:
    """Test application layer commands."""
    
    def test_generate_content_command(self):
        """Test GenerateContentCommand validation."""
        command = GenerateContentCommand(
            material="Bronze",
            sections=["introduction", "comparison"],
            total_word_budget=1200,
            max_iterations_per_section=5,
            provider=Provider.GEMINI
        )
        
        assert command.material == "Bronze"
        assert len(command.sections) == 2
        assert command.total_word_budget == 1200
    
    def test_generate_content_command_validation(self):
        """Test command validation."""
        with pytest.raises(ValueError, match="Material cannot be empty"):
            GenerateContentCommand(
                material="",
                sections=["introduction"],
                total_word_budget=1200
            )
    
    def test_analyze_content_command(self):
        """Test AnalyzeContentCommand."""
        command = AnalyzeContentCommand(
            content="Test content for analysis",
            analysis_type="comprehensive",
            provider=Provider.GEMINI
        )
        
        assert command.content == "Test content for analysis"
        assert command.analysis_type == "comprehensive"


if __name__ == "__main__":
    # Run basic tests
    print("🧪 Running Phase 1 Architecture Foundation Tests...")
    
    # Test domain models
    test_models = TestDomainModels()
    test_models.test_section_spec_creation()
    test_models.test_word_budget_creation()
    test_models.test_generation_settings_creation()
    print("✅ Domain models tests passed")
    
    # Test DI container
    container = ModernServiceContainer()
    container.register_singleton(ITestService, TestServiceImpl)
    service = asyncio.run(container.resolve(ITestService))
    assert service.get_value() == "test"
    print("✅ DI container tests passed")
    
    # Test configuration
    provider = ConfigProvider("development")
    config = provider.get_config()
    assert config.environment == Environment.DEVELOPMENT
    print("✅ Configuration tests passed")
    
    # Test domain services
    budget_service = WordBudgetDomainService()
    sections = [SectionSpec("test", SectionType.INTRODUCTION, 100, 3)]
    budget = budget_service.calculate_optimal_allocation(1000, sections)
    assert budget.total_words == 1000
    print("✅ Domain services tests passed")
    
    print("🎉 All Phase 1 foundation tests passed!")
    print("📝 Foundation is ready for Phase 2 implementation")
