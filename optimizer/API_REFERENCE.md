# Z-Beam Optimizer API Reference

## Core Classes

### ContentOptimizationOrchestrator

Main orchestration class for content optimization workflows.

#### Methods

##### `__init__(ai_service=None, workflow_service=None)`
Initialize the optimization orchestrator.

**Parameters:**
- `ai_service` (Optional[AIDetectionOptimizationService]): AI detection service instance
- `workflow_service` (Optional[IterativeWorkflowService]): Workflow service instance

**Example:**
```python
orchestrator = ContentOptimizationOrchestrator()
```

##### `async optimize_content(content, material_name, config=None, iteration_function=None, **kwargs)`
Optimize content using the decoupled optimization system.

**Parameters:**
- `content` (str): Content to optimize
- `material_name` (str): Name of the material for context
- `config` (Optional[OptimizationConfig]): Optimization configuration
- `iteration_function` (Optional[Callable]): Custom iteration function
- `**kwargs`: Additional parameters for iteration function

**Returns:**
- `OptimizationResult`: Optimization results

**Example:**
```python
result = await orchestrator.optimize_content(
    content="Original content...",
    material_name="silicon_nitride",
    config=OptimizationConfig(target_score=75.0)
)
```

##### `async batch_optimize(content_items, config=None)`
Optimize multiple content items in batch.

**Parameters:**
- `content_items` (Dict[str, str]): Dict of material_name -> content
- `config` (Optional[OptimizationConfig]): Optimization configuration

**Returns:**
- `Dict[str, OptimizationResult]`: Optimization results for each item

**Example:**
```python
results = await orchestrator.batch_optimize({
    "silicon_nitride": content1,
    "aluminum_oxide": content2
})
```

### AIDetectionOptimizationService

AI Detection Optimization Service with caching and batch processing.

#### Methods

##### `__init__(config)`
Initialize the AI detection service.

**Parameters:**
- `config` (ServiceConfiguration): Service configuration

##### `async detect_ai_content(content)`
Detect AI content in the given text.

**Parameters:**
- `content` (str): Content to analyze

**Returns:**
- `AIDetectionResult`: Detection results

**Example:**
```python
result = await service.detect_ai_content("Content to analyze...")
print(f"Score: {result.score}, Classification: {result.classification}")
```

##### `async batch_detect_ai_content(contents)`
Detect AI content in multiple texts.

**Parameters:**
- `contents` (List[str]): List of content strings

**Returns:**
- `List[AIDetectionResult]`: Detection results for each content

##### `optimize_detection_thresholds(historical_results=None, target_accuracy=0.9)`
Optimize detection thresholds based on historical data.

**Parameters:**
- `historical_results` (Optional[List]): Historical detection results
- `target_accuracy` (float): Target accuracy level

**Returns:**
- `Dict[str, Any]`: Optimization recommendations

### IterativeWorkflowService

Service for managing iterative workflows with various strategies and exit conditions.

#### Methods

##### `__init__(config)`
Initialize the iterative workflow service.

**Parameters:**
- `config` (ServiceConfiguration): Service configuration

##### `async run_iterative_workflow(workflow_id, initial_input, iteration_function, quality_function, workflow_config=None)`
Run an iterative workflow.

**Parameters:**
- `workflow_id` (str): Unique workflow identifier
- `initial_input` (Any): Initial input for the workflow
- `iteration_function` (Callable): Function to perform iteration
- `quality_function` (Callable): Function to assess quality
- `workflow_config` (Optional[WorkflowConfiguration]): Workflow configuration

**Returns:**
- `WorkflowResult`: Complete workflow result

**Example:**
```python
result = await service.run_iterative_workflow(
    workflow_id="optimization_123",
    initial_input=content,
    iteration_function=my_iteration_func,
    quality_function=my_quality_func
)
```

##### `get_workflow_status(workflow_id)`
Get status of a workflow.

**Parameters:**
- `workflow_id` (str): Workflow identifier

**Returns:**
- `Optional[Dict[str, Any]]`: Workflow status information

##### `cancel_workflow(workflow_id)`
Cancel a running workflow.

**Parameters:**
- `workflow_id` (str): Workflow identifier

**Returns:**
- `bool`: True if cancelled successfully

## Configuration Classes

### OptimizationConfig

Configuration for content optimization.

