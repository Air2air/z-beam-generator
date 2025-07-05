# 🏗️ Z-Beam Architecture Refactor Plan

## Current State Analysis

### ✅ Strengths
- Dependency Injection container exists (`ServiceContainer`)
- Interface-based design (`IContentService`, `IDetectionService`, etc.)
- Domain-driven models (`GenerationRequest`, `AIScore`, etc.)
- Centralized configuration system (recently implemented)
- Service-oriented architecture patterns

### ❌ Issues to Address
- Mixed architecture patterns (DI + legacy direct instantiation)
- Complex application bootstrap (`core/application.py`)
- Inconsistent service registration patterns
- Legacy modules bypassing modern architecture
- Import path inconsistencies
- Tight coupling in some areas

## 🎯 Refactor Goals

1. **Clean Architecture**: Implement proper hexagonal/clean architecture
2. **Consistent DI**: All services use dependency injection
3. **Testability**: 100% unit testable with proper mocking
4. **Maintainability**: Single responsibility, clear boundaries
5. **Extensibility**: Easy to add new providers, services, features
6. **Performance**: Efficient service resolution and lifecycle management

## 🏛️ Proposed New Architecture

### Layer Structure
```
├── domain/                 # Core business logic (no dependencies)
│   ├── entities/          # Business entities
│   ├── value_objects/     # Immutable value objects
│   ├── services/          # Domain services
│   └── repositories/      # Repository interfaces
├── application/           # Application use cases
│   ├── commands/          # Command handlers
│   ├── queries/           # Query handlers
│   ├── services/          # Application services
│   └── interfaces/        # Application interfaces
├── infrastructure/        # External concerns
│   ├── api/              # External API clients
│   ├── persistence/      # Data storage
│   ├── messaging/        # Event handling
│   └── configuration/    # Config providers
└── presentation/          # User interfaces
    ├── cli/              # Command line interface
    ├── api/              # REST API (future)
    └── web/              # Web interface (future)
```

### Core Components

#### 1. Domain Layer (Pure Business Logic)
```python
# domain/entities/generation_request.py
class GenerationRequest:
    """Core business entity for content generation."""
    def __init__(self, material: str, sections: List[SectionSpec]):
        self.material = material
        self.sections = sections
        self.validate()
    
    def validate(self) -> None:
        """Business rule validation."""
        if not self.material:
            raise DomainError("Material cannot be empty")

# domain/services/content_generation_domain_service.py
class ContentGenerationDomainService:
    """Domain service for content generation business rules."""
    def calculate_word_budget(self, total_words: int, sections: List[SectionSpec]) -> Dict[str, int]:
        """Business logic for word budget allocation."""
        pass
```

#### 2. Application Layer (Use Cases)
```python
# application/commands/generate_content_command.py
@dataclass
class GenerateContentCommand:
    material: str
    max_words: int
    iterations: int

class GenerateContentHandler:
    def __init__(self, content_service: IContentService, detection_service: IDetectionService):
        self._content_service = content_service
        self._detection_service = detection_service
    
    async def handle(self, command: GenerateContentCommand) -> GenerationResult:
        """Orchestrate content generation use case."""
        pass
```

#### 3. Infrastructure Layer (Technical Concerns)
```python
# infrastructure/api/gemini_client.py
class GeminiClient(IAPIClient):
    """Gemini-specific API client implementation."""
    def __init__(self, config: APIClientConfig):
        self._config = config
    
    async def generate_content(self, prompt: str, temperature: float) -> str:
        """Gemini-specific implementation."""
        pass

# infrastructure/persistence/json_prompt_repository.py
class JsonPromptRepository(IPromptRepository):
    """JSON file-based prompt storage."""
    def __init__(self, file_path: str):
        self._file_path = file_path
    
    async def get_prompt(self, key: str) -> Optional[PromptTemplate]:
        """Load prompt from JSON file."""
        pass
```

