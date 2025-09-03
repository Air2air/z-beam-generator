# Root-Level AI Detection Architecture Proposal

## Overview
Move AI detection from the content component to the root level, making it a shared service available to all components while maintaining backward compatibility.

## Current Architecture Issues
- AI detection is tightly coupled to content generation
- Other components cannot access AI detection capabilities
- Configuration is scattered across components
- Difficult to swap AI detection providers

## Proposed Architecture

### 1. Root-Level AI Detection Service (`/ai_detection/`)

```
ai_detection/
├── __init__.py
├── service.py              # Main AI detection service
├── providers/              # Provider implementations
│   ├── __init__.py
│   ├── gptzero.py         # GPTZero provider
│   ├── phrasly.py         # Phrasly.ai provider (legacy)
│   └── mock.py            # Mock provider for testing
├── config.py              # AI detection configuration
├── exceptions.py          # AI detection specific exceptions
└── types.py               # Type definitions
```

### 2. Service Interface

```python
# ai_detection/service.py
class AIDetectionService:
    """Main AI detection service interface"""

    def __init__(self, provider: str = "gptzero", config: Dict = None):
        self.provider = self._create_provider(provider, config)

    def analyze_text(self, text: str) -> AIDetectionResult:
        """Analyze text for AI detection"""
        return self.provider.analyze_text(text)

    def is_available(self) -> bool:
        """Check if AI detection service is available"""
        return self.provider.is_available()

    def _create_provider(self, provider_name: str, config: Dict):
        """Factory method for creating providers"""
        # Implementation details...
```

### 3. Component Integration

```python
# components/content/enhanced_generator.py
class EnhancedContentComponentGenerator:
    def __init__(self,
                 ai_detection_service: Optional[AIDetectionService] = None,
                 **kwargs):
        self.ai_detection = ai_detection_service
        # ... rest of initialization

    def generate(self, **kwargs):
        if self.ai_detection and self.ai_detection.is_available():
            # Use AI detection for iterative improvement
            pass
        else:
            # Fallback to original generation
            pass
```

### 4. Root Application Integration

```python
# run.py or main application entry point
def main():
    # Initialize AI detection service at root level
    ai_detection_config = load_ai_detection_config()
    ai_detection_service = AIDetectionService(
        provider=ai_detection_config.get('provider', 'gptzero'),
        config=ai_detection_config
    )

    # Create component generators with AI detection service
    content_generator = create_content_generator(
        ai_detection_service=ai_detection_service
    )

    # Other components can also receive the service
    # component_generator = create_component_generator(
    #     ai_detection_service=ai_detection_service
    # )
```

## Benefits

### 1. **Separation of Concerns**
- AI detection logic is isolated from content generation
- Each component focuses on its primary responsibility

### 2. **Reusability**
- Any component can use AI detection capabilities
- Easy to add AI detection to new components

### 3. **Flexibility**
- Easy to swap AI detection providers
- Configuration centralized at root level
- Support for multiple providers simultaneously

### 4. **Testability**
- AI detection can be mocked at the service level
- Components can be tested without AI detection dependencies

### 5. **Maintainability**
- Single source of truth for AI detection configuration
- Easier to update AI detection logic
- Better error handling and logging

## Implementation Plan

### Phase 1: Create Root-Level Service
1. Create `ai_detection/` directory structure
2. Implement base service interface
3. Move GPTZero provider to new location
4. Create provider factory

### Phase 2: Update Content Component
1. Modify content component to accept AI detection service
2. Update factory functions to inject service
3. Maintain backward compatibility

### Phase 3: Root-Level Integration
1. Update main application to initialize AI detection service
2. Update configuration loading
3. Update component creation to use service

### Phase 4: Testing & Documentation
1. Update tests to use new architecture
2. Update documentation
3. Add integration tests

## Migration Strategy

### Backward Compatibility
- Content component can still work without AI detection service
- Existing configuration files remain valid
- Graceful degradation when service unavailable

### Gradual Migration
1. Implement new architecture alongside existing
2. Update components one by one
3. Remove old code after full migration
4. Update documentation and examples

## Configuration Changes

### Current (Component-Level)
```yaml
# config/gptzero_config.yaml
GPTZERO_API_KEY: "key"
GPTZERO_TARGET_SCORE: 30.0
```

### Proposed (Root-Level)
```yaml
# config/ai_detection.yaml
provider: "gptzero"
gptzero:
  api_key: "key"
  target_score: 30.0
  max_iterations: 3
phrasly:
  api_key: "key"
  target_score: 30.0
```

## Error Handling

### Service-Level Errors
- Provider unavailable
- API rate limits
- Authentication failures
- Network timeouts

### Component-Level Fallback
- Continue generation without AI detection
- Log warnings about service unavailability
- Maintain functionality with reduced features

This architecture provides a clean separation while maintaining the powerful AI detection capabilities we've built.
