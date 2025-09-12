# Optimizer Troubleshooting Guide

## Overview
Comprehensive troubleshooting guide for the Z-Beam Optimizer system, covering common issues, diagnostic procedures, and resolution strategies.

## Quick Diagnostic Command
```bash
# Run comprehensive system health check
python3 scripts/tools/prompt_chain_diagnostics.py
```

## Common Issues and Solutions

### 1. API Configuration Errors

#### KeyError: 'name' in API Client Initialization
**Symptom**: 
```
KeyError: 'name'
  File "api/client_factory.py", line X, in create_client
```

**Root Cause**: Incomplete API provider configuration in `run.py`

**Solution**:
Ensure complete API provider configuration with all required fields:

```python
# In run.py
API_PROVIDERS = {
    "deepseek": {
        "name": "deepseek",                    # ✅ Required field
        "base_url": "https://api.deepseek.com/v1",  # ✅ Required field
        "model": "deepseek-chat",              # ✅ Required field
        "timeout": 30,                         # ✅ Required field
        "retry_delay": 1.0                     # ✅ Required field
    },
    "winston": {
        "name": "winston",                     # ✅ Required field
        "base_url": "https://api.gowinston.ai" # ✅ Required field
    }
}
```

**Validation Command**:
```bash
python3 -c "
import sys
sys.path.append('.')
from run import API_PROVIDERS
required_fields = {'deepseek': ['name', 'base_url', 'model', 'timeout', 'retry_delay'],
                   'winston': ['name', 'base_url']}
for provider, config in API_PROVIDERS.items():
    missing = [field for field in required_fields.get(provider, []) if field not in config]
    if missing:
        print(f'❌ {provider} missing: {missing}')
    else:
        print(f'✅ {provider} configuration complete')
"
```

#### SSL Certificate Errors with Winston API
**Symptom**: 
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Root Cause**: Incorrect base_url configuration

**Solution**: Use correct HTTPS endpoint:
```python
"winston": {
    "name": "winston",
    "base_url": "https://api.gowinston.ai"  # ✅ Correct HTTPS URL
}
```

### 2. Modular Component System Issues

#### Missing modular_components Section
**Symptom**:
```
KeyError: 'modular_components'
ModularLoader failed to find component mappings
```

**Root Cause**: Missing or incomplete modular_components configuration in `ai_detection_core.yaml`

**Solution**: Add complete modular_components mapping to `components/text/prompts/core/ai_detection_core.yaml`:

```yaml
modular_components:
  authenticity_enhancements: "modules/authenticity_enhancements.yaml"
  cultural_adaptation: "modules/cultural_adaptation.yaml"
  detection_avoidance: "modules/detection_avoidance.yaml"
  human_characteristics: "modules/human_characteristics.yaml"
  structural_improvements: "modules/structural_improvements.yaml"
```

**Validation Command**:
```bash
python3 -c "
import yaml
import os
core_file = 'components/text/prompts/core/ai_detection_core.yaml'
if os.path.exists(core_file):
    with open(core_file, 'r') as f:
        config = yaml.safe_load(f)
    if 'modular_components' in config:
        components = config['modular_components']
        print(f'✅ Found {len(components)} modular components:')
        for name, path in components.items():
            module_path = f'components/text/prompts/{path}'
            exists = '✅' if os.path.exists(module_path) else '❌'
            print(f'   {exists} {name}: {path}')
    else:
        print('❌ Missing modular_components section')
else:
    print('❌ Core configuration file not found')
"
```

#### Module Files Not Found
**Symptom**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'components/text/prompts/modules/[component].yaml'
```

**Root Cause**: Missing module files in the modules directory

**Solution**: Verify all required module files exist:
```bash
# Check module files
ls -la components/text/prompts/modules/
# Should show:
# authenticity_enhancements.yaml
# cultural_adaptation.yaml  
# detection_avoidance.yaml
# human_characteristics.yaml
# structural_improvements.yaml
```

**Creation Command** (if files are missing):
```bash
# Create missing module files with basic structure
for module in authenticity_enhancements cultural_adaptation detection_avoidance human_characteristics structural_improvements; do
    if [ ! -f "components/text/prompts/modules/${module}.yaml" ]; then
        echo "Creating ${module}.yaml"
        echo "${module}:" > "components/text/prompts/modules/${module}.yaml"
        echo "  # ${module} configuration" >> "components/text/prompts/modules/${module}.yaml"
    fi