#### 4. Dependency Injection Improvements
```python
# infrastructure/di/container.py
class ModernServiceContainer:
    """Enhanced DI container with lifecycle management."""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._instances: Dict[Type, Any] = {}
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register transient service (new instance each time)."""
        pass
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register singleton service (single instance)."""
        pass
    
    def register_scoped(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register scoped service (single instance per scope)."""
        pass
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register factory function."""
        pass
    
    async def resolve(self, interface: Type[T]) -> T:
        """Resolve service with proper lifecycle management."""
        pass
```

#### 5. Configuration System Enhancement
```python
# infrastructure/configuration/config_provider.py
class ConfigProvider:
    """Environment-aware configuration provider."""
    
    def __init__(self, environment: str = "production"):
        self._environment = environment
        self._config = self._load_config()
    
    def get_api_config(self, provider: str) -> APIConfig:
        """Get provider-specific API configuration."""
        pass
    
    def get_generation_config(self) -> GenerationConfig:
        """Get content generation configuration."""
        pass
    
    def get_detection_config(self) -> DetectionConfig:
        """Get detection configuration."""
        pass
```

## 🔄 Migration Strategy

### Phase 1: Foundation (Week 1)
1. **New Project Structure**: Create clean architecture folders
2. **Enhanced DI Container**: Implement `ModernServiceContainer`
3. **Domain Models**: Move and enhance existing domain models
4. **Configuration Provider**: Enhance configuration system

### Phase 2: Core Services (Week 2)
1. **Domain Services**: Extract business logic to domain layer
2. **Application Handlers**: Implement command/query handlers
3. **Infrastructure Services**: Refactor API clients and repositories
4. **Service Registration**: Migrate to new DI patterns

### Phase 3: Integration (Week 3)
1. **Application Bootstrap**: Simplify application startup
2. **Legacy Migration**: Update legacy modules to use new architecture
3. **Testing Framework**: Implement comprehensive test suite
4. **Documentation**: Update all documentation

### Phase 4: Optimization (Week 4)
1. **Performance Tuning**: Optimize service resolution
2. **Monitoring**: Add metrics and logging
3. **Validation**: Comprehensive system testing
4. **Deployment**: Production readiness

## 🧪 Testing Strategy

### Unit Tests
```python
# tests/unit/domain/services/test_content_generation_domain_service.py
class TestContentGenerationDomainService:
    def test_calculate_word_budget_distributes_correctly(self):
        service = ContentGenerationDomainService()
        result = service.calculate_word_budget(1200, sections)
        assert result["introduction"] == 180
        assert sum(result.values()) == 1200
```

### Integration Tests
```python
# tests/integration/test_content_generation_workflow.py
class TestContentGenerationWorkflow:
    async def test_full_generation_workflow(self):
        container = create_test_container()
        handler = container.resolve(GenerateContentHandler)
        result = await handler.handle(GenerateContentCommand(...))
        assert result.success
```

## 📊 Benefits Expected

### Development Benefits
- **Faster Feature Development**: Clear patterns and boundaries
- **Easier Testing**: Proper dependency injection enables easy mocking
- **Better Debugging**: Clear service boundaries and logging
- **Reduced Bugs**: Strong typing and validation

### Operational Benefits
- **Better Performance**: Optimized service lifecycle management
- **Easier Deployment**: Clear configuration management
- **Better Monitoring**: Structured logging and metrics
- **Easier Scaling**: Modular architecture supports horizontal scaling

## 🚀 Implementation Timeline

**Total Estimated Time**: 4 weeks (80-100 hours)

**Deliverables**:
1. Complete clean architecture implementation
2. 95%+ test coverage
3. Comprehensive documentation
4. Migration guide
5. Performance benchmarks

## 🔧 Tools and Technologies

- **DI Container**: Enhanced custom container with lifecycle management
- **Testing**: pytest with fixtures and mocking
- **Validation**: pydantic for data validation
- **Configuration**: python-decouple for environment management
- **Logging**: structlog for structured logging
- **Metrics**: prometheus_client for monitoring

## Next Steps

1. **Approval**: Get stakeholder approval for full refactor
2. **Planning**: Detailed sprint planning for 4-week timeline
3. **Branch Creation**: Create feature branch for architecture refactor
4. **Foundation**: Start with Phase 1 implementation

This refactor will transform Z-Beam into a modern, maintainable, and scalable system that follows industry best practices and supports future growth.
