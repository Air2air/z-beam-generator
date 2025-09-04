"""
Example usage of the complete service architecture.

This script demonstrates how to use all the new services together:
- AI Detection Optimization Service
- Iterative Workflow Service
- Dynamic Evolution Service
- Quality Assessment Service
- Configuration Optimization Service
"""

import asyncio
import logging
from typing import Any, Dict

from services import (
    ServiceConfiguration,
    service_registry
)
from services.ai_detection_optimization import (
    AIDetectionOptimizationService,
    BatchDetectionRequest
)
from services.iterative_workflow import (
    IterativeWorkflowService,
    WorkflowConfiguration,
    IterationContext
)
from services.dynamic_evolution import (
    DynamicEvolutionService,
    EvolutionStrategy,
    EvolutionTemplate
)
from services.quality_assessment import QualityAssessmentService
from services.configuration_optimizer import (
    ConfigurationOptimizationService,
    OptimizationParameter,
    OptimizationGoal,
    OptimizationStrategy
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_services():
    """Set up all services for demonstration."""
    print("🔧 Setting up services...")

    # AI Detection Service
    ai_config = ServiceConfiguration(
        name="ai_detection_service",
        settings={
            "providers": {
                "mock_provider": {
                    "type": "mock",
                    "mock_score": 0.3,
                    "mock_detected": False
                }
            }
        }
    )
    ai_service = AIDetectionOptimizationService(ai_config)
    service_registry.register_service(ai_service)

    # Iterative Workflow Service
    workflow_config = ServiceConfiguration(name="iterative_workflow_service")
    workflow_service = IterativeWorkflowService(workflow_config)
    service_registry.register_service(workflow_service)

    # Dynamic Evolution Service
    evolution_config = ServiceConfiguration(name="dynamic_evolution_service")
    evolution_service = DynamicEvolutionService(evolution_config)
    service_registry.register_service(evolution_service)

    # Quality Assessment Service
    quality_config = ServiceConfiguration(name="quality_assessment_service")
    quality_service = QualityAssessmentService(quality_config)
    service_registry.register_service(quality_service)

    # Configuration Optimization Service
    optimizer_config = ServiceConfiguration(name="configuration_optimizer_service")
    optimizer_service = ConfigurationOptimizationService(optimizer_config)
    service_registry.register_service(optimizer_service)

    return {
        "ai": ai_service,
        "workflow": workflow_service,
        "evolution": evolution_service,
        "quality": quality_service,
        "optimizer": optimizer_service
    }


async def demonstrate_ai_detection_service(ai_service):
    """Demonstrate AI Detection Service."""
    print("\n🤖 AI Detection Service Demo")

    test_content = "This is a sample piece of content for AI detection analysis."

    result = await ai_service.detect_ai_content(test_content)
    print(f"  📊 Detection Score: {result.score:.3f}")
    print(f"  🎯 Detected as AI: {result.detected}")
    print(f"  🔍 Provider: {result.provider}")

    # Batch processing
    contents = [
        "First piece of content",
        "Second piece of content",
        "Third piece of content"
    ]

    batch_result = await ai_service.batch_detect_ai_content(
        BatchDetectionRequest(contents=contents)
    )
    print(f"  📦 Batch processed {len(contents)} items")
    print(f"  📈 Average score: {batch_result.summary['average_score']:.3f}")
    return result


async def demonstrate_dynamic_evolution_service(evolution_service):
    """Demonstrate Dynamic Evolution Service."""
    print("\n🔄 Dynamic Evolution Service Demo")

    # Register evolution template
    template = evolution_service.register_template(
        template_id="content_improvement",
        base_prompt="Create high-quality content about {topic}",
        evolution_rules={
            "max_improvements": 3,
            "quality_threshold": 0.8
        },
        variables={"topic": "technology"}
    )
    print(f"  📝 Registered template: {template.template_id}")

    # Evolve content
    initial_content = "Create content about AI technology"
    performance_data = {"quality_score": 0.7, "readability_score": 0.6}

    evolved_result = await evolution_service.evolve_content(
        template_id="content_improvement",
        current_content=initial_content,
        performance_data=performance_data,
        evolution_strategy=EvolutionStrategy.GRADUAL
    )
    print(f"  ✨ Evolution Result: {evolved_result.quality_improvement:.1f}% improvement")
    print(f"  📈 New Content: {evolved_result.evolved_content}")

    return evolved_result


async def demonstrate_quality_assessment_service(quality_service):
    """Demonstrate Quality Assessment Service."""
    print("\n📊 Quality Assessment Service Demo")

    test_content = """
    # Introduction to Machine Learning

    Machine learning is a powerful technology that enables computers to learn from data.
    This article explores the fundamentals of ML and its applications in modern technology.

    ## What is Machine Learning?

    Machine learning is a subset of artificial intelligence that focuses on algorithms
    that can learn patterns from data without being explicitly programmed.

    ## Applications

    ML has numerous applications including:
    - Image recognition
    - Natural language processing
    - Predictive analytics
    - Recommendation systems

    ## Conclusion

    Machine learning continues to transform industries and will play an increasingly
    important role in our technological future.
    """

    assessment = await quality_service.assess_quality(
        content=test_content,
        content_type="technical",
        benchmark_id="standard_quality"
    )

    print(f"  🎯 Overall Score: {assessment.overall_score:.3f}")
    print(f"  📈 Grade: {assessment.grade}")
    print(f"  💪 Strengths: {len(assessment.strengths)}")
    print(f"  ⚠️  Weaknesses: {len(assessment.weaknesses)}")
    print(f"  💡 Recommendations: {len(assessment.recommendations)}")

    # Show top strengths and recommendations
    if assessment.strengths:
        print(f"  ✅ Top Strength: {assessment.strengths[0]}")
    if assessment.recommendations:
        print(f"  🎯 Top Recommendation: {assessment.recommendations[0]}")

    return assessment


async def demonstrate_configuration_optimizer_service(optimizer_service):
    """Demonstrate Configuration Optimization Service."""
    print("\n⚙️ Configuration Optimization Service Demo")

    # Register optimization parameters
    parameters = [
        OptimizationParameter(
            name="temperature",
            param_type="float",
            min_value=0.1,
            max_value=1.0,
            default_value=0.7,
            description="Creativity temperature"
        ),
        OptimizationParameter(
            name="max_tokens",
            param_type="int",
            min_value=100,
            max_value=1000,
            default_value=500,
            description="Maximum tokens to generate"
        ),
        OptimizationParameter(
            name="model",
            param_type="categorical",
            choices=["gpt-3.5", "gpt-4", "claude"],
            default_value="gpt-3.5",
            description="AI model to use"
        )
    ]

    optimizer_service.register_optimization_parameters("text_generator", parameters)
    print(f"  📋 Registered {len(parameters)} parameters for text_generator")

    # Create backup of current configuration
    current_config = {
        "temperature": 0.7,
        "max_tokens": 500,
        "model": "gpt-3.5"
    }

    backup = optimizer_service.create_configuration_backup(
        component_name="text_generator",
        configuration=current_config,
        performance_score=0.75,
        description="Baseline configuration"
    )
    print(f"  💾 Created backup: {backup.backup_id}")

    # Simple evaluation function
    async def evaluate_config(config):
        # Simulate configuration evaluation
        score = 0.5
        if config["temperature"] > 0.3:
            score += 0.1
        if config["max_tokens"] > 300:
            score += 0.1
        if config["model"] == "gpt-4":
            score += 0.2
        return min(1.0, score)

    # Run optimization
    optimization_result = await optimizer_service.optimize_configuration(
        component_name="text_generator",
        current_configuration=current_config,
        optimization_goal=OptimizationGoal.MAXIMIZE_QUALITY,
        strategy=OptimizationStrategy.RANDOM_SEARCH,
        max_iterations=5,
        evaluation_function=evaluate_config
    )

    print(f"  🚀 Optimization completed in {optimization_result.iterations_completed} iterations")
    print(f"  📊 Best score: {optimization_result.best_score:.3f}")
    print(f"  📈 Improvement: {optimization_result.improvement_percentage:.1f}%")
    return optimization_result


async def demonstrate_integrated_workflow(services):
    """Demonstrate all services working together."""
    print("\n🔗 Integrated Workflow Demo")
    print("Creating a complete content generation and improvement pipeline...")

    ai_service = services["ai"]
    workflow_service = services["workflow"]
    evolution_service = services["evolution"]
    quality_service = services["quality"]

    # Step 1: Initial content generation
    initial_content = "Create an article about renewable energy technologies"
    print(f"  📝 Initial content: {initial_content}")

    # Step 2: Quality assessment
    initial_assessment = await quality_service.assess_quality(initial_content)
    print(f"  📊 Initial quality: {initial_assessment.overall_score:.3f}")

    # Step 3: AI detection check
    detection_result = await ai_service.detect_ai_content(initial_content)
    print(f"  🤖 AI detection score: {detection_result.score:.3f}")
    # Step 4: Iterative improvement workflow
    async def improve_content_step(content: str, context: IterationContext) -> str:
        """Improve content using multiple services."""
        # Assess current quality
        assessment = await quality_service.assess_quality(content)

        # Apply evolution if quality is low
        if assessment.overall_score < 0.8:
            evolution_result = await evolution_service.evolve_content(
                template_id="content_improvement",
                current_content=content,
                performance_data={"quality_score": assessment.overall_score},
                evolution_strategy=EvolutionStrategy.GRADUAL
            )
            return evolution_result.evolved_content

        return content + " (refined)"

    async def evaluate_quality(content: str) -> float:
        """Evaluate content quality."""
        assessment = await quality_service.assess_quality(content)
        return assessment.overall_score

    # Run iterative improvement
    workflow_config = WorkflowConfiguration(
        max_iterations=3,
        quality_threshold=0.85,
        exit_conditions=["quality_threshold", "max_iterations"]
    )

    final_result = await workflow_service.run_iterative_workflow(
        workflow_id="integrated_content_improvement",
        initial_input=initial_content,
        iteration_function=improve_content_step,
        quality_function=evaluate_quality,
        workflow_config=workflow_config
    )

    # Step 5: Final assessment
    final_assessment = await quality_service.assess_quality(final_result.final_result)
    final_detection = await ai_service.detect_ai_content(final_result.final_result)

    print("  🎉 Final Results:")
    print(f"    📊 Quality Score: {final_assessment.overall_score:.3f} (Grade: {final_assessment.grade})")
    print(f"    🤖 AI Detection: {final_detection.score:.3f}")
    print(f"    🔄 Iterations: {len(final_result.iterations)}")
    print(f"    ⏱️  Total Time: {final_result.total_time:.2f}s")
    print(f"    📝 Final Content: {final_result.final_result}")

    return final_result


async def demonstrate_service_health_and_monitoring():
    """Demonstrate service health monitoring."""
    print("\n🏥 Service Health & Monitoring Demo")

    # Check all services
    health_status = service_registry.health_check_all()
    services_info = service_registry.list_services()

    print("  📊 Service Status:")
    for service_name, is_healthy in health_status.items():
        status = "✅" if is_healthy else "❌"
        version = services_info[service_name].get('version', 'unknown')
        print(f"    {status} {service_name} (v{version})")

    print(f"\n  📈 Total Services: {len(services_info)}")
    print(f"  💚 Healthy Services: {sum(health_status.values())}")


async def main():
    """Run all demonstrations."""
    print("🚀 Z-Beam Generator Service Architecture Demonstration")
    print("=" * 60)

    try:
        # Setup all services
        services = await setup_services()

        # Run individual service demonstrations
        await demonstrate_ai_detection_service(services["ai"])
        await demonstrate_dynamic_evolution_service(services["evolution"])
        await demonstrate_quality_assessment_service(services["quality"])
        await demonstrate_configuration_optimizer_service(services["optimizer"])

        # Run integrated workflow
        await demonstrate_integrated_workflow(services)

        # Show health monitoring
        await demonstrate_service_health_and_monitoring()

        print("\n🎊 All demonstrations completed successfully!")
        print("\n💡 Key Benefits Demonstrated:")
        print("  • Modular service architecture")
        print("  • Service interoperability")
        print("  • Comprehensive quality assessment")
        print("  • AI-powered optimization")
        print("  • Dynamic content evolution")
        print("  • Health monitoring and reliability")

    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