done
```

### 3. Dynamic Prompt Generator Issues

#### DynamicPromptGenerator Initialization Failure
**Symptom**:
```
Exception during DynamicPromptGenerator initialization
Cannot create generator instance
```

**Root Cause**: Modular loader prioritization issue in `_load_current_prompts` method

**Solution**: Ensure proper modular loader prioritization in `optimizer/text_optimization/dynamic_prompt_generator.py`:

```python
def _load_current_prompts(self):
    """Load prompts with modular loader priority and proper fallback."""
    try:
        # Primary: Use modular loader for complete configuration
        config = self.modular_loader.load_complete_configuration()
        logger.info("Successfully loaded configuration via modular loader")
        return config
    except Exception as e:
        logger.warning(f"Modular loader failed: {e}")
        # Fallback: Direct file loading
        try:
            return self._load_direct_prompts()
        except Exception as fallback_error:
            logger.error(f"Both modular and direct loading failed: {fallback_error}")
            raise
```

**Validation Command**:
```bash
python3 -c "
from optimizer.text_optimization.dynamic_prompt_generator import DynamicPromptGenerator
try:
    generator = DynamicPromptGenerator()
    print('✅ DynamicPromptGenerator initialized successfully')
    
    # Test prompt loading
    prompts = generator._load_current_prompts()
    print(f'✅ Loaded {len(prompts)} prompt sections')
    
except Exception as e:
    print(f'❌ Initialization failed: {e}')
    import traceback
    traceback.print_exc()
"
```

### 4. Content Generation Issues

#### Low Quality Scores
**Symptom**: Generated content consistently receives low quality scores

**Root Cause**: Insufficient enhancement flags or incorrect persona configuration

**Solution**: Optimize enhancement flags and persona settings:

```python
# Comprehensive enhancement flags
enhancement_flags = {
    'conversational_boost': True,
    'human_elements_emphasis': True,
    'sentence_variability': True,
    'cultural_adaptation': True,
    'detection_avoidance': True,
    'structural_optimization': True
}

# Test with different personas
for author_id in [1, 2, 3, 4]:  # Taiwan, Italy, Indonesia, USA
    result = generator.generate_optimized_prompt(
        material_name="aluminum",
        author_id=author_id,
        enhancement_flags=enhancement_flags
    )
```

#### Winston AI Detection Scores Too High
**Symptom**: Content flagged as AI-generated by Winston

**Root Cause**: Insufficient detection avoidance techniques

**Solution**: Enable detection avoidance enhancements:

```python
enhancement_flags = {
    'detection_avoidance': True,
    'human_elements_emphasis': True,
    'conversational_boost': True,
    'sentence_variability': True
}
```

### 5. Performance Issues

#### Slow Configuration Loading
**Symptom**: Long delays during prompt configuration loading

**Root Cause**: Repeated file I/O without caching

**Solution**: Implement configuration caching:

```python
from functools import lru_cache

@lru_cache(maxsize=10)
def cached_load_configuration():
    return modular_loader.load_complete_configuration()
```

#### Memory Usage Issues
**Symptom**: High memory consumption during optimization

**Root Cause**: Large configuration objects not being garbage collected

**Solution**: Implement proper cleanup:

```python
# After optimization
del generator
import gc
gc.collect()
```

## Diagnostic Commands

### System Health Check
```bash
# Comprehensive system validation
python3 scripts/tools/prompt_chain_diagnostics.py

# Expected output includes:
# ✅ Modular components: 5/5 loaded
# ✅ API configuration: Complete
# ✅ Personas: 4/4 available
# ✅ System health: 94.1%
```

### API Connectivity Tests
```bash
# Test DeepSeek API
python3 scripts/tools/api_terminal_diagnostics.py deepseek

# Test Winston API  
python3 scripts/tools/api_terminal_diagnostics.py winston

# Expected output:
# ✅ API endpoint reachable
# ✅ Authentication successful
# ✅ Response format valid
```

### Component Validation
```bash
# Validate modular component system
python3 -c "
from optimizer.text_optimization.utils.modular_loader import ModularLoader
loader = ModularLoader()
try:
    config = loader.load_complete_configuration()
    print(f'✅ Loaded {len(config)} configuration sections:')
    for section in config.keys():
        print(f'   - {section}')
    
    # Validate each section has content
    empty_sections = [k for k, v in config.items() if not v]
    if empty_sections:
        print(f'⚠️  Empty sections: {empty_sections}')
    else:
        print('✅ All sections have content')
        
except Exception as e:
    print(f'❌ Validation failed: {e}')
"
```

### Configuration Validation
```bash
# Check all YAML files are valid
find components/text/prompts -name "*.yaml" -exec python3 -c "
import yaml
import sys
try:
    with open('{}', 'r') as f:
        yaml.safe_load(f)
    print('✅ {}')