#### Attributes
- `target_score` (float): Target AI detection score (default: 75.0)
- `max_iterations` (int): Maximum iterations (default: 5)
- `improvement_threshold` (float): Minimum improvement threshold (default: 3.0)
- `time_limit_seconds` (Optional[float]): Time limit in seconds

**Example:**
```python
config = OptimizationConfig(
    target_score=80.0,
    max_iterations=7,
    improvement_threshold=5.0
)
```

### ServiceConfiguration

Configuration for a service.

#### Attributes
- `name` (str): Service name
- `version` (str): Service version (default: "1.0.0")
- `enabled` (bool): Whether service is enabled (default: True)
- `settings` (Optional[Dict[str, Any]]): Service-specific settings

**Example:**
```python
config = ServiceConfiguration(
    name="ai_detection_service",
    settings={
        "target_score": 75.0,
        "max_iterations": 5,
        "cache_ttl_hours": 1
    }
)
```

### WorkflowConfiguration

Configuration for iterative workflows.

#### Attributes
- `max_iterations` (int): Maximum iterations (default: 10)
- `quality_threshold` (float): Quality threshold (default: 0.9)
- `time_limit_seconds` (Optional[float]): Time limit in seconds
- `iteration_strategy` (IterationStrategy): Iteration strategy (default: LINEAR)
- `exit_conditions` (List[ExitCondition]): Exit conditions
- `convergence_threshold` (float): Convergence threshold (default: 0.01)
- `backoff_factor` (float): Backoff factor for exponential strategy (default: 2.0)

**Example:**
```python
config = WorkflowConfiguration(
    max_iterations=8,
    quality_threshold=0.85,
    time_limit_seconds=300,
    iteration_strategy=IterationStrategy.ADAPTIVE
)
```

## Result Classes

### OptimizationResult

Result of content optimization.

#### Attributes
- `success` (bool): Whether optimization was successful
- `original_content` (str): Original content
- `optimized_content` (str): Optimized content
- `original_score` (float): Original AI detection score
- `final_score` (float): Final AI detection score
- `iterations_performed` (int): Number of iterations performed
- `total_time` (float): Total optimization time in seconds
- `improvement` (float): Score improvement
- `metadata` (Dict[str, Any]): Additional metadata

**Example:**
```python
if result.success:
    print(f"Improved from {result.original_score} to {result.final_score}")
    print(f"Content: {result.optimized_content}")
```

### WorkflowResult

Result of an iterative workflow.

#### Attributes
- `workflow_id` (str): Workflow identifier
- `success` (bool): Whether workflow was successful
- `iterations` (List[IterationResult]): List of iteration results
- `final_result` (Any): Final workflow result
- `exit_reason` (str): Reason workflow exited
- `total_time` (float): Total workflow time in seconds
- `metadata` (Dict[str, Any]): Additional metadata

### AIDetectionResult

Result of AI detection analysis.

#### Attributes
- `score` (float): AI detection score (0-100)
- `confidence` (float): Confidence in classification
- `classification` (str): Classification ('human', 'ai', 'unclear')
- `provider` (str): AI detection provider
- `processing_time` (float): Processing time in seconds
- `details` (Optional[Dict[str, Any]]): Additional detection details

## Enums

### IterationStrategy
Strategies for controlling iteration timing and behavior.

#### Values
- `LINEAR`: Linear iteration timing
- `EXPONENTIAL_BACKOFF`: Exponential backoff timing
- `ADAPTIVE`: Adaptive timing based on progress

### ExitCondition
Conditions that can cause workflow termination.

#### Values
- `QUALITY_THRESHOLD`: Quality threshold reached
- `MAX_ITERATIONS`: Maximum iterations reached
- `TIME_LIMIT`: Time limit exceeded
- `CONVERGENCE`: Convergence achieved
- `MANUAL`: Manual termination

## Utility Functions

### Convenience Functions

#### `async optimize_content_simple(content, material_name, target_score=75.0, max_iterations=5)`
Simple function to optimize content with default settings.

**Parameters:**
- `content` (str): Content to optimize
- `material_name` (str): Material name for context
- `target_score` (float): Target AI detection score
- `max_iterations` (int): Maximum iterations

**Returns:**
- `OptimizationResult`: Optimization results

**Example:**
```python
result = await optimize_content_simple(
    content="Content to optimize...",
    material_name="silicon_nitride",
    target_score=80.0
)
```

#### `async batch_optimize_materials(materials_content, target_score=75.0, max_iterations=5)`
Optimize multiple materials in batch.

