"""
Simple validation test for Phase 1 architecture foundation.
"""

import asyncio
from typing import Protocol

# Test basic imports work
try:
    from domain import (
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
    print("✅ Domain imports successful")
except ImportError as e:
    print(f"❌ Domain import failed: {e}")
    exit(1)

try:
    from infrastructure.di import ModernServiceContainer
    from infrastructure.configuration import ConfigProvider, Environment
    print("✅ Infrastructure imports successful")
except ImportError as e:
    print(f"❌ Infrastructure import failed: {e}")
    exit(1)

try:
    from domain.services import WordBudgetDomainService, ContentQualityDomainService
    print("✅ Domain services imports successful")
except ImportError as e:
    print(f"❌ Domain services import failed: {e}")
    exit(1)

try:
    from application.commands import GenerateContentCommand, AnalyzeContentCommand
    print("✅ Application commands imports successful")
except ImportError as e:
    print(f"❌ Application commands import failed: {e}")
    exit(1)


class ITestService(Protocol):
    """Test service interface."""
    def get_value(self) -> str:
        ...


class TestServiceImpl:
    """Test service implementation."""
    def __init__(self):
        self.value = "test"
    
    def get_value(self) -> str:
        return self.value


def test_domain_models():
    """Test basic domain model functionality."""
    print("\n🧪 Testing Domain Models...")
    
    # Test SectionSpec
    spec = SectionSpec(
        name="introduction",
        section_type=SectionType.INTRODUCTION,
        word_budget=200,
        max_iterations=3,
        priority=1
    )
    assert spec.name == "introduction"
    assert spec.is_high_priority()
    print("  ✅ SectionSpec works")
    
    # Test WordBudget
    allocations = {"intro": 200, "body": 400}
    budget = WordBudget(total_words=600, section_allocations=allocations)
    assert budget.total_words == 600
    assert budget.get_section_budget("intro") == 200
    print("  ✅ WordBudget works")
    
    # Test GenerationSettings
    settings = GenerationSettings.create_default(Provider.GEMINI)
    assert settings.api_settings.provider == Provider.GEMINI
    assert settings.should_run_ai_detection()
    print("  ✅ GenerationSettings works")
    
    # Test DetectionResult
    result = DetectionResult.create_passed(
        ai_score=20.0,
        human_score=80.0,
        ai_confidence=0.9,
        human_confidence=0.85,
        iteration=1
    )
    assert result.status == DetectionStatus.PASSED
    assert result.passes_thresholds(25.0, 75.0)
    print("  ✅ DetectionResult works")


async def test_di_container():
    """Test dependency injection container."""
    print("\n🧪 Testing DI Container...")
    
    container = ModernServiceContainer()
    
    # Test singleton registration
    container.register_singleton(ITestService, TestServiceImpl)
    
    service1 = await container.resolve(ITestService)
    service2 = await container.resolve(ITestService)
    
    assert service1 is service2  # Same instance
    assert service1.get_value() == "test"
    print("  ✅ Singleton registration/resolution works")
    
    # Test transient registration
    container2 = ModernServiceContainer()
    container2.register_transient(ITestService, TestServiceImpl)
    
    service3 = await container2.resolve(ITestService)
    service4 = await container2.resolve(ITestService)
    
    assert service3 is not service4  # Different instances
    assert service3.get_value() == "test"
    print("  ✅ Transient registration/resolution works")
    
    # Test service info
    info = container.get_service_info(ITestService)
    assert info['interface'] == 'ITestService'
    assert info['lifetime'] == 'singleton'
    print("  ✅ Service info works")
    
    # Test scoped services
    container3 = ModernServiceContainer()
    container3.register_scoped(ITestService, TestServiceImpl)
    
    async with container3.create_scope() as scope:
        scoped1 = await scope.resolve(ITestService)
        scoped2 = await scope.resolve(ITestService)
        assert scoped1 is scoped2  # Same within scope
    print("  ✅ Scoped services work")


def test_configuration():
    """Test configuration system."""
    print("\n🧪 Testing Configuration...")
    
    provider = ConfigProvider("development")
    config = provider.get_config()
    
    assert config.environment == Environment.DEVELOPMENT
    assert config.debug is True
    print("  ✅ Configuration provider works")
    
    gen_config = provider.get_generation_config()
    assert gen_config.temperature_settings.content_generation == 0.6
    assert gen_config.threshold_settings.ai_threshold == 25.0
    print("  ✅ Generation config works")


def test_domain_services():
    """Test domain services."""
    print("\n🧪 Testing Domain Services...")
    
    # Test WordBudgetDomainService
    budget_service = WordBudgetDomainService()
    
    sections = [
        SectionSpec("intro", SectionType.INTRODUCTION, 100, 3, priority=1),
        SectionSpec("comparison", SectionType.COMPARISON, 200, 3, priority=2),
    ]
    
    budget = budget_service.calculate_optimal_allocation(1000, sections)
    assert budget.total_words == 1000
    assert sum(budget.section_allocations.values()) == 1000
    print("  ✅ WordBudgetDomainService works")
    
    # Test ContentQualityDomainService
    quality_service = ContentQualityDomainService()
    
    content = "This is test content with good structure."
    assessment = quality_service.assess_content_quality(
        content=content,
        ai_score=20.0,
        human_score=80.0,
        word_target=10
    )
    
    assert 'quality_score' in assessment
    assert 'grade' in assessment
    assert assessment['quality_score'] > 0
    print("  ✅ ContentQualityDomainService works")


def test_application_commands():
    """Test application commands."""
    print("\n🧪 Testing Application Commands...")
    
    # Test GenerateContentCommand
    command = GenerateContentCommand(
        material="Bronze",
        sections=["introduction", "comparison"],
        total_word_budget=1200,
        max_iterations_per_section=5,
        provider=Provider.GEMINI
    )
    
    assert command.material == "Bronze"
    assert len(command.sections) == 2
    print("  ✅ GenerateContentCommand works")
    
    # Test AnalyzeContentCommand
    analyze_cmd = AnalyzeContentCommand(
        content="Test content for analysis",
        analysis_type="comprehensive",
        provider=Provider.GEMINI
    )
    
    assert analyze_cmd.content == "Test content for analysis"
    assert analyze_cmd.analysis_type == "comprehensive"
    print("  ✅ AnalyzeContentCommand works")


async def main():
    """Run all tests."""
    print("🧪 Running Phase 1 Architecture Foundation Tests...\n")
    
    test_domain_models()
    await test_di_container()
    test_configuration()
    test_domain_services()
    test_application_commands()
    
    print("\n🎉 All Phase 1 foundation tests passed!")
    print("📝 Foundation is ready for Phase 2 implementation")
    print("\n📊 Phase 1 Summary:")
    print("  ✅ Clean architecture structure created")
    print("  ✅ Enhanced domain models with value objects")
    print("  ✅ Modern DI container with lifecycle management")
    print("  ✅ Environment-aware configuration system")
    print("  ✅ Domain services for business logic")
    print("  ✅ Application command patterns")
    print("\n🚀 Ready to proceed with Phase 2: Core Services")


if __name__ == "__main__":
    asyncio.run(main())