except Exception as e:
    print('❌ {}: {}'.format('{}', e))
" \;
```

## Performance Optimization

### Configuration Caching
```python
# Enable configuration caching
from functools import lru_cache
from optimizer.text_optimization.utils.modular_loader import ModularLoader

class CachedModularLoader(ModularLoader):
    @lru_cache(maxsize=1)
    def load_complete_configuration(self):
        return super().load_complete_configuration()
```

### Memory Management
```python
# Optimize memory usage
import gc
import psutil

def optimize_memory():
    """Optimize memory usage during long-running optimizations."""
    gc.collect()
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.1f} MB")
```

### Batch Processing Optimization
```python
# Optimize batch processing
def optimized_batch_generation(materials, batch_size=5):
    """Process materials in optimized batches."""
    for i in range(0, len(materials), batch_size):
        batch = materials[i:i+batch_size]
        # Process batch
        yield process_batch(batch)
        # Cleanup between batches
        gc.collect()
```

## Monitoring and Logging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Specific logger configuration
logger = logging.getLogger('optimizer.text_optimization')
logger.setLevel(logging.DEBUG)
```

### Performance Monitoring
```python
import time
import functools

def monitor_performance(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        print(f"{func.__name__} took {duration:.2f} seconds")
        return result
    return wrapper
```

### Error Tracking
```python
import traceback
import logging

def track_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            logging.error(traceback.format_exc())
            raise
    return wrapper
```

## Recovery Procedures

### Reset Configuration Cache
```bash
# Clear Python cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Reset configuration
python3 -c "
import importlib
import sys
modules_to_reload = [
    'optimizer.text_optimization.utils.modular_loader',
    'optimizer.text_optimization.dynamic_prompt_generator'
]
for module in modules_to_reload:
    if module in sys.modules:
        importlib.reload(sys.modules[module])
print('✅ Configuration cache reset')
"
```

### Restore Default Configuration
```bash
# Backup current configuration
cp components/text/prompts/core/ai_detection_core.yaml components/text/prompts/core/ai_detection_core.yaml.backup

# Restore minimal working configuration
cat > components/text/prompts/core/ai_detection_core.yaml << 'EOF'
modular_components:
  authenticity_enhancements: "modules/authenticity_enhancements.yaml"
  cultural_adaptation: "modules/cultural_adaptation.yaml"
  detection_avoidance: "modules/detection_avoidance.yaml"
  human_characteristics: "modules/human_characteristics.yaml"
  structural_improvements: "modules/structural_improvements.yaml"

# Add minimal base configuration
base_ai_detection_guidance: |
  Generate natural, human-like content that avoids AI detection.
EOF
```

### Emergency Fallback Mode
```python
# Enable fallback mode in dynamic_prompt_generator.py
class DynamicPromptGenerator:
    def __init__(self, fallback_mode=True):
        self.fallback_mode = fallback_mode
        if fallback_mode:
            self.use_minimal_configuration()
    
    def use_minimal_configuration(self):
        """Use minimal configuration for emergency operations."""
        self.config = {
            'base_ai_detection_guidance': 'Generate natural content.',
            'personas': {},
            'formatting': {}
        }
```

## Support Resources

### Documentation References
- **Main README**: `optimizer/README.md`
- **Text Optimization**: `optimizer/text_optimization/docs/README.md`
- **Modular Components**: `optimizer/docs/MODULAR_COMPONENTS_REFERENCE.md`
- **API Reference**: `optimizer/docs/API_REFERENCE.md`

### Diagnostic Tools
- **System Health**: `scripts/tools/prompt_chain_diagnostics.py`
- **API Testing**: `scripts/tools/api_terminal_diagnostics.py`
- **Configuration Validation**: Built-in validation commands

### Contact and Support
- **Issue Tracking**: Document issues with full error traces
- **Configuration Backup**: Always backup working configurations
- **Version Control**: Track all configuration changes

## Common Error Patterns

### Pattern 1: Missing Dependencies
```
ImportError: No module named 'optimizer.text_optimization.utils'
```
**Solution**: Verify Python path and module installation

### Pattern 2: Configuration File Corruption
```
yaml.YAMLError: could not determine a constructor for the tag
```
**Solution**: Validate YAML syntax and restore from backup

### Pattern 3: API Rate Limiting
```
HTTPError: 429 Too Many Requests
```
**Solution**: Implement exponential backoff and request throttling

### Pattern 4: Memory Exhaustion
```
MemoryError: Unable to allocate array
```
**Solution**: Implement batch processing and memory cleanup

This troubleshooting guide provides comprehensive coverage of common issues and their resolutions. Keep this document updated as new issues are discovered and resolved.