**Parameters:**
- `materials_content` (Dict[str, str]): Dict of material_name -> content
- `target_score` (float): Target AI detection score
- `max_iterations` (int): Maximum iterations

**Returns:**
- `Dict[str, OptimizationResult]`: Results for each material

**Example:**
```python
results = await batch_optimize_materials({
    "silicon_nitride": content1,
    "aluminum_oxide": content2
})
```

### Service Management Functions

#### `initialize_optimizer_services()`
Initialize all optimizer services.

**Returns:**
- `Dict[str, Any]`: Initialization results

**Example:**
```python
init_result = initialize_optimizer_services()
if init_result["success"]:
    print("Services initialized successfully")
```

#### `get_optimizer_service(service_name)`
Get an optimizer service by name.

**Parameters:**
- `service_name` (str): Name of the service

**Returns:**
- Service instance or None

#### `get_optimizer_status()`
Get status of all optimizer services.

**Returns:**
- `Dict[str, Any]`: Service status information

#### `cleanup_optimizer_services()`
Clean up all optimizer services.

## Error Classes

### OptimizerError
Base exception for optimizer errors.

#### Attributes
- `message` (str): Error message
- `service` (Optional[str]): Service that caused the error
- `recoverable` (bool): Whether error is recoverable

### AIDetectionError
Exception raised for AI detection errors.

### ServiceConfigurationError
Exception raised when service configuration is invalid.

### IterativeWorkflowError
Exception raised when iterative workflow operations fail.

## Examples

### Basic Optimization
```python
from optimizer.optimization_orchestrator import optimize_content_simple

# Optimize content
result = await optimize_content_simple(
    content="Original content about laser cleaning...",
    material_name="silicon_nitride",
    target_score=75.0
)

if result.success:
    print(f"✅ Optimization successful!")
    print(f"Score improved: {result.original_score} → {result.final_score}")
    print(f"Optimized content: {result.optimized_content}")
else:
    print(f"❌ Optimization failed: {result.error_message}")
```

### Advanced Orchestration
```python
from optimizer.optimization_orchestrator import ContentOptimizationOrchestrator
from optimizer.services import ServiceConfiguration

# Configure services
ai_config = ServiceConfiguration(
    name="ai_detection_service",
    settings={"target_score": 75.0, "max_iterations": 5}
)

# Initialize orchestrator
orchestrator = ContentOptimizationOrchestrator()

# Custom optimization config
from optimizer.optimization_orchestrator import OptimizationConfig
config = OptimizationConfig(
    target_score=80.0,
    max_iterations=7,
    improvement_threshold=5.0
)

# Optimize content
result = await orchestrator.optimize_content(
    content="Content to optimize...",
    material_name="aluminum_oxide",
    config=config
)

print(f"Final score: {result.final_score}")
print(f"Iterations: {result.iterations_performed}")
print(f"Total time: {result.total_time:.2f}s")
```

### Batch Processing
```python
from optimizer.optimization_orchestrator import batch_optimize_materials

# Prepare content batch
materials_content = {
    "silicon_nitride": "Content about silicon nitride...",
    "aluminum_oxide": "Content about aluminum oxide...",
    "titanium_dioxide": "Content about titanium dioxide..."
}

# Batch optimize
results = await batch_optimize_materials(
    materials_content=materials_content,
    target_score=75.0,
    max_iterations=5
)

# Process results
for material, result in results.items():
    if result.success:
        print(f"✅ {material}: {result.final_score}")
    else:
        print(f"❌ {material}: Failed")
```

### Quality Scoring Only
```python
from optimizer.text_optimization.validation.content_scorer import create_content_scorer

# Create scorer
scorer = create_content_scorer(human_threshold=80.0)

# Score content
score = scorer.score_content(
    content="Content to score...",
    material_data={"name": "silicon_nitride"},
    author_info={"id": 1}
)

print(f"Overall score: {score.overall_score}/100")
print(f"Human believability: {score.human_believability}/100")
print(f"Retry recommended: {score.retry_recommended}")
```

### Service Health Check
```python
from optimizer.service_initializer import get_optimizer_status

# Check service health
status = get_optimizer_status()

print("Service Status:")
for service_name, service_info in status['services'].items():
    health = "✅" if service_info['healthy'] else "❌"
    print(f"  {health} {service_name}: {service_info['class']}")
```

This API reference provides comprehensive documentation for all optimizer system components, making it easy for developers and AI systems to understand and use the optimization capabilities.</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/optimizer/API_REFERENCE.md
